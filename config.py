from datetime import date
from dateutil.relativedelta import relativedelta

LOGIN_URL = "https://cup.pami.org.ar/controllers/loginController.php"
BROWSER_TIMEOUT = 30000 #30 segundos.
HEADLESS = False # true para ejecutar en prod.
SCREENSHOT_DIR = "screenshots"
DOWNLOADS_DIR = "downloads"
INPUT_EXCEL_FILE = r"input_data\test_input2.xlsx"
ERROR_INDICATORS = [
    "usuario o contraseña incorrectos",
    "error",
    "acceso denegado",
]

def get_first_day_of_month():
    today = date.today()
    first_day_current_month = today.replace(day=1)
    previous_month = first_day_current_month - relativedelta(months=1)
    return previous_month.strftime("%d/%m/%Y")