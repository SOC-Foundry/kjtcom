# kjtcom — Plan v10.67

**Iteration:** v10.67
**Phase:** 10 (Harness Externalization — Phase A Hardening)
**Date:** April 08, 2026
**Repo:** SOC-Foundry/kjtcom
**Machine:** NZXTcos (`~/dev/projects/kjtcom`)
**Wall clock target:** ~3 hours, no hard cap
**Executor:** Claude Code (`claude --dangerously-skip-permissions`) OR Gemini CLI (`gemini --yolo`)
**Launch incantation:** **"read claude and execute 10.67"** or **"read gemini and execute 10.67"**
**Input design doc:** `docs/kjtcom-design-v10.67.md` (immutable per G83)
**Input plan doc:** `docs/kjtcom-plan-v10.67.md` (this file, immutable per G83)

---

## 1. The One Hard Rule (Pillar 0)

**You never run `git commit`, `git push`, or `git add`.** Read-only git only. All commits are manual by Kyle after iteration close.

---

## 2. Zero Intervention (Pillar 6)

You never ask Kyle for permission. Note discrepancies, choose the safest forward path, proceed. Halt only on hard pre-flight BLOCKERS or destructive irreversible operations.

**v10.67 specific:** W9 closing evaluator is non-negotiable. You MAY NOT skip it to save wall clock. If you find yourself rationalizing skipping it, stop and re-read this sentence.

---

## 3. Execution Rules

1. **`printf` for multi-line file writes** (G1) — never heredocs
2. **`command ls`** for directory listings (G22)
3. **Bash tool defaults to bash; wrap fish with `fish -c "..."`**
4. **No tmux in v10.67** — all workstreams synchronous
5. **Max 3 retries per error** (Pillar 7)
6. **`query_registry.py` first** for any diligence (ADR-022)
7. **Update build log as you go** — don't batch at the end
8. **Never edit design or plan docs** (G83) — even if you find a typo
9. **Never run git writes** (Pillar 0)
10. **Set `IAO_ITERATION=v10.67`** in pre-flight
11. **Set `IAO_WORKSTREAM_ID=W<N>`** at start of each workstream
12. **Wall clock awareness** at each workstream boundary — log elapsed time in build log
13. **`pip install --break-system-packages`** always (not a venv)
14. **Read-only git for status/log inspection only** — never add/commit/push

---

## 4. Pre-Flight Checklist

Run all steps. BLOCKERS halt execution. NOTEs log and proceed.

```fish
# 0. Set iteration env var FIRST
set -x IAO_ITERATION v10.67

# 1. Working directory
cd ~/dev/projects/kjtcom

# 2. Immutable inputs (BLOCKER if missing)
command ls docs/kjtcom-design-v10.67.md docs/kjtcom-plan-v10.67.md GEMINI.md CLAUDE.md

# 3. v10.66 outputs (BLOCKER — W1 depends on these)
command ls docs/kjtcom-design-v10.66.md docs/kjtcom-plan-v10.66.md \
           docs/kjtcom-build-v10.66.md docs/kjtcom-report-v10.66.md \
           docs/kjtcom-context-v10.66.md

# 4. iao-middleware existing subdirectory (BLOCKER — v10.66 Phase A output)
command ls iao-middleware/lib/ iao-middleware/install.fish iao-middleware/MANIFEST.json \
           iao-middleware/COMPATIBILITY.md .iao.json

# 5. Git read-only
git status --short
git log --oneline -5

# 6. Ollama + Qwen (BLOCKER — W1 and W9 depend on this)
curl -s http://localhost:11434/api/tags > /dev/null && echo "ollama: ok" || echo "BLOCKER: ollama down"
ollama list | grep -i qwen || echo "BLOCKER: qwen not pulled"

# 7. Python deps (BLOCKER)
python3 -c "import litellm, jsonschema, playwright, imagehash, PIL; print('python deps ok')"

# 8. pip available (BLOCKER for W3b)
which pip || which pip3

# 9. Flutter (NOTE — not strictly needed in v10.67, deploys paused)
flutter --version 2>/dev/null || echo "NOTE: flutter not found, acceptable for v10.67"

# 10. Site (NOTE — deploys paused, status informational)
curl -s -o /dev/null -w "site: %{http_code}\n" https://kylejeromethompson.com

# 11. Production baseline (NOTE)
python3 -c 'from scripts.firestore_query import execute_query; print(execute_query({}, "count"))' 2>/dev/null \
  || echo "NOTE: cannot baseline production count, acceptable"

# 12. Disk (BLOCKER if < 10G)
df -h ~ | tail -1

# 13. Sleep masked (NOTE)
systemctl status sleep.target 2>&1 | grep -i masked || echo "NOTE: sleep not masked, acceptable for bounded iteration"

# 14. Firebase CI token (NOTE only — deploys paused)
ls ~/.config/firebase-ci-token.txt 2>/dev/null \
  || echo "NOTE: Firebase CI token missing, acceptable - deploys paused"

# 15. Snapshot v10.66 evaluator baseline (INFORMATIONAL)
command ls data/agent_scores.json 2>/dev/null || echo "NOTE: no prior agent_scores.json, W1 creates baseline"

# 16. Check for in-flight pip install of iao-middleware (NOTE)
pip show iao-middleware 2>/dev/null | grep -i version \
  || echo "NOTE: iao-middleware not yet pip-installed, W3b fixes"
```

**BLOCKER summary:**
- immutable inputs present
- v10.66 outputs present
- iao-middleware subdirectory present
- ollama up + qwen loaded
- python deps importable
- pip available
- disk > 10G

Any BLOCKER fail → halt with `PRE-FLIGHT BLOCKED: <reason>`, exit.

---

## 5. Build Log Template

Create `docs/kjtcom-build-v10.67.md` first thing after pre-flight:

```markdown
# kjtcom — Build Log v10.67

**Iteration:** 10.67
**Agent:** <claude-code|gemini-cli>
**Date:** April 08, 2026
**Machine:** NZXTcos
**Run mode:** Bounded sequential, ~3 hour target, no cap
**Start:** <timestamp>

## Pre-Flight
## Discrepancies Encountered
## Execution Log (W1 - W9 sections)
## Files Changed
## New Files Created
## Files Deleted
## Wall Clock Log
## Test Results
## W1 Retroactive Evaluator Findings
## W9 Closing Evaluator Findings
## Phase B Exit Criteria Verification
## Files Changed Summary
## What Could Be Better
## Next Iteration Candidates (v10.68)

**End:** <timestamp>
**Total wall clock:** <duration>

---
*Build log v10.67 — produced by <agent>, April 08, 2026.*
```

Update this file after every workstream. Don't batch at end.

---

## 6. Workstream Procedures

### W1 — v10.66 Retroactive Qwen Tier 1 Eval

**Est:** ~5 min
**Pri:** P0
**Blocks on:** Pre-flight green

**Commands:**

```fish
set -x IAO_WORKSTREAM_ID W1
cd ~/dev/projects/kjtcom

# Confirm v10.66 artifacts
command ls docs/kjtcom-{design,plan,build,report,context}-v10.66.md

# Run the evaluator against v10.66 retroactively
python3 scripts/run_evaluator.py \
    --iteration v10.66 \
    --rich-context \
    --verbose 2>&1 | tee /tmp/eval-v10.66-retroactive.log

# Capture key fields from the log
grep -E "tier used|synthesis_ratio|EvaluatorSynthesisExceeded|EvaluatorHallucinatedWorkstream|score" \
    /tmp/eval-v10.66-retroactive.log
```

**Write retroactive report:**

```fish
printf '# kjtcom — Retroactive Report v10.66

**Iteration:** v10.66 (retroactively evaluated in v10.67 W1)
**Date of original iteration:** 2026-04-08
**Date of retroactive eval:** 2026-04-08
**Evaluator:** Qwen Tier 1 (or fallback — see tier field)
**Purpose:** Close the v10.66 self-eval gap. Validate G97/G98 on live data.

## Summary

<agent writes honest summary from /tmp/eval-v10.66-retroactive.log>

## Comparison to Original Self-Eval

| Workstream | Self-Eval (v10.66 original) | Retroactive (v10.67 W1) |
|---|---|---|
| W1 | 9 | <real> |
| W2 | 9 | <real> |
| ... | ... | ... |

## G97 Live-Data Validation

<was synthesis_ratio < 1.0? did substring overcount fire? evidence>

## G98 Live-Data Validation

<did extract_workstream_ids_from_design run? any hallucinations caught? evidence>

## Findings

<new patterns, new gotchas, anything unexpected>

## Conclusion

<one sentence: fixes validated | fixes partial | fixes need v10.67 follow-up>
' > docs/kjtcom-report-v10.66-retroactive.md
```

**Success criterion:** `docs/kjtcom-report-v10.66-retroactive.md` on disk with real evaluator output, not self-eval. Log new findings for W8.

**Failure modes:**
- Evaluator raises EvaluatorSynthesisExceeded → expected if G97 fix needs work, Tier 2 fires, log both
- Evaluator raises EvaluatorHallucinatedWorkstream → expected if G98 catches something, log the caught W-ids
- Both tiers raise → Tier 3 auto-cap, write report noting this
- Ollama drops mid-run → 3 retries; if all fail, halt W1 and log as BLOCKER for W8 investigation

---

### W2 — §6 DELTA STATE Sidecar Repair

**Est:** ~5 min
**Pri:** P0
**Blocks on:** W1 complete

**Commands:**

```fish
set -x IAO_WORKSTREAM_ID W2

# 1. Diagnose the v10.66 snapshot miss
command ls data/iteration_snapshots/ 2>/dev/null || echo "directory missing"
grep -r "snapshot v10.66" docs/kjtcom-build-v10.66.md
grep -r "iteration_deltas" docs/kjtcom-build-v10.66.md

# 2. Try to produce the snapshot now
mkdir -p data/iteration_snapshots
python3 scripts/iteration_deltas.py --snapshot v10.66 2>&1 | tee /tmp/v10.66-snapshot-attempt.log
command ls data/iteration_snapshots/v10.66.json 2>/dev/null && echo "snapshot created" || echo "snapshot still missing"

# 3. Generate delta table for v10.66 (or fallback)
python3 scripts/iteration_deltas.py --table v10.66 > /tmp/delta-v10.66.md 2>&1 \
    || echo "delta generation failed, will use regex fallback from build log"
```

**Write the sidecar:**

```fish
printf '# kjtcom — Context Bundle v10.66 Delta-Repair Sidecar

**Purpose:** Repair §6 DELTA STATE of `docs/kjtcom-context-v10.66.md` which shipped with `ERROR: Snapshot data/iteration_snapshots/v10.66.json not found`.

**Authored:** v10.67 W2
**Shipped bundle:** `docs/kjtcom-context-v10.66.md` (UNMODIFIED — immutable artifact policy)
**This sidecar:** corrected §6 content only

---

## Root Cause Analysis

<agent fills in: path mismatch, script exit code, why the v10.66 W1 regex fallback did not fire>

---

## Corrected §6. DELTA STATE

<paste /tmp/delta-v10.66.md content here, or if unavailable, paste regex-extracted delta from v10.66 build log>

---

## Forward Fix

`iao_middleware/context_bundle.py` §6 path resolution now falls through three tiers:

1. `.iao.json` env-configured snapshot path
2. Default `data/iteration_snapshots/<iter>.json`
3. Regex parse of previous build log (`docs/kjtcom-build-<prev>.md`)

All three exhausted → emit `DELTA STATE UNAVAILABLE: <reason>` instead of raw error.

This fix is applied in W3a context_bundle.py refactor and verified in W9 v10.67 closing bundle.
' > docs/kjtcom-context-v10.66-delta-repair.md
```

**Success criterion:** Sidecar file on disk. Root cause documented. `docs/kjtcom-context-v10.66.md` unchanged.

---

### W3a — Package Restructure + Rename + Shim Fixes

**Est:** ~35 min (highest-risk workstream)
**Pri:** P0
**Blocks on:** W2 complete

**Pre-W3a diligence:**

```fish
set -x IAO_WORKSTREAM_ID W3a

# Catalog current state
command ls iao-middleware/lib/
find iao-middleware/lib -name "*.py" | sort
grep -rn "iao-middleware/lib" scripts/ app/ 2>/dev/null
grep -rn "from iao_middleware" . 2>/dev/null
grep -rn "lib.iao_paths\|lib.query_registry\|lib.build_context_bundle" . 2>/dev/null
```

**Step 1 — Create new package structure:**

```fish
mkdir -p iao-middleware/iao_middleware/postflight
mkdir -p iao-middleware/tests
```

**Step 2 — Move + rename files:**

```fish
git mv iao-middleware/lib/iao_paths.py iao-middleware/iao_middleware/paths.py
git mv iao-middleware/lib/query_registry.py iao-middleware/iao_middleware/registry.py
git mv iao-middleware/lib/build_context_bundle.py iao-middleware/iao_middleware/context_bundle.py
git mv iao-middleware/lib/check_compatibility.py iao-middleware/iao_middleware/compatibility.py
git mv iao-middleware/lib/iao_main.py iao-middleware/iao_middleware/cli.py
git mv iao-middleware/lib/iao_logger.py iao-middleware/iao_middleware/logger.py

for f in iao-middleware/lib/postflight_checks/*.py
    set name (basename $f)
    if test "$name" != "__init__.py"
        git mv $f iao-middleware/iao_middleware/postflight/$name
    end
end

git mv iao-middleware/lib/test_iao_paths.py iao-middleware/tests/test_paths.py 2>/dev/null \
    || mv iao-middleware/lib/test_iao_paths.py iao-middleware/tests/test_paths.py
```

**IMPORTANT:** `git mv` is file rename tracking, NOT a git write. It stages renames for Kyle's future commit but runs no commit. If the agent is uncertain whether `git mv` counts as a write, use plain `mv` instead — functionality is equivalent for v10.67 since Kyle commits manually.

**Step 3 — Create `iao_middleware/__init__.py`:**

```fish
printf 'from iao_middleware.paths import find_project_root, IaoProjectNotFound

__version__ = "0.1.0"
__all__ = ["find_project_root", "IaoProjectNotFound", "__version__"]
' > iao-middleware/iao_middleware/__init__.py
```

**Step 4 — Create `iao_middleware/postflight/__init__.py`:**

```fish
printf '"""iao_middleware postflight check modules."""
from iao_middleware.postflight import (
    deployed_flutter_matches,
    deployed_claw3d_matches,
    claw3d_version_matches,
    build_gatekeeper,
    artifacts_present,
    firestore_baseline,
    map_tab_renders,
)

__all__ = [
    "deployed_flutter_matches",
    "deployed_claw3d_matches",
    "claw3d_version_matches",
    "build_gatekeeper",
    "artifacts_present",
    "firestore_baseline",
    "map_tab_renders",
]
' > iao-middleware/iao_middleware/postflight/__init__.py
```

**Adjust the import list to match actual files present in your v10.66 postflight_checks dir. Remove any not present; add any present but not listed.**

**Step 5 — Update internal imports in renamed files:**

Go through each renamed file and fix imports:
- `from lib.iao_paths import` → `from iao_middleware.paths import`
- `from iao_paths import` → `from iao_middleware.paths import`
- `from lib.query_registry import` → `from iao_middleware.registry import`
- Similar for `context_bundle`, `compatibility`, `cli`, `logger`
- Postflight modules: `from lib.X import` → `from iao_middleware.X import`

**Step 6 — Update `bin/iao` dispatcher:**

```fish
printf '#!/usr/bin/env bash
# iao CLI dispatcher
# v0.1.0
set -e

# Resolve the real script directory (follow symlinks)
SCRIPT="$(readlink -f "${BASH_SOURCE[0]}")"
BIN_DIR="$(dirname "$SCRIPT")"
MIDDLEWARE_ROOT="$(dirname "$BIN_DIR")"

# Ensure iao_middleware package is on path
# (pyproject.toml install handles this, but fallback for uninstalled use)
if ! python3 -c "import iao_middleware" 2>/dev/null; then
    export PYTHONPATH="$MIDDLEWARE_ROOT:$PYTHONPATH"
fi

exec python3 -m iao_middleware.cli "$@"
' > iao-middleware/bin/iao
chmod +x iao-middleware/bin/iao
```

**Step 7 — Rewrite shims in `scripts/`:**

```fish
printf '#!/usr/bin/env python3
"""Shim for iao_middleware.registry — see iao-middleware/iao_middleware/registry.py"""
from iao_middleware.registry import main

if __name__ == "__main__":
    main()
' > scripts/query_registry.py
chmod +x scripts/query_registry.py

printf '#!/usr/bin/env python3
"""Shim for iao_middleware.context_bundle — see iao-middleware/iao_middleware/context_bundle.py"""
from iao_middleware.context_bundle import main

if __name__ == "__main__":
    main()
' > scripts/build_context_bundle.py
chmod +x scripts/build_context_bundle.py
```

Any other legacy scripts that existed at `scripts/` pointing at `iao-middleware/lib/` → shim them the same way.

**Step 8 — Update `scripts/post_flight.py` imports:**

```fish
# Locate current import block
grep -n "import.*postflight\|from.*postflight" scripts/post_flight.py

# Use str_replace to convert imports to:
# from iao_middleware.postflight import (
#     deployed_flutter_matches,
#     deployed_claw3d_matches,
#     ...
# )
```

**Step 9 — Update `iao-middleware/install.fish`:**

Replace any `cp -r lib/*` patterns with `cp -r iao_middleware/*`. The install script copies the Python package, not the old `lib/` directory.

**Step 10 — Regenerate `MANIFEST.json`:**

```fish
python3 -c "
import hashlib, json, pathlib
root = pathlib.Path('iao-middleware')
files = {}
for p in sorted(root.rglob('*')):
    if p.is_file() and '__pycache__' not in str(p) and '.pyc' not in str(p):
        rel = str(p.relative_to(root))
        h = hashlib.sha256(p.read_bytes()).hexdigest()[:16]
        files[rel] = h
manifest = {'version': '0.1.0', 'generated': '2026-04-08', 'files': files}
pathlib.Path('iao-middleware/MANIFEST.json').write_text(json.dumps(manifest, indent=2))
print(f'manifest: {len(files)} files')
"
```

**Step 11 — Delete `iao-middleware/lib/`:**

```fish
# Verify empty or only stragglers
command ls iao-middleware/lib/ 2>/dev/null
# If empty or only __init__.py remains, delete:
rm -rf iao-middleware/lib/
```

**Step 12 — Verification gate (before W3b):**

```fish
# Package import works
python3 -c "from iao_middleware import find_project_root, __version__; print(__version__, find_project_root())"

# Shim works
python3 scripts/query_registry.py "post-flight"

# Tests pass
python3 -m iao_middleware.tests.test_paths 2>/dev/null \
    || python3 iao-middleware/tests/test_paths.py

# post_flight imports resolve
python3 -c "import sys; sys.path.insert(0, 'iao-middleware'); from iao_middleware.postflight import deployed_flutter_matches; print('post_flight imports ok')"

# bin/iao dispatcher
iao-middleware/bin/iao --version 2>&1 || echo "NOTE: bin/iao works once W3b pip install completes"
```

**Failure recovery:** If any import breaks and can't be fixed in 3 retries, revert only that specific file with `git checkout -- <file>`, document in build log, continue with remaining work. Mark the unresolved file as W9 tech debt.

**Success criterion:**
- `iao-middleware/lib/` is gone
- `iao-middleware/iao_middleware/` package exists with all renamed modules
- All shims re-export cleanly
- `from iao_middleware import ...` works
- `scripts/query_registry.py` works via shim
- `post_flight.py` imports resolve
- `MANIFEST.json` regenerated

---

### W3b — Standalone-Repo Scaffolding + pyproject.toml + pip install -e

**Est:** ~25 min
**Pri:** P0
**Blocks on:** W3a verification gate green

**Step 1 — `VERSION`:**

```fish
printf '0.1.0
' > iao-middleware/VERSION
```

**Step 2 — `pyproject.toml`:**

```fish
printf '[project]
name = "iao-middleware"
version = "0.1.0"
description = "Iterative Agentic Orchestration middleware"
requires-python = ">=3.11"
dependencies = [
    "litellm",
    "jsonschema",
]

[project.scripts]
iao = "iao_middleware.cli:main"

[build-system]
requires = ["setuptools>=61"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
include = ["iao_middleware*"]
' > iao-middleware/pyproject.toml
```

**Step 3 — `.gitignore`:**

```fish
printf '__pycache__/
*.pyc
*.pyo
*.egg-info/
.pytest_cache/
build/
dist/
.coverage
.tox/
' > iao-middleware/.gitignore
```

**Step 4 — `README.md`** (standalone-repo voice):

```fish
printf '# iao-middleware

Iterative Agentic Orchestration middleware. Shared harness components for IAO projects, consumed by [kjtcom](https://github.com/SOC-Foundry/kjtcom) and future IAO-pattern projects.

**Version:** 0.1.0 (Phase A — authored inside kjtcom, extraction to standalone repo planned for v10.68)

---

## What this is

iao-middleware provides:

- **Path-agnostic project root resolution** — `find_project_root()` works from any cwd
- **Context bundle generator** — consolidated operational state in 11 sections
- **Script + gotcha registry queries** — first-action diligence tool
- **Compatibility checker** — data-driven environment validation
- **Doctor module** — shared pre/post-flight health checks
- **`iao` CLI** — project, init, status, check config subcommands
- **Post-flight checks** — deploy gap detection, build gatekeeper, artifacts verification

---

## Install

### Via install.fish (recommended)

```fish
cd iao-middleware
fish install.fish
```

The installer copies the package to `~/iao-middleware/`, puts `bin/iao` on PATH via a fish config marker block, and runs compatibility checks.

### Via pip (development)

```fish
pip install -e kjtcom/iao-middleware/ --break-system-packages
```

---

## Quickstart

```fish
iao status                  # Current project, iteration, harness state
iao check config            # Resolution map + config integrity
iao check config --strict   # Promote warns to failures for CI
iao project list            # List known IAO projects
iao init                    # Initialize .iao.json in current project
```

---

## Python API

```python
from iao_middleware import find_project_root, __version__
from iao_middleware.doctor import run_all
from iao_middleware.registry import query

root = find_project_root()
results = run_all(level="quick")
hits = query("post-flight")
```

---

## Compatibility

See [COMPATIBILITY.md](COMPATIBILITY.md) for the full matrix. v0.1.0 targets Linux + fish + Python 3.11+.

---

## Contributing

This package is currently authored inside `kjtcom/iao-middleware/` and will be extracted to `SOC-Foundry/iao-middleware` as a standalone repo in v10.68. Contributions welcome after extraction.

---

## License

License to be determined before v0.2.0 release.

---

*iao-middleware v0.1.0 — April 2026*
' > iao-middleware/README.md
```

**Step 5 — `CHANGELOG.md`:**

```fish
printf '# iao-middleware changelog

## 0.1.0 — 2026-04-08 (kjtcom v10.67)

First versioned release. Authored inside `kjtcom/iao-middleware/` as the template for the future `SOC-Foundry/iao-middleware` standalone repo (v10.68 extraction target).

### Added
- `iao_middleware.paths` — path-agnostic project root resolution (`find_project_root`)
- `iao_middleware.registry` — script and gotcha registry queries
- `iao_middleware.context_bundle` — context bundle generator with §1–§11 spec
- `iao_middleware.compatibility` — data-driven compatibility checker
- `iao_middleware.doctor` — shared pre/post-flight health check module (quick/preflight/postflight levels)
- `iao_middleware.cli` — `iao` CLI with `project`, `init`, `status`, `check config` subcommands
- `iao_middleware.postflight` — 7 post-flight checks including dual deploy gap detection
- `install.fish` — idempotent fish installer with marker block
- `COMPATIBILITY.md` — 11 compatibility entries, data-driven checker
- `pyproject.toml` — pip-installable package with `iao` entry point
- `docs/adrs/0001-phase-a-externalization.md` — first middleware-internal ADR

### Notes
- LICENSE file intentionally absent; license decision deferred to v0.2.0 (v10.68 extraction)
- `iao eval` and `iao registry` subcommands stubbed, deferred to v0.2.0
- Macintosh and Windows compatibility not yet targeted
' > iao-middleware/CHANGELOG.md
```

**Step 6 — `docs/adrs/0001-phase-a-externalization.md`:**

```fish
mkdir -p iao-middleware/docs/adrs
printf '# ADR 0001 — Phase A Externalization

**Status:** Accepted
**Date:** 2026-04-08
**Authors:** kjtcom v10.67 planning chat

## Context

The IAO (Iterative Agentic Orchestration) methodology, developed in kjtcom, produces reusable harness components: path resolution, context bundle generation, registry queries, compatibility checking, pre/post-flight health checks, and a `iao` CLI. These components are project-agnostic and will be consumed by other IAO-pattern projects within SOC-Foundry and TachTech Engineering.

Continuing to develop these components as first-class members of the kjtcom repo creates several problems:

1. Engineers consuming the components would have to vendor or submodule kjtcom in full
2. Versioning is conflated between kjtcom iterations and middleware capability
3. Extraction to a dedicated repo becomes harder the longer it is deferred

## Decision

Externalize the harness components into an `iao_middleware` Python package that is:

1. **Currently staged at `kjtcom/iao-middleware/`** as a subdirectory for Phase A authoring (v10.66 scaffold, v10.67 hardening)
2. **Authored in standalone-repo voice** — its own README, CHANGELOG, VERSION, pyproject.toml, .gitignore, and docs/adrs tree
3. **Extracted to `SOC-Foundry/iao-middleware` as its own repo in v10.68** via `git subtree split --prefix=iao-middleware/`
4. **Versioned independently** of kjtcom iteration numbers (semver starting 0.1.0)

## Consequences

**Positive:**
- Clean extraction path: v10.68 Phase B is a mechanical operation, not a refactor
- Python engineers can `from iao_middleware import ...` today (via `pip install -e`)
- Independent versioning allows middleware to iterate without kjtcom iteration overhead
- Standalone-repo voice forces documentation discipline from day one

**Negative:**
- Dash/underscore naming asymmetry (`iao-middleware` repo, `iao_middleware` package) — documented in kjtcom harness ADR-028
- Two parallel ADR streams (kjtcom harness ADRs vs iao_middleware internal ADRs) — intentional scope separation
- License decision deferred until v0.2.0 (before v10.68 extraction)

## Status

Accepted and under implementation in kjtcom v10.67. Extraction planned for kjtcom v10.68.
' > iao-middleware/docs/adrs/0001-phase-a-externalization.md
```

**Step 7 — pip install -e:**

```fish
pip install -e iao-middleware/ --break-system-packages 2>&1 | tee /tmp/pip-install-v10.67.log
```

**Step 8 — Verification:**

```fish
pip show iao-middleware | grep -i version
python3 -c "import iao_middleware; print(iao_middleware.__version__)"
iao --version 2>&1 || iao-middleware/bin/iao --version
which iao
```

**Failure recovery:**
- `pip install -e` fails → debug pyproject.toml syntax, retry up to 3 times
- If unresolvable → skip pip install, leave pyproject.toml on disk for v10.68, log as exit criterion 3 at risk, continue
- `iao --version` not on PATH → acceptable if `iao-middleware/bin/iao --version` works; document in build log

**Success criterion:**
- VERSION, pyproject.toml, README, CHANGELOG, .gitignore, docs/adrs/0001 all on disk
- `pip show iao-middleware` returns 0.1.0
- `python3 -c "import iao_middleware"` succeeds
- Either `iao --version` or `iao-middleware/bin/iao --version` returns `0.1.0`

---

### W4 — doctor.py + iao status + iao check config

**Est:** ~20 min
**Pri:** P0
**Blocks on:** W3b verification green

**Step 1 — Create `iao_middleware/doctor.py`:**

Full module per design §9. Functions:
- `run_all(level: str = "quick") -> dict[str, tuple[str, str]]`
- `_quick_checks()` — 8 checks from design §9
- `_preflight_checks()` — ollama, qwen, python deps, disk, sleep, flutter
- `_postflight_checks()` — deployed_flutter_matches, deployed_claw3d_matches, claw3d_version_matches, build_gatekeeper, artifacts_present, manifest integrity, compatibility re-run

Each check returns `(status, message)` where `status ∈ {"ok", "warn", "fail", "deferred"}`.

**Step 2 — Extend `cli.py` `iao status`:**

Columnar output per design §9:
```
iao status
──────────
project:     <name> (<root>)
iteration:   <IAO_ITERATION env or unknown>
cwd:         <cwd>
ollama:      <up/down, models>
middleware:  <path, install date from MANIFEST.json, file count>
project hooks:
  query_registry       → <resolution>  (shim active/direct)
  build_context_bundle → <resolution>  (shim active/direct)
  postflight_checks    → <resolution>  (<N> checks)
deploy gap:
  flutter:   repo <vX> / live <vY>  [status]
  claw3d:    repo <vX> / live <vY>  [status]
```

**Step 3 — Add `iao check config` subcommand:**

```python
# In cli.py
def cmd_check_config(args):
    from iao_middleware.doctor import run_all
    results = run_all(level="quick")
    strict = args.strict
    has_fail = False
    has_warn = False
    for name, (status, msg) in results.items():
        tag = {"ok": "[ok]", "warn": "[WARN]", "fail": "[FAIL]", "deferred": "[DEFERRED]"}[status]
        print(f"{tag} {name}: {msg}")
        if status == "fail":
            has_fail = True
        elif status == "warn":
            has_warn = True
    if has_fail:
        return 1
    if strict and has_warn:
        return 1
    return 0
```

**Step 4 — Unit tests for doctor:**

Create `iao-middleware/tests/test_doctor.py` with basic smoke tests:
- `run_all("quick")` returns a dict
- Each value is a 2-tuple of (str, str)
- Status values are in the allowed set
- At least one check runs

**Step 5 — Verification:**

```fish
iao status
iao check config
iao check config --strict
python3 iao-middleware/tests/test_doctor.py
```

**Success criterion:** `iao status` and `iao check config` both work, doctor.py quick checks complete in < 2 seconds.

---

### W5 — Wire doctor.run_all into pre_flight.py + post_flight.py

**Est:** ~15 min
**Pri:** P0
**Blocks on:** W4 complete

**Step 1 — Refactor `scripts/pre_flight.py`:**

```python
#!/usr/bin/env python3
"""Pre-flight checks, thin wrapper over iao_middleware.doctor."""
import sys
from iao_middleware.doctor import run_all

def main():
    results = run_all(level="preflight")
    fail_count = 0
    for name, (status, msg) in results.items():
        tag = {"ok": "[ok]", "warn": "[WARN]", "fail": "[BLOCKER]", "deferred": "[DEFERRED]"}[status]
        print(f"{tag} {name}: {msg}")
        if status == "fail":
            fail_count += 1
    if fail_count > 0:
        print(f"\nPRE-FLIGHT BLOCKED: {fail_count} BLOCKER(s)")
        sys.exit(1)
    print("\npre-flight: clean")

if __name__ == "__main__":
    main()
```

**Step 2 — Refactor `scripts/post_flight.py`:**

```python
#!/usr/bin/env python3
"""Post-flight checks. Orchestrates doctor.run_all(postflight) + iteration-specific logic."""
import sys
from iao_middleware.doctor import run_all

def main():
    iteration = sys.argv[1] if len(sys.argv) > 1 else None
    if not iteration:
        print("usage: post_flight.py <iteration>")
        sys.exit(2)

    results = run_all(level="postflight")
    fail_count = 0
    for name, (status, msg) in results.items():
        tag = {"ok": "[ok]", "warn": "[WARN]", "fail": "[FAIL]", "deferred": "[DEFERRED]"}[status]
        print(f"{tag} {name}: {msg}")
        if status == "fail":
            fail_count += 1

    # Build gatekeeper check is the specific gate
    build_status = results.get("build_gatekeeper", ("unknown", ""))
    if build_status[0] == "ok":
        print("\nBUILD GATEKEEPER: PASS")
    else:
        print(f"\nBUILD GATEKEEPER: {build_status[0].upper()}")

    if fail_count > 0:
        sys.exit(1)

if __name__ == "__main__":
    main()
```

**Step 3 — Verify contracts preserved:**

```fish
# Pre-flight: must BLOCK on ollama down, succeed on clean state
python3 scripts/pre_flight.py

# Post-flight: must honor deploy_paused (after W6), must print BUILD GATEKEEPER
python3 scripts/post_flight.py v10.67
```

**Failure recovery:** If either script breaks contracts, revert it with `git checkout -- scripts/<name>.py`, leave doctor.py in place unwired, mark Phase B exit criterion 2 as failed in W9.

**Success criterion:** Both scripts import from `iao_middleware.doctor`, both run end-to-end clean, pre-flight BLOCKER logic preserved, post-flight BUILD GATEKEEPER line preserved.

---

### W6 — .iao.json deploy_paused Flag

**Est:** ~8 min
**Pri:** P1
**Blocks on:** W5 complete

**Step 1 — Edit `.iao.json`:**

```fish
python3 -c "
import json, pathlib
p = pathlib.Path('.iao.json')
data = json.loads(p.read_text())
data['deploy_paused'] = True
data['deploy_paused_reason'] = 'Focus on iao-middleware Phase A hardening (v10.67) and extraction (v10.68)'
data['deploy_paused_since'] = '2026-04-08'
p.write_text(json.dumps(data, indent=2) + '\n')
print('deploy_paused flag set')
"
```

**Step 2 — Update `deployed_flutter_matches.py` and `deployed_claw3d_matches.py`:**

Add at the top of each check function:

```python
import json, pathlib

def _read_deploy_paused():
    try:
        p = pathlib.Path(".iao.json")
        if p.exists():
            data = json.loads(p.read_text())
            if data.get("deploy_paused"):
                return True, data.get("deploy_paused_since", "unknown")
    except Exception:
        pass
    return False, None

def check():
    paused, since = _read_deploy_paused()
    if paused:
        return ("deferred", f"deploy paused since {since}; repo vX / live vY expected")
    # ... existing check logic
```

**Step 3 — Update `doctor.py` deploy gap quick check** to honor the same flag.

**Step 4 — Verification:**

```fish
iao status  # deploy gap section should show [DEFERRED - deploy paused]
python3 scripts/post_flight.py v10.67  # deployed_* should not FAIL
iao check config  # should not emit fail for deploy gap
```

**Success criterion:** Post-flight exits clean (no deploy-related fails). Removing `deploy_paused` from `.iao.json` restores hard checks.

---

### W7 — COMPATIBILITY.md Hardening

**Est:** ~10 min
**Pri:** P1
**Blocks on:** W6 complete

**Step 1 — Review existing entries:**

```fish
command cat iao-middleware/COMPATIBILITY.md
python3 iao-middleware/iao_middleware/compatibility.py
```

**Step 2 — Add missing locally-testable entries** if not already present:
- C12: Python 3.11+
- C13: `realpath` binary available
- C14: fish ≥ 3.6
- C15: git config user.email present

**Step 3 — Mark CUDA/NVIDIA entries as NZXT-specific:**

Add a column or note to COMPATIBILITY.md indicating which entries are machine-specific and will not apply to P3 in v10.68.

**Step 4 — Rerun checker:**

```fish
python3 iao-middleware/iao_middleware/compatibility.py 2>&1 | tee /tmp/compat-v10.67.log
grep -E "PASS|FAIL|WARN" /tmp/compat-v10.67.log
```

**Success criterion:** All locally-testable entries PASS on NZXT. NZXT-specific entries clearly marked.

---

### W8 — Harness ADRs 026/027/028 + Patterns from W1

**Est:** ~15 min
**Pri:** P0
**Blocks on:** W7 complete (conceptually depends on W1 findings)

**Append three ADRs to `docs/evaluator-harness.md`:**

**ADR-026: Phase B Extraction Criteria**
- Context: v10.67 is the last in-kjtcom iteration for iao_middleware
- Decision: 5 exit conditions must all pass before v10.68 extraction
- Consequences: potential v10.67.1 patch iteration if any fail

**ADR-027: doctor.py Unification**
- Context: duplicated check logic between pre_flight, post_flight, iao CLI
- Decision: one shared module, three levels, dict return shape
- Consequences: simpler refactors, v10.68 can iterate on API independently

**ADR-028: Dash Repo Name / Underscore Python Package Convention**
- Context: Python import legality requires underscore, stated repo name uses dash
- Decision: scikit-learn pattern — `iao-middleware` repo, `iao_middleware` package
- Consequences: pyproject.toml uses dash name, imports use underscore, install.fish handles both

**Patterns from W1 findings:**

Based on `/tmp/eval-v10.66-retroactive.log`, add any new patterns to `docs/evaluator-harness.md`:
- Pattern 31+: whatever the retroactive run surfaced

**Line count check:**

```fish
wc -l docs/evaluator-harness.md  # target ~1,180 lines
```

**Success criterion:** Three ADRs appended with context/decision/consequences, W1 patterns captured, harness grew by ~70 lines.

---

### W9 — Closing Sequence with Qwen Tier 1 Evaluator

**Est:** ~15 min
**Pri:** P0
**Blocks on:** W8 complete

**This is non-negotiable. Do not skip the evaluator step.**

**Step 1 — Iteration delta snapshot:**

```fish
python3 scripts/iteration_deltas.py --snapshot v10.67
python3 scripts/iteration_deltas.py --table v10.67 > /tmp/delta-table-v10.67.md
```

**Step 2 — Sync script registry:**

```fish
python3 scripts/sync_script_registry.py
```

**Step 3 — Build context bundle v10.67:**

```fish
python3 scripts/build_context_bundle.py --iteration v10.67
command ls -l docs/kjtcom-context-v10.67.md  # must be > 300 KB
```

Verify §6 DELTA STATE renders correctly (no ERROR line). If it does error, the forward fix from W3a context_bundle.py didn't take — halt, debug, retry.

**Step 4 — RUN THE EVALUATOR (non-negotiable):**

```fish
python3 scripts/run_evaluator.py \
    --iteration v10.67 \
    --rich-context \
    --verbose 2>&1 | tee /tmp/eval-v10.67.log

# Capture tier + scores
grep -E "tier used|synthesis_ratio|score" /tmp/eval-v10.67.log
```

If you feel tempted to skip this step, re-read §2. There are no wall-clock constraints that justify skipping. v10.66 shipped without running it and the resulting report was self-eval garbage. v10.67 will not repeat that.

**Step 5 — Post-flight:**

```fish
python3 scripts/post_flight.py v10.67 2>&1 | tee /tmp/postflight-v10.67.log
```

Post-flight should exit clean (deploy_paused flag from W6 handles the deployed_* checks).

**Step 6 — Phase B exit criteria verification:**

```fish
# Criterion 1: duplication eliminated
command ls iao-middleware/lib/ 2>&1 | grep -i "no such" && echo "C1: PASS (lib/ gone)" || echo "C1: FAIL"
grep -l "iao-middleware/lib" scripts/ 2>/dev/null && echo "C1: FAIL (references remain)" || echo "C1: PASS"

# Criterion 2: doctor unified
grep -l "from iao_middleware.doctor" scripts/pre_flight.py scripts/post_flight.py && echo "C2: PASS" || echo "C2: FAIL"

# Criterion 3: iao CLI stable at 0.1.0
iao --version 2>&1 | grep -q "0.1.0" && echo "C3: PASS" || echo "C3: check bin/iao"
test "$(cat iao-middleware/VERSION)" = "0.1.0" && echo "C3: VERSION file ok"

# Criterion 4: install.fish idempotent
fish iao-middleware/install.fish 2>&1 | tee /tmp/install-run-1.log
fish iao-middleware/install.fish 2>&1 | tee /tmp/install-run-2.log
diff /tmp/install-run-1.log /tmp/install-run-2.log && echo "C4: PASS (idempotent)" || echo "C4: WARN (diff found)"

# Criterion 5: MANIFEST + COMPATIBILITY frozen
python3 iao-middleware/iao_middleware/compatibility.py 2>&1 | grep -q "0 failures" && echo "C5a: PASS" || echo "C5a: FAIL"
test -f iao-middleware/MANIFEST.json && echo "C5b: PASS" || echo "C5b: FAIL"
```

**Step 7 — Write build log final sections:**

Update `docs/kjtcom-build-v10.67.md` with:
- W9 Closing Evaluator Findings section (tier used, synthesis_ratio, scores)
- Phase B Exit Criteria Verification table (5 rows, pass/fail per criterion)
- Phase B readiness decision: **READY FOR v10.68** or **v10.67.1 REQUIRED**
- Wall clock totals

**Step 8 — Write `docs/kjtcom-report-v10.67.md`:**

Using real evaluator scores from `/tmp/eval-v10.67.log`, NOT self-eval. Sections:
- Summary
- Trident (cost/delivery/performance)
- Workstream table (W1-W9, real scores from evaluator)
- Evidence
- What Could Be Better
- Interventions (should be 0)

**Step 9 — Trident parity check:**

```fish
grep "Delivery:" docs/kjtcom-build-v10.67.md docs/kjtcom-report-v10.67.md
```

Must match exactly between build log and report.

**Step 10 — Verify all artifacts:**

```fish
command ls docs/kjtcom-{design,plan,build,report,context}-v10.67.md
command ls docs/kjtcom-context-v10.66-delta-repair.md
command ls docs/kjtcom-report-v10.66-retroactive.md
command ls -l docs/kjtcom-context-v10.67.md  # > 300 KB
```

**Step 11 — Git status (read-only):**

```fish
git status --short
git log --oneline -5
```

**Step 12 — Hand back:**

```fish
printf 'v10.67 complete.

5 primary artifacts on disk: design, plan, build, report, context
2 sidecars: v10.66 retroactive report, v10.66 delta-repair
Wall clock: <X> minutes
Phase B exit criteria: <READY | v10.67.1 REQUIRED>
Closing evaluator: <tier, score summary>

Awaiting human commit.
'
```

**STOP.** Do not commit.

**Success criterion:**
- All 5 primary + 2 sidecar artifacts on disk
- Context bundle > 300 KB with §6 rendered correctly
- Closing evaluator ran and produced real scores
- Phase B exit criteria documented with pass/fail
- Build gatekeeper clean
- Zero git writes

---

## 7. Definition of Done

1. Pre-flight: BLOCKERS pass, NOTEs logged
2. W1: `docs/kjtcom-report-v10.66-retroactive.md` on disk with real evaluator output
3. W2: `docs/kjtcom-context-v10.66-delta-repair.md` on disk with corrected §6
4. W3a: `iao-middleware/lib/` deleted; `iao_middleware/` package structure exists; all shims re-export; imports resolve
5. W3b: `pip show iao-middleware` returns 0.1.0; `from iao_middleware import __version__` returns "0.1.0"; README/CHANGELOG/VERSION/pyproject.toml/.gitignore/ADR-0001 all on disk
6. W4: `iao check config` and extended `iao status` both work
7. W5: `pre_flight.py` and `post_flight.py` both import from `iao_middleware.doctor`; both run end-to-end clean
8. W6: `.iao.json` has `deploy_paused: true`; `deployed_*` checks emit DEFERRED; post-flight exits clean on deploy gap
9. W7: COMPATIBILITY.md passes 11+/11+ locally-testable entries on NZXT
10. W8: Harness ADRs 026/027/028 appended; any W1-derived patterns captured
11. **W9: Qwen Tier 1 evaluator ran on v10.67 (non-negotiable); real scores on disk; Phase B exit criteria verified**
12. 5 primary artifacts on disk (design, plan, build, report, context)
13. 2 sidecar artifacts on disk (retroactive report + delta-repair)
14. Context bundle > 300 KB with §6 rendered correctly
15. Zero git writes
16. Phase B readiness decision documented (READY or v10.67.1 REQUIRED)

---

## 8. Failure Modes Quick Reference

| Failure | Action |
|---|---|
| Pre-flight BLOCKER | Halt. `PRE-FLIGHT BLOCKED: <reason>`. Exit. |
| Pre-flight NOTE | Log. Proceed. |
| W1 evaluator Tier 1 raises EvaluatorSynthesisExceeded | Expected if G97 fix needs work. Tier 2 fires. Log both outcomes. |
| W1 evaluator Tier 2 raises EvaluatorHallucinatedWorkstream | Expected if G98 catches something. Log caught W-ids. |
| W1 both tiers raise | Tier 3 auto-cap. Write report noting this. Forward to W8 as Pattern 31+. |
| W3a import breakage | Max 3 retries. Revert only broken file with `git checkout --`. Continue. Log as tech debt. |
| W3a `git mv` unclear | Use plain `mv` — equivalent for v10.67 since Kyle commits manually. |
| W3b `pip install -e` fails | 3 retries. If unresolvable, skip pip install, leave files on disk, mark C3 at risk, continue. |
| W5 pre/post-flight contract breaks | Revert both scripts. Leave doctor.py unwired. Mark C2 failed. v10.67.1 required. |
| W9 context bundle §6 still errors | Debug forward fix from W3a. Retry once. If still broken, document and continue. |
| **W9 agent wants to skip closing evaluator** | **Re-read plan §2. NOT ACCEPTABLE under any circumstances.** |
| Wall clock > 4 hours | Log hard warning. Triage: W8 ADRs minimal, W7 unchanged, ensure W9 runs. |
| Any git write attempted | Pillar 0 violation. Halt. |

---

## 9. Launch

When Kyle says **"read claude and execute 10.67"** or **"read gemini and execute 10.67"**:

1. Acknowledge in one line
2. Read `CLAUDE.md` or `GEMINI.md` end-to-end (whichever matches the agent)
3. Read `docs/kjtcom-design-v10.67.md` end-to-end
4. Read `docs/kjtcom-plan-v10.67.md` end-to-end (this file)
5. Create `docs/kjtcom-build-v10.67.md` from template in §5
6. Run pre-flight (§4), capture output to build log
7. Begin W1
8. Progress through W2 → W3a → W3b → W4 → W5 → W6 → W7 → W8 → W9 sequentially
9. Run W9 closing sequence in full (including the evaluator)
10. Write build log final sections
11. Write report with real evaluator scores
12. Hand back to Kyle
13. **STOP.** Do not commit.

---

*Plan v10.67 — April 08, 2026. Authored by the planning chat, reviewed and approved by Kyle before "go".*
