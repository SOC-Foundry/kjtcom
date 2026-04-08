#!/usr/bin/env python3
"""Context Bundle Generator (ADR-019).
Consolidates the current iteration's operational state into a single fifth artifact.
"""
import os, sys, json, argparse, re
from datetime import datetime

PROJECT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
DOCS_DIR = os.path.join(PROJECT_DIR, 'docs')
DATA_DIR = os.path.join(PROJECT_DIR, 'data')

def _find_doc(doc_type, iteration):
    for loc in [
        os.path.join(DOCS_DIR, f"kjtcom-{doc_type}-{iteration}.md"),
        os.path.join(DOCS_DIR, "archive", f"kjtcom-{doc_type}-{iteration}.md"),
        os.path.join(DOCS_DIR, "drafts", f"kjtcom-{doc_type}-{iteration}.md"),
    ]:
        if os.path.exists(loc):
            return loc
    return None

def build_bundle(iteration):
    lines = []
    lines.append(f"# kjtcom — Context Bundle {iteration}")
    lines.append(f"")
    lines.append(f"**Date:** {datetime.now().strftime('%B %d, %Y')}")
    lines.append(f"**Iteration:** {iteration}")
    lines.append(f"")
    lines.append(f"This artifact is the consolidated operational state for {iteration}, ")
    lines.append(f"intended to be uploaded to the planning chat (ADR-019).")
    lines.append(f"")

    # 1. Immutable Inputs
    lines.append(f"## 1. IMMUTABLE INPUTS")
    for doc_type in ["design", "plan"]:
        path = _find_doc(doc_type, iteration)
        if path:
            lines.append(f"### {doc_type.upper()} ({os.path.basename(path)})")
            lines.append("```markdown")
            with open(path) as f: lines.append(f.read().strip())
            lines.append("```")
            lines.append("")
        else:
            lines.append(f"### {doc_type.upper()} (MISSING)")
            lines.append("")

    # 2. Execution Audit
    lines.append(f"## 2. EXECUTION AUDIT")
    build_log_path = _find_doc("build", iteration)
    if build_log_path:
        lines.append(f"### BUILD LOG ({os.path.basename(build_log_path)})")
        lines.append("```markdown")
        with open(build_log_path) as f: lines.append(f.read().strip())
        lines.append("```")
    else:
        lines.append("### BUILD LOG (MISSING)")
    lines.append("")

    # 3. Platform State
    lines.append(f"## 3. PLATFORM STATE")
    
    # 3.1 Gotcha Registry (Summary)
    gotcha_path = os.path.join(DATA_DIR, "gotcha_archive.json")
    if os.path.exists(gotcha_path):
        lines.append("### GOTCHA REGISTRY (Summary)")
        try:
            with open(gotcha_path) as f:
                data = json.load(f)
                resolved = data.get("resolved_gotchas", [])
                lines.append(f"Total resolved: {len(resolved)}")
                # Show last 5
                lines.append("Last 5 resolved:")
                for g in resolved[-5:]:
                    lines.append(f"- {g.get('id', '?')}: {g.get('title', '?')}")
        except:
            lines.append("Error parsing gotcha_archive.json")
    lines.append("")

    # 3.2 Script Registry (Statistics)
    registry_path = os.path.join(DATA_DIR, "script_registry.json")
    if os.path.exists(registry_path):
        lines.append("### SCRIPT REGISTRY (Statistics)")
        try:
            with open(registry_path) as f:
                data = json.load(f)
                scripts = data.get("scripts", [])
                lines.append(f"Total scripts: {len(scripts)}")
                pipelines = {}
                for s in scripts:
                    p = s.get("pipeline", "none")
                    pipelines[p] = pipelines.get(p, 0) + 1
                for p, count in pipelines.items():
                    lines.append(f"- Pipeline {p}: {count}")
        except:
            lines.append("Error parsing script_registry.json")
    lines.append("")

    # 3.3 ADR Summary (Extracted from harness)
    harness_path = os.path.join(DOCS_DIR, "evaluator-harness.md")
    if os.path.exists(harness_path):
        lines.append("### ARCHITECTURE DECISIONS (ADRs)")
        with open(harness_path) as f:
            content = f.read()
            # Look for lines like "### ADR-001"
            adrs = re.findall(r'^###\s+(ADR-\d+.*)', content, re.MULTILINE)
            for adr in adrs:
                lines.append(f"- {adr}")
    lines.append("")

    # 4. Delta State
    lines.append(f"## 4. DELTA STATE")
    try:
        # We can't easily import from scripts/ if we are in scripts/ but let's try
        # or just run it via subprocess to get the table
        res = subprocess.run([sys.executable, os.path.join(PROJECT_DIR, "scripts", "iteration_deltas.py"), "--table", iteration], 
                             capture_output=True, text=True)
        if res.returncode == 0:
            lines.append(res.stdout.strip())
        else:
            lines.append("Iteration deltas not yet available or failed.")
    except:
        lines.append("Iteration deltas failed.")
    lines.append("")

    # 5. Pipeline State
    lines.append(f"## 5. PIPELINE STATE")
    # Entity counts
    try:
        from scripts.firestore_query import execute_query
        count = execute_query({}, "count")
        lines.append(f"Total entities (Production): {count}")
    except:
        lines.append("Production count unavailable.")
    lines.append("")

    output_path = os.path.join(DOCS_DIR, f"kjtcom-context-{iteration}.md")
    with open(output_path, "w") as f:
        f.write("\n".join(lines))
    
    return output_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--iteration", default=os.environ.get('IAO_ITERATION', 'unknown'))
    args = parser.parse_args()
    
    path = build_bundle(args.iteration)
    print(f"Context bundle generated: {path} ({os.path.getsize(path)} bytes)")
