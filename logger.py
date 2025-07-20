import pandas as pd
import os
from datetime import datetime

class AutomationLogger:
    def __init__(self, log_dir="logs"):
        self.logs = []
        self.log_dir = log_dir
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
    
    def set_log_directory(self, new_dir):
        self.log_dir = new_dir
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
    
    def log(self, level, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.logs.append({
            "timestamp": timestamp,
            "level": level,
            "message": message
        })
        print(f"[{timestamp}] {level}: {message}")
    
    def info(self, message):
        self.log("INFO", message)
    
    def error(self, message):
        self.log("ERROR", message)
    
    def warning(self, message):
        self.log("WARNING", message)
    
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
        files.sort(reverse=True)  # Mas reciente primero
        return files