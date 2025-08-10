#!/usr/bin/env python3
"""
Pydantic models for Court of Accounts data
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class PublicationBase(BaseModel):
    """Base publication model"""
    title: str = Field(..., description="Publication title")
    category: str = Field(..., description="Publication category")
    url: str = Field(..., description="Publication URL")
    date: Optional[str] = Field(None, description="Publication date")
    description: Optional[str] = Field(None, description="Publication description")

class Publication(PublicationBase):
    """Complete publication model"""
    id: Optional[str] = Field(None, description="Publication ID")
    year: Optional[int] = Field(None, description="Publication year")
    commission: Optional[str] = Field(None, description="Commission name")
    ministry: Optional[str] = Field(None, description="Ministry name")
    status: Optional[str] = Field(None, description="Publication status")
    file_size: Optional[str] = Field(None, description="File size if available")
    scraped_at: Optional[datetime] = Field(None, description="When it was scraped")

class ScrapingRequest(BaseModel):
    """Request model for starting scraping"""
    max_pages: Optional[int] = Field(10, description="Maximum pages to scrape")
    force_rescrape: Optional[bool] = Field(False, description="Force re-scraping")
    year: Optional[int] = Field(None, description="Specific year to scrape")

class ScrapingResponse(BaseModel):
    """Response model for scraping operations"""
    success: bool = Field(..., description="Whether scraping was successful")
    message: str = Field(..., description="Response message")
    publications_count: Optional[int] = Field(None, description="Number of publications scraped")
    file_path: Optional[str] = Field(None, description="Path to saved data file")
    execution_time: Optional[float] = Field(None, description="Execution time in seconds")

class PublicationsResponse(BaseModel):
    """Response model for publications data"""
    success: bool = Field(..., description="Whether request was successful")
    publications: List[Publication] = Field(..., description="List of publications")
    count: int = Field(..., description="Number of publications returned")

class SearchRequest(BaseModel):
    """Request model for searching publications"""
    query: str = Field(..., description="Search query")
    year: Optional[int] = Field(None, description="Filter by year")
    category: Optional[str] = Field(None, description="Filter by category")

class StatusResponse(BaseModel):
    """Response model for scraper status"""
    success: bool = Field(..., description="Whether request was successful")
    message: str = Field(..., description="Status message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional status details")
