import uuid
import logging
import os
from google.cloud import firestore
from config.firebase_config import get_firestore_client
from google.cloud.firestore_v1.base_query import FieldFilter

# --- CONFIGURACIÓN DEL LOGGER DE BASE DE DATOS ---
if not os.path.exists('logs'):
    os.makedirs('logs')

# Creamos un logger específico para la base de datos para no mezclarlo con el de Auth
db_logger = logging.getLogger('DatabaseLogger')
db_logger.setLevel(logging.INFO)
db_logger.propagate = False

# Evitamos duplicar registros si la clase se instancia varias veces
if not db_logger.handlers:
    file_handler = logging.FileHandler('logs/database_ops.log', encoding='utf-8')
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    file_handler.setFormatter(formatter)
    db_logger.addHandler(file_handler)
# -------------------------------------------------

class DatabaseManager:
    def __init__(self):
        self.db = get_firestore_client()
        self.collection_name = "tasks"

    def create_task(self, user_id, title, description, due_date, image_url=""):
        """Crea una nueva tarea en Firestore y lo registra."""
        task_data = {
            "user_id": user_id,
            "title": title,
            "description": description,
            "due_date": due_date,
            "image_url": image_url,
            "status": "pendiente",
            "created_at": firestore.SERVER_TIMESTAMP 
        }
        
        nuevo_id = f"EduTaskTask_{uuid.uuid4()}"
        
        self.db.collection(self.collection_name).document(nuevo_id).set(task_data)
        
        # LOG DE CREACIÓN
        db_logger.info(f"CREATE: Tarea guardada. ID: {nuevo_id} | Usuario: {user_id}")
        return nuevo_id

    def get_user_tasks(self, user_id):
        """Recupera todas las tareas del usuario."""
        query = self.db.collection(self.collection_name).where(filter=FieldFilter("user_id", "==", user_id)).stream()
        
        tareas = []
        for doc in query:
            t_data = doc.to_dict()
            t_data['id'] = doc.id
            tareas.append(t_data)
            
        # db_logger.info(f"READ: Se leyeron {len(tareas)} tareas para el Usuario: {user_id}")
        return tareas

    def update_task_status(self, task_id, status):
        """Actualiza solo el estado de la tarea (Ej. a 'completada')."""
        doc_ref = self.db.collection(self.collection_name).document(task_id)
        doc_ref.update({"status": status})
        
        # LOG DE ACTUALIZACIÓN RÁPIDA
        db_logger.info(f"UPDATE STATUS: Tarea {task_id} cambió su estado a '{status}'")

    def update_task(self, task_id, updated_data):
        """Actualiza múltiples campos de una tarea existente en Firestore."""
        doc_ref = self.db.collection(self.collection_name).document(task_id)
        doc_ref.update(updated_data)
        
        # LOG DE ACTUALIZACIÓN COMPLETA (Registramos qué campos se modificaron)
        campos_modificados = list(updated_data.keys())
        db_logger.info(f"UPDATE: Tarea {task_id} actualizada. Campos afectados: {campos_modificados}")

    def delete_task(self, task_id):
        """Elimina una tarea permanentemente de Firestore."""
        self.db.collection(self.collection_name).document(task_id).delete()
        
        # LOG DE ELIMINACIÓN (Usamos nivel WARNING porque es una acción destructiva)
        db_logger.warning(f"DELETE: Tarea {task_id} ha sido ELIMINADA permanentemente de la base de datos.")