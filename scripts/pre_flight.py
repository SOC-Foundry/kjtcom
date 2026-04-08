#!/usr/bin/env python3
"""Pre-flight environment verification (ADR-011 / G71).
Thin wrapper over iao_middleware.doctor.
Follows Pillar 6: Notes discrepancies and proceeds unless a BLOCKER fails.
"""
import os
import sys
from datetime import datetime
from iao_middleware.doctor import run_all

def main():
    iteration = os.environ.get("IAO_ITERATION", "unknown")
    print(f"--- PRE-FLIGHT {iteration} ({datetime.now().isoformat()}) ---")
    
    # Run preflight level checks
    results = run_all(level="preflight")
    
    # Define which checks are BLOCKERS for pre-flight
    # If not in this list, default to NOTE (non-blocking)
    BLOCKERS = {
        "project_root",
        "iao_json",
        "ollama",
        "python_deps",
        "disk",
        # Add others as needed
    }
    
    fail_count = 0
    for name, (status, msg) in results.items():
        is_blocker = name in BLOCKERS or status == "fail"
        
        if status == "ok":
            print(f"Checking {name}... PASS")
        elif status == "fail":
            if name in BLOCKERS:
                print(f"Checking {name}... BLOCKER FAIL: {msg}")
                fail_count += 1
            else:
                print(f"Checking {name}... NOTE (Discrepancy): {msg}")
        elif status == "warn":
            print(f"Checking {name}... NOTE (Discrepancy): {msg}")
        elif status == "deferred":
            print(f"Checking {name}... DEFERRED: {msg}")
            
    if fail_count > 0:
        print(f"\nPRE-FLIGHT BLOCKED: {fail_count} BLOCKER(s)")
        sys.exit(1)
        
    print("--- PRE-FLIGHT COMPLETE: PROCEEDING ---")

if __name__ == "__main__":
    main()
