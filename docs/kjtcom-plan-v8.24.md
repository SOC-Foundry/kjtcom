# kjtcom - Plan v8.24 (Phase 8 - UI Fixes + Country Codes)

**Pipeline:** kjtcom (cross-pipeline location intelligence platform)
**Phase:** 8 (Enrichment Hardening)
**Iteration:** 24 (global counter)
**Executor:** Claude Code (Flutter app fixes + data backfill + deploy)
**Machine:** NZXTcos
**Date:** April 2026

---

## Section A: Pre-Flight (Human)

### IAO Pillar Pre-Flight Checklist

| # | Pillar | Verification | Command/Check |
|---|--------|-------------|---------------|
| P1 | Trident | $0 cost - Dart fixes + Python backfill | No paid APIs |
| P2 | Artifact Loop | v8.23 docs archived | `ls docs/archive/kjtcom-*v8.23*` -> 4 files |
| P2 | Artifact Loop | v8.24 design + plan in docs/ | `ls docs/kjtcom-{design,plan}-v8.24.md` -> 2 files |
| P3 | Diligence | Design doc reviewed | Kyle has reviewed 4 work items |
| P4 | Pre-Flight | Git clean | `git status` -> clean |
| P4 | Pre-Flight | CLAUDE.md updated | `head -3 CLAUDE.md` -> references v8.24 |
| P4 | Pre-Flight | SA credentials | `test -f "$GOOGLE_APPLICATION_CREDENTIALS" && echo SET` |
| P4 | Pre-Flight | Flutter builds | `cd app && flutter build web` -> success |
| P4 | Pre-Flight | Firebase auth | `firebase projects:list` -> no error |
| P5 | Harness | CLAUDE.md points to v8.24 docs | Verified |
| P6 | Zero-Intervention | All 4 work items pre-specified | No TBD in design doc |
| P7 | Self-Healing | flutter analyze after each change | Catches issues |
| P8 | Graduation | Fixing regressions + adding data field | Hardening |
| P9 | Post-Flight | Detail panel opens, queries still work | Regression suite |
| P10 | Improvement | G39 added | Detail panel provider chain |

### A1: Archive v8.23 Docs

```fish
cd ~/dev/projects/kjtcom
mv docs/kjtcom-design-v8.23.md docs/kjtcom-plan-v8.23.md docs/kjtcom-build-v8.23.md docs/kjtcom-report-v8.23.md docs/archive/
```

### A2: Stage v8.24 Docs

```fish
cp ~/Downloads/kjtcom-design-v8.24.md docs/
cp ~/Downloads/kjtcom-plan-v8.24.md docs/
```

### A3: Update CLAUDE.md

Replace CLAUDE.md contents with the v8.24 version (Section C of this document).

### A4: Install pycountry

```fish
pip install pycountry --break-system-packages
python3 -c "import pycountry; print('OK')"
```

### A5: Verify Flutter + Firebase

```fish
cd ~/dev/projects/kjtcom/app
flutter pub get
flutter build web
flutter analyze
flutter test
cd ..
firebase projects:list
```

---

## Section B: Claude Code Execution

**Launch:** `claude --dangerously-skip-permissions`
**First message:** See Section D (Launch Prompt).

### Step 1: Read Design Doc

Read `docs/kjtcom-design-v8.24.md` for all 4 work items.

### Step 2: W1 - Fix Detail Panel (P0)

**Diagnostic first.** Read these files in order:
1. `app/lib/widgets/detail_panel.dart` - what does it expect?
2. `app/lib/widgets/results_table.dart` - does row tap update selectedEntityProvider?
3. `app/lib/providers/selection_provider.dart` - is the provider wired?
4. `app/lib/widgets/app_shell.dart` - is detail_panel in the widget tree?
5. `app/lib/providers/firestore_provider.dart` - did v8.23 QueryResult refactor break entity selection?

Trace the full chain: row tap -> provider update -> detail panel render.

Fix the break point. After fix, verify:
- Tap a result row -> detail panel appears
- Detail panel shows entity name, pipeline badge, t_any_* field cards
- +filter/-exclude buttons work (clicking appends to query)

flutter analyze + flutter test after fix.

### Step 3: W2 - Remove "staging" Badge (P0)

Find and remove the "staging" badge from the UI. Check:
- `app/lib/widgets/app_shell.dart`
- Any widget that renders a green/colored badge with "staging" text

Remove it entirely. The app queries production - no environment badge needed.

flutter analyze + flutter test after fix.

### Step 4: Mid-Iteration Deploy (P0 fixes live)

```fish
cd ~/dev/projects/kjtcom/app
flutter build web
cd ..
firebase deploy --only hosting
```

Verify on kylejeromethompson.com:
- Click a result -> detail panel opens
- "staging" badge is gone

### Step 5: W3 - Fix Cursor Alignment (P1)

**File:** `app/lib/widgets/query_editor.dart`

Diagnose the cursor issue:
1. Are there multiple TextField widgets rendering? (explains "three cursors")
2. Is the line number gutter width mismatched with TextField padding?
3. Is cursor offset calculated correctly relative to the text content?

Fix: ensure single cursor, aligned with actual text input position.

flutter analyze + flutter test after fix.

### Step 6: W4 - Country Codes Backfill (P1)

Create `pipeline/scripts/backfill_country_codes.py`:

1. Use `pycountry` library for name-to-alpha2 lookup
2. Hardcoded fallback table for edge cases (scotland -> gb, england -> gb, palestine -> ps, etc.)
3. Read all 6,181 entities from production
4. Map each `t_any_countries` value to lowercase ISO alpha-2
5. Write `t_any_country_codes` array to each entity
6. Batch writes (500 per batch), --dry-run + --limit flags

```fish
# Install dependency
pip install pycountry --break-system-packages

# Dry run
python3 -u pipeline/scripts/backfill_country_codes.py --dry-run --limit 10

# Full run
python3 -u pipeline/scripts/backfill_country_codes.py
```

After backfill:
- Update `app/lib/models/query_clause.dart` knownFields to include `t_any_country_codes`
- Update `app/lib/models/location_entity.dart` to parse t_any_country_codes
- Verify: `t_any_country_codes contains "fr"` returns results

flutter analyze + flutter test after Dart changes.

### Step 7: Final Deploy

```fish
cd ~/dev/projects/kjtcom/app
flutter build web
cd ..
firebase deploy --only hosting
```

### Step 8: Regression Tests

Re-run key tests from v8.23:
1. `t_any_cuisines contains "french"` -> 80 results
2. `t_any_actors contains "huell howser"` -> 899 results
3. `t_any_keywords contains "medieval"` -> 653 results
4. `t_any_cuisines contains-any ["mexican", "italian"]` -> 332 results
5. `t_any_country_codes contains "fr"` -> results (NEW)
6. `t_any_country_codes contains "it"` -> results (NEW)
7. Click a result row -> detail panel opens (NEW)
8. "staging" badge absent (NEW)
9. Single cursor in query editor (NEW)

### Step 9: Security Scan + Artifacts

```
CHECKLIST:
[ ] Security: grep -rnI "AIzaSy" . -> only expected references
[ ] flutter analyze: 0 issues
[ ] flutter test: all pass
[ ] Detail panel opens on row click
[ ] "staging" badge removed
[ ] Cursor alignment fixed
[ ] t_any_country_codes populated on all 6,181 entities
[ ] t_any_country_codes queryable
[ ] firebase deploy success
```

Produce all 4 mandatory artifacts:

1. **docs/kjtcom-build-v8.24.md** - Diagnostic findings, fix details, backfill metrics
2. **docs/kjtcom-report-v8.24.md** - Success criteria, regression results, Phase 9 recommendation
3. **docs/kjtcom-changelog.md** - Append v8.24 at top
4. **README.md** - Phase 8 DONE (if all fixes land), updated field table with t_any_country_codes

Do NOT git commit or push.

---

## Section C: CLAUDE.md for v8.24

```markdown
# kjtcom - Agent Instructions (Claude Code)

## Read Order

1. docs/kjtcom-design-v8.24.md (4 work items with diagnostics)
2. docs/kjtcom-plan-v8.24.md (execute Section B)

## Context

Phase 8 UI Fixes + Country Codes. Four work items:
- W1 (P0): Fix detail panel - clicking a result row must open entity detail with t_any_* fields
- W2 (P0): Remove "staging" badge from app_shell
- W3 (P1): Fix cursor alignment in query editor (multiple cursors, misaligned position)
- W4 (P1): Backfill t_any_country_codes (ISO 3166-1 alpha-2) on all 6,181 entities

Deploy TWICE: after P0 fixes (Step 4), after all fixes (Step 7).

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

## Detail Panel Diagnostic (W1)

Read these files first to trace the break:
1. detail_panel.dart - what it renders
2. results_table.dart - row tap handler
3. selection_provider.dart - state management
4. app_shell.dart - widget tree layout
5. firestore_provider.dart - did v8.23 QueryResult refactor break selection?

The detail panel MUST show: entity name, pipeline badge, all t_any_* field cards, +filter/-exclude buttons, enrichment data.

## Data Fix Requirements

- backfill_country_codes.py: --dry-run, --limit flags
- Use pycountry library + hardcoded fallback for edge cases
- Store codes as lowercase: ["fr", "it", "us"]
- Dry-run before full run (G35)

## Permissions

- CANNOT: git add / commit / push
- CANNOT: sudo

## Artifact Rules - MANDATORY

1. docs/kjtcom-build-v8.24.md
2. docs/kjtcom-report-v8.24.md
3. docs/kjtcom-changelog.md (append v8.24)
4. README.md (Phase 8 DONE, add t_any_country_codes to field table)

## Formatting

- No em-dashes. Use " - " instead.
- Use "->" for arrows.
```

---

## Section D: Launch Prompt

```
Read CLAUDE.md, then read docs/kjtcom-design-v8.24.md for all 4 work items and docs/kjtcom-plan-v8.24.md for execution order.

Execute Section B in order:
1. W1: Diagnose and fix the detail panel - read detail_panel.dart, results_table.dart, selection_provider.dart, app_shell.dart, and firestore_provider.dart to trace why clicking a result row does not open the detail panel. Fix the break.
2. W2: Remove the "staging" badge from the UI.
3. Mid-iteration deploy (P0 fixes live).
4. W3: Fix cursor alignment in query_editor.dart - diagnose multiple cursors and misaligned position.
5. W4: Create and run backfill_country_codes.py (dry-run then full run). Update query_clause.dart knownFields and location_entity.dart model.
6. Final deploy.
7. Run regression tests (9 tests including new country code queries).
8. Produce all 4 mandatory artifacts.
```

---

## Timing Estimate

| Step | Est. Duration |
|------|---------------|
| Section A (pre-flight, human) | ~10 min |
| Steps 1-4 (detail panel + staging badge + deploy) | ~45 min |
| Step 5 (cursor fix) | ~30 min |
| Step 6 (country codes backfill + Dart updates) | ~30 min |
| Steps 7-9 (deploy + regression + artifacts) | ~30 min |
| **Total** | **~2.5-3 hours** |

---

## After v8.24

1. Commit: `git add . && git commit -m "KT 8.24 Phase 8 UI fixes + country codes" && git push`
2. Verify kylejeromethompson.com: detail panel works, staging gone, cursor fixed, country codes queryable
3. Phase 8 complete. Proceed to Phase 9 (App Optimization):
   - Lighthouse performance (FCP 7-14s target improvement)
   - Cookie consent
   - Analytics refinement
   - D12 resolution (== vs contains semantics)
   - Cursor-based pagination if needed
   - Algolia evaluation if fuzzy search needed
