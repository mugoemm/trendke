"""
Enhanced Live Streaming API with Multi-Guest Support
======================================================
Features better than TikTok Live:
- Multiple guests/co-hosts (up to 20)
- Guest request system
- Host controls (mute, kick, promote)
- Real-time chat
- Reactions and gifts
- WebRTC ready integration
"""

from fastapi import APIRouter, HTTPException, Depends, status, WebSocket, WebSocketDisconnect
from typing import List, Optional
from datetime import datetime
import uuid
import secrets
import json

from .models import *
from .db import supabase
from .auth import get_current_user

router = APIRouter(prefix="/live", tags=["Live Streaming - Multi-Guest"])


# =====================================================
# HELPER FUNCTIONS
# =====================================================

def generate_access_token() -> str:
    """Generate secure access token"""
    return secrets.token_urlsafe(32)


def generate_room_name(session_id: str) -> str:
    """Generate unique room name for WebRTC"""
    return f"live_{session_id[:8]}_{secrets.token_hex(4)}"


# =====================================================
# SESSION MANAGEMENT
# =====================================================

@router.post("/start", response_model=LiveSessionResponse)
async def start_live_session(
    session_data: LiveSessionCreateRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Start a new live session with multi-guest support
    
    Features:
    - Voice, Camera, or Studio mode
    - Configurable guest settings
    - WebRTC room creation
    """
    try:
        session_id = str(uuid.uuid4())
        access_token = generate_access_token()
        room_name = generate_room_name(session_id)
        
        # Create live session
        session_result = supabase.table("live_sessions").insert({
            "id": session_id,
            "host_id": current_user["id"],
            "title": session_data.title,
            "description": session_data.description,
            "session_type": session_data.session_type,
            "status": "active",
            "thumbnail_url": session_data.thumbnail_url,
            "access_token": access_token,
            "room_name": room_name,
            "viewer_count": 0,
            "guest_count": 0,
            "max_participants": session_data.max_participants,
            "started_at": datetime.utcnow().isoformat()
        }).execute()
        
        if not session_result.data:
            raise HTTPException(status_code=500, detail="Failed to create session")
        
        session = session_result.data[0]
        
        # Create session settings
        supabase.table("live_session_settings").insert({
            "session_id": session_id,
            "allow_guests": session_data.allow_guests,
            "require_approval": session_data.require_approval,
            "max_guests": session_data.max_guests,
            "enable_chat": session_data.enable_chat,
            "enable_gifts": session_data.enable_gifts,
            "guest_audio_default": session_data.guest_audio_default,
            "guest_video_default": session_data.guest_video_default
        }).execute()
        
        # Add host as participant
        supabase.table("live_participants").insert({
            "session_id": session_id,
            "user_id": current_user["id"],
            "role": "host",
            "status": "active",
            "audio_enabled": True,
            "video_enabled": True
        }).execute()
        
        print(f"🎥 Live session started: {session_id} by {current_user['username']}")
        
        return LiveSessionResponse(
            id=session["id"],
            host_id=session["host_id"],
            host_username=current_user["username"],
            host_avatar_url=current_user.get("avatar_url"),
            title=session["title"],
            description=session.get("description"),
            session_type=session["session_type"],
            status=session["status"],
            thumbnail_url=session.get("thumbnail_url"),
            room_name=room_name,
            access_token=access_token,
            viewer_count=0,
            guest_count=0,
            max_participants=session["max_participants"],
            started_at=session.get("started_at"),
            settings=session_data
        )
        
    except Exception as e:
        print(f"❌ Error starting live session: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start live session: {str(e)}")


@router.post("/join", response_model=EnhancedLiveJoinResponse)
async def join_live_session(
    join_request: LiveJoinRequest,
    current_user: dict = Depends(get_current_user)
):
    """Join a live session as a viewer"""
    try:
        # Get session
        session_result = supabase.table("live_sessions").select("*, live_session_settings(*)").eq(
            "id", join_request.session_id
        ).single().execute()
        
        if not session_result.data:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session = session_result.data
        
        if session["status"] != "active":
            raise HTTPException(status_code=400, detail="Session is not active")
        
        # Check capacity
        if session["viewer_count"] >= session["max_participants"]:
            raise HTTPException(status_code=400, detail="Session is full")
        
        # Update viewer count
        new_count = session["viewer_count"] + 1
        supabase.table("live_sessions").update({
            "viewer_count": new_count
        }).eq("id", join_request.session_id).execute()
        
        # Add as participant (viewer)
        supabase.table("live_participants").insert({
            "session_id": join_request.session_id,
            "user_id": current_user["id"],
            "role": "viewer",
            "status": "active"
        }).execute()
        
        # WebRTC configuration
        webrtc_config = {
            "server_url": "wss://live.trendke.com",  # Replace with your WebRTC server
            "room_name": session["room_name"],
            "participant_token": generate_access_token(),
            "ice_servers": [
                {"urls": "stun:stun.l.google.com:19302"},
                {"urls": "stun:stun1.l.google.com:19302"}
            ]
        }
        
        print(f"👤 User {current_user['username']} joined session {join_request.session_id}")
        
        return EnhancedLiveJoinResponse(
            session_id=session["id"],
            room_name=session["room_name"],
            access_token=session["access_token"],
            webrtc_config=webrtc_config,
            role="viewer",
            can_request_guest=session.get("live_session_settings", [{}])[0].get("allow_guests", True)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error joining session: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to join session: {str(e)}")


@router.post("/end/{session_id}")
async def end_live_session(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """End a live session (host only)"""
    try:
        # Verify host
        session = supabase.table("live_sessions").select("*").eq("id", session_id).single().execute()
        
        if not session.data:
            raise HTTPException(status_code=404, detail="Session not found")
        
        if session.data["host_id"] != current_user["id"]:
            raise HTTPException(status_code=403, detail="Only host can end the session")
        
        # Update session
        supabase.table("live_sessions").update({
            "status": "ended",
            "ended_at": datetime.utcnow().isoformat()
        }).eq("id", session_id).execute()
        
        # Update all participants
        supabase.table("live_participants").update({
            "status": "left",
            "left_at": datetime.utcnow().isoformat()
        }).eq("session_id", session_id).execute()
        
        print(f"🛑 Live session ended: {session_id}")
        
        return {
            "message": "Live session ended successfully",
            "session_id": session_id,
            "duration_seconds": (datetime.fromisoformat(datetime.utcnow().isoformat()) - 
                                 datetime.fromisoformat(session.data["started_at"])).seconds
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to end session: {str(e)}")


# =====================================================
# GUEST MANAGEMENT
# =====================================================

@router.post("/request-guest", response_model=GuestRequestResponse)
async def request_to_be_guest(
    request_data: GuestRequest,
    current_user: dict = Depends(get_current_user)
):
    """Request to join as a guest/co-host"""
    try:
        # Check session settings
        settings = supabase.table("live_session_settings").select("*").eq(
            "session_id", request_data.session_id
        ).single().execute()
        
        if not settings.data or not settings.data.get("allow_guests"):
            raise HTTPException(status_code=403, detail="This session doesn't allow guests")
        
        # Check if already a guest
        existing = supabase.table("live_participants").select("*").eq(
            "session_id", request_data.session_id
        ).eq("user_id", current_user["id"]).execute()
        
        if existing.data and existing.data[0]["role"] in ["guest", "cohost"]:
            raise HTTPException(status_code=400, detail="Already a guest in this session")
        
        # Create request
        result = supabase.table("live_guest_requests").insert({
            "session_id": request_data.session_id,
            "user_id": current_user["id"],
            "request_type": request_data.request_type,
            "message": request_data.message,
            "status": "pending"
        }).execute()
        
        print(f"🙋 Guest request from {current_user['username']} for session {request_data.session_id}")
        
        return GuestRequestResponse(
            id=result.data[0]["id"],
            session_id=request_data.session_id,
            user_id=current_user["id"],
            username=current_user["username"],
            avatar_url=current_user.get("avatar_url"),
            request_type=request_data.request_type,
            status="pending",
            message=request_data.message,
            created_at=result.data[0]["created_at"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create request: {str(e)}")


@router.post("/respond-guest-request")
async def respond_to_guest_request(
    response_data: GuestRequestResponseAction,
    current_user: dict = Depends(get_current_user)
):
    """Approve or reject a guest request (host only)"""
    try:
        # Get request
        request = supabase.table("live_guest_requests").select(
            "*, live_sessions!inner(host_id)"
        ).eq("id", response_data.request_id).single().execute()
        
        if not request.data:
            raise HTTPException(status_code=404, detail="Request not found")
        
        # Verify host
        if request.data["live_sessions"]["host_id"] != current_user["id"]:
            raise HTTPException(status_code=403, detail="Only host can respond to requests")
        
        # Update request
        supabase.table("live_guest_requests").update({
            "status": response_data.action,
            "responded_at": datetime.utcnow().isoformat(),
            "responded_by": current_user["id"]
        }).eq("id", response_data.request_id).execute()
        
        # If approved, add as participant
        if response_data.action == "approved":
            session_id = request.data["session_id"]
            user_id = request.data["user_id"]
            
            # Check current guest count
            session = supabase.table("live_sessions").select("guest_count, live_session_settings(max_guests)").eq(
                "id", session_id
            ).single().execute()
            
            max_guests = session.data["live_session_settings"][0]["max_guests"]
            if session.data["guest_count"] >= max_guests:
                raise HTTPException(status_code=400, detail="Maximum guests reached")
            
            # Update or insert participant
            supabase.table("live_participants").upsert({
                "session_id": session_id,
                "user_id": user_id,
                "role": request.data["request_type"],
                "status": "active",
                "audio_enabled": True,
                "video_enabled": True
            }).execute()
            
            print(f"✅ Guest request approved: {user_id} → {session_id}")
        
        return {
            "message": f"Request {response_data.action}",
            "request_id": response_data.request_id,
            "action": response_data.action
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to respond to request: {str(e)}")


@router.get("/guest-requests/{session_id}", response_model=List[GuestRequestResponse])
async def get_guest_requests(
    session_id: str,
    status: Optional[str] = "pending",
    current_user: dict = Depends(get_current_user)
):
    """Get all guest requests for a session (host only)"""
    try:
        # Verify host
        session = supabase.table("live_sessions").select("host_id").eq("id", session_id).single().execute()
        
        if not session.data:
            raise HTTPException(status_code=404, detail="Session not found")
        
        if session.data["host_id"] != current_user["id"]:
            raise HTTPException(status_code=403, detail="Only host can view requests")
        
        # Get requests
        query = supabase.table("live_guest_requests").select(
            "*, users!live_guest_requests_user_id_fkey(username, avatar_url)"
        ).eq("session_id", session_id)
        
        if status:
            query = query.eq("status", status)
        
        result = query.order("created_at", desc=True).execute()
        
        requests = []
        for req in result.data:
            user_data = req.get("users", {})
            requests.append(GuestRequestResponse(
                id=req["id"],
                session_id=req["session_id"],
                user_id=req["user_id"],
                username=user_data.get("username", ""),
                avatar_url=user_data.get("avatar_url"),
                request_type=req["request_type"],
                status=req["status"],
                message=req.get("message"),
                created_at=req["created_at"],
                responded_at=req.get("responded_at")
            ))
        
        return requests
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch requests: {str(e)}")


@router.post("/manage-participant")
async def manage_participant(
    action_data: ParticipantAction,
    current_user: dict = Depends(get_current_user)
):
    """
    Manage participants (host only)
    Actions: mute_audio, mute_video, unmute_audio, unmute_video, kick, promote_cohost, demote
    """
    try:
        # Verify host
        session = supabase.table("live_sessions").select("host_id").eq(
            "id", action_data.session_id
        ).single().execute()
        
        if not session.data or session.data["host_id"] != current_user["id"]:
            raise HTTPException(status_code=403, detail="Only host can manage participants")
        
        # Get participant
        participant = supabase.table("live_participants").select("*").eq(
            "session_id", action_data.session_id
        ).eq("user_id", action_data.user_id).single().execute()
        
        if not participant.data:
            raise HTTPException(status_code=404, detail="Participant not found")
        
        # Apply action
        update_data = {}
        
        if action_data.action == "mute_audio":
            update_data["audio_enabled"] = False
        elif action_data.action == "unmute_audio":
            update_data["audio_enabled"] = True
        elif action_data.action == "mute_video":
            update_data["video_enabled"] = False
        elif action_data.action == "unmute_video":
            update_data["video_enabled"] = True
        elif action_data.action == "kick":
            update_data["status"] = "kicked"
            update_data["left_at"] = datetime.utcnow().isoformat()
        elif action_data.action == "promote_cohost":
            update_data["role"] = "cohost"
        elif action_data.action == "demote":
            update_data["role"] = "guest"
        else:
            raise HTTPException(status_code=400, detail="Invalid action")
        
        # Update participant
        supabase.table("live_participants").update(update_data).eq(
            "session_id", action_data.session_id
        ).eq("user_id", action_data.user_id).execute()
        
        print(f"⚙️ Participant action: {action_data.action} on {action_data.user_id}")
        
        return {
            "message": f"Action '{action_data.action}' applied successfully",
            "user_id": action_data.user_id,
            "action": action_data.action
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to manage participant: {str(e)}")


@router.get("/participants/{session_id}", response_model=List[ParticipantInfo])
async def get_session_participants(session_id: str):
    """Get all active participants in a session"""
    try:
        result = supabase.table("live_participants").select(
            "*, users!live_participants_user_id_fkey(username, avatar_url)"
        ).eq("session_id", session_id).eq("status", "active").execute()
        
        participants = []
        for p in result.data:
            user_data = p.get("users", {})
            participants.append(ParticipantInfo(
                id=p["id"],
                user_id=p["user_id"],
                username=user_data.get("username", ""),
                avatar_url=user_data.get("avatar_url"),
                role=p["role"],
                status=p["status"],
                audio_enabled=p.get("audio_enabled", False),
                video_enabled=p.get("video_enabled", False),
                screen_sharing=p.get("screen_sharing", False),
                joined_at=p["joined_at"]
            ))
        
        return participants
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch participants: {str(e)}")


# =====================================================
# LIVE CHAT
# =====================================================

@router.post("/send-message")
async def send_chat_message(
    message_data: ChatMessage,
    current_user: dict = Depends(get_current_user)
):
    """Send a chat message in live session"""
    try:
        result = supabase.table("live_chat_messages").insert({
            "session_id": message_data.session_id,
            "user_id": current_user["id"],
            "message": message_data.message,
            "message_type": message_data.message_type or "text",
            "metadata": message_data.metadata
        }).execute()
        
        return {
            "id": result.data[0]["id"],
            "message": "Message sent",
            "created_at": result.data[0]["created_at"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send message: {str(e)}")


@router.get("/messages/{session_id}", response_model=List[ChatMessageResponse])
async def get_chat_messages(
    session_id: str,
    limit: int = 50,
    before: Optional[str] = None
):
    """Get chat messages for a live session"""
    try:
        query = supabase.table("live_chat_messages").select(
            "*, users!live_chat_messages_user_id_fkey(username, avatar_url)"
        ).eq("session_id", session_id)
        
        if before:
            query = query.lt("created_at", before)
        
        result = query.order("created_at", desc=True).limit(limit).execute()
        
        messages = []
        for msg in result.data:
            user_data = msg.get("users", {})
            messages.append(ChatMessageResponse(
                id=msg["id"],
                session_id=msg["session_id"],
                user_id=msg["user_id"],
                username=user_data.get("username", ""),
                avatar_url=user_data.get("avatar_url"),
                message=msg["message"],
                message_type=msg["message_type"],
                metadata=msg.get("metadata"),
                created_at=msg["created_at"]
            ))
        
        return list(reversed(messages))  # Return in chronological order
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch messages: {str(e)}")


# =====================================================
# ACTIVE SESSIONS
# =====================================================

@router.get("/active", response_model=List[LiveSessionSummary])
async def get_active_sessions(limit: int = 20):
    """Get all active live sessions"""
    try:
        result = supabase.table("live_sessions").select(
            """
            *,
            users!live_sessions_host_id_fkey(username, avatar_url),
            live_session_settings(allow_guests, max_guests)
            """
        ).eq("status", "active").order("viewer_count", desc=True).limit(limit).execute()
        
        sessions = []
        for session in result.data:
            user_data = session.get("users", {})
            settings = session.get("live_session_settings", [{}])[0]
            
            sessions.append(LiveSessionSummary(
                id=session["id"],
                host_id=session["host_id"],
                host_username=user_data.get("username", ""),
                host_avatar_url=user_data.get("avatar_url"),
                title=session["title"],
                description=session.get("description"),
                session_type=session["session_type"],
                thumbnail_url=session.get("thumbnail_url"),
                viewer_count=session.get("viewer_count", 0),
                guest_count=session.get("guest_count", 0),
                max_guests=settings.get("max_guests", 8),
                allow_guests=settings.get("allow_guests", True),
                started_at=session["started_at"]
            ))
        
        return sessions
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch active sessions: {str(e)}")


@router.get("/session/{session_id}", response_model=LiveSessionDetail)
async def get_session_details(session_id: str):
    """Get detailed information about a live session"""
    try:
        result = supabase.table("live_sessions").select(
            """
            *,
            users!live_sessions_host_id_fkey(username, avatar_url),
            live_session_settings(*),
            live_participants!inner(count)
            """
        ).eq("id", session_id).single().execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session = result.data
        user_data = session.get("users", {})
        settings = session.get("live_session_settings", [{}])[0]
        
        return LiveSessionDetail(
            id=session["id"],
            host_id=session["host_id"],
            host_username=user_data.get("username", ""),
            host_avatar_url=user_data.get("avatar_url"),
            title=session["title"],
            description=session.get("description"),
            session_type=session["session_type"],
            status=session["status"],
            thumbnail_url=session.get("thumbnail_url"),
            room_name=session.get("room_name"),
            viewer_count=session.get("viewer_count", 0),
            guest_count=session.get("guest_count", 0),
            peak_viewers=session.get("peak_viewers", 0),
            total_gifts_received=session.get("total_gifts_received", 0),
            allow_guests=settings.get("allow_guests", True),
            max_guests=settings.get("max_guests", 8),
            enable_chat=settings.get("enable_chat", True),
            enable_gifts=settings.get("enable_gifts", True),
            started_at=session["started_at"],
            ended_at=session.get("ended_at")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch session details: {str(e)}")


# =====================================================
# REACTIONS
# =====================================================

@router.post("/react")
async def send_reaction(
    reaction_data: ReactionData,
    current_user: dict = Depends(get_current_user)
):
    """Send a reaction (heart, emoji) during live"""
    try:
        supabase.table("live_reactions").insert({
            "session_id": reaction_data.session_id,
            "user_id": current_user["id"],
            "reaction_type": reaction_data.reaction_type
        }).execute()
        
        return {"message": "Reaction sent", "reaction_type": reaction_data.reaction_type}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send reaction: {str(e)}")
