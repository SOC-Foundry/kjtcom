# kjtcom - Plan v9.28 (Phase 9 - Gotcha Tab + Schema Builder + JSON Copy)

**Pipeline:** kjtcom (cross-pipeline location intelligence platform)
**Phase:** 9 (App Optimization)
**Iteration:** 28 (global counter)
**Executor:** Claude Code
**Machine:** NZXTcos
**Date:** April 2026

---

## Section A: Pre-Flight (Human)

### IAO Pillar Pre-Flight Checklist

| # | Pillar | Verification | Command/Check |
|---|--------|-------------|---------------|
| P1 | Trident | $0 cost - Dart only | No APIs |
| P2 | Artifact Loop | v9.27 docs archived | `ls docs/archive/kjtcom-*v9.27*` -> 4 files |
| P2 | Artifact Loop | v9.28 design + plan in docs/ | `ls docs/kjtcom-{design,plan}-v9.28.md` -> 2 files |
| P3 | Diligence | Design doc reviewed | Kyle approved 4 work items |
| P4 | Pre-Flight | Git clean | `git status` -> clean |
| P4 | Pre-Flight | CLAUDE.md updated | `head -3 CLAUDE.md` -> references v9.28 |
| P4 | Pre-Flight | Flutter builds | `cd app && flutter build web` -> success |
| P4 | Pre-Flight | Firebase auth | `firebase projects:list` -> no error |
| P6 | Zero-Intervention | All 4 items pre-specified | No TBD |
| P9 | Post-Flight | MANDATORY deploy + live verification | Build + deploy + browser test |

### A1: Archive v9.27 Docs

```fish
cd ~/dev/projects/kjtcom
mv docs/kjtcom-design-v9.27.md docs/kjtcom-plan-v9.27.md docs/kjtcom-build-v9.27.md docs/kjtcom-report-v9.27.md docs/archive/
```

### A2: Stage v9.28 Docs

```fish
cp ~/Downloads/kjtcom-design-v9.28.md docs/
cp ~/Downloads/kjtcom-plan-v9.28.md docs/
```

### A3: Update CLAUDE.md

Replace CLAUDE.md with the v9.28 version (Section C).

### A4: Verify Flutter + Firebase

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

Read `docs/kjtcom-design-v9.28.md` for all 4 work items.

### Step 2: W3 - Copy JSON Button on Detail Panel

Start with the smallest, most contained change.

**File:** `app/lib/widgets/detail_panel.dart`, `app/lib/models/location_entity.dart`

1. Ensure `LocationEntity` has a `Map<String, dynamic> rawData` field populated from Firestore snapshot
2. Add a copy icon button in the detail panel header row (next to entity name and close button)
3. On tap: `Clipboard.setData(ClipboardData(text: JsonEncoder.withIndent('  ').convert(entity.rawData)))`
4. Show SnackBar: "JSON copied to clipboard" (2 seconds, tech green accent)

flutter analyze + flutter test.

### Step 3: W1 - Gotcha Tab

**New file:** `app/lib/widgets/gotcha_tab.dart`
**Update:** `app/lib/widgets/kjtcom_tab_bar.dart`

1. Create `gotcha_tab.dart` with:
   - Header: "Gotcha Registry" in Cinzel + subtitle
   - Filter toggle row: All | Active | Resolved (default: All)
   - Scrollable list of gotcha cards
   - Each card: ID badge, title, prevention text, status badge
   - Gothic border treatment matching IAO tab

2. Hardcode all 42 gotchas from the design doc registry table. Use a Dart list of Gotcha objects.

3. Wire into tab bar.

flutter analyze + flutter test.

### Step 4: W2 - Schema Tab with Query Builder

**New file:** `app/lib/widgets/schema_tab.dart`
**Update:** `app/lib/widgets/kjtcom_tab_bar.dart`

1. Create `schema_tab.dart` with:
   - Header: "Thompson Indicator Fields" in Cinzel + subtitle
   - Scrollable list of field cards
   - Each card: field name (Geist Mono), type badge, description, example values
   - "+ Add to query" button (tech green) on each field
   - On click: append `| where {field} contains ""` to query provider (or `== ""` for t_log_type)
   - Switch to Results tab after appending
   - No "Add to query" button on t_any_coordinates and t_any_geohashes (view only)

2. Field data sourced from `knownFields` in `query_clause.dart` plus descriptions/examples hardcoded in schema_tab.dart.

3. Wire into tab bar.

4. Tab order: Results | Map | Globe | IAO | Gotcha | Schema

flutter analyze + flutter test.

### Step 5: Post-Flight Deploy + Live Verification (MANDATORY)

```fish
cd ~/dev/projects/kjtcom/app
flutter build web
cd ..
firebase deploy --only hosting
```

**Open kylejeromethompson.com and verify each feature:**

| # | Test | Expected |
|---|------|----------|
| 1 | Click Gotcha tab | All 42 gotchas displayed with status badges |
| 2 | Toggle Active filter | Only active gotchas shown |
| 3 | Toggle Resolved filter | Only resolved gotchas shown |
| 4 | Click Schema tab | All 22 fields displayed |
| 5 | Click "+ Add to query" on t_any_cuisines | Clause appended, switched to Results tab |
| 6 | Click "+ Add to query" on t_log_type | Uses == operator |
| 7 | t_any_coordinates shows no "Add to query" | View only |
| 8 | Run a query, click a result | Detail panel opens |
| 9 | Click copy icon on detail panel | JSON copied, SnackBar shown |
| 10 | Paste clipboard content | Valid JSON with all entity fields |
| 11 | All 6 tabs clickable | Results, Map, Globe, IAO, Gotcha, Schema |
| 12 | Previous tabs still work | Map markers, Globe stats, IAO pillars |

**If any test fails: diagnose, fix, rebuild, redeploy, re-verify.**

### Step 6: Security Scan + Artifacts

```
CHECKLIST:
[ ] Security: grep -rnI "AIzaSy" . -> only expected
[ ] All 6 tabs functional
[ ] Gotcha filter works
[ ] Schema builder adds clauses to query
[ ] JSON copy works on detail panel
[ ] flutter analyze: 0 issues
[ ] flutter test: all pass
[ ] firebase deploy: success
[ ] Live site verified in browser
```

Produce all 4 mandatory artifacts:

1. **docs/kjtcom-build-v9.28.md** - Implementation details, live verification results
2. **docs/kjtcom-report-v9.28.md** - Success criteria, full gotcha registry, Phase 9 status
3. **docs/kjtcom-changelog.md** - Append v9.28
4. **README.md** - Update tab descriptions if needed

Do NOT git commit or push.

---

## Section C: CLAUDE.md for v9.28

```markdown
# kjtcom - Agent Instructions (Claude Code)

## Read Order

1. docs/kjtcom-design-v9.28.md (4 work items + full gotcha registry G1-G44)
2. docs/kjtcom-plan-v9.28.md (execute Section B)

## Context

Phase 9 App Optimization. Four work items:
- W1: Gotcha tab (full registry G1-G42, status badges, filter toggle)
- W2: Schema tab with query builder (22 fields, click to add clause to query)
- W3: Copy JSON button on detail panel (clipboard + snackbar confirmation)
- W4: Post-flight deploy testing standard (MANDATORY build + deploy + live verify)

Tab order: Results | Map | Globe | IAO | Gotcha | Schema

kjtcom project ID: kjtcom-c78cd
Production: 6,181 entities
Live: kylejeromethompson.com

## Shell - MANDATORY

- All commands in fish shell
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

## Post-Flight Deploy (MANDATORY - W4)

After all code changes:
1. flutter build web
2. firebase deploy --only hosting
3. Open kylejeromethompson.com in browser
4. Verify EVERY new feature on the live site
5. Document results in build log
6. If any feature fails live: fix, rebuild, redeploy

## Gotcha Tab (W1)

- Hardcode all 42 gotchas as Dart objects (from design doc registry table)
- Cards: ID badge, title, prevention, status badge (ACTIVE green / RESOLVED dimmed / DOCUMENTED orange)
- Filter toggle: All | Active | Resolved
- Gothic border treatment, Cinzel header

## Schema Tab (W2)

- 22 Thompson Indicator Fields from knownFields + descriptions/examples
- Each field card: name (Geist Mono), type, description, examples
- "+ Add to query" button -> appends clause to queryProvider, switches to Results tab
- t_log_type uses == operator, all t_any_* use contains
- t_any_coordinates and t_any_geohashes are view-only (no add button)

## JSON Copy (W3)

- Copy icon in detail panel header (next to entity name / close)
- Copies full entity rawData as indented JSON
- SnackBar confirmation: "JSON copied to clipboard"
- LocationEntity must have rawData: Map<String, dynamic> from Firestore snapshot

## Permissions

- CANNOT: git add / commit / push
- CANNOT: sudo

## Artifact Rules - MANDATORY

1. docs/kjtcom-build-v9.28.md (must include live verification results)
2. docs/kjtcom-report-v9.28.md (full gotcha registry + success criteria)
3. docs/kjtcom-changelog.md (append v9.28)
4. README.md (update tab list if changed)

## Formatting

- No em-dashes. Use " - " instead.
- Use "->" for arrows.
```

---

## Section D: Launch Prompt

```
Read CLAUDE.md, then read docs/kjtcom-design-v9.28.md for all 4 work items (including full gotcha registry G1-G44 and schema field table) and docs/kjtcom-plan-v9.28.md for execution order.

Execute Section B:
1. W3: Add copy JSON button to detail panel. Ensure LocationEntity has rawData field. Clipboard + SnackBar.
2. W1: Create gotcha_tab.dart with all 42 gotchas hardcoded from the design doc. Status badges, filter toggle. Wire into tab bar.
3. W2: Create schema_tab.dart with all 22 fields from design doc. "+ Add to query" click appends clause and switches to Results tab. Wire into tab bar.
4. Tab order: Results | Map | Globe | IAO | Gotcha | Schema
5. flutter analyze + flutter test after each work item.
6. MANDATORY: flutter build web + firebase deploy --only hosting + open kylejeromethompson.com and verify ALL 12 tests from the plan. Document results.
7. Produce all 4 mandatory artifacts. Build log must include live verification results.
```

---

## Timing Estimate

| Step | Est. Duration |
|------|---------------|
| Section A (pre-flight) | ~5 min |
| Step 2 (JSON copy) | ~20 min |
| Step 3 (Gotcha tab) | ~45 min |
| Step 4 (Schema tab) | ~45 min |
| Step 5 (deploy + verify) | ~15 min |
| Step 6 (artifacts) | ~15 min |
| **Total** | **~2.5-3 hours** |

---

## After v9.28

1. Commit: `git add . && git commit -m "KT 9.28 gotcha tab + schema builder + JSON copy" && git push`
2. Verify kylejeromethompson.com: all 6 tabs, JSON copy, schema builder
3. Next iteration options:
   - v9.29: Lighthouse performance (FCP < 5s target)
   - v9.29: Cookie consent + analytics events
   - v9.29: Mobile responsiveness polish
   - Phase 10: IAO retrospective + template publication
