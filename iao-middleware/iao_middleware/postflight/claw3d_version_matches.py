#!/usr/bin/env python3
"""claw3d_version_matches.py - in-repo pre-deploy check for claw3d.html version stamp (v10.66 W10, G101)."""
import os, re, sys, json
from pathlib import Path

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

def check():
    paused, reason = _read_deploy_paused()
    if paused:
        return ("deferred", f"DEFERRED: {reason}")

    expected = os.environ.get("IAO_ITERATION", "").strip()
    if not expected:
        return False, "IAO_ITERATION env var not set"
    try:
        from iao_middleware.paths import find_project_root
        project_root = find_project_root()
    except Exception:
        project_root = Path(__file__).resolve().parent.parent.parent
    claw3d = project_root / "app" / "web" / "claw3d.html"
    if not claw3d.exists():
        return False, f"{claw3d} not found"
    text = claw3d.read_text()
    m = re.search(r"PCB Architecture (v[\d.]+)", text)
    if not m:
        return False, "title string not found in claw3d.html"
    actual = m.group(1)
    if actual != expected:
        return False, f"claw3d.html shows {actual}, expected {expected}"
    return True, f"claw3d.html shows {actual}"

if __name__ == "__main__":
    ok, msg = check()
    print(f"  {'PASS' if ok else 'FAIL'}: claw3d_version_matches ({msg})")
    sys.exit(0 if ok else 1)
