from playwright.sync_api import sync_playwright
from config import *
import time
import os 
from datetime import datetime
import pandas as pd
import requests

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
                    self.log("warning", f"NDO {ndo}: No se encontraron datos en la tabla.")
                    processed_rows.append({
                        'NDO': ndo,
                        'Status': 'No se encontraron datos en la tabla.',
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
                    self.log("info", f"NDO {ndo}: COD encontrado en la tabla.")
                    
                    button_status, error_screenshot = self.check_button_status(ndo, matching_row)
                    
                    if button_status == "processed":
                        self.log("info", f"NDO {ndo}: Caso ya procesado - Marcando como completado.")
                        processed_rows.append({
                            'NDO': ndo,
                            'Status': f'Ya estaba procesado - COD {cod_excel}',
                            'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            'Resultados': len(table_data),
                            'COD_Encontrado': cod_excel,
                            'Button_Status': 'Already processed'
                        })
                    elif button_status == "needs_upload":
                        self.log("info", f"NDO {ndo}: Boton de carga azul encontrado - Verificando estado de carga.")
                        upload_status, upload_error_screenshot = self.check_upload_button_status(ndo, matching_row)
                        
                        if upload_status == "needs_file_upload":
                            self.log("info", f"NDO {ndo}: Requiere subir archivo - Procesando...")
                            
                            informe_url = row.get('Informe', '')
                            if not informe_url:
                                self.log("error", f"NDO {ndo}: No se encontró URL de informe en el Excel")
                                failed_rows.append({
                                    'NDO': ndo,
                                    'Status': f'URL de informe no encontrada - COD {cod_excel}',
                                    'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                    'COD_Buscado': cod_excel,
                                    'Resultados_Tabla': len(table_data),
                                    'Button_Status': button_status,
                                    'Upload_Status': 'No informe URL'
                                })
                                continue
                                                    
                            upload_result = self.handle_file_upload_modal(ndo, matching_row, informe_url)
                            
                            self.log("info", f"NDO {ndo}: Upload result: {upload_result}")
                            self.log("info", f"NDO {ndo}: Upload result type: {type(upload_result)}")
                            
                            if upload_result is True:
                                self.log("info", f"NDO {ndo}: Archivo subido exitosamente - Verificando para transmitir")
                                transmit_result, transmit_error_screenshot = self.check_and_transmit(ndo, matching_row)
                                
                                if transmit_result:
                                    processed_rows.append({
                                        'NDO': ndo,
                                        'Status': f'Archivo subido y transmitido exitosamente - COD {cod_excel}',
                                        'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                        'Resultados': len(table_data),
                                        'COD_Encontrado': cod_excel,
                                        'Button_Status': 'File uploaded and transmitted',
                                        'Upload_Status': 'Completed'
                                    })
                                else:
                                    failed_row_data = {
                                        'NDO': ndo,
                                        'Status': f'Archivo subido pero no se pudo transmitir - COD {cod_excel}',
                                        'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                        'COD_Buscado': cod_excel,
                                        'Resultados_Tabla': len(table_data),
                                        'Button_Status': button_status,
                                        'Upload_Status': 'Upload successful, transmit failed'
                                    }
                                    if transmit_error_screenshot:
                                        failed_row_data['Screenshot'] = transmit_error_screenshot
                                    failed_rows.append(failed_row_data)
                                
                                processed_rows.append({
                                    'NDO': ndo,
                                    'Status': f'Archivo subido exitosamente - COD {cod_excel}',
                                    'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                    'Resultados': len(table_data),
                                    'COD_Encontrado': cod_excel,
                                    'Button_Status': 'File uploaded successfully',
                                    'Upload_Status': 'Uploaded'
                                })
                            else:
                                self.log("error", f"NDO {ndo}: Upload result no es True: {upload_result}")
                                error_screenshot = upload_result[1] if isinstance(upload_result, tuple) else None
                                failed_row_data = {
                                    'NDO': ndo,
                                    'Status': f'Error subiendo archivo - COD {cod_excel}',
                                    'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                    'COD_Buscado': cod_excel,
                                    'Resultados_Tabla': len(table_data),
                                    'Button_Status': button_status,
                                    'Upload_Status': 'Upload failed'
                                }
                                if error_screenshot:
                                    failed_row_data['Screenshot'] = error_screenshot
                                failed_rows.append(failed_row_data)
                        elif upload_status == "file_already_uploaded":
                            self.log("info", f"NDO {ndo}: Archivo ya subido - Trasmitiendo.")
                            transmit_result, transmit_error_screenshot = self.check_and_transmit(ndo, matching_row)
                            if transmit_result:
                                processed_rows.append({
                                    'NDO': ndo,
                                    'Status': f'Archivo ya subido y transmitido - COD {cod_excel}',
                                    'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                    'Resultados': len(table_data),
                                    'COD_Encontrado': cod_excel,
                                    'Button_Status': 'File already uploaded and transmitted',
                                    'Upload_Status': 'Already uploaded and completed'
                                })
                            else:
                                failed_row_data = {
                                    'NDO': ndo,
                                    'Status': f'Archivo ya subido pero no se pudo transmitir - COD {cod_excel}',
                                    'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                    'COD_Buscado': cod_excel,
                                    'Resultados_Tabla': len(table_data),
                                    'Button_Status': button_status,
                                    'Upload_Status': 'Already uploaded, transmit failed'
                                }
                                if transmit_error_screenshot:
                                    failed_row_data['Screenshot'] = transmit_error_screenshot
                                failed_rows.append(failed_row_data)
                        else:
                            self.log("warning", f"NDO {ndo}: Estado del botón de carga no pudo ser determinado.")
                            failed_row_data = {
                                'NDO': ndo,
                                'Status': f'Error determinando estado del botón de carga - COD {cod_excel}',
                                'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                'COD_Buscado': cod_excel,
                                'Resultados_Tabla': len(table_data),
                                'Button_Status': button_status,
                                'Upload_Status': upload_status
                            }
                            if upload_error_screenshot:
                                failed_row_data['Screenshot'] = upload_error_screenshot
                            failed_rows.append(failed_row_data)
                    else:
                        self.log("warning", f"NDO {ndo}: Estado del boton no pudo ser determinado.")
                        failed_row_data = {
                            'NDO': ndo,
                            'Status': f'Error determinando el estado del boton - COD {cod_excel}',
                            'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            'COD_Buscado': cod_excel,
                            'Resultados_Tabla': len(table_data),
                            'Button_Status': button_status
                        }
                        if error_screenshot:
                            failed_row_data['Screenshot'] = error_screenshot
                        failed_rows.append(failed_row_data)
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
        
    def check_button_status(self, ndo, matching_row_data):
        try:
            self.log("info", f"NDO {ndo}: Verificando estado del boton")
            
            data_id = matching_row_data.get('data_id')
            row_selector = f"tbody#ordenes tr[data-id='{data_id}']"
            
            button_selector = f"{row_selector} .boton-historial.fas.fa-check"

            self.new_page.wait_for_selector(button_selector, state="visible", timeout=5000)
            
            button = self.new_page.query_selector(button_selector)
            
            if not button:
                self.log("error", f"NDO {ndo}: No se encontro el boton de validacion.")
                return "unknown", None
            
            classes = button.get_attribute("class")
            
            if "btn-success" in classes:
                self.log("info", f"NDO {ndo}: Boton verde - Caso ya procesado.")
                return "processed", None
            elif "btn-primary" in classes:
                self.log("info", f"NDO {ndo}: Boton azul - Requiere carga de archivo.")
                return "needs_upload", None
            else:
                bg_color = self.new_page.evaluate("(elements) => window.getComputedStyle(element).backgroundColor", button)
                self.log("info", f"NDO {ndo}: Color de fondo del boton: {bg_color}")
                return "unknown", None
                
        except Exception as e:
            screenshot_path = self.take_screenshot(f"button_check_error_ndo_{ndo}")
            self.log("error", f"NDO {ndo}: Error verificando estado del boton: {str(e)}", screenshot_path)
            return "error", screenshot_path
                
    def check_upload_button_status(self, ndo, matching_row_data):
        try:
            self.log("info", f"NDO {ndo}: Verificando estado del botón de carga")
            
            data_id = matching_row_data.get('data_id')
            row_selector = f"tbody#ordenes tr[data-id='{data_id}']"
            
            upload_button_selector = f"{row_selector} .boton-historial.fas.fa-upload"

            self.new_page.wait_for_selector(upload_button_selector, state="visible", timeout=5000)
            
            upload_button = self.new_page.query_selector(upload_button_selector)
            
            if not upload_button:
                self.log("error", f"NDO {ndo}: No se encontró el botón de carga.")
                return "unknown", None
            
            classes = upload_button.get_attribute("class")
            
            if "btn-success" in classes:
                self.log("info", f"NDO {ndo}: Botón de carga verde - Requiere subir archivo.")
                return "needs_file_upload", None
            elif "btn-primary" in classes:
                self.log("info", f"NDO {ndo}: Botón de carga azul - Archivo ya subido.")
                return "file_already_uploaded", None
            else:
                bg_color = self.new_page.evaluate("(element) => window.getComputedStyle(element).backgroundColor", upload_button)
                self.log("info", f"NDO {ndo}: Color de fondo del botón de carga: {bg_color}")
                return "unknown", None
                
        except Exception as e:
            screenshot_path = self.take_screenshot(f"upload_button_check_error_ndo_{ndo}")
            self.log("error", f"NDO {ndo}: Error verificando estado del botón de carga: {str(e)}", screenshot_path)
            return "error", screenshot_path
            
    def handle_file_upload_modal(self, ndo, matching_row_data, informe_url):
        try:
            downloaded_file_path = self.download_file(ndo, informe_url)
            if not downloaded_file_path:
                self.log("error", f"NDO {ndo}: No se pudo descargar el archivo")
                return False, None
            
            self.log("info", f"NDO {ndo}: Haciendo clic en botón de carga")
            
            data_id = matching_row_data.get('data_id')
            row_selector = f"tbody#ordenes tr[data-id='{data_id}']"
            upload_button_selector = f"{row_selector} .boton-historial.fas.fa-upload"
            
            self.new_page.click(upload_button_selector)
            self.log("info", f"NDO {ndo}: Botón de carga presionado")
            
            self.log("info", f"NDO {ndo}: Esperando que aparezca el modal de carga")
            self.new_page.wait_for_selector("select[name='m_t_doc']", state="visible", timeout=10000)
            time.sleep(2)
            
            self.log("info", f"NDO {ndo}: Modal de carga detectado, obteniendo opciones del dropdown")
            
            options = self.new_page.query_selector_all("select[name='m_t_doc'] option")
            
            if not options:
                self.log("error", f"NDO {ndo}: No se encontraron opciones en el dropdown")
                screenshot_path = self.take_screenshot(f"no_options_ndo_{ndo}")
                return False, screenshot_path
            
            self.log("info", f"NDO {ndo}: Se encontraron {len(options)} opciones")
            informe_option_value = None
            
            for option in options:
                option_text = option.inner_text()
                option_value = option.get_attribute("value")
                self.log("info", f"NDO {ndo}: Opción encontrada - Texto: '{option_text}', Valor: '{option_value}'")
                
                if "Informe/Resultados" in option_text:
                    informe_option_value = option_value
                    self.log("info", f"NDO {ndo}: Opción 'Informe/Resultados' encontrada con valor: '{option_value}'")
                    break
            
            if not informe_option_value:
                self.log("error", f"NDO {ndo}: No se encontró opción 'Informe/Resultados' en el dropdown")
                screenshot_path = self.take_screenshot(f"no_informe_option_ndo_{ndo}")
                return False, screenshot_path
            
            self.log("info", f"NDO {ndo}: Seleccionando opción con valor: '{informe_option_value}'")
            self.new_page.select_option("select[name='m_t_doc']", value=informe_option_value)
            self.log("info", f"NDO {ndo}: Opción 'Informe/Resultados' seleccionada")
            
            self.log("info", f"NDO {ndo}: Esperando que aparezca el campo de archivo")
            self.new_page.wait_for_selector("input[name='m_doc']", state="visible", timeout=10000)
            time.sleep(2)
            
            self.log("info", f"NDO {ndo}: Preparando carga del archivo descargado: {downloaded_file_path}")
            
            with self.new_page.expect_file_chooser() as fc_info:
                self.log("info", f"NDO {ndo}: Haciendo clic en campo de archivo")
                self.new_page.click("input[name='m_doc']")
            
            file_chooser = fc_info.value
            self.log("info", f"NDO {ndo}: Seleccionando archivo en el diálogo")
            file_chooser.set_files(downloaded_file_path)
            self.log("info", f"NDO {ndo}: Archivo seleccionado exitosamente")
            
            self.log("info", f"NDO {ndo}: Esperando confirmación de carga de archivo")
            try:
                self.new_page.wait_for_selector("tbody#documentosGrid tr", state="visible", timeout=15000)
                
                confirmation_rows = self.new_page.query_selector_all("tbody#documentosGrid tr")
                if confirmation_rows and len(confirmation_rows) > 0:
                    first_row = confirmation_rows[0]
                    row_content = first_row.inner_text()
                    self.log("info", f"NDO {ndo}: Confirmación de carga encontrada: {row_content}")
                    
                    if "Informe/Resultados" in row_content:
                        self.log("info", f"NDO {ndo}: Archivo subido y confirmado exitosamente")
                    else:
                        self.log("warning", f"NDO {ndo}: Confirmación no contiene 'Informe/Resultados'")
                else:
                    self.log("error", f"NDO {ndo}: No se encontraron filas de confirmación")
                    screenshot_path = self.take_screenshot(f"no_confirmation_ndo_{ndo}")
                    return False, screenshot_path
                    
            except Exception as confirmation_error:
                self.log("error", f"NDO {ndo}: Error esperando confirmación de carga: {str(confirmation_error)}")
                screenshot_path = self.take_screenshot(f"upload_confirmation_error_ndo_{ndo}")
                return False, screenshot_path
            
            self.log("info", f"NDO {ndo}: Cerrando modal")
            try:
                close_buttons = self.new_page.query_selector_all("button.btn-danger[data-dismiss='modal']")
                
                close_button_found = False
                for button in close_buttons:
                    button_text = button.inner_text().strip()
                    if "Cerrar" in button_text:
                        button.click()
                        self.log("info", f"NDO {ndo}: Modal cerrado exitosamente con botón 'Cerrar'")
                        close_button_found = True
                        break
                
                if not close_button_found:
                    self.new_page.press("body", "Escape")
                    self.log("info", f"NDO {ndo}: Modal cerrado con Escape (botón Cerrar no encontrado)")
                    
            except Exception as close_error:
                self.log("warning", f"NDO {ndo}: Error cerrando modal: {str(close_error)}")
                try:
                    self.new_page.press("body", "Escape")
                    self.log("info", f"NDO {ndo}: Modal cerrado con Escape")
                except:
                    self.log("warning", f"NDO {ndo}: No se pudo cerrar el modal")
        except Exception as e:
            screenshot_path = self.take_screenshot(f"upload_modal_error_ndo_{ndo}")
            self.log("error", f"NDO {ndo}: Error procesando modal de carga: {str(e)}", screenshot_path)
            return False, screenshot_path
        
        return True
        
    def download_file(self, ndo, informe_url):
        try:
            if not os.path.exists(DOWNLOADS_DIR):
                os.makedirs(DOWNLOADS_DIR)
                
            self.log("info", f"NDO {ndo}: Descargando archivo desde: {informe_url}")
            
            response = requests.get(informe_url, timeout = 30)
            response.raise_for_status()
            
            filename = f"informe_{ndo}.pdf"
            filepath = os.path.join(DOWNLOADS_DIR, filename)
            
            with open(filepath, 'wb') as file:
                file.write(response.content)
                
            self.log("info", f"NDO {ndo}: Archivo descargado exitosamente: {filepath}")
            return filepath
        
        except Exception as e:
            self.log("error", f"NDO {ndo}: Error descargando el archivo: {str(e)}")
            return None
        
    def check_and_transmit(self, ndo, matching_row_data):
        try:
            self.log("info", f"NDO {ndo}: Verificando estado de ambos botones antes de transmitir")
            
            data_id = matching_row_data.get('data_id')
            row_selector = f"tbody#ordenes tr[data-id='{data_id}']"
            
            time.sleep(3)
            
            check_button_selector = f"{row_selector} .boton-historial.fas.fa-check"
            check_button = self.new_page.query_selector(check_button_selector)
            
            if not check_button:
                self.log("error", f"NDO {ndo}: No se encontró el botón de validación")
                return False, None
            
            check_classes = check_button.get_attribute("class")
            check_is_blue = "btn-primary" in check_classes
            
            upload_button_selector = f"{row_selector} .boton-historial.fas.fa-upload"
            upload_button = self.new_page.query_selector(upload_button_selector)
            
            if not upload_button:
                self.log("error", f"NDO {ndo}: No se encontró el botón de carga")
                return False, None
            
            upload_classes = upload_button.get_attribute("class")
            upload_is_blue = "btn-primary" in upload_classes
            
            self.log("info", f"NDO {ndo}: Estado botones - Validación: {'azul' if check_is_blue else 'otro'}, Carga: {'azul' if upload_is_blue else 'otro'}")
            
            if check_is_blue and upload_is_blue:
                self.log("info", f"NDO {ndo}: Ambos botones están azules - Procediendo a transmitir")
                
                transmit_button_selector = f"{row_selector} .boton-historial.fas.fa-arrow-right.transmitir"
                
                self.new_page.wait_for_selector(transmit_button_selector, state="visible", timeout=5000)
                self.new_page.click(transmit_button_selector)
                
                self.log("info", f"NDO {ndo}: Botón transmitir presionado exitosamente")
                
                self.log("info", f"NDO {ndo}: Esperando botón 'Confirmar'")

                confirm_button_selector = "button#transmitir-prestacion-validada.btn.btn-success[type='button']"

                self.new_page.wait_for_selector("button#transmitir-prestacion-validada", state="visible", timeout=10000)

                confirm_buttons = self.new_page.query_selector_all("button#transmitir-prestacion-validada.btn.btn-success")

                confirm_button = None
                for button in confirm_buttons:
                    button_text = button.inner_text().strip()
                    if "Confirmar" in button_text:
                        confirm_button = button
                        self.log("info", f"NDO {ndo}: Botón 'Confirmar' encontrado con texto: '{button_text}'")
                        break

                if not confirm_button:
                    self.log("error", f"NDO {ndo}: No se encontró el botón 'Confirmar' específico")
                    return False, None

                self.log("info", f"NDO {ndo}: Haciendo clic en botón 'Confirmar' y manejando diálogo")

                with self.new_page.expect_dialog() as dialog_info:
                    confirm_button.click()
                
                dialog = dialog_info.value
                dialog_message = dialog.message
                self.log("info", f"NDO {ndo}: Diálogo del navegador recibido: '{dialog_message}'")
                
                if "INFORMACION TRANSMITIDA" in dialog_message:
                    dialog.accept()
                    self.log("info", f"NDO {ndo}: Diálogo de confirmación aceptado - Transmisión completada")
                else:
                    self.log("warning", f"NDO {ndo}: Mensaje de diálogo inesperado: {dialog_message}")
                    dialog.accept()
                
                time.sleep(2)
                
                return True, None
            else:
                self.log("warning", f"NDO {ndo}: No se puede transmitir - Botones no están en estado correcto")
                return False, None
                
        except Exception as e:
            screenshot_path = self.take_screenshot(f"transmit_error_ndo_{ndo}")
            self.log("error", f"NDO {ndo}: Error verificando/transmitiendo: {str(e)}", screenshot_path)
            return False, screenshot_path