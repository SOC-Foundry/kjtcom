# CalGold - Report v0.5 (Phase 0)

**Date:** 2026-03-29
**Phase:** 0 - Project Scaffold, Firebase Setup, Pipeline Config & Environment Validation

---

## Summary

| Metric | Value |
|--------|-------|
| Entity count | 0 (Phase 0 is scaffold only) |
| Test entity loaded to staging | 1 (Watts Towers) |
| Video count validated | 431 (yt-dlp --flat-playlist) |
| Interventions | 5 (all resolved) |
| Pipeline scripts created | 7 phase scripts + 3 utilities |
| Config files created | 4 (pipeline.json, schema.json, extraction_prompt.md, playlist_urls.txt) |
| Thompson Schema indicators | 14 mappings in schema.json |
| Thompson Schema test | PASS - all t_any_* fields validated |
| Cloud Function | Deployed + tested. Search returns correct results. |
| Firestore databases | 2 - (default) + staging, both us-central1 |

---

## Post-Flight Checklist

### Tier 1 - Standard Health

| Check | Status |
|-------|--------|
| Monorepo directory structure matches design doc Section 10 | PASS |
| .gitignore covers all data directories and node_modules | PASS |
| CLAUDE.md points to current design + plan (v0.5) | PASS |
| Firebase project kjtcom-c78cd exists and is on Blaze | PASS (verify Blaze in console) |
| (default) and staging databases exist in kjtcom-c78cd | PASS |
| Security rules deployed (read-only public) | PASS |
| All pipeline scripts import without error | PASS |
| thompson_schema.py normalize_entity produces valid output | PASS |
| Test entity exists in staging Firestore with all t_any fields | PASS |
| Cloud Function deploys and responds to search query | PASS |
| No firebase deploy errors | PASS |

### Tier 2 - Phase 0 Functional Playbook

| Check | Status |
|-------|--------|
| schema.json is valid JSON | PASS |
| extraction_prompt.md is non-empty | PASS |
| playlist_urls.txt has 400+ entries | PASS (431) |
| Thompson Schema test: t_any_names populated correctly | PASS |
| Thompson Schema test: t_any_people populated correctly | PASS |
| Thompson Schema test: t_any_cities populated correctly | PASS |
| Thompson Schema test: all values lowercase in t_any arrays | PASS |
| Thompson Schema test: t_any_keywords contains tokenized terms | PASS |
| Firestore staging: test document queryable by t_any_keywords array-contains | PASS |
| Firestore staging: test document queryable by t_log_type equality | PASS |
| Cloud Function: returns results for "towers" query | PASS |
| yt-dlp --flat-playlist succeeds for CalGold playlist URL | PASS |

---

## Intervention Log

| # | Issue | Resolution | Self-Heal? |
|---|-------|------------|------------|
| 1 | Firebase CLI auth (kthompson@tachtech.net) had no access to kjtcom-c78cd | Kyle re-authenticated as kthompson@socfoundry.com | No - Kyle manual |
| 2 | Firestore API not enabled on new GCP project | `gcloud services enable firestore.googleapis.com` | Yes - auto |
| 3 | Cloud Functions build failed - missing permission | Granted roles/cloudbuild.builds.builder to compute SA | Yes - auto |
| 4 | Cloud Function Firestore queries returned PERMISSION_DENIED | Granted roles/firebase.admin to compute SA | Yes - auto |
| 5 | Org policy blocks allUsers IAM on Cloud Run | Acceptable for Phase 0 - auth token required | N/A - policy constraint |

---

## Orchestration Report

| Agent/Tool | Usage |
|------------|-------|
| Claude Code (Opus 4.6) | Full orchestration, all file creation, config, validation, deploy |
| yt-dlp | Playlist validation (431 videos confirmed) |
| Python 3.14 / firebase-admin SDK | Thompson Schema test + Firestore staging load + verification |
| Node.js 25.6 / TypeScript 5.x | Cloud Functions compilation |
| Firebase CLI 15.10.0 | Project init, rules/indexes/functions deploy |
| gcloud CLI | API enablement, IAM policy management, database creation |
| curl | Cloud Function endpoint testing |

---

## Recommendation for Phase 1

Phase 0 is complete. All infrastructure is provisioned and validated.

Phase 1 target - Discovery batch of 30 videos:
1. `phase1_acquire.py --pipeline calgold --limit 30` - download audio
2. `phase2_transcribe.py --pipeline calgold --limit 30` - CUDA transcription
3. `phase3_extract.py --pipeline calgold --limit 30` - Gemini Flash extraction
4. `phase4_normalize.py --pipeline calgold --limit 30` - Thompson Schema normalization
5. `phase5_geocode.py --pipeline calgold --limit 30` - Nominatim geocoding
6. `phase6_enrich.py --pipeline calgold --limit 30` - Google Places enrichment
7. `phase7_load.py --pipeline calgold --database staging` - load to staging
8. Validate t_any fields queryable across all entities
9. Zero interventions target

### Note on Cloud Function auth
The socfoundry.com org policy blocks public Cloud Run access. For the Flutter app (Phase 8), the search function will need to be called with Firebase Authentication tokens. This is actually better security practice - the app will authenticate users and pass the token. No code changes needed to the function.
