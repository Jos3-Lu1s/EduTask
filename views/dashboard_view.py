import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from PIL import Image, ImageTk
import urllib.request
from io import BytesIO
import logging
from models.auth import ocultar_correo
import re

class DashboardView(ttk.Frame):
    def __init__(self, parent, auth_manager, db_manager, on_logout):
        super().__init__(parent, padding="20 20 20 20")
        
        self.auth_manager = auth_manager
        self.db_manager = db_manager
        self.on_logout = on_logout
        
        # Datos del usuario actual
        self.user = self.auth_manager.current_user

        self._configurar_estilos()
        self._construir_interfaz()
        self.cargar_tareas() 

        # --- SISTEMA DE INACTIVIDAD ---
        # Configuramos el tiempo límite
        # self.timeout_ms = 5 * 60 * 1000 
        self.timeout_ms = 5000 
        self.timer_inactividad = None
        
        # Vincular la actividad del teclado y mouse a nivel de toda la ventana
        top_window = self.winfo_toplevel()
        
        # Se usa add="+" para no sobreescribir otros eventos internos de Tkinter
        self.bind_teclado = top_window.bind("<Key>", self.reiniciar_temporizador, add="+")
        self.bind_click = top_window.bind("<Button>", self.reiniciar_temporizador, add="+")
        self.bind_movimiento = top_window.bind("<Motion>", self.reiniciar_temporizador, add="+")
        
        # Iniciamos el temporizador por primera vez
        self.reiniciar_temporizador()
        # ------------------------------

    def _configurar_estilos(self):
        self.configure(style="TFrame")
        estilo = ttk.Style()
        estilo.configure("Peligro.TButton", font=("Segoe UI", 10, "bold"), background="#E74C3C", foreground="white")
        estilo.map("Peligro.TButton", background=[("active", "#C0392B")])
        estilo.configure("Exito.TButton", font=("Segoe UI", 10, "bold"), background="#2ECC71", foreground="white")
        estilo.map("Exito.TButton", background=[("active", "#27AE60")])

        try:
            imagen_original = Image.open("assets/image.jpg")
            imagen_original = imagen_original.resize((50, 50), Image.Resampling.LANCZOS)
            self.img_fila = ImageTk.PhotoImage(imagen_original)
            estilo.configure("Treeview", rowheight=55) 
        except Exception as e:
            print(f"Error cargando la imagen: {e}")
            self.img_fila = None

    def validar_entrada(self, nuevo_texto, longitud_maxima, tipo_campo):
        if len(nuevo_texto) > int(longitud_maxima):
            return False

        if tipo_campo == "texto_limpio":
            # Letras, números, puntuación básica. BLOQUEA: < > { } = ` ~ (Símbolos de inyección)
            patron = r'^[a-zA-Z0-9áéíóúÁÉÍÓÚñÑ\s.,!?()\-:;]*$'
        elif tipo_campo == "url":
            # Caracteres válidos para un enlace web
            patron = r'^[a-zA-Z0-9:\/\.\-\_?&=%]*$'
        else:
            patron = r'.*'

        return re.match(patron, nuevo_texto) is not None

    def limitar_descripcion(self, event):
        """Valida longitud y caracteres para el widget Text."""
        teclas_control = ['BackSpace', 'Delete', 'Left', 'Right', 'Up', 'Down']
        if event.keysym in teclas_control:
            return

        # 1. Bloquear caracteres peligrosos en tiempo real al teclear
        if event.char and not re.match(r'[a-zA-Z0-9áéíóúÁÉÍÓÚñÑ\s.,!?()\-:;\n]', event.char):
            return "break"

        # 2. Bloquear si excede la longitud
        if len(self.entry_desc.get("1.0", "end-1c")) >= 250:
            return "break"

    def sanitizar_texto(self, texto, es_multilinea=False):
        if not texto:
            return ""
        texto = texto.strip()
        if not es_multilinea:
            # Quita espacios dobles en títulos
            texto = re.sub(r' +', ' ', texto) 
        else:
            # En la descripción respetamos los saltos de línea (\n) pero quitamos dobles espacios
            texto = re.sub(r'[ \t]+', ' ', texto)
        return texto
    # -----------------------------------

    def _construir_interfaz(self):
        # --- ENCABEZADO ---
        frame_header = ttk.Frame(self)
        frame_header.pack(fill="x", pady=(0, 20))
        
        ttk.Label(frame_header, text="Mis Tareas Académicas", style="Titulo.TLabel").pack(side="left")
        
        btn_logout = ttk.Button(frame_header, text="Cerrar Sesión", style="Secundario.TButton", command=self.procesar_logout)
        btn_logout.pack(side="right")
        
        nombre_usuario = self.user.get('name', 'Estudiante')
        ttk.Label(frame_header, text=f"Hola, {nombre_usuario}", style="Normal.TLabel").pack(side="right", padx=20)

        # --- CUERPO PRINCIPAL ---
        frame_body = ttk.Frame(self)
        frame_body.pack(fill="both", expand=True)

        self.cmd_titulo = (self.register(self.validar_entrada), '%P', '50', 'texto_limpio')
        self.cmd_link = (self.register(self.validar_entrada), '%P', '300', 'url')

        # PANEL IZQUIERDO: Formulario
        frame_form = ttk.LabelFrame(frame_body, text="Nueva Tarea", padding="15 15 15 15")
        frame_form.pack(side="left", fill="y", padx=(0, 20))

        # Leyenda indicativa
        ttk.Label(frame_form, text="* Indica un campo obligatorio", font=("Segoe UI", 9, "italic"), foreground="#7F8C8D", background="#F4F6F9").pack(anchor="w", pady=(0, 10))

        ttk.Label(frame_form, text="Título * (Max 50):", style="Normal.TLabel").pack(anchor="w")
        self.entry_titulo = ttk.Entry(frame_form, width=32, font=("Segoe UI", 11), validate="key", validatecommand=self.cmd_titulo)
        self.entry_titulo.pack(pady=(0, 10), ipady=3)

        ttk.Label(frame_form, text="Descripción (Opcional, Max 250):", style="Normal.TLabel").pack(anchor="w")
        self.entry_desc = tk.Text(frame_form, width=32, height=6, font=("Segoe UI", 10))
        self.entry_desc.pack(pady=(0, 10))

        self.entry_desc.bind("<KeyPress>", self.limitar_descripcion)

        ttk.Label(frame_form, text="Fecha de Entrega *:", style="Normal.TLabel").pack(anchor="w")
        self.entry_fecha = DateEntry(
            frame_form, 
            width=30, 
            font=("Segoe UI", 11),
            background='#3498DB',
            foreground='white',
            borderwidth=1,
            date_pattern='yyyy-mm-dd'
        )
        self.entry_fecha.pack(pady=(0, 15), ipady=3)

        ttk.Label(frame_form, text="Link de Imagen (Opcional, Max 300):", style="Normal.TLabel").pack(anchor="w")
        self.entry_link_img = ttk.Entry(frame_form, width=32, font=("Segoe UI", 11), validate="key", validatecommand=self.cmd_link)
        self.entry_link_img.pack(pady=(0, 25), ipady=3)

        btn_agregar = ttk.Button(frame_form, text="Agregar Tarea", style="Principal.TButton", command=self.agregar_tarea)
        btn_agregar.pack(fill="x")

        # PANEL DERECHO
        frame_derecho = ttk.Frame(frame_body)
        frame_derecho.pack(side="right", fill="both", expand=True)

        frame_acciones = ttk.Frame(frame_derecho)
        frame_acciones.pack(side="bottom", fill="x", pady=(10, 0))

        btn_completar = ttk.Button(frame_acciones, text="Marcar como Completada", style="Exito.TButton", command=self.completar_tarea)
        btn_completar.pack(side="left", padx=(0, 10))

        btn_eliminar = ttk.Button(frame_acciones, text="Eliminar Tarea", style="Peligro.TButton", command=self.eliminar_tarea)
        btn_eliminar.pack(side="left")

        frame_tabla_scroll = ttk.Frame(frame_derecho)
        frame_tabla_scroll.pack(side="top", fill="both", expand=True)

        scrollbar_y = ttk.Scrollbar(frame_tabla_scroll, orient="vertical")
        scrollbar_y.pack(side="right", fill="y")

        columnas = ("titulo", "descripcion", "fecha", "estado")
        self.tabla = ttk.Treeview(
            frame_tabla_scroll, 
            columns=columnas, 
            show="tree headings", 
            selectmode="browse",
            yscrollcommand=scrollbar_y.set
        )
        scrollbar_y.config(command=self.tabla.yview)

        self.tabla.heading("#0", text="Imagen")
        self.tabla.column("#0", width=70, anchor="center")
        
        self.tabla.heading("titulo", text="Título")
        self.tabla.heading("descripcion", text="Descripción")
        self.tabla.heading("fecha", text="Fecha de Entrega")
        self.tabla.heading("estado", text="Estado")

        self.tabla.column("titulo", width=180)
        self.tabla.column("descripcion", width=280)
        self.tabla.column("fecha", width=130, anchor="center")
        self.tabla.column("estado", width=110, anchor="center")

        self.tabla.pack(side="left", fill="both", expand=True)

        self.tabla.bind("<Double-1>", self.abrir_modal_edicion)

        self.tabla.tag_configure("completada", foreground="#27AE60")
        self.tabla.tag_configure("pendiente", foreground="#34495E")

    # --- LÓGICA DE DATOS ---
    def cargar_tareas(self):
        for item in self.tabla.get_children():
            self.tabla.delete(item)

        if not hasattr(self, 'imagenes_cache'):
            self.imagenes_cache = {}
        self.imagenes_cache.clear()

        self.tareas_actuales = {}

        try:
            tareas = self.db_manager.get_user_tasks(self.user['uid'])
            for t in tareas:
                self.tareas_actuales[t['id']] = t  

                imagen_a_mostrar = self.img_fila 
                enlace = t.get('image_url', "") 
                if enlace:
                    try:
                        with urllib.request.urlopen(enlace) as respuesta:
                            datos = respuesta.read()
                        img_web = Image.open(BytesIO(datos)).resize((50, 50), Image.Resampling.LANCZOS)
                        imagen_a_mostrar = ImageTk.PhotoImage(img_web)
                    except Exception as e:
                        print(f"Error descargando imagen para tarea {t['id']}: {e}")

                self.imagenes_cache[t['id']] = imagen_a_mostrar

                estado_db = t.get('status', 'pendiente')
                if estado_db == 'completada':
                    indicador_visual = "✅ Terminada"
                    tag_color = "completada"
                else:
                    indicador_visual = "⏳ Pendiente"
                    tag_color = "pendiente"

                self.tabla.insert(
                    "", 
                    "end", 
                    iid=t['id'], 
                    image=imagen_a_mostrar, 
                    values=(t['title'], t['description'], t['due_date'], indicador_visual),
                    tags=(tag_color,)
                )
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar las tareas: {e}")

    def agregar_tarea(self):
        titulo = self.sanitizar_texto(self.entry_titulo.get())
        desc = self.sanitizar_texto(self.entry_desc.get("1.0", tk.END), es_multilinea=True)
        fecha = self.sanitizar_texto(self.entry_fecha.get())
        link_img = self.sanitizar_texto(self.entry_link_img.get())

        if not titulo or not fecha:
            messagebox.showwarning("Campos incompletos", "Por favor, completa los campos obligatorios marcados con asterisco (*).")
            return

        try:
            self.db_manager.create_task(self.user['uid'], titulo, desc, fecha, link_img) 
            messagebox.showinfo("Éxito", "Tarea agregada correctamente.")
            
            self.entry_titulo.delete(0, tk.END)
            self.entry_desc.delete("1.0", tk.END)
            self.entry_fecha.delete(0, tk.END)
            self.entry_link_img.delete(0, tk.END)
            
            self.cargar_tareas()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar la tarea: {e}")

    def completar_tarea(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Sin selección", "Por favor, selecciona una tarea de la tabla.")
            return
            
        task_id = seleccion[0] 
        try:
            self.db_manager.update_task_status(task_id, "completada")
            self.cargar_tareas()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar la tarea: {e}")

    def eliminar_tarea(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Sin selección", "Por favor, selecciona una tarea de la tabla.")
            return
            
        if messagebox.askyesno("Confirmar", "¿Estás seguro de que deseas eliminar esta tarea permanentemente?"):
            task_id = seleccion[0]
            try:
                self.db_manager.delete_task(task_id)
                self.cargar_tareas()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar la tarea: {e}")

    # --- LÓGICA DE INACTIVIDAD ---
    def reiniciar_temporizador(self, event=None):
        """Cancela el reloj actual y comienza uno nuevo desde cero."""
        if self.timer_inactividad:
            self.after_cancel(self.timer_inactividad)
        
        # Solo reiniciamos si esta vista sigue existiendo (evita errores al cambiar de ventana)
        if self.winfo_exists():
            self.timer_inactividad = self.after(self.timeout_ms, self.cerrar_sesion_inactividad)

    def cerrar_sesion_inactividad(self):
        """Fuerza el cierre de sesión cuando el temporizador llega a su límite."""
        # --- CORRECCIÓN: Ocultamos el correo antes de enviarlo al log ---
        correo_seguro = ocultar_correo(self.user['email'])
        logging.warning(f"SESIÓN EXPIRADA: Cierre automático por inactividad ({correo_seguro})")
        # ----------------------------------------------------------------
        
        messagebox.showwarning(
            "Sesión Expirada", 
            "Por tu seguridad, la sesión se ha cerrado automáticamente tras 5 minutos de inactividad."
        )
        self.procesar_logout()

    def procesar_logout(self):
        """Limpia todo antes de regresar al login."""
        # Detener el reloj para que no siga contando en la pantalla de Login
        if self.timer_inactividad:
            self.after_cancel(self.timer_inactividad)
            
        # Desvincular los eventos del mouse/teclado para no gastar recursos
        top_window = self.winfo_toplevel()
        try:
            top_window.unbind("<Key>", self.bind_teclado)
            top_window.unbind("<Button>", self.bind_click)
            top_window.unbind("<Motion>", self.bind_movimiento)
        except Exception:
            pass 
            
        # 3. Cerramos sesión y avisamos a app_window.py
        self.auth_manager.logout_user()
        self.on_logout()
    
    def abrir_modal_edicion(self, event):
        """Abre una ventana emergente para editar la tarea seleccionada."""
        seleccion = self.tabla.selection()
        if not seleccion:
            return
            
        task_id = seleccion[0]
        # Recuperamos todos los datos originales de la tarea
        tarea_data = getattr(self, 'tareas_actuales', {}).get(task_id)
        
        if not tarea_data:
            return

        modal = tk.Toplevel(self)
        modal.title("Editar Tarea")
        modal.geometry("450x550")
        modal.configure(bg="#F4F6F9")
        modal.grab_set()

        modal.bind("<Key>", self.reiniciar_temporizador, add="+")
        modal.bind("<Button>", self.reiniciar_temporizador, add="+")
        modal.bind("<Motion>", self.reiniciar_temporizador, add="+")

        ttk.Label(modal, text="Editar Tarea", font=("Segoe UI", 16, "bold"), background="#F4F6F9").pack(pady=15)

        frame_form = ttk.Frame(modal, padding=20, style="TFrame")
        frame_form.pack(fill="both", expand=True)

        # Creación y llenado de campos
        ttk.Label(frame_form, text="Título * (Max 50):", style="Normal.TLabel").pack(anchor="w")
        entry_titulo = ttk.Entry(frame_form, width=35, font=("Segoe UI", 11), validate="key", validatecommand=self.cmd_titulo)
        entry_titulo.insert(0, tarea_data.get('title', ''))
        entry_titulo.pack(pady=(0, 10), ipady=3)

        ttk.Label(frame_form, text="Descripción (Opcional, Max 250):", style="Normal.TLabel").pack(anchor="w")
        entry_desc = tk.Text(frame_form, width=35, height=5, font=("Segoe UI", 10))
        entry_desc.insert("1.0", tarea_data.get('description', ''))
        entry_desc.pack(pady=(0, 10))
        entry_desc.bind("<KeyPress>", self.limitar_descripcion)

        ttk.Label(frame_form, text="Fecha de Entrega *:", style="Normal.TLabel").pack(anchor="w")
        entry_fecha = DateEntry(frame_form, width=33, font=("Segoe UI", 11), background='#3498DB', foreground='white', borderwidth=1, date_pattern='yyyy-mm-dd')
        entry_fecha.set_date(tarea_data.get('due_date', ''))
        entry_fecha.pack(pady=(0, 10), ipady=3)

        ttk.Label(frame_form, text="Link de Imagen (Opcional, Max 300):", style="Normal.TLabel").pack(anchor="w")
        entry_link = ttk.Entry(frame_form, width=35, font=("Segoe UI", 11), validate="key", validatecommand=self.cmd_link)
        entry_link.insert(0, tarea_data.get('image_url', ''))
        entry_link.pack(pady=(0, 20), ipady=3)

        # Función interna para guardar los cambios
        def guardar_cambios():
            nuevo_titulo = self.sanitizar_texto(self.entry_titulo.get())
            nueva_desc = self.sanitizar_texto(self.entry_desc.get("1.0", tk.END), es_multilinea=True)
            nueva_fecha = self.sanitizar_texto(self.entry_fecha.get())
            nuevo_link = self.sanitizar_texto(self.entry_link_img.get())

            if not nuevo_titulo or not nueva_fecha:
                messagebox.showwarning("Campos incompletos", "El Título y la Fecha son obligatorios.", parent=modal)
                return

            datos_actualizados = {
                "title": nuevo_titulo,
                "description": nueva_desc,
                "due_date": nueva_fecha,
                "image_url": nuevo_link
            }

            try:
                self.db_manager.update_task(task_id, datos_actualizados)
                modal.destroy()
                self.cargar_tareas()
                messagebox.showinfo("Éxito", "Tarea actualizada correctamente.")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo actualizar la tarea: {e}", parent=modal)

        btn_guardar = ttk.Button(frame_form, text="Guardar Cambios", style="Principal.TButton", command=guardar_cambios)
        btn_guardar.pack(fill="x", pady=(0, 10))
        
        btn_cancelar = ttk.Button(frame_form, text="Cancelar", style="Secundario.TButton", command=modal.destroy)
        btn_cancelar.pack(fill="x")