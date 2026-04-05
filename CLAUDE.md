# kjtcom - Agent Instructions (Claude Code)

## Read Order

1. docs/kjtcom-design-v9.37.md
2. docs/kjtcom-plan-v9.37.md

## Shell - MANDATORY

* Run: claude config set preferredShell fish (before first launch)
* All commands execute in fish shell
* Environment variables are in ~/.config/fish/config.fish
* NEVER use bash syntax (no ${VAR}, no heredocs, no source ~/.bashrc)
* If a command fails with "not a valid variable", you are in bash. Switch to fish.

## Security - ABSOLUTE RULES

* NEVER write API keys, tokens, or credentials into ANY file in the repo
* NEVER include API keys in build logs, reports, or changelog artifacts
* NEVER echo or print API key values in commands that get logged
* Read keys from environment variables ONLY
* NEVER capture customer alert/detection data from Panther SIEM
* Panther scrape captures UI structure ONLY - DOM, CSS, layout. No result row data.
* Violation of these rules is a BLOCKING failure - stop and alert Kyle

## Gotcha G2 - CUDA LD_LIBRARY_PATH (READ THIS)

* faster-whisper/ctranslate2 WILL fail if LD_LIBRARY_PATH is not set
* Check: echo $LD_LIBRARY_PATH (must be non-empty and include cuda/cublas/cudnn)
* If empty: source ~/.config/fish/config.fish

## Permissions

* CAN: flutter build web, firebase deploy --only hosting/firestore/functions
* CAN: pip install, npm install (project-level)
* CAN: ollama run, ollama pull, ollama list, ollama create
* CAN: curl http://localhost:11434/api/* (Ollama API)
* CAN: curl http://localhost:9222/* (Chrome CDP - Panther scrape)
* CAN: dart mcp-server, claude mcp add
* CAN: npx firebase-tools, npx @upstash/context7-mcp, npx firecrawl-mcp, npx @playwright/mcp
* CANNOT: git add / commit / push
* CANNOT: sudo (ask Kyle)

## Database Rules

* Load to "staging" database only
* NEVER write to "(default)" without Kyle approval

## Multi-Agent Orchestration - MANDATORY (v9.35+)

* Every iteration MUST consult at least 2 LLMs before executing changes
* You (Claude Code) count as LLM #1
* LLM #2 MUST be a local model via Ollama at localhost:11434
* Available local models (run sequentially, never simultaneously):
  - qwen3.5:9b - PERMANENT EVALUATOR + code review. ~5.1 GB VRAM. Use /no_think prefix for JSON output (G51).
  - nemotron-mini:4b - Fast second opinion. ~2.7 GB VRAM.
  - haervwe/GLM-4.6V-Flash-9B - Vision/screenshot analysis. ~4.8 GB VRAM.
* Consult via API (preferred over ollama run for clean output):
  ```fish
  curl -s http://localhost:11434/api/chat -d '{
    "model": "qwen3.5:9b",
    "messages": [{"role": "user", "content": "/no_think Your prompt here"}],
    "stream": false
  }' | python3 -c "import sys,json; print(json.load(sys.stdin)['message']['content'])"
  ```

## Agent Evaluator Middleware - MANDATORY (v9.36+)

* Qwen3.5-9B is the PERMANENT EVALUATOR
* At end of every iteration, run: python3 scripts/run_evaluator.py
* Scores append to agent_scores.json (never overwrite)
* Report MUST include Agent Scorecard with per-iteration scores folded in
* iteration_registry.json tracks historical efficacy (v9.37+)

## MCP Servers - MANDATORY (v9.35+)

* Firebase MCP: Validate Firestore queries, inspect documents. Needs firebase login --reauth per session (G53).
* Context7 MCP: Fetch current Flutter/Dart/Riverpod docs BEFORE making API calls
* Firecrawl MCP: Scrape reference UIs. May need debugging (G52).
* Playwright MCP: Post-deploy smoke tests, Panther CDP scraping
* Dart MCP: dart mcp-server (requires Dart 3.9+). Code analysis, widget tree, pub.dev search, test runner.
* MCP config: .mcp.json (Claude Code) + .gemini/settings.json (Gemini CLI)

## Changelog

* Write all changes to docs/kjtcom-changelog.md (unified, not per-pipeline)
* APPEND entries - never overwrite previous entries

## Artifact Rules - MANDATORY

* Every iteration produces:
  1. docs/kjtcom-design-v{VERSION}.md
  2. docs/kjtcom-plan-v{VERSION}.md
  3. docs/kjtcom-build-v{VERSION}.md
  4. docs/kjtcom-report-v{VERSION}.md (with Agent Scorecard)
* Also update: docs/kjtcom-changelog.md, README.md, agent_scores.json, docs/install.fish (if new deps)
* Report MUST confirm install.fish was updated or state "No new dependencies"

## Living Documents

* docs/install.fish - update when ANY package installed (pip, npm, pacman, yay, ollama, dart pub)
* iteration_registry.json - updated by Qwen evaluator each iteration
* agent_scores.json - appended by evaluator each iteration

## Formatting

* No em-dashes. Use " - " instead.
* Use "->" for arrows.

## Project Context

* Live site: kylejeromethompson.com
* GitHub: SOC-Foundry/kjtcom
* Firebase project: kjtcom-c78cd
* Production entities: 6,181 across 3 pipelines
* Phase: 9 - App Optimization
* Flutter app: 25 Dart files, ~4,200 LOC, 6 tabs
* Gotchas: 47 documented (G1-G53)
* Kyle handles all git. Agents NEVER touch git.
