# CLAUDE.md — kjtcom Agent Harness (Claude Code)

**Launch:** `read claude and execute 10.61`
**Repo:** SOC-Foundry/kjtcom
**Site:** kylejeromethompson.com
**Firebase:** kjtcom-c78cd (Blaze)
**Shell:** fish + tmux on NZXTcos and tsP3-cos

---

## RULES

1. **NEVER** `git commit`, `git push`. All git = Kyle only.
2. **NEVER** heredocs. `printf` only (G1). `command ls` (G22). `fish -c` wrappers (G19).
3. **NEVER** simultaneous GPU. Graduated tmux, unload Ollama first (G18).
4. Read ENTIRE files before editing. `grep` all related patterns.
5. 4 artifacts per iteration. Post-flight MANDATORY. `10/10` prohibited. Harness never shrinks.
6. **REPORTS MANDATORY.** Fallback: Qwen → Gemini → self-eval. No empty scorecards.
7. **G56: ALL Claw3D data INLINE. NEVER fetch() external JSON.**
8. **G58: Design/plan docs are IMMUTABLE during execution. generate_artifacts.py skips them.**
9. **G59: HARD CHIP CONTAINMENT.** Every chip label MUST render inside its chip box. Every chip MUST render inside its board boundary. The chip render function must MEASURE text width and CLAMP to chip width. If text overflows after 4 iterations of patches, the implementation approach is wrong — use a fundamentally different text rendering strategy. See W3.
10. **Component review every iteration.** Before finalizing Claw3D data, audit all middleware/pipeline/frontend/backend components against the actual codebase. No additions missed.

---

## PROJECT STATE

| Pipeline | t_log_type | Color | Entities | Shows | Status |
|----------|-----------|-------|----------|-------|--------|
| California's Gold | calgold | #DA7E12 | 899 | California's Gold | Production |
| Rick Steves' Europe | ricksteves | #3B82F6 | 4,182 | Rick Steves' Europe | Production |
| Diners Drive-Ins and Dives | tripledb | #DD3333 | 1,100 | Diners Drive-Ins and Dives | Production |
| Anthony Bourdain | bourdain | #8B5CF6 | 351 | No Reservations | Staging (114/114) |
| Anthony Bourdain | bourdain | #8B5CF6 | 0 | **Parts Unknown** | **Phase 1 starting** |

**Total:** 6,181 production + 351 staging. Bourdain is a single pipeline with `t_any_shows` differentiating series.

**Parts Unknown playlist:** `https://www.youtube.com/watch?v=6PQB1S5sZQ0&list=PLfLND2Lym9knKTVU7lHYROAGWmTH2kEFo`

---

## AGENTS

| Agent | Role |
|-------|------|
| Claude Code | Executor: app, middleware, docs (Phases 6-7) |
| Gemini CLI | Executor: pipeline (Phases 1-5) |
| Qwen3.5-9B | Evaluator (local Ollama) |
| Gemini Flash | Intent routing, extraction, evaluator fallback |
| OpenClaw | Local sandbox agent (middleware component, Phase 10+) |

---

## GOTCHAS

| ID | Title | Status |
|----|-------|--------|
| G1 | Heredocs | Active |
| G18 | CUDA OOM | Active |
| G53 | Firebase MCP reauth | Recurring |
| G56 | Claw3D fetch() 404 | Resolved v10.57 |
| G58 | Agent overwrites design/plan | Resolved v10.60 |
| **G59** | **Claw3D chip text overflow — 4 failed attempts** | **Resolved v10.61 (canvas texture)** |

---

## v10.61 WORKSTREAMS

### W1: Parts Unknown Pipeline — Phase 1 Discovery (P1)

**GEMINI CLI executes this workstream.**

Start the second Bourdain show under the existing `bourdain` pipeline. `t_any_shows` differentiates: existing entities have `["No Reservations"]`, new entities get `["Parts Unknown"]`.

**Playlist:** `https://www.youtube.com/watch?v=6PQB1S5sZQ0&list=PLfLND2Lym9knKTVU7lHYROAGWmTH2kEFo`

First, determine playlist size:
```bash
yt-dlp --flat-playlist --print "%(playlist_index)s %(title)s" \
  "https://www.youtube.com/watch?v=6PQB1S5sZQ0&list=PLfLND2Lym9knKTVU7lHYROAGWmTH2kEFo" | wc -l
```

**Phase 1 batch:** First 30 videos (or all if playlist is smaller).

```bash
yt-dlp --playlist-items 1-30 -x --audio-format mp3 \
  -o "pipeline/data/bourdain/audio/pu_%(playlist_index)03d_%(title)s.%(ext)s" \
  "https://www.youtube.com/watch?v=6PQB1S5sZQ0&list=PLfLND2Lym9knKTVU7lHYROAGWmTH2kEFo"
```

**Note the `pu_` prefix** on filenames to distinguish from No Reservations files.

Pipeline steps: acquire → transcribe (graduated tmux, G18) → extract (Gemini Flash) → normalize → geocode → enrich → load staging.

**Extraction prompt update:** The `pipeline/config/bourdain/extraction_prompt.md` must set `t_any_shows: ["Parts Unknown"]` for all entities from this playlist. The existing No Reservations entities already have `t_any_shows: ["No Reservations"]`.

**Dedup:** Parts Unknown may visit the same locations as No Reservations. Dedup merges `t_any_shows` arrays: an entity visited in both shows gets `["No Reservations", "Parts Unknown"]`.

**DO NOT load to production. Staging only.**

**Evidence:** Entity count, `t_any_shows` correctly populated, checkpoint updated.

---

### W2: GCP Portability Planning — ADR-013 (P1)

**This is a planning workstream. No infrastructure built yet.**

Produce `docs/gcp-portability-plan.md` covering:

**1. Registry artifacts to scrub and transfer:**
| Artifact | Location | Scrub needed | Transfer method |
|----------|----------|-------------|-----------------|
| evaluator-harness.md | docs/ | Remove kjtcom-specific entity counts, keep ADRs/patterns/methodology | Copy, parameterize counts |
| middleware_registry.json | data/ | Replace kjtcom component IDs with generic template IDs | Export → parameterize |
| gotcha_archive.json | data/ | Keep universal gotchas (G1,G18,G19,G22), remove kjtcom-specific | Filter by `universal` tag |
| agent_scores.json | root | Do NOT transfer — this is kjtcom's history | Leave behind |
| claw3d_components.json | data/ | Rebuild for intranet board layout | New file |
| eval_schema.json | data/ | Transfer as-is — schema validation is universal | Copy |
| CLAUDE.md / GEMINI.md | root | Template the workstream section, keep rules | Parameterize |
| Pipeline configs | pipeline/config/ | New configs per intranet source type | New files |
| Pipeline scripts | pipeline/scripts/ | phases 1-7 are universal, extraction prompts are source-specific | Copy scripts, new prompts |

**2. GCP resource build order:**
```
Phase A: VPC + IAM (tachnet-intranet project)
  - VPC with private subnet for Ollama/GPU instances
  - IAM roles: pipeline-executor, evaluator, deployer
  - Service accounts for each role

Phase B: Compute
  - GPU instance for transcription (equivalent to NZXTcos RTX 2080)
  - CPU instance for middleware (evaluator, RAG, bot)
  - Cloud Run for pipeline scripts (serverless batch)

Phase C: Storage + Database
  - Firestore (intranet-specific project)
  - Cloud Storage for audio/transcripts/checkpoints
  - ChromaDB on CPU instance (or Vertex AI Vector Search)

Phase D: Middleware deployment
  - Ollama on GPU instance (Qwen, Nemotron)
  - Evaluator harness + fallback chain
  - Telegram bot as Cloud Run service
  - Pub/sub topic router for downstream consumers

Phase E: Pipeline configs
  - Per-source extraction prompts (Gmail, Slack, CRM, docs, etc.)
  - Thompson Schema v4 fields (ADR-011) activated per source
  - Firestore triggers → pub/sub → tachtrack.com portals
```

**3. Harness readiness checklist before intranet buildout:**
```
[ ] Evaluator produces scored reports without human intervention (G55/G57 fully resolved)
[ ] generate_artifacts.py respects immutability (G58 resolved ✓)
[ ] All gotchas tagged universal vs kjtcom-specific
[ ] Pipeline scripts parameterized (no hardcoded paths, env vars for all config)
[ ] Extraction prompt template documented (how to write one for a new source type)
[ ] Post-flight checks parameterized (site URL, bot handle, MCP list as config)
[ ] ADR registry portable (ADR-001 through ADR-013 apply to any IAO project)
[ ] Thompson Schema v4 fields defined (ADR-011 ✓)
[ ] Pub/sub topic router designed (ADR for intranet, not yet written)
[ ] Claw3D PCB template exportable (board definitions as config, not hardcoded)
```

**4. Pipeline analysis — ADR addendum:**
Compare the two pipeline configurations:
- **v1 (CalGold/RickSteves/TripleDB):** 3 separate pipeline runs, each with its own extraction prompt. CalGold was first (many hiccups). RickSteves was cleanest (reference). TripleDB was imported (different source format).
- **v2 (Bourdain — No Reservations + Parts Unknown):** Single pipeline, two shows differentiated by `t_any_shows`. Same extraction prompt with show-specific override. This is the model for intranet (single pipeline infrastructure, multiple source configs).

**Recommendation:** Use v2 (Bourdain) as the template for intranet. Single pipeline codebase, source-specific extraction prompts, `t_any_sources` field for differentiation (analogous to `t_any_shows`). Focus on RickSteves pipeline execution as the operational reference (cleanest run history).

**Evidence:** `docs/gcp-portability-plan.md` exists with all 4 sections.

---

### W3: Claw3D — Hard Chip Containment (P0)

**This has failed in v10.57, v10.58, v10.59, and v10.60.** Incremental label shortening and chip widening is not working. The fundamental problem is that HTML overlay text positioned via `Vector3.project()` doesn't respect Three.js geometry boundaries — the text just floats wherever the projected coordinate lands, with no relationship to the chip box size.

**G59: Change the rendering approach entirely.**

**Option A (recommended): Render labels as canvas textures ON the chip geometry.**
Instead of HTML overlays, draw text onto a `CanvasTexture` and apply it as the chip face material. The text is literally painted onto the chip surface — it physically cannot overflow because the texture IS the chip.

```javascript
function createChipTexture(label, status, width, height) {
    const canvas = document.createElement('canvas');
    canvas.width = width * 64;  // resolution
    canvas.height = height * 64;
    const ctx = canvas.getContext('2d');
    
    // Chip background
    ctx.fillStyle = '#1F2937';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Border
    ctx.strokeStyle = status === 'active' ? '#4ADE80' : 
                      status === 'degraded' ? '#EF9F27' : '#666';
    ctx.lineWidth = 2;
    ctx.strokeRect(1, 1, canvas.width-2, canvas.height-2);
    
    // Label — auto-size to fit
    ctx.fillStyle = '#C9D1D9';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    let fontSize = 14;
    ctx.font = `${fontSize}px monospace`;
    while (ctx.measureText(label).width > canvas.width - 8 && fontSize > 6) {
        fontSize--;
        ctx.font = `${fontSize}px monospace`;
    }
    ctx.fillText(label, canvas.width/2, canvas.height/2);
    
    // LED dot
    ctx.beginPath();
    ctx.arc(canvas.width - 8, 8, 4, 0, Math.PI * 2);
    ctx.fillStyle = status === 'active' ? '#4ADE80' : 
                    status === 'degraded' ? '#EF9F27' : '#666';
    ctx.fill();
    
    return new THREE.CanvasTexture(canvas);
}
```

The key: `ctx.measureText(label).width` is used to AUTO-SHRINK the font until it fits. Text physically cannot overflow because it's measured against the canvas dimensions before rendering.

**Board containment:** Chip positions are computed from the board dimensions with padding. Same grid layout as before, but now guaranteed because the chip geometries have fixed sizes and the grid math ensures they fit within the board PlaneGeometry.

**Board titles:** Also render as canvas textures or as a single HTML overlay positioned at the top of each board (verified to be within board bounds).

**Keep hover tooltips as HTML overlays** — those SHOULD float above the chip (they're temporary popups). Only the permanent chip labels move to canvas textures.

**Component review pass (Rule 10):**

Current middleware components — verify against codebase:
| Component | File/Location | Status | On board? |
|-----------|--------------|--------|-----------|
| evaluator | scripts/run_evaluator.py | Active | Yes |
| harness | docs/evaluator-harness.md | Active (761 lines) | Yes |
| ADR registry | docs/evaluator-harness.md §3 | Active (12 ADRs) | Yes |
| artifact_gen | scripts/generate_artifacts.py | Active (G58 fixed) | Yes |
| gotcha_archive | data/gotcha_archive.json | Active (G1-G59) | Yes |
| agent_scores | agent_scores.json | Active | Yes |
| pre_flight | (manual checklist) | Active | Yes |
| post_flight | scripts/post_flight.py | Active (15 checks) | Yes |
| intent_router | scripts/intent_router.py | Active (3-route) | Yes |
| telegram_bot | scripts/telegram_bot.py | Active (systemd) | Yes |
| rag_pipeline | scripts/embed_archive.py | Active (1,819 chunks) | Yes |
| iao_logger | scripts/iao_logger.py | Active (JSONL) | Yes |
| qwen_9b | Ollama local | Active | Yes |
| nemotron_4b | Ollama local | Active | Yes |
| gemini_flash | API | Active | Yes |
| firebase_mcp | MCP server | Active | Yes |
| context7_mcp | MCP server | Active | Yes |
| playwright_mcp | MCP server | Active | Yes |
| firecrawl_mcp | MCP server | Active | Yes |
| dart_mcp | MCP server | Active | Yes |
| claude_code | Agent | Active | Yes |
| gemini_cli | Agent | Active | Yes |
| **openclaw** | **open-interpreter** | **NEW — add to board** | **No → add** |

**Add OpenClaw to middleware board** as a chip: `{id:"openclaw", status:"active", detail:"Local sandbox agent"}`. It was installed in v9.39 and is a middleware component for sandboxed agent execution.

**Evidence:**
- All labels render inside chip boxes (canvas texture guarantees this)
- All chips inside board boundaries (grid math + padding)
- Board titles inside boards
- OpenClaw chip on middleware board
- Hover tooltips still work (HTML overlay for tooltips only)
- 0 console errors, G56=0

---

### W4: Harness + ADR Updates (P2)

**Append to `docs/evaluator-harness.md`:**

1. **ADR-013: Pipeline Configuration Portability**
   - Two configs tracked: v1 (CalGold/RickSteves/TripleDB) and v2 (Bourdain multi-show)
   - v2 is the template for intranet (single pipeline, multiple source configs)
   - RickSteves is the operational reference (cleanest execution history)
   - Parts Unknown validates multi-show within single pipeline (t_any_shows differentiation)

2. **Pattern 18: Chip text overflow despite repeated fixes (G59)**
   - HTML overlay text has no relationship to Three.js geometry boundaries
   - Fix: canvas texture rendering with auto-measured font sizing
   - Prevention: never use HTML overlays for permanent labels on geometry

3. **Component review checklist** — new section requiring a pass every iteration to verify all middleware components are represented on the PCB board.

**Evidence:** ADR-013, Pattern 18, component review section. `wc -l` > 761.

---

## EXECUTION ORDER

1. **W3: Claw3D hard containment** (P0, tsP3-cos) — canvas texture approach
2. **W1: Parts Unknown Phase 1** (P1, Gemini CLI on NZXTcos) — parallel with W3
3. **W2: GCP portability plan** (P1) — after W1 so pipeline analysis includes Parts Unknown
4. **W4: Harness updates** (P2) — after W2/W3
5. Post-flight + living docs + report

---

## COMPLETION CHECKLIST

```
[ ] W1: Parts Unknown Phase 1 entities in staging
[ ] W1: t_any_shows correctly set to ["Parts Unknown"]
[ ] W1: Checkpoint updated for Parts Unknown
[ ] W2: docs/gcp-portability-plan.md exists (4 sections)
[ ] W2: Pipeline analysis compares v1 vs v2
[ ] W3: All chip labels render inside chip boxes (canvas texture)
[ ] W3: All chips inside board boundaries
[ ] W3: OpenClaw chip on middleware board
[ ] W3: Component review pass complete (23+ components verified)
[ ] W3: 0 console errors, G56=0
[ ] W4: ADR-013 in harness
[ ] W4: Pattern 18 (G59) in failure catalog
[ ] W4: Component review checklist section added
[ ] W4: Harness > 761 lines
[ ] Report scored, post-flight passes, changelog, 4 artifacts
```
