# CalGold - Build v4.12 (Phase 4 - Validation + Schema v3)

**Pipeline:** calgold
**Phase:** 4 (Validation)
**Iteration:** 12 (global counter)
**Date:** 2026-03-30

---

## Section A: Gemini CLI Execution (Schema Prep + Phases 1-5)

**Agent:** Gemini CLI (`gemini --yolo`)
**Interventions:** 0

### Step 0: Pre-Flight
- All checks passed: API keys SET, CUDA visible, LD_LIBRARY_PATH set
- Previous docs archived to docs/archive/
- 90 audio, 90 transcripts, 90 extracted confirmed from v3.10

### Step 0.5: Schema v3 Config Changes
- Updated `pipeline/config/calgold/schema.json` with 6 new t_any_* field mappings: t_any_actors, t_any_roles, t_any_cuisines, t_any_dishes, t_any_eras, t_any_continents
- Updated `pipeline/config/calgold/extraction_prompt.md` with actors, roles, cuisines, dishes, eras, continents in JSON output format
- Enhanced `phase4_normalize.py` with COUNTRY_TO_CONTINENT dictionary (30+ country mappings)
- Enhanced `phase5_geocode.py` to parse address.county from Nominatim response into t_any_counties
- t_schema_version default bumped to 3

### Step 1: Acquire (phase1_acquire.py)
- Command: `python3 pipeline/scripts/phase1_acquire.py --pipeline calgold --limit 120`
- Result: 30 new MP3 files (checkpoint skipped 1-90). Total audio: 120
- No errors

### Step 2: Transcribe (phase2_transcribe.py)
- Background execution with polling (G18 mitigation)
- Result: 30 new transcripts. Total: 120/120
- No errors

### Step 3: Re-Extract ALL 120 (phase3_extract.py)
- Command: `python3 pipeline/scripts/phase3_extract.py --pipeline calgold --limit 120`
- Result: ALL 120 extracted JSON files overwritten with v3 prompt (actors, roles, cuisines, dishes, eras, continents)
- Every entity now contains the 6 new fields
- No errors

### Step 4: Re-Normalize ALL 120 (phase4_normalize.py)
- Command: `python3 pipeline/scripts/phase4_normalize.py --pipeline calgold --limit 120`
- Result: ALL entities normalized with schema v3 fields, t_schema_version: 3
- Continent lookup applied: all CalGold entities -> ["North America"]
- No errors

### Step 5: Re-Geocode ALL 120 (phase5_geocode.py)
- Command: `python3 pipeline/scripts/phase5_geocode.py --pipeline calgold --limit 120`
- Result: County parsing active. t_any_counties populated from Nominatim address.county
- 120/120 geocoded files produced
- No errors

### Handoff
- Checkpoint written to pipeline/data/calgold/handoff-v4.12.json
- schema_version: 3, new_fields: all 6 present
- Counts: 120 transcripts, 120 extracted, 120 normalized, 120 geocoded
- Status: ready_for_phase_6_7
- Zero interventions

---

## Section B: Claude Code Execution (Phases 6-7 + Post-Flight)

**Agent:** Claude Code (Opus 4.6, `--dangerously-skip-permissions`)
**Interventions:** 1 (checkpoint reset - see below)

### Handoff Verification
- Read pipeline/data/calgold/handoff-v4.12.json
- schema_version: 3 confirmed
- All 6 new fields present in new_fields array
- transcript/extracted/normalized/geocoded counts: 120 each
- status: ready_for_phase_6_7

### Step 6: Enrich (phase6_enrich.py)
- Command: `python3 pipeline/scripts/phase6_enrich.py --pipeline calgold`
- **Intervention:** Initial run only enriched 30 new files (checkpoint had 90 from v3.10). Old 90 enriched files were schema v2 without the new fields. Reset checkpoint and re-ran for all 120.
- Result: 120 files enriched via Google Places API
- Total entities: 296
- Enrichment rate: 289/296 (97.6%)
- Coordinate backfill: 201 entities received coordinates from Google Places
- 7 misses (niche infrastructure/events without Places listings)
- No API errors

### Step 7: Load (phase7_load.py)
- Command: `python3 pipeline/scripts/phase7_load.py --pipeline calgold --database staging`
- Reset load checkpoint (same stale v3.10 checkpoint issue)
- Result: 120 files, 296 documents loaded to staging
- Total unique CalGold entities in Firestore staging: 300 (net of all dedup merges)
- Total platform entities: 412 (300 CalGold + 112 RickSteves visible in staging)
- Pipeline registry updated with entity_count and t_schema_version: 3
- No errors

### Step 8: Post-Flight - Schema v3 Validation

**Standard checks:**
- [x] Security: `grep -rnI "AIzaSy" .` -> only doc references (12 matches, all in docs/)
- [x] Entity count: 300 CalGold entities in Firestore staging
- [x] Enrichment rate: 289/296 (97.6%)
- [x] Geocoding rate: 289/296 (97.6%)

**Schema v3 checks:**
- [x] t_schema_version: 296/296 (100%) at version 3
- [x] t_any_actors: 296/296 (100%) populated - all contain "Huell Howser"
- [x] t_any_roles: 296/296 (100%) populated - all contain "host"
- [x] t_any_continents: 296/296 (100%) populated with ["North America"]
- [x] t_any_counties: 249/296 (84.1%) populated (non-empty county strings)
- [x] t_any_cuisines: 56/296 populated (food-related entities)
- [x] t_any_dishes: 69/296 populated (food-related entities)
- [x] t_any_eras: 244/296 (82.4%) populated (history-related entities)

**Food entity spot-check:**
- Linbrook Bowling Center: cuisines=["american", "pizza"], dishes=["extra large deluxe", "hamburger", "hot dog", "pizza"]
- Narona 50 Lodge: cuisines=["norwegian", "scandinavian"], dishes=["coffee", "lefse", "lutefisk", "norwegian meatballs"]
- In-N-Out Burger Museum: cuisines=["american"], dishes=["3x3", "4x4", "animal-style burger", "double-double", "french fries"]

**History entity spot-check:**
- The Original 16 to 1 Mine: eras=["1850s", "1940s", "1950s", "1960s", "gold rush"]
- Subway Terminal Building: eras=["1908", "1916", "1920s", "1924-1925", "world war ii"]
- Marshall Gold Discovery State Historic Park: eras present

### Step 9: Artifacts
- [x] docs/calgold-build-v4.12.md (this file)
- [x] docs/calgold-report-v4.12.md
- [x] docs/kjtcom-changelog.md (v4.12 appended at top)
- [x] README.md (Thompson Schema, Project Status, Pipelines, Changelog updated)
