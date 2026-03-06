import tkinter as tk
from models.auth import AuthManager
from models.database import DatabaseManager
from views.login_view import LoginView
from views.dashboard_view import DashboardView

class AppWindow(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("EduTask - Organización Académica")
        self.geometry("450x620") 
        self.configure(bg="#F4F6F9")
        self.resizable(False, False)

        self.eval('tk::PlaceWindow . center')

        # Inicializamos los Modelos
        self.auth_manager = AuthManager()
        self.db_manager = DatabaseManager()

        self.vista_actual = None

        self.mostrar_login()

    def cambiar_vista(self, nueva_vista_clase, **kwargs):
        if self.vista_actual is not None:
            self.vista_actual.destroy()
            
        self.vista_actual = nueva_vista_clase(self, **kwargs)
        self.vista_actual.pack(fill="both", expand=True)

    def mostrar_login(self):
        self.geometry("450x620")
        self.eval('tk::PlaceWindow . center') 
        
        self.cambiar_vista(
            LoginView, 
            auth_manager=self.auth_manager, 
            on_login_success=self.mostrar_dashboard
        )

    def mostrar_dashboard(self):
        self.geometry("950x600")
        self.eval('tk::PlaceWindow . center')
        
        self.cambiar_vista(
            DashboardView,
            auth_manager=self.auth_manager,
            db_manager=self.db_manager,
            on_logout=self.cerrar_sesion
        )
        
    def cerrar_sesion(self):
        self.mostrar_login()