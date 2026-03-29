# CalGold - Plan v1.6 (Phase 1 - Discovery)

**Phase:** 1 - Discovery (30 videos through full pipeline)
**Executor:** Claude Code (YOLO mode, Opus)
**Machine:** NZXTcos (Intel i9-13900K, RTX 2080 SUPER, 64 GB DDR4, CachyOS)
**Goal:** Process 30 CalGold videos through all 7 pipeline stages. Validate Thompson Schema normalization at scale. Load enriched entities to staging Firestore. Achieve zero interventions. Produce Phase 1 report.

---

## Project Identity

| Key | Value |
|-----|-------|
| Domain | kylejeromethompson.com |
| Repository | `git@github.com:SOC-Foundry/kjtcom.git` |
| Firebase Project ID | `kjtcom-c78cd` |
| GCP Parent Org | socfoundry.com |
| Dev Machine | NZXTcos |

---

## Autonomy Rules

```
1. AUTO-PROCEED. NEVER ask permission. YOLO.
2. SELF-HEAL: max 3 attempts per error. Checkpoint after every step.
3. Git READ only. NEVER git add/commit/push.
4. FORMATTING: No em-dashes. Use " - " instead. Use "->" for arrows.
5. MANDATORY: produce calgold-build + calgold-report + calgold-changelog
6. DATABASE: Load to "staging" database only. NEVER write to "(default)" in Phase 1.
7. LIMITS: --limit 30 on all phase scripts. Do NOT process more than 30 videos.
```

---

## Pre-Flight Checklist

```
[ ] v0.5 artifacts archived to docs/archive/
[ ] calgold-design-v1.6.md in docs/
[ ] calgold-plan-v1.6.md in docs/ (this file)
[ ] CLAUDE.md updated to point to v1.6 docs
[ ] git status clean
[ ] API keys validated:
    [ ] echo $GEMINI_API_KEY (non-empty, kjtcom key)
    [ ] echo $GOOGLE_PLACES_API_KEY (non-empty, kjtcom key)
    [ ] echo $GOOGLE_APPLICATION_CREDENTIALS (points to kjtcom-sa.json)
    [ ] test -f $GOOGLE_APPLICATION_CREDENTIALS (file exists)
    [ ] firebase use kjtcom-c78cd succeeds
[ ] Build tools verified:
    [ ] python3 --version (>= 3.10)
    [ ] yt-dlp --version
    [ ] python3 -c "import faster_whisper" (no error)
    [ ] nvidia-smi (RTX 2080 SUPER visible)
[ ] Previous test entity in staging Firestore (from v0.5) - leave it, don't wipe
[ ] Disk space: at least 10 GB free (30 videos x ~50MB audio + transcripts)
[ ] CUDA LD_LIBRARY_PATH set in fish config
```

---

## Step 0: Archive v0.5 + Update README

```fish
cd ~/dev/projects/kjtcom

# Archive v0.5 docs
mv docs/calgold-design-v0.5.md docs/archive/
mv docs/calgold-plan-v0.5.md docs/archive/
mv docs/calgold-build-v0.5.md docs/archive/
mv docs/calgold-report-v0.5.md docs/archive/
mv docs/calgold-changelog-v0.5.md docs/archive/

# Place v1.6 docs (should already be in docs/ from Kyle)
ls docs/calgold-design-v1.6.md docs/calgold-plan-v1.6.md

# Update CLAUDE.md
printf '# kjtcom - Agent Instructions\n\n## Read Order\n1. docs/calgold-design-v1.6.md\n2. docs/calgold-plan-v1.6.md\n' > CLAUDE.md

# Replace README.md with new Hyperagents-style version
# (Kyle will provide the README content or agent generates from design doc)
```

**Success criteria:** Only v1.6 docs in docs/. v0.5 docs in docs/archive/. CLAUDE.md points to v1.6.

---

## Step 1: Acquire Audio (phase1_acquire.py)

Download audio for the first 30 videos in the CalGold playlist.

```fish
cd ~/dev/projects/kjtcom
python3 pipeline/scripts/phase1_acquire.py --pipeline calgold --limit 30
```

**Expected behavior:**
- Reads pipeline/config/calgold/playlist_urls.txt
- Downloads first 30 video IDs as mp3 to pipeline/data/calgold/audio/
- Writes checkpoint_acquire.json after each download
- Skips any video IDs already in checkpoint
- Timeout: 120 seconds per video

**Expected output:**
- 30 mp3 files in pipeline/data/calgold/audio/
- checkpoint_acquire.json with 30 completed entries

**If errors:**
- yt-dlp 403/429: wait 30 seconds, retry. Max 3 attempts.
- Video unavailable: log and skip. Count toward the 30.
- Timeout: log and skip.

**Success criteria:** >= 28 of 30 videos downloaded. checkpoint_acquire.json exists.

---

## Step 2: Transcribe Audio (phase2_transcribe.py)

Transcribe all downloaded audio using faster-whisper on the RTX 2080 SUPER.

```fish
python3 pipeline/scripts/phase2_transcribe.py --pipeline calgold --limit 30
```

**Expected behavior:**
- Reads mp3 files from pipeline/data/calgold/audio/
- Uses faster-whisper with CUDA (large-v3 model)
- Outputs timestamped JSON to pipeline/data/calgold/transcripts/
- Each transcript: `{ "video_id": "...", "segments": [{ "start": 0.0, "end": 2.5, "text": "..." }, ...] }`
- Writes checkpoint_transcribe.json after each transcription
- Timeout: 300 seconds per video

**Expected output:**
- ~28-30 JSON transcript files in pipeline/data/calgold/transcripts/
- Average transcript: 25-30 min episode -> ~5,000-10,000 words

**If errors:**
- CUDA OOM: reduce model to medium. Log the swap.
- Timeout: log and skip. Likely a 60+ minute episode.
- LD_LIBRARY_PATH not set: STOP. This is Gotcha G2. Fix fish config and re-run.

**Success criteria:** >= 27 of 30 videos transcribed. Spot-check 3 transcripts for quality - should contain recognizable location names and Huell Howser speech patterns.

---

## Step 3: Extract Entities (phase3_extract.py)

Send transcripts to Gemini 2.5 Flash API with the CalGold extraction prompt.

```fish
python3 pipeline/scripts/phase3_extract.py --pipeline calgold --limit 30
```

**Expected behavior:**
- Reads transcripts from pipeline/data/calgold/transcripts/
- Reads extraction prompt from pipeline/config/calgold/extraction_prompt.md
- Sends full transcript + prompt to Gemini Flash API (1M context - no chunking)
- Parses JSON response into pipeline/data/calgold/extracted/{video_id}.json
- Each extracted file: JSON array of location objects per the extraction prompt schema
- Writes checkpoint_extract.json after each extraction
- Timeout: 300 seconds per video

**Expected output:**
- ~27-30 JSON extraction files
- Each file contains 1-5 location objects (some episodes visit multiple places)
- Total: 40-80 raw location entities across 30 videos

**If errors:**
- Gemini 429 (rate limit): exponential backoff starting at 10 seconds. Max 3 retries.
- Gemini returns invalid JSON: log the raw response, skip. Count as extraction failure.
- Gemini returns empty array: valid - some videos may not have geocodable locations. Log but don't count as failure.
- Timeout: log and skip.

**Success criteria:** >= 25 of 30 videos extracted. Total raw entities >= 30. Spot-check 5 extractions for quality - entities should have name, city, description at minimum.

---

## Step 4: Normalize Entities (phase4_normalize.py)

Apply Thompson Schema normalization using schema.json indicator mappings.

```fish
python3 pipeline/scripts/phase4_normalize.py --pipeline calgold --limit 30
```

**Expected behavior:**
- Reads extracted JSON from pipeline/data/calgold/extracted/
- Reads schema.json from pipeline/config/calgold/
- For each raw entity, calls `normalize_entity()` from thompson_schema.py
- Populates all t_* standard fields and t_any_* indicator arrays
- Deduplicates by name + city (merge visits arrays)
- Outputs normalized JSONL to pipeline/data/calgold/normalized/calgold_normalized.jsonl
- All t_any_* values lowercased and sorted

**Expected output:**
- Single JSONL file with 30-60 unique normalized entities (after dedup)
- Every entity has: t_log_type, t_row_id, t_event_time, t_parse_time, t_source_label, t_schema_version
- Every entity has: t_any_names, t_any_cities, t_any_states (at minimum)
- Every entity has: source.* with original extracted data preserved

**Validation:**
After normalization, run validation:
```fish
python3 -c "
import json
with open('pipeline/data/calgold/normalized/calgold_normalized.jsonl') as f:
    entities = [json.loads(line) for line in f]
print(f'Total entities: {len(entities)}')
print(f'With t_any_names: {sum(1 for e in entities if e.get(\"t_any_names\"))}')
print(f'With t_any_cities: {sum(1 for e in entities if e.get(\"t_any_cities\"))}')
print(f'With t_any_states: {sum(1 for e in entities if e.get(\"t_any_states\"))}')
print(f'All lowercase: {all(v == v.lower() for e in entities for v in e.get(\"t_any_names\", []))}')
print(f'Dedup merges: {sum(1 for e in entities if len(e.get(\"source\", {}).get(\"visits\", [])) > 1)}')
"
```

**Success criteria:** All entities have t_any_names and t_any_cities. All t_any values lowercase. At least 1 dedup merge found (Huell revisited some places).

---

## Step 5: Geocode Entities (phase5_geocode.py)

Geocode all normalized entities via Nominatim.

```fish
python3 pipeline/scripts/phase5_geocode.py --pipeline calgold --limit 30
```

**Expected behavior:**
- Reads normalized JSONL
- For each entity, queries Nominatim with: `{name}, {city}, {state}`
- Rate limit: 1 request per second (Nominatim policy)
- Populates t_any_coordinates, t_any_geohashes (4/5/6 char), and t_enrichment.nominatim
- Outputs geocoded JSONL to pipeline/data/calgold/geocoded/
- Writes checkpoint_geocode.json

**Expected output:**
- Geocoded JSONL with lat/lon for 60-80% of entities
- Not all entities will geocode (obscure locations, natural features, demolished sites)
- t_any_geohashes contains 3 values per entity (precision 4, 5, 6)

**If errors:**
- Nominatim 429: wait 2 seconds, retry. Max 3.
- No result: leave coordinates empty. Log. Don't fail.
- Timeout: retry once.

**Success criteria:** >= 60% geocoded. All geocoded entities have t_any_geohashes with 3 precision levels.

---

## Step 6: Enrich Entities (phase6_enrich.py)

Enrich geocoded entities via Google Places API (New).

```fish
python3 pipeline/scripts/phase6_enrich.py --pipeline calgold --limit 30
```

**Expected behavior:**
- Reads geocoded JSONL
- For each entity with coordinates, searches Google Places by name + location
- Populates t_enrichment.google_places (place_id, rating, current_name, still_open, website, phone)
- Adds google_current_name to t_any_names if different from source name
- Outputs enriched JSONL to pipeline/data/calgold/enriched/
- Writes checkpoint_enrich.json

**Expected output:**
- Enriched JSONL with Google Places data for 40-60% of geocoded entities
- Some locations won't match (demolished, renamed, too obscure)
- t_enrichment.google_places.t_match records what search term matched

**Success criteria:** >= 40% of geocoded entities enriched. Spot-check 5 enriched entities - ratings should be reasonable (2.0-5.0).

---

## Step 7: Load to Staging Firestore (phase7_load.py)

Load all enriched entities to the staging database.

```fish
python3 pipeline/scripts/phase7_load.py --pipeline calgold --database staging
```

**Expected behavior:**
- Reads enriched JSONL
- Batched writes to Firestore staging database, `locations` collection
- Updates `pipelines/calgold` document with entity_count, last_run, phases_complete
- Updates `videos/{video_id}` documents with status and timestamps

**Expected output:**
- 30-60 documents in staging `locations` collection
- Pipeline registry updated
- Video bookkeeping updated

**Validation after load:**
```fish
python3 -c "
from google.cloud import firestore
db = firestore.Client(database='staging')

# Count
docs = list(db.collection('locations').where('t_log_type', '==', 'calgold').stream())
print(f'CalGold entities in staging: {len(docs)}')

# Test t_any query
results = list(db.collection('locations').where('t_any_states', 'array_contains', 'ca').stream())
print(f'Entities in CA: {len(results)}')

# Test keyword search
results = list(db.collection('locations').where('t_any_keywords', 'array_contains', 'park').stream())
print(f'Entities with keyword park: {len(results)}')

# Pipeline registry
pipeline = db.document('pipelines/calgold').get()
print(f'Pipeline entity_count: {pipeline.to_dict().get(\"entity_count\")}')
"
```

**Success criteria:** All enriched entities loaded. array-contains queries on t_any_keywords, t_any_states, t_any_cities all return results. Pipeline registry updated.

---

## Step 8: Post-Flight Verification

### Tier 1 - Standard Health

```
[ ] All 7 phase scripts completed without fatal errors
[ ] Checkpoint files exist for all phases
[ ] No uncaught Python exceptions in build log
[ ] Staging Firestore has CalGold entities
[ ] Pipeline registry (pipelines/calgold) updated with entity_count > 0
[ ] CLAUDE.md points to v1.6 docs
[ ] Changelog entry written
```

### Tier 2 - Phase 1 Functional Playbook

```
[ ] >= 28 of 30 videos acquired (audio files exist)
[ ] >= 27 of 30 videos transcribed (transcript JSON exists)
[ ] >= 25 of 30 videos extracted (extraction JSON exists)
[ ] Total unique normalized entities >= 30
[ ] All entities have t_any_names populated (non-empty array)
[ ] All entities have t_any_cities populated (non-empty array)
[ ] All entities have t_any_states = ["ca"]
[ ] All t_any_* values are lowercase
[ ] >= 60% of entities geocoded (have t_any_coordinates)
[ ] >= 40% of geocoded entities enriched (have t_enrichment.google_places)
[ ] Firestore staging: array-contains on t_any_keywords returns results
[ ] Firestore staging: array-contains on t_any_states returns results
[ ] Firestore staging: t_log_type == 'calgold' returns correct count
[ ] At least 1 dedup merge occurred (multi-visit entity)
[ ] Cloud Function search returns CalGold entities for relevant query
```

---

## Step 9: Produce Artifacts

### 9.1 Build Log

Write `docs/calgold-build-v1.6.md`:
- Full session transcript with per-phase metrics
- Extraction success/failure counts
- Geocoding hit rate
- Enrichment match rate

### 9.2 Report

Write `docs/calgold-report-v1.6.md`:
- Summary metrics table (entities, geocoded, enriched, dedup merges)
- Per-phase timing
- Intervention count and descriptions
- Orchestration report
- Extraction prompt quality assessment (did it capture the right entities?)
- Recommendation for Phase 2

### 9.3 Changelog

Append to `docs/calgold-changelog-v1.6.md`:
```
**v1.6 (Phase 1 - Discovery)**
- 30-video discovery batch: {acquired}/{transcribed}/{extracted}
- {N} unique entities after normalization and dedup
- Geocoding: {N}% hit rate via Nominatim
- Enrichment: {N}% match rate via Google Places
- Thompson Schema validated at scale: all t_any_* fields populated
- {N} interventions
- README overhauled: Hyperagents-style with IAO Nine Pillars
```

---

## Environment Variables Required

```fish
# Verify these are set (should already be from Phase 0 fish config)
echo $GEMINI_API_KEY
echo $GOOGLE_PLACES_API_KEY
echo $GOOGLE_APPLICATION_CREDENTIALS
echo $LD_LIBRARY_PATH  # Must include CUDA libs for faster-whisper
```

---

## Estimated Timeline

| Phase | Duration | Notes |
|-------|----------|-------|
| Step 0 (archive + README) | 2 min | File moves |
| Step 1 (acquire 30 videos) | 10-15 min | yt-dlp, network-bound |
| Step 2 (transcribe 30 videos) | 15-30 min | CUDA-bound, ~60s per 25-min episode |
| Step 3 (extract 30 videos) | 5-10 min | Gemini Flash API, ~10s per video |
| Step 4 (normalize) | 1 min | Local Python, fast |
| Step 5 (geocode) | 5-10 min | Nominatim 1 req/sec rate limit |
| Step 6 (enrich) | 5-10 min | Google Places API |
| Step 7 (load to staging) | 1 min | Firestore batch writes |
| Step 8 (post-flight) | 2 min | Validation queries |
| Step 9 (artifacts) | 3 min | Write build/report/changelog |
| **Total** | **~45-90 min** | Mostly transcription + geocoding |
