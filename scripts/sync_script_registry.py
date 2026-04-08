#!/usr/bin/env python3
"""Sync data/script_registry.json (ADR-017 / ADR-022).
Walks scripts/ and pipeline/scripts/ recursively. Each .py file gets an entry
with path, purpose, function summary, mtime, last_used, lines, status,
plus ADR-022 fields: inputs, outputs, dependencies, pipeline.
"""
import os, json, time, ast, re, subprocess
from datetime import datetime
from pathlib import Path

ROOTS = ["scripts", "pipeline/scripts"]
REGISTRY_PATH = "data/script_registry.json"
EVENT_LOG = "data/iao_event_log.jsonl"

def docstring_purpose(path):
    try:
        with open(path) as f:
            tree = ast.parse(f.read())
        ds = ast.get_docstring(tree) or ""
        return ds.strip().split("\n")[0][:200] if ds else "(no docstring)"
    except Exception:
        try:
            with open(path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        return line[:200]
                    if line.startswith("#"):
                        return line.lstrip("#").strip()[:200]
        except:
            pass
        return "(parse failed)"

def function_names(path):
    try:
        with open(path) as f:
            tree = ast.parse(f.read())
        return [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)][:20]
    except Exception:
        return []

def last_used(path):
    basename = os.path.basename(path)
    try:
        if not os.path.exists(EVENT_LOG):
            return "never"
        with open(EVENT_LOG, 'rb') as f:
            try:
                f.seek(-200000, os.SEEK_END)
            except OSError:
                pass
            lines = f.readlines()
            for line in reversed(lines):
                try:
                    event = json.loads(line)
                    text = str(event.get("input_summary", "")) + str(event.get("target", "")) + str(event.get("output_summary", ""))
                    if basename in text:
                        return event.get("timestamp")
                except:
                    continue
        return "never"
    except Exception:
        return "never"

def status_for(path, last_used_iso):
    mtime = os.path.getmtime(path)
    if last_used_iso == "never":
        if (time.time() - mtime) > 120 * 86400: return "dead"
        return "stale"
    try:
        used_date = last_used_iso.split("T")[0]
        # v10.65 date is April 07, 2026
        if used_date >= "2026-03-07": return "active"
        return "stale"
    except Exception:
        return "unknown"

def extract_metadata_heuristics(path):
    """ADR-022: Heuristically extract inputs, outputs, dependencies, and pipeline."""
    inputs = []
    outputs = []
    deps = []
    pipeline = "none"
    
    try:
        content = open(path).read()
        
        # Pipeline check
        if "pipeline/" in path or "t_log_type" in content:
            for p in ["calgold", "ricksteves", "tripledb", "bourdain"]:
                if p in path or p in content:
                    pipeline = p
                    break
            if pipeline == "none" and "pipeline/" in path:
                pipeline = "common"

        # Checkpoint usage (ADR-022)
        if "Checkpoint(" in content:
            outputs.append("pipeline/data/{pipeline}/checkpoint.json")

        # Heuristics for inputs/outputs (files mentioned in content)
        data_matches = re.findall(r'[\'"](pipeline/data/[^\'"]+\.[a-z0-9]+)[\'"]', content)
        data_matches += re.findall(r'[\'"](data/[^\'"]+\.[a-z0-9]+)[\'"]', content)
        for m in data_matches:
            if any(x in m for x in ["checkpoint", "log", "registry", "archive"]):
                if "checkpoint" in m or "log" in m:
                    if m not in inputs: inputs.append(m)
                    if m not in outputs: outputs.append(m)
                else:
                    if m not in inputs: inputs.append(m)
            elif m.endswith(".json") or m.endswith(".jsonl") or m.endswith(".png"):
                if m not in inputs: inputs.append(m)

        # Dependencies (imports)
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    deps.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    deps.append(node.module)

        # Refine outputs: if file is opened with 'w' or 'a'
        write_matches = re.findall(r'open\s*\(\s*([^,]+)\s*,\s*[\'"]([wa][b+]?)[\'"]', content)
        # This regex is hard to get right without full tracing, but let's try to find literals
        for m_path_expr, mode in write_matches:
             m_lit = re.search(r'[\'"]([^\'"]+)[\'"]', m_path_expr)
             if m_lit:
                 out_file = m_lit.group(1)
                 if out_file not in outputs: outputs.append(out_file)

    except Exception:
        pass
        
    return {
        "inputs": sorted(list(set(inputs))),
        "outputs": sorted(list(set(outputs))),
        "dependencies": sorted(list(set(deps))),
        "pipeline": pipeline
    }

def main():
    existing = {}
    if os.path.exists(REGISTRY_PATH):
        try:
            with open(REGISTRY_PATH) as f:
                old_data = json.load(f)
                for s in old_data.get("scripts", []):
                    existing[s["path"]] = s
        except:
            pass

    entries = []
    for root in ROOTS:
        if not os.path.exists(root): continue
        for dirpath, _, files in os.walk(root):
            for fn in files:
                if not fn.endswith(".py") or fn == "__init__.py": continue
                p = os.path.join(dirpath, fn)
                lu = last_used(p)
                
                old_entry = existing.get(p, {})
                heuristics = extract_metadata_heuristics(p)
                
                # Merge: heuristics provide defaults, old_entry can override if it was manual
                # Actually for this iteration, I want to force update most of them to populate v2 fields
                
                entry = {
                    "path": p,
                    "purpose": docstring_purpose(p),
                    "function_names": function_names(p),
                    "created_iteration": old_entry.get("created_iteration", "unknown"),
                    "last_modified_date": datetime.fromtimestamp(os.path.getmtime(p)).date().isoformat(),
                    "last_used_date": lu,
                    "owner_workstream": old_entry.get("owner_workstream", "unassigned"),
                    "lines": sum(1 for _ in open(p)),
                    "status": status_for(p, lu),
                    "linked_gotchas": old_entry.get("linked_gotchas", []),
                    "pipeline": heuristics["pipeline"] if old_entry.get("pipeline") in [None, "none", "unknown"] else old_entry.get("pipeline", heuristics["pipeline"]),
                    "inputs": sorted(list(set(old_entry.get("inputs", []) + heuristics["inputs"]))) if old_entry.get("inputs") else heuristics["inputs"],
                    "outputs": sorted(list(set(old_entry.get("outputs", []) + heuristics["outputs"]))) if old_entry.get("outputs") else heuristics["outputs"],
                    "dependencies": sorted(list(set(old_entry.get("dependencies", []) + heuristics["dependencies"]))) if old_entry.get("dependencies") else heuristics["dependencies"],
                }
                
                # Cleanup empty strings or None from lists
                for key in ["inputs", "outputs", "dependencies", "linked_gotchas"]:
                    entry[key] = [x for x in entry[key] if x]
                
                entries.append(entry)
    
    registry = {
        "schema_version": 2,
        "last_synced": datetime.now().isoformat() + "Z",
        "scripts": sorted(entries, key=lambda x: x["path"]),
    }
    
    os.makedirs(os.path.dirname(REGISTRY_PATH), exist_ok=True)
    with open(REGISTRY_PATH, "w") as f:
        json.dump(registry, f, indent=2)
    
    print(f"Synced {len(entries)} scripts to {REGISTRY_PATH} (v2 schema)")
    active = [e for e in entries if e["status"] == "active"]
    print(f"  Active: {len(active)}, Stale: {len(entries)-len(active)}")

if __name__ == "__main__":
    main()
