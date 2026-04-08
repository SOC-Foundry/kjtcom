#!/usr/bin/env python3
"""Artifact enforcement post-flight check. (G61, ADR-019)"""
import os
from pathlib import Path

def check(iteration=None):
    """G61 check: iteration MUST have build, report, and context artifacts on disk."""
    if not iteration:
        iteration = os.environ.get("IAO_ITERATION", "unknown")
        
    from iao.paths import find_project_root
    try:
        base_dir = find_project_root()
    except Exception:
        base_dir = Path.cwd()
        
    failures = []
    for atype in ["build", "report", "context"]:
        path = base_dir / "docs" / f"kjtcom-{atype}-{iteration}.md"
        if not path.exists():
            # Check drafts as well
            draft_path = base_dir / "docs" / "drafts" / f"kjtcom-{atype}-{iteration}.md"
            if draft_path.exists():
                continue
            failures.append(f"{atype}_artifact missing")
            continue
            
        size = path.stat().st_size
        threshold = 100000 if atype == "context" else 100
        if size < threshold:
            failures.append(f"{atype}_artifact too small ({size} bytes)")
            
    if failures:
        return ("fail", ", ".join(failures))
    return ("ok", "all 3 artifacts present and valid size")

if __name__ == "__main__":
    status, msg = check()
    print(f"  {status.upper()}: artifacts_present ({msg})")
    import sys
    sys.exit(0 if status == "ok" else 1)
