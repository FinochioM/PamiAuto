LOGIN_URL = "https://cup.pami.org.ar/controllers/loginController.php"
BROWSER_TIMEOUT = 30000 #30 segundos.
HEADLESS = False # true para ejecutar en prod.
SCREENSHOT_DIR = "screenshots"
ERROR_INDICATORS = [
    "usuario o contraseña incorrectos",
    "error",
    "acceso denegado",
]