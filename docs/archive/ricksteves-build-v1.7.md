# RickSteves - Build Log v1.7 (Phase 1 - Discovery)

**Date:** March 29, 2026
**Executor:** Claude Code (YOLO mode, Opus)
**Machine:** NZXTcos (Intel i9-13900K, RTX 2080 SUPER, 64 GB DDR4, CachyOS)

---

## Pre-Flight

- API keys: GEMINI_API_KEY SET, GOOGLE_PLACES_API_KEY SET, GOOGLE_APPLICATION_CREDENTIALS SET
- Firebase: kjtcom-c78cd active
- Python: 3.14.3, yt-dlp: 2026.03.17, faster-whisper: OK
- CUDA: NVIDIA GeForce RTX 2080 SUPER visible
- LD_LIBRARY_PATH: required manual set to /usr/local/lib/ollama/mlx_cuda_v13:/usr/local/lib/ollama/cuda_v12
- Disk: 737G free

---

## Step 0: Setup + Migrations

- Created pipeline/config/ricksteves/ with pipeline.json, schema.json, extraction_prompt.md
- Generated playlist_urls.txt: **1,865 filtered videos** (exact match to design spec)
- Created pipeline/data/ricksteves/{audio,transcripts,extracted,normalized,geocoded,enriched}
- Migrated phase3_extract.py from google.generativeai to google.genai (google-genai 1.69.0)
- Verified google.genai SDK with test call
- Updated phase5_geocode.py: added country field to Nominatim query for international locations
- Updated phase6_enrich.py: added country to Google Places query, added places.location to field mask, added coordinate backfill from Google Places
- Updated phase7_load.py: parameterized pipeline registry (was hardcoded to CalGold)
- Added 4 new composite indexes to firestore.indexes.json (t_any_countries, t_any_regions)
- Deployed indexes via firebase deploy --only firestore:indexes
- Backfilled 56 CalGold entities to schema v2: t_any_countries: ["us"], t_schema_version: 2

---

## Step 1: Acquire (phase1_acquire.py)

- **30/30 videos downloaded** (100%)
- Mix of Travel Bites, full episodes, and compilations
- No failures or retries needed

---

## Step 2: Transcribe (phase2_transcribe.py)

- **30/30 transcribed** (100%)
- Model: large-v3, device: cuda, compute_type: float16
- Required LD_LIBRARY_PATH for libcudnn.so.9 and libcublas.so.12
- Duration: ~25 minutes total
- Longer episodes (ugFmDGDzExY: 2273 segments) took several minutes each

---

## Step 3: Extract (phase3_extract.py)

- **30/30 extracted** (100%)
- google.genai SDK migration successful
- Model: gemini-2.5-flash
- **223 total raw entities** from 30 videos (7.4 entities/video average)
- Highest yield: 70GXfWe3CyA (37 entities), 7glld8yO3Xo (30 entities), ugFmDGDzExY (24 entities)
- 5 videos returned 0 entities (non-location content)

---

## Step 4: Normalize (phase4_normalize.py)

- **223 entities normalized** to Thompson Schema v2
- All 223 entities have t_any_countries populated (100%)
- 102/223 have t_any_regions populated (46%)
- 199/223 have t_any_cities populated (89%)
- All 223 at t_schema_version: 2
- **23 unique countries**: austria, belgium, czech republic, denmark, england, finland, france, germany, greece, iceland, italy, netherlands, norway, poland, portugal, scotland, spain, switzerland, turkey, united kingdom, united states, vatican city (+ 1 empty string)

---

## Step 5: Geocode (phase5_geocode.py)

- **153/223 geocoded via Nominatim** (68%)
- International country field in query improved geocoding significantly vs CalGold's 43%
- Rate limit: 1 req/sec
- Notable misses: some niche museums, chapels within churches, artworks-as-locations

---

## Step 6: Enrich (phase6_enrich.py)

- Initial run failed: bash session did not inherit fish config env vars (GOOGLE_PLACES_API_KEY)
- Re-run via `fish -c` resolved the issue
- **197/200 enriched** (98%) via Google Places
- **66 coordinate backfills** from Google Places for entities Nominatim missed
- **Final geocoding rate: 98%** (153 Nominatim + 66 Places backfill = 197/200 with coordinates)
- 3 misses: The Garden of Earthly Delights, Doni Tondo, Bandini Pieta (artworks, not geocodable places)

---

## Step 7: Load (phase7_load.py)

- **223 documents loaded to staging** Firestore
- Pipeline registry updated with RickSteves metadata (parameterized, no longer hardcoded)
- 200 unique entities in Firestore (23 duplicates from cross-video appearances)
- Cross-pipeline validation:
  - Total entities in staging: 256 (56 CalGold + 200 RickSteves)
  - Keyword "church": 18 results from BOTH pipelines
  - Country "us": 56 results (CalGold)
  - Country "italy": 38 results (RickSteves)
  - Country "france": 25 results (RickSteves)
  - CalGold schema v2: 56/56 (100%)
  - RickSteves schema v2: 200/200 (100%)

---

## Step 8: Post-Flight

- Security scan: zero API keys in repo files (verified)
- All 7 phase scripts completed
- Checkpoint files exist for all phases
- CLAUDE.md has security section

---

## Interventions

1. **LD_LIBRARY_PATH** - Had to manually set to include CUDA libraries for transcription (Gotcha G2 recurrence). Consider adding to fish config.

---

## Timing

| Phase | Duration |
|-------|----------|
| Step 0 (setup + migrations) | ~10 min |
| Step 1 (acquire 30 videos) | ~8 min |
| Step 2 (transcribe 30 videos) | ~25 min |
| Step 3 (extract 30 videos) | ~5 min |
| Step 4 (normalize) | < 1 min |
| Step 5 (geocode) | ~5 min |
| Step 6 (enrich) | ~5 min |
| Step 7 (load + validation) | ~3 min |
| Step 8-9 (post-flight + artifacts) | ~5 min |
| **Total** | **~60 min** |
