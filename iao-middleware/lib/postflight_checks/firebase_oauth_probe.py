#!/usr/bin/env python3
"""Firebase dual-path probe (ADR-023 / G53 / G95).
Verifies connectivity via Service Account, CI Token, and User OAuth.
"""
import os, subprocess, sys

def check_sa():
    sa_path = os.path.expanduser("~/.config/gcloud/kjtcom-sa.json")
    if not os.path.exists(sa_path):
        return False, "SA file missing"
    
    env = os.environ.copy()
    env["GOOGLE_APPLICATION_CREDENTIALS"] = sa_path
    try:
        # Try a command that requires SA permissions
        r = subprocess.run(["gcloud", "auth", "list", "--format=json"], 
                           capture_output=True, text=True, timeout=15, env=env)
        return r.returncode == 0, "gcloud auth ok" if r.returncode == 0 else f"gcloud fail: {r.stderr[:50]}"
    except Exception as e:
        return False, str(e)

def check_ci_token():
    token_path = os.path.expanduser("~/.config/firebase-ci-token.txt")
    if not os.path.exists(token_path):
        return False, "CI token file missing"
    
    try:
        with open(token_path) as f:
            token = f.read().strip()
        if not token:
            return False, "CI token empty"
            
        r = subprocess.run(["npx", "-y", "firebase-tools", "projects:list", "--token", token, "--json"],
                           capture_output=True, text=True, timeout=30)
        return r.returncode == 0, "token ok" if r.returncode == 0 else "token invalid/expired"
    except Exception as e:
        return False, str(e)

def check_oauth():
    # bare firebase projects:list uses whatever is in ~/.config/configstore/firebase-tools.json
    try:
        r = subprocess.run(["npx", "-y", "firebase-tools", "projects:list", "--json"],
                           capture_output=True, text=True, timeout=30)
        return r.returncode == 0, "oauth ok" if r.returncode == 0 else "oauth expired/missing"
    except Exception as e:
        return False, str(e)

def run_probe():
    print("Firebase Connectivity Probe (G95):")
    
    sa_ok, sa_msg = check_sa()
    print(f"  {'PASS' if sa_ok else 'FAIL'}: Service Account ({sa_msg})")
    
    ci_ok, ci_msg = check_ci_token()
    print(f"  {'PASS' if ci_ok else 'FAIL'}: CI Token ({ci_msg})")
    
    oa_ok, oa_msg = check_oauth()
    print(f"  {'PASS' if oa_ok else 'FAIL'}: User OAuth ({oa_msg})")
    
    # At least one must pass for operational readiness
    # Both SA and CI/OAuth should ideally pass
    return sa_ok or ci_ok or oa_ok

if __name__ == "__main__":
    success = run_probe()
    sys.exit(0 if success else 1)
