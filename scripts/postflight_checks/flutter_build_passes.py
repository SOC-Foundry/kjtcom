#!/usr/bin/env python3
"""Build gatekeeper post-flight check. (ADR-020)"""
import os
import subprocess
import sys
from pathlib import Path

def is_app_touched():
    """Returns True if app/ has changes in git or IAO_TOUCHED_APP is set."""
    if os.environ.get("IAO_TOUCHED_APP") == "1":
        return True
    try:
        # Check git status for app/ directory
        r = subprocess.run(
            ["git", "status", "--short", "app/"],
            capture_output=True, text=True, check=True
        )
        return len(r.stdout.strip()) > 0
    except Exception:
        # Fallback to True if git fails for some reason, safer to check
        return True

def run_build():
    """Runs flutter build web --release and returns (passed, log_text, build_size)."""
    base_dir = Path(__file__).parent.parent.parent
    app_dir = base_dir / "app"
    log_path = "/tmp/v10.65-flutter-build.log"
    
    print(f"  Running flutter build web --release in {app_dir}...")
    try:
        # Using bash -c for compatibility if needed, though subprocess.run usually fine
        with open(log_path, "w") as f:
            r = subprocess.run(
                ["flutter", "build", "web", "--release"],
                cwd=app_dir,
                stdout=f,
                stderr=subprocess.STDOUT,
                text=True,
                timeout=300 # 5 min timeout
            )
        
        with open(log_path, "r") as f:
            log_text = f.read()
            
        if r.returncode == 0:
            # Success, measure build size
            build_web_dir = app_dir / "build" / "web"
            size_bytes = sum(f.stat().st_size for f in build_web_dir.glob('**/*') if f.is_file())
            return True, log_text, size_bytes
        else:
            return False, log_text, 0
    except Exception as e:
        return False, str(e), 0

def get_error_summary(log_text):
    """Extracts first 3 Error: lines with file:line:column."""
    errors = []
    for line in log_text.splitlines():
        if "Error:" in line or "error:" in line or ".dart:" in line:
            # Try to catch file:line:column pattern
            if ".dart:" in line:
                errors.append(line.strip())
        if len(errors) >= 3:
            break
    return errors

def run_check():
    """Main entry point for post_flight.py."""
    if not is_app_touched():
        print("  SKIP: flutter_build_passes (app/ not touched)")
        return None, ""

    passed, log_text, size = run_build()
    if passed:
        size_mb = size / (1024 * 1024)
        print(f"  PASS: flutter_build_passes (build size: {size_mb:.2f} MB)")
        return True, log_text
    else:
        errors = get_error_summary(log_text)
        print(f"  FAIL: flutter_build_passes")
        for err in errors:
            print(f"    {err}")
        return False, log_text

if __name__ == "__main__":
    passed, _ = run_check()
    sys.exit(0 if passed is not False else 1)
