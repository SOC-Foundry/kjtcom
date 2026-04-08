#!/usr/bin/env python3
"""Firestore baseline post-flight check.
Verifies entity counts across pipelines.
"""
import os
import sys

def check():
    """Verify entity count via direct Firestore check."""
    try:
        # We need to ensure we can import from scripts/ or that we have a better way
        # For now, we'll try to use the project's firestore_query script
        from iao_middleware.paths import find_project_root
        root = find_project_root()
        scripts_dir = str(root / "scripts")
        if scripts_dir not in sys.path:
            sys.path.insert(0, scripts_dir)
            
        from firestore_query import execute_query
        
        # Check all pipelines
        result_all = execute_query({}, "count")

        # Parse count from "N results found."
        count = 0
        if "results found" in result_all:
            count = int(result_all.split(" ")[0])

        threshold = 6181
        if count >= threshold:
            return ("ok", f"total_entities={count} (threshold={threshold})")
        else:
            return ("fail", f"total_entities={count} < threshold {threshold}")
    except Exception as e:
        return ("fail", f"error: {e}")

if __name__ == "__main__":
    status, msg = check()
    print(f"  {status.upper()}: firestore_baseline ({msg})")
    sys.exit(0 if status == "ok" else 1)
