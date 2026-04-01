# kjtcom Comprehensive Status Report

**Date:** 2026-04-01
**Branch:** `main`
**Latest commit:** `1a99abd` - "KT completed 6.20 and updated README"
**Total commits:** 17

---

## 1. README vs Reality

The README is well-maintained and generally accurate. Discrepancies found:

| Area | README Says | Reality | Severity |
|------|-------------|---------|----------|
| **Phase status line** | "Phase 6e v6.20" / "Status: Phase 6e Deploy DONE" | Phase 6e was indeed completed in v6.20. However, the v7.21 design and plan docs exist in `docs/`, indicating Phase 7 work has been planned. README still reflects v6.20 as the latest. | Low - correct at time of last commit |
| **Phase 6e Deploy iteration** | Phase table shows 6e as DONE at v6.19 | v6.20 was a visual polish sub-iteration of 6e. The table says "6e Deploy DONE v6.19" but the changelog describes v6.20 as "Phase 6e - Visual Polish". Phase 6e spans v6.19-v6.20 but the table only shows v6.19. | Low |
| **Phase 7 status** | "Pending" with no iteration | v7.21 design and plan docs exist. The design doc's phase table says "IN PROGRESS v7.21". README hasn't been updated yet. | Medium - inconsistent |
| **Phase 5 RickSteves** | "CalGold DONE v5.14" (no mention of RickSteves Phase 5 status) | Design doc v7.21 says "RickSteves IN PROGRESS v5.15". No v5.15 artifacts exist in docs/ or archive/. | Medium - invisible state |
| **Entity counts** | CalGold 899, RickSteves 1,035 (total 1,934) | Matches v5.14 + v4.13 final counts. Correct. | None |
| **Citing section** | Duplicated BibTeX block (lines 479-497) | Two identical `@misc{thompson2026iao}` blocks. Copy-paste artifact. | Low |
| **File structure** | Shows `requirements/` | `requirements/` directory contains only `install.fish`. Not listed by find. | Low |
| **Pipeline table** | Shows `tripledb` and `bourdain` as future pipelines | No config exists for either in `pipeline/config/`. Correct - they're listed as candidates. | None |
| **ricksteves pipeline.json** | `t_schema_version: 2` in pipeline.json | Schema.json says version 3. Pipeline.json metadata hasn't been bumped. | Low |

---

## 2. CLAUDE.md Staleness

**CLAUDE.md references iteration: v6.19 (Phase 6e Deploy)**
**Should reference: v7.21 (Phase 7 Firestore Load)**

| Issue | Detail |
|-------|--------|
| **Read Order** | Points to `docs/kjtcom-report-v6.18.md` and `docs/kjtcom-design-v6.15.md`. Both are now in `docs/archive/`. These files don't exist at the referenced paths. |
| **Context** | Says "Phase 6e Deploy" - Phase 6e is complete. Should be Phase 7. |
| **Tasks** | Lists flutter build + firebase deploy + analytics tasks - all completed in v6.19. Should list Phase 7 migration tasks. |
| **Artifact Rules** | References v6.19 artifacts - should be v7.21. |
| **Prompt block** | Contains the v6.19 launch prompt embedded in the file (lines 50-53). This is metadata that was committed as part of the file content. |
| **v7.21 CLAUDE.md ready** | The plan doc `docs/kjtcom-plan-v7.21.md` (lines 340-395) contains a fully prepared CLAUDE.md replacement for v7.21. It just hasn't been applied yet. |

**Verdict:** CLAUDE.md is 2 iterations stale (should be v7.21, is v6.19). The replacement text is already written in the plan doc.

---

## 3. GEMINI.md Staleness

**GEMINI.md references: Phase 6a Discovery (v6.15)**
**Should reference: Current phase (v7.21 or later)**

| Issue | Detail |
|-------|--------|
| **Read Order** | Points to `docs/kjtcom-design-v6.15.md` and `docs/kjtcom-plan-v6.15.md`. Both now in archive. |
| **Context** | "Phase 6a Discovery. Scrape 8 public competitor sites via Playwright MCP." - This was 5 iterations ago. |
| **MCP Tools** | References Firecrawl cert issues (G28) and Panther scraping ban (G29) - both phase-6a-specific. |
| **Scraping Parameters** | Viewport dimensions for web scraping - no longer relevant. |
| **Artifact Rules** | v6.15 artifacts. |
| **Machine reference** | References "tsP3-cos (P3 Ultra)" - the README and latest plan reference different machines. |

**Verdict:** GEMINI.md is 6 iterations stale. Not blocking since Gemini CLI doesn't appear to be the executor for Phase 7, but it should be updated or marked as dormant.

---

## 4. docs/ Current State

Active files in `docs/`:

| File | Iteration | Matches Latest? | Notes |
|------|-----------|-----------------|-------|
| `kjtcom-changelog.md` | All (v0.5 - v6.20) | Yes | Comprehensive changelog, v2.9 is out of chronological order (at bottom). |
| `kjtcom-design-v7.21.md` | v7.21 | Yes | Phase 7 design with TripleDB schema mapping. Ready for execution. |
| `kjtcom-plan-v7.21.md` | v7.21 | Yes | Phase 7 execution plan with full CLAUDE.md replacement. |
| `install.fish` | N/A | N/A | Environment setup script (14K lines). |
| `tmux-v5.14.md` | v5.14 | Stale | tmux runner notes from Phase 5. Should be archived. |

**Issue:** `tmux-v5.14.md` is orphaned in `docs/` - it belongs in `docs/archive/` with the other v5.14 artifacts.

---

## 5. docs/archive/ Completeness

### CalGold Pipeline (Phases 0-5)

| Iteration | Design | Plan | Build | Report | Complete? |
|-----------|--------|------|-------|--------|-----------|
| v0.5 | Yes | Yes | Yes | Yes | Yes |
| v1.6 | Yes (shared as v1.6) | Yes (shared as v1.6) | Yes (v1.6) | Yes (v1.6) | Yes |
| v2.8 | Yes | Yes | Yes | Yes | Yes |
| v3.10 | Yes | Yes | Yes | Yes | Yes |
| v4.12 | Yes | Yes | Yes | Yes | Yes |
| v5.14 | Yes | Yes | Yes | Yes | Yes |

### RickSteves Pipeline (Phases 1-4)

| Iteration | Design | Plan | Build | Report | Complete? |
|-----------|--------|------|-------|--------|-----------|
| v1.7 | Yes | Yes | Yes | Yes | Yes |
| v2.9 | Yes | Yes | Yes | Yes | Yes |
| v3.11 | Yes | Yes | Yes | Yes | Yes |
| v4.13 | Yes | Yes | Yes | Yes | Yes |

### kjtcom App (Phase 6)

| Iteration | Design | Plan | Build | Report | Complete? |
|-----------|--------|------|-------|--------|-----------|
| v6.15 | Yes | Yes | Yes | Yes | Yes |
| v6.16 | No | No | Yes | Yes | **Missing design+plan** |
| v6.17 | No | No | Yes | Yes | **Missing design+plan** |
| v6.18 | No | No | Yes | Yes | **Missing design+plan** |
| v6.19 | No | No | Yes | Yes | **Missing design+plan** |
| v6.20 | No | No | Yes | Yes | **Missing design+plan** |

**Gap analysis:** Iterations v6.16 through v6.20 have build+report docs but no standalone design or plan docs. This is likely intentional - v6.15 was the overarching design/plan for all of Phase 6, with subsequent sub-phases (6b-6e) producing only build and report artifacts. This is consistent with the IAO methodology where the design doc is a "living" document shared across sub-phases.

### Other archived artifacts
- `deploy-desktop-verification.png` - screenshot from v6.19
- `qa-desktop-1440x900.png`, `qa-mobile-375x812.png`, `qa-tablet-768x1024.png` - QA screenshots from v6.18
- `smoke-chrome-1440x900.png`, `smoke-firefox-1440x900.png` - smoke test screenshots from v6.19
- `v6.20-clean-build.png`, `v6.20-desktop-cachebust.png`, `v6.20-desktop-verification.png`, `v6.20-webapp-verify.png` - v6.20 verification screenshots
- `kjtcom-query-mockup.html` - HTML mockup from design phase
- `kjtcom-changelog-v1.6.md`, `calgold-changelog-v0.5.md`, `ricksteves-changelog-v1.7.md` - early per-pipeline changelogs (superseded by unified changelog)

**No missing iterations detected.** Archive is complete.

---

## 6. App Inventory

### Dart Files (16 total)

| File | Lines | Purpose | v6.20 Feature? |
|------|-------|---------|----------------|
| `main.dart` | 27 | App entry, Firebase init, Riverpod scope | Core |
| `firebase_options.dart` | 22 | Firebase config (API key, project ID, GA4 measurement ID) | Core |
| `models/location_entity.dart` | 59 | Firestore doc -> typed Dart object (t_any_* fields) | Core |
| `models/query_clause.dart` | 47 | Parse query editor syntax (where/contains/==) | Core |
| `providers/firestore_provider.dart` | 77 | Firestore stream with arrayContains queries | Core |
| `providers/query_provider.dart` | 21 | Query text state management | Core |
| `providers/selection_provider.dart` | 5 | Selected entity state | Core |
| `theme/theme.dart` | 57 | Dark theme builder from tokens | Core |
| `theme/tokens.dart` | 103 | Design tokens (colors, typography, spacing, breakpoints) | Core |
| `widgets/app_shell.dart` | 174 | Root layout scaffold | Core |
| `widgets/detail_panel.dart` | 284 | Entity detail with +filter/-exclude buttons | Core |
| `widgets/entity_count_row.dart` | 135 | "X entities across Y countries" with count-up animation | **v6.20** |
| `widgets/globe_hero.dart` | 40 | Globe background at 15% opacity | **v6.20** |
| `widgets/kjtcom_tab_bar.dart` | 58 | Results/Map/Globe tabs | Core |
| `widgets/pipeline_badge.dart` | 30 | Pipeline-colored badges (CG/RS/TD/NR) | Core |
| `widgets/query_editor.dart` | 320 | Syntax-highlighted editor with rotating queries + blinking cursor | **v6.20** |
| `widgets/results_table.dart` | 181 | 5-column responsive data table with pipeline dots | Core |
| `test/widget_test.dart` | 24 | QueryClause parsing tests (3 tests) | Core |

### v6.20 Changelog Verification

| Feature | Present in Code? | Status |
|---------|------------------|--------|
| Syntax-highlighted query editor | Yes - `query_editor.dart` with 5-color regex tokenizer | Confirmed |
| Results table | Yes - `results_table.dart` with 5 columns | Confirmed |
| Detail panel | Yes - `detail_panel.dart` with +filter/-exclude | Confirmed |
| Pipeline-colored dots | Yes - `pipeline_badge.dart` + `tokens.dart` pipeline color map | Confirmed |
| Rotating example queries | Yes - `query_editor.dart` (5 queries, 6s cycle) | Confirmed |
| Count-up animation | Yes - `entity_count_row.dart` (600ms easeOut) | Confirmed |
| Globe background | Yes - `globe_hero.dart` (15% opacity, globe_hero.jpg) | Confirmed |
| Blinking cursor | Yes - `query_editor.dart` (530ms interval) | Confirmed |

**App matches v6.20 changelog description completely.**

---

## 7. Pipeline Script Inventory

| Script | Phase | Purpose | Library Status |
|--------|-------|---------|----------------|
| `phase1_acquire.py` | 1 | YouTube -> MP3 via yt-dlp | OK |
| `phase2_transcribe.py` | 2 | MP3 -> JSON via faster-whisper (CUDA) | OK |
| `phase3_extract.py` | 3 | Transcript -> entities via Gemini Flash | **Uses `google.genai`** (migrated from `google.generativeai` in v1.7) |
| `phase4_normalize.py` | 4 | Raw -> Thompson Fields (t_any_*) | OK |
| `phase5_geocode.py` | 5 | Nominatim geocoding + geohash | OK |
| `phase6_enrich.py` | 6 | Google Places enrichment | OK |
| `phase7_load.py` | 7 | JSONL -> Firestore staging | OK |
| `utils/checkpoint.py` | Util | Checkpoint/resume tracking | OK |
| `utils/geohash.py` | Util | Geohash wrapper | OK |
| `utils/thompson_schema.py` | Util | Core normalization + keyword tokenization | OK |
| `group_b_runner.sh` | Util | tmux unattended runner | OK |
| `__init__.py` | Util | Package init | OK |

**No deprecated library references.** The `google.generativeai` -> `google.genai` migration was completed in v1.7.

---

## 8. Schema State

### calgold/schema.json
- `schema_version`: **3**
- Fields: names, people, cities, countries (default: "us"), states (default: "ca"), counties, regions, keywords, categories, video_ids, actors, roles, cuisines, dishes, eras, continents
- **All v3 fields present.** Complete.

### ricksteves/schema.json
- `schema_version`: **3**
- Fields: names, people, cities, countries, states (as `state_province`), regions, keywords, categories, video_ids, actors, roles, shows, eras, continents
- **All v3 fields present.** Complete.
- Note: `cuisines` and `dishes` are not in ricksteves schema mapping (appropriate for a travel show vs food show).

### calgold/pipeline.json
- `t_schema_version`: **1** (metadata says v1, actual schema.json is v3)
- **Discrepancy:** pipeline.json metadata hasn't been bumped to match schema.json v3.

### ricksteves/pipeline.json
- `t_schema_version`: **2** (metadata says v2, actual schema.json is v3)
- **Discrepancy:** Same issue - pipeline.json metadata is behind schema.json.

These discrepancies are cosmetic - the actual schema enforcement happens in `phase4_normalize.py` which reads `schema.json`, not `pipeline.json`'s version field.

---

## 9. Security Scan

```
grep -rnI "AIzaSy" . --include='*.py' --include='*.dart' --include='*.md' --include='*.json' --include='*.ts'
```

**Findings:**

| File | Line | Content | Verdict |
|------|------|---------|---------|
| `app/lib/firebase_options.dart:13` | `apiKey: 'AIzaSyCBw0VLhPbQ-h5mCONdQyGz9WFedxRvJas'` | **Firebase Web API key** - this is a public client key by design. Firebase Web API keys are intended to be shipped in client code. Security is enforced via Firestore rules (read-only, write-denied). | EXPECTED |
| 26 matches in `docs/` and `CLAUDE.md`/`GEMINI.md` | All are references to the `grep -rnI "AIzaSy"` security scan command itself | EXPECTED |

**No leaked secret keys.** The only actual key value is the Firebase Web API key in `firebase_options.dart`, which is a public client identifier (not a secret).

---

## 10. Files That Shouldn't Be Tracked

### Tracked by git but should be in .gitignore:

| File(s) | Count | Issue | Priority |
|---------|-------|-------|----------|
| `.CLAUDE.md.kate-swp` | 1 | Kate editor swap file | **High** - active editor artifact |
| `.playwright-mcp/*.log` | 8 | Playwright MCP console logs | **High** - ephemeral test output |
| `.playwright-mcp/*.yml` | 23 | Playwright MCP page snapshots | **High** - ephemeral test output |
| `extract_v4.12.log`, `extract_v4.13.log` | 2 | Pipeline extraction logs | **Medium** - regeneratable |
| `transcribe.log`, `transcribe_v3.11.log`, `transcribe_v4.12.log`, `transcribe_v4.13.log` | 4 | Pipeline transcription logs | **Medium** - regeneratable |
| `test.log` | 1 | Test output log | **Medium** |
| `pipeline/data/calgold/logs/*.log` | 2 | Production run logs | **Low** - historical reference |
| `app/.metadata` | 1 | Flutter metadata | **Low** |
| `audios.txt`, `transcripts.txt` | 2 | Scratch/temp files | **Medium** |
| `update_readme.py` | 1 | One-off script | **Low** |
| `functions/lib/*` | 3 | Compiled Cloud Functions output (index.js, index.d.ts, index.js.map) | **Medium** - build artifact |
| `app/.idea/*` | 5 | IntelliJ/Android Studio IDE config | **Medium** |
| `app/.flutter-plugins-dependencies` | 1 | Flutter generated file | **Low** |
| `app/kjtcom.iml` | 1 | IntelliJ module file | **Low** |
| `app/.firebaserc` | 1 | Firebase project alias file | **Low** - but contains project config |

### .gitignore gaps:

The `.gitignore` is missing entries for:
```
*.kate-swp
*.swp
*.log
.playwright-mcp/
app/.idea/
app/.metadata
app/.flutter-plugins-dependencies
app/*.iml
functions/lib/
audios.txt
transcripts.txt
update_readme.py
```

**Total tracked files that should be ignored: ~53 files**

---

## 11. Readiness for v7.21 (Phase 7 Firestore Load)

### Ready

- v7.21 design doc (`docs/kjtcom-design-v7.21.md`) is comprehensive with full TripleDB schema mapping
- v7.21 plan doc (`docs/kjtcom-plan-v7.21.md`) has step-by-step execution with dry-run safety
- Replacement CLAUDE.md text is pre-written in the plan doc
- Firestore rules allow Admin SDK writes (bypasses rules, write:false only blocks client)
- Firebase project configured (`kjtcom-c78cd`)
- Pipeline scripts are stable (zero interventions in recent iterations)
- App already handles multiple pipelines via `t_log_type` discriminator
- `pipeline_badge.dart` already has TripleDB ("TD") badge color mapping in tokens.dart

### Blocking Issues

| # | Issue | Action Required | Severity |
|---|-------|-----------------|----------|
| 1 | **CLAUDE.md is stale** | Replace with v7.21 version from plan doc (lines 340-395) | **Blocking** |
| 2 | **Previous docs not archived** | `docs/` currently has no v6.x artifacts (they appear to have been moved to archive based on git status showing deletions). The git status shows these files as deleted from `docs/` and new in `docs/archive/` but **this change is uncommitted**. | **Blocking** - needs commit |
| 3 | **TripleDB SA credential** | Plan requires `~/.config/gcloud/tripledb-sa.json` on execution machine. Verify it exists. | **Blocking** |
| 4 | **TripleDB project ID** | Plan uses placeholder `TRIPLEDB_PROJECT_ID`. Must be resolved from SA file (Section A2). | **Blocking** |
| 5 | **Machine mismatch** | CLAUDE.md + plan reference different machines (`tsP3-cos` in plan vs current machine). Verify target execution environment. | **Low** |

### Recommended Pre-Flight Checklist

1. **Commit the docs archive move** - The git status shows all v6.x docs have been moved from `docs/` to `docs/archive/` but this hasn't been committed.
2. **Replace CLAUDE.md** with the v7.21 version from the plan doc.
3. **Update GEMINI.md** or mark it as dormant (it's 6 iterations stale).
4. **Clean up tracked artifacts** - Add `.playwright-mcp/`, `*.log`, `*.kate-swp`, etc. to `.gitignore` and remove from tracking.
5. **Fix README duplicated citing section** (lines 479-497 are a duplicate).
6. **Bump pipeline.json schema versions** - calgold is v1, ricksteves is v2, both should be v3 to match schema.json.
7. **Archive `docs/tmux-v5.14.md`** to `docs/archive/`.
8. **Verify TripleDB SA credentials** and project ID on target machine.
9. **Fix changelog ordering** - v2.9 entry is at the bottom of the changelog instead of in chronological position.

### Summary

The repo is in good shape overall. The core pipeline code, Flutter app, and Firestore config are all stable and well-documented. The main pre-v7.21 work is housekeeping: committing the pending docs archive move, updating CLAUDE.md, and cleaning up tracked artifacts. The v7.21 design and plan docs are thorough and ready for execution.
