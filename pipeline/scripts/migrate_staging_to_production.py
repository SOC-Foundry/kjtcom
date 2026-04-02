#!/usr/bin/env python3
"""Copy CalGold + RickSteves entities from kjtcom staging to production.

Reads all documents from the staging database's locations collection
and writes them to the production (default) database's locations collection.
No transformation - direct field copy. Batch writes (500 per batch).

Usage:
    python3 pipeline/scripts/migrate_staging_to_production.py
"""

import os
import sys

import firebase_admin
from firebase_admin import credentials, firestore


def main():
    kjtcom_sa = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "")
    if not kjtcom_sa:
        print("ERROR: GOOGLE_APPLICATION_CREDENTIALS not set")
        sys.exit(1)

    print("[1/3] Connecting to kjtcom Firestore (staging + production)...")
    cred = credentials.Certificate(kjtcom_sa)
    app = firebase_admin.initialize_app(cred, {"projectId": "kjtcom-c78cd"})

    staging_db = firestore.client(app=app, database_id="staging")
    prod_db = firestore.client(app=app)

    # --- Read all documents from staging ---
    print("[2/3] Reading from staging 'locations' collection...")
    docs = list(staging_db.collection("locations").stream())
    print(f"  Read {len(docs)} documents from staging")

    if not docs:
        print("No documents found in staging. Exiting.")
        return

    # Count by pipeline
    pipeline_counts = {}
    schema_counts = {}

    # --- Batch write to production ---
    print("[3/3] Writing to production (default) database...")
    batch_size = 500
    written = 0

    for start in range(0, len(docs), batch_size):
        batch = prod_db.batch()
        chunk = docs[start:start + batch_size]
        for doc in chunk:
            data = doc.to_dict()
            doc_ref = prod_db.collection("locations").document(doc.id)
            batch.set(doc_ref, data)

            # Track counts
            lt = data.get("t_log_type", "unknown")
            pipeline_counts[lt] = pipeline_counts.get(lt, 0) + 1
            sv = data.get("t_schema_version", "unknown")
            schema_counts[sv] = schema_counts.get(sv, 0) + 1

        batch.commit()
        written += len(chunk)
        print(f"  Batch committed: {written}/{len(docs)}")

    # --- Summary ---
    print(f"\n{'='*60}")
    print(f"STAGING -> PRODUCTION COPY COMPLETE")
    print(f"{'='*60}")
    print(f"  Total copied: {written}")
    print(f"\n  By pipeline (t_log_type):")
    for lt, count in sorted(pipeline_counts.items()):
        print(f"    {lt:20s} {count}")
    print(f"\n  By schema version:")
    for sv, count in sorted(schema_counts.items()):
        print(f"    v{sv:<20} {count}")


if __name__ == "__main__":
    main()
