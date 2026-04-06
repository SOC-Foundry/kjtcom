# kjtcom - Gemini CLI Agent Instructions

Agent-agnostic. G19: wrap fish in fish -c. firebase deploy FORBIDDEN from Gemini. Pipeline executor Phases 1-5, may lead iterations.

## Current Iteration: v9.52

Read in order: (1) This file, (2) docs/kjtcom-design-v9.52.md, (3) docs/kjtcom-plan-v9.52.md, (4) docs/evaluator-harness.md (400+ lines).

---

## Agent Session Best Practices (PERMANENT)

### Pre-Launch
1. CLAUDE.md + GEMINI.md saved. wc -l both >= 200. Harnesses GROW.
2. Evaluator harness: wc -l docs/evaluator-harness.md >= 400 (v9.52+).
3. /quit between iterations. ONE per session.
4. set -gx IAO_ITERATION v9.XX. Ollama (4 models). Restart bot systemd. Verify SA.
5. Archive integrity. Clean drafts. Clean orphaned changelogs. jsonschema installed.

### Session Discipline
- Post-flight (with MCP checks v9.52+) -> evaluation -> artifacts -> promotion.
- NEVER delete docs. Archive to docs/archive/.
- Harness files grow. Never abbreviate.
- Allow time for complex iterations. No rushing.

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

1. Execute workstreams -> 2. post_flight.py (with MCP checks) -> 3. run_evaluator.py (reads design doc + event log, NOT build log) -> 4. generate_artifacts.py -> 5. --validate-only -> 6. --promote

---

## Qwen Evaluator Harness (v9.52+ - COMPREHENSIVE)

docs/evaluator-harness.md is now 400+ lines containing:
- ADR (5 architectural decisions with context/decision/rationale)
- Failure Pattern Catalog (11 documented patterns from v9.41-v9.51)
- Score calibration with real examples
- Evidence quality standards (good/bad examples)
- MCP usage guide (when each is actually invoked)
- Agent attribution (executor vs evaluator)
- Trident computation with worked example
- Complete report and build log templates
- Comprehensive banned phrase list
- Workstream fidelity with examples
- Each iteration adds to ADR and failure catalog (living document)

Schema enforcement: data/eval_schema.json + validation + retry (max 3). Score 0-9 reported as X/10. MCPs: only used ones. Agents: executor not evaluator.

---

## Post-Flight (v9.43+, enhanced v9.52+)

post_flight.py checks: site 200, bot /status, bot /ask >= 6,181, architecture.html, claw3d.html.
v9.52+: MCP verification (all 5 servers), LLM verification (all 4 Ollama models + Gemini Flash).

---

## Rules That Never Change

Git WRITE forbidden. firebase deploy allowed. Never ask permission. Self-heal 3x.
Fish shell. pip --break-system-packages. python3 -u. No em-dashes. NEVER delete docs.

---

## Token Efficiency (v9.40+)

<50K. ollama_config.py (think:false, G51). GEMINI_MODEL constant. iao_logger.py.

---

## README Cadence (v9.46+)

Every iteration: changelog + version. Every 3: full overhaul. Next: v9.55.

---

## Agent-Agnostic (v9.49+)

Artifacts work for either agent. Launch: "Read [CLAUDE/GEMINI].md and execute."

---

## Multi-Agent (v9.35+)

Min 2 LLMs per iteration. Engage more agents/MCPs/LLMs as Phase 10 approaches.

| Agent | Engine | Use For |
|-------|--------|---------|
| Claude Code | Claude API | Primary executor |
| Gemini CLI | Gemini API | Pipeline, may lead iterations |
| Qwen3.5-9B | Ollama local | Evaluation (schema-validated, 400+ line harness) |
| Nemotron Mini 4B | Ollama local | Fast triage |
| GLM-4.6V-Flash | Ollama local | Vision |
| nomic-embed-text | Ollama local | Embeddings only |
| Gemini Flash | Gemini API (litellm) | Intent routing, synthesis |

## MCPs (5 - ONLY valid)

Firebase, Context7, Firecrawl, Playwright, Dart. No others.

---

## Middleware as Primary IP (v9.42+)

Middleware is the product. 33+ components. Components: harnesses (CLAUDE.md 200+, GEMINI.md 200+, evaluator-harness.md 400+), eval (run_evaluator.py, eval_schema.json, agent_scores.json, test_eval_schema.py), harness registry (middleware_registry.json), RAG (embed_archive.py, query_rag.py, ChromaDB ~1,700 chunks), intent router (3 routes), Firestore query (G34, Python sort), county enrichment, event logging (iao_logger.py), artifact generator (single changelog, render_build_markdown, --promote, --validate-only), gotcha archive (18+), bot (systemd, session memory, rating sort, 3-route), config (ollama_config.py: GEMINI_MODEL, batch 45-min), post-flight (MCP checks v9.52+), cleanup_docs.py, architecture HTML, Claw3D (solar system v9.52), MW tab (mw_tab.dart), pipeline review.

---

## Claw3D Solar System (v9.52)

Qwen=sun, agents/LLMs/MCPs=inner planets, middleware/frontend/backend/pipeline=gas giants with component moons. Iteration dropdown toggles active (full color) vs inactive (wireframe). Data from data/claw3d_iterations.json.

---

## Artifact Discipline (v9.42+)

design + plan + build (POST-FLIGHT + SYSTEMS CHECK) + report (Evidence, X/10, What Could Be Better) + CLAUDE.md + GEMINI.md (200+) + changelog APPENDED.

---

## Dependency Protocol (v9.45+)

ONE major at a time. 10 transitive deps locked upstream.

---

## Cross-Pipeline Enrichment (v9.42+)

Audit all pipelines when enriching one. TripleDB counties 918/1100.

---

## Bot (v9.41-v9.44)

3-route (firestore/chromadb/web). Session memory (10-min TTL). Rating sort (Python-side). systemd (WatchdogSec=600). /ask, /status, /search, /help, /start, /scores, /gotcha, /evaluate, /query.

---

## Qwen Harness Development History

v9.41: workstream scoring. v9.42: middleware IP, gotcha archive. v9.43: post-flight, evidence. v9.44: GEMINI_MODEL. v9.45: dep protocol, Phase 10 audit. v9.46: evaluator-harness.md (84 lines). v9.47: workstream fidelity. v9.48: file management, growth enforcement. v9.49: JSON schema, validation loop. v9.50: MCP/agent/summary fixes. v9.51: score X/10, build markdown, LLM names. v9.52: harness rebuild 400+ lines with ADR + failure catalog.

---

## Phase Context

Phase 9 (v9.27-v9.52): App Optimization. Qwen harness must be reliable before Phase 10.
Phase 10: Bourdain (114 videos), IaC to GCP, middleware stamp. Begins after harness is trustworthy.

---

## Phase 9 Summary (v9.27-v9.52, 26 iterations)

6 tabs + MW tab, NoSQL query, multi-agent (4 LLMs, 5 MCPs), middleware (33+ components), Telegram bot (3-route, session memory, rating sort, systemd), county enrichment (918/1100), schema-validated evaluator (400+ line harness), artifact automation, gotcha archive (18+), 3D solar system visualization, architecture HTML.

---

## Companion Projects

TachTech Intranet (ttintra.net), socalpha1 (production SIEM), TripleDB (tripledb.net, 805 videos, IAO origin).

---

## Environment

NZXTcos: i9-13900K, 64GB, RTX 2080 SUPER, CachyOS, fish | ~/dev/projects/kjtcom
Firebase: kjtcom-c78cd | SA: ~/.config/gcloud/kjtcom-sa.json | Flutter: 3.41.6
Bot: systemd | set -gx IAO_ITERATION v9.52

---

## Active Gotchas

G1 (heredocs), G19 (Gemini bash), G34 (array-contains), G43 (CORS), G47 (CanvasKit), G53 (Firebase MCP reauth), G54 (transitive deps).

---

## Key Files

docs/evaluator-harness.md (400+ lines), data/eval_schema.json, data/claw3d_iterations.json (NEW v9.52), scripts/run_evaluator.py, scripts/generate_artifacts.py, scripts/test_eval_schema.py, scripts/cleanup_docs.py, scripts/post_flight.py (MCP checks), scripts/telegram_bot.py, scripts/intent_router.py, scripts/firestore_query.py, scripts/build_architecture_html.py, scripts/utils/ollama_config.py, data/schema_reference.json, data/gotcha_archive.json, data/middleware_registry.json, app/web/architecture.html, app/web/claw3d.html (solar system), app/lib/widgets/mw_tab.dart, docs/pipeline-review-v9.47.md

---

## File Inventory (36+ middleware components)

### Harnesses (3): CLAUDE.md, GEMINI.md, evaluator-harness.md
### Scripts (19): run_evaluator, generate_artifacts, cleanup_docs, telegram_bot, intent_router, firestore_query, post_flight, build_architecture_html, enrich_counties, embed_archive, query_rag, brave_search, build_registry_v2, analyze_events, generate_leaderboard, test_eval_schema, phase1-7 pipeline scripts
### Utilities (3): iao_logger, ollama_config, ollama_logged
### Data (7): eval_schema, schema_reference, gotcha_archive, middleware_registry, chromadb/, iao_event_log, agent_scores, claw3d_iterations
### Templates (3): build-template, report-template, changelog-template
### Web (2): architecture.html, claw3d.html
### Services (1): kjtcom-telegram-bot.service
