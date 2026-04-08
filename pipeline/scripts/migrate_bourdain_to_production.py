#!/usr/bin/env python3
"""Migrate Bourdain entities from staging to production Firestore."""
import os, sys, firebase_admin
from firebase_admin import credentials, firestore

def main():
    sa_path = os.path.expanduser("~/.config/gcloud/kjtcom-sa.json")
    if not os.path.exists(sa_path):
        print("ERROR: Service account not found")
        sys.exit(1)

    cred = credentials.Certificate(sa_path)
    app = firebase_admin.initialize_app(cred, {"projectId": "kjtcom-c78cd"})

    staging_db = firestore.client(app=app, database_id="staging")
    prod_db = firestore.client(app=app)

    print("Reading 'bourdain' entities from staging...")
    # Use keyword filter for newer SDK compatibility
    from google.cloud.firestore_v1.base_query import FieldFilter
    docs = list(staging_db.collection("locations").where(filter=FieldFilter("t_log_type", "==", "bourdain")).stream())
    
    print(f"Found {len(docs)} documents in staging.")
    if not docs:
        print("Nothing to migrate.")
        return

    print("Writing to production (default) database...")
    batch_size = 500
    written = 0

    for i in range(0, len(docs), batch_size):
        batch = prod_db.batch()
        chunk = docs[i:i + batch_size]
        for doc in chunk:
            data = doc.to_dict()
            doc_ref = prod_db.collection("locations").document(doc.id)
            batch.set(doc_ref, data)
        batch.commit()
        written += len(chunk)
        print(f"  Batch committed: {written}/{len(docs)}")

    print(f"Migration complete. {written} Bourdain entities copied to production.")

if __name__ == "__main__":
    main()
