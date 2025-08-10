#!/usr/bin/env python3
"""
Configuration settings for the FastAPI application
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings"""
    
    # API Configuration
    api_title: str = "Moroccan Court of Accounts Scraper API"
    api_version: str = "1.0.0"
    api_description: str = "API for scraping and retrieving Court of Accounts publications"
    
    # Security
    api_key: str = os.getenv("API_KEY", "default_api_key_change_in_production")
    
    # Environment
    vercel_env: str = os.getenv("VERCEL_ENV", "development")
    debug: bool = os.getenv("VERCEL_ENV", "development") == "development"
    
    # Database (if using external)
    database_url: Optional[str] = os.getenv("DATABASE_URL")
    
    # Redis (if using Vercel KV)
    upstash_redis_rest_url: Optional[str] = os.getenv("UPSTASH_REDIS_REST_URL")
    upstash_redis_rest_token: Optional[str] = os.getenv("UPSTASH_REDIS_REST_TOKEN")
    
    # Scraper Configuration
    scraper_config_file: str = os.getenv("SCRAPER_CONFIG_FILE", "config/scraper_config.json")
    
    # Rate Limiting
    rate_limit_per_minute: int = 60
    
    # CORS
    cors_origins: list = ["*"]  # Configure as needed for production
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Create settings instance
settings = Settings()
