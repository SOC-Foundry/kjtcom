#!/usr/bin/env python3
"""deployed_flutter_matches.py - verify Flutter app deploy matches IAO_ITERATION (v10.66 W10)."""
import os, re, sys, urllib.request, json, pathlib

def _read_deploy_paused():
    try:
        from iao_middleware.paths import find_project_root
        root = find_project_root()
        p = root / ".iao.json"
        if p.exists():
            data = json.loads(p.read_text())
            if data.get("deploy_paused"):
                return True, data.get("deploy_paused_since", "unknown")
    except Exception:
        pass
    return False, None

def check():
    paused, since = _read_deploy_paused()
    if paused:
        return ("deferred", f"deploy paused since {since}; matching iteration not expected")

    url = "https://kylejeromethompson.com/"
    expected = os.environ.get("IAO_ITERATION", "").strip()
    if not expected:
        return False, "IAO_ITERATION env var not set"
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
    except Exception as e:
        return False, f"fetch failed: {e}"
    m = re.search(r'IAO_ITERATION\s*[=:]\s*["\']?(v[\d.]+)', html)
    if not m:
        m = re.search(r'(v10\.\d+)', html)
        if not m:
            return False, "could not find IAO_ITERATION in page source"
    actual = m.group(1)
    if actual != expected:
        return False, f"deployed={actual}, expected={expected}"
    return True, f"deployed={actual}"

if __name__ == "__main__":
    ok, msg = check()
    print(f"  {'PASS' if ok else 'FAIL'}: deployed_flutter_matches ({msg})")
    sys.exit(0 if ok else 1)
