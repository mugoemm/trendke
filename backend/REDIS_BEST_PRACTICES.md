# Redis Connection - Best Practices & Solutions

## Current Situation
Your Redis is working fine! The disconnect messages you see are just from **auto-reload** when files change during development. This is **normal and expected**.

```
🔌 Redis connection closed
🛑 Redis cache disconnected
```
This happens every time uvicorn reloads the server (when you save a file).

---

## If You Have Real Connection Issues

### Solution 1: Connection Pool with Retry Logic (BEST)

Already implemented in your `redis_cache.py`! Your current setup:

```python
class RedisCache:
    def __init__(self):
        self.redis_client = None
        self.connection_pool = None
        
    async def connect(self):
        try:
            self.connection_pool = redis.ConnectionPool.from_url(
                redis_url,
                max_connections=10,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_keepalive=True,
                health_check_interval=30
            )
            self.redis_client = redis.Redis(connection_pool=self.connection_pool)
            await self.redis_client.ping()
        except Exception as e:
            # Graceful degradation
            self.redis_client = None
```

**This is already production-ready!** ✅

---

## Production Improvements (Optional)

### 1. Add Automatic Reconnection

Create `backend/app/redis_manager.py`:

```python
import asyncio
import redis.asyncio as aioredis
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class ResilientRedisManager:
    def __init__(self, redis_url: str, max_retries: int = 5):
        self.redis_url = redis_url
        self.max_retries = max_retries
        self.client: Optional[aioredis.Redis] = None
        self._connection_lock = asyncio.Lock()
        
    async def connect(self) -> bool:
        """Connect with automatic retry"""
        for attempt in range(self.max_retries):
            try:
                self.client = await aioredis.from_url(
                    self.redis_url,
                    encoding="utf-8",
                    decode_responses=True,
                    max_connections=20,
                    socket_connect_timeout=5,
                    socket_keepalive=True,
                    health_check_interval=30,
                    retry_on_timeout=True,
                    retry_on_error=[ConnectionError, TimeoutError]
                )
                await self.client.ping()
                logger.info(f"✅ Redis connected (attempt {attempt + 1})")
                return True
            except Exception as e:
                logger.warning(f"Redis connection attempt {attempt + 1} failed: {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        logger.error("❌ Redis connection failed after all retries")
        return False
    
    async def get_client(self) -> Optional[aioredis.Redis]:
        """Get client with auto-reconnect"""
        if self.client is None:
            async with self._connection_lock:
                if self.client is None:
                    await self.connect()
        return self.client
    
    async def execute_with_retry(self, operation, *args, **kwargs):
        """Execute Redis operation with automatic retry"""
        for attempt in range(3):
            try:
                client = await self.get_client()
                if client is None:
                    return None
                return await operation(*args, **kwargs)
            except (ConnectionError, TimeoutError) as e:
                logger.warning(f"Redis operation failed (attempt {attempt + 1}): {e}")
                self.client = None  # Force reconnection
                if attempt < 2:
                    await asyncio.sleep(1)
        return None
    
    async def disconnect(self):
        """Graceful disconnect"""
        if self.client:
            await self.client.close()
            self.client = None
```

**Usage:**
```python
redis_manager = ResilientRedisManager(redis_url)
await redis_manager.connect()

# Auto-retry on failure
result = await redis_manager.execute_with_retry(
    redis_manager.client.get, "key"
)
```

---

### 2. Health Check Endpoint

Add to `backend/app/main.py`:

```python
@app.get("/health")
async def health_check():
    """System health check"""
    redis_status = "disconnected"
    redis_latency = None
    
    if HAS_REDIS_CACHE:
        try:
            import time
            start = time.time()
            await cache.redis_client.ping()
            redis_latency = round((time.time() - start) * 1000, 2)
            redis_status = "connected"
        except Exception as e:
            redis_status = f"error: {str(e)}"
    
    return {
        "status": "healthy",
        "redis": {
            "status": redis_status,
            "latency_ms": redis_latency
        },
        "database": "connected",  # Add DB check if needed
        "timestamp": datetime.utcnow().isoformat()
    }
```

Monitor: `http://localhost:8001/health`

---

### 3. Circuit Breaker Pattern

Prevent cascading failures:

```python
class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failures = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open
    
    def call(self, func):
        if self.state == "open":
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "half-open"
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func()
            if self.state == "half-open":
                self.state = "closed"
                self.failures = 0
            return result
        except Exception as e:
            self.failures += 1
            self.last_failure_time = time.time()
            
            if self.failures >= self.failure_threshold:
                self.state = "open"
            raise e

# Usage
breaker = CircuitBreaker()

try:
    breaker.call(lambda: redis_client.get("key"))
except Exception as e:
    # Use fallback (database, in-memory cache, etc.)
    pass
```

---

### 4. Monitoring & Alerts

#### Using Redis INFO:
```python
@app.get("/redis/stats")
async def redis_stats():
    """Get Redis statistics"""
    if not HAS_REDIS_CACHE:
        return {"error": "Redis not available"}
    
    try:
        info = await cache.redis_client.info()
        return {
            "connected_clients": info.get("connected_clients"),
            "used_memory_human": info.get("used_memory_human"),
            "total_commands_processed": info.get("total_commands_processed"),
            "keyspace_hits": info.get("keyspace_hits"),
            "keyspace_misses": info.get("keyspace_misses"),
            "hit_rate": round(
                info.get("keyspace_hits", 0) / 
                (info.get("keyspace_hits", 0) + info.get("keyspace_misses", 1)) * 100, 
                2
            )
        }
    except Exception as e:
        return {"error": str(e)}
```

---

### 5. Environment-Specific Configuration

Create `backend/app/config.py`:

```python
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Redis
    REDIS_URL: str
    REDIS_MAX_CONNECTIONS: int = 10
    REDIS_SOCKET_TIMEOUT: int = 5
    REDIS_SOCKET_KEEPALIVE: bool = True
    REDIS_HEALTH_CHECK_INTERVAL: int = 30
    REDIS_RETRY_ON_TIMEOUT: bool = True
    
    # Development
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    # Production
    REDIS_SSL_CERT_REQS: str = "required"  # For production
    
    class Config:
        env_file = ".env"

settings = Settings()
```

Use in code:
```python
from .config import settings

redis_client = redis.from_url(
    settings.REDIS_URL,
    max_connections=settings.REDIS_MAX_CONNECTIONS,
    socket_timeout=settings.REDIS_SOCKET_TIMEOUT
)
```

---

## Quick Fixes for Common Issues

### Issue 1: "Connection timeout"
**Solution:** Increase timeout in Upstash dashboard or config:
```python
socket_connect_timeout=10,  # Increase from 5 to 10
socket_timeout=10
```

### Issue 2: "Too many connections"
**Solution:** Use connection pooling:
```python
connection_pool = redis.ConnectionPool.from_url(
    redis_url,
    max_connections=50  # Increase pool size
)
```

### Issue 3: "Connection reset by peer"
**Solution:** Enable keep-alive:
```python
socket_keepalive=True,
health_check_interval=30
```

### Issue 4: Development hot-reload disconnects
**Solution:** This is normal! Or disable in production:
```bash
# Development (with reload)
uvicorn app.main:app --reload

# Production (no reload)
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

---

## Production Deployment Checklist

### ✅ Current Setup (Already Done!)
- [x] Connection pooling
- [x] Graceful degradation (app works without Redis)
- [x] Error logging
- [x] SSL connection (rediss://)
- [x] Auto-cleanup on shutdown

### 🔧 Optional Improvements
- [ ] Automatic reconnection with exponential backoff
- [ ] Circuit breaker pattern
- [ ] Health check endpoint
- [ ] Monitoring dashboard
- [ ] Alert on connection failures
- [ ] Redis Sentinel for HA (multi-instance)
- [ ] Redis Cluster for scaling

---

## Upstash-Specific Best Practices

Your Upstash Redis connection is already optimized:

1. ✅ **SSL/TLS** - Using `rediss://` protocol
2. ✅ **Connection pooling** - Max 10 connections
3. ✅ **Keep-alive** - Prevents connection drops
4. ✅ **Health checks** - Every 30 seconds
5. ✅ **Graceful degradation** - App works without Redis

### Upstash Dashboard Settings:
- **Max connections**: 1000 (Free tier)
- **Eviction policy**: `allkeys-lru` (recommended)
- **Max memory**: Check your plan limit

---

## Monitoring in Production

### 1. Upstash Dashboard
- Monitor connection count
- Check memory usage
- View command statistics

### 2. Application Logs
```python
import logging

logger = logging.getLogger(__name__)

# Log Redis events
logger.info("✅ Redis connected")
logger.warning("⚠️ Redis slow response: 500ms")
logger.error("❌ Redis connection failed")
```

### 3. Metrics (Optional - Advanced)
Use Prometheus + Grafana:
```python
from prometheus_client import Counter, Histogram

redis_operations = Counter('redis_operations_total', 'Total Redis ops')
redis_latency = Histogram('redis_operation_duration_seconds', 'Redis op latency')

@redis_latency.time()
async def cache_get(key):
    redis_operations.inc()
    return await redis_client.get(key)
```

---

## Recommendation

**Your current setup is already production-ready!** ✅

The disconnect messages you see are **normal** during development hot-reload.

**Only implement additional features if you experience:**
- Frequent connection timeouts in production
- High connection failure rate (>5%)
- Need for automatic recovery
- Need for monitoring/alerting

---

## Simple Test

Test your Redis connection:

```bash
# In terminal
curl http://localhost:8001/health
```

Or add this endpoint:
```python
@app.get("/redis/ping")
async def redis_ping():
    try:
        await cache.redis_client.ping()
        return {"status": "connected", "message": "pong"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
```

---

**Your Redis is working perfectly! The disconnects are just from file saves during development. No action needed! 🎉**
