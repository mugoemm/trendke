# 🚀 Quick Start - Enhanced Live Streaming Testing

## 1️⃣ Apply Database Schema (DO THIS FIRST!)

### Option A: Supabase Dashboard (Easiest) ⭐
1. Go to https://supabase.com/dashboard
2. Select your TrendKe project
3. Click **"SQL Editor"** in the left sidebar
4. Click **"New query"** button
5. Open `backend/LIVE_MULTI_GUEST_SCHEMA.sql` in a text editor
6. Copy ALL the SQL content
7. Paste into the Supabase SQL editor
8. Click **"Run"** button (or press Ctrl+Enter)
9. Wait for success message ✅

### Verify Tables Created:
```sql
-- Run this in SQL Editor to verify
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name LIKE 'live_%'
ORDER BY table_name;

-- Expected output (6 tables):
-- live_chat_messages
-- live_guest_requests
-- live_participants
-- live_reactions
-- live_session_settings
-- live_sessions (already existed)
```

---

## 2️⃣ Test Backend API

### Start the Backend Server:
```powershell
cd backend
uvicorn app.main:app --reload --port 8001
```

### Open API Documentation:
**Browser**: http://localhost:8001/docs

You should see new endpoints:
- `POST /live/start` - Start live session
- `POST /live/join` - Join as viewer
- `POST /live/request-guest` - Request to be guest
- `POST /live/respond-guest-request` - Approve/reject request
- `POST /live/manage-participant` - Control participants
- `GET /live/participants/{session_id}` - Get all participants
- `POST /live/send-message` - Send chat message
- `GET /live/messages/{session_id}` - Get chat history
- `GET /live/guest-requests/{session_id}` - View requests
- `GET /live/active` - List active sessions
- `GET /live/session/{session_id}` - Get session details
- `POST /live/react` - Send reaction
- `POST /live/end/{session_id}` - End session

---

## 3️⃣ Quick API Test (Without Frontend)

### Step 1: Login to Get Token
```bash
# Using curl (PowerShell)
$response = Invoke-RestMethod -Uri "http://localhost:8001/auth/login" -Method POST -ContentType "application/json" -Body '{"username":"your_username","password":"your_password"}'
$token = $response.access_token
```

### Step 2: Start a Live Session
```bash
$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}

$body = @{
    title = "Test Multi-Guest Stream"
    description = "Testing the new system"
    session_type = "camera"
    max_participants = 100
    allow_guests = $true
    require_approval = $true
    max_guests = 10
    enable_chat = $true
    enable_gifts = $true
    guest_audio_default = $true
    guest_video_default = $true
} | ConvertTo-Json

$session = Invoke-RestMethod -Uri "http://localhost:8001/live/start" -Method POST -Headers $headers -Body $body
$sessionId = $session.id

Write-Host "Session started! ID: $sessionId"
```

### Step 3: Get Active Sessions (No Auth Needed)
```bash
Invoke-RestMethod -Uri "http://localhost:8001/live/active" -Method GET
```

### Step 4: Join as Viewer (Different User)
```bash
# Login as another user first, then:
$joinBody = @{
    session_id = $sessionId
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8001/live/join" -Method POST -Headers $headers -Body $joinBody
```

### Step 5: Request to Be Guest
```bash
$requestBody = @{
    session_id = $sessionId
    request_type = "guest"
    message = "Can I join?"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8001/live/request-guest" -Method POST -Headers $headers -Body $requestBody
```

### Step 6: Get Pending Requests (As Host)
```bash
Invoke-RestMethod -Uri "http://localhost:8001/live/guest-requests/$sessionId?status=pending" -Method GET -Headers $headers
```

### Step 7: Approve Request (As Host)
```bash
$approveBody = @{
    request_id = "REQUEST_ID_FROM_STEP_6"
    action = "approved"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8001/live/respond-guest-request" -Method POST -Headers $headers -Body $approveBody
```

### Step 8: Send Chat Message
```bash
$chatBody = @{
    session_id = $sessionId
    message = "Hello everyone!"
    message_type = "text"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8001/live/send-message" -Method POST -Headers $headers -Body $chatBody
```

### Step 9: Send Reaction
```bash
$reactionBody = @{
    session_id = $sessionId
    reaction_type = "heart"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8001/live/react" -Method POST -Headers $headers -Body $reactionBody
```

### Step 10: End Session (As Host)
```bash
Invoke-RestMethod -Uri "http://localhost:8001/live/end/$sessionId" -Method POST -Headers $headers
```

---

## 4️⃣ Test with Swagger UI (Easier!)

1. Go to http://localhost:8001/docs
2. Click **"Authorize"** button (top right)
3. Enter your JWT token (from login)
4. Click **"Authorize"**
5. Now you can test all endpoints by clicking "Try it out"

### Recommended Test Flow:
1. **POST /live/start** - Create a session
2. **GET /live/active** - Verify it appears
3. **POST /live/join** - Join as viewer
4. **POST /live/request-guest** - Request guest access
5. **GET /live/guest-requests/{session_id}** - See pending requests
6. **POST /live/respond-guest-request** - Approve request
7. **GET /live/participants/{session_id}** - See all participants
8. **POST /live/send-message** - Send chat
9. **GET /live/messages/{session_id}** - Read chat
10. **POST /live/react** - Send reaction
11. **POST /live/end/{session_id}** - End session

---

## 5️⃣ Check Database Records

### In Supabase SQL Editor:
```sql
-- View active sessions
SELECT * FROM live_sessions WHERE is_active = true;

-- View participants
SELECT * FROM live_participants ORDER BY joined_at DESC LIMIT 10;

-- View guest requests
SELECT * FROM live_guest_requests ORDER BY created_at DESC LIMIT 10;

-- View chat messages
SELECT * FROM live_chat_messages ORDER BY created_at DESC LIMIT 20;

-- View reactions
SELECT * FROM live_reactions ORDER BY created_at DESC LIMIT 50;

-- View session settings
SELECT * FROM live_session_settings;
```

---

## 6️⃣ Common Issues & Solutions

### Issue: "Table does not exist"
**Solution**: Run the SQL schema from Step 1

### Issue: "Unauthorized"
**Solution**: 
- Make sure you're logged in
- Include `Authorization: Bearer YOUR_TOKEN` header
- Token might be expired - login again

### Issue: "Host verification failed"
**Solution**: Only the host can perform certain actions (approve guests, kick, end session)

### Issue: "Maximum guests reached"
**Solution**: Increase `max_guests` in session settings or kick existing guests

### Issue: "Session not found"
**Solution**: Use the correct session_id from the start response

---

## 7️⃣ Monitor Backend Logs

Watch the backend console for real-time logs:
```
📨 POST /live/start
✅ Live session started by user: xyz
📤 POST /live/start - Status: 200

📨 POST /live/request-guest
✅ Guest request created for session: abc
📤 POST /live/request-guest - Status: 200
```

---

## 8️⃣ Performance Verification

### Check Response Times:
All endpoints should respond within:
- Session start: < 2 seconds
- Join: < 1 second
- Guest request: < 500ms
- Chat message: < 200ms
- Approve request: < 1 second

### Check Database:
```sql
-- Count active sessions
SELECT COUNT(*) FROM live_sessions WHERE is_active = true;

-- Count participants
SELECT session_id, COUNT(*) as participant_count
FROM live_participants
WHERE status = 'active'
GROUP BY session_id;

-- Chat message count per session
SELECT session_id, COUNT(*) as message_count
FROM live_chat_messages
GROUP BY session_id
ORDER BY message_count DESC;
```

---

## 9️⃣ Next Steps After Backend Testing

Once backend is working:

1. **Choose WebRTC Provider**
   - LiveKit (recommended)
   - Agora
   - Daily.co

2. **Install Frontend Dependencies**
   ```bash
   cd frontend
   npm install livekit-client socket.io-client
   ```

3. **Create Enhanced LiveRoom Component**
   - Use template from DEPLOYMENT_CHECKLIST.md
   - Implement participant grid
   - Add host controls
   - Build chat interface

4. **Add WebSocket for Real-Time Updates**
   - Implement WebSocket manager in backend
   - Connect frontend to WebSocket
   - Handle real-time events

5. **Test with Multiple Users**
   - Open multiple browser windows
   - Test full guest request flow
   - Verify all controls work
   - Check chat synchronization

---

## 🎉 Success Checklist

- [ ] SQL schema applied to Supabase
- [ ] New tables visible in Supabase dashboard
- [ ] Backend server running without errors
- [ ] New endpoints visible in /docs
- [ ] Can start a live session
- [ ] Can join as viewer
- [ ] Can request guest access
- [ ] Can approve/reject requests
- [ ] Can send chat messages
- [ ] Can send reactions
- [ ] Can view participants
- [ ] Can end session
- [ ] Database records created correctly

---

## 📞 Need Help?

Check these files:
- **Full Guide**: `LIVE_STREAMING_GUIDE.md`
- **Deployment Steps**: `DEPLOYMENT_CHECKLIST.md`
- **Backend Code**: `app/live_enhanced.py`
- **Database Schema**: `LIVE_MULTI_GUEST_SCHEMA.sql`
- **API Docs**: http://localhost:8001/docs

---

**You're all set! Start testing the backend API! 🚀**
