import bcrypt
import logging
import os
from config.firebase_config import get_firestore_client
from google.cloud.firestore_v1.base_query import FieldFilter

# --- CONFIGURACIÓN DEL SISTEMA DE LOGS ---
if not os.path.exists('logs'):
    os.makedirs('logs')

logging.basicConfig(
    filename='logs/auth_security.log', 
    level=logging.INFO,                
    format='%(asctime)s - %(levelname)s - %(message)s', 
    datefmt='%Y-%m-%d %H:%M:%S'
)

# --- FUNCIÓN PARA ENMASCARAR CORREOS ---
def ocultar_correo(email):
    """Convierte juanperez@gmail.com en ju***z@g***.com por privacidad."""
    try:
        if "@" not in email:
            return "***@***.***"
            
        nombre, dominio = email.split('@')
        
        # Enmascarar el nombre (deja los primeros 2 y el último)
        if len(nombre) > 3:
            nombre_oculto = f"{nombre[:2]}***{nombre[-1]}"
        else:
            nombre_oculto = f"{nombre[0]}***"
            
        # Enmascarar el dominio (deja la primera letra del proveedor)
        partes_dominio = dominio.split('.')
        dominio_oculto = f"{partes_dominio[0][0]}***.{'.'.join(partes_dominio[1:])}"
        
        return f"{nombre_oculto}@{dominio_oculto}"
    except Exception:
        return "***@***.***" # Fallback por seguridad en caso de error
# ---------------------------------------

class AuthManager:
    def __init__(self):
        self.db = get_firestore_client()
        self.collection_name = "users" 
        self.current_user = None

    def register_user(self, nombre, email, password):
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
        # Usamos ocultar_correo() en el log
        logging.info(f"NUEVO REGISTRO: Usuario creado exitosamente ({ocultar_correo(email)})")
        return doc_ref.id 

    def login_user(self, email, password):
        users_ref = self.db.collection(self.collection_name)
        query = users_ref.where(filter=FieldFilter("email", "==", email)).stream()
        
        user_doc = None
        for doc in query:
            user_doc = doc
            break

        correo_seguro = ocultar_correo(email) # Variable segura para usar en todos los logs

        if not user_doc:
            logging.warning(f"INTENTO FALLIDO: Correo no registrado ({correo_seguro})")
            raise Exception("Usuario no encontrado.")

        user_data = user_doc.to_dict()
        doc_ref = users_ref.document(user_doc.id) 

        if user_data.get("is_suspended", False):
            logging.warning(f"ACCESO DENEGADO: Intento de login en cuenta SUSPENDIDA ({correo_seguro})")
            raise Exception("Tu cuenta está SUSPENDIDA. Por favor, contacta a soporte técnico.")

        password_valida = bcrypt.checkpw(
            password.encode('utf-8'), 
            user_data["password"].encode('utf-8')
        )

        if not password_valida:
            intentos_globales = user_data.get("failed_attempts", 0) + 1
            
            if intentos_globales >= 6:
                doc_ref.update({"is_suspended": True, "failed_attempts": intentos_globales})
                logging.error(f"CUENTA SUSPENDIDA: El usuario {correo_seguro} alcanzo los 6 intentos fallidos.")
                raise Exception("Has fallado 6 veces consecutivas. Tu cuenta ha sido SUSPENDIDA. Contacta a soporte técnico.")
            else:
                doc_ref.update({"failed_attempts": intentos_globales})
                logging.warning(f"PASSWORD INCORRECTO: Usuario {correo_seguro}. Intento {intentos_globales}/6")
                raise Exception("Contraseña incorrecta.")
            
        if user_data.get("failed_attempts", 0) > 0:
            doc_ref.update({"failed_attempts": 0})
            logging.info(f"CONTADOR REINICIADO: Login exitoso para {correo_seguro}")

        logging.info(f"LOGIN EXITOSO: Acceso concedido a {correo_seguro}")

        self.current_user = {
            "uid": user_doc.id,
            "email": user_data["email"],
            "name": user_data.get("name", "Estudiante"),
            "idToken": None 
        }
        return self.current_user

    def logout_user(self):
        if self.current_user:
            correo_seguro = ocultar_correo(self.current_user['email'])
            logging.info(f"LOGOUT: El usuario {correo_seguro} cerro sesion.")
        self.current_user = None