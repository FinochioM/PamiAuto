from playwright.sync_api import sync_playwright
from config import *
import time

class BrowserAutomation:
    def __init__(self, logger=None):
        self.browser = None
        self.page = None
        self.logger = logger
    
    def log(self, level, message):
        if self.logger:
            getattr(self.logger, level)(message)
    
    def start_browser(self):
        self.log("info", "Iniciando Playwright")
        self.playwright = sync_playwright().start()
        
        self.log("info", "Lanzando navegador Chromium")
        self.browser = self.playwright.chromium.launch(headless=HEADLESS)
        
        self.log("info", "Creando nueva página")
        self.page = self.browser.new_page()
        self.page.set_default_timeout(BROWSER_TIMEOUT)
        
        self.log("info", "Navegador iniciado correctamente")

    def navigate_to_login(self):
        self.log("info", f"Navegando a: {LOGIN_URL}")
        self.page.goto(LOGIN_URL)
        self.log("info", "Página cargada correctamente")

    def close_browser(self):
        if self.browser:
            self.log("info", "Cerrando navegador")
            self.browser.close()
        if hasattr(self, 'playwright'):
            self.playwright.stop()
    
    def fill_login_form(self, username, password):
        self.log("info", "Esperando que aparezca el campo de usuario")
        self.page.wait_for_selector("#usua_logeo", state="visible")
        time.sleep(1)
        
        self.log("info", "Completando campo de usuario")
        self.page.fill("#usua_logeo", username)
        
        self.log("info", "Completando campo de contraseña")
        self.page.fill("#password", password)
        
        self.log("info", "Haciendo clic en botón Ingresar")
        self.page.click('input[type="submit"][value="Ingresar"]')
        
        self.log("info", "Formulario de login completado")