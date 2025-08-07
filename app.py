import sys
import threading
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt6.QtCore import QTimer, pyqtSignal, QObject
from browser_automation import BrowserAutomation
from logger import AutomationLogger
from logs_window import LogsWindow
from settings_manager import SettingsManager
from settings_window import SettingsWindow

class WorkerSignals(QObject):
    status_update = pyqtSignal(str, str)
    error_occurred = pyqtSignal(str)
    automation_finished = pyqtSignal()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(r"..\PamiAuto\ui\main.ui", self)
        
        self.settings_manager = SettingsManager()
        
        self.automation = None
        self.logger = AutomationLogger(settings_manager=self.settings_manager)
        self.worker_signals = WorkerSignals()
        
        self.setup_connections()
        self.setup_signals()
        
        self.setup_initial_state()
    
    def setup_connections(self):
        self.startAutomation.clicked.connect(self.start_automation_thread)
        
        # agregar despues
        self.logsButton.clicked.connect(self.show_logs)
        self.settingsButton.clicked.connect(self.show_settings)
    
    def setup_signals(self):
        self.worker_signals.status_update.connect(self.update_status)
        self.worker_signals.error_occurred.connect(self.show_error)
        self.worker_signals.automation_finished.connect(self.automation_completed)
    
    def setup_initial_state(self):
        self.passInput.setEchoMode(self.passInput.EchoMode.Password)

        self.userInput.setPlaceholderText("Ingrese su usuario")
        self.passInput.setPlaceholderText("Ingrese su contraseña")
    
    def start_automation_thread(self):
        username = self.userInput.text().strip()
        password = self.passInput.text().strip()
        
        if not username or not password:
            self.logger.error("Usuario o contraseña vacíos")
            QMessageBox.critical(self, "Error", "Por favor ingrese usuario y contraseña")
            return
        
        self.startAutomation.setEnabled(False)
        self.startAutomation.setText("Ejecutando...")
        
        thread = threading.Thread(target=self.run_automation, args=(username, password))
        thread.daemon = True
        thread.start()
    
    def run_automation(self, username, password):
        try:
            self.logger.info("Iniciando automatización")
            self.worker_signals.status_update.emit("Iniciando automatización...", "orange")
            
            self.logger.info("Creando instancia de BrowserAutomation")
            self.automation = BrowserAutomation(self.logger, self.settings_manager)

            self.logger.info("Leyendo datos de Excel")
            self.worker_signals.status_update.emit("Leyendo datos de Excel...", "orange")
            excel_data = self.automation.read_excel_data()

            self.logger.info("Iniciando navegador")
            self.worker_signals.status_update.emit("Iniciando navegador...", "orange")
            self.automation.start_browser()
            
            self.logger.info("Navegando a página de login")
            self.worker_signals.status_update.emit("Navegando a login...", "orange")
            self.automation.navigate_to_login()
            
            self.logger.info("Completando formulario de login")
            self.worker_signals.status_update.emit("Completando login...", "orange")
            self.automation.fill_login_form(username, password)
            
            self.logger.info("Haciendo clic en botón OME")
            self.worker_signals.status_update.emit("Navegando a OME...", "orange")
            self.automation.click_ome_button()
            
            self.logger.info("Haciendo clic en Panel de prestaciones")
            self.worker_signals.status_update.emit("Navegando a Panel...", "orange")
            self.automation.click_panel_prestaciones()

            self.worker_signals.status_update.emit("Loopeando sobre el excel", "orange")
            self.automation.process_excel_data(excel_data)

            self.logger.info("Automatización completada exitosamente")
            self.worker_signals.status_update.emit("Automatización completada", "green")
            
        except Exception as e:
            error_msg = f"Error en automatización: {str(e)}"
            self.logger.error(error_msg)
            self.worker_signals.error_occurred.emit(error_msg)
            self.worker_signals.status_update.emit("Error en automatización", "red")
        
        finally:
            if self.automation:
                self.automation.close_browser()
            self.worker_signals.automation_finished.emit()
    
    def update_status(self, message, color):
        print(f"Status: {message} (Color: {color})")
    
    def show_error(self, error_message):
        QMessageBox.critical(self, "Error", error_message)
    
    def automation_completed(self):
        self.startAutomation.setEnabled(True)
        self.startAutomation.setText("Iniciar Automatización")
        
        processed_rows = getattr(self.automation, 'processed_rows', [])
        failed_rows = getattr(self.automation, 'failed_rows', [])
        already_processed = getattr(self.automation, 'already_processed_cases', [])
        
        log_file = self.logger.save_to_excel(processed_rows, failed_rows, already_processed)
        if log_file:
            self.logger.info(f"Log guardado en: {log_file}")
    
    def show_logs(self):
        logs_window = LogsWindow(self.logger, self)
        logs_window.exec()
    
    def show_settings(self):
        settings_window = SettingsWindow(self.settings_manager, self)
        settings_window.exec()

def main():
    app = QApplication(sys.argv)
    
    window = MainWindow()
    window.show()
    
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()