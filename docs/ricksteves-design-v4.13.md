# RickSteves - Design v4.13 (Phase 4 - Validation + Schema v3)

**Pipeline:** ricksteves (Rick Steves' Europe)
**Phase:** 4 (Validation)
**Iteration:** 13 (global counter)
**Executor:** Gemini CLI (Schema prep + Phases 1-5) + Claude Code (Phases 6-7)
**Date:** March 2026

---

## Objective

Migrate the RickSteves pipeline to Thompson Schema v3 and process videos 121-150 (30 new). Re-extract ALL 150 RickSteves transcripts with the v3 prompt so every entity gets the 7 new fields. This is the last gate before Phase 5 production runs for both pipelines.

---

## Schema v3 - New Fields

The script enhancements (continent lookup in phase4_normalize.py, county parsing in phase5_geocode.py) were already made in v4.12 and carry forward. Only the RickSteves-specific config files need updating.

| Field | Type | Description | RickSteves Example |
|-------|------|-------------|-------------------|
| t_any_actors | array[string] | Named people featured | ["Rick Steves", "local guide name"] |
| t_any_roles | array[string] | Normalized role types | ["host", "guide", "chef", "artisan"] |
| t_any_shows | array[string] | Show name(s) | ["Rick Steves' Europe"] |
| t_any_cuisines | array[string] | Cuisine categories | ["French", "Italian", "Tapas"] |
| t_any_dishes | array[string] | Specific food items | ["croissant", "gelato", "paella"] |
| t_any_eras | array[string] | Historical periods | ["Medieval", "Renaissance", "Roman"] |
| t_any_continents | array[string] | Continent(s) | ["Europe"] or ["Africa"] |

**t_any_shows is new for v4.13.** Not present in v4.12 CalGold run. After v4.13 completes, CalGold entities should also be backfilled with t_any_shows: ["California's Gold"]. This can be done as a simple Firestore update during post-flight or deferred to v5 production.

**t_any_counties:** Nominatim returns county-equivalent administrative divisions for some European countries but not all. Expected lower population rate than CalGold (~84%). Not a concern -- regions (t_any_regions) serve the same purpose for international content.

---

## Architecture Decisions

[DECISION] **Full Re-Extraction.** ALL 150 RickSteves transcripts (videos 1-150) get re-extracted with the updated v3 extraction prompt. Phases 1-2 are incremental (only new videos 121-150). Phases 3-5 re-process ALL 150.

[DECISION] **Checkpoint Resets Before Phase 6.** Learned from v4.12: enrichment and load checkpoints from v3.11 will be stale (schema v2, 120 files). Plan MUST specify resetting both checkpoints before running phases 6-7. This prevents the intervention that occurred in v4.12.

[DECISION] **CalGold t_any_shows Backfill.** After v4.13 validates t_any_shows on RickSteves, backfill all CalGold entities with t_any_shows: ["California's Gold"]. This is a simple Firestore batch update, not a full re-extraction.

[DECISION] **Split-Agent Model (Proven x4).** Same pattern. Gemini CLI phases 1-5. Claude Code phases 6-7 + artifacts.

[DECISION] **Schema v3 Locked After v4.13.** No more field additions until Phase 10 retrospective. The 7 new fields plus the counties enhancement are sufficient for TripleDB and Bourdain pipeline onboarding.

---

## Success Criteria

| Criteria | Target | Measurement |
|----------|--------|-------------|
| Acquisition (new) | 30/30 (100%) | Audio file count delta |
| Transcription (new) | 30/30 (100%) | Transcript file count delta |
| Re-extraction (all) | 150/150 (100%) | All extracted JSON contains v3 fields |
| Geocoding | >95% | Nominatim + Places backfill |
| Enrichment | >95% | Google Places API |
| t_any_actors populated | >90% | All should include "Rick Steves" |
| t_any_shows populated | 100% | All should be ["Rick Steves' Europe"] |
| t_any_continents populated | 100% | Derived from t_any_countries |
| t_any_counties populated | >40% | Lower target for international content |
| t_schema_version | 3 on ALL entities | Firestore query |
| Interventions (Gemini) | 0 | Count |
| Interventions (Claude) | 0 | Count |
| Security | Zero API keys | grep scan |
| Artifacts | 4 mandatory docs | build, report, changelog, README |

---

## Gotchas Active

| ID | Gotcha | Prevention |
|----|--------|-----------|
| G2 | LD_LIBRARY_PATH for CUDA | RESOLVED - in script + config.fish |
| G11 | API key leaks | NEVER cat config.fish |
| G13 | Nominatim misses niche names | Google Places backfill |
| G18 | Gemini 5-min timeout | Background transcription |
| G19 | Gemini runs bash | fish -c wrappers |
| G20 | Config.fish contains keys | grep only, never cat |
| G21 | CUDA OOM dual process | ONE transcription at a time |
| G22 | fish ls color codes | command ls or Python |
| G24 | Checkpoint staleness on re-extraction | Reset enrichment + load checkpoints before Phase 6 |

---

## Execution Flow

```
Gemini CLI (Section A):
  Step 0: Pre-flight
  Step 0.5: Schema v3 config changes (RickSteves-specific)
    - Update pipeline/config/ricksteves/schema.json (add 7 fields including t_any_shows)
    - Update pipeline/config/ricksteves/extraction_prompt.md (v3 output format)
    - Continent lookup + county parsing already in shared scripts from v4.12
  Step 1: Acquire videos 121-150 (30 new, checkpoint skips 1-120)
  Step 2: Transcribe videos 121-150 (30 new, background job)
  Step 3: Re-extract ALL 150 videos with v3 prompt
  Step 4: Re-normalize ALL 150 (continent lookup active)
  Step 5: Re-geocode ALL 150 (county parsing active)
  Handoff checkpoint

Claude Code (Section B):
  Step 5.5: Reset enrichment + load checkpoints (G24)
  Step 6: Re-enrich ALL 150
  Step 7: Re-load ALL 150 (schema v3)
  Step 7.5: Backfill CalGold t_any_shows (if time permits)
  Step 8: Post-flight (validate v3 fields)
  Step 9: Artifacts (4 mandatory)
```

---

## Phase Structure Reference

| Phase | Name | Status |
|-------|------|--------|
| 0 | Scaffold & Environment | DONE (v0.5) |
| 1 | Discovery (30 videos) | DONE (v1.6, v1.7) |
| 2 | Calibration (60 videos) | DONE (v2.8, v2.9) |
| 3 | Stress Test (90 videos) | DONE (v3.10, v3.11) |
| 4 | Validation + Schema v3 (120 videos) | DONE CalGold (v4.12), IN PROGRESS RickSteves (v4.13) |
| 5 | Production Run (full datasets) | Pending |
| 6 | Flutter App | Pending |
| 7 | Firestore Load | Pending |
| 8 | Enrichment Hardening | Pending |
| 9 | App Optimization | Pending |
| 10 | Retrospective + Template | Pending |
