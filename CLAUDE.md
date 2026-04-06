# CLAUDE.md — kjtcom Agent Harness (Claude Code)

**Launch:** `read claude and execute 10.57`
**Repo:** SOC-Foundry/kjtcom
**Site:** kylejeromethompson.com
**Firebase:** kjtcom-c78cd (Blaze)
**Shell:** fish + tmux on NZXTcos and tsP3-cos

---

## RULES

1. **NEVER** run `git commit`, `git push`, or any git write operation. All git operations are manual (Kyle only).
2. **NEVER** use heredocs. Use `printf` blocks only (G1).
3. **NEVER** run simultaneous GPU processes. Graduated tmux batches only (G18).
4. Use `command ls` to avoid color codes (G22). Use `fish -c "..."` wrappers (G19).
5. Use `-u` flag on all Python scripts for unbuffered stdout.
6. Read the ENTIRE relevant file before editing. `grep` for ALL related patterns across `app/`.
7. Every iteration produces 4 artifacts: design, plan, build, report. No exceptions.
8. Post-flight (`python3 scripts/post_flight.py`) is MANDATORY before marking any iteration complete.
9. `10/10` scores prohibited. `agent_scores.json` is append-only. Evaluator harness never shrinks.
10. Changelog prefixes: `NEW:`, `UPDATED:`, `FIXED:`. No fluff words.
11. **REPORTS ARE MANDATORY.** Fallback chain: Qwen → Gemini Flash → self-eval. Empty scorecards are never acceptable.
12. **Claw3D JSON must be INLINE in the HTML file.** Do NOT use fetch() for any JSON data. Firebase Hosting does not serve `data/` directory files. This has broken Claw3D in v10.54, v10.55, and v10.56 (G56). Embed all component and iteration data as JS objects directly in the script block.

---

## PROJECT CONTEXT

Cross-pipeline location intelligence platform. YouTube playlists → Thompson Indicator Fields (`t_any_*`) → Firestore → Flutter Web.

| Pipeline | t_log_type | Color | Entities | Status |
|----------|-----------|-------|----------|--------|
| California's Gold | calgold | #DA7E12 | 899 | Production |
| Rick Steves' Europe | ricksteves | #3B82F6 | 4,182 | Production |
| Diners Drive-Ins and Dives | tripledb | #DD3333 | 1,100 | Production |
| Anthony Bourdain | bourdain | #8B5CF6 | 188 | **Staging (Phase 2)** |

**Total:** 6,181 production + 188 staging.

---

## AGENT MODEL

| Agent | Role | When |
|-------|------|------|
| Claude Code | Primary executor (Phases 6-7, app, docs) | This file |
| Gemini CLI | Primary executor (Phases 1-5) | GEMINI.md |
| Qwen3.5-9B | Evaluator (local Ollama) | docs/evaluator-harness.md |
| Gemini Flash | Intent routing, extraction, **evaluator fallback** | API |

**Evaluator fallback:** Qwen (3 attempts) → Gemini Flash (2 attempts) → self-eval (always succeeds, cap 7/10)

**MCP Servers:** Firebase, Context7, Playwright, Firecrawl, Dart/Flutter

---

## ACTIVE GOTCHAS

| ID | Title | Status | Workaround |
|----|-------|--------|------------|
| G1 | Heredocs break agents | Active | printf only |
| G18 | CUDA OOM RTX 2080 SUPER | Active | Graduated tmux, unload Ollama first |
| G19 | Gemini CLI runs bash | Active | fish -c wrappers |
| G34 | Firestore array-contains | Active | Client-side post-filter |
| G45 | Query editor cursor | Active | flutter_code_editor pending |
| G47 | CanvasKit DOM | Open | Playwright screenshots only |
| G53 | Firebase MCP reauth | Recurring | Script wrapper with retry |
| G55 | Qwen empty reports | Resolved v10.56 | Fallback chain |
| **G56** | **Claw3D fetch() 404 on Firebase Hosting** | **NEW** | **Inline all data as JS objects. NEVER fetch .json** |

---

## ARTIFACT CONVENTIONS

**Naming:** `kjtcom-{type}-v{X.XX}.md` (design/plan/build/report)
**Archive:** Previous artifacts → `docs/archive/`
**Changelog:** `docs/kjtcom-changelog.md` — `NEW:` / `UPDATED:` / `FIXED:` prefixes
**Evaluator harness:** `docs/evaluator-harness.md` — living document, 601+ lines, contains ADRs
**agent_scores.json:** Canonical `{"iterations": [...]}` schema, 5 scoring dimensions (0-10, max 50)

---

## v10.57 WORKSTREAMS

### W1: Claw3D 4-Board PCB — Fix G56 + New Layout (P0)

**G56 root cause:** `claw3d.html` fetches external JSON files (`claw3d_components.json`, `claw3d_iterations.json`). These files live in `data/` in the repo. Firebase Hosting only serves `app/web/` build output. The fetch 404s. This has broken Claw3D in v10.54, v10.55, and v10.56.

**Fix:** ALL data must be inline JavaScript objects inside `claw3d.html`. No `fetch()`. No external JSON. The file must be 100% self-contained.

**New 4-board layout (per Kyle's sketch):**
```
┌──────────┐  ┌──────────┐
│ Frontend │  │ Pipeline │     ← small boards, side by side, top row
└────┬─────┘  └────┬─────┘
     │              │
     ▼              ▼
┌─────────────────────────────┐
│                             │
│        Middleware            │  ← LARGE board, full width, significantly bigger
│                             │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│          Backend            │  ← full width, bottom
└─────────────────────────────┘
```

**Board assignments (what lives where):**

**Frontend** (#0D9488 teal, top-left, small) — what's deployed in Firebase:
- query_editor, results_table, detail_panel
- map_tab, globe_tab, iao_tab, mw_tab, schema_tab
- claw3d, firebase_hosting

**Pipeline** (#DA7E12 amber, top-right, small) — local GPU extraction scripts:
- yt_dlp, faster_whisper, gemini_extract
- normalize, geocode, enrich, load
- tmux_runner, checkpoint

**Middleware** (#8B5CF6 purple, center, LARGE) — the hub. Everything routes through here:
- Harness & evaluation: evaluator, harness, ADR, artifact_gen, gotcha_archive, agent_scores
- Operations: pre_flight, post_flight, intent_router, telegram_bot, rag_pipeline
- LLMs: qwen_9b, nemotron_4b, gemini_flash
- MCPs: firebase_mcp, context7_mcp, playwright_mcp, firecrawl_mcp, dart_mcp
- Agents: claude_code, gemini_cli

**Backend** (#3B82F6 blue, bottom, full width) — Firestore + log sources:
- firestore (locations collection)
- production_db, staging_db
- Log sources: calgold (#DA7E12, 899), ricksteves (#3B82F6, 4,182), tripledb (#DD3333, 1,100), bourdain (#8B5CF6, 188)

**Component placement rule:** If a component is used in multiple boards (e.g. Gemini Flash is both pipeline extraction AND middleware intent routing), defer to Middleware unless it is a primary component of that board (Flutter → Frontend, Firestore → Backend, faster-whisper → Pipeline).

**Connectors (animated dashed traces):**
- Frontend → Middleware (down-left): Riverpod state, Firestore stream
- Pipeline → Middleware (down-right): pipeline scripts, checkpoint JSON
- Middleware → Backend (down): Firebase Admin SDK, Ollama API, ChromaDB

**Interaction:**
- Hover chip → dark tooltip (green border, monospace: name + status LED + detail text)
- Click board → camera lerps to close-up (~1s)
- Escape / "All boards" button → camera lerps to overview
- Iteration dropdown → chip states toggle per iteration history

**Three.js r128 constraints:** Same as v10.56. NO OrbitControls, NO CapsuleGeometry, NO TextGeometry. Chips = BoxGeometry, boards = PlaneGeometry + EdgesGeometry. Text = HTML overlay via Vector3.project(). Background 0x0D1117.

**CRITICAL: Inline data example:**
```javascript
const BOARDS = [
  {
    id: "frontend", label: "Frontend", color: 0x0D9488,
    pos: [-3, 3, 0], size: [5, 3],
    chips: [
      {id:"query_editor", status:"active", detail:"NoSQL parser"},
      {id:"results_table", status:"active", detail:"Paginated grid"},
      {id:"detail_panel", status:"active", detail:"Entity inspector"},
      {id:"map_tab", status:"active", detail:"OpenStreetMap markers"},
      {id:"globe_tab", status:"active", detail:"Continent cards"},
      {id:"iao_tab", status:"active", detail:"Trident + 10 pillars"},
      {id:"mw_tab", status:"active", detail:"33 components"},
      {id:"schema_tab", status:"active", detail:"22 t_any_* fields"},
      {id:"claw3d", status:"active", detail:"PCB architecture viz"},
      {id:"firebase_hosting", status:"active", detail:"CDN + SSL"}
    ]
  },
  {
    id: "pipeline", label: "Pipeline", color: 0xDA7E12,
    pos: [3, 3, 0], size: [5, 3],
    chips: [
      {id:"yt_dlp", status:"active", detail:"YouTube audio download"},
      {id:"faster_whisper", status:"active", detail:"CUDA transcription"},
      {id:"gemini_extract", status:"active", detail:"Entity extraction API"},
      {id:"normalize", status:"active", detail:"Schema v3 t_any_*"},
      {id:"geocode", status:"active", detail:"Nominatim 1 req/sec"},
      {id:"enrich", status:"active", detail:"Google Places API"},
      {id:"load", status:"active", detail:"Firebase Admin SDK"},
      {id:"tmux_runner", status:"active", detail:"Graduated GPU batches"},
      {id:"checkpoint", status:"active", detail:"JSON state persistence"}
    ]
  },
  {
    id: "middleware", label: "Middleware", color: 0x8B5CF6,
    pos: [0, -1.5, 0], size: [12, 6],
    chips: [
      {id:"evaluator", status:"active", detail:"Qwen fallback chain, G55 resolved"},
      {id:"harness", status:"active", detail:"601-line operating manual"},
      {id:"ADR", status:"active", detail:"10 architecture decisions"},
      {id:"artifact_gen", status:"active", detail:"4-doc loop"},
      {id:"gotcha_archive", status:"active", detail:"G1-G56, 18+ resolved"},
      {id:"agent_scores", status:"active", detail:"5-dim scoring, append-only"},
      {id:"pre_flight", status:"active", detail:"Environment validation"},
      {id:"post_flight", status:"active", detail:"14+ checks"},
      {id:"intent_router", status:"active", detail:"3-route Gemini Flash"},
      {id:"telegram_bot", status:"active", detail:"systemd, session memory"},
      {id:"rag_pipeline", status:"active", detail:"1,819 ChromaDB chunks"},
      {id:"qwen_9b", status:"active", detail:"Evaluator LLM, 256K ctx"},
      {id:"nemotron_4b", status:"active", detail:"Code review, 4K ctx"},
      {id:"gemini_flash", status:"active", detail:"Intent routing + extraction"},
      {id:"firebase_mcp", status:"active", detail:"G53 recurring reauth"},
      {id:"context7_mcp", status:"active", detail:"API docs lookup"},
      {id:"playwright_mcp", status:"active", detail:"Browser automation"},
      {id:"firecrawl_mcp", status:"active", detail:"Web scraping"},
      {id:"dart_mcp", status:"active", detail:"Flutter/Dart analysis"},
      {id:"claude_code", status:"active", detail:"Primary executor, Phases 6-7"},
      {id:"gemini_cli", status:"active", detail:"Primary executor, Phases 1-5"}
    ]
  },
  {
    id: "backend", label: "Backend", color: 0x3B82F6,
    pos: [0, -6.5, 0], size: [12, 3],
    chips: [
      {id:"firestore", status:"active", detail:"Single locations collection"},
      {id:"production_db", status:"active", detail:"6,181 entities"},
      {id:"staging_db", status:"active", detail:"188 Bourdain entities"},
      {id:"calgold", status:"active", detail:"899 entities", color:0xDA7E12},
      {id:"ricksteves", status:"active", detail:"4,182 entities", color:0x3B82F6},
      {id:"tripledb", status:"active", detail:"1,100 entities", color:0xDD3333},
      {id:"bourdain", status:"degraded", detail:"188 staging, Phase 2", color:0x8B5CF6}
    ]
  }
];
```

**Post-flight G56 check:**
```python
# In post_flight.py:
import re
content = open("app/web/claw3d.html").read()
fetches = re.findall(r'fetch\s*\([^)]*\.json', content)
assert len(fetches) == 0, f"FAIL: G56 - {len(fetches)} external JSON fetches found. Must be 0."
```

**Evidence:**
- Page loads at kylejeromethompson.com/claw3d.html (screenshot)
- `grep -c "fetch.*\.json" app/web/claw3d.html` returns 0
- 4 boards visible, MW visibly larger
- Hover + click-to-zoom functional
- Browser console: 0 errors

---

### W2: Bourdain Pipeline — Phase 3 (P1)

**Videos 61-90.** Machine: NZXTcos. **Staging only.**

```
yt-dlp --playlist-items 61-90 -x --audio-format mp3
faster-whisper (graduated tmux: 3 batches of 10, unload Ollama first)
Gemini Flash extraction
phase4_normalize.py --pipeline bourdain
phase5_geocode.py --pipeline bourdain
phase6_enrich.py --pipeline bourdain
phase7_load.py --pipeline bourdain --database staging
```

**Dedup against existing 188 entities.** Update `data/bourdain/checkpoint.json`.

---

### W3: ADR-010 (GCP Portability) + Harness Update (P1)

**Append to `docs/evaluator-harness.md`:**

1. **ADR-010: GCP Portability Design** — Pipeline and middleware are designed portable from local to GCP (tachnet-intranet). Two pipeline configs tracked: v1 (CalGold/RickSteves/TripleDB, established) and v2 (Bourdain, current). Focus on RickSteves as reference pipeline. Intranet will have different log sources (docs, spreadsheets, PDFs, meeting transcripts, Gmail, Slack, CRM) but same Thompson Indicator Fields normalization. Pub/sub topic router in intranet middleware enables Firestore to push to downstream consumers (tachtrack.com portals). Middleware scripts must not hardcode local paths.

2. **Pattern 16: External JSON fetch on Firebase Hosting (G56)** — Failure: `fetch('file.json')` returns 404 because Firebase Hosting only serves the build output directory. Prevention: all data must be inline JS objects. File existence checks in post-flight are insufficient.

3. **Evidence standards for Claw3D** — Must include `grep` for fetch+json (must be 0), screenshot of loaded page, browser console error count.

**Evidence:** `wc -l docs/evaluator-harness.md` > 601. ADR-010 present. G56 pattern present.

---

### W4: Post-Flight Hardening (P2)

Add G56 prevention check to `scripts/post_flight.py`:
- `grep` for `fetch` + `.json` in claw3d.html → must be 0
- If Playwright available: local serve + screenshot smoke test

---

## EXECUTION ORDER

1. **W1: Claw3D 4-Board** (P0, tsP3-cos) — 3 consecutive failures, fix G56 root cause
2. **W2: Bourdain Phase 3** (P1, NZXTcos) — parallel with W1
3. **W3: ADR-010 + Harness** (P1) — after W1/W2
4. **W4: Post-Flight** (P2) — after W3
5. Post-flight + living docs + report

---

## COMPLETION CHECKLIST

```
[ ] W1: claw3d.html loads at live URL — 4 boards visible, MW is largest
[ ] W1: grep -c "fetch.*\.json" app/web/claw3d.html returns 0
[ ] W1: Hover tooltips + click-to-zoom work
[ ] W1: 0 browser console errors
[ ] W2: Bourdain Phase 3 entities in staging
[ ] W2: checkpoint.json updated
[ ] W3: ADR-010 in evaluator-harness.md
[ ] W3: G56 pattern in failure catalog
[ ] W3: harness > 601 lines
[ ] W4: post_flight.py has G56 check
[ ] Report has non-empty scorecard
[ ] post_flight.py passes all checks
[ ] changelog updated
[ ] 4 artifacts: design, plan, build, report
```
