#!/usr/bin/env python3
"""Dart analyze check for changed files. (ADR-020)"""
import os
import subprocess
import sys
import re
from pathlib import Path

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
    
    # Run from repo root
    base_dir = Path(__file__).parent.parent.parent
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
        
        # Robust count: look for lines that contain ' • ' OR start with '  error', '  warning', '  info'
        # Also skip the 'Analyzing...' and summary lines
        lines = issues_text.splitlines()
        issue_lines = []
        for line in lines:
            if " • " in line or re.match(r"^\s+(error|warning|info|lint) ", line.lower()):
                issue_lines.append(line.strip())
        
        return passed, len(issue_lines), issues_text
    except Exception as e:
        return False, 1, str(e)

def run_check():
    """Main entry point for post_flight.py."""
    files = get_changed_dart_files()
    if not files:
        print("  SKIP: dart_analyze_changed (no changed dart files)")
        return True, 0, ""

    print(f"  Running dart analyze on {len(files)} changed files...")
    passed, count, text = run_analyze(files)
    if passed:
        print(f"  PASS: dart_analyze_changed (0 issues)")
        return True, 0, text
    else:
        # If count is 0 but passed is False, we failed to parse but dart returned non-zero
        effective_count = count if count > 0 else 1
        print(f"  FAIL: dart_analyze_changed ({effective_count} issues found)")
        
        # Extract issues for display
        display_lines = []
        for line in text.splitlines():
            if " • " in line or re.match(r"^\s+(error|warning|info|lint) ", line.lower()):
                display_lines.append(line.strip())
        
        if not display_lines and text.strip():
            # Fallback to first non-empty lines if parsing failed
            display_lines = [l.strip() for l in text.splitlines() if l.strip() and "Analyzing" not in l][:3]

        for l in display_lines[:3]:
            print(f"    {l}")
            
        return False, effective_count, text

if __name__ == "__main__":
    passed, _, _ = run_check()
    sys.exit(0 if passed else 1)
