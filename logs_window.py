import os
import sys
import subprocess
import platform
from datetime import datetime
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QListWidget, 
                             QPushButton, QLabel, QMessageBox, QListWidgetItem)
from PyQt6.QtCore import Qt
from config import *

class LogsWindow(QDialog):
    def __init__(self, logger, parent=None):
        super().__init__(parent)
        self.logger = logger
        self.setWindowTitle("Archivos de Log")
        self.setGeometry(200, 200, 600, 400)
        self.setModal(True)
        
        self.setup_ui()
        self.load_log_files()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        title_label = QLabel("Archivos de Log disponibles:")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        self.log_list = QListWidget()
        self.log_list.setStyleSheet("""
            QListWidget {
                border: 2px solid #e0e0e0;
                border-radius: 5px;
                background-color: white;
                color: black;
                selection-background-color: #0159A9;
                selection-color: white;
                font-size: 12px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #f0f0f0;
                color: black;
            }
            QListWidget::item:hover {
                background-color: #f5f5f5;
                color: black;
            }
            QListWidget::item:selected {
                background-color: #0159A9;
                color: white;
            }
        """)
        self.log_list.itemDoubleClicked.connect(self.open_selected_file)
        layout.addWidget(self.log_list)
        
        info_label = QLabel("Doble clic en un archivo para abrirlo")
        info_label.setStyleSheet("color: #666; font-size: 11px; font-style: italic;")
        layout.addWidget(info_label)
        
        button_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("Actualizar Lista")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #0159A9;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #003d7a;
            }
            QPushButton:pressed {
                background-color: #002a5c;
            }
        """)
        refresh_btn.clicked.connect(self.load_log_files)
        button_layout.addWidget(refresh_btn)
        
        open_folder_btn = QPushButton("Abrir Carpeta de Logs")
        open_folder_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:pressed {
                background-color: #1e7e34;
            }
        """)
        open_folder_btn.clicked.connect(self.open_logs_folder)
        button_layout.addWidget(open_folder_btn)
        
        button_layout.addStretch()
        
        close_btn = QPushButton("Cerrar")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
            QPushButton:pressed {
                background-color: #bd2130;
            }
        """)
        close_btn.clicked.connect(self.close)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def load_log_files(self):
        """Load and display log files sorted by creation date (newest first)"""
        self.log_list.clear()
        
        try:
            log_files = self.logger.get_log_files()
            
            if not log_files:
                item = QListWidgetItem("No se encontraron archivos de log")
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEnabled)
                item.setData(Qt.ItemDataRole.UserRole, None)
                self.log_list.addItem(item)
                return
            
            file_details = []
            for filename in log_files:
                filepath = os.path.join(self.logger.log_dir, filename)
                if os.path.exists(filepath):
                    creation_time = os.path.getctime(filepath)
                    file_size = os.path.getsize(filepath)
                    file_details.append({
                        'filename': filename,
                        'filepath': filepath,
                        'creation_time': creation_time,
                        'size': file_size
                    })
            
            file_details.sort(key=lambda x: x['creation_time'], reverse=True)
            
            for file_info in file_details:
                filename = file_info['filename']
                filepath = file_info['filepath']
                creation_time = datetime.fromtimestamp(file_info['creation_time'])
                file_size = self.format_file_size(file_info['size'])
                
                display_text = f"{filename}\n📅 {creation_time.strftime('%Y-%m-%d %H:%M:%S')} | 📄 {file_size}"
                
                item = QListWidgetItem(display_text)
                item.setData(Qt.ItemDataRole.UserRole, filepath)
                self.log_list.addItem(item)
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error cargando archivos de log:\n{str(e)}")
    
    def format_file_size(self, size_bytes):
        """Format file size in human readable format"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
    
    def open_selected_file(self, item):
        """Open the selected log file"""
        filepath = item.data(Qt.ItemDataRole.UserRole)
        
        if not filepath:
            return
            
        if not os.path.exists(filepath):
            QMessageBox.warning(self, "Archivo no encontrado", 
                              f"El archivo no existe:\n{filepath}")
            self.load_log_files()
            return
        
        try:
            if platform.system() == "Windows":
                os.startfile(filepath)
            elif platform.system() == "Darwin":
                subprocess.run(["open", filepath])
            else:
                subprocess.run(["xdg-open", filepath])
                
        except Exception as e:
            QMessageBox.critical(self, "Error", 
                               f"No se pudo abrir el archivo:\n{str(e)}\n\nRuta: {filepath}")
    
    def open_logs_folder(self):
        """Open the logs folder in file explorer"""
        try:
            logs_path = os.path.abspath(self.logger.log_dir)
            
            if not os.path.exists(logs_path):
                QMessageBox.warning(self, "Carpeta no encontrada", 
                                  f"La carpeta de logs no existe:\n{logs_path}")
                return
            
            if platform.system() == "Windows":
                os.startfile(logs_path)
            elif platform.system() == "Darwin":
                subprocess.run(["open", logs_path])
            else:
                subprocess.run(["xdg-open", logs_path])
                
        except Exception as e:
            QMessageBox.critical(self, "Error", 
                               f"No se pudo abrir la carpeta de logs:\n{str(e)}")