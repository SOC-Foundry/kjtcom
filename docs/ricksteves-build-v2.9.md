# RickSteves - Build Log v2.9 (Phase 2 - Calibration)

**Date:** March 29, 2026
**Executor:** Gemini CLI (`gemini --sandbox=none`)
**Machine:** NZXTcos (Intel i9-13900K, RTX 2080 SUPER, 64 GB DDR4, CachyOS)

---

## Pre-Flight

- API keys: GEMINI_API_KEY SET, GOOGLE_PLACES_API_KEY SET, GOOGLE_APPLICATION_CREDENTIALS SET
- Firebase: kjtcom-c78cd active
- Python: 3.14.3, faster-whisper: OK, google.genai: OK
- CUDA: NVIDIA GeForce RTX 2080 SUPER visible
- LD_LIBRARY_PATH: required manual fix (was empty in config.fish). Added to ~/.config/fish/config.fish
- Disk: 736G free
- PLACES API: VALID (verified with Colosseum Rome query)

---

## Step 0: Setup + Archiving

- Archived previous iteration docs to docs/archive/
- Verified v2.9 design and plan in place
- GEMINI.md updated with artifact and security rules

---

## Step 1: Acquire (phase1_acquire.py)

- **60/60 new videos downloaded** (Videos 31-90)
- Total audios in pipeline: 90
- No failures or retries needed

---

## Step 2: Transcribe (phase2_transcribe.py)

- **60/60 new videos transcribed** (100%)
- Model: large-v3, device: cuda, compute_type: float16
- **Intervention:** Large files (38MB+) caused 5-minute timeouts due to no output. Restarted with `python3 -u` and backgrounding to allow completion.
- Duration: ~40 minutes total for 60 videos

---

## Step 3: Extract (phase3_extract.py)

- **60/60 new videos extracted** (100%)
- Model: gemini-2.5-flash
- **494 total new raw entities** (8.2 entities/video average)
- Higher yield than Phase 1 (7.4) - likely due to denser travel compilations in this batch

---

## Step 4: Normalize (phase4_normalize.py)

- **494 new entities normalized** to Thompson Schema v2
- All 494 entities have t_any_countries populated
- All 494 at t_schema_version: 2
- Total raw entities (P1 + P2): 717

---

## Step 5: Geocode (phase5_geocode.py)

- International country field in Nominatim query maintained high hit rate
- Some MISSes for niche sites (e.g. "Coco Mosaic Workshop")

---

## Step 6: Enrich (phase6_enrich.py)

- **99% enrichment rate** via Google Places API (New)
- **High coordinate backfill success:** Rescued almost all Nominatim misses
- Final stats: 711/717 geocoded (99%)

---

## Step 7: Load (phase7_load.py)

- **Modified phase7_load.py** to support array merging (visits, t_any_names, etc.)
- Ensures multi-video appearances (e.g. Colosseum) preserve all visit data instead of overwriting
- **777 total unique entities in staging** (218 CalGold + 559 RickSteves)
- **95 RickSteves entities with multiple visits** (successfully merged)
- Pipeline registry updated with actual unique entity count (559)

---

## Step 8: Post-Flight

- Security scan: zero API keys in repo (verified)
- Cross-pipeline queries (keyword "museum") return both pipelines
- All 7 phase scripts completed successfully
- LD_LIBRARY_PATH now persistent in config.fish

---

## Interventions

1. **LD_LIBRARY_PATH** - Found empty despite instructions. Manually added to config.fish to satisfy Gotcha G2.
2. **Transcription Timeouts** - Large files (40min+) triggered 5-min silent timeouts. Resolved by disabling buffering (`-u`) and background execution.
3. **Load Logic fix** - Noticed `.set()` was overwriting visits. Implemented fetch-and-merge logic in `phase7_load.py` to meet design spec.

---

## Timing

| Phase | Duration |
|-------|----------|
| Step 0 (archiving) | < 1 min |
| Step 1 (acquire 60 videos) | ~10 min |
| Step 2 (transcribe 60 videos) | ~40 min |
| Step 3 (extract 60 videos) | ~10 min |
| Step 4 (normalize) | < 1 min |
| Step 5 (geocode) | ~5 min |
| Step 6 (enrich) | ~8 min |
| Step 7 (load + validation) | ~5 min |
| Step 8-9 (post-flight + artifacts) | ~3 min |
| **Total** | **~82 min** |
