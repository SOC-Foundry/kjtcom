# kjtcom - Build Log v10.56

**Phase:** 10 - Pipeline Expansion & Platform Hardening
**Iteration:** 10.56
**Date:** April 06, 2026
**Agent:** Claude Code (Opus 4.6, primary)
**Machine:** NZXTcos

---

## W1: Fix Qwen Evaluator + Fallback Chain (P0)

### Diagnosis

Read `scripts/run_evaluator.py` (514 lines). Traced 4 root causes:

1. **`parse_workstream_count()`** (line 118) only parsed table format `| W1 | Name |` but v10.x design docs use `### W1: Name (P0)` heading format. Returned 0 workstreams for v10.54/v10.55/v10.56.

2. **`build_execution_context()`** relied solely on `data/iao_event_log.jsonl` which only had v9.39 entries. No v10.x event log data existed, so Qwen received near-empty context and correctly concluded "no workstreams executed."

3. **`data/eval_schema.json`** priority enum was `["P1","P2","P3"]` - missing `"P0"`. Any W1 marked P0 caused schema validation failure.

4. **Fallback was a minimal template** (`build_fallback()`) that produced score=5 for all workstreams with generic evidence text. Not a real evaluation.

### Fixes Applied

- `parse_workstream_count()`: Added regex-based heading format parser (`### W{n}: Name (P{n})`). Falls back to table format if no headings found. Tested: correctly finds 4 workstreams in v10.56 design doc.

- `build_execution_context()`: Now also reads build log (`docs/kjtcom-build-{version}.md`) and changelog entries for evidence when event log is empty.

- `eval_schema.json`: Priority enum expanded to `["P0","P1","P2","P3"]`.

- Three-tier fallback chain:
  - Tier 1: Qwen3.5-9B via Ollama (3 attempts, schema validation + retry feedback)
  - Tier 2: Gemini Flash via litellm (2 attempts, schema validation)
  - Tier 3: Self-eval (always succeeds, scores capped at 7/10)
  - Added `call_gemini_flash()` and `generate_self_eval()` functions
  - Refactored `evaluate_with_retry()` into `try_qwen_tier()` + `try_gemini_tier()` + fallback
  - New CLI flags: `--verbose`, `--test-fallback gemini|self-eval`

### Pre-flight Verification

- Qwen responsive: `curl` test returned valid JSON
- litellm available: import succeeds
- Workstream parser test: correctly finds 4 workstreams from v10.56 design doc

### Archive Analysis

- Qwen timed out on 98KB archive prompt (300s timeout insufficient for 32K context)
- Gemini Flash succeeded: produced 173-line `docs/bourdain-scaling-plan.md`
- Plan includes entity yield projections (3.2/video), batch schedule, iteration breakdown

### Evidence

- `scripts/run_evaluator.py`: ~580 lines, fallback chain implemented
- `data/eval_schema.json`: P0 in priority enum
- `docs/bourdain-scaling-plan.md`: 173 lines, concrete execution plan
- `docs/evaluator-harness.md`: 601 lines (up from 528), G55 ADR appended

---

## W2: Claw3D PCB Redesign (P1)

### Implementation

Complete rewrite of `app/web/claw3d.html` (486 lines) replacing solar system with PCB architecture.

- Three circuit boards: Frontend (#0D9488), Middleware (#8B5CF6), Backend (#3B82F6)
- 24 IC chip components (8 per board, 2x4 grid)
- LED status indicators (green=active, amber=degraded, gray=inactive)
- Pin arrays on chip edges
- HTML overlay labels positioned via Vector3.project()
- Animated dashed inter-board connectors (LineDashedMaterial + dashOffset animation)
- Raycaster hover tooltips (dark bg, green border, monospace)
- Click-to-zoom on boards with camera lerp
- Escape/All-boards button to return to overview
- Iteration dropdown from claw3d_iterations.json
- Three.js r128 CDN, no OrbitControls, no CapsuleGeometry, no TextGeometry

### Data Files

- `data/claw3d_components.json`: 56 lines, 3 boards, 24 chips, 5 connectors
- `data/claw3d_iterations.json`: 18 lines, v10.56 entry added

### Validation

All 18 requirement checks pass:
- Three.js r128 CDN, No OrbitControls, No CapsuleGeometry, No TextGeometry
- Tooltip, Raycaster, Vector3.lerp, LineDashedMaterial, computeLineDistances
- BoxGeometry, PlaneGeometry, EdgesGeometry, SphereGeometry(0.05)
- Background 0x0D1117, dashOffset animation, Escape key handler

---

## W3: Bourdain Pipeline Phase 2 (P1)

### Phase 1 Status (prior iteration)

- 30 videos acquired, transcribed, extracted, normalized, geocoded, enriched
- 96 entities loaded to staging across 20 countries
- Checkpoint: `pipeline/data/bourdain/checkpoint.json`

### Phase 2 Progress

- **Acquire:** yt-dlp downloaded videos 31-60 (30 videos). All 30 MP3 files in `pipeline/data/bourdain/audio/`.
- **Transcribe:** Batch 1 (10 videos) in progress. GPU memory conflict with Ollama resolved (unloaded Qwen, freed 6.3GB VRAM). Using large-v3 model with CUDA float16.
- **Remaining phases:** Extract, normalize, geocode, enrich, load - pending transcription completion.

### G18 Compliance

- CUDA OOM on first attempt (Ollama Qwen loaded in VRAM)
- Unloaded Qwen via `keep_alive: 0` API call
- GPU memory freed from 7.4GB to 1.2GB
- Transcription restarted with graduated batches (--limit 10)

---

## W4: README Overhaul (P2)

### Changes

- Version: Phase 10 v10.56 (ACTIVE)
- Status line: Evaluator Fallback Chain + PCB Architecture + Bourdain Phase 2
- Pipelines table: Added Bourdain row (#8B5CF6, 96 staging, Phase 1 Complete), added Color column
- Architecture section: Updated current state line (v10.56, 4 pipelines, 601-line harness, PCB architecture)
- Architecture links: Replaced "3D IAO Visualization" with "Interactive PCB Architecture Diagram"
- Claw3D description: Replaced "3D Solar System" with "PCB Architecture"
- Middleware section: Added evaluator fallback chain and ChromaDB chunk count
- Tech stack: Updated Evaluation and 3D Visualization rows
- Phase 10 Roadmap: Updated with Bourdain progress and evaluator hardening
- Project Status: Updated Phase 10 iteration range
- Changelog: Added v10.56, v10.55, v10.54 entries
- Line count: 672 -> 700

---

## Living Docs Updates

- `docs/evaluator-harness.md`: 528 -> 601 lines (+73). G55 ADR with root cause analysis, resolution documentation, and v10.56 evidence standards.
- `docs/kjtcom-changelog.md`: v10.56 entry added (14 bullet points).
- `docs/bourdain-scaling-plan.md`: New file, 173 lines, Gemini Flash archive analysis.

---

*Build log v10.56. April 6, 2026. Claude Code (Opus 4.6). 4 workstreams executed.*
