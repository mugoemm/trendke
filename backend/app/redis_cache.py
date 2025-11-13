"""
Redis Caching Service for TrendKe
Caches video feeds, trending videos, user data, and frequently accessed content
"""
import redis.asyncio as redis
import json
import os
from typing import Optional, List, Dict, Any
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class RedisCache:
    def __init__(self):
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.redis: Optional[redis.Redis] = None
        self.enabled = False
        
    async def connect(self):
        """Connect to Redis server"""
        try:
            # Simple connection - rediss:// protocol handles SSL automatically
            self.redis = await redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            # Test connection
            await self.redis.ping()
            self.enabled = True
            print(f"✅ Redis cache connected successfully (URL: {self.redis_url})")
        except Exception as e:
            self.enabled = False
            print(f"❌ Redis connection failed: {e}")
    
    async def disconnect(self):
        """Disconnect from Redis"""
        if self.redis:
            await self.redis.close()
            print("🔌 Redis connection closed")
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.enabled:
            return None
        
        try:
            value = await self.redis.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            print(f"⚠️  Redis GET error: {e}")
            return None
    
    async def set(self, key: str, value: Any, expire: int = 300):
        """
        Set value in cache
        expire: TTL in seconds (default 5 minutes)
        """
        if not self.enabled:
            return False
        
        try:
            serialized = json.dumps(value, default=str)
            await self.redis.set(key, serialized, ex=expire)
            return True
        except Exception as e:
            print(f"⚠️  Redis SET error: {e}")
            return False
    
    async def delete(self, key: str):
        """Delete key from cache"""
        if not self.enabled:
            return False
        
        try:
            await self.redis.delete(key)
            return True
        except Exception as e:
            print(f"⚠️  Redis DELETE error: {e}")
            return False
    
    async def delete_pattern(self, pattern: str):
        """Delete all keys matching pattern"""
        if not self.enabled:
            return False
        
        try:
            keys = await self.redis.keys(pattern)
            if keys:
                await self.redis.delete(*keys)
            return True
        except Exception as e:
            print(f"⚠️  Redis DELETE PATTERN error: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        if not self.enabled:
            return False
        
        try:
            return await self.redis.exists(key) > 0
        except Exception as e:
            print(f"⚠️  Redis EXISTS error: {e}")
            return False
    
    # === Video Feed Caching ===
    
    async def get_video_feed(self, user_id: Optional[str], limit: int, offset: int) -> Optional[List[Dict]]:
        """Get cached video feed"""
        key = f"feed:{user_id or 'public'}:{limit}:{offset}"
        return await self.get(key)
    
    async def set_video_feed(self, user_id: Optional[str], limit: int, offset: int, videos: List[Dict], expire: int = 300):
        """Cache video feed (5 minutes TTL)"""
        key = f"feed:{user_id or 'public'}:{limit}:{offset}"
        await self.set(key, videos, expire)
    
    async def invalidate_video_feeds(self):
        """Invalidate all video feed caches"""
        await self.delete_pattern("feed:*")
        print("🔄 Video feed cache invalidated")
    
    # === Trending Videos Caching ===
    
    async def get_trending_videos(self) -> Optional[List[Dict]]:
        """Get cached trending videos"""
        return await self.get("trending:videos")
    
    async def set_trending_videos(self, videos: List[Dict], expire: int = 900):
        """Cache trending videos (15 minutes TTL)"""
        await self.set("trending:videos", videos, expire)
        print(f"📊 Cached {len(videos)} trending videos")
    
    # === User Data Caching ===
    
    async def get_user(self, user_id: str) -> Optional[Dict]:
        """Get cached user data"""
        return await self.get(f"user:{user_id}")
    
    async def set_user(self, user_id: str, user_data: Dict, expire: int = 600):
        """Cache user data (10 minutes TTL)"""
        await self.set(f"user:{user_id}", user_data, expire)
    
    async def invalidate_user(self, user_id: str):
        """Invalidate user cache"""
        await self.delete(f"user:{user_id}")
        print(f"🔄 User cache invalidated: {user_id}")
    
    # === Video Details Caching ===
    
    async def get_video(self, video_id: str) -> Optional[Dict]:
        """Get cached video details"""
        return await self.get(f"video:{video_id}")
    
    async def set_video(self, video_id: str, video_data: Dict, expire: int = 600):
        """Cache video details (10 minutes TTL)"""
        await self.set(f"video:{video_id}", video_data, expire)
    
    async def invalidate_video(self, video_id: str):
        """Invalidate video cache"""
        await self.delete(f"video:{video_id}")
        await self.invalidate_video_feeds()  # Also invalidate feeds
        print(f"🔄 Video cache invalidated: {video_id}")
    
    # === Comments Caching ===
    
    async def get_video_comments(self, video_id: str, limit: int) -> Optional[List[Dict]]:
        """Get cached video comments"""
        key = f"comments:{video_id}:{limit}"
        return await self.get(key)
    
    async def set_video_comments(self, video_id: str, limit: int, comments: List[Dict], expire: int = 300):
        """Cache video comments (5 minutes TTL)"""
        key = f"comments:{video_id}:{limit}"
        await self.set(key, comments, expire)
    
    async def invalidate_video_comments(self, video_id: str):
        """Invalidate video comments cache"""
        await self.delete_pattern(f"comments:{video_id}:*")
        print(f"🔄 Comments cache invalidated: {video_id}")
    
    # === Analytics/Stats Caching ===
    
    async def increment_views(self, video_id: str):
        """Increment video view count (for real-time stats)"""
        if not self.enabled:
            return
        
        try:
            key = f"views:{video_id}"
            await self.redis.incr(key)
            await self.redis.expire(key, 3600)  # Expire after 1 hour
        except Exception as e:
            print(f"⚠️  Redis INCR error: {e}")
    
    async def get_view_count(self, video_id: str) -> int:
        """Get cached view count"""
        if not self.enabled:
            return 0
        
        try:
            count = await self.redis.get(f"views:{video_id}")
            return int(count) if count else 0
        except Exception as e:
            print(f"⚠️  Redis GET error: {e}")
            return 0
    
    # === Rate Limiting (Bonus) ===
    
    async def check_rate_limit(self, key: str, limit: int, window: int) -> bool:
        """
        Check if rate limit exceeded
        key: unique identifier (e.g., "api:user_123")
        limit: max requests allowed
        window: time window in seconds
        """
        if not self.enabled:
            return True  # Allow if Redis disabled
        
        try:
            current = await self.redis.incr(key)
            if current == 1:
                await self.redis.expire(key, window)
            return current <= limit
        except Exception as e:
            print(f"⚠️  Redis rate limit error: {e}")
            return True  # Allow on error


# Global cache instance
cache = RedisCache()
