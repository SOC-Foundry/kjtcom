"""Fix CalGold t_any_shows casing.

Reads all CalGold entities from production, lowercases their
t_any_shows values, and writes back. Follows the same batch-write
+ dry-run pattern as backfill_schema_v3.py.
"""

import argparse
import sys

from google.cloud import firestore


def main():
    parser = argparse.ArgumentParser(
        description="Lowercase t_any_shows for CalGold entities"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print changes without writing to Firestore"
    )
    parser.add_argument(
        "--limit", type=int, default=0,
        help="Limit number of entities to process (0 = all)"
    )
    args = parser.parse_args()

    db = firestore.Client()
    col = db.collection("locations")

    query = col.where("t_log_type", "==", "calgold")
    docs = query.stream()

    updates = []
    skipped = 0

    for doc in docs:
        data = doc.to_dict()
        shows = data.get("t_any_shows", [])
        if not isinstance(shows, list):
            continue

        lowered = [s.lower() if isinstance(s, str) else s for s in shows]

        if lowered == shows:
            skipped += 1
            continue

        updates.append((doc.reference, shows, lowered))

        if args.limit and len(updates) >= args.limit:
            break

    print(f"CalGold entities scanned. Need update: {len(updates)}, already lowercase: {skipped}")

    if not updates:
        print("Nothing to update.")
        return

    if args.dry_run:
        for ref, old, new in updates[:10]:
            print(f"  [DRY-RUN] {ref.id}: {old} -> {new}")
        if len(updates) > 10:
            print(f"  ... and {len(updates) - 10} more")
        return

    # Batch write (max 500 per batch)
    batch_size = 500
    total_written = 0

    for i in range(0, len(updates), batch_size):
        batch = db.batch()
        chunk = updates[i : i + batch_size]
        for ref, _, lowered in chunk:
            batch.update(ref, {"t_any_shows": lowered})
        batch.commit()
        total_written += len(chunk)
        print(f"  Batch committed: {total_written}/{len(updates)}")

    print(f"Done. Updated {total_written} entities.")


if __name__ == "__main__":
    main()
