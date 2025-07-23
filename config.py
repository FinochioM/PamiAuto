LOGIN_URL = "https://cup.pami.org.ar/controllers/loginController.php"
BROWSER_TIMEOUT = 30000 #30 segundos.
HEADLESS = False # true para ejecutar en prod.
SCREENSHOT_DIR = "screenshots"
INPUT_EXCEL_FILE = r"C:\Users\matif\Development\PamiAuto\input_data\InformesPAMI.xlsx"
ERROR_INDICATORS = [
    "usuario o contraseña incorrectos",
    "error",
    "acceso denegado",
]