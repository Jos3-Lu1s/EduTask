import requests
from config.firebase_config import FIREBASE_WEB_API_KEY

class AuthManager:
    def __init__(self):
        self.api_key = FIREBASE_WEB_API_KEY
        self.current_user = None  # Almacenará el UID y token si el login es exitoso

    def register_user(self, email, password):
        """Registra un nuevo usuario en Firebase Auth."""
        endpoint = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={self.api_key}"
        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }
        
        response = requests.post(endpoint, json=payload)
        data = response.json()
        
        if "error" in data:
            raise Exception(data["error"]["message"])
            
        return data["localId"] # Retorna el UID del nuevo usuario

    def login_user(self, email, password):
        """Inicia sesión y guarda los datos del usuario actual."""
        endpoint = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={self.api_key}"
        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }
        
        response = requests.post(endpoint, json=payload)
        data = response.json()
        
        if "error" in data:
            raise Exception(data["error"]["message"])
            
        # Guardamos la sesión en memoria
        self.current_user = {
            "uid": data["localId"],
            "idToken": data["idToken"],
            "email": data["email"]
        }
        return self.current_user

    def logout_user(self):
        """Limpia la sesión actual."""
        self.current_user = None