import pandas as pd
import os
from datetime import datetime

class AutomationLogger:
    def __init__(self, log_dir="logs", screenshot_dir="screenshots", settings_manager = None):
        self.logs = []
        self.settings_manager = settings_manager
        
        self.fallback_log_dir = log_dir
        self.fallback_screenshot_dir = screenshot_dir
        
        self.processed_rows = []
        self.failed_rows = []

        self._ensure_directories_exist()
        
    @property
    def log_dir(self):
        """Get current log directory from settings or fallback"""
        if self.settings_manager:
            return self.settings_manager.get_logs_dir()
        return self.fallback_log_dir
    
    @property
    def screenshot_dir(self):
        """Get current screenshot directory from settings or fallback"""
        if self.settings_manager:
            return self.settings_manager.get_screenshot_dir()
        return self.fallback_screenshot_dir
    
    def _ensure_directories_exist(self):
        """Create directories if they don't exist"""
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
        if not os.path.exists(self.screenshot_dir):
            os.makedirs(self.screenshot_dir)
    
    def set_directories(self, log_dir, screenshot_dir):
        self.log_dir = log_dir
        self.screenshot_dir = screenshot_dir
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
        if not os.path.exists(self.screenshot_dir):
            os.makedirs(self.screenshot_dir)
    
    def log(self, level, message, screenshot_path=None):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = {
            "timestamp": timestamp,
            "level": level,
            "message": message
        }
        if screenshot_path:
            log_entry["screenshot"] = screenshot_path
        
        self.logs.append(log_entry)
        print(f"[{timestamp}] {level}: {message}")

    def info(self, message, screenshot_path=None):
        self.log("INFO", message, screenshot_path)
    
    def error(self, message, screenshot_path=None):
        self.log("ERROR", message, screenshot_path)
    
    def warning(self, message, screenshot_path=None):
        self.log("WARNING", message, screenshot_path)
    
    def save_to_excel(self, processed_rows=None, failed_rows=None, already_processed=None):
        self._ensure_directories_exist()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"automation_log_{timestamp}.xlsx"
        filepath = os.path.join(self.log_dir, filename)
        
        with pd.ExcelWriter(filepath) as writer:
            if self.logs:
                df_logs = pd.DataFrame(self.logs)
                df_logs.to_excel(writer, sheet_name='Logs', index=False)
            
            if processed_rows:
                df_processed = pd.DataFrame(processed_rows)
                df_processed.to_excel(writer, sheet_name='Processed', index=False)
    
            if failed_rows:
                df_failed = pd.DataFrame(failed_rows)
                df_failed.to_excel(writer, sheet_name='Not_Processed', index=False)
                
            if already_processed:
                df_already_processed = pd.DataFrame(already_processed)
                df_already_processed.to_excel(writer, sheet_name='Already_Processed', index=False)
        
        return filepath
    
    def get_log_files(self):
        if not os.path.exists(self.log_dir):
            return []
        
        files = [f for f in os.listdir(self.log_dir) if f.endswith('.xlsx')]
        files.sort(reverse=True)
        return files