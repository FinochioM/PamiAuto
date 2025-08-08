import json
import os
from config import *

class SettingsManager:
    def __init__(self):
        self.settings_file = "user_settings.json"
        self.default_settings = {
            "browser_timeout": BROWSER_TIMEOUT,
            "screenshot_dir": SCREENSHOT_DIR,
            "downloads_dir": DOWNLOADS_DIR,
            "logs_dir": "logs",
        }
        self.settings = self.load_settings()
    
    def load_settings(self):
        """Load settings from file, create with defaults if not exists"""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                merged_settings = self.default_settings.copy()
                merged_settings.update(settings)
                return merged_settings
            except Exception as e:
                print(f"Error loading settings: {e}")
                return self.default_settings.copy()
        else:
            return self.default_settings.copy()
    
    def save_settings(self):
        """Save current settings to file"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False
    
    def get(self, key):
        """Get a setting value"""
        return self.settings.get(key, self.default_settings.get(key))
    
    def set(self, key, value):
        """Set a setting value"""
        self.settings[key] = value
    
    def get_browser_timeout(self):
        """Get browser timeout in milliseconds"""
        return self.get("browser_timeout")
    
    def set_browser_timeout(self, timeout_ms):
        """Set browser timeout in milliseconds"""
        self.set("browser_timeout", timeout_ms)
    
    def get_screenshot_dir(self):
        """Get screenshot directory"""
        return self.get("screenshot_dir")
    
    def set_screenshot_dir(self, directory):
        """Set screenshot directory"""
        self.set("screenshot_dir", directory)
    
    def get_downloads_dir(self):
        """Get downloads directory"""
        return self.get("downloads_dir")
    
    def set_downloads_dir(self, directory):
        """Set downloads directory"""
        self.set("downloads_dir", directory)
        
    def get_logs_dir(self):
        """Get logs directory"""
        return self.get("logs_dir")
    
    def set_logs_dir(self, directory):
        """Set logs directory"""
        self.set("logs_dir", directory)