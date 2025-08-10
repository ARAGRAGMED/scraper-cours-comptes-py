#!/usr/bin/env python3
"""
Security utilities for API authentication
"""

from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .config import settings

# HTTP Bearer scheme for API key authentication
security = HTTPBearer()

async def verify_api_key(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Verify the API key from the Authorization header"""
    if credentials.credentials != settings.api_key:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials

# Dependency for protected endpoints
def get_api_key(api_key: str = Depends(verify_api_key)):
    """Dependency to get verified API key"""
    return api_key
