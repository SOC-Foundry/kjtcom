# RickSteves - Design v2.9

**ADR-002 | Living Architecture Document**
**Project:** kylejeromethompson.com - Multi-Pipeline Location Intelligence Platform
**Pipeline 2:** RickSteves (Rick Steves' Europe)
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

RickSteves Phase 1 (v1.7) processed 30 videos and produced 200 unique destination entities across 23 countries. 98% geocoded (Nominatim + Places backfill). 98% enriched. Thompson Schema v2 validated. Cross-pipeline queries confirmed working.

Phase 2 (v2.9) is the **Calibration batch** - videos 31-60 from the filtered 1,865-video playlist. This is the first iteration executed by **Gemini CLI** instead of Claude Code - proving the IAO two-environment model where Claude Code proves a pattern and Gemini CLI replays it at zero cost.

**Executor:** Gemini CLI (`gemini --sandbox=none`)

Phase 2 targets:
- Process videos 31-60 (next 30 from filtered playlist)
- Validate dedup merges (Rick revisits popular destinations across episodes)
- Maintain >= 80% geocoding (Nominatim + Places backfill)
- Maintain >= 80% enrichment
- Zero interventions (all gotchas pre-solved)
- Re-enrich Phase 1 entities that missed coordinate backfill (if any)

---

# 2. Architecture Carried Forward

All architecture from v1.7 ricksteves design is carried forward:

- Thompson Schema v2 (t_any_* with t_any_countries, t_any_regions)
- Firestore multi-database (default + staging)
- Cloud Functions search API
- Pipeline stage scripts (shared, config-driven, fish shell)
- Composite indexes (including v1.7 additions for countries/regions)
- Google Places coordinate backfill after enrichment
- google.genai SDK (migrated from deprecated google-generativeai)
- Security rules (no API keys in repo)

---

# 3. Gemini CLI Execution Notes

This is the first pipeline iteration executed by Gemini CLI. Key differences from Claude Code:

| Aspect | Claude Code | Gemini CLI |
|--------|-------------|------------|
| Cost | Claude Max subscription tokens | Free (Gemini free tier) |
| Mode | `claude --dangerously-skip-permissions` | `gemini --sandbox=none` |
| Config file | CLAUDE.md | GEMINI.md (identical content) |
| Shell | fish (via preferredShell config) | fish (native on CachyOS) |
| Token budget | ~88K per 5-hour window | Free tier (generous for execution) |
| Best for | First iteration (proving patterns) | Second iteration (replaying proven patterns) |

Gemini CLI reads GEMINI.md the same way Claude Code reads CLAUDE.md. The plan document is identical. The pipeline scripts are identical. The only difference is which LLM agent executes them.

**If Gemini CLI encounters an error Claude Code would have self-healed:** Log it, attempt the same 3-retry strategy. If it can't resolve after 3 attempts, log the error in the build doc and continue to the next step. Kyle will review and address in the next iteration.

---

# 4. Phase 2 Calibration Decisions

## 4.1 Dedup Validation

Phase 1 had 23 duplicates resolved via deterministic row IDs (Firestore .set()). Phase 2 will likely encounter more cross-episode duplicates for popular destinations (Colosseum, Eiffel Tower, Uffizi). The normalization script handles this via:
- Deterministic t_row_id generation (pipeline + name slug)
- Firestore .set() overwrites with latest data
- Visits arrays should merge (multiple episodes mentioning same place)

## 4.2 Entity Yield Expectations

Phase 1 averaged 7.4 entities/video (much higher than CalGold's 1.9). Phase 2 should be similar. Expected: 30 videos -> 150-250 raw entities -> 100-180 unique after dedup.

## 4.3 Country Distribution

Phase 1 covered 23 countries. Phase 2 will expand this. The first 30 videos were heavy on Poland, Iceland, and Italy (the most recent uploads). Videos 31-60 may shift to other countries as we move deeper into the channel's upload history.

---

# 5. Gotchas Registry (Current - 17 items)

All G1-G17 from calgold-design-v2.8.md carried forward. No new gotchas expected for this iteration since it replays a proven pattern.

Critical for Gemini CLI:
- **G2:** LD_LIBRARY_PATH must be set before transcription
- **G16:** API key must be validated against actual endpoint, not just env var
- **G17:** Shell must be fish. Gemini CLI on CachyOS runs fish natively.

---

# 6. Locked Decisions

All previous locked decisions carried forward, plus:

| Decision | Value | Locked At | Rationale |
|----------|-------|-----------|-----------|
| RickSteves Phase 2 executor | Gemini CLI | v2.9 | Proven pattern from Phase 1. Free execution. |
| RickSteves Phase 2 batch | Videos 31-60 | v2.9 | Sequential. No cherry-picking. |
| IAO two-environment model | Claude Code proves, Gemini CLI replays | v2.9 | Saves Claude Max tokens for architecture work. |

---

# 7. Changelog

**v2.9 (RickSteves Phase 2 - Calibration)**
- Videos 31-60 processed through full pipeline via Gemini CLI.
- First Gemini CLI pipeline execution on kjtcom.
- Dedup validation across Phase 1 + Phase 2 entities.

**v2.8 (CalGold Phase 2 - Calibration)**
- Videos 31-60 processed. Phase 1 re-enriched with coordinate backfill.

**v1.7 (RickSteves Phase 1 - Discovery)**
- 200 destinations across 23 countries. Schema v2. 98% geocoded. 98% enriched.

**v1.6 (CalGold Phase 1 - Discovery)**
- 57 entities. 43% geocoded. 100% enriched. Thompson Schema v1 validated.

**v0.5 (Phase 0 - Scaffold)**
- Repo, Firebase, multi-database, Thompson Schema, pipeline config.
