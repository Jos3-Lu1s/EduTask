import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from PIL import Image, ImageTk
import urllib.request
from io import BytesIO

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
        self.cargar_tareas() # Cargamos las tareas apenas se abre la ventana

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
            estilo.configure("Treeview", rowheight=55,) 
            
        except Exception as e:
            print(f"Error cargando la imagen: {e}")
            self.img_fila = None

    def _construir_interfaz(self):
        # --- ENCABEZADO ---
        frame_header = ttk.Frame(self)
        frame_header.pack(fill="x", pady=(0, 20))
        
        ttk.Label(frame_header, text="Mis Tareas Académicas", style="Titulo.TLabel").pack(side="left")
        
        btn_logout = ttk.Button(frame_header, text="Cerrar Sesión", style="Secundario.TButton", command=self.procesar_logout)
        btn_logout.pack(side="right")
        
        ttk.Label(frame_header, text=f"Usuario: {self.user['email']}", style="Normal.TLabel").pack(side="right", padx=20)

        # --- CUERPO PRINCIPAL (Dividido en 2 columnas) ---
        frame_body = ttk.Frame(self)
        frame_body.pack(fill="both", expand=True)

        # PANEL IZQUIERDO: Formulario
        frame_form = ttk.LabelFrame(frame_body, text="Nueva Tarea", padding="15 15 15 15")
        frame_form.pack(side="left", fill="y", padx=(0, 20))

        ttk.Label(frame_form, text="Título:", style="Normal.TLabel").pack(anchor="w")
        self.entry_titulo = ttk.Entry(frame_form, width=30, font=("Segoe UI", 11))
        self.entry_titulo.pack(pady=(0, 10), ipady=3)

        ttk.Label(frame_form, text="Descripción:", style="Normal.TLabel").pack(anchor="w")
        self.entry_desc = tk.Text(frame_form, width=30, height=5, font=("Segoe UI", 10))
        self.entry_desc.pack(pady=(0, 10))

        ttk.Label(frame_form, text="Fecha de Entrega:", style="Normal.TLabel").pack(anchor="w")
        
        self.entry_fecha = DateEntry(
            frame_form, 
            width=28, 
            font=("Segoe UI", 11),
            background='#3498DB',
            foreground='white',
            borderwidth=1,
            date_pattern='yyyy-mm-dd'
        )
        self.entry_fecha.pack(pady=(0, 20), ipady=3)

        self.entry_fecha.pack(pady=(0, 20), ipady=3)

        ttk.Label(frame_form, text="Link de Imagen (Opcional):", style="Normal.TLabel").pack(anchor="w")
        self.entry_link_img = ttk.Entry(frame_form, width=30, font=("Segoe UI", 11))
        self.entry_link_img.pack(pady=(0, 20), ipady=3)

        btn_agregar = ttk.Button(frame_form, text="Agregar Tarea", style="Principal.TButton", command=self.agregar_tarea)
        btn_agregar.pack(fill="x")

        # PANEL DERECHO: Tabla de Tareas (Treeview)
        frame_tabla = ttk.Frame(frame_body)
        frame_tabla.pack(side="right", fill="both", expand=True)

        # Columnas
        columnas = ("titulo", "descripcion", "fecha", "estado")
        
        self.tabla = ttk.Treeview(frame_tabla, columns=columnas, show="tree headings", selectmode="browse")
        
        self.tabla.heading("#0", text="Imagen")
        self.tabla.column("#0", width=70, anchor="center")
        
        self.tabla.heading("titulo", text="Título")
        self.tabla.heading("descripcion", text="Descripción")
        self.tabla.heading("fecha", text="Fecha de Entrega")
        self.tabla.heading("estado", text="Estado")

        self.tabla.column("titulo", width=150)
        self.tabla.column("descripcion", width=250)
        self.tabla.column("fecha", width=120, anchor="center")
        self.tabla.column("estado", width=100, anchor="center")

        self.tabla.pack(fill="both", expand=True, pady=(0, 10))

        # Botones de Acción para la tabla
        frame_acciones = ttk.Frame(frame_tabla)
        frame_acciones.pack(fill="x")

        btn_completar = ttk.Button(frame_acciones, text="Marcar como Completada", style="Exito.TButton", command=self.completar_tarea)
        btn_completar.pack(side="left", padx=(0, 10))

        btn_eliminar = ttk.Button(frame_acciones, text="Eliminar Tarea", style="Peligro.TButton", command=self.eliminar_tarea)
        btn_eliminar.pack(side="left")

    # --- LÓGICA DE DATOS ---

    def cargar_tareas(self):
        """Limpia la tabla y carga las tareas desde Firebase."""
        for item in self.tabla.get_children():
            self.tabla.delete(item)

        if not hasattr(self, 'imagenes_cache'):
            self.imagenes_cache = {}
        self.imagenes_cache.clear()

        try:
            tareas = self.db_manager.get_user_tasks(self.user['uid'])
            for t in tareas:
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

                self.tabla.insert(
                    "", 
                    "end", 
                    iid=t['id'], 
                    image=imagen_a_mostrar, 
                    values=(t['title'], t['description'], t['due_date'], t['status'])
                )
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar las tareas: {e}")

    def agregar_tarea(self):
        titulo = self.entry_titulo.get().strip()
        desc = self.entry_desc.get("1.0", tk.END).strip()
        fecha = self.entry_fecha.get().strip()
        link_img = self.entry_link_img.get().strip()

        if not titulo or not fecha:
            messagebox.showwarning("Campos incompletos", "El título y la fecha son obligatorios.")
            return

        try:
            self.db_manager.create_task(self.user['uid'], titulo, desc, fecha, link_img) 
            messagebox.showinfo("Éxito", "Tarea agregada correctamente.")
            
            # Limpiar formulario
            self.entry_titulo.delete(0, tk.END)
            self.entry_desc.delete("1.0", tk.END)
            self.entry_fecha.delete(0, tk.END)
            self.entry_link_img.delete(0, tk.END)
            
            # Recargar la tabla
            self.cargar_tareas()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar la tarea: {e}")

    def completar_tarea(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Sin selección", "Por favor, selecciona una tarea de la tabla.")
            return
            
        task_id = seleccion[0] # El ID del documento en Firebase que asignamos como iid
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

    def procesar_logout(self):
        self.auth_manager.logout_user()
        self.on_logout()