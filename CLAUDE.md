# kjtcom - Claude Code Agent Instructions

## Current Iteration: v9.51

Read in order: (1) This file, (2) docs/kjtcom-design-v9.51.md, (3) docs/kjtcom-plan-v9.51.md, (4) docs/evaluator-harness.md.

---

## Agent Session Best Practices (PERMANENT)

### Pre-Launch
1. CLAUDE.md + GEMINI.md saved. wc -l both >= 200. Harnesses GROW.
2. /quit between iterations. ONE per session.
3. set -gx IAO_ITERATION v9.XX. Ollama (4 models). Restart bot systemd. Verify SA.
4. Archive integrity. Clean drafts. Clean orphaned changelogs.
5. jsonschema installed.

### Session Discipline
- Post-flight -> evaluation -> artifacts -> promotion. No unpromoted drafts.
- NEVER delete docs. Archive to docs/archive/.
- Harness files grow. Never abbreviate.

### Environment
- SA: ~/.config/gcloud/{project}-sa.json. API keys: fish config, KJTCOM_* prefix.
- claude --dangerously-skip-permissions / gemini --yolo
- Bot: systemd kjtcom-telegram-bot.service. Sleep: systemctl mask suspend.

---

## File Management (v9.48+ - ABSOLUTE)

docs/: current iteration + living docs. docs/archive/: all prior (one copy). docs/drafts/: ephemeral.
Single changelog: kjtcom-changelog.md. Append top. Never create changelog-v{X}.md.
NEVER delete docs.

---

## Execution Order (v9.49+ - CORRECTED)

1. Execute workstreams -> 2. post_flight.py -> 3. run_evaluator.py (NOT current build log) -> 4. generate_artifacts.py -> 5. --validate-only -> 6. --promote

---

## Qwen Schema-Validated Harness (v9.49+)

data/eval_schema.json enforces: score 0-9 (report as X/10 NOT X/9 - v9.51 fix), MCPs whitelist (only used ones), outcome enum, improvements min 2, what_could_be_better min 3, summary plain text (no JSON - v9.50 fix), agents = executor not evaluator (v9.50 fix).

Validation + retry (max 3). Specific error feedback. Schema > prompt.

### v9.51 Fixes
- Score scale: "8/9" bug. Schema says max=9 on 10-point scale. Report as X/10.
- Build log: raw JSON in execution section. render_build_markdown() converts to prose.
- LLM names: exact Ollama names (qwen3.5:9b not "qwen-max").
- Trident cost: count llm_call events. Never "0 tokens" when events exist.

---

## Post-Flight (v9.43+ - MANDATORY)

post_flight.py. Site 200, bot /status, /ask >= 6,181, architecture.html, claw3d.html.

---

## Rules That Never Change

Git WRITE forbidden. firebase deploy allowed. Never ask permission. Self-heal 3x.
Fish shell. pip --break-system-packages. python3 -u. No em-dashes. NEVER delete docs.

---

## Token Efficiency (v9.40+)

<50K. ollama_config.py (think:false, G51). GEMINI_MODEL constant. iao_logger.py.

---

## README Cadence (v9.46+)

Every iteration: changelog + version. Every 3: full overhaul. Next overhaul: v9.52.

---

## Agent-Agnostic (v9.49+)

Artifacts work for either agent. Launch: "Read [CLAUDE/GEMINI].md and execute."

---

## Multi-Agent (v9.35+)

Min 2 LLMs. Claude Code, Gemini CLI, Qwen3.5-9B (evaluator), Nemotron Mini 4B, GLM-4.6V-Flash, nomic-embed-text, Gemini Flash (litellm).

## MCPs (5 - ONLY valid)

Firebase, Context7, Firecrawl, Playwright, Dart. No others.

---

## Middleware as Primary IP (v9.42+)

Middleware is the product. Components: harnesses (CLAUDE.md, GEMINI.md 200+, evaluator-harness.md), eval (run_evaluator.py schema-validated, eval_schema.json, agent_scores.json, test_eval_schema.py v9.51), harness registry (middleware_registry.json), RAG (embed_archive.py, query_rag.py, ChromaDB ~1,700 chunks), intent router (3 routes), Firestore query (G34, Python sort), county enrichment, event logging (iao_logger.py), artifact generator (single changelog, --promote, --validate-only, render_build_markdown v9.51), gotcha archive (18+), bot (systemd, session memory, rating sort, 3-route), config (ollama_config.py: GEMINI_MODEL, batch 45-min), post-flight, cleanup_docs.py, architecture HTML, Claw3D (~28 nodes), MW tab (mw_tab.dart), pipeline review.

---

## Artifact Discipline (v9.42+)

design + plan + build (POST-FLIGHT, markdown prose not JSON) + report (Evidence, X/10 scores, What Could Be Better) + CLAUDE.md + GEMINI.md (200+) + changelog APPENDED.

---

## Dependency Upgrade Protocol (v9.45+)

ONE major at a time. Context7 MCP. analyze -> test -> build. 10 transitive deps locked upstream.

---

## Cross-Pipeline Schema Enrichment (v9.42+)

Audit all pipelines when enriching one. TripleDB counties 918/1100.

---

## Bot Features (v9.41-v9.44)

3-route intent router (firestore/chromadb/web). Session memory (10-min TTL). Rating sort (Python-side). systemd managed (WatchdogSec=600). Commands: /ask, /status, /search, /help, /start, /scores, /gotcha, /evaluate, /query.

---

## Claw3D (v9.38, updated v9.50)

Three.js at kylejeromethompson.com/claw3d.html. ~28 nodes. Updated from 15 (v9.38) to 28 (v9.50). 3D button accessible from main app (v9.51).

---

## Phase Context

Phase 9 (v9.27-v9.51+): App Optimization. Qwen harness reliable before Phase 10.
Phase 10: Bourdain (114 videos), IaC to GCP, middleware stamp. Several more v9.XX iterations until Qwen is trustworthy.

---

## Phase 9 Summary (v9.27-v9.51, 25 iterations)

6-tab Flutter app + MW tab, NoSQL query, multi-agent (4 LLMs, 5 MCPs), middleware (33 components), Telegram bot (3-route, session memory, rating sort, systemd), county enrichment (918/1100), schema-validated evaluator, artifact automation, gotcha archive (18+), 3D visualization (28 nodes), architecture HTML.

---

## Companion Projects

TachTech Intranet (ttintra.net): GCP tachnet-intranet, Flutter Web, Okta SSO planned.
socalpha1: Production SIEM agentic model, Pub/Sub -> 4 agents -> SOAR.
TripleDB (tripledb.net): 805 DDD videos, 1,100 restaurants, IAO methodology origin (48+ iterations).

---

## Environment

NZXTcos: i9-13900K, 64GB, RTX 2080 SUPER, CachyOS, fish | ~/dev/projects/kjtcom
Firebase: kjtcom-c78cd | SA: ~/.config/gcloud/kjtcom-sa.json | Flutter: 3.41.6
Bot: systemd kjtcom-telegram-bot.service | set -gx IAO_ITERATION v9.51

---

## Active Gotchas

G1 (heredocs), G19 (Gemini bash), G34 (array-contains), G43 (CORS), G47 (CanvasKit), G53 (Firebase MCP reauth), G54 (transitive deps). See data/gotcha_archive.json.

---

## Key Files

docs/evaluator-harness.md, data/eval_schema.json, scripts/run_evaluator.py, scripts/generate_artifacts.py, scripts/test_eval_schema.py (NEW v9.51), scripts/cleanup_docs.py, scripts/telegram_bot.py, scripts/intent_router.py, scripts/firestore_query.py, scripts/post_flight.py, scripts/build_architecture_html.py, scripts/utils/ollama_config.py, data/schema_reference.json, data/gotcha_archive.json, data/middleware_registry.json, app/web/architecture.html, app/web/claw3d.html, app/lib/widgets/mw_tab.dart, docs/pipeline-review-v9.47.md

---

## Qwen Harness Development History (reference)

- v9.41: Workstream-level scoring introduced (per-W# outcome, agents, LLMs, MCPs)
- v9.42: Middleware as IP mandate. Gotcha archive. Cross-pipeline enrichment.
- v9.43: Post-flight verification mandatory. Evidence column. MCP whitelist.
- v9.44: Gemini model string centralized (GEMINI_MODEL). Python-side sort.
- v9.45: Dependency upgrade protocol. Phase 10 readiness audit (17/18 ready).
- v9.46: Evaluator harness file (docs/evaluator-harness.md). Skeptical scoring. Banned phrases. "What Could Be Better" mandatory.
- v9.47: Workstream fidelity rule. Evidence cross-check. Pipeline phase review.
- v9.48: File management rules. Harness growth enforcement (200+ lines). Qwen structural enforcement in Python.
- v9.49: JSON schema validation (data/eval_schema.json). Validation + retry loop. Execution order corrected.
- v9.50: MCPs = only used (not full enum). Agent attribution = executor not evaluator. Plain text summary.
- v9.51: Score scale X/10 not X/9. Build log rendered as markdown not JSON. LLM exact names. Schema test cases.

Each iteration added structural enforcement. Prompt guidance alone produces ~6-28% compliance. Schema + validation + feedback produces 99%+ (Typia/AutoBe research, Qwen Meetup Korea 2025).

---

## File Inventory (complete middleware catalog)

### Harnesses (3)
CLAUDE.md, GEMINI.md, docs/evaluator-harness.md

### Scripts (18)
run_evaluator.py, generate_artifacts.py, cleanup_docs.py, telegram_bot.py, intent_router.py, firestore_query.py, post_flight.py, build_architecture_html.py, enrich_counties.py, embed_archive.py, query_rag.py, brave_search.py, build_registry_v2.py, analyze_events.py, generate_leaderboard.py, test_eval_schema.py (NEW v9.51)

### Utilities (3)
scripts/utils/iao_logger.py, scripts/utils/ollama_config.py, scripts/utils/ollama_logged.py

### Data Stores (6)
data/eval_schema.json, data/schema_reference.json, data/gotcha_archive.json, data/middleware_registry.json, data/chromadb/, data/iao_event_log.jsonl, agent_scores.json

### Templates (3)
template/artifacts/build-template.md, template/artifacts/report-template.md, template/artifacts/changelog-template.md

### Web Assets (2)
app/web/architecture.html, app/web/claw3d.html

### Services (1)
kjtcom-telegram-bot.service
