"""Generate value_index.json for query autocomplete.

Reads all entities from production Firestore, collects distinct values
for each t_any_* array field and t_log_type, sorts alphabetically,
caps at 500 values per field, and writes to app/assets/value_index.json.
"""

import json
import os
from collections import defaultdict
from google.cloud import firestore

os.environ.setdefault(
    "GOOGLE_APPLICATION_CREDENTIALS",
    os.path.expanduser("~/.config/gcloud/kjtcom-sa.json"),
)

PROJECT_ID = "kjtcom-c78cd"
OUTPUT_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "app", "assets", "value_index.json"
)
MAX_VALUES_PER_FIELD = 500


def main():
    db = firestore.Client(project=PROJECT_ID)
    docs = db.collection("locations").stream()

    index = defaultdict(set)
    count = 0

    for doc in docs:
        count += 1
        data = doc.to_dict()
        for key, val in data.items():
            if key.startswith("t_any_") and isinstance(val, list):
                for item in val:
                    s = str(item).strip()
                    if s and not isinstance(item, dict):
                        index[key].add(s.lower())
            elif key == "t_log_type" and isinstance(val, str):
                index["t_log_type"].add(val.lower())

        if count % 1000 == 0:
            print(f"  Processed {count} entities...")

    print(f"Total entities processed: {count}")

    # Sort and cap
    result = {}
    for field in sorted(index.keys()):
        values = sorted(index[field])[:MAX_VALUES_PER_FIELD]
        result[field] = values

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"\nWrote {OUTPUT_PATH}")
    for field in sorted(result.keys()):
        print(f"  {field}: {len(result[field])} values")


if __name__ == "__main__":
    main()
