#!/usr/bin/env python3
"""
Court of Accounts API routes
"""

from fastapi import APIRouter, Query, HTTPException, Body
from typing import List, Optional, Dict, Any
import json
from pathlib import Path
import sys
import os

router = APIRouter()

# Add the app directory to Python path for importing services
app_path = Path(__file__).parent.parent.parent / "app"
sys.path.insert(0, str(app_path))

def load_publications_data():
    """Load publications data from JSON file"""
    try:
        # Get the path to the data file relative to the project root
        data_file = Path(__file__).parent.parent.parent / "data" / "court-accounts-publications-2025.json"
        
        if not data_file.exists():
            print(f"⚠️ Data file not found: {data_file}")
            return []
            
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Extract publications from the data structure
        publications = data.get('data', [])
        print(f"✅ Loaded {len(publications)} publications from JSON file")
        return publications
        
    except Exception as e:
        print(f"❌ Error loading publications data: {e}")
        return []

async def get_scraper_service():
    """Get the Court of Accounts scraper service"""
    try:
        from services.court_accounts_service import CourtAccountsService
        return CourtAccountsService()
    except ImportError as e:
        print(f"❌ Error importing CourtAccountsService: {e}")
        return None

@router.get("/court-accounts/publications")
async def get_publications(
    year: Optional[int] = Query(None, description="Filter by year"),
    category: Optional[str] = Query(None, description="Filter by category")
):
    """Get publications with optional filtering"""
    try:
        publications = load_publications_data()
        
        if year:
            publications = [p for p in publications if p.get("year") == year]
        if category:
            publications = [p for p in publications if p.get("category") == category]
            
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
        publications = load_publications_data()
        categories = list(set(p.get("category", "") for p in publications if p.get("category")))
        return {"categories": categories}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/court-accounts/scrape")
async def start_scraping(request_data: Dict[str, Any] = Body(default=None)):
    """Start live scraping of Court of Accounts publications"""
    try:
        # Get the scraper service
        service = await get_scraper_service()
        if not service:
            return {
                "success": False,
                "message": "Failed to initialize scraper service",
                "details": {"status": "error"}
            }
        
        # Check if scraping is already running
        if service.is_running:
            return {
                "success": False,
                "message": "Scraping is already running",
                "details": {"status": "running"}
            }
        
        # Start the actual scraping process
        print("🚀 Starting live scraping...")
        
        # Use request data from frontend or defaults
        max_pages = request_data.get('max_pages', 10) if request_data else 10
        force_rescrape = request_data.get('force_rescrape', True) if request_data else True
        
        print(f"📊 Scraping parameters: max_pages={max_pages}, force_rescrape={force_rescrape}")
        
        # Create a scraping request with user parameters
        from app.models.court_accounts import ScrapingRequest
        request = ScrapingRequest(
            max_pages=max_pages,
            force_rescrape=force_rescrape
        )
        
        # Run the scraper
        print("🔄 Running scraper...")
        response = await service.start_scraping(request)
        
        if response.success:
            print(f"✅ Scraping completed! Found {response.publications_count} publications")
            print(f"📊 Response details: {response}")
            return {
                "success": True,
                "message": f"Scraping completed! Found {response.publications_count} publications.",
                "publications_count": response.publications_count,
                "details": {"status": "completed"}
            }
        else:
            print(f"❌ Scraping failed: {response.message}")
            return {
                "success": False,
                "message": f"Scraping failed: {response.message}",
                "details": {"status": "failed"}
            }
            
    except Exception as e:
        print(f"❌ Error during scraping: {e}")
        return {
            "success": False,
            "message": f"Scraping error: {str(e)}",
            "details": {"status": "error"}
        }

@router.get("/court-accounts/status")
async def get_scraping_status():
    """Get current scraping status"""
    try:
        publications = load_publications_data()
        return {
            "success": True,
            "message": "Status retrieved successfully",
            "details": {
                "is_running": False,
                "last_run": None,
                "publications_count": len(publications)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
