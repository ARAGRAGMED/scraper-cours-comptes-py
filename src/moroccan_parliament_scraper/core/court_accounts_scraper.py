#!/usr/bin/env python3
"""
Moroccan Court of Accounts Publications Scraper
Enhanced scraper for extracting publications data from the Court of Accounts website
"""

import requests
import json
import re
import time
import os
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, parse_qs
from ..utils.config_manager import ConfigManager

class CourtOfAccountsScraper:
    """Enhanced scraper for Court of Accounts publications with configuration management and proxy support"""
    
    def __init__(self, force_rescrape=None, config_file="config/scraper_config.json"):
        """Initialize scraper with configuration"""
        self.config = ConfigManager(config_file)
        
        # Use config settings or override with parameters
        self.force_rescrape = force_rescrape if force_rescrape is not None else self.config.get('scraper_settings.force_rescrape', False)
        self.enable_logs = self.config.get('scraper_settings.enable_logs', True)
        
        # Initialize session with proxy support
        self.session = self._create_session()
        
        # Base URLs for Court of Accounts
        self.base_url = "https://www.courdescomptes.ma"
        self.publications_url = f"{self.base_url}/publications/"
        
        # Publication categories from the website
        self.publication_categories = [
            "Rapport thématique",
            "Rapport particulier", 
            "Rapport annuel",
            "Rapport partis politiques",
            "Synthèses des missions CRC",
            "Arrêt",
            "Référé",
            "Formulaire"
        ]
        
        # Focus on current year only
        self.current_year = datetime.now().year
        
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
        user_agent = self.config.get('request_settings.user_agent', 
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        session.headers.update({'User-Agent': user_agent})
        
        # Set proxy if enabled
        if self.config.get('proxy_settings.enable_proxies', False):
            self._set_proxy(session)
        
        return session
    
    def _set_proxy(self, session):
        """Set proxy for the session"""
        proxies_list = self.config.get('proxy_settings.proxies', [])
        if proxies_list:
            proxy = proxies_list[self.current_proxy_index % len(proxies_list)]
            session.proxies.update(proxy)
            if self.enable_logs:
                self._log(f"🌐 Using proxy: {proxy.get('http', 'Direct connection')}", "proxy")
    
    def _rotate_proxy(self):
        """Rotate to the next proxy"""
        if self.config.get('proxy_settings.enable_proxies', False) and self.config.get('proxy_settings.proxy_rotation', True):
            self.current_proxy_index += 1
            self._set_proxy(self.session)
            if self.enable_logs:
                self._log("🔄 Rotated to next proxy", "proxy")
    
    def _log(self, message, log_type="general"):
        """Enhanced logging with type filtering"""
        if not self.enable_logs:
            return
        
        # Check if this log type should be shown
        show_log = True
        if log_type == "detailed_extraction":
            show_log = self.config.get('logging_settings.show_detailed_extraction', True)
        elif log_type == "progress":
            show_log = self.config.get('logging_settings.show_progress', True)
        elif log_type == "proxy":
            show_log = self.config.get('logging_settings.show_proxy_info', True)
        
        if show_log:
            print(message)
    
    def _make_request(self, url, retries=None):
        """Make HTTP request with retry logic and proxy rotation"""
        if retries is None:
            retries = self.config.get('request_settings.retry_attempts', 3)
        
        timeout = self.config.get('request_settings.timeout', 30)
        
        for attempt in range(retries + 1):
            try:
                response = self.session.get(url, timeout=timeout)
                response.raise_for_status()
                return response
                
            except requests.exceptions.RequestException as e:
                if attempt < retries:
                    self._log(f"⚠️  Request failed (attempt {attempt + 1}/{retries + 1}): {e}", "progress")
                    
                    # Rotate proxy on failure if enabled
                    if self.config.get('proxy_settings.enable_proxies', False):
                        self._rotate_proxy()
                    
                    # Wait before retry
                    delay = self.config.get('request_settings.delay_between_requests', 2)
                    time.sleep(delay * (attempt + 1))  # Exponential backoff
                else:
                    self._log(f"❌ Request failed after {retries + 1} attempts: {e}", "progress")
                    raise
        
        return None
    
    def extract_publications_from_page(self, page_content, base_url):
        """Extract publication data from a publications page"""
        soup = BeautifulSoup(page_content, 'html.parser')
        publications = []
        
        # Find publication items with class 'item' and data-time attribute for current year
        publication_items = soup.find_all('div', class_='item', attrs={'data-time': str(self.current_year)})
        
        self._log(f"📋 Found {len(publication_items)} items for {self.current_year}", "detailed_extraction")
        
        for item in publication_items:
            try:
                publication_data = self._extract_publication_from_item(item, base_url)
                if publication_data:
                    # Extract additional details from the publication's detail page
                    if publication_data.get('url'):
                        self._log(f"🔍 Extracting details from: {publication_data['url']}", "detailed_extraction")
                        detailed_data = self.extract_publication_details(publication_data['url'])
                        if detailed_data:
                            # Merge detailed data with basic data
                            publication_data.update(detailed_data)
                    
                    publications.append(publication_data)
                    self._log(f"✅ Extracted: {publication_data['title'][:50]}...", "detailed_extraction")
                    
            except Exception as e:
                self._log(f"⚠️  Error extracting publication: {e}", "detailed_extraction")
                continue
        
        return publications
    
    def _extract_publication_from_item(self, item, base_url):
        """Extract publication data from a single item div"""
        publication = {
            'title': '',
            'date': '',
            'year': None,  # Add year field
            'category': '',
            'description': '',
            'pdf_url': '',
            'pdf_filename': '',
            'url': '',
            'scraped_at': datetime.now().isoformat(),
            'source_url': base_url
        }
        
        # Extract title from data-title attribute
        title = item.get('data-title', '').strip()
        if title:
            publication['title'] = title
        
        # Extract category from data-cat attribute
        category_attr = item.get('data-cat', '').strip()
        if category_attr:
            # Convert category attribute to readable format
            category_map = {
                'rapport-annuel': 'Rapport annuel',
                'rapport-thematique': 'Rapport thématique', 
                'rapport-particulier': 'Rapport particulier',
                'rapport-partis-politiques': 'Rapport partis politiques',
                'syntheses-des-missions-crc': 'Synthèses des missions CRC',
                'arret': 'Arrêt',
                'refere': 'Référé',
                'formulaire': 'Formulaire'
            }
            publication['category'] = category_map.get(category_attr, category_attr)
        
        # Extract date from time element
        time_element = item.find('time')
        if time_element:
            date_text = time_element.get_text(strip=True)
            publication['date'] = date_text
            
            # Extract year from date
            import re
            year_match = re.search(r'(\d{4})', date_text)
            if year_match:
                publication['year'] = int(year_match.group(1))
            else:
                publication['year'] = self.current_year  # Use current year as fallback
        
        # Extract URL from the link
        link_element = item.find('a')
        if link_element:
            publication['url'] = link_element.get('href', '')
        
        # Extract title from h2 element if not found in data-title
        if not publication['title']:
            h2_element = item.find('h2')
            if h2_element:
                publication['title'] = h2_element.get_text(strip=True)
        
        # Look for PDF links in the item or try to find them on the detail page
        # For now, we'll leave PDF extraction for later as it requires visiting individual pages
        
        return publication if publication['title'] else None
    
    def extract_publication_details(self, url):
        """Extract detailed information from a publication's detail page"""
        try:
            self._log(f"📄 Fetching details from: {url}", "detailed_extraction")
            
            response = self._make_request(url)
            if not response:
                self._log(f"⚠️  Failed to fetch detail page: {url}", "detailed_extraction")
                return None
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            details = {
                'description': '',
                'author': '',
                'pdf_files': [],
                'additional_files': [],
                'full_content': '',
                'arabic_version_url': '',
                'language_versions': {},
                'publication_details': {}
            }
            
            # Extract description from OpenGraph meta first, then content
            og_description = soup.find('meta', property='og:description')
            if og_description:
                details['description'] = og_description.get('content', '').strip()
            
            # If no OG description, extract from article content
            if not details['description']:
                content_selectors = [
                    '.entry-content',
                    '.post-content', 
                    '.article-content',
                    '.content',
                    'article .content',
                    '.single-content'
                ]
                
                for selector in content_selectors:
                    content_elem = soup.select_one(selector)
                    if content_elem:
                        # Get text content, cleaning up whitespace
                        content_text = content_elem.get_text(separator=' ', strip=True)
                        # Take first 500 characters as description
                        details['description'] = content_text[:500] + ('...' if len(content_text) > 500 else '')
                        details['full_content'] = content_text
                        break
            
            # Extract author information
            author_section = soup.find('h3', string=re.compile(r'Auteur', re.IGNORECASE))
            if author_section:
                author_elem = author_section.find_next('p', class_='txtRougeP1')
                if author_elem:
                    details['author'] = author_elem.get_text(strip=True)
            
            # Extract language versions (Arabic, Amazigh, English)
            language_links = soup.find_all('a', class_='wpml-ls-link')
            for link in language_links:
                lang_span = link.find('span', class_='wpml-ls-native')
                if lang_span:
                    lang_text = lang_span.get_text(strip=True)
                    lang_url = link.get('href', '')
                    
                    if 'العربية' in lang_text or 'arabic' in lang_text.lower():
                        details['arabic_version_url'] = lang_url
                        details['language_versions']['arabic'] = {
                            'name': lang_text,
                            'url': lang_url
                        }
                    elif 'ⵜⴰⵎⴰⵣⵉⵖⵜ' in lang_text or 'amazigh' in lang_text.lower():
                        details['language_versions']['amazigh'] = {
                            'name': lang_text,
                            'url': lang_url
                        }
                    elif 'english' in lang_text.lower() or 'anglais' in lang_text.lower():
                        details['language_versions']['english'] = {
                            'name': lang_text,
                            'url': lang_url
                        }
            
            # Extract PDF links from regular href attributes
            pdf_links = soup.find_all('a', href=re.compile(r'\.pdf$', re.IGNORECASE))
            other_file_links = soup.find_all('a', href=re.compile(r'\.(doc|docx|xls|xlsx|zip|rar)$', re.IGNORECASE))
            
            # Extract PDF links from JavaScript onclick functions (Court of Accounts specific)
            onclick_elements = soup.find_all(attrs={'onclick': re.compile(r'open_doc\([\'"]([^\'"]*\.pdf)[\'"]', re.IGNORECASE)})
            
            # Process regular PDF links
            for link in pdf_links:
                pdf_url = urljoin(url, link.get('href', ''))
                pdf_text = link.get_text(strip=True)
                file_info = {
                    'url': pdf_url,
                    'filename': pdf_url.split('/')[-1],
                    'title': pdf_text or pdf_url.split('/')[-1],
                    'type': 'pdf'
                }
                details['pdf_files'].append(file_info)
            
            # Process JavaScript onclick PDF links
            for element in onclick_elements:
                onclick_value = element.get('onclick', '')
                pdf_match = re.search(r'open_doc\([\'"]([^\'"]*\.pdf)[\'"]', onclick_value, re.IGNORECASE)
                if pdf_match:
                    pdf_url = pdf_match.group(1)
                    
                    # Find the title from the same item container
                    item_container = element.find_parent('div', class_='item')
                    if item_container:
                        title_elem = item_container.find('h2', class_='widthTitle')
                        if title_elem:
                            pdf_title = title_elem.get_text(strip=True)
                        else:
                            pdf_title = pdf_url.split('/')[-1]
                    else:
                        pdf_title = pdf_url.split('/')[-1]
                    
                    # Detect language and document type
                    is_arabic = any(keyword in pdf_title.lower() for keyword in ['ar', 'arabe', 'arabic', 'عربي'])
                    # Check both title and URL for synthesis indicators
                    is_synthesis = (any(keyword in pdf_title.lower() for keyword in ['synthèse', 'synthese', 'synthesis', 'resume', 'summary']) or
                                  any(keyword in pdf_url.lower() for keyword in ['synthese', 'synthèse']))
                    is_french = 'fr' in pdf_title.lower() or 'français' in pdf_title.lower()
                    
                    file_info = {
                        'url': pdf_url,
                        'filename': pdf_url.split('/')[-1],
                        'title': pdf_title,
                        'type': 'pdf',
                        'language': 'arabic' if is_arabic else ('french' if is_french else 'unknown'),
                        'document_type': 'synthesis' if is_synthesis else 'main_report'
                    }
                    details['pdf_files'].append(file_info)
            
            # Process other files
            for link in other_file_links:
                file_url = urljoin(url, link.get('href', ''))
                file_text = link.get_text(strip=True)
                file_ext = file_url.split('.')[-1].lower()
                file_info = {
                    'url': file_url,
                    'filename': file_url.split('/')[-1],
                    'title': file_text or file_url.split('/')[-1],
                    'type': file_ext
                }
                details['additional_files'].append(file_info)
            
            # Set main PDF if available
            if details['pdf_files']:
                main_pdf = details['pdf_files'][0]
                details['pdf_url'] = main_pdf['url']
                details['pdf_filename'] = main_pdf['filename']
            
            # Extract publication date or other metadata
            date_patterns = [
                r'(\d{1,2}\s+\w+\s+\d{4})',
                r'(\d{4}-\d{2}-\d{2})',
                r'(\d{2}/\d{2}/\d{4})'
            ]
            
            page_text = soup.get_text()
            for pattern in date_patterns:
                match = re.search(pattern, page_text)
                if match:
                    details['publication_details']['extracted_date'] = match.group(1)
                    break
            
            self._log(f"📋 Extracted {len(details['pdf_files'])} PDF files and {len(details['additional_files'])} other files", "detailed_extraction")
            
            return details
            
        except Exception as e:
            self._log(f"⚠️  Error extracting details from {url}: {e}", "detailed_extraction")
            return None
    
    def _extract_publication_data(self, item, soup, base_url):
        """Extract individual publication data"""
        publication = {
            'title': '',
            'date': '',
            'year': None,  # Add year field
            'category': '',
            'description': '',
            'pdf_url': '',
            'pdf_filename': '',
            'scraped_at': datetime.now().isoformat(),
            'source_url': base_url
        }
        
        # Try to extract publication information
        # This will need to be refined based on the actual HTML structure
        
        # Extract date (format appears to be "DD MMM. YYYY")
        date_match = re.search(r'(\d{1,2})\s+(\w+)\.\s+(\d{4})', str(item))
        if date_match:
            day, month_abbr, year = date_match.groups()
            publication['date'] = f"{day} {month_abbr}. {year}"
            publication['year'] = int(year)  # Store year as integer
        
        # Extract category and title
        # Based on the search results format: "Date - Category Title"
        text_content = item.get_text(strip=True) if hasattr(item, 'get_text') else str(item)
        
        # Look for category patterns
        for category in self.publication_categories:
            if category.lower() in text_content.lower():
                publication['category'] = category
                break
        
        # Extract title (everything after the category)
        title_match = re.search(r'-\s*(.+)$', text_content)
        if title_match:
            publication['title'] = title_match.group(1).strip()
        else:
            publication['title'] = text_content.strip()
        
        # Look for PDF links
        if hasattr(item, 'find_all'):
            pdf_links = item.find_all('a', href=re.compile(r'\.pdf$', re.I))
            if pdf_links:
                pdf_link = pdf_links[0]
                publication['pdf_url'] = urljoin(base_url, pdf_link.get('href', ''))
                publication['pdf_filename'] = publication['pdf_url'].split('/')[-1]
        
        # Only return if we have meaningful data
        if publication['title'] and (publication['date'] or publication['category']):
            return publication
        
        return None
    
    def scrape_publications(self, max_pages=10):
        """Scrape current year publications"""
        
        self._log("============================================================", "progress")
        self._log("🏛️  COURT OF ACCOUNTS PUBLICATIONS SCRAPER", "progress")
        self._log("============================================================", "progress")
        self._log(f"📋 Scraping Court of Accounts publications for {self.current_year}", "progress")
        
        if self.force_rescrape:
            self._log("🔄 FORCE RE-SCRAPING MODE: Will re-scrape existing data", "progress")
        else:
            self._log("✅ NORMAL MODE: Will skip existing data", "progress")
        
        self._log("============================================================", "progress")
        
        all_publications = []
        
        # Use the base publications URL without parameters first
        # We'll filter by year after scraping the data
        url = self.publications_url
        
        # Since the site shows the same content on all pages, just scrape once
        try:
            self._log(f"📄 Processing publications page...", "progress")
            
            response = self._make_request(url)
            if not response:
                self._log(f"⚠️  Failed to fetch publications page", "progress")
                return []
            
            publications = self.extract_publications_from_page(response.text, self.base_url)
            
            if not publications:
                self._log(f"📭 No publications found on page", "progress")
                return []
            
            # Remove duplicates based on title and date
            seen_publications = set()
            unique_publications = []
            
            for pub in publications:
                pub_key = (pub['title'], pub['date'])
                if pub_key not in seen_publications:
                    seen_publications.add(pub_key)
                    unique_publications.append(pub)
            
            all_publications = unique_publications
            self._log(f"✅ Found {len(all_publications)} unique publications for {self.current_year}", "progress")
                    
        except Exception as e:
            self._log(f"❌ Error processing publications page: {e}", "progress")
            return []
        
        self.results = all_publications
        return all_publications
    
    def save_results(self, filename=None):
        """Save results to JSON file"""
        if not self.results:
            self._log("❌ No results to save", "progress")
            return False
        
        # Create data directory if it doesn't exist
        os.makedirs("data", exist_ok=True)
        
        if not filename:
            current_year = datetime.now().year
            filename = f"data/court-accounts-publications-{current_year}.json"
        
        # Prepare output data structure
        output_data = {
            "scraped_at": datetime.now().isoformat(),
            "total_items": len(self.results),
            "source_website": "https://www.courdescomptes.ma/publications/",
            "data_extraction_level": "Enhanced with publication details and PDF links",
            "publication_categories": self.publication_categories,
            "duplicate_checking": "Enabled" if not self.force_rescrape else "Disabled",
            "data": self.results
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)
            
            self._log("💾 Saving results...", "progress")
            self._log(f"✅ Results saved to {filename}", "progress")
            self._log(f"📊 File contains {len(self.results)} publication items", "progress")
            
            return True
            
        except Exception as e:
            self._log(f"❌ Error saving results: {e}", "progress")
            return False
    
    def run(self, max_pages=10):
        """Main execution method for current year publications"""
        try:
            # Check for existing data if not force re-scraping
            if not self.force_rescrape:
                existing_count = self._check_existing_data()
                if existing_count > 0:
                    self._log(f"✅ Data already exists with {existing_count} items!", "progress")
                    self._log("📋 Force re-scraping is disabled.", "progress")
                    self._log("💡 To re-scrape existing data, set 'force_rescrape': true in config/scraper_config.json", "progress")
                    return True
            
            # Scrape publications
            publications = self.scrape_publications(max_pages)
            
            if not publications:
                self._log("📭 No publications found to process", "progress")
                self._log("❌ No results found. Exiting.", "progress")
                return False
            
            # Save results
            success = self.save_results()
            
            if success:
                self._log("", "progress")
                self._log("============================================================", "progress")
                self._log("🎉 SCRAPING COMPLETE!", "progress")
                self._log("============================================================", "progress")
                self._log(f"📊 Total publications scraped: {len(publications)}", "progress")
                
                # Show sample results
                self._log("📊 Sample Results:", "progress")
                for i, pub in enumerate(publications[:5], 1):
                    title_preview = pub['title'][:80] + "..." if len(pub['title']) > 80 else pub['title']
                    self._log(f"   {i}. {pub['date']}: {title_preview} ({pub['category']})", "progress")
                
                if len(publications) > 5:
                    self._log(f"   ... and {len(publications) - 5} more publications", "progress")
                
                self._log("", "progress")
                self._log("✅ Scraping completed successfully!", "progress")
                self._log("📋 Next steps:", "progress")
                self._log("1. Review the generated JSON file in the data/ directory", "progress")
                self._log("2. Check the extracted publication data", "progress")
                self._log("3. Use the web viewer to explore the publications", "progress")
                self._log("4. Set up automated runs for regular updates", "progress")
                self._log("5. Modify config/scraper_config.json to customize settings", "progress")
                
                return True
            else:
                return False
                
        except KeyboardInterrupt:
            self._log("\n⚠️  Scraping interrupted by user", "progress")
            return False
        except Exception as e:
            self._log(f"❌ Unexpected error: {e}", "progress")
            return False
    
    def _check_existing_data(self):
        """Check if data already exists"""
        current_year = datetime.now().year
        filename = f"data/court-accounts-publications-{current_year}.json"
        
        if not os.path.exists(filename):
            return 0
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('total_items', 0)
        except Exception as e:
            if self.enable_logs:
                self._log(f"⚠️  Error checking existing data: {e}", "progress")
        
        return 0
