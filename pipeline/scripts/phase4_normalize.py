"""Phase 4: Normalize extracted entities with Thompson Schema.

THIS IS THE KEY SCRIPT - Thompson Schema normalization.

Input: pipeline/data/{pipeline}/extracted/*.json
       pipeline/config/{pipeline}/schema.json
Output: pipeline/data/{pipeline}/normalized/*.jsonl
Logic: Read schema.json indicators, populate all t_any_* fields.
"""

import argparse
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from scripts.utils.checkpoint import Checkpoint
from scripts.utils.thompson_schema import normalize_entity


def main():
    parser = argparse.ArgumentParser(description="Normalize entities with Thompson Schema")
    parser.add_argument("--pipeline", required=True, help="Pipeline ID")
    parser.add_argument("--limit", type=int, default=0, help="Max files to normalize (0=all)")
    args = parser.parse_args()

    base = os.path.dirname(os.path.dirname(__file__))
    config_dir = os.path.join(base, "config", args.pipeline)
    extracted_dir = os.path.join(base, "data", args.pipeline, "extracted")
    output_dir = os.path.join(base, "data", args.pipeline, "normalized")
    os.makedirs(output_dir, exist_ok=True)

    # Load schema
    schema_path = os.path.join(config_dir, "schema.json")
    with open(schema_path) as f:
        schema = json.load(f)

    checkpoint = Checkpoint(args.pipeline, "normalize")

    extracted_files = sorted(glob.glob(os.path.join(extracted_dir, "*.json")))
    total_entities = 0
    count = 0

    for extracted_path in extracted_files:
        video_id = os.path.splitext(os.path.basename(extracted_path))[0]
        if checkpoint.is_done(video_id):
            continue

        if args.limit and count >= args.limit:
            break

        with open(extracted_path) as f:
            entities = json.load(f)

        if not isinstance(entities, list):
            entities = [entities]

        output_path = os.path.join(output_dir, f"{video_id}.jsonl")
        with open(output_path, "w") as f:
            for entity in entities:
                if not entity.get("name"):
                    print(f"  SKIP: null-name entity in {video_id}")
                    continue
                normalized = normalize_entity(entity, schema)
                f.write(json.dumps(normalized) + "\n")
                total_entities += 1

        checkpoint.mark_done(video_id)
        count += 1
        print(f"  Normalized {video_id}: {len(entities)} entities ({count})")

    print(f"Normalized {count} new files, {total_entities} entities. Total files: {checkpoint.count()}")


if __name__ == "__main__":
    main()
