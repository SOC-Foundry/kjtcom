# kjtcom - Claude Code Agent Instructions

## Current Iteration: v9.41

IMPORTANT: Read documents in this EXACT order before executing:

1. This file (CLAUDE.md)
2. docs/kjtcom-design-v9.41.md - Workstreams, architecture, amendments
3. docs/kjtcom-plan-v9.41.md - Step-by-step execution
4. docs/kjtcom-kt-v9.40.md - Full project context (if available in archive)

Do NOT begin execution until files 1-3 have been read.

---

## Rules That Never Change

- Git WRITE commands FORBIDDEN (add, commit, push, checkout, branch, tag). Kyle handles ALL git.
- firebase deploy is ALLOWED (hosting only). Kyle may also deploy manually.
- NEVER ask permission. The plan IS the permission. If you find yourself typing a question mark, STOP. Re-read the plan. Execute.
- Self-heal errors: diagnose -> fix -> re-run (max 3 attempts, then log as gotcha and skip).
- Fish shell throughout. pip --break-system-packages. python3 -u for unbuffered output.
- No em-dashes anywhere. Use " - " for dashes. Use "->" for arrows.
- "pipelines" and "log types," never "tables" or "datasets."
- Build on existing code. Do NOT recreate scaffolds or overwrite working files without reading them first.

---

## Token Efficiency Mandate (v9.40+)

- Target: <50K Claude Code tokens per infrastructure iteration
- ALL Ollama calls use scripts/utils/ollama_config.py (think:false mandatory, G51)
- num_predict: 512 default, 2048 for evaluations
- Prefer direct file reads over LLM interpretation for structured data
- Prefer local LLM (Qwen, Nemotron) for simple tasks over Claude API calls
- Log all token usage via scripts/utils/iao_logger.py

---

## Multi-Agent Orchestration (v9.35+)

- Minimum 2 LLMs per iteration
- Document which agents/LLMs/MCPs were used per workstream (v9.41+ amendment)
- Agent evaluator: Qwen3.5-9B is permanent evaluator via scripts/run_evaluator.py
- Agent scores appended to agent_scores.json with workstream-level detail

Available agents:
| Agent | Engine | Use For |
|-------|--------|---------|
| Claude Code | Claude API (this agent) | Primary executor, Flutter, architecture |
| Qwen3.5-9B | Ollama local | Evaluation, code review, simple triage |
| Nemotron Mini 4B | Ollama local | Fast triage |
| GLM-4.6V-Flash | Ollama local | Vision, screenshots |
| nomic-embed-text | Ollama local | Embeddings only |
| Gemini Flash | Gemini API (litellm) | OpenClaw synthesis, intent routing |

---

## MCP Servers (v9.35+)

5 servers configured in .mcp.json:
| Server | Use For |
|--------|---------|
| Firebase MCP | Firestore queries |
| Context7 MCP | API documentation lookup |
| Firecrawl MCP | Web scraping |
| Playwright MCP | Browser automation (G47: CanvasKit blocks DOM) |
| Dart MCP | Code analysis |

Use applicable servers. Document skips with rationale.

---

## P3 Diligence Event Logging (v9.39+)

- ALL scripts use scripts/utils/iao_logger.py
- ALL Telegram bot messages logged (inbound + outbound)
- ALL Ollama calls logged via scripts/utils/ollama_logged.py
- Event types: llm_call, api_call, agent_msg
- Events written to data/iao_event_log.jsonl
- Report includes Event Log Summary section

---

## Workstream-Level Tracking (v9.41+)

- Qwen evaluator scores EACH workstream (W#) individually
- Per workstream: outcome, agents, LLMs, MCPs, score (0-10), notes
- Workstreams array appended to agent_scores.json
- Report MUST include Workstream Scorecard table

---

## Living Documents (v9.38+)

Update these every iteration that changes them:
- docs/install.fish
- docs/kjtcom-architecture.mmd
- docs/kjtcom-changelog.md (append entry)

---

## Artifact Loop (v9.41+)

Every iteration produces:
- kjtcom-design-v{X}.md (pre-staged from claude.ai)
- kjtcom-plan-v{X}.md (pre-staged from claude.ai)
- kjtcom-build-v{X}.md (generated via generate_artifacts.py, reviewed)
- kjtcom-report-v{X}.md (generated via generate_artifacts.py, reviewed)
- Updated CLAUDE.md + GEMINI.md
- Changelog entry

Post-execution: run scripts/generate_artifacts.py for draft build log + report.
Run scripts/run_evaluator.py for workstream-level scoring.

---

## Environment

| Fact | Value |
|------|-------|
| Machine | NZXTcos: i9-13900K, 64GB RAM, RTX 2080 SUPER, CachyOS, fish shell |
| Path | ~/dev/projects/kjtcom |
| Firebase | kjtcom-c78cd |
| SA | ~/.config/gcloud/kjtcom-sa.json |
| Flutter SDK | 3.41.6, Dart 3.11.4 |
| Iteration Env | set -gx IAO_ITERATION v9.41 |
| Telegram Bot | tmux session "telegram-bot" |

---

## Active Gotchas

| ID | Description | Status |
|----|-------------|--------|
| G34 | Single array-contains per Firestore query | ACTIVE - post-filter workaround |
| G47 | CanvasKit blocks Playwright DOM interaction | Open |
| G53 | Firebase MCP reauth per session | Recurring |

---

## Key Files

| File | Purpose |
|------|---------|
| scripts/telegram_bot.py | Telegram bot (dual retrieval in v9.41) |
| scripts/intent_router.py | Gemini Flash intent classification (NEW v9.41) |
| scripts/firestore_query.py | Firestore query execution (NEW v9.41) |
| scripts/generate_artifacts.py | Post-iteration artifact drafts (NEW v9.41) |
| scripts/query_rag.py | ChromaDB semantic search |
| scripts/embed_archive.py | Archive -> ChromaDB embedder |
| scripts/run_evaluator.py | Qwen evaluation with workstream scoring |
| scripts/utils/iao_logger.py | Event logger |
| scripts/utils/ollama_config.py | Ollama defaults (think:false, num_predict) |
| scripts/utils/ollama_logged.py | Auto-logging Ollama wrapper |
| data/schema_reference.json | Thompson Schema reference for intent router (NEW v9.41) |
| data/chromadb/ | RAG vector store |
| data/iao_event_log.jsonl | P3 Diligence event stream |
| agent_scores.json | Agent + workstream scoring |
