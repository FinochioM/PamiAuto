import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from browser_automation import BrowserAutomation
from logger import AutomationLogger
import threading

class PamiAutoGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.username = ""
        self.password = ""
        self.automation = None
        self.logger = AutomationLogger()
        self.current_log_dir = "logs"
        self.setup_gui()

    def setup_gui(self):
        self.root.title("PAMI Automation")
        self.root.geometry("400x350")
        self.root.resizable(False, False)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.login_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.login_frame, text="Login")
        self.setup_login_tab()

        self.logging_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.logging_frame, text="Logs")
        self.setup_logging_tab()

        self.settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_frame, text="Configuración")
        self.setup_settings_tab()

    def setup_login_tab(self):
        tk.Label(self.login_frame, text="Usuario:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.username_entry = tk.Entry(self.login_frame, width=25)
        self.username_entry.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(self.login_frame, text="Contraseña:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.password_entry = tk.Entry(self.login_frame, show="*", width=25)
        self.password_entry.grid(row=1, column=1, padx=10, pady=10)

        self.start_button = tk.Button(self.login_frame, text="Iniciar Automatización",
                                     command=self.start_automation_thread, bg="#4CAF50", fg="white")
        self.start_button.grid(row=2, column=0, columnspan=2, pady=20)

        self.status_label = tk.Label(self.login_frame, text="Listo para iniciar", fg="blue")
        self.status_label.grid(row=3, column=0, columnspan=2, pady=10)

    def setup_logging_tab(self):
        tk.Label(self.logging_frame, text="Archivos de Log:").pack(pady=10)

        self.log_listbox = tk.Listbox(self.logging_frame, height=10, width=50)
        self.log_listbox.pack(pady=10)

        tk.Button(self.logging_frame, text="Actualizar Lista",
                 command=self.refresh_log_list).pack(pady=5)

        self.refresh_log_list()

    def refresh_log_list(self):
        self.log_listbox.delete(0, tk.END)
        log_files = self.logger.get_log_files()
        for file in log_files:
            self.log_listbox.insert(tk.END, file)

    def start_automation_thread(self):
        thread = threading.Thread(target=self.start_automation)
        thread.daemon = True
        thread.start()

    def start_automation(self):
        self.username = self.username_entry.get().strip()
        self.password = self.password_entry.get().strip()

        if not self.username or not self.password:
            self.logger.error("Usuario o contraseña vacíos")
            messagebox.showerror("Error", "Por favor ingrese usuario y contraseña")
            return

        self.logger.info("Iniciando automatización")
        self.status_label.config(text="Iniciando automatización...", fg="orange")
        self.start_button.config(state="disabled")

        try:
            self.process_automation_steps()
        except Exception as e:
            error_msg = f"Error en automatización: {str(e)}"
            self.logger.error(error_msg)
            messagebox.showerror("Error", error_msg)
            self.status_label.config(text="Error al ejecutar", fg="red")
        finally:
            self.start_button.config(state="normal")
            log_file = self.logger.save_to_excel()
            if log_file:
                self.logger.info(f"Log guardado en: {log_file}")
                self.refresh_log_list()

    def process_automation_steps(self):
        self.logger.info("Creando instancia de BrowserAutomation")
        self.automation = BrowserAutomation(self.logger)

        self.logger.info("Iniciando navegador")
        self.status_label.config(text="Iniciando navegador...", fg="orange")
        self.automation.start_browser()

        self.logger.info("Navegando a página de login")
        self.status_label.config(text="Navegando a login...", fg="orange")
        self.automation.navigate_to_login()

        self.logger.info("Completando formulario de login")
        self.status_label.config(text="Completando login...", fg="orange")
        self.automation.fill_login_form(self.username, self.password)

        self.logger.info("Login completado exitosamente")
        self.status_label.config(text="Login completado", fg="green")

        self.logger.info("Haciendo clic en botón OME")
        self.status_label.config(text="Navegando a OME...", fg="orange")
        self.automation.click_ome_button()

        self.logger.info("Navegación a OME completada")
        self.status_label.config(text="OME abierto correctamente", fg="green")

        self.logger.info("Haciendo clic en Panel de prestaciones")
        self.status_label.config(text="Navegando a Panel...", fg="orange")
        self.automation.click_panel_prestaciones()

        self.logger.info("Panel de prestaciones abierto")
        self.status_label.config(text="Panel abierto correctamente", fg="green")

    def setup_settings_tab(self):
        tk.Label(self.settings_frame, text="Directorio de Logs:", font=("Arial", 10, "bold")).pack(pady=(20, 5))

        self.log_dir_label = tk.Label(self.settings_frame, text=self.current_log_dir,
                                     bg="white", relief="sunken", width=40)
        self.log_dir_label.pack(pady=5)

        tk.Button(self.settings_frame, text="Cambiar Directorio",
                 command=self.change_log_directory, bg="#2196F3", fg="white").pack(pady=10)

        tk.Button(self.settings_frame, text="Restaurar por Defecto",
                 command=self.reset_log_directory).pack(pady=5)

    def change_log_directory(self):
        new_dir = filedialog.askdirectory(
            title="Seleccionar directorio para logs",
            initialdir=self.current_log_dir
        )

        if new_dir:
            self.current_log_dir = new_dir
            self.logger.set_log_directory(new_dir)
            self.log_dir_label.config(text=new_dir)
            self.refresh_log_list()
            messagebox.showinfo("Éxito", f"Directorio de logs cambiado a:\n{new_dir}")

    def reset_log_directory(self):
        self.current_log_dir = "logs"
        self.logger.set_log_directory("logs")
        self.log_dir_label.config(text="logs")
        self.refresh_log_list()
        messagebox.showinfo("Éxito", "Directorio de logs restaurado por defecto")

    def run(self):
        self.root.mainloop()