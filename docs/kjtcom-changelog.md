# kjtcom - Unified Changelog

**v9.38 (Phase 9 - Middleware Development: RAG + Telegram + Claw3D + Evaluator + Template)**
- RAG pipeline operational: nomic-embed-text + ChromaDB, 130 archive files embedded as 1,307 chunks
- scripts/embed_archive.py, query_rag.py, build_registry_v2.py created
- Telegram bot (scripts/telegram_bot.py) with 7 commands: /status /query /evaluate /gotcha /scores /ask /search
- Brave Search API wrapper (scripts/brave_search.py) created
- Claw3D Three.js prototype (docs/claw3d-prototype/index.html) - 15 nodes, animated data flow
- Agent evaluator enhanced: token tracking (prompt_tokens, eval_tokens) in agent_scores.json
- Leaderboard generator (scripts/generate_leaderboard.py) created
- docs/kjtcom-architecture.mmd living chart created with full system diagram
- Portable template (template/) with CLAUDE.md, GEMINI.md, .mcp.json, evaluator, RAG, schema, gotcha
- OpenClaw DEFERRED: tiktoken build failure on Python 3.14
- Updated: CLAUDE.md, GEMINI.md (read order), install.fish (nomic-embed, chromadb, telegram-bot, API keys)
- flutter analyze: 0 issues. flutter test: 15/15 pass. 0 production deploys.
- Kyle interventions: 2 resolved (KJTCOM_TELEGRAM_BOT_TOKEN, KJTCOM_BRAVE_SEARCH_API_KEY set + verified)

**v9.37 (Phase 9 - Dart 3.9 Upgrade + Dart MCP + Middleware Registry + Panther Scrape + MCP Fixes)**
- Biggest dep upgrade since Phase 6: 5 major version bumps (firebase_core 3->4, cloud_firestore 5->6, flutter_riverpod 2->3, google_fonts 6->8, flutter_map 7->8)
- Riverpod 3.x migration: replaced 5 StateProviders with NotifierProvider+Notifier pattern, renamed valueOrNull->value, updated 18 call sites across 8 widget files
- flutter analyze: 0 issues. flutter test: 15/15 pass. flutter build web: success (42.1s)
- MCP servers: ALL 4 operational (was 2/4 in v9.36). G52 (Firecrawl) RESOLVED. G53 (Firebase) RESOLVED.
- Dart MCP server added to .mcp.json and .gemini/settings.json (5 MCP servers total)
- Panther SIEM scrape executed via CDP: captured query editor DOM, 1,274 CSS tokens, DOM structure tree
- SECURITY: Deleted screenshots containing customer detection data per policy. DOM/CSS captures retained.
- Created docs/panther-reference/panther-scrape-notes.md mapping Panther UI elements to kjtcom equivalents
- Created scripts/build_registry.py for Qwen middleware iteration registry builder
- Created iteration_registry.json with historical data from 33 iterations (v0.5-v9.36)
- Qwen3.5-9B consulted on upgrade risks and scored v9.37 agents (Claude Code 44/50, Qwen 33/50)
- Context7 MCP used for Riverpod 3.x migration documentation
- Updated docs/install.fish with Dart MCP verification step (5c/10)
- Updated GEMINI.md read order to v9.37
- Kyle interventions: 0 (Firebase reauth and Chrome debug port pre-staged)

**v9.36 (Phase 9 - Panther SIEM Scrape + Agent Evaluator Middleware)**
- Infrastructure + reference capture iteration. Zero Flutter app changes. Zero regressions.
- Installed Playwright chromium browsers (Chrome for Testing 147.0.7727.15)
- MCP Validation: Context7 PASS, Playwright PASS, Firebase FAIL (needs reauth), Firecrawl NOT LOADED
- Created Agent Evaluator Middleware: docs/evaluator-prompt.md, agent_scores.json, scripts/run_evaluator.py
- Qwen3.5-9B retroactively scored v9.35 agents (Claude Code 32/50, Qwen 28/50, Nemotron 14/50, GLM 14/50)
- Discovered Qwen /no_think requirement for JSON output (G51)
- Consulted Qwen3.5-9B on Panther DOM selector strategy - adopted data-testid/aria-label approach
- Context7 MCP confirmed Playwright connect_over_cdp API for CDP attachment
- Playwright MCP captured kjtcom.com live site screenshot (6,181 entities verified)
- Panther CDP scrape script prepared (scripts/panther_scrape.py) - blocked on Chrome debug port
- Created docs/panther-reference/ directory with kjtcom Playwright test screenshot
- 3 new gotchas: G51 (Qwen /no_think), G52 (Firecrawl not loading), G53 (Firebase reauth)
- Kyle interventions: 1 pending (Chrome debug port restart)

**v9.35 (Phase 9 - Multi-Agent Orchestration Restoration)**
- Infrastructure-only iteration. Zero Flutter app changes. Zero regressions.
- Deployed 3 local LLMs via Ollama: Qwen3.5-9B (primary), Nemotron Mini 4B (fast), GLM-4.6V-Flash-9B (vision)
- Fixed Nemotron pull: `nemotron3-nano:4b` tag does not exist -> `nemotron-mini:4b` is the correct tag
- GLM-4V not available locally -> used community upload `haervwe/GLM-4.6V-Flash-9B`
- Removed unusable `nemotron:latest` (42 GB) from Ollama
- Created .mcp.json with 4 MCP servers: Firebase, Context7, Firecrawl, Playwright
- Created .gemini/settings.json with 2 MCP servers: Firebase, Context7
- Dart/Flutter MCP deferred to v9.36 (package @anthropic/mcp-dart does not exist on npm)
- Updated CLAUDE.md with correct model names (nemotron-mini:4b, haervwe/GLM-4.6V-Flash-9B)
- Rewrote GEMINI.md with v9.35+ orchestration mandate
- Updated docs/install.fish with Ollama model pulls (Step 5b/10)
- Qwen3.5-9B consulted for .mcp.json code review - 1 valid concern (firebase version, verified OK), 1 incorrect suggestion (package name), 1 style note
- flutter analyze: 0 issues. flutter test: 15/15 pass
- Kyle interventions: 1 (Firecrawl API key addition)

**v9.34 (Phase 9 - Gemini: Quote Cursor + Inline Autocomplete)**
- W1: Fix quote cursor in query editor (G45 resolved). Used `WidgetsBinding.instance.addPostFrameCallback` to ensure selection survives the build cycle in `schema_tab.dart`, `query_editor.dart`, and `detail_panel.dart`.
- W2: Replaced overlay-based autocomplete with inline Panther-style suggestions. Suggestions appear in a compact Column below query text with keyboard navigation (Tab/Enter/Arrows/Escape).
- W3: Fix +filter/-exclude operators. Array fields (`t_any_*`) use `contains`, scalar fields (`t_log_type`) use `==`. Both use `!=` for exclude. `t_log_type` is now filterable from the detail panel.
- 5 modified files, 1 production deploy. flutter analyze: 0 issues. flutter test: 15/15 pass
- Security scan clean: no leaked credentials
- Gemini CLI interventions: 0

**v9.33 (Phase 9 - Parser Regression + Quotes + Operators)**
- W1: Parser regression fix deployed - quoted regex confirmed first, unquoted fallback. 3 new regression tests (15 total)
- W2: Quotes restored in schema builder (`| where field contains ""`), cursor placed between quotes via programmaticUpdateProvider flag (G45 attempt #6)
- W3: +filter uses == operator, -exclude uses != operator. Both use programmaticUpdateProvider flag
- W4: Feedback message already correct, no change needed
- W5: DEFERRED - Riverpod 3 removes StateProvider, requires >50 lines migration across 13 files
- 5 files modified, 2 production deploys. flutter analyze: 0 issues. flutter test: 15/15 pass
- Security scan clean: no leaked credentials
- Claude Code interventions: 0

**v9.32 (Phase 9 - Shows Fix + Operators + Detail Sort + Quote Rethink)**
- W1: TripleDB t_any_shows lowercased (1,100 entities) - G37/G49 resolved
- W6: Comprehensive lowercase ALL t_any_* data (1,286/6,181 entities updated) - G36 permanently resolved
- W4: Schema builder appends without quotes, parser accepts unquoted values - G45 eliminated
- W2: != operator added (server-side isNotEqualTo for scalar, client-side for array)
- W3: Detail panel fields sorted alphabetically by key
- W5: Autocomplete detection updated for no-quotes approach (unquoted + empty value modes)
- 2 new pipeline scripts, 8 files modified, 3 new tests (12/12 pass)
- 1 production deploy. flutter analyze: 0 issues
- Security scan clean: no leaked credentials
- Claude Code interventions: 0

**v9.31 (Phase 9 - Persistent Bug Fix + Playwright Verification)**
- DIAGNOSTIC-FIRST approach: read every file, grep all patterns, add debugPrint before fixing
- W1: 1000-result limit CONFIRMED RESOLVED via Playwright screenshot (6,181 entities shown, no limit in code)
- W2: Quote cursor hardened with addPostFrameCallback to survive frame-timing edge cases (G45)
- W3: Autocomplete value-mode fix: re-trigger suggestions when valueIndexProvider FutureProvider loads
- W4: TripleDB verified via Python Firestore query (1,100 docs, correct schema, correct query parsing)
- W5: Clear button added to query editor chrome bar (clears query, results, and selected entity)
- Playwright verification: screenshots captured but CanvasKit blocks DOM interaction (G47 confirmed)
- 3 modified files, 3 Playwright screenshots. 1 production deploy
- flutter analyze: 0 issues. flutter test: 9/9 pass
- Security scan clean: no leaked credentials
- Claude Code interventions: 0

**v9.30 (Phase 9 - App Optimization: Autocomplete + Quote Fix + Limit Verification)**
- Query field autocomplete: type `t_any_c` to see matching fields, Tab to accept
- Query value autocomplete: type inside quotes to see matching values from precomputed index (21 fields, 6,878 values)
- Fixed quote cursor placement (3rd attempt, G45 resolved): shared TextEditingController via provider, cursor lands between quotes
- Confirmed Firestore limit removal from v9.29 via grep + Python Firestore verification (G46 resolved)
- Trident labels confirmed consistent ("Cost", "Delivery", "Performance") at all viewports
- Updated stats footer: 30 iterations, 29 zero-intervention
- New: generate_value_index.py, query_autocomplete.dart, value_index.json
- 7 modified files, 3 new files. 1 production deploy
- flutter analyze: 0 issues. flutter test: 9/9 pass
- Security scan clean: no leaked credentials
- Claude Code interventions: 0

**v9.29 (Phase 9 - App Optimization: UX Polish - Trident, Limits, Schema, Quotes)**
- Removed Firestore .limit(1000): all matching entities returned, pagination handles display (20/50/100)
- Simplified QueryResult class: removed isTruncated, removed truncation indicator widget
- Fixed schema builder quote placement (G45): clause appended without closing quote, user types value naturally
- Updated query_clause.dart parser to accept unclosed quotes at end of line
- Shortened trident prong labels for mobile: "Cost", "Delivery", "Performance"
- Schema field audit: all 22 fields confirmed present (t_any_cuisines already added in v9.28)
- Updated stats footer: 29 iterations, 28 zero-intervention
- 5 modified files. 1 production deploy
- flutter analyze: 0 issues. flutter test: 9/9 pass
- Security scan clean: no leaked credentials
- Claude Code interventions: 0

**v9.28 (Phase 9 - App Optimization: Gotcha Tab + Schema Builder + JSON Copy)**
- New Gotcha tab: 25 gotchas (G1-G44) displayed as styled cards with status badges (ACTIVE/RESOLVED/DOCUMENTED)
- Gotcha filter toggle: All | Active | Resolved
- New Schema tab: 22 Thompson Indicator Fields with type badges, descriptions, examples
- Schema query builder: "+ Add to query" button appends clause to query editor and switches to Results tab
- t_log_type uses == operator; all t_any_* use contains; coordinates and geohashes are view-only
- Copy JSON button on entity detail panel: copies full entity rawData as indented JSON with SnackBar confirmation
- Tab bar expanded to 6 tabs: Results | Map | Globe | IAO | Gotcha | Schema
- Post-flight deploy testing established as MANDATORY standard for all future iterations
- 2 new files (gotcha_tab.dart, schema_tab.dart), 4 modified files
- 1 production deploy. flutter analyze: 0 issues. flutter test: 9/9 pass
- Security scan clean: no leaked credentials
- Claude Code interventions: 0

**v9.27 (Phase 9 - App Optimization: Visual Refresh + Tab Wiring)**
- Gothic/cyberpunk visual refresh: Cinzel font for headers, gothic green borders (30% opacity) on card containers, hover glow effects
- All 4 tabs now functional: Results | Map | Globe | IAO
- Map tab: flutter_map + OpenStreetMap with pipeline-colored entity markers, marker tap opens detail panel
- Globe tab: stats dashboard with continent cards, country grid, pipeline distribution bar. Click filters to Results tab
- IAO Pillar tab: trident SVG graphic + 10 pillar cards (VERBATIM text) + project stats footer (6,181 / 3 / 27 / 26)
- Search results pagination: dropdown (20/50/100, default 20) + page navigation (Previous | Page N of M | Next)
- New dependencies: flutter_map ^7.0.2, latlong2 ^0.9.1
- 5 new files, 7 modified files. 2 production deploys
- flutter analyze: 0 issues. flutter test: 9/9 pass
- Security scan clean: no leaked credentials
- Claude Code interventions: 0

**v8.26 (Phase 8 - Gotcha Registry + Query UX Fix)**
- Removed rotating example queries from query editor: Timer.periodic (6s cycle), 5-query list, initial query population all removed
- Query editor now starts empty - no more overwriting user input mid-typing (G42 resolved)
- Added static help text below editor showing example query syntax (Geist Mono, secondary color, not injected into input)
- Established gotcha registry standard: full G1-G42 registry with status in every design doc and report going forward
- 1 production deploy. flutter analyze: 0 issues. flutter test: 9/9 pass
- Security scan clean: no leaked credentials
- Phase 8 (Enrichment Hardening) COMPLETE across v8.22-v8.26
- Claude Code interventions: 0

**v8.25 (Phase 8 - Filter Fix + README Overhaul)**
- Fixed +filter/-exclude duplicate bug in query_provider.dart: dedup check prevents identical clauses, guard flag prevents rebuild-triggered re-entry
- Root cause: appendClause modified queryProvider state, triggering widget rebuild, which re-fired the handler (1-4 duplicate lines per click)
- Fix: (1) check if clause already exists in query text before appending, (2) _isAppending guard flag with Future.microtask reset
- Comprehensive README overhaul: complete rewrite with new Live App section, Query System section, updated project status
- Added app query flow architecture diagram (Query Editor -> QueryClause Parser -> Firestore Provider -> Results)
- Updated project status: Phase 8 DONE v8.22-v8.25
- Added tsP3-cos to hardware section
- Truncated README changelog to last 5 iterations with link to full changelog
- Updated Future Directions with v8.22 assessment conclusions (HyperAgents deferred, Algolia deferred)
- 1 production deploy (filter fix). Final deploy after README overhaul.
- flutter analyze: 0 issues. flutter test: 9/9 pass
- Security scan clean: no leaked credentials
- Phase 8 (Enrichment Hardening) COMPLETE - all workstreams delivered across v8.22-v8.25
- Claude Code interventions: 0

**v8.24 (Phase 8 - UI Fixes + Country Codes)**
- Fixed detail panel: clicking a result row now opens entity detail with t_any_* field cards at all viewport widths
- Detail panel on mobile/tablet: overlay with scrim backdrop, animated width transition on desktop
- Removed "staging" badge from app header - app queries production since v7.21
- Fixed cursor alignment in query editor: removed custom cursor (duplicate cursors), removed per-line padding drift
- Backfilled t_any_country_codes (ISO 3166-1 alpha-2) on 6,161/6,181 entities (99.7% coverage)
- Added t_any_country_codes to knownFields and LocationEntity model
- 2 production deploys: mid-iteration (P0 fixes) + final (all fixes)
- flutter analyze: 0 issues. flutter test: 9/9 pass (3 new country code tests)
- Security scan clean: no leaked credentials
- Phase 8 (Enrichment Hardening) COMPLETE
- Claude Code interventions: 0

**v8.23 (Phase 8 - NoSQL Query Remediation)**
- Resolved all 12 query defects from v8.22 assessment (3 P0, 5 P1, 2 P2, 1 P3 deferred)
- Case sensitivity fix: all query values lowercased before Firestore dispatch (D1, D3, D4)
- CalGold data fix: 899/899 t_any_shows values lowercased (D2)
- Updated 5 example queries - all validated against production, all return >0 results
- Added result count badge in tech green above results table (D8)
- Added truncation indicator when results hit limit (D9)
- Implemented `contains-any` operator -> Firestore `arrayContainsAny` (D7)
- Increased result limit from 200 to 1000 - no more silent truncation (D6)
- Added field name validation against 21 known t_any_* fields (D10)
- Added parse error feedback for malformed queries (D11)
- Added informational note for multi-array-contains queries about client-side filtering (D5)
- 2 production deploys: mid-iteration (P0 fix) + final (all fixes)
- Regression: 11/12 PASS (D12 deferred to Phase 9)
- flutter analyze: 0 issues. flutter test: 6/6 pass
- Security scan clean: no leaked credentials
- Claude Code interventions: 0

**v8.22 (Phase 8 - Enrichment Hardening + Query Assessment)**
- Backfilled 323 non-v3 entities (121 CalGold + 202 RickSteves) to schema v3: 100% coverage (6,181/6,181)
- Enriched 391/405 TripleDB entities via Google Places API: enrichment rate 63% -> 98%
- Backfilled 88 TripleDB coordinates (91% -> 99%) and 48 cities (89% -> 93%)
- Comprehensive NoSQL query assessment: 12 defects identified across 6 categories
- Critical finding: 2 of 5 rotating example queries return 0 results due to case-sensitive arrayContains (D1)
- Critical finding: 200-result limit silently truncates compound queries (D6), hiding 50-69% of results
- `contains-any` operator: Firestore supports natively but Flutter parser does not implement it (D7)
- No result counts displayed in app UI (D8)
- MCP registry: 4 Firebase MCP servers identified; gannonh/firebase-mcp recommended for v8.23
- HyperAgents assessment: premature for v8.23 query fixes, defer to Phase 10 for extraction optimization
- Algolia/Typesense assessment: defer to Phase 9 - Firestore-native fixes sufficient for 6,181 entities
- v8.23 remediation spec produced: 10 work items (3 P0, 5 P1, 2 P2) with implementation order
- Security scan clean: no leaked credentials
- Claude Code interventions: 0

**v7.21 (Phase 7 - Firestore Load + TripleDB Migration)**
- Migrated 1,102 TripleDB restaurants from external Firestore project (tripledb-e0f77) to kjtcom production
- Cross-project Admin SDK with two SA credentials (TachTech-Engineering + socfoundry.com)
- Full Thompson Indicator Fields v3 schema mapping with 14 Google Places enrichment fields carried forward (G31)
- Deterministic t_row_id for dedup safety: 1,102 written, 1,100 unique in production (G33)
- Copied 5,081 CalGold + RickSteves entities from staging to production (no transformation)
- Production totals: 6,181 entities (899 CalGold + 4,182 RickSteves + 1,100 TripleDB)
- TripleDB field rates: cuisines 100%, dishes 100%, actors 100%, coordinates 91%, shows 100%
- Schema v3: 94% overall (323 pre-existing v1/v2 entities from earlier phases)
- Security scan clean: no leaked credentials
- Claude Code interventions: 0

**v6.20 (Phase 6e - Visual Polish)**
- Closed 5 visual gaps between HTML mockup and deployed Flutter app
- Added globe_hero.jpg background at 15% opacity (replaces gradient placeholder)
- Added rotating example queries (5 queries, 6s cycle) showcasing all 5 syntax highlight colors
- Added blinking green cursor underscore on empty last line (530ms interval)
- Added animated count-up for entity and country counts (600ms easeOut)
- Fixed Riverpod ref.listen timing race: provider initial value now matches first example query
- Pipeline-colored dots confirmed working (implemented in v6.17, no change needed)
- flutter analyze: 0 issues. flutter test: 3/3 pass. Console errors: 0
- Claude Code interventions: 0

**v6.19 (Phase 6e - Deploy)**
- Deployed Flutter Web app to Firebase Hosting at kylejeromethompson.com
- Build: flutter build web --release (16.9s, 39 files, CanvasKit renderer)
- Firebase deploy: 39 files to kjtcom-c78cd hosting
- Added Google Analytics (GA4) via gtag.js (Measurement ID: G-JMVEJLW9PC)
- Chrome smoke test: full SIEM UI render, 0 console errors
- Firefox smoke test: page loads (correct title, 0 errors); canvas blank in headless (known CanvasKit limitation)
- Security scan: Firebase Web API key only (public client key, expected)
- Phase 6 (Flutter App) complete across all 5 sub-phases (6a-6e)
- Claude Code interventions: 0

**v6.18 (Phase 6d - QA)**
- Executed multi-viewport visual audit (1440x900, 768x1024, 375x812) using Playwright MCP
- Validated responsive layout shifts: query editor full-width on mobile, table columns hidden on tablet/mobile
- Completed Lighthouse compliance audit: Accessibility 0.92 (PASS >= 0.90), SEO 1.0 (PASS >= 0.90)
- Confirmed design contract adherence: dark SIEM aesthetic (#0D1117), Geist font stack, green terminal accents
- Verified SIEM-style information density and "Investigate"/"staging" status tone
- Benchmarked initialization performance: 7.7s - 14.1s FCP (standard Flutter bootstrap overhead)
- Produced Phase 6d mandatory artifacts: build, report, and screenshots
- Gemini CLI interventions: 0

**v6.17 (Phase 6c - Implementation)**
- Built Flutter Web app from Phase 6b design contract: 12 Dart files, 8 widget components
- Geist Sans + Geist Mono fonts bundled from npm (geist@1.7.0, SIL OFL)
- Syntax-highlighted query editor with 5-color tokenizer (field/operator/value/keyword/collection)
- Results table: 5-column grid with pipeline-colored dots, responsive column hiding
- Entity detail panel: t_any_* field cards with +filter/-exclude buttons -> query append
- Riverpod state: queryProvider, resultsProvider (Firestore stream), selectedEntityProvider
- Firestore query: server-side arrayContains + client-side filtering for multi-clause queries
- flutter analyze: 0 issues. flutter build web: success. flutter test: 3/3 pass
- Firebase web app registered (flutterfire configure). App ID: 1:703812044891:web:84b2df9330066bfbe6177e
- Claude Code interventions: 1 (Firebase auth - user resolved)

**v6.16 (Phase 6b - Design Contract)**
- Synthesized Phase 6a scrape archive (8 sites + Panther SIEM) into three-file design contract
- design-tokens.json: 100+ tokens (colors, typography, spacing, elevation, breakpoints, layout, animation)
- design-brief.md: aesthetic direction, color rules, imagery strategy, tone, responsive behavior
- component-patterns.md: 10 widget blueprints with token mappings, interaction patterns, accessibility
- Locked visual identity: dark SIEM aesthetic (#0D1117 base), Geist Sans/Mono, pipeline-colored dots
- Defined core interaction patterns: row-select -> detail panel, +filter/-exclude -> query append
- Zero Flutter code changes. Specification-only phase.
- Claude Code interventions: 0

**v6.15 (Phase 6a - Discovery)**
- Scraped 8 public competitor sites via Playwright MCP across Pipeline, Investigation, and Concierge categories.
- Captured desktop and mobile screenshots plus accessibility snapshots for structural analysis.
- Selected Geist Sans/Mono (Scanner.dev) as the primary typographic reference.
- Validated pipeline aesthetics (Monad, Cribl) and editorial polish (Black Tomato) for kjtcom.

**v5.14 (CalGold Phase 5 - Production Run)**
- Full production run: 390/431 videos processed (41 unavailable on YouTube)
- 829 entities extracted, 899 unique CalGold entities in Firestore staging
- tmux graduated timeout passes: 600s (109 transcripts, CUDA OOM) + 1200s (281 remaining, clean)
- Geocoding: 31% Nominatim -> 95% after Google Places coordinate backfill (538 backfilled)
- Enrichment: 95% via Google Places (795/829)
- Schema v3: 100%. Actors 100%, continents 100%, eras 76%
- t_any_shows backfill: 899/899 CalGold entities updated with ["California's Gold"]
- tmux interventions: 1 (CUDA OOM, checkpoint recovery). Claude Code interventions: 0
- Total platform: 1,934 entities (899 CalGold + 1,035 RickSteves)

**v4.13 (RickSteves Phase 4 - Validation + Schema v3)**
- Schema v3 migration: 7 new t_any_* fields (actors, roles, shows, cuisines, dishes, eras, continents)
- Videos 121-150 acquired/transcribed (30 new). ALL 150 re-extracted with v3 prompt
- 150 total videos processed, 991 documents loaded, 1,035 unique RickSteves entities in staging
- Schema v3 validation (744 v3 entities): actors 100%, shows 100%, continents 99%, eras 73%, counties 38%
- CalGold t_any_shows backfill: 412/412 entities updated with ["California's Gold"]
- Country distribution expanded to 33 (up from 30)
- Geocoding and enrichment: >95% via Google Places
- Gemini CLI interventions: 0. Claude Code interventions: 1 (checkpoint path mismatch in plan)
- Total platform: 1,447 entities (412 CalGold + 1,035 RickSteves) across 33 countries
- Both pipelines validated for Phase 5 (Production Run)

**v4.12 (CalGold Phase 4 - Validation + Schema v3)**
- Schema v3 migration: 6 new t_any_* fields (actors, roles, cuisines, dishes, eras, continents)
- Videos 91-120 acquired/transcribed (30 new). ALL 120 re-extracted with v3 prompt
- 120 total videos processed, 296 entities, 300 unique in Firestore staging
- Schema v3 validation: t_any_actors 100%, t_any_continents 100%, t_any_counties 84.1%, t_any_eras 82.4%
- Script enhancements: continent lookup in phase4_normalize.py, county parsing in phase5_geocode.py
- Geocoding: 97.6% (201 coords backfilled from Google Places)
- Enrichment: 97.6% via Google Places (289/296)
- Gemini CLI interventions: 0. Claude Code interventions: 1 (checkpoint reset for full re-enrichment)
- Total platform: 969 entities (300 CalGold + 669 RickSteves) across 30 countries
- Phase 5 (Production Run) recommended

**v3.11 (RickSteves Phase 3 - Stress Test)**
- Videos 91-120 processed via split-agent model: Gemini CLI (phases 1-5) + Claude Code (phases 6-7)
- 120 total videos processed, 869 raw entities, 669 unique in Firestore staging
- 42 multi-visit entity merges in this batch (200 cumulative across all phases)
- Geocoding: 99.3% (Nominatim + Google Places coordinate backfill)
- Enrichment: 99.3% via Google Places (863/869)
- New countries: Egypt, Ethiopia, Vatican City (30 total, up from 29)
- Zero interventions for both agents (Gemini: 0, Claude: 0)
- Third consecutive zero-intervention split-agent execution
- Total platform: 887 entities (218 CalGold + 669 RickSteves) across 30 countries

**v3.10 (CalGold Phase 3 - Stress Test)**
- Videos 61-90 processed via split-agent model: Gemini CLI (phases 1-5) + Claude Code (phases 6-7)
- 90 total videos processed, 226 total entities, 218 unique in Firestore staging
- 5 multi-visit entity merges across Phase 1-3 batches
- Geocoding: 36% Nominatim -> 98% after Google Places coordinate backfill (140 backfilled)
- Enrichment: 98% via Google Places (222/226)
- 4 misses: niche infrastructure (debris basins, historic water channels, private rail car)
- G2 (CUDA LD_LIBRARY_PATH) permanently resolved - zero failures across full iteration
- Zero interventions for both agents (Gemini: 0, Claude: 0)
- First successful split-agent execution with handoff checkpoint protocol
- Total platform: 777 entities (218 CalGold + 559 RickSteves) across 29 countries

**v2.9 (RickSteves Phase 2 - Calibration)**
- Videos 31-90 processed via Gemini CLI (first Gemini execution on kjtcom)
- 494 new entities, 559 total RickSteves entities across 29 countries
- Geocoding: 99% (Nominatim + Places backfill)
- Enrichment: 99% via Google Places
- Dedup merges: 95 entities with multiple visits (implemented array merge in phase7_load.py)
- 3 interventions (LD_LIBRARY_PATH fix, transcription timeouts, load logic merge)
- Total platform: 777 entities (218 CalGold + 559 RickSteves)

**v2.8 (CalGold Phase 2 - Calibration)**
- Videos 31-60 processed: 60/60/60 (acquired/transcribed/extracted)
- 162 new entities, 218 total CalGold entities after dedup
- Phase 1 re-enriched: coordinate backfill pushed geocoding from 43% to 97%
- Enrichment: 97% via Google Places
- Dedup merges: 3 entities with multiple visits
- Schema upgraded to v2 with t_any_countries: ["us"]
- 2 interventions (G2 CUDA path, schema v1 -> v2)
- Total platform: 418 entities (218 CalGold + 200 RickSteves) across 24 countries

**v1.7 (RickSteves Phase 1 - Discovery)**
- Pipeline 2 live: Rick Steves' Europe, 30 videos, 200 unique destinations across 23 countries
- Thompson Schema evolved to v2: added t_any_countries, t_any_regions
- Geocoding: 98% (68% Nominatim + 66 backfilled from Google Places)
- Enrichment: 98% via Google Places (197/200)
- Cross-pipeline queries validated
- CalGold entities backfilled to schema v2 (56/56)
- Migrated phase3_extract.py from google.generativeai to google.genai
- 256 total entities in staging (56 CalGold + 200 RickSteves)
- 1 intervention (LD_LIBRARY_PATH for CUDA)

**v1.6 (CalGold Phase 1 - Discovery)**
- 30-video discovery batch: 30/30 acquired, 30/30 transcribed, 30/30 extracted
- 57 unique California locations normalized via Thompson Schema
- Geocoding: 43% via Nominatim (niche/historic locations missed)
- Enrichment: 100% match rate via Google Places API (New)
- 56 documents loaded to staging Firestore
- 3 interventions resolved (CUDA path, pip install, Places API key)

**v0.5 (Phase 0 - Scaffold)**
- Repo, Firebase, multi-database, Thompson Schema, pipeline config
- 431 CalGold playlist URLs validated
- Cloud Functions search endpoint deployed
