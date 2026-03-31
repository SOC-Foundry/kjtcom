# kjtcom - Unified Changelog

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

**v2.9 (RickSteves Phase 2 - Calibration)**
- Videos 31-90 processed via Gemini CLI (first Gemini execution on kjtcom)
- 494 new entities, 559 total RickSteves entities across 29 countries
- Geocoding: 99% (Nominatim + Places backfill)
- Enrichment: 99% via Google Places
- Dedup merges: 95 entities with multiple visits (implemented array merge in phase7_load.py)
- 3 interventions (LD_LIBRARY_PATH fix, transcription timeouts, load logic merge)
- Total platform: 777 entities (218 CalGold + 559 RickSteves)

