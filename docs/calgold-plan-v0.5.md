# CalGold - Plan v0.5 (Phase 0)

**Phase:** 0 - Project Scaffold, Firebase Setup, Pipeline Config & Environment Validation
**Executor:** Claude Code (YOLO mode, Opus)
**Machine:** NZXTcos (Intel i9-13900K, RTX 2080 SUPER, 64 GB DDR4, CachyOS)
**Goal:** Scaffold the kjtcom monorepo, configure Firebase Blaze (kjtcom-c78cd) with multi-database, create the CalGold pipeline config with Thompson Schema, validate the environment, and produce the Phase 0 report. Plan Phase 1.

---

## Project Identity

| Key | Value |
|-----|-------|
| Domain | kylejeromethompson.com |
| Repository | `git@github.com:SOC-Foundry/kjtcom.git` |
| Firebase Project Name | kjtcom |
| Firebase Project ID | `kjtcom-c78cd` |
| Firebase Project Number | 703812044891 |
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
6. DATABASE: Load to "staging" database only. NEVER write to "(default)" in Phase 0.
```

---

## Pre-Flight Checklist

```
[ ] Previous docs archived to docs/archive/ (N/A - Phase 0, no previous)
[ ] calgold-design-v0.5.md in docs/
[ ] calgold-plan-v0.5.md in docs/ (this file)
[ ] CLAUDE.md created and pointing to design + plan
[ ] git status clean (repo: git@github.com:SOC-Foundry/kjtcom.git)
[ ] API keys validated:
    [ ] GEMINI_API_KEY set and non-empty
    [ ] GOOGLE_PLACES_API_KEY set and non-empty
    [ ] Firebase CLI authenticated (firebase login)
    [ ] firebase use kjtcom-c78cd succeeds
[ ] Build tools verified:
    [ ] flutter --version (>= 3.x)
    [ ] dart --version
    [ ] python3 --version (>= 3.10)
    [ ] firebase --version (>= 13.x)
    [ ] yt-dlp --version
    [ ] faster-whisper or ctranslate2 importable
[ ] CUDA verified: nvidia-smi shows RTX 2080 SUPER
[ ] Firebase project exists: kjtcom (kjtcom-c78cd)
[ ] Firebase Blaze billing enabled under socfoundry.com GCP org
[ ] Budget alert set at $10/month
```

---

## Step 0: Validate YouTube Playlist

```fish
# Validate the CalGold playlist
yt-dlp --flat-playlist --print "%(id)s %(title)s" \
  "https://www.youtube.com/playlist?list=PLr7fFk3JB5ic-nEyrqLj6MGDox5DO8oMl" | wc -l

# Expected: ~431 lines
# Save the full list for reference
yt-dlp --flat-playlist --print "%(id)s %(title)s" \
  "https://www.youtube.com/playlist?list=PLr7fFk3JB5ic-nEyrqLj6MGDox5DO8oMl" \
  > pipeline/config/calgold/playlist_urls.txt
```

**Success criteria:** playlist_urls.txt exists with 400+ entries.

---

## Step 1: Scaffold Monorepo

Clone the repo and create the directory structure defined in the design doc Section 10.

```fish
# Clone the repo (already created on GitHub under SOC-Foundry org)
mkdir -p ~/dev/projects
git clone git@github.com:SOC-Foundry/kjtcom.git ~/dev/projects/kjtcom
cd ~/dev/projects/kjtcom

# Root files
touch README.md CLAUDE.md GEMINI.md .gitignore firebase.json firestore.rules firestore.indexes.json .firebaserc

# App scaffold (Flutter - create later in Phase 8)
mkdir -p app

# Pipeline structure
mkdir -p pipeline/scripts/utils
mkdir -p pipeline/config/calgold
mkdir -p pipeline/data/calgold/{audio,transcripts,extracted,normalized,geocoded,enriched}
mkdir -p pipeline/agents

# Cloud Functions
mkdir -p functions/src

# Docs
mkdir -p docs/archive

# Requirements
mkdir -p requirements
```

### .gitignore

```
# Pipeline data (large, regeneratable)
pipeline/data/*/audio/
pipeline/data/*/transcripts/
pipeline/data/*/extracted/
pipeline/data/*/normalized/
pipeline/data/*/geocoded/
pipeline/data/*/enriched/

# Node
node_modules/
package-lock.json

# Flutter
app/.dart_tool/
app/.packages
app/build/

# Firebase
.firebase/

# OS
.DS_Store
*.pyc
__pycache__/

# Keys
*.key
*.pem
```

### CLAUDE.md

```markdown
# kjtcom - Agent Instructions
# kylejeromethompson.com - Multi-Pipeline Location Intelligence Platform

## Read Order
1. docs/calgold-design-v0.5.md (architecture + Thompson Schema)
2. docs/calgold-plan-v0.5.md (current execution plan)

## Project Identity
- Repo: git@github.com:SOC-Foundry/kjtcom.git
- Firebase: kjtcom (kjtcom-c78cd) under socfoundry.com
- Domain: kylejeromethompson.com

## Permissions
- CAN: flutter build web, firebase deploy --only hosting, firebase deploy --only firestore:rules
- CAN: firebase deploy --only functions
- CAN: pip install, npm install (project-level)
- CANNOT: git add / commit / push (Kyle commits at phase boundaries)
- CANNOT: sudo (ask Kyle - sudo exception)

## Database Rules
- Development loads go to the "staging" database
- Production loads go to "(default)" database ONLY after Kyle approves
- NEVER delete documents in "(default)" without explicit Kyle approval

## Formatting
- No em-dashes. Use " - " instead.
- Use "->" for arrows.
```

**Success criteria:** Directory tree matches design doc. .gitignore covers all data directories and node_modules.

---

## Step 2: Firebase Project Setup

### 2.1 Select Firebase Project

The Firebase project already exists under the socfoundry.com GCP org.

```fish
# Set as active project
firebase use kjtcom-c78cd

# Verify
firebase projects:list | grep kjtcom
```

### 2.2 Verify Blaze Billing

Blaze must be enabled in the Firebase Console under the socfoundry.com org.

**Kyle manual step:** Go to https://console.firebase.google.com/project/kjtcom-c78cd/usage/details -> Verify Blaze plan is active. Set budget alert at $10/month under GCP billing for socfoundry.com.

### 2.3 Enable Firestore

```fish
# Enable Firestore (default database) - may already exist
firebase firestore:databases:create --location=us-central1 --project kjtcom-c78cd

# Create staging database
firebase firestore:databases:create staging --location=us-central1 --project kjtcom-c78cd
```

### 2.4 Deploy Security Rules

Write `firestore.rules` per design doc Section 7.2, then:

```fish
firebase deploy --only firestore:rules
```

### 2.5 Deploy Composite Indexes

Write `firestore.indexes.json` per design doc Section 7.3, then:

```fish
firebase deploy --only firestore:indexes
```

### 2.6 Enable Firebase Hosting

```fish
firebase init hosting
# Public directory: app/build/web
# Single-page app: Yes
# GitHub Actions: No
```

### 2.7 Initialize Cloud Functions

```fish
cd functions
npm init -y
npm install firebase-functions firebase-admin
npm install -D typescript
cd ..
```

**Success criteria:**
- `firebase projects:list` shows kjtcom
- `firebase firestore:databases:list --project kjtcom-c78cd` shows (default) and staging
- `firebase deploy --only firestore:rules` succeeds
- `functions/package.json` exists with firebase-functions dependency

---

## Step 3: CalGold Pipeline Config

### 3.1 Write pipeline.json

```fish
# pipeline/config/calgold/pipeline.json
```

Content per design doc Section 4.2 (pipeline registry format).

### 3.2 Write schema.json

Content per design doc Section 6.1. This is the Thompson Schema indicator mapping for CalGold.

### 3.3 Write extraction_prompt.md

Content per design doc Section 6.2. This is the Gemini Flash extraction prompt.

### 3.4 Save playlist_urls.txt

Already created in Step 0.

**Success criteria:** All four config files exist in `pipeline/config/calgold/`. schema.json validates as valid JSON. extraction_prompt.md is non-empty.

---

## Step 4: Pipeline Scripts (Stubs)

Create stub scripts for all 7 pipeline stages. Each script:
- Accepts `--pipeline` argument (e.g., `--pipeline calgold`)
- Reads config from `pipeline/config/{pipeline}/`
- Reads/writes data from `pipeline/data/{pipeline}/`
- Supports `--database` argument for Firestore target (default: staging)
- Implements checkpoint/resume pattern

### 4.1 phase1_acquire.py

```fish
# Stub: downloads audio from YouTube playlist
# Input: pipeline/config/{pipeline}/playlist_urls.txt
# Output: pipeline/data/{pipeline}/audio/*.mp3
```

### 4.2 phase2_transcribe.py

```fish
# Stub: transcribes audio to timestamped JSON
# Input: pipeline/data/{pipeline}/audio/*.mp3
# Output: pipeline/data/{pipeline}/transcripts/*.json
# Requires: NVIDIA CUDA (NZXTcos or tsP3-cos)
```

### 4.3 phase3_extract.py

```fish
# Stub: extracts structured entities via Gemini Flash API
# Input: pipeline/data/{pipeline}/transcripts/*.json
#        pipeline/config/{pipeline}/extraction_prompt.md
# Output: pipeline/data/{pipeline}/extracted/*.json
```

### 4.4 phase4_normalize.py

```fish
# THIS IS THE KEY SCRIPT - Thompson Schema normalization
# Input: pipeline/data/{pipeline}/extracted/*.json
#        pipeline/config/{pipeline}/schema.json
# Output: pipeline/data/{pipeline}/normalized/*.jsonl
# Logic: Read schema.json indicators, populate all t_any_* fields
```

### 4.5 phase5_geocode.py

```fish
# Stub: geocodes entities via Nominatim
# Input: pipeline/data/{pipeline}/normalized/*.jsonl
# Output: pipeline/data/{pipeline}/geocoded/*.jsonl
# Rate limit: 1 req/sec
```

### 4.6 phase6_enrich.py

```fish
# Stub: enriches entities via Google Places API
# Input: pipeline/data/{pipeline}/geocoded/*.jsonl
# Output: pipeline/data/{pipeline}/enriched/*.jsonl
# Populates: t_enrichment.google_places and t_enrichment.nominatim
```

### 4.7 phase7_load.py

```fish
# Stub: loads enriched JSONL into Firestore
# Input: pipeline/data/{pipeline}/enriched/*.jsonl
# Target: --database staging (default) or --database "(default)"
# Creates: documents in locations/ collection, updates pipelines/ registry
```

### 4.8 thompson_schema.py (utility)

```fish
# Core normalization utility
# Functions:
#   normalize_entity(raw: dict, schema: dict) -> dict
#   generate_row_id(pipeline_id: str, entity: dict) -> str
#   tokenize_for_search(text: str) -> list[str]
#   compute_geohashes(lat: float, lon: float) -> list[str]
#   lowercase_array(arr: list) -> list[str]
```

**Success criteria:** All 7 phase scripts + thompson_schema.py exist. Each imports successfully (`python3 -c "import scripts.phase1_acquire"`). phase4_normalize.py reads schema.json and produces a valid normalized entity when given a mock input.

---

## Step 5: Thompson Schema Validation

### 5.1 Create Test Entity

Create a mock extracted entity for Watts Towers and run it through the normalization pipeline to validate the Thompson Schema output.

```fish
cd pipeline
python3 -c "
from scripts.utils.thompson_schema import normalize_entity
import json

# Mock extracted entity
raw = {
    'name': 'Watts Towers',
    'description': '17 interconnected sculptural towers built by Italian immigrant Simon Rodia',
    'city': 'Los Angeles',
    'state': 'CA',
    'county': 'Los Angeles',
    'historical_period': '1921-1954',
    'builder': 'Simon Rodia',
    'designation': 'National Historic Landmark',
    'huell_quote': 'This is AMAZING!',
    'episode_categories': ['art', 'architecture', 'history'],
    'aka_names': ['Nuestro Pueblo'],
    'visits': [{'video_id': 'test123', 'video_title': 'Watts Towers', 'timestamp_start': 45.0}]
}

# Load schema
with open('config/calgold/schema.json') as f:
    schema = json.load(f)

# Normalize
result = normalize_entity(raw, schema)
print(json.dumps(result, indent=2))
"
```

### 5.2 Validate Output

The output MUST contain:
- All `t_*` standard fields (t_log_type, t_row_id, t_event_time, t_parse_time, t_source_label, t_schema_version)
- All `t_any_*` indicator arrays populated from the schema.json mappings
- `t_any_names` contains ["watts towers", "nuestro pueblo"]
- `t_any_people` contains ["simon rodia", "huell howser"]
- `t_any_cities` contains ["los angeles"]
- `t_any_states` contains ["ca"]
- `t_any_categories` contains ["art", "architecture", "history"]
- `t_any_keywords` contains tokenized description terms
- All values lowercase in t_any arrays
- `source` contains the original raw entity
- No t_enrichment yet (enrichment happens in phase 5-6)

### 5.3 Load Test Entity to Staging

```fish
python3 scripts/phase7_load.py --pipeline calgold --database staging --input test_entity.jsonl
```

Verify in Firebase Console: staging database -> locations collection -> document exists with all t_any fields.

**Success criteria:** Test entity loads to staging Firestore. All t_any fields populated correctly. Document is queryable via Firebase Console.

---

## Step 6: Cloud Function Stub

### 6.1 Write Search Function

Create `functions/src/search.ts` with a minimal search endpoint:

```typescript
// Accepts: { query: string, filters: object, limit: number }
// Returns: { results: array, total: number }
// Phase 0: Simple pass-through to Firestore array-contains on t_any_keywords
// Phase N: Add fuzzy search, geo-radius, multi-array, Gemini NLP
```

### 6.2 Deploy to Firebase

```fish
cd functions
npm run build
firebase deploy --only functions
```

### 6.3 Test

```fish
curl -X POST https://us-central1-kjtcom-c78cd.cloudfunctions.net/search \
  -H "Content-Type: application/json" \
  -d '{"query": "watts towers", "limit": 10}'
```

**Success criteria:** Cloud Function deploys. Returns the test Watts Towers entity when queried with "watts towers".

---

## Step 7: Post-Flight Verification

### Tier 1 - Standard Health

```
[ ] Monorepo directory structure matches design doc Section 10
[ ] .gitignore covers all data directories and node_modules
[ ] CLAUDE.md points to current design + plan (v0.5)
[ ] Firebase project kjtcom-c78cd exists and is on Blaze
[ ] (default) and staging databases exist in kjtcom-c78cd
[ ] Security rules deployed (read-only public)
[ ] All pipeline scripts import without error
[ ] thompson_schema.py normalize_entity produces valid output
[ ] Test entity exists in staging Firestore with all t_any fields
[ ] Cloud Function deploys and responds to search query
[ ] No firebase deploy errors
[ ] flutter analyze clean (if Flutter app scaffolded)
```

### Tier 2 - Phase 0 Functional Playbook

```
[ ] pipeline/config/calgold/schema.json is valid JSON
[ ] pipeline/config/calgold/extraction_prompt.md is non-empty
[ ] pipeline/config/calgold/playlist_urls.txt has 400+ entries
[ ] Thompson Schema test: t_any_names, t_any_people, t_any_cities populated correctly
[ ] Thompson Schema test: all values lowercase in t_any arrays
[ ] Thompson Schema test: t_any_keywords contains tokenized description terms
[ ] Firestore staging: test document queryable by t_any_keywords array-contains
[ ] Firestore staging: test document queryable by t_log_type equality
[ ] Cloud Function: returns results for "watts towers" query
[ ] yt-dlp --flat-playlist succeeds for CalGold playlist URL
```

---

## Step 8: Produce Artifacts

### 8.1 Build Log

Write `docs/calgold-build-v0.5.md` - session transcript.

### 8.2 Report

Write `docs/calgold-report-v0.5.md` with:
- Entity count: 0 (Phase 0 is scaffold only)
- Video count validated: {from yt-dlp}
- Interventions: {count and description}
- Orchestration report: which agents/tools used
- Recommendation for Phase 1

### 8.3 Changelog

Write `docs/calgold-changelog-v0.5.md`:
```
**v0.5 (Phase 0 - Scaffold)**
- Repo: git@github.com:SOC-Foundry/kjtcom.git
- Firebase: kjtcom (kjtcom-c78cd) under socfoundry.com, Blaze billing
- Monorepo scaffolded: app/, pipeline/, functions/, docs/
- Multi-database configured: (default) + staging
- Thompson Schema (t_any_*) designed and validated with test entity
- CalGold pipeline config: schema.json (14 indicator mappings), extraction_prompt.md
- Cloud Functions search endpoint deployed (stub)
- 7 pipeline stage scripts stubbed with --pipeline and --database arguments
- {count} CalGold playlist URLs validated via yt-dlp
```

---

## Phase 1 Preview

Phase 1 will be a Discovery batch - 30 videos from the CalGold playlist processed through the full pipeline. Same progressive batching strategy as TripleDB.

**Phase 1 target:**
- Download 30 videos (yt-dlp)
- Transcribe 30 videos (faster-whisper CUDA)
- Extract locations (Gemini Flash API + extraction_prompt.md)
- Normalize with Thompson Schema (phase4 + schema.json)
- Geocode via Nominatim
- Load to staging Firestore
- Validate t_any fields queryable
- Zero interventions target

---

## Environment Variables Required

```fish
# fish config (~/.config/fish/config.fish)
set -gx GEMINI_API_KEY "..."
set -gx GOOGLE_PLACES_API_KEY "..."
set -gx GOOGLE_APPLICATION_CREDENTIALS "$HOME/.config/firebase/kjtcom-c78cd-sa.json"
set -gx LD_LIBRARY_PATH /usr/lib/python3.12/site-packages/nvidia/cublas/lib:/usr/lib/python3.12/site-packages/nvidia/cudnn/lib $LD_LIBRARY_PATH
set -gx CHROME_EXECUTABLE (which google-chrome-stable)
```

**Kyle manual step:** Download service account key from GCP Console -> IAM -> Service Accounts for kjtcom-c78cd project. Save to the path above. Do NOT commit this file.

---

## Hardware Assignment

| Step | Machine | Reason |
|------|---------|--------|
| All Phase 0 steps | NZXTcos | Primary dev. CUDA available for transcription validation. |
| Step 0 (yt-dlp) | NZXTcos | Consistent environment. Could run on any machine. |
| Step 5.3 (staging load) | NZXTcos | Firebase Admin SDK needs service account credentials for kjtcom-c78cd. |
| Step 6 (Cloud Functions) | NZXTcos | Node.js + Firebase CLI. Deploy to kjtcom-c78cd. |
