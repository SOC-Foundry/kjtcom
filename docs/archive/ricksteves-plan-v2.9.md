# RickSteves - Plan v2.9 (Phase 2 - Calibration)

**Phase:** 2 - Calibration (videos 31-60 through full pipeline)
**Executor:** Gemini CLI (`gemini --sandbox=none`)
**Machine:** NZXTcos (Intel i9-13900K, RTX 2080 SUPER, 64 GB DDR4, CachyOS)
**Goal:** Process videos 31-60 from RickSteves filtered playlist. Validate dedup across Phase 1 + Phase 2. Maintain 80%+ geocoding and enrichment. Zero interventions. Update all 4 artifacts.

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
5. DATABASE: Load to "staging" database only. NEVER write to "(default)".
6. LIMITS: Process videos 31-60 only (next 30 after Phase 1). Use --limit 60.
7. SECURITY: NEVER write API keys into ANY file. Print "SET" or "NOT SET" only.
8. SHELL: All commands in fish. This machine runs fish natively.
9. ARTIFACTS: Before completing, update ALL 4 files:
   - docs/ricksteves-build-v2.9.md
   - docs/ricksteves-report-v2.9.md
   - docs/kjtcom-changelog.md (APPEND entry - never overwrite previous entries)
   - README.md (update project status table and changelog section)
   If any re-run, fix, or backfill changes metrics, update ALL 4 again.
10. INSTALL.FISH: If ANY new package is installed (pip, npm, pacman, yay),
    update docs/install.fish to reflect the current working state.
```

---

## Pre-Flight Checklist

```
[ ] v1.7 RickSteves artifacts in docs/archive/
[ ] ricksteves-design-v2.9.md in docs/
[ ] ricksteves-plan-v2.9.md in docs/ (this file)
[ ] GEMINI.md updated with read order, security, G2, artifact rules
[ ] git status clean

[ ] Shell: fish confirmed (echo $FISH_VERSION returns a value)

[ ] Environment variables (print SET/NOT SET only):
    [ ] GEMINI_API_KEY is SET
    [ ] GOOGLE_PLACES_API_KEY is SET
    [ ] GOOGLE_APPLICATION_CREDENTIALS is SET and file exists
    [ ] LD_LIBRARY_PATH is SET and includes cuda paths (GOTCHA G2)

[ ] API endpoint validation (GOTCHA G16):
    python3 -c "
    import os, urllib.request, json
    key = os.environ.get('GOOGLE_PLACES_API_KEY', '')
    url = 'https://places.googleapis.com/v1/places:searchText'
    req = urllib.request.Request(url,
        data=json.dumps({'textQuery': 'Colosseum Rome', 'maxResultCount': 1}).encode(),
        headers={'Content-Type': 'application/json', 'X-Goog-Api-Key': key,
                 'X-Goog-FieldMask': 'places.displayName'})
    try:
        resp = urllib.request.urlopen(req)
        print('PLACES API: VALID')
    except Exception as e:
        print(f'PLACES API: INVALID - {e}')
    "

[ ] firebase use kjtcom-c78cd succeeds
[ ] nvidia-smi shows RTX 2080 SUPER
[ ] python3 -c "import faster_whisper" succeeds
[ ] python3 -c "import google.genai" succeeds (NOT google.generativeai)
[ ] Staging Firestore has:
    [ ] CalGold entities (from Phase 1 + Phase 2)
    [ ] 200 RickSteves entities (from Phase 1)
[ ] Disk space >= 20 GB free
[ ] RickSteves Phase 1 checkpoint files exist in pipeline/data/ricksteves/
```

---

## Step 0: Archive Previous Docs + Update GEMINI.md

```fish
cd ~/dev/projects/kjtcom

# Archive previous iteration docs (if not already archived)
mv docs/ricksteves-design-v1.7.md docs/archive/ 2>/dev/null
mv docs/ricksteves-plan-v1.7.md docs/archive/ 2>/dev/null
mv docs/ricksteves-build-v1.7.md docs/archive/ 2>/dev/null
mv docs/ricksteves-report-v1.7.md docs/archive/ 2>/dev/null
mv docs/ricksteves-changelog-v1.7.md docs/archive/ 2>/dev/null
mv docs/calgold-design-v2.8.md docs/archive/ 2>/dev/null
mv docs/calgold-plan-v2.8.md docs/archive/ 2>/dev/null
mv docs/calgold-build-v2.8.md docs/archive/ 2>/dev/null
mv docs/calgold-report-v2.8.md docs/archive/ 2>/dev/null

# Verify v2.9 docs in place
ls docs/ricksteves-design-v2.9.md docs/ricksteves-plan-v2.9.md
```

**Success criteria:** Only v2.9 docs in docs/ (plus kjtcom-changelog.md, install.fish, README.md). All previous versions in archive.

---

## Step 1: Acquire Audio (videos 31-60)

```fish
python3 pipeline/scripts/phase1_acquire.py --pipeline ricksteves --limit 60
```

Checkpoints skip the first 30 (already downloaded in Phase 1). Downloads videos 31-60.

**Expected:** ~30 new downloads. Mix of Travel Bites (short) and full episodes (longer). Some may be unavailable.

**Success criteria:** >= 25 new videos downloaded.

---

## Step 2: Transcribe Audio

```fish
# GOTCHA G2: Verify LD_LIBRARY_PATH before transcription
echo $LD_LIBRARY_PATH
# Must be non-empty. If empty: source ~/.config/fish/config.fish

python3 pipeline/scripts/phase2_transcribe.py --pipeline ricksteves --limit 60
```

Skips Phase 1 transcriptions via checkpoint.

**Success criteria:** >= 24 new transcripts.

---

## Step 3: Extract Entities

```fish
python3 pipeline/scripts/phase3_extract.py --pipeline ricksteves --limit 60
```

Uses google.genai SDK. Reads ricksteves extraction_prompt.md. Skips Phase 1 extractions.

**Expected:** 150-250 new raw entities from 30 videos (7+ entities/video average from Phase 1).

**Success criteria:** >= 22 new extractions. Total new raw entities >= 100.

---

## Step 4: Normalize Entities

```fish
python3 pipeline/scripts/phase4_normalize.py --pipeline ricksteves --limit 60
```

**Validation:**
```fish
python3 -c "
import json, glob
entities = []
for f in glob.glob('pipeline/data/ricksteves/normalized/*.jsonl'):
    with open(f) as fh:
        entities.extend([json.loads(line) for line in fh])
multi_visit = [e for e in entities if len(e.get('source', {}).get('visits', [])) > 1]
print(f'Total entities: {len(entities)}')
print(f'With t_any_countries: {sum(1 for e in entities if e.get(\"t_any_countries\"))}')
print(f'Unique countries: {sorted(set(c for e in entities for c in e.get(\"t_any_countries\", [])))}')
print(f'Entities with multiple visits (dedup merges): {len(multi_visit)}')
for e in multi_visit[:5]:
    print(f'  {e[\"t_any_names\"][0]}: {len(e[\"source\"][\"visits\"])} visits')
print(f'Schema v2: {sum(1 for e in entities if e.get(\"t_schema_version\") == 2)}')
"
```

**Success criteria:** All entities on schema v2. All have t_any_countries. Dedup merge count reported. New countries beyond Phase 1's 23 expected.

---

## Step 5: Geocode Entities

```fish
python3 pipeline/scripts/phase5_geocode.py --pipeline ricksteves --limit 60
```

International geocoding with country field in Nominatim query.

**Success criteria:** >= 60% of new entities geocoded via Nominatim.

---

## Step 6: Enrich Entities

```fish
python3 pipeline/scripts/phase6_enrich.py --pipeline ricksteves --limit 60
```

Google Places enrichment + coordinate backfill for Nominatim misses.

**If enrichment fails with 400 (API key invalid):** The fish session has the correct key. If running in a subshell that doesn't inherit fish env, source the config first:
```fish
source ~/.config/fish/config.fish
python3 pipeline/scripts/phase6_enrich.py --pipeline ricksteves --limit 60
```

**Validation:**
```fish
python3 -c "
import json, glob
entities = []
for f in glob.glob('pipeline/data/ricksteves/enriched/*.jsonl'):
    with open(f) as fh:
        entities.extend([json.loads(line) for line in fh])
with_coords = sum(1 for e in entities if e.get('t_any_coordinates'))
with_enrichment = sum(1 for e in entities if e.get('t_enrichment', {}).get('google_places'))
print(f'Total entities: {len(entities)}')
print(f'With coordinates: {with_coords} ({100*with_coords//max(len(entities),1)}%)')
print(f'With enrichment: {with_enrichment} ({100*with_enrichment//max(len(entities),1)}%)')
"
```

**Success criteria:** >= 80% geocoded (Nominatim + Places backfill). >= 80% enriched.

---

## Step 7: Load to Staging Firestore

```fish
python3 pipeline/scripts/phase7_load.py --pipeline ricksteves --database staging
```

**Cross-pipeline validation:**
```fish
python3 -c "
from google.cloud import firestore
db = firestore.Client(database='staging')

calgold = list(db.collection('locations').where('t_log_type', '==', 'calgold').stream())
ricksteves = list(db.collection('locations').where('t_log_type', '==', 'ricksteves').stream())
print(f'CalGold: {len(calgold)}')
print(f'RickSteves: {len(ricksteves)} (was 200 in Phase 1)')
print(f'Total: {len(calgold) + len(ricksteves)}')

# Country distribution
countries = {}
for d in ricksteves:
    for c in d.to_dict().get('t_any_countries', []):
        countries[c] = countries.get(c, 0) + 1
print(f'RickSteves countries ({len(countries)}): {dict(sorted(countries.items(), key=lambda x: -x[1])[:10])}')

# Cross-pipeline
results = list(db.collection('locations').where('t_any_keywords', 'array_contains', 'museum').stream())
pipelines = set(d.to_dict().get('t_log_type') for d in results)
print(f'Keyword \"museum\": {len(results)} results from {pipelines}')

# Dedup - multi-visit entities
multi = sum(1 for d in ricksteves if len(d.to_dict().get('source', {}).get('visits', [])) > 1)
print(f'RickSteves entities with multiple visits: {multi}')
"
```

**Success criteria:**
- RickSteves entity count increased from 200
- Cross-pipeline queries still return both pipelines
- Country count >= 23 (should grow)
- Pipeline registry updated

---

## Step 8: Post-Flight Verification

### Tier 1 - Standard Health

```
[ ] All 7 phase scripts completed without fatal errors
[ ] Checkpoint files exist for all phases
[ ] No API keys in any repo file (grep -rn "AIzaSy" in repo)
[ ] Staging Firestore RickSteves entity count > 200
[ ] CalGold entities unchanged
[ ] Pipeline registry updated
[ ] GEMINI.md has shell + security + G2 + artifact sections
```

### Tier 2 - Phase 2 Functional Playbook

```
[ ] >= 25 new videos acquired
[ ] >= 24 new videos transcribed
[ ] >= 22 new videos extracted
[ ] New entities on schema v2 with t_any_countries
[ ] Dedup merge count reported (entities with multiple visits)
[ ] >= 80% geocoded (Nominatim + Places backfill)
[ ] >= 80% enriched via Google Places
[ ] Cross-pipeline keyword query returns both pipelines
[ ] All t_any_* values lowercase
[ ] Zero API keys in repo (final scan)
[ ] docs/install.fish updated if any new packages installed
```

---

## Step 9: Produce Artifacts

**MANDATORY: Update ALL 4 files before completing.**

### 9.1 Build Log
Write `docs/ricksteves-build-v2.9.md`

### 9.2 Report
Write `docs/ricksteves-report-v2.9.md` with:
- Phase 1 vs Phase 2 comparison
- Dedup merge results
- Cumulative metrics (total RickSteves entities, total platform entities, country count)
- Gemini CLI execution assessment (did it match Claude Code quality?)
- Recommendation for Phase 3

### 9.3 Unified Changelog
**APPEND** to `docs/kjtcom-changelog.md`:
```
**v2.9 (RickSteves Phase 2 - Calibration)**
- Videos 31-60 processed via Gemini CLI (first Gemini execution on kjtcom)
- {N} new entities, {N} total RickSteves entities across {N} countries
- Geocoding: {N}% (Nominatim + Places backfill)
- Enrichment: {N}% via Google Places
- Dedup merges: {N} entities with multiple visits
- {N} interventions
- Total platform: {N} entities ({N} CalGold + {N} RickSteves)
```

### 9.4 README.md
Update project status table and changelog section.

---

## Estimated Timeline

| Phase | Duration | Notes |
|-------|----------|-------|
| Step 0 (archive + GEMINI.md) | 2 min | File moves |
| Step 1 (acquire ~30 videos) | 10-15 min | Skips Phase 1 via checkpoint |
| Step 2 (transcribe ~30 videos) | 15-30 min | CUDA. G2 check first. |
| Step 3 (extract ~30 videos) | 5-10 min | Gemini Flash API |
| Step 4 (normalize) | 1 min | Dedup validation |
| Step 5 (geocode) | 5-10 min | Nominatim with country field |
| Step 6 (enrich) | 5-10 min | Google Places + coordinate backfill |
| Step 7 (load + validation) | 5 min | Cross-pipeline queries |
| Step 8 (post-flight) | 3 min | Validation + security scan |
| Step 9 (artifacts - ALL 4 files) | 5 min | Build, report, changelog, README |
| **Total** | **~55-85 min** |
