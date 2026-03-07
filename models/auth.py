import bcrypt
import logging
import os
import uuid
from datetime import datetime, timedelta, timezone # Importamos manejo de tiempo
from config.firebase_config import get_firestore_client
from google.cloud.firestore_v1.base_query import FieldFilter

if not os.path.exists('logs'):
    os.makedirs('logs')

logging.basicConfig(
    filename='logs/auth_security.log', 
    level=logging.INFO,                
    format='%(asctime)s - %(levelname)s - %(message)s', 
    datefmt='%Y-%m-%d %H:%M:%S'
)

def ocultar_correo(email):
    try:
        if "@" not in email:
            return "***@***.***"
        nombre, dominio = email.split('@')
        if len(nombre) > 3:
            nombre_oculto = f"{nombre[:2]}***{nombre[-1]}"
        else:
            nombre_oculto = f"{nombre[0]}***"
        partes_dominio = dominio.split('.')
        dominio_oculto = f"{partes_dominio[0][0]}***.{'.'.join(partes_dominio[1:])}"
        return f"{nombre_oculto}@{dominio_oculto}"
    except Exception:
        return "***@***.***"

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
            "is_suspended": False,
            "locked_until": None
        }

        nuevo_id = f"EduTaskUser_{uuid.uuid4()}"
        
        users_ref.document(nuevo_id).set(user_data)
        
        logging.info(f"NUEVO REGISTRO: Usuario creado exitosamente ({ocultar_correo(email)}) con ID: {nuevo_id}")
        return nuevo_id

    def login_user(self, email, password):
        users_ref = self.db.collection(self.collection_name)
        query = users_ref.where(filter=FieldFilter("email", "==", email)).stream()
        
        user_doc = None
        for doc in query:
            user_doc = doc
            break

        correo_seguro = ocultar_correo(email)

        if not user_doc:
            logging.warning(f"INTENTO FALLIDO: Correo no registrado ({correo_seguro})")
            raise Exception("Usuario no encontrado.")

        user_data = user_doc.to_dict()
        doc_ref = users_ref.document(user_doc.id) 

        # VERIFICAR SUSPENSIÓN PERMANENTE
        if user_data.get("is_suspended", False):
            logging.warning(f"ACCESO DENEGADO: Intento de login en cuenta SUSPENDIDA ({correo_seguro})")
            raise Exception("Tu cuenta está SUSPENDIDA. Por favor, contacta a soporte técnico.")

        # VERIFICAR BLOQUEO TEMPORAL DE 1 MINUTO
        locked_until = user_data.get("locked_until")
        if locked_until:
            now = datetime.now(timezone.utc)
            if now < locked_until:
                segundos_restantes = (locked_until - now).seconds
                logging.warning(f"BLOQUEO ACTIVO: {correo_seguro} intento entrar antes de tiempo.")
                raise Exception(f"BLOQUEO_TEMPORAL:{segundos_restantes}")

        # VERIFICAR CONTRASEÑA
        password_valida = bcrypt.checkpw(
            password.encode('utf-8'), 
            user_data["password"].encode('utf-8')
        )

        if not password_valida:
            intentos = user_data.get("failed_attempts", 0) + 1
            
            if intentos >= 6:
                doc_ref.update({"is_suspended": True, "failed_attempts": intentos})
                logging.error(f"CUENTA SUSPENDIDA: El usuario {correo_seguro} alcanzó 6 intentos.")
                raise Exception("Has fallado 6 veces consecutivas. Tu cuenta ha sido SUSPENDIDA. Contacta a soporte técnico.")
            
            elif intentos == 3:
                lock_time = datetime.now(timezone.utc) + timedelta(minutes=1)
                doc_ref.update({"failed_attempts": intentos, "locked_until": lock_time})
                logging.warning(f"BLOQUEO DE 1 MINUTO APLICADO: {correo_seguro} fallo 3 veces.")
                raise Exception("BLOQUEO_TEMPORAL:60")
                
            else:
                doc_ref.update({"failed_attempts": intentos})
                logging.warning(f"CONTRASEÑA INCORRECTA: Usuario {correo_seguro}. Intento {intentos}/6")
                raise Exception(f"Contraseña incorrecta.\nLlevas {intentos} de 6 intentos.")
            
        # LOGIN EXITOSO: LIMPIAMOS TODOS LOS ERRORES
        if user_data.get("failed_attempts", 0) > 0 or user_data.get("locked_until"):
            doc_ref.update({"failed_attempts": 0, "locked_until": None})
            logging.info(f"CONTADORES REINICIADOS: Login exitoso para {correo_seguro}")

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

    def verify_password(self, password):
        """Verifica la contraseña del usuario actual para acciones sensibles."""
        if not self.current_user:
            raise Exception("No hay una sesión activa.")
            
        doc_ref = self.db.collection(self.collection_name).document(self.current_user['uid'])
        doc = doc_ref.get()
        
        if not doc.exists:
            raise Exception("El usuario no existe en la base de datos.")
            
        user_data = doc.to_dict()
        
        password_valida = bcrypt.checkpw(
            password.encode('utf-8'), 
            user_data["password"].encode('utf-8')
        )
        
        if not password_valida:
            raise Exception("Contraseña incorrecta. Acción denegada.")
            
        return True