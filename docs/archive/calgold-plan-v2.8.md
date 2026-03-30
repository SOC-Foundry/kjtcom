# CalGold - Plan v2.8 (Phase 2 - Calibration)

**Phase:** 2 - Calibration (videos 31-60 through full pipeline + Phase 1 re-enrichment)
**Executor:** Claude Code (YOLO mode, Opus)
**Machine:** NZXTcos (Intel i9-13900K, RTX 2080 SUPER, 64 GB DDR4, CachyOS)
**Goal:** Process videos 31-60 from CalGold playlist. Re-enrich Phase 1 entities with Google Places coordinate backfill. Validate dedup merges across both batches. Achieve zero interventions. Update all artifacts.

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
6. LIMITS: Process videos 31-60 only (next 30 after Phase 1).
7. SECURITY: NEVER write API keys into ANY file. Print "SET" or "NOT SET" only.
8. SHELL: All commands in fish. Use fish syntax. No bash.
9. ARTIFACTS: Before completing, update ALL 4 files:
   - docs/calgold-build-v2.8.md
   - docs/calgold-report-v2.8.md
   - docs/kjtcom-changelog.md (APPEND entry - never overwrite previous entries)
   - README.md (update project status table and changelog section)
   If any re-run, fix, or backfill changes metrics, update ALL 4 again.
```

---

## Pre-Flight Checklist

```
[ ] v1.6 CalGold artifacts in docs/archive/
[ ] v1.7 RickSteves artifacts in docs/archive/
[ ] calgold-design-v2.8.md in docs/
[ ] calgold-plan-v2.8.md in docs/ (this file)
[ ] CLAUDE.md updated with:
    [ ] Read order points to calgold v2.8 docs
    [ ] Security section present
    [ ] Shell section mandates fish
    [ ] Gotcha G2 (CUDA LD_LIBRARY_PATH) warning present
    [ ] Artifact rules present (4 files, unified changelog)
[ ] git status clean

[ ] Shell: fish confirmed (echo $FISH_VERSION must return a value)
[ ] Shell: claude config set preferredShell fish (run if not already set)

[ ] Environment variables (print SET/NOT SET only):
    [ ] GEMINI_API_KEY is SET
    [ ] GOOGLE_PLACES_API_KEY is SET
    [ ] GOOGLE_APPLICATION_CREDENTIALS is SET and file exists
    [ ] LD_LIBRARY_PATH is SET and includes cuda/cublas/cudnn paths (GOTCHA G2)

[ ] API endpoint validation (NOT just env var check - GOTCHA G16):
    fish -c 'python3 -c "
import os, urllib.request, json
key = os.environ.get(\"GOOGLE_PLACES_API_KEY\", \"\")
url = \"https://places.googleapis.com/v1/places:searchText\"
req = urllib.request.Request(url,
    data=json.dumps({\"textQuery\": \"Yosemite\", \"maxResultCount\": 1}).encode(),
    headers={\"Content-Type\": \"application/json\", \"X-Goog-Api-Key\": key,
             \"X-Goog-FieldMask\": \"places.displayName\"})
try:
    resp = urllib.request.urlopen(req)
    print(\"PLACES API: VALID\")
except Exception as e:
    print(f\"PLACES API: INVALID - {e}\")
"'

[ ] firebase use kjtcom-c78cd succeeds
[ ] nvidia-smi shows RTX 2080 SUPER
[ ] python3 -c "import faster_whisper" succeeds
[ ] Staging Firestore has:
    [ ] 56 CalGold entities (from Phase 1)
    [ ] 200 RickSteves entities (from v1.7)
    [ ] pipelines/calgold document exists
[ ] Disk space >= 10 GB free
```

---

## Step 0: Archive Previous Docs + Update CLAUDE.md

```fish
cd ~/dev/projects/kjtcom

# Archive v1.6 and v1.7 docs
mv docs/calgold-design-v1.6.md docs/archive/
mv docs/calgold-plan-v1.6.md docs/archive/
mv docs/calgold-build-v1.6.md docs/archive/
mv docs/calgold-report-v1.6.md docs/archive/
mv docs/ricksteves-design-v1.7.md docs/archive/
mv docs/ricksteves-plan-v1.7.md docs/archive/
mv docs/ricksteves-build-v1.7.md docs/archive/
mv docs/ricksteves-report-v1.7.md docs/archive/
mv docs/ricksteves-changelog-v1.7.md docs/archive/

# Verify v2.8 docs in place
ls docs/calgold-design-v2.8.md docs/calgold-plan-v2.8.md
```

Update CLAUDE.md with full shell, security, G2, and artifact rules per the template Kyle provided.

**Success criteria:** Only v2.8 docs in docs/ (plus kjtcom-changelog.md and README.md). All previous versions in archive.

---

## Step 1: Acquire Audio (videos 31-60)

```fish
python3 pipeline/scripts/phase1_acquire.py --pipeline calgold --limit 60
```

The script uses checkpoints - it will skip the first 30 (already downloaded) and download videos 31-60.

**Expected:** ~30 new downloads. Some may be unavailable (private/terminated like Phase 1's 11 skips). The script continues past failures.

**Success criteria:** >= 25 new videos downloaded (total ~55-60 in audio/).

---

## Step 2: Transcribe Audio

```fish
python3 pipeline/scripts/phase2_transcribe.py --pipeline calgold --limit 60
```

Skips already-transcribed Phase 1 files. Transcribes only new Phase 2 audio.

**GOTCHA G2 CHECK:** Before this step, verify LD_LIBRARY_PATH:
```fish
echo $LD_LIBRARY_PATH
# Must be non-empty and include cuda paths
# If empty, source fish config: source ~/.config/fish/config.fish
```

**Success criteria:** >= 24 new transcripts. Spot-check 2 for quality.

---

## Step 3: Extract Entities

```fish
python3 pipeline/scripts/phase3_extract.py --pipeline calgold --limit 60
```

Uses google.genai (migrated in v1.7). Skips Phase 1 extractions via checkpoint.

**Expected:** ~25-30 new extractions. 1.9 entities/video average (CalGold pattern).

**Success criteria:** >= 22 new extractions. Total new raw entities >= 30.

---

## Step 4: Normalize Entities

```fish
python3 pipeline/scripts/phase4_normalize.py --pipeline calgold --limit 60
```

**Critical for Phase 2:** This is where dedup should trigger. If any Phase 2 entities match Phase 1 entities by name + city, the visits arrays should merge.

**Validation:**
```fish
python3 -c "
import json, glob
entities = []
for f in glob.glob('pipeline/data/calgold/normalized/*.jsonl'):
    with open(f) as fh:
        entities.extend([json.loads(line) for line in fh])
multi_visit = [e for e in entities if len(e.get('source', {}).get('visits', [])) > 1]
print(f'Total entities: {len(entities)}')
print(f'Entities with multiple visits (dedup merges): {len(multi_visit)}')
for e in multi_visit[:5]:
    print(f'  {e[\"t_any_names\"][0]}: {len(e[\"source\"][\"visits\"])} visits')
print(f'Schema v2: {sum(1 for e in entities if e.get(\"t_schema_version\") == 2)}')
print(f'With t_any_countries: {sum(1 for e in entities if e.get(\"t_any_countries\"))}')
"
```

**Success criteria:** All entities on schema v2. All have t_any_countries: ["us"]. Dedup merge count reported (even if 0 - that's valid data).

---

## Step 5: Geocode Entities

```fish
python3 pipeline/scripts/phase5_geocode.py --pipeline calgold --limit 60
```

Now includes country field in Nominatim query (improvement from v1.7).

**Success criteria:** >= 50% of NEW entities geocoded via Nominatim.

---

## Step 6: Enrich Entities + Re-Enrich Phase 1

This is the key Phase 2 step. Two operations:

### 6.1 Enrich Phase 2 entities

```fish
python3 pipeline/scripts/phase6_enrich.py --pipeline calgold --limit 60
```

### 6.2 Re-enrich Phase 1 entities (coordinate backfill)

Phase 1 entities were enriched but did NOT get the Google Places coordinate backfill (added in v1.7). Clear the enrichment checkpoint and re-run on ALL entities:

```fish
rm pipeline/data/calgold/.checkpoint_enrich.json
python3 pipeline/scripts/phase6_enrich.py --pipeline calgold
```

This re-enriches all ~90+ entities. Phase 1 entities that Nominatim missed (32 of 57) should now get coordinates from Google Places.

**Validation:**
```fish
python3 -c "
import json, glob
entities = []
for f in glob.glob('pipeline/data/calgold/enriched/*.jsonl'):
    with open(f) as fh:
        entities.extend([json.loads(line) for line in fh])
with_coords = sum(1 for e in entities if e.get('t_any_coordinates'))
with_enrichment = sum(1 for e in entities if e.get('t_enrichment', {}).get('google_places'))
print(f'Total entities: {len(entities)}')
print(f'With coordinates (Nominatim + Places backfill): {with_coords} ({100*with_coords//max(len(entities),1)}%)')
print(f'With Google Places enrichment: {with_enrichment} ({100*with_enrichment//max(len(entities),1)}%)')
"
```

**Success criteria:** >= 80% geocoded (Nominatim + Places backfill combined). >= 80% enriched.

---

## Step 7: Load to Staging Firestore

```fish
rm pipeline/data/calgold/.checkpoint_load.json
python3 pipeline/scripts/phase7_load.py --pipeline calgold --database staging
```

Clear the load checkpoint to re-load ALL CalGold entities (Phase 1 re-enriched + Phase 2 new).

**Cross-pipeline validation:**
```fish
python3 -c "
from google.cloud import firestore
db = firestore.Client(database='staging')

# Counts
calgold = list(db.collection('locations').where('t_log_type', '==', 'calgold').stream())
ricksteves = list(db.collection('locations').where('t_log_type', '==', 'ricksteves').stream())
print(f'CalGold: {len(calgold)} (was 56 in Phase 1)')
print(f'RickSteves: {len(ricksteves)} (should still be 200)')
print(f'Total: {len(calgold) + len(ricksteves)}')

# CalGold geocoding rate
with_coords = sum(1 for d in calgold if d.to_dict().get('t_any_coordinates'))
print(f'CalGold with coordinates: {with_coords}/{len(calgold)} ({100*with_coords//max(len(calgold),1)}%)')

# CalGold enrichment rate
with_places = sum(1 for d in calgold if d.to_dict().get('t_enrichment', {}).get('google_places'))
print(f'CalGold with Places enrichment: {with_places}/{len(calgold)} ({100*with_places//max(len(calgold),1)}%)')

# Schema v2
v2 = sum(1 for d in calgold if d.to_dict().get('t_schema_version') == 2)
print(f'CalGold on schema v2: {v2}/{len(calgold)}')

# Cross-pipeline keyword
results = list(db.collection('locations').where('t_any_keywords', 'array_contains', 'park').stream())
pipelines = set(d.to_dict().get('t_log_type') for d in results)
print(f'Keyword \"park\": {len(results)} results from {pipelines}')

# Dedup check - entities with multiple visits
multi = sum(1 for d in calgold if len(d.to_dict().get('source', {}).get('visits', [])) > 1)
print(f'CalGold entities with multiple visits (dedup merges): {multi}')
"
```

**Success criteria:**
- CalGold entity count increased from 56 (new entities from Phase 2)
- CalGold geocoding >= 80% (up from 43% in Phase 1)
- CalGold enrichment >= 80%
- RickSteves entities unchanged (still 200)
- Cross-pipeline queries still work
- All CalGold entities on schema v2
- Pipeline registry updated

---

## Step 8: Post-Flight Verification

### Tier 1 - Standard Health

```
[ ] All 7 phase scripts completed without fatal errors
[ ] Checkpoint files exist for all phases
[ ] No API keys in any repo file (grep -rn "AIzaSy" in repo root)
[ ] Staging Firestore CalGold entity count > 56 (increased from Phase 1)
[ ] RickSteves entities unchanged at 200
[ ] Pipeline registry updated with new entity count
[ ] CLAUDE.md has shell + security + G2 + artifact sections
```

### Tier 2 - Phase 2 Functional Playbook

```
[ ] >= 25 new videos acquired (videos 31-60)
[ ] >= 24 new videos transcribed
[ ] >= 22 new videos extracted
[ ] New entities normalized with schema v2 (t_any_countries: ["us"])
[ ] Dedup merge count reported
[ ] CalGold geocoding >= 80% (Nominatim + Places backfill)
[ ] CalGold enrichment >= 80% via Google Places
[ ] Phase 1 entities re-enriched with coordinate backfill
[ ] Cross-pipeline keyword query returns both CalGold and RickSteves
[ ] All t_any_* values lowercase
[ ] Zero API keys in repo (final grep scan)
```

---

## Step 9: Produce Artifacts

**MANDATORY: Update ALL 4 files before completing.**

### 9.1 Build Log
Write `docs/calgold-build-v2.8.md`

### 9.2 Report
Write `docs/calgold-report-v2.8.md` with:
- Phase 1 vs Phase 2 comparison (entity yield, geocoding, enrichment)
- Dedup merge results
- Re-enrichment results (how many Phase 1 entities got coordinate backfill)
- Cumulative metrics (total CalGold entities, total platform entities)
- Recommendation for Phase 3

### 9.3 Unified Changelog
**APPEND** to `docs/kjtcom-changelog.md`:
```
**v2.8 (CalGold Phase 2 - Calibration)**
- Videos 31-60 processed: {acquired}/{transcribed}/{extracted}
- {N} new entities, {N} total CalGold entities after dedup
- Phase 1 re-enriched: coordinate backfill pushed geocoding from 43% to {N}%
- Enrichment: {N}% via Google Places
- Dedup merges: {N} entities with multiple visits
- {N} interventions
- Total platform: {N} entities ({N} CalGold + 200 RickSteves) across {N} countries
```

### 9.4 README.md
Update project status table and changelog section.

---

## Estimated Timeline

| Phase | Duration | Notes |
|-------|----------|-------|
| Step 0 (archive + CLAUDE.md) | 2 min | File moves |
| Step 1 (acquire ~30 videos) | 10-15 min | Skips Phase 1 via checkpoint |
| Step 2 (transcribe ~30 videos) | 15-30 min | CUDA. G2 check first. |
| Step 3 (extract ~30 videos) | 5-10 min | google.genai + Gemini Flash |
| Step 4 (normalize) | 1 min | Dedup validation |
| Step 5 (geocode) | 3-5 min | Nominatim with country field |
| Step 6 (enrich + re-enrich Phase 1) | 5-10 min | Full re-run on all entities |
| Step 7 (load + validation) | 5 min | Re-load all CalGold entities |
| Step 8 (post-flight) | 3 min | Validation queries |
| Step 9 (artifacts - ALL 4 files) | 5 min | Build, report, changelog, README |
| **Total** | **~55-85 min** |
