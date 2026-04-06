# kjtcom - Gemini CLI Agent Instructions

## Current Iteration: v9.50

Read in order: (1) This file, (2) docs/kjtcom-design-v9.50.md, (3) docs/kjtcom-plan-v9.50.md, (4) docs/evaluator-harness.md. Agent-agnostic - Gemini can execute from this file alone.

## Your Role
Pipeline executor (Phases 1-5). Gemini Flash API: intent routing, synthesis. May lead iterations (led v9.47/v9.48). G19: Gemini runs bash - wrap fish commands in fish -c. firebase deploy FORBIDDEN from Gemini.

Read in order: (1) This file, (2) docs/kjtcom-design-v9.50.md, (3) docs/kjtcom-plan-v9.50.md, (4) docs/evaluator-harness.md.

---

## Agent Session Best Practices (PERMANENT)

### Pre-Launch
1. CLAUDE.md + GEMINI.md saved BEFORE starting. wc -l both >= 200.
2. /quit between iterations. ONE per session. Token context degrades.
3. set -gx IAO_ITERATION v9.XX. Verify Ollama (4 models). Restart bot systemd. Verify SA.
4. Archive integrity: ls docs/archive/ | wc -l. Clean drafts. Clean orphaned changelogs.
5. pip install jsonschema --break-system-packages (if not installed).

### Session Discipline
- Post-flight -> evaluation -> artifact generation -> promotion.
- Drafts cross-checked. NEVER leave unpromoted.
- Harnesses GROW. Never abbreviate. 200+ lines enforced.
- NEVER delete docs. Archive to docs/archive/.

### Environment
- SA keys: ~/.config/gcloud/{project}-sa.json (NEVER in repo)
- API keys: fish shell config, KJTCOM_* prefix
- claude --dangerously-skip-permissions / gemini --yolo
- Bot: systemd kjtcom-telegram-bot.service
- Sleep: systemctl mask suspend

---

## File Management (v9.48+ - ABSOLUTE)

docs/: current iteration + living docs only. docs/archive/: all prior (one copy). docs/drafts/: ephemeral.
Single changelog: docs/kjtcom-changelog.md. Append top. Never create changelog-v{X}.md.
NEVER delete docs. NEVER rm docs/kjtcom-*.md.

---

## Execution Order (v9.49+ - CORRECTED)

Evaluator NEVER reads current build log. Correct sequence:
1. Execute workstreams
2. post_flight.py
3. run_evaluator.py (reads design doc + event log + file checks, NOT build log)
4. generate_artifacts.py (produces build/report/changelog from evaluation JSON)
5. --validate-only -> --promote

---

## Qwen Schema-Validated Harness (v9.49+)

All Qwen calls use data/eval_schema.json. Key constraints:
- score max 9 (never 10)
- mcps: ONLY servers actually used, not full enum (v9.50 fix)
- outcome: complete/partial/failed/deferred
- improvements: min 2 per workstream
- what_could_be_better: min 3
- summary: plain text 50-500 chars, NO JSON (v9.50 fix)
- agents: executing agent from design doc, NOT "Qwen" (v9.50 fix)

Validation + retry (max 3). Specific error feedback on failure. Schema enforcement > prompt guidance.

---

## Qwen Harness Bug Fixes (v9.50)

Three patterns fixed:
1. MCPs: Qwen was listing all 5 for every workstream. Fix: maxItems 3, "list ONLY MCPs actually invoked"
2. Agent attribution: Qwen listed herself. Fix: "You are EVALUATOR not executor. Executor is in design doc header."
3. Raw JSON in narrative: Fix: summary field is plain text. generate_artifacts.py renders JSON to markdown.

---

## Post-Flight (v9.43+ - MANDATORY)

post_flight.py before ending. Site 200, bot /status, bot /ask >= 6,181, architecture.html, claw3d.html.
If ANY fails: fix first.

---

## Rules That Never Change

Git WRITE forbidden. firebase deploy allowed. Never ask permission. Self-heal 3x.
Fish shell. pip --break-system-packages. python3 -u. No em-dashes. NEVER delete docs.

---

## Token Efficiency (v9.40+)

<50K. ollama_config.py (think:false). GEMINI_MODEL constant. iao_logger.py.

---

## README Cadence (v9.46+)

Every iteration: changelog + version. Every 3: full overhaul. v9.50 is overhaul (v9.46, v9.49, but v9.49 was missed - catch up now).

---

## Agent-Agnostic Artifacts (v9.49+)

Design docs work for either agent. Launch: "Read [CLAUDE/GEMINI].md and execute."

---

## Multi-Agent (v9.35+)

Min 2 LLMs. Claude Code, Gemini CLI, Qwen3.5-9B (evaluator), Nemotron Mini 4B, GLM-4.6V-Flash, nomic-embed-text, Gemini Flash (litellm).

## MCPs (5 - ONLY valid names)

Firebase, Context7, Firecrawl, Playwright, Dart. No others.

---

## Middleware as Primary IP (v9.42+)

Middleware is the product. Components: harnesses (CLAUDE.md, GEMINI.md 200+, evaluator-harness.md), eval (run_evaluator.py schema-validated, eval_schema.json, agent_scores.json), harness registry (middleware_registry.json), RAG (embed_archive.py, query_rag.py, ChromaDB ~1,700 chunks), intent router (3 routes), Firestore query (G34, Python sort), county enrichment, event logging (iao_logger.py), artifact generator (single changelog, --promote, --validate-only), gotcha archive (18+ resolved), bot (systemd, session memory, rating sort, 3-route), config (ollama_config.py: GEMINI_MODEL, batch 45-min), post-flight, cleanup_docs.py, architecture HTML, Claw3D (~28 nodes v9.50), MW tab (mw_tab.dart), pipeline review.

---

## Artifact Discipline (v9.42+)

design + plan + build (POST-FLIGHT) + report (Evidence, schema-validated scorecard, What Could Be Better) + CLAUDE.md + GEMINI.md (200+) + changelog APPENDED.
Workflow: execute -> post-flight -> evaluate (schema) -> generate -> validate -> promote.

---

## Phase Context

Phase 9 (v9.27-v9.50+): App Optimization. Qwen harness reliability required before Phase 10.
Phase 10: Bourdain (114 videos), IaC to GCP, middleware stamp. ~v10.52+.

---

## Environment

NZXTcos: i9-13900K, 64GB, RTX 2080 SUPER, CachyOS, fish
Path: ~/dev/projects/kjtcom | Firebase: kjtcom-c78cd | SA: ~/.config/gcloud/kjtcom-sa.json
Flutter: 3.41.6, Dart 3.11.4 | Bot: systemd kjtcom-telegram-bot.service
Iteration: set -gx IAO_ITERATION v9.50

---

## Active Gotchas

G1 (heredocs), G19 (Gemini bash), G34 (array-contains), G43 (CORS), G47 (CanvasKit), G53 (Firebase MCP reauth), G54 (transitive deps). See data/gotcha_archive.json.

---

## Key Files

docs/evaluator-harness.md, data/eval_schema.json, scripts/run_evaluator.py, scripts/generate_artifacts.py, scripts/cleanup_docs.py, scripts/telegram_bot.py, scripts/intent_router.py, scripts/firestore_query.py, scripts/post_flight.py, scripts/build_architecture_html.py, scripts/enrich_counties.py, scripts/embed_archive.py, scripts/utils/ollama_config.py, data/schema_reference.json, data/gotcha_archive.json, data/middleware_registry.json, app/web/architecture.html, app/web/claw3d.html, app/lib/widgets/mw_tab.dart, docs/pipeline-review-v9.47.md

---

## Dependency Upgrade Protocol (v9.45+)

ONE major version at a time. Context7 MCP for changelogs. analyze -> test -> build after each.
v9.45 finding: 10 transitive deps locked by upstream (flutter_map, SDK). Not actionable.

---

## Cross-Pipeline Schema Enrichment (v9.42+)

When enriching a field on one pipeline, audit ALL pipelines for the same field. Schema gaps logged. schema_reference.json flags per-pipeline coverage. TripleDB counties enriched v9.42 (918/1100).

---

## Bot Features (v9.41-v9.44)

- 3-route intent router: firestore (entity data), chromadb (dev history), web (external)
- Session memory: in-memory dict per user_id, 10-min TTL, "those 26" resolves
- Rating-aware: Python-side sort on t_enrichment.google_places.rating, top N queries
- systemd managed: WatchdogSec=600, auto-restart, sdnotify
- Commands: /ask, /status, /search, /help, /start, /scores, /gotcha, /evaluate, /query

---

## Claw3D Visualization (v9.38, updated v9.50)

Three.js IAO workspace at kylejeromethompson.com/claw3d.html. ~28 nodes representing agents, middleware, data stores, and infrastructure. Updated from v9.38 (15 nodes) to v9.50 (28 nodes) with intent router, gotcha archive, evaluator harness, systemd bot, schema validation, MW tab.

---

## Phase 9 Summary (v9.27-v9.50, 24 iterations)

Key deliverables: 6-tab Flutter app (Results, Map, Globe, IAO, MW, Schema), NoSQL query system, multi-agent orchestration (4 local LLMs, 5 MCPs), middleware layer (20+ components), Telegram bot (3-route, session memory, rating sort, systemd), county enrichment (918/1100), schema-validated evaluator, artifact automation, gotcha archive (18+ resolved), 3D visualization, architecture HTML.

---

## Companion Projects

### TachTech Intranet (ttintra.net)
- GCP: tachnet-intranet. Flutter Web, 10 dashboard modules, Okta SSO planned.
- Middleware adoption from kjtcom lab documented in intranet-update-v2.7.md.

### socalpha1 (TachTech-Engineering/socalpha1)
- Production customer SIEM agentic model. Pub/Sub -> 4 parallel agents -> Cloud Workflows -> Tines SOAR.
- Pattern influences kjtcom intent routing architecture.

### TripleDB (tripledb.net)
- 805 DDD YouTube videos, 1,100 restaurant entities. Flutter Web app at tripledb.net.
- IAO methodology originally developed here across 48+ iterations.
