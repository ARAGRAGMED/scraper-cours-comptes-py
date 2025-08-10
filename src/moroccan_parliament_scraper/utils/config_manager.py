#!/usr/bin/env python3
"""
Configuration Manager for Moroccan Parliament Legislation Scraper
"""

import json
import os
from typing import Dict, List, Optional, Any

class ConfigManager:
    """Manages configuration settings for the scraper"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        default_config = {
            "scraper_settings": {
                "force_rescrape": False,
                "enable_logs": True,
                "max_pages": 10,
                "save_format": "json"
            },
            "proxy_settings": {
                "enable_proxies": False,
                "proxies": [
                    {
                        "http": "http://proxy1.example.com:8080",
                        "https": "http://proxy1.example.com:8080"
                    },
                    {
                        "http": "http://proxy2.example.com:8080",
                        "https": "http://proxy2.example.com:8080"
                    }
                ],
                "proxy_rotation": True,
                "proxy_timeout": 10
            },
            "request_settings": {
                "timeout": 30,
                "retry_attempts": 3,
                "delay_between_requests": 2,
                "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            },
            "logging_settings": {
                "log_level": "INFO",
                "show_progress": True,
                "show_detailed_extraction": True,
                "show_commission_checks": True,
                "show_ministry_checks": True
            }
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # Merge with default config to ensure all keys exist
                    return self.merge_configs(default_config, config)
            else:
                # Create default config file
                self.save_config(default_config)
                return default_config
        except Exception as e:
            print(f"⚠️  Error loading config: {e}")
            print("📋 Using default configuration")
            return default_config
    
    def merge_configs(self, default: Dict, user: Dict) -> Dict:
        """Merge user config with default config"""
        result = default.copy()
        
        for key, value in user.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self.merge_configs(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def save_config(self, config: Dict[str, Any]) -> bool:
        """Save configuration to JSON file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"❌ Error saving config: {e}")
            return False
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """Get a configuration value using dot notation (e.g., 'scraper_settings.force_rescrape')"""
        keys = key_path.split('.')
        value = self.config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key_path: str, value: Any) -> bool:
        """Set a configuration value using dot notation"""
        keys = key_path.split('.')
        config = self.config
        
        try:
            # Navigate to the parent of the target key
            for key in keys[:-1]:
                if key not in config:
                    config[key] = {}
                config = config[key]
            
            # Set the value
            config[keys[-1]] = value
            return self.save_config(self.config)
        except Exception as e:
            print(f"❌ Error setting config value: {e}")
            return False
    
    def get_proxies(self) -> List[Dict[str, str]]:
        """Get list of proxies if enabled"""
        if self.get('proxy_settings.enable_proxies', False):
            return self.get('proxy_settings.proxies', [])
        return []
    
    def get_current_proxy(self, index: int = 0) -> Optional[Dict[str, str]]:
        """Get a specific proxy by index"""
        proxies = self.get_proxies()
        if proxies and 0 <= index < len(proxies):
            return proxies[index]
        return None
    
    def should_show_log(self, log_type: str) -> bool:
        """Check if a specific log type should be shown based on log level and settings"""
        if not self.get('scraper_settings.enable_logs', True):
            return False
        
        # Get log level and convert to numeric value
        log_level = self.get('logging_settings.log_level', 'INFO').upper()
        log_levels = {
            'DEBUG': 0,
            'INFO': 1,
            'WARNING': 2,
            'ERROR': 3,
            'CRITICAL': 4
        }
        current_level = log_levels.get(log_level, 1)  # Default to INFO
        
        # Determine log type level
        log_type_levels = {
            'progress': 1,  # INFO level
            'detailed_extraction': 0,  # DEBUG level
            'commission_checks': 1,  # INFO level
            'ministry_checks': 1,  # INFO level
            'error': 3,  # ERROR level
            'warning': 2,  # WARNING level
            'debug': 0,  # DEBUG level
        }
        
        type_level = log_type_levels.get(log_type, 1)  # Default to INFO
        
        # Only show if the log type level is >= current log level
        if type_level < current_level:
            return False
        
        # Also check the specific show_* setting
        return self.get(f'logging_settings.show_{log_type}', True)
    
    def print_config_summary(self):
        """Print a summary of current configuration"""
        print("\n" + "="*50)
        print("⚙️  CONFIGURATION SUMMARY")
        print("="*50)
        
        # Scraper settings
        print("📋 Scraper Settings:")
        print(f"   Force Re-scrape: {self.get('scraper_settings.force_rescrape')}")
        print(f"   Enable Logs: {self.get('scraper_settings.enable_logs')}")

        print(f"   Save Format: {self.get('scraper_settings.save_format')}")
        
        # Proxy settings
        print("\n🌐 Proxy Settings:")
        print(f"   Enable Proxies: {self.get('proxy_settings.enable_proxies')}")
        print(f"   Proxy Count: {len(self.get('proxy_settings.proxies', []))}")
        print(f"   Proxy Rotation: {self.get('proxy_settings.proxy_rotation')}")
        print(f"   Proxy Timeout: {self.get('proxy_settings.proxy_timeout')}s")
        
        # Request settings
        print("\n📡 Request Settings:")
        print(f"   Timeout: {self.get('request_settings.timeout')}s")
        print(f"   Retry Attempts: {self.get('request_settings.retry_attempts')}")
        print(f"   Delay Between Requests: {self.get('request_settings.delay_between_requests')}s")
        
        # Logging settings
        print("\n📝 Logging Settings:")
        print(f"   Log Level: {self.get('logging_settings.log_level')}")
        print(f"   Show Progress: {self.get('logging_settings.show_progress')}")
        print(f"   Show Detailed Extraction: {self.get('logging_settings.show_detailed_extraction')}")
        print(f"   Show Commission Checks: {self.get('logging_settings.show_commission_checks')}")
        print(f"   Show Ministry Checks: {self.get('logging_settings.show_ministry_checks')}")
        
        print("="*50)
    
    def update_proxies(self, proxies: List[Dict[str, str]]) -> bool:
        """Update the proxy list"""
        return self.set('proxy_settings.proxies', proxies)
    
    def enable_proxies(self, enable: bool = True) -> bool:
        """Enable or disable proxy usage"""
        return self.set('proxy_settings.enable_proxies', enable)
    
    def set_force_rescrape(self, force: bool = True) -> bool:
        """Set force rescrape setting"""
        return self.set('scraper_settings.force_rescrape', force)
    
    def enable_logs(self, enable: bool = True) -> bool:
        """Enable or disable logging"""
        return self.set('scraper_settings.enable_logs', enable)
