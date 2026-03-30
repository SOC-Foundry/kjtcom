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

                # Merge logic: Fetch existing doc and merge arrays
                doc_ref = db.collection("locations").document(doc_id)
                doc_snap = doc_ref.get()

                if doc_snap.exists:
                    existing = doc_snap.to_dict()
                    # Merge arrays
                    for array_field in ["t_any_names", "t_any_countries", "t_any_regions", 
                                       "t_any_cities", "t_any_keywords", "t_any_urls",
                                       "t_any_coordinates", "t_any_geohashes"]:
                        if array_field in entity and array_field in existing:
                            if array_field == "t_any_coordinates":
                                # Merge list of dicts by string representation or specific fields
                                combined = existing[array_field] + entity[array_field]
                                unique = []
                                seen = set()
                                for item in combined:
                                    # Create a stable key for the coordinate dict
                                    key = f"{item.get('lat')}:{item.get('lon')}"
                                    if key not in seen:
                                        unique.append(item)
                                        seen.add(key)
                                entity[array_field] = unique
                            else:
                                # Combine and unique for list of strings
                                merged = list(set(existing[array_field] + entity[array_field]))
                                entity[array_field] = sorted(merged)
                    
                    # Special merge for source.visits if both exist
                    if "source" in entity and "visits" in entity["source"]:
                        existing_source = existing.get("source", {})
                        existing_visits = existing_source.get("visits", [])
                        new_visits = entity["source"]["visits"]
                        # Match on video_id to avoid double-adding same visit
                        seen_video_ids = {v["video_id"] for v in existing_visits if "video_id" in v}
                        for nv in new_visits:
                            if nv.get("video_id") not in seen_video_ids:
                                existing_visits.append(nv)
                        entity["source"]["visits"] = existing_visits

                doc_ref.set(entity)
                total_docs += 1
                print(f"  Loaded: {doc_id}")

        checkpoint.mark_done(file_id)
        count += 1

    # Update pipeline registry from pipeline.json
    from datetime import datetime, timezone
    base = base if 'base' in dir() else os.path.dirname(os.path.dirname(__file__))
    pipeline_json_path = os.path.join(base, "config", args.pipeline, "pipeline.json")
    with open(pipeline_json_path) as pf:
        pipeline_meta = json.load(pf)
    
    # Get true entity count from Firestore
    actual_count = len(list(db.collection("locations").where("t_log_type", "==", args.pipeline).stream()))
    
    db.collection("pipelines").document(args.pipeline).set({
        "display_name": pipeline_meta.get("display_name", args.pipeline),
        "host": pipeline_meta.get("host", ""),
        "source_network": pipeline_meta.get("source_network", ""),
        "source_url": pipeline_meta.get("source_url", pipeline_meta.get("playlist_url", "")),
        "video_count": pipeline_meta.get("video_count", 0),
        "entity_count": actual_count,
        "entity_type": pipeline_meta.get("entity_type", ""),
        "icon": pipeline_meta.get("icon", ""),
        "color": pipeline_meta.get("color", ""),
        "t_schema_version": pipeline_meta.get("t_schema_version", 1),
        "last_run": datetime.now(timezone.utc).isoformat(),
    }, merge=True)

    print(f"Loaded {count} files, {total_docs} documents to {args.database}. Total unique entities: {actual_count}")


if __name__ == "__main__":
    main()
