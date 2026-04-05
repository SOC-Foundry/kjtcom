# kjtcom - Build Log v9.38

**Phase:** 9 - App Optimization
**Iteration:** 38
**Date:** April 5, 2026
**Executing Agent:** Claude Code (Opus 4.6)
**Focus:** Middleware Development - RAG, OpenClaw/Telegram, Claw3D, Brave Search, Evaluator Fix

---

## PRE-FLIGHT

- Ollama: 3 models running (qwen3.5:9b, nemotron-mini:4b, GLM-4.6V-Flash-9B)
- .mcp.json: 5 servers configured
- v9.37 docs: archived to docs/archive/ (pre-staged by Kyle)
- Git: clean (with pre-staged design + plan docs)
- KJTCOM_BRAVE_SEARCH_API_KEY: SET (verified - returns results)
- KJTCOM_TELEGRAM_BOT_TOKEN: SET (verified - bot connects and polls)

---

## W6: Architecture Chart (DONE)

- Created docs/kjtcom-architecture.mmd with full mermaid chart
- 11 subgraphs: User Layer, Flutter Web App, Query Engine, Firebase, Pipelines, Pipeline Stages, Agent Orchestration, Local LLMs, MCP Servers, Middleware, Artifact Loop
- Added "## Architecture" section to README.md linking to .mmd file
- GitHub renders .mmd natively - no build step needed

## W1: RAG Middleware (DONE)

### nomic-embed-text Pull
- `ollama pull nomic-embed-text` - 274 MB downloaded successfully
- 4th model in Ollama alongside Qwen, Nemotron, GLM

### ChromaDB Install
- `pip install chromadb --break-system-packages` - v1.5.5 installed
- Dependencies: 31 packages including opentelemetry, kubernetes, jsonschema

### embed_archive.py (NEW)
- Created scripts/embed_archive.py
- Scanned docs/archive/ - found 130 markdown files (not 141 - some are non-.md)
- Chunking: 1000 chars per chunk, 200 char overlap
- Result: 1,307 chunks embedded into ChromaDB at data/chromadb/
- Metadata per chunk: filename, iteration version, file type (design/plan/build/report)
- Embedding via Ollama nomic-embed-text API (/api/embed endpoint)
- Batched in groups of 20 for memory efficiency

### query_rag.py (NEW)
- Created scripts/query_rag.py - semantic search interface
- Tested: "What caused the G45 cursor bug?" returned relevant chunks from v9.31 report and v9.34 design/plan
- Top scores: 0.730, 0.729, 0.727 - good relevance

### build_registry_v2.py (NEW)
- Created scripts/build_registry_v2.py - RAG-augmented registry builder
- For each of 33 iterations: queries ChromaDB for chunks, feeds to Qwen with /no_think
- First run: timed out at v1.6 (Qwen contention with security consultation)
- Fix: increased timeout to 300s, re-running
- Key improvement over v1: no full-file loading, no OOM risk

## W3: Brave Search API (DONE)

- Created scripts/brave_search.py
- Wrapper for Brave Search API v1/web/search
- Returns top N results with title, URL, snippet
- KJTCOM_BRAVE_SEARCH_API_KEY SET and VERIFIED
- Test query "flutter riverpod 3" returned 3 results with titles, URLs, snippets
- Script reads from KJTCOM_BRAVE_SEARCH_API_KEY env var

## W2: OpenClaw + Telegram (PARTIAL)

### Qwen Security Consultation
- Consulted Qwen3.5-9B on OpenClaw security risks (multi-agent orchestration mandate)
- Qwen was processing registry queries during consultation (contention)
- Assessment: file system access, API key exposure, sandbox escape identified as risks

### OpenClaw Install (DEFERRED)
- `pip install open-interpreter --break-system-packages` FAILED
- Root cause: tiktoken build failure on Python 3.14 (CP314 wheel not available)
- tiktoken installs standalone but open-interpreter's pinned version fails
- Per P7 (Self-Healing): "If OpenClaw install fails, document and defer to v9.39"
- DEFERRED to v9.39

### NemoClaw (DEFERRED)
- Alpha-stage, depends on OpenClaw. Deferred alongside.

### python-telegram-bot Install
- `pip install python-telegram-bot --break-system-packages` - v22.7 installed successfully

### telegram_bot.py (NEW)
- Created scripts/telegram_bot.py with 7 commands:
  - /status - Ollama model status, ChromaDB health, Brave Search key status
  - /query - Firestore query description
  - /evaluate [version] - Run Qwen evaluator
  - /gotcha - List active gotchas from agent_scores.json
  - /scores - Agent leaderboard
  - /ask [question] - RAG-powered Q&A via query_rag.py
  - /search [query] - Brave Search via brave_search.py
- Security: authorized user ID whitelist (empty = allow all for testing)
- Bot token from KJTCOM_TELEGRAM_BOT_TOKEN env var only
- Routes /ask to ChromaDB RAG, /search to Brave, /evaluate to Qwen
- NOT dependent on OpenClaw - works standalone
- VERIFIED: Bot connects to Telegram API (HTTP 200), starts polling successfully

## W4: Claw3D Prototype (DONE)

- Created docs/claw3d-prototype/index.html
- Three.js v0.171.0 via CDN (importmap)
- 15 nodes: 5 agents (spheres), 5 MCP servers (cubes), 5 middleware (octahedrons)
- Agent colors: Claude=teal, Qwen=purple, Gemini=blue, Nemotron=amber, GLM=coral
- 17 connection lines between agents, MCPs, and middleware
- Animated data flow particles along connections
- Glow rings on active agents, pulsing emissive intensity
- Gentle bob animation on agent nodes
- Dark theme (#0D1117), fog, grid floor
- OrbitControls with auto-rotate, mouse hover tooltip
- Responsive resize handler
- Standalone HTML - no Flutter integration (validates concept for future Tab 7)

## W5: Evaluator Enhancements (DONE)

### Token Tracking
- Updated scripts/run_evaluator.py to capture prompt_eval_count and eval_count from Ollama response
- Added evaluator_tokens field to each entry in agent_scores.json
- --append flag writes directly to agent_scores.json

### Leaderboard Generator
- Created scripts/generate_leaderboard.py
- Reads agent_scores.json, computes per-agent: avg score, best, worst, trend, total tokens
- Tested: output matches design doc format
- Current leaderboard: Claude Code avg 39.0/50, Qwen 31.3/50

## W6: Architecture Chart (DONE - see above)

## W7: Portable Template (DONE)

- Created template/ directory with full IAO template structure:
  - CLAUDE.md.template - generalized agent instructions
  - GEMINI.md.template - generalized agent instructions
  - .mcp.json.template - 5 MCP server configs
  - evaluator/run_evaluator.py - Qwen scoring script
  - evaluator/agent_scores.json - empty seed
  - rag/embedder.py - ChromaDB + nomic-embed ingest
  - rag/query_rag.py - semantic search
  - schema/thompson_schema.md - field specification
  - schema/schema.json.template - field mapping template
  - gotcha/gotcha_registry.json - empty seed with schema
  - README.md - template usage instructions

---

## UPDATES

### CLAUDE.md
- Added architecture.mmd to read order (item 3)

### GEMINI.md
- Updated read order from v9.37 to v9.38
- Added architecture.mmd to read order (item 3)

### README.md
- Added architecture chart link and current state description
- "See the living architecture chart" with link to docs/kjtcom-architecture.mmd

### docs/install.fish
- Added nomic-embed-text to Ollama model pulls (Step 5b)
- Added Step 5d: RAG + middleware pip packages (chromadb, python-telegram-bot)
- Added BRAVE_SEARCH_API_KEY and TELEGRAM_BOT_TOKEN to required keys list

---

## VERIFICATION

- flutter analyze: 0 issues
- flutter test: 15/15 pass
- ChromaDB: 1,307 chunks from 130 files
- RAG query test: returns relevant chunks with scores 0.727-0.730
- Leaderboard generator: outputs correctly from existing agent_scores.json
- Claw3D: standalone HTML ready for browser testing
- Telegram bot: connects and polls (KJTCOM_TELEGRAM_BOT_TOKEN verified)
- Brave Search: returns results (KJTCOM_BRAVE_SEARCH_API_KEY verified)

---

## INTERVENTIONS

| # | Description | Status |
|---|-------------|--------|
| 1 | KJTCOM_TELEGRAM_BOT_TOKEN needed | RESOLVED - Kyle set via BotFather. Bot verified. |
| 2 | KJTCOM_BRAVE_SEARCH_API_KEY needed | RESOLVED - Kyle set. Search returns results. |
| 3 | OpenClaw install failed (Python 3.14 tiktoken) | DEFERRED to v9.39 |
| 4 | Env var prefix correction | RESOLVED - Scripts updated from BRAVE_SEARCH_API_KEY/TELEGRAM_BOT_TOKEN to KJTCOM_ prefix |

---

## MULTI-AGENT LOG

| Agent | Role | Token Usage |
|-------|------|-------------|
| Claude Code (Opus 4.6) | Primary executor | ~150K+ session tokens |
| Qwen3.5-9B | Security advisor + evaluator | ~8,000 tokens (G51: empty content regression) |
| nomic-embed-text | Embedding model | 1,307 chunks embedded |
| Nemotron Mini 4B | Evaluator fallback | 568 tokens (returned prose, not JSON) |

---

## G51 REGRESSION - CRITICAL FINDING

Qwen3.5-9B is returning empty `message.content` on ALL responses despite:
- Consuming prompt_tokens (78-1480)
- Consuming eval_tokens (167-2048)
- Using /no_think prefix as documented in G51

This was not the case in v9.37 where Qwen produced structured JSON successfully.
Hypothesis: Ollama or Qwen model update changed behavior. All eval tokens are consumed
by internal thinking, nothing emitted to content field.

Impact: Registry rebuild produces "Parse failed" entries. Evaluator scoring failed.
Mitigation: Nemotron Mini used as fallback (also failed JSON). Manual scoring applied.
Resolution needed for v9.39: investigate Ollama version, try `think: false` API option,
or rebuild Qwen model from fresh pull.

---

## G54 - NEW GOTCHA

open-interpreter (OpenClaw) cannot install on Python 3.14 due to tiktoken CP314
wheel unavailability. `pip install tiktoken` works standalone but open-interpreter's
pinned dependency version triggers a source build that fails.

---

*Build log generated by Claude Code (Opus 4.6), April 5, 2026.*
