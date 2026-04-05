# kjtcom - Execution Plan v9.38

**Phase:** 9 - App Optimization
**Iteration:** 38
**Date:** April 5, 2026
**Executing Agent:** Claude Code (Opus 4.6)
**Estimated Duration:** 4-5 hours (largest middleware iteration)

---

## PRE-FLIGHT CHECKLIST

- [ ] Ollama running with 3 models
- [ ] .mcp.json present with 5 servers (Firebase, Context7, Firecrawl, Playwright, Dart)
- [ ] v9.37 docs archived
- [ ] Git clean
- [ ] Telegram account available (Kyle creates bot via BotFather)
- [ ] Brave Search API key obtained (https://brave.com/search/api/)
- [ ] Working directory: ~/dev/projects/kjtcom

---

## STEP 1: Architecture Chart (W6) - 15 min

Create the living architecture file first so all subsequent changes update it.

```fish
# 1a. Create docs/kjtcom-architecture.mmd
# Paste the full mermaid chart from kjtcom-v938-blueprint.md

# 1b. Add link in README.md
# Under a new "## Architecture" section:
# "See the [living architecture chart](docs/kjtcom-architecture.mmd) for the full system diagram."

# 1c. Verify GitHub renders it
# .mmd files render natively on GitHub
```

---

## STEP 2: RAG Middleware (W1) - 60 min

### 2a. Pull embedding model

```fish
ollama pull nomic-embed-text
# ~270 MB download, fits alongside any other model
```

### 2b. Install ChromaDB

```fish
pip install chromadb --break-system-packages
# Verify:
python3 -c "import chromadb; print(chromadb.__version__)"
```

### 2c. Create embedder script

Create `scripts/embed_archive.py`:
- Scan docs/archive/ for all .md files (141 files)
- Chunk each file: 1000 chars, 200 char overlap
- Add metadata: filename, iteration version, file type
- Embed via Ollama nomic-embed-text API
- Store in ChromaDB persistent directory: `data/chromadb/`

```fish
python3 scripts/embed_archive.py
# Expected: 141 files embedded, ~500-1000 chunks total
```

### 2d. Create RAG query script

Create `scripts/query_rag.py`:
- Accept natural language query
- Embed query via nomic-embed-text
- Search ChromaDB for top-k similar chunks (k=5)
- Return chunks with metadata

```fish
python3 scripts/query_rag.py "What caused the G45 cursor bug?"
# Expected: Returns chunks from v9.29-v9.34 build logs discussing cursor placement
```

### 2e. Rebuild iteration_registry.json

Create `scripts/build_registry_v2.py`:
- For each of 37 iterations (v0.5 through v9.37):
  - Query ChromaDB for chunks matching that iteration version
  - Feed relevant chunks (2-4K tokens max) to Qwen with /no_think
  - Qwen extracts: agents, outcomes, gotchas, failures, successes
  - Output structured JSON
- Merge all into iteration_registry.json
- Include gotcha registry with agent attribution

```fish
python3 scripts/build_registry_v2.py
# This runs sequentially: embed query (nomic) -> retrieve chunks -> score (Qwen)
# Models load/unload between steps, no VRAM conflict
```

### 2f. Update install.fish

Add nomic-embed-text pull and chromadb install to Step 5b/10.

---

## STEP 3: Brave Search API (W3) - 15 min

### 3a. Verify API key

```fish
test -n "$BRAVE_SEARCH_API_KEY"; and echo "SET"; or echo "NOT SET"
# If NOT SET, Kyle adds to config.fish
```

### 3b. Create search wrapper

Create `scripts/brave_search.py`:
- Accept query string
- Call Brave Search API v1/web/search
- Return top 5 results with title, URL, snippet
- Used by OpenClaw bot and agent scripts

```fish
python3 scripts/brave_search.py "flutter_code_editor package"
# Expected: Returns search results with snippets
```

### 3c. Update install.fish

Add BRAVE_SEARCH_API_KEY to the "Required keys" section in Next Steps.

---

## STEP 4: OpenClaw + Telegram (W2) - 60 min

### 4a. Install OpenClaw

```fish
pip install open-interpreter --break-system-packages
# Verify:
python3 -c "import interpreter; print('OpenClaw OK')"
```

### 4b. Install NemoClaw (if available)

```fish
pip install nemoclaw --break-system-packages 2>/dev/null
# If not on pip, clone from GitHub:
# git clone https://github.com/NVIDIA/NemoClaw.git /tmp/nemoclaw
# pip install /tmp/nemoclaw --break-system-packages
# If neither works, document as deferred. NemoClaw is alpha.
```

### 4c. Telegram BotFather Setup

Kyle creates the bot manually:
1. Open Telegram, message @BotFather
2. `/newbot` -> name: "kjtcom IAO Agent" -> username: `kjtcom_iao_bot`
3. Copy bot token
4. Add to config.fish: `set -gx TELEGRAM_BOT_TOKEN "your-token"`
5. Source config: `source ~/.config/fish/config.fish`

This is the ONE expected intervention.

### 4d. Install python-telegram-bot

```fish
pip install python-telegram-bot --break-system-packages
```

### 4e. Create Telegram bot script

Create `scripts/telegram_bot.py`:

```python
# Telegram bot that routes commands to kjtcom agents
# Commands:
#   /status  - Ollama model status, MCP health
#   /query   - Firestore query via Firebase MCP pattern
#   /evaluate - Run Qwen evaluator
#   /gotcha  - List active gotchas
#   /scores  - Agent leaderboard
#   /ask     - RAG-powered Q&A over archive
#   /search  - Brave Search API query
#
# Routes to:
#   - Ollama API (localhost:11434) for LLM queries
#   - ChromaDB for RAG queries
#   - Brave Search API for web queries
#   - Firestore Admin SDK for data queries
```

### 4f. Test bot

```fish
# Start bot in background
python3 scripts/telegram_bot.py &

# From Telegram, message @kjtcom_iao_bot:
# /status
# Expected: "Ollama: running. Models: qwen3.5:9b, nemotron-mini:4b, ..."
# /ask What is the Thompson Schema?
# Expected: RAG-powered answer from archive
```

---

## STEP 5: Claw3D Prototype (W4) - 30 min

### 5a. Create prototype directory

```fish
mkdir -p docs/claw3d-prototype
```

### 5b. Build standalone HTML/Three.js prototype

Create `docs/claw3d-prototype/index.html`:
- Three.js scene with dark background (#0D1117)
- Agent nodes as labeled spheres (Qwen=purple, Claude=teal, Gemini=blue, Nemotron=amber, GLM=coral)
- MCP server nodes as smaller cubes
- Connection lines between agents and their MCP servers
- Animated particles along connections showing data flow
- Status colors: green=active, gray=idle, red=error
- Camera orbit controls

### 5c. Reference

- github.com/iamlukethedev/Claw3D for implementation patterns
- Use Three.js via CDN (cdnjs.cloudflare.com)

---

## STEP 6: Evaluator Enhancements (W5) - 30 min

### 6a. Add token tracking to agent_scores.json

Update `scripts/run_evaluator.py` to capture:
- prompt_tokens from Ollama response metadata
- eval_tokens from Ollama response metadata
- total_tokens calculated

### 6b. Merge gotcha registry

Update `scripts/build_registry_v2.py` to include gotcha_registry section with:
- Agent attribution (caused_by, caught_by, resolved_by)
- Recurrence tracking
- Cross-reference with iteration data

### 6c. Build leaderboard generator

Create `scripts/generate_leaderboard.py`:
- Reads agent_scores.json
- Computes per-agent: avg score, best, worst, trend, total tokens
- Outputs formatted table for report

---

## STEP 7: Portable Template (W7) - 30 min

### 7a. Create template directory

```fish
mkdir -p template/evaluator template/rag template/schema template/gotcha
```

### 7b. Create template files

Copy and generalize these files into template/:
- CLAUDE.md -> CLAUDE.md.template (replace "kjtcom" with {PROJECT_NAME})
- GEMINI.md -> GEMINI.md.template
- .mcp.json -> .mcp.json.template
- evaluator-prompt.md, run_evaluator.py -> template/evaluator/
- embed_archive.py, query_rag.py -> template/rag/
- Thompson Schema spec -> template/schema/
- Gotcha registry seed -> template/gotcha/

### 7c. Create template README

Create `template/README.md` explaining how to stamp the template onto a new project.

---

## STEP 8: Qwen Consultation + Scoring (20 min)

### 8a. Consult Qwen on OpenClaw integration risks

```fish
curl -s http://localhost:11434/api/chat -d '{
  "model": "qwen3.5:9b",
  "messages": [{"role": "user", "content": "/no_think What are the security risks of running OpenClaw with Telegram as the interface? Consider file system access, API key exposure, and sandbox escape. Give me a risk assessment."}],
  "stream": false
}' | python3 -c "import sys,json; print(json.load(sys.stdin)['message']['content'])"
```

### 8b. Run evaluator at end of iteration

```fish
python3 scripts/run_evaluator.py --version v9.38 \
  --build-log docs/kjtcom-build-v9.38.md \
  --active-gotchas "G47,G51"
```

---

## STEP 9: Artifacts (15 min)

- [ ] docs/kjtcom-architecture.mmd (living mermaid chart - NEW)
- [ ] docs/kjtcom-design-v9.38.md (pre-staged)
- [ ] docs/kjtcom-plan-v9.38.md (pre-staged)
- [ ] docs/kjtcom-build-v9.38.md (you create)
- [ ] docs/kjtcom-report-v9.38.md (with Agent Scorecard + token tracking)
- [ ] docs/kjtcom-changelog.md (append v9.38)
- [ ] agent_scores.json (append v9.38 with token tracking)
- [ ] iteration_registry.json (rebuilt via RAG - all iterations)
- [ ] scripts/embed_archive.py (NEW)
- [ ] scripts/query_rag.py (NEW)
- [ ] scripts/build_registry_v2.py (NEW)
- [ ] scripts/brave_search.py (NEW)
- [ ] scripts/telegram_bot.py (NEW)
- [ ] scripts/generate_leaderboard.py (NEW)
- [ ] docs/claw3d-prototype/index.html (NEW)
- [ ] template/ directory (NEW - portable IAO template)
- [ ] .mcp.json (unchanged unless new MCP added)
- [ ] README.md (add Architecture section linking to .mmd)
- [ ] CLAUDE.md (update read order)
- [ ] GEMINI.md (update read order)
- [ ] docs/install.fish (add nomic-embed, chromadb, telegram, brave, openclaw)

Archive v9.37 docs first: `mv docs/kjtcom-*-v9.37.md docs/archive/`

---

## POST-FLIGHT CHECKLIST

- [ ] nomic-embed-text pulled and embedding works
- [ ] ChromaDB installed and 141 files embedded
- [ ] RAG queries return relevant chunks
- [ ] iteration_registry.json rebuilt with all iterations scored
- [ ] Brave Search API returns results
- [ ] OpenClaw installed (or documented as deferred)
- [ ] Telegram bot responds to /status and /ask
- [ ] Claw3D prototype renders in browser
- [ ] docs/kjtcom-architecture.mmd created and linked from README
- [ ] template/ directory created with all components
- [ ] Token tracking in agent_scores.json
- [ ] Gotcha registry merged into iteration_registry.json
- [ ] install.fish updated with all new deps
- [ ] flutter analyze: 0 issues
- [ ] flutter test: 15/15 pass
- [ ] Agent Scorecard in report with token tracking

---

## INTERVENTION POINTS

| # | Trigger | Resolution |
|---|---------|------------|
| 1 | Telegram BotFather token | Kyle creates bot, adds token to config.fish |
| 2 | Brave Search API key | Kyle obtains from brave.com/search/api/, adds to config.fish |
| 3 | Firebase reauth (G53) | Kyle runs firebase login --reauth if session expired |

Zero-intervention target: 2-3 (API key setup requires human).

---

*Plan document generated from claude.ai Opus 4.6 session, April 5, 2026.*
