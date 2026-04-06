# kjtcom - Claude Code Agent Instructions

## Current Iteration: v9.49

IMPORTANT: Read documents in this EXACT order before executing:

1. This file (CLAUDE.md)
2. docs/kjtcom-design-v9.49.md - Workstreams, architecture, amendments
3. docs/kjtcom-plan-v9.49.md - Step-by-step execution
4. docs/evaluator-harness.md - Qwen's evaluation personality

Do NOT begin execution until files 1-3 have been read.

---

## Agent Session Best Practices (v9.42+ - PERMANENT)

### Pre-Launch Checklist
1. CLAUDE.md and GEMINI.md MUST be saved to disk in the launch directory BEFORE starting.
2. Verify harness line counts: wc -l CLAUDE.md GEMINI.md - both >= 200. Harnesses grow, never shrink.
3. /quit every session and start fresh. ONE iteration per session. Token context degrades.
4. set -gx IAO_ITERATION v9.XX BEFORE launching.
5. Verify Ollama: ollama list shows 4 models.
6. Restart bot: sudo systemctl restart kjtcom-telegram-bot
7. Verify Firebase SA: test -f ~/.config/gcloud/kjtcom-sa.json
8. Verify archive: ls docs/archive/ | wc -l (>= prior count).
9. Clean drafts: rm -f docs/drafts/*.md
10. Clean orphaned changelogs: rm -f docs/changelog-v*.md
11. Verify jsonschema installed: python3 -c "import jsonschema" (v9.49+)

### Session Discipline
- If session crashes, /quit and relaunch. Do not recover mid-session.
- Every session ends with: post-flight -> evaluation -> artifact generation -> promotion.
- Drafts cross-checked and promoted. NEVER leave unpromoted drafts.
- Harness files GROW. Never abbreviate. The depth is the competitive advantage.

### Environment Architecture
- GCP SA keys: ~/.config/gcloud/{project}-sa.json (NEVER in repo)
- API keys: fish shell config, per-project prefixed (KJTCOM_*)
- Agent launches: claude --dangerously-skip-permissions / gemini --yolo
- Bot: systemd (kjtcom-telegram-bot.service)
- Sleep mask: systemctl mask suspend on dev machines

### CRITICAL: Document Archival
- NEVER run rm or git rm on ANY docs/kjtcom-*.md file.
- Use mv docs/kjtcom-*-v{X}.md docs/archive/ instead.
- Kyle moves current docs to archive after git push.

---

## File Management Rules (v9.48+ - ABSOLUTE)

docs/ holds ONLY: current iteration artifacts + living docs (changelog, architecture.mmd, install.fish, evaluator-harness.md, pipeline-review, eval_schema.json).
docs/archive/ holds: ALL prior iteration artifacts (one copy, no duplicates).
docs/drafts/ is EPHEMERAL: wiped each iteration, empty after promotion.
Single Changelog: ONE file docs/kjtcom-changelog.md. Append to top. Never create changelog-v{X}.md.
NEVER delete docs. Archive to docs/archive/.

---

## Execution Order (v9.49+ - CORRECTED)

The evaluator NEVER reads the current iteration's build log (it doesn't exist yet).

Correct sequence:
1. Execute workstreams (plan Steps 1-N)
2. python3 scripts/post_flight.py (verification)
3. python3 scripts/run_evaluator.py --iteration v9.XX --workstreams
   -> Reads: design doc (workstream list) + event log + file existence
   -> Produces: validated JSON scores in agent_scores.json
4. python3 scripts/generate_artifacts.py
   -> Reads: agent_scores.json + event log + git diff
   -> Produces: build log + report + changelog entry in docs/drafts/
5. python3 scripts/generate_artifacts.py --validate-only
6. python3 scripts/generate_artifacts.py --promote

---

## Qwen Schema-Validated Harness (v9.49+ - ARCHITECTURAL)

All Qwen evaluation calls use strict JSON schema (data/eval_schema.json). Key constraints enforced by schema:
- score max 9 (never 10)
- mcps enum: Firebase, Context7, Firecrawl, Playwright, Dart, "-"
- outcome enum: complete, partial, failed, deferred
- improvements minItems 2 per workstream
- what_could_be_better minItems 3
- delivery pattern "X/Y workstreams"
- evidence minLength 10

Validation + retry loop: on schema violation, Qwen receives specific error feedback and retries (max 3). This replaces prompt-only constraints with structural enforcement.

Research basis: Typia/AutoBe at Qwen Meetup Korea showed schema + validation + feedback loops achieve 99.8% compliance vs. 6.75% for prompt-only.

---

## Post-Flight Verification (v9.43+ - MANDATORY)

After workstreams, BEFORE evaluation:
1. python3 scripts/post_flight.py - all checks pass
2. Site HTTP 200, bot /status, bot /ask >= 6,181, architecture.html, claw3d.html
3. Log results in POST-FLIGHT section of build log
4. If ANY fails: fix, re-deploy, re-verify.

---

## Rules That Never Change

- Git WRITE FORBIDDEN. Kyle handles ALL git.
- firebase deploy ALLOWED (hosting only).
- NEVER ask permission. The plan IS the permission.
- Self-heal errors (3 attempts then gotcha).
- Fish shell. pip --break-system-packages. python3 -u.
- No em-dashes. " - " for dashes. "->" for arrows.
- "pipelines" and "log types." Never "tables" or "datasets."
- Build on existing code. Read before overwriting.
- NEVER delete docs.

---

## Token Efficiency (v9.40+)

<50K tokens. ALL Ollama calls use ollama_config.py (think:false, G51). Gemini Flash: GEMINI_MODEL from ollama_config.py. Log via iao_logger.py.

---

## README Refresh Cadence (v9.46+)

Every iteration: update changelog + version. Every 3 iterations: FULL overhaul.
Schedule: v9.46, v9.49, v10.52, etc. v9.49 is an overhaul iteration.

---

## Dependency Upgrade Protocol (v9.45+)

ONE major version at a time. Context7 MCP for changelogs. analyze -> test -> build after each.
v9.45 finding: 10 transitive deps locked by upstream. Not actionable.

---

## Agent-Agnostic Artifacts (v9.49+)

Design docs and plans work for either Claude Code or Gemini CLI. Both CLAUDE.md and GEMINI.md are comprehensive. Launch prompt: "Read [CLAUDE/GEMINI].md and execute."

---

## Multi-Agent Orchestration (v9.35+)

Minimum 2 LLMs. Document per workstream.

| Agent | Engine | Use For |
|-------|--------|---------|
| Claude Code | Claude API | Primary executor (when leading) |
| Gemini CLI | Gemini API | Pipeline executor, may lead iterations |
| Qwen3.5-9B | Ollama local | Evaluation (schema-validated v9.49+) |
| Nemotron Mini 4B | Ollama local | Fast triage |
| GLM-4.6V-Flash | Ollama local | Vision |
| nomic-embed-text | Ollama local | Embeddings only |
| Gemini Flash | Gemini API (litellm) | Intent routing, synthesis |

---

## MCP Servers (5 - ONLY valid names)

Firebase, Context7, Firecrawl, Playwright, Dart. No others exist.

---

## Middleware as Primary IP (v9.42+)

Middleware is the product. kjtcom is the lab. Components:
- Harnesses: CLAUDE.md, GEMINI.md (200+ lines), evaluator-harness.md
- Evaluation: run_evaluator.py (schema-validated v9.49+), eval_schema.json, agent_scores.json
- Harness Registry: middleware_registry.json
- RAG: embed_archive.py, query_rag.py, ChromaDB (~1,700 chunks)
- Intent Router: intent_router.py (3 routes: firestore/chromadb/web)
- Firestore Query: firestore_query.py (G34 workaround, Python sort)
- County Enrichment: enrich_counties.py
- Event Logging: iao_logger.py, iao_event_log.jsonl, analyze_events.py
- Artifact Generator: generate_artifacts.py (single changelog, --promote, --validate-only)
- Gotcha Archive: gotcha_archive.json (18+ resolved)
- Bot: telegram_bot.py (systemd, session memory, rating sort, 3-route)
- Config: ollama_config.py (defaults, batch 45-min, GEMINI_MODEL)
- Post-Flight: post_flight.py
- Cleanup: cleanup_docs.py
- Architecture: build_architecture_html.py, architecture.html
- Claw3D: claw3d.html
- Pipeline Review: pipeline-review-v9.47.md
- MW Tab: mw_tab.dart (NEW v9.49)

---

## Artifact Discipline (v9.42+)

Every iteration: design, plan, build (POST-FLIGHT section), report (Evidence column, schema-validated scorecard, What Could Be Better), CLAUDE.md, GEMINI.md (both >= 200), changelog APPENDED.

Workflow: execute -> post-flight -> evaluate (schema) -> generate -> validate -> promote.

---

## Phase Context

Phase 9 (v9.27-v9.49+): App Optimization. Qwen harness must be reliable before Phase 10.
Phase 10: Bourdain Pipeline (114 videos), IaC to GCP, middleware stamp. ~v10.51+.

---

## Environment

| Fact | Value |
|------|-------|
| Machine | NZXTcos: i9-13900K, 64GB, RTX 2080 SUPER, CachyOS, fish |
| Path | ~/dev/projects/kjtcom |
| Firebase | kjtcom-c78cd |
| SA | ~/.config/gcloud/kjtcom-sa.json |
| Flutter | 3.41.6, Dart 3.11.4 |
| Iteration | set -gx IAO_ITERATION v9.49 |
| Bot | systemd: kjtcom-telegram-bot.service |
| Deploy | cd ~/dev/projects/kjtcom && firebase deploy --only hosting |

---

## Active Gotchas

G1 (heredocs), G19 (Gemini bash), G34 (array-contains), G43 (CORS), G47 (CanvasKit DOM), G53 (Firebase MCP reauth), G54 (transitive deps). See data/gotcha_archive.json.

---

## Key Files

docs/evaluator-harness.md, data/eval_schema.json (NEW v9.49), scripts/run_evaluator.py (schema-validated), scripts/generate_artifacts.py (corrected order), scripts/cleanup_docs.py, scripts/telegram_bot.py, scripts/intent_router.py, scripts/firestore_query.py, scripts/post_flight.py, scripts/build_architecture_html.py, scripts/enrich_counties.py, scripts/embed_archive.py, scripts/utils/ollama_config.py (GEMINI_MODEL), data/schema_reference.json, data/gotcha_archive.json, data/middleware_registry.json, app/web/architecture.html, app/web/claw3d.html, app/lib/widgets/mw_tab.dart (NEW v9.49), docs/pipeline-review-v9.47.md
