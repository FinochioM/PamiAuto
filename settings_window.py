from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QSpinBox, QGroupBox, QMessageBox,
                             QLineEdit, QFileDialog, QDateTimeEdit, QCheckBox)
from PyQt6.QtCore import Qt, QDateTime
import os
from datetime import datetime

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
        
        date_group = QGroupBox("Filtro de Rango de Fechas")
        date_layout = QVBoxLayout()
        
        start_layout = QHBoxLayout()
        self.start_enabled_checkbox = QCheckBox("Fecha de inicio:")
        self.start_enabled_checkbox.stateChanged.connect(self.on_start_enabled_changed)
        self.start_datetime = QDateTimeEdit()
        self.start_datetime.setDisplayFormat("yyyy-MM-dd hh:mm:ss")
        self.start_datetime.setDateTime(QDateTime.currentDateTime())
        
        start_layout.addWidget(self.start_enabled_checkbox)
        start_layout.addWidget(self.start_datetime)
        start_layout.addStretch()
        
        date_layout.addLayout(start_layout)
      
        end_layout = QHBoxLayout()
        self.end_enabled_checkbox = QCheckBox("Fecha de fin:")
        self.end_enabled_checkbox.stateChanged.connect(self.on_end_enabled_changed)
        self.end_datetime = QDateTimeEdit()
        self.end_datetime.setDisplayFormat("yyyy-MM-dd hh:mm:ss")
        self.end_datetime.setDateTime(QDateTime.currentDateTime())
        
        end_layout.addWidget(self.end_enabled_checkbox)
        end_layout.addWidget(self.end_datetime)
        end_layout.addStretch()
        
        date_layout.addLayout(end_layout)
        
        date_help_label = QLabel("Desmarca las casillas para procesar todos los registros sin filtro de fecha.\nSi solo marcas una fecha, se aplicará como límite único.")
        date_help_label.setStyleSheet("color: #666; font-size: 11px; font-style: italic;")
        date_layout.addWidget(date_help_label)
        
        date_group.setLayout(date_layout)
        layout.addWidget(date_group)
        
        sheets_group = QGroupBox("Configuración de Google Sheets")
        sheets_layout = QVBoxLayout()
        
        service_account_layout = QHBoxLayout()
        service_account_label = QLabel("Archivo de credenciales:")
        self.service_account_input = QLineEdit()
        self.service_account_input.setReadOnly(True)
        service_account_browse_btn = QPushButton("Examinar")
        service_account_browse_btn.clicked.connect(self.browse_service_account_file)
        
        service_account_layout.addWidget(service_account_label)
        service_account_layout.addWidget(self.service_account_input)
        service_account_layout.addWidget(service_account_browse_btn)
        
        sheets_layout.addLayout(service_account_layout)
        
        worksheet_layout = QHBoxLayout()
        worksheet_label = QLabel("Nombre de la hoja:")
        self.worksheet_name_input = QLineEdit()
        self.worksheet_name_input.setPlaceholderText("prestaciones_PAMI")
        
        worksheet_layout.addWidget(worksheet_label)
        worksheet_layout.addWidget(self.worksheet_name_input)
        worksheet_layout.addStretch()
        
        sheets_layout.addLayout(worksheet_layout)
        
        url_layout = QHBoxLayout()
        url_label = QLabel("URL de Google Sheets:")
        self.sheets_url_input = QLineEdit()
        self.sheets_url_input.setPlaceholderText("https://docs.google.com/spreadsheets/d/...")
        
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.sheets_url_input)
        
        sheets_layout.addLayout(url_layout)
        
        id_layout = QHBoxLayout()
        id_label = QLabel("ID de Google Sheets:")
        self.sheets_id_input = QLineEdit()
        self.sheets_id_input.setPlaceholderText("16r7nB5lPMLEmTEk7Np0knv-AUvBVIktdjA36Ya96JAk")
        
        id_layout.addWidget(id_label)
        id_layout.addWidget(self.sheets_id_input)
        
        sheets_layout.addLayout(id_layout)
        
        sheets_help_label = QLabel("Cambiar la URL o ID requiere acceso al nuevo Google Sheets.\nSolo modifica estos valores si sabes lo que estás haciendo.")
        sheets_help_label.setStyleSheet("color: #e67e22; font-size: 11px; font-style: italic;")
        sheets_layout.addWidget(sheets_help_label)
        
        sheets_group.setLayout(sheets_layout)
        layout.addWidget(sheets_group)
        
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
        
        logs_layout = QHBoxLayout()
        logs_label = QLabel("Directorio de logs:")
        self.logs_dir_input = QLineEdit()
        self.logs_dir_input.setReadOnly(True)
        logs_browse_btn = QPushButton("Examinar")
        logs_browse_btn.clicked.connect(self.browse_logs_dir)

        logs_layout.addWidget(logs_label)
        logs_layout.addWidget(self.logs_dir_input)
        logs_layout.addWidget(logs_browse_btn)

        dirs_layout.addLayout(logs_layout)
        
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
        self.logs_dir_input.setText(self.settings_manager.get_logs_dir())
        
        start_enabled = self.settings_manager.is_date_range_start_enabled()
        self.start_enabled_checkbox.setChecked(start_enabled)
        self.start_datetime.setEnabled(start_enabled)
        
        self.service_account_input.setText(self.settings_manager.get_service_account_file())
        self.worksheet_name_input.setText(self.settings_manager.get_worksheet_name())
        self.sheets_url_input.setText(self.settings_manager.get_google_sheets_url())
        self.sheets_id_input.setText(self.settings_manager.get_google_sheets_id())
        
        start_date = self.settings_manager.get_date_range_start()
        if start_date:
            self.start_datetime.setDateTime(QDateTime.fromSecsSinceEpoch(int(start_date.timestamp())))
        
        end_enabled = self.settings_manager.is_date_range_end_enabled()
        self.end_enabled_checkbox.setChecked(end_enabled)
        self.end_datetime.setEnabled(end_enabled)
        
        end_date = self.settings_manager.get_date_range_end()
        if end_date:
            self.end_datetime.setDateTime(QDateTime.fromSecsSinceEpoch(int(end_date.timestamp())))
    
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
            self.settings_manager.set_logs_dir(self.logs_dir_input.text())
            
            start_enabled = self.start_enabled_checkbox.isChecked()
            start_datetime = None
            if start_enabled:
                qt_datetime = self.start_datetime.dateTime()
                start_datetime = datetime.fromtimestamp(qt_datetime.toSecsSinceEpoch())
            self.settings_manager.set_date_range_start(start_datetime, start_enabled)
            
            end_enabled = self.end_enabled_checkbox.isChecked()
            end_datetime = None
            if end_enabled:
                qt_datetime = self.end_datetime.dateTime()
                end_datetime = datetime.fromtimestamp(qt_datetime.toSecsSinceEpoch())
            self.settings_manager.set_date_range_end(end_datetime, end_enabled)
            
            self.settings_manager.set_service_account_file(self.service_account_input.text())
            self.settings_manager.set_worksheet_name(self.worksheet_name_input.text())
            self.settings_manager.set_google_sheets_url(self.sheets_url_input.text())
            self.settings_manager.set_google_sheets_id(self.sheets_id_input.text())
            
            if self.settings_manager.save_settings():
                QMessageBox.information(self, "Configuración", 
                                      "Configuración guardada exitosamente.\n\nLos cambios se aplicarán inmediatamente.")
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
            self.logs_dir_input.setText("logs")
            
            self.start_enabled_checkbox.setChecked(True)
            self.end_enabled_checkbox.setChecked(True)
            current_time = QDateTime.currentDateTime()
            self.start_datetime.setDateTime(current_time)
            self.end_datetime.setDateTime(current_time)
            self.start_datetime.setEnabled(True)
            self.end_datetime.setEnabled(True)
            
            self.service_account_input.setText("credenciales_bio_sheets.json")
            self.worksheet_name_input.setText("prestaciones_PAMI")
            self.sheets_url_input.setText("https://docs.google.com/spreadsheets/d/16r7nB5lPMLEmTEk7Np0knv-AUvBVIktdjA36Ya96JAk/edit?gid=438980283#gid=438980283&fvid=86172977")
            self.sheets_id_input.setText("16r7nB5lPMLEmTEk7Np0knv-AUvBVIktdjA36Ya96JAk")

    def browse_logs_dir(self):
        """Open folder dialog to select logs directory"""
        current_dir = self.logs_dir_input.text()
        if not current_dir or not os.path.exists(current_dir):
            current_dir = os.getcwd()
        
        directory = QFileDialog.getExistingDirectory(
            self, 
            "Seleccionar Directorio de Logs", 
            current_dir
        )
        
        if directory:
            self.logs_dir_input.setText(directory)
            
    def on_start_enabled_changed(self):
        """Enable/disable start datetime picker"""
        self.start_datetime.setEnabled(self.start_enabled_checkbox.isChecked())
    
    def on_end_enabled_changed(self):
        """Enable/disable end datetime picker"""
        self.end_datetime.setEnabled(self.end_enabled_checkbox.isChecked())
    
    def browse_service_account_file(self):
        """Open file dialog to select service account JSON file"""
        current_file = self.service_account_input.text()
        if current_file and os.path.exists(current_file):
            current_dir = os.path.dirname(current_file)
        else:
            current_dir = os.getcwd()
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar Archivo de Credenciales",
            current_dir,
            "JSON Files (*.json);;All Files (*)"
        )
        
        if file_path:
            self.service_account_input.setText(file_path)