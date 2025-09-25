"""
Rate limiting middleware for FastAPI.
"""
import time
from typing import Dict, Optional
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from app.services.cache import RedisCache


class RateLimiter:
    """Rate limiter using Redis for distributed rate limiting."""
    
    def __init__(self, requests_per_minute: int = 60, requests_per_hour: int = 1000):
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.cache = RedisCache()
    
    async def is_allowed(self, client_ip: str, endpoint: str = "default") -> bool:
        """
        Check if the client is allowed to make a request.
        
        Args:
            client_ip: Client IP address
            endpoint: API endpoint being accessed
            
        Returns:
            True if request is allowed, False otherwise
        """
        current_time = int(time.time())
        minute_key = f"rate_limit:{client_ip}:{endpoint}:minute:{current_time // 60}"
        hour_key = f"rate_limit:{client_ip}:{endpoint}:hour:{current_time // 3600}"
        
        try:
            # Check minute rate limit
            minute_count = await self.cache.get(minute_key)
            if minute_count is None:
                minute_count = 0
            
            if int(minute_count) >= self.requests_per_minute:
                return False
            
            # Check hour rate limit
            hour_count = await self.cache.get(hour_key)
            if hour_count is None:
                hour_count = 0
            
            if int(hour_count) >= self.requests_per_hour:
                return False
            
            # Increment counters
            await self.cache.set(minute_key, str(int(minute_count) + 1), ttl=60)
            await self.cache.set(hour_key, str(int(hour_count) + 1), ttl=3600)
            
            return True
            
        except Exception:
            # If Redis is down, allow the request (fail open)
            return True
    
    async def get_remaining_requests(self, client_ip: str, endpoint: str = "default") -> Dict[str, int]:
        """
        Get remaining requests for the client.
        
        Args:
            client_ip: Client IP address
            endpoint: API endpoint being accessed
            
        Returns:
            Dictionary with remaining requests
        """
        current_time = int(time.time())
        minute_key = f"rate_limit:{client_ip}:{endpoint}:minute:{current_time // 60}"
        hour_key = f"rate_limit:{client_ip}:{endpoint}:hour:{current_time // 3600}"
        
        try:
            minute_count = await self.cache.get(minute_key) or 0
            hour_count = await self.cache.get(hour_key) or 0
            
            return {
                "minute_remaining": max(0, self.requests_per_minute - int(minute_count)),
                "hour_remaining": max(0, self.requests_per_hour - int(hour_count)),
                "minute_limit": self.requests_per_minute,
                "hour_limit": self.requests_per_hour,
            }
        except Exception:
            return {
                "minute_remaining": self.requests_per_minute,
                "hour_remaining": self.requests_per_hour,
                "minute_limit": self.requests_per_minute,
                "hour_limit": self.requests_per_hour,
            }


# Global rate limiter instance
rate_limiter = RateLimiter()


async def rate_limit_middleware(request: Request, call_next):
    """
    Rate limiting middleware.
    
    Args:
        request: FastAPI request
        call_next: Next middleware/handler
        
    Returns:
        Response or rate limit error
    """
    # Get client IP
    client_ip = request.client.host if request.client else "unknown"
    
    # Get endpoint for more granular rate limiting
    endpoint = request.url.path
    
    # Check rate limit
    is_allowed = await rate_limiter.is_allowed(client_ip, endpoint)
    
    if not is_allowed:
        # Get remaining requests for error message
        remaining = await rate_limiter.get_remaining_requests(client_ip, endpoint)
        
        return JSONResponse(
            status_code=429,
            content={
                "detail": "Rate limit exceeded",
                "retry_after": 60,  # seconds
                "limits": remaining
            },
            headers={
                "Retry-After": "60",
                "X-RateLimit-Limit-Minute": str(rate_limiter.requests_per_minute),
                "X-RateLimit-Limit-Hour": str(rate_limiter.requests_per_hour),
                "X-RateLimit-Remaining-Minute": str(remaining["minute_remaining"]),
                "X-RateLimit-Remaining-Hour": str(remaining["hour_remaining"]),
            }
        )
    
    # Add rate limit headers to response
    response = await call_next(request)
    
    # Get remaining requests for headers
    remaining = await rate_limiter.get_remaining_requests(client_ip, endpoint)
    
    response.headers["X-RateLimit-Limit-Minute"] = str(rate_limiter.requests_per_minute)
    response.headers["X-RateLimit-Limit-Hour"] = str(rate_limiter.requests_per_hour)
    response.headers["X-RateLimit-Remaining-Minute"] = str(remaining["minute_remaining"])
    response.headers["X-RateLimit-Remaining-Hour"] = str(remaining["hour_remaining"])
    
    return response
