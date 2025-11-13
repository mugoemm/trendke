"""
WebSocket Manager for Real-time Features
Handles connections, broadcasts, and room-based messaging
"""
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Set, List, Optional
import json
import asyncio
from datetime import datetime
import uuid

class ConnectionManager:
    def __init__(self):
        # Active connections: {user_id: {connection_id: WebSocket}}
        self.active_connections: Dict[str, Dict[str, WebSocket]] = {}
        
        # Room subscriptions: {room_name: Set[user_id]}
        self.rooms: Dict[str, Set[str]] = {}
        
        # Video viewers: {video_id: Set[user_id]}
        self.video_viewers: Dict[str, Set[str]] = {}
        
        # Live session connections: {session_id: {user_id: {websocket, role, username}}}
        self.live_sessions: Dict[str, Dict[str, dict]] = {}
        
        # WebRTC peer connections tracking
        self.webrtc_peers: Dict[str, Set[str]] = {}  # session_id: Set[user_ids]
        
    async def connect(self, websocket: WebSocket, user_id: str, connection_id: str = None):
        """Connect a new WebSocket client"""
        await websocket.accept()
        
        if connection_id is None:
            connection_id = str(uuid.uuid4())
        
        if user_id not in self.active_connections:
            self.active_connections[user_id] = {}
        
        self.active_connections[user_id][connection_id] = websocket
        
        # Send welcome message
        await self.send_personal_message(
            {
                "type": "connection_established",
                "message": "Connected to TrendKe WebSocket",
                "user_id": user_id,
                "connection_id": connection_id,
                "timestamp": datetime.now().isoformat()
            },
            user_id
        )
        
        print(f"✅ WebSocket connected: user={user_id}, connection={connection_id}")
        return connection_id
    
    def disconnect(self, user_id: str, connection_id: str):
        """Disconnect a WebSocket client"""
        if user_id in self.active_connections:
            if connection_id in self.active_connections[user_id]:
                del self.active_connections[user_id][connection_id]
                
            # Remove user if no more connections
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
                
                # Clean up room subscriptions
                for room_users in self.rooms.values():
                    room_users.discard(user_id)
                
                # Clean up video viewers
                for viewers in self.video_viewers.values():
                    viewers.discard(user_id)
        
        print(f"🔌 WebSocket disconnected: user={user_id}, connection={connection_id}")
    
    async def send_personal_message(self, message: dict, user_id: str):
        """Send message to specific user (all their connections)"""
        if user_id in self.active_connections:
            disconnected = []
            for connection_id, websocket in self.active_connections[user_id].items():
                try:
                    await websocket.send_json(message)
                except Exception as e:
                    print(f"⚠️  Failed to send to {user_id}/{connection_id}: {e}")
                    disconnected.append(connection_id)
            
            # Clean up disconnected
            for connection_id in disconnected:
                self.disconnect(user_id, connection_id)
    
    async def broadcast(self, message: dict, exclude_user: Optional[str] = None):
        """Broadcast message to all connected users"""
        for user_id in list(self.active_connections.keys()):
            if user_id != exclude_user:
                await self.send_personal_message(message, user_id)
    
    async def broadcast_to_room(self, room: str, message: dict, exclude_user: Optional[str] = None):
        """Broadcast message to all users in a room"""
        if room in self.rooms:
            for user_id in self.rooms[room]:
                if user_id != exclude_user:
                    await self.send_personal_message(message, user_id)
    
    def join_room(self, user_id: str, room: str):
        """Add user to a room"""
        if room not in self.rooms:
            self.rooms[room] = set()
        self.rooms[room].add(user_id)
        print(f"👥 User {user_id} joined room: {room}")
    
    def leave_room(self, user_id: str, room: str):
        """Remove user from a room"""
        if room in self.rooms:
            self.rooms[room].discard(user_id)
            if not self.rooms[room]:
                del self.rooms[room]
        print(f"👋 User {user_id} left room: {room}")
    
    async def join_video(self, user_id: str, video_id: str):
        """User starts watching a video"""
        if video_id not in self.video_viewers:
            self.video_viewers[video_id] = set()
        
        self.video_viewers[video_id].add(user_id)
        viewer_count = len(self.video_viewers[video_id])
        
        # Notify all viewers of updated count
        await self.broadcast_to_video(
            video_id,
            {
                "type": "viewer_update",
                "video_id": video_id,
                "viewer_count": viewer_count,
                "timestamp": datetime.now().isoformat()
            }
        )
        
        print(f"📺 User {user_id} watching video {video_id} ({viewer_count} viewers)")
    
    async def leave_video(self, user_id: str, video_id: str):
        """User stops watching a video"""
        if video_id in self.video_viewers:
            self.video_viewers[video_id].discard(user_id)
            viewer_count = len(self.video_viewers[video_id])
            
            if viewer_count == 0:
                del self.video_viewers[video_id]
            else:
                # Notify remaining viewers
                await self.broadcast_to_video(
                    video_id,
                    {
                        "type": "viewer_update",
                        "video_id": video_id,
                        "viewer_count": viewer_count,
                        "timestamp": datetime.now().isoformat()
                    }
                )
        
        print(f"📺 User {user_id} stopped watching video {video_id}")
    
    async def broadcast_to_video(self, video_id: str, message: dict):
        """Send message to all users watching a video"""
        if video_id in self.video_viewers:
            for user_id in self.video_viewers[video_id]:
                await self.send_personal_message(message, user_id)
    
    def get_online_users(self) -> List[str]:
        """Get list of all connected user IDs"""
        return list(self.active_connections.keys())
    
    def get_room_users(self, room: str) -> List[str]:
        """Get list of users in a room"""
        return list(self.rooms.get(room, set()))
    
    def get_video_viewers(self, video_id: str) -> int:
        """Get count of users watching a video"""
        return len(self.video_viewers.get(video_id, set()))
    
    async def send_notification(self, user_id: str, notification_type: str, data: dict):
        """Send notification to specific user"""
        message = {
            "type": "notification",
            "notification_type": notification_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        await self.send_personal_message(message, user_id)


# Global WebSocket manager instance
ws_manager = ConnectionManager()


# Notification helper functions
async def notify_new_follower(user_id: str, follower_username: str, follower_avatar: str = None):
    """Notify user of new follower"""
    await ws_manager.send_notification(
        user_id,
        "new_follower",
        {
            "message": f"{follower_username} started following you",
            "follower_username": follower_username,
            "follower_avatar": follower_avatar
        }
    )


async def notify_new_like(user_id: str, video_id: str, liker_username: str, video_title: str):
    """Notify user of new like on their video"""
    await ws_manager.send_notification(
        user_id,
        "new_like",
        {
            "message": f"{liker_username} liked your video: {video_title}",
            "video_id": video_id,
            "liker_username": liker_username,
            "video_title": video_title
        }
    )


async def notify_new_comment(user_id: str, video_id: str, commenter_username: str, comment: str, video_title: str):
    """Notify user of new comment on their video"""
    await ws_manager.send_notification(
        user_id,
        "new_comment",
        {
            "message": f"{commenter_username} commented: {comment[:50]}...",
            "video_id": video_id,
            "commenter_username": commenter_username,
            "comment": comment,
            "video_title": video_title
        }
    )


async def broadcast_new_video(uploader_id: str, uploader_username: str, video_id: str, video_title: str, thumbnail_url: str):
    """Broadcast new video upload to all users"""
    await ws_manager.broadcast(
        {
            "type": "new_video",
            "uploader_id": uploader_id,
            "uploader_username": uploader_username,
            "video_id": video_id,
            "video_title": video_title,
            "thumbnail_url": thumbnail_url,
            "timestamp": datetime.now().isoformat()
        },
        exclude_user=uploader_id
    )


async def broadcast_trending_update(video_ids: List[str]):
    """Notify all users of trending videos update"""
    await ws_manager.broadcast(
        {
            "type": "trending_update",
            "message": "Trending videos updated!",
            "video_ids": video_ids,
            "timestamp": datetime.now().isoformat()
        }
    )


# ============================================================================
# LIVE STREAMING REAL-TIME FEATURES
# ============================================================================

class LiveStreamManager:
    """Enhanced manager for live streaming with WebRTC signaling"""
    
    def __init__(self, connection_manager: ConnectionManager):
        self.manager = connection_manager
    
    async def join_live_session(self, websocket: WebSocket, session_id: str, user_id: str, username: str, role: str = "viewer"):
        """Join a live streaming session (connection already accepted in route handler)"""
        
        # Initialize session if not exists
        if session_id not in self.manager.live_sessions:
            self.manager.live_sessions[session_id] = {}
        
        # Store user info
        self.manager.live_sessions[session_id][user_id] = {
            "websocket": websocket,
            "role": role,
            "username": username,
            "connected_at": datetime.now().isoformat(),
            "audio_enabled": True,
            "video_enabled": role != "viewer"  # Viewers don't have video by default
        }
        
        # Add to WebRTC peers if not viewer
        if role != "viewer":
            if session_id not in self.manager.webrtc_peers:
                self.manager.webrtc_peers[session_id] = set()
            self.manager.webrtc_peers[session_id].add(user_id)
        
        viewer_count = len(self.manager.live_sessions[session_id])
        
        # Notify existing users about new participant
        await self.broadcast_to_session(session_id, {
            "type": "user_joined",
            "user_id": user_id,
            "username": username,
            "role": role,
            "viewer_count": viewer_count,
            "timestamp": datetime.now().isoformat()
        }, exclude_user=user_id)
        
        # Send current participants to new user
        participants = []
        for uid, info in self.manager.live_sessions[session_id].items():
            if uid != user_id:
                participants.append({
                    "user_id": uid,
                    "username": info["username"],
                    "role": info["role"],
                    "audio_enabled": info["audio_enabled"],
                    "video_enabled": info["video_enabled"]
                })
        
        await websocket.send_json({
            "type": "current_participants",
            "participants": participants,
            "viewer_count": viewer_count,
            "timestamp": datetime.now().isoformat()
        })
        
        print(f"✅ User {username} joined live session {session_id} as {role}")
        return viewer_count
    
    def leave_live_session(self, session_id: str, user_id: str):
        """Leave a live streaming session"""
        if session_id in self.manager.live_sessions:
            user_info = self.manager.live_sessions[session_id].pop(user_id, None)
            
            # Remove from WebRTC peers
            if session_id in self.manager.webrtc_peers:
                self.manager.webrtc_peers[session_id].discard(user_id)
            
            if user_info:
                viewer_count = len(self.manager.live_sessions[session_id])
                
                # Notify remaining users
                asyncio.create_task(self.broadcast_to_session(session_id, {
                    "type": "user_left",
                    "user_id": user_id,
                    "username": user_info["username"],
                    "viewer_count": viewer_count,
                    "timestamp": datetime.now().isoformat()
                }))
                
                print(f"👋 User {user_info['username']} left live session {session_id}")
            
            # Clean up empty session
            if not self.manager.live_sessions[session_id]:
                del self.manager.live_sessions[session_id]
                if session_id in self.manager.webrtc_peers:
                    del self.manager.webrtc_peers[session_id]
    
    async def broadcast_to_session(self, session_id: str, message: dict, exclude_user: str = None):
        """Broadcast message to all users in a live session"""
        if session_id not in self.manager.live_sessions:
            return
        
        disconnected = []
        for user_id, info in self.manager.live_sessions[session_id].items():
            if user_id == exclude_user:
                continue
            
            try:
                await info["websocket"].send_json(message)
            except Exception as e:
                print(f"⚠️  Failed to send to {user_id} in session {session_id}: {e}")
                disconnected.append(user_id)
        
        # Clean up disconnected users
        for user_id in disconnected:
            self.leave_live_session(session_id, user_id)
    
    async def send_to_user(self, session_id: str, user_id: str, message: dict):
        """Send message to specific user in session"""
        if session_id in self.manager.live_sessions and user_id in self.manager.live_sessions[session_id]:
            try:
                await self.manager.live_sessions[session_id][user_id]["websocket"].send_json(message)
            except Exception as e:
                print(f"⚠️  Failed to send to user {user_id}: {e}")
                self.leave_live_session(session_id, user_id)
    
    async def send_to_role(self, session_id: str, role: str, message: dict):
        """Send message to all users with specific role"""
        if session_id not in self.manager.live_sessions:
            return
        
        for user_id, info in self.manager.live_sessions[session_id].items():
            if info["role"] == role:
                await self.send_to_user(session_id, user_id, message)
    
    async def handle_chat_message(self, session_id: str, user_id: str, message: str):
        """Handle chat message in live session"""
        if session_id not in self.manager.live_sessions or user_id not in self.manager.live_sessions[session_id]:
            return
        
        user_info = self.manager.live_sessions[session_id][user_id]
        
        await self.broadcast_to_session(session_id, {
            "type": "chat_message",
            "user_id": user_id,
            "username": user_info["username"],
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
        
        print(f"💬 Chat in {session_id}: {user_info['username']}: {message}")
    
    async def handle_reaction(self, session_id: str, user_id: str, reaction: str):
        """Handle reaction in live session"""
        if session_id not in self.manager.live_sessions or user_id not in self.manager.live_sessions[session_id]:
            return
        
        user_info = self.manager.live_sessions[session_id][user_id]
        
        await self.broadcast_to_session(session_id, {
            "type": "reaction",
            "user_id": user_id,
            "username": user_info["username"],
            "reaction": reaction,
            "timestamp": datetime.now().isoformat()
        })
        
        print(f"💖 Reaction in {session_id}: {user_info['username']} sent {reaction}")
    
    async def handle_guest_request(self, session_id: str, user_id: str):
        """Handle guest join request"""
        if session_id not in self.manager.live_sessions or user_id not in self.manager.live_sessions[session_id]:
            return
        
        user_info = self.manager.live_sessions[session_id][user_id]
        
        # Send to host and cohosts only
        await self.send_to_role(session_id, "host", {
            "type": "guest_request",
            "user_id": user_id,
            "username": user_info["username"],
            "timestamp": datetime.now().isoformat()
        })
        
        await self.send_to_role(session_id, "cohost", {
            "type": "guest_request",
            "user_id": user_id,
            "username": user_info["username"],
            "timestamp": datetime.now().isoformat()
        })
        
        print(f"🙋 Guest request in {session_id}: {user_info['username']}")
    
    async def handle_guest_response(self, session_id: str, user_id: str, approved: bool, approved_by_id: str):
        """Handle guest request response"""
        if session_id not in self.manager.live_sessions:
            return
        
        approver_info = self.manager.live_sessions[session_id].get(approved_by_id)
        if not approver_info:
            return
        
        if approved:
            # Update user role to guest
            if user_id in self.manager.live_sessions[session_id]:
                self.manager.live_sessions[session_id][user_id]["role"] = "guest"
                self.manager.live_sessions[session_id][user_id]["video_enabled"] = True
                
                # Add to WebRTC peers
                if session_id not in self.manager.webrtc_peers:
                    self.manager.webrtc_peers[session_id] = set()
                self.manager.webrtc_peers[session_id].add(user_id)
                
                # Notify the approved user
                await self.send_to_user(session_id, user_id, {
                    "type": "guest_approved",
                    "approved_by": approver_info["username"],
                    "timestamp": datetime.now().isoformat()
                })
                
                # Broadcast to everyone
                await self.broadcast_to_session(session_id, {
                    "type": "guest_joined",
                    "user_id": user_id,
                    "username": self.manager.live_sessions[session_id][user_id]["username"],
                    "timestamp": datetime.now().isoformat()
                })
                
                print(f"✅ Guest approved in {session_id}: {user_id}")
        else:
            # Notify rejection
            await self.send_to_user(session_id, user_id, {
                "type": "guest_rejected",
                "rejected_by": approver_info["username"],
                "timestamp": datetime.now().isoformat()
            })
            
            print(f"❌ Guest rejected in {session_id}: {user_id}")
    
    async def handle_participant_action(self, session_id: str, target_user_id: str, action: str, by_user_id: str, **kwargs):
        """Handle host actions on participants (mute, kick, promote, etc.)"""
        if session_id not in self.manager.live_sessions:
            return
        
        by_user_info = self.manager.live_sessions[session_id].get(by_user_id)
        if not by_user_info or by_user_info["role"] not in ["host", "cohost"]:
            return  # Only host/cohost can perform actions
        
        if action == "mute_audio":
            if target_user_id in self.manager.live_sessions[session_id]:
                self.manager.live_sessions[session_id][target_user_id]["audio_enabled"] = False
                
                await self.send_to_user(session_id, target_user_id, {
                    "type": "force_mute_audio",
                    "by": by_user_info["username"],
                    "timestamp": datetime.now().isoformat()
                })
                
                await self.broadcast_to_session(session_id, {
                    "type": "participant_audio_changed",
                    "user_id": target_user_id,
                    "audio_enabled": False
                })
        
        elif action == "mute_video":
            if target_user_id in self.manager.live_sessions[session_id]:
                self.manager.live_sessions[session_id][target_user_id]["video_enabled"] = False
                
                await self.send_to_user(session_id, target_user_id, {
                    "type": "force_mute_video",
                    "by": by_user_info["username"],
                    "timestamp": datetime.now().isoformat()
                })
                
                await self.broadcast_to_session(session_id, {
                    "type": "participant_video_changed",
                    "user_id": target_user_id,
                    "video_enabled": False
                })
        
        elif action == "kick":
            if target_user_id in self.manager.live_sessions[session_id]:
                await self.send_to_user(session_id, target_user_id, {
                    "type": "kicked",
                    "by": by_user_info["username"],
                    "reason": kwargs.get("reason", "Removed by host"),
                    "timestamp": datetime.now().isoformat()
                })
                
                # Close their connection
                try:
                    await self.manager.live_sessions[session_id][target_user_id]["websocket"].close()
                except:
                    pass
                
                self.leave_live_session(session_id, target_user_id)
                
                print(f"👢 User {target_user_id} kicked from {session_id} by {by_user_info['username']}")
        
        elif action == "promote":
            new_role = kwargs.get("new_role", "cohost")
            if target_user_id in self.manager.live_sessions[session_id]:
                self.manager.live_sessions[session_id][target_user_id]["role"] = new_role
                
                await self.send_to_user(session_id, target_user_id, {
                    "type": "promoted",
                    "new_role": new_role,
                    "by": by_user_info["username"],
                    "timestamp": datetime.now().isoformat()
                })
                
                await self.broadcast_to_session(session_id, {
                    "type": "participant_role_changed",
                    "user_id": target_user_id,
                    "new_role": new_role
                })
                
                print(f"⬆️ User {target_user_id} promoted to {new_role} in {session_id}")
    
    async def handle_webrtc_signal(self, session_id: str, from_user_id: str, to_user_id: str, signal_type: str, signal_data: dict):
        """Handle WebRTC signaling (offer, answer, ICE candidates)"""
        if session_id not in self.manager.live_sessions:
            return
        
        signal_message = {
            "type": "webrtc_signal",
            "signal_type": signal_type,  # "offer", "answer", "ice_candidate"
            "from_user_id": from_user_id,
            "signal_data": signal_data,
            "timestamp": datetime.now().isoformat()
        }
        
        if to_user_id == "all":
            # Broadcast to all WebRTC peers (mesh topology)
            await self.broadcast_to_session(session_id, signal_message, exclude_user=from_user_id)
        else:
            # Send to specific user (SFU or P2P)
            await self.send_to_user(session_id, to_user_id, signal_message)
        
        print(f"📡 WebRTC {signal_type} from {from_user_id} to {to_user_id} in {session_id}")
    
    async def handle_session_ended(self, session_id: str):
        """End live session and notify all users"""
        if session_id not in self.manager.live_sessions:
            return
        
        await self.broadcast_to_session(session_id, {
            "type": "session_ended",
            "message": "The live session has ended",
            "timestamp": datetime.now().isoformat()
        })
        
        # Close all connections
        for user_id in list(self.manager.live_sessions[session_id].keys()):
            try:
                await self.manager.live_sessions[session_id][user_id]["websocket"].close()
            except:
                pass
            self.leave_live_session(session_id, user_id)
        
        print(f"🛑 Live session ended: {session_id}")
    
    def get_session_viewer_count(self, session_id: str) -> int:
        """Get number of viewers in session"""
        return len(self.manager.live_sessions.get(session_id, {}))
    
    def get_session_participants(self, session_id: str) -> List[dict]:
        """Get all participants in session"""
        if session_id not in self.manager.live_sessions:
            return []
        
        participants = []
        for user_id, info in self.manager.live_sessions[session_id].items():
            participants.append({
                "user_id": user_id,
                "username": info["username"],
                "role": info["role"],
                "audio_enabled": info["audio_enabled"],
                "video_enabled": info["video_enabled"],
                "connected_at": info["connected_at"]
            })
        
        return participants


# Global live stream manager
live_manager = LiveStreamManager(ws_manager)
