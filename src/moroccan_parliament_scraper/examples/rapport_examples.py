#!/usr/bin/env python3
"""
Example script to demonstrate how to access rapport section data
"""

import json
import sys
import os

# Add the parent directory to the path to import the scraper
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from moroccan_parliament_scraper.core.legislation_scraper import MoroccanParliamentScraper

def access_rapport_data():
    """Example of how to access rapport section data from Lecture 2 items"""
    
    # Load the JSON data
    with open('extracted-data-2025.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("🔍 Accessing Rapport Section Data from Lecture 2 Items")
    print("=" * 60)
    
    # Find Lecture 2 items
    lecture2_items = [item for item in data['data'] if item['stage'] == 'Lecture 2']
    
    if not lecture2_items:
        print("❌ No Lecture 2 items found in the data")
        return
    
    print(f"✅ Found {len(lecture2_items)} Lecture 2 item(s)")
    print()
    
    for i, item in enumerate(lecture2_items, 1):
        print(f"📋 Item {i}: {item['law_number']} - {item['title'][:80]}...")
        
        # Access rapport section data
        if 'deuxieme_lecture' in item and 'rapport_section' in item['deuxieme_lecture']:
            rapport = item['deuxieme_lecture']['rapport_section']
            
            print(f"   📄 Rapport Section: {rapport['section_title']}")
            print(f"   📁 Files found: {len(rapport['files'])}")
            
            for j, file_info in enumerate(rapport['files'], 1):
                print(f"      {j}. {file_info['title']}")
                print(f"         📎 URL: {file_info['url']}")
                print(f"         📏 Size: {file_info['size']}")
                print(f"         📄 Filename: {file_info['filename']}")
                print()
        else:
            print("   ❌ No rapport section found")
            print()
    
    print("🎯 Example Code to Access Rapport Data:")
    print("=" * 40)
    print("""
# Load JSON data
with open('extracted-data-2025.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Find Lecture 2 items
lecture2_items = [item for item in data['data'] if item['stage'] == 'Lecture 2']

# Access rapport section for each Lecture 2 item
for item in lecture2_items:
    if 'deuxieme_lecture' in item and 'rapport_section' in item['deuxieme_lecture']:
        rapport = item['deuxieme_lecture']['rapport_section']
        print(f"Section: {rapport['section_title']}")
        
        for file_info in rapport['files']:
            print(f"  - {file_info['title']}: {file_info['url']}")
    """)

if __name__ == "__main__":
    access_rapport_data()
