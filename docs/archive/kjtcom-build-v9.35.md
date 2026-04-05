# kjtcom - Build Log v9.35

**Phase:** 9 - App Optimization
**Iteration:** 35
**Date:** April 4, 2026
**Executing Agent:** Claude Code (Opus 4.6)
**Focus:** Multi-Agent Orchestration Restoration + LLM/MCP Infrastructure

---

## PRE-FLIGHT

- Ollama 0.20.2 installed and running
- CUDA detected: RTX 2080 SUPER, 8192 MiB VRAM
- Qwen3.5-9B pre-pulled (6.6 GB on disk)
- nemotron:latest (42 GB) pre-pulled but unusable on 8 GB GPU
- Firebase SA JSON present
- Node.js v25.8.2, npm 11.12.1
- v9.34 docs already archived by Kyle to docs/archive/
- flutter analyze: 0 issues, flutter test: 15/15 pass (pre-flight baseline)

---

## STEP 1: Fix Nemotron Pull (COMPLETED)

**Problem:** `nemotron3-nano:4b` tag does not exist in Ollama registry. `ollama search` command not available in Ollama 0.20.2.

**Resolution:**
1. Web search found correct tag: `nemotron-mini:4b` (NVIDIA Nemotron-Mini-4B-Instruct)
2. `ollama pull nemotron-mini:4b` - SUCCESS (2.7 GB)
3. Removed unusable `nemotron:latest` (42 GB) - `ollama rm nemotron:latest`

**Verification:** `curl localhost:11434/api/chat` with model `nemotron-mini:4b` - responded "Four" to "What is 2+2?" in 8ms eval time.

**Design doc correction:** Model name changed from `nemotron-nano` to `nemotron-mini:4b` throughout.

---

## STEP 2: Pull GLM-4.6V-Flash (COMPLETED)

**Problem:** `glm4` in Ollama registry is text-only. `glm-4.6` exists but is cloud-only (no local weights). No official GLM vision model available for local download.

**Resolution:** Found community upload `haervwe/GLM-4.6V-Flash-9B` (unofficial but functional). Pulled successfully (8.0 GB on disk).

**Verification:** API query returned coherent Flutter description. Output includes `<|begin_of_box|>` formatting tags - content artifact, not an error.

---

## STEP 3: Verify All 3 Local LLMs (COMPLETED)

| Model | Tag | Disk Size | VRAM Used | Response | Status |
|-------|-----|-----------|-----------|----------|--------|
| Qwen3.5-9B | qwen3.5:9b | 6.6 GB | ~5.1 GB | Riverpod explanation (verbose thinking mode) | PASS |
| Nemotron Mini 4B | nemotron-mini:4b | 2.7 GB | ~2.7 GB | "Four" (2 tokens, 8ms) | PASS |
| GLM-4.6V-Flash-9B | haervwe/GLM-4.6V-Flash-9B | 8.0 GB | ~4.8 GB | Flutter description (253 tokens, 47s) | PASS |

**VRAM check:** After GLM load, `nvidia-smi` showed 4756 MiB used, 3023 MiB free. All models fit individually within 8 GB. Sequential loading confirmed - no simultaneous model issues.

**Qwen thinking mode note:** `/set parameter think false` is not a recognized command in Qwen3.5. Thinking fires by default. For fast queries, use `"options": {"num_predict": 1024}` via API to limit output. For complex reasoning, let thinking run with higher num_predict.

---

## STEP 4-5: Create MCP Configs (COMPLETED)

**Created:** `.mcp.json` (Claude Code) with 4 MCP servers:
- `firebase` - npx firebase-tools@latest experimental:mcp
- `context7` - npx @upstash/context7-mcp@latest
- `firecrawl` - npx firecrawl-mcp (API key inherited from shell env)
- `playwright` - npx @playwright/mcp

**Created:** `.gemini/settings.json` (Gemini CLI) with 2 MCP servers:
- `firebase` - npx firebase-tools@latest experimental:mcp
- `context7` - npx @upstash/context7-mcp@latest

**Package verification:**
- `@anthropic/mcp-dart` - NOT FOUND on npm. Dart/Flutter MCP deferred to v9.36.
- `@anthropic/mcp-playwright` - NOT FOUND. Correct package is `@playwright/mcp` (v0.0.70).
- `firecrawl-mcp` - v3.11.0, confirmed on npm.
- `firebase-tools` - v15.13.0, confirmed MCP support.

**Firecrawl API key:** Kyle added to `~/.config/fish/config.fish` during session. Verified SET.

**Security note:** .mcp.json contains NO API keys. Firecrawl key is inherited from shell environment per CLAUDE.md security mandate.

---

## STEP 6: MCP Server Testing (DEFERRED)

MCP servers require a fresh Claude Code session to load from .mcp.json. Testing will occur on next session launch. Configs are syntactically valid JSON (verified).

**Playwright browsers:** Not yet installed. Run `npx playwright install chromium` on next session.

---

## STEP 7-8: Update Agent Instructions (COMPLETED)

**CLAUDE.md:** Updated model names:
- `nemotron-nano` -> `nemotron-mini:4b` (~2.7 GB VRAM)
- `glm4` -> `haervwe/GLM-4.6V-Flash-9B` (~4.8 GB VRAM)

**GEMINI.md:** Full rewrite from v9.34-specific instructions to v9.35+ general-purpose instructions with:
- Updated read order to v9.35 docs
- Added security rules section
- Added full orchestration mandate with correct model names
- Added MCP servers section
- Added permissions, database rules, artifact rules
- Added project context section

---

## STEP 9: Archive v9.34 Docs (COMPLETED - by Kyle)

Kyle pre-archived all 4 v9.34 docs to `docs/archive/` before session start:
- kjtcom-build-v9.34.md
- kjtcom-design-v9.34.md
- kjtcom-plan-v9.34.md
- kjtcom-report-v9.34.md

---

## STEP 10: Living Documents (COMPLETED)

**docs/install.fish:** Added Step 5b/10 for Ollama + local LLMs:
- Ollama installation check
- Model pulls: qwen3.5:9b, nemotron-mini:4b, haervwe/GLM-4.6V-Flash-9B
- Added ollama to verification checks

---

## STEP 11: Flutter Regression Check (COMPLETED)

```
flutter analyze: No issues found! (ran in 0.5s)
flutter test: 15/15 All tests passed!
```

No Flutter app changes in this iteration (infrastructure only). Zero regression.

---

## Agent Orchestration

### LLMs Consulted

| # | Agent | Role | Consultation |
|---|-------|------|-------------|
| 1 | Claude Code (Opus 4.6) | Primary executor | All steps |
| 2 | Qwen3.5-9B (local, Ollama) | Code reviewer | .mcp.json config review |
| 3 | Nemotron Mini 4B (local, Ollama) | Verification | VRAM/response test only |
| 4 | GLM-4.6V-Flash-9B (local, Ollama) | Verification | VRAM/response test only |

### Qwen3.5-9B Consultation Detail

**Prompt:** Review .mcp.json for correctness, missing fields, security issues, package name accuracy.

**Response (3 points):**
1. "Package name is likely incorrect. Use `@firecrawl/mcp`." - INCORRECT. `firecrawl-mcp` verified on npm (v3.11.0).
2. "Ensure firebase-tools is v13.15+ to support experimental:mcp." - VALID concern. Verified at v15.13.0 - OK.
3. "Avoid `-y latest` in production." - NOTED. Acceptable for dev harness. No action.

**Disposition:** 1 valid concern (verified OK), 1 incorrect suggestion (package name), 1 style note (accepted risk). No changes to .mcp.json.

### MCP Servers Used

| Server | Used | Notes |
|--------|------|-------|
| Firebase MCP | NO | Not yet loaded (requires session restart) |
| Context7 MCP | NO | Not yet loaded (requires session restart) |
| Firecrawl MCP | NO | Not yet loaded (requires session restart) |
| Playwright MCP | NO | Not yet loaded (requires session restart) |
| Dart/Flutter MCP | NO | Package does not exist on npm. Deferred to v9.36. |

**Justification:** This is the infrastructure setup iteration. MCP servers are being configured, not used. They will be loaded on next Claude Code or Gemini CLI session launch.

---

*Build log generated by Claude Code (Opus 4.6), April 4, 2026.*
