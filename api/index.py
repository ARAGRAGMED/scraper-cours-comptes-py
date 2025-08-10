#!/usr/bin/env python3
"""
Vercel serverless function entry point
"""

import sys
from pathlib import Path

# Add the app directory to the Python path
app_path = Path(__file__).parent.parent / "app"
sys.path.insert(0, str(app_path))

# Import the FastAPI app
from main import app

# Export the app for Vercel
handler = app
