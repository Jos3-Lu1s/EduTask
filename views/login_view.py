import tkinter as tk
from tkinter import ttk, messagebox

class LoginView(ttk.Frame):
    def __init__(self, parent, auth_manager, on_login_success):
        super().__init__(parent, padding="50 50 50 50")
        
        self.auth_manager = auth_manager
        self.on_login_success = on_login_success 

        self._configurar_estilos()
        self._construir_interfaz()

    def _configurar_estilos(self):
        estilo = ttk.Style()
        estilo.theme_use('clam')

        fuente_titulo = ("Segoe UI", 24, "bold")
        fuente_normal = ("Segoe UI", 11)

        estilo.configure("TFrame", background="#F4F6F9")
        self.configure(style="TFrame")

        estilo.configure("Titulo.TLabel", font=fuente_titulo, background="#F4F6F9", foreground="#2C3E50")
        estilo.configure("Normal.TLabel", font=fuente_normal, background="#F4F6F9", foreground="#34495E")

        estilo.configure("Principal.TButton", font=("Segoe UI", 11, "bold"), background="#3498DB", foreground="white", padding=8)
        estilo.map("Principal.TButton", background=[("active", "#2980B9")]) # Color al pasar el mouse

        estilo.configure("Secundario.TButton", font=("Segoe UI", 10), background="#ECF0F1", foreground="#2C3E50", padding=5)
        estilo.map("Secundario.TButton", background=[("active", "#BDC3C7")])

    def _construir_interfaz(self):
        """Construye los widgets de la vista."""
        lbl_titulo = ttk.Label(self, text="EduTask", style="Titulo.TLabel")
        lbl_titulo.pack(pady=(0, 5))

        lbl_subtitulo = ttk.Label(self, text="Gestor de Actividades Académicas", style="Normal.TLabel")
        lbl_subtitulo.pack(pady=(0, 30))

        lbl_nombre = ttk.Label(self, text="Nombre (Solo para registro):", style="Normal.TLabel")
        lbl_nombre.pack(anchor="w")
        self.entry_nombre = ttk.Entry(self, font=("Segoe UI", 11), width=35)
        self.entry_nombre.pack(pady=(0, 15), ipady=4)

        lbl_correo = ttk.Label(self, text="Correo Electrónico:", style="Normal.TLabel")
        lbl_correo.pack(anchor="w")
        self.entry_correo = ttk.Entry(self, font=("Segoe UI", 11), width=35)
        self.entry_correo.pack(pady=(0, 15), ipady=4)

        lbl_pass = ttk.Label(self, text="Contraseña:", style="Normal.TLabel")
        lbl_pass.pack(anchor="w")
        self.entry_pass = ttk.Entry(self, font=("Segoe UI", 11), width=35, show="•") # Oculta la contraseña
        self.entry_pass.pack(pady=(0, 25), ipady=4)

        btn_login = ttk.Button(self, text="Iniciar Sesión", style="Principal.TButton", command=self.procesar_login)
        btn_login.pack(fill="x", pady=(0, 10))

        ttk.Separator(self, orient='horizontal').pack(fill='x', pady=10)

        btn_registro = ttk.Button(self, text="Crear Cuenta Nueva", style="Secundario.TButton", command=self.procesar_registro)
        btn_registro.pack(fill="x")

    def procesar_login(self):
        correo = self.entry_correo.get().strip()
        password = self.entry_pass.get().strip()

        if not correo or not password:
            messagebox.showwarning("Campos vacíos", "Por favor ingresa tu correo y contraseña.")
            return

        try:
            # Llamamos a nuestro modelo de autenticación
            self.auth_manager.login_user(correo, password)
            self.on_login_success()  # Le avisamos a la ventana principal que cambie de pantalla
        except Exception as e:
            messagebox.showerror("Error de Autenticación", f"Credenciales incorrectas o usuario no encontrado.\n\nDetalle: {str(e)}")

    def procesar_registro(self):
        nombre = self.entry_nombre.get().strip()
        correo = self.entry_correo.get().strip()
        password = self.entry_pass.get().strip()

        if not nombre or not correo or not password:
            messagebox.showwarning("Campos vacíos", "Por favor ingresa tu nombre, correo y contraseña para registrarte.")
            return
            
        if len(password) < 6:
            messagebox.showwarning("Contraseña débil", "La contraseña debe tener al menos 6 caracteres.")
            return

        try:
            self.auth_manager.register_user(nombre, correo, password)
            messagebox.showinfo("Éxito", "Cuenta creada correctamente. Ahora puedes iniciar sesión.")
            self.entry_pass.delete(0, tk.END)
            self.entry_nombre.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Error al Registrar", f"No se pudo crear la cuenta.\n\nDetalle: {str(e)}")