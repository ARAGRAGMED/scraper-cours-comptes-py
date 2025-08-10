#!/usr/bin/env python3
"""
Vercel serverless function entry point
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse

# Create a minimal FastAPI app for testing
app = FastAPI(title="Court Accounts Scraper API")

@app.get("/")
async def root():
    return {"message": "Court Accounts Scraper API is running!"}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "Court Accounts Scraper API"}

@app.get("/test")
async def test():
    return {"message": "Test endpoint working!"}

# Export the app for Vercel
handler = app
