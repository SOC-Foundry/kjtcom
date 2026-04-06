# kjtcom - Gemini CLI Agent Instructions

## Current Iteration: v9.47 (YOU ARE THE PRIMARY EXECUTOR)

IMPORTANT: Read documents in this EXACT order before executing:

1. This file (GEMINI.md) - you are the lead agent this iteration
2. docs/kjtcom-design-v9.47.md - Workstreams, architecture, amendments
3. docs/kjtcom-plan-v9.47.md - Step-by-step execution

Do NOT begin execution until files 1-3 have been read.

---

## Your Role This Iteration

You are the PRIMARY executor for v9.47. Claude Code has run 6 consecutive iterations (v9.41-v9.46). This is a fresh-perspective iteration AND a validation test: if this harness file is written well enough, you should execute without context loss. If you struggle, the harness needs more detail.

---

## Agent Session Best Practices (PERMANENT)

1. GEMINI.md saved to launch directory BEFORE starting. ONE iteration per session.
2. `set -gx IAO_ITERATION v9.47` BEFORE launching.
3. Verify Ollama: `ollama list` shows 4 models.
4. Verify archive: `ls docs/archive/ | wc -l` (>= 179).
5. **NEVER delete docs. Archive: mv docs/kjtcom-*-v{X}.md docs/archive/**
6. Every session ends: artifacts -> post-flight -> promotion.
7. Harness files GROW. Never abbreviate.

---

## Project Overview

kjtcom is a location intelligence platform at kylejeromethompson.com. 6,181 entities across 3 pipelines (CalGold 899, RickSteves 4,182, TripleDB 1,100). Flutter Web frontend, Firebase/Firestore backend, Python pipeline scripts. Thompson Schema (t_any_* fields) paralleling Panther SIEM p_any_*.

But kjtcom is really an IAO methodology lab. The middleware is the product that stamps onto TachTech Intranet (ttintra.net) and production customer deployments.

---

## Rules That Never Change

- Git READ commands ALLOWED (pull, log, status, diff, show)
- Git WRITE commands FORBIDDEN (add, commit, push, checkout, branch, tag)
- firebase deploy FORBIDDEN - Kyle deploys manually
- flutter build web and flutter run ARE ALLOWED for testing
- NEVER ask permission. The plan IS the permission.
- Self-heal errors: diagnose -> fix -> re-run (max 3 attempts, then log as gotcha)
- Fish shell throughout. pip --break-system-packages. python3 -u.
- No em-dashes. " - " for dashes. "->" for arrows.
- "pipelines" and "log types," never "tables" or "datasets."
- Build on existing code. Read files before overwriting.
- **NEVER run rm or git rm on docs/kjtcom-*.md. Archive to docs/archive/.**

---

## Qwen Evaluator Harness (v9.46+)

Qwen's rules live in docs/evaluator-harness.md. Loaded by run_evaluator.py and generate_artifacts.py. Key rules:
- Never 10/10. Max 9/10.
- Evidence required for every score.
- 2 improvements per workstream, even successful ones.
- No corporate fluff. Banned phrases enforced.
- Trident: actual values, never "Review..." or "TBD."
- "What Could Be Better" section with >= 3 items.
- **Workstream fidelity: EXACT W# list from design doc. No adding, renaming, or reordering. If design doc has 4 workstreams, scorecard has 4 rows. (v9.47 fix)**
- **Evidence cross-check: if changelog says a file was created, trust changelog over file existence queries. (v9.47 fix)**

---

## Post-Flight Verification (MANDATORY)

Run scripts/post_flight.py before ending. Checks: site HTTP 200, bot /status, bot /ask >= 6,181, architecture.html loads. Additionally verify claw3d.html loads after W3.

---

## Token Efficiency (v9.40+)

ALL Ollama calls use scripts/utils/ollama_config.py (think:false mandatory, G51). num_predict: 512 default, 2048 evaluations. Gemini Flash: use GEMINI_MODEL from ollama_config.py. Log via iao_logger.py.

---

## Middleware as Primary IP

Components: harnesses (CLAUDE.md, GEMINI.md, evaluator-harness.md), harness registry (middleware_registry.json), evaluator (run_evaluator.py + workstream scoring + claim audit), RAG (embed_archive.py + query_rag.py + ChromaDB 1,590 chunks), intent router (3 routes: firestore/chromadb/web), Firestore query (G34 workaround, Python sort), county enrichment, event logging (iao_logger.py), artifact generator (--promote/--validate-only), gotcha archive (18 resolved), bot (systemd, session memory, rating sort, 3-route), config (ollama_config.py), post-flight, architecture HTML, Claw3D.

---

## Artifact Discipline

Every iteration produces: design, plan, build (POST-FLIGHT section), report (Evidence column, Trident filled, What Could Be Better), CLAUDE.md, GEMINI.md, changelog (NEW/UPDATED/FIXED, no TBD).

Workflow: generate -> evaluate -> validate -> promote. Never leave unpromoted drafts.

---

## MCP Servers (5 - ONLY valid names)

Firebase, Context7, Firecrawl, Playwright, Dart. Available in .gemini/settings.json: Firebase, Context7.

---

## Multi-Agent

| Agent | Engine | Use For |
|-------|--------|---------|
| Gemini CLI | Gemini API | PRIMARY EXECUTOR this iteration |
| Qwen3.5-9B | Ollama local | Evaluation, scoring |
| nomic-embed-text | Ollama local | Embeddings |
| Claude Code | Claude API | NOT executing this iteration |

---

## Environment

| Fact | Value |
|------|-------|
| Machine | NZXTcos: i9-13900K, 64GB, RTX 2080 SUPER, CachyOS, fish |
| Path | ~/dev/projects/kjtcom |
| Firebase | kjtcom-c78cd |
| SA | ~/.config/gcloud/kjtcom-sa.json |
| Flutter | 3.41.6, Dart 3.11.4 |
| Iteration | set -gx IAO_ITERATION v9.47 |
| Bot | systemd: kjtcom-telegram-bot.service |
| Deploy | cd ~/dev/projects/kjtcom && firebase deploy --only hosting |

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
| G54 | Transitive dep lock (10 Flutter packages) | Documented |

See data/gotcha_archive.json for resolved gotchas.

---

## Key Files

| File | Purpose |
|------|---------|
| docs/evaluator-harness.md | Qwen personality (refine in W1) |
| scripts/run_evaluator.py | Qwen eval (loads harness) |
| scripts/generate_artifacts.py | Artifact drafts (loads harness) |
| scripts/telegram_bot.py | Bot (3-route, session memory, systemd) |
| scripts/intent_router.py | Gemini Flash intent (3 routes) |
| scripts/firestore_query.py | Firestore query (G34, Python sort) |
| scripts/post_flight.py | Post-flight verification |
| scripts/build_architecture_html.py | MMD -> HTML |
| docs/claw3d-prototype/index.html | Claw3D source (deploy in W3) |
| scripts/phase1_acquire.py through phase7_load.py | Pipeline scripts (review in W2) |
| data/schema_reference.json | Schema ref |
| data/gotcha_archive.json | Resolved gotchas |
| data/middleware_registry.json | Middleware catalog |
