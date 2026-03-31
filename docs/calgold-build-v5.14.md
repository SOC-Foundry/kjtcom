# CalGold - Build Log v5.14 (Phase 5 - Production Run)

**Pipeline:** calgold
**Phase:** 5 (Production Run)
**Iteration:** 14 (global counter)
**Date:** March 30-31, 2026
**Executor:** tmux (phases 1-5) + Claude Code Opus 4.6 (phases 6-7)

---

## Pre-Flight

- [x] Runner script `group_b_runner.sh` created and validated
- [x] TRANSCRIBE_TIMEOUT env var confirmed in phase2_transcribe.py
- [x] LD_LIBRARY_PATH set in script and config.fish
- [x] 431 playlist URLs in pipeline/config/calgold/playlist_urls.txt
- [x] 120 videos already processed through v4.12/v4.13 (schema v3)

---

## Pass 1 - 600s Timeout

**Started:** Mon Mar 30 09:39:12 AM PDT 2026
**Result:** CUDA OOM crash after 109 new transcripts

| Metric | Count |
|--------|-------|
| New transcripts | 109 |
| Acquire failures | 41 (private/terminated YouTube videos) |
| Timeouts | 0 |
| Errors | 1 (CUDA OOM on video QyMgjb8dBRQ) |

The pass crashed during transcription of video QyMgjb8dBRQ with `RuntimeError: CUDA failed with error out of memory`. Checkpoint resume allowed pass 2 to continue where pass 1 left off.

---

## Pass 2 - 1200s Timeout

**Started:** Mon Mar 30 03:37:03 PM PDT 2026
**Finished:** Mon Mar 30 10:35:30 PM PDT 2026
**Runtime:** ~7 hours

| Metric | Count |
|--------|-------|
| Total audio | 390 |
| Total transcripts | 390 |
| Total extractions | 390 |
| Total normalized | 390 |
| Total geocoded | 390 |
| New geocoded (this pass) | 161 |

Pass 2 completed all remaining videos. No pass 3 was needed - all 390 acquirable videos were fully processed in 2 passes.

---

## Pass 3 - Not Required

All 390 acquirable videos completed in passes 1-2. The 41 missing videos (431 - 390) are YouTube-side failures:
- Private videos (sign-in required): 5
- Terminated accounts: 4
- Other unavailable: 32

These are genuine platform gaps, not pipeline failures.

---

## Quality Sweep (Section E)

Run after pass 2 completion. Re-normalized and re-geocoded the full dataset.

| Metric | Value |
|--------|-------|
| Total geocoded files | 390 |
| Total entities | 829 |
| Geocoded (pre-enrichment) | 257 (31%) |
| Schema v3 | 829 (100%) |
| Has actors | 829 (100%) |
| Has continents | 829 (100%) |

The 31% pre-enrichment geocoding rate is expected for CalGold - Nominatim struggles with niche California landmarks. Google Places backfill in phase 6 addresses this.

---

## Checkpoint Reset (G24/G25)

Before running phases 6-7, reset stale checkpoints:

```
rm pipeline/data/calgold/.checkpoint_enrich.json
rm pipeline/data/calgold/.checkpoint_load.json
```

Both files confirmed removed before phase 6 launch.

---

## Phase 6 - Enrich

**Executor:** Claude Code (Opus 4.6)
**Command:** `python3 pipeline/scripts/phase6_enrich.py --pipeline calgold`

| Metric | Value |
|--------|-------|
| Files enriched | 390/390 |
| Entities enriched | 829 |
| Geocoded (post-enrichment) | 795 (95%) |
| Google Places matched | 795 (95%) |
| Coordinate backfills | 538 (from 31% -> 95%) |
| Not enriched | 34 (4%) |

The 34 unenriched entities are niche/historic California locations that Google Places cannot match (debris basins, private facilities, demolished buildings, etc.).

---

## Phase 7 - Load to Staging

**Executor:** Claude Code (Opus 4.6)
**Command:** `python3 pipeline/scripts/phase7_load.py --pipeline calgold --database staging`

| Metric | Value |
|--------|-------|
| Files loaded | 390 |
| Documents loaded | 829 |
| Unique entities in staging | 899 |
| Dedup merges | ~70 (829 loaded + existing -> 899 unique) |

---

## CalGold t_any_shows Backfill

Backfilled all CalGold entities with `t_any_shows: ["California's Gold"]`:

| Metric | Value |
|--------|-------|
| Total CalGold entities | 899 |
| Updated (new) | 778 |
| Already had t_any_shows | 121 (from v4.13 backfill) |

---

## Post-Flight Checklist

- [x] Security: `grep -rnI "AIzaSy" .` -> only doc references (5 matches, all in docs/ and CLAUDE.md)
- [x] Total CalGold entities in staging: 899
- [x] All entities at t_schema_version: 3 (100%)
- [x] Geocoding rate: 95% (795/829)
- [x] Enrichment rate: 95% (795/829)
- [x] t_any_shows backfill: 899/899 (100%)
- [x] Cross-pipeline: 1,934 total entities (899 CalGold + 1,035 RickSteves)

---

## Platform Totals

| Pipeline | Entities | Status |
|----------|----------|--------|
| CalGold | 899 | Phase 5 DONE |
| RickSteves | 1,035 | Phase 4 DONE |
| **Total** | **1,934** | |
