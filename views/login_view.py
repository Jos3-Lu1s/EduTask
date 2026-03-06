import tkinter as tk
from tkinter import ttk, messagebox
import re

class LoginView(ttk.Frame):
    def __init__(self, parent, auth_manager, on_login_success):
        super().__init__(parent, padding="30 30 30 30")
        
        self.auth_manager = auth_manager
        self.on_login_success = on_login_success 
        self.terminos_aceptados = tk.BooleanVar(value=False)

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
        
        estilo.configure("TNotebook", background="#F4F6F9", borderwidth=0)
        estilo.configure("TNotebook.Tab", font=("Segoe UI", 11), padding=[15, 5])
        estilo.map("TNotebook.Tab", background=[("selected", "#FFFFFF")], foreground=[("selected", "#2C3E50")])

        estilo.configure("TCheckbutton", background="#F4F6F9", font=("Segoe UI", 10))

    def _construir_interfaz(self):
        lbl_titulo = ttk.Label(self, text="EduTask", style="Titulo.TLabel")
        lbl_titulo.pack(pady=(0, 5))

        lbl_subtitulo = ttk.Label(self, text="Gestor de Actividades Académicas", style="Normal.TLabel")
        lbl_subtitulo.pack(pady=(0, 20))

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        frame_login = ttk.Frame(self.notebook, padding="20 20 20 20", style="TFrame")
        self.notebook.add(frame_login, text="Iniciar Sesión")
        self._construir_tab_login(frame_login)

        frame_registro = ttk.Frame(self.notebook, padding="20 20 20 20", style="TFrame")
        self.notebook.add(frame_registro, text="Registrarse")
        self._construir_tab_registro(frame_registro)

    def _construir_tab_login(self, parent):
        ttk.Label(parent, text="Correo Electrónico:", style="Normal.TLabel").pack(anchor="w")
        self.login_correo = ttk.Entry(parent, font=("Segoe UI", 11), width=35)
        self.login_correo.pack(pady=(0, 15), ipady=4)

        ttk.Label(parent, text="Contraseña:", style="Normal.TLabel").pack(anchor="w")
        self.login_pass = ttk.Entry(parent, font=("Segoe UI", 11), width=35, show="•")
        self.login_pass.pack(pady=(0, 25), ipady=4)

        btn_login = ttk.Button(parent, text="Entrar", style="Principal.TButton", command=self.procesar_login)
        btn_login.pack(fill="x", pady=(0, 10))

    def _construir_tab_registro(self, parent):
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
        self.reg_pass_conf.pack(pady=(0, 15), ipady=3)

        # --- SECCIÓN DE TÉRMINOS Y CONDICIONES ---
        frame_terminos = ttk.Frame(parent, style="TFrame")
        frame_terminos.pack(fill="x", pady=(0, 15))

        chk_terminos = ttk.Checkbutton(
            frame_terminos, 
            text="Acepto los", 
            variable=self.terminos_aceptados,
            style="TCheckbutton"
        )
        chk_terminos.pack(side="left")

        btn_leer_terminos = ttk.Button(frame_terminos, text="Términos y Condiciones", command=self.mostrar_terminos)
        btn_leer_terminos.pack(side="left", padx=(5, 0))
        # -------------------------------------------

        btn_registro = ttk.Button(parent, text="Crear Cuenta", style="Secundario.TButton", command=self.procesar_registro)
        btn_registro.pack(fill="x")

    def mostrar_terminos(self):
        """Abre una ventana emergente con el texto de los términos y condiciones."""
        ventana_terminos = tk.Toplevel(self)
        ventana_terminos.title("Términos y Condiciones")
        ventana_terminos.geometry("500x400")
        ventana_terminos.configure(bg="#F4F6F9")
        
        ventana_terminos.grab_set() 

        def aceptar_y_cerrar():
            self.terminos_aceptados.set(True)
            ventana_terminos.destroy()
        
        ventana_terminos.protocol("WM_DELETE_WINDOW", aceptar_y_cerrar)

        frame_texto = ttk.Frame(ventana_terminos, padding=15)
        frame_texto.pack(fill="both", expand=True)

        scrollbar = ttk.Scrollbar(frame_texto)
        scrollbar.pack(side="right", fill="y")

        texto_widget = tk.Text(
            frame_texto, 
            wrap="word", 
            yscrollcommand=scrollbar.set, 
            font=("Segoe UI", 10),
            bg="white",
            relief="flat"
        )
        texto_widget.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=texto_widget.yview)

        terms_text = (
            "1. ACEPTACIÓN DE LOS TÉRMINOS Y CONDICIONES\n"
            "Al utilizar este software, el usuario acepta estos términos y condiciones, que constituyen un acuerdo legal entre el usuario y EduTask Solutions.\n\n"
            
            "2. DESCRIPCIÓN DEL SERVICIO\n"
            "EduTask Solutions proporciona una plataforma para la gestión de tareas educativas de manera eficiente y organizada. El uso de la plataforma está restringido a fines personales y educativos.\n\n"
            
            "3. USO DEL SOFTWARE\n"
            "El software está destinado únicamente a usuarios finales. No se permite el uso comercial o la redistribución del software sin el consentimiento explícito de EduTask Solutions.\n\n"
            
            "4. REQUISITOS DEL USUARIO\n"
            "El usuario debe ser mayor de 13 años para utilizar esta aplicación. Al registrarse, el usuario declara ser mayor de edad o tener el consentimiento de un tutor legal.\n\n"
            
            "5. PRIVACIDAD Y PROTECCIÓN DE DATOS\n"
            "EduTask Solutions recopila y procesa datos personales de acuerdo con su Política de Privacidad. El usuario acepta el tratamiento de sus datos para fines relacionados con el uso de la plataforma.\n\n"
            
            "6. RESPONSABILIDAD DEL USUARIO\n"
            "El usuario es responsable de mantener la confidencialidad de su cuenta, incluyendo el nombre de usuario y la contraseña. EduTask Solutions no se hace responsable de cualquier pérdida o daño que surja debido al uso no autorizado de la cuenta del usuario.\n\n"
            
            "7. EXONERACIÓN DE RESPONSABILIDAD\n"
            "EduTask Solutions no se hace responsable por cualquier tipo de daño directo o indirecto, pérdida de datos o fallos en el sistema, derivados del uso de la aplicación.\n\n"
            
            "8. TERMINACIÓN DEL SERVICIO\n"
            "EduTask Solutions se reserva el derecho de suspender o terminar la cuenta de un usuario en caso de incumplimiento de estos términos y condiciones.\n\n"
            
            "9. MODIFICACIONES A LOS TÉRMINOS\n"
            "EduTask Solutions se reserva el derecho de modificar estos términos y condiciones en cualquier momento. El usuario será notificado de las modificaciones y deberá aceptar los nuevos términos para seguir utilizando el servicio.\n\n"
            
            "10. LEY APLICABLE Y JURISDICCIÓN\n"
            "Estos términos y condiciones se rigen por las leyes del país en el que EduTask Solutions tiene su sede. Cualquier disputa será resuelta en los tribunales competentes de dicha jurisdicción.\n\n"
            
            "Al hacer clic en 'Aceptar', el usuario reconoce haber leído, comprendido y aceptado estos términos y condiciones."
        )
        texto_widget.insert("1.0", terms_text)
        
        texto_widget.config(state="disabled")

        btn_cerrar = ttk.Button(ventana_terminos, text="Cerrar", command=aceptar_y_cerrar)
        btn_cerrar.pack(pady=10)

    def procesar_login(self):
        correo = self.login_correo.get().strip()
        password = self.login_pass.get().strip()

        if not correo or not password:
            messagebox.showwarning("Campos vacíos", "Por favor ingresa tu correo y contraseña.")
            return

        patron_correo = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not re.match(patron_correo, correo):
            messagebox.showwarning("Correo inválido", "El formato del correo electrónico no es válido.")
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

        # Verifica que no haya campos vacíos
        if not nombre or not correo or not password or not confirmacion:
            messagebox.showwarning("Campos vacíos", "Por favor llena todos los campos para registrarte.")
            return
        
        patron_correo = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not re.match(patron_correo, correo):
            messagebox.showwarning("Correo inválido", "Por favor ingresa un correo electrónico válido (ej. usuario@dominio.com).")
            return
            
        # Verifica términos y condiciones
        if not self.terminos_aceptados.get():
            messagebox.showwarning("Términos Requeridos", "Debes leer y aceptar los Términos y Condiciones para crear una cuenta.")
            return

        # Verifica que las contraseñas coincidan
        if password != confirmacion:
            messagebox.showwarning("Error", "Las contraseñas no coinciden. Inténtalo de nuevo.")
            return

        # --- REGLAS DE SEGURIDAD PARA LA CONTRASEÑA ---
        if len(password) < 8:
            messagebox.showwarning("Contraseña débil", "La contraseña debe tener al menos 8 caracteres.")
            return
        if not re.search(r"[A-Z]", password):
            messagebox.showwarning("Contraseña débil", "La contraseña debe incluir al menos una letra mayúscula.")
            return
        if not re.search(r"[a-z]", password):
            messagebox.showwarning("Contraseña débil", "La contraseña debe incluir al menos una letra minúscula.")
            return
        if not re.search(r"\d", password):
            messagebox.showwarning("Contraseña débil", "La contraseña debe incluir al menos un número.")
            return
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>\-_]", password):
            messagebox.showwarning("Contraseña débil", "La contraseña debe incluir al menos un carácter especial (ej. @, #, $, _, -).")
            return

        try:
            self.auth_manager.register_user(nombre, correo, password)
            messagebox.showinfo("Éxito", "Cuenta creada correctamente. Ahora puedes iniciar sesión.")
            
            self.reg_nombre.delete(0, tk.END)
            self.reg_correo.delete(0, tk.END)
            self.reg_pass.delete(0, tk.END)
            self.reg_pass_conf.delete(0, tk.END)
            self.terminos_aceptados.set(False) 
            
            self.notebook.select(0)
            self.login_correo.delete(0, tk.END)
            self.login_correo.insert(0, correo)
            
        except Exception as e:
            messagebox.showerror("Error al Registrar", f"No se pudo crear la cuenta.\n\nDetalle: {str(e)}")