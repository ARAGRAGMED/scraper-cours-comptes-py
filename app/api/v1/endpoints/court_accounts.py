#!/usr/bin/env python3
"""
Court of Accounts API endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, Query, HTTPException, Depends
from app.models.court_accounts import (
    ScrapingRequest, ScrapingResponse, PublicationsResponse, 
    SearchRequest, StatusResponse
)
from app.services.court_accounts_service import court_accounts_service
from app.core.security import get_api_key

router = APIRouter()

@router.post("/scrape", response_model=ScrapingResponse)
async def start_scraping(request: ScrapingRequest):
    """Start scraping publications from the Court of Accounts website"""
    try:
        result = await court_accounts_service.start_scraping(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stop", response_model=StatusResponse)
async def stop_scraping():
    """Stop ongoing scraping process"""
    try:
        result = await court_accounts_service.stop_scraping()
        return StatusResponse(
            success=True,
            message="Scraping stopped successfully",
            details=result
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status", response_model=StatusResponse)
async def get_scraping_status():
    """Get current scraping status"""
    try:
        status = await court_accounts_service.get_status()
        return StatusResponse(
            success=True,
            message="Status retrieved successfully",
            details=status
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/publications", response_model=PublicationsResponse)
async def get_publications(
    year: Optional[int] = Query(None, description="Filter by year"),
    category: Optional[str] = Query(None, description="Filter by category")
):
    """Get scraped publications with optional filtering"""
    try:
        publications = await court_accounts_service.get_publications(
            year=year, category=category
        )
        return PublicationsResponse(
            success=True,
            publications=publications,
            count=len(publications)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/publications/{year}", response_model=PublicationsResponse)
async def get_publications_by_year(
    year: int,
    category: Optional[str] = Query(None, description="Filter by category")
):
    """Get publications for a specific year"""
    try:
        publications = await court_accounts_service.get_publications(year, category)
        return PublicationsResponse(
            success=True,
            publications=publications,
            count=len(publications)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/publications/category/{category}", response_model=PublicationsResponse)
async def get_publications_by_category(
    category: str,
    year: Optional[int] = Query(None, description="Filter by year")
):
    """Get publications filtered by category"""
    try:
        publications = await court_accounts_service.get_publications(category=category)
        return PublicationsResponse(
            success=True,
            publications=publications,
            count=len(publications)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search", response_model=PublicationsResponse)
async def search_publications(request: SearchRequest):
    """Search publications by query"""
    try:
        publications = await court_accounts_service.search_publications(request.query)
        return PublicationsResponse(
            success=True,
            publications=publications,
            count=len(publications)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/categories")
async def get_available_categories():
    """Get list of available publication categories"""
    try:
        categories = await court_accounts_service.get_available_categories()
        return {"categories": categories}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
