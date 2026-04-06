# kjtcom - Design Document v10.56

**Phase:** 10 - Pipeline Expansion & Platform Hardening
**Iteration:** 10.56
**Date:** April 06, 2026
**Previous:** v10.55 (Bourdain Phase 1 delivered 96 entities, Claw3D fixed but animate broken, evaluator produced 3rd consecutive empty report)

---

## v10.55 POST-MORTEM

v10.55 delivered real work — 96 Bourdain entities in staging, Claw3D TypeError fix, agent_scores.json schema conversion, 604-line retrospective, 6 new post-flight checks — but the evaluator failed again. Three consecutive hollow reports is a systemic failure, not a fluke.

**What worked:**
- Bourdain Phase 1 completed cleanly: 30 videos acquired, transcribed, extracted, normalized, geocoded, enriched, loaded to staging. 96 entities across 20 countries. Zero interventions.
- agent_scores.json converted to canonical `{"iterations": [...]}` schema. 4 duplicate entries removed.
- Phase 9 retrospective rebuilt to 604 lines with 130 workstreams inventoried and zero Unknown rows.
- post_flight.py expanded to 14 checks including static asset validation.

**What failed:**
1. **Qwen evaluator (G55):** Third consecutive empty report. The report says "No workstreams were executed" despite 17 files changed and 5 workstreams with clear deliverables. The build log and changelog prove the work happened — the evaluator pipeline is broken at the handoff layer. Root cause is likely: (a) `run_evaluator.py` not passing build log content as context to Qwen, (b) Qwen's JSON output failing schema validation with no retry, or (c) the fallback template writing an empty scorecard instead of escalating.
2. **README not updated:** Only 2 lines changed. Bourdain pipeline not listed. Still references solar system.
3. **Claw3D animate toggle broken:** The fix resolved the TypeError crash but the animation toggle doesn't work. The page loads static but the toggle does nothing.

**Decision: Register G55 and implement evaluator fallback chain.** Qwen remains primary evaluator but Gemini Flash and self-eval are fallbacks. An empty report is never acceptable again.

---

## WORKSTREAMS

### W1: Fix Qwen Evaluator + Fallback Chain + Archive Analysis (P0)

**Objective:** Diagnose why Qwen produced 3 empty reports, fix the pipeline, implement a Qwen → Gemini Flash → self-eval fallback chain, and run Qwen against the full Phase 1-5 archive to produce a Bourdain scaling plan.

**Why P0:** The evaluator is the audit trail. Without scored reports, the IAO methodology's accountability loop is broken. Every other workstream depends on this — if W2/W3/W4 execute perfectly but produce another empty report, the iteration is still a failure.

**Diagnosis targets in `scripts/run_evaluator.py`:**
- Does the script read `docs/kjtcom-build-v{version}.md`? Or does it expect the build log path as an argument?
- Does it pass the build log content in the Ollama API prompt? Or just the file path?
- Does it validate Qwen's JSON response against `data/eval_schema.json`?
- On validation failure, does it retry with diagnostic feedback? Or does it write an empty template?
- Does it handle Qwen's `think` mode output (G51)? The `think:false` flag must be set.
- Is `agent_scores.json` being written with the correct path (repo root, not scripts/)?

**Fallback chain implementation:**
```
Qwen3.5-9B (3 attempts, schema validation each)
    ↓ all fail
Gemini Flash API (2 attempts, same schema)
    ↓ all fail
Executing agent self-eval (always succeeds, cap scores at 7/10)
```

Each level logs: attempt number, raw response (first 500 chars), validation error if any. The final report must note which evaluator produced it.

**Archive analysis for Bourdain scaling:**
After the evaluator pipeline is fixed, feed Qwen the full archive:
- All `kjtcom-report-v*.md` and `kjtcom-build-v*.md` from `docs/archive/` for CalGold, RickSteves, and TripleDB Phase 1-5 iterations
- Ask Qwen to analyze: iteration counts per phase, failure patterns, parallelization opportunities, optimal batch sizes, entity yield per video
- Output: `docs/bourdain-scaling-plan.md` — concrete plan for running Bourdain from Phase 2 through Phase 5 in minimum iterations

**Success criteria:**
- `run_evaluator.py` produces a report with non-empty scorecard for v10.56
- Fallback chain is implemented and testable (`--test-fallback` flag)
- `docs/bourdain-scaling-plan.md` exists with data-driven recommendations
- `agent_scores.json` has v10.56 entry with 5-dimension scores

---

### W2: Claw3D PCB Redesign (P1)

**Objective:** Replace the broken solar system visualization with a three-board PCB (Printed Circuit Board) architecture diagram. Three separate circuit boards — Frontend, Middleware, Backend — with IC chip components, copper trace connectors, LED status indicators, hover tooltips, and click-to-zoom navigation.

**Why PCB:** The circuit board metaphor maps naturally to the platform architecture. Frontend/Middleware/Backend are literally separate layers. Components are chips on a board. Data flows are traces. Status indicators are LEDs. The SIEM/cyber aesthetic (dark background, green accents, monospace labels) is native to PCB debug tooling. It's readable, screenshottable, and technically coherent with the portfolio narrative.

**Three boards:**

| Board | Border Color | Trace Color | Chip Count |
|-------|-------------|-------------|------------|
| Frontend | #0D9488 (teal) | teal | 8 |
| Middleware | #8B5CF6 (purple) | purple | 8 |
| Backend | #3B82F6 (blue) | blue | 8 |

**Component inventory (24 chips total):**

Frontend: query_editor, results_table, detail_panel, map_tab, globe_tab, iao_tab, mw_tab, schema_tab

Middleware: intent_router, rag_pipeline, evaluator (DEGRADED), telegram_bot, artifact_gen, post_flight, gotcha_archive, agent_scores (DEGRADED)

Backend: calgold (#DA7E12), ricksteves (#3B82F6), tripledb (#DD3333), bourdain (#8B5CF6, DEGRADED), qwen_9b (DEGRADED), nemotron_4b, chromadb, firebase_mcp

**Each chip renders as:**
- Flat rectangular box (BoxGeometry, height=0.1)
- Label text (HTML overlay via Vector3.project())
- Pin array on edges (thin lines extending from chip border)
- LED indicator (tiny sphere at top-right corner): green=active, amber=degraded, gray=inactive
- Intra-board copper traces connecting related chips

**Inter-board connectors:**
- Frontend → Middleware: "Riverpod state", "Firestore stream"
- Middleware → Backend: "Ollama API", "Firebase Admin SDK", "ChromaDB embed"
- Animated dashed lines (LineDashedMaterial, dashOffset animated in render loop)
- Orthogonal routing (L-bends), never diagonal, never through chips

**Interaction:**
- **Hover chip:** Dark tooltip div appears showing chip name, status (active/degraded/inactive with colored dot), and detail text in monospace. Tooltip follows mouse cursor, clamped to viewport edges.
- **Click board:** Camera smoothly lerps to close-up of that board (~1s transition). Chips enlarge proportionally. Intra-board traces and labels become fully readable.
- **Click "All boards" or Escape:** Camera lerps back to overview showing all three boards.
- **Iteration dropdown:** Preserved from current version. Selecting a past iteration updates chip visibility and LED states based on what existed at that point.

**Technical constraints (Three.js r128):**
- CDN: `https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js`
- NO OrbitControls (not in r128 core — implement camera lerp manually)
- NO CapsuleGeometry (not in r128 — use BoxGeometry and SphereGeometry)
- NO 3D TextGeometry — all text via HTML overlay divs
- Background: `0x0D1117` (matches site dark theme)
- Raycaster for hover detection, onClick for zoom
- Component data loaded from `data/claw3d_components.json`
- Iteration data loaded from `data/claw3d_iterations.json`

**Data file:** `data/claw3d_components.json` — full schema with 3 boards, 24 chips, 5 connectors. See CLAUDE.md W2 for complete JSON.

**Success criteria:**
- Page loads at kylejeromethompson.com/claw3d.html, 0 JS console errors
- All 3 boards visible at default zoom, properly spaced
- Hover any chip → tooltip appears with name + status + detail
- Click any board → smooth zoom to board close-up
- Animated dashed traces flow between boards
- Iteration dropdown toggles chip states
- Screenshottable: a screenshot clearly communicates the architecture to a non-technical viewer

---

### W3: Bourdain Pipeline — Accelerated Phase 2-5 (P1)

**Objective:** Continue the Bourdain pipeline beyond Phase 1. Execute according to Qwen's scaling plan (`docs/bourdain-scaling-plan.md` from W1). If the scaling plan isn't ready, fall back to Phase 2 (videos 31-60).

**Context:** Phase 1 delivered 96 entities from 30 videos across 20 countries. The extraction prompt and pipeline config are established in `pipeline/config/bourdain/`. The pipeline scripts accept `--pipeline bourdain` flags.

**Default plan (Phase 2 — videos 31-60):**
1. `yt-dlp --playlist-items 31-60 -x --audio-format mp3` → `data/bourdain/audio/`
2. `faster-whisper` transcription — graduated tmux batches (G18), 3 batches of 10, timeout 600s, never simultaneous
3. `Gemini 2.5 Flash` extraction using `pipeline/config/bourdain/extraction_prompt.md`
4. `phase4_normalize.py --pipeline bourdain` — schema v3
5. `phase5_geocode.py --pipeline bourdain` — Nominatim 1 req/sec
6. `phase6_enrich.py --pipeline bourdain` — Google Places API
7. `phase7_load.py --pipeline bourdain --database staging` — staging only

**If Qwen scaling plan recommends collapsing phases or larger batches:** follow those recommendations instead. The goal is to move faster than CalGold/RickSteves — they averaged 4+ iterations per pipeline to reach Phase 5. Bourdain should reach Phase 5 in 2-3 iterations.

**Playlist:** `https://www.youtube.com/playlist?list=PLEVfhwFNb44fPn5N3OXk-aEHFvLOPzXKo`
**Machine:** NZXTcos (GPU required for transcription)
**DO NOT load to production. Staging only.**

**Success criteria:**
- 30 additional videos processed (or more per scaling plan)
- Entity count increase (expect ~150-300 new entities)
- Schema v3 compliance on all new entities
- Dedup against Phase 1's 96 entities (array merge for multi-episode locations)
- Checkpoint updated: `data/bourdain/checkpoint.json`

---

### W4: README Overhaul (P2)

**Objective:** Comprehensive README update — 3 iterations overdue.

**Required updates:**
- Version: Phase 10 v10.56 (ACTIVE)
- Status line: "Pipeline Expansion + PCB Architecture + Evaluator Hardening"
- Pipelines: add Bourdain row (t_log_type: bourdain, color: #8B5CF6, entity count, Phase 1 complete)
- Architecture section: replace solar system references with PCB architecture description. Link to `kylejeromethompson.com/claw3d.html` as "Interactive PCB Architecture Diagram"
- Middleware section: add evaluator fallback chain (Qwen → Gemini Flash → self-eval)
- Add G55 to gotcha summary
- Update entity counts (6,181 production + Bourdain staging count)
- Mermaid trident chart (graph BT, shaft #0D9488, prong #161B22 stroke #4ADE80)
- Changelog section: point to `docs/kjtcom-changelog.md`
- Update "Current state" line in Architecture section with v10.56 component counts

**Success criteria:**
- Bourdain pipeline listed with color code and entity count
- PCB architecture referenced (not solar system)
- Evaluator fallback chain documented
- `wc -l README.md` shows growth

---

## PRIORITY ORDER

1. **W1: Fix Qwen Evaluator** (P0) — unblocks all evaluation, produces Bourdain scaling plan
2. **W3: Bourdain Pipeline** (P1) — primary feature work, longest running, parallel on NZXTcos
3. **W2: Claw3D PCB Redesign** (P1) — parallel on tsP3-cos
4. **W4: README Overhaul** (P2) — after W2/W3 so entity counts and PCB links are current

---

## AGENT ASSIGNMENTS

| Workstream | Machine | Primary Agent | Evaluator | Key LLMs | Key MCPs |
|-----------|---------|---------------|-----------|----------|----------|
| W1 | NZXTcos | Claude Code | Qwen→Gemini→self | Qwen3.5-9B, Gemini Flash | - |
| W2 | tsP3-cos | Claude Code | (via W1 fallback) | - | Playwright (screenshot) |
| W3 | NZXTcos | Gemini CLI | (via W1 fallback) | Gemini 2.5 Flash (extraction) | Firebase |
| W4 | tsP3-cos | Claude Code | (via W1 fallback) | - | - |

---

## TRIDENT TARGETS

| Prong | Target |
|-------|--------|
| Cost | <100K Claude tokens. Gemini free tier for extraction. Ollama free for Qwen. |
| Delivery | 4/4 workstreams complete. Non-empty report (enforced by fallback chain). |
| Performance | Claw3D loads with hover tooltips. Bourdain entities in staging. Evaluator produces scored report. |

---

## FILES EXPECTED TO CHANGE

- `scripts/run_evaluator.py` — fallback chain implementation
- `app/web/claw3d.html` — complete PCB rewrite
- `data/claw3d_components.json` — new file, 24 chips across 3 boards
- `data/claw3d_iterations.json` — updated with v10.56 entry
- `data/bourdain/` — Phase 2 pipeline outputs
- `data/bourdain/checkpoint.json` — updated counts
- `docs/bourdain-scaling-plan.md` — new file, Qwen archive analysis
- `docs/phase9-retrospective.md` — no changes expected (rebuilt in v10.55)
- `docs/evaluator-harness.md` — append G55 pattern + fallback chain ADR
- `agent_scores.json` — v10.56 entry appended
- `README.md` — full overhaul
- `docs/kjtcom-changelog.md` — v10.56 entry
- `docs/kjtcom-build-v10.56.md` — build log
- `docs/kjtcom-report-v10.56.md` — evaluation report (non-empty, guaranteed)

---

*Design v10.56, April 06, 2026. 4 workstreams, PCB architecture, evaluator fallback chain.*
