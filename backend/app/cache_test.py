"""
Cache testing endpoints
"""
from fastapi import APIRouter, HTTPException
from datetime import datetime
import uuid

router = APIRouter(prefix="/cache", tags=["Cache"])

try:
    from .redis_cache import cache
    HAS_REDIS = True
except ImportError:
    HAS_REDIS = False


@router.get("/test")
async def test_cache():
    """
    Test Redis cache connection
    Sets a test key and retrieves it to confirm Redis is working
    """
    if not HAS_REDIS or not cache.enabled:
        return {
            "status": "disabled",
            "message": "Redis cache is not available",
            "enabled": False
        }
    
    try:
        # Generate test data
        test_key = f"test:ping:{uuid.uuid4()}"
        test_value = {
            "message": "Redis is working!",
            "timestamp": datetime.now().isoformat(),
            "test_id": str(uuid.uuid4())
        }
        
        # Set test key (10 second expiry)
        await cache.set(test_key, test_value, expire=10)
        
        # Retrieve test key
        retrieved = await cache.get(test_key)
        
        # Verify
        if retrieved and retrieved.get("message") == test_value["message"]:
            # Clean up
            await cache.delete(test_key)
            
            return {
                "status": "success",
                "message": "✅ Redis cache is working correctly!",
                "enabled": True,
                "redis_url": cache.redis_url.replace(cache.redis_url.split('@')[-1] if '@' in cache.redis_url else '', '***') if '@' in cache.redis_url else cache.redis_url,
                "test_data": {
                    "written": test_value,
                    "retrieved": retrieved,
                    "match": True
                }
            }
        else:
            return {
                "status": "error",
                "message": "❌ Redis set/get mismatch",
                "enabled": True,
                "test_data": {
                    "written": test_value,
                    "retrieved": retrieved,
                    "match": False
                }
            }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Cache test failed: {str(e)}"
        )


@router.get("/stats")
async def cache_stats():
    """Get cache statistics and info"""
    if not HAS_REDIS or not cache.enabled:
        return {
            "status": "disabled",
            "message": "Redis cache is not available",
            "enabled": False
        }
    
    try:
        # Get Redis info
        info = await cache.redis.info("stats")
        keyspace = await cache.redis.info("keyspace")
        
        # Count keys by pattern
        all_keys = await cache.redis.keys("*")
        feed_keys = [k for k in all_keys if k.startswith("feed:")]
        trending_keys = [k for k in all_keys if k.startswith("trending:")]
        user_keys = [k for k in all_keys if k.startswith("user:")]
        video_keys = [k for k in all_keys if k.startswith("video:")]
        
        return {
            "status": "success",
            "enabled": True,
            "redis_url": cache.redis_url,
            "statistics": {
                "total_keys": len(all_keys),
                "feed_caches": len(feed_keys),
                "trending_caches": len(trending_keys),
                "user_caches": len(user_keys),
                "video_caches": len(video_keys),
                "hits": info.get("keyspace_hits", 0),
                "misses": info.get("keyspace_misses", 0),
                "hit_rate": f"{(info.get('keyspace_hits', 0) / max(info.get('keyspace_hits', 0) + info.get('keyspace_misses', 1), 1) * 100):.2f}%"
            },
            "keyspace_info": keyspace
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get cache stats: {str(e)}"
        )


@router.delete("/clear")
async def clear_cache():
    """Clear all cache (admin only in production!)"""
    if not HAS_REDIS or not cache.enabled:
        return {
            "status": "disabled",
            "message": "Redis cache is not available",
            "enabled": False
        }
    
    try:
        # Get count before clearing
        all_keys = await cache.redis.keys("*")
        count = len(all_keys)
        
        # Clear all
        await cache.redis.flushdb()
        
        return {
            "status": "success",
            "message": f"✅ Cleared {count} cached items",
            "cleared_count": count
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clear cache: {str(e)}"
        )
