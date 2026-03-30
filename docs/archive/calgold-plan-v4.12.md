# CalGold - Plan v4.12 (Phase 4 - Validation + Schema v3)

**Pipeline:** calgold
**Phase:** 4 (Validation)
**Iteration:** 12 (global counter)
**Batch:** Videos 91-120 (30 new) + Re-extraction of ALL 120
**Date:** March 2026

---

## Section A: Gemini CLI Execution (Schema Prep + Phases 1-5)

**Launch:** `gemini --yolo`
**First message:** "Read GEMINI.md, then execute Section A of docs/calgold-plan-v4.12.md. This iteration includes schema v3 migration. Start with Step 0, then Step 0.5 (schema changes), then phases 1-5. Stop at handoff checkpoint."

### Step 0: Pre-Flight Verification

```
CHECKLIST:
[ ] Previous docs archived: docs/archive/ contains v3.10 and v3.11 artifacts
[ ] Current docs in place: docs/calgold-design-v4.12.md and docs/calgold-plan-v4.12.md exist
[ ] GEMINI.md updated with v4.12 references
[ ] Git status clean
[ ] API keys (SET/NOT SET only, NEVER cat config.fish):
    - fish -c "test -n \$GEMINI_API_KEY && echo SET || echo NOT SET"
    - fish -c "test -n \$GOOGLE_PLACES_API_KEY && echo SET || echo NOT SET"
    - fish -c "test -n \$GOOGLE_APPLICATION_CREDENTIALS && echo SET || echo NOT SET"
[ ] CUDA visible: fish -c "nvidia-smi | head -5"
[ ] LD_LIBRARY_PATH set: fish -c "echo \$LD_LIBRARY_PATH"
[ ] Disk space: df -h /home | tail -1 (need >50GB free)
[ ] Python deps: fish -c "python3 -c 'import faster_whisper; import google.genai; print(\"OK\")'"
[ ] Places API valid: fish -c "curl -s 'https://places.googleapis.com/v1/places:searchText' -H 'Content-Type: application/json' -H 'X-Goog-Api-Key: '\$GOOGLE_PLACES_API_KEY -H 'X-Goog-FieldMask: places.displayName' -d '{\"textQuery\": \"Watts Towers Los Angeles\"}' | head -3"
[ ] Current counts: audio=90, transcripts=90, extracted=90
```

### Step 0.5: Schema v3 Config Changes

**This is the critical step. All config and script changes must be made BEFORE running the pipeline.**

#### 0.5a: Update schema.json

Edit `pipeline/config/calgold/schema.json` to add the 6 new field mappings:

```json
{
  "t_any_actors": "actors",
  "t_any_roles": "roles",
  "t_any_cuisines": "cuisines",
  "t_any_dishes": "dishes",
  "t_any_eras": "eras",
  "t_any_continents": "continents"
}
```

Also update `t_schema_version` default to 3.

**Verify:** `fish -c "cat pipeline/config/calgold/schema.json | python3 -c 'import json,sys; d=json.load(sys.stdin); print([k for k in d if \"actor\" in k or \"cuisine\" in k or \"dish\" in k or \"era\" in k or \"continent\" in k or \"role\" in k])'"` should show all 6 new keys.

#### 0.5b: Update extraction_prompt.md

Edit `pipeline/config/calgold/extraction_prompt.md` to include the new fields in the expected JSON output. The extraction prompt must instruct Gemini Flash to extract:

- **actors**: Named people featured (always include "Huell Howser" for CalGold, plus any featured person - park rangers, historians, business owners, chefs, docents, etc.)
- **roles**: Normalized role types for each actor (host, park ranger, historian, chef, owner, docent, guide, curator, artist, farmer, etc.)
- **cuisines**: Cuisine types if food is featured (Mexican, BBQ, Bakery, Seafood, etc.). Empty array if no food.
- **dishes**: Specific food items mentioned (fish tacos, date shake, tri-tip, sourdough bread, etc.). Empty array if no food.
- **eras**: Historical periods or time references (Gold Rush, 1920s, Spanish Colonial, Victorian, WWII, etc.). Empty array if no historical context.
- **continents**: Always ["North America"] for CalGold.

The JSON output format in the prompt should look like:

```json
{
  "locations": [
    {
      "name": "Location Name",
      "city": "City",
      "state": "CA",
      "county": "County Name",
      "description": "Brief description",
      "keywords": ["keyword1", "keyword2"],
      "categories": ["category1"],
      "actors": ["Huell Howser", "Other Person"],
      "roles": ["host", "park ranger"],
      "cuisines": ["Mexican"],
      "dishes": ["fish tacos"],
      "eras": ["Gold Rush"],
      "continents": ["North America"]
    }
  ]
}
```

**Verify:** `fish -c "grep -c 'actors\|roles\|cuisines\|dishes\|eras\|continents' pipeline/config/calgold/extraction_prompt.md"` should return 6+.

#### 0.5c: Enhance phase4_normalize.py - Continent Lookup

Add a country-to-continent dictionary to phase4_normalize.py. When t_any_countries is populated, auto-derive t_any_continents. The dictionary should cover at minimum all 30 currently active countries plus the US.

```python
COUNTRY_TO_CONTINENT = {
    "us": "North America", "united states": "North America",
    "france": "Europe", "italy": "Europe", "spain": "Europe",
    "germany": "Europe", "austria": "Europe", "switzerland": "Europe",
    "netherlands": "Europe", "belgium": "Europe", "england": "Europe",
    "united kingdom": "Europe", "scotland": "Europe", "ireland": "Europe",
    "portugal": "Europe", "greece": "Europe", "turkey": "Europe",
    "croatia": "Europe", "czech republic": "Europe", "czechia": "Europe",
    "hungary": "Europe", "poland": "Europe", "norway": "Europe",
    "sweden": "Europe", "denmark": "Europe", "finland": "Europe",
    "romania": "Europe", "bulgaria": "Europe", "slovenia": "Europe",
    "montenegro": "Europe", "bosnia and herzegovina": "Europe",
    "vatican city": "Europe",
    "morocco": "Africa", "egypt": "Africa", "ethiopia": "Africa",
    "israel": "Asia", "iran": "Asia", "india": "Asia", "japan": "Asia",
    "china": "Asia", "south korea": "Asia", "thailand": "Asia",
    "vietnam": "Asia", "cambodia": "Asia",
    "canada": "North America", "mexico": "North America",
    "brazil": "South America", "argentina": "South America",
    "peru": "South America", "colombia": "South America",
    "australia": "Oceania", "new zealand": "Oceania",
}
```

If t_any_countries is empty or country not in dictionary, leave t_any_continents as whatever the extraction provided. For CalGold, the extraction prompt already specifies ["North America"] so this is a safety net.

**Verify:** After modifying, run `fish -c "python3 -c 'exec(open(\"pipeline/scripts/phase4_normalize.py\").read()); print(\"OK\")'"` to check for syntax errors.

#### 0.5d: Enhance phase5_geocode.py - County Parsing

Modify phase5_geocode.py to parse the `county` field from the Nominatim `address` response object. When Nominatim returns address data, extract `address.county` and write it to `t_any_counties` (as an array: e.g. ["Los Angeles County"]).

Nominatim response example:
```json
{
  "address": {
    "tourism": "Watts Towers",
    "city": "Los Angeles",
    "county": "Los Angeles County",
    "state": "California",
    "country": "United States"
  }
}
```

Parse: `county = address.get("county", "")` -> if non-empty, add to t_any_counties array.

**Verify:** After modifying, run `fish -c "python3 -c 'exec(open(\"pipeline/scripts/phase5_geocode.py\").read()); print(\"OK\")'"` to check for syntax errors.

#### 0.5e: Verify All Changes

```
fish -c "cd ~/dev/projects/kjtcom && echo '--- schema.json ---' && python3 -c 'import json; d=json.load(open(\"pipeline/config/calgold/schema.json\")); [print(k) for k in sorted(d) if k.startswith(\"t_any\")]'"
```

Should show t_any_actors, t_any_categories, t_any_cities, t_any_continents, t_any_coordinates, t_any_counties, t_any_countries, t_any_cuisines, t_any_dishes, t_any_eras, t_any_geohashes, t_any_keywords, t_any_names, t_any_people, t_any_regions, t_any_roles, t_any_states, t_any_urls, t_any_video_ids.

### Step 1: Acquire (phase1_acquire.py)

```fish
fish -c "cd ~/dev/projects/kjtcom && python3 pipeline/scripts/phase1_acquire.py --pipeline calgold --limit 120"
```

**Expected:** 30 new MP3 files (checkpoint skips 1-90). Total: 120.
**Verify:** `fish -c "command ls pipeline/data/calgold/audio/*.mp3 | wc -l"` -> 120

### Step 2: Transcribe (phase2_transcribe.py)

**Background job (G18):**

```fish
fish -c "cd ~/dev/projects/kjtcom && nohup python3 -u pipeline/scripts/phase2_transcribe.py --pipeline calgold --limit 120 > transcribe_v4.12.log 2>&1 &"
```

**Poll every 60 seconds:**
```fish
fish -c "command ls ~/dev/projects/kjtcom/pipeline/data/calgold/transcripts/*.json | wc -l"
```

**Expected:** Count goes from 90 to 120 (~15 min for 30 CalGold episodes).
**Wait until 120 before proceeding. ONE process only (G21).**

### Step 3: Re-Extract ALL 120 Videos (phase3_extract.py)

**CRITICAL: This re-extracts ALL 120 videos with the updated v3 extraction prompt, overwriting previous extracted JSON.**

```fish
fish -c "cd ~/dev/projects/kjtcom && python3 pipeline/scripts/phase3_extract.py --pipeline calgold --limit 120"
```

**Expected:** 120 extracted JSON files, each containing the new fields (actors, roles, cuisines, dishes, eras, continents).
**Verify new fields present:** `fish -c "python3 -c 'import json,os; f=os.listdir(\"pipeline/data/calgold/extracted/\")[0]; d=json.load(open(f\"pipeline/data/calgold/extracted/{f}\")); locs=d.get(\"locations\",[]); print(\"actors\" in locs[0] if locs else \"no locations\")'"` -> True
**This will take ~20 min for 120 videos via Gemini Flash API.**

### Step 4: Re-Normalize ALL 120 (phase4_normalize.py)

```fish
fish -c "cd ~/dev/projects/kjtcom && python3 pipeline/scripts/phase4_normalize.py --pipeline calgold --limit 120"
```

**Expected:** ALL entities normalized with t_any_actors, t_any_roles, t_any_cuisines, t_any_dishes, t_any_eras, t_any_continents populated. t_schema_version: 3.
**Verify:** `fish -c "head -1 pipeline/data/calgold/normalized/normalized.jsonl | python3 -c 'import json,sys; d=json.loads(sys.stdin.readline()); print(d.get(\"t_any_actors\"), d.get(\"t_any_continents\"), d.get(\"t_schema_version\"))'"` -> should show actors array, ["North America"], 3

### Step 5: Re-Geocode ALL 120 (phase5_geocode.py)

```fish
fish -c "cd ~/dev/projects/kjtcom && python3 pipeline/scripts/phase5_geocode.py --pipeline calgold --limit 120"
```

**Expected:** County parsing active. t_any_counties populated from Nominatim address.county.
**Verify county populated:** `fish -c "python3 -c 'import json; lines=open(\"pipeline/data/calgold/geocoded/geocoded.jsonl\").readlines()[:5]; [print(json.loads(l).get(\"t_any_counties\",[])) for l in lines]'"` -> should show county arrays.

### Handoff Checkpoint

```fish
fish -c "cd ~/dev/projects/kjtcom && python3 -c \"
import json, glob
checkpoint = {
    'iteration': 'v4.12',
    'agent': 'gemini-cli',
    'phases_completed': ['0.5-schema-v3', 1, 2, 3, 4, 5],
    'schema_version': 3,
    'new_fields': ['t_any_actors', 't_any_roles', 't_any_cuisines', 't_any_dishes', 't_any_eras', 't_any_continents'],
    'audio_count': len(glob.glob('pipeline/data/calgold/audio/*.mp3')),
    'transcript_count': len(glob.glob('pipeline/data/calgold/transcripts/*.json')),
    'extracted_count': len(glob.glob('pipeline/data/calgold/extracted/*.json')),
    'status': 'ready_for_phase_6_7'
}
json.dump(checkpoint, open('pipeline/data/calgold/handoff-v4.12.json','w'), indent=2)
print(json.dumps(checkpoint, indent=2))
\""
```

**STOP HERE. Human reviews checkpoint, then launches Claude Code.**

---

## Section B: Claude Code Execution (Phases 6-7 + Post-Flight)

**Launch:** `claude --dangerously-skip-permissions`
**First message:** (see prompts section)

### Handoff Verification

Read pipeline/data/calgold/handoff-v4.12.json. Verify:
- schema_version: 3
- new_fields contains all 6 fields
- audio/transcript/extracted counts all at 120
- status: ready_for_phase_6_7

### Step 6: Re-Enrich ALL 120 (phase6_enrich.py)

```fish
cd ~/dev/projects/kjtcom
python3 pipeline/scripts/phase6_enrich.py --pipeline calgold
```

**Note:** phase6 does NOT accept --database flag (file I/O only).
**Expected:** >95% enrichment. All 120 files re-enriched.

### Step 7: Re-Load ALL 120 (phase7_load.py)

```fish
python3 pipeline/scripts/phase7_load.py --pipeline calgold --database staging
```

**Expected:** All entities loaded with schema v3 fields. Multi-visit merge preserves existing data while adding new fields. t_schema_version: 3 on all documents.
**Verify:** Query Firestore for any calgold entity, confirm t_any_actors, t_any_continents, t_schema_version: 3 present.

### Step 8: Post-Flight - Schema v3 Validation

```
STANDARD CHECKS:
[ ] Security: grep -rnI "AIzaSy" . -> only doc references
[ ] Entity count: Firestore staging calgold document count
[ ] Cross-pipeline: keyword search returns both pipelines

SCHEMA V3 CHECKS:
[ ] t_schema_version: ALL calgold entities at version 3
[ ] t_any_actors: spot-check 5 entities, all should contain "Huell Howser"
[ ] t_any_roles: spot-check 5 entities, all should contain "host"
[ ] t_any_continents: ALL calgold entities have ["North America"]
[ ] t_any_counties: >80% of geocoded entities have county populated
[ ] t_any_cuisines: spot-check 3 food-related entities, should be non-empty
[ ] t_any_dishes: spot-check 3 food-related entities, should be non-empty
[ ] t_any_eras: spot-check 3 history-related entities, should be non-empty
```

### Step 9: Produce Artifacts

**All 4 mandatory artifacts:**

1. **docs/calgold-build-v4.12.md** - Include schema v3 migration detail, script changes, re-extraction stats
2. **docs/calgold-report-v4.12.md** - Schema v3 field population rates, Phase 1-4 cumulative metrics, recommendation for Phase 5
3. **docs/kjtcom-changelog.md** - Append v4.12 at top, note schema v3 migration
4. **README.md** - Update Thompson Schema section with new fields, update Project Status, Pipelines, Changelog

---

## Timing Estimate

| Phase | Agent | Est. Duration |
|-------|-------|---------------|
| Step 0 (pre-flight) | Gemini | ~3 min |
| Step 0.5 (schema v3 config) | Gemini | ~15 min |
| Step 1 (acquire 30 new) | Gemini | ~5 min |
| Step 2 (transcribe 30 new) | Gemini | ~15 min |
| Step 3 (re-extract all 120) | Gemini | ~20 min |
| Step 4 (re-normalize all 120) | Gemini | ~2 min |
| Step 5 (re-geocode all 120) | Gemini | ~10 min |
| Handoff review | Human | ~5 min |
| Step 6 (re-enrich all 120) | Claude | ~10 min |
| Step 7 (re-load all 120) | Claude | ~5 min |
| Step 8-9 (post-flight + artifacts) | Claude | ~10 min |
| **Total** | **Split** | **~100 min** |
