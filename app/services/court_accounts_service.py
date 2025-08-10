#!/usr/bin/env python3
"""
Service layer for Court of Accounts scraping operations
"""

import time
import sys
import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

# Add the src directory to the Python path
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

from moroccan_parliament_scraper.core.court_accounts_scraper import CourtOfAccountsScraper
from app.models.court_accounts import ScrapingRequest, ScrapingResponse, Publication

class CourtAccountsService:
    """Service for Court of Accounts scraping operations"""
    
    def __init__(self):
        self.scraper = None
        self.is_running = False
        self.last_run = None
        self.last_run_duration = None
        self.last_scraped_data = []  # Store last scraped data in memory
        self._load_existing_data()  # Load existing data from JSON file
    
    def _load_existing_data(self):
        """Load existing publications data from JSON file"""
        try:
            data_file = Path(__file__).parent.parent.parent / "data" / "court-accounts-publications-2025.json"
            if data_file.exists():
                with open(data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if 'data' in data and isinstance(data['data'], list):
                        self.last_scraped_data = data['data']
                        print(f"Loaded {len(self.last_scraped_data)} publications from existing data file")
        except Exception as e:
            print(f"Error loading existing data: {e}")
            self.last_scraped_data = []
    
    def _refresh_data_from_file(self):
        """Refresh publications data from JSON file"""
        self._load_existing_data()

    async def start_scraping(self, request: ScrapingRequest) -> ScrapingResponse:
        """Start scraping with the given parameters"""
        if self.is_running:
            return ScrapingResponse(
                success=False,
                message="Scraping is already running"
            )
        
        try:
            self.is_running = True
            start_time = time.time()
            
            # Create scraper instance
            self.scraper = CourtOfAccountsScraper(
                force_rescrape=request.force_rescrape
            )
            
            # Run the scraper
            success = self.scraper.run(
                max_pages=request.max_pages
            )
            
            execution_time = time.time() - start_time
            self.last_run = datetime.now()
            self.last_run_duration = execution_time
            
            if success:
                # Store results in memory
                self.last_scraped_data = self.scraper.results
                
                return ScrapingResponse(
                    success=True,
                    message="Scraping completed successfully",
                    publications_count=len(self.last_scraped_data),
                    file_path="Data stored in memory",
                    execution_time=execution_time
                )
            else:
                return ScrapingResponse(
                    success=False,
                    message="Scraping failed",
                    execution_time=execution_time
                )
                
        except Exception as e:
            return ScrapingResponse(
                success=False,
                message=f"Scraping error: {str(e)}"
            )
        finally:
            self.is_running = False
            self.scraper = None
    
    async def stop_scraping(self) -> Dict[str, Any]:
        """Stop the currently running scraper"""
        if not self.is_running:
            return {
                "success": False,
                "message": "No scraping is currently running"
            }
        
        try:
            # For now, we can't easily stop the scraper mid-process
            # This would require implementing a stop mechanism in the scraper
            self.is_running = False
            self.scraper = None
            
            return {
                "success": True,
                "message": "Scraping stopped"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error stopping scraper: {str(e)}"
            }
    
    async def get_publications(self, year: Optional[int] = None, category: Optional[str] = None) -> List[Publication]:
        """Get publications from memory (last scraped data) or from file if needed"""
        # If no data in memory, try to load from file
        if not self.last_scraped_data:
            self._refresh_data_from_file()
        
        if not self.last_scraped_data:
            return []
        
        publications = self.last_scraped_data.copy()
        
        # Filter by year if specified
        if year:
            publications = [pub for pub in publications if pub.get('year') == year]
        
        # Filter by category if specified
        if category:
            publications = [pub for pub in publications if pub.get('category') == category]
        
        # Convert to Publication models
        result = []
        for pub in publications:
            try:
                pub_model = Publication(
                    id=pub.get('id'),
                    title=pub.get('title', ''),
                    category=pub.get('category', ''),
                    url=pub.get('url', ''),
                    date=pub.get('date'),
                    description=pub.get('description'),
                    year=pub.get('year'),
                    commission=pub.get('commission'),
                    ministry=pub.get('ministry'),
                    status=pub.get('status'),
                    file_size=pub.get('file_size'),
                    scraped_at=pub.get('scraped_at')
                )
                result.append(pub_model)
            except Exception as e:
                # Skip invalid publications
                print(f"Error processing publication: {e}")
                continue
        
        return result
    
    async def search_publications(self, query: str, year: Optional[int] = None, category: Optional[str] = None) -> List[Publication]:
        """Search publications by query"""
        # If no data in memory, try to load from file
        if not self.last_scraped_data:
            self._refresh_data_from_file()
        
        if not self.last_scraped_data:
            return []
        
        publications = self.last_scraped_data.copy()
        
        # Filter by query
        query_lower = query.lower()
        publications = [pub for pub in publications if 
                       query_lower in pub.get('title', '').lower() or
                       query_lower in pub.get('category', '').lower() or
                       query_lower in pub.get('description', '').lower()]
        
        # Filter by year if specified
        if year:
            publications = [pub for pub in publications if pub.get('year') == year]
        
        # Filter by category if specified
        if category:
            publications = [pub for pub in publications if pub.get('category') == category]
        
        # Convert to Publication models
        result = []
        for pub in publications:
            try:
                pub_model = Publication(
                    id=pub.get('id'),
                    title=pub.get('title', ''),
                    category=pub.get('category', ''),
                    url=pub.get('url', ''),
                    date=pub.get('date'),
                    description=pub.get('description'),
                    year=pub.get('year'),
                    commission=pub.get('commission'),
                    ministry=pub.get('ministry'),
                    status=pub.get('status'),
                    file_size=pub.get('file_size'),
                    scraped_at=pub.get('scraped_at')
                )
                result.append(pub_model)
            except Exception as e:
                # Skip invalid publications
                print(f"Error processing publication: {e}")
                continue
        
        return result
    
    async def get_status(self) -> Dict[str, Any]:
        """Get current scraping status"""
        if not self.last_scraped_data:
            self._refresh_data_from_file()
        
        return {
            "is_running": self.is_running,
            "last_run": self.last_run.isoformat() if self.last_run else None,
            "last_run_duration": self.last_run_duration,
            "publications_count": len(self.last_scraped_data),
            "scraper_instance": self.scraper is not None
        }
    
    async def get_available_categories(self) -> List[str]:
        """Get available categories from actual publications data"""
        # If no data in memory, try to load from file
        if not self.last_scraped_data:
            self._refresh_data_from_file()
        
        if not self.last_scraped_data:
            # Try to get categories from file metadata
            try:
                data_file = Path(__file__).parent.parent.parent / "data" / "court-accounts-publications-2025.json"
                if data_file.exists():
                    with open(data_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if 'publication_categories' in data and isinstance(data['publication_categories'], list):
                            return sorted(data['publication_categories'])
            except Exception as e:
                print(f"Error reading categories from file metadata: {e}")
            return []
        
        # Extract unique categories from publications
        categories = set()
        for pub in self.last_scraped_data:
            if pub.get('category'):
                categories.add(pub['category'])
        
        # Sort categories alphabetically
        return sorted(list(categories))

# Create global service instance
court_accounts_service = CourtAccountsService()
