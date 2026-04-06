# kjtcom - Design Document v9.48

**Phase:** 9 - App Optimization (FINAL)
**Iteration:** 48
**Date:** April 5, 2026
**Focus:** Structural Cleanup + Qwen Harness Hardening + File Management Fix + Harness Growth Enforcement

---

## AMENDMENTS (all prior amendments remain in effect)

### File Management Rules - REVISED (v9.48+, replaces all prior)

The file structure is getting messy. These rules are absolute:

**docs/** holds ONLY:
- Current iteration artifacts: kjtcom-design-v{CURRENT}.md, kjtcom-plan-v{CURRENT}.md, kjtcom-build-v{CURRENT}.md, kjtcom-report-v{CURRENT}.md
- Living docs: kjtcom-changelog.md, kjtcom-architecture.mmd, install.fish, evaluator-harness.md, pipeline-review-v9.47.md
- No other iteration-versioned files

**docs/archive/** holds:
- ALL prior iteration artifacts (one copy only, no duplicates)
- The KT docs, changelog snapshots, etc.

**docs/drafts/** is EPHEMERAL:
- Wiped at start of each iteration: `rm -f docs/drafts/*.md`
- Holds Qwen-generated drafts during the iteration
- After validation and promotion, drafts move to docs/ and drafts/ is empty again
- NEVER committed to git with stale content

**Single Changelog Rule:**
- ONE file: docs/kjtcom-changelog.md
- Each iteration APPENDS to the top of this file
- generate_artifacts.py modifies the existing changelog, does NOT create changelog-v{X}.md
- Any existing changelog-v{X}.md files in docs/ must be deleted (content already in main changelog)

**No Duplicate Files:**
- A file must exist in EITHER docs/ OR docs/archive/, never both
- Kyle moves current docs to archive manually after git push
- The agent does NOT copy files to archive - it only writes to docs/ and docs/drafts/

### Harness Growth Enforcement - MANDATORY (v9.48+)

CLAUDE.md and GEMINI.md must be at LEAST 200 lines each. If an agent produces a harness file shorter than the prior iteration's version, the file is rejected. Harnesses grow by accumulating amendments, best practices, and institutional knowledge. They never shrink.

Verification: `wc -l CLAUDE.md GEMINI.md` at pre-flight. If either is shorter than prior iteration, do not proceed.

### Qwen Structural Enforcement - NEW (v9.48+)

The evaluator harness (docs/evaluator-harness.md) is necessary but not sufficient. Qwen still hallucinates workstreams because the prompt structure allows it. The fix is structural enforcement in Python:

1. run_evaluator.py MUST parse the design doc to extract the workstream table
2. Count the W# rows in the design doc
3. After Qwen returns its evaluation, validate: scorecard row count == design doc W# count
4. If mismatch: log error, re-prompt Qwen with explicit "You returned N workstreams but the design doc has M. Re-evaluate with exactly M workstreams."
5. Max 2 retries. If still wrong after 2 retries, log as gotcha and use the design doc workstream list with Qwen's scores mapped by name matching.

This is the "trust but verify" pattern from socalpha1.

---

## WORKSTREAMS

| # | Workstream | Priority | Description |
|---|-----------|----------|-------------|
| W1 | File management cleanup | P1 | Delete orphaned changelog-v*.md files. Ensure no duplicates between docs/ and archive/. Fix generate_artifacts.py to append to single changelog. Clean docs/drafts/. |
| W2 | Qwen structural enforcement in Python | P1 | Parse design doc for W# count. Validate Qwen output. Re-prompt on mismatch. Eliminate hallucinated workstreams at code level. |
| W3 | Rebuild CLAUDE.md and GEMINI.md to 200+ lines | P1 | Restore full harness content that was trimmed in v9.47. Both files must exceed 200 lines with all accumulated amendments. |
| W4 | Post-flight + final Phase 9 verification | P2 | Post-flight pass. Verify all living docs current. Verify claw3d.html loads. Confirm Phase 9 is ready to close. |

---

## W1: File Management Cleanup (P1)

### Cleanup Script

Create scripts/cleanup_docs.py:

```python
"""Clean up docs/ directory per v9.48 file management rules."""
import os
import glob

def cleanup():
    # 1. Delete orphaned changelog-v*.md files in docs/
    for f in glob.glob("docs/changelog-v*.md"):
        print(f"DELETE: {f} (content in kjtcom-changelog.md)")
        os.remove(f)

    # 2. Find duplicates between docs/ and archive/
    docs_files = set(os.path.basename(f) for f in glob.glob("docs/kjtcom-*.md"))
    archive_files = set(os.path.basename(f) for f in glob.glob("docs/archive/kjtcom-*.md"))
    duplicates = docs_files & archive_files
    for dup in duplicates:
        # Keep archive copy, remove docs/ copy (unless it's current iteration)
        current_iter = os.environ.get("IAO_ITERATION", "").replace("v", "")
        if current_iter not in dup:
            print(f"DUPLICATE: docs/{dup} (also in archive/)")

    # 3. Clean drafts
    for f in glob.glob("docs/drafts/*.md"):
        print(f"CLEAN DRAFT: {f}")
        os.remove(f)

    # 4. Verify single changelog
    assert os.path.exists("docs/kjtcom-changelog.md"), "Missing main changelog!"
```

### generate_artifacts.py Fix

Update the changelog generation to:
1. Read existing docs/kjtcom-changelog.md
2. Generate the new entry
3. Prepend the new entry after the `# kjtcom - Unified Changelog` header
4. Write back to docs/kjtcom-changelog.md
5. Do NOT create docs/changelog-v{X}.md or docs/drafts/changelog-v{X}.md

---

## W2: Qwen Structural Enforcement (P1)

### Design Doc Parser

Add to scripts/run_evaluator.py:

```python
def parse_workstream_count(design_doc_path):
    """Parse design doc to extract workstream table and count W# rows."""
    with open(design_doc_path) as f:
        content = f.read()

    # Find the WORKSTREAMS table
    lines = content.split("\n")
    w_count = 0
    w_names = []
    in_table = False
    for line in lines:
        if "| # |" in line or "| W#" in line:
            in_table = True
            continue
        if in_table and line.startswith("|"):
            if "---" in line:
                continue
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 3 and parts[1].startswith("W"):
                w_count += 1
                w_names.append(parts[2])  # workstream name
        elif in_table and not line.startswith("|"):
            in_table = False

    return w_count, w_names

def validate_qwen_output(qwen_scores, expected_count, expected_names):
    """Validate Qwen's scorecard against design doc."""
    actual_count = len(qwen_scores)
    if actual_count != expected_count:
        return False, f"Workstream count mismatch: Qwen returned {actual_count}, design doc has {expected_count}"
    return True, "OK"
```

### Re-prompt Logic

```python
# After Qwen evaluation:
valid, msg = validate_qwen_output(scores, expected_count, expected_names)
if not valid:
    # Re-prompt with explicit count constraint
    retry_prompt = f"""
    ERROR: {msg}
    The design document lists EXACTLY {expected_count} workstreams:
    {chr(10).join(f'  W{i+1}: {name}' for i, name in enumerate(expected_names))}

    Re-evaluate using ONLY these {expected_count} workstreams. Return exactly {expected_count} scores.
    """
    # Retry up to 2 times
```

### Evidence Validation

For each workstream Qwen scores as "complete", verify:
- At least one file path cited in Evidence column exists on disk
- If Evidence references a command output, check event log for matching event

---

## W3: Rebuild Harness Files (P1)

Both CLAUDE.md and GEMINI.md were trimmed in v9.47 (from 200+ to ~150 lines). This violates the harness growth principle.

Rebuild both to 200+ lines by restoring all accumulated content:
- Full Agent Session Best Practices section
- Full Post-Flight Verification section
- Full Qwen Claim Audit section with all banned phrases
- Full Middleware as Primary IP with complete component list
- Full Environment table
- Full Active Gotchas table
- Full Key Files table
- All amendments from v9.40 through v9.48
- File management rules (new v9.48)
- Harness growth enforcement (new v9.48)
- Qwen structural enforcement (new v9.48)

The pre-flight checklist must include: `wc -l CLAUDE.md GEMINI.md` and verify both >= 200.

---

## W4: Post-Flight + Phase 9 Final (P2)

1. Run post_flight.py - all checks pass
2. Verify claw3d.html loads at kylejeromethompson.com/claw3d.html
3. Run cleanup_docs.py
4. Verify docs/ has only current iteration + living docs
5. Verify docs/drafts/ is empty after promotion
6. Final assessment: is Phase 9 ready to close?

Phase 9 close criteria:
- [ ] All living docs current
- [ ] Qwen produces valid scorecards (no hallucinated workstreams)
- [ ] File management clean
- [ ] Post-flight passes
- [ ] Harness files >= 200 lines each
- [ ] Bot operational (systemd, session memory, rating sort, 3-route)
- [ ] Pipeline review complete (docs/pipeline-review-v9.47.md)
- [ ] Middleware registry complete

If all checked, Phase 9 is closed in the build log and we proceed to Phase 10 in the next iteration.

---

## TRIDENT

| Prong | Target |
|-------|--------|
| Cost | $0. <50K tokens. |
| Delivery | 4 workstreams. File management clean. Qwen structurally enforced. Harnesses rebuilt. |
| Performance | Qwen evaluation produces exactly N workstream rows where N matches design doc. Zero hallucinated workstreams. |

---

*Design document v9.48, April 5, 2026.*
