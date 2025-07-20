from playwright.sync_api import sync_playwright
from config import *

class BrowserAutomation:
    def __init__(self):
        self.browser = None
        self.page = None
    
    def start_browser(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=HEADLESS)
        self.page = self.browser.new_page()
        self.page.set_default_timeout(BROWSER_TIMEOUT)

    def navigate_to_login(self):
        self.page.goto(LOGIN_URL)

    def close_browser(self):
        if self.browser:
            self.browser.close()
        if hasattr(self, 'playwright'):
            self.playwright.stop()