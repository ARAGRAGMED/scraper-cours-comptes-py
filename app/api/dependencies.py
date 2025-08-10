#!/usr/bin/env python3
"""
Shared API dependencies
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from ..core.config import settings

# HTTP Bearer scheme
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user from API key"""
    if credentials.credentials != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"api_key": credentials.credentials}

# Rate limiting dependency (simple implementation)
class RateLimiter:
    def __init__(self, max_requests: int = 60):
        self.max_requests = max_requests
        self.requests = {}
    
    async def check_rate_limit(self, client_id: str = "default"):
        """Check if client has exceeded rate limit"""
        import time
        current_time = time.time()
        
        if client_id not in self.requests:
            self.requests[client_id] = []
        
        # Remove old requests (older than 1 minute)
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id] 
            if current_time - req_time < 60
        ]
        
        if len(self.requests[client_id]) >= self.max_requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Try again later."
            )
        
        self.requests[client_id].append(current_time)
        return True

# Create rate limiter instance
rate_limiter = RateLimiter(settings.rate_limit_per_minute)

async def check_rate_limit():
    """Dependency to check rate limiting"""
    return await rate_limiter.check_rate_limit()
