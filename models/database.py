import uuid
from google.cloud import firestore
from config.firebase_config import get_firestore_client
from google.cloud.firestore_v1.base_query import FieldFilter

class DatabaseManager:
    def __init__(self):
        # Obtenemos el cliente de Firestore usando nuestra configuración
        self.db = get_firestore_client()
        self.collection_name = "tasks"

    def create_task(self, user_id, title, description, due_date, image_url=""):
        """Crea una nueva tarea en Firestore vinculada al UID del usuario."""
        task_data = {
            "user_id": user_id,
            "title": title,
            "description": description,
            "due_date": due_date,
            "image_url": image_url,
            "status": "pendiente",
            "created_at": firestore.SERVER_TIMESTAMP
        }

        nuevo_id = f"EduTask_{uuid.uuid4()}"
        
        self.db.collection(self.collection_name).document(nuevo_id).set(task_data)
        
        return nuevo_id

    def get_user_tasks(self, uid):
        """Obtiene solo las tareas que le pertenecen al usuario actual."""
        tasks_ref = self.db.collection(self.collection_name)
        
        query = tasks_ref.where(filter=FieldFilter("user_id", "==", uid))
        docs = query.stream()
        
        tasks = []
        for doc in docs:
            task_dict = doc.to_dict()
            # Guardamos el ID del documento dentro del diccionario para poder editarlo o borrarlo después
            task_dict["id"] = doc.id 
            tasks.append(task_dict)
            
        return tasks

    def update_task_status(self, task_id, new_status):
        """Actualiza el estado de una tarea (ej. de 'pendiente' a 'completada')."""
        doc_ref = self.db.collection(self.collection_name).document(task_id)
        doc_ref.update({"status": new_status})

    def delete_task(self, task_id):
        """Elimina permanentemente una tarea de Firestore."""
        doc_ref = self.db.collection(self.collection_name).document(task_id)
        doc_ref.delete()

    def update_task(self, task_id, updated_data):
        """Actualiza múltiples campos de una tarea existente en Firestore."""
        doc_ref = self.db.collection(self.collection_name).document(task_id)
        doc_ref.update(updated_data)