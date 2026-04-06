# kjtcom - Claude Code Agent Instructions

## Current Iteration: v9.53

Read in order: (1) This file, (2) docs/kjtcom-design-v9.53.md, (3) docs/kjtcom-plan-v9.53.md, (4) docs/evaluator-harness.md (528+ lines).


---

## Agent Session Best Practices (PERMANENT)

### Pre-Launch
1. CLAUDE.md + GEMINI.md saved. wc -l both >= 200. Evaluator harness >= 400.
2. /quit between iterations. ONE per session.
3. set -gx IAO_ITERATION v9.XX. Ollama (4 models). Restart bot systemd. Verify SA.
4. Archive integrity. Clean drafts. Clean orphaned changelogs. jsonschema installed.

### Session Discipline
- Post-flight (MCP checks) -> evaluation -> artifacts -> promotion.
- NEVER delete docs. Archive to docs/archive/. Harness files grow.

---

## File Management (v9.48+)

docs/: current + living docs. docs/archive/: prior (one copy). docs/drafts/: ephemeral.
Single changelog. NEVER delete docs.

---

## Execution Order (v9.49+)

Execute -> post_flight.py -> run_evaluator.py (NOT build log) -> generate_artifacts.py -> validate -> promote.

---

## Qwen Evaluator (v9.52+ - 528 lines)

docs/evaluator-harness.md: 9 ADRs, 15 failure patterns, score calibration, evidence standards, MCP guide, agent attribution, Trident computation, report/build templates, banned phrases, workstream fidelity.
Schema: data/eval_schema.json. Validation + retry (max 3) with specific field-path error feedback (v9.53).
Score 0-9 as X/10. MCPs: only used. Agents: executor not evaluator. Summary: plain text.

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

Claude Code, Gemini CLI, Qwen3.5-9B (evaluator 528-line harness), Nemotron Mini 4B, GLM-4.6V-Flash, nomic-embed-text, Gemini Flash (litellm). MCPs: Firebase, Context7, Firecrawl, Playwright, Dart.

---

## Middleware as Primary IP (v9.42+)

33+ components. Harnesses (CLAUDE 200+, GEMINI 200+, evaluator 528+), eval (run_evaluator, eval_schema, agent_scores, test_eval_schema), registry (middleware_registry), RAG (embed_archive, query_rag, ChromaDB ~1,819 chunks), intent router (3 routes), Firestore query (G34, Python sort), county enrichment, event logging, artifact generator (single changelog, render_build_markdown), gotcha archive (18+), bot (systemd, session memory, rating sort, 3-route), config (ollama_config: GEMINI_MODEL, batch 45-min), post-flight (MCP checks), cleanup_docs, architecture HTML, Claw3D (solar system + iteration toggle v9.52), MW tab, pipeline review.

---

## Claw3D Solar System (v9.52, fixes v9.53)

Qwen=sun. Inner: agents/LLMs. Asteroid belt: MCPs. Outer gas giants: middleware/frontend/pipeline/backend with component moons. Iteration dropdown. v9.53 fixes: 75% slower orbits, 40% tighter radii, green connector lines, tidal lock (no axis spin).

---

## Artifact Discipline (v9.42+)

design + plan + build (POST-FLIGHT, SYSTEMS CHECK) + report (Evidence, X/10, What Could Be Better) + CLAUDE.md + GEMINI.md (200+) + changelog APPENDED.

---

## Qwen Harness History

v9.41-v9.45: scoring, evidence, post-flight. v9.46: harness file (84 lines). v9.47: fidelity. v9.48: structural enforcement. v9.49: JSON schema. v9.50: MCP/agent/summary fixes. v9.51: X/10 scale, markdown rendering. v9.52: 528-line rebuild with ADR + 15 failure patterns. v9.53: retry error specificity, final tuning.

---

## Phase Context

Phase 9 (v9.27-v9.53): App Optimization. v9.53 is the FINAL Phase 9 iteration.
Phase 10: Bourdain (114 videos), IaC to GCP, middleware stamp. Begins v10.54.

---

## Companion Projects

TachTech Intranet (ttintra.net), socalpha1 (production SIEM), TripleDB (tripledb.net).

---

## Environment

NZXTcos: i9-13900K, 64GB, RTX 2080 SUPER, CachyOS, fish | ~/dev/projects/kjtcom
Firebase: kjtcom-c78cd | SA: ~/.config/gcloud/kjtcom-sa.json | Flutter: 3.41.6
Bot: systemd | set -gx IAO_ITERATION v9.53

---

## Active Gotchas

G1 (heredocs), G19 (Gemini bash), G34 (array-contains), G43 (CORS), G47 (CanvasKit), G53 (Firebase MCP reauth), G54 (transitive deps).

---

## Key Files

docs/evaluator-harness.md (528+), data/eval_schema.json, data/claw3d_iterations.json, scripts/run_evaluator.py, scripts/generate_artifacts.py, scripts/test_eval_schema.py, scripts/cleanup_docs.py, scripts/post_flight.py (MCP checks), scripts/telegram_bot.py, scripts/intent_router.py, scripts/firestore_query.py, scripts/build_architecture_html.py, scripts/utils/ollama_config.py, data/schema_reference.json, data/gotcha_archive.json, data/middleware_registry.json, app/web/architecture.html, app/web/claw3d.html (solar system), app/lib/widgets/mw_tab.dart

---

## File Inventory (36+ components)

Harnesses (3), Scripts (19), Utilities (3), Data (8), Templates (3), Web (2), Services (1)

---

## Complete Amendment History (carry forward)

- v9.40: Token efficiency (<50K), ollama_config.py (think:false, G51)
- v9.41: Workstream-level evaluator tracking, Gemini Flash intent router, artifact automation
- v9.42: Agent session best practices, middleware as IP, resolved gotcha archive, cross-pipeline enrichment, Qwen 45-min timeout, systemd bot, internet query stream, doc archival enforcement
- v9.43: Post-flight verification mandatory, Qwen claim audit (evidence column), doc archival reinforced
- v9.44: Gemini model centralized (GEMINI_MODEL), Python-side sort (avoid composite indexes), doc archival third reinforcement
- v9.45: Dependency upgrade protocol (one major at a time), Phase 10 readiness audit
- v9.46: Evaluator harness file (evaluator-harness.md), README 3-iteration cadence, skeptical scoring
- v9.47: Workstream fidelity (exact W# from design doc), evidence cross-check, pipeline review, Claw3D deploy
- v9.48: File management rules (absolute), harness growth enforcement (200+ lines), Qwen structural enforcement (parse design doc, validate count), single changelog
- v9.49: JSON schema validation (eval_schema.json), validation + retry loop, execution order corrected (evaluator never reads current build log), agent-agnostic artifacts, MW tab
- v9.50: MCPs = only used (not full enum), agent attribution = executor not evaluator, plain text summary (no JSON), render_report_markdown(), build log rendering
- v9.51: Score X/10 (not X/9), render_build_markdown(), LLM exact names, schema test cases, 3D button
- v9.52: Evaluator harness rebuild (528 lines, 9 ADRs, 15 failure patterns), Claw3D solar system redesign (iteration toggle), Phase 10 systems check (5 MCPs, 5 LLMs), MCP checks in post-flight
- v9.53: Claw3D orbital mechanics (slow, tight, connectors, tidal lock), schema retry field-path errors, final Qwen tuning, Phase 9 close-out

---

## Phase 9 Achievement Summary (v9.27-v9.53, 27 iterations)

### App
- 7 tabs: Results, Map, Globe, IAO, MW (Middleware), Schema + main search
- NoSQL query editor with syntax highlighting, autocomplete, operators
- Gothic/cyber visual identity (Cinzel, Geist, green glow, dark SIEM base)
- 6,181 entities across 3 pipelines (CalGold 899, RickSteves 4,182, TripleDB 1,100)
- MW tab showing 33+ middleware components with gotcha archive

### Middleware (33+ components)
- Schema-validated evaluator with 528-line harness, 9 ADRs, 15 failure patterns
- 3-route intent router (firestore/chromadb/web) via Gemini Flash
- Telegram bot with session memory, rating sort, systemd resilience
- RAG pipeline (1,819 chunks in ChromaDB)
- Artifact automation (generate + evaluate + validate + promote)
- Gotcha archive (18+ resolved patterns)
- Post-flight verification (site, bot, MCPs, LLMs)
- County enrichment (918/1100 TripleDB entities)

### Infrastructure
- Multi-agent: 4 local LLMs (Ollama), 5 MCP servers, Gemini Flash API
- systemd-managed bot with watchdog
- 3D solar system visualization (Claw3D) with iteration history
- Interactive architecture diagram (Mermaid HTML)
- Comprehensive install.fish (450+ lines)

### Documentation
- 27 design docs, 27 plans, 27 build logs, 27 reports in archive
- 528-line evaluator harness with ADR
- Pipeline review (7 phases documented)
- Intranet update (v2.7 cross-project)
- 800+ line README

---

## Bourdain Pipeline Prep (Phase 10)

- 114 YouTube videos (Anthony Bourdain: Parts Unknown, No Reservations)
- Full 7-phase pipeline dry run: acquire -> transcribe -> extract -> normalize -> geocode -> enrich -> load
- Estimated runtime: 8-12 hours total
- Pipeline review: docs/pipeline-review-v9.47.md
- Extraction prompt template needed (Bourdain-specific)
- New t_log_type: "bourdain"
- Expected entity count: 500-1,500 locations across 60+ countries

---

*CLAUDE.md v9.53 - 202 lines. Phase 9 final iteration.*
