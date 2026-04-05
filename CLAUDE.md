# kjtcom - Claude Code Agent Instructions

## Current Iteration: v9.44

IMPORTANT: Read documents in this EXACT order before executing:

1. This file (CLAUDE.md)
2. docs/kjtcom-design-v9.44.md - Workstreams, architecture, amendments
3. docs/kjtcom-plan-v9.44.md - Step-by-step execution

Do NOT begin execution until files 1-3 have been read.

---

## Agent Session Best Practices (v9.42+ - PERMANENT)

### Pre-Launch Checklist
1. CLAUDE.md and GEMINI.md MUST be saved to disk in the launch directory BEFORE starting.
2. /quit every session and start fresh between iterations.
3. `set -gx IAO_ITERATION v9.XX` BEFORE launching.
4. Verify Ollama: `ollama list` shows 4 models.
5. Restart bot: `sudo systemctl restart kjtcom-telegram-bot`
6. Verify Firebase SA: `test -f ~/.config/gcloud/kjtcom-sa.json`.
7. Verify archive integrity: `ls docs/archive/ | wc -l` (must be >= prior iteration count).

### Session Discipline
- ONE iteration per session. Never chain.
- If session crashes, /quit and relaunch.
- Every session ends with: artifact production -> post-flight verification -> promotion.
- Drafts cross-checked and promoted. NEVER leave unpromoted drafts.
- Harness files GROW. Never abbreviate.

### CRITICAL: Document Archival
- **NEVER run rm or git rm on ANY docs/kjtcom-*.md file.**
- Use `mv docs/kjtcom-*-v{X}.md docs/archive/` instead.
- If you find yourself about to delete a doc file, STOP. Archive it.
- This rule has been violated in v9.42 and v9.43. It must not happen again.

### Environment Architecture
- GCP SA keys: ~/.config/gcloud/{project}-sa.json (NEVER in repo)
- API keys: fish shell config, per-project prefixed (KJTCOM_*)
- Agent launches: `claude --dangerously-skip-permissions` / `gemini --yolo`
- Bot: systemd (kjtcom-telegram-bot.service)
- Sleep mask: `systemctl mask suspend` on dev machines

---

## Post-Flight Verification - MANDATORY (v9.43+)

After every iteration, BEFORE the session ends:

1. `python3 scripts/post_flight.py` - all checks must pass
2. Verify site: HTTP 200 from kylejeromethompson.com
3. Verify bot: /status responds via Telegram
4. Verify query: /ask returns correct entity count (>= 6,181)
5. Verify architecture.html loads
6. Log results in build log POST-FLIGHT VERIFICATION section
7. If ANY check fails: fix, re-deploy, re-verify. Do NOT end session with failures.

---

## Qwen Claim Audit - MANDATORY (v9.43+)

- Every "complete" workstream needs linked evidence in the scorecard
- Scorecard includes Evidence column
- Valid MCPs ONLY: Firebase, Context7, Firecrawl, Playwright, Dart
- No "TBD" anywhere in report or changelog
- Workstream names must EXACTLY match design doc W# labels (v9.44+ fix)
- Specific numbers required (entity counts, chunk counts, test results)

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
- **NEVER delete docs. ALWAYS archive to docs/archive/.**

---

## Token Efficiency Mandate (v9.40+)

- Target: <50K Claude Code tokens per iteration
- ALL Ollama calls use ollama_config.py (think:false, G51)
- num_predict: 512 default, 2048 evaluations, 2048 batch (45-min timeout)
- Gemini Flash model: use GEMINI_MODEL from ollama_config.py (v9.44+)
- Log all usage via iao_logger.py

---

## Gemini Flash Model String (v9.44+)

The Gemini Flash model string is centralized in scripts/utils/ollama_config.py as GEMINI_MODEL. ALL litellm calls for Gemini must use this constant. History of model string issues:
- v9.41: gemini/gemini-2.0-flash deprecated (404)
- v9.43: litellm.AuthenticationError 400
- v9.44: diagnosed and fixed, centralized as GEMINI_MODEL

Never hardcode the model string in individual scripts.

---

## Multi-Agent Orchestration (v9.35+)

Minimum 2 LLMs. Document per workstream.

| Agent | Engine | Use For |
|-------|--------|---------|
| Claude Code | Claude API | Primary executor |
| Qwen3.5-9B | Ollama local | Evaluation, code review |
| Nemotron Mini 4B | Ollama local | Fast triage |
| GLM-4.6V-Flash | Ollama local | Vision |
| nomic-embed-text | Ollama local | Embeddings only |
| Gemini Flash | Gemini API (litellm) | Intent routing, synthesis |

---

## MCP Servers (5 total - ONLY these names are valid)

Firebase, Context7, Firecrawl, Playwright, Dart. No others exist.

---

## Middleware as Primary IP (v9.42+)

Middleware is the product. kjtcom is the lab. Every iteration adds to middleware.

Components: harnesses (grow, never shrink), harness registry, evaluator (workstream scoring + claim audit), RAG, intent router (3 routes: firestore/chromadb/web), Firestore query (G34 workaround, Python-side sort v9.44+), county enrichment, event logging, artifact generator (--promote/--validate-only), gotcha archive, bot (systemd, session memory v9.43+, rating-aware v9.44+), config (ollama_config.py: defaults + batch + GEMINI_MODEL), post-flight verification, architecture HTML renderer.

---

## Bot Session Memory (v9.43+)

In-memory dict keyed by user_id. 10-min TTL. "those 26" or "out of them" resolves to previous result set. Context passed to Gemini Flash for follow-up.

---

## Rating-Aware Queries (v9.43+, fixed v9.44)

schema_reference.json includes sortable_fields: t_enrichment.google_places.rating and user_ratings_total. Sort in Python (v9.44) to avoid composite index dependency. Intent router recognizes "highest rated", "best", "top N".

---

## Artifact Discipline (v9.42+)

Every iteration produces: design, plan, build (with POST-FLIGHT section), report (with Evidence column), CLAUDE.md, GEMINI.md, changelog entry (not a stub).

Workflow: generate -> evaluate -> validate -> promote. Never leave unpromoted drafts.

Changelog must use NEW/UPDATED/FIXED prefixes with specific numbers. "TBD" is banned.

---

## Environment

| Fact | Value |
|------|-------|
| Machine | NZXTcos: i9-13900K, 64GB, RTX 2080 SUPER, CachyOS, fish |
| Path | ~/dev/projects/kjtcom |
| Firebase | kjtcom-c78cd |
| SA | ~/.config/gcloud/kjtcom-sa.json |
| Flutter | 3.41.6, Dart 3.11.4 |
| Iteration | set -gx IAO_ITERATION v9.44 |
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
| G57 | Gemini Flash model string instability | RESOLVED (v9.44) - centralized in GEMINI_MODEL |

See data/gotcha_archive.json for all resolved gotchas.

---

## Key Files

| File | Purpose |
|------|---------|
| scripts/telegram_bot.py | Bot (3-route, session memory, rating sort, systemd) |
| scripts/intent_router.py | Gemini Flash intent (3 routes, sort/limit, uses GEMINI_MODEL) |
| scripts/firestore_query.py | Firestore query (G34, Python-side sort v9.44+) |
| scripts/post_flight.py | Post-flight verification |
| scripts/build_architecture_html.py | MMD -> HTML renderer |
| scripts/enrich_counties.py | County enrichment |
| scripts/generate_artifacts.py | Artifacts (--promote, --validate-only, Evidence) |
| scripts/run_evaluator.py | Qwen eval (claim audit, exact W# names) |
| scripts/utils/ollama_config.py | Ollama defaults + batch + GEMINI_MODEL |
| data/schema_reference.json | Schema ref (sortable_fields) |
| data/gotcha_archive.json | Resolved gotchas |
| data/middleware_registry.json | Middleware catalog |
| app/web/architecture.html | Interactive architecture diagram |
