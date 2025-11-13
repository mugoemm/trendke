from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional
from datetime import datetime
import uuid
import secrets

from .models import (
    LiveSessionCreate, LiveSession, LiveJoinRequest, 
    LiveJoinResponse, LiveSessionType, LiveSessionStatus
)
from .db import db, supabase
from .auth import get_current_user

router = APIRouter(prefix="/live", tags=["Live Streaming"])


def generate_access_token() -> str:
    """Generate secure access token for live session"""
    return secrets.token_urlsafe(32)


@router.post("/start", response_model=LiveSession)
async def start_live_session(
    session_data: LiveSessionCreate,
    current_user: dict = Depends(get_current_user)
):
    """Start a new live streaming session (voice/camera/studio)"""
    try:
        session_id = str(uuid.uuid4())
        access_token = generate_access_token()
        
        # Create live session in database
        live_session_data = {
            "id": session_id,
            "host_id": current_user["id"],
            "title": session_data.title,
            "description": session_data.description,
            "session_type": session_data.session_type,
            "status": LiveSessionStatus.ACTIVE,
            "thumbnail_url": session_data.thumbnail_url,
            "access_token": access_token,
            "viewer_count": 0,
            "max_participants": session_data.max_participants,
            "started_at": datetime.utcnow().isoformat()
        }
        
        created_session = db.create_live_session(live_session_data)
        if not created_session:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create live session"
            )
        
        return LiveSession(
            id=created_session["id"],
            host_id=created_session["host_id"],
            host_username=current_user["username"],
            host_avatar_url=current_user.get("avatar_url"),
            title=created_session["title"],
            description=created_session.get("description"),
            session_type=created_session["session_type"],
            status=created_session["status"],
            thumbnail_url=created_session.get("thumbnail_url"),
            access_token=created_session["access_token"],
            viewer_count=created_session.get("viewer_count", 0),
            max_participants=created_session.get("max_participants", 50),
            started_at=created_session.get("started_at"),
            ended_at=created_session.get("ended_at"),
            created_at=created_session["created_at"]
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start live session: {str(e)}"
        )


@router.post("/join", response_model=LiveJoinResponse)
async def join_live_session(
    join_request: LiveJoinRequest,
    current_user: dict = Depends(get_current_user)
):
    """Join an active live session"""
    try:
        # Get session details
        session = supabase.table("live_sessions").select("""
            *,
            users!live_sessions_host_id_fkey (username, avatar_url)
        """).eq("id", join_request.session_id).single().execute()
        
        if not session.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Live session not found"
            )
        
        session_data = session.data
        
        if session_data["status"] != LiveSessionStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Live session is not active"
            )
        
        # Check participant limit
        current_viewers = session_data.get("viewer_count", 0)
        max_participants = session_data.get("max_participants", 50)
        
        if current_viewers >= max_participants:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Live session is at maximum capacity"
            )
        
        # Increment viewer count
        supabase.table("live_sessions").update({
            "viewer_count": current_viewers + 1
        }).eq("id", join_request.session_id).execute()
        
        # Generate WebRTC configuration
        # TODO: Integrate with LiveKit/Janus for actual WebRTC config
        webrtc_config = {
            "server_url": "wss://livekit.example.com",
            "room_name": session_data["id"],
            "participant_token": generate_access_token(),
            "ice_servers": [
                {"urls": "stun:stun.l.google.com:19302"}
            ]
        }
        
        user_data = session_data.get("users", {})
        live_session = LiveSession(
            id=session_data["id"],
            host_id=session_data["host_id"],
            host_username=user_data.get("username", ""),
            host_avatar_url=user_data.get("avatar_url"),
            title=session_data["title"],
            description=session_data.get("description"),
            session_type=session_data["session_type"],
            status=session_data["status"],
            thumbnail_url=session_data.get("thumbnail_url"),
            viewer_count=current_viewers + 1,
            max_participants=max_participants,
            started_at=session_data.get("started_at"),
            created_at=session_data["created_at"]
        )
        
        return LiveJoinResponse(
            session=live_session,
            access_token=session_data["access_token"],
            webrtc_config=webrtc_config
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to join live session: {str(e)}"
        )


@router.post("/{session_id}/end")
async def end_live_session(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """End a live session"""
    try:
        # Get session
        session = supabase.table("live_sessions").select("*").eq("id", session_id).single().execute()
        
        if not session.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Live session not found"
            )
        
        # Check if user is the host
        if session.data["host_id"] != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the host can end the session"
            )
        
        # Update session status
        db.update_live_session(session_id, {
            "status": LiveSessionStatus.ENDED,
            "ended_at": datetime.utcnow().isoformat()
        })
        
        return {"message": "Live session ended successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to end live session: {str(e)}"
        )


@router.get("/list", response_model=List[LiveSession])
async def list_active_sessions(status: str = "active"):
    """Get list of active live sessions"""
    sessions = db.get_live_sessions(status=status)
    
    result = []
    for session in sessions:
        user_data = session.get("users", {})
        result.append(LiveSession(
            id=session["id"],
            host_id=session["host_id"],
            host_username=user_data.get("username", ""),
            host_avatar_url=user_data.get("avatar_url"),
            title=session["title"],
            description=session.get("description"),
            session_type=session["session_type"],
            status=session["status"],
            thumbnail_url=session.get("thumbnail_url"),
            viewer_count=session.get("viewer_count", 0),
            max_participants=session.get("max_participants", 50),
            started_at=session.get("started_at"),
            ended_at=session.get("ended_at"),
            created_at=session["created_at"]
        ))
    
    return result


@router.get("/{session_id}", response_model=LiveSession)
async def get_session_details(session_id: str):
    """Get details of a specific live session"""
    try:
        session = supabase.table("live_sessions").select("""
            *,
            users!live_sessions_host_id_fkey (username, avatar_url)
        """).eq("id", session_id).single().execute()
        
        if not session.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Live session not found"
            )
        
        session_data = session.data
        user_data = session_data.get("users", {})
        
        return LiveSession(
            id=session_data["id"],
            host_id=session_data["host_id"],
            host_username=user_data.get("username", ""),
            host_avatar_url=user_data.get("avatar_url"),
            title=session_data["title"],
            description=session_data.get("description"),
            session_type=session_data["session_type"],
            status=session_data["status"],
            thumbnail_url=session_data.get("thumbnail_url"),
            viewer_count=session_data.get("viewer_count", 0),
            max_participants=session_data.get("max_participants", 50),
            started_at=session_data.get("started_at"),
            ended_at=session_data.get("ended_at"),
            created_at=session_data["created_at"]
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch session details: {str(e)}"
        )
