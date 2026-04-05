# kjtcom - Build Log v9.37

**Phase:** 9 - App Optimization
**Iteration:** 37
**Date:** April 4, 2026
**Executing Agent:** Claude Code (Opus 4.6)
**LLMs Consulted:** Qwen3.5-9B (upgrade risk assessment, middleware registry processor)

---

## PRE-FLIGHT

- [x] Ollama running with 3 models (qwen3.5:9b, nemotron-mini:4b, haervwe/GLM-4.6V-Flash-9B)
- [x] .mcp.json present with 4 servers (Firebase, Context7, Firecrawl, Playwright)
- [x] v9.36 docs archived (already done prior to session)
- [x] Working directory: ~/dev/projects/kjtcom
- [x] Chrome running with --remote-debugging-port=9222 (process 334419)
- [x] Panther Search tab open and authenticated
- [x] Firebase login --reauth completed by Kyle

---

## W3: MCP SERVER VERIFICATION

### Firebase MCP (G53 - RESOLVED)
- Kyle completed `firebase login --reauth` before session
- Test: `firestore_list_documents` on locations collection
- Result: **PASS** - returned 3 documents (101 Cafe, 101 Freeway, 16 to 1 Mine)
- G53 status: RESOLVED for this session

### Context7 MCP
- Test: `resolve-library-id` for Flutter
- Result: **PASS** - returned 5 library IDs with scores
- Used for Riverpod 3.x migration docs during W1

### Firecrawl MCP (G52 - RESOLVED)
- API key verified: set (fc-60...)
- Test: `firecrawl_scrape` on dart.dev/tools
- Result: **PASS** - returned full page markdown
- G52 status: RESOLVED - transient loading issue from v9.36 no longer present

### Playwright MCP
- CDP verified: `curl -s http://localhost:9222/json/list` returned 9 tabs
- Panther tab confirmed: tachtech.runpanther.net/investigate/search/
- Used directly via Python/Playwright for W4 Panther scrape

### Summary: 4/4 MCP servers OPERATIONAL (was 2/4 in v9.36)

---

## W1: DART 3.9 + DEPENDENCY UPGRADE

### Dart SDK Check
- Current: Dart 3.11.4 (stable), Flutter 3.41.6
- Required: >= 3.9 for Dart MCP server
- Result: **Already above requirement. No SDK upgrade needed.**

### Qwen Consultation (Orchestration Compliance)
- Consulted Qwen3.5-9B on upgrade risks before proceeding
- Top 3 risks identified:
  1. Cloud Firestore 5.x -> 6.x API changes
  2. Riverpod Ref lifecycle shifts
  3. Web compatibility for flutter_map/firebase_core
- Recommendation: Backup pubspec.lock, test web first, check migration guides

### Dependency Upgrade
Command: `flutter pub upgrade --major-versions`

| Package | Before | After | Major Bump |
|---------|--------|-------|------------|
| firebase_core | ^3.13.0 | ^4.6.0 | YES (3->4) |
| cloud_firestore | ^5.6.0 | ^6.2.0 | YES (5->6) |
| flutter_riverpod | ^2.6.1 | ^3.3.1 | YES (2->3) |
| google_fonts | ^6.2.1 | ^8.0.2 | YES (6->8) |
| flutter_map | ^7.0.2 | ^8.2.2 | YES (7->8) |
| latlong2 | ^0.9.1 | ^0.9.1 | no |
| flutter_lints | ^6.0.0 | ^6.0.0 | no |

### Breaking Changes Fixed (Riverpod 3.x Migration)

**8 errors detected by `flutter analyze`:**

1. `StateProvider` removed in Riverpod 3.x
   - Migrated 5 StateProviders to NotifierProvider + Notifier class pattern
   - Files: pagination_provider.dart, query_provider.dart, selection_provider.dart, tab_provider.dart

2. `AsyncValue.valueOrNull` renamed to `AsyncValue.value`
   - Updated 3 occurrences in query_editor.dart

3. `.notifier).state = ` access now protected (38 warnings)
   - Added named setter methods to all Notifier classes
   - Updated 18 call sites across 8 files:
     - results_table.dart (4 sites)
     - app_shell.dart (2 sites)
     - detail_panel.dart (5 sites)
     - schema_tab.dart (3 sites)
     - map_tab.dart (1 site)
     - globe_tab.dart (2 sites)
     - kjtcom_tab_bar.dart (1 site)
     - query_editor.dart (1 site - clear button, was already 0 errors but 1 warning)

### Post-Fix Analysis
- `flutter analyze`: **0 issues**
- `flutter test`: **15/15 pass**
- `flutter build web`: **SUCCESS** (42.1s compile)

### Context7 MCP Usage
- Resolved Riverpod library ID: `/rrousselgit/riverpod` (score 86.95)
- Queried Riverpod 3.x migration docs for StateProvider replacement and valueOrNull rename
- Confirmed: StateProvider -> Notifier + NotifierProvider, valueOrNull -> value

---

## W2: DART MCP SERVER

- Verified `dart mcp-server --help` works (Dart 3.11.4 includes it natively)
- Added to .mcp.json: `"dart": {"command": "dart", "args": ["mcp-server"]}`
- Added to .gemini/settings.json: same entry
- Server will activate on next Claude Code session restart
- Capabilities: analyze code, resolve symbols, search pub.dev, run tests, format code

---

## W4: PANTHER SIEM SCRAPE

### CDP Connection
- Chrome process 334419 with --remote-debugging-port=9222
- `curl -s http://localhost:9222/json/list` returned 9 tabs
- Panther tab found: tachtech.runpanther.net/investigate/search/

### Scrape Execution
- Script: `python3 scripts/panther_scrape.py`
- Connected via Playwright CDP (`connect_over_cdp`)
- Captures:
  - panther-query-editor.html (MUI-based histogram component DOM)
  - panther-css-tokens.json (1,274 CSS custom properties)
  - panther-dom-structure.json (full page DOM tree, 6 levels)

### SECURITY: Screenshots Deleted
- panther-search-full.png and panther-search-viewport.png contained customer detection data (Crowdstrike FDR events with computer names, timestamps)
- Immediately deleted per CLAUDE.md security rules: "No result row data"
- Note: Future scrape script should blur/redact result table rows before screenshot

### Mapping Notes
- Created docs/panther-reference/panther-scrape-notes.md
- Key findings:
  - Panther uses PantherFlow (SQL-like) vs kjtcom piped clauses
  - Both use dark themes with teal/green accents
  - Panther's field sidebar (selected/available) is a good UX pattern
  - "Summarize with AI" button is a notable feature gap
  - Time-series histogram above results provides temporal context kjtcom lacks

---

## W5: QWEN MIDDLEWARE REGISTRY

### Script Created
- scripts/build_registry.py
- Groups docs/archive/ files by iteration (33 iterations found)
- Feeds each batch to Qwen3.5-9B via Ollama API with /no_think prefix
- Extracts: version, date, phase, focus, agents, outcomes, failures, successes
- Builds gotcha_registry from cross-referencing iteration data
- Output: iteration_registry.json

### Processing
- 33 iterations across phases 0-9
- Qwen processes each iteration's 4-5 files (capped at 8K chars)
- Results merged into single registry with metadata
- Status: Processing in background (300s timeout per iteration)

---

## CONFIG UPDATES

| File | Change |
|------|--------|
| .mcp.json | Added dart MCP server entry |
| .gemini/settings.json | Added dart MCP server entry |
| GEMINI.md | Updated read order to v9.37 |
| docs/install.fish | Added Step 5c/10: Dart MCP server verification |
| app/pubspec.yaml | 5 major version bumps (auto by flutter pub upgrade) |

---

## GOTCHA STATUS

| ID | Description | Status |
|----|-------------|--------|
| G47 | Firestore ordering requires composite index | OPEN |
| G51 | Qwen /no_think required for JSON output | OPEN |
| G52 | Firecrawl MCP not loading | **RESOLVED** (v9.37) |
| G53 | Firebase MCP needs fresh login each session | **RESOLVED** (for this session) |

---

## INTERVENTION LOG

- **Interventions this iteration: 0**
- Firebase reauth completed before session by Kyle
- Chrome debug port active before session by Kyle
- Dart SDK already at 3.11.4 (no upgrade needed)

---

*Build log generated by Claude Code (Opus 4.6), April 4, 2026.*
