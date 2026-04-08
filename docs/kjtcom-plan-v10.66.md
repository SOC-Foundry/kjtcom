# kjtcom — Iteration Plan v10.66

**Iteration:** v10.66
**Phase:** 10 (Platform Hardening → Harness Externalization Phase A)
**Date:** April 08, 2026
**Primary executing agent:** Gemini CLI (`gemini --yolo`)
**Alternate:** Claude Code (`claude --dangerously-skip-permissions`)
**Machine:** NZXTcos (`~/dev/projects/kjtcom`)
**Run mode:** **Bounded fast iteration.** Target wall clock: **< 60 minutes**. Absolute cap: **90 minutes**.
**Reads:** `GEMINI.md` (or `CLAUDE.md`), this plan, and `kjtcom-design-v10.66.md`.
**Hard contract:** No `git commit`, no `git push`, no `git add`, no git writes. Manual git only.

This plan is the immutable INPUT artifact (Pillar 2). Do not rewrite during execution. Produce `kjtcom-build-v10.66.md`, `kjtcom-report-v10.66.md`, AND `kjtcom-context-v10.66.md` (with expanded §1-§11 spec) as OUTPUT artifacts.

---

## 1. Objectives

1. **Context bundle hardening** — fix three v10.65 bundle bugs (ADR dedup, delta state generator, pipeline count query) and expand to the full §1-§11 spec so v10.67's planning session needs exactly one file upload.
2. **Path-agnostic middleware** — `iao-middleware/lib/iao_paths.py` as the single source of truth for project root resolution, refactor v10.65 components to use it.
3. **Phase A harness externalization** — create `kjtcom/iao-middleware/` directory tree, move-with-shims the universal components from `scripts/`, ship the install script, ship the compatibility checker.
4. **iao CLI** — `iao project`, `iao init`, `iao status` subcommands working (`iao eval` deferred to v10.67).
5. **Evaluator hardening** — G97 synthesis ratio exact-match fix, G98 Tier 2 design-doc anchor fix.
6. **claw3d version sync + dual deploy-gap checks** — G101 fix plus the three-check architecture from ADR-025.
7. **Two-harness diligence wiring** — GEMINI.md and CLAUDE.md reference `iao-middleware/` as the universal harness.
8. **Harness update** — ADRs 023-025, Patterns 28-30, gotchas G97/G98/G101.
9. **Closing** — full orchestration with auto-deploy if CI token present.

**Implicit objective:** prove the fast-iteration execution pattern. v10.65 was 22 hours (all-day unattended). v10.66 is < 60 minutes. If this works, it validates that kjtcom iterations can be targeted and bounded, not always sprawling.

---

## 2. Trident Targets

| Prong | Target | Measurement |
|---|---|---|
| Cost | < 30K total LLM tokens | Sum from event log (post-W6 workstream-tagged) |
| Delivery | 11/11 workstreams complete | Reported by evaluator with audit trail |
| Performance | 12 concrete checks (see §10 DoD) | Direct file/system inspection |

---

## 3. The Ten Pillars of IAO (Verbatim)

1. **Trident** — Cost / Delivery / Performance triangle governs every decision
2. **Artifact Loop** — design → plan (INPUT, immutable) → build → report → context bundle (5 artifacts)
3. **Diligence** — Read before you code. **First action: `python3 scripts/query_registry.py "<topic>"`**
4. **Pre-Flight Verification** — Validate environment before execution
5. **Agentic Harness Orchestration** — The harness is the product; the model is the engine
6. **Zero-Intervention Target** — The agent does not ask permission. Notes discrepancies and proceeds.
7. **Self-Healing Execution** — Max 3 retries per error
8. **Phase Graduation** — Sandbox → staging → production
9. **Post-Flight Functional Testing** — Build is a gatekeeper
10. **Continuous Improvement** — Retrospectives feed into the next plan

---

## 4. Pre-Flight Checklist

Run BEFORE starting W1. **Discrepancies do not block — note them and proceed (Pillar 6).** The only blockers are: Ollama down, Python deps missing, immutable inputs absent, site 5xx.

```fish
# 0. Set the iteration env var FIRST
set -x IAO_ITERATION v10.66

# 1. Working directory
cd ~/dev/projects/kjtcom

# 2. Confirm immutable inputs (BLOCKER if missing)
command ls docs/kjtcom-design-v10.66.md docs/kjtcom-plan-v10.66.md GEMINI.md CLAUDE.md

# 3. Confirm last iteration's outputs (NOTE if missing)
command ls docs/kjtcom-build-v10.65.md docs/kjtcom-report-v10.65.md docs/kjtcom-context-v10.65.md 2>/dev/null \
  || echo "DISCREPANCY NOTED: v10.65 artifacts missing"

# 4. Git read-only
git status --short
git log --oneline -5

# 5. Ollama + Qwen (BLOCKER if Ollama down)
curl -s http://localhost:11434/api/tags > /dev/null && echo "ollama: ok" || echo "BLOCKER: ollama down"
ollama list | grep -i qwen || echo "DISCREPANCY NOTED: qwen not pulled"

# 6. Python deps (BLOCKER if missing)
python3 --version
python3 -c "import litellm, jsonschema, playwright, imagehash, PIL; print('python deps ok')"

# 7. Flutter (BLOCKER for W10 build gatekeeper if W10 touches app/)
flutter --version

# 8. Site is up
curl -s -o /dev/null -w "site: %{http_code}\n" https://kylejeromethompson.com

# 9. v10.65 Flutter app is deployed (validates Kyle's morning deploy)
curl -s https://kylejeromethompson.com/ 2>/dev/null | grep -o "v10\.65\|v10\.64" | head -1

# 10. claw3d.html current stale state (baseline for W10 verification)
curl -s https://kylejeromethompson.com/claw3d.html | grep -o "PCB Architecture v[0-9.]*" | head -1

# 11. Production entity baseline (should be 6,785)
python3 -c 'from scripts.firestore_query import execute_query; print(execute_query({}, "count"))' 2>/dev/null \
  || echo "DISCREPANCY NOTED: cannot baseline production count"

# 12. Disk
df -h ~ | tail -1

# 13. Sleep masked
systemctl status sleep.target 2>&1 | grep -i masked || echo "DISCREPANCY NOTED: sleep not masked"

# 14. Firebase CI token (optional — auto-deploy dependency)
ls ~/.config/firebase-ci-token.txt 2>/dev/null \
  || echo "DISCREPANCY NOTED: Firebase CI token missing; auto-deploy will be skipped"

# 15. No stale tmux sessions
tmux ls 2>&1 | head -5
# If pu_phase3 exists and is idle: tmux kill-session -t pu_phase3
```

If a BLOCKER fails, halt with `PRE-FLIGHT BLOCKED: <reason>` to build log and exit. NOTE-level discrepancies → log and proceed.

---

## 5. Workflow Execution Order

```
T+0       PRE-FLIGHT                          ~3 min
T+3       W1 context bundle fixes             ~8 min
T+11      W2 iao_paths.py + refactor          ~10 min
T+21      W3 iao-middleware/ tree + move      ~10 min
T+31      W4 install.fish                     ~8 min
T+39      W5 COMPATIBILITY.md + checker       ~4 min
T+43      W6 iao CLI                          ~6 min
T+49      W7 G97 synthesis fix                ~3 min
T+52      W8 G98 Tier 2 anchor                ~5 min
T+57      W9 GEMINI.md/CLAUDE.md updates      ~3 min
T+60      W10 claw3d + dual deploy checks     ~5 min
T+65      W11 harness + closing               ~5 min
T+70      DONE
```

**Target: ~60 min. Realistic: 60-70 min. Absolute cap: 90 min.**

---

## 6. Workstream Workflows

The full workstream design lives in `docs/kjtcom-design-v10.66.md` §8. This section is the executable subset.

### W1: Context Bundle Bug Fixes + §1-§11 Spec Expansion (P0)

**Diligence:** Read `scripts/build_context_bundle.py` directly. Read the v10.65 context bundle at `docs/kjtcom-context-v10.65.md` to see the three bugs in action.

**Steps:**
1. Open `scripts/build_context_bundle.py`
2. Find the ADR list generator (likely uses `glob` against `docs/evaluator-harness.md` or reads a JSON). Add dedup via `seen_ids = set()` filtering.
3. Find the delta state section. Wrap the snapshot load in try/except. On failure, parse the previous build log's "Iteration Delta Table" via regex: `r"## Iteration Delta Table\n\n(\|.*?\n)(?:\|.*?\n)+"`
4. Find the pipeline count query. Before the Firestore client call, add:
   ```python
   import json
   from pathlib import Path
   iao_json = project_root / ".iao.json"
   if iao_json.exists():
       iao_data = json.loads(iao_json.read_text())
       env_prefix = iao_data.get("env_prefix", "KJTCOM")
       creds_var = f"{env_prefix}_GOOGLE_APPLICATION_CREDENTIALS"
       if creds_var in os.environ:
           os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.environ[creds_var]
   ```
5. Expand the bundle to §1-§11 per design doc §4. New sections to add:
   - §3 Launch Artifacts: embed `GEMINI.md` and `CLAUDE.md` verbatim
   - §4 Harness State: embed `docs/evaluator-harness.md`, `docs/kjtcom-changelog.md`, `README.md` verbatim
   - §8 Environment State: tail `firebase-debug.log` (50 lines), tail `data/agent_scores.json` (last 5 entries), tail `data/iao_event_log.jsonl` (200 lines), current date + uname + python/flutter/ollama versions
   - §9 Artifacts Inventory: `ls -la docs/kjtcom-*-v10.66.md` output + SHA256 hashes
   - §10 Diagnostic Captures: conditional output of failed post-flight checks
   - §11 install.fish: embed `iao-middleware/install.fish` (will be empty until W4 ships; that's fine for W1's test)
6. Test: `python3 scripts/build_context_bundle.py --iteration v10.65`. Verify retroactively:
   - No ADR duplicates in §5
   - Delta table in §6 has real rows
   - Pipeline count in §7 is numeric or `env_var_missing`
   - All sections §1-§11 present
   - Total size > 300 KB

**Success criteria:** All three v10.65 bugs fixed. Bundle generator runs without crashing on missing credentials. Retroactive v10.65 bundle > 300 KB with §1-§11 populated.

---

### W2: iao_paths.py Shared Helper + v10.65 Component Refactor (P0, ADR-024)

**Diligence:** Read `scripts/query_registry.py`, `scripts/build_context_bundle.py`, `scripts/utils/iao_logger.py`, `scripts/postflight_checks/*.py` to identify every hardcoded path or cwd-relative read.

**Steps:**
1. Create `iao-middleware/lib/iao_paths.py` with the exact content from design doc §5.
2. Create `iao-middleware/lib/__init__.py` (empty) so Python treats it as a package.
3. Create `iao-middleware/__init__.py` (empty).
4. Write unit test file `iao-middleware/lib/test_iao_paths.py`:
   ```python
   import os, tempfile, json
   from pathlib import Path
   from iao_paths import find_project_root, IaoProjectNotFound

   def test_finds_via_env_var():
       with tempfile.TemporaryDirectory() as tmp:
           (Path(tmp) / ".iao.json").write_text('{"name": "test"}')
           os.environ["IAO_PROJECT_ROOT"] = tmp
           try:
               assert find_project_root() == Path(tmp).resolve()
           finally:
               del os.environ["IAO_PROJECT_ROOT"]

   def test_finds_via_cwd_walk():
       with tempfile.TemporaryDirectory() as tmp:
           (Path(tmp) / ".iao.json").write_text('{"name": "test"}')
           sub = Path(tmp) / "scripts" / "utils"
           sub.mkdir(parents=True)
           os.environ.pop("IAO_PROJECT_ROOT", None)
           assert find_project_root(start=sub) == Path(tmp).resolve()

   def test_raises_when_missing():
       import pytest
       with tempfile.TemporaryDirectory() as tmp:
           os.environ.pop("IAO_PROJECT_ROOT", None)
           try:
               find_project_root(start=Path(tmp))
               assert False, "expected IaoProjectNotFound"
           except IaoProjectNotFound:
               pass

   if __name__ == "__main__":
       test_finds_via_env_var()
       test_finds_via_cwd_walk()
       test_raises_when_missing()
       print("PASS: iao_paths tests")
   ```
5. Run `python3 iao-middleware/lib/test_iao_paths.py`, verify PASS.
6. Refactor `scripts/query_registry.py` to import `iao_paths` and use `find_project_root()` for resolving `data/script_registry.json`. Pattern:
   ```python
   import sys
   from pathlib import Path
   sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "iao-middleware" / "lib"))
   from iao_paths import find_project_root

   project_root = find_project_root()
   registry_path = project_root / "data" / "script_registry.json"
   ```
7. Same refactor for `scripts/build_context_bundle.py`, `scripts/utils/iao_logger.py`, and every file in `scripts/postflight_checks/`.
8. Test each refactored script from `/tmp/` (outside kjtcom) with `IAO_PROJECT_ROOT=~/dev/projects/kjtcom` set. Verify they find the right files.

**Success criteria:** `iao_paths.py` exists, 3 unit tests pass, all 4+ refactored scripts work from outside the project directory with env var set, all work from inside via cwd walk.

---

### W3: kjtcom/iao-middleware/ Tree + Move-with-Shims (P0, ADR-023)

**Diligence:** Review W2's refactored files to know what's getting moved.

**Steps:**
1. Create the directory tree:
   ```fish
   mkdir -p iao-middleware/bin
   mkdir -p iao-middleware/lib/postflight_checks
   mkdir -p iao-middleware/prompts
   mkdir -p iao-middleware/templates
   mkdir -p iao-middleware/data
   mkdir -p iao-middleware/docs
   ```
2. Create `.iao.json` at project root:
   ```json
   {
     "iao_version": "0.1",
     "name": "kjtcom",
     "artifact_prefix": "kjtcom",
     "gcp_project": "kjtcom-c78cd",
     "env_prefix": "KJTCOM",
     "current_iteration": "v10.66",
     "phase": 10,
     "evaluator_default_tier": "qwen",
     "created_at": "2026-04-08T<HH:MM:SS>+00:00"
   }
   ```
3. For each module being moved, use this pattern:
   ```fish
   # Move the file
   mv scripts/query_registry.py iao-middleware/lib/query_registry.py

   # Create the shim in the old location
   printf '"""Shim: moved to iao-middleware/lib/query_registry.py in v10.66 W3."""\nimport sys\nfrom pathlib import Path\n_iao_lib = Path(__file__).resolve().parent.parent / "iao-middleware" / "lib"\nif str(_iao_lib) not in sys.path:\n    sys.path.insert(0, str(_iao_lib))\nfrom query_registry import *  # noqa: F401, F403, E402\n' > scripts/query_registry.py
   ```
4. Modules to move:
   - `scripts/query_registry.py`
   - `scripts/build_context_bundle.py`
   - `scripts/utils/iao_logger.py` → `iao-middleware/lib/iao_logger.py`
   - `scripts/postflight_checks/flutter_build_passes.py`
   - `scripts/postflight_checks/dart_analyze_changed.py`
   - `scripts/postflight_checks/deployed_iteration_matches.py` (will be renamed in W10)
   - `scripts/postflight_checks/firebase_oauth_probe.py`
5. Create `iao-middleware/MANIFEST.json`:
   ```python
   import hashlib, json, os
   from pathlib import Path

   mw = Path("iao-middleware")
   manifest = {"version": "0.1", "files": {}}
   for f in sorted(mw.rglob("*")):
       if f.is_file() and f.name != "MANIFEST.json":
           rel = str(f.relative_to(mw))
           h = hashlib.sha256(f.read_bytes()).hexdigest()[:16]
           manifest["files"][rel] = {"sha256_16": h, "size": f.stat().st_size}

   (mw / "MANIFEST.json").write_text(json.dumps(manifest, indent=2))
   ```
6. Verify shims work: `python3 scripts/query_registry.py "post-flight"` — should return real results.
7. Verify direct imports work: `python3 -c "from iao_middleware.lib.query_registry import main; print('ok')"` — may need sys.path tweak.
8. Run `python3 scripts/post_flight.py v10.66` — every post-flight check must still execute (even if some fail for other reasons).

**Success criteria:** Directory tree exists, `.iao.json` at project root, all 7 modules moved with shims, `MANIFEST.json` populated, `scripts/post_flight.py` still runs, no import errors.

---

### W4: iao-middleware/install.fish (P0)

**Diligence:** Review `docs/install.fish` (the existing CachyOS toolchain installer) to understand the fish patterns Kyle already uses.

**Steps:**
1. Create `iao-middleware/install.fish` with the shape from design doc §8 W4. Key requirements:
   - Self-locate via `(dirname (realpath (status filename)))`
   - Walk up to find parent `.iao.json`
   - Read `COMPATIBILITY.md` via the checker (W5 dependency — if W5 hasn't shipped yet at runtime, skip this step and log "compatibility check deferred")
   - Copy `bin/`, `lib/`, `prompts/`, `templates/`, `MANIFEST.json` to `~/iao-middleware/`
   - `chmod +x ~/iao-middleware/bin/iao`
   - Idempotent fish config edits with marker blocks `# >>> iao-middleware >>>` / `# <<< iao-middleware <<<`
   - Add PATH entry: `set -gx PATH ~/iao-middleware/bin $PATH`
   - Add active-project source line: `test -f ~/.config/iao/active.fish; and source ~/.config/iao/active.fish`
2. Test idempotency: run the install script twice from NZXTcos. Second run should NOT duplicate the fish config entries.
3. Verify post-install: `set -gx PATH ~/iao-middleware/bin $PATH && iao --version` — should print `iao 0.1.0` (W6 ships the binary that this uses).
4. If W6 hasn't shipped at the time of W4's test, the `iao --version` test is deferred to W6's verification.

**Success criteria:** Install script self-locates, copies components to `~/iao-middleware/`, writes fish config idempotently, runs on NZXTcos and produces a clean install. Failed runs are caught and logged.

---

### W5: COMPATIBILITY.md + Checker (P1)

**Diligence:** None needed — this is greenfield.

**Steps:**
1. Create `iao-middleware/COMPATIBILITY.md` with 11 requirements per design doc §8 W5.
2. Create `iao-middleware/lib/check_compatibility.py`:
   ```python
   """check_compatibility.py — reads COMPATIBILITY.md and runs each check."""
   import re, subprocess, sys
   from pathlib import Path

   def parse_checklist(md_path):
       lines = md_path.read_text().splitlines()
       rows = []
       in_table = False
       for line in lines:
           if line.startswith("| ID |"):
               in_table = True
               continue
           if line.startswith("|---"):
               continue
           if in_table and line.startswith("|") and "|" in line[1:]:
               parts = [p.strip() for p in line.split("|")[1:-1]]
               if len(parts) >= 4 and parts[0].startswith("C"):
                   rows.append({
                       "id": parts[0],
                       "requirement": parts[1],
                       "check": parts[2].strip("`"),
                       "required": parts[3] == "yes",
                       "notes": parts[4] if len(parts) > 4 else "",
                   })
       return rows

   def run_check(cmd):
       try:
           r = subprocess.run(cmd, shell=True, capture_output=True, timeout=10)
           return r.returncode == 0
       except Exception:
           return False

   def main():
       md = Path(__file__).resolve().parent.parent / "COMPATIBILITY.md"
       rows = parse_checklist(md)
       failed_required = 0
       for row in rows:
           ok = run_check(row["check"])
           status = "PASS" if ok else ("FAIL" if row["required"] else "SKIP")
           print(f"  {status}: {row['id']} {row['requirement']}")
           if not ok and row["required"]:
               failed_required += 1
       sys.exit(1 if failed_required > 0 else 0)

   if __name__ == "__main__":
       main()
   ```
3. Test: `python3 iao-middleware/lib/check_compatibility.py` — verify output reports PASS for all required items on NZXTcos.
4. Integrate into `install.fish` W4 before the copy step (if not already done during W4).

**Success criteria:** `COMPATIBILITY.md` exists with ≥11 entries, checker runs cleanly on NZXTcos, all required checks PASS, installer integrates with checker.

---

### W6: iao CLI (project, init, status subcommands) (P1)

**Diligence:** None needed — the previous planning session prototyped this and the design doc §8 W6 has the exact shape.

**Steps:**
1. Create `iao-middleware/bin/iao`:
   ```bash
   #!/usr/bin/env bash
   set -e
   SCRIPT="$0"
   while [ -L "$SCRIPT" ]; do
       LINK="$(readlink "$SCRIPT")"
       case "$LINK" in /*) SCRIPT="$LINK" ;; *) SCRIPT="$(dirname "$SCRIPT")/$LINK" ;; esac
   done
   BIN_DIR="$(cd "$(dirname "$SCRIPT")" && pwd)"
   IAO_HOME="${IAO_MIDDLEWARE_HOME:-$(dirname "$BIN_DIR")}"
   LIB_DIR="$IAO_HOME/lib"
   export IAO_MIDDLEWARE_HOME="$IAO_HOME"
   exec python3 "$LIB_DIR/iao_main.py" "$@"
   ```
   Make executable: `chmod +x iao-middleware/bin/iao`
2. Create `iao-middleware/lib/iao_main.py` — argparse router with subcommands `project`, `init`, `status`. Stubs for `eval` and `registry` that print "deferred to v10.67" and exit 2.
3. Create `iao-middleware/lib/iao_project.py` — `add`, `list`, `switch`, `current`, `remove`. Uses `~/.config/iao/projects.json`. Writes `~/.config/iao/active.fish` on switch.
4. Create `iao-middleware/lib/iao_init.py` — bootstraps a new project with `.iao.json`, `docs/`, `data/`, `CLAUDE.md`, `GEMINI.md`. Refuses to overwrite existing `.iao.json` unless `--force`.
5. Create `iao-middleware/lib/iao_status.py` (or include in iao_main.py) — shows active project, cwd project, recent build logs, Ollama status.
6. Test:
   ```fish
   set -gx PATH ~/dev/projects/kjtcom/iao-middleware/bin $PATH
   iao --version                           # iao 0.1.0
   iao --help                              # shows subcommands
   iao project --help                      # shows project subsubcommands
   iao status                              # shows active project or "none"
   iao eval                                # prints deferred message, exits 2
   ```
7. If Kyle wants to register kjtcom as the first project (optional for W6; iao init can do it in W6 or manually later):
   ```fish
   iao project add kjtcom --gcp-project kjtcom-c78cd --prefix KJTCOM --path ~/dev/projects/kjtcom --no-shell-edit
   iao project list
   iao project current
   ```

**Success criteria:** `iao` dispatcher works, all 3 subcommands (project, init, status) functional, `iao eval` and `iao registry` stubbed with clear deferral messages.

---

### W7: G97 Synthesis Ratio Exact-Match Fix (P0)

**Diligence:** Read `scripts/run_evaluator.py` lines ~370-400 (the `normalize_llm_output()` synthesis calculation).

**Steps:**
1. Find the synthesis ratio calculation. Current code approximately:
   ```python
   for cf in core_fields:
       if any(cf in f for f in synthesized):
           count += 1
   ```
2. Replace with exact match:
   ```python
   for cf in core_fields:
       if cf in synthesized:  # exact membership check
           count += 1
   ```
   (Using set membership is even cleaner than `any(cf == f for f in synthesized)`.)
3. Add unit test — create `tests/test_evaluator.py` or append to existing:
   ```python
   def test_improvements_padded_not_counted_as_improvements():
       synthesized = {"improvements_padded", "mcps", "llms"}
       core_fields = ["improvements", "outcome", "score"]
       count = sum(1 for cf in core_fields if cf in synthesized)
       assert count == 0, f"expected 0, got {count}"
       print("PASS: test_improvements_padded_not_counted_as_improvements")

   if __name__ == "__main__":
       test_improvements_padded_not_counted_as_improvements()
   ```
4. Run the test: `python3 tests/test_evaluator.py`
5. Retroactive verification: `python3 scripts/run_evaluator.py --iteration v10.65 --dry-run 2>&1 | grep synthesis_ratio` — verify all ratios are strictly < 1.0

**Success criteria:** Unit test passes, retroactive v10.65 eval shows ratios < 1.0.

---

### W8: G98 Tier 2 Design-Doc Anchor Fix (P0)

**Diligence:** Read `scripts/run_evaluator.py` `try_gemini_tier()` function (or equivalent Tier 2 call path).

**Steps:**
1. Find the Tier 2 Gemini Flash prompt construction
2. Add a helper function at module level:
   ```python
   import re
   def extract_workstream_ids_from_design(design_path):
       """Parse a design doc for ### W<N> headers and return sorted IDs."""
       text = Path(design_path).read_text()
       matches = re.findall(r'^###\s+W(\d+)[\s—\-:]', text, re.MULTILINE)
       return [f"W{n}" for n in sorted(set(matches), key=int)]
   ```
3. In the Tier 2 call, load the design doc and extract ground-truth IDs:
   ```python
   design_path = find_project_root() / "docs" / f"kjtcom-design-{iteration}.md"
   ground_truth_ids = extract_workstream_ids_from_design(design_path)
   ```
4. Prepend to the Tier 2 prompt:
   ```python
   anchor = f"""
   GROUND TRUTH WORKSTREAM IDS: {ground_truth_ids}

   You MUST score exactly these workstreams. Do not invent workstreams not in
   this list. Do not add a W{len(ground_truth_ids)+1} or higher. If the build
   log does not contain a section for one of these IDs, mark it outcome=missing.
   """
   prompt = anchor + "\n" + original_prompt
   ```
5. After Tier 2 returns, validate:
   ```python
   returned_ids = {ws["id"] for ws in parsed_response.get("workstreams", [])}
   hallucinated = returned_ids - set(ground_truth_ids)
   if hallucinated:
       raise EvaluatorHallucinatedWorkstream(
           f"Tier 2 invented workstreams not in design: {hallucinated}"
       )
   ```
6. Add `EvaluatorHallucinatedWorkstream` exception class
7. In the main eval loop, catch `EvaluatorHallucinatedWorkstream` → log → fall through to Tier 3
8. Retroactive test: run against v10.65 build log with v10.65 design as anchor. Expected: Tier 2 returns exactly 15 workstreams (not 16 as in v10.65's broken report).

**Success criteria:** Ground-truth extraction works, Tier 2 prompt includes the anchor, hallucinated workstream IDs are caught, retroactive v10.65 test produces 15 workstreams.

---

### W9: GEMINI.md + CLAUDE.md Two-Harness Diligence Wiring (P1)

**Diligence:** Read current `GEMINI.md` and `CLAUDE.md` to find the "Diligence" section.

**Steps:**
1. Add new section after §13 "Diligence Reads" in both files:
   ```markdown
   ## 13a. Two-Harness Diligence Model (NEW v10.66, ADR-023)

   Diligence reads consult both harnesses in this order:
   1. Universal harness: `iao-middleware/` (Phase A, v10.66+)
   2. Project harness: `scripts/`, `data/`, `docs/` (kjtcom-specific)

   First action of any diligence: `python3 scripts/query_registry.py "<topic>"`.
   The registry reader consults both harnesses and returns results with source
   labels (universal vs project).

   For gotchas: project-specific gotchas in `data/gotcha_archive.json` take
   precedence over universal gotchas in `iao-middleware/data/gotchas.json`.

   Install-script-missing is a documented failure mode: if `~/iao-middleware/bin`
   is not on PATH, run `fish iao-middleware/install.fish` first. Do not
   escalate — log and proceed.
   ```
2. Update the diligence table (section 13 in both files) to reference `query_registry.py` first for each workstream
3. Add bullet to Execution Rules: "Before invoking `iao` CLI commands, verify `~/iao-middleware/bin` is on PATH."
4. Add failure mode row: "query_registry returns empty → fall back to direct file read, log as v10.67 overlay candidate"
5. Bump version stamp on both files to v10.66

**Success criteria:** Both files have the new §13a section, table updated, version bumped.

---

### W10: claw3d.html Version Sync + Dual Deploy-Gap Checks (P0, ADR-025, G101)

**Diligence:** Read `app/web/claw3d.html` to find the hardcoded title and iteration dropdown. Read `scripts/postflight_checks/deployed_iteration_matches.py` (will be renamed).

**Steps:**
1. Edit `app/web/claw3d.html`:
   - Find `kjtcom PCB Architecture v10.64` (near the bottom, footer or credits area). Change to `kjtcom PCB Architecture v10.66`
   - Find the iteration dropdown `<select>` element. Current options end at v10.64 with `selected`.
   - Add: `<option value="v10.65">v10.65</option>` and `<option value="v10.66" selected>v10.66 (Current)</option>`
   - Remove `selected` attribute from v10.64
2. Rename post-flight check:
   ```fish
   mv scripts/postflight_checks/deployed_iteration_matches.py scripts/postflight_checks/deployed_claw3d_matches.py
   ```
3. Update `deployed_claw3d_matches.py`: rename main function, update log messages to say "claw3d" not "iteration", keep the core logic (scrape claw3d.html via curl+regex, compare to `IAO_ITERATION`)
4. Create `scripts/postflight_checks/deployed_flutter_matches.py`:
   ```python
   """deployed_flutter_matches.py — verify Flutter app deploy matches IAO_ITERATION.

   Scrapes kylejeromethompson.com for the Flutter app's version stamp.
   The stamp is exposed via window.IAO_ITERATION in app/web/index.html.
   """
   import os, re, sys, urllib.request

   def check():
       url = "https://kylejeromethompson.com/"
       expected = os.environ.get("IAO_ITERATION", "").strip()
       if not expected:
           return False, "IAO_ITERATION env var not set"
       try:
           with urllib.request.urlopen(url, timeout=10) as resp:
               html = resp.read().decode("utf-8", errors="ignore")
       except Exception as e:
           return False, f"fetch failed: {e}"
       # Look for IAO_ITERATION in index.html or loaded scripts
       # Primary: window.IAO_ITERATION = "v10.66"
       m = re.search(r'IAO_ITERATION\s*[=:]\s*["\']?(v[\d.]+)', html)
       if not m:
           return False, "could not find IAO_ITERATION in page source"
       actual = m.group(1)
       if actual != expected:
           return False, f"deployed={actual}, expected={expected}"
       return True, f"deployed={actual}"

   if __name__ == "__main__":
       ok, msg = check()
       print(f"{'PASS' if ok else 'FAIL'}: deployed_flutter_matches ({msg})")
       sys.exit(0 if ok else 1)
   ```
5. Create `scripts/postflight_checks/claw3d_version_matches.py`:
   ```python
   """claw3d_version_matches.py — verify claw3d.html's in-repo version stamp matches IAO_ITERATION.

   This is a PRE-DEPLOY check — it catches G101-class staleness before deploy.
   """
   import os, re, sys
   from pathlib import Path

   def check():
       expected = os.environ.get("IAO_ITERATION", "").strip()
       if not expected:
           return False, "IAO_ITERATION env var not set"
       # Find project root dynamically
       try:
           sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "iao-middleware" / "lib"))
           from iao_paths import find_project_root
           project_root = find_project_root()
       except Exception:
           project_root = Path(__file__).resolve().parent.parent.parent
       claw3d = project_root / "app" / "web" / "claw3d.html"
       if not claw3d.exists():
           return False, f"{claw3d} not found"
       text = claw3d.read_text()
       m = re.search(r"PCB Architecture (v[\d.]+)", text)
       if not m:
           return False, "title string not found in claw3d.html"
       actual = m.group(1)
       if actual != expected:
           return False, f"claw3d.html shows {actual}, expected {expected}"
       return True, f"claw3d.html shows {actual}"

   if __name__ == "__main__":
       ok, msg = check()
       print(f"{'PASS' if ok else 'FAIL'}: claw3d_version_matches ({msg})")
       sys.exit(0 if ok else 1)
   ```
6. Wire all three into `scripts/post_flight.py`:
   ```python
   results["claw3d_version_matches"] = run_script("postflight_checks/claw3d_version_matches.py")
   results["deployed_claw3d_matches"] = run_script("postflight_checks/deployed_claw3d_matches.py")
   results["deployed_flutter_matches"] = run_script("postflight_checks/deployed_flutter_matches.py")
   if results["deployed_flutter_matches"] != results["deployed_claw3d_matches"]:
       print("WARNING: deployment state mismatch between Flutter and claw3d")
   ```
7. Test:
   ```fish
   set -x IAO_ITERATION v10.66
   python3 scripts/postflight_checks/claw3d_version_matches.py    # PASS after step 1
   python3 scripts/postflight_checks/deployed_flutter_matches.py  # FAIL (live is v10.65)
   python3 scripts/postflight_checks/deployed_claw3d_matches.py   # FAIL (live is v10.64)
   ```
8. **Note:** If `app/web/index.html` doesn't yet expose `window.IAO_ITERATION`, add it as part of this workstream. Search for the `<script>` block near Flutter bootstrap and add `window.IAO_ITERATION = "v10.66";` before the loader.

**Success criteria:** claw3d.html reads v10.66, three post-flight check files exist, pre-deploy check catches repo staleness, post-deploy checks clearly report the gap.

---

### W11: Harness Update + Closing Sequence (P0)

**Diligence:** Read `docs/evaluator-harness.md` to find the ADR section and Pattern section.

**Steps:**
1. Append ADRs 023, 024, 025 to `docs/evaluator-harness.md` (bodies from design doc §7)
2. Append Failure Patterns 28, 29, 30:
   - Pattern 28: Tier 2 Hallucination When Tier 1 Fails — links G98, ADR-021 (extended), W8
   - Pattern 29: Synthesis Substring Match Overcounting — links G97, ADR-021 (extended), W7
   - Pattern 30: Version String Drift Between claw3d and Flutter — links G101, ADR-025, W10
3. Update gotcha cross-reference table with G97, G98, G101
4. Verify harness line count: target ≥ 1,100 lines (was 1,062 post-v10.65)
5. Append v10.66 entry to `docs/kjtcom-changelog.md`:
   ```markdown
   ## v10.66 - 2026-04-08

   - NEW: Phase A Harness Externalization - `kjtcom/iao-middleware/` directory ships the universal components with install.fish (ADR-023).
   - NEW: Path-Agnostic Component Resolution - `iao_paths.find_project_root()` as single source of truth (ADR-024).
   - NEW: Dual Deploy-Gap Detection - three post-flight checks for claw3d and Flutter separately (ADR-025).
   - NEW: `iao` CLI with project, init, status subcommands (eval deferred to v10.67).
   - NEW: COMPATIBILITY.md data-driven checker read by install.fish.
   - FIXED: G97 Synthesis ratio substring overcounting (exact-match semantics).
   - FIXED: G98 Tier 2 Gemini Flash workstream hallucination (design-doc anchor).
   - FIXED: G101 claw3d.html version stamp stale at v10.64.
   - FIXED: G99 Context bundle cosmetic bugs (ADR dedup, delta state, pipeline count).
   - UPDATED: Context bundle spec expanded to §1-§11 (design docs, launch artifacts, harness state, env state, diagnostic captures, install.fish embedded).
   - Interventions: 0
   ```
6. Update `README.md` to v10.66: iao-middleware section, ADR count = 25, current iteration stamp, any line count bump
7. **Closing sequence:**
   ```fish
   # a. Delta table
   python3 scripts/iteration_deltas.py --snapshot v10.66 2>&1 | tee -a /tmp/closing.log
   python3 scripts/iteration_deltas.py --table v10.66 > /tmp/delta-table-v10.66.md

   # b. Registry sync
   python3 scripts/sync_script_registry.py 2>&1 | tee -a /tmp/closing.log

   # c. Evaluator run (W7 and W8 fixes should prevent Tier 2 fall-through and hallucination)
   python3 scripts/run_evaluator.py --iteration v10.66 --rich-context --verbose 2>&1 | tee /tmp/eval-v10.66.log

   # d. Verify Trident parity
   grep "Delivery:" docs/kjtcom-build-v10.66.md docs/kjtcom-report-v10.66.md

   # e. Context bundle (W1-expanded generator)
   python3 scripts/build_context_bundle.py --iteration v10.66
   command ls -l docs/kjtcom-context-v10.66.md
   # Must be > 300 KB

   # f. Final post-flight (build gatekeeper + three deploy-gap checks)
   python3 scripts/post_flight.py v10.66 2>&1 | tee /tmp/postflight-v10.66.log

   # g. Auto-deploy if conditions met
   if test -f ~/.config/firebase-ci-token.txt; and grep -q "BUILD GATEKEEPER: PASS" /tmp/postflight-v10.66.log
       cd app
       flutter build web --release
       set -x FIREBASE_TOKEN (cat ~/.config/firebase-ci-token.txt)
       firebase deploy --only hosting --token $FIREBASE_TOKEN
       cd ..
   else
       # Write EVENING_DEPLOY_REQUIRED.md
       printf "%s\n" "# EVENING DEPLOY REQUIRED" "" "v10.66 is complete. Auto-deploy skipped." "" "## Action" "1. cd app && flutter build web --release && firebase deploy --only hosting" "2. python3 scripts/postflight_checks/deployed_flutter_matches.py" "3. python3 scripts/postflight_checks/deployed_claw3d_matches.py" > EVENING_DEPLOY_REQUIRED.md
   end

   # h. Verify 5 artifacts
   command ls docs/kjtcom-{design,plan,build,report,context}-v10.66.md

   # i. Git status read-only
   git status --short
   git log --oneline -5

   # j. Hand back
   echo "v10.66 complete. All 5 artifacts on disk. Awaiting human commit."
   ```

**Success criteria:**
- Harness ≥ 1,100 lines, 25 ADRs, ≥ 30 patterns
- Changelog has v10.66 entry
- README updated
- Closing sequence ran
- All 5 artifacts on disk
- Context bundle > 300 KB
- Build gatekeeper PASS
- Trident parity verified
- Auto-deploy succeeded OR EVENING_DEPLOY_REQUIRED.md written

---

## 7. Active Gotchas (v10.66 Snapshot)

After v10.65: 60 entries. v10.66 adds G97, G98, G99 (retroactive), G101 → 64 entries.

| ID | Title | Status |
|---|---|---|
| G1 | Heredocs break agents | Active |
| G18 | CUDA OOM | Active (not relevant this iteration) |
| G19 | Gemini bash by default | Active |
| G22 | `ls` color codes | Active |
| G45 | Query editor cursor bug | Resolved v10.64 |
| G53 | Firebase MCP reauth | Mitigated v10.65 |
| G80 | Qwen empty reports | Pattern 21 rounds 1-3 |
| G91 | Build-side-effect late workstreams | Resolved v10.65 W1 |
| G92 | Tier 2 synthesis padding | Partial v10.65 W2 |
| G93 | Closing report Trident mismatch | Resolved v10.65 W2 |
| G94 | Gotcha consolidation audit | Resolved v10.65 W8 |
| G95 | Firebase OAuth/SA dual-path | Mitigated v10.65 W9 |
| G96 | Magic color constants | Resolved v10.65 W11 |
| **G97** | **Synthesis ratio substring overcounting** | **NEW v10.66, TARGETED W7** |
| **G98** | **Tier 2 Gemini Flash workstream hallucination** | **NEW v10.66, TARGETED W8** |
| **G99** | **Context bundle cosmetic bugs** | **NEW v10.66 (retroactive), TARGETED W1** |
| **G101** | **claw3d.html version stamp drift** | **NEW v10.66, TARGETED W10** |

---

## 8. Post-Flight Expectations

After W11 closing sequence, expected output:

```
Post-flight verification for v10.66:
========================================
  PASS: site_200 (status=200)
  PASS: bot_status (bot=@kjtcom_iao_bot)
  PASS: bot_query (total_entities=6785)
  PASS: claw3d_no_external_json
  PASS: claw3d_html (exists)
  PASS: architecture_html (exists)
MCP Verification:
  PASS: firebase_oauth_probe (path A: sa_json)
  PASS: context7_mcp (functional)
  PASS: firecrawl_mcp (functional)
  PASS: playwright_mcp (functional)
  PASS: dart_mcp (functional)
Build Gatekeeper (W1 v10.65):
  PASS: dart_analyze_changed
  PASS: flutter_build_passes
Visual Verification:
  PASS: visual_baseline_diff:index
  PASS: visual_baseline_diff:claw3d
  PASS: visual_baseline_diff:architecture
Deploy Gap Check (W10 v10.66, NEW):
  PASS: claw3d_version_matches (claw3d.html shows v10.66)
  FAIL: deployed_flutter_matches (deployed=v10.65, expected=v10.66) [DEFERRED]
  FAIL: deployed_claw3d_matches (deployed=v10.64, expected=v10.66) [DEFERRED]
  NOTE: both deferred failures are expected; deploy happens in closing sequence step g
Artifact Enforcement (G86):
  PASS: build_artifact (>12K bytes)
  PASS: report_artifact (>6K bytes)
  PASS: context_bundle_present (>300K bytes, §1-§11 populated)
Script Registry:
  PASS: script_registry_fresh
  PASS: script_registry_has_inputs
========================================
Post-flight: 21/23 passed, 2 deferred (deploy gap — resolves after step g)
```

After closing sequence step g completes (auto-deploy OR manual deploy via EVENING_DEPLOY_REQUIRED.md), the two deferred failures should flip to PASS.

---

## 9. Closing Sequence Reference

```fish
# 1. Delta table
python3 scripts/iteration_deltas.py --snapshot v10.66
python3 scripts/iteration_deltas.py --table v10.66 > /tmp/delta-table-v10.66.md

# 2. Final registry sync
python3 scripts/sync_script_registry.py

# 3. Evaluator (expect G97/G98 fixes to prevent Tier 2 hallucination)
python3 scripts/run_evaluator.py --iteration v10.66 --rich-context --verbose 2>&1 | tee /tmp/eval-v10.66.log

# 4. Verify Trident parity (G93 stays fixed)
grep "Delivery:" docs/kjtcom-build-v10.66.md docs/kjtcom-report-v10.66.md

# 5. Context bundle (W1-expanded, §1-§11 spec)
python3 scripts/build_context_bundle.py --iteration v10.66
command ls -l docs/kjtcom-context-v10.66.md  # > 300 KB required

# 6. Final post-flight (build gatekeeper + three deploy-gap checks)
python3 scripts/post_flight.py v10.66 2>&1 | tee /tmp/postflight-v10.66.log

# 7. Auto-deploy (conditional on build gatekeeper PASS + CI token present)
if test -f ~/.config/firebase-ci-token.txt; and grep -q "BUILD GATEKEEPER: PASS" /tmp/postflight-v10.66.log
    cd app
    flutter build web --release
    firebase deploy --only hosting --token (cat ~/.config/firebase-ci-token.txt)
    cd ..
end

# 8. Write EVENING_DEPLOY_REQUIRED.md if auto-deploy didn't run

# 9. Verify all 5 artifacts
command ls docs/kjtcom-{design,plan,build,report,context}-v10.66.md

# 10. Git status read-only
git status --short
git log --oneline -5

# 11. Hand back
```

---

## 10. Definition of Done

The iteration is complete when ALL of these are true:

1. **Pre-flight:** BLOCKERS pass; NOTE-level discrepancies logged
2. **W1:** Context bundle generator fixes verified via retroactive v10.65 run; bundle > 300 KB with §1-§11
3. **W2:** `iao_paths.py` exists, unit tests pass, v10.65 components refactored to use it
4. **W3:** `iao-middleware/` tree exists with bin/lib/prompts/templates/data/docs; `.iao.json` at project root; MANIFEST.json populated; move-with-shims works
5. **W4:** `install.fish` self-locates, runs, idempotent fish config edits
6. **W5:** `COMPATIBILITY.md` exists with ≥11 entries, checker runs cleanly
7. **W6:** `iao` CLI with project/init/status subcommands works; `iao --version` returns cleanly
8. **W7:** G97 unit test passes; retroactive v10.65 synthesis ratios < 1.0
9. **W8:** G98 fix catches hallucinated W16 against v10.65 retroactively
10. **W9:** GEMINI.md and CLAUDE.md have §13a Two-Harness Diligence section
11. **W10:** claw3d.html reads v10.66; three post-flight check files exist; at least pre-deploy check PASSES
12. **W11:** Harness ≥ 1,100 lines with ADRs 023-025 and Patterns 28-30; closing sequence ran

**Closing artifacts:**
13. `kjtcom-build-v10.66.md` exists, > 10,000 bytes
14. `kjtcom-report-v10.66.md` exists; Trident matches build log; no hallucinated workstreams
15. `kjtcom-context-v10.66.md` exists, > 300 KB, §1-§11 all populated
16. Post-flight green except deferred deploy-gap checks
17. **Hard contract:** Zero git writes by the agent

**Wall clock:**
18. Total execution time < 90 minutes (target < 60)
19. If > 90 minutes: warning emitted, agent proceeds to W11 closing regardless

**After closing (human steps):**
20. Manual `flutter build web --release && firebase deploy --only hosting` if auto-deploy didn't run
21. Re-run `deployed_flutter_matches` post-deploy: PASS
22. Manual git commit + push

---

*Plan v10.66 — April 08, 2026. Authored by the planning chat. Immutable during execution per ADR-012. Pairs with `kjtcom-design-v10.66.md`.*
