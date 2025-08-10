#!/usr/bin/env python3
"""
Main script for Moroccan Parliament Legislation Scraper
"""

from .core.legislation_scraper import MoroccanParliamentScraper

def main():
    """Main function to run the scraper"""
    # Create scraper instance with configuration
    scraper = MoroccanParliamentScraper()
    
    # Run the scraper (will use config settings)
    success = scraper.run()
    
    if success:
        print("\n✅ Scraping completed successfully!")
        print("📋 Next steps:")
        print("1. Review the generated JSON file")
        print("2. Check the extracted legislation data")
        print("3. Use the commission-based filtering for targeted scraping")
        print("4. Set up automated runs for regular updates")
        print("5. Modify config.json to customize settings")
    else:
        print("\n❌ Scraping failed. Check the error messages above.")

if __name__ == "__main__":
    main()
