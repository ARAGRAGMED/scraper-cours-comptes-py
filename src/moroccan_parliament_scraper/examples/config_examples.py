#!/usr/bin/env python3
"""
Example script showing how to use the configuration system
"""

from ..utils.config_manager import ConfigManager
from ..core.legislation_scraper import MoroccanParliamentScraper

def example_config_usage():
    """Demonstrate configuration usage"""
    
    print("🔧 CONFIGURATION SYSTEM EXAMPLES")
    print("=" * 50)
    
    # 1. Load and display current configuration
    print("\n1. 📋 Current Configuration:")
    config = ConfigManager()
    config.print_config_summary()
    
    # 2. Update configuration programmatically
    print("\n2. ⚙️  Updating Configuration:")
    
    # Enable force rescrape
    config.set_force_rescrape(True)
    print("✅ Set force_rescrape = True")
    
    # Disable detailed extraction logs
    config.set('logging_settings.show_detailed_extraction', False)
    print("✅ Disabled detailed extraction logs")
    
    # Add a custom proxy
    custom_proxies = [
        {
            "http": "http://your-proxy-server.com:8080",
            "https": "http://your-proxy-server.com:8080"
        }
    ]
    config.update_proxies(custom_proxies)
    print("✅ Added custom proxy")
    
    # Enable proxy usage
    config.enable_proxies(True)
    print("✅ Enabled proxy usage")
    
    # 3. Show updated configuration
    print("\n3. 📋 Updated Configuration:")
    config.print_config_summary()
    
    # 4. Run scraper with custom configuration
    print("\n4. 🚀 Running Scraper with Custom Config:")
    print("Note: This will use the updated configuration settings")
    
    # Uncomment the line below to actually run the scraper
    # scraper = MoroccanParliamentScraper()
    # success = scraper.run()
    
    print("(Scraper execution commented out for demo purposes)")
    
    # 5. Reset to default configuration
    print("\n5. 🔄 Resetting to Default Configuration:")
    config.set_force_rescrape(False)
    config.set('logging_settings.show_detailed_extraction', True)
    config.enable_proxies(False)
    config.update_proxies([])
    print("✅ Reset to default configuration")

def example_proxy_configuration():
    """Example of proxy configuration"""
    
    print("\n🌐 PROXY CONFIGURATION EXAMPLE")
    print("=" * 40)
    
    config = ConfigManager()
    
    # Example proxy list
    example_proxies = [
        {
            "http": "http://proxy1.company.com:8080",
            "https": "http://proxy1.company.com:8080"
        },
        {
            "http": "http://proxy2.company.com:8080", 
            "https": "http://proxy2.company.com:8080"
        },
        {
            "http": "http://proxy3.company.com:8080",
            "https": "http://proxy3.company.com:8080"
        }
    ]
    
    print("📋 Example proxy configuration:")
    for i, proxy in enumerate(example_proxies, 1):
        print(f"   Proxy {i}: {proxy['http']}")
    
    print("\n💡 To use these proxies:")
    print("1. Update the 'proxies' array in config.json")
    print("2. Set 'enable_proxies' to true")
    print("3. Set 'proxy_rotation' to true for automatic rotation")

def example_logging_configuration():
    """Example of logging configuration"""
    
    print("\n📝 LOGGING CONFIGURATION EXAMPLE")
    print("=" * 40)
    
    print("📋 Available logging options:")
    print("   • show_progress: Main progress messages")
    print("   • show_detailed_extraction: Detailed extraction logs")
    print("   • show_commission_checks: Commission checking logs")
    print("   • show_ministry_checks: Ministry checking logs")
    
    print("\n💡 To disable specific log types:")
    print("1. Set 'enable_logs' to false to disable all logs")
    print("2. Set individual 'show_*' options to false")
    print("3. Example: 'show_commission_checks': false")

if __name__ == "__main__":
    example_config_usage()
    example_proxy_configuration()
    example_logging_configuration()
    
    print("\n" + "=" * 50)
    print("🎉 Configuration examples completed!")
    print("📋 Check config.json to see the current settings")
    print("🔧 Modify config.json to customize the scraper behavior")
