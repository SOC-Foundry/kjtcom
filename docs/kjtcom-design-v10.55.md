# kjtcom - Design Document v10.55

**Phase:** 10 - Pipeline Expansion & Platform Hardening
**Iteration:** 10.55
**Date:** April 05, 2026
**Previous:** v10.54 (hollow — evaluator produced empty scorecard despite 20 files changed)

---

## v10.54 POST-MORTEM

v10.54 delivered file changes but failed its own evaluation loop. Specific failures:

1. **Report/Build mismatch:** Build log claims W1-W3 complete at 10/10, but the Report shows "No workstream data" and 2 total events. The evaluator did not read its own build log.
2. **Phase 9 retrospective is shallow:** 88 of ~158 workstream rows have "Unknown" actual outcome. Sections 2-6 contain generic observations, not data extracted from the 27 archived iterations. The retrospective needs to be rebuilt from scratch by actually reading every `kjtcom-report-v9.XX.md` and `kjtcom-build-v9.XX.md` in `docs/archive/`.
3. **agent_scores.json not updating:** The file received 91 lines of additions in the diff but the scoring pipeline (`run_evaluator.py`) is not reading/writing it correctly. Either the JSON structure is malformed, the write path is wrong, or the evaluator isn't calling the score append function.
4. **Claw3D doesn't load:** `app/web/claw3d.html` was rebuilt (522 lines) but the page fails to render. This is a blocking visual for the portfolio site. Post-flight did not test static HTML assets — this is a gap in `post_flight.py`.
5. **Post-flight gap:** `post_flight.py` must add a local file existence + basic HTML validation check for `claw3d.html` and `architecture.html`. A simple check: file exists, contains `<html`, contains `<script`, no unclosed tags in the first 50 lines.

---

## WORKSTREAMS

### W1: Bourdain Pipeline — Phase 1 Discovery (P1)

**Objective:** Kick off Pipeline 4 (Anthony Bourdain) using the established 7-phase extraction pipeline. This iteration executes Phase 1 only (Discovery batch — first 30 of 114 videos).

**Playlist URL:** `https://www.youtube.com/playlist?list=PLEVfhwFNb44fPn5N3OXk-aEHFvLOPzXKo`
**Total videos:** 114
**Phase 1 batch:** Videos 1-30
**Pipeline ID:** `bourdain`
**t_log_type:** `bourdain`
**t_source_label:** `Anthony Bourdain`

**Phase 1 Steps:**
1. `yt-dlp` — Acquire 30 videos from the playlist (audio only, mp3)
2. `faster-whisper` (CUDA) — Transcribe to timestamped text
3. `Gemini 2.5 Flash API` — Extract entities using Bourdain-specific extraction prompt
4. `phase4_normalize.py` — Normalize to Thompson Indicator Fields (schema v3, `t_any_*`)
5. `phase5_geocode.py` — Geocode via Nominatim (1 req/sec)
6. `phase6_enrich.py` — Enrich via Google Places API (New)
7. `phase7_load.py` — Load to Firestore staging database

**Extraction prompt considerations:**
- Bourdain content is travel/food focused — expect high entity density per video (restaurants, street food vendors, markets, neighborhoods)
- Shows likely include: No Reservations, Parts Unknown, A Cook's Tour, The Layover
- Schema fields with high expected yield: `t_any_names`, `t_any_cities`, `t_any_countries`, `t_any_cuisines`, `t_any_dishes`, `t_any_keywords`, `t_any_people`
- Need to handle multi-show content — `t_any_shows` must capture the specific show per entity
- Dedup strategy: same restaurant appearing across episodes gets array-merged (existing pattern from CalGold/RickSteves)

**Success criteria:**
- 30/30 videos acquired (note unavailable count if any)
- 30/30 transcribed
- Entity count extracted (expect 200-400 based on CalGold/RickSteves ratios)
- Schema v3 compliance: 100% on required fields
- Geocoding rate: >90%
- Enrichment rate: >90%
- Entities loaded to staging Firestore
- Zero production impact (staging database only)

**Evidence required:**
- `data/bourdain/` directory with phase outputs
- Entity count, country count, geocoding %, enrichment %
- Any new gotchas logged

---

### W2: Phase 9 Retrospective Rebuild (P1)

**Objective:** Rebuild `docs/phase9-retrospective.md` from scratch. The v10.54 version is unacceptable — 88 workstream rows say "Unknown" and the analysis is generic.

**Requirements:**
1. **Read every archived iteration:** `docs/archive/kjtcom-report-v9.27.md` through `kjtcom-report-v9.53.md` AND `kjtcom-build-v9.27.md` through `kjtcom-build-v9.53.md`. That's up to 54 files. If some iterations are missing from archive, note which ones.
2. **Workstream inventory:** Every row must have an actual outcome (complete/partial/failed/deferred). No "Unknown" allowed. If the report for that iteration doesn't exist, mark as "MISSING REPORT" — do not guess.
3. **Quantitative analysis:**
   - Total workstreams planned vs. completed vs. partial vs. failed vs. deferred
   - Completion rate per iteration
   - Completion rate by priority (P0/P1/P2/P3)
   - Completion rate by workstream category (UI fix, middleware, infrastructure, evaluator, documentation)
   - Intervention count per iteration (from changelog or report)
   - Token spend trend if available from event logs
4. **Pattern analysis:**
   - Which workstream types consistently complete on first attempt?
   - Which types require multi-iteration rework? (list specific examples with iteration numbers)
   - What is the average number of iterations to resolve a recurring bug? (cite: quote cursor, 1000-result limit, autocomplete)
5. **Gotcha analysis:**
   - Total gotchas introduced during Phase 9
   - Resolved vs. still active
   - Which resolutions stuck vs. recurred (with iteration numbers)
   - Time-to-resolution distribution
6. **IAO methodology assessment:**
   - What worked: specific evidence, not generalities
   - What didn't work: specific evidence
   - Recommendations for Phase 10 with concrete actions

**Output:** `docs/phase9-retrospective.md` — minimum 300 lines, data-driven, no fluff.

**Evidence required:**
- `wc -l docs/phase9-retrospective.md` >= 300
- Zero rows with "Unknown" in the workstream inventory
- At least 5 quantitative metrics computed from actual data

---

### W3: Fix Claw3D (P1)

**Objective:** `kylejeromethompson.com/claw3d.html` must load and render correctly.

**Current state:** Page doesn't load at all. The v10.54 rebuild (522 lines) broke it.

**Diagnostic steps:**
1. Open `app/web/claw3d.html` and check for syntax errors (unclosed tags, malformed JS, missing Three.js CDN import)
2. Verify the Three.js CDN URL is valid and accessible
3. Check `data/claw3d_iterations.json` — is it valid JSON? Does the HTML reference the correct path?
4. Test locally: serve with `python3 -m http.server` and verify in browser (or use Playwright MCP to screenshot)

**Design requirements (carried from briefing):**
- ALL objects visible in ONE viewport — nothing off-screen
- Static by default — readable as an architecture diagram, not a screensaver
- Animation: kill entirely OR add a start/stop toggle (default: stopped)
- Consider 2D top-down orbital layout where positions are fixed and labeled
- Keep the iteration dropdown (v9.41-v9.53) with active/inactive coloring
- Must be screenshottable and explainable to a non-technical audience

**Success criteria:**
- Page loads without JS errors in browser console
- All nodes visible without scrolling or panning
- Labels readable at default zoom
- Iteration toggle functional

**Evidence required:**
- Playwright screenshot or manual verification
- `wc -l app/web/claw3d.html`
- Browser console error count: 0

---

### W4: Fix agent_scores.json Pipeline (P2)

**Objective:** The evaluator scoring pipeline must correctly read iteration results and append scores to `agent_scores.json`.

**Canonical schema (from v9.36 design):**
```json
{
  "iterations": [
    {
      "iteration": "v10.55",
      "date": "2026-04-05",
      "evaluator": "qwen3.5:9b",
      "scores": [
        {
          "agent": "claude-code-opus",
          "role": "primary_executor",
          "problem_analysis": 8,
          "code_correctness": 9,
          "efficiency": 7,
          "gotcha_avoidance": 10,
          "novel_contribution": 6,
          "total": 40,
          "notes": "Brief justification"
        }
      ],
      "gotcha_events": []
    }
  ]
}
```

**5 scoring dimensions (0-10 each, max 50):**
1. Problem Analysis — correctly identified the problem and proposed viable approaches?
2. Code Correctness — code suggestions accurate, functional, regression-free?
3. Efficiency — tokens consumed vs value delivered?
4. Gotcha Avoidance — avoided repeating known failure patterns?
5. Novel Contribution — surfaced approaches or insights others missed?

**Diagnostic steps:**
1. `cat agent_scores.json | python3 -m json.tool` — check structure matches canonical schema
2. `grep -n "agent_scores" scripts/run_evaluator.py` — find where it reads/writes
3. `grep -n "agent_scores" scripts/generate_artifacts.py` — find where it reads/writes
4. Trace the data flow: where does the score get computed? Where does it get written? Is the file path correct?
5. Check if the 91 lines added in v10.54 are valid entries or template stubs
6. Verify `run_evaluator.py` calls the Ollama API with the correct scoring prompt and parses the JSON response

**Fix requirements:**
- `agent_scores.json` must use the canonical `iterations` array schema above
- Each entry must have all 5 scoring dimensions per agent, plus total
- `run_evaluator.py` must append to the `iterations` array as its final step (append-only, never overwrite)
- After v10.55 completes, `agent_scores.json` must have a valid entry for v10.55

**Evidence required:**
- `python3 -c "import json; d=json.load(open('agent_scores.json')); print(len(d['iterations']), 'entries')"` — valid JSON with correct structure
- v10.55 entry present after evaluation
- Each score entry has all 5 dimensions populated (no nulls except for unused agents)

---

### W5: Post-Flight Enhancement — Static Asset Checks (P2)

**Objective:** `post_flight.py` must verify that static HTML assets (`claw3d.html`, `architecture.html`) are valid and loadable.

**New checks to add:**
1. File existence check for `app/web/claw3d.html` and `app/web/architecture.html`
2. Basic HTML validation: file contains `<!DOCTYPE` or `<html`, contains `<script`
3. Three.js CDN reachability check (HTTP HEAD request to the CDN URL used in `claw3d.html`)
4. JSON data file validation: `data/claw3d_iterations.json` is valid JSON
5. Optional: If Playwright MCP is available, screenshot `claw3d.html` served locally and verify image is not blank

**Evidence required:**
- `post_flight.py` diff showing new checks
- Post-flight output showing PASS for static asset checks

---

## PRIORITY ORDER

1. **W3: Fix Claw3D** — unblocks visual portfolio, quick diagnostic win
2. **W1: Bourdain Pipeline Phase 1** — primary feature work, highest value
3. **W2: Phase 9 Retrospective Rebuild** — required for methodology credibility
4. **W4: Fix agent_scores.json** — pipeline integrity
5. **W5: Post-Flight Enhancement** — prevents future Claw3D-type misses

---

## AGENT ASSIGNMENTS

| Workstream | Primary Agent | Evaluator | LLMs | MCPs |
|-----------|---------------|-----------|------|------|
| W1 | Gemini CLI | Qwen3.5-9B | Gemini 2.5 Flash (extraction) | Firebase, Context7 |
| W2 | Claude Code | Qwen3.5-9B | - | - |
| W3 | Claude Code | Qwen3.5-9B | - | Playwright (screenshot) |
| W4 | Claude Code | Qwen3.5-9B | - | - |
| W5 | Claude Code | Qwen3.5-9B | - | - |

---

## TRIDENT TARGETS

| Prong | Target |
|-------|--------|
| Cost | <100K Claude tokens (heavy iteration). Gemini free tier for extraction. |
| Delivery | 5/5 workstreams complete |
| Performance | Schema-validated Qwen eval. Claw3D loads. Bourdain Phase 1 entities in staging. |

---

## FILES EXPECTED TO CHANGE

- `data/bourdain/` — new directory with pipeline outputs
- `docs/phase9-retrospective.md` — rebuilt from scratch
- `app/web/claw3d.html` — fixed to load and render
- `agent_scores.json` — pipeline fixed, v10.55 entry appended
- `scripts/post_flight.py` — static asset checks added
- `docs/kjtcom-changelog.md` — v10.55 entry
- `docs/kjtcom-build-v10.55.md` — build log
- `docs/kjtcom-report-v10.55.md` — evaluation report
- `README.md` — version bump to v10.55

---

## LAUNCH PROMPT

```
Read CLAUDE.md and execute.
```

For Bourdain pipeline specifically:
```
Read GEMINI.md and execute W1 (Bourdain Pipeline Phase 1). Playlist URL: https://www.youtube.com/playlist?list=PLEVfhwFNb44fPn5N3OXk-aEHFvLOPzXKo