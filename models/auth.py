import bcrypt
from config.firebase_config import get_firestore_client
from google.cloud.firestore_v1.base_query import FieldFilter

class AuthManager:
    def __init__(self):
        self.db = get_firestore_client()
        self.collection_name = "users" 
        self.current_user = None

    def register_user(self, nombre, email, password):
        """Registra un nuevo usuario incluyendo campos de seguridad en la DB."""
        users_ref = self.db.collection(self.collection_name)
        
        query = users_ref.where(filter=FieldFilter("email", "==", email)).stream()
        if any(query):
            raise Exception("Este correo electrónico ya está registrado.")

        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

        user_data = {
            "name": nombre,
            "email": email,
            "password": hashed_password.decode('utf-8'),
            "failed_attempts": 0,
            "is_suspended": False
        }
        
        update_time, doc_ref = users_ref.add(user_data)
        return doc_ref.id 

    def login_user(self, email, password):
        """Inicia sesión y maneja suspensiones por 6 intentos fallidos."""
        users_ref = self.db.collection(self.collection_name)
        query = users_ref.where(filter=FieldFilter("email", "==", email)).stream()
        
        user_doc = None
        for doc in query:
            user_doc = doc
            break

        if not user_doc:
            raise Exception("Usuario no encontrado.")

        user_data = user_doc.to_dict()
        doc_ref = users_ref.document(user_doc.id) 

        # VERIFICAR SI LA CUENTA YA ESTÁ SUSPENDIDA
        if user_data.get("is_suspended", False):
            raise Exception("Tu cuenta está SUSPENDIDA. Por favor, contacta a soporte técnico.")

        # VERIFICAR CONTRASEÑA
        password_valida = bcrypt.checkpw(
            password.encode('utf-8'), 
            user_data["password"].encode('utf-8')
        )

        if not password_valida:
            # Si falla, suma 1 al contador global en Firestore
            intentos_globales = user_data.get("failed_attempts", 0) + 1
            
            if intentos_globales >= 6:
                # Al sexto error, suspendemos en Firestore
                doc_ref.update({"is_suspended": True, "failed_attempts": intentos_globales})
                raise Exception("Has fallado 6 veces consecutivas. Tu cuenta ha sido SUSPENDIDA. Contacta a soporte técnico.")
            else:
                # Guarda el incremento de error
                doc_ref.update({"failed_attempts": intentos_globales})
                raise Exception("Contraseña incorrecta.")
            
        # SI LA CONTRASEÑA ES CORRECTA, REINICIA EL CONTADOR DE FIRESTORE
        if user_data.get("failed_attempts", 0) > 0:
            doc_ref.update({"failed_attempts": 0})

        self.current_user = {
            "uid": user_doc.id,
            "email": user_data["email"],
            "name": user_data.get("name", "Estudiante"),
            "idToken": None 
        }
        return self.current_user

    def logout_user(self):
        self.current_user = None