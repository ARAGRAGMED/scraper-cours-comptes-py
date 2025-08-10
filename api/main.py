#!/usr/bin/env python3
"""
Main FastAPI application for Moroccan Court of Accounts Scraper API
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import os
from pathlib import Path

# Import routers with flexible imports for different environments
try:
    # Try package imports first (for Vercel)
    from api.routes import court_accounts
except ImportError:
    try:
        # Try relative imports (for local development)
        from routes import court_accounts
    except ImportError:
        # Fallback to direct imports
        import sys
        sys.path.append(os.path.dirname(__file__))
        from routes import court_accounts

# Create FastAPI app
app = FastAPI(
    title="Moroccan Court of Accounts Scraper API",
    description="API for scraping and retrieving Court of Accounts publications",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(court_accounts.router, prefix="/api")

# Root endpoint for the main page (serves the frontend directly)
@app.get("/")
async def main_page():
    """Main page endpoint - serves the frontend directly"""
    # Read the HTML file from public directory
    public_dir = Path(__file__).parent.parent / "public"
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
