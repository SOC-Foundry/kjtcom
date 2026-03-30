# CalGold - Design v3.10 (Phase 3 - Stress Test)

**Pipeline:** calgold (California's Gold - Huell Howser)
**Phase:** 3 (Stress Test)
**Iteration:** 10 (global counter)
**Executor:** Gemini CLI (Phases 1-5) + Claude Code (Phases 6-7)
**Date:** March 2026

---

## Objective

Process CalGold videos 61-90 (30 new videos) through the full 7-phase pipeline using a split-agent model: Gemini CLI handles phases 1-5 (acquire, transcribe, extract, normalize, geocode) for zero-cost mechanical execution, then Claude Code handles phases 6-7 (enrich, load) where merge logic and error handling require stronger reasoning. Validate pipeline stability at the 90-video mark before graduating to Phase 4 (Validation).

---

## Architecture Decisions

[DECISION] **Split-Agent Execution Model.** Gemini CLI runs phases 1-5 autonomously with `--sandbox=none --yolo` flags. Human reviews phase 5 output (geocoded JSONL), then launches Claude Code with `--dangerously-skip-permissions` for phases 6-7. This exploits each agent's strengths: Gemini for free, deterministic script replay; Claude for nuanced merge logic and post-flight validation. Handoff point: geocoded JSONL file in `pipeline/data/calgold/geocoded/`.

[DECISION] **Gemini CLI Full Autonomy.** Launch command: `gemini --sandbox=none --yolo`. Combined with `Shift+Tab` for auto-accept edits, this eliminates the permission-prompt stalling observed in v2.9 where Gemini waited 60+ minutes for approval on basic commands like `ls` and `wc`.

[DECISION] **LD_LIBRARY_PATH Embedded in Script.** Per v2.8 report recommendation, `phase2_transcribe.py` now sets `LD_LIBRARY_PATH` at the top of the script via `os.environ`, complementing the config.fish fix from v2.9. This kills G2 permanently -- neither agent nor shell configuration can break CUDA transcription.

[DECISION] **Transcription Background Execution.** Gemini CLI has a 5-minute stdout timeout (G18). All transcription MUST run as a background job with stdout polling. The plan prescribes the exact command pattern. Claude Code does not have this limitation but the script change benefits both agents.

[DECISION] **Array Merge on Load.** The `phase7_load.py` fetch-and-merge pattern validated in v2.9 (95 multi-visit entities) is now the permanent load strategy. `.set()` is permanently replaced with fetch-existing + merge arrays + `.set()`.

[DECISION] **Thompson Schema v2 Locked.** No schema changes in Phase 3. All entities use v2 with `t_any_countries: ["us"]` for CalGold.

---

## Success Criteria

| Criteria | Target | Measurement |
|----------|--------|-------------|
| Acquisition | 30/30 (100%) | `wc -l pipeline/data/calgold/audio/*.mp3` delta |
| Transcription | 30/30 (100%) | `wc -l pipeline/data/calgold/transcripts/*.json` delta |
| Extraction | 30/30 (100%) | `wc -l pipeline/data/calgold/extracted/*.json` delta |
| Geocoding | >95% | Nominatim + Places backfill |
| Enrichment | >95% | Google Places API (New) |
| Dedup accuracy | All multi-visit entities merged | Spot-check 5 known duplicates |
| Interventions (Gemini phases 1-5) | 0 | Count manual fixes during execution |
| Interventions (Claude phases 6-7) | 0 | Count manual fixes during execution |
| Security | Zero API keys in repo | `grep -rnI "AIzaSy" .` returns only plan checklist references |
| Artifacts | 4 mandatory docs produced | build, report, changelog, README |
| Total entities in staging | ~248+ (218 + 30 new) | Firestore document count |

---

## Gotchas Active for This Iteration

| ID | Gotcha | Prevention |
|----|--------|-----------|
| G1 | fish has no heredocs | Use printf or echo-append |
| G2 | LD_LIBRARY_PATH for CUDA | Now in config.fish AND phase2_transcribe.py. Verify both in pre-flight. |
| G11 | API key leaks | NEVER cat config.fish. Print SET/NOT SET only. |
| G13 | Nominatim misses niche names | Google Places coordinate backfill |
| G17 | Claude Code runs bash | preferredShell fish + CLAUDE.md mandate |
| G18 | Gemini 5-min timeout | Background transcription + polling |
| G19 | Gemini runs bash by default | All commands via `fish -c "..."` |
| G20 | Gemini leaked API keys | NEVER cat/read config.fish. grep only. |
| G21 | CUDA OOM with dual transcription | ONE process at a time |
| G22 | fish ls color codes | Use `command ls` or Python |

---

## File Layout

```
docs/
  calgold-design-v3.10.md    (this file)
  calgold-plan-v3.10.md      (execution plan)
  calgold-build-v3.10.md     (produced by agent)
  calgold-report-v3.10.md    (produced by agent)
  kjtcom-changelog.md        (append entry)
  archive/                   (v2.8 + v2.9 docs archived here)

pipeline/
  scripts/                   (shared, no changes expected)
  config/calgold/
    pipeline.json
    schema.json
    extraction_prompt.md
    playlist_urls.txt
  data/calgold/               (gitignored, working data)
```

---

## Agent Handoff Protocol

1. **Gemini CLI** executes phases 1-5 per `calgold-plan-v3.10.md` Section A.
2. Gemini produces a handoff checkpoint file: `pipeline/data/calgold/handoff-v3.10.json` containing counts for each phase.
3. **Human** reviews handoff checkpoint, verifies counts, spot-checks 3 geocoded entities.
4. **Claude Code** executes phases 6-7 per `calgold-plan-v3.10.md` Section B.
5. Claude produces all 4 artifacts (build, report, changelog append, README update).
6. **Human** reviews artifacts, runs `grep -rnI "AIzaSy" .`, commits, pushes.

---

## Future Integration Notes (Not for This Iteration)

- **OpenClaw:** Phase 5 production runs could wrap each pipeline as an OpenClaw agent with heartbeat-driven execution and Telegram status updates.
- **HyperAgents:** Phase 10 retrospective could use Meta's HyperAgent framework to evolve `extraction_prompt.md` variants using IAO metrics as fitness signals.
- **Claw3D:** Phase 8 Flutter app development could add a Claw3D monitoring dashboard for parallel pipeline visualization.
