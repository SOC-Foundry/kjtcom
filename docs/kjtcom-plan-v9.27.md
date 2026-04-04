# kjtcom - Plan v9.27 (Phase 9 - App Optimization: Visual Refresh + Tab Wiring)

**Pipeline:** kjtcom (cross-pipeline location intelligence platform)
**Phase:** 9 (App Optimization)
**Iteration:** 27 (global counter)
**Executor:** Claude Code
**Machine:** NZXTcos
**Date:** April 2026

---

## Section A: Pre-Flight (Human)

### IAO Pillar Pre-Flight Checklist

| # | Pillar | Verification | Command/Check |
|---|--------|-------------|---------------|
| P1 | Trident | $0 cost - flutter_map is free (OSM tiles) | No paid APIs |
| P2 | Artifact Loop | v8.26 docs archived | `ls docs/archive/kjtcom-*v8.26*` -> 4 files |
| P2 | Artifact Loop | v9.27 design + plan in docs/ | `ls docs/kjtcom-{design,plan}-v9.27.md` -> 2 files |
| P3 | Diligence | Design doc reviewed, 5 workstreams understood | Kyle approved |
| P4 | Pre-Flight | Git clean | `git status` -> clean |
| P4 | Pre-Flight | CLAUDE.md updated | `head -3 CLAUDE.md` -> references v9.27 |
| P4 | Pre-Flight | Flutter builds | `cd app && flutter build web` -> success |
| P4 | Pre-Flight | Firebase auth | `firebase projects:list` -> no error |
| P6 | Zero-Intervention | All 5 workstreams pre-specified with library choices | No TBD |
| P9 | Post-Flight | All 4 tabs functional, pagination working, visual refresh applied | Manual verification |

### A1: Archive v8.26 Docs

```fish
cd ~/dev/projects/kjtcom
mv docs/kjtcom-design-v8.26.md docs/kjtcom-plan-v8.26.md docs/kjtcom-build-v8.26.md docs/kjtcom-report-v8.26.md docs/archive/
```

### A2: Stage v9.27 Docs

```fish
cp ~/Downloads/kjtcom-design-v9.27.md docs/
cp ~/Downloads/kjtcom-plan-v9.27.md docs/
```

### A3: Update CLAUDE.md

Replace CLAUDE.md with the v9.27 version (Section C).

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

Read `docs/kjtcom-design-v9.27.md` for all 5 workstreams.

### Step 2: Add Dependencies

```fish
cd ~/dev/projects/kjtcom/app
```

Add to `pubspec.yaml`:
- `flutter_map: ^7.0.0` (or latest compatible with Flutter 3.41.6)
- `latlong2: ^0.9.0`
- `google_fonts: ^6.0.0` (already present - verify Cinzel is available)

```fish
flutter pub get
```

If `flutter_map` version conflicts, check pub.dev for the latest compatible version (G44).

### Step 3: Workstream 1 - Gothic/Cyber Visual Refresh

**Files:** `tokens.dart`, `theme.dart`, `app_shell.dart`, `results_table.dart`, `detail_panel.dart`

1. Add gothic tokens to `tokens.dart`:
   - `gothicFont: 'Cinzel'` (via google_fonts)
   - `borderGlow: BoxShadow(color: Color(0x334ADE80), blurRadius: 8)`
   - `gothicBorder: Border(...)` double-line treatment
   - `cornerAccentSize: 8.0`

2. Update card containers in `app_shell.dart`, `results_table.dart`, `detail_panel.dart`:
   - Apply gothic border decoration to main containers
   - Add glow effect on hover states
   - Keep query editor clean (no ornamental borders on input)

3. After changes: `flutter analyze` + `flutter test`

### Step 4: Workstream 5 - Search Results Pagination

**File:** `results_table.dart`, new `pagination_provider.dart`

1. Create `app/lib/providers/pagination_provider.dart`:
   - `pageSizeProvider`: StateProvider<int> (default 20, options: 20, 50, 100)
   - `currentPageProvider`: StateProvider<int> (default 0)

2. Update `results_table.dart`:
   - Add dropdown above table: `Show: 20 | 50 | 100`
   - Slice entity list: `entities.skip(page * pageSize).take(pageSize)`
   - Add page navigation below table: `< Previous | Page N of M | Next >`
   - Result count row shows total, pagination shows current window

3. After changes: `flutter analyze` + `flutter test`

### Step 5: Deploy Checkpoint #1 (Visual + Pagination)

```fish
cd ~/dev/projects/kjtcom/app
flutter build web
cd ..
firebase deploy --only hosting
```

Verify on kylejeromethompson.com:
- Gothic border treatments visible on containers
- Pagination dropdown works (20/50/100)
- Page navigation works
- Query results still function correctly

### Step 6: Workstream 3 - Map Tab

**New file:** `app/lib/widgets/map_tab.dart`
**Update:** `app/lib/widgets/kjtcom_tab_bar.dart` (wire Map tab to new widget)

1. Read `kjtcom_tab_bar.dart` to understand current tab structure
2. Read current Map tab content (likely placeholder or empty)
3. Create `map_tab.dart`:
   - FlutterMap widget with OpenStreetMap TileLayer
   - MarkerLayer from current query results
   - Pipeline-colored markers (gold/blue/red based on t_log_type)
   - On marker tap: set selectedEntityProvider -> detail panel opens
   - Initial bounds: fit all markers, fallback to Europe center
4. Wire into tab bar

5. Test: run a query, switch to Map tab, verify markers appear, click a marker.

6. If CORS issues with OSM tiles in CanvasKit (G43):
   - Try adding `--web-renderer html` to build
   - Or use a CORS-friendly tile server URL

7. After changes: `flutter analyze` + `flutter test`

### Step 7: Workstream 4 - Globe Tab

**New file:** `app/lib/widgets/globe_tab.dart`
**Update:** `app/lib/widgets/kjtcom_tab_bar.dart`

1. Create `globe_tab.dart` as a stats dashboard:
   - Globe hero background (globe_hero.jpg at 15% opacity, already an asset)
   - Continent cards: 7 continents, each showing entity count + country count + top 3 countries
   - Data from `t_any_continents` and `t_any_country_codes` across ALL production entities (not just current query)
   - Use a one-time Firestore aggregate query or precomputed stats provider
   - Country grid below: all countries sorted by entity count, clickable
   - Click a continent/country -> appends filter to query editor, switches to Results tab
   - Gothic border treatment on continent cards, Cinzel font for headers

2. Wire into tab bar

3. After changes: `flutter analyze` + `flutter test`

### Step 8: Workstream 2 - IAO Pillar Tab

**New file:** `app/lib/widgets/iao_tab.dart`
**Update:** `app/lib/widgets/kjtcom_tab_bar.dart`

1. Create `iao_tab.dart`:
   - **Trident SVG** at top: render the IAO trident as a custom SVG widget
     - Central shaft in teal (#0D9488)
     - Three prongs with labels in tech green on dark background
     - Gothic border frame around the graphic
   - **10 Pillar cards** in a scrollable ListView:
     - Each card: pillar number (large Cinzel, tech green), title (Cinzel, white), description (Geist Sans, secondary)
     - Gothic double-line border with corner accents
     - Subtle green glow on hover
   - **Stats footer**:
     - Total entities, pipelines, iterations, zero-intervention count
     - Compact horizontal row

2. All 10 pillar texts must be VERBATIM from the README/design doc. Do not summarize or rephrase.

3. Wire into tab bar as the 4th tab: Results | Map | Globe | IAO

4. After changes: `flutter analyze` + `flutter test`

### Step 9: Deploy Checkpoint #2 (All Tabs)

```fish
cd ~/dev/projects/kjtcom/app
flutter build web
cd ..
firebase deploy --only hosting
```

### Step 10: Full Functional Test

Test every tab and interaction on kylejeromethompson.com:

**Results tab:**
- [ ] Query returns results with pagination (default 20)
- [ ] Pagination dropdown (20/50/100) works
- [ ] Page navigation (Previous/Next) works
- [ ] Click result -> detail panel opens
- [ ] +filter/-exclude -> single line added (no duplicates)
- [ ] Gothic border treatment visible

**Map tab:**
- [ ] Switching to Map shows OpenStreetMap with markers
- [ ] Markers colored by pipeline
- [ ] Click marker -> detail panel opens (or shows entity name)
- [ ] Query changes update markers
- [ ] No CORS errors in console

**Globe tab:**
- [ ] Continent cards show entity/country counts
- [ ] Country grid shows all countries
- [ ] Click continent/country -> filters query, switches to Results
- [ ] Globe background visible

**IAO tab:**
- [ ] Trident graphic renders
- [ ] All 10 pillars displayed with correct text
- [ ] Gothic styling (Cinzel font, borders, glow)
- [ ] Stats footer shows correct numbers

### Step 11: Security Scan + Artifacts

```
CHECKLIST:
[ ] Security: grep -rnI "AIzaSy" . -> only expected
[ ] All 4 tabs functional
[ ] Pagination working (20/50/100)
[ ] Gothic/cyber visual refresh applied
[ ] flutter analyze: 0 issues
[ ] flutter test: all pass
[ ] firebase deploy: success
```

Produce all 4 mandatory artifacts:

1. **docs/kjtcom-build-v9.27.md** - Implementation details per workstream
2. **docs/kjtcom-report-v9.27.md** - Tab functional test results, visual refresh summary, Phase 9 next steps
3. **docs/kjtcom-changelog.md** - Append v9.27
4. **README.md** - Phase 9 IN PROGRESS, update if tab descriptions change

Do NOT git commit or push.

---

## Section C: CLAUDE.md for v9.27

```markdown
# kjtcom - Agent Instructions (Claude Code)

## Read Order

1. docs/kjtcom-design-v9.27.md (5 workstreams with architecture decisions)
2. docs/kjtcom-plan-v9.27.md (execute Section B)

## Context

Phase 9 App Optimization. Five workstreams:
1. Gothic/cyberpunk visual refresh (selective flourishes on dark SIEM base)
2. IAO Pillar tab (trident SVG + 10 pillar cards + stats footer)
3. Map tab fix (flutter_map + OpenStreetMap, entity markers)
4. Globe tab fix (stats dashboard with continent/country breakdown)
5. Search results pagination (20/50/100 dropdown, page navigation)

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

## New Dependencies

- flutter_map (latest compatible with Flutter 3.41.6) - check pub.dev (G44)
- latlong2
- google_fonts Cinzel already available via existing google_fonts package

## Visual Direction

Gothic + cyberpunk on dark SIEM base:
- Keep: #0D1117 surface, #4ADE80 tech green, Geist Sans/Mono
- Add: Cinzel font (google_fonts) for headers, double-line borders at 30% opacity, corner accents, green glow on hover
- Apply to: card containers, IAO tab, section headers
- Do NOT apply to: query editor input field (keep clean/functional)

## IAO Tab Content

All 10 pillar texts MUST be copied VERBATIM from the design doc. Do not summarize, rephrase, or abbreviate.

## Map Tab

- flutter_map + OpenStreetMap tiles (free, no API key)
- Markers from t_any_coordinates, colored by pipeline
- On marker tap: set selectedEntityProvider
- If CORS issues (G43): try --web-renderer html build flag

## Globe Tab

- Stats dashboard, NOT Three.js
- Continent cards + country grid from t_any_continents/t_any_country_codes
- Click -> appends filter clause, switches to Results tab
- Globe hero background at 15% opacity

## Pagination

- Dropdown: 20 | 50 | 100 (default 20)
- Client-side pagination from Firestore result set
- Page nav: Previous | Page N of M | Next

## Permissions

- CANNOT: git add / commit / push
- CANNOT: sudo

## Artifact Rules - MANDATORY

1. docs/kjtcom-build-v9.27.md
2. docs/kjtcom-report-v9.27.md (must include tab functional test results)
3. docs/kjtcom-changelog.md (append v9.27)
4. README.md (update if needed)

## Formatting

- No em-dashes. Use " - " instead.
- Use "->" for arrows.
```

---

## Section D: Launch Prompt

```
Read CLAUDE.md, then read docs/kjtcom-design-v9.27.md for all 5 workstreams and docs/kjtcom-plan-v9.27.md for execution order.

Execute Section B:
1. Add flutter_map + latlong2 to pubspec.yaml, flutter pub get
2. Workstream 1: Gothic/cyber visual refresh - add tokens, apply border treatments and glow effects
3. Workstream 5: Pagination - create pagination provider, add dropdown + page nav to results table
4. Deploy checkpoint #1 (visual + pagination live)
5. Workstream 3: Map tab - create map_tab.dart with flutter_map + OpenStreetMap, pipeline-colored markers
6. Workstream 4: Globe tab - create globe_tab.dart stats dashboard with continent cards + country grid
7. Workstream 2: IAO tab - create iao_tab.dart with trident SVG + 10 pillar cards (text VERBATIM from design doc) + stats footer
8. Wire all tabs in kjtcom_tab_bar.dart: Results | Map | Globe | IAO
9. Deploy checkpoint #2 (all tabs live)
10. Full functional test (all 4 tabs, pagination, detail panel from each tab)
11. Security scan + all 4 mandatory artifacts
```

---

## Timing Estimate

| Step | Est. Duration |
|------|---------------|
| Section A (pre-flight) | ~10 min |
| Steps 2-5 (visual + pagination + deploy) | ~60 min |
| Steps 6-7 (map + globe tabs) | ~90 min |
| Step 8 (IAO tab) | ~45 min |
| Steps 9-11 (deploy + test + artifacts) | ~30 min |
| **Total** | **~4-5 hours** |

---

## After v9.27

1. Commit: `git add . && git commit -m "KT 9.27 Phase 9 visual refresh + tab wiring" && git push`
2. Verify kylejeromethompson.com: all 4 tabs, gothic styling, pagination
3. Next iteration options:
   - v9.28: Lighthouse performance optimization (FCP target < 5s)
   - v9.28: Cookie consent + analytics events
   - v9.28: Mobile responsiveness polish
   - Phase 10: IAO retrospective + template publication
