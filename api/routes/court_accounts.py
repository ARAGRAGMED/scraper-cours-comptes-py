#!/usr/bin/env python3
"""
Court of Accounts API routes
"""

from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
import json

router = APIRouter()

# Mock data for testing - we'll replace this with real service calls later
mock_publications = [
    {
        "id": 1,
        "title": "Test Publication 1",
        "category": "Rapport",
        "year": 2025,
        "url": "https://example.com/1"
    },
    {
        "id": 2,
        "title": "Test Publication 2", 
        "category": "Audit",
        "year": 2025,
        "url": "https://example.com/2"
    }
]

@router.get("/court-accounts/publications")
async def get_publications(
    year: Optional[int] = Query(None, description="Filter by year"),
    category: Optional[str] = Query(None, description="Filter by category")
):
    """Get publications with optional filtering"""
    try:
        publications = mock_publications
        
        if year:
            publications = [p for p in publications if p["year"] == year]
        if category:
            publications = [p for p in publications if p["category"] == category]
            
        return {
            "success": True,
            "publications": publications,
            "count": len(publications)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/court-accounts/categories")
async def get_available_categories():
    """Get available categories"""
    try:
        categories = list(set(p["category"] for p in mock_publications))
        return {"categories": categories}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/court-accounts/scrape")
async def start_scraping():
    """Start scraping publications"""
    try:
        return {
            "success": True,
            "message": "Scraping started successfully",
            "details": {"status": "running"}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/court-accounts/status")
async def get_scraping_status():
    """Get current scraping status"""
    try:
        return {
            "success": True,
            "message": "Status retrieved successfully",
            "details": {
                "is_running": False,
                "last_run": None,
                "publications_count": len(mock_publications)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
