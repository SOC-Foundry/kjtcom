# IAO Portable Template

Stampable template for Iterative Agentic Orchestration (IAO) projects.

## Quick Start

1. Copy this template/ directory to your new project root
2. Rename `.template` files (remove the `.template` extension)
3. Replace placeholder tokens:
   - `{PROJECT_NAME}` - your project name
   - `{PROJECT_DESCRIPTION}` - one-line description
   - `{CURRENT_VERSION}` - e.g., v1.0
   - `{PIPELINE_ID}` - pipeline identifier
4. Install dependencies:
   ```fish
   ollama pull qwen3.5:9b
   ollama pull nomic-embed-text
   pip install chromadb --break-system-packages
   ```
5. Initialize:
   ```fish
   mkdir -p docs/archive data/chromadb
   cp .mcp.json.template .mcp.json
   ```

## Components

| Component | Purpose |
|-----------|---------|
| CLAUDE.md.template | Agent instructions for Claude Code |
| GEMINI.md.template | Agent instructions for Gemini CLI |
| .mcp.json.template | MCP server configuration (5 servers) |
| evaluator/ | Qwen3.5-9B scoring with token tracking |
| rag/ | ChromaDB + nomic-embed-text RAG pipeline |
| schema/ | Thompson Indicator Fields spec + mapping template |
| gotcha/ | Failure pattern registry seed |

## Methodology

IAO (Iterative Agentic Orchestration) is a structured approach to running AI coding agents with:
- Multi-LLM consultation (min 2 per iteration)
- 4-artifact output loop (design, plan, build, report)
- Agent evaluator middleware (Qwen scoring)
- RAG over archived artifacts
- Gotcha registry for failure prevention
- Zero-intervention target

See the kjtcom README for full IAO methodology documentation.
