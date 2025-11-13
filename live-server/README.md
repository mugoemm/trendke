# TrendKe Live Streaming Server

This directory contains configuration and setup instructions for the WebRTC media server used for live streaming features.

## Supported Media Servers

TrendKe supports multiple WebRTC media server solutions. Choose one based on your needs:

### 1. LiveKit (Recommended for MVP)

**Pros:**
- Free tier available
- Easy to setup
- Great documentation
- Built-in recording
- Scalable

**Setup:**
1. Sign up at [LiveKit Cloud](https://livekit.io/)
2. Create a new project
3. Get your API key and secret
4. Update backend `.env` with:
   ```
   LIVEKIT_API_KEY=your_api_key
   LIVEKIT_API_SECRET=your_api_secret
   LIVEKIT_WS_URL=wss://your-project.livekit.cloud
   ```

**Documentation:** https://docs.livekit.io/

### 2. Janus Gateway (Self-hosted)

**Pros:**
- Open source and free
- Full control
- High performance

**Cons:**
- More complex setup
- Requires server infrastructure

**Setup:**
See `janus/` directory for Docker setup

### 3. Jitsi Meet (Open Source Alternative)

**Pros:**
- Completely free
- Easy to deploy
- Good for multi-party video

**Setup:**
See `jitsi/` directory for Docker setup

## Quick Start with LiveKit

### Backend Integration

```python
# In backend/app/live.py
import livekit
from livekit import api

# Generate participant token
def generate_livekit_token(room_name: str, participant_name: str):
    token = api.AccessToken(
        api_key=LIVEKIT_API_KEY,
        api_secret=LIVEKIT_API_SECRET
    )
    
    token.with_identity(participant_name).with_name(participant_name)
    token.with_grants(api.VideoGrants(
        room_join=True,
        room=room_name,
    ))
    
    return token.to_jwt()
```

### Frontend Integration

```javascript
// Already included in package.json
import { Room, RoomEvent } from 'livekit-client';

const room = new Room();
await room.connect(LIVEKIT_URL, token);
```

## Features Support

| Feature | LiveKit | Janus | Jitsi |
|---------|---------|-------|-------|
| Voice Only | ✅ | ✅ | ✅ |
| Camera | ✅ | ✅ | ✅ |
| Studio Mode | ✅ | ✅ | ✅ |
| Recording | ✅ | ⚠️ | ✅ |
| Screen Share | ✅ | ✅ | ✅ |
| Chat | ✅ | ❌ | ✅ |

## Deployment

### Development
- Use LiveKit Cloud free tier
- No additional setup needed

### Production
- **Option 1:** LiveKit Cloud (Paid tiers)
- **Option 2:** Self-host on Railway/Render
- **Option 3:** AWS/GCP with Docker

## Testing

Test live streaming locally:

1. Start backend: `cd backend && uvicorn app.main:app --reload`
2. Start frontend: `cd frontend && npm run dev`
3. Navigate to `/dashboard` and click "Start Live"
4. Open in another browser/incognito to join as viewer

## Troubleshooting

### Common Issues

1. **CORS errors:** Ensure backend allows frontend origin
2. **WebRTC connection fails:** Check STUN/TURN server configuration
3. **Audio/Video not working:** Browser permissions required

### Debug Mode

Enable debug logging in frontend:
```javascript
import { setLogLevel } from 'livekit-client';
setLogLevel('debug');
```

## Cost Estimates (Production)

### LiveKit Cloud
- Free: Up to 10,000 participant minutes/month
- Starter: $99/month - 100,000 participant minutes
- Growth: $299/month - 500,000 participant minutes

### Self-Hosted (Railway/Render)
- Server: ~$10-20/month
- Bandwidth: Pay as you go
- Recording storage: ~$0.02/GB

## Next Steps

1. Sign up for LiveKit Cloud
2. Configure environment variables
3. Test voice/camera/studio modes
4. Implement recording (optional)
5. Add chat overlay (using Supabase Realtime)
