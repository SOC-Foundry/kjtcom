# kjtcom - Agent Instructions (Claude Code)

## Read Order

1. docs/kjtcom-design-v9.38.md
2. docs/kjtcom-plan-v9.38.md
3. docs/kjtcom-architecture.mmd (living architecture chart)

## Shell - MANDATORY

* Run: claude config set preferredShell fish (before first launch)
* All commands execute in fish shell
* NEVER use bash syntax (no ${VAR}, no heredocs, no source ~/.bashrc)

## Security - ABSOLUTE RULES

* NEVER write API keys, tokens, or credentials into ANY file in the repo
* NEVER include API keys in build logs, reports, or changelog artifacts
* Read keys from environment variables ONLY (KJTCOM_TELEGRAM_BOT_TOKEN, KJTCOM_BRAVE_SEARCH_API_KEY, FIRECRAWL_API_KEY)
* NEVER capture customer data from Panther SIEM
* Violation = BLOCKING failure - stop and alert Kyle

## Permissions

* CAN: flutter build web, firebase deploy, pip install, npm install
* CAN: ollama run/pull/list/create, curl localhost:11434/*
* CAN: curl localhost:9222/* (Chrome CDP)
* CAN: dart mcp-server, claude mcp add
* CAN: python3 scripts/telegram_bot.py, python3 scripts/embed_archive.py
* CANNOT: git add / commit / push
* CANNOT: sudo (ask Kyle)

## Database Rules

* Load to "staging" database only. NEVER write to "(default)" without Kyle approval.

## Multi-Agent Orchestration - MANDATORY (v9.35+)

* Every iteration MUST consult at least 2 LLMs
* You (Claude Code) count as LLM #1
* LLM #2 via Ollama at localhost:11434:
  - qwen3.5:9b - PERMANENT EVALUATOR. Use /no_think for JSON. ~5.1 GB VRAM.
  - nemotron-mini:4b - Fast triage. ~2.7 GB VRAM.
  - haervwe/GLM-4.6V-Flash-9B - Vision. ~4.8 GB VRAM.
  - nomic-embed-text - Embedding ONLY (not chat). ~270 MB VRAM.
* Consult via API (clean output):
  ```fish
  curl -s http://localhost:11434/api/chat -d '{
    "model": "qwen3.5:9b",
    "messages": [{"role": "user", "content": "/no_think Your prompt"}],
    "stream": false
  }' | python3 -c "import sys,json; print(json.load(sys.stdin)['message']['content'])"
  ```

## Agent Evaluator Middleware - MANDATORY (v9.36+)

* Qwen3.5-9B is PERMANENT EVALUATOR
* Run: python3 scripts/run_evaluator.py at end of every iteration
* Scores append to agent_scores.json with token tracking (prompt_tokens, eval_tokens)
* Report MUST include Agent Scorecard with scores + token usage

## RAG Middleware (v9.38+)

* ChromaDB vector store at data/chromadb/
* nomic-embed-text for embeddings via Ollama
* scripts/embed_archive.py - ingest docs/archive/ into ChromaDB
* scripts/query_rag.py - semantic search over archive
* scripts/build_registry_v2.py - RAG-augmented registry builder

## MCP Servers - MANDATORY (v9.35+)

* Firebase MCP: Firestore queries. Needs firebase login --reauth per session (G53).
* Context7 MCP: Flutter/Dart/Riverpod API docs.
* Firecrawl MCP: Web scraping.
* Playwright MCP: Browser automation + CDP.
* Dart MCP: dart mcp-server. Code analysis + testing.

## OpenClaw + Telegram (v9.38+)

* OpenClaw: Local sandbox agent (open-interpreter)
* Telegram bot: scripts/telegram_bot.py (TELEGRAM_BOT_TOKEN from env)
* Brave Search: scripts/brave_search.py (BRAVE_SEARCH_API_KEY from env)
* NemoClaw: Security layer if available (alpha)

## Living Documents

* docs/install.fish - update when ANY package installed
* docs/kjtcom-architecture.mmd - update when architecture changes
* iteration_registry.json - updated by evaluator each iteration
* agent_scores.json - appended by evaluator each iteration

## Artifact Rules - MANDATORY

* Every iteration produces: design, plan, build, report
* Report MUST include Agent Scorecard with token tracking
* Report MUST confirm: install.fish updated / architecture.mmd updated / or "no changes"
* Update: changelog, README, agent_scores.json, install.fish, architecture.mmd as needed

## Formatting

* No em-dashes. Use " - " instead. Use "->" for arrows.

## Project Context

* Live site: kylejeromethompson.com | GitHub: SOC-Foundry/kjtcom | Firebase: kjtcom-c78cd
* 6,181 entities, 3 pipelines, 25 Dart files, ~4,200 LOC, 6 tabs, 47 gotchas (G1-G53)
* Kyle handles all git. Agents NEVER touch git.
