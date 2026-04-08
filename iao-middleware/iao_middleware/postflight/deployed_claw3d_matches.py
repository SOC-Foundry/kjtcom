#!/usr/bin/env python3
"""Post-flight check: verify deployed claw3d.html version matches IAO_ITERATION.

Renamed from deployed_iteration_matches.py in v10.66 W10 (ADR-025).
"""
import os, sys, argparse, re, json, pathlib

def _read_deploy_paused():
    try:
        from iao_middleware.paths import find_project_root
        root = find_project_root()
        p = root / ".iao.json"
        if p.exists():
            data = json.loads(p.read_text())
            if data.get("deploy_paused"):
                return True, data.get("deploy_paused_reason", "paused")
    except Exception:
        pass
    return False, None

def run_check(iteration=None):
    paused, reason = _read_deploy_paused()
    if paused:
        print(f"  DEFERRED: deployed_claw3d_matches ({reason})")
        return "deferred"

    if not iteration:
        iteration = os.environ.get('IAO_ITERATION', 'unknown')
    url = "https://kylejeromethompson.com/claw3d.html"
    try:
        import requests
        r = requests.get(url, timeout=15)
        if r.status_code != 200:
            print(f"  FAIL: deployed_claw3d_matches (HTTP {r.status_code})")
            return False
        content = r.text
        m = re.search(r'PCB Architecture (v\d+\.\d+)', content)
        deployed = m.group(1) if m else "unknown"
        if deployed == iteration:
            print(f"  PASS: deployed_claw3d_matches (claw3d.html shows {deployed})")
            return True
        print(f"  FAIL: deployed_claw3d_matches (deployed={deployed}, expected={iteration})")
        return False
    except Exception as e:
        print(f"  FAIL: deployed_claw3d_matches (error: {e})")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("iteration", nargs="?", default=os.environ.get('IAO_ITERATION'))
    args = parser.parse_args()
    sys.exit(0 if run_check(args.iteration) else 1)
