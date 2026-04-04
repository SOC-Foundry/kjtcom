# RickSteves - Design v5.17 (Phase 5 - Production Run)

**Pipeline:** ricksteves (Rick Steves' Europe)
**Phase:** 5 (Production Run)
**Iteration:** 17 (global counter)
**Executor:** tmux (unattended, auto-restart) + Claude Code (post-run enrichment/load)
**Date:** March-April 2026

---

## Objective

Process all remaining Rick Steves videos (151-1865, ~1,715 remaining) through phases 1-5 in unattended tmux sessions with graduated timeout passes. Schema v3 is locked. Prompts are locked. This is pure production throughput.

After all videos are acquired, transcribed, and extracted, Claude Code runs phases 6-7 (enrich, load) to push the full dataset into staging Firestore.

This is 5.5x the scale of CalGold v5.14 (1,715 vs 311 remaining) with longer episodes (25-30 min avg vs 15-20 min). Plan accordingly for multi-day tmux runs and CUDA OOM recovery.

---

## Architecture Decisions

[DECISION] **tmux for Phases 1-5.** Same as v5.14. No agent needed. group_b_runner.sh (proven in v5.14) executes phases 1-5 sequentially. Checkpoint-based resume means crashes and restarts are safe.

[DECISION] **Auto-Restart Wrapper.** CalGold v5.14 hit CUDA OOM after ~109 videos. At 1,715 videos, expect ~10-15 OOM crashes during Pass 1. A bash while-loop wrapper auto-restarts the runner after OOM. Checkpoints skip already-processed videos on restart.

[DECISION] **Graduated Timeout Passes.** Rick Steves episodes average 25-30 min (longer than CalGold's 15-20 min). Three passes: 600s (standard episodes), 1200s (longer specials), 1800s (marathons/compilations). CalGold needed only 2 passes - RickSteves will likely need all 3.

[DECISION] **Claude Code for Phases 6-7 Only.** Same split as v5.14. After all tmux passes complete and quality sweep confirms counts, Claude Code runs enrichment and load.

[DECISION] **No Re-Extraction.** Only processes NEW videos. The 150 videos already extracted with v3 prompts from v4.13 are untouched. Checkpoints skip them automatically.

[DECISION] **Schema v3 Locked.** No field additions. extraction_prompt.md is frozen.

[DECISION] **Concurrent Frontend Work Safe.** Kyle will be developing the Flutter frontend (Phase 6) on P3 while NZXTcos runs tmux production passes. No conflicts - frontend work is in app/, pipeline data is in pipeline/data/ and docs/. Pull before committing on either machine.

---

## Production Estimates

| Metric | Estimate |
|--------|----------|
| Remaining videos | ~1,715 (1,865 total - 150 processed) |
| Avg episode length | ~25-30 min (longer than CalGold) |
| Transcription speed | ~3-4x realtime on RTX 2080 SUPER (large-v3) |
| OOM crash frequency | ~every 100-200 videos (VRAM fragmentation) |
| Expected OOM restarts (Pass 1) | ~10-15 |

### Pass Timing

| Pass | Timeout | Expected Videos | Est. Runtime | Notes |
|------|---------|-----------------|--------------|-------|
| Pass 1 | 600s | ~1,200-1,400 | 5-7 days | Auto-restart wrapper handles OOM |
| Pass 2 | 1200s | ~200-400 | 1-2 days | Longer specials |
| Pass 3 | 1800s | ~50-100 | 12-24 hours | Marathons/compilations |
| Quality sweep | N/A | All | ~2-3 hours | Full normalize + geocode |
| Enrich + load | N/A | All | ~3-5 hours | Claude Code |
| **Total** | | **~1,715 videos** | **~8-10 days** |

### CalGold v5.14 Comparison

| Metric | CalGold v5.14 | RickSteves v5.17 |
|--------|---------------|------------------|
| Remaining videos | 311 | 1,715 |
| Avg episode length | 15-20 min | 25-30 min |
| Passes needed | 2 | 3 (expected) |
| Total wall clock | ~14 hours | ~8-10 days |
| Scale factor | 1x | ~5.5x videos, ~2x episode length |

---

## Success Criteria

| Criteria | Target |
|----------|--------|
| Total videos processed | 1,865/1,865 or documented gap list |
| Acquisition | >95% of 1,865 |
| Transcription | >95% of acquired |
| Extraction | >95% of transcribed |
| Geocoding (after enrichment) | >95% |
| Enrichment | >95% |
| t_schema_version | 3 on all new entities |
| Security | Zero API keys in repo |
| Artifacts | 4 mandatory docs |

---

## Gotchas Active

| ID | Gotcha | Prevention |
|----|--------|-----------|
| G2 | LD_LIBRARY_PATH | RESOLVED - in script + config.fish |
| G11 | API key leaks | Runner script uses env vars only |
| G13 | Nominatim niche misses | Google Places backfill in Phase 6 (better coverage for European cities) |
| G21 | CUDA OOM | Auto-restart wrapper. OOM every ~100-200 videos is expected at this scale |
| G24 | Checkpoint staleness | Only processing NEW videos, no re-extraction |
| G25 | Checkpoint paths | Actual paths: .checkpoint_enrich.json / .checkpoint_load.json in data root |
| G26 | **NEW** - Multi-day tmux | Use `tee -a` (append) for logging. Check disk space before launch (>100GB free) |

---

## Phase Structure Reference

| Phase | Name | Status |
|-------|------|--------|
| 0 | Scaffold & Environment | DONE (v0.5) |
| 1 | Discovery (30 videos) | DONE (v1.6, v1.7) |
| 2 | Calibration (60 videos) | DONE (v2.8, v2.9) |
| 3 | Stress Test (90 videos) | DONE (v3.10, v3.11) |
| 4 | Validation + Schema v3 (120 videos) | DONE (v4.12, v4.13) |
| 5 | Production Run (full datasets) | CalGold DONE (v5.14), RickSteves IN PROGRESS (v5.17) |
| 6 | Flutter App | IN PROGRESS (v6.15 DONE, v6.16 IN PROGRESS on P3) |
| 7 | Firestore Load | Pending |
| 8 | Enrichment Hardening | Pending |
| 9 | App Optimization | Pending |
| 10 | Retrospective + Template | Pending |
