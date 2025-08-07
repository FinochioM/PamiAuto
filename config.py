from datetime import date, datetime
from dateutil.relativedelta import relativedelta

LOGIN_URL = "https://cup.pami.org.ar/controllers/loginController.php"
BROWSER_TIMEOUT = 30000 # migrated to settings
HEADLESS = False # true para ejecutar en prod.
SCREENSHOT_DIR = "screenshots"
DOWNLOADS_DIR = "downloads"
ERROR_INDICATORS = [
    "usuario o contraseña incorrectos",
    "error",
    "acceso denegado",
]

GOOGLE_SHEETS_URL = "https://docs.google.com/spreadsheets/d/16r7nB5lPMLEmTEk7Np0knv-AUvBVIktdjA36Ya96JAk/edit?gid=438980283#gid=438980283&fvid=86172977"
GOOGLE_SHEETS_ID = "16r7nB5lPMLEmTEk7Np0knv-AUvBVIktdjA36Ya96JAk"
WORKSHEET_NAME = "prestaciones_PAMI"
SERVICE_ACCOUNT_FILE = "credenciales_bio_sheets.json"

DATE_RANGE_START = datetime(2025, 8, 1, 7, 24) 
DATE_RANGE_END = datetime(2025, 8, 1, 7, 25)

def get_first_day_of_month():
    today = date.today()
    first_day_current_month = today.replace(day=1)
    previous_month = first_day_current_month - relativedelta(months=1)
    return previous_month.strftime("%d/%m/%Y")