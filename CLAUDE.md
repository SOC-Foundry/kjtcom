# kjtcom - Claude Code Agent Instructions

## Current Iteration: v9.46

Read in order: (1) This file, (2) docs/kjtcom-design-v9.46.md, (3) docs/kjtcom-plan-v9.46.md.

---

## Agent Session Best Practices (PERMANENT)

1. CLAUDE.md + GEMINI.md saved to disk BEFORE starting. ONE iteration per session.
2. `set -gx IAO_ITERATION v9.XX`. Verify Ollama (4 models). Restart bot systemd. Verify SA.
3. Verify archive: `ls docs/archive/ | wc -l` (>= prior count).
4. **NEVER delete docs. Archive to docs/archive/.**
5. Harness files GROW. Never abbreviate.
6. Every session ends: artifacts -> post-flight -> promotion. No unpromoted drafts.

---

## Qwen Evaluator Harness (v9.46+ - PERMANENT)

Qwen's evaluation personality and rules live in docs/evaluator-harness.md. This file is loaded by run_evaluator.py and generate_artifacts.py every time Qwen is invoked. Key rules:
- Never 10/10. Max is 9/10 for exceptional work.
- Evidence or it didn't happen. Every score cites a file, output, or test result.
- Name 2 improvements per workstream, even successful ones.
- No corporate fluff. Banned phrases enforced.
- Trident: actual values, never "Review..." or "TBD."
- "What Could Be Better" section mandatory with >= 3 items.
- Contradict when warranted. Evaluator's job is truth.

---

## README Refresh Cadence (v9.46+ - PERMANENT)

- **Every iteration:** update changelog section, version/phase number.
- **Every 3 iterations:** FULL review and overhaul (content accuracy, stale descriptions, link verification, new features documented). Schedule: v9.46, v9.49, v10.52, etc.
- README is the public face. It must reflect current state.

---

## Post-Flight Verification (MANDATORY)

post_flight.py before ending. Site 200, bot /status, bot /ask >= 6,181, architecture.html. For dep upgrades: verify Map tab. If ANY fails: fix first.

---

## Qwen Claim Audit (MANDATORY)

Evidence column. Valid MCPs: Firebase, Context7, Firecrawl, Playwright, Dart. No TBD/Review. Exact W# names. Specific numbers. Now enforced via evaluator harness.

---

## Rules That Never Change

Git WRITE forbidden. firebase deploy allowed. Never ask permission. Self-heal 3x. Fish shell. pip --break-system-packages. python3 -u. No em-dashes. NEVER delete docs.

---

## Dependency Upgrade Protocol (v9.45+)

ONE major version at a time. Read changelog first (Context7 MCP). analyze -> test -> build after each. Document breaking changes. v9.45 finding: 10 transitive deps locked by upstream (flutter_map, SDK). Not actionable.

---

## Token Efficiency (v9.40+)

<50K. ollama_config.py (think:false, G51). GEMINI_MODEL constant. Log via iao_logger.py.

---

## Phase Context

Phase 9 (v9.27-v9.47): App Optimization. Final iterations. Phase 10: Bourdain pipeline (114 videos), IaC to GCP, middleware stamp. Bourdain dry run is 2-3 iterations into Phase 10.

---

## Multi-Agent + MCP

Minimum 2 LLMs. Valid MCPs: Firebase, Context7, Firecrawl, Playwright, Dart. No others.

---

## Middleware as Primary IP

Components: harnesses (CLAUDE.md, GEMINI.md, evaluator-harness.md), harness registry, evaluator, RAG, intent router (3 routes), Firestore query (G34, Python sort), county enrichment, event logging, artifact generator, gotcha archive, bot (systemd, session memory, rating sort, 3-route), config, post-flight, architecture HTML.

---

## Environment

NZXTcos: ~/dev/projects/kjtcom | Firebase: kjtcom-c78cd | SA: ~/.config/gcloud/kjtcom-sa.json | Bot: systemd kjtcom-telegram-bot.service | Flutter: 3.41.6

---

## Active Gotchas

G1 (heredocs), G34 (array-contains), G43 (CORS), G47 (CanvasKit), G53 (Firebase MCP reauth), G54 (transitive dep lock). See data/gotcha_archive.json for resolved.

---

## Key Files

docs/evaluator-harness.md (NEW v9.46), scripts/run_evaluator.py, scripts/generate_artifacts.py, scripts/telegram_bot.py, scripts/intent_router.py, scripts/firestore_query.py, scripts/post_flight.py, scripts/build_architecture_html.py, scripts/utils/ollama_config.py, data/schema_reference.json, data/gotcha_archive.json, data/middleware_registry.json, app/web/architecture.html
