import tkinter as tk
from tkinter import ttk, messagebox

class LoginView(ttk.Frame):
    def __init__(self, parent, auth_manager, on_login_success):
        super().__init__(parent, padding="30 30 30 30")
        
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
        estilo.map("Principal.TButton", background=[("active", "#2980B9")]) 

        estilo.configure("Secundario.TButton", font=("Segoe UI", 11, "bold"), background="#2ECC71", foreground="white", padding=8)
        estilo.map("Secundario.TButton", background=[("active", "#27AE60")])
        
        # Estilo para las pestañas
        estilo.configure("TNotebook", background="#F4F6F9", borderwidth=0)
        estilo.configure("TNotebook.Tab", font=("Segoe UI", 11), padding=[15, 5])
        estilo.map("TNotebook.Tab", background=[("selected", "#FFFFFF")], foreground=[("selected", "#2C3E50")])

    def _construir_interfaz(self):
        # Encabezado
        lbl_titulo = ttk.Label(self, text="EduTask", style="Titulo.TLabel")
        lbl_titulo.pack(pady=(0, 5))

        lbl_subtitulo = ttk.Label(self, text="Gestor de Actividades Académicas", style="Normal.TLabel")
        lbl_subtitulo.pack(pady=(0, 20))

        # --- SISTEMA DE PESTAÑAS (Notebook) ---
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        # 1. Pestaña de Inicio de Sesión
        frame_login = ttk.Frame(self.notebook, padding="20 20 20 20", style="TFrame")
        self.notebook.add(frame_login, text="Iniciar Sesión")
        self._construir_tab_login(frame_login)

        # 2. Pestaña de Registro
        frame_registro = ttk.Frame(self.notebook, padding="20 20 20 20", style="TFrame")
        self.notebook.add(frame_registro, text="Registrarse")
        self._construir_tab_registro(frame_registro)

    def _construir_tab_login(self, parent):
        """Construye los campos exclusivos para el inicio de sesión."""
        ttk.Label(parent, text="Correo Electrónico:", style="Normal.TLabel").pack(anchor="w")
        self.login_correo = ttk.Entry(parent, font=("Segoe UI", 11), width=35)
        self.login_correo.pack(pady=(0, 15), ipady=4)

        ttk.Label(parent, text="Contraseña:", style="Normal.TLabel").pack(anchor="w")
        self.login_pass = ttk.Entry(parent, font=("Segoe UI", 11), width=35, show="•")
        self.login_pass.pack(pady=(0, 25), ipady=4)

        btn_login = ttk.Button(parent, text="Entrar", style="Principal.TButton", command=self.procesar_login)
        btn_login.pack(fill="x", pady=(0, 10))

    def _construir_tab_registro(self, parent):
        """Construye los campos exclusivos para el registro."""
        ttk.Label(parent, text="Nombre Completo:", style="Normal.TLabel").pack(anchor="w")
        self.reg_nombre = ttk.Entry(parent, font=("Segoe UI", 11), width=35)
        self.reg_nombre.pack(pady=(0, 10), ipady=3)

        ttk.Label(parent, text="Correo Electrónico:", style="Normal.TLabel").pack(anchor="w")
        self.reg_correo = ttk.Entry(parent, font=("Segoe UI", 11), width=35)
        self.reg_correo.pack(pady=(0, 10), ipady=3)

        ttk.Label(parent, text="Contraseña:", style="Normal.TLabel").pack(anchor="w")
        self.reg_pass = ttk.Entry(parent, font=("Segoe UI", 11), width=35, show="•")
        self.reg_pass.pack(pady=(0, 10), ipady=3)

        ttk.Label(parent, text="Confirmar Contraseña:", style="Normal.TLabel").pack(anchor="w")
        self.reg_pass_conf = ttk.Entry(parent, font=("Segoe UI", 11), width=35, show="•")
        self.reg_pass_conf.pack(pady=(0, 20), ipady=3)

        btn_registro = ttk.Button(parent, text="Crear Cuenta", style="Secundario.TButton", command=self.procesar_registro)
        btn_registro.pack(fill="x")

    def procesar_login(self):
        correo = self.login_correo.get().strip()
        password = self.login_pass.get().strip()

        if not correo or not password:
            messagebox.showwarning("Campos vacíos", "Por favor ingresa tu correo y contraseña.")
            return

        try:
            self.auth_manager.login_user(correo, password)
            self.on_login_success() 
        except Exception as e:
            messagebox.showerror("Error de Autenticación", f"Credenciales incorrectas o usuario no encontrado.\n\nDetalle: {str(e)}")

    def procesar_registro(self):
        nombre = self.reg_nombre.get().strip()
        correo = self.reg_correo.get().strip()
        password = self.reg_pass.get().strip()
        confirmacion = self.reg_pass_conf.get().strip()

        if not nombre or not correo or not password or not confirmacion:
            messagebox.showwarning("Campos vacíos", "Por favor llena todos los campos para registrarte.")
            return
            
        if password != confirmacion:
            messagebox.showwarning("Error", "Las contraseñas no coinciden. Inténtalo de nuevo.")
            return

        if len(password) < 6:
            messagebox.showwarning("Contraseña débil", "La contraseña debe tener al menos 6 caracteres.")
            return

        try:
            self.auth_manager.register_user(nombre, correo, password)
            messagebox.showinfo("Éxito", "Cuenta creada correctamente. Ahora puedes iniciar sesión.")
            
            # Limpiamos los campos del registro
            self.reg_nombre.delete(0, tk.END)
            self.reg_correo.delete(0, tk.END)
            self.reg_pass.delete(0, tk.END)
            self.reg_pass_conf.delete(0, tk.END)
            
            # Cambiamos automáticamente a la pestaña de "Iniciar Sesión" (índice 0)
            self.notebook.select(0)
            
            # Opcional: Autocompletamos el correo en el login para mayor comodidad
            self.login_correo.delete(0, tk.END)
            self.login_correo.insert(0, correo)
            
        except Exception as e:
            messagebox.showerror("Error al Registrar", f"No se pudo crear la cuenta.\n\nDetalle: {str(e)}")