import json
import os
from datetime import datetime
from config import *

class SettingsManager:
    def __init__(self):
        self.settings_file = "user_settings.json"
        self.default_settings = {
            "browser_timeout": BROWSER_TIMEOUT,
            "screenshot_dir": SCREENSHOT_DIR,
            "downloads_dir": DOWNLOADS_DIR,
            "logs_dir": "logs",
            "date_range_start_enabled": True,
            "date_range_start": "2025-08-01 07:24:00",
            "date_range_end_enabled": True,
            "date_range_end": "2025-08-01 07:25:00",
            "service_account_file": SERVICE_ACCOUNT_FILE,
            "worksheet_name": WORKSHEET_NAME,
            "google_sheets_url": GOOGLE_SHEETS_URL,
            "google_sheets_id": GOOGLE_SHEETS_ID,
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
        
    def get_date_range_start(self):
        """Get date range start as datetime object or None if disabled"""
        if not self.get("date_range_start_enabled"):
            return None
        try:
            date_str = self.get("date_range_start")
            return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        except:
            return None
        
    def set_date_range_start(self, date_time, enabled=True):
        """Set date range start"""
        self.set("date_range_start_enabled", enabled)
        if date_time and enabled:
            self.set("date_range_start", date_time.strftime("%Y-%m-%d %H:%M:%S"))
            
    def get_date_range_end(self):
        """Get date range end as datetime or None if disabled"""
        if not self.get("date_range_end_enabled"):
            return None
        try:
            date_str = self.get("date_range_end")
            return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        except:
            return None
        
    def set_date_range_end(self, date_time, enabled=True):
        """set date range end"""
        self.set("date_range_end_enabled", enabled)
        if date_time and enabled:
            self.set("date_range_end", date_time.strftime("%Y-%m-%d %H:%M:%S"))
            
    def is_date_range_start_enabled(self):
        """Check if date range start is enabled"""
        return self.get("date_range_start_enabled")
    
    def is_date_range_end_enabled(self):
        """Check if date range end is enabled"""
        return self.get("date_range_end_enabled")
    
    def get_service_account_file(self):
        """Get service account file path"""
        return self.get("service_account_file")

    def set_service_account_file(self, file_path):
        """Set service account file path"""
        self.set("service_account_file", file_path)

    def get_worksheet_name(self):
        """Get worksheet name"""
        return self.get("worksheet_name")

    def set_worksheet_name(self, name):
        """Set worksheet name"""
        self.set("worksheet_name", name)

    def get_google_sheets_url(self):
        """Get Google Sheets URL"""
        return self.get("google_sheets_url")

    def set_google_sheets_url(self, url):
        """Set Google Sheets URL"""
        self.set("google_sheets_url", url)

    def get_google_sheets_id(self):
        """Get Google Sheets ID"""
        return self.get("google_sheets_id")

    def set_google_sheets_id(self, sheets_id):
        """Set Google Sheets ID"""
        self.set("google_sheets_id", sheets_id)