"""Phase 7: Load enriched JSONL into Cloud Firestore.

Input: pipeline/data/{pipeline}/enriched/*.jsonl
Target: --database staging (default) or --database "(default)"
Creates: documents in locations/ collection, updates pipelines/ registry.
"""

import argparse
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from scripts.utils.checkpoint import Checkpoint


def main():
    parser = argparse.ArgumentParser(description="Load entities into Firestore")
    parser.add_argument("--pipeline", required=True, help="Pipeline ID")
    parser.add_argument("--database", default="staging", help="Firestore database ID")
    parser.add_argument("--input", default=None, help="Specific JSONL file to load (overrides data dir)")
    parser.add_argument("--limit", type=int, default=0, help="Max files to load (0=all)")
    args = parser.parse_args()

    import firebase_admin
    from firebase_admin import credentials, firestore

    # Initialize Firebase Admin
    if not firebase_admin._apps:
        cred_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        if cred_path and os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
        else:
            firebase_admin.initialize_app()

    db = firestore.client(database_id=args.database)

    # Load from specific file or data directory
    if args.input:
        files = [args.input]
    else:
        base = os.path.dirname(os.path.dirname(__file__))
        enriched_dir = os.path.join(base, "data", args.pipeline, "enriched")
        files = sorted(glob.glob(os.path.join(enriched_dir, "*.jsonl")))

    checkpoint = Checkpoint(args.pipeline, "load")
    total_docs = 0
    count = 0

    for filepath in files:
        file_id = os.path.splitext(os.path.basename(filepath))[0]
        if checkpoint.is_done(file_id):
            continue

        if args.limit and count >= args.limit:
            break

        with open(filepath) as f:
            for line in f:
                entity = json.loads(line)
                doc_id = entity.get("t_row_id", file_id)

                db.collection("locations").document(doc_id).set(entity)
                total_docs += 1
                print(f"  Loaded: {doc_id}")

        checkpoint.mark_done(file_id)
        count += 1

    # Update pipeline registry
    from datetime import datetime, timezone
    db.collection("pipelines").document(args.pipeline).set({
        "display_name": "California's Gold",
        "host": "Huell Howser",
        "source_network": "PBS SoCal / KCET",
        "playlist_url": "https://www.youtube.com/playlist?list=PLr7fFk3JB5ic-nEyrqLj6MGDox5DO8oMl",
        "video_count": 431,
        "entity_count": total_docs,
        "entity_type": "landmark",
        "icon": "castle",
        "color": "#C4A000",
        "t_schema_version": 1,
        "last_run": datetime.now(timezone.utc).isoformat(),
    }, merge=True)

    print(f"Loaded {count} files, {total_docs} documents to {args.database}. Total: {checkpoint.count()}")


if __name__ == "__main__":
    main()
