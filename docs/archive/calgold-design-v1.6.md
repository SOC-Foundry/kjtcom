# CalGold - Design v1.6

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
| Firebase Project Number | 703812044891 |
| GCP Parent Org | socfoundry.com |
| Primary Dev Machine | NZXTcos (Intel i9-13900K, RTX 2080 SUPER, 64 GB DDR4, CachyOS) |

---

# What This Iteration Delivers

Phase 0 (v0.5) scaffolded the monorepo, configured Firebase Blaze with multi-database, created the CalGold pipeline config, validated the Thompson Schema with a test entity, and deployed a Cloud Functions search stub.

Phase 1 (v1.6) is the **Discovery batch** - 30 videos processed through the full 7-stage pipeline. This proves:

1. yt-dlp acquires CalGold playlist audio reliably
2. faster-whisper (CUDA) transcribes Huell Howser's voice accurately
3. Gemini Flash extracts California locations from transcripts
4. The Thompson Schema normalization produces queryable t_any_* fields
5. Nominatim geocodes extracted locations
6. Google Places enriches with ratings, open/closed, websites
7. Enriched entities load to staging Firestore and are cross-queryable

---

# Architecture Carried Forward from v0.5

The following sections are unchanged from calgold-design-v0.5.md:

- Section 2: Platform Constraints (Pillar 8)
- Section 3: Thompson Schema (t_any_*) - full spec
- Section 4: Data Model - full document examples
- Section 5: Pipeline Architecture - all 7 stages
- Section 6: CalGold Pipeline Config - schema.json, extraction_prompt.md
- Section 7: Firestore Database Design - multi-database, security rules, indexes
- Section 8: Cloud Functions Search API
- Section 10: Repo Structure
- Section 12: Gotchas Registry

Refer to v0.5 (now in docs/archive/) for full details. This document covers only Phase 1 additions.

---

# Phase 1 Specific Design Decisions

## Batch Size: 30 Videos

Per IAO Pillar 6 (Progressive Batching), Phase 1 processes 30 of 431 videos. This is ~7% of the dataset - enough to validate the full pipeline, small enough to iterate quickly.

The 30 videos are the first 30 from playlist_urls.txt (yt-dlp order). No cherry-picking.

## Extraction Prompt Tuning

The extraction prompt from v0.5 (Section 6.2) will be used as-is for Phase 1. If the 30-video batch reveals systematic extraction failures (missed locations, hallucinated entities, schema violations), the prompt will be revised for Phase 2.

The extraction_prompt.md asks Gemini Flash to return a JSON array of location objects. Each video may produce 0-5+ locations. Expected yield: 30 videos -> 40-80 unique locations after dedup.

## Deduplication Strategy

Huell revisited some locations across episodes. The normalization script (phase4) should detect duplicates by:

1. Exact name match (case-insensitive)
2. Name similarity (Levenshtein distance < 3)
3. Same city + similar name

When duplicates are found, merge visits arrays. Keep the richer description. This is the same approach TripleDB used successfully.

## Geohash Precision

Geohashes are stored at 3 precision levels per entity:
- 4 characters (~20km precision) - regional proximity
- 5 characters (~5km precision) - city-level proximity
- 6 characters (~1km precision) - neighborhood proximity

This enables tiered proximity queries without computing distances at query time.

## Checkpoint Strategy

All phase scripts use JSON checkpoint files in `pipeline/data/calgold/`:
- `checkpoint_acquire.json` - tracks downloaded video IDs
- `checkpoint_transcribe.json` - tracks transcribed video IDs
- `checkpoint_extract.json` - tracks extracted video IDs
- etc.

On crash/relaunch, completed items are skipped. This is critical for Phase 5+ (production runs) but built in from Phase 1.

## Timeout Budgets

| Phase | Timeout per Item | Rationale |
|-------|-----------------|-----------|
| Acquire (yt-dlp) | 120 seconds | Most videos are 25-30 min. Download should be fast. |
| Transcribe (faster-whisper) | 300 seconds | 30-min episodes transcribe in ~60s on RTX 2080 SUPER. 300s covers edge cases. |
| Extract (Gemini Flash) | 300 seconds | Same as TripleDB. Handles 200K-char transcripts. |
| Geocode (Nominatim) | 30 seconds | Simple HTTP request. 1 req/sec rate limit is the real constraint. |
| Enrich (Google Places) | 30 seconds | Simple HTTP request. |

## Future LLM Integration Notes

The extraction stage currently uses Gemini 2.5 Flash API exclusively. Future iterations will evaluate:

- **Claude Sonnet API** - verification pass on extracted entities (quality check)
- **Meta HyperAgents** - self-improving extraction prompts that evolve across iterations
- **Local LLMs (Nemotron, Qwen via Ollama)** - offline extraction fallback
- **Multi-LLM ensemble** - extract with Flash, verify with Sonnet, resolve conflicts with Opus

The pipeline architecture already supports this - phase3_extract.py reads the extraction prompt from config but the LLM endpoint is configurable. Adding a new LLM is a config change, not a code change.

---

# Locked Decisions

All v0.5 locked decisions carried forward, plus:

| Decision | Value | Locked At | Rationale |
|----------|-------|-----------|-----------|
| Phase 1 batch size | 30 videos | v1.6 | Progressive batching. ~7% of dataset. |
| Geohash precisions | 4, 5, 6 characters | v1.6 | Regional, city, neighborhood proximity tiers. |
| Dedup strategy | Name match + city + Levenshtein | v1.6 | Proven on TripleDB. |
| Timeout: extract | 300 seconds | v1.6 | Matches TripleDB. Handles marathon transcripts. |
| README structure | Hyperagents-style with IAO pillars | v1.6 | Professional showcase. |

---

# Changelog

**v1.6 (Phase 1 - Discovery)**
- 30-video discovery batch through full CalGold pipeline.
- README overhaul: Hyperagents-style with IAO Nine Pillars, Thompson Schema spec, architecture diagram, future directions (HyperAgents, multi-LLM).
- Dedup strategy defined: name match + city + Levenshtein.
- Geohash 3-tier precision: 4/5/6 characters.
- Timeout budgets: 120s acquire, 300s transcribe, 300s extract, 30s geocode/enrich.
- Checkpoint/resume pattern for all 7 phase scripts.
- v0.5 artifacts archived to docs/archive/.

**v0.5 (Phase 0 - Scaffold)**
- Repo: git@github.com:SOC-Foundry/kjtcom.git
- Firebase: kjtcom (kjtcom-c78cd) under socfoundry.com, Blaze billing
- Monorepo scaffolded: app/, pipeline/, functions/, docs/
- Multi-database configured: (default) + staging, both us-central1
- Thompson Schema (t_any_*) designed and validated with test entity
- CalGold pipeline config: schema.json (14 indicator mappings), extraction_prompt.md
- Cloud Functions search endpoint deployed
- 431 CalGold playlist URLs validated via yt-dlp
- 5 interventions resolved (Firebase auth, API enablement, IAM permissions)
