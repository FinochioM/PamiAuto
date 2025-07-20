from browser_automation import BrowserAutomation

def main():
    automation = BrowserAutomation()
    try:
        automation.start_browser()
        automation.navigate_to_login()

        # Mantener el navegador abierto

        input("Presiona Enter para cerrar el navegador...")
    finally:
        automation.close_browser()

if __name__ == "__main__":
    main()