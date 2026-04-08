#!/usr/bin/env python3
"""iao bundle generator - 10.68.1 W7 rewrite.

Implements the 10-item minimum bundle specification from design 10.68.0 §10.
Reads artifact_prefix from .iao.json so it is project-agnostic.
"""
import os
import sys
import json
import argparse
import hashlib
import platform
import subprocess
from datetime import datetime
from pathlib import Path

from iao.paths import find_project_root, IaoProjectNotFound

PROJECT_DIR = find_project_root()
DOCS_DIR = PROJECT_DIR / "docs"
DATA_DIR = PROJECT_DIR / "data"

EXCLUSIONS = {
    Path.home() / ".config" / "fish" / "config.fish",
}


def _iao_data():
    p = PROJECT_DIR / ".iao.json"
    if p.exists():
        try:
            return json.loads(p.read_text())
        except Exception:
            return {}
    return {}


def _prefix():
    d = _iao_data()
    return d.get("artifact_prefix") or d.get("name") or "project"


def _read(path):
    try:
        return Path(path).read_text(errors="ignore").rstrip()
    except Exception as e:
        return f"(read failed: {e})"


def _embed(label, path, lang="markdown"):
    out = [f"### {label} ({Path(path).name if path else 'MISSING'})"]
    if path and Path(path).exists() and path not in EXCLUSIONS:
        out.append(f"```{lang}")
        out.append(_read(path))
        out.append("```")
    else:
        out.append("(missing)")
    out.append("")
    return out


def _find_doc(prefix, doc_type, iteration):
    for loc in [
        DOCS_DIR / f"{prefix}-{doc_type}-{iteration}.md",
        DOCS_DIR / "archive" / f"{prefix}-{doc_type}-{iteration}.md",
        DOCS_DIR / "drafts" / f"{prefix}-{doc_type}-{iteration}.md",
    ]:
        if loc.exists():
            return loc
    return None


def _section(title):
    return [f"## {title}", ""]


def _tail(path, n=500):
    if not path or not Path(path).exists():
        return "(missing)"
    try:
        lines = Path(path).read_text(errors="ignore").splitlines()
        return "\n".join(lines[-n:])
    except Exception as e:
        return f"(read failed: {e})"


def _file_inventory(root, max_files=400):
    out = []
    for p in sorted(Path(root).rglob("*")):
        s = str(p)
        if not p.is_file():
            continue
        if "__pycache__" in s or ".egg-info" in s or s.endswith(".pyc"):
            continue
        try:
            h = hashlib.sha256(p.read_bytes()).hexdigest()[:16]
            out.append(f"{h}  {p.relative_to(root)}")
        except Exception:
            continue
        if len(out) >= max_files:
            out.append("... (truncated)")
            break
    return "\n".join(out)


def _env_snapshot():
    info = {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "node": platform.node(),
    }
    try:
        r = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=5)
        info["ollama"] = r.stdout.strip().splitlines()[:5]
    except Exception:
        info["ollama"] = "(unavailable)"
    try:
        r = subprocess.run(["df", "-h", str(Path.home())], capture_output=True, text=True, timeout=5)
        info["disk"] = r.stdout.strip().splitlines()[-1]
    except Exception:
        info["disk"] = "(unavailable)"
    return info


def build_bundle(iteration):
    prefix = _prefix()
    project_code = _iao_data().get("project_code", "")
    parts = iteration.split('.')
    plan_iter = f"{parts[0]}.{parts[1]}.0" if len(parts) >= 3 else iteration
    sidecar_phase = f"{parts[0]}.{parts[1]}" if len(parts) >= 2 else iteration

    lines = []
    lines.append(f"# {prefix} - Bundle {iteration}")
    lines.append("")
    lines.append(f"**Generated:** {datetime.utcnow().isoformat()}Z")
    lines.append(f"**Iteration:** {iteration}")
    lines.append(f"**Project code:** {project_code}")
    lines.append(f"**Project root:** {PROJECT_DIR}")
    lines.append("")
    lines.append("---")
    lines.append("")

    lines += _section("§1. Design")
    lines += _embed("DESIGN", _find_doc(prefix, "design", plan_iter))

    lines += _section("§2. Plan")
    lines += _embed("PLAN", _find_doc(prefix, "plan", plan_iter))

    lines += _section("§3. Build Log")
    lines += _embed("BUILD", _find_doc(prefix, "build", iteration))

    lines += _section("§4. Report")
    lines += _embed("REPORT", _find_doc(prefix, "report", iteration))

    lines += _section("§5. Harness")
    lines += _embed("base.md", PROJECT_DIR / "iao" / "docs" / "harness" / "base.md")
    if project_code:
        lines += _embed("project.md", PROJECT_DIR / project_code / "docs" / "harness" / "project.md")

    lines += _section("§6. README")
    lines += _embed("README", PROJECT_DIR / "README.md")

    lines += _section("§7. CHANGELOG")
    lines += _embed("CHANGELOG", PROJECT_DIR / "CHANGELOG.md")

    lines += _section("§8. CLAUDE.md")
    lines += _embed("CLAUDE.md", PROJECT_DIR / "CLAUDE.md")

    lines += _section("§9. GEMINI.md")
    lines += _embed("GEMINI.md", PROJECT_DIR / "GEMINI.md")

    lines += _section("§10. .iao.json")
    lines += _embed(".iao.json", PROJECT_DIR / ".iao.json", lang="json")

    lines += _section("§11. Sidecars")
    sidecar = DOCS_DIR / f"classification-{sidecar_phase}.json"
    if sidecar.exists():
        lines += _embed("classification", sidecar, lang="json")
    sterilization = PROJECT_DIR / "iao" / "docs" / f"sterilization-log-{sidecar_phase}.md"
    if sterilization.exists():
        lines += _embed("sterilization-log", sterilization)

    lines += _section("§12. Gotcha Registry")
    lines += _embed("gotcha_archive.json", DATA_DIR / "gotcha_archive.json", lang="json")

    lines += _section("§13. Script Registry")
    lines += _embed("script_registry.json", DATA_DIR / "script_registry.json", lang="json")

    lines += _section("§14. iao MANIFEST")
    lines += _embed("MANIFEST.json", PROJECT_DIR / "iao" / "MANIFEST.json", lang="json")

    lines += _section("§15. install.fish")
    lines += _embed("install.fish", PROJECT_DIR / "iao" / "install.fish", lang="fish")

    lines += _section("§16. COMPATIBILITY")
    lines += _embed("COMPATIBILITY.md", PROJECT_DIR / "iao" / "COMPATIBILITY.md")

    lines += _section("§17. projects.json")
    lines += _embed("projects.json", PROJECT_DIR / "iao" / "projects.json", lang="json")

    lines += _section("§18. Event Log (tail 500)")
    lines.append("```jsonl")
    lines.append(_tail(DATA_DIR / "iao_event_log.jsonl", 500))
    lines.append("```")
    lines.append("")

    lines += _section("§19. iao/ File Inventory (sha256_16)")
    lines.append("```")
    lines.append(_file_inventory(PROJECT_DIR / "iao"))
    lines.append("```")
    lines.append("")

    lines += _section("§20. Environment")
    lines.append("```json")
    lines.append(json.dumps(_env_snapshot(), indent=2, default=str))
    lines.append("```")
    lines.append("")

    output_path = DOCS_DIR / f"{prefix}-bundle-{iteration}.md"
    output_path.write_text("\n".join(lines))
    return output_path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--iteration", default=os.environ.get("IAO_ITERATION", "unknown"))
    args = parser.parse_args()
    path = build_bundle(args.iteration)
    print(f"Bundle generated: {path} ({path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
