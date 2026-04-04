# kjtcom - Plan v8.25 (Phase 8 - Filter Fix + README Overhaul)

**Pipeline:** kjtcom (cross-pipeline location intelligence platform)
**Phase:** 8 (Enrichment Hardening)
**Iteration:** 25 (global counter)
**Executor:** Claude Code
**Machine:** NZXTcos
**Date:** April 2026

---

## Section A: Pre-Flight (Human)

### IAO Pillar Pre-Flight Checklist

| # | Pillar | Verification | Command/Check |
|---|--------|-------------|---------------|
| P1 | Trident | $0 cost - Dart fix + markdown | No APIs needed |
| P2 | Artifact Loop | v8.24 docs archived | `ls docs/archive/kjtcom-*v8.24*` -> 4 files |
| P2 | Artifact Loop | v8.25 design + plan in docs/ | `ls docs/kjtcom-{design,plan}-v8.25.md` -> 2 files |
| P3 | Diligence | Design doc reviewed | Kyle has reviewed both workstreams |
| P4 | Pre-Flight | Git clean | `git status` -> clean |
| P4 | Pre-Flight | CLAUDE.md updated | `head -3 CLAUDE.md` -> references v8.25 |
| P4 | Pre-Flight | Flutter builds | `cd app && flutter build web` -> success |
| P4 | Pre-Flight | Firebase auth | `firebase projects:list` -> no error |
| P6 | Zero-Intervention | Both workstreams pre-specified | No TBD in design doc |
| P9 | Post-Flight | +filter test: 5 clicks = exactly 5 lines (or 1 if dedup) | Manual verification |

### A1: Archive v8.24 Docs

```fish
cd ~/dev/projects/kjtcom
mv docs/kjtcom-design-v8.24.md docs/kjtcom-plan-v8.24.md docs/kjtcom-build-v8.24.md docs/kjtcom-report-v8.24.md docs/archive/
```

### A2: Stage v8.25 Docs

```fish
cp ~/Downloads/kjtcom-design-v8.25.md docs/
cp ~/Downloads/kjtcom-plan-v8.25.md docs/
```

### A3: Update CLAUDE.md

Replace CLAUDE.md contents with the v8.25 version (Section C of this document).

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

Read `docs/kjtcom-design-v8.25.md` for both workstreams.

### Step 2: W-A - Fix +filter/-exclude Duplicate Bug

**File:** `app/lib/widgets/detail_panel.dart`

1. Read the file completely. Find the `+filter` and `-exclude` onPressed handlers.
2. Identify why multiple fires occur:
   - Does the handler call `ref.read(queryProvider.notifier).state = ...`?
   - Does the detail panel widget watch `queryProvider`?
   - If yes: modifying query triggers rebuild, rebuild re-registers handler, handler fires again.
3. Implement fix:

**Dedup approach (Option A from design doc):**
```dart
void _appendClause(String clause, WidgetRef ref) {
  final current = ref.read(queryProvider);
  // Check if this exact clause already exists
  if (current.contains(clause.trim())) return;
  // Append
  final newQuery = current.trimRight() + '\n' + clause;
  ref.read(queryProvider.notifier).state = newQuery;
}
```

**Guard flag approach (belt + suspenders):**
```dart
bool _isAppending = false;

void _appendClause(String clause, WidgetRef ref) {
  if (_isAppending) return;
  _isAppending = true;
  try {
    final current = ref.read(queryProvider);
    if (current.contains(clause.trim())) return;
    final newQuery = current.trimRight() + '\n' + clause;
    ref.read(queryProvider.notifier).state = newQuery;
  } finally {
    // Reset after microtask to prevent same-frame re-entry
    Future.microtask(() => _isAppending = false);
  }
}
```

Note: If detail_panel.dart is a StatelessWidget/ConsumerWidget, the `_isAppending` flag won't persist. Convert to StatefulWidget/ConsumerStatefulWidget if needed, or use a static/external flag.

4. After fix: `flutter analyze` + `flutter test`
5. Build and deploy:

```fish
cd ~/dev/projects/kjtcom/app
flutter build web
cd ..
firebase deploy --only hosting
```

6. Verify on kylejeromethompson.com:
   - Search `t_any_countries contains "italy"`
   - Click a result to open detail panel
   - Click +filter on `t_any_continents: "europe"` -> adds exactly 1 line
   - Click +filter on `t_any_continents: "europe"` again -> no-op (already exists)
   - Click +filter on `t_any_country_codes: "it"` -> adds exactly 1 new line
   - Click -exclude on a field -> adds exactly 1 line

### Step 3: W-B - README Overhaul

**File:** `README.md`

Rewrite the README from scratch. Use the current README as reference for sections that are already good (IAO methodology, mermaid chart, 10 pillars). The new README must follow this exact structure:

**1. Title + Badges + Intro**
- Keep existing badges (Flutter, Firebase, Gemini, Claude, MIT)
- Rewrite intro paragraph to mention: 3 live pipelines, 6,181 entities, functional NoSQL query system, live at kylejeromethompson.com
- Status line: `Phase 8 v8.25 | Status: Phase 8 Enrichment Hardening DONE`

**2. Live App (NEW section)**
```markdown
## Live App

**[kylejeromethompson.com](https://kylejeromethompson.com)** - Search 6,181 geocoded entities across 3 pipelines:

- **NoSQL query editor** with syntax highlighting, case-insensitive search, `contains` and `contains-any` operators
- **Result counts** with truncation indicators for large result sets
- **Entity detail panel** with t_any_* field cards, Google Places enrichment data, +filter/-exclude query builders
- **Pipeline-colored results** - CalGold (gold), RickSteves (blue), TripleDB (red)
- **Cross-pipeline search** - a single query spans all 3 datasets
```

**3. Architecture**
- Keep the existing pipeline diagram
- Add a second diagram showing the app query flow: Query Editor -> QueryClause Parser -> Firestore Provider -> arrayContains / arrayContainsAny -> Results Table + Detail Panel

**4. Data Architecture**
- Keep from v7.21 (single-collection, t_log_type discriminator, multi-database)

**5. Thompson Indicator Fields**
- Keep existing tables
- Add `t_any_country_codes` to the indicator fields table: `array[string] | ISO 3166-1 alpha-2 codes (v8.24) | ["fr", "it", "us"]`

**6. Pipelines**
- Keep current table (390/1865/805 videos, 899/4182/1100 entities, all Phase 7 DONE)
- Add bourdain as pending

**7. Query System (NEW section)**
```markdown
## Query System

The NoSQL query editor supports structured queries against Thompson Indicator Fields:

**Operators:**
- `contains` - array membership (e.g., `t_any_cuisines contains "french"`)
- `contains-any` - array membership for multiple values (e.g., `t_any_cuisines contains-any ["mexican", "italian"]`)
- `==` - equality (e.g., `t_log_type == "tripledb"`)

**Features:**
- Case-insensitive search (all values lowercased before dispatch)
- Syntax highlighting (5-color tokenizer: field/operator/value/keyword/collection)
- Result count badge with truncation indicator
- Multi-clause queries (first clause server-side, additional client-side from 1,000 results)
- Field validation against 22 known fields
- Parse error feedback for malformed input
- +filter/-exclude buttons in detail panel append to query

**Example queries:**
(list 5-8 example queries with expected result counts)
```

**8. IAO Methodology**
- Keep ENTIRE section as-is: mermaid chart, 10 pillars (verbatim), IAO components table, split-agent execution table, agent performance table

**9. Project Status**
- Update table: Phase 8 DONE v8.22-v8.25, Phase 9 Pending

**10. Tech Stack**
- Keep as-is

**11. Hardware**
- Add tsP3-cos:
```
tsP3-cos (Secondary Dev)
CPU:  Intel Core i9 (ThinkStation P3 Ultra SFF G2)
OS:   CachyOS (Arch-based) / fish shell
```

**12. Cost**
- Keep as-is

**13. Future Directions**
- Update HyperAgents paragraph with v8.22 conclusion (defer to Phase 10)
- Update search paragraph with Algolia assessment (defer unless fuzzy search needed)
- Keep SIEM migration tooling paragraph

**14. Changelog**
- Truncate to last 5 iterations (v8.25 through v7.21)
- Add note: "Full changelog: [docs/kjtcom-changelog.md](docs/kjtcom-changelog.md)"

**15. Author + Citing**
- Keep as-is

After rewrite: `flutter analyze` (ensure no README references break anything).

### Step 4: Final Verification

```fish
# Build and deploy
cd ~/dev/projects/kjtcom/app
flutter build web
cd ..
firebase deploy --only hosting
```

Verify:
1. +filter bug fixed (single line per click, dedup works)
2. README renders correctly on GitHub

### Step 5: Security Scan + Artifacts

```
CHECKLIST:
[ ] Security: grep -rnI "AIzaSy" . -> only expected references
[ ] +filter: 1 line per click, dedup prevents duplicates
[ ] -exclude: 1 line per click
[ ] README: Phase 8 DONE, 6,181 entities, Live App section, Query System section
[ ] README: t_any_country_codes in field table
[ ] README: changelog truncated to last 5
[ ] flutter analyze: 0 issues
[ ] flutter test: all pass
[ ] firebase deploy: success
```

Produce all 4 mandatory artifacts:

1. **docs/kjtcom-build-v8.25.md** - Filter fix diagnostic, README diff summary
2. **docs/kjtcom-report-v8.25.md** - Success criteria, Phase 8 complete summary, Phase 9 recommendation
3. **docs/kjtcom-changelog.md** - Append v8.25 at top
4. **README.md** - Complete overhaul (this IS the primary deliverable)

Do NOT git commit or push.

---

## Section C: CLAUDE.md for v8.25

```markdown
# kjtcom - Agent Instructions (Claude Code)

## Read Order

1. docs/kjtcom-design-v8.25.md (filter fix + README overhaul spec)
2. docs/kjtcom-plan-v8.25.md (execute Section B)

## Context

Phase 8 final cleanup. Two workstreams:
- W-A: Fix +filter/-exclude duplicate bug in detail_panel.dart (adds 1-4 lines per click, should add exactly 1)
- W-B: Comprehensive README overhaul - full rewrite to reflect current state

kjtcom project ID: kjtcom-c78cd
Production: 6,181 entities (899 CalGold + 4,182 RickSteves + 1,100 TripleDB)
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

## Filter Fix (W-A)

Root cause: +filter handler modifies queryProvider, which triggers a detail panel rebuild, which re-fires the handler. Fix with:
1. Dedup: check if clause already exists in current query before appending
2. Guard flag: prevent re-entry during same event loop tick
3. May need to convert StatelessWidget to ConsumerStatefulWidget for the guard flag

Test: click +filter 3 times on same field -> only 1 line added (dedup). Click +filter on 3 different fields -> 3 lines added.

## README Overhaul (W-B)

Complete rewrite following the exact structure in the design doc. Key requirements:
- NEW "Live App" section with kylejeromethompson.com link and feature list
- NEW "Query System" section documenting operators, features, examples
- Add t_any_country_codes to indicator fields table
- Update Project Status: Phase 8 DONE
- Keep IAO section EXACTLY as-is (mermaid chart + 10 pillars verbatim)
- Truncate changelog to last 5 iterations, link to full changelog
- Add tsP3-cos to Hardware section

## Permissions

- CANNOT: git add / commit / push
- CANNOT: sudo

## Artifact Rules - MANDATORY

1. docs/kjtcom-build-v8.25.md
2. docs/kjtcom-report-v8.25.md (include Phase 8 complete summary + Phase 9 recommendation)
3. docs/kjtcom-changelog.md (append v8.25)
4. README.md (COMPLETE OVERHAUL - this is the primary deliverable)

## Formatting

- No em-dashes. Use " - " instead.
- Use "->" for arrows.
```

---

## Section D: Launch Prompt

```
Read CLAUDE.md, then read docs/kjtcom-design-v8.25.md for both workstreams and docs/kjtcom-plan-v8.25.md for execution order.

Execute Section B:
1. W-A: Read detail_panel.dart completely. Find the +filter/-exclude onPressed handlers. Diagnose why they fire multiple times per click (likely: modifying queryProvider triggers rebuild which re-fires handler). Fix with dedup check + guard flag. flutter analyze + flutter test.
2. Build and deploy the filter fix.
3. W-B: Rewrite README.md from scratch following the exact structure in the design doc. Key additions: "Live App" section, "Query System" section, t_any_country_codes in field table, Phase 8 DONE in status, changelog truncated to last 5.
4. Keep the IAO section EXACTLY as-is including the mermaid trident chart and all 10 pillars verbatim.
5. Final build, deploy, security scan.
6. Produce all 4 mandatory artifacts.
```

---

## Timing Estimate

| Step | Est. Duration |
|------|---------------|
| Section A (pre-flight, human) | ~10 min |
| Step 2 (filter fix + deploy) | ~30 min |
| Step 3 (README overhaul) | ~45 min |
| Steps 4-5 (final deploy + artifacts) | ~20 min |
| **Total** | **~1.5-2 hours** |

---

## After v8.25

1. Commit: `git add . && git commit -m "KT 8.25 Phase 8 filter fix + README overhaul" && git push`
2. Verify on GitHub: README renders with Live App section, Query System section, mermaid chart
3. **Phase 8 COMPLETE.** Proceed to Phase 9 (App Optimization):
   - Lighthouse performance (FCP 7-14s)
   - Cookie consent
   - Analytics custom events
   - D12 resolution
   - Cursor-based pagination
   - Algolia evaluation
