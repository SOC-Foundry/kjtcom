# kjtcom - Execution Plan v9.35

**Phase:** 9 - App Optimization
**Iteration:** 35
**Date:** April 4, 2026
**Executing Agent:** Claude Code (Opus) with Qwen3.5-9B consultation
**Estimated Duration:** 2-3 hours

---

## PRE-FLIGHT CHECKLIST

- [ ] Ollama installed and running (`systemctl status ollama`)
- [ ] CUDA detected (`nvidia-smi` shows RTX 2080 SUPER)
- [ ] Qwen3.5-9B pulled (`ollama list` shows qwen3.5:9b)
- [ ] Firebase SA JSON present (`~/.config/gcloud/kjtcom-sa.json`)
- [ ] Node.js installed (`node --version` -> v20+)
- [ ] npx available (`npx --version`)
- [ ] Previous docs archived (`mv docs/kjtcom-*-v9.34.md docs/archive/`)
- [ ] Git clean (`git status` -> no uncommitted changes)
- [ ] Working directory: `~/dev/projects/kjtcom`

---

## STEP 1: Fix Nemotron 3 Nano Pull (15 min)

The `nemotron3-nano:4b` tag failed in the initial pull. Resolve the correct tag.

```fish
# 1a. Search Ollama registry for Nemotron
ollama search nemotron
# Look for: nemotron-nano, nemotron3-nano, nvidia/nemotron-3-nano-4b

# 1b. Try common tag patterns
ollama pull nemotron-nano
# or
ollama pull nemotron3-nano
# or
ollama pull hf.co/nvidia/Nemotron-3-Nano-4B-Instruct-GGUF:Q4_K_M

# 1c. If no Ollama tag exists, manual GGUF approach:
pip install huggingface_hub --break-system-packages
huggingface-cli download nvidia/Nemotron-3-Nano-4B-Instruct-GGUF \
  --include "*.Q4_K_M.gguf" \
  --local-dir ~/models/nemotron-nano-4b

# Create Modelfile
printf 'FROM ~/models/nemotron-nano-4b/nemotron-3-nano-4b-instruct.Q4_K_M.gguf
PARAMETER temperature 0.7
PARAMETER num_ctx 8192
' > /tmp/Modelfile.nemotron

ollama create nemotron-nano -f /tmp/Modelfile.nemotron
```

**Verification:**
```fish
ollama run nemotron-nano "What is 2+2" --verbose
# Expected: answer in <5s, VRAM usage ~3 GB
```

**Self-healing:** If GGUF download fails or model won't load, skip Nemotron and use Qwen3.5-9B as the primary local model with GLM-4.6V-Flash as secondary. Log the failure in the build doc.

---

## STEP 2: Pull GLM-4.6V-Flash (10 min)

```fish
# 2a. Search for correct tag
ollama search glm

# 2b. Pull the model
ollama pull glm4
# or
ollama pull glm-4.6v-flash

# 2c. Verify
ollama run glm4 "Describe the key features of Flutter's Riverpod state management" --verbose
# Expected: coherent answer, VRAM ~5 GB
```

**Self-healing:** If GLM not available in Ollama, substitute with Qwen3-8B (`ollama pull qwen3:8b`) as the third model option.

---

## STEP 3: Verify All Local LLMs (10 min)

```fish
# 3a. List all models
ollama list
# Expected: qwen3.5:9b, nemotron-nano (or equivalent), glm4 (or equivalent)

# 3b. VRAM test each model (run sequentially, not simultaneously)
ollama run qwen3.5:9b "Analyze this Dart code and suggest improvements: class QueryClause { final String field; final String operator; static QueryClause? parse(String line) { } }" --verbose

# Wait for completion, then:
ollama run nemotron-nano "What are the pros and cons of replacing Flutter's TextField with flutter_code_editor package?" --verbose

# Wait for completion, then:
ollama run glm4 "Review this Firestore query pattern for performance issues: query.where('t_any_cuisines', arrayContains: 'french').where('t_log_type', isEqualTo: 'tripledb')" --verbose

# 3c. Verify VRAM stays under 8 GB for each
nvidia-smi
# Check: each model should show <7 GB VRAM usage individually
```

---

## STEP 4: Configure Firebase MCP (20 min)

```fish
# 4a. Ensure firebase-tools is current
npx firebase-tools@latest --version

# 4b. Verify Firebase auth
npx firebase-tools@latest login:list
# Should show authenticated account with kjtcom-c78cd access

# 4c. Create .mcp.json for Claude Code
cd ~/dev/projects/kjtcom

printf '{
  "mcpServers": {
    "firebase": {
      "command": "npx",
      "args": ["-y", "firebase-tools@latest", "experimental:mcp"]
    }
  }
}
' > .mcp.json

# 4d. Test Firebase MCP (via Claude Code)
# Launch Claude Code and verify:
# - "Get project info for kjtcom-c78cd"
# - "List collections in default database"
# - "Get Firestore security rules"
# - "Get 3 documents from locations collection"
```

**Verification:** Claude Code should be able to query Firestore documents via MCP without manual Admin SDK scripts.

---

## STEP 5: Configure Context7 MCP (10 min)

```fish
# 5a. Add to .mcp.json
cd ~/dev/projects/kjtcom

# Edit .mcp.json to add Context7
# (use the agent or manual edit - do not overwrite Firebase config)

# Final .mcp.json should look like:
# {
#   "mcpServers": {
#     "firebase": {
#       "command": "npx",
#       "args": ["-y", "firebase-tools@latest", "experimental:mcp"]
#     },
#     "context7": {
#       "command": "npx",
#       "args": ["-y", "@upstash/context7-mcp@latest"]
#     }
#   }
# }

# 5b. Test Context7 MCP (via Claude Code)
# Launch Claude Code and verify:
# - "Look up the current flutter_riverpod API for StateProvider"
# - "Get the flutter_map 7.x API for TileLayer"
```

---

## STEP 6: Configure Firecrawl MCP (15 min)

```fish
# 6a. Get Firecrawl API key (if not already set)
# Visit firecrawl.dev for API key
# Add to config.fish:
# set -gx FIRECRAWL_API_KEY "your-key-here"

# 6b. Add to .mcp.json
# {
#   "firecrawl": {
#     "command": "npx",
#     "args": ["-y", "firecrawl-mcp"],
#     "env": {
#       "FIRECRAWL_API_KEY": "<key>"
#     }
#   }
# }

# 6c. Test Firecrawl MCP (via Claude Code)
# - "Scrape the Panther SIEM search documentation at docs.panther.com/search"
```

**Note:** If Firecrawl requires a paid API key, defer to v9.36 and document in build log. Do not block the iteration on this.

---

## STEP 7: Configure Playwright MCP (10 min)

```fish
# 7a. Add to .mcp.json
# {
#   "playwright": {
#     "command": "npx",
#     "args": ["-y", "@anthropic/mcp-playwright"]
#   }
# }

# 7b. Install Playwright browsers
npx playwright install chromium

# 7c. Test Playwright MCP (via Claude Code)
# - "Navigate to kylejeromethompson.com and take a screenshot"
# - Note: G47 means no DOM interaction with CanvasKit, but screenshots work
```

---

## STEP 8: Configure Dart/Flutter MCP (10 min)

```fish
# 8a. Search for official Dart MCP
# Check: https://github.com/anthropics/mcp-dart or similar

# 8b. If available, add to .mcp.json
# {
#   "dart": {
#     "command": "npx",
#     "args": ["-y", "@anthropic/mcp-dart"]
#   }
# }

# 8c. If not available, document as "P3 - deferred to v9.36"
```

**Self-healing:** The Dart/Flutter MCP may not exist as a stable package yet. If so, skip and note in build log. This is P3 priority.

---

## STEP 9: Configure Gemini CLI MCP Servers (15 min)

```fish
# 9a. Create Gemini MCP config
mkdir -p ~/dev/projects/kjtcom/.gemini

printf '{
  "mcpServers": {
    "firebase": {
      "command": "npx",
      "args": ["-y", "firebase-tools@latest", "experimental:mcp"]
    },
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp@latest"]
    }
  }
}
' > ~/dev/projects/kjtcom/.gemini/settings.json

# 9b. Verify Gemini CLI picks up the config
# Launch gemini and test:
# - "List Firestore collections in my project"
```

---

## STEP 10: Update Agent Instruction Files (15 min)

### CLAUDE.md Updates

Append to CLAUDE.md:

```markdown
## Multi-Agent Orchestration - MANDATORY (v9.35+)

* Every iteration MUST consult at least 2 LLMs before executing changes
* Available local models: qwen3.5:9b, nemotron-nano, glm4 (via Ollama at localhost:11434)
* Consult local model for: approach analysis, code review, alternative solutions
* Use Firebase MCP to validate Firestore state before and after changes
* Use Context7 MCP to fetch current API docs before making API calls
* Document agent consultations in the build log "Agent Orchestration" section
```

### GEMINI.md Updates

Append the same orchestration mandate to GEMINI.md.

---

## STEP 11: Verify Complete Harness (15 min)

```fish
# 11a. Verify Ollama models
ollama list
# Expected: 3 models listed

# 11b. Verify MCP servers (Claude Code)
# Launch Claude Code in ~/dev/projects/kjtcom
# Run: "List all available MCP tools"
# Expected: Firebase tools, Context7 tools, Playwright tools visible

# 11c. End-to-end orchestration test
# Ask Claude Code:
# "Query Firestore for 3 TripleDB entities, then ask Qwen3.5-9B
#  via curl to localhost:11434 to analyze the schema structure"

# 11d. Verify no VRAM conflicts
nvidia-smi
# Should show: Ollama process using VRAM for whichever model was last loaded
```

---

## STEP 12: Produce Artifacts (15 min)

- [ ] docs/kjtcom-design-v9.35.md - This design doc (copy from Claude output)
- [ ] docs/kjtcom-plan-v9.35.md - This plan doc (copy from Claude output)
- [ ] docs/kjtcom-build-v9.35.md - Session transcript (Claude Code generates)
- [ ] docs/kjtcom-report-v9.35.md - Metrics + Agent Orchestration section
- [ ] docs/kjtcom-changelog.md - Append v9.35 entry
- [ ] CLAUDE.md - Updated with orchestration mandate
- [ ] GEMINI.md - Updated with orchestration mandate
- [ ] .mcp.json - Created with all MCP server configs
- [ ] .gemini/settings.json - Created with Gemini MCP configs

---

## POST-FLIGHT CHECKLIST

- [ ] All 3 local LLMs respond to queries
- [ ] Firebase MCP can read Firestore documents
- [ ] Context7 MCP can fetch Flutter documentation
- [ ] Playwright MCP can take screenshots of kylejeromethompson.com
- [ ] Firecrawl MCP configured (or deferred with documentation)
- [ ] Dart/Flutter MCP configured (or deferred with documentation)
- [ ] CLAUDE.md updated with orchestration mandate
- [ ] GEMINI.md updated with orchestration mandate
- [ ] All 4 IAO artifacts produced (design, plan, build, report)
- [ ] Changelog appended
- [ ] No Flutter app changes (infrastructure-only iteration)
- [ ] `flutter analyze` still shows 0 issues (no regression)
- [ ] `flutter test` still passes (no regression)

---

## INTERVENTION POINTS

These are the only questions the agent should need to ask Kyle:

1. **Firecrawl API key** - Does Kyle have one, or should we defer?
2. **Nemotron model tag** - If `ollama search nemotron` returns unexpected results
3. **GLM model tag** - If `ollama search glm` returns unexpected results

All other decisions are pre-answered in this plan. Zero-intervention target: 0.

---

*Plan document generated from claude.ai Opus 4.6 session, April 4, 2026.*
