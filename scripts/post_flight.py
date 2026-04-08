#!/usr/bin/env python3
"""Post-flight verification for kjtcom iterations.
Thin wrapper over iao.doctor.
"""
import os
import sys
from iao.doctor import run_all

def main():
    iteration = sys.argv[1] if len(sys.argv) > 1 else os.environ.get('IAO_ITERATION', 'unknown')
    print(f"Post-flight verification for {iteration}:")
    print("=" * 40)

    # Run postflight level checks
    results = run_all(level="postflight")
    
    fail_count = 0
    for name, (status, msg) in results.items():
        tag = {"ok": "[ok]", "warn": "[WARN]", "fail": "[FAIL]", "deferred": "[DEFERRED]"}[status]
        print(f"{tag:10} {name:25}: {msg}")
        if status == "fail":
            fail_count += 1

    # Plan requirement: Build gatekeeper check is the specific gate
    build_status, build_msg = results.get("build_gatekeeper", ("fail", "check missing"))
    if build_status == "ok":
        print("\nBUILD GATEKEEPER: PASS")
    else:
        print(f"\nBUILD GATEKEEPER: {build_status.upper()}")

    # Summary
    total = len(results)
    passed = sum(1 for s, _ in results.values() if s in ("ok", "deferred"))
    
    print("=" * 40)
    print(f"Post-flight: {passed}/{total} passed or deferred")

    if fail_count > 0:
        print("WARNING: Post-flight verification FAILED. Do NOT mark iteration complete.")
        sys.exit(1)
        
    print("Post-flight: clean")
    sys.exit(0)

if __name__ == '__main__':
    main()
