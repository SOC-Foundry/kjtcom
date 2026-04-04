"""Comprehensive lowercase fix for ALL t_any_* string values.

Reads ALL entities from production, lowercases every string value
in every t_any_* array field, and writes back. Permanent G36 resolution.
"""

import argparse
import sys

from google.cloud import firestore


def main():
    parser = argparse.ArgumentParser(
        description="Lowercase ALL t_any_* string values across all entities"
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

    docs = col.stream()

    updates = []
    scanned = 0
    skipped = 0

    for doc in docs:
        scanned += 1
        data = doc.to_dict()
        changed_fields = {}

        for key, val in data.items():
            if not key.startswith("t_any_"):
                continue
            if not isinstance(val, list):
                continue

            lowered = []
            field_changed = False
            for item in val:
                if isinstance(item, str):
                    low = item.lower()
                    lowered.append(low)
                    if low != item:
                        field_changed = True
                else:
                    # Non-string items (dicts like coordinates) pass through
                    lowered.append(item)

            if field_changed:
                changed_fields[key] = (val, lowered)

        if changed_fields:
            updates.append((doc.reference, changed_fields))
        else:
            skipped += 1

        if args.limit and len(updates) >= args.limit:
            break

    print(f"Scanned: {scanned}, need update: {len(updates)}, already lowercase: {skipped}")

    if not updates:
        print("Nothing to update.")
        return

    if args.dry_run:
        for ref, fields in updates[:10]:
            print(f"  [DRY-RUN] {ref.id}:")
            for field, (old, new) in fields.items():
                # Show only changed values
                changed = [(o, n) for o, n in zip(old, new) if isinstance(o, str) and o != n]
                for o, n in changed[:3]:
                    print(f"    {field}: \"{o}\" -> \"{n}\"")
                if len(changed) > 3:
                    print(f"    ... and {len(changed) - 3} more in {field}")
        if len(updates) > 10:
            print(f"  ... and {len(updates) - 10} more entities")
        return

    # Batch write (max 500 per batch)
    batch_size = 500
    total_written = 0

    for i in range(0, len(updates), batch_size):
        batch = db.batch()
        chunk = updates[i : i + batch_size]
        for ref, fields in chunk:
            update_data = {field: lowered for field, (_, lowered) in fields.items()}
            batch.update(ref, update_data)
        batch.commit()
        total_written += len(chunk)
        print(f"  Batch committed: {total_written}/{len(updates)}")

    print(f"Done. Updated {total_written} entities across {scanned} scanned.")


if __name__ == "__main__":
    main()
