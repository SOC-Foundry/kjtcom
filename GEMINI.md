# GEMINI.md — kjtcom Agent Harness (Gemini CLI)

**Launch:** `gemini --yolo` then `Read GEMINI.md and execute 10.59`
**Repo:** SOC-Foundry/kjtcom
**Site:** kylejeromethompson.com
**Firebase:** kjtcom-c78cd (Blaze)
**Shell:** Gemini runs bash. Wrap fish commands with `fish -c "..."` (G19).

---

## RULES

1. **NEVER** `git commit`, `git push`, or any git write. All git = Kyle only.
2. **NEVER** heredocs. Use `printf` blocks only (G1).
3. **NEVER** `cat ~/.config/fish/config.fish` — Gemini has leaked API keys doing this.
4. **NEVER** simultaneous GPU processes. Graduated tmux batches, unload Ollama first (G18).
5. Gemini runs bash by default. Use `fish -c "..."` for fish-specific commands (G19).
6. Use `command ls` to avoid color code pollution (G22).
7. Read ENTIRE files before editing. `grep` for ALL related patterns.
8. Every iteration produces 4 artifacts: design, plan, build, report. No exceptions.
9. Post-flight (`python3 scripts/post_flight.py`) is MANDATORY before marking complete.
10. `10/10` scores prohibited. `agent_scores.json` is append-only. Harness never shrinks.
11. Changelog prefixes: `NEW:`, `UPDATED:`, `FIXED:`. No fluff words (successfully, robust, comprehensive).
12. **REPORTS MANDATORY.** Fallback: Qwen → Gemini Flash → self-eval. Empty scorecards = failure.
13. **G56: ALL Claw3D data INLINE as JS objects. NEVER fetch() external JSON.**
14. **G57: Qwen needs more context, not tighter rules. Feed rich context (50-80KB).**
15. Do NOT use `--start` flag on pipeline scripts. They use checkpoint resume.

---

## PROJECT STATE

| Pipeline | t_log_type | Color | Entities | Status |
|----------|-----------|-------|----------|--------|
| California's Gold | calgold | #DA7E12 | 899 | Production |
| Rick Steves' Europe | ricksteves | #3B82F6 | 4,182 | Production |
| Diners Drive-Ins and Dives | tripledb | #DD3333 | 1,100 | Production |
| Anthony Bourdain | bourdain | #8B5CF6 | 275 | **Staging (Phase 3, 90/114 videos)** |

**Total:** 6,181 production + 275 staging.

---

## AGENTS

| Agent | Role |
|-------|------|
| Gemini CLI | **Primary executor this iteration** — all 4 workstreams |
| Qwen3.5-9B | Evaluator (local Ollama) |
| Gemini Flash | Extraction API, evaluator fallback |

**Evaluator fallback:** Qwen (3) → Gemini Flash (2) → self-eval (cap 7/10)

---

## GOTCHAS

| ID | Title | Workaround |
|----|-------|------------|
| G1 | Heredocs | printf only |
| G18 | CUDA OOM RTX 2080 SUPER | Graduated tmux, unload Ollama first |
| G19 | Gemini runs bash | `fish -c "..."` for fish commands |
| G22 | ls color codes | `command ls` |
| G34 | Firestore array-contains | Client-side post-filter |
| G53 | Firebase MCP reauth | Retry wrapper |
| G56 | Claw3D fetch() 404 | Inline all data as JS objects. NEVER fetch .json |
| G57 | Qwen schema too strict | Expand context (50-80KB), not tighter rules |

**CRITICAL Gemini-specific:** NEVER run `cat ~/.config/fish/config.fish` — this has leaked API keys in past sessions.

---

## v10.59 WORKSTREAMS

### W1: Bourdain Pipeline — Phase 4 Final Batch (P1)

**Complete the 114-video playlist.** Videos 91-114 (24 remaining).

**Playlist:** `https://www.youtube.com/playlist?list=PLEVfhwFNb44fPn5N3OXk-aEHFvLOPzXKo`
**Machine:** NZXTcos (GPU required)

#### Step 1: Acquire
```bash
yt-dlp --playlist-items 91-114 \
  -x --audio-format mp3 \
  -o "data/bourdain/audio/%(playlist_index)03d_%(title)s.%(ext)s" \
  "https://www.youtube.com/playlist?list=PLEVfhwFNb44fPn5N3OXk-aEHFvLOPzXKo"
```

#### Step 2: Unload Ollama (G18 — free GPU memory)
```bash
curl -s http://localhost:11434/api/generate -d '{"model":"qwen3.5:9b","keep_alive":0}'
sleep 5
nvidia-smi  # Verify VRAM freed
```

#### Step 3: Transcribe (graduated tmux batches, SEQUENTIAL)
```bash
# Batch 1: videos 91-100
python3 -u scripts/phase2_transcribe.py --pipeline bourdain --start 91 --end 100 --timeout 600
# Wait for completion, verify output, then:

# Batch 2: videos 101-110
python3 -u scripts/phase2_transcribe.py --pipeline bourdain --start 101 --end 110 --timeout 600
# Wait, then:

# Batch 3: videos 111-114
python3 -u scripts/phase2_transcribe.py --pipeline bourdain --start 111 --end 114 --timeout 600
```

**DO NOT run batches simultaneously.** One at a time. Check for CUDA OOM between batches.

#### Step 4: Re-attempt video 089
Video 089 failed in Phase 3 (38K char compilation episode). If transcript exists:
```bash
wc -c pipeline/data/bourdain/transcripts/*089*
# If > 20000 chars, note as "compilation episode, skipped" in build log
# If < 20000, re-run extraction for just this video
```

#### Step 5: Extract → Normalize → Geocode → Enrich → Load
```bash
python3 -u scripts/phase3_extract.py --pipeline bourdain
python3 -u scripts/phase4_normalize.py --pipeline bourdain
python3 -u scripts/phase5_geocode.py --pipeline bourdain
python3 -u scripts/phase6_enrich.py --pipeline bourdain
python3 -u scripts/phase7_load.py --pipeline bourdain --database staging
```

**DO NOT load to production. Staging only.**

#### Step 6: Update checkpoint
```bash
python3 -c "
import json
cp = json.load(open('pipeline/data/bourdain/checkpoint.json'))
cp['phase'] = 4
cp['videos_acquired'] = 114
# Fill in actual counts after each step
json.dump(cp, open('pipeline/data/bourdain/checkpoint.json','w'), indent=2)
"
```

**Evidence:** Entity count increase, checkpoint `phase4_complete`, total countries, extraction failures.

---

### W2: Claw3D Chip Text Fix (P1)

**Problem:** Chip labels overflow boxes. Text scrunched and overlapping.

**Fix: Shorten labels + widen chips.**

#### Step 1: Edit chip labels in `app/web/claw3d.html`

Find the inline `BOARDS` array. Replace long chip IDs with shortened versions:

| Board | Old ID | New ID |
|-------|--------|--------|
| Frontend | query_editor | query_ed |
| Frontend | results_table | results |
| Frontend | detail_panel | detail |
| Frontend | map_tab | map |
| Frontend | globe_tab | globe |
| Frontend | iao_tab | iao |
| Frontend | schema_tab | schema |
| Frontend | firebase_hosting | fb_host |
| Pipeline | faster_whisper | whisper |
| Pipeline | gemini_extract | extract |
| Pipeline | tmux_runner | tmux |
| Middleware | artifact_gen | artifact |
| Middleware | gotcha_archive | gotchas |
| Middleware | agent_scores | scores |
| Middleware | intent_router | router |
| Middleware | telegram_bot | tg_bot |
| Middleware | rag_pipeline | rag |
| Middleware | iao_logger | logger |
| Middleware | firebase_mcp | fb_mcp |
| Middleware | context7_mcp | c7_mcp |
| Middleware | playwright_mcp | pw_mcp |
| Middleware | firecrawl_mcp | fc_mcp |
| Middleware | dart_mcp | dart_mcp |
| Middleware | claude_code | claude |
| Middleware | gemini_cli | gemini |
| Middleware | gemini_flash | gflash |
| Middleware | nemotron_4b | nemotron |
| Backend | production_db | prod_db |
| Backend | staging_db | stg_db |

**Keep the full name in the `detail` field** — it shows in the hover tooltip.

#### Step 2: Widen chips

Find the `BoxGeometry` creation for chips. Change width:
```javascript
// Find this line (approximately):
new THREE.BoxGeometry(1.0, 0.1, 0.6)
// Change to:
new THREE.BoxGeometry(1.2, 0.1, 0.6)
```

Also adjust the grid spacing if chips are placed on a grid — increase the column gap to match the wider chips.

#### Step 3: Update version
Change the title/version string to v10.59.

#### Step 4: G56 check + deploy
```bash
grep -c "fetch.*\.json" app/web/claw3d.html
# Must return 0

fish -c "cd app && flutter build web"
fish -c "firebase deploy --only hosting"
```

#### Step 5: Verify
Open `https://kylejeromethompson.com/claw3d.html` — all labels readable, no overlap, tooltips show full names.

---

### W3: Qwen Context Expansion (P1)

**Qwen needs more data, not more rules (G57).**

#### Step 1: Add `build_rich_context()` to `scripts/run_evaluator.py`

```python
def build_rich_context(iteration):
    """Build 50-80KB context package for Qwen evaluation."""
    import os
    parts = []
    
    # Current iteration artifacts
    for doc_type in ["build", "design"]:
        path = f"docs/kjtcom-{doc_type}-{iteration}.md"
        if os.path.exists(path):
            parts.append(f"=== CURRENT {doc_type.upper()} ({iteration}) ===")
            parts.append(open(path).read())
    
    # Few-shot: 2-3 example reports that have complete scorecards
    for ver in ["v10.56", "v10.58"]:
        for loc in [f"docs/kjtcom-report-{ver}.md", f"docs/archive/kjtcom-report-{ver}.md"]:
            if os.path.exists(loc):
                parts.append(f"=== EXAMPLE REPORT ({ver}) — match this format ===")
                parts.append(open(loc).read())
                break
    
    # Middleware registry
    if os.path.exists("data/middleware_registry.json"):
        parts.append("=== MIDDLEWARE REGISTRY ===")
        parts.append(open("data/middleware_registry.json").read())
    
    # Gotcha archive
    if os.path.exists("data/gotcha_archive.json"):
        parts.append("=== GOTCHA ARCHIVE ===")
        parts.append(open("data/gotcha_archive.json").read())
    
    # ADRs from harness
    if os.path.exists("docs/evaluator-harness.md"):
        harness = open("docs/evaluator-harness.md").read()
        adr_start = harness.find("## 3.")
        adr_end = harness.find("## 4.")
        if adr_start > 0 and adr_end > 0:
            parts.append("=== ARCHITECTURE DECISIONS ===")
            parts.append(harness[adr_start:adr_end])
    
    # Recent changelog (first 5 entries)
    if os.path.exists("docs/kjtcom-changelog.md"):
        cl = open("docs/kjtcom-changelog.md").read()
        entries = cl.split("\n## ")[:6]
        parts.append("=== RECENT CHANGELOG ===")
        parts.append("\n## ".join(entries))
    
    ctx = "\n\n".join(parts)
    print(f"[EVAL] Rich context: {len(ctx):,} chars (~{len(ctx)//4:,} tokens)")
    return ctx
```

#### Step 2: Update the evaluator prompt

Replace the current prompt builder to use rich context and emphasize example matching:

```python
def build_eval_prompt(rich_context, iteration):
    return f"""You are Qwen, the evaluator for kjtcom.

IMPORTANT: Study the EXAMPLE REPORTS above. Your output must match their exact markdown format:
- Summary paragraph (2-4 sentences)
- Workstream Scores table (| # | Workstream | Priority | Outcome | Score | Evidence |)
- Trident section
- What Could Be Better section (2-5 items)

Use the build log and design doc to score each workstream 1-9 out of 10.
Use the middleware registry, gotcha archive, and ADRs for context about the project.

{rich_context}

Produce the evaluation report for iteration {iteration} now. Output ONLY the markdown report, no preamble."""
```

#### Step 3: Wire it up

In the main evaluation flow, replace the old context builder:
```python
# OLD: context = build_execution_context(iteration)
# NEW:
context = build_rich_context(iteration)
prompt = build_eval_prompt(context, iteration)
```

#### Step 4: Test
```bash
# Reload Qwen (was unloaded for GPU in W1)
curl -s http://localhost:11434/api/chat -d '{"model":"qwen3.5:9b","messages":[{"role":"user","content":"ping"}],"stream":false}' | python3 -c "import sys,json; print(json.load(sys.stdin)['message']['content'])"

# Run evaluator with verbose
python3 -u scripts/run_evaluator.py --iteration v10.58 --verbose 2>&1 | tee /tmp/eval_test.log

# Check context size (target 50-80KB)
grep "Rich context" /tmp/eval_test.log

# Check which tier succeeded
grep "EVAL" /tmp/eval_test.log
```

---

### W4: README Overhaul (P1)

**Significant rewrite. The README has been stale for multiple iterations.**

#### Read current state first
```bash
wc -l README.md
head -20 README.md
```

#### Required updates

1. **Header:** Phase 10 v10.59 (ACTIVE). Status: Bourdain Pipeline Complete + PCB Architecture + Middleware Hardening

2. **Pipeline table:** 4 rows. Add Bourdain with #8B5CF6, entity count from checkpoint, "Phase 4 (staging)".

3. **Architecture section:**
   - Replace ALL solar system / "3D IAO Visualization" references with PCB
   - Link: `[Interactive PCB Architecture](https://kylejeromethompson.com/claw3d.html)`
   - Describe 4-board layout: Frontend (Firebase Hosting, Flutter Web), Pipeline (local GPU extraction), Middleware (orchestration hub — agents, LLMs, MCPs, harness, ADRs), Backend (Firestore, log sources)
   - Current state line: v10.59, 4 pipelines, 727-line harness, 11 ADRs, 22+ middleware chips

4. **Middleware section (expand significantly):**
   - Evaluator: 727-line harness, 3-tier fallback, 16 failure patterns, 11 ADRs
   - List ADR-001 through ADR-011 (one line each)
   - Components: intent router, RAG (1,819 chunks), Telegram bot, artifact automation, pre/post-flight
   - Agents: Claude Code, Gemini CLI, Qwen3.5-9B, Nemotron, GLM
   - MCPs: Firebase, Context7, Playwright, Firecrawl, Dart
   - Evaluator fallback chain description

5. **Thompson Indicator Fields:** v3 (22 fields) + v4 preview note referencing ADR-011

6. **10 Pillars:** Verbatim from current README. Include Mermaid trident chart.

7. **Changelog:** Include v10.54 through v10.59

8. **GCP Portability:** Brief mention of ADR-010, intranet vision

#### Deploy README
```bash
# README.md is in repo root, gets deployed with flutter build web
# But also rendered on GitHub — verify markdown renders correctly
wc -l README.md  # Target 750+
```

---

## EXECUTION ORDER

1. **W1: Bourdain Phase 4** — start first, longest (2-3 hours GPU work)
2. **W2: Claw3D chip text** — after W1 acquire step while transcription runs in tmux
3. **W3: Qwen context expansion** — after W1 transcription completes (need Ollama back)
4. **W4: README overhaul** — after W1/W2 so counts are final
5. Post-flight + living docs + report

---

## POST-FLIGHT + REPORT

```bash
# Post-flight
python3 scripts/post_flight.py

# Archive v10.58
mkdir -p docs/archive
cp docs/kjtcom-build-v10.58.md docs/archive/
cp docs/kjtcom-report-v10.58.md docs/archive/
cp docs/kjtcom-design-v10.58.md docs/archive/ 2>/dev/null
cp docs/kjtcom-plan-v10.58.md docs/archive/ 2>/dev/null

# Update changelog
# (append v10.59 entry to docs/kjtcom-changelog.md)

# Run evaluator WITH RICH CONTEXT
python3 -u scripts/run_evaluator.py --iteration v10.59 --verbose

# Verify report exists and has scores
grep -c "^| W" docs/kjtcom-report-v10.59.md
# Must be >= 1. If 0, produce report manually (self-eval fallback tier 3).
```

---

## COMPLETION CHECKLIST

```
[ ] W1: Bourdain Phase 4 complete (videos 91-114)
[ ] W1: Total Bourdain entity count documented
[ ] W1: checkpoint.json phase4_complete
[ ] W2: Chip labels readable at default zoom, no overlap
[ ] W2: Wider chips (1.2), shorter labels, tooltips show full names
[ ] W2: G56=0, 0 console errors
[ ] W3: build_rich_context() in run_evaluator.py
[ ] W3: Context size 50-80KB reported in verbose output
[ ] W4: README overhauled (750+ lines)
[ ] W4: 4 pipelines, PCB architecture, middleware section
[ ] W4: Mermaid trident chart present
[ ] Report has scored workstreams (>= 1 row)
[ ] Post-flight passes all checks
[ ] Changelog updated
[ ] 4 artifacts: design, plan, build, report
[ ] No git operations performed (Rule 1)
```

---

*GEMINI.md v10.59, April 06, 2026. Primary executor: Gemini CLI. 4 workstreams. Bourdain final batch + Claw3D text + Qwen context + README overhaul.*
