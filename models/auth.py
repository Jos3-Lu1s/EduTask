import bcrypt
from config.firebase_config import get_firestore_client
from google.cloud.firestore_v1.base_query import FieldFilter

class AuthManager:
    def __init__(self):
        self.db = get_firestore_client()
        self.collection_name = "users" 
        self.current_user = None

    def register_user(self, nombre, email, password):
        """Registra un nuevo usuario en Firestore"""
        users_ref = self.db.collection(self.collection_name)
        
        query = users_ref.where(filter=FieldFilter("email", "==", email)).stream()
        if any(query):
            raise Exception("Este correo electrónico ya está registrado.")

        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

        user_data = {
            "name": nombre,
            "email": email,
            "password": hashed_password.decode('utf-8') 
        }
        
        update_time, doc_ref = users_ref.add(user_data)
        return doc_ref.id 

    def login_user(self, email, password):
        """Inicia sesión y recupera los datos del usuario"""
        users_ref = self.db.collection(self.collection_name)
        
        query = users_ref.where(filter=FieldFilter("email", "==", email)).stream()
        
        user_doc = None
        for doc in query:
            user_doc = doc
            break

        if not user_doc:
            raise Exception("Usuario no encontrado.")

        user_data = user_doc.to_dict()

        password_valida = bcrypt.checkpw(
            password.encode('utf-8'), 
            user_data["password"].encode('utf-8')
        )

        if not password_valida:
            raise Exception("Contraseña incorrecta.")
            
        self.current_user = {
            "uid": user_doc.id,
            "email": user_data["email"],
            "name": user_data.get("name", "Estudiante"),
            "idToken": None 
        }
        return self.current_user

    def logout_user(self):
        """Limpia la sesión actual."""
        self.current_user = None