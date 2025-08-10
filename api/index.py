#!/usr/bin/env python3
"""
Vercel serverless function entry point
"""

import json

def handler(request, context):
    """Vercel Python handler function"""
    
    # Get the path from the request
    path = request.get('path', '/')
    
    # Simple routing
    if path == '/':
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Court Accounts Scraper API is running!"}),
            "headers": {"Content-Type": "application/json"}
        }
    elif path == '/health':
        return {
            "statusCode": 200,
            "body": json.dumps({"status": "healthy", "service": "Court Accounts Scraper API"}),
            "headers": {"Content-Type": "application/json"}
        }
    elif path == '/test':
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Test endpoint working!"}),
            "headers": {"Content-Type": "application/json"}
        }
    else:
        return {
            "statusCode": 404,
            "body": json.dumps({"error": "Not found"}),
            "headers": {"Content-Type": "application/json"}
        }
