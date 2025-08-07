from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QSpinBox, QGroupBox, QMessageBox,
                             QLineEdit, QFileDialog)
from PyQt6.QtCore import Qt
import os

class SettingsWindow(QDialog):
    def __init__(self, settings_manager, parent=None):
        super().__init__(parent)
        self.settings_manager = settings_manager
        self.setWindowTitle("Configuración")
        self.setGeometry(300, 300, 500, 400)
        self.setModal(True)
        
        self.setup_ui()
        self.load_current_settings()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        title_label = QLabel("Configuración de la Aplicación")
        title_label.setStyleSheet("font-weight: bold; font-size: 16px; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        browser_group = QGroupBox("Configuración del Navegador")
        browser_layout = QVBoxLayout()
        
        timeout_layout = QHBoxLayout()
        timeout_label = QLabel("Timeout del navegador (segundos):")
        self.timeout_spinbox = QSpinBox()
        self.timeout_spinbox.setMinimum(5)  # Minimum 5 seconds
        self.timeout_spinbox.setMaximum(300)  # Maximum 5 minutes
        self.timeout_spinbox.setValue(30)  # Default 30 seconds
        self.timeout_spinbox.setSuffix(" segundos")
        
        timeout_layout.addWidget(timeout_label)
        timeout_layout.addWidget(self.timeout_spinbox)
        timeout_layout.addStretch()
        
        browser_layout.addLayout(timeout_layout)
        
        help_label = QLabel("El timeout determina cuánto tiempo espera el navegador\npor los elementos de la página antes de dar error.")
        help_label.setStyleSheet("color: #666; font-size: 11px; font-style: italic;")
        browser_layout.addWidget(help_label)
        
        browser_group.setLayout(browser_layout)
        layout.addWidget(browser_group)
        
        dirs_group = QGroupBox("Configuración de Directorios")
        dirs_layout = QVBoxLayout()
        
        screenshot_layout = QHBoxLayout()
        screenshot_label = QLabel("Directorio de capturas:")
        self.screenshot_dir_input = QLineEdit()
        self.screenshot_dir_input.setReadOnly(True)
        screenshot_browse_btn = QPushButton("Examinar")
        screenshot_browse_btn.clicked.connect(self.browse_screenshot_dir)
        
        screenshot_layout.addWidget(screenshot_label)
        screenshot_layout.addWidget(self.screenshot_dir_input)
        screenshot_layout.addWidget(screenshot_browse_btn)
        
        dirs_layout.addLayout(screenshot_layout)
        
        downloads_layout = QHBoxLayout()
        downloads_label = QLabel("Directorio de descargas:")
        self.downloads_dir_input = QLineEdit()
        self.downloads_dir_input.setReadOnly(True)
        downloads_browse_btn = QPushButton("Examinar")
        downloads_browse_btn.clicked.connect(self.browse_downloads_dir)
        
        downloads_layout.addWidget(downloads_label)
        downloads_layout.addWidget(self.downloads_dir_input)
        downloads_layout.addWidget(downloads_browse_btn)
        
        dirs_layout.addLayout(downloads_layout)
        
        dir_help_label = QLabel("Los directorios se crearán automáticamente si no existen.")
        dir_help_label.setStyleSheet("color: #666; font-size: 11px; font-style: italic;")
        dirs_layout.addWidget(dir_help_label)
        
        dirs_group.setLayout(dirs_layout)
        layout.addWidget(dirs_group)
        
        layout.addStretch()
        
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
            QPushButton:pressed {
                background-color: #1e7e34;
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
            QPushButton:pressed {
                background-color: #bd2130;
            }
        """)
        cancel_btn.clicked.connect(self.close)
        
        reset_btn = QPushButton("Restablecer")
        reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
            QPushButton:pressed {
                background-color: #495057;
            }
        """)
        reset_btn.clicked.connect(self.reset_to_defaults)
        
        button_layout.addWidget(reset_btn)
        button_layout.addStretch()
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def load_current_settings(self):
        """Load current settings into the UI"""
        timeout_seconds = self.settings_manager.get_browser_timeout() // 1000
        self.timeout_spinbox.setValue(timeout_seconds)
        
        self.screenshot_dir_input.setText(self.settings_manager.get_screenshot_dir())
        self.downloads_dir_input.setText(self.settings_manager.get_downloads_dir())
    
    def browse_screenshot_dir(self):
        """Open folder dialog to select screenshot directory"""
        current_dir = self.screenshot_dir_input.text()
        if not current_dir or not os.path.exists(current_dir):
            current_dir = os.getcwd()
        
        directory = QFileDialog.getExistingDirectory(
            self, 
            "Seleccionar Directorio de Capturas", 
            current_dir
        )
        
        if directory:
            self.screenshot_dir_input.setText(directory)
    
    def browse_downloads_dir(self):
        """Open folder dialog to select downloads directory"""
        current_dir = self.downloads_dir_input.text()
        if not current_dir or not os.path.exists(current_dir):
            current_dir = os.getcwd()
        
        directory = QFileDialog.getExistingDirectory(
            self, 
            "Seleccionar Directorio de Descargas", 
            current_dir
        )
        
        if directory:
            self.downloads_dir_input.setText(directory)
    
    def save_settings(self):
        """Save settings and close dialog"""
        try:
            timeout_ms = self.timeout_spinbox.value() * 1000
            self.settings_manager.set_browser_timeout(timeout_ms)
            
            self.settings_manager.set_screenshot_dir(self.screenshot_dir_input.text())
            self.settings_manager.set_downloads_dir(self.downloads_dir_input.text())
            
            if self.settings_manager.save_settings():
                QMessageBox.information(self, "Configuración", 
                                      "Configuración guardada exitosamente.\n\nLos cambios se aplicarán en la próxima ejecución.")
                self.accept()
            else:
                QMessageBox.critical(self, "Error", "Error guardando la configuración.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error guardando configuración:\n{str(e)}")
    
    def reset_to_defaults(self):
        """Reset all settings to defaults"""
        reply = QMessageBox.question(self, "Restablecer Configuración",
                                   "¿Está seguro que desea restablecer todos los valores a sus configuraciones por defecto?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.timeout_spinbox.setValue(30)  # Default 30 seconds
            self.screenshot_dir_input.setText("screenshots")
            self.downloads_dir_input.setText("downloads")