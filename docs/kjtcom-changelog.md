# kjtcom - Unified Changelog

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

