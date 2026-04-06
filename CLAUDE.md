# CLAUDE.md — kjtcom Agent Harness (Claude Code)

**Launch:** `read claude and execute 10.56`
**Repo:** SOC-Foundry/kjtcom
**Site:** kylejeromethompson.com
**Firebase:** kjtcom-c78cd (Blaze)
**Shell:** fish + tmux on NZXTcos and tsP3-cos

---

## RULES

1. **NEVER** run `git commit`, `git push`, or any git write operation. All git operations are manual (Kyle only).
2. **NEVER** use heredocs in shell commands. Use `printf` blocks only (G1).
3. **NEVER** run simultaneous GPU processes. Graduated tmux batches only (G18 — RTX 2080 SUPER 8GB VRAM).
4. Use `command ls` to avoid color code pollution in output (G22).
5. Use `fish -c "..."` wrappers when executing shell commands (G19).
6. Use `-u` flag on all Python scripts for unbuffered stdout.
7. Read the ENTIRE relevant file before editing — not just the function.
8. `grep` for ALL related patterns across `app/` before making changes.
9. Every iteration produces 4 artifacts: design, plan, build, report. No exceptions.
10. Post-flight (`python3 scripts/post_flight.py`) is MANDATORY before marking any iteration complete.
11. `10/10` scores are strictly prohibited in evaluator output.
12. The evaluator harness (`docs/evaluator-harness.md`) must NEVER shrink. Only append.
13. `agent_scores.json` is append-only. Never overwrite existing entries.
14. Changelog entries use prefixes: `NEW:`, `UPDATED:`, `FIXED:`. No fluff words (successfully, robust, comprehensive).
15. **REPORTS ARE MANDATORY.** If Qwen fails to produce a valid report, the executing agent MUST produce the report itself. An empty scorecard is NEVER acceptable. See EVALUATOR FALLBACK CHAIN below.

---

## PROJECT CONTEXT

kjtcom is a cross-pipeline location intelligence platform. YouTube playlists → entity extraction → Thompson Indicator Fields (`t_any_*`) → Firestore → Flutter Web frontend.

**Pipelines:**

| Pipeline | t_log_type | Color | Entities | Status |
|----------|-----------|-------|----------|--------|
| California's Gold | calgold | #DA7E12 | 899 | Active |
| Rick Steves' Europe | ricksteves | #3B82F6 | 4,182 | Active |
| Diners Drive-Ins and Dives | tripledb | #DD3333 | 1,100 | Active |
| Anthony Bourdain | bourdain | #8B5CF6 | 96 | **Phase 1 complete (staging)** |

**Total production entities:** 6,181 across 3 pipelines. Bourdain has 96 in staging.

**Thompson Indicator Fields (schema v3):** `t_log_type`, `t_row_id`, `t_event_time`, `t_parse_time`, `t_source_label`, `t_schema_version`, `t_any_names`, `t_any_people`, `t_any_cities`, `t_any_states`, `t_any_counties`, `t_any_countries`, `t_any_country_codes`, `t_any_regions`, `t_any_coordinates`, `t_any_geohashes`, `t_any_keywords`, `t_any_categories`, `t_any_actors`, `t_any_roles`, `t_any_shows`, `t_any_cuisines`, `t_any_dishes`, `t_any_eras`, `t_any_continents`

---

## AGENT MODEL

| Agent | Role | When |
|-------|------|------|
| Claude Code | Primary executor (Phases 6-7, app fixes, docs) | This file |
| Gemini CLI | Primary executor (Phases 1-5, extraction) | GEMINI.md |
| Qwen3.5-9B | Evaluator (permanent, local Ollama) | docs/evaluator-harness.md |
| Nemotron Mini 4B | Code review (local Ollama) | On-demand |
| GLM-4.6V-Flash | Visual review (local Ollama) | On-demand |
| Gemini Flash | Intent routing, extraction, synthesis, **evaluator fallback** | API |

**MCP Servers:** Firebase, Context7, Playwright, Firecrawl, Dart/Flutter

---

## EVALUATOR FALLBACK CHAIN

**Problem:** Qwen produced 3 consecutive empty reports (v10.54, v10.55, v10.55-retry). Reports are the audit trail — without them, the iteration didn't happen.

**Fallback chain (try in order):**

```
1. Qwen3.5-9B (via Ollama API, docs/evaluator-harness.md)
   - Feed: build log + design doc + event log
   - Validate: JSON schema check on output
   - If valid → use as report
   - If invalid after 3 retries → fall through

2. Gemini Flash (via API, same prompt as Qwen)
   - Feed: same context
   - Validate: same schema check
   - If valid → use as report, note "Evaluator: gemini-flash (Qwen fallback)"
   - If invalid after 2 retries → fall through

3. Executing agent (Claude Code or Gemini CLI) produces report directly
   - Use the evaluator harness as a rubric
   - Self-evaluate honestly (no self-grading bias — cap own scores at 7/10)
   - Note "Evaluator: self-eval (Qwen + Gemini fallback)"
   - This ALWAYS succeeds. There is no scenario where no report is produced.
```

**Implementation in `run_evaluator.py`:**
```python
def evaluate(build_log, design_doc, event_log):
    # Attempt 1: Qwen
    for attempt in range(3):
        result = call_ollama("qwen3.5:9b", prompt)
        if validate_schema(result):
            return result, "qwen3.5:9b"
    
    # Attempt 2: Gemini Flash
    for attempt in range(2):
        result = call_gemini_flash(prompt)
        if validate_schema(result):
            return result, "gemini-flash (qwen-fallback)"
    
    # Attempt 3: Executor self-eval
    return generate_self_eval(build_log, design_doc), "self-eval (fallback)"
```

**The executing agent MUST check the report after `run_evaluator.py` completes.** If the report has an empty scorecard, the agent must produce the report itself before marking the iteration complete.

---

## ACTIVE GOTCHAS

| ID | Title | Status | Workaround |
|----|-------|--------|------------|
| G1 | Heredocs break agents | Active | printf blocks only |
| G18 | CUDA OOM on RTX 2080 SUPER | Active | Graduated tmux batches, never simultaneous |
| G19 | Gemini CLI runs bash | Active | fish -c wrappers |
| G22 | ls color codes in output | Active | command ls |
| G34 | Firestore single array-contains | Active | Client-side post-filter |
| G45 | Query editor cursor bug | Active | flutter_code_editor migration pending |
| G47 | CanvasKit DOM interaction | Open | Playwright screenshots only |
| G53 | Firebase MCP reauth | Recurring | Script wrapper with retry |
| G54 | Transitive deps locked | Active | Wait for upstream |
| G55 | Qwen evaluator empty reports | **NEW** | Fallback chain (see above) |

---

## ARTIFACT CONVENTIONS

**Naming:** `kjtcom-{type}-v{X.XX}.md` where type is design/plan/build/report
**Archive:** Previous iteration artifacts move to `docs/archive/`
**Changelog:** `docs/kjtcom-changelog.md` — every entry starts with `NEW:`, `UPDATED:`, or `FIXED:`
**README:** Version bump every iteration. Full overhaul this iteration (every 3 iterations).
**Evaluator harness:** `docs/evaluator-harness.md` — living document, never shrinks, currently 528 lines

**agent_scores.json schema:**
```json
{
  "iterations": [
    {
      "iteration": "vX.XX",
      "date": "YYYY-MM-DD",
      "evaluator": "qwen3.5:9b",
      "scores": [
        {
          "agent": "agent-name",
          "role": "role-in-iteration",
          "problem_analysis": 0,
          "code_correctness": 0,
          "efficiency": 0,
          "gotcha_avoidance": 0,
          "novel_contribution": 0,
          "total": 0,
          "notes": "Brief justification"
        }
      ],
      "gotcha_events": []
    }
  ]
}
```

---

## POST-FLIGHT CHECKLIST

Every iteration MUST run `python3 scripts/post_flight.py` before completion. Checks:
- Site returns 200 at kylejeromethompson.com
- Telegram bot responds to /status
- MCP server reachability
- Static assets: claw3d.html, architecture.html (exist + valid HTML + script tags)
- JSON data files: claw3d_iterations.json, claw3d_components.json valid
- Flutter analyze: 0 issues
- Flutter test: all pass
- **NEW:** Report scorecard is non-empty (at least 1 workstream row with a score)

---

## v10.56 WORKSTREAMS

### W1: Fix Qwen Evaluator + Fallback Chain + Archive Analysis (P0)

**This is P0 because without a working evaluator, the IAO methodology is broken.**

**Step 1: Diagnose `run_evaluator.py`**
1. `wc -l scripts/run_evaluator.py`
2. `grep -n "ollama\|qwen\|json\|schema\|validate" scripts/run_evaluator.py`
3. Trace the data flow: does the script read the build log? Does it pass it to Qwen as context? Does it parse the JSON response? Does it validate against `data/eval_schema.json`?
4. Run manually: `python3 -u scripts/run_evaluator.py --iteration v10.55 --verbose`
5. Check Qwen is responsive: `curl -s http://localhost:11434/api/chat -d '{"model":"qwen3.5:9b","messages":[{"role":"user","content":"Say hello"}],"stream":false}' | python3 -c "import sys,json; print(json.load(sys.stdin)['message']['content'])"`
6. **Most likely root cause:** The script isn't feeding the build log content to Qwen, OR Qwen's JSON output fails schema validation and the fallback writes an empty template instead of retrying.

**Step 2: Implement fallback chain**
- Qwen (3 attempts) → Gemini Flash (2 attempts) → self-eval (always succeeds)
- Log which evaluator produced the report
- Add `--verbose` flag for debugging

**Step 3: Feed Qwen the full archive for Bourdain scaling**
Once evaluator is fixed, run a dedicated Qwen analysis session:
- Feed ALL Phase 1-5 reports from CalGold, RickSteves, TripleDB (from `docs/archive/`)
- Prompt: "Analyze these pipeline execution reports. For each phase (1-5), identify: average iteration count, common failure patterns, which phases can be parallelized or collapsed, optimal batch sizes, and expected entity yield per video. Produce a concrete execution plan for running the Bourdain pipeline (114 videos) from Phase 2 through Phase 5 in the minimum number of iterations."
- Save to `docs/bourdain-scaling-plan.md`

**Evidence required:**
- `run_evaluator.py` produces a non-empty report for v10.56
- Fallback chain code exists with Qwen → Gemini → self-eval
- `docs/bourdain-scaling-plan.md` exists
- `agent_scores.json` has v10.56 entry

---

### W2: Claw3D PCB Redesign (P1)

**Kill the solar system. Replace with a three-board PCB architecture visualization.**

**Concept:** Three circuit boards (Frontend, Middleware, Backend) arranged as separate planes. IC chip components on each board with copper trace connectors, LED status indicators, and pin arrays. Animated dashed-line traces flow between boards. Click board to zoom in. Hover any chip for detail tooltip.

**Board layout:**
```
[Frontend Board]  — #0D9488 border, teal traces
    gap (animated inter-board traces)
[Middleware Board] — #8B5CF6 border, purple traces
    gap (animated inter-board traces)
[Backend Board]   — #3B82F6 border, blue traces
```

**Frontend board chips:**
| Chip | Status | Tooltip Detail |
|------|--------|----------------|
| query_editor | active | NoSQL parser, syntax highlighting |
| results_table | active | Paginated grid, 20/50/100 per page |
| detail_panel | active | Entity inspector, t_any_* field cards |
| map_tab | active | OpenStreetMap, pipeline-colored markers |
| globe_tab | active | Continent cards, country grid |
| iao_tab | active | Trident SVG, 10 pillar cards |
| mw_tab | active | 33 middleware components |
| schema_tab | active | 22 Thompson Indicator Fields |

**Middleware board chips:**
| Chip | Status | Tooltip Detail |
|------|--------|----------------|
| intent_router | active | 3-route Gemini Flash (firestore/chromadb/web) |
| rag_pipeline | active | 1,819 chunks in ChromaDB, nomic-embed-text |
| evaluator | **degraded** | Qwen 528-line harness, G55 empty reports |
| telegram_bot | active | systemd managed, session memory, rating sort |
| artifact_gen | active | 4-doc loop (design/plan/build/report) |
| post_flight | active | 14 checks, static asset validation |
| gotcha_archive | active | 18+ resolved patterns, G1-G55 |
| agent_scores | **degraded** | Append-only, 5-dim scoring, canonical schema |

**Backend board chips:**
| Chip | Status | Tooltip Detail | Border Color |
|------|--------|----------------|-------------|
| calgold | active | 899 entities, California's Gold | #DA7E12 |
| ricksteves | active | 4,182 entities, Rick Steves' Europe | #3B82F6 |
| tripledb | active | 1,100 entities, Diners Drive-Ins and Dives | #DD3333 |
| bourdain | **degraded** | 96 staging entities, Phase 1 complete | #8B5CF6 |
| qwen_9b | **degraded** | Evaluator LLM, 256K context, G55 | default |
| nemotron_4b | active | Code review, 4K context | default |
| chromadb | active | Vector store, 1,819 chunks | default |
| firebase_mcp | active | G53 recurring reauth | default |

**Inter-board connectors (animated dashed traces):**
- Frontend → Middleware: "Riverpod state", "Firestore stream"
- Middleware → Backend: "Ollama API", "Firebase Admin SDK", "ChromaDB embed"
- Orthogonal routing only (L-bends), never through chips

**Interaction:**
- **Hover chip:** Tooltip appears with chip name, status LED, detail text. Tooltip follows mouse, stays within viewport bounds. Tooltip has dark background with monospace text (matches SIEM aesthetic).
- **Click board:** Camera smoothly lerps to close-up of that board. Chips enlarge, intra-board traces become visible, labels fully readable.
- **Click "All boards" / press Escape:** Camera lerps back to overview.
- **Iteration dropdown:** Select iteration → chips update active/inactive/degraded state. Boards always visible, chips within them toggle based on what existed at that iteration.

**Technical constraints:**
- Three.js r128 via `https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js`
- NO OrbitControls import (not in r128 core)
- NO CapsuleGeometry (not in r128)
- Chips: `BoxGeometry` (flat, height=0.1) with `MeshBasicMaterial`
- Boards: `PlaneGeometry` with thin border via `EdgesGeometry` + `LineSegments`
- Text labels: HTML overlay div positioned via `Vector3.project()` — NOT 3D TextGeometry
- Tooltips: HTML div, absolutely positioned, show/hide on raycaster intersect
- Zoom: camera position lerp using `Vector3.lerp()` in render loop
- Inter-board traces: `Line` with `LineDashedMaterial`, animate `dashOffset` in render loop
- Intra-board traces: thin `LineSegments` connecting related chips
- LED indicators: tiny `SphereGeometry` (radius=0.05) on each chip corner
- Status colors: active=#4ADE80, degraded=#EF9F27, inactive=gray
- Background: `scene.background = new THREE.Color(0x0D1117)`
- Load from `data/claw3d_components.json` and `data/claw3d_iterations.json`

**Data file: `data/claw3d_components.json`**
```json
{
  "boards": [
    {
      "id": "frontend",
      "label": "Frontend board",
      "color": "#0D9488",
      "components": [
        {"id": "query_editor", "label": "query_editor", "status": "active", "detail": "NoSQL parser, syntax highlighting"},
        {"id": "results_table", "label": "results_table", "status": "active", "detail": "Paginated grid, 20/50/100"},
        {"id": "detail_panel", "label": "detail_panel", "status": "active", "detail": "Entity inspector, t_any_* cards"},
        {"id": "map_tab", "label": "map_tab", "status": "active", "detail": "OpenStreetMap, colored markers"},
        {"id": "globe_tab", "label": "globe_tab", "status": "active", "detail": "Continent cards, country grid"},
        {"id": "iao_tab", "label": "iao_tab", "status": "active", "detail": "Trident SVG, 10 pillars"},
        {"id": "mw_tab", "label": "mw_tab", "status": "active", "detail": "33 middleware components"},
        {"id": "schema_tab", "label": "schema_tab", "status": "active", "detail": "22 Thompson Indicator Fields"}
      ]
    },
    {
      "id": "middleware",
      "label": "Middleware board",
      "color": "#8B5CF6",
      "components": [
        {"id": "intent_router", "label": "intent_router", "status": "active", "detail": "3-route Gemini Flash"},
        {"id": "rag_pipeline", "label": "rag_pipeline", "status": "active", "detail": "1,819 ChromaDB chunks"},
        {"id": "evaluator", "label": "evaluator", "status": "degraded", "detail": "Qwen 528-line harness, G55"},
        {"id": "telegram_bot", "label": "telegram_bot", "status": "active", "detail": "systemd, session memory"},
        {"id": "artifact_gen", "label": "artifact_gen", "status": "active", "detail": "4-doc artifact loop"},
        {"id": "post_flight", "label": "post_flight", "status": "active", "detail": "14 validation checks"},
        {"id": "gotcha_archive", "label": "gotcha_archive", "status": "active", "detail": "18+ resolved, G1-G55"},
        {"id": "agent_scores", "label": "agent_scores", "status": "degraded", "detail": "5-dim scoring, append-only"}
      ]
    },
    {
      "id": "backend",
      "label": "Backend board",
      "color": "#3B82F6",
      "components": [
        {"id": "calgold", "label": "calgold", "status": "active", "detail": "899 entities", "color": "#DA7E12"},
        {"id": "ricksteves", "label": "ricksteves", "status": "active", "detail": "4,182 entities", "color": "#3B82F6"},
        {"id": "tripledb", "label": "tripledb", "status": "active", "detail": "1,100 entities", "color": "#DD3333"},
        {"id": "bourdain", "label": "bourdain", "status": "degraded", "detail": "96 staging entities", "color": "#8B5CF6"},
        {"id": "qwen_9b", "label": "qwen_9b", "status": "degraded", "detail": "Evaluator LLM, 256K ctx"},
        {"id": "nemotron_4b", "label": "nemotron_4b", "status": "active", "detail": "Code review, 4K ctx"},
        {"id": "chromadb", "label": "chromadb", "status": "active", "detail": "Vector store, nomic-embed"},
        {"id": "firebase_mcp", "label": "firebase_mcp", "status": "active", "detail": "G53 recurring reauth"}
      ]
    }
  ],
  "connectors": [
    {"from": "frontend", "to": "middleware", "label": "Riverpod state", "color": "#0D9488"},
    {"from": "frontend", "to": "middleware", "label": "Firestore stream", "color": "#0D9488"},
    {"from": "middleware", "to": "backend", "label": "Ollama API", "color": "#8B5CF6"},
    {"from": "middleware", "to": "backend", "label": "Firebase Admin SDK", "color": "#3B82F6"},
    {"from": "middleware", "to": "backend", "label": "ChromaDB embed", "color": "#8B5CF6"}
  ]
}
```

**Evidence required:**
- `app/web/claw3d.html` loads, 0 JS errors
- All 3 boards visible at default zoom
- Hover tooltip works on any chip (shows name + status + detail)
- Click-to-zoom works on each board
- Animated traces visible between boards
- `data/claw3d_components.json` valid JSON, 24 chips across 3 boards

---

### W3: Bourdain Pipeline — Accelerated Phase 2-5 (P1)

**Depends on W1 output (`docs/bourdain-scaling-plan.md`).** Execute Qwen's recommended plan.

**Default plan if Qwen analysis not ready — Phase 2 (videos 31-60):**
```
yt-dlp --playlist-items 31-60 -x --audio-format mp3
faster-whisper (CUDA, graduated tmux batches per G18)
Gemini Flash extraction (pipeline/config/bourdain/extraction_prompt.md)
phase4_normalize.py --pipeline bourdain
phase5_geocode.py --pipeline bourdain
phase6_enrich.py --pipeline bourdain
phase7_load.py --pipeline bourdain --database staging
```

**Playlist:** `https://www.youtube.com/playlist?list=PLEVfhwFNb44fPn5N3OXk-aEHFvLOPzXKo`
**Machine:** NZXTcos (GPU required)
**DO NOT load to production. Staging only.**

**Evidence:** Entity count increase, checkpoint updated, schema v3 verified.

---

### W4: README Overhaul (P2)

Updates required:
- Phase 10 active, v10.56
- 4 pipelines (add Bourdain: #8B5CF6, entity count, Phase 1 complete)
- Replace solar system references with PCB architecture
- Update Architecture section links
- Mermaid trident chart (graph BT, shaft=#0D9488, prong=#161B22 stroke #4ADE80)
- G55 in gotcha summary
- Evaluator fallback chain in middleware description

---

## EXECUTION ORDER

1. **W1** — Fix evaluator (P0, unblocks everything)
2. **W3** — Bourdain pipeline (P1, longest, start on NZXTcos in parallel)
3. **W2** — Claw3D PCB redesign (P1, tsP3-cos)
4. **W4** — README overhaul (P2, after W2/W3 so counts are current)
5. Post-flight + living docs + report (with working fallback chain)

---

## COMPLETION CHECKLIST

```
[ ] W1: run_evaluator.py produces non-empty report with fallback chain
[ ] W1: docs/bourdain-scaling-plan.md exists (Qwen archive analysis)
[ ] W1: agent_scores.json has v10.56 entry
[ ] W2: claw3d.html loads PCB layout, 0 JS errors
[ ] W2: Hover tooltips work on chips (name + status + detail)
[ ] W2: Click-to-zoom works on boards
[ ] W2: data/claw3d_components.json exists, 24 chips, valid JSON
[ ] W3: Bourdain entity count increased in staging
[ ] W3: data/bourdain/checkpoint.json updated
[ ] W4: README.md overhauled, Bourdain listed, PCB referenced
[ ] Report has non-empty scorecard (enforced by fallback chain)
[ ] post_flight.py passes all checks
[ ] docs/kjtcom-changelog.md updated
[ ] All 4 artifacts produced: design, plan, build, report
```
