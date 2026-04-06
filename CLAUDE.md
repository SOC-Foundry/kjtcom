# CLAUDE.md — kjtcom Agent Harness (Claude Code)

**Launch:** `read claude and execute 10.55`
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
5. Use `fish -c "..."` wrappers when executing shell commands (G19 — Gemini CLI runs bash by default).
6. Use `-u` flag on all Python scripts for unbuffered stdout.
7. Use `printf` blocks for all multi-line content — never heredocs.
8. Read the ENTIRE relevant file before editing — not just the function.
9. `grep` for ALL related patterns across `app/` before making changes.
10. Every iteration produces 4 artifacts: design, plan, build, report. No exceptions.
11. Post-flight (`python3 scripts/post_flight.py`) is MANDATORY before marking any iteration complete.
12. `10/10` scores are strictly prohibited in evaluator output.
13. The evaluator harness (`docs/evaluator-harness.md`) must NEVER shrink. Only append.
14. `agent_scores.json` is append-only. Never overwrite existing entries.
15. Changelog entries use prefixes: `NEW:`, `UPDATED:`, `FIXED:`. No fluff words (successfully, robust, comprehensive).

---

## PROJECT CONTEXT

kjtcom is a cross-pipeline location intelligence platform. YouTube playlists → entity extraction → Thompson Indicator Fields (`t_any_*`) → Firestore → Flutter Web frontend.

**Pipelines:**

| Pipeline | t_log_type | Color | Entities | Status |
|----------|-----------|-------|----------|--------|
| California's Gold | calgold | #DA7E12 | 899 | Active |
| Rick Steves' Europe | ricksteves | #3B82F6 | 4,182 | Active |
| Diners Drive-Ins and Dives | tripledb | #DD3333 | 1,100 | Active |
| Anthony Bourdain | bourdain | #8B5CF6 | 0 | **Phase 1 in v10.55** |

**Total production entities:** 6,181 across 3 pipelines.

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
| Gemini Flash | Intent routing, extraction, synthesis | API |

**MCP Servers:** Firebase, Context7, Playwright, Firecrawl, Dart/Flutter

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
| G47 | CanvasKit DOM interaction | Open | Playwright screenshots only, no DOM queries |
| G53 | Firebase MCP reauth | Recurring | Script wrapper with retry |
| G54 | Transitive deps locked by upstream | Active | Wait for upstream releases |

---

## ARTIFACT CONVENTIONS

**Naming:** `kjtcom-{type}-v{X.XX}.md` where type is design/plan/build/report
**Archive:** Previous iteration artifacts move to `docs/archive/` before new ones are created
**Changelog:** `docs/kjtcom-changelog.md` — every entry starts with `NEW:`, `UPDATED:`, or `FIXED:`
**README:** Version bump every iteration. Full overhaul every 3 iterations.
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

Every iteration MUST run `python3 scripts/post_flight.py` before completion. Post-flight verifies:
- Site returns 200 at kylejeromethompson.com
- Telegram bot responds to /status
- MCP server reachability
- Static assets exist and have valid HTML structure (claw3d.html, architecture.html)
- JSON data files are valid (claw3d_iterations.json)
- Flutter analyze: 0 issues
- Flutter test: all pass

---

## v10.55 WORKSTREAMS

### W1: Bourdain Pipeline — Phase 1 Discovery (P1)

**Playlist:** `https://www.youtube.com/playlist?list=PLEVfhwFNb44fPn5N3OXk-aEHFvLOPzXKo`
**Videos:** 1-30 of 114
**Machine:** NZXTcos (GPU required)
**Primary agent:** Gemini CLI (GEMINI.md) — Claude Code supports if needed

Pipeline execution:
1. `yt-dlp --playlist-items 1-30 -x --audio-format mp3` → `data/bourdain/audio/`
2. `faster-whisper` transcription (CUDA, graduated tmux batches per G18)
   - Batch 1: videos 1-10, timeout 600s
   - Batch 2: videos 11-20, timeout 600s
   - Batch 3: videos 21-30, timeout 600s
   - NEVER run simultaneous batches
3. `Gemini 2.5 Flash` extraction with Bourdain-specific prompt
   - `t_any_shows`: capture specific show (No Reservations, Parts Unknown, A Cook's Tour, The Layover)
   - High entity density expected (restaurants, markets, street food vendors, neighborhoods)
   - `t_any_cuisines` and `t_any_dishes` heavily populated
4. `phase4_normalize.py --pipeline bourdain` (schema v3)
5. `phase5_geocode.py --pipeline bourdain` (Nominatim 1 req/sec)
6. `phase6_enrich.py --pipeline bourdain` (Google Places API)
7. `phase7_load.py --pipeline bourdain --database staging`

**DO NOT load to production. Staging only.**
**Save checkpoint:** `data/bourdain/checkpoint.json`

Config:
- `t_log_type`: `bourdain`
- `t_source_label`: `Anthony Bourdain`
- Pipeline color: `#8B5CF6`

---

### W2: Phase 9 Retrospective Rebuild (P1)

**Output:** `docs/phase9-retrospective.md` — rebuilt from scratch.

The v10.54 version is rejected. 88 workstream rows say "Unknown." Analysis sections are generic.

Steps:
1. `command ls docs/archive/ | grep "v9\." | sort` — list all Phase 9 archives
2. Read EVERY `kjtcom-report-v9.XX.md` and `kjtcom-build-v9.XX.md` in `docs/archive/`
3. Build workstream inventory table: every row MUST have actual outcome (complete/partial/failed/deferred). If report file missing, mark `MISSING REPORT`. Zero "Unknown" rows.
4. Compute metrics from actual data:
   - Total workstreams planned vs. completed vs. partial vs. failed vs. deferred
   - Completion rate per iteration
   - Completion rate by priority (P0/P1/P2/P3)
   - Completion rate by category (UI fix, middleware, infrastructure, evaluator, documentation)
   - Intervention count per iteration
   - Multi-iteration bug traces: quote cursor (v9.29→v9.34, 7 attempts), 1000-result limit (v9.29→v9.31, 4 attempts), autocomplete (v9.30→v9.34, 5 attempts)
5. Write pattern analysis with specific iteration citations
6. Write gotcha analysis: every G## introduced in Phase 9, resolved vs. active, resolution durability
7. Write IAO methodology assessment with evidence

**Minimum 300 lines. Zero Unknown rows. At least 5 quantitative metrics computed from actual data.**

Verify: `wc -l docs/phase9-retrospective.md`

---

### W3: Fix Claw3D (P1)

**Problem:** `kylejeromethompson.com/claw3d.html` stuck on "Loading Static Solar System v10.54..." — JS initialization crashes before Three.js canvas renders.

**Diagnostic first. Do not blindly rewrite.**

1. Check Three.js CDN URL resolves:
   `curl -sI https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js | head -1`
2. Validate JSON: `python3 -c "import json; json.load(open('data/claw3d_iterations.json')); print('VALID')"`
3. Check fetch path in claw3d.html — Firebase Hosting serves from `app/web/` root. If the HTML fetches `data/claw3d_iterations.json` using a repo-relative path, it will 404 on Firebase. The JSON must either be in `app/web/` or fetched from a path relative to the hosted root.
   `grep -n "fetch\|\.json" app/web/claw3d.html`
4. Check for r128 API mismatches:
   - `THREE.OrbitControls` is NOT in r128 core — needs separate CDN import or removal
   - `THREE.CapsuleGeometry` does NOT exist in r128 — use CylinderGeometry or SphereGeometry
   - `grep -n "OrbitControls\|CapsuleGeometry" app/web/claw3d.html`
5. Serve locally: `cd app/web && python3 -m http.server 8080` — check browser console for errors

**Design requirements:**
- ALL objects visible in ONE viewport — nothing off-screen
- Static by default — readable as an architecture diagram, not a screensaver
- Animation: kill entirely OR add start/stop toggle (default: stopped)
- Keep iteration dropdown (v9.41-v9.53) with active/inactive coloring
- Must be screenshottable and explainable to non-technical audience

**Deploy:** `cd app && flutter build web && firebase deploy --only hosting`
**Verify:** Playwright screenshot or manual check. Browser console: 0 errors.

---

### W4: Fix agent_scores.json Pipeline (P2)

**Problem:** `agent_scores.json` not updating. The 91 lines added in v10.54 may be malformed or the write path is broken.

1. `cat agent_scores.json | python3 -m json.tool` — check structure
2. `grep -rn "agent_scores" scripts/` — trace all read/write paths
3. Verify `run_evaluator.py` appends to the `iterations` array using the canonical schema (see ARTIFACT CONVENTIONS above)
4. Fix the write path. Test: `python3 scripts/run_evaluator.py --iteration v10.55`
5. Verify: `python3 -c "import json; d=json.load(open('agent_scores.json')); print(len(d['iterations']), 'entries')"`

---

### W5: Post-Flight Static Asset Checks (P2)

**Problem:** Post-flight did not catch that Claw3D was broken. Add checks.

Add to `scripts/post_flight.py`:
1. File existence for `app/web/claw3d.html` and `app/web/architecture.html`
2. HTML structure validation: contains `<html` or `<!doctype`, contains `<script`
3. JSON validation for `data/claw3d_iterations.json`
4. Three.js CDN reachability (HTTP HEAD to the CDN URL in claw3d.html)

Run and verify all new checks pass.

---

## EXECUTION ORDER

1. W3: Fix Claw3D (quick diagnostic win, unblocks deploy)
2. W1: Bourdain Pipeline Phase 1 (primary feature work, longest)
3. W2: Phase 9 Retrospective Rebuild (data-driven analysis)
4. W4: Fix agent_scores.json (pipeline integrity)
5. W5: Post-Flight Enhancement (prevent future misses)
6. Post-flight + living docs (changelog, README, evaluator run)

---

## COMPLETION CHECKLIST

```
[ ] W3: claw3d.html loads, all nodes visible, 0 JS errors
[ ] W1: Bourdain Phase 1 entities in staging, checkpoint saved
[ ] W2: phase9-retrospective.md >= 300 lines, 0 Unknown rows, 5+ metrics
[ ] W4: agent_scores.json valid JSON, v10.55 entry present
[ ] W5: post_flight.py has static asset checks, all pass
[ ] post_flight.py passes all checks
[ ] docs/kjtcom-changelog.md updated with v10.55 entry
[ ] README.md version bumped to v10.55
[ ] All 4 artifacts produced: design, plan, build, report
```
