import os
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

load_dotenv()

# Tu Web API Key de la consola de Firebase
FIREBASE_WEB_API_KEY = os.getenv("FIREBASE_WEB_API_KEY")

# Inicialización de Firebase Admin para Firestore
def get_firestore_client():
    # Verifica si la app ya fue inicializada para no duplicarla
    if not firebase_admin._apps:
        cred = credentials.Certificate("serviceAccountKey.json")
        firebase_admin.initialize_app(cred)
    
    return firestore.client()