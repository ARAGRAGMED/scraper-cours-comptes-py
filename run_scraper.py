#!/usr/bin/env python3
"""
Main entry point for Moroccan Court of Accounts Publications Scraper
"""

import sys
import os
from datetime import datetime

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from moroccan_parliament_scraper import CourtOfAccountsScraper

def main():
    """Main function to run the scraper"""
    print("🏛️  Moroccan Court of Accounts Publications Scraper")
    print("=" * 50)
    
    # Create scraper instance with configuration
    scraper = CourtOfAccountsScraper()
    
    # Show configuration status if logs are disabled
    if not scraper.enable_logs:
        print("📋 Configuration Status:")
        print(f"   Force Re-scrape: {scraper.force_rescrape}")
        print(f"   Enable Logs: {scraper.enable_logs}")
        print(f"   Current Year: {scraper.current_year}")
        print("=" * 50)
    
    # Run the scraper (will use config settings)
    success = scraper.run()
    
    # Check if data exists and force_rescrape is disabled
    data_file = f"data/court-accounts-publications-{datetime.now().year}.json"
    if not success and not scraper.force_rescrape and os.path.exists(data_file):
        print("\n✅ Data already exists!")
        print("📋 Force re-scraping is disabled.")
        print("💡 To re-scrape existing data, set 'force_rescrape': true in config/scraper_config.json")
        return
    
    if success:
        print("\n✅ Scraping completed successfully!")
        print("📋 Next steps:")
        print("1. Review the generated JSON file in the data/ directory")
        print("2. Check the extracted publications data")
        print("3. Use the category-based filtering for targeted scraping")
        print("4. Set up automated runs for regular updates")
        print("5. Modify config/scraper_config.json to customize settings")
    else:
        print("\n❌ Scraping failed.")
        print("📋 Possible reasons:")
        print("1. Data already exists and force_rescrape is disabled")
        print("2. Network connectivity issues")
        print("3. Website structure changes")
        print("4. Check the error messages above for details")

if __name__ == "__main__":
    main()
