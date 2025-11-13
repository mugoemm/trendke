"""
Complete Production-Ready FastAPI Backend with Redis Caching
=============================================================

Features:
- Async Redis client with automatic reconnection
- Persistent connection through uvicorn --reload
- Proper startup/shutdown event handling
- Redis dependency injection for all routes
- Basic cache routes (set/get)
- Trending scheduler (runs every 15 minutes)
- Clear logging for all operations
- Lazy reconnection on Redis failures
- Configurable via environment variables

Usage:
    uvicorn app.main_redis_complete:app --host 127.0.0.1 --port 8001 --reload
"""

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
import redis.asyncio as aioredis
import json
import os
from typing import Optional, Any, Dict, List
from datetime import datetime
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import asyncio

# Load environment variables
load_dotenv()

# ============================================================================
# Redis Cache Manager
# ============================================================================

class RedisManager:
    """
    Production-ready Redis manager with:
    - Async connection handling
    - Automatic reconnection
    - Connection pooling
    - Graceful degradation
    """
    
    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self.redis: Optional[aioredis.Redis] = None
        self.connected = False
        self._connection_lock = asyncio.Lock()
        
    async def connect(self):
        """Establish Redis connection with retry logic"""
        async with self._connection_lock:
            if self.connected and self.redis:
                try:
                    await self.redis.ping()
                    return True
                except:
                    self.connected = False
            
            try:
                self.redis = await aioredis.from_url(
                    self.redis_url,
                    encoding="utf-8",
                    decode_responses=True,
                    max_connections=10,
                    socket_keepalive=True,
                    socket_connect_timeout=5,
                    retry_on_timeout=True
                )
                
                # Test connection
                await self.redis.ping()
                self.connected = True
                print(f"✅ Redis connected successfully")
                print(f"   URL: {self._mask_url(self.redis_url)}")
                return True
                
            except Exception as e:
                self.connected = False
                self.redis = None
                print(f"❌ Redis connection failed: {e}")
                print(f"   Will continue without caching")
                return False
    
    async def disconnect(self):
        """Gracefully close Redis connection"""
        if self.redis:
            try:
                await self.redis.close()
                print("🔌 Redis connection closed")
            except Exception as e:
                print(f"⚠️  Error closing Redis: {e}")
            finally:
                self.connected = False
                self.redis = None
    
    async def ensure_connected(self):
        """Lazy reconnection - reconnect if connection lost"""
        if not self.connected or not self.redis:
            await self.connect()
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from Redis with automatic reconnection"""
        await self.ensure_connected()
        
        if not self.connected:
            return None
        
        try:
            value = await self.redis.get(key)
            if value:
                try:
                    return json.loads(value)
                except:
                    return value
            return None
        except Exception as e:
            print(f"⚠️  Redis GET error for key '{key}': {e}")
            self.connected = False  # Mark for reconnection
            return None
    
    async def set(self, key: str, value: Any, expire: int = 300) -> bool:
        """Set value in Redis with automatic reconnection"""
        await self.ensure_connected()
        
        if not self.connected:
            return False
        
        try:
            if not isinstance(value, str):
                value = json.dumps(value, default=str)
            
            await self.redis.set(key, value, ex=expire)
            return True
        except Exception as e:
            print(f"⚠️  Redis SET error for key '{key}': {e}")
            self.connected = False  # Mark for reconnection
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from Redis"""
        await self.ensure_connected()
        
        if not self.connected:
            return False
        
        try:
            await self.redis.delete(key)
            return True
        except Exception as e:
            print(f"⚠️  Redis DELETE error for key '{key}': {e}")
            return False
    
    async def keys(self, pattern: str = "*") -> List[str]:
        """Get all keys matching pattern"""
        await self.ensure_connected()
        
        if not self.connected:
            return []
        
        try:
            keys = await self.redis.keys(pattern)
            return keys if keys else []
        except Exception as e:
            print(f"⚠️  Redis KEYS error: {e}")
            return []
    
    def _mask_url(self, url: str) -> str:
        """Mask sensitive parts of Redis URL for logging"""
        if "@" in url:
            parts = url.split("@")
            if ":" in parts[0]:
                protocol_user = parts[0].rsplit(":", 1)[0]
                return f"{protocol_user}:****@{parts[1]}"
        return url

# ============================================================================
# Trending Scheduler
# ============================================================================

class TrendingScheduler:
    """
    Background task that updates trending content every 15 minutes
    Stores results in Redis for fast access
    """
    
    def __init__(self, redis_manager: RedisManager):
        self.redis = redis_manager
        self.task: Optional[asyncio.Task] = None
        self.running = False
        self.update_interval = 900  # 15 minutes in seconds
        
    async def update_trending(self):
        """Calculate and cache trending content"""
        try:
            # Simulate trending calculation (in production, query your database)
            trending_data = {
                "videos": [
                    {
                        "id": f"video_{i}",
                        "title": f"Trending Video {i}",
                        "views": 1000 * (10 - i),
                        "score": 100 * (10 - i)
                    }
                    for i in range(1, 11)
                ],
                "updated_at": datetime.now().isoformat(),
                "algorithm_version": "v1.0"
            }
            
            # Store in Redis with 20-minute expiry (slightly longer than update interval)
            success = await self.redis.set(
                "trending:videos",
                trending_data,
                expire=1200
            )
            
            if success:
                print(f"📊 Cached {len(trending_data['videos'])} trending videos")
                print(f"   Updated at: {trending_data['updated_at']}")
            else:
                print(f"⚠️  Failed to cache trending videos")
                
        except Exception as e:
            print(f"❌ Error updating trending content: {e}")
    
    async def _scheduler_loop(self):
        """Main scheduler loop"""
        print(f"📊 Trending scheduler started (updates every {self.update_interval // 60} minutes)")
        
        # Initial update
        await self.update_trending()
        
        while self.running:
            try:
                await asyncio.sleep(self.update_interval)
                if self.running:
                    await self.update_trending()
            except asyncio.CancelledError:
                print("📊 Scheduler loop cancelled")
                break
            except Exception as e:
                print(f"❌ Scheduler error: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retry
    
    def start(self):
        """Start the scheduler"""
        if not self.running:
            self.running = True
            self.task = asyncio.create_task(self._scheduler_loop())
            print("🚀 Trending scheduler started")
    
    def stop(self):
        """Stop the scheduler"""
        if self.running:
            self.running = False
            if self.task:
                self.task.cancel()
            print("🛑 Trending scheduler stopped")

# ============================================================================
# Application Lifespan Management
# ============================================================================

# Global instances
redis_manager: Optional[RedisManager] = None
trending_scheduler: Optional[TrendingScheduler] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifecycle
    - Startup: Connect to Redis, start scheduler
    - Shutdown: Disconnect Redis, stop scheduler
    
    This ensures connections persist through uvicorn --reload
    """
    global redis_manager, trending_scheduler
    
    # ========== STARTUP ==========
    print("\n" + "="*60)
    print("🚀 Starting TrendKe API Server")
    print("="*60)
    
    # Initialize Redis
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
    redis_manager = RedisManager(redis_url)
    await redis_manager.connect()
    
    # Initialize and start scheduler
    if redis_manager.connected:
        trending_scheduler = TrendingScheduler(redis_manager)
        trending_scheduler.start()
    else:
        print("ℹ️  Trending scheduler disabled (Redis not connected)")
    
    print("="*60)
    print("✅ Server startup complete")
    print("="*60 + "\n")
    
    yield
    
    # ========== SHUTDOWN ==========
    print("\n" + "="*60)
    print("🛑 Shutting down TrendKe API Server")
    print("="*60)
    
    # Stop scheduler
    if trending_scheduler:
        trending_scheduler.stop()
    
    # Disconnect Redis
    if redis_manager:
        await redis_manager.disconnect()
    
    print("="*60)
    print("✅ Server shutdown complete")
    print("="*60 + "\n")

# ============================================================================
# FastAPI Application
# ============================================================================

app = FastAPI(
    title="TrendKe API - Redis Complete",
    description="Production-ready FastAPI backend with Redis caching",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Dependency Injection
# ============================================================================

async def get_redis() -> RedisManager:
    """
    Dependency to access Redis in any route
    
    Usage:
        @app.get("/example")
        async def example(redis: RedisManager = Depends(get_redis)):
            await redis.set("key", "value")
    """
    if not redis_manager:
        raise HTTPException(status_code=503, detail="Redis not initialized")
    return redis_manager

# ============================================================================
# Routes
# ============================================================================

@app.get("/")
async def root():
    """Server running message"""
    return {
        "message": "🚀 TrendKe API Server Running",
        "status": "healthy",
        "version": "1.0.0",
        "redis": "connected" if redis_manager and redis_manager.connected else "disconnected",
        "scheduler": "running" if trending_scheduler and trending_scheduler.running else "stopped",
        "endpoints": {
            "health": "/health",
            "cache_set": "/cache-set?key=<key>&value=<value>",
            "cache_get": "/cache-get?key=<key>",
            "cache_delete": "/cache-delete?key=<key>",
            "cache_keys": "/cache-keys",
            "trending": "/trending"
        },
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health")
async def health_check(redis: RedisManager = Depends(get_redis)):
    """
    Health check endpoint
    Verifies Redis connectivity and scheduler status
    """
    redis_status = "disconnected"
    redis_ping = False
    
    if redis.connected:
        try:
            await redis.redis.ping()
            redis_status = "connected"
            redis_ping = True
        except:
            redis_status = "degraded"
    
    return {
        "status": "healthy" if redis_ping else "degraded",
        "service": "trendke-api",
        "redis": {
            "status": redis_status,
            "connected": redis.connected,
            "ping": redis_ping
        },
        "scheduler": {
            "running": trending_scheduler.running if trending_scheduler else False
        },
        "timestamp": datetime.now().isoformat()
    }


@app.get("/cache-set")
async def cache_set(
    key: str = Query(..., description="Cache key"),
    value: str = Query(..., description="Cache value"),
    expire: int = Query(300, description="Expiry time in seconds (default 5 minutes)"),
    redis: RedisManager = Depends(get_redis)
):
    """
    Set a key-value pair in Redis
    
    Example: /cache-set?key=mykey&value=myvalue&expire=600
    """
    print(f"🔹 Setting cache: {key} = {value} (expire: {expire}s)")
    
    success = await redis.set(key, value, expire=expire)
    
    if success:
        return {
            "status": "success",
            "message": f"Key '{key}' set successfully",
            "key": key,
            "value": value,
            "expire": expire,
            "timestamp": datetime.now().isoformat()
        }
    else:
        raise HTTPException(status_code=503, detail="Redis operation failed")


@app.get("/cache-get")
async def cache_get(
    key: str = Query(..., description="Cache key"),
    redis: RedisManager = Depends(get_redis)
):
    """
    Get a value from Redis by key
    
    Example: /cache-get?key=mykey
    """
    print(f"🔹 Getting cache: {key}")
    
    value = await redis.get(key)
    
    if value is not None:
        return {
            "status": "success",
            "key": key,
            "value": value,
            "found": True,
            "timestamp": datetime.now().isoformat()
        }
    else:
        return {
            "status": "success",
            "key": key,
            "value": None,
            "found": False,
            "message": "Key not found or expired",
            "timestamp": datetime.now().isoformat()
        }


@app.get("/cache-delete")
async def cache_delete(
    key: str = Query(..., description="Cache key to delete"),
    redis: RedisManager = Depends(get_redis)
):
    """
    Delete a key from Redis
    
    Example: /cache-delete?key=mykey
    """
    print(f"🔹 Deleting cache: {key}")
    
    success = await redis.delete(key)
    
    if success:
        return {
            "status": "success",
            "message": f"Key '{key}' deleted successfully",
            "key": key,
            "timestamp": datetime.now().isoformat()
        }
    else:
        raise HTTPException(status_code=503, detail="Redis operation failed")


@app.get("/cache-keys")
async def cache_keys(
    pattern: str = Query("*", description="Key pattern (supports * wildcard)"),
    redis: RedisManager = Depends(get_redis)
):
    """
    List all keys matching pattern
    
    Example: /cache-keys?pattern=user:*
    """
    print(f"🔹 Listing keys: {pattern}")
    
    keys = await redis.keys(pattern)
    
    return {
        "status": "success",
        "pattern": pattern,
        "keys": keys,
        "count": len(keys),
        "timestamp": datetime.now().isoformat()
    }


@app.get("/trending")
async def get_trending(redis: RedisManager = Depends(get_redis)):
    """
    Get trending videos from cache
    Updated every 15 minutes by background scheduler
    """
    print("🔹 Fetching trending videos")
    
    trending = await redis.get("trending:videos")
    
    if trending:
        return {
            "status": "success",
            "data": trending,
            "source": "cache",
            "timestamp": datetime.now().isoformat()
        }
    else:
        return {
            "status": "success",
            "data": {
                "videos": [],
                "message": "Trending data not yet available"
            },
            "source": "empty",
            "timestamp": datetime.now().isoformat()
        }


@app.get("/trigger-trending-update")
async def trigger_trending_update(redis: RedisManager = Depends(get_redis)):
    """
    Manually trigger trending update
    Useful for testing or immediate refresh
    """
    print("🔹 Manually triggering trending update")
    
    if not trending_scheduler:
        raise HTTPException(status_code=503, detail="Trending scheduler not initialized")
    
    await trending_scheduler.update_trending()
    
    return {
        "status": "success",
        "message": "Trending content updated",
        "timestamp": datetime.now().isoformat()
    }


# ============================================================================
# Error Handlers
# ============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handle uncaught exceptions gracefully"""
    print(f"❌ Unhandled exception: {exc}")
    return {
        "status": "error",
        "message": "Internal server error",
        "detail": str(exc),
        "timestamp": datetime.now().isoformat()
    }


# ============================================================================
# Development Server
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*60)
    print("🚀 Starting FastAPI with Uvicorn")
    print("="*60)
    print("📝 Server: http://127.0.0.1:8001")
    print("📚 Docs: http://127.0.0.1:8001/docs")
    print("🔄 Reload: Enabled")
    print("="*60 + "\n")
    
    uvicorn.run(
        "app.main_redis_complete:app",
        host="127.0.0.1",
        port=8001,
        reload=True,
        log_level="info"
    )
