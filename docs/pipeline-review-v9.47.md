# Pipeline Phase Review - Bourdain Prep (v9.47)

This document reviews the 7-phase IAO pipeline in preparation for the "Bourdain" pipeline (114 videos). It identifies current scripts, known issues, and recommended middleware enhancements for Phase 10.

## Overview

| Phase | Script | Primary Tool | Est. Runtime (114 videos) |
|-------|--------|--------------|---------------------------|
| 1 | `pipeline/scripts/phase1_acquire.py` | yt-dlp | ~30 min |
| 2 | `pipeline/scripts/phase2_transcribe.py` | faster-whisper (CUDA) | ~4-6 hours |
| 3 | `pipeline/scripts/phase3_extract.py` | Gemini Flash API | ~2-3 hours |
| 4 | `pipeline/scripts/phase4_normalize.py` | Python (Thompson Schema) | ~10 min |
| 5 | `pipeline/scripts/phase5_geocode.py` | Nominatim (OSM) | ~30-60 min |
| 6 | `pipeline/scripts/phase6_enrich.py` | Google Places API | ~20-30 min |
| 7 | `pipeline/scripts/phase7_load.py` | Firebase Admin SDK | ~5 min |

**Total Est. E2E Runtime:** ~8-11 hours (highly dependent on CUDA availability for transcription).

---

## Phase-by-Phase Detail

### Phase 1: Acquire
- **Location:** `pipeline/scripts/phase1_acquire.py`
- **Function:** Downloads audio from YouTube playlists or URLs.
- **Known Issues:** 
    - YouTube availability (private/deleted videos).
    - Age-restricted content requiring cookie authentication.
    - Large playlist ordering drift.
- **Middleware Enhancements:**
    - Implement robust checkpoint resumption to handle network interruptions.
    - Automated skipping of files that already exist on disk (size/hash check).

### Phase 2: Transcribe
- **Location:** `pipeline/scripts/phase2_transcribe.py`
- **Function:** Converts MP3 audio to timestamped JSON transcripts.
- **Known Issues:**
    - **G2/G23:** CUDA `LD_LIBRARY_PATH` dependency in Fish shell.
    - **G21:** CUDA Out-of-Memory (OOM) on large files.
    - Fixed timeouts causing premature termination on long videos.
- **Middleware Enhancements:**
    - **Graduated Timeouts:** Implement logic to scale timeout based on file duration (e.g., 2m for clips, 10m for episodes, 20m for marathons).
    - **Batching:** Sub-batching within CUDA memory limits to prevent OOM.

### Phase 3: Extract
- **Location:** `pipeline/scripts/phase3_extract.py`
- **Function:** Identifies entities (locations, shows, etc.) from transcripts using LLMs.
- **Known Issues:**
    - Prompt drift: one prompt doesn't fit all pipelines (RickSteves vs. TripleDB).
    - API rate limits (Gemini Flash RPM/TPM).
- **Middleware Enhancements:**
    - **Prompt Management:** Move extraction prompts to `template/config/{pipeline}/` and load dynamically.
    - **Token Optimization:** Summarize long transcripts before extraction to save cost/tokens.

### Phase 4: Normalize
- **Location:** `pipeline/scripts/phase4_normalize.py`
- **Function:** Maps raw LLM output to Thompson Schema (`t_any_*` fields).
- **Known Issues:**
    - **G37/G49:** Mixed-case show names causing retrieval issues in the bot.
    - Schema drift between different LLM versions.
- **Middleware Enhancements:**
    - **Schema Validator:** Integrate a Pydantic-based or JSON Schema validator against `data/schema_reference.json`.
    - **Force Lowercase:** Enforce lowercase for categorical fields (`t_any_shows`, `t_any_continents`).

### Phase 5: Geocode
- **Location:** `pipeline/scripts/phase5_geocode.py`
- **Function:** Converts location names to Lat/Lng coordinates.
- **Known Issues:**
    - Nominatim 1 request/second rate limit.
    - Poor performance for highly specific or niche locations.
- **Middleware Enhancements:**
    - **Smart Backfill:** Automatically fallback to Google Places geocoding if Nominatim fails (partial implementation exists, needs formalization).
    - **Local Cache:** Cache coordinates for common cities/regions to bypass API calls.

### Phase 6: Enrich
- **Location:** `pipeline/scripts/phase6_enrich.py`
- **Function:** Adds ratings, reviews, and metadata from Google Places.
- **Known Issues:**
    - Google Places API cost (must stay within free tier/credits).
    - Field mask selection (missing critical fields like `priceLevel`).
- **Middleware Enhancements:**
    - **Enrichment Cache:** Persistent SQLite store for enrichment results to avoid paying for the same place twice.
    - **Validation:** Cross-check LLM-extracted name against Google-returned name for confidence scoring.

### Phase 7: Load
- **Location:** `pipeline/scripts/phase7_load.py`
- **Function:** Uploads final entities to Firestore.
- **Known Issues:**
    - **G33:** Duplicate entity IDs if script is re-run without care.
    - **G35:** Production write safety (accidental overwrites).
- **Middleware Enhancements:**
    - **Dry-Run Mode:** Mandatory summary output showing exactly what will change before writes occur.
    - **Post-Load Enrichment:** Trigger `scripts/enrich_counties.py` automatically after loading a new pipeline.
    - **Deduplication:** Internal logic to check for existing IDs in the target collection.

---

## Phase 10 Recommendations

1. **Integrated Runner:** Create `pipeline/scripts/runner.py` that orchestrates all 7 phases with a single command and unified logging.
2. **Standardized Logging:** Update all pipeline scripts to use `scripts/utils/iao_logger.py` for consistent observability.
3. **Registry Integration:** Automatically update `data/middleware_registry.json` and `iteration_registry.json` when a new pipeline is loaded.

*Produced v9.47, April 5, 2026.*
