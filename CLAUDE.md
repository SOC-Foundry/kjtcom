# kjtcom - Claude Code Agent Instructions

## Current Iteration: v9.42

IMPORTANT: Read documents in this EXACT order before executing:

1. This file (CLAUDE.md)
2. docs/kjtcom-design-v9.42.md - Workstreams, architecture, amendments
3. docs/kjtcom-plan-v9.42.md - Step-by-step execution
4. docs/kjtcom-kt-v9.40.md - Full project context (if available in archive)

Do NOT begin execution until files 1-3 have been read.

---

## Agent Session Best Practices (v9.42+ - PERMANENT)

These are hard-won operational patterns from 41 iterations. Follow them every time.

### Pre-Launch Checklist
1. CLAUDE.md and GEMINI.md MUST be saved to disk in the launch directory BEFORE starting the agent session. If stale or missing, the session runs on wrong context.
2. /quit every session and start fresh between iterations. Token context degrades over long sessions - early tokens carry more weight than late ones. A fresh session with good harness files outperforms a stale session.
3. `set -gx IAO_ITERATION v9.XX` BEFORE launching.
4. Verify Ollama running: `ollama list` should show 4 models.
5. Kill and restart Telegram bot between iterations (or restart systemd service).
6. Verify Firebase SA: `test -f ~/.config/gcloud/kjtcom-sa.json`.

### Session Discipline
- ONE iteration per session. Never chain iterations.
- If session crashes or stalls, /quit and relaunch with same launch prompt. Do not recover mid-session.
- Every session ends with artifact production. No exceptions.
- Drafts in docs/drafts/ MUST be cross-checked against actual execution before promotion.
- Use `--promote` flag on generate_artifacts.py to move validated drafts to docs/.

### Environment Architecture
- GCP SA keys: ~/.config/gcloud/{project}-sa.json (NEVER in repo, NEVER in env vars as plaintext)
- API keys: fish shell config, per-project prefixed (KJTCOM_*, TACHNET_*)
- Agent launches: `claude --dangerously-skip-permissions` / `gemini --yolo`
- Persistent processes: tmux (legacy) or systemd services (v9.42+)
- Sleep mask: `systemctl mask suspend` on dev machines

### Token Efficiency
- Harness files (CLAUDE.md, GEMINI.md) should GROW over time. Never abbreviate.
- The depth and specificity of these files is the primary competitive advantage of IAO.
- Middleware is the IP. Every iteration should add to it.

---

## Rules That Never Change

- Git WRITE commands FORBIDDEN (add, commit, push, checkout, branch, tag). Kyle handles ALL git.
- firebase deploy is ALLOWED (hosting only). Kyle may also deploy manually.
- NEVER ask permission. The plan IS the permission.
- Self-heal errors: diagnose -> fix -> re-run (max 3 attempts, then log as gotcha and skip).
- Fish shell throughout. pip --break-system-packages. python3 -u for unbuffered output.
- No em-dashes anywhere. Use " - " for dashes. Use "->" for arrows.
- "pipelines" and "log types," never "tables" or "datasets."
- Build on existing code. Do NOT recreate scaffolds or overwrite working files without reading them first.

---

## Token Efficiency Mandate (v9.40+)

- Target: <50K Claude Code tokens per infrastructure iteration
- ALL Ollama calls use scripts/utils/ollama_config.py (think:false mandatory, G51)
- num_predict: 512 default, 2048 for evaluations, 2048 with 45-min timeout for batch ops (v9.42+)
- Prefer direct file reads over LLM interpretation for structured data
- Prefer local LLM (Qwen, Nemotron) for simple tasks
- Log all token usage via scripts/utils/iao_logger.py

---

## Multi-Agent Orchestration (v9.35+)

- Minimum 2 LLMs per iteration
- Document which agents/LLMs/MCPs were used per workstream (v9.41+)
- Agent evaluator: Qwen3.5-9B is permanent evaluator via scripts/run_evaluator.py
- Agent scores with workstream-level detail appended to agent_scores.json
- Evaluator MUST cross-check workstream outcomes against actual execution (exit codes, file existence) before scoring (v9.42+ fix)

Available agents:
| Agent | Engine | Use For |
|-------|--------|---------|
| Claude Code | Claude API (this agent) | Primary executor, Flutter, architecture |
| Qwen3.5-9B | Ollama local | Evaluation, code review, simple triage |
| Nemotron Mini 4B | Ollama local | Fast triage |
| GLM-4.6V-Flash | Ollama local | Vision, screenshots |
| nomic-embed-text | Ollama local | Embeddings only |
| Gemini Flash | Gemini API (litellm) | Intent routing, synthesis, OpenClaw |

---

## MCP Servers (v9.35+)

5 servers in .mcp.json:
| Server | Use For |
|--------|---------|
| Firebase MCP | Firestore queries |
| Context7 MCP | API documentation lookup |
| Firecrawl MCP | Web scraping |
| Playwright MCP | Browser automation (G47: CanvasKit blocks DOM) |
| Dart MCP | Code analysis |

Use applicable servers. Document skips with rationale.

---

## Middleware as Primary IP (v9.42+)

The middleware layer is the primary intellectual property. kjtcom is the lab; middleware stamps onto intranet, socalpha1, and customer deployments. Every iteration should ask: "what did we add to the middleware that makes the next project easier?"

Middleware components:
- **Harnesses:** CLAUDE.md, GEMINI.md (grow, never shrink)
- **Harness Registry:** data/middleware_registry.json
- **Evaluator:** run_evaluator.py, agent_scores.json
- **RAG:** embed_archive.py, query_rag.py, ChromaDB
- **Intent Router:** intent_router.py, schema_reference.json (3 routes: firestore, chromadb, web)
- **Firestore Query:** firestore_query.py
- **County Enrichment:** enrich_counties.py (cross-pipeline schema enrichment)
- **Event Logging:** iao_logger.py, iao_event_log.jsonl, analyze_events.py
- **Artifact Generator:** generate_artifacts.py, template/artifacts/ (with --promote, --validate-only)
- **Gotcha Archive:** data/gotcha_archive.json (resolved gotchas with resolution patterns)
- **Bot:** telegram_bot.py (systemd managed, 3-route retrieval: firestore, chromadb, web)
- **Config:** ollama_config.py (defaults, batch defaults with 45-min timeout), ollama_logged.py

---

## P3 Diligence Event Logging (v9.39+)

- ALL scripts use scripts/utils/iao_logger.py
- ALL Telegram bot messages logged (inbound + outbound)
- ALL Ollama calls logged via scripts/utils/ollama_logged.py
- Event types: llm_call, api_call, agent_msg, command
- Events written to data/iao_event_log.jsonl
- Report includes Event Log Summary section

---

## Workstream-Level Tracking (v9.41+)

- Qwen evaluator scores EACH workstream (W#) individually
- Per workstream: outcome, agents, LLMs, MCPs, score (0-10), notes
- Cross-check outcomes against exit codes and file existence BEFORE scoring (v9.42+ fix)
- Workstreams array appended to agent_scores.json
- Report MUST include Workstream Scorecard table

---

## Artifact Discipline (v9.42+)

Every iteration produces:
- kjtcom-design-v{X}.md (pre-staged from claude.ai)
- kjtcom-plan-v{X}.md (pre-staged from claude.ai)
- kjtcom-build-v{X}.md (generated, cross-checked, promoted)
- kjtcom-report-v{X}.md (with Workstream Scorecard, cross-checked, promoted)
- Updated CLAUDE.md + GEMINI.md
- Changelog entry

Post-execution workflow:
1. generate_artifacts.py -> drafts to docs/drafts/
2. run_evaluator.py --workstreams -> workstream scoring
3. generate_artifacts.py --validate-only -> cross-check Qwen accuracy
4. generate_artifacts.py --promote -> move validated drafts to docs/
5. Verify docs/ has all 4 artifacts + updated changelog

Drafts NEVER sit in docs/drafts/ unpromoted at end of session.

---

## Resolved Gotcha Archive (v9.42+)

Resolved gotchas stored in data/gotcha_archive.json with resolution patterns. Evaluator queries this archive. When resolving a new gotcha, ALWAYS add it to the archive with: ID, description, resolution, iteration_resolved, root_cause category, prevention pattern.

Root cause categories: environment, llm_config, dependency, firestore, flutter, pipeline, mcp, security, timeout

---

## Cross-Pipeline Schema Enrichment (v9.42+)

When a field is enriched on one pipeline, ALL pipelines must be audited for the same enrichment. Schema gaps must be logged and addressed. data/schema_reference.json flags per-pipeline field coverage.

---

## Living Documents (v9.38+)

Update every iteration that changes them:
- docs/install.fish
- docs/kjtcom-architecture.mmd
- docs/kjtcom-changelog.md
- data/middleware_registry.json (if middleware changes)
- data/gotcha_archive.json (if gotchas resolved)

---

## Environment

| Fact | Value |
|------|-------|
| Machine | NZXTcos: i9-13900K, 64GB RAM, RTX 2080 SUPER, CachyOS, fish shell |
| Path | ~/dev/projects/kjtcom |
| Firebase | kjtcom-c78cd |
| SA | ~/.config/gcloud/kjtcom-sa.json |
| Flutter SDK | 3.41.6, Dart 3.11.4 |
| Iteration Env | set -gx IAO_ITERATION v9.42 |
| Telegram Bot | systemd: kjtcom-telegram-bot.service (v9.42+) |
| Bot Env | /home/kyle/.config/kjtcom/bot.env |

---

## Active Gotchas

| ID | Description | Status |
|----|-------------|--------|
| G1 | Heredocs in fish - use printf | ACTIVE |
| G34 | Single array-contains per Firestore query | ACTIVE - post-filter workaround |
| G43 | Map tile CORS | ACTIVE |
| G44 | flutter_map compat | ACTIVE |
| G47 | CanvasKit blocks Playwright DOM interaction | Open |
| G53 | Firebase MCP reauth per session | Recurring |

See data/gotcha_archive.json for all resolved gotchas and their resolution patterns.

---

## Key Files

| File | Purpose |
|------|---------|
| scripts/telegram_bot.py | Bot (3-route retrieval: firestore, chromadb, web; systemd managed) |
| scripts/intent_router.py | Gemini Flash intent classification (3 routes) |
| scripts/firestore_query.py | Firestore query execution with G34 workaround |
| scripts/enrich_counties.py | Cross-pipeline county enrichment (NEW v9.42) |
| scripts/generate_artifacts.py | Artifact drafts with --promote and --validate-only |
| scripts/run_evaluator.py | Qwen evaluation with workstream scoring + cross-check |
| scripts/query_rag.py | ChromaDB semantic search |
| scripts/embed_archive.py | Archive -> ChromaDB embedder |
| scripts/brave_search.py | Brave Search API wrapper |
| scripts/build_registry_v2.py | RAG-augmented registry builder (45-min timeout) |
| scripts/utils/iao_logger.py | Event logger |
| scripts/utils/ollama_config.py | Ollama defaults + batch defaults (45-min timeout) |
| scripts/utils/ollama_logged.py | Auto-logging Ollama wrapper |
| data/schema_reference.json | Thompson Schema reference for intent router |
| data/gotcha_archive.json | Resolved gotchas with resolution patterns (NEW v9.42) |
| data/middleware_registry.json | Middleware component catalog (NEW v9.42) |
| data/chromadb/ | RAG vector store (1,419 chunks) |
| data/iao_event_log.jsonl | P3 Diligence event stream |
| agent_scores.json | Agent + workstream scoring |
| template/artifacts/ | Build, report, changelog templates |
| kjtcom-telegram-bot.service | systemd unit file (NEW v9.42) |
| docs/cross-project/ | Cross-project update artifacts |
