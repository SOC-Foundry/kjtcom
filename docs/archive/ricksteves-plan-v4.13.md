# RickSteves - Plan v4.13 (Phase 4 - Validation + Schema v3)

**Pipeline:** ricksteves
**Phase:** 4 (Validation)
**Iteration:** 13 (global counter)
**Batch:** Videos 121-150 (30 new) + Re-extraction of ALL 150
**Date:** March 2026

---

## Section A: Gemini CLI Execution (Schema Prep + Phases 1-5)

**Launch:** `gemini --yolo`
**First message:** "Read GEMINI.md, then execute Section A of docs/ricksteves-plan-v4.13.md. This iteration includes schema v3 migration for RickSteves. Start with Step 0, then Step 0.5 (schema changes), then phases 1-5. Stop at handoff checkpoint."

### Step 0: Pre-Flight Verification

```
CHECKLIST:
[ ] Previous docs archived: docs/archive/ contains v4.12 artifacts
[ ] Current docs in place: docs/ricksteves-design-v4.13.md and docs/ricksteves-plan-v4.13.md exist
[ ] GEMINI.md updated with v4.13 references
[ ] Git status clean
[ ] API keys (SET/NOT SET only, NEVER cat config.fish):
    - fish -c "test -n \$GEMINI_API_KEY && echo SET || echo NOT SET"
    - fish -c "test -n \$GOOGLE_PLACES_API_KEY && echo SET || echo NOT SET"
    - fish -c "test -n \$GOOGLE_APPLICATION_CREDENTIALS && echo SET || echo NOT SET"
[ ] CUDA visible: fish -c "nvidia-smi | head -5"
[ ] LD_LIBRARY_PATH set: fish -c "echo \$LD_LIBRARY_PATH"
[ ] Disk space: df -h /home | tail -1 (need >50GB free)
[ ] Python deps: fish -c "python3 -c 'import faster_whisper; import google.genai; print(\"OK\")'"
[ ] Places API valid: fish -c "curl -s 'https://places.googleapis.com/v1/places:searchText' -H 'Content-Type: application/json' -H 'X-Goog-Api-Key: '\$GOOGLE_PLACES_API_KEY -H 'X-Goog-FieldMask: places.displayName' -d '{\"textQuery\": \"Colosseum Rome\"}' | head -3"
[ ] Current counts: fish -c "command ls pipeline/data/ricksteves/audio/*.mp3 | wc -l" (expect 120)
[ ] Current transcripts: fish -c "command ls pipeline/data/ricksteves/transcripts/*.json | wc -l" (expect 120)
```

### Step 0.5: Schema v3 Config Changes

**Note:** phase4_normalize.py (continent lookup) and phase5_geocode.py (county parsing) were already enhanced in v4.12. Only RickSteves-specific config files need updating.

#### 0.5a: Update schema.json

Edit `pipeline/config/ricksteves/schema.json` to add the 7 new field mappings:

```json
{
  "t_any_actors": "actors",
  "t_any_roles": "roles",
  "t_any_shows": "shows",
  "t_any_cuisines": "cuisines",
  "t_any_dishes": "dishes",
  "t_any_eras": "eras",
  "t_any_continents": "continents"
}
```

Also update `t_schema_version` default to 3.

**Verify:** `fish -c "cat pipeline/config/ricksteves/schema.json | python3 -c 'import json,sys; d=json.load(sys.stdin); print([k for k in d if \"actor\" in k or \"cuisine\" in k or \"dish\" in k or \"era\" in k or \"continent\" in k or \"role\" in k or \"show\" in k])'"` -> should show all 7 new keys.

#### 0.5b: Update extraction_prompt.md

Edit `pipeline/config/ricksteves/extraction_prompt.md` to include the new fields in the expected JSON output. The extraction prompt must instruct Gemini Flash to extract:

- **actors**: Named people featured (always include "Rick Steves", plus local guides, chefs, artisans, historians, hoteliers, tour operators, etc.)
- **roles**: Normalized role types (host, guide, chef, artisan, historian, hotelier, sommelier, fisherman, baker, etc.)
- **shows**: Always ["Rick Steves' Europe"] for this pipeline.
- **cuisines**: Cuisine types if food is featured (French, Italian, Tapas, Greek, Turkish, Moroccan, etc.). Empty array if no food.
- **dishes**: Specific food items mentioned (croissant, gelato, paella, bratwurst, schnitzel, moussaka, etc.). Empty array if no food.
- **eras**: Historical periods or time references (Medieval, Renaissance, Roman, Ottoman, Victorian, WWII, Cold War, etc.). Empty array if no historical context.
- **continents**: The continent(s) for this location. Usually ["Europe"] but can be ["Africa"] for Morocco/Egypt episodes, ["Asia"] for Turkey episodes, etc. Derive from the country.

The JSON output format in the prompt should look like:

```json
{
  "locations": [
    {
      "name": "Location Name",
      "city": "City",
      "country": "Country",
      "region": "Region or Province",
      "description": "Brief description",
      "keywords": ["keyword1", "keyword2"],
      "categories": ["category1"],
      "actors": ["Rick Steves", "Local Guide Name"],
      "roles": ["host", "guide"],
      "shows": ["Rick Steves' Europe"],
      "cuisines": ["French"],
      "dishes": ["croissant", "croque monsieur"],
      "eras": ["Medieval", "Renaissance"],
      "continents": ["Europe"]
    }
  ]
}
```

**Verify:** `fish -c "grep -c 'actors\|roles\|shows\|cuisines\|dishes\|eras\|continents' pipeline/config/ricksteves/extraction_prompt.md"` -> should return 7+.

#### 0.5c: Verify Script Enhancements From v4.12

The shared scripts already have the enhancements from v4.12. Verify they're still intact:

```fish
fish -c "grep -c 'COUNTRY_TO_CONTINENT' pipeline/scripts/phase4_normalize.py"
```
-> should return 1+

```fish
fish -c "grep -c 'county' pipeline/scripts/phase5_geocode.py"
```
-> should return 1+

If either returns 0, the v4.12 changes were lost. Re-apply per calgold-design-v4.12.md Step 0.5c/0.5d.

### Step 1: Acquire (phase1_acquire.py)

```fish
fish -c "cd ~/dev/projects/kjtcom && python3 pipeline/scripts/phase1_acquire.py --pipeline ricksteves --limit 150"
```

**Expected:** 30 new MP3 files (checkpoint skips 1-120). Total: 150.
**Verify:** `fish -c "command ls pipeline/data/ricksteves/audio/*.mp3 | wc -l"` -> 150

### Step 2: Transcribe (phase2_transcribe.py)

**Background job (G18). Rick Steves episodes are 30-60 min -- budget ~30 minutes.**

```fish
fish -c "cd ~/dev/projects/kjtcom && nohup python3 -u pipeline/scripts/phase2_transcribe.py --pipeline ricksteves --limit 150 > transcribe_v4.13.log 2>&1 &"
```

**Poll every 60 seconds:**
```fish
fish -c "command ls ~/dev/projects/kjtcom/pipeline/data/ricksteves/transcripts/*.json | wc -l"
```

**Expected:** Count goes from 120 to 150 (~30 min).
**Wait until 150 before proceeding. ONE process only (G21).**

### Step 3: Re-Extract ALL 150 Videos (phase3_extract.py)

**CRITICAL: Re-extracts ALL 150 videos with v3 prompt, overwriting previous extracted JSON.**

```fish
fish -c "cd ~/dev/projects/kjtcom && python3 pipeline/scripts/phase3_extract.py --pipeline ricksteves --limit 150"
```

**Expected:** 150 extracted JSON files, each containing the 7 new fields.
**This will take ~25 min for 150 videos via Gemini Flash API.**
**Verify new fields:** `fish -c "python3 -c 'import json,os; files=sorted(os.listdir(\"pipeline/data/ricksteves/extracted/\")); d=json.load(open(f\"pipeline/data/ricksteves/extracted/{files[-1]}\")); locs=d.get(\"locations\",[]); print(\"actors\" in locs[0], \"shows\" in locs[0] if locs else \"no locations\")'"` -> True True

### Step 4: Re-Normalize ALL 150 (phase4_normalize.py)

```fish
fish -c "cd ~/dev/projects/kjtcom && python3 pipeline/scripts/phase4_normalize.py --pipeline ricksteves --limit 150"
```

**Expected:** ALL entities normalized with v3 fields. t_any_continents derived from t_any_countries via the COUNTRY_TO_CONTINENT dictionary. t_schema_version: 3.
**Verify:** `fish -c "tail -1 pipeline/data/ricksteves/normalized/normalized.jsonl | python3 -c 'import json,sys; d=json.loads(sys.stdin.readline()); print(d.get(\"t_any_actors\"), d.get(\"t_any_continents\"), d.get(\"t_any_shows\"), d.get(\"t_schema_version\"))'"` -> should show actors, continent, show, 3

### Step 5: Re-Geocode ALL 150 (phase5_geocode.py)

```fish
fish -c "cd ~/dev/projects/kjtcom && python3 pipeline/scripts/phase5_geocode.py --pipeline ricksteves --limit 150"
```

**Expected:** County parsing active where Nominatim provides it. International locations may have lower county population than CalGold.

### Handoff Checkpoint

```fish
fish -c "cd ~/dev/projects/kjtcom && python3 -c \"
import json, glob
checkpoint = {
    'iteration': 'v4.13',
    'agent': 'gemini-cli',
    'phases_completed': ['0.5-schema-v3', 1, 2, 3, 4, 5],
    'schema_version': 3,
    'new_fields': ['t_any_actors', 't_any_roles', 't_any_shows', 't_any_cuisines', 't_any_dishes', 't_any_eras', 't_any_continents'],
    'audio_count': len(glob.glob('pipeline/data/ricksteves/audio/*.mp3')),
    'transcript_count': len(glob.glob('pipeline/data/ricksteves/transcripts/*.json')),
    'extracted_count': len(glob.glob('pipeline/data/ricksteves/extracted/*.json')),
    'status': 'ready_for_phase_6_7'
}
json.dump(checkpoint, open('pipeline/data/ricksteves/handoff-v4.13.json','w'), indent=2)
print(json.dumps(checkpoint, indent=2))
\""
```

**STOP HERE. Human reviews checkpoint, then launches Claude Code.**

---

## Section B: Claude Code Execution (Phases 6-7 + Post-Flight)

**Launch:** `claude --dangerously-skip-permissions`
**First message:** (see prompts)

### Handoff Verification

Read pipeline/data/ricksteves/handoff-v4.13.json. Verify schema_version: 3, new_fields contains all 7, counts at 150.

### Step 5.5: Reset Checkpoints (G24 - CRITICAL)

**Learned from v4.12:** The enrichment and load checkpoints from v3.11 contain 120 stale entries (schema v2). They MUST be reset before re-enriching and re-loading all 150.

```fish
cd ~/dev/projects/kjtcom

# Reset enrichment checkpoint
python3 -c "
import json, os
cp_path = 'pipeline/data/ricksteves/enriched/.checkpoint.json'
if os.path.exists(cp_path):
    print(f'Old checkpoint: {json.load(open(cp_path))}')
    os.remove(cp_path)
    print('Enrichment checkpoint reset')
else:
    print('No enrichment checkpoint found')
"

# Reset load checkpoint
python3 -c "
import json, os
cp_path = 'pipeline/data/ricksteves/loaded/.checkpoint.json'
if os.path.exists(cp_path):
    print(f'Old checkpoint: {json.load(open(cp_path))}')
    os.remove(cp_path)
    print('Load checkpoint reset')
else:
    print('No load checkpoint found')
"
```

**Verify both are cleared before proceeding.**

### Step 6: Re-Enrich ALL 150 (phase6_enrich.py)

```fish
python3 pipeline/scripts/phase6_enrich.py --pipeline ricksteves
```

**Note:** phase6 does NOT accept --database flag (file I/O only).
**Expected:** >95% enrichment. All 150 files re-enriched with v3 data.

### Step 7: Re-Load ALL 150 (phase7_load.py)

```fish
python3 pipeline/scripts/phase7_load.py --pipeline ricksteves --database staging
```

**Expected:** All entities loaded with schema v3 fields. Multi-visit merge preserves all visit data. t_schema_version: 3 on all documents.

### Step 7.5: Backfill CalGold t_any_shows (Optional)

If time permits, backfill all CalGold entities with t_any_shows: ["California's Gold"]:

```fish
python3 -c "
from google.cloud import firestore
import os
os.environ.setdefault('GOOGLE_APPLICATION_CREDENTIALS', os.path.expanduser('~/.config/gcloud/kjtcom-sa.json'))
db = firestore.Client(project='kjtcom-c78cd', database='staging')
docs = db.collection('locations').where('t_log_type', '==', 'calgold').stream()
count = 0
for doc in docs:
    doc.reference.update({'t_any_shows': ['California\\'s Gold']})
    count += 1
print(f'Backfilled t_any_shows on {count} CalGold entities')
"
```

**If this fails or takes too long, defer to a future iteration. Not blocking.**

### Step 8: Post-Flight - Schema v3 Validation

```
STANDARD CHECKS:
[ ] Security: grep -rnI "AIzaSy" . -> only doc references
[ ] Entity count: Firestore staging ricksteves document count
[ ] Cross-pipeline: keyword search returns both pipelines

SCHEMA V3 CHECKS:
[ ] t_schema_version: ALL ricksteves entities at version 3
[ ] t_any_actors: >90% populated, all should include "Rick Steves"
[ ] t_any_roles: >90% populated, all should include "host"
[ ] t_any_shows: 100% populated with ["Rick Steves' Europe"]
[ ] t_any_continents: 100% populated (derived from countries)
[ ] t_any_counties: check population rate (lower expected for international)
[ ] t_any_cuisines: spot-check 3 food-related entities
[ ] t_any_dishes: spot-check 3 food-related entities
[ ] t_any_eras: spot-check 3 history-related entities
[ ] Country distribution: verify count (was 30 in v3.11)
```

### Step 9: Produce Artifacts

**All 4 mandatory artifacts:**

1. **docs/ricksteves-build-v4.13.md** - Include schema v3 migration detail, checkpoint reset, CalGold backfill status
2. **docs/ricksteves-report-v4.13.md** - Schema v3 field population rates, Phase 1-4 cumulative metrics, recommendation for Phase 5
3. **docs/kjtcom-changelog.md** - Append v4.13 at top, note schema v3 migration for RickSteves
4. **README.md** - Update Project Status (Phase 4 DONE for both pipelines), Pipelines table, Changelog. Use this phase structure:

```
| Phase | Name                                | Status  | Iteration         |
|-------|-------------------------------------|---------|-------------------|
| 0     | Scaffold & Environment              | DONE    | v0.5              |
| 1     | Discovery (30 videos)               | DONE    | v1.6, v1.7        |
| 2     | Calibration (60 videos)             | DONE    | v2.8, v2.9        |
| 3     | Stress Test (90 videos)             | DONE    | v3.10, v3.11      |
| 4     | Validation + Schema v3 (120 videos) | DONE    | v4.12, v4.13      |
| 5     | Production Run (full datasets)      | Pending | -                 |
| 6     | Flutter App                         | Pending | -                 |
| 7     | Firestore Load                      | Pending | -                 |
| 8     | Enrichment Hardening                | Pending | -                 |
| 9     | App Optimization                    | Pending | -                 |
| 10    | Retrospective + Template            | Pending | -                 |
```

---

## Timing Estimate

| Phase | Agent | Est. Duration |
|-------|-------|---------------|
| Step 0 (pre-flight) | Gemini | ~3 min |
| Step 0.5 (schema v3 config) | Gemini | ~10 min |
| Step 1 (acquire 30 new) | Gemini | ~5 min |
| Step 2 (transcribe 30 new) | Gemini | ~30 min |
| Step 3 (re-extract all 150) | Gemini | ~25 min |
| Step 4 (re-normalize all 150) | Gemini | ~2 min |
| Step 5 (re-geocode all 150) | Gemini | ~12 min |
| Handoff review | Human | ~5 min |
| Step 5.5 (checkpoint resets) | Claude | ~1 min |
| Step 6 (re-enrich all 150) | Claude | ~12 min |
| Step 7 (re-load all 150) | Claude | ~5 min |
| Step 7.5 (CalGold backfill) | Claude | ~3 min |
| Step 8-9 (post-flight + artifacts) | Claude | ~10 min |
| **Total** | **Split** | **~120 min** |
