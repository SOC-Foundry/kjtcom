# kjtcom - Claude Code Agent Instructions

## Current Iteration: v9.43

IMPORTANT: Read documents in this EXACT order before executing:

1. This file (CLAUDE.md)
2. docs/kjtcom-design-v9.43.md - Workstreams, architecture, amendments
3. docs/kjtcom-plan-v9.43.md - Step-by-step execution

Do NOT begin execution until files 1-3 have been read.

---

## Agent Session Best Practices (v9.42+ - PERMANENT)

### Pre-Launch Checklist
1. CLAUDE.md and GEMINI.md MUST be saved to disk in the launch directory BEFORE starting.
2. /quit every session and start fresh between iterations. Token context degrades over long sessions.
3. `set -gx IAO_ITERATION v9.XX` BEFORE launching.
4. Verify Ollama: `ollama list` shows 4 models.
5. Restart Telegram bot: `sudo systemctl restart kjtcom-telegram-bot`
6. Verify Firebase SA: `test -f ~/.config/gcloud/kjtcom-sa.json`.

### Session Discipline
- ONE iteration per session. Never chain.
- If session crashes, /quit and relaunch. Do not recover mid-session.
- Every session ends with: artifact production -> post-flight verification -> promotion.
- Drafts cross-checked and promoted before session ends. NEVER leave unpromoted drafts.
- Harness files GROW. Never abbreviate.
- Previous iteration docs go to docs/archive/. NEVER delete them.

### Environment Architecture
- GCP SA keys: ~/.config/gcloud/{project}-sa.json (NEVER in repo)
- API keys: fish shell config, per-project prefixed (KJTCOM_*)
- Agent launches: `claude --dangerously-skip-permissions` / `gemini --yolo`
- Bot: systemd service (kjtcom-telegram-bot.service), not tmux
- Sleep mask: `systemctl mask suspend` on dev machines

---

## Post-Flight Verification - MANDATORY (v9.43+)

After every iteration, BEFORE the session ends:

1. `curl -s -o /dev/null -w "%{http_code}" https://kylejeromethompson.com` -> expect 200
2. Verify bot: send /status to @kjtcom_iao_bot, verify response
3. Verify query: send `/ask how many entities are in the database`, verify count >= 6,181
4. Run: `python3 scripts/post_flight.py`
5. Log results in build log under POST-FLIGHT VERIFICATION section
6. If ANY check fails: log as gotcha, do NOT mark iteration complete

---

## Qwen Claim Audit - MANDATORY (v9.43+)

Every workstream Qwen marks "complete" MUST have linked evidence:
- File exists (ls -la)
- Command output captured
- Test passed (flutter test)
- Bot responded (Telegram API)
- Site loaded (curl HTTP 200)

"Complete" without evidence = "unverified."

Workstream Scorecard MUST include Evidence column.

Qwen MCP whitelist (only valid values): Firebase, Context7, Firecrawl, Playwright, Dart. Anything else is hallucinated. If no MCP used, column is "-".

No "TBD" in Trident evaluation. No corporate fluff. Specific numbers required.

---

## Rules That Never Change

- Git WRITE commands FORBIDDEN. Kyle handles ALL git.
- firebase deploy ALLOWED (hosting only).
- NEVER ask permission. The plan IS the permission.
- Self-heal errors: diagnose -> fix -> re-run (max 3 attempts, then gotcha).
- Fish shell. pip --break-system-packages. python3 -u.
- No em-dashes. " - " for dashes. "->" for arrows.
- "pipelines" and "log types," never "tables" or "datasets."
- Build on existing code. Read files before overwriting.
- Previous iteration docs archived to docs/archive/, NEVER deleted.

---

## Token Efficiency Mandate (v9.40+)

- Target: <50K Claude Code tokens per infrastructure iteration
- ALL Ollama calls use scripts/utils/ollama_config.py (think:false mandatory, G51)
- num_predict: 512 default, 2048 for evaluations, 2048 with 45-min timeout for batch ops
- Prefer local LLM for simple tasks. Log all usage via iao_logger.py.

---

## Multi-Agent Orchestration (v9.35+)

Minimum 2 LLMs per iteration. Document per workstream.

| Agent | Engine | Use For |
|-------|--------|---------|
| Claude Code | Claude API | Primary executor, Flutter, architecture |
| Qwen3.5-9B | Ollama local | Evaluation, code review |
| Nemotron Mini 4B | Ollama local | Fast triage |
| GLM-4.6V-Flash | Ollama local | Vision, screenshots |
| nomic-embed-text | Ollama local | Embeddings only |
| Gemini Flash | Gemini API (litellm) | Intent routing, synthesis |

---

## MCP Servers (5 total)

| Server | Use For |
|--------|---------|
| Firebase MCP | Firestore queries |
| Context7 MCP | API documentation |
| Firecrawl MCP | Web scraping |
| Playwright MCP | Browser automation (G47: CanvasKit blocks DOM) |
| Dart MCP | Code analysis |

These are the ONLY valid MCP server names. No others exist.

---

## Middleware as Primary IP (v9.42+)

Middleware is the product. kjtcom is the lab. Every iteration adds to middleware.

Components: harnesses (CLAUDE.md/GEMINI.md - grow, never shrink), harness registry (middleware_registry.json), evaluator (run_evaluator.py + workstream scoring + claim audit), RAG (embed_archive.py + query_rag.py), intent router (3 routes: firestore/chromadb/web), Firestore query module, county enrichment, event logging, artifact generator (--promote/--validate-only), gotcha archive, bot (systemd managed, session memory v9.43+, rating-aware v9.43+), config (ollama_config.py with batch defaults), post-flight verification (v9.43+), architecture HTML renderer (v9.43+).

---

## Artifact Discipline (v9.42+)

Every iteration produces:
- kjtcom-design-v{X}.md (pre-staged)
- kjtcom-plan-v{X}.md (pre-staged)
- kjtcom-build-v{X}.md (generated, cross-checked, promoted; includes POST-FLIGHT VERIFICATION section)
- kjtcom-report-v{X}.md (Workstream Scorecard with Evidence column, promoted)
- CLAUDE.md + GEMINI.md (updated)
- Changelog entry (specific numbers, not TBD)

Workflow: generate -> evaluate -> validate -> promote. Drafts never sit unpromoted.

---

## Bot Session Memory (v9.43+)

Telegram bot stores last query context per user_id (in-memory dict, 10-min TTL). References like "those 26" or "out of them" resolve to previous result set. Context passed to Gemini Flash for follow-up analysis.

---

## Rating-Aware Queries (v9.43+)

schema_reference.json includes sortable_fields: t_enrichment.google_places.rating and user_ratings_total. Intent router recognizes "highest rated", "best", "top N", "most reviewed" and generates sort/limit parameters.

---

## Environment

| Fact | Value |
|------|-------|
| Machine | NZXTcos: i9-13900K, 64GB RAM, RTX 2080 SUPER, CachyOS, fish |
| Path | ~/dev/projects/kjtcom |
| Firebase | kjtcom-c78cd |
| SA | ~/.config/gcloud/kjtcom-sa.json |
| Flutter | 3.41.6, Dart 3.11.4 |
| Iteration | set -gx IAO_ITERATION v9.43 |
| Bot | systemd: kjtcom-telegram-bot.service |
| Bot Env | /home/kyle/.config/kjtcom/bot.env |

---

## Active Gotchas

| ID | Description | Status |
|----|-------------|--------|
| G1 | Heredocs in fish - use printf | ACTIVE |
| G34 | Single array-contains per Firestore query | ACTIVE |
| G43 | Map tile CORS | ACTIVE |
| G47 | CanvasKit blocks Playwright DOM | Open |
| G53 | Firebase MCP reauth per session | Recurring |

See data/gotcha_archive.json for resolved gotchas.

---

## Key Files

| File | Purpose |
|------|---------|
| scripts/telegram_bot.py | Bot (3-route, session memory, rating-aware, systemd) |
| scripts/intent_router.py | Gemini Flash (3 routes, sort/limit) |
| scripts/firestore_query.py | Firestore query (G34 workaround, orderBy) |
| scripts/post_flight.py | Post-flight verification (NEW v9.43) |
| scripts/build_architecture_html.py | MMD -> HTML renderer (NEW v9.43) |
| scripts/enrich_counties.py | County enrichment |
| scripts/generate_artifacts.py | Artifacts (--promote, --validate-only, Evidence column) |
| scripts/run_evaluator.py | Qwen eval (workstreams, claim audit, MCP whitelist) |
| scripts/query_rag.py | ChromaDB search |
| scripts/embed_archive.py | Archive -> ChromaDB |
| scripts/brave_search.py | Brave Search API |
| scripts/utils/iao_logger.py | Event logger |
| scripts/utils/ollama_config.py | Ollama defaults (batch: 45-min timeout) |
| data/schema_reference.json | Schema ref (sortable_fields v9.43+) |
| data/gotcha_archive.json | Resolved gotchas |
| data/middleware_registry.json | Middleware catalog |
| app/web/architecture.html | Interactive architecture diagram (NEW v9.43) |
