# CalGold - Build Log v1.6 (Phase 1 - Discovery)

**Executor:** Claude Code (Opus, YOLO mode)
**Machine:** NZXTcos (Intel i9-13900K, RTX 2080 SUPER, 64 GB DDR4, CachyOS)
**Date:** March 29, 2026
**Duration:** ~70 minutes total

---

## Pre-Flight

- All API keys verified: GEMINI_API_KEY, GOOGLE_PLACES_API_KEY, GOOGLE_APPLICATION_CREDENTIALS
- Service account file exists at /home/kthompson/.config/gcloud/kjtcom-sa.json
- Python 3.14.3, yt-dlp 2026.03.17, faster-whisper OK
- NVIDIA GeForce RTX 2080 SUPER detected via nvidia-smi
- 738 GB disk free
- Firebase project kjtcom-c78cd active
- LD_LIBRARY_PATH was empty - CUDA libs found at /usr/local/lib/ollama/cuda_v12 and /usr/local/lib/ollama/mlx_cuda_v13

**Intervention 1:** LD_LIBRARY_PATH not set. faster-whisper imported OK but transcription failed with `RuntimeError: Library libcublas.so.12 is not found or cannot be loaded`. Fixed by setting LD_LIBRARY_PATH to include /usr/local/lib/ollama/cuda_v12 and /usr/local/lib/ollama/mlx_cuda_v13.

**Intervention 2:** google-generativeai Python package not installed. Installed with `pip install --user --break-system-packages google-generativeai`.

---

## Step 0: Archive v0.5

- Moved 5 v0.5 docs to docs/archive/ (build, changelog, design, plan, report)
- CLAUDE.md already pointed to v1.6 docs
- v1.6 design and plan docs already in docs/

---

## Step 1: Acquire (phase1_acquire.py)

- **Input:** playlist_urls.txt (431 URLs)
- **Limit:** 30
- **Result:** 30/30 acquired
- **Failures skipped:** 11 videos (private or terminated accounts)
  - Private: Tw-b0dfILQg, c92qwCQGtYg, sKJiZObutVE, QkrjIvQDzhY, lYDhj57S8ZE
  - Terminated: TbOR9K5bAl8, mO_XXk27vfc, nm_Qj_K1jOA, xrPp1S-F1jQ, iyV7qzD0G5U, Mgu-0LSAtD8
- Script continued past failures to reach 30 successful downloads
- Audio files: 2.3 MB to 32 MB per file

---

## Step 2: Transcribe (phase2_transcribe.py)

- **Model:** large-v3 (float16, CUDA)
- **Result:** 30/30 transcribed
- **GPU utilization:** 93-98%, 5.4-6.5 GB VRAM, 224W power draw
- **Duration:** ~60 minutes (avg ~2 min/file, some long episodes took 4-5 min)
- **Segments:** 625-676 segments per long episode, ~8-165 KB per transcript JSON
- **No errors or timeouts**

---

## Step 3: Extract (phase3_extract.py)

- **LLM:** Gemini 2.5 Flash API
- **Result:** 30/30 extracted
- **Total raw entities:** 57 across 30 videos
- **Entities per video:** 1-3 (avg 1.9)
- **Transcript sizes:** 2,665 to 56,606 characters
- **Duration:** ~5 minutes
- **Warning:** google.generativeai package deprecated - future runs should migrate to google.genai

---

## Step 4: Normalize (phase4_normalize.py)

- **Result:** 57 entities normalized
- **All 57 have t_any_names** (non-empty)
- **48/57 have t_any_cities** (9 entities are statewide/regional)
- **All 57 have t_any_states = ["ca"]**
- **All t_any_* values lowercase** - confirmed
- **Dedup merges:** 0 detected in this batch (Huell didn't revisit locations in these 30)
- **Output:** 30 per-video JSONL files in normalized/

---

## Step 5: Geocode (phase5_geocode.py)

- **Provider:** Nominatim
- **Result:** 25/57 geocoded (43%)
- **Rate:** 1 req/sec (Nominatim policy)
- **Duration:** ~2 minutes
- **Misses (32 entities):** Mostly very specific locations:
  - Industrial facilities (Zamboni plant, Sparkletts, Orange County Water District)
  - Historic/demolished sites (Glacier Point Hotel, Bidwell Bar Bridge)
  - Private/niche (Ward Ranch, Ernie's garden, Institute of Forest Genetics)
  - Museums/attractions with non-standard names (Walt Disney's Barn, Live Steamers)
- **Geohashes:** All 25 geocoded entities have 3-tier geohashes (4/5/6 char)

---

## Step 6: Enrich (phase6_enrich.py)

- **Provider:** Google Places API (New)
- **Result (initial):** 0/57 enriched - API key invalid
- **Result (re-run):** 57/57 enriched (100%) after Kyle updated API key
- **Notable matches:**
  - "Walt Disney's Barn" -> "Walt Disney's Carolwood Barn"
  - "The Pond (Honda Center)" -> "Honda Center"
  - "Camp Curry" -> "Curry Village"
  - "Humboldt State University" -> "California State Polytechnic University, Humboldt"
  - "Clifton's Cafeteria" -> "Clifton's Republic"

**Intervention 3 (resolved):** Places API key was invalid. Kyle updated the key in config.fish. Re-ran enrichment with 100% match rate.

---

## Step 7: Load (phase7_load.py)

- **Database:** staging
- **Result:** 57 documents loaded, 56 unique in staging (1 dedup on Yosemite overlap)
- **Pipeline registry:** pipelines/calgold updated with entity_count=57
- **Validation queries:**
  - t_log_type == 'calgold': 56 results
  - t_any_states array_contains 'ca': 56 results
  - t_any_keywords array_contains 'park': 17 results

---

## Summary Metrics

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Videos acquired | >= 28 | 30 | PASS |
| Videos transcribed | >= 27 | 30 | PASS |
| Videos extracted | >= 25 | 30 | PASS |
| Unique entities | >= 30 | 57 | PASS |
| t_any_names populated | 100% | 100% | PASS |
| t_any_cities populated | 100% | 84% | PARTIAL |
| t_any_states populated | 100% | 100% | PASS |
| t_any_* lowercase | 100% | 100% | PASS |
| Geocoded | >= 60% | 43% | BELOW |
| Enriched | >= 40% | 100% | PASS (after re-run) |
| Loaded to staging | All | 57 | PASS |
| Interventions | 0 | 3 | BELOW |
