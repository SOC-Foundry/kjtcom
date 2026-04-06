# kjtcom - Gemini CLI Agent Instructions

## Current Iteration: v9.48

IMPORTANT: Read documents in this EXACT order before executing:

1. This file (GEMINI.md)
2. docs/kjtcom-design-v9.48.md - Workstreams, architecture, amendments
3. docs/kjtcom-plan-v9.48.md - Step-by-step execution
4. docs/evaluator-harness.md - Qwen's evaluation personality

Do NOT begin execution until files 1-3 have been read.

---

## Your Role

Gemini CLI is the pipeline executor for Phases 1-5 (Acquire, Transcribe, Extract, Normalize, Geocode) and supports Claude Code on infrastructure iterations when directed. Gemini Flash API serves as the intent routing engine for the Telegram bot /ask command (3 routes: firestore, chromadb, web) and as the synthesis engine for bot responses. In v9.47, Gemini CLI was the primary executor - it may lead future iterations as well.

---

## Agent Session Best Practices (v9.42+ - PERMANENT)

### Pre-Launch Checklist
1. GEMINI.md MUST be saved to disk in the launch directory BEFORE starting.
2. Verify harness line count: `wc -l GEMINI.md` - must be >= 200 lines. Harnesses grow, never shrink. (v9.48+)
3. /quit every session and start fresh between iterations. ONE iteration per session.
4. `set -gx IAO_ITERATION v9.XX` BEFORE launching.
5. Verify Ollama running: `ollama list` should show 4 models.
6. Restart bot: `sudo systemctl restart kjtcom-telegram-bot`
7. Verify Firebase SA: `test -f ~/.config/gcloud/kjtcom-sa.json`.
8. Verify archive integrity: `ls docs/archive/ | wc -l` (>= prior count).
9. Clean drafts: `rm -f docs/drafts/*.md` (ephemeral directory).
10. Clean orphaned changelogs: verify no docs/changelog-v*.md files exist.

### Session Discipline
- If session crashes, /quit and relaunch. Do not recover mid-session.
- Every session ends with: artifact production -> post-flight verification -> draft promotion.
- Drafts cross-checked and promoted. NEVER leave unpromoted drafts.
- Harness files GROW. Never abbreviate. Never trim. The depth is the competitive advantage.

---

## File Management Rules (v9.48+ - ABSOLUTE)

### docs/ holds ONLY:
- Current iteration artifacts (design, plan, build, report)
- Living docs: kjtcom-changelog.md, kjtcom-architecture.mmd, install.fish, evaluator-harness.md, pipeline-review-v9.47.md

### docs/archive/ holds:
- ALL prior iteration artifacts (one copy only, no duplicates)

### docs/drafts/ is EPHEMERAL:
- Wiped at start of each iteration. Empty after promotion.

### Single Changelog:
- ONE file: docs/kjtcom-changelog.md. Append to top, never create changelog-v{X}.md.

### Document Archival:
- **NEVER run rm or git rm on ANY docs/kjtcom-*.md file.**
- **NEVER delete docs. Archive to docs/archive/.**
- Kyle moves current docs to archive after git push.

---

## Post-Flight Verification (v9.43+ - MANDATORY)

After every iteration, BEFORE session ends:
1. `python3 scripts/post_flight.py` - all checks pass
2. Site HTTP 200 from kylejeromethompson.com
3. Bot /status responds via Telegram
4. Bot /ask returns >= 6,181 entities
5. architecture.html loads (HTTP 200)
6. claw3d.html loads (HTTP 200)
7. Log results in POST-FLIGHT section of build log
8. If ANY fails: fix, re-deploy, re-verify. Do NOT end session with failures.

---

## Qwen Evaluator (v9.46+ - MANDATORY)

### Harness
docs/evaluator-harness.md loaded as system prompt. Skeptical, fact-based, evidence-required.

### Core Rules
- Never 10/10. Max 9/10.
- Evidence for every score. 2 improvements per workstream.
- No corporate fluff. Banned phrases enforced.
- Trident: actual values. "Review..." and "TBD" banned.
- "What Could Be Better" section mandatory with >= 3 items.

### Structural Enforcement (v9.48+)
- run_evaluator.py PARSES design doc for W# count
- Validates Qwen output: scorecard rows == design doc workstreams
- Re-prompts on mismatch (max 2 retries)
- No hallucinated workstreams. If design doc has 4, scorecard has 4. Period.

### Workstream Fidelity (v9.47+)
- EXACT W# list from design doc. No adding, renaming, reordering.

---

## Rules That Never Change

- Git READ commands ALLOWED (pull, log, status, diff, show)
- Git WRITE commands FORBIDDEN (add, commit, push, checkout, branch, tag)
- firebase deploy FORBIDDEN - Kyle deploys manually
- flutter build web and flutter run ARE ALLOWED for testing
- NEVER ask permission. The plan IS the permission.
- Self-heal errors: diagnose -> fix -> re-run (max 3 attempts, then gotcha)
- Fish shell throughout. pip --break-system-packages. python3 -u.
- No em-dashes. " - " for dashes. "->" for arrows.
- "pipelines" and "log types," never "tables" or "datasets."
- Build on existing code. Read files before overwriting.
- NEVER delete docs. Archive to docs/archive/.

---

## Token Efficiency (v9.40+)

- ALL Ollama calls use scripts/utils/ollama_config.py (think:false mandatory, G51)
- num_predict: 512 default, 2048 evaluations, 2048 batch (45-min timeout)
- Gemini Flash: use GEMINI_MODEL from ollama_config.py (v9.44+)
- Log all calls via iao_logger.py

---

## Dependency Upgrade Protocol (v9.45+)

- ONE major version at a time. Minor versions can batch.
- Read changelog first (Context7 MCP). analyze -> test -> build after each.
- v9.45 finding: 10 transitive deps locked by upstream. Not actionable.

---

## README Refresh Cadence (v9.46+)

- Every iteration: update changelog section, version/phase number
- Every 3 iterations: full review and overhaul

---

## Multi-Agent Orchestration (v9.35+)

Minimum 2 LLMs per iteration. Document per workstream.

| Agent | Engine | Use For |
|-------|--------|---------|
| Claude Code | Claude API | Primary executor (when leading) |
| Gemini CLI | Gemini API | Pipeline executor, may lead iterations |
| Qwen3.5-9B | Ollama local | Evaluation, scoring |
| Nemotron Mini 4B | Ollama local | Fast triage |
| GLM-4.6V-Flash | Ollama local | Vision |
| nomic-embed-text | Ollama local | Embeddings only |
| Gemini Flash | Gemini API (litellm) | Intent routing, synthesis |

---

## MCP Servers (5 total - ONLY valid names)

| Server | Use For |
|--------|---------|
| Firebase MCP | Firestore queries |
| Context7 MCP | API documentation |
| Firecrawl MCP | Web scraping |
| Playwright MCP | Browser automation (G47) |
| Dart MCP | Code analysis |

No other MCP server names exist. Available in .gemini/settings.json: Firebase, Context7.

---

## Middleware as Primary IP (v9.42+)

Middleware is the product. kjtcom is the lab. Every iteration adds to middleware.

Components:
- **Harnesses:** CLAUDE.md, GEMINI.md (200+ lines, grow never shrink), evaluator-harness.md
- **Harness Registry:** data/middleware_registry.json
- **Evaluator:** run_evaluator.py (structural enforcement v9.48+), agent_scores.json
- **RAG:** embed_archive.py, query_rag.py, ChromaDB (~1,690 chunks)
- **Intent Router:** intent_router.py (3 routes: firestore/chromadb/web)
- **Firestore Query:** firestore_query.py (G34 workaround, Python sort)
- **County Enrichment:** enrich_counties.py
- **Event Logging:** iao_logger.py, iao_event_log.jsonl, analyze_events.py
- **Artifact Generator:** generate_artifacts.py (single changelog, --promote, --validate-only)
- **Gotcha Archive:** data/gotcha_archive.json (18+ resolved)
- **Bot:** telegram_bot.py (systemd, session memory, rating sort, 3-route)
- **Config:** ollama_config.py (defaults, batch, GEMINI_MODEL)
- **Post-Flight:** post_flight.py
- **Cleanup:** cleanup_docs.py (v9.48+)
- **Architecture:** build_architecture_html.py, app/web/architecture.html
- **Claw3D:** app/web/claw3d.html
- **Pipeline Review:** docs/pipeline-review-v9.47.md

---

## Artifact Discipline (v9.42+)

Every iteration: design, plan, build (POST-FLIGHT section), report (Evidence column, exact W# count, What Could Be Better), CLAUDE.md, GEMINI.md (both >= 200 lines), changelog APPENDED to single file.

Workflow: generate -> evaluate (structural enforcement) -> validate -> promote.

---

## Phase Context

Phase 9 (v9.27-v9.48): App Optimization. v9.48 is the final iteration pending close-out.
Phase 10: Bourdain Pipeline (114 videos), IaC to GCP, middleware stamp. Bourdain ~v10.50.

---

## Environment

| Fact | Value |
|------|-------|
| Machine | NZXTcos: i9-13900K, 64GB, RTX 2080 SUPER, CachyOS, fish |
| NZXTcos Path | ~/dev/projects/kjtcom |
| tsP3-cos Path | ~/Development/Projects/kjtcom |
| Firebase | kjtcom-c78cd |
| SA | ~/.config/gcloud/kjtcom-sa.json |
| Flutter | 3.41.6, Dart 3.11.4 |
| Iteration Env | set -gx IAO_ITERATION v9.48 |
| Telegram Bot | systemd: kjtcom-telegram-bot.service |
| Bot Env | /home/kyle/.config/kjtcom/bot.env |
| Deploy | cd ~/dev/projects/kjtcom && firebase deploy --only hosting |
| Sleep Mask | systemctl mask suspend (NZXTcos) |

---

## Active Gotchas

| ID | Description | Status |
|----|-------------|--------|
| G1 | Heredocs in fish - use printf | ACTIVE |
| G19 | Gemini runs bash - wrap in fish -c | ACTIVE |
| G34 | Single array-contains per Firestore query | ACTIVE |
| G43 | Map tile CORS | ACTIVE |
| G47 | CanvasKit blocks Playwright DOM | Open |
| G53 | Firebase MCP reauth per session | Recurring |
| G54 | 10 transitive deps locked by upstream | Documented |

See data/gotcha_archive.json for all 18+ resolved gotchas.

---

## Key Files

| File | Purpose |
|------|---------|
| docs/evaluator-harness.md | Qwen personality directive |
| scripts/cleanup_docs.py | File management enforcement (v9.48) |
| scripts/run_evaluator.py | Qwen eval (structural enforcement, W# validation) |
| scripts/generate_artifacts.py | Artifact drafts (single changelog) |
| scripts/telegram_bot.py | Bot (3-route, session memory, rating sort, systemd) |
| scripts/intent_router.py | Intent classification (3 routes, GEMINI_MODEL) |
| scripts/firestore_query.py | Firestore query (G34, Python sort) |
| scripts/post_flight.py | Post-flight verification |
| scripts/build_architecture_html.py | MMD -> HTML |
| scripts/enrich_counties.py | County enrichment |
| scripts/embed_archive.py | Archive -> ChromaDB |
| scripts/utils/ollama_config.py | Ollama defaults + GEMINI_MODEL |
| scripts/utils/iao_logger.py | Event logger |
| data/schema_reference.json | Schema reference (sortable_fields) |
| data/gotcha_archive.json | Resolved gotchas |
| data/middleware_registry.json | Middleware catalog |
| app/web/architecture.html | Architecture diagram |
| app/web/claw3d.html | 3D IAO visualization |
| docs/pipeline-review-v9.47.md | Bourdain prep |
