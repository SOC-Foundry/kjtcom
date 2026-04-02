# kjtcom - Plan v7.21 (Phase 7 - Firestore Load + TripleDB Migration)

**Pipeline:** kjtcom (cross-pipeline location intelligence platform)
**Phase:** 7 (Firestore Load)
**Iteration:** 21 (global counter)
**Executor:** Claude Code (migration script)
**Machine:** tsP3-cos (ThinkStation P3 Ultra SFF G2)
**Date:** April 2026

---

## Section A: Pre-Flight (Human, tsP3-cos)

### A1: Verify Both SA Credentials

```fish
cd ~/dev/projects/kjtcom

# kjtcom SA (already configured)
test -f "$GOOGLE_APPLICATION_CREDENTIALS" && echo "kjtcom SA: EXISTS" || echo "kjtcom SA: MISSING"

# TripleDB SA - copy from NZXTcos or download from GCP Console
# Project: TachTech-Engineering TripleDB Firebase project
# If not present, download from GCP Console -> IAM -> Service Accounts
ls ~/.config/gcloud/tripledb-sa.json 2>/dev/null && echo "TripleDB SA: EXISTS" || echo "TripleDB SA: MISSING"

# If missing:
# scp kthompson@nzxtcos:~/.config/gcloud/tripledb-sa.json ~/.config/gcloud/
# OR download from GCP Console for the TripleDB project
```

### A2: Identify TripleDB Firebase Project ID

```fish
# Check the TripleDB SA file for project_id (grep only, never cat full file - G11)
grep "project_id" ~/.config/gcloud/tripledb-sa.json
# Expected: something like "tripledb-xxxxx" or the actual project ID
```

Record the project ID - the plan references it as `tripledb-e0f77` throughout.

### A3: Install Python Dependencies

```fish
pip install firebase-admin geohash2 --break-system-packages
python3 -c "import firebase_admin; import geohash2; print('OK')"
```

### A4: Verify kjtcom Production Database Access

```fish
# Quick test: count documents in production (default) database
python3 -c "
from google.cloud import firestore
import os
os.environ.setdefault('GOOGLE_APPLICATION_CREDENTIALS', os.path.expanduser('~/.config/gcloud/kjtcom-sa.json'))
db = firestore.Client(project='kjtcom-c78cd')
docs = list(db.collection('locations').limit(5).stream())
print(f'Production (default) locations: {len(docs)} (expect 0 - empty)')
"
```

### A5: Verify kjtcom Staging Database Access

```fish
python3 -c "
from google.cloud import firestore
import os
os.environ.setdefault('GOOGLE_APPLICATION_CREDENTIALS', os.path.expanduser('~/.config/gcloud/kjtcom-sa.json'))
db = firestore.Client(project='kjtcom-c78cd', database='staging')
docs = list(db.collection('locations').limit(5).stream())
print(f'Staging locations sample: {len(docs)} docs')
if docs:
    d = docs[0].to_dict()
    print(f'Sample t_log_type: {d.get(\"t_log_type\")}')
    print(f'Sample t_schema_version: {d.get(\"t_schema_version\")}')
"
```

### A6: Inspect TripleDB Firestore Schema (CRITICAL - G31)

```fish
# Read 3 sample documents from TripleDB to verify actual schema
# REPLACE tripledb-e0f77 with actual project ID from A2
python3 -c "
from google.cloud import firestore
import json

db = firestore.Client(
    project='tripledb-e0f77',
    credentials_file='~/.config/gcloud/tripledb-sa.json'
)
# Try 'restaurants' collection first (expected from schema docs)
for doc in db.collection('restaurants').limit(3).stream():
    d = doc.to_dict()
    print(f'=== {doc.id} ===')
    print(f'Keys: {sorted(d.keys())}')
    print(f'name: {d.get(\"name\")}')
    print(f'city: {d.get(\"city\")}')
    print(f'state: {d.get(\"state\")}')
    print(f'cuisine_type: {d.get(\"cuisine_type\")}')
    print(f'latitude: {d.get(\"latitude\")}')
    print(f'google_rating: {d.get(\"google_rating\")}')
    print(f'dishes count: {len(d.get(\"dishes\", []))}')
    print(f'visits count: {len(d.get(\"visits\", []))}')
    print()
"
```

**STOP AND REVIEW.** If the actual schema differs from what's documented in the design doc, update the mapping before proceeding to Section B. The design doc schema is based on past conversations and may be outdated (G31).

### A7: Count TripleDB Documents

```fish
python3 -c "
from google.cloud import firestore
db = firestore.Client(
    project='tripledb-e0f77',
    credentials_file='~/.config/gcloud/tripledb-sa.json'
)
count = 0
for doc in db.collection('restaurants').stream():
    count += 1
print(f'TripleDB restaurants: {count}')
"
```

---

## Section B: Claude Code Execution (Migration Script + Load)

**Launch:** `claude --dangerously-skip-permissions`
**First message:** See prompt at end of this document.

### Step 1: Read Design Doc

Read `docs/kjtcom-design-v7.21.md` for the complete schema mapping specification.

### Step 2: Create Migration Script

Create `pipeline/scripts/migrate_tripledb.py`:

The script must:

1. Initialize two Firestore clients:
   - Source: TripleDB project (read-only)
   - Destination: kjtcom production (default) database (write)

2. Read all documents from TripleDB's `restaurants` collection

3. For each document, apply the Thompson Indicator Fields mapping:

   **Direct mappings:**
   - name -> t_any_names: [name]
   - city -> t_any_cities: [city.lower()]
   - state -> t_any_states: [state.lower()]
   - lat/lon -> t_any_coordinates: [{"lat": lat, "lon": lon}]
   - cuisine_type -> t_any_cuisines: split on comma/slash, lowercase, array
   - dishes[].dish_name -> t_any_dishes: flattened lowercase array
   - owner_chef -> t_any_people: [owner_chef] if not null
   - visits[].video_id -> t_any_video_ids: flattened array
   - visits[].youtube_url -> t_any_urls: flattened array

   **Hardcoded backfills:**
   - t_log_type = "tripledb"
   - t_any_actors = ["Guy Fieri"] + [owner_chef] if present
   - t_any_roles = ["host"] + ["chef"/"owner"] if owner_chef present
   - t_any_shows = ["Diners, Drive-Ins and Dives"]
   - t_any_countries = ["us"]
   - t_any_continents = ["North America"]
   - t_any_eras = []
   - t_schema_version = 3

   **Derived fields:**
   - t_any_keywords: combine cuisine_type + dish ingredients + dish categories, dedup
   - t_any_categories: from cuisine_type + "restaurant"
   - t_any_geohashes: computed from lat/lon if coordinates exist
   - t_row_id: deterministic hash of (name + city + "tripledb") for dedup safety

   **Enrichment carry-forward:**
   - google_rating -> t_enrichment.google_places.rating
   - still_open -> t_enrichment.google_places.still_open
   - website_url -> t_enrichment.google_places.website

4. Write transformed documents to kjtcom's `locations` collection using batch writes (500 docs per batch)

5. Print summary: total read, total written, field population rates

**Script flags:**
- `--dry-run`: Print mapping for first 5 docs without writing
- `--limit N`: Process only N documents (for testing)
- `--project tripledb-e0f77`: Source project ID
- `--sa-path PATH`: Path to TripleDB SA JSON

### Step 3: Dry Run (5 Documents)

```fish
python3 pipeline/scripts/migrate_tripledb.py \
  --project tripledb-e0f77 \
  --sa-path ~/.config/gcloud/tripledb-sa.json \
  --dry-run --limit 5
```

Review the output. Verify all Thompson fields are populated correctly. Check for null values, empty arrays, malformed data.

### Step 4: Full TripleDB Migration

```fish
python3 pipeline/scripts/migrate_tripledb.py \
  --project tripledb-e0f77 \
  --sa-path ~/.config/gcloud/tripledb-sa.json
```

Expected: ~1,100 documents written to production `locations` collection with t_log_type="tripledb".

### Step 5: Staging -> Production Migration (CalGold + RickSteves)

Create `pipeline/scripts/migrate_staging_to_production.py`:

```fish
python3 pipeline/scripts/migrate_staging_to_production.py
```

The script reads ALL documents from kjtcom staging database `locations` collection and writes them to the production (default) database `locations` collection. No transformation - direct field copy. Batch writes (500 per batch).

Expected: 5,081 documents (899 CalGold + 4,182 RickSteves) copied to production.

### Step 6: Post-Load Verification

```fish
python3 -c "
from google.cloud import firestore
import os
os.environ.setdefault('GOOGLE_APPLICATION_CREDENTIALS', os.path.expanduser('~/.config/gcloud/kjtcom-sa.json'))
db = firestore.Client(project='kjtcom-c78cd')

# Count by pipeline
calgold = ricksteves = tripledb = 0
v3 = 0
for doc in db.collection('locations').stream():
    d = doc.to_dict()
    lt = d.get('t_log_type', '')
    if lt == 'calgold': calgold += 1
    elif lt == 'ricksteves': ricksteves += 1
    elif lt == 'tripledb': tripledb += 1
    if d.get('t_schema_version') == 3: v3 += 1

total = calgold + ricksteves + tripledb
print(f'=== PRODUCTION FIRESTORE VERIFICATION ===')
print(f'CalGold: {calgold}')
print(f'RickSteves: {ricksteves}')
print(f'TripleDB: {tripledb}')
print(f'Total: {total}')
print(f'Schema v3: {v3} ({v3*100//total}%)')
"
```

### Step 7: TripleDB Field Population Audit

```fish
python3 -c "
from google.cloud import firestore
import os
os.environ.setdefault('GOOGLE_APPLICATION_CREDENTIALS', os.path.expanduser('~/.config/gcloud/kjtcom-sa.json'))
db = firestore.Client(project='kjtcom-c78cd')

total = 0
has_cuisines = has_dishes = has_actors = has_coords = has_shows = has_enrichment = 0

for doc in db.collection('locations').where('t_log_type', '==', 'tripledb').stream():
    d = doc.to_dict()
    total += 1
    if d.get('t_any_cuisines'): has_cuisines += 1
    if d.get('t_any_dishes'): has_dishes += 1
    if d.get('t_any_actors'): has_actors += 1
    if d.get('t_any_coordinates'): has_coords += 1
    if d.get('t_any_shows'): has_shows += 1
    if d.get('t_enrichment', {}).get('google_places'): has_enrichment += 1

print(f'=== TRIPLEDB FIELD POPULATION ===')
print(f'Total: {total}')
print(f'Cuisines: {has_cuisines} ({has_cuisines*100//total}%)')
print(f'Dishes: {has_dishes} ({has_dishes*100//total}%)')
print(f'Actors: {has_actors} ({has_actors*100//total}%)')
print(f'Coordinates: {has_coords} ({has_coords*100//total}%)')
print(f'Shows: {has_shows} ({has_shows*100//total}%)')
print(f'Enrichment: {has_enrichment} ({has_enrichment*100//total}%)')
"
```

### Step 8: Live Site Verification

```fish
# Visit kylejeromethompson.com in a browser
# Verify:
# [ ] Rotating example queries show result counts > 0
# [ ] Searching t_any_cuisines contains "barbecue" returns TripleDB results
# [ ] TripleDB results have red pipeline dots
# [ ] CalGold results have gold pipeline dots
# [ ] RickSteves results have blue pipeline dots
# [ ] Clicking a result shows the detail panel with t_any_* fields
# [ ] +filter/-exclude buttons work on TripleDB entity fields
```

### Step 9: Provision Composite Indexes

If any queries fail with "requires an index" errors, create the indexes:

```fish
# Option A: Let Firestore auto-suggest (error messages include a direct link)
# Option B: Add to firestore.indexes.json and deploy
firebase deploy --only firestore:indexes --project kjtcom-c78cd
```

### Step 10: Security Scan + Artifacts

```
CHECKLIST:
[ ] Security: grep -rnI "AIzaSy" . -> only expected references
[ ] Total entities in production (target: ~6,281+)
[ ] All entities at t_schema_version: 3
[ ] 3 distinct t_log_type values
[ ] kylejeromethompson.com displays results from all 3 pipelines
[ ] TripleDB pipeline dots are red (#DD3333)
```

Produce all 4 mandatory artifacts:

1. **docs/kjtcom-build-v7.21.md** - Migration script detail, dry run output, full run metrics, staging copy metrics
2. **docs/kjtcom-report-v7.21.md** - Entity counts, field population rates, cross-pipeline verification, recommendation for Phase 8
3. **docs/kjtcom-changelog.md** - Append v7.21 at top
4. **README.md** - Phase 7 DONE, updated entity counts, 3 pipelines active

Do NOT git commit or push.

---

## CLAUDE.md for v7.21

```markdown
# kjtcom - Agent Instructions (Claude Code)

## Read Order

1. docs/kjtcom-design-v7.21.md (schema mapping specification)
2. docs/kjtcom-plan-v7.21.md (execute Section B)

## Context

Phase 7 Firestore Load. Two tasks:
1. Migrate ~1,100 TripleDB restaurants from external Firestore project
   to kjtcom production locations collection (Option 4: schema mapping)
2. Copy 5,081 CalGold + RickSteves entities from staging to production

TripleDB SA credentials are at ~/.config/gcloud/tripledb-sa.json
kjtcom SA credentials are at $GOOGLE_APPLICATION_CREDENTIALS
TripleDB project ID: tripledb-e0f77
kjtcom project ID: kjtcom-c78cd

## Shell - MANDATORY

- All commands in fish shell
- NEVER cat config.fish or SA JSON files (G20, G11)

## Security

- grep -rnI "AIzaSy" . before completion
- NEVER print SA credentials or API keys
- Print only SET/NOT SET for key checks

## Migration Script Requirements

- migrate_tripledb.py: --dry-run, --limit, --project, --sa-path flags
- migrate_staging_to_production.py: simple copy, no transformation
- Batch writes (500 docs per batch) for both scripts
- Deterministic t_row_id for dedup safety (G33)
- Print summary with field population rates after each migration

## Permissions

- CANNOT: git add / commit / push
- CANNOT: sudo

## Artifact Rules - MANDATORY

1. docs/kjtcom-build-v7.21.md
2. docs/kjtcom-report-v7.21.md
3. docs/kjtcom-changelog.md (append v7.21)
4. README.md (Phase 7 DONE, updated entity counts)

## Formatting

- No em-dashes. Use " - " instead.
- Use "->" for arrows.
```

---

## Launch Prompt

```
Read CLAUDE.md, then read the full design doc at docs/kjtcom-design-v7.21.md for the schema mapping specification. Create both migration scripts (migrate_tripledb.py and migrate_staging_to_production.py). Run the TripleDB dry run first (--dry-run --limit 5), verify the mapping output, then run the full TripleDB migration followed by the staging->production copy. Verify entity counts and field population rates. Produce all 4 mandatory artifacts for v7.21.
```

---

## Timing Estimate

| Step | Est. Duration |
|------|---------------|
| Section A (pre-flight, human) | ~15 min |
| Step 1-2 (read design + create scripts) | ~15 min |
| Step 3 (dry run) | ~2 min |
| Step 4 (full TripleDB migration) | ~5-10 min |
| Step 5 (staging -> production) | ~5-10 min |
| Steps 6-9 (verification + indexes) | ~10 min |
| Step 10 (security + artifacts) | ~10 min |
| **Total** | **~1-1.5 hours** |

---

## After v7.21

1. Commit: `git add . && git commit -m "KT 7.21 Phase 7 complete - 3 pipelines loaded, ~6,281 entities in production" && git push`
2. Visit kylejeromethompson.com - verify live cross-pipeline queries
3. RickSteves Phase 5 (v5.15) still running on NZXTcos - when complete, run Phase 7 load for the expanded RickSteves dataset
4. Phase 8 (Enrichment Hardening) - backfill any sparse fields identified in v7.21 field audit
5. Bourdain pipeline scoping (4th pipeline)
