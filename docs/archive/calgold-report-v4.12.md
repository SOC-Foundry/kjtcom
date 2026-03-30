# CalGold - Report v4.12 (Phase 4 - Validation + Schema v3)

**Pipeline:** calgold
**Phase:** 4 (Validation)
**Iteration:** 12 (global counter)
**Date:** 2026-03-30

---

## Metrics

| Metric | Phase 1 (v1.6) | Phase 2 (v2.8) | Phase 3 (v3.10) | Phase 4 (v4.12) | Cumulative |
|--------|----------------|----------------|-----------------|-----------------|------------|
| Videos processed | 30 | 60 | 90 | 120 | 120 |
| New batch size | 30 | 30 | 30 | 30 | - |
| Acquired | 30/30 (100%) | 30/30 (100%) | 30/30 (100%) | 30/30 (100%) | 120/120 (100%) |
| Transcribed | 30/30 (100%) | 30/30 (100%) | 30/30 (100%) | 30/30 (100%) | 120/120 (100%) |
| Extracted | 30/30 (100%) | 30/30 (100%) | 30/30 (100%) | 120/120 (100%) re-extracted | 120/120 (100%) |
| Total entities | 57 | 162 | 226 | 296 | 296 |
| Unique entities (Firestore) | 56 | 218 | 218 | 300 | 300 |
| Multi-visit merges | 1 | 3 | 5 | - | - |
| Geocoding (Nominatim only) | 43% | ~35% | 33% | - | - |
| Geocoding (after Places backfill) | 43% | 97% | 98% | 97.6% | 97.6% (289/296) |
| Enrichment (Google Places) | 100% | 97% | 98% | 97.6% | 97.6% (289/296) |
| Coords backfilled from Places | - | ~100 | 140 | 201 | 201 |
| Schema version | 1 | 2 | 2 | 3 | 3 |

---

## Schema v3 Field Population Rates

| Field | Target | Actual | Status |
|-------|--------|--------|--------|
| t_schema_version = 3 | 100% | 296/296 (100%) | PASS |
| t_any_actors populated | >90% | 296/296 (100%) | PASS |
| t_any_actors contains "Huell Howser" | >90% | 296/296 (100%) | PASS |
| t_any_roles populated | >90% | 296/296 (100%) | PASS |
| t_any_roles contains "host" | >90% | 296/296 (100%) | PASS |
| t_any_continents populated | 100% | 296/296 (100%) | PASS |
| t_any_continents = ["North America"] | 100% | 296/296 (100%) | PASS |
| t_any_counties populated | >80% | 249/296 (84.1%) | PASS |
| t_any_cuisines (food entities) | non-empty | 56/296 (18.9%) | PASS |
| t_any_dishes (food entities) | non-empty | 69/296 (23.3%) | PASS |
| t_any_eras (history entities) | non-empty | 244/296 (82.4%) | PASS |

**Notes on food/history fields:**
- 75 total food-related entities identified (cuisines or dishes non-empty)
- 244 total history-related entities identified (eras non-empty)
- These are contextual fields - not all CalGold locations involve food or history. The population rates reflect the content, not extraction quality.

---

## Agent Performance

| Metric | Gemini CLI (Schema + Phases 1-5) | Claude Code (Phases 6-7) |
|--------|----------------------------------|--------------------------|
| Phases executed | 0.5 (schema v3), 1, 2, 3, 4, 5 | 6, 7, post-flight, artifacts |
| Interventions | 0 | 1 |
| Errors encountered | 0 | 0 |
| Plan corrections needed | 0 | 1 (checkpoint reset for full re-enrichment) |
| Execution mode | --yolo | --dangerously-skip-permissions |

**Intervention detail (Claude Code):** The enrichment and load checkpoints retained 90 entries from v3.10. Since v4.12 re-extracted ALL 120 videos with the v3 prompt, the old 90 enriched files were stale (schema v2, no new fields). Claude Code detected this by inspecting file timestamps and field presence, reset both checkpoints, and re-ran enrichment and load for all 120. This is a plan gap - the plan should have specified checkpoint resets before Phase 6.

**Split-agent model assessment:** Fourth consecutive execution of the Gemini/Claude split model. Gemini CLI handled the expanded scope (schema v3 config changes + full re-extraction of all 120 videos) with zero interventions. The schema migration (prompt updates, script enhancements, full re-extraction) was well-suited to Gemini CLI's mechanical execution strength. Claude Code's single intervention was a legitimate detection of stale state that the plan did not account for.

---

## Enrichment Misses (7 entities)

| Entity | Reason |
|--------|--------|
| Brotherhood Raceway Park | Defunct raceway - no Places listing |
| Sombrero Canyon Debris Basin | Niche flood control infrastructure |
| Sombrero Canyon Flood Control Debris Basin | Variant name of above |
| Zanja Madre (Mother Ditch) Section | Historic water channel |
| Los Angeles Storm Drain System segments | Underground infrastructure |
| Arroyo Seco Channel | Flood control channel |
| Death Valley Temporary Lake | Ephemeral natural feature |

All misses are consistent with G13 (niche locations without Google Places presence).

---

## Design Doc Estimate vs Actual

| Metric | Design Target | Actual | Status |
|--------|--------------|--------|--------|
| Acquisition (new batch) | 30/30 (100%) | 30/30 (100%) | MET |
| Re-extraction (all) | 120/120 (100%) | 120/120 (100%) | MET |
| Geocoding | >95% | 97.6% | EXCEEDED |
| Enrichment | >95% | 97.6% | EXCEEDED |
| t_any_actors populated | >90% | 100% | EXCEEDED |
| t_any_continents populated | 100% | 100% | MET |
| t_any_counties populated | >80% | 84.1% | MET |
| t_schema_version = 3 | 100% | 100% | MET |
| Interventions (Gemini) | 0 | 0 | MET |
| Interventions (Claude) | 0 | 1 | MISSED |
| Security | Zero API keys | Zero API keys | MET |

---

## Gotcha Status

| ID | Status | Notes |
|----|--------|-------|
| G2 | **Resolved** | LD_LIBRARY_PATH embedded - zero CUDA failures across 4 phases |
| G11 | Active | No API key leaks detected |
| G13 | Active | 7 niche misses as expected |
| G18 | Active | Gemini used background transcription |
| G19 | Active | Gemini used fish -c correctly |
| G20 | Active | No config.fish reads detected |
| G21 | Active | Single transcription process, no OOM |
| G22 | Active | Used `command ls` throughout |
| **NEW** | Active | Checkpoint staleness across iterations - plan should specify checkpoint resets when re-processing all files |

---

## Recommendation for Phase 5

**PROCEED to Phase 5 (Production Run).**

Rationale:
1. **Schema v3 validated.** All 6 new fields populate at or above target rates across 296 entities from 120 videos. t_any_actors (100%), t_any_continents (100%), t_any_counties (84.1%), t_any_cuisines/dishes/eras (contextually appropriate).
2. **Full re-extraction successful.** ALL 120 videos re-extracted with the v3 prompt - no data loss, no field regression, every entity at t_schema_version: 3.
3. **Pipeline stability confirmed.** 4 consecutive phases with 100% acquisition, transcription, and extraction rates. Geocoding and enrichment stable at ~98%.
4. **G2 permanently resolved.** Zero CUDA failures across all 4 phases.
5. **Split-agent model proven x4.** Gemini CLI handled schema migration + mechanical phases. Claude Code handled enrichment, load, validation, and artifacts. One intervention (checkpoint staleness) is a plan gap, not a pipeline deficiency.
6. **Cross-pipeline readiness.** Script enhancements (continent lookup, county parsing) carry forward to RickSteves v4.13. Only extraction_prompt.md needs per-pipeline customization.

**Phase 5 scope:** Process remaining ~311 CalGold videos (121-431) in production batches. Schema v3 is validated and ready for scale. RickSteves should be migrated to schema v3 via v4.13 before or in parallel with CalGold Phase 5.

---

## Platform Totals

| Pipeline | Entities | Countries | Schema Version |
|----------|----------|-----------|----------------|
| CalGold | 300 | 1 (US) | 3 |
| RickSteves | 669 | 30 | 2 |
| **Total** | **969** | **30** | **Mixed (v2/v3)** |
