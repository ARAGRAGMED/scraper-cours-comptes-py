#!/usr/bin/env python3
"""
Main FastAPI application for Moroccan Court of Accounts Scraper API
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import os
import sys
from pathlib import Path

# Add the current directory to Python path for local development
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Import routers with flexible imports for different environments
try:
    # Try relative imports (for local development)
    from routes import court_accounts
    print("✅ Successfully imported court_accounts from routes")
except ImportError as e:
    print(f"❌ Error importing from routes: {e}")
    try:
        # Try package imports (for Vercel)
        from api.routes import court_accounts
        print("✅ Successfully imported court_accounts from api.routes")
    except ImportError as e2:
        print(f"❌ Error importing from api.routes: {e2}")
        # Create a minimal router for testing
        from fastapi import APIRouter
        court_accounts = APIRouter()
        print("⚠️ Using fallback router")

# Create FastAPI app
app = FastAPI(
    title="Moroccan Court of Accounts Scraper API",
    description="API for scraping and retrieving Court of Accounts publications",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (CSS, JS, images)
public_dir = Path(__file__).parent.parent / "public"
app.mount("/css", StaticFiles(directory=str(public_dir / "css")), "css")
app.mount("/js", StaticFiles(directory=str(public_dir / "js")), "js")

# Include API routers
app.include_router(court_accounts.router, prefix="/api")
print(f"✅ Router included: {court_accounts.router}")

# Root endpoint for the main page (serves the frontend directly)
@app.get("/")
async def main_page():
    """Main page endpoint - serves the frontend directly"""
    # Read the HTML file from public directory
    html_file = public_dir / "index.html"
    
    if html_file.exists():
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        return HTMLResponse(content=html_content, status_code=200)
    else:
        return HTMLResponse(content="<h1>Frontend not found</h1>", status_code=404)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Court of Accounts Scraper API"}

# Test endpoint
@app.get("/test")
async def test():
    """Test endpoint"""
    return {"message": "Test endpoint working!"}

# Docs redirect endpoint
@app.get("/docs")
async def docs_redirect():
    """Redirect to FastAPI docs"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/docs")

# API info endpoint
@app.get("/api")
async def api_info():
    """API information and available endpoints"""
    return {
        "title": "Moroccan Court of Accounts Scraper API",
        "version": "1.0.0",
        "description": "API for scraping and retrieving Court of Accounts publications",
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json",
            "health": "/health",
            "test": "/test",
            "api": "/api",
            "court_accounts": {
                "publications": "/api/court-accounts/publications",
                "categories": "/api/court-accounts/categories",
                "scrape": "/api/court-accounts/scrape",
                "status": "/api/court-accounts/status"
            }
        }
    }
