#!/usr/bin/env python3
"""
Common API response models
"""

from typing import Optional, Any, Dict, List
from pydantic import BaseModel, Field

class BaseResponse(BaseModel):
    """Base response model"""
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Response message")
    data: Optional[Any] = Field(None, description="Response data")

class ErrorResponse(BaseModel):
    """Error response model"""
    success: bool = Field(False, description="Operation failed")
    error: str = Field(..., description="Error message")
    details: Optional[str] = Field(None, description="Error details")
    error_code: Optional[str] = Field(None, description="Error code")

class PaginatedResponse(BaseModel):
    """Paginated response model"""
    items: List[Any] = Field(..., description="List of items")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Items per page")
    pages: int = Field(..., description="Total number of pages")

class HealthResponse(BaseModel):
    """Health check response model"""
    status: str = Field(..., description="Service status")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="API version")
    timestamp: str = Field(..., description="Current timestamp")
