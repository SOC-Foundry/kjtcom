# CalGold - Build v3.10 (Phase 3 - Stress Test)

**Pipeline:** calgold
**Phase:** 3 (Stress Test)
**Iteration:** 10 (global counter)
**Date:** 2026-03-29

---

## Section A: Gemini CLI Execution (Phases 1-5)

**Agent:** Gemini CLI (`gemini --sandbox=none --yolo`)
**Interventions:** 0

### Step 0: Pre-Flight
- All checks passed: API keys SET, CUDA visible, LD_LIBRARY_PATH set, 60 audio/60 transcripts confirmed
- Disk space sufficient, Python deps validated

### Step 1: Acquire (phase1_acquire.py)
- Command: `python3 pipeline/scripts/phase1_acquire.py --pipeline calgold --start 61 --limit 30`
- Result: 30 new MP3 files downloaded. Total: 90/90
- No errors

### Step 2: Transcribe (phase2_transcribe.py)
- Command: `nohup python3 -u pipeline/scripts/phase2_transcribe.py --pipeline calgold --start 61 --limit 30`
- Background execution with polling (G18 mitigation)
- Result: 30 new transcripts. Total: 90/90
- LD_LIBRARY_PATH embedded in script (G2 permanently resolved)
- No errors

### Step 3: Extract (phase3_extract.py)
- Command: `python3 pipeline/scripts/phase3_extract.py --pipeline calgold --start 61 --limit 30`
- Result: 30 new extracted JSON files. Total: 90/90
- No errors

### Step 4: Normalize (phase4_normalize.py)
- Command: `python3 pipeline/scripts/phase4_normalize.py --pipeline calgold --start 61 --limit 30`
- Result: All entities normalized with t_any_countries: ["us"], t_schema_version: 2
- No errors

### Step 5: Geocode (phase5_geocode.py)
- Command: `python3 pipeline/scripts/phase5_geocode.py --pipeline calgold --start 61 --limit 30`
- Result: 33% geocoded via Nominatim (new batch). Many niche California locations missed (G13 expected)
- No errors

### Handoff
- Checkpoint written to pipeline/data/calgold/handoff-v3.10.json
- Status: ready_for_phase_6_7
- Counts: 90 audio, 90 transcripts, 90 extracted
- Zero interventions

---

## Section B: Claude Code Execution (Phases 6-7 + Post-Flight)

**Agent:** Claude Code (Opus, `--dangerously-skip-permissions`)
**Interventions:** 0

### Step 6: Enrich (phase6_enrich.py)
- Command: `python3 pipeline/scripts/phase6_enrich.py --pipeline calgold`
- Note: Plan specified `--database staging` but phase6 does not accept that flag (file I/O only, no Firestore). Corrected and ran without it.
- Result: 90 files enriched via Google Places API
- Enrichment rate: 222/226 (98%)
- Coordinate backfill: 140 entities received coordinates from Google Places
- Geocoding rate post-backfill: 222/226 (98%) - up from 36% Nominatim-only
- 4 misses (all obscure/niche): Sombrero Canyon Debris Basin, Sombrero Canyon Flood Control Debris Basin, Zanja Madre (Mother Ditch) Section, The California Private Pullman Car
- No errors

### Step 7: Load (phase7_load.py)
- Command: `python3 pipeline/scripts/phase7_load.py --pipeline calgold --database staging`
- Result: 90 files loaded with array merge (fetch-and-merge pattern)
- Total unique CalGold entities in Firestore staging: 218
- Multi-visit merges: 5 entities shared across old and new batches
- Entity math: 132 unique (files 1-60) + 90 unique (files 61-90) - 5 overlaps = 217 unique row IDs -> 218 Firestore docs (1 additional from normalization variance)
- Pipeline registry updated with entity_count: 218
- No errors

### Step 8: Post-Flight
- [x] Security: `grep -rnI "AIzaSy" .` -> only plan/design checklist references (7 matches, all in docs)
- [x] Entity count: 218 CalGold entities in Firestore staging
- [x] Schema spot-check: UCLA Campus, Self-Realization Fellowship Lake Shrine, Old Town Temecula - all t_schema_version: 2, t_any_countries: ["us"]
- [x] Geocoding rate: 222/226 (98%)
- [x] Enrichment rate: 222/226 (98%)

### Step 9: Artifacts
- [x] docs/calgold-build-v3.10.md (this file)
- [x] docs/calgold-report-v3.10.md
- [x] docs/kjtcom-changelog.md (v3.10 appended at top)
- [x] README.md (Project Status, Pipelines, Changelog updated)
