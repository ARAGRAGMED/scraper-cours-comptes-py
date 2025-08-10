#!/usr/bin/env python3
"""
Main API router for v1 endpoints
"""

from fastapi import APIRouter
from .endpoints import court_accounts

# Create main API router
api_router = APIRouter()

# Include endpoint routers
api_router.include_router(
    court_accounts.router,
    prefix="/court-accounts",
    tags=["Court of Accounts"]
)
