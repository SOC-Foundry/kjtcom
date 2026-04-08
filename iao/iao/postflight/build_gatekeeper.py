#!/usr/bin/env python3
"""Build gatekeeper post-flight check. (ADR-020)
Combines Dart analysis and Flutter build verification.
"""
import os
import subprocess
import sys
import re
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

def get_changed_dart_files():
    """Returns list of changed .dart files in app/."""
    try:
        r = subprocess.run(
            ["git", "status", "--short", "app/"],
            capture_output=True, text=True, check=True
        )
        files = []
        for line in r.stdout.splitlines():
            if len(line) < 4: continue
            # line is " M path/to/file.dart" or "?? path/to/file.dart"
            path_str = line[3:].strip()
            if path_str.endswith(".dart"):
                files.append(path_str)
        return files
    except Exception:
        return []

def run_analyze(files):
    """Runs dart analyze on specific files and returns (passed, issues_count, issues_text)."""
    if not files:
        return True, 0, ""
    
    # Try to find project root to run from
    from iao.paths import find_project_root
    try:
        base_dir = find_project_root()
    except Exception:
        base_dir = Path.cwd()
        
    cmd = ["dart", "analyze"] + files
    
    try:
        r = subprocess.run(
            cmd,
            cwd=base_dir,
            capture_output=True, text=True,
            timeout=60
        )
        
        passed = (r.returncode == 0)
        issues_text = r.stdout + r.stderr
        
        lines = issues_text.splitlines()
        issue_lines = []
        for line in lines:
            if " • " in line or re.match(r"^\s+(error|warning|info|lint) ", line.lower()):
                issue_lines.append(line.strip())
        
        return passed, len(issue_lines), issues_text
    except Exception as e:
        return False, 1, str(e)

def run_build():
    """Runs flutter build web --release and returns (passed, log_text, build_size)."""
    from iao.paths import find_project_root
    try:
        base_dir = find_project_root()
    except Exception:
        base_dir = Path.cwd()
        
    app_dir = base_dir / "app"
    log_path = "/tmp/v10.67-flutter-build.log"
    
    print(f"  Running flutter build web --release in {app_dir}...")
    try:
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
            if ".dart:" in line:
                errors.append(line.strip())
        if len(errors) >= 3:
            break
    return errors

def check():
    """Main entry point for doctor.py."""
    if not is_app_touched():
        return ("ok", "app/ not touched, build skipped")

    # 1. Dart Analyze
    files = get_changed_dart_files()
    if files:
        print(f"  Running dart analyze on {len(files)} changed files...")
        passed, count, text = run_analyze(files)
        if not passed:
            return ("fail", f"dart analyze found {count} issue(s)")
    
    # 2. Flutter Build
    passed, log_text, size = run_build()
    if passed:
        size_mb = size / (1024 * 1024)
        return ("ok", f"build passed ({size_mb:.2f} MB)")
    else:
        errors = get_error_summary(log_text)
        err_msg = errors[0] if errors else "unknown error"
        return ("fail", f"flutter build failed: {err_msg}")

if __name__ == "__main__":
    status, msg = check()
    print(f"  {status.upper()}: build_gatekeeper ({msg})")
    sys.exit(0 if status == "ok" else 1)
