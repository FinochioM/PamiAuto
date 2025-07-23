import pandas as pd
import os
from datetime import datetime

class AutomationLogger:
    def __init__(self, log_dir="logs", screenshot_dir="screenshots"):
        self.logs = []
        self.log_dir = log_dir
        self.screenshot_dir = screenshot_dir
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
    
    def save_to_excel(self):
        if not self.logs:
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"automation_log_{timestamp}.xlsx"
        filepath = os.path.join(self.log_dir, filename)
        
        df = pd.DataFrame(self.logs)
        df.to_excel(filepath, index=False)
        
        return filepath
    
    def get_log_files(self):
        if not os.path.exists(self.log_dir):
            return []
        
        files = [f for f in os.listdir(self.log_dir) if f.endswith('.xlsx')]
        files.sort(reverse=True)
        return files