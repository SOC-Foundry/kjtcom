# kjtcom — Plan 10.69.0

**Iteration:** 10.69.0 (phase.iteration.run — `.0` = planning draft)
**Phase:** 10 (Harness Externalization + Retrospective)
**Phase position:** Final iteration of Phase 10
**Date:** April 08, 2026
**Repo:** SOC-Foundry/kjtcom
**Machine:** NZXTcos (`~/dev/projects/kjtcom`)
**Wall clock target:** ~4-6 hours, no hard cap
**Executor:** Claude Code (`claude --dangerously-skip-permissions`) OR Gemini CLI (`gemini --yolo`)
**Launch incantation:** **"read claude and execute 10.69"** or **"read gemini and execute 10.69"**
**Input design doc:** `docs/kjtcom-design-10.69.0.md` (immutable per iaomw-G083)
**Input plan doc:** `docs/kjtcom-plan-10.69.0.md` (this file, immutable per iaomw-G083)
**Significance:** Final iteration of kjtcom Phase 10. Closes blocked conditions, transitions kjtcom to steady-state, establishes iao authoring environment.

---

## 1. The Hard Rules

### Pillar 0 — No Git Writes
**You never run `git commit`, `git push`, or `git add`.** Read-only git only. `git mv` for rename tracking is acceptable. `git checkout --` for rollback during failure recovery is acceptable. All commits manual by Kyle after iteration close.

### Pillar 6 — Zero Intervention
**You never ask Kyle for permission.** Log discrepancies, choose safest forward path, proceed. Halt only on hard pre-flight BLOCKERS or destructive irreversible operations.

### W7 Closing Evaluator Non-Negotiable
The closing Qwen evaluator with `--synthesis-mode weighted` is mandatory at W7. Wall clock is not a valid reason to skip. The W1 fixes from earlier in this iteration should make Tier 1 work cleanly. If they don't and evaluator legitimately falls back, document tier-by-tier outcomes per CLAUDE.md §3 / GEMINI.md §3 — but never CHOOSE to skip the attempt.

---

## 2. The 10.66 / 10.67 / 10.68 Failure Modes You Must NOT Repeat

**10.66:** agent skipped closing evaluator to save wall clock with 50 minutes of slack. **Forbidden.**

**10.67:** evaluator ran, both tiers fell back legitimately, agent honestly produced self-eval fallback. **Acceptable.**

**10.68.1:** evaluator ran, both tiers fell back for the same iaomw-G097/G098 reasons, agent honestly produced self-eval fallback AND self-identified the retroactive build log fill as a process failure. **Acceptable but exposed two debts (evaluator hardening, build log auto-append) that 10.69 W1 and W3 close.**

**The pattern:** skipping is a choice, failing is a circumstance. You may never choose to skip. You may document a legitimate failure. **In W7 of this iteration**, the W1 evaluator hardening should resolve the iaomw-G097/G098 issues — if it does, you'll get real Qwen scores. If W1's fixes are insufficient, document tier outcomes honestly and mark D7 as `blocked-by-evaluator-still`, signaling 10.69.2 needs deeper evaluator surgery.

**Build log discipline is W3's specific target.** Once W3 ships the `iao log workstream-complete` command, you MUST use it at the end of every workstream W1-W7. Do not batch build log writes. The 10.68.1 retroactive-fill failure mode is exactly what W3 makes impossible.

---

## 3. Execution Rules

1. **`printf` for multi-line file writes** (iaomw-G001)
2. **`command ls`** for directory listings (iaomw-G022)
3. **Bash defaults to bash; wrap fish with `fish -c "..."`**
4. **No tmux in 10.69** — synchronous only
5. **Max 3 retries per error** (Pillar 7)
6. **`iao registry query "<topic>"` first** for any diligence
7. **Update build log incrementally** via `iao log workstream-complete` (post-W3) or manual append (pre-W3) — **never batch at end**
8. **Never edit design or plan docs** (iaomw-G083)
9. **Never run git writes** (Pillar 0)
10. **Set `IAO_ITERATION=10.69.1`** in pre-flight (NOT `v10.69.1` — no `v` prefix)
11. **Set `IAO_WORKSTREAM_ID=W<N>`** at start of each workstream
12. **Wall clock awareness** at each workstream boundary
13. **Never `cat ~/.config/fish/config.fish`** — Gemini leaks API keys; use `grep -c "# >>> iao" ~/.config/fish/config.fish` for marker checks
14. **`pip install --break-system-packages`** always
15. **W0 runs first** (update `.iao.json current_iteration`)
16. **W3 enables auto-append; from W4 onward, use `iao log workstream-complete` at every workstream boundary**

---

## 4. Pre-Flight Checklist

```fish
# 0. Set iteration env var FIRST (no 'v' prefix)
set -x IAO_ITERATION 10.69.1

# 1. Working directory
cd ~/dev/projects/kjtcom

# 2. Immutable inputs (BLOCKER)
command ls docs/kjtcom-design-10.69.0.md docs/kjtcom-plan-10.69.0.md

# 3. 10.68.1 outputs present (BLOCKER)
command ls docs/kjtcom-design-10.68.0.md docs/kjtcom-plan-10.68.0.md \
           docs/kjtcom-build-10.68.1.md docs/kjtcom-report-10.68.1.md \
           docs/kjtcom-bundle-10.68.1.md

# 4. 10.68 sidecars present (BLOCKER for W2 reference)
command ls docs/classification-10.68.json iao/docs/sterilization-log-10.68.md

# 5. iao package from 10.68 present (BLOCKER)
command ls iao/iao/__init__.py iao/iao/cli.py iao/iao/doctor.py iao/iao/postflight/

# 6. pip install verification (BLOCKER)
pip show iao 2>/dev/null | grep -i "version.*0.1.0" \
    || echo "BLOCKER: iao not installed at 0.1.0"

# 7. iao CLI works (BLOCKER)
iao --version 2>&1 | grep -q "0.1.0" || echo "BLOCKER: iao CLI broken"
iao status 2>&1 | head -5

# 8. Git read-only
git status --short
git log --oneline -5

# 9. Ollama + Qwen (BLOCKER for W1 + W7)
curl -s http://localhost:11434/api/tags > /dev/null && echo "ollama: ok" || echo "BLOCKER: ollama down"
ollama list | grep -i qwen || echo "BLOCKER: qwen not pulled"

# 10. Python deps (BLOCKER)
python3 -c "import litellm, jsonschema; print('python deps ok')"

# 11. Disk (BLOCKER if < 10G)
df -h ~ | tail -1

# 12. Deploy paused flag still set (NOTE — should be from 10.67/10.68)
python3 -c "import json; d = json.load(open('.iao.json')); print('deploy_paused:', d.get('deploy_paused'))"

# 13. .iao.json current state (INFORMATIONAL)
python3 -c "import json; d = json.load(open('.iao.json')); print('current_iteration:', d.get('current_iteration')); print('project_code:', d.get('project_code'))"

# 14. iao authoring location does NOT exist yet (NOTE — W6 creates it)
test -d ~/dev/projects/iao && echo "NOTE: iao authoring location already exists, W6 will not recreate" \
    || echo "iao authoring location absent — W6 will create"

# 15. evaluator script exists for W1 work (BLOCKER)
test -f scripts/run_evaluator.py || echo "BLOCKER: run_evaluator.py missing"
```

**BLOCKER summary:**
- Immutable inputs present
- 10.68.1 outputs present
- 10.68 sidecars present
- iao package present
- pip shows iao 0.1.0
- `iao --version` works
- ollama + qwen
- python deps
- disk > 10G
- evaluator script present

Any BLOCKER → halt with `PRE-FLIGHT BLOCKED: <reason>`, exit.

---

## 5. Build Log Template

Create `docs/kjtcom-build-10.69.1.md` immediately after pre-flight passes:

```markdown
# kjtcom — Build Log 10.69.1

**Iteration:** 10.69.1 (phase 10, iteration 69, run 1 — first execution)
**Agent:** <claude-code|gemini-cli>
**Date:** April 08, 2026
**Machine:** NZXTcos
**Run mode:** Bounded sequential, ~4-6 hour target, no cap
**Significance:** Final iteration of Phase 10 — closes blocked conditions, transitions kjtcom to steady-state, establishes iao authoring environment
**Start:** <timestamp>

## Pre-Flight
## Discrepancies Encountered
## Execution Log (W0 - W7 sections)
## Files Changed
## New Files Created
## Files Deleted
## Wall Clock Log
## W1 Evaluator Hardening Outcomes
## W2 Postflight Refactor Summary
## W7 Closing Evaluator Findings
## Iteration Deliverables Verification (D1-D7)
## Phase 10 Exit Criteria Verification
## Iteration Graduation Recommendation
## Phase 10 Graduation Recommendation
## Files Changed Summary
## What Could Be Better
## Next Iteration Candidates (iao 0.2.0 + Phase 1 launch)

**End:** <timestamp>
**Total wall clock:** <duration>

---
*Build log 10.69.1 — produced by <agent>, April 08, 2026.*
```

Update continuously. The build log is the iteration's narrative AND the input the closing evaluator reads.

**Important:** until W3 ships the `iao log workstream-complete` command, you must manually append entries to the Execution Log section after each workstream completes. Do NOT batch — append per workstream. From W4 onward, use the new command.

---

## 6. Workstream Procedures

### W0 — Update `.iao.json current_iteration` to 10.69.1

**Est:** 2 min
**Pri:** P0
**Deliverable:** Pre-flight step (no D number)
**Blocks on:** Pre-flight green

**Goal:** Ensure `.iao.json current_iteration` reflects 10.69.1 so the iao_logger fix from 10.68.1 W0 picks up the correct iteration for all subsequent event log entries.

**Steps:**

```fish
set -x IAO_WORKSTREAM_ID W0

python3 -c "
import json, pathlib
p = pathlib.Path('.iao.json')
d = json.loads(p.read_text())
d['current_iteration'] = '10.69.1'
p.write_text(json.dumps(d, indent=2) + '\n')
print('current_iteration updated to 10.69.1')
"

# Verify
python3 -c "import json; d = json.loads(open('.iao.json').read()); assert d['current_iteration'] == '10.69.1'; print('verified')"

# Test logger picks up new iteration
python3 -c "
import os
os.environ['IAO_ITERATION'] = '10.69.1'
from iao.logger import log_event
log_event('w0_verification', {'test': True})
"
tail -1 data/event_log.jsonl | grep '"iteration": "10.69.1"' && echo "logger ok" || echo "WARN: logger may need check"
```

**Append to build log Execution Log:**
```markdown
### W0 — Update .iao.json current_iteration

- Set .iao.json current_iteration to 10.69.1
- Verified logger picks up new iteration
- Wall clock: <X>:<Y> - <X>:<Y> (2 min)
```

**Success:** `.iao.json current_iteration` is `10.69.1`. Logger writes new iteration tag.

---

### W1 — Evaluator Tooling Hardening

**Est:** 60 min
**Pri:** P0
**Deliverable:** D1
**Blocks on:** W0 complete

**Goal:** Three concrete fixes to `scripts/run_evaluator.py` so the closing eval at W7 actually produces real Qwen scores instead of falling back to self-eval.

**Step 1 — Read current evaluator structure:**

```fish
set -x IAO_WORKSTREAM_ID W1

# Locate evaluator and understand current artifact loading
grep -n "kjtcom-design\|kjtcom-plan\|kjtcom-build\|kjtcom-report\|kjtcom-bundle\|kjtcom-context" scripts/run_evaluator.py | head -30

# Find synthesis_ratio computation
grep -n "synthesis_ratio\|EvaluatorSynthesisExceeded" scripts/run_evaluator.py | head -20

# Find Gemini Flash schema validation
grep -n "gemini\|schema\|validate" scripts/run_evaluator.py | head -20

# Find workstream ID extraction
grep -n "workstream\|w_count\|extract_workstream" scripts/run_evaluator.py | head -20
```

**Step 2 — Add filename layout resolver:**

Add to `scripts/run_evaluator.py` (or create `iao/iao/evaluator/paths.py` if you want clean separation):

```python
def resolve_artifact_paths(iteration: str, project: str = "kjtcom") -> dict:
    """
    Resolve artifact paths for a given iteration.
    
    Handles both legacy (v10.67) and new (10.69.1) formats.
    For new format, resolves design/plan to .0 and build/report/bundle to actual run.
    """
    import re, pathlib
    
    docs = pathlib.Path("docs")
    paths = {}
    
    # Detect format
    is_new = bool(re.match(r'^\d+\.\d+\.\d+$', iteration))
    is_legacy = bool(re.match(r'^v?\d+\.\d+$', iteration))
    
    if is_new:
        # Parse phase.iter.run
        phase, iter_n, run = iteration.split('.')
        planning_iter = f"{phase}.{iter_n}.0"
        
        paths['design'] = docs / f"{project}-design-{planning_iter}.md"
        paths['plan'] = docs / f"{project}-plan-{planning_iter}.md"
        paths['build'] = docs / f"{project}-build-{iteration}.md"
        paths['report'] = docs / f"{project}-report-{iteration}.md"
        paths['bundle'] = docs / f"{project}-bundle-{iteration}.md"
    elif is_legacy:
        # Strip 'v' if present
        clean = iteration.lstrip('v')
        for kind in ['design', 'plan', 'build', 'report']:
            paths[kind] = docs / f"{project}-{kind}-v{clean}.md"
        # Bundle was called 'context' in legacy era
        paths['bundle'] = docs / f"{project}-context-v{clean}.md"
    else:
        raise ValueError(f"Unrecognized iteration format: {iteration}")
    
    # Verify all exist
    missing = [k for k, v in paths.items() if not v.exists()]
    if missing:
        # Fallback: try alternate spelling (underscore vs dot in filename)
        for k in missing[:]:
            alt = pathlib.Path(str(paths[k]).replace('.', '_', 1).replace('_md', '.md'))
            if alt.exists():
                paths[k] = alt
                missing.remove(k)
    
    if missing:
        raise FileNotFoundError(f"Missing artifacts for {iteration}: {missing}")
    
    return paths
```

Integrate this into the existing artifact-loading code path. Replace any hardcoded `f"docs/kjtcom-design-{iteration}.md"` style construction with `resolve_artifact_paths(iteration)['design']`.

**Step 3 — Add `--synthesis-mode` flag and weighted calculation:**

Locate the synthesis_ratio computation. Currently it raises `EvaluatorSynthesisExceeded` per workstream when ratio > 0.5. Refactor to:

```python
def compute_synthesis_ratios(workstreams_data: list, mode: str = "weighted") -> dict:
    """
    Compute synthesis ratios with three modes:
    - strict: per-workstream gate (legacy behavior)
    - weighted: weighted average across all workstreams (new default)
    - loose: skip synthesis check entirely
    """
    if mode == "loose":
        return {"average": 0.0, "should_fail": False, "per_workstream": {}}
    
    per_ws = {}
    for ws in workstreams_data:
        ws_id = ws.get('id', 'unknown')
        # Existing per-workstream synthesis calculation
        ratio = compute_workstream_synthesis(ws)
        per_ws[ws_id] = ratio
    
    if mode == "strict":
        # Legacy: any single workstream > 0.5 = failure
        should_fail = any(r > 0.5 for r in per_ws.values())
        return {"average": max(per_ws.values(), default=0.0), "should_fail": should_fail, "per_workstream": per_ws}
    
    # weighted: average across all workstreams
    if per_ws:
        avg = sum(per_ws.values()) / len(per_ws)
    else:
        avg = 0.0
    should_fail = avg > 0.5
    return {"average": avg, "should_fail": should_fail, "per_workstream": per_ws}


def normalize_boilerplate(text: str, all_workstream_texts: list) -> str:
    """
    Strip boilerplate phrases that appear in >50% of workstream sections.
    Returns the text with downweighted (truncated) boilerplate.
    """
    from collections import Counter
    
    # Common phrases (3-7 words) that appear across workstreams
    def extract_phrases(t):
        words = t.split()
        return [' '.join(words[i:i+5]) for i in range(len(words) - 4)]
    
    all_phrases = []
    for ws_text in all_workstream_texts:
        all_phrases.extend(extract_phrases(ws_text))
    
    counter = Counter(all_phrases)
    threshold = len(all_workstream_texts) * 0.5
    boilerplate = {phrase for phrase, count in counter.items() if count >= threshold}
    
    # Strip from this text
    normalized = text
    for phrase in boilerplate:
        normalized = normalized.replace(phrase, '[BOILERPLATE]')
    
    return normalized
```

Add CLI flag:
```python
parser.add_argument('--synthesis-mode', choices=['strict', 'weighted', 'loose'], 
                    default='weighted',
                    help='Synthesis ratio calculation mode (default: weighted)')
```

**Step 4 — Add Gemini Flash schema repair pass:**

Locate where Gemini Flash output is validated. Add repair pass:

```python
def repair_gemini_schema(raw_json_str: str, schema: dict) -> tuple:
    """
    Attempt to repair common Gemini Flash schema validation failures.
    Returns (repaired_dict, was_repaired, repair_log).
    """
    import json
    repair_log = []
    
    try:
        data = json.loads(raw_json_str)
    except json.JSONDecodeError as e:
        # Try to extract JSON from markdown code fence
        import re
        m = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', raw_json_str, re.DOTALL)
        if m:
            data = json.loads(m.group(1))
            repair_log.append("extracted JSON from markdown fence")
        else:
            return None, False, [f"unparseable: {e}"]
    
    # Fill missing required fields
    required = schema.get('required', [])
    for field in required:
        if field not in data:
            # Sensible defaults
            if field == 'workstreams':
                data['workstreams'] = []
            elif field in ('iteration', 'summary'):
                data[field] = f"<missing-{field}>"
            elif field == 'trident':
                data['trident'] = {'cost': 'N/A', 'delivery': 'N/A', 'performance': 'N/A'}
            else:
                data[field] = None
            repair_log.append(f"filled missing field: {field}")
    
    # Type coercion for common cases
    if 'workstreams' in data and isinstance(data['workstreams'], dict):
        # Sometimes Gemini returns dict-of-workstreams instead of list
        data['workstreams'] = [{'id': k, **v} for k, v in data['workstreams'].items()]
        repair_log.append("converted workstreams dict to list")
    
    return data, len(repair_log) > 0, repair_log
```

Wire into the Gemini Flash evaluation path: after schema validation fails, attempt repair, log result, retry validation. If still fails, fall through to next tier.

**Step 5 — Add workstream ID alias resolution:**

```python
def resolve_workstream_id_alias(reported_id: str, ground_truth_ids: list) -> str:
    """
    Resolve a model-reported workstream ID against ground truth.
    Handles cases like reported='W3' when ground truth has 'W3a' but no 'W3'.
    """
    # Exact match
    if reported_id in ground_truth_ids:
        return reported_id
    
    # Try sub-lettered match: reported='W3' could mean 'W3a' if W3a exists and W3 doesn't
    matching_subs = [gt for gt in ground_truth_ids if gt.startswith(reported_id) and len(gt) == len(reported_id) + 1]
    if len(matching_subs) == 1:
        return matching_subs[0]
    
    # Try parent match: reported='W3a' could mean 'W3' if W3 exists and W3a doesn't
    if reported_id[-1].isalpha() and reported_id[:-1] in ground_truth_ids:
        return reported_id[:-1]
    
    return reported_id  # No alias found, return as-is and let validation handle it
```

Integrate into the workstream ID validation pass after Gemini Flash output is parsed.

**Step 6 — Write unit tests:**

Create `iao/tests/test_evaluator.py`:

```python
"""Tests for evaluator hardening (10.69 W1)."""
import pytest
from pathlib import Path

# Tests assume run_evaluator.py functions can be imported
import sys
sys.path.insert(0, 'scripts')
from run_evaluator import (
    resolve_artifact_paths,
    compute_synthesis_ratios,
    normalize_boilerplate,
    repair_gemini_schema,
    resolve_workstream_id_alias,
)


def test_resolve_paths_phase_iteration_run(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "kjtcom-design-10.69.0.md").touch()
    (docs / "kjtcom-plan-10.69.0.md").touch()
    (docs / "kjtcom-build-10.69.1.md").touch()
    (docs / "kjtcom-report-10.69.1.md").touch()
    (docs / "kjtcom-bundle-10.69.1.md").touch()
    
    paths = resolve_artifact_paths("10.69.1")
    assert paths['design'].name == "kjtcom-design-10.69.0.md"
    assert paths['build'].name == "kjtcom-build-10.69.1.md"


def test_resolve_paths_legacy(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "kjtcom-design-v10.67.md").touch()
    (docs / "kjtcom-plan-v10.67.md").touch()
    (docs / "kjtcom-build-v10.67.md").touch()
    (docs / "kjtcom-report-v10.67.md").touch()
    (docs / "kjtcom-context-v10.67.md").touch()
    
    paths = resolve_artifact_paths("v10.67")
    assert paths['design'].name == "kjtcom-design-v10.67.md"
    assert paths['bundle'].name == "kjtcom-context-v10.67.md"


def test_synthesis_weighted_mode():
    workstreams = [
        {'id': 'W1', 'text': 'something'},
        {'id': 'W2', 'text': 'something else'},
        {'id': 'W3', 'text': 'high synthesis content'},
    ]
    # In weighted mode, single high-ratio workstream shouldn't trip the gate
    # (assuming weighted average stays under 0.5)
    result = compute_synthesis_ratios(workstreams, mode='weighted')
    assert 'average' in result
    assert 'should_fail' in result


def test_boilerplate_normalizer():
    texts = [
        "Updated MANIFEST.json. Verified imports. Ran tests.",
        "Added new module. Updated MANIFEST.json. Verified imports.",
        "Changed config. Updated MANIFEST.json. Ran tests.",
    ]
    normalized = normalize_boilerplate(texts[0], texts)
    # "Updated MANIFEST.json" appears in all 3 → should be marked boilerplate
    assert "[BOILERPLATE]" in normalized or "MANIFEST" not in normalized


def test_gemini_repair_missing_field():
    raw = '{"iteration": "10.69.1", "summary": "test"}'
    schema = {"required": ["iteration", "summary", "workstreams", "trident"]}
    data, repaired, log = repair_gemini_schema(raw, schema)
    assert data is not None
    assert repaired is True
    assert "workstreams" in data
    assert "trident" in data


def test_workstream_id_alias():
    ground_truth = ['W1', 'W2', 'W3a', 'W3b', 'W4']
    # Reported 'W3' when only 'W3a' exists with that prefix → should return W3a
    # But there are TWO matches (W3a, W3b), so should NOT alias
    assert resolve_workstream_id_alias('W3', ground_truth) == 'W3'  # Ambiguous, return as-is
    
    # Reported 'W5a' when only 'W5' would exist → return W5
    ground_truth_2 = ['W1', 'W2', 'W3', 'W4', 'W5']
    assert resolve_workstream_id_alias('W5a', ground_truth_2) == 'W5'
    
    # Exact match
    assert resolve_workstream_id_alias('W3a', ground_truth) == 'W3a'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

Run tests:
```fish
python3 -m pytest iao/tests/test_evaluator.py -v
```

**Step 7 — Regression test against 10.68.1:**

```fish
python3 scripts/run_evaluator.py \
    --iteration 10.68.1 \
    --rich-context \
    --synthesis-mode weighted \
    --verbose 2>&1 | tee /tmp/eval-10.68.1-rerun.log

grep -E "tier used|synthesis_ratio|score|graduation" /tmp/eval-10.68.1-rerun.log
```

**Expected:** Tier 1 Qwen now produces real output for 10.68.1. If Tier 1 still fails, Tier 2 should produce real output (with repair pass logged). If both still fail, that's a deeper issue and W7 will need to handle it.

**Append to build log:**
```markdown
### W1 — Evaluator Tooling Hardening

- Added resolve_artifact_paths() with phase.iteration.run support + legacy fallback
- Added --synthesis-mode flag with weighted default
- Added boilerplate normalizer
- Added Gemini Flash schema repair pass
- Added workstream ID alias resolution
- Unit tests: 6/6 PASS
- Regression test against 10.68.1: <TIER USED> with synthesis_ratio <RATIO>
- Wall clock: <duration>
```

If you have W3 done at this point (which you don't yet — W3 is later), use `iao log workstream-complete W1 pass "Evaluator hardening shipped"`.

**Failure recovery:**
- Unit test fails → standard 3-retry, revert specific fix
- 10.68.1 regression still falls back → mark D1 PARTIAL, document which fixes worked, continue. W7 will give the real verdict.

**Success:** D1 green. Evaluator hardening shipped.

---

### W2 — Postflight Plugin Loader Refactor

**Est:** 50 min
**Pri:** P0
**Deliverable:** D2
**Blocks on:** W1 complete

**Goal:** iao postflight becomes a plugin loader. kjtcom-specific checks move to `kjtco/postflight/`. iao base ships only universal checks.

**Step 1 — Create kjtco postflight directory:**

```fish
set -x IAO_WORKSTREAM_ID W2

mkdir -p kjtco/postflight
touch kjtco/postflight/__init__.py
```

**Step 2 — Identify which checks are kjtcom-specific:**

```fish
command ls iao/iao/postflight/
# Expected: __init__.py, build_gatekeeper.py, deployed_flutter_matches.py, 
# deployed_claw3d_matches.py, claw3d_version_matches.py, artifacts_present.py,
# firestore_baseline.py, map_tab_renders.py
```

The kjtcom-specific ones (move to kjtco/postflight/):
- `deployed_flutter_matches.py`
- `deployed_claw3d_matches.py`
- `claw3d_version_matches.py`
- `firestore_baseline.py`
- `map_tab_renders.py`

The universal ones (stay in iao/iao/postflight/):
- `build_gatekeeper.py`
- `artifacts_present.py` (after generalization in step 5)

**Step 3 — Move kjtcom-specific checks:**

```fish
git mv iao/iao/postflight/deployed_flutter_matches.py kjtco/postflight/
git mv iao/iao/postflight/deployed_claw3d_matches.py kjtco/postflight/
git mv iao/iao/postflight/claw3d_version_matches.py kjtco/postflight/
git mv iao/iao/postflight/firestore_baseline.py kjtco/postflight/
git mv iao/iao/postflight/map_tab_renders.py kjtco/postflight/
```

**Step 4 — Update moved modules' imports:**

Each moved module probably imported from `iao.postflight.X` or had relative imports. Update each:

```fish
for f in kjtco/postflight/*.py
    sed -i 's|from iao\.postflight\.|from kjtco.postflight.|g' $f
    sed -i 's|from \.|from kjtco.postflight.|g' $f
end
```

Verify each module still imports cleanly:
```fish
for f in kjtco/postflight/*.py
    if test (basename $f) != "__init__.py"
        python3 -c "import sys; sys.path.insert(0, '.'); exec(open('$f').read())" 2>&1 | head -5
    end
end
```

**Step 5 — Generalize `artifacts_present.py`:**

Currently it hardcodes `kjtcom-context-{iteration}.md`. Update to read from `.iao.json bundle_format`:

```fish
view iao/iao/postflight/artifacts_present.py
```

Then edit to read `bundle_format` field:

```python
import json
import pathlib

def check(iteration: str) -> tuple:
    """Verify all expected iteration artifacts are on disk."""
    iao_json = pathlib.Path(".iao.json")
    if not iao_json.exists():
        return ("fail", ".iao.json not found")
    
    config = json.loads(iao_json.read_text())
    bundle_format = config.get("bundle_format", "kjtcom-bundle-{iteration}.md")
    project_prefix = config.get("artifact_prefix", "kjtcom")
    
    # Parse iteration to get planning version
    parts = iteration.split('.')
    if len(parts) == 3:
        planning = f"{parts[0]}.{parts[1]}.0"
    else:
        planning = iteration
    
    docs = pathlib.Path("docs")
    expected = {
        "design": docs / f"{project_prefix}-design-{planning}.md",
        "plan": docs / f"{project_prefix}-plan-{planning}.md",
        "build": docs / f"{project_prefix}-build-{iteration}.md",
        "report": docs / f"{project_prefix}-report-{iteration}.md",
        "bundle": docs / bundle_format.format(iteration=iteration),
    }
    
    missing = [k for k, v in expected.items() if not v.exists()]
    if missing:
        return ("fail", f"missing artifacts: {missing}")
    
    return ("ok", f"all 5 artifacts present")
```

**Step 6 — Create the plugin loader:**

```fish
cat > iao/iao/postflight/loader.py << 'PYEOF'
"""Postflight check plugin loader.

Discovers and loads check modules from both iao base and project-specific paths.
Project checks take precedence on name collision.
"""
import importlib
import importlib.util
import json
import pathlib
from typing import Callable


def discover_iao_checks() -> dict:
    """Scan iao/iao/postflight/ for check modules."""
    checks = {}
    base_dir = pathlib.Path(__file__).parent
    for f in base_dir.glob("*.py"):
        if f.stem in ("__init__", "loader"):
            continue
        try:
            module = importlib.import_module(f"iao.postflight.{f.stem}")
            if hasattr(module, "check"):
                checks[f.stem] = module.check
        except Exception as e:
            pass  # Log but don't crash
    return checks


def discover_project_checks(project_code: str) -> dict:
    """Scan <project_code>/postflight/ for check modules."""
    checks = {}
    proj_dir = pathlib.Path(project_code) / "postflight"
    if not proj_dir.exists():
        return checks
    
    for f in proj_dir.glob("*.py"):
        if f.stem == "__init__":
            continue
        try:
            spec = importlib.util.spec_from_file_location(
                f"{project_code}.postflight.{f.stem}", f
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            if hasattr(module, "check"):
                checks[f.stem] = module.check
        except Exception as e:
            pass  # Log but don't crash
    return checks


def load_all_checks(iao_json_path: str = ".iao.json") -> dict:
    """Combine iao base and project checks. Project takes precedence."""
    iao_checks = discover_iao_checks()
    
    # Read project_code from .iao.json
    iao_json = pathlib.Path(iao_json_path)
    if not iao_json.exists():
        return iao_checks
    
    config = json.loads(iao_json.read_text())
    project_code = config.get("project_code")
    if not project_code:
        return iao_checks
    
    project_checks = discover_project_checks(project_code)
    
    # Merge: project wins on collision
    merged = dict(iao_checks)
    merged.update(project_checks)
    
    # Filter to only enabled checks if specified in .iao.json
    enabled = config.get("postflight_checks")
    if enabled:
        merged = {k: v for k, v in merged.items() if k in enabled}
    
    return merged
PYEOF
```

**Step 7 — Update `iao/iao/postflight/__init__.py` to use the loader:**

```python
"""iao postflight checks."""
from iao.postflight.loader import load_all_checks, discover_iao_checks, discover_project_checks

__all__ = ["load_all_checks", "discover_iao_checks", "discover_project_checks"]
```

**Step 8 — Update `iao/iao/doctor.py` to use the loader:**

Find where doctor.py imports postflight checks. Replace hardcoded imports with:

```python
from iao.postflight import load_all_checks

def _postflight_checks() -> dict:
    """Run all postflight checks via plugin loader."""
    checks = load_all_checks()
    results = {}
    for name, check_fn in checks.items():
        try:
            results[name] = check_fn()
        except Exception as e:
            results[name] = ("fail", f"check error: {e}")
    return results
```

**Step 9 — Update `.iao.json` with `bundle_format` and `postflight_checks`:**

```fish
python3 -c "
import json, pathlib
p = pathlib.Path('.iao.json')
d = json.loads(p.read_text())
d['bundle_format'] = 'kjtcom-bundle-{iteration}.md'
d['postflight_checks'] = [
    'build_gatekeeper',
    'artifacts_present',
    'deployed_flutter_matches',
    'deployed_claw3d_matches',
    'claw3d_version_matches',
    'map_tab_renders',
    'firestore_baseline'
]
p.write_text(json.dumps(d, indent=2) + '\n')
print('postflight config added')
"
```

**Step 10 — Update map_tab_renders.py to honor deploy_paused:**

```fish
view kjtco/postflight/map_tab_renders.py
```

Add deploy_paused check at top of `check()`:

```python
import json, pathlib

def _read_deploy_paused():
    try:
        d = json.loads(pathlib.Path(".iao.json").read_text())
        return d.get("deploy_paused", False), d.get("deploy_paused_since")
    except Exception:
        return False, None

def check():
    paused, since = _read_deploy_paused()
    if paused:
        return ("deferred", f"deploy paused since {since}")
    # ... existing check logic
```

**Step 11 — Verify end-to-end:**

```fish
python3 scripts/post_flight.py 10.69.1 2>&1 | tee /tmp/postflight-w2-test.log
grep -E "ok\]|fail\]|deferred\]|warn\]" /tmp/postflight-w2-test.log
```

Expected:
- `build_gatekeeper`: ok
- `artifacts_present`: depends on whether build/report/bundle exist yet (probably fail at this point — that's fine, will pass at W7)
- `deployed_flutter_matches`: deferred
- `deployed_claw3d_matches`: deferred
- `claw3d_version_matches`: deferred
- `map_tab_renders`: deferred
- `firestore_baseline`: depends on Firestore connectivity

**Append to build log + use iao log workstream-complete (will be available after W3, for now manual append):**

```markdown
### W2 — Postflight Plugin Loader Refactor

- Created kjtco/postflight/ with 5 moved checks
- Generalized artifacts_present.py to read bundle_format from .iao.json
- Created iao/iao/postflight/loader.py with discover + load_all_checks
- Updated doctor.py to use plugin loader
- Updated .iao.json with bundle_format + postflight_checks fields
- Updated map_tab_renders.py to honor deploy_paused flag
- End-to-end post_flight.py run: <results>
- Wall clock: <duration>
```

**Failure recovery:**
- Plugin loader can't find a moved check → fall back to direct imports for that check, document gap
- Import break → standard 3-retry, revert specific file

**Success:** D2 green.

---

### W3 — Build Log Auto-Append Hook

**Est:** 35 min
**Pri:** P0
**Deliverable:** D3
**Blocks on:** W2 complete

**Goal:** Eliminate retroactive build-log-fill failure mode via `iao log workstream-complete` command.

**Step 1 — Create `iao/iao/log.py`:**

```fish
set -x IAO_WORKSTREAM_ID W3

cat > iao/iao/log.py << 'PYEOF'
"""iao log — workstream completion logging for build logs."""
import datetime
import json
import os
import pathlib
import re
from typing import Optional


def workstream_complete(
    workstream_id: str,
    status: str,
    summary: str,
    build_log_path: Optional[str] = None,
) -> tuple:
    """
    Append a workstream completion entry to the iteration's build log.
    
    Args:
        workstream_id: e.g. "W1", "W3a"
        status: one of "pass", "partial", "fail"
        summary: one-sentence summary of what completed
        build_log_path: explicit path, else auto-detect from .iao.json
    
    Returns: (status, message)
    """
    if status not in ("pass", "partial", "fail"):
        return ("fail", f"invalid status: {status}")
    
    if not build_log_path:
        # Auto-detect from .iao.json
        try:
            iao_json = pathlib.Path(".iao.json")
            config = json.loads(iao_json.read_text())
            iteration = config.get("current_iteration")
            project = config.get("artifact_prefix", "kjtcom")
            if not iteration:
                return ("fail", ".iao.json missing current_iteration")
            build_log_path = f"docs/{project}-build-{iteration}.md"
        except Exception as e:
            return ("fail", f"could not auto-detect build log: {e}")
    
    build_log = pathlib.Path(build_log_path)
    if not build_log.exists():
        return ("fail", f"build log not found: {build_log_path}")
    
    # Construct entry
    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    status_marker = {"pass": "✓", "partial": "⚠", "fail": "✗"}[status]
    
    entry = f"\n### {workstream_id} {status_marker} {status.upper()}\n\n"
    entry += f"**Completed:** {timestamp}\n"
    entry += f"**Summary:** {summary}\n"
    
    # Atomic append
    try:
        with open(build_log, "a") as f:
            f.write(entry)
    except Exception as e:
        return ("fail", f"append error: {e}")
    
    return ("ok", f"appended {workstream_id} entry to {build_log_path}")


def check_build_log_complete(
    build_log_path: Optional[str] = None,
    expected_workstreams: Optional[list] = None,
) -> tuple:
    """
    Verify build log contains entries for all expected workstreams.
    
    Returns: (status, message)
    """
    if not build_log_path:
        try:
            iao_json = pathlib.Path(".iao.json")
            config = json.loads(iao_json.read_text())
            iteration = config.get("current_iteration")
            project = config.get("artifact_prefix", "kjtcom")
            build_log_path = f"docs/{project}-build-{iteration}.md"
        except Exception:
            return ("fail", "could not auto-detect build log")
    
    build_log = pathlib.Path(build_log_path)
    if not build_log.exists():
        return ("fail", f"build log not found: {build_log_path}")
    
    text = build_log.read_text()
    
    # Find all W## entries
    found = set(re.findall(r'### (W\d+[a-z]?)', text))
    
    if expected_workstreams:
        missing = set(expected_workstreams) - found
        if missing:
            return ("warn", f"missing entries: {sorted(missing)}")
    
    return ("ok", f"found {len(found)} workstream entries: {sorted(found)}")


if __name__ == "__main__":
    import sys
    cmd = sys.argv[1] if len(sys.argv) > 1 else None
    if cmd == "workstream-complete":
        if len(sys.argv) < 5:
            print("usage: iao log workstream-complete <W#> <pass|partial|fail> <summary>")
            sys.exit(2)
        result = workstream_complete(sys.argv[2], sys.argv[3], " ".join(sys.argv[4:]))
        print(f"[{result[0]}] {result[1]}")
        sys.exit(0 if result[0] == "ok" else 1)
    else:
        print("usage: iao log workstream-complete <W#> <status> <summary>")
        sys.exit(2)
PYEOF
```

**Step 2 — Wire `iao log` subcommand into cli.py:**

```fish
view iao/iao/cli.py
```

Add a `log` subcommand handler:

```python
def cmd_log(args):
    if args.action == "workstream-complete":
        from iao.log import workstream_complete
        result = workstream_complete(args.workstream_id, args.status, args.summary)
        print(f"[{result[0]}] {result[1]}")
        return 0 if result[0] == "ok" else 1
    return 2

# In main():
log_parser = subparsers.add_parser("log", help="Iteration logging commands")
log_subparsers = log_parser.add_subparsers(dest="action")
ws_parser = log_subparsers.add_parser("workstream-complete", help="Append workstream completion entry")
ws_parser.add_argument("workstream_id")
ws_parser.add_argument("status", choices=["pass", "partial", "fail"])
ws_parser.add_argument("summary")
```

**Step 3 — Add post-flight check `build_log_complete`:**

```fish
cat > iao/iao/postflight/build_log_complete.py << 'PYEOF'
"""Post-flight check: verify build log contains entries for all workstreams."""
from iao.log import check_build_log_complete

def check():
    return check_build_log_complete()
PYEOF
```

Add to `.iao.json postflight_checks` list:

```fish
python3 -c "
import json, pathlib
p = pathlib.Path('.iao.json')
d = json.loads(p.read_text())
if 'build_log_complete' not in d['postflight_checks']:
    d['postflight_checks'].insert(2, 'build_log_complete')
p.write_text(json.dumps(d, indent=2) + '\n')
"
```

**Step 4 — Test:**

```fish
# Create a test build log
cat > /tmp/test-build.md << 'EOF'
# Test Build Log

## Execution Log
EOF

# Append a test entry
python3 -m iao.log workstream-complete W1 pass "test summary" 2>&1
# Should fail because /tmp/test-build.md isn't the .iao.json-configured location

# Test via CLI with explicit build log
python3 iao/iao/log.py workstream-complete W1 pass "test summary"
# Same — auto-detect from .iao.json which points at the real build log

# Verify against actual build log
iao log workstream-complete W3 pass "Build log auto-append hook shipped"
tail -10 docs/kjtcom-build-10.69.1.md
```

**Step 5 — Write unit test:**

```fish
cat > iao/tests/test_log.py << 'PYEOF'
"""Tests for iao.log."""
import json
import pathlib
import pytest
import tempfile
from iao.log import workstream_complete, check_build_log_complete


def test_workstream_complete_appends(tmp_path):
    build_log = tmp_path / "test-build.md"
    build_log.write_text("# Test Build Log\n\n## Execution Log\n")
    
    result = workstream_complete("W1", "pass", "test summary", str(build_log))
    assert result[0] == "ok"
    
    content = build_log.read_text()
    assert "### W1" in content
    assert "PASS" in content
    assert "test summary" in content


def test_workstream_complete_invalid_status(tmp_path):
    build_log = tmp_path / "test-build.md"
    build_log.write_text("# Test\n")
    
    result = workstream_complete("W1", "weird", "summary", str(build_log))
    assert result[0] == "fail"


def test_check_build_log_complete(tmp_path):
    build_log = tmp_path / "test-build.md"
    build_log.write_text("""# Test
### W1 PASS
### W2 PASS
### W3 PASS
""")
    
    result = check_build_log_complete(str(build_log), ["W1", "W2", "W3"])
    assert result[0] == "ok"
    
    result_missing = check_build_log_complete(str(build_log), ["W1", "W2", "W3", "W4"])
    assert result_missing[0] == "warn"
    assert "W4" in result_missing[1]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
PYEOF

python3 -m pytest iao/tests/test_log.py -v
```

**Step 6 — Use the new command for THIS workstream's completion:**

```fish
iao log workstream-complete W3 pass "Build log auto-append hook shipped, command + post-flight check + tests"
```

**From W4 onward, every workstream MUST end with `iao log workstream-complete`.**

**Failure recovery:**
- `iao log` command fails → manual append, mark D3 PARTIAL, document
- Atomic append fails → fall back to non-atomic, mark D3 PARTIAL

**Success:** D3 green.

---

### W4 — Phase 10 Charter Retrofit

**Est:** 25 min
**Pri:** P0
**Deliverable:** D4
**Blocks on:** W3 complete

**Goal:** Write Phase 10 charter to disk, commit it as canonical Phase 10 history, add iaomw-Pattern-31 to base.md.

**Step 1 — Create phase-charters directory:**

```fish
set -x IAO_WORKSTREAM_ID W4

mkdir -p docs/phase-charters
```

**Step 2 — Write the Phase 10 charter:**

Copy §1 Phase Charter from `docs/kjtcom-design-10.69.0.md` (this iteration's design) into a standalone file. The charter content is already authored — just extract and save:

```fish
# Read design doc, extract §1 Phase Charter section
python3 << 'PYEOF'
import re, pathlib

design = pathlib.Path("docs/kjtcom-design-10.69.0.md").read_text()

# Extract from "## 1. Phase Charter" to "## 2. Why 10.69 Exists"
m = re.search(r'## 1\. Phase Charter.*?(?=## 2\. )', design, re.DOTALL)
if not m:
    print("FAIL: could not extract Phase Charter section")
    exit(1)

charter_content = m.group(0)

# Wrap in standalone doc structure
output = f"""# kjtcom Phase 10 Charter

**Project:** kjtcom
**Phase:** 10
**Status:** active (graduating at 10.69.X close)
**Document type:** standalone phase charter
**Source:** retroactively extracted from kjtcom-design-10.69.0.md §1
**Authored:** 2026-04-08 (10.69.1 W4)

---

{charter_content}

---

*This document is canonical Phase 10 history for kjtcom. It pairs with the
phase-iteration design docs that referenced it. Future engineers reading
kjtcom's evolution should start here for strategic context, then read
individual iteration design docs (10.66.0 through 10.69.0) for tactical
detail.*
"""

pathlib.Path("docs/phase-charters/kjtcom-phase-10.md").write_text(output)
print("Phase 10 charter written to docs/phase-charters/kjtcom-phase-10.md")
PYEOF
```

**Step 3 — Create phase-charters README:**

```fish
cat > docs/phase-charters/README.md << 'EOF'
# Phase Charters

This directory contains canonical phase charters for kjtcom. Phase charters
are strategic-level documents that frame iterations within a phase.

## What is a phase charter

Every iteration's design doc §1 is a Phase Charter section. Charters live
here as standalone history. Future engineers reading kjtcom's evolution can
trace phases via this directory.

## Format

See `iao/templates/phase-charter-template.md` (after W4 of 10.69.1) for the
canonical template. Charter sections include:

- Why this phase exists (elevator pitch)
- Phase objectives (3-7 high-level goals)
- Phase entry criteria (where we started)
- Phase exit criteria (graduation conditions, machine-checkable)
- Iterations planned (forward sketch, revisable)
- Current iteration position
- Charter revision history

## Charters in this directory

| File | Phase | Status | Notes |
|---|---|---|---|
| kjtcom-phase-10.md | 10 | active | Harness Externalization + Retrospective. Retroactively documented at 10.69 W4. |

## Future projects

iao itself, intra, and any future iao-ecosystem project should produce its
own `<project>-phase-<N>.md` charter at the start of each phase, following
the canonical template.
EOF
```

**Step 4 — Create the phase charter template at `iao/templates/`:**

```fish
mkdir -p iao/templates
cat > iao/templates/phase-charter-template.md << 'EOF'
# <Project> Phase <N> Charter

**Project:** <project name>
**Phase:** <N>
**Status:** draft | active | graduated | archived
**Document type:** standalone phase charter
**Authored:** <YYYY-MM-DD>

---

## Phase Charter

**Phase:** <N> — <descriptive name>
**Status:** <status>
**Charter author:** <engineer name or "iao planning chat">
**Charter version:** 0.1
**Charter date:** <YYYY-MM-DD>

### Why This Phase Exists

<2-4 sentences explaining what problem this phase solves and why it
needed to be its own phase rather than rolled into the previous one.
This is the elevator pitch — if a new engineer joined the project
mid-phase, this paragraph tells them what they're walking into.>

### Phase Objectives

<3-7 high-level goals for this entire phase. Each objective is a
sentence or two, not a workstream list. Phase objectives are for the
phase, not for any single iteration.>

1. <objective 1>
2. <objective 2>
3. <objective 3>

### Phase Entry Criteria

<What was true when this phase began. The "where we started" snapshot.
3-7 bullet points enumerating concrete starting conditions.>

- <criterion 1>
- <criterion 2>

### Phase Exit Criteria (Graduation Conditions)

<What must be true for this phase to graduate. Each criterion is
machine-checkable where possible.>

- [ ] <exit criterion 1>
- [ ] <exit criterion 2>
- [ ] <exit criterion 3>

### Iterations Planned in This Phase

<Forward sketch — revisable as the phase progresses.>

| Iteration | Scope | Status |
|---|---|---|
| <N>.0 | <scope> | <planned/active/graduated> |
| <N>.1 | <scope> | <status> |

### Current Iteration Position

**Currently executing:** <N>.<M>.<R>
**Iterations completed in this phase:** <list>
**Iterations remaining (estimated):** <list>
**Phase progress:** <X of Y planned iterations>

### Phase Charter Revision History

| Version | Date | Iteration | Change |
|---|---|---|---|
| 0.1 | <YYYY-MM-DD> | <iter>.0 | Initial charter draft |
EOF
```

**Step 5 — Add iaomw-Pattern-31 to base.md:**

```fish
view iao/docs/harness/base.md
# Find the Patterns section and append the new entry
```

Append to the Patterns section of `iao/docs/harness/base.md`:

```markdown
### iaomw-Pattern-31: Phase Charters as Strategic Layer

**Context:** Iterations are tactical (what to do this week). Phases are
strategic (what we're trying to accomplish over multiple iterations).
Without explicit phase charters, iteration scopes drift and engineers
lose track of why they're iterating.

**Pattern:** Every project authoring iao-ecosystem design docs includes
a §1 Phase Charter section with: phase name, why-this-phase-exists,
phase objectives, entry criteria, exit criteria, iterations planned,
current position, and revision history. Charter is written at phase
start (or retroactively if retrofit), revised as iterations surface
new realities, and committed to design history as
`docs/phase-charters/<project>-phase-<N>.md`.

**Discovered:** kjtcom Phase 10 was authored without a formal charter.
The phase wandered into iao-middleware externalization, classification
taxonomy, dash/underscore renames, and bundle reformatting without
clear strategic framing. Retroactive charter at kjtcom 10.69 W4
captured the phase's actual shape. Future phases author charters at
start.

**Rationale for extension-only:** Phase charters are forward-looking
strategic documents. They enforce discipline at the multi-iteration
level. Engineers consuming iao learn this pattern from base, write
their own charters, and build their projects with explicit phase
structure from day one.
```

**Step 6 — Update kjtco/docs/harness/project.md to acknowledge new base IDs:**

Add `iaomw-Pattern-31` to the project harness's acknowledgment list in its header.

**Step 7 — Verify:**

```fish
command ls docs/phase-charters/kjtcom-phase-10.md docs/phase-charters/README.md iao/templates/phase-charter-template.md
grep -c "iaomw-Pattern-31" iao/docs/harness/base.md
grep -c "iaomw-Pattern-31" kjtco/docs/harness/project.md
iao check harness  # Should be clean
```

**Use iao log:**

```fish
iao log workstream-complete W4 pass "Phase 10 charter retrofit + template + iaomw-Pattern-31 added"
```

**Success:** D4 green.

---

### W5 — kjtcom Steady-State Transition

**Est:** 30 min
**Pri:** P0
**Deliverable:** D5
**Blocks on:** W4 complete

**Goal:** kjtcom transitions from active development lab to steady-state production reference. NOT shutdown — continues running production, gets occasional updates, but at much lower cadence with lighter ceremony.

**Step 1 — Add mode field to .iao.json:**

```fish
set -x IAO_WORKSTREAM_ID W5

python3 -c "
import json, pathlib
p = pathlib.Path('.iao.json')
d = json.loads(p.read_text())
d['mode'] = 'steady-state'
d['mode_since'] = '2026-04-08'
d['mode_rationale'] = 'kjtcom is the original IAO POC. It graduated from active development at the end of Phase 10. It continues as a production reference site for show browsing, with minimal schema/query/pipeline updates as needed, on a much lower cadence than Phase 10 development.'
p.write_text(json.dumps(d, indent=2) + '\n')
print('mode set to steady-state')
"
```

**Step 2 — Create maintenance directory + README:**

```fish
mkdir -p docs/maintenance

cat > docs/maintenance/README.md << 'EOF'
# kjtcom Maintenance Notes

This directory holds maintenance notes for kjtcom in steady-state mode
(post-Phase-10).

## When to write a maintenance note vs a full iteration

**Write a maintenance note** for routine work:
- Schema migrations (Firestore field additions, type tweaks)
- Query updates (new filter combinations, performance tuning)
- Dependency bumps (Flutter, Python deps, Firebase SDK)
- Single-pipeline schema additions
- Hotfixes
- Minor README updates
- Production data refreshes

**Write a full iteration** (design + plan + build + report + bundle) for:
- New feature work that touches multiple files
- Major refactors
- Harness sync from iao that requires testing
- New pipeline addition
- Architecture changes
- Anything you want the planning chat to review

## Maintenance note format

Filename: `YYYY-MM-<short-description>.md`

Content (lightweight):

```markdown
# kjtcom Maintenance Note — <description>

**Date:** <YYYY-MM-DD>
**Maintainer:** Kyle
**Type:** schema | query | dep | hotfix | data | other

## What

<one paragraph: what changed>

## Why

<one paragraph: why it changed>

## Files Touched

- file1
- file2

## Verification

<one paragraph: how it was verified>

## iao base sync needed?

<yes/no, and if yes, what to acknowledge in kjtco/docs/harness/project.md>
```

That's it. No 5 artifacts. No evaluator. Single-file note.

## When to escalate to a full iteration

If you find yourself writing a maintenance note that touches more than ~5
files, makes architectural decisions, or needs review — stop and write a
full iteration design doc instead. Maintenance notes are for routine work,
not for thinking through complex changes.

## Iao base updates

When iao iterates and adds new patterns/ADRs/gotchas, kjtcom needs to
acknowledge them in `kjtco/docs/harness/project.md` header on next
maintenance touch. Run `iao check harness` to see what needs acknowledging.
EOF
```

**Step 3 — Create maintenance guide:**

```fish
cat > docs/kjtcom-maintenance-guide.md << 'EOF'
# kjtcom Maintenance Guide

**Status as of 2026-04-08:** kjtcom has transitioned to steady-state mode
following the graduation of Phase 10 (Harness Externalization + Retrospective).

## What kjtcom is now

kjtcom is:
- A production reference site at kylejeromethompson.com
- A working show-browsing tool for California's Gold, Rick Steves' Europe,
  Diners Drive-Ins and Dives, and Anthony Bourdain content
- The original IAO methodology POC, preserved as a working example
- A reference implementation that other iao-ecosystem projects can study

## What kjtcom is not (anymore)

kjtcom is no longer:
- The active development lab for the iao methodology (that's the iao
  project at ~/dev/projects/iao/ now)
- The primary venue for new harness work, evaluator improvements, or
  pattern discoveries (those happen in iao now)
- An iteration-cadence project (it was iterating daily-to-weekly during
  Phase 10; now it iterates on demand, possibly weeks-to-months between
  touches)

## Maintenance workflow

### Routine maintenance (most common)

For schema updates, query tweaks, dependency bumps, hotfixes, or production
data refreshes:

1. Make the change
2. Test it locally
3. Write a maintenance note in `docs/maintenance/YYYY-MM-<description>.md`
   following the format in `docs/maintenance/README.md`
4. Manually commit + push (no IAO ceremony needed)
5. If deploys are paused, unpause via `.iao.json deploy_paused: false`,
   deploy, re-pause if appropriate

### Full iteration (rare)

For new feature work, major refactors, architectural changes, or anything
you want the planning chat to review:

1. Open a planning chat session
2. Bring the latest kjtcom bundle (or generate one with
   `python3 scripts/build_bundle.py --iteration <next-iteration>`)
3. Discuss scope, get design + plan from planning chat
4. Execute as a full IAO iteration (W0, W1, ..., closing eval, graduation)
5. Iteration counter continues from wherever Phase 10 left off (10.70+)

### iao base sync

When iao iterates (iao 0.2.0, 0.3.0, etc.) and adds new patterns or ADRs
to base.md, kjtcom should acknowledge them on next maintenance touch:

1. Run `iao check harness` from kjtcom directory
2. Note any Rule C warnings (unacknowledged base IDs)
3. Update `kjtco/docs/harness/project.md` header acknowledgment list
4. Re-run `iao check harness` — should be clean

This sync is lightweight and happens during routine maintenance. It does
not require its own iteration.

## Production system

| Component | Status | Notes |
|---|---|---|
| kylejeromethompson.com (Flutter) | Production | v10.65 deployed (deploy paused since 10.67) |
| Firestore (kjtcom-c78cd) | Production | 6,785 entities across 4 pipelines |
| Google Places enrichment | Production | Stable |
| Telegram bot | Production | Read-only, query-mode |
| Pipelines (calgold, ricksteves, tripledb, bourdain) | Production frozen | No new processing planned |

## Production data

| Pipeline | Entities | Coverage |
|---|---|---|
| calgold | 899 | Complete (Huell Howser California's Gold) |
| ricksteves | 4,182 | Complete (Rick Steves' Europe) |
| tripledb | 1,100 | Complete (Diners Drive-Ins and Dives) |
| bourdain | 604 | Complete (No Reservations + Parts Unknown subset) |

If new episodes need to be added (e.g., Parts Unknown 115+), that's a
maintenance task. The pipeline scripts in `scripts/pipelines/` are still
operational.

## Harness state

kjtcom's harness lives at `kjtco/docs/harness/project.md` (kjtcom-specific
content) and extends `iao/docs/harness/base.md` (universal content).

`iao check harness` verifies alignment. Run it at the start of any
maintenance work to ensure base hasn't drifted in a way that requires
acknowledgment.

## Emergency contact

Kyle Thompson, VP Engineering, TachTech Engineering. kjtcom is a personal
production system but uses some of the same infrastructure patterns
(IAO methodology) that TachTech engineers use professionally. For
pattern questions, refer to iao project at ~/dev/projects/iao/.
EOF
```

**Step 4 — Write inaugural maintenance note:**

```fish
cat > docs/maintenance/2026-04-graduation.md << 'EOF'
# kjtcom Maintenance Note — Phase 10 Graduation

**Date:** 2026-04-08
**Maintainer:** Kyle (via 10.69.1 execution)
**Type:** other (graduation)

## What

kjtcom transitioned from active development mode (Phase 10) to steady-state
mode. `.iao.json` now has `mode: steady-state`. Maintenance guide and
maintenance directory established. Future work happens at lower cadence.

## Why

Phase 10's objectives are met:
- Harness externalized as iao package
- Standalone-repo authoring conventions established
- POC knowledge harvested into iao base via classification
- Phase/iteration/run formal numbering adopted
- 5-char project code taxonomy applied
- iao delivered to P3 as physical zip artifact (10.68.1 W9)
- iao authoring environment established at ~/dev/projects/iao/ (10.69.1 W6)

kjtcom continues as production reference site. iao becomes the active
development venue.

## Files Touched

- .iao.json (mode field added)
- docs/kjtcom-maintenance-guide.md (created)
- docs/maintenance/README.md (created)
- docs/maintenance/2026-04-graduation.md (this file)
- README.md (status updated)

## Verification

- `iao status` shows mode: steady-state
- Maintenance guide is on disk and readable
- This inaugural maintenance note exists

## iao base sync needed?

No — this transition is the act of graduating. iao base is at v0.1.0
and aligned with kjtco/docs/harness/project.md as of 10.68.1.
EOF
```

**Step 5 — Update README.md:**

```fish
view README.md | head -30
```

Edit the project root README.md to add (or update) a status section:

```markdown
## Status

kjtcom is the original IAO methodology POC. As of Phase 10 graduation
(April 2026), kjtcom has transitioned to **steady-state production
reference mode**. It continues to run as a show-browsing tool and serves
as a working example of an IAO-pattern project.

Active development lab activity has moved to the **iao project** at
`~/dev/projects/iao/`. For future kjtcom maintenance, see
`docs/kjtcom-maintenance-guide.md`.
```

**Step 6 — Verify:**

```fish
iao status  # should show mode: steady-state
command ls docs/kjtcom-maintenance-guide.md docs/maintenance/README.md docs/maintenance/2026-04-graduation.md
grep -i "steady-state" README.md
```

**Use iao log:**

```fish
iao log workstream-complete W5 pass "kjtcom transitioned to steady-state mode with maintenance guide and inaugural note"
```

**Failure recovery:**
- `iao status` doesn't recognize `mode` field → that's fine for 10.69, mark D5 PARTIAL with note "iao tooling will read mode field in iao 0.2.0+"

**Success:** D5 green.

---

### W6 — iao Authoring Environment Setup

**Est:** 40 min
**Pri:** P0
**Deliverable:** D6
**Blocks on:** W5 complete

**Goal:** Establish `~/dev/projects/iao/` as the iao authoring location, separate from kjtcom. iao gets its own `.iao.json`, its own iteration counter starting at 0.1.0.

**Step 1 — Create directory and copy iao codebase:**

```fish
set -x IAO_WORKSTREAM_ID W6

mkdir -p ~/dev/projects/iao
cp -r ~/dev/projects/kjtcom/iao/. ~/dev/projects/iao/
command ls ~/dev/projects/iao/
```

**Step 2 — Create iao's own .iao.json:**

```fish
cat > ~/dev/projects/iao/.iao.json << 'EOF'
{
  "iao_version": "0.1",
  "name": "iao",
  "project_code": "iaomw",
  "artifact_prefix": "iao",
  "current_iteration": "0.1.0",
  "phase": 0,
  "mode": "active-development",
  "evaluator_default_tier": "qwen",
  "deploy_paused": false,
  "created_at": "2026-04-08T00:00:00+00:00",
  "bundle_format": "iao-bundle-{iteration}.md",
  "postflight_checks": [
    "build_gatekeeper",
    "artifacts_present",
    "build_log_complete"
  ]
}
EOF
```

**Step 3 — Initialize as standalone git repo (LOCAL ONLY, no remote, no add, no commit):**

```fish
cd ~/dev/projects/iao
git init
# DO NOT git add. DO NOT git commit. Leave staging for Kyle's manual first commit.
git status --short | head -10
cd ~/dev/projects/kjtcom
```

**Step 4 — Create iao authoring directory structure:**

```fish
mkdir -p ~/dev/projects/iao/docs/phase-charters
mkdir -p ~/dev/projects/iao/deliverables

# Copy P3 zip into iao deliverables (it was originally produced from kjtcom)
cp ~/dev/projects/kjtcom/deliverables/iao-v0.1.0-alpha.zip ~/dev/projects/iao/deliverables/ 2>/dev/null \
    || echo "NOTE: P3 zip not in expected location, manual copy may be needed"
```

**Step 5 — Write iao 0.1.0 design stub:**

```fish
cat > ~/dev/projects/iao/docs/iao-design-0.1.0.md << 'EOF'
# iao — Design 0.1.0

**Iteration:** 0.1.0 (phase 0, iteration 1, run 0)
**Phase:** 0 — Project Setup and Build-Out
**Date:** 2026-04-08
**Repo:** (local only, no github yet)
**Machine:** NZXTcos (~/dev/projects/iao/)
**Significance:** First iao iteration authored in iao's own project location, separate from kjtcom.

---

## 1. Phase Charter

**Phase:** 0 — Project Setup and Build-Out
**Status:** active
**Charter author:** iao planning chat
**Charter version:** 0.1
**Charter date:** 2026-04-08

### Why This Phase Exists

iao was authored inside kjtcom during kjtcom Phase 10. Phase 0 of iao itself
is "establish iao as a standalone authorable project with its own iteration
history, separate from any consumer." This phase exists so iao stops being
a sub-project of kjtcom and becomes its own thing.

Phase 0 is always the project setup and build-out phase. Every project in
the iao ecosystem has a Phase 0. For iao itself, Phase 0 is unusual in that
it follows extraction from a parent project (kjtcom Phase 10). For new
projects starting fresh, Phase 0 will look more like greenfield bring-up.

### Phase Objectives

1. iao authoring lives at ~/dev/projects/iao/ separate from kjtcom
2. iao iteration history starts at 0.1.0 with this design doc
3. First non-extraction iao iteration scope is defined (will be 0.2.0)
4. P3 bring-up zip remains synced with iao authoring location (not kjtcom)
5. iao's own evaluator runs locally from iao directory (not from kjtcom's)
6. iao's own bundle format and post-flight configuration verified

### Phase Entry Criteria

- iao codebase exists at v0.1.0 with full Phase A externalization complete
- kjtcom Phase 10 graduating (10.69.X)
- P3 zip exists in kjtcom deliverables (synced to iao deliverables in W6)
- iao runs cleanly via `pip install -e` on NZXT (achieved via kjtcom 10.67)
- iaomw-Pattern-31 (Phase Charters) established in base.md (kjtcom 10.69 W4)

### Phase Exit Criteria

- [ ] iao authored at ~/dev/projects/iao/ with own git repo (this iteration W6 of kjtcom 10.69)
- [ ] iao 0.1.0 design + plan + first iteration artifacts on disk (this iteration)
- [ ] iao's first independent iteration (0.2.0) planned (next session)
- [ ] P3 zip synced from iao authoring location (W6 step 4)
- [ ] iao authoring environment validated with `iao status` from iao directory (W6 step 7)
- [ ] iao 0.2.0 design + plan produced and ready to execute

### Iterations Planned in This Phase

| Iteration | Scope | Status |
|---|---|---|
| 0.1.0 | Authoring environment establishment (this iteration, established by kjtcom 10.69 W6) | active |
| 0.2.0 | Phase 1 launch — Universal Consumer (bridge files, iao consult, iao operator run) | planned |

### Current Iteration Position

**Currently executing:** 0.1.0 (authoring environment setup, established by kjtcom 10.69 W6)
**Iterations completed in this phase:** none
**Iterations remaining (estimated):** 0.1.X (any cleanup), then graduate to Phase 1 with 0.2.0

### Phase Charter Revision History

| Version | Date | Iteration | Change |
|---|---|---|---|
| 0.1 | 2026-04-08 | kjtcom 10.69.1 W6 | Initial charter, retroactively documented as iao 0.1.0 phase 0 starting point |

---

## 2. Why 0.1.0 Exists

iao Phase 0 starts with a single iteration (0.1.0) that establishes iao as
its own project. This iteration was largely set up by kjtcom 10.69 W6 — the
directory exists, the .iao.json exists, the codebase is copied from kjtcom.

What 0.1.0 needs to add (in a future planning session, not in this stub):

1. iao's own README narrative (currently inherited from kjtcom; needs iao-voice rewrite)
2. iao's own CHANGELOG narrative (same)
3. Verification that all iao tests pass from the iao directory (not kjtcom directory)
4. iao's first own bundle (~/dev/projects/iao/docs/iao-bundle-0.1.0.md)
5. iao's own classification audit (does iao need to retag anything? probably no, but verify)
6. Phase 0 exit criteria verification

This stub design doc gets fleshed out in a future iao 0.1.0 planning session.
For now, it exists so iao has a starting point.

---

## 3. Forward Context — iao Phase 1 (Universal Consumer)

After Phase 0 graduates, iao Phase 1 begins with iteration 0.2.0.

Phase 1 — Universal Consumer:
- Bridge files at ~/.claude/CLAUDE.md and ~/.gemini/GEMINI.md (default-on,
  override-able)
- `iao consult` command (universal entry point for "I'm an LLM, what should
  I know about this folder")
- `iao operator run` command (Qwen direct invocation for orchestrator-
  delegated tasks)
- `~/.iao/global.json` config for non-project iao usage
- Token-efficient context delivery (relevant subset matching)

See `~/dev/projects/kjtcom/docs/kjtcom-design-10.69.0.md` §10 for full
forward context on Phase 1.

---

## 4. Status

This is a stub. Full iao 0.1.0 design will be authored in a future planning
session. The stub exists so:

1. iao authoring environment has a starting point on disk
2. Phase 0 charter is committed to iao history
3. The phase.iteration.run format is established for iao from day one
4. Future iao iterations have a precedent file format to follow

---

*Design 0.1.0 (stub) — April 08, 2026. Authored as part of kjtcom 10.69.1
W6. Will be fleshed out in a future iao planning session before iao 0.1.0
executes.*
EOF
```

**Step 6 — Document the authoring/vendoring relationship:**

```fish
cat > ~/dev/projects/iao/docs/README.md << 'EOF'
# iao Documentation

## What iao is

iao (Iterative Agentic Orchestration) is a living methodology template
extracted from the kjtcom POC. iao provides a Python package, CLI, harness
documentation, and conventions for projects following the IAO pattern.

## Authoring vs Vendoring

iao lives in two places on NZXT:

1. **~/dev/projects/iao/** — authoring location, where iao iterates,
   owns its own design history. This is where iao gets developed.

2. **~/dev/projects/kjtcom/iao/** — vendored copy, used by kjtcom for its
   steady-state operation. Synced from authoring location during kjtcom
   maintenance cycles.

Future iao iterations happen in (1). Sync to (2) is a manual step Kyle
performs during kjtcom maintenance cycles.

## iao iteration history

| Iteration | Date | Phase | Status |
|---|---|---|---|
| 0.1.0 | 2026-04-08 | 0 (Setup + Build-Out) | stub on disk, full authoring pending |

## Future iterations

| Iteration | Phase | Scope (planned) |
|---|---|---|
| 0.1.X | 0 | Cleanup, validation, README rewrite in iao voice |
| 0.2.0 | 1 (Universal Consumer) | Bridge files + iao consult + iao operator run |
| 0.3.0+ | 1 | Per the Phase 1 forward context in kjtcom 10.69.0 design §10 |

## Project code

iao's 5-character project code is `iaomw` (preserves the "middleware"
historical lineage even though the user-facing name dropped the suffix).
Registered in `iao/projects.json`.

## Phase charters

Phase charters live in `docs/phase-charters/`. iao Phase 0 charter is
embedded in `iao-design-0.1.0.md` §1 for now; will be extracted to
standalone `docs/phase-charters/iao-phase-0.md` in a future iteration.
EOF
```

**Step 7 — Verify iao authoring environment:**

```fish
cd ~/dev/projects/iao

iao status 2>&1 | head -10
# Expected: project: iao, mode: active-development, iteration: 0.1.0

iao check config 2>&1 | head -10
# Expected: most checks pass, may have warnings about being a fresh project

cd ~/dev/projects/kjtcom
```

**Step 8 — Update kjtcom's `docs/maintenance/README.md` to reference iao authoring location:**

```fish
# Add to existing maintenance README a section pointing at iao
cat >> docs/maintenance/README.md << 'EOF'

## iao authoring location

Active iao development happens at `~/dev/projects/iao/`, NOT here. When
iao iterates and produces new base patterns/ADRs, sync the relevant
content to kjtcom's vendored copy at `~/dev/projects/kjtcom/iao/` as
part of the maintenance touch that acknowledges those new base IDs.

Sync command (future):
```fish
# When iao reaches a new version, sync the package code:
cp -r ~/dev/projects/iao/iao/* ~/dev/projects/kjtcom/iao/iao/
# Re-run pip install -e to pick up changes:
pip install -e ~/dev/projects/kjtcom/iao/ --break-system-packages
# Acknowledge new base IDs in kjtco/docs/harness/project.md header
iao check harness
```
EOF
```

**Use iao log:**

```fish
iao log workstream-complete W6 pass "iao authoring environment established at ~/dev/projects/iao/ with .iao.json and design 0.1.0 stub"
```

**Failure recovery:**
- `cp -r` fails → check disk space, permissions, retry
- `iao status` from iao directory fails → debug, may need to set PYTHONPATH or reinstall pip package from new location
- `git init` in iao dir fails → mark D6 PARTIAL, note that git init can be done manually post-iteration

**Success:** D6 green.

---

### W7 — Closing Sequence with Hardened Evaluator

**Est:** 25 min
**Pri:** P0
**Deliverable:** D7
**Blocks on:** W6 complete

**Goal:** Run the closing evaluator (now hardened by W1), produce real Qwen scores, emit Phase 10 graduation recommendation.

**This is mandatory. Do not skip.**

**Step 1 — Iteration delta snapshot:**

```fish
set -x IAO_WORKSTREAM_ID W7

python3 scripts/iteration_deltas.py --snapshot 10.69.1 2>&1 | tee /tmp/delta-10.69.1.log
```

**Step 2 — Sync script registry:**

```fish
python3 scripts/sync_script_registry.py 2>&1 | tee /tmp/registry-sync-10.69.1.log
```

**Step 3 — Build the bundle:**

```fish
python3 scripts/build_bundle.py --iteration 10.69.1
command ls -l docs/kjtcom-bundle-10.69.1.md
# Must exist and be > 600KB
```

**Step 4 — Run the evaluator (with W1 hardening fixes):**

```fish
python3 scripts/run_evaluator.py \
    --iteration 10.69.1 \
    --rich-context \
    --synthesis-mode weighted \
    --verbose 2>&1 | tee /tmp/eval-10.69.1.log
```

The W1 fixes should resolve:
- Filename layout issue (evaluator finds `kjtcom-design-10.69.0.md`)
- Synthesis ratio sensitivity (weighted mode default)
- Gemini Flash schema validation (repair pass enabled)

Expected outcome: real Qwen Tier 1 output, not self-eval fallback.

**Step 5 — Parse evaluator output:**

```fish
grep -E "tier used|synthesis_ratio|graduation_assessment|score" /tmp/eval-10.69.1.log
```

**Step 6 — Run post-flight (uses W2 plugin loader):**

```fish
python3 scripts/post_flight.py 10.69.1 2>&1 | tee /tmp/postflight-10.69.1.log
```

Expected:
- `build_gatekeeper`: PASS
- `artifacts_present`: PASS (now reads bundle_format from .iao.json)
- `build_log_complete`: PASS (W3 hook used by all workstreams)
- `deployed_flutter_matches`: DEFERRED (deploy paused)
- `deployed_claw3d_matches`: DEFERRED
- `claw3d_version_matches`: DEFERRED
- `map_tab_renders`: DEFERRED (now honors deploy_paused)
- `firestore_baseline`: depends on connectivity

**Step 7 — Verify D1-D7 deliverables:**

```fish
# D1 - evaluator works
grep -E "tier used.*qwen" /tmp/eval-10.69.1.log && echo "D1 PASS" || echo "D1 PARTIAL"

# D2 - postflight plugin loader
command ls kjtco/postflight/*.py 2>/dev/null && echo "D2 PASS" || echo "D2 FAIL"

# D3 - build log auto-append hook
iao log workstream-complete W7-test pass "test" 2>&1 | grep -q "ok" && echo "D3 PASS" || echo "D3 FAIL"

# D4 - Phase 10 charter
test -f docs/phase-charters/kjtcom-phase-10.md && echo "D4 PASS" || echo "D4 FAIL"

# D5 - kjtcom steady-state
python3 -c "import json; print('D5 PASS' if json.loads(open('.iao.json').read()).get('mode') == 'steady-state' else 'D5 FAIL')"

# D6 - iao authoring environment
test -f ~/dev/projects/iao/.iao.json && echo "D6 PASS" || echo "D6 FAIL"

# D7 - closing eval ran
test -f /tmp/eval-10.69.1.log && echo "D7 PASS" || echo "D7 FAIL"
```

**Step 8 — Write build log W7 section + Phase 10 graduation verification:**

Append final sections to `docs/kjtcom-build-10.69.1.md`:

```markdown
## W7 Closing Evaluator Findings

**Tier used:** <from /tmp/eval-10.69.1.log>
**Synthesis ratio:** <from log>
**Overall score:** <from log>
**Graduation assessment:** <from log if available>

## Iteration Deliverables Verification (D1-D7)

| # | Deliverable | W# | Status | Evidence |
|---|---|---|---|---|
| D1 | Evaluator hardening | W1 | <PASS/PARTIAL/FAIL> | <evidence> |
| D2 | Postflight plugin loader | W2 | <PASS/PARTIAL/FAIL> | <evidence> |
| D3 | Build log auto-append | W3 | <PASS/PARTIAL/FAIL> | <evidence> |
| D4 | Phase 10 charter retrofit | W4 | <PASS/PARTIAL/FAIL> | <evidence> |
| D5 | kjtcom steady-state | W5 | <PASS/PARTIAL/FAIL> | <evidence> |
| D6 | iao authoring environment | W6 | <PASS/PARTIAL/FAIL> | <evidence> |
| D7 | Closing evaluator ran | W7 | <PASS/PARTIAL/FAIL> | <evidence> |

## Phase 10 Exit Criteria Verification

(Copy from design §1 Phase Charter Exit Criteria, mark each with PASS/FAIL/N-A)

## Iteration Graduation Recommendation

<one of:>
- **GRADUATE TO 10.70.0:** All D1-D7 green. (Note: 10.70 doesn't exist yet — kjtcom is in steady-state. Next development happens in iao project, not kjtcom.)
- **RERUN AS 10.69.2:** D<N> failed.
- **BLOCKED BY EVALUATOR:** D7 fell back to self-eval again; deeper evaluator surgery needed.

## Phase 10 Graduation Recommendation

<one of:>
- **GRADUATE PHASE 10:** All Phase 10 exit criteria green. kjtcom's active development era ends. Next planning chat session works on iao 0.2.0.
- **REQUIRES 10.69.X:** Phase 10 exit criteria not all met. 10.69.2 needed.
- **BLOCKED:** Defer phase graduation to manual review.
```

**Step 9 — Write `docs/kjtcom-report-10.69.1.md`** using real evaluator output (or documented fallback)

**Step 10 — Verify all artifacts:**

```fish
command ls docs/kjtcom-design-10.69.0.md \
           docs/kjtcom-plan-10.69.0.md \
           docs/kjtcom-build-10.69.1.md \
           docs/kjtcom-report-10.69.1.md \
           docs/kjtcom-bundle-10.69.1.md \
           docs/phase-charters/kjtcom-phase-10.md \
           docs/kjtcom-maintenance-guide.md \
           docs/maintenance/2026-04-graduation.md \
           ~/dev/projects/iao/.iao.json \
           ~/dev/projects/iao/docs/iao-design-0.1.0.md
```

**Step 11 — Read-only git status:**

```fish
cd ~/dev/projects/kjtcom
git status --short
git log --oneline -5

cd ~/dev/projects/iao
git status --short
cd ~/dev/projects/kjtcom
```

**Step 12 — Use iao log for W7 completion:**

```fish
iao log workstream-complete W7 pass "Closing sequence complete with <evaluator outcome>"
```

**Step 13 — Emit Phase 10 graduation handback:**

```fish
printf '
==============================================
10.69.1 COMPLETE — PHASE 10 GRADUATION ASSESSMENT
==============================================

Iteration 10.69.1 Deliverables: <N>/7 green

  D1 Evaluator hardening:        <PASS|PARTIAL|FAIL>
  D2 Postflight plugin loader:    <PASS|PARTIAL|FAIL>
  D3 Build log auto-append:       <PASS|PARTIAL|FAIL>
  D4 Phase 10 charter retrofit:   <PASS|PARTIAL|FAIL>
  D5 kjtcom steady-state:         <PASS|PARTIAL|FAIL>
  D6 iao authoring environment:   <PASS|PARTIAL|FAIL>
  D7 Closing evaluator ran:       <PASS|PARTIAL|FAIL>

Qwen tier used: <tier>
Qwen graduation_assessment: <value>

PHASE 10 EXIT CRITERIA: <all criteria from design §1, marked>

ITERATION RECOMMENDATION: <GRADUATE 10.69 | RERUN 10.69.2 | BLOCKED>
PHASE 10 RECOMMENDATION: <GRADUATE PHASE 10 | REQUIRES 10.69.X | BLOCKED>

Next phase context:
  - iao authoring at ~/dev/projects/iao/ (iteration 0.1.0 stub on disk)
  - kjtcom in steady-state mode (mode flag set, maintenance guide written)
  - First iao 0.2.0 candidate scope: bridge files + Universal Consumer launch

Awaiting human review of bundle and dual graduation decision (iteration + phase).
'
```

**STOP.** Do not commit. Do not push.

**Failure recovery:**
- W1 evaluator fixes still insufficient → mark D7 `blocked-by-evaluator-still`, recommend 10.69.2
- post-flight failures → debug, retry, mark relevant Ds as PARTIAL if unresolvable
- Wall clock > 6 hours and W7 not yet started → triage, but W7 still MUST run

**Success:** D7 green. Phase 10 graduation recommendation in hand.

---

## 7. Definition of Done

1. Pre-flight: BLOCKERS pass, NOTEs logged
2. W0: `.iao.json current_iteration` is `10.69.1`
3. W1: Evaluator hardening shipped, tests pass, retroactive 10.68.1 rerun produces real or improved output
4. W2: `kjtco/postflight/` exists with moved checks, plugin loader loads both base + project, both 10.68.1 post-flight failures resolved
5. W3: `iao log workstream-complete` command exists, used by W4-W7, post-flight `build_log_complete` check exists
6. W4: `docs/phase-charters/kjtcom-phase-10.md` on disk, `iao/templates/phase-charter-template.md` on disk, iaomw-Pattern-31 in base.md, kjtco project.md acknowledges new ID
7. W5: `.iao.json mode: steady-state`, maintenance guide on disk, README updated, inaugural maintenance note written
8. W6: `~/dev/projects/iao/` exists with own `.iao.json`, iao 0.1.0 design stub on disk, `iao status` from iao dir works
9. W7: Closing evaluator ran (real or documented fallback), Phase 10 exit criteria verified, dual graduation recommendation emitted
10. 5 primary artifacts: design 10.69.0, plan 10.69.0, build 10.69.1, report 10.69.1, bundle 10.69.1
11. Sidecars: phase-10 charter, maintenance guide, inaugural maintenance note, iao 0.1.0 design stub
12. Bundle ≥ 600KB
13. Zero git writes
14. Phase 10 dual graduation recommendation in build log AND stdout handback

---

## 8. Failure Modes Quick Reference

| Failure | Action |
|---|---|
| Pre-flight BLOCKER | Halt. `PRE-FLIGHT BLOCKED: <reason>`. Exit. |
| W0 .iao.json edit fails | `git checkout -- .iao.json`, retry |
| W1 evaluator fixes break further | Revert specific fix, mark D1 PARTIAL, continue |
| W1 unit tests fail | 3-retry, revert specific fix |
| W2 import break after move | `git checkout -- <file>`, mark check as not-yet-moved |
| W3 `iao log` fails | Manual append, mark D3 PARTIAL |
| W4 charter writing fails | Path issue, retry with absolute paths |
| W5 mode flag breaks `iao check config` | Revert, mark D5 PARTIAL, document |
| W6 cp fails | Investigate disk/permissions, retry |
| W6 `iao status` from iao dir fails | Debug PYTHONPATH or pip install, mark D6 PARTIAL |
| **W7 evaluator falls back AGAIN despite W1** | Mark D7 `blocked-by-evaluator-still`, defer Phase 10 graduation, recommend 10.69.2 |
| W7 build_gatekeeper FAIL | Real failure, debug, Phase 10 graduation blocked |
| Wall clock > 7 hours | Triage W4/W5 to lighter, W1/W2/W3/W6/W7 MUST run |
| **Agent considers skipping W7 evaluator** | Re-read §2. Not acceptable. Run it. |
| Any git write attempted | Pillar 0 violation. Halt. |

---

## 9. Launch

When Kyle says **"read claude and execute 10.69"** or **"read gemini and execute 10.69"**:

1. Acknowledge in one line
2. Read `CLAUDE.md` or `GEMINI.md` end-to-end
3. Read `docs/kjtcom-design-10.69.0.md` end-to-end
4. Read `docs/kjtcom-plan-10.69.0.md` end-to-end (this file)
5. Create `docs/kjtcom-build-10.69.1.md` from §5 template
6. Run pre-flight §4, capture to build log
7. Begin W0 (.iao.json update)
8. W1 (evaluator hardening)
9. W2 (postflight refactor)
10. W3 (build log hook) **— from W4 onward, use `iao log workstream-complete` at every workstream end**
11. W4 (phase 10 charter retrofit)
12. W5 (kjtcom steady-state)
13. W6 (iao authoring environment)
14. **W7 (closing sequence — MANDATORY evaluator run)**
15. Write build log final sections with D1-D7 + Phase 10 exit criteria verification
16. Emit dual graduation recommendation handback to stdout
17. Verify all artifacts on disk
18. **STOP.** Do not commit.

---

*Plan 10.69.0 — April 08, 2026. Final iteration of kjtcom Phase 10. Authored by the planning chat. Establishes phase charter as required §1 going forward via W4.*
