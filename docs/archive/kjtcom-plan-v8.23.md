# kjtcom - Plan v8.23 (Phase 8 - NoSQL Query Remediation)

**Pipeline:** kjtcom (cross-pipeline location intelligence platform)
**Phase:** 8 (Enrichment Hardening)
**Iteration:** 23 (global counter)
**Executor:** Claude Code (Flutter app fixes + data fix + deploy)
**Machine:** NZXTcos
**Date:** April 2026

---

## Section A: Pre-Flight (Human)

### IAO Pillar Pre-Flight Checklist

| # | Pillar | Verification | Command/Check |
|---|--------|-------------|---------------|
| P1 | Trident | $0 cost - Dart changes + one Python data fix + deploy | No paid APIs needed |
| P2 | Artifact Loop | v8.22 docs archived | `ls docs/archive/kjtcom-*v8.22*` -> 4 files |
| P2 | Artifact Loop | v8.23 design + plan in docs/ | `ls docs/kjtcom-{design,plan}-v8.23.md` -> 2 files |
| P3 | Diligence | Design doc reviewed | Kyle has read design-v8.23.md and v8.22 defect table |
| P4 | Pre-Flight | Git clean | `git status` -> clean |
| P4 | Pre-Flight | CLAUDE.md updated | `head -3 CLAUDE.md` -> references v8.23 |
| P4 | Pre-Flight | SA credentials | `test -f "$GOOGLE_APPLICATION_CREDENTIALS" && echo SET` |
| P4 | Pre-Flight | Flutter builds | `cd app && flutter build web` -> success |
| P4 | Pre-Flight | Firebase auth valid | `firebase projects:list` -> no auth error |
| P5 | Harness | Firebase MCP configured | See A5 below |
| P6 | Zero-Intervention | All 9 work items pre-specified with file paths | No TBD in design doc |
| P7 | Self-Healing | `flutter analyze` after each change | Catches issues before deploy |
| P8 | Graduation | Fixes query system built in Phase 6 | Hardening, not new features |
| P9 | Post-Flight | Regression test suite defined | 12 tests from v8.22 defect table |
| P10 | Improvement | G36, G37 resolved by W1, W3 | G38 added for firebase auth |

### A1: Archive v8.22 Docs

```fish
cd ~/dev/projects/kjtcom
mv docs/kjtcom-design-v8.22.md docs/archive/
mv docs/kjtcom-plan-v8.22.md docs/archive/
mv docs/kjtcom-build-v8.22.md docs/archive/
mv docs/kjtcom-report-v8.22.md docs/archive/
```

### A2: Stage v8.23 Docs

```fish
cp ~/Downloads/kjtcom-design-v8.23.md docs/
cp ~/Downloads/kjtcom-plan-v8.23.md docs/
```

### A3: Update CLAUDE.md

Replace CLAUDE.md contents with the v8.23 version (Section C of this document).

### A4: Verify Flutter Builds

```fish
cd ~/dev/projects/kjtcom/app
flutter pub get
flutter build web
flutter analyze
flutter test
```

All must pass before launching Claude Code.

### A5: Configure Firebase MCP (Optional but Recommended)

Add to Claude Code's MCP config (usually `~/.config/claude/mcp_settings.json` or project-level `.mcp.json`):

```json
{
  "mcpServers": {
    "firebase": {
      "command": "npx",
      "args": ["-y", "firebase-mcp"],
      "env": {
        "GOOGLE_APPLICATION_CREDENTIALS": "/home/kthompson/.config/gcloud/kjtcom-sa.json"
      }
    }
  }
}
```

If Firebase MCP setup is non-trivial, skip it - Claude Code can use Python Firestore queries as fallback. This is a P2 optimization, not a blocker.

### A6: Verify Firebase Auth

```fish
cd ~/dev/projects/kjtcom
firebase projects:list
```

If auth error: `firebase login --reauth` (G38).

---

## Section B: Claude Code Execution

**Launch:** `claude --dangerously-skip-permissions`
**First message:** See Section D (Launch Prompt).

### Step 1: Read Design Doc + v8.22 Report

Read `docs/kjtcom-design-v8.23.md` for work items and `docs/archive/kjtcom-report-v8.22.md` for the defect table.

### Step 2: W1 - Lowercase Query Values (P0)

**File:** `app/lib/providers/firestore_provider.dart`

Add `.toLowerCase()` to all query value dispatches. This is the single highest-impact fix.

After change: `flutter analyze` + `flutter test`

### Step 3: W2 - Update Example Queries (P0)

**File:** `app/lib/widgets/query_editor.dart`

Replace all 5 example queries with validated lowercase queries. Before hardcoding, verify each query returns > 0 results against production Firestore (use Firebase MCP or Python).

Recommended new examples (validate counts first):
1. `t_any_cuisines contains "french"` (verify ~80 results)
2. `t_any_actors contains "huell howser"` (verify 899 results)
3. `t_any_countries contains "italy"` (verify ~600 results)
4. `t_any_dishes contains "gelato"` (verify > 0 results)
5. `t_any_keywords contains "medieval"` (verify ~653 results)

After change: `flutter analyze` + `flutter test`

### Step 4: Mid-Iteration Deploy (P0 fix live)

```fish
cd ~/dev/projects/kjtcom/app
flutter build web
cd ..
firebase deploy --only hosting
```

Verify on kylejeromethompson.com: all 5 example queries now return results.

### Step 5: W3 - CalGold t_any_shows Data Fix (P1)

Create `pipeline/scripts/fix_calgold_shows_case.py`:
- Read CalGold entities from production
- Lowercase all t_any_shows values
- Dry-run first, then full run

```fish
python3 -u pipeline/scripts/fix_calgold_shows_case.py --dry-run --limit 5
python3 -u pipeline/scripts/fix_calgold_shows_case.py
```

Verify: `t_any_shows contains "california's gold"` now returns 899 results.

### Step 6: W5 + W6 - Result Count + Truncation Indicator (P1)

**Files:** `app/lib/widgets/results_table.dart` or new widget

Add result count display: `N results` in tech green Geist Mono above the results table.

Add truncation indicator: when results.length == limit, show `Showing N of N+ results`.

After change: `flutter analyze` + `flutter test`

### Step 7: W4 - Implement `contains-any` Operator (P1)

**Files:** `app/lib/models/query_clause.dart`, `app/lib/providers/firestore_provider.dart`

Add `contains-any` to parser regex. Parse value as comma-separated list or JSON array. Map to Firestore `arrayContainsAny`. Validate max 30 values (Firestore limit).

After change: `flutter analyze` + `flutter test`

Verify: `t_any_cuisines contains-any ["mexican", "italian"]` returns ~332 results.

### Step 8: W7 - Increase Result Limit (P1)

**File:** `app/lib/providers/firestore_provider.dart`

Change `query.limit(200)` to `query.limit(1000)`. This covers all current query scenarios (max observed was 653 for "medieval").

After change: `flutter analyze` + `flutter test`

### Step 9: W8 + W9 - Validation + Error Feedback (P2)

**Files:** `app/lib/models/query_clause.dart`, `app/lib/widgets/query_editor.dart`

W8: Add field name validation against known t_any_* field list. Invalid fields produce an error clause.

W9: Display parse error below query editor when input doesn't match expected syntax. Display informational note for multi-array queries about client-side filtering.

After change: `flutter analyze` + `flutter test`

### Step 10: Final Deploy

```fish
cd ~/dev/projects/kjtcom/app
flutter build web
cd ..
firebase deploy --only hosting
```

### Step 11: Regression Test Suite

Re-run all 12 defect tests from v8.22 against the deployed site. For each test, record:
- Query string
- Expected result (from design doc)
- Actual result on deployed site
- PASS/FAIL

Use Playwright MCP if available, or Python Firestore queries + manual UI verification.

### Step 12: Security Scan + Artifacts

```
CHECKLIST:
[ ] Security: grep -rnI "AIzaSy" . -> only expected references
[ ] flutter analyze: 0 issues
[ ] flutter test: all pass
[ ] All 5 example queries return > 0 results on live site
[ ] Result count displayed
[ ] Truncation indicator shown for broad queries
[ ] contains-any operator works
[ ] CalGold t_any_shows lowercased (899/899)
[ ] Regression: 11/12 tests pass (D12 deferred)
```

Produce all 4 mandatory artifacts:

1. **docs/kjtcom-build-v8.23.md** - Work item implementation details, flutter analyze/test results, deploy logs
2. **docs/kjtcom-report-v8.23.md** - Regression test results, defect resolution matrix, recommendation for Phase 9
3. **docs/kjtcom-changelog.md** - Append v8.23 at top
4. **README.md** - Phase 8 status updated, query system described as operational

Do NOT git commit or push.

---

## Section C: CLAUDE.md for v8.23

```markdown
# kjtcom - Agent Instructions (Claude Code)

## Read Order

1. docs/kjtcom-design-v8.23.md (work items W1-W9 with exact file paths)
2. docs/kjtcom-plan-v8.23.md (execute Section B)
3. docs/archive/kjtcom-report-v8.22.md (defect table for regression testing)

## Context

Phase 8 NoSQL Query Remediation. Fix all 12 query defects from v8.22 assessment.
- P0: Case sensitivity fix + example query update (W1, W2)
- P1: Data fix + result counts + contains-any + pagination (W3, W4, W5, W6, W7)
- P2: Validation + error feedback (W8, W9)

Deploy TWICE: once after P0 fixes (Step 4), once after all fixes (Step 10).

kjtcom project ID: kjtcom-c78cd
SA credentials: $GOOGLE_APPLICATION_CREDENTIALS
Production database: (default)
Production collection: locations
Total entities: 6,181

## Shell - MANDATORY

- All commands in fish shell
- Use python3 -u for unbuffered stdout
- NEVER cat config.fish or SA JSON files (G20, G11)

## Security

- grep -rnI "AIzaSy" . before completion
- NEVER print SA credentials or API keys

## Flutter Requirements

- Run `flutter analyze` after every Dart file change
- Run `flutter test` after every Dart file change
- Build: `cd app && flutter build web`
- Deploy: `cd ~/dev/projects/kjtcom && firebase deploy --only hosting`
- Deploy from repo root, not app/ (G38)

## Data Fix Requirements

- fix_calgold_shows_case.py: --dry-run, --limit flags
- Dry-run before full run (G35)

## Regression Testing

- After final deploy, re-run all 12 tests from v8.22 defect table
- Record query, expected, actual, PASS/FAIL for each

## Permissions

- CANNOT: git add / commit / push
- CANNOT: sudo

## Artifact Rules - MANDATORY

1. docs/kjtcom-build-v8.23.md
2. docs/kjtcom-report-v8.23.md (MUST include regression test results)
3. docs/kjtcom-changelog.md (append v8.23)
4. README.md (Phase 8 DONE, query system operational)

## Formatting

- No em-dashes. Use " - " instead.
- Use "->" for arrows.
```

---

## Section D: Launch Prompt

```
Read CLAUDE.md, then read docs/kjtcom-design-v8.23.md for all 9 work items and docs/kjtcom-plan-v8.23.md for execution order. Also read docs/archive/kjtcom-report-v8.22.md for the defect table you are fixing.

Execute Section B in order:
1. W1 (lowercase query values) + W2 (update example queries) - validate each example returns > 0 results first
2. Mid-iteration deploy (P0 fix goes live)
3. W3 (CalGold t_any_shows data fix - dry-run then full run)
4. W5 + W6 (result count + truncation indicator)
5. W4 (contains-any operator)
6. W7 (increase result limit to 1000)
7. W8 + W9 (field validation + error feedback)
8. Final deploy
9. Run complete regression test suite (all 12 defects from v8.22)
10. Produce all 4 mandatory artifacts
```

---

## Timing Estimate

| Step | Est. Duration |
|------|---------------|
| Section A (pre-flight, human) | ~15 min |
| Steps 1-4 (P0 fix + deploy) | ~30 min |
| Step 5 (data fix) | ~10 min |
| Steps 6-8 (P1 fixes) | ~60-90 min |
| Step 9 (P2 fixes) | ~30 min |
| Steps 10-12 (deploy + regression + artifacts) | ~30 min |
| **Total** | **~3-4 hours** |

---

## After v8.23

1. Commit: `git add . && git commit -m "KT 8.23 Phase 8 query remediation - all defects resolved" && git push`
2. Verify kylejeromethompson.com - all queries operational, counts visible
3. Phase 8 complete. Proceed to Phase 9 (App Optimization):
   - Lighthouse performance (FCP was 7-14s in v6.18)
   - Cookie consent
   - Analytics refinement
   - Evaluate Algolia if fuzzy/cross-field search needed
4. Phase 10: IAO retrospective + template publication
