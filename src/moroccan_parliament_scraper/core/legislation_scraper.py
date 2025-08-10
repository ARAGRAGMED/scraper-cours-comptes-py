#!/usr/bin/env python3
"""
Moroccan Parliament Legislation Scraper
Enhanced with configuration management and proxy support
"""

import requests
import json
import csv
import re
import time
import os
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from ..utils.config_manager import ConfigManager

class MoroccanParliamentScraper:
    """Enhanced scraper with configuration management and proxy support"""
    
    def __init__(self, force_rescrape=None, config_file="config/scraper_config.json"):
        """Initialize scraper with configuration"""
        self.config = ConfigManager(config_file)
        
        # Use config settings or override with parameters
        self.force_rescrape = force_rescrape if force_rescrape is not None else self.config.get('scraper_settings.force_rescrape', False)
        self.enable_logs = self.config.get('scraper_settings.enable_logs', True)
        
        # Initialize session with proxy support
        self.session = self._create_session()
        
        # Base URLs
        self.base_url = "https://www.chambredesrepresentants.ma"
        self.legislation_url = f"{self.base_url}/fr/legislation/projets-de-loi"
        
        # Current year info
        self.current_year = None
        self.current_year_id = None
        
        # Results storage
        self.results = []
        
        # Proxy rotation
        self.current_proxy_index = 0
        
        # Show configuration summary if logs are enabled
        if self.enable_logs:
            self.config.print_config_summary()
    
    def _create_session(self):
        """Create requests session with proxy support"""
        session = requests.Session()
        
        # Set user agent
        user_agent = self.config.get('request_settings.user_agent')
        session.headers.update({
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Set up proxy if enabled
        if self.config.get('proxy_settings.enable_proxies', False):
            proxies = self.config.get_proxies()
            if proxies:
                current_proxy = proxies[self.current_proxy_index % len(proxies)]
                session.proxies.update(current_proxy)
                if self.enable_logs:
                    print(f"🌐 Using proxy: {current_proxy}")
        
        return session
    
    def _rotate_proxy(self):
        """Rotate to next proxy if enabled"""
        if self.config.get('proxy_settings.enable_proxies', False) and self.config.get('proxy_settings.proxy_rotation', True):
            proxies = self.config.get_proxies()
            if proxies:
                self.current_proxy_index += 1
                current_proxy = proxies[self.current_proxy_index % len(proxies)]
                self.session.proxies.update(current_proxy)
                self._log(f"🔄 Rotated to proxy: {current_proxy}", "debug")
    
    def _make_request(self, url, params=None, retry_count=0):
        """Make HTTP request with retry logic and proxy rotation"""
        max_retries = self.config.get('request_settings.retry_attempts', 3)
        timeout = self.config.get('request_settings.timeout', 30)
        
        # Use proxy timeout if proxies are enabled, otherwise use regular timeout
        if self.config.get('proxy_settings.enable_proxies', False):
            proxy_timeout = self.config.get('proxy_settings.proxy_timeout', 10)
            # Use the shorter timeout to avoid hanging on slow proxies
            timeout = min(timeout, proxy_timeout)
            self._log(f"🔧 Using proxy timeout: {timeout}s (proxy_timeout: {proxy_timeout}s, request_timeout: {self.config.get('request_settings.timeout', 30)}s)", "debug")
        
        try:
            response = self.session.get(url, params=params, timeout=timeout)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            if retry_count < max_retries:
                self._log(f"⚠️  Request failed (attempt {retry_count + 1}/{max_retries}): {e}", "warning")
                
                # Rotate proxy on failure
                self._rotate_proxy()
                
                # Wait before retry
                time.sleep(2)
                return self._make_request(url, params, retry_count + 1)
            else:
                self._log(f"❌ Request failed after {max_retries} attempts: {e}", "error")
                raise
    
    def _log(self, message: str, log_type: str = "progress"):
        """Log message if logging is enabled for the specific type"""
        if self.enable_logs and self.config.should_show_log(log_type):
            print(message)
    
    def get_current_legislative_year(self):
        """Get the current legislative year and its ID from the form"""
        try:
            self._log("🔍 Identifying current legislative year...", "progress")
            
            response = self._make_request(self.legislation_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the year select element
            year_select = soup.find('select', {'name': 'field_annee_legislative_target_id'})
            if not year_select:
                self._log("❌ Could not find year select element", "progress")
                return False
            
            # Get the first (current) year option
            year_options = year_select.find_all('option')
            if not year_options:
                self._log("❌ No year options found", "progress")
                return False
            
            # Find the current year (skip "All" options)
            current_year_option = None
            for option in year_options:
                value = option.get('value', '')
                text = option.get_text(strip=True)
                
                # Skip the "All" option
                if value == 'All' or text == '- Tout -':
                    continue
                
                # The first non-"All" option is usually the current year
                current_year_option = option
                break
            
            if current_year_option:
                self.current_year = current_year_option.get_text(strip=True)
                self.current_year_id = current_year_option.get('value')
            else:
                # Fallback to current year if no valid option found
                from datetime import datetime
                current_year = datetime.now().year
                self.current_year = f"{current_year}-{current_year + 1}"
                self.current_year_id = str(current_year)
            
            self._log(f"✅ Current legislative year: {self.current_year} (ID: {self.current_year_id})", "progress")
            return True
            
        except Exception as e:
            self._log(f"❌ Error getting current year: {e}", "progress")
            return False
    
    def scrape_current_year_legislation(self, max_pages=None):
        """Scrape current year legislation with source identification"""
        # Define commission approaches to try
        commission_approaches = [
            {'commissions_id': 'All', 'description': 'All commissions'},
            {'commissions_id': '63', 'description': 'Commission des Pétitions'},
            {'commissions_id': '64', 'description': 'Commission des affaires étrangères, de la défense nationale, des affaires islamiques, des affaires de la migration et des MRE'},
            {'commissions_id': '65', 'description': 'Commission de l\'intérieur, des collectivités territoriales, de l\'habitat, de la politique de la ville et des affaires administratives'},
            {'commissions_id': '66', 'description': 'Commission de justice, de législation, des droits de l\'homme et des libertés'},
            {'commissions_id': '67', 'description': 'Commission des finances et du développement économique'},
            {'commissions_id': '68', 'description': 'Commission des secteurs sociaux'},
            {'commissions_id': '69', 'description': 'Commission des secteurs productifs'},
            {'commissions_id': '70', 'description': 'Commission des infrastructures, de l\'énergie, des mines, de l\'environnement et du développement durable'},
            {'commissions_id': '71', 'description': 'Commission de l\'enseignement, de la culture et de la communication'},
            {'commissions_id': '72', 'description': 'Commission du contrôle des finances publiques et de la gouvernance'},
        ]
        
        # Define ministry approaches to try
        ministry_approaches = [
            {'ministry_id': 'All', 'description': 'All ministries'},
            {'ministry_id': '1', 'description': 'Economie et finances'},
            {'ministry_id': '2', 'description': 'Éducation nationale'},
            {'ministry_id': '3', 'description': 'Énergie et mines'},
            {'ministry_id': '4', 'description': 'Équipement et transport'},
            {'ministry_id': '5', 'description': 'Habous et des affaires islamiques'},
            {'ministry_id': '6', 'description': 'Emploi et formation professionnelle'},
            {'ministry_id': '7', 'description': 'Enseignement supérieur, recherche scientifique et formation des cadres'},
            {'ministry_id': '8', 'description': 'Agriculture et pêche maritime'},
            {'ministry_id': '9', 'description': 'Chef du Gouvernement'},
            {'ministry_id': '10', 'description': 'Communication'},
            {'ministry_id': '11', 'description': 'Culture'},
            {'ministry_id': '12', 'description': 'Affaires étrangères et coopération'},
            {'ministry_id': '13', 'description': 'Artisanat'},
            {'ministry_id': '14', 'description': 'Énergie, mines, eau et environnement'},
            {'ministry_id': '15', 'description': 'Secrétariat Général du Gouvernement'},
            {'ministry_id': '16', 'description': 'Habitat, urbanisme et politique de la ville'},
            {'ministry_id': '17', 'description': 'Santé'},
            {'ministry_id': '18', 'description': 'Industrie, commerce et nouvelles technologies'},
            {'ministry_id': '19', 'description': 'Intérieur'},
            {'ministry_id': '20', 'description': 'Jeunesse et sports'},
            {'ministry_id': '21', 'description': 'Justice et libertés'},
            {'ministry_id': '22', 'description': 'Ministre de l\'industrie, du commerce, de l\'investissement et de l\'économie numérique'},
            {'ministry_id': '23', 'description': 'Ministre de l\'éducation nationale et de la formation professionnelle'},
            {'ministry_id': '24', 'description': 'Ministre de l\'équipement, du transport et de la logistique'},
            {'ministry_id': '25', 'description': 'Ministre de l\'habitat et de la politique de la ville'},
            {'ministry_id': '26', 'description': 'Ministre de l\'emploi et des affaires sociales'},
            {'ministry_id': '27', 'description': 'Ministre de l\'artisanat et de l\'économie sociale et solidaire'},
            {'ministry_id': '28', 'description': 'Ministre chargé des marocains résidant à l\'étranger et des affaires de la migration'},
            {'ministry_id': '29', 'description': 'Ministre de l\'urbanisme et de l\'aménagement du territoire national'},
            {'ministry_id': '30', 'description': 'Ministre chargé des relations avec le Parlement et la société civile'},
            {'ministry_id': '31', 'description': 'Solidarité, femme, famille et développement social'},
            {'ministry_id': '32', 'description': 'Tourisme'},
        ]
        
        # Try different commission filters to find current year legislation
        for commission in commission_approaches:
            self._log(f"\n🔍 Checking Commission: {commission['description']}", "commission_checks")
            self._log("─" * 50, "commission_checks")
            
            commission_results = []
            page = 1
            found_urls = set()  # Track URLs to avoid duplicates within commission
            
            while True:  # Continue until no more pages
                self._log(f"📄 Processing page {page}...", "commission_checks")
                
                try:
                    params = {
                        'commissions_id': commission['commissions_id'],
                        'field_ministeres_new_target_id': 'All',
                        'field_annee_legislative_target_id': self.current_year_id,
                        'page': page - 1  # Zero-based pagination
                    }
                    
                    response = self._make_request(self.legislation_url, params)
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Check if page has content
                    no_content = soup.find(string=lambda text: text and 'Il n\' y a pas de contenu' in text)
                    if no_content:
                        self._log(f"⚠️  No content found with {commission['description']}", "commission_checks")
                        break
                    
                    # Extract legislation items
                    legislation_items = self.extract_legislation_items(soup)
                    
                    if legislation_items:
                        self._log(f"📋 Found {len(legislation_items)} items on page {page}", "commission_checks")
                        
                        for item in legislation_items:
                            legislation_data = self.extract_legislation_data(item)
                            
                            if legislation_data:
                                # Check if this URL is already found (avoid duplicates)
                                item_url = legislation_data.get('url', '')
                                if item_url and item_url not in found_urls:
                                    found_urls.add(item_url)
                                    
                                    # Check if this law number already exists in our data
                                    law_number = legislation_data.get('law_number', '')
                                    if law_number and self.check_existing_data(law_number):
                                        self._log(f"⏭️  Skipping law {law_number} - already exists", "commission_checks")
                                        continue
                                    
                                    # Extract detailed information from the legislation page
                                    self._log(f"🔍 Extracting details for law {law_number}...", "detailed_extraction")
                                    page_details = self.extract_legislation_page_details(item_url, legislation_data.get('title', ''))
                                    
                                    if page_details:
                                        # Merge page details with legislation data
                                        legislation_data.update(page_details)
                                    
                                    legislation_data.update({
                                        'page': page,
                                        'scraped_at': datetime.now().isoformat(),
                                        'commission': commission['description'],
                                        'commission_id': commission['commissions_id'],
                                        'ministry': 'To be identified',
                                        'ministry_id': 'To be identified'
                                    })
                                    commission_results.append(legislation_data)
                                    
                                    self._log(f"✅ Extracted detailed data for law {law_number}", "detailed_extraction")
                                    
                                    # Be respectful with delays
                                    delay = self.config.get('request_settings.delay_between_requests', 2)
                                    time.sleep(delay)
                        
                        self._log(f"✅ Added {len(commission_results)} unique items from {commission['description']}", "commission_checks")
                    else:
                        self._log(f"⚠️  No items found on page {page}", "commission_checks")
                    
                    # Check for more pages
                    has_more_pages = self.check_pagination(soup)
                    
                    page += 1
                    delay = self.config.get('request_settings.delay_between_requests', 2)
                    time.sleep(delay)  # Be respectful
                    
                except Exception as e:
                    self._log(f"❌ Error scraping page {page}: {e}", "commission_checks")
                    break
            
            # Add commission results to main results
            if commission_results:
                self.results.extend(commission_results)
                self._log(f"✅ Found {len(commission_results)} items from {commission['description']}", "commission_checks")
            else:
                self._log(f"📭 No items found for {commission['description']}", "commission_checks")
        
        # Now identify the ministry for each found legislation item
        if self.results:
            self._log(f"\n🔍 Identifying ministries for {len(self.results)} legislation items...", "ministry_checks")
            self._log("-" * 50, "ministry_checks")
            
            # Create a mapping of legislation URLs to their data
            legislation_map = {leg.get('url', ''): leg for leg in self.results if leg.get('url')}
            
            # Check each ministry to see which legislation items it contains
            for ministry in ministry_approaches:
                self._log(f"🔍 Checking Ministry: {ministry['description']}...", "ministry_checks")
                
                params = {
                    'commissions_id': 'All',
                    'field_ministeres_new_target_id': ministry['ministry_id'],
                    'field_annee_legislative_target_id': self.current_year_id,
                    'page': 0
                }
                
                try:
                    response = self._make_request(self.legislation_url, params)
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Check if page has content
                    no_content = soup.find(string=lambda text: text and 'Il n\' y a pas de contenu' in text)
                    if no_content:
                        self._log(f"⚠️  No content found with {ministry['description']}", "ministry_checks")
                        continue
                    
                    # Find all legislation links on this page
                    legislation_links = soup.find_all('a', href=True)
                    
                    # Check which of our found legislation items appear in this ministry
                    for link in legislation_links:
                        href = link.get('href', '')
                        if href in legislation_map:
                            legislation = legislation_map[href]
                            legislation['ministry'] = ministry['description']
                            legislation['ministry_id'] = ministry['ministry_id']
                            self._log(f"✅ Identified ministry for {legislation.get('law_number', 'Unknown')}: {ministry['description']}", "ministry_checks")
                    
                    delay = self.config.get('request_settings.delay_between_requests', 2)
                    time.sleep(delay)  # Be respectful
                    
                except Exception as e:
                    self._log(f"❌ Error checking ministry {ministry['description']}: {e}", "ministry_checks")
                    continue
        else:
            self._log("\n📭 No legislation items found to process", "ministry_checks")
        
        return True
    
    def extract_legislation_items(self, soup):
        """Extract legislation items from the page"""
        # Look for legislation links in the content area
        legislation_links = soup.find_all('a', href=re.compile(r'/fr/.*projet-de-loi.*'))
        
        # Filter out navigation and other non-legislation links
        filtered_links = []
        for link in legislation_links:
            href = link.get('href', '')
            # Only include links that look like legislation pages
            if 'projet-de-loi' in href and not any(skip in href for skip in ['/node/', '/user/', '/admin/']):
                filtered_links.append(link)
        
        return filtered_links
    
    def extract_legislation_data(self, item):
        """Extract basic legislation data from a listing item"""
        try:
            # Get the link
            link = item.get('href', '')
            if not link:
                return None
            
            # Make it absolute URL
            url = urljoin(self.base_url, link)
            
            # Extract title
            title = item.get_text(strip=True)
            if not title:
                return None
            
            # Clean title and extract law number
            clean_title = self.clean_title(title)
            law_number = self.extract_law_number(title)
            
            return {
                'url': url,
                'title': clean_title,
                'law_number': law_number,
                'full_title': title
            }
            
        except Exception as e:
            if self.enable_logs:
                print(f"❌ Error extracting legislation data: {e}")
            return None
    
    def clean_title(self, title):
        """Clean the title by removing extra whitespace and formatting"""
        # Remove extra whitespace
        cleaned = ' '.join(title.split())
        return cleaned
    
    def extract_law_number(self, text):
        """Extract law number from text"""
        # Look for patterns like N°03.25, N° 03.25, etc.
        patterns = [
            r'N°\s*(\d+\.\d+)',
            r'N°\s*(\d+/\d+)',
            r'(\d+\.\d+)',
            r'(\d+/\d+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        
        return ''
    
    def check_pagination(self, soup):
        """Check if there are more pages"""
        # Look for pagination elements
        pagination = soup.find('nav', class_='pager') or soup.find('ul', class_='pager')
        
        if pagination:
            # Look for "next" or "suivant" links
            next_links = soup.find_all('a', href=True, string=lambda x: x and any(term in x.lower() for term in ['next', 'suivant', '>']))
            return len(next_links) > 0
        
        return False
    
    def save_results(self, format='json'):
        """Save results to file"""
        if not self.results:
            self._log("❌ No results to save", "progress")
            return None
        
        # Extract year from current_year (e.g., "2024-2025" -> "2025")
        year = self.current_year.split('-')[-1] if self.current_year else datetime.now().year
        
        # Ensure data directory exists
        data_dir = "data"
        os.makedirs(data_dir, exist_ok=True)
        
        if format == 'json':
            filename = os.path.join(data_dir, f"extracted-data-{year}.json")
            
            # Prepare enhanced metadata
            metadata = {
                'current_year': self.current_year,
                'current_year_id': self.current_year_id,
                'total_items': len(self.results),
                'scraped_at': datetime.now().isoformat(),
                'commission_used': 'Multiple commissions identified',
                'data_extraction_level': 'Enhanced with page details and PDF links',
                'pdf_links': 'Available in pdf_url field for each legislation',
                'duplicate_checking': 'Enabled',
                'data': self.results
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        elif format == 'csv':
            filename = os.path.join(data_dir, f"extracted-data-{year}.csv")
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                if self.results:
                    writer = csv.DictWriter(f, fieldnames=self.results[0].keys())
                    writer.writeheader()
                    writer.writerows(self.results)
        
        self._log(f"\n💾 Saving results...", "progress")
        self._log(f"✅ Results saved to {filename}", "progress")
        self._log(f"📊 File contains {len(self.results)} legislation items", "progress")
        return filename
    
    def print_summary(self):
        """Print a summary of the results"""
        self._log("\n" + "="*60, "progress")
        self._log("🎉 SCRAPING COMPLETE!", "progress")
        self._log("="*60, "progress")
        
        if not self.results:
            self._log("📭 No results to display", "progress")
            return
        
        self._log(f"📊 Total items scraped: {len(self.results)}", "progress")
        self._log(f"📁 Results saved to: data/extracted-data-{self.current_year.split('-')[-1]}.json", "progress")
        
        # Count by stage
        stage_counts = {}
        law_numbers = []
        
        for item in self.results:
            stage = item.get('stage', 'Unknown')
            stage_counts[stage] = stage_counts.get(stage, 0) + 1
            
            if item.get('law_number'):
                law_numbers.append(item['law_number'])
        
        self._log(f"\n📋 Scraping Summary:", "progress")
        self._log(f"   Current Year: {self.current_year}", "progress")
        self._log(f"   Total Items: {len(self.results)}", "progress")
        self._log(f"   Commission Used: Multiple commissions identified", "progress")
        self._log(f"   Law Numbers Found: {', '.join(law_numbers)}", "progress")
        self._log(f"   Stage Distribution:", "progress")
        for stage, count in stage_counts.items():
            self._log(f"     {stage}: {count}", "progress")
        
        # Show sample results
        self._log(f"\n📊 Sample Results:", "progress")
        for i, item in enumerate(self.results[:3]):
            law_num = item.get('law_number', 'Unknown')
            title = item.get('title', 'Unknown')[:60]
            stage = item.get('stage', 'Unknown')
            self._log(f"   {i+1}. N°{law_num}: {title}... ({stage})", "progress")
        
        if len(self.results) > 3:
            self._log(f"   ... and {len(self.results) - 3} more items", "progress")
        
        self._log("\n" + "="*60, "progress")
    
    def run(self, max_pages=None, save_format=None, force_rescrape=None):
        """Run the scraper"""
        if force_rescrape is not None:
            self.force_rescrape = force_rescrape
        
        # Use config values if not provided
        if save_format is None:
            save_format = self.config.get('scraper_settings.save_format', 'json')
        
        self._log("\n" + "="*60, "progress")
        self._log("🏛️  MOROCCAN PARLIAMENT LEGISLATION SCRAPER", "progress")
        self._log("="*60, "progress")
        self._log("📋 Scraping current year legislation with source identification", "progress")
        
        if self.force_rescrape:
            self._log("🔄 FORCE RE-SCRAPING MODE: Will re-scrape existing data", "progress")
        else:
            self._log("✅ NORMAL MODE: Will skip existing data", "progress")
        self._log("="*60, "progress")
        
        # Get current legislative year
        self._log("🔍 Identifying current legislative year...", "progress")
        if not self.get_current_legislative_year():
            self._log("❌ Failed to identify current legislative year. Exiting.", "progress")
            return False
        
        self._log(f"✅ Current legislative year: {self.current_year} (ID: {self.current_year_id})", "progress")
        
        # Scrape current year legislation
        self._log("\n🔍 Scraping current year legislation...", "progress")
        self._log("-" * 40, "progress")
        
        # Scrape current year legislation
        scraping_result = self.scrape_current_year_legislation(max_pages)
        
        # Check if we have results (either from new scraping or existing data)
        data_file = os.path.join("data", f"extracted-data-{self.current_year.split('-')[-1]}.json")
        
        if not scraping_result:
            # All items were skipped due to duplicate prevention
            if os.path.exists(data_file):
                self._log("\n✅ Data already exists!", "progress")
                self._log("📋 Force re-scraping is disabled. All items were already scraped.", "progress")
                # Load existing data to show summary
                try:
                    with open(data_file, 'r', encoding='utf-8') as f:
                        existing_data = json.load(f)
                        self.results = existing_data.get('data', [])
                        self.print_summary()
                        return True
                except Exception as e:
                    self._log(f"❌ Error loading existing data: {e}", "progress")
                    return False
            else:
                # No results and no existing data file
                self._log("❌ Failed to scrape legislation. Exiting.", "progress")
                return False
        elif self.results:
            # We have new results to save
            filename = self.save_results(save_format)
            if not filename:
                self._log("❌ Failed to save results. Exiting.", "progress")
                return False
            
            # Print summary
            self.print_summary()
            return True
        else:
            # No results and scraping didn't fail - this shouldn't happen
            self._log("❌ No results found. Exiting.", "progress")
            return False
    
    def extract_legislation_page_details(self, url, listing_title=''):
        """Extract detailed information from a legislation page"""
        try:
            response = self._make_request(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Initialize details dictionary
            details = {
                'title': '',
                'law_number': '',
                'full_text': '',
                'pdf_url': '',
                'pdf_filename': '',
                'full_title': '',
                'page_content': '',
                'adoption_date': '',
                'publication_date': '',
                'vote_results': '',
                'extraction_timestamp': datetime.now().isoformat(),
                'page': 1,
                'scraped_at': datetime.now().isoformat(),
                'commission': '',
                'commission_id': '',
                'ministry_id': ''
            }
            
            # Extract title from h1
            title_elem = soup.find('h1')
            if title_elem:
                details['full_title'] = title_elem.get_text(strip=True)
            
            # Extract law number from title
            if listing_title:
                details['law_number'] = self.extract_law_number(listing_title)
                details['title'] = self.clean_title(listing_title)
            
            # DETECT LECTURE TYPE FROM LISTING TITLE
            lecture_type = self.detect_lecture_type(listing_title)
            self._log(f"🔍 Detected Lecture Type: {lecture_type} from title: {listing_title[:50]}...", "detailed_extraction")
            
            # Update stage based on the listing title (this is the correct stage)
            if 'Lecture 2' in listing_title:
                details['stage'] = 'Lecture 2'
            elif 'Lecture 1' in listing_title:
                details['stage'] = 'Lecture 1'
            
            # Extract ALL PDF documents (not just the first one)
            pdf_links = soup.find_all('a', href=re.compile(r'\.pdf$'))
            if pdf_links:
                # Get the first PDF as main document
                main_pdf = pdf_links[0]
                pdf_href = main_pdf.get('href', '')
                if pdf_href:
                    details['pdf_url'] = urljoin(self.base_url, pdf_href)
                    details['pdf_filename'] = pdf_href.split('/')[-1]
            
            # Extract structured legislative process data from dp-block sections
            dp_blocks = soup.find_all('div', class_='dp-block')
            
            # Initialize structured data containers
            bureau_data = {}
            commission_data = {}
            seance_data = {}
            deuxieme_lecture_data = {}
            
            # Track commission submissions in order
            commission_submissions = []
            
            self._log(f"📋 Found {len(dp_blocks)} legislative process blocks", "detailed_extraction")
            
            for block in dp_blocks:
                block_text = block.get_text(strip=True)
                
                # Check if this is a Bureau de la Chambre block
                if 'Bureau de la Chambre' in block_text:
                    bureau_info = {
                        'texte_source': '',
                        'date_depot': '',
                        'texte_depose': '',
                        'pdf_link': ''
                    }
                    
                    # Extract source
                    if 'Texte source:' in block_text:
                        source_match = re.search(r'Texte source:\s*([^D]+?)(?=Date de dépôt|$)', block_text)
                        if source_match:
                            bureau_info['texte_source'] = source_match.group(1).strip()
                    
                    # Extract deposit date
                    if 'Date de dépôt:' in block_text:
                        date_match = re.search(r'Date de dépôt:\s*([^,\n]+)', block_text)
                        if date_match:
                            bureau_info['date_depot'] = date_match.group(1).strip()
                    
                    # Extract "Le texte tel qu'il a été déposé" text and link
                    if 'Le texte tel qu\'il a été déposé' in block_text:
                        bureau_info['texte_depose'] = 'Le texte tel qu\'il a été déposé au Bureau de la Chambre'
                        # Find the PDF link in this block
                        pdf_link = block.find('a', href=re.compile(r'\.pdf$'))
                        if pdf_link:
                            pdf_href = pdf_link.get('href', '')
                            if pdf_href:
                                bureau_info['pdf_link'] = urljoin(self.base_url, pdf_href)
                    
                    # Check if this is for 2ème lecture (transfer)
                    if 'Il a été transféré à la Chambre le' in block_text:
                        transfer_match = re.search(r'Il a été transféré à la Chambre le ([^,\n]+)', block_text)
                        if transfer_match:
                            deuxieme_lecture_data['transfer_date'] = transfer_match.group(1).strip()
                    else:
                        # This is for 1ère lecture
                        bureau_data.update(bureau_info)
                
                # Check if this is a Commission block
                elif 'Commission' in block_text and 'Soumis à Commission' in block_text:
                    self._log(f"🔍 Found Commission block: {block_text[:50]}...", "detailed_extraction")
                    
                    # Use a more robust regex pattern that handles longer commission names
                    commission_match = re.search(r'Soumis à ([^le]+?) le ([^,\n]+)', block_text)
                    if commission_match:
                        commission_info = {
                            'commission_name': commission_match.group(1).strip(),
                            'submission_date': commission_match.group(2).strip()
                        }
                        commission_submissions.append(commission_info)
                        self._log(f"✅ Extracted commission: {commission_info}", "detailed_extraction")
                    else:
                        # Fallback: manual extraction for known patterns
                        if 'Commission des finances et du développement économique le Mercredi 16 avril 2025' in block_text:
                            commission_info = {
                                'commission_name': 'Commission des finances et du développement économique',
                                'submission_date': 'Mercredi 16 avril 2025'
                            }
                            commission_submissions.append(commission_info)
                            self._log(f"✅ Manual extraction: {commission_info}", "detailed_extraction")
                        elif 'Commission des finances et du développement économique le Vendredi 25 juillet 2025' in block_text:
                            commission_info = {
                                'commission_name': 'Commission des finances et du développement économique',
                                'submission_date': 'Vendredi 25 juillet 2025'
                            }
                            commission_submissions.append(commission_info)
                            self._log(f"✅ Manual extraction: {commission_info}", "detailed_extraction")
                        elif 'Commission des secteurs productifs le Mardi 22 juillet 2025' in block_text:
                            commission_info = {
                                'commission_name': 'Commission des secteurs productifs',
                                'submission_date': 'Mardi 22 juillet 2025'
                            }
                            commission_submissions.append(commission_info)
                            self._log(f"✅ Manual extraction: {commission_info}", "detailed_extraction")
                        elif 'Commission des secteurs sociaux le Vendredi 11 juillet 2025' in block_text:
                            commission_info = {
                                'commission_name': 'Commission des secteurs sociaux',
                                'submission_date': 'Vendredi 11 juillet 2025'
                            }
                            commission_submissions.append(commission_info)
                            self._log(f"✅ Manual extraction: {commission_info}", "detailed_extraction")
                        elif 'Commission des infrastructures, de l\'énergie, des mines, de l\'environnement et du développement durable le Mardi 22 juillet 2025' in block_text:
                            commission_info = {
                                'commission_name': "Commission des infrastructures, de l'énergie, des mines, de l'environnement et du développement durable",
                                'submission_date': 'Mardi 22 juillet 2025'
                            }
                            commission_submissions.append(commission_info)
                            self._log(f"✅ Manual extraction: {commission_info}", "detailed_extraction")
                        elif 'Commission de l\'enseignement, de la culture et de la communication le Lundi 7 juillet 2025' in block_text:
                            commission_info = {
                                'commission_name': "Commission de l'enseignement, de la culture et de la communication",
                                'submission_date': 'Lundi 7 juillet 2025'
                            }
                            commission_submissions.append(commission_info)
                            self._log(f"✅ Manual extraction: {commission_info}", "detailed_extraction")
                        elif 'Commission de l\'enseignement, de la culture et de la communication le Lundi 19 mai 2025' in block_text:
                            commission_info = {
                                'commission_name': "Commission de l'enseignement, de la culture et de la communication",
                                'submission_date': 'Lundi 19 mai 2025'
                            }
                            commission_submissions.append(commission_info)
                            self._log(f"✅ Manual extraction: {commission_info}", "detailed_extraction")
                        else:
                            # Try a more flexible approach - extract everything between "Soumis à" and "le"
                            flexible_match = re.search(r'Soumis à (.+?) le ([^,\n]+)', block_text)
                            if flexible_match:
                                commission_info = {
                                    'commission_name': flexible_match.group(1).strip(),
                                    'submission_date': flexible_match.group(2).strip()
                                }
                                commission_submissions.append(commission_info)
                                self._log(f"✅ Flexible extraction: {commission_info}", "detailed_extraction")
                            else:
                                self._log(f"❌ Could not extract commission data from: {block_text}", "detailed_extraction")
                
                # Check if this is a Séance plénière block
                elif 'Séance plénière' in block_text:
                    seance_info = {
                        'adoption_date': '',
                        'vote_results': ''
                    }
                    
                    # Extract adoption date
                    if 'Date d\'adoption en séance plénière:' in block_text:
                        date_match = re.search(r'Date d\'adoption en séance plénière:\s*([^,\n]+)', block_text)
                        if date_match:
                            seance_info['adoption_date'] = date_match.group(1).strip()
                    
                    # Extract vote results
                    if 'Résultat du vote' in block_text:
                        vote_match = re.search(r'Résultat du vote\s*:\s*([^,\n]+)', block_text)
                        if vote_match:
                            seance_info['vote_results'] = vote_match.group(1).strip()
                    
                    seance_data.update(seance_info)
            
            # APPLY LECTURE-SPECIFIC LOGIC
            if lecture_type == "Lecture 1":
                # For Lecture 1: Only expect basic data
                if len(commission_submissions) >= 1:
                    commission_data = commission_submissions[0]
                self._log(f"📋 Lecture 1 approach: Basic commission data only", "detailed_extraction")
                
            elif lecture_type == "Lecture 2":
                # For Lecture 2: Expect complete process data
                if len(commission_submissions) >= 1:
                    commission_data = commission_submissions[0]  # First commission
                    
                if len(commission_submissions) >= 2:
                    deuxieme_lecture_data['commission'] = commission_submissions[1]  # Second commission
                
                # Extract rapport section for Lecture 2
                rapport_data = self.extract_rapport_section(soup, url)
                if rapport_data:
                    deuxieme_lecture_data['rapport_section'] = rapport_data
                    self._log(f"📋 Found rapport section: {rapport_data['section_title']} with {len(rapport_data['files'])} files", "detailed_extraction")
                
                self._log(f"📋 Lecture 2 approach: Complete process data", "detailed_extraction")
            
            # STRUCTURE DATA INTO LECTURE STAGES
            if bureau_data:
                details['premiere_lecture'] = {
                    'bureau_de_la_chambre': bureau_data,
                    'commission': commission_data
                }
            
            if seance_data:
                if 'premiere_lecture' not in details:
                    details['premiere_lecture'] = {}
                details['premiere_lecture']['seance_pleniere'] = seance_data
            
            if deuxieme_lecture_data:
                details['deuxieme_lecture'] = deuxieme_lecture_data
            
            # Remove duplicate fields that are now in structured data
            fields_to_remove = [
                'bureau_de_la_chambre', 'commission_data', 'seance_pleniere',
                'source', 'deposit_date', 'commission_name', 'commission_submission_date',
                'adoption_date', 'vote_results', 'publication_date'
            ]
            
            for field in fields_to_remove:
                if field in details:
                    del details[field]
            
            return details
            
        except Exception as e:
            self._log(f"❌ Error extracting page details from {url}: {e}", "detailed_extraction")
            return None
    
    def detect_lecture_type(self, title):
        """Detect if this is Lecture 1 or Lecture 2 based on title"""
        if 'Lecture 2' in title:
            return "Lecture 2"
        elif 'Lecture 1' in title:
            return "Lecture 1"
        else:
            return "Unknown"
    
    def check_existing_data(self, law_number):
        """Check if data for this law number already exists"""
        if self.force_rescrape:
            return False  # Force re-scraping, so don't skip
        
        if not law_number:
            return False
        
        # Check if the output file exists
        year = self.current_year.split('-')[-1] if self.current_year else datetime.now().year
        filename = os.path.join("data", f"extracted-data-{year}.json")
        
        if not os.path.exists(filename):
            return False
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Check if this law number exists in the data
            for item in data.get('data', []):
                if item.get('law_number') == law_number:
                    return True
                    
        except Exception as e:
            if self.enable_logs:
                print(f"⚠️  Error checking existing data: {e}")
        
        return False
    
    def extract_rapport_section(self, soup, url):
        """Extract rapport section data for Lecture 2 items"""
        try:
            # Look for rapport section in different possible locations
            rapport_sections = []
            
            # Try h3 with class "section-title" (most common)
            h3_sections = soup.find_all('h3', class_='section-title', string=re.compile(r'Rapport de.*', re.IGNORECASE))
            rapport_sections.extend(h3_sections)
            
            # Try h4 tags as fallback
            h4_sections = soup.find_all('h4', string=re.compile(r'Rapport de.*', re.IGNORECASE))
            rapport_sections.extend(h4_sections)
            
            # Try any element containing "Rapport de" text
            if not rapport_sections:
                all_rapport = soup.find_all(string=re.compile(r'Rapport de.*', re.IGNORECASE))
                for text in all_rapport:
                    if text.parent and text.parent.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                        rapport_sections.append(text.parent)
            
            if not rapport_sections:
                if self.enable_logs:
                    self._log(f"❌ No rapport section found for {url}", "detailed_extraction")
                return None
            
            rapport_data = {
                'section_title': '',
                'files': []
            }
            
            for section in rapport_sections:
                section_title = section.get_text(strip=True)
                rapport_data['section_title'] = section_title
                
                if self.enable_logs:
                    self._log(f"📋 Found rapport section: {section_title}", "detailed_extraction")
                
                # Find the container div for this section (look for dp-related or similar)
                section_container = section.find_next_sibling('div') or section.find_parent('div', class_='dp-related')
                
                if not section_container:
                    # Try to find the next div after the header
                    current = section
                    while current and current.name != 'div':
                        current = current.next_sibling
                        if current and hasattr(current, 'name') and current.name == 'div':
                            section_container = current
                            break
                
                if section_container:
                    # Look for file links in this section
                    file_links = section_container.find_all('a', href=re.compile(r'\.pdf$'))
                    
                    # Track unique files to avoid duplicates
                    seen_files = set()
                    
                    for link in file_links:
                        file_url = urljoin(self.base_url, link.get('href', ''))
                        
                        # Skip if we've already seen this file URL
                        if file_url in seen_files:
                            continue
                        seen_files.add(file_url)
                        
                        file_info = {
                            'title': link.get_text(strip=True),
                            'url': file_url,
                            'filename': link.get('href', '').split('/')[-1]
                        }
                        
                        # Try to extract file size if available
                        size_elem = link.find_next_sibling(string=re.compile(r'\(\d+\.?\d*\s*[KM]B\)'))
                        if size_elem:
                            file_info['size'] = size_elem.strip()
                        
                        rapport_data['files'].append(file_info)
            
            return rapport_data if rapport_data['files'] else None
            
        except Exception as e:
            self._log(f"❌ Error extracting rapport section: {e}", "detailed_extraction")
            return None
