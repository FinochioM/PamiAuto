from playwright.sync_api import sync_playwright
from config import *
import time
import os 
from datetime import datetime
import pandas as pd

class AutomationError(Exception):
    pass

class BrowserAutomation:
    def __init__(self, logger=None):
        self.browser = None
        self.page = None
        self.new_page = None
        self.logger = logger
        self.excel_data = []
        self.processed_rows = []
        self.failed_rows = []

    def log(self, level, message, screenshot_path=None):
        if self.logger:
            getattr(self.logger, level)(message, screenshot_path)

    def take_screenshot(self, description="error"):
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{description}_{timestamp}.png"
            filepath = os.path.join(SCREENSHOT_DIR, filename)
            
            current_page = self.new_page if self.new_page else self.page
            if current_page:
                current_page.screenshot(path=filepath)
                return filepath
        except Exception as e:
            self.log("error", f"Failed to take screenshot: {str(e)}")
        return None

    def check_for_errors(self, page):
        page_content = page.content().lower()
        for error_indicator in ERROR_INDICATORS:
            if error_indicator in page_content:
                screenshot_path = self.take_screenshot("login_error")
                self.log("error", f"Login failed: Found error indicator '{error_indicator}'", screenshot_path)
                raise AutomationError(f"Login failed: {error_indicator}")

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
        time.sleep(3)
        
        self.check_for_errors(self.page)
        
        try:
            self.page.wait_for_selector("#cup_ome", state="visible", timeout=5000)
            self.log("info", "Login exitoso: Botón OME encontrado")
        except:
            screenshot_path = self.take_screenshot("login_timeout")
            self.log("error", "Login falló: No se encontró el botón OME", screenshot_path)
            raise AutomationError("Login failed: OME button not found")

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
        time.sleep(2)

    def click_panel_prestaciones(self):
        self.log("info", "Esperando que aparezca el botón Panel de prestaciones")
        try:
            self.new_page.wait_for_selector("a[href='transmision.php']", state="visible")
            time.sleep(1)

            self.log("info", "Haciendo clic en Panel de prestaciones")
            self.new_page.click("a[href='transmision.php']")

            self.log("info", "Navegación a Panel de prestaciones completada")
        except:
            screenshot_path = self.take_screenshot("panel_error")
            self.log("error", "Error navegando a Panel de prestaciones", screenshot_path)
            raise AutomationError("Failed to navigate to Panel de prestaciones")
        
    def read_excel_data(self):
        try:
            self.log("info", f"Leyendo archivo Excel: {INPUT_EXCEL_FILE}")
            df = pd.read_excel(INPUT_EXCEL_FILE)
            self.excel_data = df.to_dict('records')
            self.log("info", f"Se leyeron {len(self.excel_data)} registros del Excel")
            return self.excel_data
        except Exception as e:
            self.log("error", f"Error leyendo archivo Excel: {str(e)}")
            raise AutomationError(f"Failed to read Excel file: {str(e)}")
        
    def process_excel_data(self, excel_data):
        self.log("info", "Procesando datos de Excel")
        processed_rows = []
        failed_rows = []

        for index, row in enumerate(excel_data):
            ndo = row.get('NDO', f'Fila_{index + 1}')
            cod_excel = row.get('COD', '')
            self.log("info", f"Iniciando procesamiento de NDO: {ndo} (Fila {index + 1})")

            try:
                # seleccionar Nro. Documento del dropdown
                self.log("info", f"NDO {ndo}: Seleccionando 'Nro. Documento' en dropdown 'Afiliado Por'")
                self.new_page.wait_for_selector("select[name='tipo_afiliado']", state="visible")
                self.new_page.select_option("select[name='tipo_afiliado']", value="2")
                self.log("info", f"NDO {ndo}: Selección completada")

                # ingresar primer dia del mes anterior en el campo 'Fecha turno desde'
                date_value = get_first_day_of_month()
                self.log("info", f"NDO {ndo}: Ingresando fecha {date_value}")
                self.new_page.wait_for_selector("input[name='f_turno_desde']", state="visible")
                self.new_page.click("input[name='f_turno_desde']")  # Foco
                self.new_page.fill("input[name='f_turno_desde']", "")  # Limpiar
                self.new_page.type("input[name='f_turno_desde']", date_value, delay=100)
                self.new_page.press("input[name='f_turno_desde']", "Enter")
                self.log("info", f"NDO {ndo}: Fecha tipeada y confirmada correctamente")

                # esperar un poco para que se actualice la pagina
                self.log("info", f"NDO {ndo}: Esperando actualización de página")
                time.sleep(3)

                self.log("info", f"NDO {ndo}: Ingresando NDO en campo de afiliado")
                self.new_page.wait_for_selector("input[name='n_afiliado']", state="visible")
                self.new_page.fill("input[name='n_afiliado']", str(ndo))
                self.log("info", f"NDO {ndo}: NDO ingresado correctamente")

                # apretar en el botón Buscar
                self.log("info", f"NDO {ndo}: Haciendo clic en botón Buscar")
                self.new_page.wait_for_selector("input[name='buscar']", state="visible")
                self.new_page.click("input[name='buscar']")
                self.log("info", f"NDO {ndo}: Búsqueda iniciada correctamente")
                
                # extraer datos de la tabla
                table_data = self.extract_table_data(ndo)

                if not table_data:
                    self.log("warning", f"NDO {ndo}: Procesado pero sin resultados")
                    processed_rows.append({
                        'NDO': ndo,
                        'Status': 'Procesado pero sin resultados',
                        'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'Resultados': 0
                    })
                    continue

                # verificar si coinciden los datos del excel con los de la tabla ('COD' en excel con 'Practica' en tabla)
                self.log("info", f"NDO {ndo}: Buscando COD {cod_excel} en {len(table_data)} resultados de la tabla.")
                cod_found = False
                matching_row = None

                for table_row in table_data:
                    practica_full = table_row.get('practica', '')
                    if ' - ' in practica_full:
                        practica_code = practica_full.split(' - ')[0].strip()
                    else:
                        practica_code = practica_full.split()[0] if practica_full else ''
                    
                    self.log("info", f"NDO {ndo}: Comparando COD {cod_excel} con codigo de practica {practica_code}")

                    if str(cod_excel) == str(practica_code):
                        cod_found = True
                        matching_row = table_row
                        self.log("info", f"NDO {ndo}: COD {cod_excel} encontrado en la tabla.")
                        break
                
                if cod_found:
                    self.log("info", f"NDO {ndo}: Procesado exitosamente - COD encontrado")
                    processed_rows.append({
                        'NDO': ndo,
                        'Status': f'Procesado exitosamente - COD {cod_excel} encontrado',
                        'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'Resultados': len(table_data),
                        'COD_Encontrado': cod_excel
                    })
                else:
                    self.log("warning", f"NDO {ndo}: COD {cod_excel} no encontrado en ninguna fila de la tabla")
                    failed_rows.append({
                        'NDO': ndo,
                        'Status': f'COD {cod_excel} no encontrado en la tabla',
                        'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'COD_Buscado': cod_excel,
                        'Resultados_Tabla': len(table_data)
                    })
            except Exception as e:
                screenshot_path = self.take_screenshot(f"error_ndo_{ndo}")
                error_msg = f"NDO {ndo}: Error en procesamiento - {str(e)}"
                self.log("error", error_msg, screenshot_path)

                failed_rows.append({
                    'NDO': ndo,
                    'Status': 'Error al procesar NDO.',
                    'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'Error': str(e),
                    'Screenshot': screenshot_path if screenshot_path else 'No se pudo tomar screenshot'
                })

        self.processed_rows = processed_rows
        self.failed_rows = failed_rows

        self.log("info", f"Procesamiento completado. Exitosos: {len(processed_rows)}, Fallidos: {len(failed_rows)}")

    def extract_table_data(self, ndo):
        try:
            self.log("info", f"NDO {ndo}: Esperando que aparezca la tabla de resultados.")
            self.new_page.wait_for_selector("table.bandeja-transmision", state="visible", timeout=10000)
            time.sleep(2)
            rows = self.new_page.query_selector_all("tbody#ordenes tr")

            if not rows:
                self.log("warning", f"NDO {ndo}: No se encontraron resultados en la tabla.")
                return []

            table_data = []
            self.log("info", f"NDO {ndo}: Se encontraron {len(rows)} filas en la tabla.")

            for index, row in enumerate(rows):
                try:
                    data_id = row.get_attribute("data-id")
                    data_practica = row.get_attribute("data-practica")
                    data_n_orden = row.get_attribute("data-n_orden")
                    data_n_beneficio = row.get_attribute("data-n_beneficio")

                    cells = row.query_selector_all("td")
                    if len(cells) >= 7:
                        row_data = {
                            'data_id': data_id,
                            'data_practica': data_practica,
                            'data_n_orden': data_n_orden,
                            'data_n_beneficio': data_n_beneficio,
                            'nro_orden': cells[0].inner_text().strip(),
                            'fecha_emision': cells[1].inner_text().strip(),
                            'nro_beneficio': cells[2].inner_text().strip(),
                            'apellido_nombre': cells[3].inner_text().strip(),
                            'practica': cells[4].inner_text().strip(),
                            'turno': cells[5].inner_text().strip(),
                            'transmitida': cells[6].inner_text().strip()
                        }
                        table_data.append(row_data)
                        self.log("info", f"NDO {ndo}: Fila {index + 1} extraída - Orden: {row_data['nro_orden']}")

                except Exception as e:
                    self.log("warning", f"NDO {ndo}: Error extrayendo fila {index + 1}: {str(e)}")
                    continue
                
            self.log("info", f"NDO {ndo}: Extracción de tabla completada. {len(table_data)} filas procesadas")
            return table_data

        except Exception as e:
            screenshot_path = self.take_screenshot(f"table_error_ndo_{ndo}")
            self.log("error", f"NDO {ndo}: Error en extracción de tabla: {str(e)}", screenshot_path)
            return []