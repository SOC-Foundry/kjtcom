# CalGold - Build Log v2.8 (Phase 2 - Calibration)

**Executor:** Claude Code (Opus, YOLO mode)
**Machine:** NZXTcos (Intel i9-13900K, RTX 2080 SUPER, 64 GB DDR4, CachyOS)
**Date:** 2026-03-29

---

## Pre-Flight

- [x] Fish shell confirmed: 4.5.0
- [x] GEMINI_API_KEY: SET
- [x] GOOGLE_PLACES_API_KEY: SET
- [x] GOOGLE_APPLICATION_CREDENTIALS: SET (file exists)
- [x] LD_LIBRARY_PATH: NOT SET initially (G2 triggered - sourced fish config)
- [x] Google Places API: VALID (endpoint test passed)
- [x] nvidia-smi: RTX 2080 SUPER
- [x] faster_whisper import: OK
- [x] Disk: 737 GB free
- [x] v1.6/v1.7 docs archived to docs/archive/
- [x] CLAUDE.md: shell, security, G2, artifact sections all present

---

## Step 0: Archive + CLAUDE.md

- Archived ricksteves v1.7 docs (design, plan, build, report, changelog) to docs/archive/
- Archived kjtcom-changelog-v1.6.md to docs/archive/
- CLAUDE.md already had all required sections from Kyle's prep
- Status: DONE

---

## Step 1: Acquire Audio (videos 31-60)

```
Command: python3 pipeline/scripts/phase1_acquire.py --pipeline calgold --limit 60
```

- 11 videos unavailable (private/terminated YouTube accounts)
- 60 new videos downloaded successfully
- Checkpoint: 90 total (30 Phase 1 + 60 Phase 2)
- Status: DONE

---

## Step 2: Transcribe Audio

```
Command: python3 pipeline/scripts/phase2_transcribe.py --pipeline calgold --limit 60
```

- G2 TRIGGERED: First attempt failed with `RuntimeError: Library libcublas.so.12 is not found or cannot be loaded`
- Fix: Set LD_LIBRARY_PATH to `/usr/local/lib/ollama/cuda_v12:/usr/local/lib/ollama/mlx_cuda_v13`
- Re-ran successfully with CUDA acceleration
- 60 new transcripts, 90 total
- Segment counts ranged from 420 to 1530 per video
- Spot-check: Clear Huell Howser content, proper segmentation
- Status: DONE (1 intervention - G2/CUDA path)

---

## Step 3: Extract Entities

```
Command: python3 pipeline/scripts/phase3_extract.py --pipeline calgold --limit 60
```

- 60 new extractions via google.genai (Gemini Flash)
- 226 total raw entities across 90 files
- Average: 2.5 entities/video (up from 1.9 in Phase 1)
- Status: DONE

---

## Step 4: Normalize Entities

```
Command: python3 pipeline/scripts/phase4_normalize.py --pipeline calgold --limit 60
```

- Initial run: 169 new entities from Phase 2 videos
- Issue: schema.json had t_schema_version: 1 and no t_any_countries mapping
- Fix: Updated schema.json to t_schema_version: 2, added country indicator with default "us", added region indicator
- Cleared normalize checkpoint, re-ran on ALL 90 files
- Results:
  - 226 total entities
  - Schema v2: 226/226 (100%)
  - t_any_countries: 226/226 (100%)
  - t_any_states: 226/226 (100%)
  - t_any_cities: 209/226 (92%)
  - Dedup merges: 3 entities with multiple visits
    - "Islands A, B, C, and D" (2 visits)
    - "Glendora Castle" (2 visits)
    - "GWRS Main Facility" (2 visits)
- Status: DONE

---

## Step 5: Geocode Entities

```
Command: python3 pipeline/scripts/phase5_geocode.py --pipeline calgold
```

- Cleared checkpoint, re-geocoded all 90 files
- Nominatim geocoding: 82/226 (36%)
- Many niche/historic CalGold locations missed by Nominatim (expected - G13)
- Status: DONE

---

## Step 6: Enrich + Re-Enrich Phase 1

```
Command: python3 pipeline/scripts/phase6_enrich.py --pipeline calgold
```

- Cleared checkpoint, enriched all 226 entities
- Google Places matched: 222/226 (98%)
- Coordinate backfill from Places: pushed geocoding from 36% to 98%
- 4 entities missed (no Places match)
- Status: DONE

---

## Step 7: Load to Staging Firestore

```
Command: python3 pipeline/scripts/phase7_load.py --pipeline calgold --database staging
```

- Cleared load checkpoint, loaded all 226 entities
- Firestore dedup reduced to 218 unique documents
- Cross-pipeline validation:
  - CalGold: 218 entities (up from 56)
  - RickSteves: 200 entities (unchanged)
  - Total platform: 418 entities
  - CalGold geocoding: 213/218 (97%)
  - CalGold enrichment: 213/218 (97%)
  - Schema v2: 218/218 (100%)
  - t_any_countries: 218/218 (100%)
  - Cross-pipeline "park" query: 54 results from both pipelines
  - Dedup merges: 3 entities with multiple visits
- Status: DONE

---

## Step 8: Post-Flight Verification

### Tier 1 - Standard Health
- [x] All 7 phase scripts completed
- [x] All checkpoint files exist
- [x] No API keys in repo (clean scan)
- [x] Staging CalGold: 218 entities (up from 56)
- [x] RickSteves: 200 (unchanged)
- [x] CLAUDE.md has all required sections

### Tier 2 - Phase 2 Functional Playbook
- [x] 60 new videos acquired
- [x] 60 new videos transcribed
- [x] 60 new videos extracted
- [x] All entities schema v2 with t_any_countries: ["us"]
- [x] 3 dedup merges reported
- [x] CalGold geocoding: 97% (target >= 80%)
- [x] CalGold enrichment: 97% (target >= 80%)
- [x] Phase 1 entities re-enriched with coordinate backfill
- [x] Cross-pipeline keyword query returns both pipelines
- [x] All t_any_* values lowercase (0 violations)
- [x] Zero API keys in repo

---

## Interventions

| # | Issue | Resolution | Root Cause |
|---|-------|-----------|-----------|
| 1 | LD_LIBRARY_PATH not set (G2) | Set to ollama CUDA paths | fish config not sourced by default in Bash subprocess |
| 2 | schema.json still on v1 | Updated to v2 with countries/regions | Not updated during v1.7 RickSteves work |

---

## Summary

- 60 new videos processed through full 7-phase pipeline
- 162 net new CalGold entities (218 total, up from 56)
- Geocoding jumped from 43% to 97% (Google Places backfill)
- Enrichment: 97% (222/226 raw matched)
- 3 dedup merges validated across Phase 1 + Phase 2
- Platform total: 418 entities across 2 pipelines
- 2 interventions (G2 CUDA path, schema v1 -> v2 upgrade)
