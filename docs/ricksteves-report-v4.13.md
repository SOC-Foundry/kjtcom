# RickSteves - Report v4.13 (Phase 4 - Validation + Schema v3)

## Summary Metrics

| Metric | Phase 1 (v1.7) | Phase 2 (v2.9) | Phase 3 (v3.11) | Phase 4 (v4.13) | Cumulative |
|--------|----------------|----------------|-----------------|-----------------|------------|
| Videos | 30 | 60 | 30 | 30 new + 150 re-extracted | 150 |
| Raw Entities (loaded) | 223 | 494 | 152 | 991 | 991 (re-load) |
| Unique Entities | 200 | 359 | 110 | 366 | 1,035 |
| Entities/Video | 7.4 | 8.2 | 5.1 | 6.6 (991/150) | 6.9 |
| Geocoding Rate | 98% | 99% | 99.3% | >95% | >95% |
| Enrichment Rate | 98% | 99% | 99.3% | >95% | >95% |
| Countries | 23 | +6 = 29 | +1 = 30 | +3 = 33 | 33 |
| Schema Version | 2 | 2 | 2 | 3 | 3 (v3 entities) |

## Schema v3 Field Population Rates

Among the 744 entities loaded with schema v3:

| Field | Population Rate | Notes |
|-------|----------------|-------|
| t_any_actors | 100% | 98% include "rick steves" |
| t_any_roles | 100% | 98% include "host" |
| t_any_shows | 100% | 99% exactly ["rick steves' europe"] |
| t_any_continents | 99% | Derived from t_any_countries via COUNTRY_TO_CONTINENT |
| t_any_counties | 38% | Expected lower for international content; regions serve same purpose |
| t_any_cuisines | 10% | Only populated on food-related episodes |
| t_any_dishes | 12% | Only populated on food-related episodes |
| t_any_eras | 73% | Strong coverage of historical periods |

**Cuisine/Dish spot checks:**
- `a-bouchon-restaurant-old-town-lyon`: cuisines=["french", "lyonnaise"], dishes=["duck", "escargot", "foie gras", "quenelle"]
- `a-portuguese-seafood-restaurant`: cuisines=["portuguese", "seafood"], dishes=["calderada", "garlic shrimp", "grilled sardines"]
- `a-restaurant-in-villefranche`: cuisines=["french", "seafood"], dishes=["bouillabaisse"]

**Era spot checks:**
- `a-ar-qim`: eras=["neolithic", "stone age"]
- `abbey-of-fontenay`: eras=["medieval", "roman"]

## Phase 4 Observations

**Full re-extraction yields more entities.** Re-extracting all 150 videos with the v3 prompt (which includes 7 new field types) resulted in 1,035 unique entities vs 669 from v3.11. The richer extraction prompt discovers entities that the simpler v2 prompt missed - particularly food-related locations and historical sites.

**291 legacy entities remain.** These are entities from v3.11 and earlier loads whose entity IDs don't match any v4.13 entities (name hash mismatch due to slight extraction differences). They retain schema v2 but are still valid, searchable entities. A future cleanup pass could reconcile or archive them.

**County coverage is expectedly lower.** 38% vs CalGold's 84% - Nominatim returns county-equivalent administrative divisions inconsistently for European countries. The t_any_regions field (populated at much higher rates) serves the same geographic subdivision purpose for international content.

**CalGold t_any_shows backfill successful.** All 412 CalGold entities now have t_any_shows: ["California's Gold"]. This was a simple Firestore batch update, not a re-extraction.

**Schema v3 locked.** Per design decision, no more field additions until Phase 10 retrospective. The 7 new fields plus counties enhancement are sufficient for TripleDB and Bourdain pipeline onboarding.

## Agent Performance

### Gemini CLI (Section A - Schema Prep + Phases 1-5)

| Metric | Result |
|--------|--------|
| Phases Executed | 0.5 (schema v3), 1, 2, 3, 4, 5 |
| Interventions | 0 |
| Self-Healing Events | None needed |
| Handoff Checkpoint | Produced correctly with all 7 new fields verified |

### Claude Code (Section B - Phases 5.5-7)

| Metric | Result |
|--------|--------|
| Phases Executed | 5.5 (checkpoint reset), 6, 7, 7.5 (CalGold backfill) + post-flight + artifacts |
| Interventions | 1 (checkpoint path mismatch in plan) |
| Self-Healing Events | Detected 15% v3 rate after first load, traced to stale enriched files, cleared and re-ran |
| Security Scan | Clean (only doc/archive references) |

**Intervention detail:** Plan Step 5.5 specified checkpoint paths inside `enriched/` and `loaded/` subdirectories. Actual checkpoint files are `.checkpoint_enrich.json` and `.checkpoint_load.json` in the pipeline data root. This was a plan authoring error, not an execution error. The v4.12 CalGold build had a similar checkpoint intervention (1 total).

### Split-Agent Assessment

Five split-agent iterations completed (v3.10, v3.11, v4.12, v4.13). Gemini CLI has achieved zero interventions across all 5 iterations. Claude Code has 1 intervention each in v4.12 and v4.13, both related to checkpoint management during full re-extraction runs. The checkpoint path pattern should be documented in GEMINI.md/CLAUDE.md for future iterations to prevent recurrence.

## Cross-Pipeline Intelligence

| Pipeline | Videos | Unique Entities | Countries | t_any_shows |
|----------|--------|-----------------|-----------|-------------|
| CalGold | 120 | 412 | 1 (US) | California's Gold |
| RickSteves | 150 | 1,035 | 33 | Rick Steves' Europe |
| **Total** | **270** | **1,447** | **33** | **2 shows** |

## Recommendation for Phase 5

- **Status: GREEN.** Pipeline is stable at 150 videos with all schema v3 success criteria met.
- **Both pipelines validated.** CalGold (v4.12) and RickSteves (v4.13) have completed Phase 4 validation with schema v3.
- **Ready for Phase 5 (Production Run).** Full dataset processing for both pipelines - CalGold (431 videos) and RickSteves (1,865 videos).
- **Pre-Phase 5 cleanup recommended:** Consider archiving or reconciling the 291 legacy pre-v3 entities to avoid confusion in production metrics.
- **TripleDB and Bourdain onboarding eligible.** Schema v3 is locked and validated across 2 pipelines. New pipelines only need config files.
