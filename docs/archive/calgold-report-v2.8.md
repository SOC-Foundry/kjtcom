# CalGold - Report v2.8 (Phase 2 - Calibration)

**Pipeline:** CalGold (California's Gold with Huell Howser)
**Phase:** 2 - Calibration (videos 31-60 + Phase 1 re-enrichment)
**Date:** 2026-03-29

---

## Phase 1 vs Phase 2 Comparison

| Metric | Phase 1 (v1.6) | Phase 2 (v2.8) | Delta |
|--------|----------------|----------------|-------|
| Videos processed | 30 | 60 (30 new) | +30 |
| Raw entities | 57 | 226 (169 new) | +169 |
| Entities/video | 1.9 | 2.5 (Phase 2 avg: 2.8) | +0.6 |
| Unique in staging | 56 | 218 | +162 |
| Geocoding (Nominatim) | 43% | 36% (raw) | -7% |
| Geocoding (+ Places backfill) | 43% | 97% | +54% |
| Enrichment | 100% | 97% | -3% |
| Schema version | v1 | v2 | Upgraded |
| t_any_countries | 0% | 100% | +100% |
| City coverage | 84% | 92% | +8% |
| Dedup merges | 0 | 3 | +3 |
| Interventions | 3 | 2 | -1 |

---

## Key Findings

### 1. Google Places Coordinate Backfill - Transformative

The single most impactful improvement from v1.7. Nominatim alone achieved only 36% for CalGold entities (niche historic locations, small landmarks). Google Places backfill pushed this to **97%** - matching RickSteves' 98%.

This validates the design decision (G13 mitigation) to use Google Places as a coordinate backfill source.

### 2. Entity Yield Increased

Phase 2 averaged 2.8 entities/video (vs 1.9 in Phase 1). This suggests the extraction prompt handles CalGold's longer-form episodes well. Some episodes like "Old Town Temecula" (14 entities) and "UCLA" (6 entities) yielded high counts due to multiple distinct locations within a single episode.

### 3. Dedup Working Correctly

3 dedup merges detected across Phase 1 + Phase 2:
- **Islands A, B, C, and D** (THUMS Islands, Long Beach) - appeared in 2 episodes
- **Glendora Castle** - appeared in 2 episodes
- **GWRS Main Facility** (Orange County Water District) - appeared in 2 episodes

These are legitimate revisits by Huell Howser. The visits arrays merged correctly.

### 4. Schema v2 Migration Complete

CalGold entities now carry `t_any_countries: ["us"]` and support `t_any_regions`. Cross-pipeline queries by country now work across CalGold (US-only) and RickSteves (23 countries).

### 5. Phase 1 Re-Enrichment Successful

All 57 Phase 1 entities were re-enriched with the Google Places coordinate backfill. The 32 entities Nominatim missed in Phase 1 now have coordinates.

---

## Cumulative Metrics

### CalGold Pipeline
| Metric | Value |
|--------|-------|
| Total videos processed | 60 (of 431 in playlist) |
| Total raw entities | 226 |
| Unique entities in staging | 218 |
| Geocoded (Nominatim + Places) | 213/218 (97%) |
| Enriched (Google Places) | 213/218 (97%) |
| Schema version | v2 |
| Dedup merges | 3 |

### Platform Total
| Metric | Value |
|--------|-------|
| Total entities | 418 |
| CalGold | 218 |
| RickSteves | 200 |
| Countries represented | 24 (23 RickSteves + US) |
| Cross-pipeline queries | Validated (keyword, country, geohash) |

---

## Intervention Analysis

| # | Issue | Category | Preventable? |
|---|-------|----------|-------------|
| 1 | LD_LIBRARY_PATH not set | G2 (CUDA) | Partially - fish config not auto-sourced in subprocess |
| 2 | schema.json on v1 | Config drift | Yes - should have been updated during v1.7 |

**Intervention rate: 2** (down from 3 in Phase 1). G2 continues to trigger (documented in every phase) due to fish shell subprocess environment inheritance. The schema config drift was a one-time catch-up.

---

## Recommendation for Phase 3

### Ready for Stress Test

Phase 2 calibration targets met or exceeded:
- Geocoding: 97% (target >= 80%) - EXCEEDED
- Enrichment: 97% (target >= 80%) - EXCEEDED
- Schema v2: 100% - MET
- Dedup: Validated (3 merges) - MET
- Cross-pipeline: Validated - MET

### Phase 3 Proposal (Stress Test - videos 61-90)

1. **Process next 30 videos** (61-90 from playlist) through full pipeline
2. **Monitor dedup scaling** - more revisits expected as Huell covers more of the same California geography
3. **Evaluate extraction prompt** - Phase 2's 2.8 entities/video is healthy. If Phase 3 drops significantly, tune the prompt.
4. **Target: zero interventions** - G2 should be addressed by pre-setting LD_LIBRARY_PATH in the pipeline scripts themselves, not relying on fish config
5. **Pre-fix: Embed LD_LIBRARY_PATH in transcribe script** to prevent G2 from triggering again

### Suggested G2 Fix for Phase 3

Add LD_LIBRARY_PATH setup directly to phase2_transcribe.py:
```python
import os
os.environ.setdefault("LD_LIBRARY_PATH", "/usr/local/lib/ollama/cuda_v12:/usr/local/lib/ollama/mlx_cuda_v13")
```

This would eliminate the most persistent gotcha across all iterations.

---

## Metrics Summary

```
CalGold Phase 2 (v2.8) - Calibration
  Videos: 60 acquired / 60 transcribed / 60 extracted
  Entities: 226 raw -> 218 unique in staging
  Geocoding: 97% (Nominatim 36% + Places backfill 61%)
  Enrichment: 97% via Google Places
  Schema: v2 (100% t_any_countries)
  Dedup: 3 merges
  Interventions: 2
  Platform: 418 total entities (218 CalGold + 200 RickSteves)
```
