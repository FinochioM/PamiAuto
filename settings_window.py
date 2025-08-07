import os
import json
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QLineEdit, QMessageBox, QFileDialog, QTextEdit)
from PyQt6.QtCore import Qt

class SettingsWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuración")
        self.setGeometry(200, 200, 500, 400)
        self.setModal(True)
        
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        google_label = QLabel("Configuración de Google Sheets:")
        google_label.setStyleSheet("font-weight: bold; font-size: 14px; margin-bottom: 10px;")
        layout.addWidget(google_label)
        
        creds_layout = QHBoxLayout()
        self.creds_path_edit = QLineEdit()
        self.creds_path_edit.setPlaceholderText("Ruta al archivo credentials.json de Google")
        self.creds_path_edit.setReadOnly(True)
        
        browse_btn = QPushButton("Examinar")
        browse_btn.clicked.connect(self.browse_credentials_file)
        
        creds_layout.addWidget(QLabel("Archivo de credenciales:"))
        creds_layout.addWidget(self.creds_path_edit)
        creds_layout.addWidget(browse_btn)
        layout.addLayout(creds_layout)
        
        instructions = QTextEdit()
        instructions.setMaximumHeight(150)
        instructions.setReadOnly(True)
        instructions.setPlainText("""Instrucciones para configurar Google Sheets:

1. Ve a Google Cloud Console (console.cloud.google.com)
2. Crea un nuevo proyecto o selecciona uno existente
3. Habilita la API de Google Sheets
4. Crea credenciales (OAuth 2.0 Client ID)
5. Descarga el archivo JSON de credenciales
6. Usa el botón "Examinar" para seleccionar el archivo""")
        layout.addWidget(instructions)
        
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("Guardar")
        save_btn.setStyleSheet("""
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
        """)
        save_btn.clicked.connect(self.save_settings)
        
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.setStyleSheet("""
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
        """)
        cancel_btn.clicked.connect(self.close)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def browse_credentials_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Seleccionar archivo de credenciales",
            "",
            "JSON files (*.json)"
        )
        if file_path:
            self.creds_path_edit.setText(file_path)
    
    def load_settings(self):
        """Load saved settings"""
        try:
            if os.path.exists("app_settings.json"):
                with open("app_settings.json", "r") as f:
                    settings = json.load(f)
                    self.creds_path_edit.setText(settings.get("google_credentials_path", ""))
        except Exception as e:
            print(f"Error loading settings: {e}")
    
    def save_settings(self):
        """Save settings to file"""
        try:
            settings = {
                "google_credentials_path": self.creds_path_edit.text()
            }
            
            with open("app_settings.json", "w") as f:
                json.dump(settings, f, indent=2)
            
            QMessageBox.information(self, "Configuración", "Configuración guardada exitosamente")
            self.close()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error guardando configuración:\n{str(e)}")