"""Checkpoint/resume support for pipeline stages.

Each stage writes a checkpoint file after processing each item.
On resume, already-processed items are skipped.
"""

import json
import os


class Checkpoint:
    """Track processed items for resume support."""

    def __init__(self, pipeline_id: str, stage: str):
        self.path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "data", pipeline_id, f".checkpoint_{stage}.json"
        )
        self.processed: set[str] = set()
        self._load()

    def _load(self):
        if os.path.exists(self.path):
            with open(self.path) as f:
                data = json.load(f)
                self.processed = set(data.get("processed", []))

    def save(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w") as f:
            json.dump({"processed": sorted(self.processed)}, f)

    def is_done(self, item_id: str) -> bool:
        return item_id in self.processed

    def mark_done(self, item_id: str):
        self.processed.add(item_id)
        self.save()

    def count(self) -> int:
        return len(self.processed)
