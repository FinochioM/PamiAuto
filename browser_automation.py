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
        if hasattr(self, 'new_page') and self.new_page:
            self.log("info", "Cerrando página OME")
            self.new_page.close()
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
        
        self.log("info", "Formulario de login completado, esperando...")
        time.sleep(2)  # Esperar unos segundos para que se cargue la página

    def click_ome_button(self):
        self.log("info", "Esperando que aparezca el botón OME")
        self.page.wait_for_selector("#cup_ome", state="visible")
        time.sleep(1)
        
        self.log("info", "Haciendo clic en botón OME")
        with self.page.context.expect_page() as new_page_info:
            self.page.click("#cup_ome")
        
        self.new_page = new_page_info.value
        self.new_page.set_default_timeout(BROWSER_TIMEOUT)
        
        self.log("info", "Nueva página OME abierta correctamente")
        self.log("info", f"URL de nueva página: {self.new_page.url}")
        time.sleep(2)  # Esperar unos segundos para que se cargue la página
    
    def click_panel_prestaciones(self):
        self.log("info", "Esperando que aparezca el botón Panel de prestaciones")
        self.new_page.wait_for_selector("a[href='transmision.php']", state="visible")
        time.sleep(1)
        
        self.log("info", "Haciendo clic en Panel de prestaciones")
        self.new_page.click("a[href='transmision.php']")
        
        self.log("info", "Navegación a Panel de prestaciones completada")