#!/usr/bin/env python3
"""Post-flight check: Verify live site matches current iteration."""
import os, sys, requests, argparse

def run_check(iteration=None):
    if not iteration:
        iteration = os.environ.get('IAO_ITERATION', 'unknown')
        
    url = "https://kylejeromethompson.com/claw3d.html"
    try:
        r = requests.get(url, timeout=15)
        if r.status_code != 200:
            print(f"  FAIL: deployed_iteration_matches (HTTP {r.status_code})")
            return False
            
        content = r.text
        # Look for the exact iteration string (e.g. v10.65)
        if iteration in content:
            print(f"  PASS: deployed_iteration_matches (live site matches {iteration})")
            return True
        else:
            # Try to find what IS deployed
            import re
            m = re.search(r'PCB Architecture (v\d+\.\d+)', content)
            deployed = m.group(1) if m else "unknown"
            print(f"  FAIL: deployed_iteration_matches (live={deployed}, expected={iteration})")
            return False
    except Exception as e:
        print(f"  FAIL: deployed_iteration_matches (error: {e})")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("iteration", nargs="?", default=os.environ.get('IAO_ITERATION'))
    args = parser.parse_args()
    success = run_check(args.iteration)
    sys.exit(0 if success else 1)
