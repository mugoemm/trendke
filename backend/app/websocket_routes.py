"""
WebSocket Routes for Real-time Features
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from typing import Optional
import json
from datetime import datetime

from .websocket_manager import ws_manager, live_manager
from .auth import verify_token

router = APIRouter(prefix="/ws", tags=["WebSocket"])


# Test endpoint to verify route is reachable
@router.get("/live/{session_id}/test")
async def test_live_route(session_id: str):
    """Test endpoint to verify the route is working"""
    return {"status": "ok", "session_id": session_id, "message": "Route is working"}


# Simple test WebSocket without authentication
@router.websocket("/test")
async def test_websocket(websocket: WebSocket):
    """Simple test WebSocket to verify WebSocket works at all"""
    print("\n🧪 TEST WebSocket connection attempt")
    await websocket.accept()
    print("🧪 TEST WebSocket accepted")
    await websocket.send_json({"type": "test", "message": "Test WebSocket works!"})
    print("🧪 TEST Message sent")
    
    try:
        while True:
            data = await websocket.receive_text()
            print(f"🧪 TEST Received: {data}")
            await websocket.send_json({"type": "echo", "data": data})
    except WebSocketDisconnect:
        print("🧪 TEST WebSocket disconnected")


@router.websocket("/connect")
async def websocket_endpoint(
    websocket: WebSocket,
    token: Optional[str] = Query(None)
):
    """
    Main WebSocket endpoint for real-time features
    
    Usage:
    ws://localhost:8000/ws/connect?token=YOUR_JWT_TOKEN
    
    Message Types:
    - join_room: {"action": "join_room", "room": "room_name"}
    - leave_room: {"action": "leave_room", "room": "room_name"}
    - join_video: {"action": "join_video", "video_id": "video_123"}
    - leave_video: {"action": "leave_video", "video_id": "video_123"}
    - ping: {"action": "ping"}
    """
    
    # Authenticate user
    try:
        if not token:
            await websocket.close(code=1008, reason="Missing authentication token")
            return
        
        # Verify JWT token
        from .auth import verify_token
        payload = verify_token(token)
        user_id = payload.get("sub")
        
        if not user_id:
            await websocket.close(code=1008, reason="Invalid token")
            return
        
    except Exception as e:
        await websocket.close(code=1008, reason=f"Authentication failed: {str(e)}")
        return
    
    # Connect WebSocket
    connection_id = await ws_manager.connect(websocket, user_id)
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_text()
            message = json.loads(data)
            
            action = message.get("action")
            
            # Handle different actions
            if action == "ping":
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                })
            
            elif action == "join_room":
                room = message.get("room")
                if room:
                    ws_manager.join_room(user_id, room)
                    await websocket.send_json({
                        "type": "room_joined",
                        "room": room,
                        "timestamp": datetime.now().isoformat()
                    })
            
            elif action == "leave_room":
                room = message.get("room")
                if room:
                    ws_manager.leave_room(user_id, room)
                    await websocket.send_json({
                        "type": "room_left",
                        "room": room,
                        "timestamp": datetime.now().isoformat()
                    })
            
            elif action == "join_video":
                video_id = message.get("video_id")
                if video_id:
                    await ws_manager.join_video(user_id, video_id)
            
            elif action == "leave_video":
                video_id = message.get("video_id")
                if video_id:
                    await ws_manager.leave_video(user_id, video_id)
            
            elif action == "chat_message":
                # Room-based chat
                room = message.get("room")
                text = message.get("message")
                if room and text:
                    await ws_manager.broadcast_to_room(
                        room,
                        {
                            "type": "chat_message",
                            "room": room,
                            "user_id": user_id,
                            "message": text,
                            "timestamp": datetime.now().isoformat()
                        }
                    )
            
            else:
                await websocket.send_json({
                    "type": "error",
                    "message": f"Unknown action: {action}",
                    "timestamp": datetime.now().isoformat()
                })
    
    except WebSocketDisconnect:
        ws_manager.disconnect(user_id, connection_id)
        print(f"🔌 Client disconnected: {user_id}")
    
    except Exception as e:
        print(f"❌ WebSocket error for {user_id}: {e}")
        ws_manager.disconnect(user_id, connection_id)


@router.get("/stats")
async def get_websocket_stats():
    """Get WebSocket connection statistics"""
    online_users = ws_manager.get_online_users()
    
    return {
        "status": "success",
        "stats": {
            "online_users": len(online_users),
            "active_rooms": len(ws_manager.rooms),
            "videos_being_watched": len(ws_manager.video_viewers),
            "total_connections": sum(len(conns) for conns in ws_manager.active_connections.values())
        },
        "online_user_ids": online_users,
        "rooms": {room: len(users) for room, users in ws_manager.rooms.items()},
        "video_viewers": {video: len(users) for video, users in ws_manager.video_viewers.items()}
    }


@router.get("/room/{room_name}/users")
async def get_room_users(room_name: str):
    """Get list of users in a room"""
    users = ws_manager.get_room_users(room_name)
    
    return {
        "status": "success",
        "room": room_name,
        "user_count": len(users),
        "users": users
    }


@router.get("/video/{video_id}/viewers")
async def get_video_viewers(video_id: str):
    """Get viewer count for a video"""
    viewer_count = ws_manager.get_video_viewers(video_id)
    
    return {
        "status": "success",
        "video_id": video_id,
        "viewer_count": viewer_count
    }


# ============================================================================
# LIVE STREAMING WEBSOCKET
# ============================================================================

@router.websocket("/live/{session_id}")
async def live_stream_websocket(
    websocket: WebSocket,
    session_id: str,
    token: Optional[str] = Query(None),
    username: Optional[str] = Query(None)
):
    """
    WebSocket endpoint for live streaming sessions
    
    Usage:
    ws://localhost:8001/ws/live/SESSION_ID?token=JWT_TOKEN&username=USERNAME
    
    Features:
    - Real-time participant updates
    - Live chat messages
    - Reactions (❤️🔥👏😮)
    - Guest request system
    - WebRTC signaling
    - Host controls (mute, kick, promote)
    
    Message Types:
    {
        "action": "chat",
        "message": "Hello everyone!"
    }
    
    {
        "action": "reaction",
        "reaction": "❤️"  // ❤️, 🔥, 👏, 😮
    }
    
    {
        "action": "request_guest"
    }
    
    {
        "action": "respond_guest",
        "target_user_id": "user_123",
        "approved": true
    }
    
    {
        "action": "participant_action",
        "target_user_id": "user_123",
        "action_type": "mute_audio"  // mute_audio, mute_video, kick, promote
    }
    
    {
        "action": "webrtc_signal",
        "to_user_id": "user_123",  // or "all" for broadcast
        "signal_type": "offer",  // offer, answer, ice_candidate
        "signal_data": {...}
    }
    
    {
        "action": "ping"
    }
    """
    
    try:
        print(f"\n🔵 WebSocket connection attempt to session: {session_id}")
        print(f"   Token provided: {bool(token)}")
        print(f"   Username: {username}")
        
        # ACCEPT CONNECTION FIRST
        await websocket.accept()
        print(f"✅ WebSocket accepted")
        
        # Authenticate user
        try:
            if not token:
                print(f"❌ No token provided")
                await websocket.close(code=1008, reason="Missing authentication token")
                return
            
            payload = verify_token(token)
            user_id = payload.get("sub")
            print(f"✅ Token verified, user_id: {user_id}")
            
            if not user_id or not username:
                print(f"❌ Invalid credentials - user_id: {user_id}, username: {username}")
                await websocket.close(code=1008, reason="Invalid credentials")
                return
        
        except Exception as e:
            print(f"❌ Authentication failed: {e}")
            await websocket.close(code=1008, reason=f"Authentication failed: {str(e)}")
            return
    
    except Exception as outer_error:
        print(f"❌❌❌ CRITICAL ERROR in WebSocket handler: {outer_error}")
        import traceback
        traceback.print_exc()
        return
    
    # Check if user is host
    # For now, we'll determine role based on session data
    # In production, query the database
    role = "viewer"  # Default role
    
    # Connect to live session
    try:
        viewer_count = await live_manager.join_live_session(
            websocket, session_id, user_id, username, role
        )
        
        print(f"✅ {username} connected to live session {session_id} ({viewer_count} viewers)")
        
    except Exception as e:
        print(f"❌ Failed to join session: {e}")
        await websocket.close(code=1011, reason=str(e))
        return
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_text()
            message = json.loads(data)
            
            action = message.get("action")
            
            if action == "ping":
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                })
            
            elif action == "chat":
                text = message.get("message", "")
                if text:
                    await live_manager.handle_chat_message(session_id, user_id, text)
            
            elif action == "reaction":
                reaction = message.get("reaction", "❤️")
                await live_manager.handle_reaction(session_id, user_id, reaction)
            
            elif action == "request_guest":
                await live_manager.handle_guest_request(session_id, user_id)
            
            elif action == "respond_guest":
                target_user_id = message.get("target_user_id")
                approved = message.get("approved", False)
                if target_user_id:
                    await live_manager.handle_guest_response(
                        session_id, target_user_id, approved, user_id
                    )
            
            elif action == "participant_action":
                target_user_id = message.get("target_user_id")
                action_type = message.get("action_type")
                if target_user_id and action_type:
                    await live_manager.handle_participant_action(
                        session_id, target_user_id, action_type, user_id, **message
                    )
            
            elif action == "webrtc_signal":
                to_user_id = message.get("to_user_id", "all")
                signal_type = message.get("signal_type")
                signal_data = message.get("signal_data", {})
                
                await live_manager.handle_webrtc_signal(
                    session_id, user_id, to_user_id, signal_type, signal_data
                )
            
            elif action == "update_media_status":
                # Update user's media status (audio/video enabled)
                audio_enabled = message.get("audio_enabled")
                video_enabled = message.get("video_enabled")
                
                if session_id in live_manager.manager.live_sessions:
                    if user_id in live_manager.manager.live_sessions[session_id]:
                        if audio_enabled is not None:
                            live_manager.manager.live_sessions[session_id][user_id]["audio_enabled"] = audio_enabled
                        if video_enabled is not None:
                            live_manager.manager.live_sessions[session_id][user_id]["video_enabled"] = video_enabled
                        
                        # Broadcast status change
                        await live_manager.broadcast_to_session(session_id, {
                            "type": "participant_media_changed",
                            "user_id": user_id,
                            "audio_enabled": audio_enabled,
                            "video_enabled": video_enabled
                        })
            
            else:
                await websocket.send_json({
                    "type": "error",
                    "message": f"Unknown action: {action}",
                    "timestamp": datetime.now().isoformat()
                })
    
    except WebSocketDisconnect:
        live_manager.leave_live_session(session_id, user_id)
        print(f"🔌 {username} disconnected from live session {session_id}")
    
    except Exception as e:
        print(f"❌ WebSocket error for {username} in session {session_id}: {e}")
        live_manager.leave_live_session(session_id, user_id)


@router.get("/live/{session_id}/stats")
async def get_live_session_stats(session_id: str):
    """Get live session statistics"""
    viewer_count = live_manager.get_session_viewer_count(session_id)
    participants = live_manager.get_session_participants(session_id)
    
    return {
        "status": "success",
        "session_id": session_id,
        "viewer_count": viewer_count,
        "participants": participants
    }


@router.post("/live/{session_id}/end")
async def end_live_session(session_id: str):
    """End live session and disconnect all users"""
    await live_manager.handle_session_ended(session_id)
    
    return {
        "status": "success",
        "message": "Live session ended",
        "session_id": session_id
    }
