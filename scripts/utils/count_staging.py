import firebase_admin
from firebase_admin import credentials, firestore
import os

sa_path = os.path.expanduser("~/.config/gcloud/kjtcom-sa.json")
cred = credentials.Certificate(sa_path)
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

# Connect to staging database
db = firestore.client(database_id="staging")
docs = db.collection("locations").where("t_log_type", "==", "bourdain").stream()
count = sum(1 for _ in docs)
print(f"Bourdain entities in staging: {count}")
