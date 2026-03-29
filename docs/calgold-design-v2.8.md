# CalGold - Design v2.8

**ADR-001 | Living Architecture Document**
**Project:** kylejeromethompson.com - Multi-Pipeline Location Intelligence Platform
**Pipeline 1:** CalGold (California's Gold with Huell Howser)
**Author:** Kyle Thompson, VP of Engineering & Solutions Architect @ TachTech Engineering
**Date:** March 29, 2026

---

## Project Identity

| Key | Value |
|-----|-------|
| Domain | kylejeromethompson.com |
| Repository | `git@github.com:SOC-Foundry/kjtcom.git` |
| Firebase Project ID | `kjtcom-c78cd` |
| GCP Parent Org | socfoundry.com |
| Primary Dev Machine | NZXTcos (Intel i9-13900K, RTX 2080 SUPER, 64 GB DDR4, CachyOS) |

---

# 1. What This Iteration Delivers

Phase 1 (v1.6) processed 30 videos and produced 57 entities (56 unique in staging). Geocoding was 43% via Nominatim, enrichment hit 100% after the API key fix. Thompson Schema v1 validated. No dedup merges in the first 30.

Phase 2 (v2.8) is the **Calibration batch** - the next 30 videos (videos 31-60 from the playlist). This iteration benefits from every improvement made during RickSteves Phase 1 (v1.7):

1. **Google Places coordinate backfill** - pushes geocoding from 43% toward 90%+
2. **Schema v2** - CalGold entities now carry t_any_countries: ["us"]
3. **google.genai migration** - deprecated SDK replaced
4. **Parameterized pipeline registry** - no more hardcoded CalGold references
5. **Country field in Nominatim queries** - improved geocoding accuracy
6. **fish shell enforcement** - Claude Code runs fish, not bash
7. **API key validation** - pre-flight tests actual endpoint, not just env var presence

Phase 2 targets:
- Process videos 31-60 (next 30 from playlist)
- Validate dedup merges (Huell likely revisits locations from Phase 1 batch)
- Achieve >= 80% geocoding (Nominatim + Places backfill)
- Achieve >= 80% enrichment
- Zero interventions (all gotchas addressed in CLAUDE.md)
- Re-enrich Phase 1 CalGold entities that missed the Places coordinate backfill

---

# 2. Architecture Carried Forward

All architecture from v0.5 design and v1.7 ricksteves design is carried forward:

- Thompson Schema v2 (t_any_* with t_any_countries, t_any_regions)
- Firestore multi-database (default + staging)
- Cloud Functions search API
- Pipeline stage scripts (shared, config-driven)
- Composite indexes (including v1.7 additions for countries/regions)

This document covers only Phase 2 additions and calibration decisions.

---

# 3. Phase 2 Calibration Decisions

## 3.1 Re-Enrich Phase 1 Entities

Phase 1 CalGold entities were enriched (100% match) but did NOT have the Google Places coordinate backfill that was added during RickSteves v1.7. Phase 2 should:

1. Clear the Phase 1 enrichment checkpoint
2. Re-run phase6_enrich.py on ALL CalGold entities (Phase 1 + Phase 2)
3. This backfills coordinates for the 32 entities Nominatim missed in Phase 1
4. Expected: CalGold geocoding jumps from 43% to ~90%

## 3.2 Dedup Calibration

Phase 1 had 0 dedup merges because the first 30 videos didn't overlap. Phase 2 (videos 31-60) may include episodes where Huell revisits Phase 1 locations. The dedup strategy (name match + city + Levenshtein) needs validation:

- After normalization, check for entities that match Phase 1 entities by name + city
- Verify the visits array merges correctly (Phase 1 visit + Phase 2 visit on same entity)
- If dedup is too aggressive (merging distinct locations): tighten Levenshtein threshold
- If dedup is too loose (missing obvious duplicates): loosen threshold or add fuzzy match

## 3.3 Extraction Prompt Assessment

Phase 1 yielded 1.9 entities/video. Compare Phase 2 yield:
- If significantly higher or lower, the prompt may need tuning
- If entities are missing city/county fields (Phase 1 had 84% city coverage), consider adding "if the city is not explicitly mentioned, infer it from context" to the prompt
- If entities include non-geocodable items (events, TV shows, abstract concepts), add negative examples

## 3.4 Cumulative Dataset After Phase 2

After Phase 2, CalGold staging should contain:
- ~100-120 unique entities (Phase 1: 56, Phase 2: ~50-70, minus dedup merges)
- All on Thompson Schema v2
- All with t_any_countries: ["us"]
- >= 80% geocoded (Nominatim + Places backfill)
- >= 80% enriched via Google Places

Combined with RickSteves (200 entities), staging will have ~300-320 total entities across 24+ countries.

---

# 4. Gotchas Registry (Current State)

| ID | Gotcha | Prevention | Source |
|----|--------|-----------|--------|
| G1 | fish has no heredocs | Use printf or echo-append | TripleDB v0.7 |
| G2 | LD_LIBRARY_PATH must be set for CUDA | Check in pre-flight. In CLAUDE.md. | TripleDB v2.11 |
| G3 | Gemini Flash timeouts on marathon transcripts | 300s timeout | TripleDB v2.11 |
| G4 | Null-name entities collapse during dedup | Input validation before normalization | TripleDB v5.14 |
| G5 | dart:html crashes before framework init | Lazy init, deferred DOM access | TripleDB v9.36 |
| G6 | Claude Code crashes in IDE terminal | Run from Konsole | KT v10.48 |
| G7 | Cloudflare WARP requires NODE_EXTRA_CA_CERTS | Set env var for Node.js MCP | TripleDB |
| G8 | Firestore array-contains limited to ONE per query | Merge arrays or Cloud Function | v0.4 |
| G9 | Cannot query into arrays of maps | Promote queryable fields to t_any | v0.4 |
| G10 | Blaze billing surprises | $10/month budget alert | v0.4 |
| G11 | API keys leaked into build logs | Security section in CLAUDE.md | v1.6 |
| G12 | google-generativeai deprecated | Migrated to google.genai | v1.6 |
| G13 | Nominatim struggles with niche names | Google Places coordinate backfill | v1.6 |
| G14 | International locations need country fields | t_any_countries, t_any_regions | v1.7 |
| G15 | Rick Steves channel has non-location content | Pre-filtered playlist. Empty array OK. | v1.7 |
| G16 | API key SET != API key VALID | Pre-flight tests actual endpoint | v1.7 |
| G17 | Claude Code runs bash, not fish | preferredShell fish + CLAUDE.md mandate | v1.7 |

---

# 5. Locked Decisions

All previous locked decisions carried forward, plus:

| Decision | Value | Locked At | Rationale |
|----------|-------|-----------|-----------|
| Phase 2 batch | Videos 31-60 (next 30) | v2.8 | Sequential from playlist. No cherry-picking. |
| Re-enrich Phase 1 | Yes, with Places coordinate backfill | v2.8 | Phase 1 missed backfill (added in v1.7). |
| Geocoding target | >= 80% (Nominatim + Places) | v2.8 | Raised from 60% now that backfill exists. |
| Enrichment target | >= 80% | v2.8 | Conservative. Phase 1 hit 100%. |
| Unified changelog | docs/kjtcom-changelog.md | v2.8 | All pipelines write to one file. |
| Claude Code shell | fish (preferredShell) | v2.8 | Prevents bash/fish env var inheritance issues. |
| Pre-flight API validation | Test actual endpoint, not just env var | v2.8 | G16 prevention. |

---

# 6. Changelog

**v2.8 (CalGold Phase 2 - Calibration)**
- Videos 31-60 processed through full pipeline.
- Re-enriched Phase 1 entities with Google Places coordinate backfill.
- Dedup validation across Phase 1 + Phase 2 entities.
- Geocoding target raised to 80% (Nominatim + Places backfill).
- fish shell enforcement, API endpoint validation in pre-flight.
- 17 gotchas documented (G1-G17).

**v1.7 (RickSteves Phase 1 - Discovery)**
- 200 destinations across 23 countries. Schema v2. 98% geocoded. 98% enriched.

**v1.6 (CalGold Phase 1 - Discovery)**
- 57 entities. 43% geocoded. 100% enriched. Thompson Schema v1 validated.

**v0.5 (Phase 0 - Scaffold)**
- Repo, Firebase, multi-database, Thompson Schema, pipeline config.
