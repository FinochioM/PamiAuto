from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import time
import random

# Variables de ventana de configuracion
LOGIN_URL = "https://cup.pami.org.ar/controllers/loginController.php"
BROWSER_TIMEOUT = 30000
HEADLESS = False
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

# Funciones de utilidad
def get_first_day_of_month():
    today = date.today()
    first_day_current_month = today.replace(day=1)
    previous_month = first_day_current_month - relativedelta(months=1)
    return previous_month.strftime("%d/%m/%Y")

def random_delay_short():
    """Random delay between 1-5 seconds (closer to 5)"""
    delay = random.uniform(3.0, 5.0)
    time.sleep(delay)
    return delay

def random_delay_medium():
    """Random delay between 5-10 seconds"""
    delay = random.uniform(5.0, 10.0)
    time.sleep(delay)
    return delay

def random_delay_long():
    """Random delay between 10-30 seconds (between cases)"""
    delay = random.uniform(10.0, 30.0)
    time.sleep(delay)
    return delay

def random_delay_micro():
    """Very short random delay between 0.5-2 seconds"""
    delay = random.uniform(0.5, 2.0)
    time.sleep(delay)
    return delay

def random_delay_file_operations():
    """Random delay for file operations 2-7 seconds"""
    delay = random.uniform(2.0, 7.0)
    time.sleep(delay)
    return delay

def column_number_to_letter(col_num):
    """Convert column number to letter (1=A, 2=B, etc.)"""
    result = ""
    while col_num > 0:
        col_num -= 1
        result = chr(65 + col_num % 26) + result
        col_num //= 26
    return result


# WEB ELEMENT SELECTORS
LOGIN_USERNAME_FIELD = "#usua_logeo"
LOGIN_PASSWORD_FIELD = "#password"
LOGIN_SUBMIT_BUTTON = 'input[type="submit"][value="Ingresar"]'

OME_BUTTON = "#cup_ome"
PANEL_PRESTACIONES_LINK = "a[href='transmision.php']"

AFILIADO_DROPDOWN = "select[name='tipo_afiliado']"
AFILIADO_DROPDOWN_VALUE = "2"
FECHA_TURNO_FIELD = "input[name='f_turno_desde']"
AFILIADO_NUMBER_FIELD = "input[name='n_afiliado']"
SEARCH_BUTTON = "input[name='buscar']"

RESULTS_TABLE = "table.bandeja-transmision"
TABLE_ROWS = "tbody#ordenes tr"

VALIDATION_BUTTON = ".boton-historial.fas.fa-check"
UPLOAD_BUTTON = ".boton-historial.fas.fa-upload"
TRANSMIT_BUTTON = ".boton-historial.fas.fa-arrow-right.transmitir"

BTN_SUCCESS_CLASS = "btn-success"
BTN_PRIMARY_CLASS = "btn-primary"

MODAL_DOCTYPE_DROPDOWN = "select[name='m_t_doc']"
MODAL_FILE_INPUT = "input[name='m_doc']"
MODAL_CONFIRMATION_ROWS = "tbody#documentosGrid tr"
MODAL_CLOSE_BUTTON = "button.btn-danger[data-dismiss='modal']"

TRANSMIT_CONFIRM_BUTTON = "button#transmitir-prestacion-validada"

INFORME_OPTION_TEXT = "Informe/Resultados"
CLOSE_BUTTON_TEXT = "Cerrar"
CONFIRM_BUTTON_TEXT = "Confirmar"
TRANSMISSION_SUCCESS_TEXT = "INFORMACIÓN TRANSMITIDA"