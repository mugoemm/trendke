"""
Middleware for rate limiting and security
"""
from fastapi import Request, HTTPException, status
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, Tuple
import time

# In-memory rate limiter (use Redis in production)
rate_limit_storage: Dict[str, list] = defaultdict(list)


class RateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self, requests: int = 5, window: int = 60):
        """
        Args:
            requests: Number of requests allowed
            window: Time window in seconds
        """
        self.requests = requests
        self.window = window
    
    async def __call__(self, request: Request):
        """Check if request should be rate limited"""
        client_ip = request.client.host
        path = request.url.path
        
        # Combine IP and path for unique key
        key = f"{client_ip}:{path}"
        now = time.time()
        
        # Clean old entries
        rate_limit_storage[key] = [
            timestamp for timestamp in rate_limit_storage[key]
            if now - timestamp < self.window
        ]
        
        # Check if limit exceeded
        if len(rate_limit_storage[key]) >= self.requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Try again in {self.window} seconds."
            )
        
        # Add current request timestamp
        rate_limit_storage[key].append(now)


# Different rate limiters for different endpoints
auth_rate_limiter = RateLimiter(requests=5, window=60)  # 5 attempts per minute
upload_rate_limiter = RateLimiter(requests=10, window=300)  # 10 uploads per 5 minutes
comment_rate_limiter = RateLimiter(requests=30, window=60)  # 30 comments per minute
