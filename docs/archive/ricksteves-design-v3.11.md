# RickSteves - Design v3.11 (Phase 3 - Stress Test)

**Pipeline:** ricksteves (Rick Steves' Europe)
**Phase:** 3 (Stress Test)
**Iteration:** 11 (global counter)
**Executor:** Gemini CLI (Phases 1-5) + Claude Code (Phases 6-7)
**Date:** March 2026

---

## Objective

Process RickSteves videos 91-120 (30 new videos) through the full 7-phase pipeline using the split-agent model validated in v3.10. Gemini CLI handles phases 1-5 (acquire, transcribe, extract, normalize, geocode), Claude Code handles phases 6-7 (enrich, load) plus post-flight and artifacts. Validate pipeline stability at the 120-video mark for international content before graduating to Phase 4 (Validation).

---

## Architecture Decisions

[DECISION] **Split-Agent Model (Proven in v3.10).** Gemini CLI runs phases 1-5 with `gemini --yolo`. Claude Code runs phases 6-7 with `claude --dangerously-skip-permissions`. Handoff via checkpoint file at pipeline/data/ricksteves/handoff-v3.11.json. v3.10 achieved zero interventions on both sides - same protocol applies.

[DECISION] **Gemini CLI Launch: `gemini --yolo` Only.** v3.10 confirmed that `--yolo` implies sandbox bypass (status bar showed "no sandbox" without explicit `--sandbox=none` flag). Single flag launch.

[DECISION] **International Geocoding Advantage.** RickSteves entities include t_any_countries which boosts Nominatim hit rates (98-99% in phases 1-2 vs CalGold's 35-43%). Expect higher Nominatim baseline with fewer Places backfills needed.

[DECISION] **Array Merge on Load (Validated).** phase7_load.py fetch-and-merge pattern handles multi-visit entities. RickSteves has 95 multi-visit entities from v2.9 - expect additional merges from the phase 3 batch as popular European destinations appear in multiple episodes.

[DECISION] **Thompson Schema v2 Locked.** No schema changes. All RickSteves entities carry t_any_countries (multi-value, e.g. ["france", "italy"]) and t_any_regions.

[DECISION] **LD_LIBRARY_PATH Embedded.** G2 permanently resolved in v3.10 - LD_LIBRARY_PATH is now in both config.fish and phase2_transcribe.py.

---

## Success Criteria

| Criteria | Target | Measurement |
|----------|--------|-------------|
| Acquisition | 30/30 (100%) | Audio file count delta |
| Transcription | 30/30 (100%) | Transcript file count delta |
| Extraction | 30/30 (100%) | Extracted JSON file count delta |
| Geocoding | >95% | Nominatim + Places backfill |
| Enrichment | >95% | Google Places API (New) |
| Dedup accuracy | All multi-visit entities merged | Spot-check 5 known destinations |
| Interventions (Gemini phases 1-5) | 0 | Count manual fixes |
| Interventions (Claude phases 6-7) | 0 | Count manual fixes |
| Security | Zero API keys in repo | grep -rnI "AIzaSy" . |
| Artifacts | 4 mandatory docs produced | build, report, changelog, README |
| Total RickSteves entities | ~559+ (with dedup merges) | Firestore staging count |

---

## Gotchas Active for This Iteration

| ID | Gotcha | Prevention |
|----|--------|-----------|
| G1 | fish has no heredocs | Use printf or echo-append |
| G2 | LD_LIBRARY_PATH for CUDA | RESOLVED - embedded in script + config.fish |
| G11 | API key leaks | NEVER cat config.fish. Print SET/NOT SET only. |
| G13 | Nominatim misses niche names | Google Places coordinate backfill |
| G18 | Gemini 5-min timeout | Background transcription + polling |
| G19 | Gemini runs bash by default | All commands via fish -c "..." |
| G20 | Gemini leaked API keys | NEVER cat/read config.fish. grep only. |
| G21 | CUDA OOM with dual transcription | ONE process at a time |
| G22 | fish ls color codes | Use command ls or Python |

---

## File Layout

```
docs/
  ricksteves-design-v3.11.md    (this file)
  ricksteves-plan-v3.11.md      (execution plan)
  ricksteves-build-v3.11.md     (produced by agent)
  ricksteves-report-v3.11.md    (produced by agent)
  kjtcom-changelog.md           (append entry)
  archive/                      (v3.10 docs archived here)
```

---

## Agent Handoff Protocol

1. **Gemini CLI** executes phases 1-5 per ricksteves-plan-v3.11.md Section A.
2. Gemini produces handoff checkpoint: pipeline/data/ricksteves/handoff-v3.11.json
3. **Human** reviews checkpoint, verifies counts.
4. **Claude Code** executes phases 6-7 per ricksteves-plan-v3.11.md Section B.
5. Claude produces all 4 artifacts.
6. **Human** reviews artifacts, runs security scan, commits, pushes.

---

## RickSteves-Specific Notes

- Rick Steves episodes are longer than CalGold (30-60 min vs 15-30 min). Transcription will take longer per video. Budget ~30 min for transcription phase.
- Entity yield is higher (8.0 entities/video average vs CalGold's ~3.6). Expect ~240 raw entities from 30 videos.
- Multi-visit merges are more frequent for popular European destinations (Colosseum, Eiffel Tower, etc.).
- Country distribution may expand beyond the current 29 countries if this batch covers new regions.
