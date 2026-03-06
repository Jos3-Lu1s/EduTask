import bcrypt
from config.firebase_config import get_firestore_client
from google.cloud.firestore_v1.base_query import FieldFilter

class AuthManager:
    def __init__(self):
        self.db = get_firestore_client()
        self.collection_name = "users" 
        self.current_user = None

    def register_user(self, email, password):
        """Registra un nuevo usuario en Firestore encriptando su contraseña."""
        users_ref = self.db.collection(self.collection_name)
        
        # Verificar si el correo ya existe
        query = users_ref.where(filter=FieldFilter("email", "==", email)).stream()
        if any(query):
            raise Exception("Este correo electrónico ya está registrado.")

        # Hashear la contraseña
        # gensalt() añade un valor aleatorio para hacer el hash único
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

        # Guardar en Firestore
        user_data = {
            "email": email,
            "password": hashed_password.decode('utf-8') # Guardar el hash como string
        }
        
        update_time, doc_ref = users_ref.add(user_data)
        return doc_ref.id # Retorna el ID del documento (UID)

    def login_user(self, email, password):
        """Inicia sesión buscando en Firestore y verificando el hash."""
        users_ref = self.db.collection(self.collection_name)
        
        # Buscar al usuario por correo
        query = users_ref.where(filter=FieldFilter("email", "==", email)).stream()
        
        user_doc = None
        for doc in query:
            user_doc = doc
            break

        if not user_doc:
            raise Exception("Usuario no encontrado.")

        user_data = user_doc.to_dict()

        # Verificar que la contraseña coincida con el hash guardado
        password_valida = bcrypt.checkpw(
            password.encode('utf-8'), 
            user_data["password"].encode('utf-8')
        )

        if not password_valida:
            raise Exception("Contraseña incorrecta.")
            
        self.current_user = {
            "uid": user_doc.id,
            "email": user_data["email"],
            "idToken": None 
        }
        return self.current_user

    def logout_user(self):
        """Limpia la sesión actual."""
        self.current_user = None