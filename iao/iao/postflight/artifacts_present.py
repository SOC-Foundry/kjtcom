#!/usr/bin/env python3
"""Artifact enforcement post-flight check. (G61, ADR-019)"""
import os
from pathlib import Path

def check(iteration=None):
    """ADR-019/G103: Verify all 3 artifacts (build, report, bundle) are present."""
    if not iteration:
        iteration = os.environ.get("IAO_ITERATION", "unknown")
        
    from iao.paths import find_project_root
    import json
    try:
        base_dir = find_project_root()
        config_path = base_dir / ".iao.json"
        config = json.loads(config_path.read_text())
        project = config.get("project_code", "kjtcom")
        bundle_kind = config.get("bundle_format", "context")
    except Exception:
        base_dir = Path.cwd()
        project = "kjtcom"
        bundle_kind = "context"
        
    failures = []
    # Primary artifacts: build, report, bundle (base)
    for atype in ["build", "report", bundle_kind]:
        # Handle kjtcom- vs project- prefixing
        # G103: try project code prefix first
        found = False
        for prefix in [project, "kjtcom"]:
            path = base_dir / "docs" / f"{prefix}-{atype}-{iteration}.md"
            if path.exists():
                found = True
                break
            # Check drafts
            draft_path = base_dir / "docs" / "drafts" / f"{prefix}-{atype}-{iteration}.md"
            if draft_path.exists():
                path = draft_path
                found = True
                break
        
        if not found:
            failures.append(f"{atype}_artifact missing")
            continue
            
        size = path.stat().st_size
        # Thresholds: bundle must be > 100KB, others > 100 bytes
        threshold = 100000 if atype == bundle_kind else 100
        if size < threshold:
            failures.append(f"{atype}_artifact too small ({size} bytes)")
            
    if failures:
        return ("fail", ", ".join(failures))
    return ("ok", f"all 3 artifacts present ({project})")

if __name__ == "__main__":
    status, msg = check()
    print(f"  {status.upper()}: artifacts_present ({msg})")
    import sys
    sys.exit(0 if status == "ok" else 1)
