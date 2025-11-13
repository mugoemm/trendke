# Enhanced Live Streaming with Multi-Guest Support
## Better than TikTok Live! 🎥🚀

### Overview
This enhanced live streaming system provides enterprise-grade features that surpass TikTok Live, Instagram Live, and other platforms:

## 🌟 Key Features

### 1. **Multi-Guest Hosting (Up to 20 guests!)**
- **TikTok Live**: Limited to 1 guest
- **TrendKe**: Support for up to 20 simultaneous guests/co-hosts
- Perfect for:
  - Panel discussions
  - Q&A sessions
  - Group interviews
  - Multi-creator collaborations
  - Virtual events

### 2. **Advanced Guest Management**
- **Guest Request System**: Viewers can request to join as guests
- **Approval Workflow**: Host approves/rejects requests
- **Role Management**:
  - `host`: Session creator with full control
  - `cohost`: Co-host with moderator privileges
  - `guest`: Temporary participant
  - `viewer`: Audience member

### 3. **Granular Host Controls**
- **Individual Control**: Mute/unmute each participant
- **Camera Control**: Enable/disable video for guests
- **Screen Sharing**: Allow/disallow screen sharing
- **Kick/Remove**: Remove disruptive participants
- **Promote/Demote**: Elevate guests to co-hosts

### 4. **Real-Time Chat**
- Message history with pagination
- System messages for join/leave events
- Gift notifications in chat
- Slow mode support
- Chat filtering options

### 5. **Reactions & Engagement**
- Live reactions (❤️ 🔥 👏 😮 😢)
- Floating animations
- Gift sending during live
- Viewer count tracking
- Peak viewer statistics

### 6. **Session Types**
- **Voice Only**: Audio-only sessions (like Twitter Spaces)
- **Camera**: Video sessions
- **Studio**: Professional multi-camera setup

---

## 📊 Database Schema

### New Tables

#### 1. **live_participants**
Tracks all users in a live session with their roles and permissions.

```sql
- id: UUID
- session_id: References live_sessions
- user_id: References users
- role: host | cohost | guest | viewer
- status: active | muted | kicked | left
- audio_enabled: boolean
- video_enabled: boolean
- screen_sharing: boolean
- joined_at, left_at: timestamps
```

#### 2. **live_guest_requests**
Manages guest join requests.

```sql
- id: UUID
- session_id: References live_sessions
- user_id: References users
- request_type: guest | cohost
- status: pending | approved | rejected | cancelled
- message: Optional message from requester
- created_at, responded_at: timestamps
- responded_by: User who approved/rejected
```

#### 3. **live_chat_messages**
Stores chat messages.

```sql
- id: UUID
- session_id: References live_sessions
- user_id: References users
- message: text
- message_type: text | gift | system | sticker
- metadata: JSONB for extra data
- created_at: timestamp
```

#### 4. **live_session_settings**
Per-session configuration.

```sql
- session_id: UUID (PK)
- allow_guests: boolean
- require_approval: boolean
- max_guests: integer (1-20)
- enable_chat: boolean
- enable_gifts: boolean
- chat_slow_mode: integer (seconds)
- guest_audio_default: boolean
- guest_video_default: boolean
```

#### 5. **live_reactions**
Tracks real-time reactions.

```sql
- id: UUID
- session_id: References live_sessions
- user_id: References users
- reaction_type: heart | fire | clap | wow | sad
- created_at: timestamp
```

---

## 🔌 API Endpoints

### Session Management

#### `POST /live/start`
Start a new live session.

**Request:**
```json
{
  "title": "My Amazing Live Stream",
  "description": "Let's chat about tech!",
  "session_type": "camera",
  "max_participants": 100,
  "allow_guests": true,
  "require_approval": true,
  "max_guests": 8,
  "enable_chat": true,
  "enable_gifts": true,
  "guest_audio_default": true,
  "guest_video_default": true
}
```

**Response:**
```json
{
  "id": "uuid",
  "room_name": "live_abc123_xyz",
  "access_token": "secure_token",
  "host_username": "creator",
  "title": "My Amazing Live Stream",
  "viewer_count": 0,
  "guest_count": 0
}
```

#### `POST /live/join`
Join a live session as a viewer.

**Request:**
```json
{
  "session_id": "uuid"
}
```

**Response:**
```json
{
  "session_id": "uuid",
  "room_name": "live_abc123_xyz",
  "access_token": "token",
  "webrtc_config": {
    "server_url": "wss://live.trendke.com",
    "room_name": "live_abc123_xyz",
    "participant_token": "participant_token",
    "ice_servers": [...]
  },
  "role": "viewer",
  "can_request_guest": true
}
```

#### `POST /live/end/{session_id}`
End a live session (host only).

**Response:**
```json
{
  "message": "Live session ended successfully",
  "session_id": "uuid",
  "duration_seconds": 1234
}
```

### Guest Management

#### `POST /live/request-guest`
Request to join as a guest.

**Request:**
```json
{
  "session_id": "uuid",
  "request_type": "guest",
  "message": "Can I join to discuss this topic?"
}
```

#### `POST /live/respond-guest-request`
Approve/reject a guest request (host only).

**Request:**
```json
{
  "request_id": "uuid",
  "action": "approved"
}
```

#### `GET /live/guest-requests/{session_id}`
Get all pending guest requests (host only).

**Query Params:** `status=pending|approved|rejected`

#### `POST /live/manage-participant`
Control a participant (host only).

**Request:**
```json
{
  "session_id": "uuid",
  "user_id": "uuid",
  "action": "mute_audio"
}
```

**Actions:**
- `mute_audio` / `unmute_audio`
- `mute_video` / `unmute_video`
- `kick`
- `promote_cohost`
- `demote`

#### `GET /live/participants/{session_id}`
Get all active participants.

**Response:**
```json
[
  {
    "user_id": "uuid",
    "username": "user1",
    "avatar_url": "...",
    "role": "host",
    "status": "active",
    "audio_enabled": true,
    "video_enabled": true,
    "screen_sharing": false,
    "joined_at": "2025-11-10T..."
  }
]
```

### Chat

#### `POST /live/send-message`
Send a chat message.

**Request:**
```json
{
  "session_id": "uuid",
  "message": "Hello everyone!",
  "message_type": "text"
}
```

#### `GET /live/messages/{session_id}?limit=50&before=timestamp`
Get chat messages.

### Active Sessions

#### `GET /live/active?limit=20`
Get all active live sessions.

**Response:**
```json
[
  {
    "id": "uuid",
    "host_username": "creator",
    "title": "Live Stream",
    "viewer_count": 123,
    "guest_count": 3,
    "max_guests": 8,
    "allow_guests": true,
    "started_at": "..."
  }
]
```

#### `GET /live/session/{session_id}`
Get detailed session information.

### Reactions

#### `POST /live/react`
Send a reaction.

**Request:**
```json
{
  "session_id": "uuid",
  "reaction_type": "heart"
}
```

---

## 🎨 Frontend Integration Guide

### 1. **Setup Instructions**

```bash
# Install required packages
npm install socket.io-client simple-peer

# For WebRTC (use one of these)
npm install livekit-client  # Recommended
npm install agora-rtc-sdk-ng
npm install @daily-co/daily-js
```

### 2. **Basic Live Room Component Structure**

```jsx
import { useState, useEffect } from 'react';
import LiveKit from 'livekit-client';

const EnhancedLiveRoom = ({ sessionId }) => {
  const [participants, setParticipants] = useState([]);
  const [guestRequests, setGuestRequests] = useState([]);
  const [chatMessages, setChatMessages] = useState([]);
  const [isHost, setIsHost] = useState(false);
  
  // WebRTC room connection
  // Guest management UI
  // Chat interface
  // Reactions
  // Host controls
  
  return (
    <div className="live-room">
      {/* Main video grid */}
      {/* Guest requests panel */}
      {/* Chat sidebar */}
      {/* Controls bar */}
    </div>
  );
};
```

### 3. **WebRTC Integration Options**

#### Option A: LiveKit (Recommended)
```javascript
import { Room, RoomEvent } from 'livekit-client';

const room = new Room();
await room.connect(webrtcConfig.server_url, webrtcConfig.participant_token);

room.on(RoomEvent.TrackSubscribed, (track, publication, participant) => {
  // Render participant video/audio
});
```

#### Option B: Agora
```javascript
import AgoraRTC from 'agora-rtc-sdk-ng';

const client = AgoraRTC.createClient({ mode: 'rtc', codec: 'vp8' });
await client.join(appId, channelName, token);
```

#### Option C: Daily.co
```javascript
import Daily from '@daily-co/daily-js';

const callFrame = Daily.createFrame();
await callFrame.join({ url: roomUrl, token: token });
```

---

## 🚀 Deployment Setup

### 1. **Run SQL Schema**
```bash
# In Supabase SQL Editor, run:
psql < LIVE_MULTI_GUEST_SCHEMA.sql
```

### 2. **Update Backend**
```python
# In app/main.py, add:
from .live_enhanced import router as live_enhanced_router
app.include_router(live_enhanced_router)
```

### 3. **Environment Variables**
```env
# WebRTC Server (choose one)
LIVEKIT_API_KEY=your_key
LIVEKIT_API_SECRET=your_secret
LIVEKIT_URL=wss://your-project.livekit.cloud

# Or Agora
AGORA_APP_ID=your_app_id
AGORA_APP_CERTIFICATE=your_certificate

# Or Daily.co
DAILY_API_KEY=your_api_key
```

### 4. **Test Endpoints**
```bash
# Start a session
curl -X POST http://localhost:8001/live/start \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Live",
    "session_type": "camera",
    "allow_guests": true
  }'

# Get active sessions
curl http://localhost:8001/live/active
```

---

## 📱 Mobile App Support

### React Native
```javascript
import { RTCView } from 'react-native-webrtc';
// Same API endpoints work!
```

### Flutter
```dart
import 'package:livekit_client/livekit_client.dart';
// Compatible with backend API
```

---

## 🎯 Use Cases

1. **Podcast Recording**: Host + multiple guests discussion
2. **Panel Discussions**: 10+ experts on a topic
3. **Q&A Sessions**: Bring audience members on stage
4. **Virtual Events**: Multi-speaker conferences
5. **Collaborative Streaming**: Co-create content live
6. **Educational Webinars**: Teacher + student participants
7. **Gaming Tournaments**: Commentators + players

---

## 🔒 Security Features

- JWT authentication required
- Host-only actions verified
- Rate limiting on requests
- Participant validation
- Token expiration
- Row-level security (RLS) in database

---

## 📈 Analytics & Monitoring

Track in real-time:
- Peak viewers
- Average session duration
- Guest participation rate
- Chat activity
- Gift revenue
- Reaction engagement

---

## 🎁 Monetization Features

- Gifts during live streams
- Paid access sessions
- Subscription-only lives
- Tipping system
- Virtual items marketplace

---

## 🆚 Comparison with TikTok Live

| Feature | TikTok Live | TrendKe Live |
|---------|-------------|--------------|
| Max Guests | 1 | 20 |
| Guest Requests | ❌ | ✅ |
| Role Management | ❌ | ✅ (host/cohost/guest) |
| Individual Controls | ❌ | ✅ |
| Session Types | Video only | Voice/Video/Studio |
| Chat Features | Basic | Advanced + slow mode |
| Reactions | Basic | Rich reactions |
| Recording | ❌ | ✅ (optional) |
| Screen Sharing | ❌ | ✅ |
| Co-host Promotion | ❌ | ✅ |
| API Access | ❌ | ✅ Full REST API |

---

## 📝 Next Steps

1. ✅ Run the SQL schema in Supabase
2. ✅ Add enhanced live router to main app
3. ⏳ Implement frontend components
4. ⏳ Choose WebRTC provider (LiveKit/Agora/Daily)
5. ⏳ Test multi-guest scenarios
6. ⏳ Add analytics dashboard
7. ⏳ Deploy to production

---

## 🐛 Troubleshooting

### Issue: "Maximum guests reached"
**Solution**: Check `max_guests` in session settings, increase if needed.

### Issue: WebRTC connection fails
**Solution**: Verify ICE servers, check firewall, ensure HTTPS.

### Issue: Guest request not showing
**Solution**: Ensure WebSocket connection active, check RLS policies.

---

## 📚 Additional Resources

- [LiveKit Documentation](https://docs.livekit.io/)
- [Agora WebRTC Guide](https://docs.agora.io/)
- [WebRTC Best Practices](https://webrtc.org/getting-started/)
- [Supabase Realtime](https://supabase.com/docs/guides/realtime)

---

**Built with ❤️ for TrendKe - The Future of Social Live Streaming!**
