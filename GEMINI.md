# kjtcom - Gemini CLI Agent Instructions

## Current Iteration: v10.54

Agent-agnostic. G19: wrap fish in fish -c. firebase deploy FORBIDDEN from Gemini. Pipeline executor Phases 1-5.

Read in order: (1) This file, (2) docs/kjtcom-design-v10.54.md, (3) docs/kjtcom-plan-v10.54.md, (4) docs/evaluator-harness.md (target 400+ lines).

---

## PHASE 10 CONTEXT

Phase 9 complete (v9.27-v9.53, 27 iterations). Phase 10: IAO Retrospective, Pipeline Template, Bourdain Prep.
v10.54: Claw3D static rebuild + Phase 9 retrospective + harness regression fix.
~v10.57: Bourdain pipeline dry run (114 videos). Kyle provides playlist URL.
~v10.59: IaC packaging for GCP (tachnet-intranet).

---

## Agent Session Best Practices (PERMANENT)

1. CLAUDE.md + GEMINI.md saved. wc -l both >= 200. Evaluator harness >= 400.
2. /quit between iterations. ONE per session.
3. set -gx IAO_ITERATION v10.XX. Ollama (4 models). Restart bot. Verify SA.
4. Archive integrity. Clean drafts. Clean orphaned changelogs. jsonschema installed.
5. Post-flight (MCP checks) -> evaluation -> artifacts -> promotion.
6. NEVER delete docs. Archive to docs/archive/. Harness files grow.

---

## File Management (v9.48+)

docs/: current + living docs. docs/archive/: prior (one copy). docs/drafts/: ephemeral.
Single changelog. NEVER delete docs. NEVER rm docs/kjtcom-*.md.

---

## Execution Order (v9.49+)

Execute -> post_flight.py -> run_evaluator.py (NOT build log) -> generate_artifacts.py -> validate -> promote.

---

## Qwen Evaluator (v9.52+ - 528 lines target)

docs/evaluator-harness.md: 9 ADRs, 15+ failure patterns, score calibration, evidence standards, MCP guide, agent attribution, Trident computation, templates, banned phrases, workstream fidelity.
Schema: data/eval_schema.json. Validation + retry (max 3) with field-path errors (v9.53).
Score 0-9 as X/10. MCPs: only used. Agents: executor not evaluator.
CRITICAL: verify line count each iteration. If shrank, restore from git.

---

## Post-Flight (v9.43+, MCP checks v9.52+)

post_flight.py: site 200, bot /status, /ask >= 6,181, architecture.html, claw3d.html, 5 MCP checks.

---

## Rules That Never Change

Git WRITE forbidden. firebase deploy allowed. Never ask permission. Self-heal 3x.
Fish shell. pip --break-system-packages. python3 -u. No em-dashes. NEVER delete docs.

---

## Token Efficiency (v9.40+)

<50K. ollama_config.py (think:false, G51). GEMINI_MODEL. iao_logger.py.

---

## Agent-Agnostic (v9.49+). Launch: "Read [CLAUDE/GEMINI].md and execute."

---

## Multi-Agent (v9.35+)

Claude Code, Gemini CLI, Qwen3.5-9B (evaluator), Nemotron Mini 4B, GLM-4.6V-Flash, nomic-embed-text, Gemini Flash. MCPs: Firebase, Context7, Firecrawl, Playwright, Dart.

---

## Middleware as Primary IP (33+ components)

Harnesses (CLAUDE 200+, GEMINI 200+, evaluator 400+), eval (run_evaluator, eval_schema, agent_scores, test_eval_schema), registry (middleware_registry), RAG (embed_archive, query_rag, ChromaDB ~1,819 chunks), intent router (3 routes), Firestore query (G34, Python sort), county enrichment, event logging, artifact generator (single changelog, render markdown), gotcha archive (18+), bot (systemd, session memory, rating sort, 3-route), config (ollama_config: GEMINI_MODEL, batch 45-min), post-flight (MCP checks), cleanup_docs, architecture HTML, Claw3D (static solar system v10.54), MW tab, pipeline review.

---

## Claw3D Solar System (v10.54 - STATIC REBUILD)

Zero animation on objects. Static elliptical disc layout. OrbitControls camera (drag/scroll).
46 nodes: 1 sun (Qwen) + 5 inner (agents) + 5 asteroids (MCPs) + 4 gas giants + 31 moons.
Active: solid color + animated connectors. Inactive: outline only + static connectors.
Hover tooltip: name, type, function, status, file path.
Iteration dropdown toggles active/inactive state per historical iteration.
Moons grouped sun-facing side of their parent planet.

---

## Artifact Discipline (v9.42+)

design + plan + build (POST-FLIGHT) + report (Evidence, X/10, What Could Be Better) + CLAUDE.md + GEMINI.md (200+) + changelog APPENDED.

---

## README Cadence (v9.46+)

Every iteration: changelog + version. Every 3: full overhaul. Next: v10.55.

---

## Amendment History

v9.40-v9.53: see CLAUDE.md v9.53 for complete list. Key: token efficiency, workstream scoring, post-flight, schema validation, file management, harness growth, single changelog, execution order, agent-agnostic, MCP/agent attribution fixes, score X/10, build markdown rendering.

---

## Phase 9 Summary (v9.27-v9.53, 27 iterations)

7 tabs (Results, Map, Globe, IAO, MW, Schema + search), 6,181 entities, 3 pipelines, multi-agent (4 LLMs, 5 MCPs), 33+ middleware components, Telegram bot (3-route, session memory, rating sort, systemd), schema-validated evaluator (528-line harness, 9 ADRs, 15 failure patterns), county enrichment (918/1100), 3D solar system visualization, architecture HTML.

---

## Companion Projects

TachTech Intranet (ttintra.net): GCP tachnet-intranet, Okta SSO planned, intranet-update-v2.7.md produced.
socalpha1: production SIEM, Pub/Sub -> 4 agents -> SOAR.
TripleDB (tripledb.net): 805 DDD videos, 1,100 restaurants, IAO origin (48+ iterations).

---

## Environment

NZXTcos: i9-13900K, 64GB, RTX 2080 SUPER, CachyOS, fish | ~/dev/projects/kjtcom
Firebase: kjtcom-c78cd | SA: ~/.config/gcloud/kjtcom-sa.json | Flutter: 3.41.6
Bot: systemd kjtcom-telegram-bot.service | set -gx IAO_ITERATION v10.54

---

## Active Gotchas

G1 (heredocs), G19 (Gemini bash), G34 (array-contains), G43 (CORS), G47 (CanvasKit), G53 (Firebase MCP reauth), G54 (transitive deps).

---

## Key Files

docs/evaluator-harness.md (400+), docs/phase9-retrospective.md (NEW v10.54), data/eval_schema.json, data/claw3d_iterations.json, scripts/run_evaluator.py, scripts/generate_artifacts.py, scripts/post_flight.py, scripts/telegram_bot.py, scripts/intent_router.py, scripts/firestore_query.py, scripts/build_architecture_html.py, scripts/utils/ollama_config.py, data/middleware_registry.json, data/gotcha_archive.json, app/web/claw3d.html (static solar system), app/web/architecture.html, app/lib/widgets/mw_tab.dart

---

*GEMINI.md v10.54. Phase 10 begins.*

---

## Bourdain Pipeline Prep (v10.57 target)

- 114 YouTube videos (Anthony Bourdain: Parts Unknown, No Reservations)
- Full 7-phase: acquire -> transcribe -> extract -> normalize -> geocode -> enrich -> load
- New t_log_type: "bourdain"
- Extraction prompt template needed (Bourdain-specific - different format from DDD/CalGold/RickSteves)
- Estimated: 500-1,500 entities across 60+ countries
- Runtime estimate: 8-12 hours total across 7 phases
- Pipeline review: docs/pipeline-review-v9.47.md
- Kyle provides playlist URL when ready

---

## Qwen Harness Development History

v9.41: workstream scoring. v9.42: middleware IP, gotcha archive. v9.43: post-flight, evidence. v9.44: GEMINI_MODEL. v9.45: dep protocol. v9.46: harness file (84 lines). v9.47: fidelity. v9.48: structural enforcement. v9.49: JSON schema. v9.50: MCP/agent fixes. v9.51: X/10 scale. v9.52: 528-line rebuild (9 ADRs, 15 patterns). v9.53: retry specificity. v10.54: regression check.

---

## Cross-Pipeline Schema Enrichment (v9.42+)

Audit all pipelines when enriching one. TripleDB counties enriched v9.42 (918/1100). When Bourdain pipeline loads, all existing schema patterns apply. New fields may require backfill across CalGold/RickSteves/TripleDB.

---

## Bot Features (v9.41-v9.44)

3-route intent router (firestore/chromadb/web). Session memory (10-min TTL). Rating sort (Python-side). systemd managed (WatchdogSec=600). Commands: /ask, /status, /search, /help, /start, /scores, /gotcha, /evaluate, /query. Public access: https://t.me/kjtcom_iao_bot

---

## Dependency Protocol (v9.45+)

ONE major at a time. 10 transitive deps locked by upstream (flutter_map, SDK). Not actionable.

---

## File Inventory (36+ middleware components)

### Harnesses (3): CLAUDE.md, GEMINI.md, evaluator-harness.md
### Scripts (19): run_evaluator, generate_artifacts, cleanup_docs, telegram_bot, intent_router, firestore_query, post_flight, build_architecture_html, enrich_counties, embed_archive, query_rag, brave_search, build_registry_v2, analyze_events, generate_leaderboard, test_eval_schema, phase1-7
### Utilities (3): iao_logger, ollama_config, ollama_logged
### Data (8): eval_schema, schema_reference, gotcha_archive, middleware_registry, chromadb/, iao_event_log, agent_scores, claw3d_iterations
### Templates (3): build-template, report-template, changelog-template
### Web (2): architecture.html, claw3d.html
### Services (1): kjtcom-telegram-bot.service
### Docs (3): pipeline-review-v9.47, phase9-retrospective (NEW v10.54), evaluator-harness

---
*GEMINI.md v10.54 - Phase 10 kickoff. 200+ lines.*
