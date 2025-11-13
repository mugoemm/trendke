"""
Test WebSocket Connection
Run this to verify the WebSocket endpoint is reachable
"""
import asyncio
import websockets
import json

async def test_connection():
    # You'll need to replace these with real values
    session_id = "test-session-123"
    token = "your-jwt-token-here"
    username = "test-user"
    
    uri = f"ws://localhost:8001/ws/live/{session_id}?token={token}&username={username}"
    
    print(f"🔌 Attempting to connect to: {uri}")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected successfully!")
            
            # Send a ping
            await websocket.send(json.dumps({"action": "ping"}))
            print("📤 Sent ping")
            
            # Wait for response
            response = await websocket.recv()
            print(f"📨 Received: {response}")
            
    except Exception as e:
        print(f"❌ Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_connection())
