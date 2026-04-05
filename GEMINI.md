# kjtcom - Agent Instructions (Gemini CLI)

## Read Order

1. docs/kjtcom-design-v9.45.md
2. docs/kjtcom-plan-v9.45.md
3. docs/kjtcom-architecture.mmd (living architecture chart)

## Context

Flutter Web app at kylejeromethompson.com. Location intelligence platform with 6,181 entities.
Project: kjtcom-c78cd
App code: app/lib/
Production: Firebase Hosting

## Shell

- NZXTcos uses fish shell
- All shell commands MUST be wrapped in `fish -c "..."`  (G19)
- NEVER cat ~/.config/fish/config.fish (G20)
- NEVER cat SA credential JSON files (G11)
- Use `python3 -u` for unbuffered stdout

## Security - ABSOLUTE RULES

* NEVER write API keys, tokens, or credentials into ANY file in the repo
* NEVER include API keys in build logs, reports, or changelog artifacts
* NEVER echo or print API key values in commands that get logged
* Read keys from environment variables ONLY
* If a key needs to be tested, print only "SET" or "NOT SET", never the value
* Violation of these rules is a BLOCKING failure - stop and alert Kyle

## Key Files

- app/lib/widgets/query_editor.dart - query editor with TextField + syntax highlighting
- app/lib/providers/query_provider.dart - query state + TextEditingController provider
- app/lib/widgets/schema_tab.dart - schema builder with "+ Add to query" button
- app/lib/widgets/query_autocomplete.dart - inline autocomplete
- app/lib/widgets/detail_panel.dart - +filter/-exclude buttons
- app/lib/models/query_clause.dart - parser + knownFields
- app/assets/value_index.json - precomputed distinct values per field

## Permissions

- CAN: flutter build web, firebase deploy --only hosting/firestore/functions
- CAN: pip install, npm install (project-level)
- CAN: ollama run, ollama pull, ollama list, ollama create
- CAN: curl http://localhost:11434/api/* (Ollama API)
- CANNOT: git add / commit / push
- CANNOT: sudo (ask Kyle)

## Database Rules

* Load to "staging" database only
* NEVER write to "(default)" without Kyle approval

## Multi-Agent Orchestration - MANDATORY (v9.35+)

* Every iteration MUST consult at least 2 LLMs before executing changes
* You (Gemini CLI) count as LLM #1
* LLM #2 MUST be a local model via Ollama at localhost:11434
* Available local models (run sequentially, never simultaneously):
  - qwen3.5:9b - Primary local. Code review, approach analysis, docs. ~5.1 GB VRAM.
  - nemotron-mini:4b - Fast second opinion, tool use, agentic reasoning. ~2.7 GB VRAM.
  - haervwe/GLM-4.6V-Flash-9B - Vision-capable, screenshot analysis, UI review. ~4.8 GB VRAM.
* To consult a local model:
  ```fish
  fish -c 'ollama run qwen3.5:9b "Your prompt here" --verbose'
  ```
  Or via API:
  ```fish
  fish -c 'curl -s http://localhost:11434/api/chat -d \'{"model": "qwen3.5:9b", "messages": [{"role": "user", "content": "Your prompt here"}], "stream": false}\' | python3 -c "import sys,json; print(json.load(sys.stdin)[\'message\'][\'content\'])"'
  ```
* Consult local models for: approach options, code review, alternative solutions, bug analysis
* Document ALL agent consultations in the build log "Agent Orchestration" section

## MCP Servers - MANDATORY (v9.35+)

* Firebase MCP: Validate Firestore queries, inspect documents, verify security rules
* Context7 MCP: Fetch current Flutter/Dart/Riverpod docs BEFORE making API calls
* Firecrawl MCP: Scrape reference UIs (Panther SIEM, competitor editors)
* Playwright MCP: Post-deploy smoke tests (screenshots - G47 blocks DOM interaction)
* Dart/Flutter MCP: Code analysis, widget tree inspection (when available)
* If an MCP server is unavailable, document the reason in the build log
* MCP config lives in .gemini/settings.json

## Flutter Build + Deploy

- Build: fish -c "cd app && flutter build web"
- Deploy: fish -c "cd ~/dev/projects/kjtcom && firebase deploy --only hosting"
- Deploy from repo root, not app/ (G38)
- flutter analyze + flutter test after every change

## Artifact Rules - MANDATORY

* Every iteration MUST produce/update these 4 files before completing:
  1. docs/kjtcom-design-v{VERSION}.md (living architecture + orchestration mandate)
  2. docs/kjtcom-plan-v{VERSION}.md (execution steps)
  3. docs/kjtcom-build-v{VERSION}.md (session transcript)
  4. docs/kjtcom-report-v{VERSION}.md (metrics + Agent Orchestration section)
* The report MUST include an "Agent Orchestration" section listing:
  - Which LLMs were consulted (minimum 2)
  - Which MCP servers were used
  - Key decisions influenced by multi-agent input
  - Any MCP servers skipped and why
* Update docs/kjtcom-changelog.md (APPEND, never overwrite)
* Update README.md (project status, pipelines table, changelog section)

## Formatting

- No em-dashes. Use " - " instead.
- Use "->" for arrows.

## Project Context

* Live site: kylejeromethompson.com
* GitHub: SOC-Foundry/kjtcom
* Firebase project: kjtcom-c78cd
* Production entities: 6,181 across 3 pipelines (CalGold, RickSteves, TripleDB)
* Current phase: 9 - App Optimization
* Flutter app: 25 Dart files, ~4,200 LOC, 6 tabs
* Gotchas: 44 documented (G1-G50)
* Kyle handles all git. Agents NEVER touch git.
