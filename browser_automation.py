from playwright.sync_api import sync_playwright
from config import *
import time
import os 
from datetime import datetime
import pandas as pd
import requests
import  gspread
from google.oauth2.service_account import Credentials

class AutomationError(Exception):
    pass

class BrowserAutomation:
    def __init__(self, logger=None, settings_manager = None):
        self.browser = None
        self.page = None
        self.new_page = None
        self.logger = logger
        self.settings_manager = settings_manager
        self.excel_data = []
        self.processed_rows = []
        self.failed_rows = []
        self.already_processed_cases = []
        self.original_indices = []
        self.stop_requested = False
        
    def request_stop(self):
        """Request graceful stop after current case"""
        self.stop_requested = True
        self.log("info", "Solicitud de parada recibida - Terminando con caso actual...")

    def log(self, level, message, screenshot_path=None):
        if self.logger:
            getattr(self.logger, level)(message, screenshot_path)

    def take_screenshot(self, description="error"):
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{description}_{timestamp}.png"
            
            screenshot_dir = self.settings_manager.get_screenshot_dir() if self.settings_manager else SCREENSHOT_DIR
            
            if not os.path.exists(screenshot_dir):
                os.makedirs(screenshot_dir)
            
            filepath = os.path.join(screenshot_dir, filename)
            
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
        
        try:
            import sys
            if hasattr(sys, '_MEIPASS'):
                browsers_path = os.path.join(sys._MEIPASS, 'playwright', 'driver', 'package', '.local-browsers')
                if os.path.exists(browsers_path):
                    os.environ['PLAYWRIGHT_BROWSERS_PATH'] = browsers_path
                    self.log("info", f"Using bundled browsers from: {browsers_path}")
            
            self.browser = self.playwright.chromium.launch(headless=HEADLESS)
            
        except Exception as e:
            if "Executable doesn't exist" in str(e):
                self.log("info", "Navegadores no encontrados. Instalando automáticamente...")
                try:
                    import subprocess
                    import sys
                    
                    result = subprocess.run(
                        [sys.executable, "-m", "playwright", "install", "chromium"],
                        capture_output=True,
                        text=True,
                        timeout=300
                    )
                    
                    if result.returncode != 0:
                        self.log("error", f"Error instalando navegadores: {result.stderr}")
                        raise AutomationError(f"Failed to install browsers: {result.stderr}")
                    
                    self.log("info", "Navegadores instalados exitosamente")
                    self.browser = self.playwright.chromium.launch(headless=HEADLESS)
                    
                except subprocess.TimeoutExpired:
                    self.log("error", "Timeout instalando navegadores")
                    raise AutomationError("Browser installation timed out")
                except Exception as install_error:
                    self.log("error", f"Error instalando navegadores: {str(install_error)}")
                    raise AutomationError(f"Failed to install browsers: {str(install_error)}")
            else:
                raise e

        timeout = self.settings_manager.get_browser_timeout() if self.settings_manager else BROWSER_TIMEOUT
        self.page = self.browser.new_page()
        self.page.set_default_timeout(timeout)

        self.log("info", f"Navegador iniciado correctamente (timeout: {timeout}ms)")

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
        self.page.wait_for_selector(LOGIN_USERNAME_FIELD, state="visible")
        time.sleep(1)

        self.log("info", "Completando campo de usuario")
        self.page.fill(LOGIN_USERNAME_FIELD, username)

        self.log("info", "Completando campo de contraseña")
        self.page.fill(LOGIN_PASSWORD_FIELD, password)

        self.log("info", "Haciendo clic en botón Ingresar")
        self.page.click(LOGIN_SUBMIT_BUTTON)

        self.log("info", "Formulario de login completado, esperando...")
        time.sleep(3)
        
        self.check_for_errors(self.page)
        
        try:
            self.page.wait_for_selector(OME_BUTTON, state="visible", timeout=5000)
            self.log("info", "Login exitoso: Botón OME encontrado")
        except:
            screenshot_path = self.take_screenshot("login_timeout")
            self.log("error", "Login falló: No se encontró el botón OME", screenshot_path)
            raise AutomationError("Login failed: OME button not found")

    def click_ome_button(self):
        self.log("info", "Esperando que aparezca el botón OME")
        self.page.wait_for_selector(OME_BUTTON, state="visible")
        time.sleep(1)

        self.log("info", "Haciendo clic en botón OME")
        with self.page.context.expect_page() as new_page_info:
            self.page.click(OME_BUTTON)

        self.new_page = new_page_info.value
        
        timeout = self.settings_manager.get_browser_timeout() if self.settings_manager else BROWSER_TIMEOUT
        self.new_page.set_default_timeout(timeout)

        self.log("info", "Nueva página OME abierta correctamente")
        self.log("info", f"URL de nueva página: {self.new_page.url}")
        time.sleep(2)

    def click_panel_prestaciones(self):
        self.log("info", "Esperando que aparezca el botón Panel de prestaciones")
        try:
            self.new_page.wait_for_selector(PANEL_PRESTACIONES_LINK, state="visible")
            time.sleep(1)

            self.log("info", "Haciendo clic en Panel de prestaciones")
            self.new_page.click(PANEL_PRESTACIONES_LINK)
            
            delay = random_delay_medium()
            self.log("info", f"Esperando {delay:.1f} segundos después de cargar panel de prestaciones")
        except:
            screenshot_path = self.take_screenshot("panel_error")
            self.log("error", "Error navegando a Panel de prestaciones", screenshot_path)
            raise AutomationError("Failed to navigate to Panel de prestaciones")
            
    def read_excel_data(self):
        try:
            self.log("info", "Conectando a Google Sheets")
            
            scope = ['https://spreadsheets.google.com/feeds',
                    'https://www.googleapis.com/auth/drive']
            
            service_account_file = self.settings_manager.get_service_account_file() if self.settings_manager else SERVICE_ACCOUNT_FILE
            sheets_id = self.settings_manager.get_google_sheets_id() if self.settings_manager else GOOGLE_SHEETS_ID
            worksheet_name = self.settings_manager.get_worksheet_name() if self.settings_manager else WORKSHEET_NAME
            
            creds = Credentials.from_service_account_file(service_account_file, scopes=scope)
            client = gspread.authorize(creds)
            
            sheet = client.open_by_key(sheets_id).worksheet(worksheet_name)
            
            data = sheet.get_all_records()
            df = pd.DataFrame(data)
            
            all_values = sheet.get_all_values()
            header_row = all_values[0] if all_values else []
            
            if 'Procesado' not in header_row:
                self.log("info", "Agregando columna 'Procesado' a Google Sheets")
                procesado_col = len(header_row) + 1
                sheet.update_cell(1, procesado_col, 'Procesado')
                
                data = sheet.get_all_records()
                df = pd.DataFrame(data)
                self.log("info", "Columna 'Procesado' agregada exitosamente (solo encabezado)")
            else:
                self.log("info", "La columna 'Procesado' ya existe en Google Sheets")

            df['_original_sheet_row'] = df.index + 2
            
            if self.settings_manager:
                date_range_start = self.settings_manager.get_date_range_start()
                date_range_end = self.settings_manager.get_date_range_end()
            else:
                date_range_start = DATE_RANGE_START if 'DATE_RANGE_START' in globals() else None
                date_range_end = DATE_RANGE_END if 'DATE_RANGE_END' in globals() else None
            
            if date_range_start is not None or date_range_end is not None:
                self.log("info", f"Aplicando filtro de fecha desde {date_range_start} hasta {date_range_end}")
                
                df['FechaTurno'] = pd.to_datetime(df['FechaTurno'], errors='coerce')
                original_count = len(df)
                
                if date_range_start is not None:
                    df = df[df['FechaTurno'] >= date_range_start]

                if date_range_end is not None:
                    if date_range_end.hour == 0 and date_range_end.minute == 0 and date_range_end.second == 0:
                        end_date_inclusive = pd.Timestamp(date_range_end).replace(hour=23, minute=59, second=59)
                    else:
                        end_date_inclusive = pd.Timestamp(date_range_end)
                    
                    df = df[df['FechaTurno'] <= end_date_inclusive]
                
                df = df.dropna(subset=['FechaTurno'])
                filtered_count = len(df)
                self.log("info", f"Filtro aplicado: {original_count} registros originales -> {filtered_count} registros filtrados")
            else:
                self.log("info", "Sin filtro de fecha - procesando todos los registros")
            
            if 'Procesado' in df.columns:
                df['Procesado'] = df['Procesado'].fillna('No')
                df.loc[df['Procesado'].isin(['', None, 0]), 'Procesado'] = 'No'
            else:
                df['Procesado'] = 'No'
            
            self.google_sheet = sheet
            self.google_df = df
            
            already_processed_df = df[df['Procesado'] == 'Si']
            self.already_processed_cases = []
            
            for _, row in already_processed_df.iterrows():
                ndo = row.get('NDO', 'N/A')
                cod = row.get('CODIGO_PAMI', 'N/A')
                self.already_processed_cases.append({
                    'NDO': ndo,
                    'COD': cod,
                    'Status': 'Ya procesado anteriormente',
                    'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'APE': row.get('APE', ''),
                    'NOM': row.get('NOM', '')
                })
            
            unprocessed_df = df[df['Procesado'] == 'No']
            self.excel_data = unprocessed_df.to_dict('records')
            
            total_cases = len(df)
            processed_cases = len(already_processed_df)
            unprocessed_cases = len(self.excel_data)
            
            self.log("info", f"Total de casos (filtrados): {total_cases}, Ya procesados: {processed_cases}, Sin procesar: {unprocessed_cases}")
            
            return self.excel_data
            
        except Exception as e:
            self.log("error", f"Error leyendo Google Sheets: {str(e)}")
            raise AutomationError(f"Failed to read Google Sheets: {str(e)}")
        
    def process_excel_data(self, excel_data):
        self.log("info", "Procesando datos de Excel")
        processed_rows = []
        failed_rows = []

        for index, row in enumerate(excel_data):
            if self.stop_requested:
                self.log("info", f"Parada solicitada - Procesamiento detenido en caso {index + 1}")
                break
            
            if index > 0:
                delay = random_delay_long()
                self.log("info", f"Esperando {delay:.1f} segundos antes del siguiente caso")
                
                if self.stop_requested:
                    self.log("info", "Parada solicitada durante espera - Deteniendo procesamiento")
                    break
                
            ndo = row.get('NDO', f'Fila_{index + 1}')
            cod_excel = row.get('CODIGO_PAMI', '')
            self.log("info", f"Iniciando procesamiento de NDO: {ndo} (Fila {index + 1})")

            try:
                # seleccionar Nro. Documento del dropdown
                self.log("info", f"NDO {ndo}: Seleccionando 'Nro. Documento' en dropdown 'Afiliado Por'")
                self.new_page.wait_for_selector(AFILIADO_DROPDOWN, state="visible")
                self.new_page.select_option(AFILIADO_DROPDOWN, value=AFILIADO_DROPDOWN_VALUE)
                self.log("info", f"NDO {ndo}: Selección completada")
                
                delay = random_delay_micro()
                self.log("info", f"NDO {ndo}: Esperando {delay:.1f} segundos después de selección")

                # ingresar primer dia del mes anterior en el campo 'Fecha turno desde'
                date_value = get_first_day_of_month()
                self.log("info", f"NDO {ndo}: Ingresando fecha {date_value}")
                self.new_page.wait_for_selector(FECHA_TURNO_FIELD, state="visible")
                self.new_page.click(FECHA_TURNO_FIELD)  # Foco
                self.new_page.fill(FECHA_TURNO_FIELD, "")  # Limpiar
                self.new_page.type(FECHA_TURNO_FIELD, date_value, delay=100)
                self.new_page.press(FECHA_TURNO_FIELD, "Enter")
                self.log("info", f"NDO {ndo}: Fecha tipeada y confirmada correctamente")

                delay = random_delay_short()
                self.log("info", f"NDO {ndo}: Esperando {delay:.1f} segundos entre fecha y NDO")

                self.log("info", f"NDO {ndo}: Ingresando NDO en campo de afiliado")
                self.new_page.wait_for_selector(AFILIADO_NUMBER_FIELD, state="visible")
                self.new_page.fill(AFILIADO_NUMBER_FIELD, str(ndo))
                self.log("info", f"NDO {ndo}: NDO ingresado correctamente")
                
                delay = random_delay_micro()
                self.log("info", f"NDO {ndo}: Esperando {delay:.1f} segundos antes de buscar")

                # apretar en el botón Buscar
                self.log("info", f"NDO {ndo}: Haciendo clic en botón Buscar")
                self.new_page.wait_for_selector(SEARCH_BUTTON, state="visible")
                self.new_page.click(SEARCH_BUTTON)
                self.log("info", f"NDO {ndo}: Búsqueda iniciada correctamente")
                
                delay = random_delay_short()
                self.log("info", f"NDO {ndo}: Esperando {delay:.1f} segundos para que carguen los resultados")
                
                # extraer datos de la tabla
                table_data = self.extract_table_data(ndo)

                if not table_data:
                    self.log("warning", f"NDO {ndo}: No se encontraron datos en la tabla.")
                    failed_rows.append({
                        'NDO': ndo,
                        'Status': 'No se encontraron datos en la tabla.',
                        'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'Resultados': 0
                    })
                    self.update_case_as_failed(index)
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
                    
                    if button_status == "processed" or button_status == "already_completed":
                        if button_status == "processed":
                            self.log("info", f"NDO {ndo}: Caso ya procesado o validacion manual pendiente - Marcando como completado.")
                            status_message = f'Ya estaba procesado o falta validacion manual - COD {cod_excel}'
                            button_status_desc = 'Already processed or manual validation missing'
                            
                            failed_rows.append({
                                'NDO': ndo,
                                'Status': status_message,
                                'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                'Resultados': len(table_data),
                                'COD_Encontrado': cod_excel,
                                'Button_Status': button_status_desc
                            })
                            self.update_case_as_failed(index)
                        else:
                            self.log("info", f"NDO {ndo}: Caso ya completado y aceptado - Marcando como completado.")
                            status_message = f'Ya estaba completado y aceptado - COD {cod_excel}'
                            button_status_desc = 'Already completed and accepted'
                            
                            processed_rows.append({
                                'NDO': ndo,
                                'Status': status_message,
                                'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                'Resultados': len(table_data),
                                'COD_Encontrado': cod_excel,
                                'Button_Status': button_status_desc
                            })
                            self.update_case_as_processed(index)
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
                                self.update_case_as_failed(index)
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
                                    
                                    self.update_case_as_processed(index)
                                else:
                                    failed_row_data = {
                                        'NDO': ndo,
                                        'Status': f'Archivo subido por el bot pero no se pudo transmitir - COD {cod_excel}',
                                        'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                        'COD_Buscado': cod_excel,
                                        'Resultados_Tabla': len(table_data),
                                        'Button_Status': button_status,
                                        'Upload_Status': 'Upload successful, transmit failed'
                                    }
                                    if transmit_error_screenshot:
                                        failed_row_data['Screenshot'] = transmit_error_screenshot
                                    failed_rows.append(failed_row_data)
                                    self.update_case_as_failed(index)
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
                                self.update_case_as_failed(index)
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
                                self.update_case_as_processed(index)
                            else:
                                failed_row_data = {
                                    'NDO': ndo,
                                    'Status': f'Archivo ya subido anteriormente pero no se pudo transmitir - COD {cod_excel}',
                                    'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                    'COD_Buscado': cod_excel,
                                    'Resultados_Tabla': len(table_data),
                                    'Button_Status': button_status,
                                    'Upload_Status': 'Already uploaded, transmit failed'
                                }
                                if transmit_error_screenshot:
                                    failed_row_data['Screenshot'] = transmit_error_screenshot
                                failed_rows.append(failed_row_data)
                                self.update_case_as_failed(index)
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
                            self.update_case_as_failed(index)
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
                        self.update_case_as_failed(index)
                        if error_screenshot:
                            failed_row_data['Screenshot'] = error_screenshot
                        failed_rows.append(failed_row_data)
                        self.update_case_as_failed(index)
                else:
                    self.log("warning", f"NDO {ndo}: COD {cod_excel} no encontrado en ninguna fila de la tabla")
                    failed_rows.append({
                        'NDO': ndo,
                        'Status': f'COD {cod_excel} no encontrado en la tabla',
                        'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'COD_Buscado': cod_excel,
                        'Resultados_Tabla': len(table_data)
                    })
                    self.update_case_as_failed(index)
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
                
                self.update_case_as_failed(index)

        self.processed_rows = processed_rows
        self.failed_rows = failed_rows
        
        total_processed = len(processed_rows)
        total_failed = len(failed_rows)

        if self.stop_requested:
            self.log("info", f"Procesamiento detenido por usuario. Casos completados: {total_processed}, Fallidos: {total_failed}")
        else:
            self.log("info", f"Procesamiento completado. Exitosos: {total_processed}, Fallidos: {total_failed}")

    def extract_table_data(self, ndo):
        try:
            self.log("info", f"NDO {ndo}: Esperando que aparezca la tabla de resultados.")
            self.new_page.wait_for_selector(RESULTS_TABLE, state="visible", timeout=10000)
            
            delay = random_delay_micro()
            self.log("info", f"NDO {ndo}: Esperando {delay:.1f} segundos para estabilización de tabla")
        
            rows = self.new_page.query_selector_all(TABLE_ROWS)

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
            
            delay = random_delay_micro()
            self.log("info", f"NDO {ndo}: Esperando {delay:.1f} segundos antes de verificar botón")
            
            data_id = matching_row_data.get('data_id')
            row_selector = f"{TABLE_ROWS}[data-id='{data_id}']"
            
            button_selector = f"{row_selector} {VALIDATION_BUTTON}"

            try:
                self.new_page.wait_for_selector(button_selector, state="visible", timeout=5000)
                button = self.new_page.query_selector(button_selector)
                
                if not button:
                    self.log("info", f"NDO {ndo}: No se encontró el botón de validación - Caso ya procesado y aceptado")
                    return "already_completed", None
                
                classes = button.get_attribute("class")
                
                if BTN_SUCCESS_CLASS in classes:
                    self.log("info", f"NDO {ndo}: Botón verde - Validación manual no realizada")
                    return "processed", None
                elif BTN_PRIMARY_CLASS in classes:
                    self.log("info", f"NDO {ndo}: Botón azul - Requiere carga de archivo")
                    return "needs_upload", None
                else:
                    self.log("info", f"NDO {ndo}: Estado del botón no reconocido - Asumiendo ya procesado")
                    return "already_completed", None
                    
            except Exception as selector_error:
                self.log("info", f"NDO {ndo}: No se pudo encontrar botón de validación - Caso ya procesado y aceptado")
                return "already_completed", None
                
        except Exception as e:
            screenshot_path = self.take_screenshot(f"button_check_error_ndo_{ndo}")
            self.log("error", f"NDO {ndo}: Error verificando estado del botón: {str(e)}", screenshot_path)
            return "error", screenshot_path
                
    def check_upload_button_status(self, ndo, matching_row_data):
        try:
            self.log("info", f"NDO {ndo}: Verificando estado del botón de carga")
            
            data_id = matching_row_data.get('data_id')
            row_selector = f"{TABLE_ROWS}[data-id='{data_id}']"
            
            upload_button_selector = f"{row_selector} {UPLOAD_BUTTON}"

            self.new_page.wait_for_selector(upload_button_selector, state="visible", timeout=5000)
            
            upload_button = self.new_page.query_selector(upload_button_selector)
            
            if not upload_button:
                self.log("error", f"NDO {ndo}: No se encontró el botón de carga.")
                return "unknown", None
            
            classes = upload_button.get_attribute("class")
            
            if BTN_SUCCESS_CLASS in classes:
                self.log("info", f"NDO {ndo}: Botón de carga verde - Requiere subir archivo.")
                return "needs_file_upload", None
            elif BTN_PRIMARY_CLASS in classes:
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
            
            delay = random_delay_micro()
            self.log("info", f"NDO {ndo}: Esperando {delay:.1f} segundos antes de abrir modal de carga")
        
            self.log("info", f"NDO {ndo}: Haciendo clic en botón de carga")
            
            data_id = matching_row_data.get('data_id')
            row_selector = f"{TABLE_ROWS}[data-id='{data_id}']"
            upload_button_selector = f"{row_selector} {UPLOAD_BUTTON}"
            
            self.new_page.click(upload_button_selector)
            self.log("info", f"NDO {ndo}: Botón de carga presionado")
            
            self.log("info", f"NDO {ndo}: Esperando que aparezca el modal de carga")
            self.new_page.wait_for_selector(MODAL_DOCTYPE_DROPDOWN, state="visible", timeout=10000)
            
            delay = random_delay_short()
            self.log("info", f"NDO {ndo}: Esperando {delay:.1f} segundos para que cargue el modal")
            
            self.log("info", f"NDO {ndo}: Modal de carga detectado, obteniendo opciones del dropdown")
            
            options = self.new_page.query_selector_all("{MODAL_DOCTYPE_DROPDOWN} option")
            
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
                
                if INFORME_OPTION_TEXT in option_text:
                    informe_option_value = option_value
                    self.log("info", f"NDO {ndo}: Opción 'Informe/Resultados' encontrada con valor: '{option_value}'")
                    break
            
            if not informe_option_value:
                self.log("error", f"NDO {ndo}: No se encontró opción 'Informe/Resultados' en el dropdown")
                screenshot_path = self.take_screenshot(f"no_informe_option_ndo_{ndo}")
                return False, screenshot_path
            
            self.log("info", f"NDO {ndo}: Seleccionando opción con valor: '{informe_option_value}'")
            self.new_page.select_option(MODAL_DOCTYPE_DROPDOWN, value=informe_option_value)
            self.log("info", f"NDO {ndo}: Opción 'Informe/Resultados' seleccionada")
            
            self.log("info", f"NDO {ndo}: Esperando que aparezca el campo de archivo")
            self.new_page.wait_for_selector(MODAL_FILE_INPUT, state="visible", timeout=10000)
            time.sleep(2)
            
            self.log("info", f"NDO {ndo}: Preparando carga del archivo descargado: {downloaded_file_path}")
            
            with self.new_page.expect_file_chooser() as fc_info:
                self.log("info", f"NDO {ndo}: Haciendo clic en campo de archivo")
                self.new_page.click(MODAL_FILE_INPUT)
            
            file_chooser = fc_info.value
            self.log("info", f"NDO {ndo}: Seleccionando archivo en el diálogo")
            file_chooser.set_files(downloaded_file_path)
            self.log("info", f"NDO {ndo}: Archivo seleccionado exitosamente")
            
            delay = random_delay_file_operations()
            self.log("info", f"NDO {ndo}: Esperando {delay:.1f} segundos después de seleccionar archivo")
            
            self.log("info", f"NDO {ndo}: Esperando confirmación de carga de archivo")
            try:
                self.new_page.wait_for_selector(MODAL_CONFIRMATION_ROWS, state="visible", timeout=15000)
                
                confirmation_rows = self.new_page.query_selector_all(MODAL_CONFIRMATION_ROWS)
                if confirmation_rows and len(confirmation_rows) > 0:
                    first_row = confirmation_rows[0]
                    row_content = first_row.inner_text()
                    self.log("info", f"NDO {ndo}: Confirmación de carga encontrada: {row_content}")
                    
                    if INFORME_OPTION_TEXT in row_content:
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
                close_buttons = self.new_page.query_selector_all(MODAL_CLOSE_BUTTON)
                
                close_button_found = False
                for button in close_buttons:
                    button_text = button.inner_text().strip()
                    if CLOSE_BUTTON_TEXT in button_text:
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
            downloads_dir = self.settings_manager.get_downloads_dir() if self.settings_manager else DOWNLOADS_DIR
            
            if not os.path.exists(downloads_dir):
                os.makedirs(downloads_dir)
                
            self.log("info", f"NDO {ndo}: Descargando archivo desde: {informe_url}")
            
            response = requests.get(informe_url, timeout = 30)
            response.raise_for_status()
            
            filename = f"informe_{ndo}.pdf"
            filepath = os.path.join(downloads_dir, filename)
            
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
            
            delay = random_delay_short()
            self.log("info", f"NDO {ndo}: Esperando {delay:.1f} segundos antes de verificar transmisión")
            
            data_id = matching_row_data.get('data_id')
            row_selector = f"{TABLE_ROWS}[data-id='{data_id}']"
            
            time.sleep(3)
            
            check_button_selector = f"{row_selector} {VALIDATION_BUTTON}"
            check_button = self.new_page.query_selector(check_button_selector)
            
            if not check_button:
                self.log("error", f"NDO {ndo}: No se encontró el botón de validación")
                return False, None
            
            check_classes = check_button.get_attribute("class")
            check_is_blue = BTN_PRIMARY_CLASS in check_classes
            
            upload_button_selector = f"{row_selector} {UPLOAD_BUTTON}"
            upload_button = self.new_page.query_selector(upload_button_selector)
            
            if not upload_button:
                self.log("error", f"NDO {ndo}: No se encontró el botón de carga")
                return False, None
            
            upload_classes = upload_button.get_attribute("class")
            upload_is_blue = BTN_PRIMARY_CLASS in upload_classes
            
            self.log("info", f"NDO {ndo}: Estado botones - Validación: {'azul' if check_is_blue else 'otro'}, Carga: {'azul' if upload_is_blue else 'otro'}")
            
            if check_is_blue and upload_is_blue:
                self.log("info", f"NDO {ndo}: Ambos botones están azules - Procediendo a transmitir")
                
                delay = random_delay_short()
                self.log("info", f"NDO {ndo}: Esperando {delay:.1f} segundos antes de transmitir")
           
                transmit_button_selector = f"{row_selector} {TRANSMIT_BUTTON}"
                
                self.new_page.wait_for_selector(transmit_button_selector, state="visible", timeout=5000)
                self.new_page.click(transmit_button_selector)
                
                self.log("info", f"NDO {ndo}: Botón transmitir presionado exitosamente")
                
                self.log("info", f"NDO {ndo}: Esperando botón 'Confirmar'")

                self.new_page.wait_for_selector(TRANSMIT_CONFIRM_BUTTON, state="visible", timeout=10000)

                confirm_buttons = self.new_page.query_selector_all("{TRANSMIT_CONFIRM_BUTTON}.btn.btn-success")

                confirm_button = None
                for button in confirm_buttons:
                    button_text = button.inner_text().strip()
                    if CONFIRM_BUTTON_TEXT in button_text:
                        confirm_button = button
                        self.log("info", f"NDO {ndo}: Botón 'Confirmar' encontrado con texto: '{button_text}'")
                        break

                if not confirm_button:
                    self.log("error", f"NDO {ndo}: No se encontró el botón 'Confirmar' específico")
                    return False, None

                self.log("info", f"NDO {ndo}: Haciendo clic en botón 'Confirmar' y manejando diálogo")

                try:
                    with self.new_page.expect_event("dialog", timeout=15000) as dialog_info:
                        confirm_button.click()
                        
                    dialog = dialog_info.value
                    dialog_message = dialog.message
                    self.log("info", f"NDO {ndo}: Dialogo del navegador recibido: '{dialog_message}'")
                    
                    dialog.accept()

                    if TRANSMISSION_SUCCESS_TEXT in dialog_message:
                        self.log("info", f"NDO {ndo}: Diálogo de confirmación aceptado - Transmisión completada")
                    else:
                        self.log("warning", f"NDO {ndo}: Mensaje de diálogo inesperado: {dialog_message}")
                    return True, None
                except Exception as dialog_error:
                    self.log("error", f"NDO {ndo}: Error manejando diálogo: {str(dialog_error)}")
                    return False, None
                
        except Exception as e:
            screenshot_path = self.take_screenshot(f"transmit_error_ndo_{ndo}")
            self.log("error", f"NDO {ndo}: Error verificando/transmitiendo: {str(e)}", screenshot_path)
            return False, screenshot_path
            
    def update_case_as_processed(self, case_index):
        try:
            case_data = self.excel_data[case_index]
            ndo_to_update = case_data.get('NDO')
            cod_to_update = case_data.get('CODIGO_PAMI')
            
            if not ndo_to_update or not cod_to_update:
                self.log("error", f"No NDO or COD found for case index {case_index}")
                return
            
            current_data = self.google_sheet.get_all_records()
            all_values = self.google_sheet.get_all_values()
            header_row = all_values[0] if all_values else []
            
            if 'Procesado' not in header_row:
                self.log("error", "Columna 'Procesado' no encontrada en Google Sheets")
                return
                
            procesado_col = header_row.index('Procesado') + 1
            
            target_row = None
            for i, record in enumerate(current_data):
                if (str(record.get('NDO', '')) == str(ndo_to_update) and 
                    str(record.get('CODIGO_PAMI', '')) == str(cod_to_update)):
                    target_row = i + 2
                    break
            
            if target_row is None:
                self.log("error", f"No se encontró NDO {ndo_to_update} con COD {cod_to_update} en la hoja actual")
                return
            
            current_value = self.google_sheet.cell(target_row, procesado_col).value
            if current_value == 'Si':
                self.log("warning", f"NDO {ndo_to_update} COD {cod_to_update} ya estaba marcado como procesado")
                return
            
            self.google_sheet.update_cell(target_row, procesado_col, 'Si')
            self.log("info", f"NDO {ndo_to_update} COD {cod_to_update} marcado como procesado en fila {target_row}")
            
        except Exception as e:
            self.log("error", f"Error actualizando caso como procesado: {str(e)}")

    def update_case_as_failed(self, case_index):
        try:
            case_data = self.excel_data[case_index]
            ndo_to_update = case_data.get('NDO')
            cod_to_update = case_data.get('CODIGO_PAMI')
            
            if not ndo_to_update or not cod_to_update:
                self.log("error", f"No NDO or COD found for case index {case_index}")
                return
            
            current_data = self.google_sheet.get_all_records()
            all_values = self.google_sheet.get_all_values()
            header_row = all_values[0] if all_values else []
            
            if 'Procesado' not in header_row:
                self.log("error", "Columna 'Procesado' no encontrada en Google Sheets")
                return
                
            procesado_col = header_row.index('Procesado') + 1
            
            target_row = None
            for i, record in enumerate(current_data):
                if (str(record.get('NDO', '')) == str(ndo_to_update) and 
                    str(record.get('CODIGO_PAMI', '')) == str(cod_to_update)):
                    target_row = i + 2
                    break
            
            if target_row is None:
                self.log("error", f"No se encontró NDO {ndo_to_update} con COD {cod_to_update} en la hoja actual")
                return
            
            self.google_sheet.update_cell(target_row, procesado_col, 'No')
            self.log("info", f"NDO {ndo_to_update} COD {cod_to_update} marcado como NO procesado en fila {target_row}")
            
        except Exception as e:
            self.log("error", f"Error actualizando caso como no procesado: {str(e)}")