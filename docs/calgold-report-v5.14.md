# CalGold - Report v5.14 (Phase 5 - Production Run)

**Pipeline:** calgold (California's Gold - Huell Howser)
**Phase:** 5 (Production Run)
**Iteration:** 14 (global counter)
**Date:** March 30-31, 2026

---

## Executive Summary

CalGold Phase 5 production run processed 390 out of 431 playlist videos (90.5% acquisition rate) through the full 7-phase pipeline. The 41 missing videos are YouTube-side failures (private/terminated), not pipeline issues. The dataset yielded 829 entities across 390 videos, with 899 unique entities in Firestore staging after dedup merges with existing data from phases 1-4.

---

## Cumulative Metrics (Phases 1-5)

| Metric | Phase 4 (v4.12) | Phase 5 (v5.14) | Delta |
|--------|-----------------|-----------------|-------|
| Videos processed | 120 | 390 | +270 |
| Total entities | 300 | 829 | +529 |
| Unique in staging | 412 | 899 | +487 |
| Geocoding rate | 97.6% | 95% | -2.6% |
| Enrichment rate | 97.6% | 95% | -2.6% |
| Schema v3 | 100% | 100% | - |
| Actors populated | 100% | 100% | - |
| Continents populated | 100% | 100% | - |
| Eras populated | 82.4% | 76% | -6.4% |

The slight dip in geocoding/enrichment rates at scale is expected - the long tail of niche California landmarks (debris basins, demolished buildings, private facilities) that Google Places cannot match grows proportionally with dataset size. The 95% rate exceeds the 95% target.

---

## Production Throughput

| Pass | Timeout | Videos Processed | Runtime | Outcome |
|------|---------|-----------------|---------|---------|
| Pass 1 | 600s | 109 (new transcripts) | ~6 hours | CUDA OOM crash |
| Pass 2 | 1200s | 281 (remaining) | ~7 hours | Complete |
| Pass 3 | 1800s | Not needed | - | Skipped |
| Quality sweep | N/A | 390 (all) | ~30 min | 829 entities |
| Enrich (Phase 6) | N/A | 390 files | ~5 min | 795/829 matched |
| Load (Phase 7) | N/A | 390 files | ~10 min | 899 unique |
| **Total** | | **390 videos** | **~14 hours** | |

### Throughput Analysis

- **Acquisition:** 390/431 (90.5%) - 41 unavailable on YouTube
- **Transcription:** 390/390 (100%) - all acquired videos transcribed
- **Extraction:** 390/390 (100%) - all transcripts extracted
- **Normalize + Geocode:** 390/390 (100%)
- **Enrichment:** 795/829 entities (95.9%)
- **Load:** 829/829 entities (100%)

The 2-pass approach (600s + 1200s) was sufficient for CalGold. Pass 1 crashed on CUDA OOM (G21) but checkpoint resume handled recovery cleanly. CalGold episodes are shorter than Rick Steves, so the 1800s pass was unnecessary.

---

## Schema v3 Field Population

| Field | Rate | Notes |
|-------|------|-------|
| t_any_actors | 100% | Huell Howser + guests |
| t_any_shows | 100% | Backfilled post-load |
| t_any_continents | 100% | All "north america" |
| t_any_eras | 76% | Not all episodes reference historical periods |
| t_any_categories | 100% | Landmark, museum, restaurant, etc. |
| t_any_keywords | 100% | Full keyword extraction |
| t_any_coordinates | 95% | After Google Places backfill |
| t_any_counties | ~80% | California county extraction |

---

## Gaps

### Unavailable Videos (41)

41 of 431 playlist URLs returned errors from YouTube:
- **Private videos** (5): Require sign-in, likely content creator restrictions
- **Terminated accounts** (4): Associated YouTube accounts no longer exist
- **Other unavailable** (32): Various YouTube-side removal reasons

These are platform-level gaps, not pipeline failures. Documented as-is.

### Unenriched Entities (34)

34 entities (4.1%) could not be matched by Google Places:
- Niche infrastructure (debris basins, water reclamation plants)
- Demolished/renamed buildings
- Private facilities and homes
- Hyper-local landmarks (parking lots, specific street corners)

This is consistent with CalGold's subject matter - Huell Howser frequently visited obscure California locations that don't have Google Places listings.

---

## Interventions

| Agent | Interventions | Details |
|-------|--------------|---------|
| tmux (phases 1-5) | 1 | CUDA OOM in pass 1, recovered via pass 2 checkpoint resume |
| Claude Code (phases 6-7) | 0 | Clean execution |
| **Total** | **1** | |

---

## Recommendations

1. **RickSteves Phase 5**: Ready to proceed. Use the same `group_b_runner.sh` with `ricksteves` pipeline. RickSteves episodes are longer, so expect 3 passes (600s, 1200s, 1800s) to be necessary.

2. **Enrichment hardening**: The 34 unenriched CalGold entities could benefit from a fallback geocoder (OpenCage, MapBox) or manual coordinate entry for high-value landmarks.

3. **t_any_shows extraction**: Currently backfilled post-load. Consider adding show name extraction to the CalGold extraction prompt for future re-runs.

---

## Platform Status

| Pipeline | Videos | Entities | Geocoded | Enriched | Status |
|----------|--------|----------|----------|----------|--------|
| CalGold | 390 | 899 | 95% | 95% | Phase 5 DONE |
| RickSteves | 150 | 1,035 | >95% | >95% | Phase 4 DONE |
| **Total** | **540** | **1,934** | | | |
