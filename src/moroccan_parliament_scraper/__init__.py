#!/usr/bin/env python3
"""
Moroccan Court of Accounts Publications Scraper

A comprehensive web scraper for extracting current year publications data
from the Moroccan Court of Accounts website with enhanced filtering,
proxy support, and configuration management.
"""

__version__ = "1.0.0"
__author__ = "Court of Accounts Scraper Team"
__description__ = "Enhanced scraper for Moroccan Court of Accounts publications with configuration management and proxy support"

# Import main classes for easy access
from .core.court_accounts_scraper import CourtOfAccountsScraper
from .utils.config_manager import ConfigManager

# Main exports
__all__ = [
    'CourtOfAccountsScraper',
    'ConfigManager',
]

# Package metadata
__package_info__ = {
    'name': 'court_accounts_scraper',
    'version': __version__,
    'description': __description__,
    'author': __author__,
    'main_class': 'CourtOfAccountsScraper',
    'config_class': 'ConfigManager',
}
