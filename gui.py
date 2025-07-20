import tkinter as tk
from tkinter import ttk, messagebox
from browser_automation import BrowserAutomation

class LoginGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.username = ""
        self.password = ""
        self.automation = None
        self.setup_gui()
    
    def setup_gui(self):
        self.root.title("PAMI Automation")
        self.root.geometry("300x200")
        self.root.resizable(False, False)
        
        tk.Label(self.root, text="Usuario:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.username_entry = tk.Entry(self.root, width=25)
        self.username_entry.grid(row=0, column=1, padx=10, pady=10)
        
        tk.Label(self.root, text="Contraseña:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.password_entry = tk.Entry(self.root, show="*", width=25)
        self.password_entry.grid(row=1, column=1, padx=10, pady=10)

        self.start_button = tk.Button(self.root, text="Iniciar Automatización", 
                                     command=self.start_automation, bg="#4CAF50", fg="white")
        self.start_button.grid(row=2, column=0, columnspan=2, pady=20)
        
        self.status_label = tk.Label(self.root, text="Listo para iniciar", fg="blue")
        self.status_label.grid(row=3, column=0, columnspan=2, pady=10)
    
    def start_automation(self):
        self.username = self.username_entry.get().strip()
        self.password = self.password_entry.get().strip()
        
        if not self.username or not self.password:
            messagebox.showerror("Error", "Por favor ingrese usuario y contraseña")
            return
        
        self.status_label.config(text="Iniciando automatización...", fg="orange")
        self.start_button.config(state="disabled")
        
        try:
            self.automation = BrowserAutomation()
            self.automation.start_browser()
            self.automation.navigate_to_login()
            self.status_label.config(text="Navegador abierto - Complete manualmente", fg="green")
        except Exception as e:
            messagebox.showerror("Error", f"Error al iniciar: {str(e)}")
            self.status_label.config(text="Error al iniciar", fg="red")
            self.start_button.config(state="normal")
    
    def run(self):
        self.root.mainloop()
        if self.automation:
            self.automation.close_browser()