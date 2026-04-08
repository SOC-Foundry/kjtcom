#!/usr/bin/env python3
"""Context Bundle Generator (ADR-019, expanded to spec §1-§11 in v10.66 W1).

Fixes from v10.66 W1:
- ADR dedup (sort + unique on adr_id)
- Delta state fallback to parsing previous build log when snapshot fails
- Pipeline count: read .iao.json -> env_prefix -> ${PREFIX}_GOOGLE_APPLICATION_CREDENTIALS
- Expanded to §1-§11 spec from design v10.66 §4
"""
import os
import sys
import json
import argparse
import re
import hashlib
import platform
import subprocess
from datetime import datetime
from pathlib import Path


from iao_middleware.paths import find_project_root, IaoProjectNotFound

PROJECT_DIR = find_project_root()
DOCS_DIR = PROJECT_DIR / "docs"
DATA_DIR = PROJECT_DIR / "data"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--iteration", default=os.environ.get("IAO_ITERATION", "unknown"))
    args = parser.parse_args()
    path = build_bundle(args.iteration)
    print(f"Context bundle generated: {path} ({path.stat().st_size} bytes)")


def _find_doc(doc_type, iteration):
    for loc in [
        DOCS_DIR / f"kjtcom-{doc_type}-{iteration}.md",
        DOCS_DIR / "archive" / f"kjtcom-{doc_type}-{iteration}.md",
        DOCS_DIR / "drafts" / f"kjtcom-{doc_type}-{iteration}.md",
    ]:
        if loc.exists():
            return loc
    return None


def _read(path):
    try:
        return Path(path).read_text(errors="ignore").strip()
    except Exception as e:
        return f"(read failed: {e})"


def _embed(label, path, lang="markdown"):
    out = [f"### {label} ({Path(path).name if path else 'MISSING'})"]
    if path and Path(path).exists():
        out.append(f"```{lang}")
        out.append(_read(path))
        out.append("```")
    else:
        out.append("(missing)")
    out.append("")
    return out


def _section_immutable_inputs(iteration):
    lines = ["## §1. IMMUTABLE INPUTS", ""]
    for dt in ["design", "plan"]:
        lines += _embed(dt.upper(), _find_doc(dt, iteration))
    return lines


def _section_execution_audit(iteration):
    lines = ["## §2. EXECUTION AUDIT", ""]
    lines += _embed("BUILD LOG", _find_doc("build", iteration))
    lines += _embed("REPORT", _find_doc("report", iteration))
    return lines


def _section_launch_artifacts():
    lines = ["## §3. LAUNCH ARTIFACTS", ""]
    lines += _embed("GEMINI.md", PROJECT_DIR / "GEMINI.md")
    lines += _embed("CLAUDE.md", PROJECT_DIR / "CLAUDE.md")
    return lines


def _section_harness_state():
    lines = ["## §4. HARNESS STATE", ""]
    lines += _embed("evaluator-harness.md", DOCS_DIR / "evaluator-harness.md")
    lines += _embed("changelog", DOCS_DIR / "kjtcom-changelog.md")
    lines += _embed("README", PROJECT_DIR / "README.md")
    return lines


def _dedup_adrs(content):
    """Extract ADR list, dedup by id, sort."""
    matches = re.findall(r'^###\s+(ADR-\d+)([^\n]*)', content, re.MULTILINE)
    seen = {}
    for adr_id, rest in matches:
        if adr_id not in seen:
            seen[adr_id] = (adr_id + rest).strip()
    return [seen[k] for k in sorted(seen, key=lambda s: int(s.split("-")[1]))]


def _section_platform_state():
    lines = ["## §5. PLATFORM STATE", ""]
    # Gotcha registry: count + last 10 added/modified
    gotcha_path = DATA_DIR / "gotcha_archive.json"
    lines.append("### Gotcha Registry")
    if gotcha_path.exists():
        try:
            data = json.loads(gotcha_path.read_text())
            entries = data.get("resolved_gotchas") or data.get("gotchas") or []
            if isinstance(data, list):
                entries = data
            lines.append(f"Total entries: {len(entries)}")
            lines.append("Last 10:")
            for g in entries[-10:]:
                if isinstance(g, dict):
                    lines.append(f"- {g.get('id', '?')}: {g.get('title', '?')}")
        except Exception as e:
            lines.append(f"(parse error: {e})")
    else:
        lines.append("(gotcha_archive.json not found)")
    lines.append("")

    # Script registry
    reg_path = DATA_DIR / "script_registry.json"
    lines.append("### Script Registry")
    if reg_path.exists():
        try:
            data = json.loads(reg_path.read_text())
            scripts = data.get("scripts", []) if isinstance(data, dict) else data
            lines.append(f"Total scripts: {len(scripts)}")
            pipelines = {}
            for s in scripts:
                p = s.get("pipeline", "none") if isinstance(s, dict) else "none"
                pipelines[p] = pipelines.get(p, 0) + 1
            for p, c in sorted(pipelines.items()):
                lines.append(f"- {p}: {c}")
        except Exception as e:
            lines.append(f"(parse error: {e})")
    lines.append("")

    # ADR registry (deduplicated)
    harness_path = DOCS_DIR / "evaluator-harness.md"
    lines.append("### ADR Registry (deduplicated)")
    if harness_path.exists():
        adrs = _dedup_adrs(harness_path.read_text())
        lines.append(f"Total ADRs: {len(adrs)}")
        for adr in adrs:
            lines.append(f"- {adr}")
    lines.append("")
    return lines


def _section_delta_state(iteration):
    lines = ["## §6. DELTA STATE", ""]
    deltas_script = PROJECT_DIR / "scripts" / "iteration_deltas.py"
    ok = False
    
    # Tier 1 & 2: try script-generated table from snapshot
    if deltas_script.exists():
        try:
            # Check for snapshot first (Tier 2 default path)
            # Tier 1 would be from .iao.json but we use default for now
            snapshot_path = DATA_DIR / "iteration_snapshots" / f"{iteration}.json"
            if snapshot_path.exists():
                res = subprocess.run(
                    [sys.executable, str(deltas_script), "--table", iteration],
                    capture_output=True, text=True, timeout=30
                )
                if res.returncode == 0 and res.stdout.strip():
                    lines.append(res.stdout.strip())
                    ok = True
        except Exception:
            pass
            
    if not ok:
        # Tier 3: parse previous build log's Iteration Delta Table
        lines.append("(snapshot generator failed or snapshot missing; falling back to previous build log parse)")
        prev_iters = []
        try:
            # Try to find previous iteration ID
            major_str, minor_str = iteration.lstrip("v").split(".")
            major = int(major_str)
            minor = int(minor_str)
            prev_iters = [f"v{major}.{minor-i}" for i in range(1, 4)]
        except Exception:
            pass
            
        found_fallback = False
        for pv in prev_iters:
            blog = _find_doc("build", pv)
            if blog:
                txt = blog.read_text(errors="ignore")
                m = re.search(r"(##+\s*Iteration Delta Table.*?)(?=\n##+\s|\Z)", txt, re.DOTALL)
                if m:
                    lines.append(f"From {blog.name}:")
                    lines.append(m.group(1).strip())
                    found_fallback = True
                    break
        
        if not found_fallback:
            lines.append("DELTA STATE UNAVAILABLE: snapshot missing and no prior build log found")
            
    lines.append("")
    return lines


def _section_pipeline_state():
    lines = ["## §7. PIPELINE STATE", ""]
    # Set creds env var via .iao.json env_prefix
    iao = PROJECT_DIR / ".iao.json"
    if iao.exists():
        try:
            iao_data = json.loads(iao.read_text())
            env_prefix = iao_data.get("env_prefix", "KJTCOM")
            creds_var = f"{env_prefix}_GOOGLE_APPLICATION_CREDENTIALS"
            if creds_var in os.environ:
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.environ[creds_var]
        except Exception:
            pass

    try:
        sys.path.insert(0, str(PROJECT_DIR))
        from scripts.firestore_query import execute_query
        count = execute_query({}, "count")
        lines.append(f"Production total entities: {count}")
    except Exception as e:
        lines.append(f"pipeline_count: env_var_missing ({e})")
    lines.append("")
    lines.append("Per-pipeline (static post-v10.65):")
    lines.append("- calgold: 899")
    lines.append("- ricksteves: 4182")
    lines.append("- tripledb: 1100")
    lines.append("- bourdain: 604")
    lines.append("Staging: 0")
    lines.append("")
    return lines


def _tail(path, n):
    try:
        with open(path, "r", errors="ignore") as f:
            return "".join(f.readlines()[-n:])
    except Exception:
        return ""


def _section_environment_state():
    lines = ["## §8. ENVIRONMENT STATE", ""]
    fb = PROJECT_DIR / "firebase-debug.log"
    lines.append("### firebase-debug.log (last 50 lines)")
    lines.append("```")
    lines.append(_tail(fb, 50) if fb.exists() else "(missing)")
    lines.append("```")
    lines.append("")

    scores = DATA_DIR / "agent_scores.json"
    lines.append("### agent_scores.json (last 5 entries)")
    if scores.exists():
        try:
            data = json.loads(scores.read_text())
            if isinstance(data, list):
                tail = data[-5:]
            elif isinstance(data, dict):
                tail = list(data.items())[-5:]
            else:
                tail = []
            lines.append("```json")
            lines.append(json.dumps(tail, indent=2))
            lines.append("```")
        except Exception as e:
            lines.append(f"(parse error: {e})")
    lines.append("")

    elog = DATA_DIR / "iao_event_log.jsonl"
    lines.append("### iao_event_log.jsonl (last 200 lines)")
    lines.append("```")
    lines.append(_tail(elog, 200) if elog.exists() else "(missing)")
    lines.append("```")
    lines.append("")

    lines.append("### System")
    lines.append(f"- date: {datetime.now().isoformat()}")
    lines.append(f"- hostname: {platform.node()}")
    lines.append(f"- uname: {platform.platform()}")
    lines.append(f"- python: {platform.python_version()}")
    for cmd, label in [(["flutter", "--version"], "flutter"),
                       (["ollama", "list"], "ollama")]:
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            lines.append(f"- {label}:")
            lines.append("  " + r.stdout.strip().splitlines()[0] if r.stdout.strip() else "  (no output)")
        except Exception:
            lines.append(f"- {label}: unavailable")
    lines.append("")
    return lines


def _section_artifacts_inventory(iteration):
    lines = ["## §9. ARTIFACTS INVENTORY", ""]
    for dt in ["design", "plan", "build", "report", "context"]:
        p = DOCS_DIR / f"kjtcom-{dt}-{iteration}.md"
        if p.exists():
            sz = p.stat().st_size
            h = hashlib.sha256(p.read_bytes()).hexdigest()
            lines.append(f"- {p.name}: {sz} bytes  sha256={h}")
        else:
            lines.append(f"- {p.name}: MISSING")
    lines.append("")
    return lines


def _section_diagnostic_captures():
    lines = ["## §10. DIAGNOSTIC CAPTURES", ""]
    urgent = PROJECT_DIR / "URGENT_BUILD_BREAK.md"
    if urgent.exists():
        lines += _embed("URGENT_BUILD_BREAK.md", urgent)
    else:
        lines.append("(no URGENT_BUILD_BREAK.md)")
        lines.append("")
    return lines


def _section_install_fish():
    lines = ["## §11. install.fish", ""]
    install = PROJECT_DIR / "iao-middleware" / "install.fish"
    if install.exists():
        lines += _embed("install.fish", install, lang="fish")
    else:
        lines.append("(iao-middleware/install.fish not yet present)")
        lines.append("")
    return lines


def build_bundle(iteration):
    lines = []
    lines.append(f"# kjtcom — Context Bundle {iteration}")
    lines.append("")
    lines.append(f"**Date:** {datetime.now().strftime('%B %d, %Y')}")
    lines.append(f"**Iteration:** {iteration}")
    lines.append("")
    lines.append("Consolidated operational state per ADR-019 expanded to §1-§11 (v10.66 W1).")
    lines.append("")

    lines += _section_immutable_inputs(iteration)
    lines += _section_execution_audit(iteration)
    lines += _section_launch_artifacts()
    lines += _section_harness_state()
    lines += _section_platform_state()
    lines += _section_delta_state(iteration)
    lines += _section_pipeline_state()
    lines += _section_environment_state()
    lines += _section_artifacts_inventory(iteration)
    lines += _section_diagnostic_captures()
    lines += _section_install_fish()

    output_path = DOCS_DIR / f"kjtcom-context-{iteration}.md"
    output_path.write_text("\n".join(lines))
    return output_path


if __name__ == "__main__":
    main()
