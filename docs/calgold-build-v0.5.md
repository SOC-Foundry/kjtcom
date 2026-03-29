# CalGold - Build Log v0.5 (Phase 0)

**Date:** 2026-03-29
**Executor:** Claude Code (Opus 4.6, YOLO mode)
**Machine:** NZXTcos (i9-13900K, RTX 2080 SUPER, 64 GB DDR4, CachyOS)

---

## Pre-Flight Validation

| Check | Result |
|-------|--------|
| GEMINI_API_KEY | SET |
| GOOGLE_PLACES_API_KEY | SET |
| Flutter | 3.41.4 (stable) |
| Dart | 3.11.1 (stable) |
| Python | 3.14.3 |
| Firebase CLI | 15.10.0 |
| yt-dlp | 2026.03.17 |
| faster-whisper | importable (CUDA) |
| nvidia-smi | NVIDIA GeForce RTX 2080 SUPER |
| Firebase auth | kthompson@socfoundry.com (re-authenticated from kthompson@tachtech.net) |

---

## Step 0: Validate YouTube Playlist

- Command: `yt-dlp --flat-playlist` on CalGold playlist
- Result: **431 videos** confirmed
- Output: `pipeline/config/calgold/playlist_urls.txt` (431 lines)

---

## Step 1: Scaffold Monorepo

- Created directory structure per design doc Section 10
- Root files: .gitignore, firebase.json, .firebaserc, firestore.rules, firestore.indexes.json, CLAUDE.md, GEMINI.md, README.md
- Pipeline dirs: scripts/, config/calgold/, data/calgold/{6 stages}/, agents/
- Functions: functions/src/, package.json, tsconfig.json
- Docs: docs/, docs/archive/
- All __init__.py files for Python package imports

---

## Step 2: Firebase Project Setup

- Re-authenticated as kthompson@socfoundry.com (initial auth was kthompson@tachtech.net - no access)
- `firebase init` completed - hosting configured (build/web)
- Enabled Firestore API via `gcloud services enable firestore.googleapis.com`
- Created (default) database in us-central1
- Created staging database in us-central1
- Deployed security rules (public read, admin write via SDK)
- Deployed 4 composite indexes
- Granted compute service account: roles/cloudbuild.builds.builder, roles/datastore.user, roles/firebase.admin

---

## Step 3: CalGold Pipeline Config

All four config files created in `pipeline/config/calgold/`:
- pipeline.json - pipeline metadata
- schema.json - 14 indicator mappings for Thompson Schema
- extraction_prompt.md - Gemini Flash extraction prompt
- playlist_urls.txt - 431 video IDs + titles

---

## Step 4: Pipeline Scripts

Created 7 phase scripts + 3 utilities:
- phase1_acquire.py - yt-dlp audio download with checkpoint
- phase2_transcribe.py - faster-whisper CUDA transcription
- phase3_extract.py - Gemini Flash entity extraction
- phase4_normalize.py - Thompson Schema normalization (KEY SCRIPT)
- phase5_geocode.py - Nominatim geocoding (1 req/sec)
- phase6_enrich.py - Google Places API enrichment
- phase7_load.py - Firestore load with --database flag
- utils/thompson_schema.py - normalize_entity, tokenize, geohash, row ID
- utils/checkpoint.py - resume support
- utils/geohash.py - geohash encoding

All scripts support: --pipeline, --limit, --database (phase7)
All scripts use checkpoint/resume pattern.

---

## Step 5: Thompson Schema Validation

Test entity: Watts Towers (mock extracted data)

| Field | Expected | Actual | Pass? |
|-------|----------|--------|-------|
| t_any_names | ["nuestro pueblo", "watts towers"] | ["nuestro pueblo", "watts towers"] | YES |
| t_any_people | ["huell howser", "simon rodia"] | ["huell howser", "simon rodia"] | YES |
| t_any_cities | ["los angeles"] | ["los angeles"] | YES |
| t_any_states | ["ca"] | ["ca"] | YES |
| t_any_counties | ["los angeles"] | ["los angeles"] | YES |
| t_any_categories | ["architecture", "art", "history"] | ["architecture", "art", "history"] | YES |
| t_any_keywords | tokenized description terms | 10 tokens including "national historic landmark" | YES |
| All values lowercase | yes | yes | YES |
| source preserved | yes | yes | YES |
| Default "huell howser" applied | yes | yes | YES |

Test entity loaded to staging Firestore:
- Document: calgold-watts-towers-82c2c9 in staging/locations
- Verified: array-contains query on t_any_keywords returns 1 result
- Verified: t_log_type equality query returns 1 result

---

## Step 6: Cloud Function

- functions/src/index.ts - search endpoint with array-contains on t_any_keywords
- TypeScript compiles clean
- Deployed to us-central1: https://search-rse3bxwgqa-uc.a.run.app
- Fixed: Cloud Build permissions (roles/cloudbuild.builds.builder)
- Fixed: Firestore access (roles/firebase.admin)
- Note: socfoundry.com org policy blocks allUsers/allAuthenticatedUsers IAM - function requires auth token
- Tested with auth token: query "towers" returns Watts Towers entity correctly

---

## Interventions

| # | Description | Resolution |
|---|-------------|------------|
| 1 | Firebase CLI authenticated as kthompson@tachtech.net - no access to kjtcom-c78cd | Kyle re-authenticated as kthompson@socfoundry.com |
| 2 | Firestore API not enabled on kjtcom-c78cd | Enabled via gcloud services enable |
| 3 | Cloud Functions build failed - missing permission on build service account | Granted roles/cloudbuild.builds.builder to compute SA |
| 4 | Cloud Function search returned 500 - Firestore permission denied | Granted roles/firebase.admin to compute SA |
| 5 | Org policy blocks allUsers IAM binding on Cloud Run | Function requires auth token (acceptable for Phase 0) |

---

## Tools Used

- Claude Code (Opus 4.6) - orchestration
- yt-dlp - playlist validation
- Python 3.14 - Thompson Schema normalization + Firestore staging load
- Node.js 25.6 / TypeScript 5.x - Cloud Functions
- Firebase CLI 15.10.0 - project init, deploy rules/indexes/functions
- gcloud CLI - API enablement, IAM policy, database creation
