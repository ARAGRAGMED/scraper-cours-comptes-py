#!/usr/bin/env python3
"""
FastAPI Application for Moroccan Court of Accounts Scraper
Main entry point for Vercel deployment
"""

import os
import sys
from pathlib import Path

# Add the src directory to the Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from .api.v1.api import api_router
from .core.config import settings

# Create FastAPI app
app = FastAPI(
    title="Moroccan Court of Accounts Scraper API",
    description="API for scraping and retrieving Court of Accounts publications",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure as needed for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api/v1")

# Mount static files from public directory
app.mount("/", StaticFiles(directory="public", html=True), name="static")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Court of Accounts Scraper API"}

@app.get("/favicon.ico")
async def favicon():
    """Serve favicon"""
    return FileResponse("public/favicon.ico")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Court of Accounts Scraper API"}

# For local development
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
