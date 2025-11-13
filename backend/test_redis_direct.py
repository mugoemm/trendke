"""
Simple Redis connection test
"""
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def test_redis():
    try:
        import redis.asyncio as redis
        
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        print(f"Connecting to: {redis_url}")
        
        r = await redis.from_url(redis_url, encoding="utf-8", decode_responses=True)
        
        # Test connection
        pong = await r.ping()
        print(f"✅ PING: {pong}")
        
        # Set a test key
        await r.set("test:hello", "world", ex=10)
        print("✅ SET test:hello = world")
        
        # Get the test key
        value = await r.get("test:hello")
        print(f"✅ GET test:hello = {value}")
        
        # Delete the test key
        await r.delete("test:hello")
        print("✅ DEL test:hello")
        
        await r.close()
        print("\n🎉 Redis is working perfectly!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_redis())
