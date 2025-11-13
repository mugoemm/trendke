from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv

from .auth import router as auth_router
from .video import router as video_router
from .live import router as live_router
from .live_enhanced import router as live_enhanced_router
from .gifts import router as gifts_router
from .notifications import router as notifications_router
from .payments import router as payments_router
from .cache_test import router as cache_router
from .websocket_routes import router as websocket_router
from .social import router as social_router

# Try to import extended auth router (optional features)
try:
    from .auth_extended import router as auth_extended_router
    HAS_EXTENDED_AUTH = True
except ImportError:
    HAS_EXTENDED_AUTH = False
    print("ℹ️  Extended auth features not available (email/2FA). Install: pip install sendgrid")

# Try to import trending scheduler (optional feature)
try:
    from .trending_scheduler import trending_scheduler
    HAS_TRENDING_SCHEDULER = True
except ImportError:
    HAS_TRENDING_SCHEDULER = False
    print("ℹ️  Trending scheduler not available. Install: pip install apscheduler")

# Try to import Redis cache (optional feature)
try:
    from .redis_cache import cache
    HAS_REDIS_CACHE = True
except ImportError:
    HAS_REDIS_CACHE = False
    print("ℹ️  Redis cache not available. Install: pip install redis")


# Load .env for local development only
if os.environ.get("ENV", "development") == "development":
    load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="TrendKe API",
    description="Social media platform with live streaming and gifting",
    version="1.0.0"
)

# CORS Configuration
# Allow both local development and production frontend
frontend_url = os.environ.get("FRONTEND_URL", "http://localhost:5173")
allowed_origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    frontend_url,
]

# Add production Vercel domains
if "vercel.app" in frontend_url:
    # Allow all Vercel preview deployments
    allowed_origins.extend([
        "https://*.vercel.app",
        frontend_url.replace("https://", "https://*."),  # Preview deployments
    ])

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request, call_next):
    print(f"📨 {request.method} {request.url.path}")
    response = await call_next(request)
    print(f"📤 {request.method} {request.url.path} - Status: {response.status_code}")
    return response

# Include routers
app.include_router(auth_router)
if HAS_EXTENDED_AUTH:
    app.include_router(auth_extended_router)
app.include_router(video_router)
app.include_router(live_router)
app.include_router(live_enhanced_router)  # Enhanced multi-guest live streaming
app.include_router(gifts_router)
app.include_router(notifications_router)
app.include_router(payments_router)
app.include_router(cache_router)
app.include_router(websocket_router)
app.include_router(social_router)  # Follow/Unfollow features


@app.on_event("startup")
async def startup_event():
    """Start background tasks on app startup"""
    # Connect to Redis cache
    if HAS_REDIS_CACHE:
        await cache.connect()
        print("🚀 Redis cache initialized")
    else:
        print("ℹ️  Redis cache disabled (install redis to enable)")
    
    # Start trending scheduler
    if HAS_TRENDING_SCHEDULER:
        trending_scheduler.start()
        print("🚀 Trending scheduler started")
    else:
        print("ℹ️  Trending scheduler disabled (install apscheduler to enable)")
    
    # Debug: Print WebSocket routes
    print("\n🔍 Registered WebSocket routes:")
    for route in app.routes:
        if hasattr(route, 'path') and '/ws/' in route.path:
            print(f"   {route.path}")


@app.on_event("shutdown")
async def shutdown_event():
    """Stop background tasks on app shutdown"""
    # Disconnect from Redis
    if HAS_REDIS_CACHE:
        await cache.disconnect()
        print("🛑 Redis cache disconnected")
    
    # Stop trending scheduler
    if HAS_TRENDING_SCHEDULER:
        trending_scheduler.stop()
        print("🛑 Trending scheduler stopped")


@app.get("/")
async def root():
    """API root endpoint"""
    print("🏠 Root endpoint accessed")
    return {
        "message": "Welcome to TrendKe API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "auth": "/auth",
            "videos": "/videos",
            "live": "/live",
            "gifts": "/gifts",
            "notifications": "/notifications",
            "payments": "/payments"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint with database connectivity check"""
    from .db import supabase
    
    health_status = {
        "status": "healthy",
        "service": "trendke-api",
        "database": "disconnected"
    }
    
    # Check database connectivity
    try:
        if supabase:
            # Simple query to test connection
            test = supabase.table("users").select("id").limit(1).execute()
            health_status["database"] = "connected"
    except Exception as e:
        health_status["status"] = "degraded"
        health_status["database_error"] = str(e)
    
    return health_status


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handle uncaught exceptions"""
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "message": str(exc)
        }
    )


if __name__ == "__main__":
    import uvicorn
    # Detect environment: use reload and localhost in dev, $PORT and 0.0.0.0 in prod
    env = os.environ.get("ENV", "development")
    if env == "production":
        # Render sets $PORT; must listen on 0.0.0.0 and use $PORT for HTTP traffic
        port = int(os.environ.get("PORT", 8000))
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=port,
            reload=False  # Never use reload in production
        )
    else:
        # Local dev: use reload and localhost
        uvicorn.run(
            "app.main:app",
            host="127.0.0.1",
            port=8000,
            reload=True
        )
