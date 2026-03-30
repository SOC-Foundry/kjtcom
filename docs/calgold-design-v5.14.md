# CalGold - Design v5.14 (Phase 5 - Production Run)

**Pipeline:** calgold (California's Gold - Huell Howser)
**Phase:** 5 (Production Run)
**Iteration:** 14 (global counter)
**Executor:** tmux (unattended) + Claude Code (post-run enrichment/load)
**Date:** March 2026

---

## Objective

Process all remaining CalGold videos (121-431, ~311 remaining) through phases 1-5 in unattended tmux sessions with graduated timeout passes. Schema v3 is locked. Prompts are locked. This is pure production throughput -- no schema changes, no script modifications, no agent reasoning needed for phases 1-5.

After all videos are acquired, transcribed, and extracted, Claude Code runs phases 6-7 (enrich, load) to push the full dataset into staging Firestore.

---

## Architecture Decisions

[DECISION] **tmux for Phases 1-5.** No agent needed. A bash runner script executes phases 1-5 sequentially in tmux. Checkpoint-based resume means crashes and restarts are safe. Human monitors via `tmux attach` and reviews logs between passes.

[DECISION] **Graduated Timeout Passes.** CalGold episodes are shorter than Rick Steves (15-30 min vs 30-60 min), so most should complete in a single 600s pass. But some compilation/marathon episodes exist. Three passes: 600s, 1200s, 1800s.

[DECISION] **Claude Code for Phases 6-7 Only.** After all tmux passes complete and the quality sweep confirms extraction counts, Claude Code runs enrichment and load. This is the same split as v3.10-v4.13 but with tmux replacing Gemini CLI for the mechanical work.

[DECISION] **No Re-Extraction.** Unlike v4.12/v4.13 which re-extracted everything for schema v3, this run only processes NEW videos. The 120 videos already extracted with v3 prompts are untouched. Checkpoints skip them automatically.

[DECISION] **Schema v3 Locked.** No field additions. extraction_prompt.md is frozen. All new entities get the full v3 field set (actors, roles, shows, cuisines, dishes, eras, continents).

[DECISION] **Checkpoint Paths Documented.** Learned from v4.12/v4.13: actual checkpoint files are `.checkpoint_enrich.json` and `.checkpoint_load.json` in `pipeline/data/calgold/` root. NOT inside subdirectories.

---

## Production Estimates

| Metric | Estimate |
|--------|----------|
| Remaining videos | ~311 (431 total - 120 processed) |
| Avg episode length | ~20 min (CalGold episodes are shorter) |
| Transcription speed | ~3-4x realtime on RTX 2080 SUPER (large-v3) |
| Transcription time (600s pass) | ~8-12 hours (handles ~250-280 videos) |
| Transcription time (1200s pass) | ~4-8 hours (handles ~20-40 stragglers) |
| Transcription time (1800s pass) | ~2-4 hours (handles ~5-10 marathons) |
| Extraction time | ~1-2 hours (Gemini Flash, all 311 videos) |
| Normalize + geocode | ~30 min |
| Enrich + load | ~1-2 hours (Claude Code) |
| **Total wall clock** | **~24-36 hours across 3-4 days** |

---

## Success Criteria

| Criteria | Target |
|----------|--------|
| Total videos processed | 431/431 (100%) or documented gap list |
| Acquisition | >95% of 431 |
| Transcription | >95% of acquired |
| Extraction | >95% of transcribed |
| Geocoding (after backfill) | >95% |
| Enrichment | >95% |
| t_schema_version | 3 on all new entities |
| Security | Zero API keys in repo |
| Artifacts | 4 mandatory docs |

---

## Gotchas Active

| ID | Gotcha | Prevention |
|----|--------|-----------|
| G2 | LD_LIBRARY_PATH | RESOLVED -- in script + config.fish |
| G11 | API key leaks | Runner script uses env vars only |
| G13 | Nominatim niche misses | Google Places backfill in Phase 6 |
| G18 | Gemini 5-min timeout | N/A -- using tmux, not Gemini CLI |
| G21 | CUDA OOM dual process | Runner kills GPU processes before transcription |
| G24 | Checkpoint staleness | Only processing NEW videos, no re-extraction |
| G25 | Checkpoint paths | Actual paths: .checkpoint_enrich.json / .checkpoint_load.json in data root |

---

## Phase Structure Reference

| Phase | Name | Status |
|-------|------|--------|
| 0 | Scaffold & Environment | DONE (v0.5) |
| 1 | Discovery (30 videos) | DONE (v1.6, v1.7) |
| 2 | Calibration (60 videos) | DONE (v2.8, v2.9) |
| 3 | Stress Test (90 videos) | DONE (v3.10, v3.11) |
| 4 | Validation + Schema v3 (120 videos) | DONE (v4.12, v4.13) |
| 5 | Production Run (full datasets) | IN PROGRESS CalGold (v5.14) |
| 6 | Flutter App | Pending |
| 7 | Firestore Load | Pending |
| 8 | Enrichment Hardening | Pending |
| 9 | App Optimization | Pending |
| 10 | Retrospective + Template | Pending |

---

## Runner Script

The plan includes a `group_b_runner.sh` script adapted from TripleDB v5.15. It runs phases 1-3 (acquire, transcribe, extract) with configurable timeouts, then phases 4-5 (normalize, geocode). The script:

- Accepts a TIMEOUT parameter for transcription
- Kills any existing GPU processes before transcription
- Sets LD_LIBRARY_PATH explicitly
- Runs all phases sequentially with checkpoint resume
- Logs everything to a timestamped log file
- Prints summary counts at the end

Phases 6-7 (enrich, load) are handled separately by Claude Code after all tmux passes complete.
