# RickSteves - Plan v1.7 (Phase 1 - Discovery)

**Phase:** 1 - Discovery (30 videos through full pipeline)
**Executor:** Claude Code (YOLO mode, Opus)
**Machine:** NZXTcos (Intel i9-13900K, RTX 2080 SUPER, 64 GB DDR4, CachyOS)
**Goal:** Process 30 Rick Steves videos through all 7 pipeline stages. Validate Thompson Schema v2 (t_any_countries, t_any_regions) with international locations. Validate cross-pipeline queries against CalGold data in staging. Achieve zero interventions. Produce Phase 1 report.

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
5. MANDATORY: produce ricksteves-build + ricksteves-report + ricksteves-changelog
6. DATABASE: Load to "staging" database only. NEVER write to "(default)".
7. LIMITS: --limit 30 on all phase scripts. Do NOT process more than 30 videos.
8. SECURITY: NEVER write API keys, tokens, or credentials into ANY file.
   Print only "SET" or "NOT SET" when validating keys. NEVER echo key values.
```

---

## Pre-Flight Checklist

```
[ ] CalGold v1.6 artifacts in docs/archive/ (CalGold Phase 1 complete)
[ ] ricksteves-design-v1.7.md in docs/
[ ] ricksteves-plan-v1.7.md in docs/ (this file)
[ ] CLAUDE.md updated:
    [ ] Read order points to ricksteves v1.7 docs
    [ ] Security section present (ABSOLUTE RULES)
[ ] git status clean
[ ] API keys validated (print SET/NOT SET only - NEVER print values):
    [ ] GEMINI_API_KEY is SET
    [ ] GOOGLE_PLACES_API_KEY is SET
    [ ] GOOGLE_APPLICATION_CREDENTIALS is SET and file exists
    [ ] firebase use kjtcom-c78cd succeeds
[ ] Build tools verified:
    [ ] python3 --version (>= 3.10)
    [ ] yt-dlp --version
    [ ] python3 -c "import faster_whisper" (no error)
    [ ] nvidia-smi (RTX 2080 SUPER visible)
    [ ] LD_LIBRARY_PATH includes CUDA libs (Gotcha G2 - check BEFORE transcription)
[ ] google.genai migration: phase3_extract.py uses google.genai, NOT google-generativeai
[ ] CalGold entities exist in staging Firestore (56 documents from Phase 1)
[ ] pipeline/config/ricksteves/ directory created with all 4 config files
[ ] pipeline/data/ricksteves/ directories created (audio, transcripts, extracted, etc.)
[ ] Disk space: at least 20 GB free (Rick Steves videos may be longer than CalGold)
```

---

## Step 0: Setup Pipeline Config + Schema v2 Migration

### 0.1 Create RickSteves Pipeline Config

```fish
mkdir -p pipeline/config/ricksteves
mkdir -p pipeline/data/ricksteves/{audio,transcripts,extracted,normalized,geocoded,enriched}
```

Create four files in `pipeline/config/ricksteves/`:
- `pipeline.json` - per design doc Section 3.3
- `schema.json` - per design doc Section 3.1 (16 indicator mappings)
- `extraction_prompt.md` - per design doc Section 3.2
- `playlist_urls.txt` - the 1,865 filtered video IDs + titles

### 0.2 Copy Filtered Playlist

The filtered playlist file (1,865 lines) should be at `pipeline/config/ricksteves/playlist_urls.txt`. If not present, generate it:

```fish
yt-dlp --flat-playlist --print "%(id)s %(title)s" \
  "https://www.youtube.com/c/RickSteves/videos" | \
  grep -viE 'preview|trailer|promo|packing|democracy|nationalism|christian|cannabis|marijuana|simpsons|blooper|outtake|how to avoid|choosing accom|planning a smart|bus tours and private|avoiding crowds' \
  > pipeline/config/ricksteves/playlist_urls.txt

wc -l pipeline/config/ricksteves/playlist_urls.txt
# Expected: ~1865
```

### 0.3 Update Shared Pipeline Scripts for Schema v2

Modify `pipeline/scripts/utils/thompson_schema.py`:
- `normalize_entity()` must handle `t_any_countries` and `t_any_regions` indicator mappings
- No code changes needed if the function is already driven by schema.json indicators (it should be)
- Verify by running a mock entity through the normalizer with the ricksteves schema.json

### 0.4 Migrate phase3_extract.py to google.genai

Replace `import google.generativeai` with `import google.genai` (or the correct new SDK import). Test with a single CalGold transcript to confirm it still works.

### 0.5 Update Geocoding to Use Google Places Fallback

Modify `pipeline/scripts/phase5_geocode.py` OR modify `pipeline/scripts/phase7_load.py`:
- After enrichment (phase6), if an entity has `t_enrichment.google_places` with coordinates but no `t_any_coordinates`, backfill from the enrichment data
- This fixes the 43% geocoding rate from CalGold Phase 1

### 0.6 Backfill CalGold Entities with Schema v2 Fields

```python
# One-time backfill of existing CalGold entities in staging
from google.cloud import firestore
db = firestore.Client(database='staging')

for doc in db.collection('locations').where('t_log_type', '==', 'calgold').stream():
    doc.reference.update({
        't_any_countries': ['us'],
        't_any_regions': [],
        't_schema_version': 2
    })
```

### 0.7 Update CLAUDE.md

```
# kjtcom - Agent Instructions

## Read Order
1. docs/ricksteves-design-v1.7.md
2. docs/ricksteves-plan-v1.7.md

## Security - ABSOLUTE RULES
- NEVER write API keys, tokens, or credentials into ANY file in the repo
- NEVER include API keys in build logs, reports, or changelog artifacts
- NEVER echo or print API key values in commands that get logged
- Read keys from environment variables ONLY
- If a key needs to be tested, print only "SET" or "NOT SET", never the value
- Violation of these rules is a BLOCKING failure - stop and alert Kyle

## Permissions
- CAN: flutter build web, firebase deploy --only hosting/firestore/functions
- CAN: pip install, npm install (project-level)
- CANNOT: git add / commit / push (Kyle commits at phase boundaries)
- CANNOT: sudo (ask Kyle - sudo exception)

## Database Rules
- Load to "staging" database only
- NEVER write to "(default)" without Kyle approval
- NEVER delete documents without Kyle approval

## Formatting
- No em-dashes. Use " - " instead.
- Use "->" for arrows.
```

**Success criteria:** All config files created. Schema v2 migration complete. CalGold entities backfilled. google.genai migration tested. CLAUDE.md has security section.

---

## Step 1: Acquire Audio (phase1_acquire.py)

```fish
python3 pipeline/scripts/phase1_acquire.py --pipeline ricksteves --limit 30
```

**Expected behavior:**
- Reads first 30 video IDs from playlist_urls.txt
- Downloads as mp3 to pipeline/data/ricksteves/audio/
- Rick Steves videos range from 3-min Travel Bites to 60-min specials
- Checkpoint after each download

**If errors:**
- Some videos may be region-locked or removed. Skip and continue.
- yt-dlp 403/429: wait 30 seconds, retry. Max 3.

**Success criteria:** >= 28 of 30 videos downloaded.

---

## Step 2: Transcribe Audio (phase2_transcribe.py)

```fish
python3 pipeline/scripts/phase2_transcribe.py --pipeline ricksteves --limit 30
```

**Expected behavior:**
- faster-whisper with CUDA (large-v3 model)
- Rick Steves speaks clearly with minimal background noise - high transcription quality expected
- Travel Bites (~3-5 min) transcribe in ~15-30 seconds
- Full episodes (~30 min) transcribe in ~60-90 seconds
- LD_LIBRARY_PATH must be set (Gotcha G2 - pre-flight catches this)

**Note on non-English content:** Rick Steves episodes include foreign language snippets (Italian menus, French signs, etc.). faster-whisper may transcribe these phonetically. The extraction prompt should handle this gracefully.

**Success criteria:** >= 27 of 30 transcribed. Spot-check: transcripts contain recognizable European place names.

---

## Step 3: Extract Entities (phase3_extract.py)

```fish
python3 pipeline/scripts/phase3_extract.py --pipeline ricksteves --limit 30
```

**Expected behavior:**
- Uses updated google.genai SDK (NOT deprecated google-generativeai)
- Reads ricksteves extraction_prompt.md
- Rick Steves Travel Bites should yield 1-2 entities each
- Travel Guide compilations should yield 3-10 entities each
- Full episodes should yield 5-15 entities each
- Expected total: 60-150 raw entities from 30 videos

**If the first 30 videos are mostly Travel Bites (short clips):** Entity-per-video ratio will be lower (~1.5). This is fine - the extraction prompt handles it.

**If the first 30 videos include compilations:** Entity-per-video ratio could be 3-5. Even better.

**Success criteria:** >= 25 of 30 extracted. Total raw entities >= 40. Entities include `country` field (not just `city`).

---

## Step 4: Normalize Entities (phase4_normalize.py)

```fish
python3 pipeline/scripts/phase4_normalize.py --pipeline ricksteves --limit 30
```

**Critical validation for Schema v2:**
- Every entity MUST have `t_any_countries` populated (non-empty)
- `t_any_regions` populated where the extraction returned a region
- `t_any_states` may be empty for European entities (correct behavior)
- `t_schema_version` = 2 on all entities
- All t_any values lowercase

```fish
python3 -c "
import json, glob
entities = []
for f in glob.glob('pipeline/data/ricksteves/normalized/*.jsonl'):
    with open(f) as fh:
        entities.extend([json.loads(line) for line in fh])
print(f'Total: {len(entities)}')
print(f'With t_any_countries: {sum(1 for e in entities if e.get(\"t_any_countries\"))}')
print(f'With t_any_regions: {sum(1 for e in entities if e.get(\"t_any_regions\"))}')
print(f'With t_any_cities: {sum(1 for e in entities if e.get(\"t_any_cities\"))}')
print(f'Schema v2: {sum(1 for e in entities if e.get(\"t_schema_version\") == 2)}')
print(f'Unique countries: {sorted(set(c for e in entities for c in e.get(\"t_any_countries\", [])))}')
"
```

**Success criteria:** All entities have t_any_countries. Multiple countries represented. Schema version = 2.

---

## Step 5: Geocode Entities (phase5_geocode.py)

```fish
python3 pipeline/scripts/phase5_geocode.py --pipeline ricksteves --limit 30
```

**Nominatim international geocoding notes:**
- European landmarks generally geocode well (Uffizi Gallery, Notre-Dame, Colosseum)
- Use English names for queries: "Uffizi Gallery, Florence, Italy" not "Galleria degli Uffizi"
- Rate limit: 1 req/sec

**Success criteria:** >= 50% geocoded via Nominatim. The enrichment step will backfill the rest.

---

## Step 6: Enrich Entities (phase6_enrich.py)

```fish
python3 pipeline/scripts/phase6_enrich.py --pipeline ricksteves --limit 30
```

**Google Places international notes:**
- Google Places works worldwide. European landmarks should have high match rates.
- The API returns coordinates - use these to backfill t_any_coordinates for entities Nominatim missed.

**After enrichment, run coordinate backfill:**

```fish
python3 -c "
import json, glob
# Check how many entities now have coordinates (from either source)
entities = []
for f in glob.glob('pipeline/data/ricksteves/enriched/*.jsonl'):
    with open(f) as fh:
        entities.extend([json.loads(line) for line in fh])
with_coords = sum(1 for e in entities if e.get('t_any_coordinates'))
print(f'Entities with coordinates: {with_coords}/{len(entities)} ({100*with_coords//len(entities)}%)')
"
```

**Success criteria:** >= 70% enriched. Coordinate coverage >= 70% (combining Nominatim + Google Places).

---

## Step 7: Load to Staging Firestore (phase7_load.py)

```fish
python3 pipeline/scripts/phase7_load.py --pipeline ricksteves --database staging
```

**CRITICAL: Cross-pipeline validation after load.**

This is the moment of truth. Both CalGold AND RickSteves data now coexist in staging.

```fish
python3 -c "
from google.cloud import firestore
db = firestore.Client(database='staging')

# Total entity count across all pipelines
all_docs = list(db.collection('locations').stream())
print(f'Total entities in staging: {len(all_docs)}')

# Per-pipeline counts
calgold = list(db.collection('locations').where('t_log_type', '==', 'calgold').stream())
ricksteves = list(db.collection('locations').where('t_log_type', '==', 'ricksteves').stream())
print(f'CalGold: {len(calgold)}')
print(f'RickSteves: {len(ricksteves)}')

# CROSS-PIPELINE QUERY: keyword search across both datasets
results = list(db.collection('locations').where('t_any_keywords', 'array_contains', 'church').stream())
pipelines_hit = set(d.to_dict().get('t_log_type') for d in results)
print(f'Keyword \"church\": {len(results)} results from pipelines: {pipelines_hit}')

# NEW FIELD: t_any_countries query
us = list(db.collection('locations').where('t_any_countries', 'array_contains', 'us').stream())
italy = list(db.collection('locations').where('t_any_countries', 'array_contains', 'italy').stream())
print(f'Country \"us\": {len(us)} (should be CalGold entities)')
print(f'Country \"italy\": {len(italy)} (should be RickSteves entities)')

# CalGold backfill verification
calgold_v2 = sum(1 for d in calgold if d.to_dict().get('t_schema_version') == 2)
print(f'CalGold on schema v2: {calgold_v2}/{len(calgold)}')
"
```

**Success criteria:**
- Both pipelines have entities in staging
- Cross-pipeline keyword query returns results from BOTH pipelines
- `t_any_countries` queries work: "us" returns CalGold, "italy" returns RickSteves
- CalGold entities backfilled to schema v2
- Cloud Function search returns results from both pipelines

---

## Step 8: Post-Flight Verification

### Tier 1 - Standard Health

```
[ ] All 7 phase scripts completed without fatal errors
[ ] Checkpoint files exist for all phases
[ ] No API keys in any repo file (grep -r "AIzaSy" in repo root)
[ ] Staging Firestore has RickSteves entities
[ ] Pipeline registry (pipelines/ricksteves) updated
[ ] CLAUDE.md has security section
[ ] Changelog entry written
```

### Tier 2 - Phase 1 Functional Playbook

```
[ ] >= 28 of 30 videos acquired
[ ] >= 27 of 30 videos transcribed
[ ] >= 25 of 30 videos extracted
[ ] Total unique normalized entities >= 40
[ ] All entities have t_any_names populated
[ ] All entities have t_any_countries populated (SCHEMA V2 CRITICAL)
[ ] All entities have t_any_cities populated (>= 80%)
[ ] All t_any_* values lowercase
[ ] t_schema_version = 2 on all new entities
[ ] >= 50% geocoded via Nominatim
[ ] >= 70% geocoded after Google Places coordinate backfill
[ ] >= 60% enriched via Google Places
[ ] Multiple countries in t_any_countries (not all the same)
[ ] CROSS-PIPELINE: keyword query returns results from both calgold AND ricksteves
[ ] CROSS-PIPELINE: t_any_countries "us" returns CalGold entities
[ ] CROSS-PIPELINE: t_any_countries "italy" (or other) returns RickSteves entities
[ ] CalGold entities backfilled with t_any_countries: ["us"] and t_schema_version: 2
[ ] Cloud Function search returns results from both pipelines
[ ] No API keys anywhere in repo (final grep scan)
```

---

## Step 9: Produce Artifacts

### 9.1 Build Log

Write `docs/ricksteves-build-v1.7.md` - session transcript with per-phase metrics.

### 9.2 Report

Write `docs/ricksteves-report-v1.7.md`:
- Summary metrics (entities, countries, geocoded, enriched)
- Cross-pipeline validation results
- Schema v2 validation
- Extraction prompt quality assessment
- Recommendation for Phase 2

### 9.3 Changelog

Append to `docs/ricksteves-changelog-v1.7.md`:
```
**v1.7 (RickSteves Phase 1 - Discovery)**
- 30-video discovery batch: {acquired}/{transcribed}/{extracted}
- {N} unique destinations across {N} countries
- Thompson Schema v2 validated: t_any_countries, t_any_regions populated
- Geocoding: {N}% (Nominatim + Google Places backfill)
- Enrichment: {N}% via Google Places
- Cross-pipeline queries validated: keyword, country, and geohash queries
  return results from both CalGold and RickSteves
- CalGold entities backfilled to schema v2
- {N} interventions
- Security: zero API keys in repo (verified)
```

---

## Estimated Timeline

| Phase | Duration | Notes |
|-------|----------|-------|
| Step 0 (config + migrations) | 10-15 min | Schema v2, google.genai, geocode fix, backfill |
| Step 1 (acquire 30 videos) | 10-15 min | Network-bound. Mix of short clips and full episodes. |
| Step 2 (transcribe 30 videos) | 15-30 min | CUDA-bound. Short clips are fast. |
| Step 3 (extract 30 videos) | 5-10 min | Gemini Flash API. |
| Step 4 (normalize) | 1 min | Local Python. |
| Step 5 (geocode) | 5-10 min | Nominatim 1 req/sec. |
| Step 6 (enrich) | 5-10 min | Google Places API. |
| Step 7 (load + cross-pipeline validation) | 5 min | Firestore writes + validation queries. |
| Step 8 (post-flight) | 5 min | Validation + security scan. |
| Step 9 (artifacts) | 5 min | Write build/report/changelog. |
| **Total** | **~60-90 min** | Similar to CalGold Phase 1. |

---

## Environment Variables Required

```fish
# Verify these are set (print SET/NOT SET only)
echo "GEMINI_API_KEY: $(test -n "$GEMINI_API_KEY" && echo SET || echo NOT SET)"
echo "GOOGLE_PLACES_API_KEY: $(test -n "$GOOGLE_PLACES_API_KEY" && echo SET || echo NOT SET)"
echo "GOOGLE_APPLICATION_CREDENTIALS: $(test -f "$GOOGLE_APPLICATION_CREDENTIALS" && echo SET || echo NOT SET)"
```
