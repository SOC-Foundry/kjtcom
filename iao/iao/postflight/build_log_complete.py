#!/usr/bin/env python3
"""Build log completeness post-flight check. (ADR-022, 10.69 W3)"""
import os
import re
from pathlib import Path

def check(iteration=None):
    """ADR-022: Verify build log contains all workstreams from design."""
    if not iteration:
        iteration = os.environ.get("IAO_ITERATION", "unknown")
        
    from iao.paths import find_project_root
    import json
    try:
        root = find_project_root()
        iao_json = root / ".iao.json"
        prefix = "kjtcom"
        if iao_json.exists():
            config = json.loads(iao_json.read_text())
            prefix = config.get("artifact_prefix") or config.get("name") or config.get("project_code") or "kjtcom"
    except Exception:
        root = Path.cwd()
        prefix = "kjtcom"
        
    # 1. Resolve design path
    design_path = None
    # Try phase.iter.run format
    if re.match(r'^\d+\.\d+\.\d+$', iteration):
        phase, iter_n, run = iteration.split('.')
        planning_iter = f"{phase}.{iter_n}.0"
        for p_pref in [prefix, "kjtcom"]:
            p = root / "docs" / f"{p_pref}-design-{planning_iter}.md"
            if p.exists():
                design_path = p
                break
    
    if not design_path:
        # Try legacy
        for p_pref in [prefix, "kjtcom"]:
            p = root / "docs" / f"{p_pref}-design-{iteration}.md"
            if p.exists():
                design_path = p
                break

    if not design_path:
        return ("warn", "design doc not found, skipping completeness check")

    # 2. Extract workstream IDs from design
    design_text = design_path.read_text()
    expected_ids = re.findall(r'^###\s+(W\d+[a-z]?)[\s\u2014\-:]', design_text, re.MULTILINE)
    if not expected_ids:
        return ("ok", "no workstreams found in design")

    # 3. Find build log
    build_log_path = None
    for p_pref in [prefix, "kjtcom"]:
        p = root / "docs" / f"{p_pref}-build-{iteration}.md"
        if p.exists():
            build_log_path = p
            break
        p_draft = root / "docs" / "drafts" / f"{p_pref}-build-{iteration}.md"
        if p_draft.exists():
            build_log_path = p_draft
            break
            
    if not build_log_path:
        return ("fail", "build log artifact missing")

    # 4. Check for workstream headers in build log
    build_text = build_log_path.read_text()
    missing = []
    for wid in expected_ids:
        # Match ### W1 or ### W1 - PASS or ### W1 — PASS
        if not re.search(rf'^###\s+{wid}[\s\u2014\-:]', build_text, re.MULTILINE):
            missing.append(wid)
            
    if missing:
        return ("fail", f"missing workstreams in build log: {', '.join(missing)}")
        
    return ("ok", f"all {len(expected_ids)} workstreams logged")

if __name__ == "__main__":
    status, msg = check()
    print(f"  {status.upper()}: build_log_complete ({msg})")
