# kjtcom - Report v9.35

**Phase:** 9 - App Optimization
**Iteration:** 35
**Date:** April 4, 2026
**Executing Agent:** Claude Code (Opus 4.6)
**Focus:** Multi-Agent Orchestration Restoration + LLM/MCP Infrastructure

---

## Executive Summary

v9.35 restored IAO Pillar 2 (Agentic Orchestration) by deploying 3 local LLMs and configuring 4 MCP servers. This was an infrastructure-only iteration - zero Flutter app changes, zero regressions.

---

## Metrics

| Metric | Value | Change from v9.34 |
|--------|-------|--------------------|
| Total entities | 6,181 | No change |
| Pipelines | 3 | No change |
| Flutter LOC | ~4,200 | No change |
| Dart files | 25 | No change |
| flutter analyze | 0 issues | No change |
| flutter test | 15/15 pass | No change |
| Gotchas | 44 (G1-G50) | No change |
| Local LLMs deployed | 3 | +3 (NEW) |
| MCP servers configured | 4 | +4 (NEW) |
| Iterations with orchestration | 2 of 35 | +1 |
| Kyle interventions | 1 (API key) | Target was 0 |

---

## Local LLM Deployment

| Model | Ollama Tag | Disk | VRAM | Speed | Status |
|-------|-----------|------|------|-------|--------|
| Qwen3.5-9B | qwen3.5:9b | 6.6 GB | ~5.1 GB | 54-58 t/s | DEPLOYED |
| Nemotron Mini 4B | nemotron-mini:4b | 2.7 GB | ~2.7 GB | Fast | DEPLOYED |
| GLM-4.6V-Flash-9B | haervwe/GLM-4.6V-Flash-9B | 8.0 GB | ~4.8 GB | ~5.4 t/s | DEPLOYED |

**Total disk:** 17.3 GB. **Max VRAM (single model):** ~5.1 GB. All fit in 8 GB RTX 2080 SUPER.

**Key decisions:**
- `nemotron-nano` tag does not exist -> used `nemotron-mini:4b` (NVIDIA's 4B instruct model)
- `glm4` is text-only, `glm-4.6` is cloud-only -> used community upload `haervwe/GLM-4.6V-Flash-9B`
- Removed pre-existing `nemotron:latest` (42 GB) - unusable on 8 GB GPU

---

## MCP Server Configuration

| Server | Package | Config File | Status |
|--------|---------|-------------|--------|
| Firebase MCP | firebase-tools@15.13.0 | .mcp.json + .gemini/settings.json | CONFIGURED |
| Context7 MCP | @upstash/context7-mcp | .mcp.json + .gemini/settings.json | CONFIGURED |
| Firecrawl MCP | firecrawl-mcp@3.11.0 | .mcp.json | CONFIGURED |
| Playwright MCP | @playwright/mcp@0.0.70 | .mcp.json | CONFIGURED |
| Dart/Flutter MCP | @anthropic/mcp-dart | N/A | DEFERRED (package does not exist) |

**Connection testing:** Deferred to next session launch. MCP servers load from .mcp.json on Claude Code startup.

---

## Files Created/Modified

| File | Action | Purpose |
|------|--------|---------|
| .mcp.json | CREATED | Claude Code MCP server config (4 servers) |
| .gemini/settings.json | CREATED | Gemini CLI MCP server config (2 servers) |
| CLAUDE.md | MODIFIED | Updated model names to match installed tags |
| GEMINI.md | REWRITTEN | Full v9.35+ agent instructions with orchestration mandate |
| docs/install.fish | MODIFIED | Added Ollama + local LLM install step (5b/10) |
| docs/kjtcom-design-v9.35.md | PRE-EXISTING | Created by Kyle via claude.ai session |
| docs/kjtcom-plan-v9.35.md | PRE-EXISTING | Created by Kyle via claude.ai session |
| docs/kjtcom-build-v9.35.md | CREATED | This session's build log |
| docs/kjtcom-report-v9.35.md | CREATED | This document |
| docs/kjtcom-changelog.md | APPENDED | v9.35 entry |

---

## Intervention Log

| # | Type | Description | Resolution |
|---|------|-------------|------------|
| 1 | API Key | Firecrawl API key not in fish env | Kyle added to config.fish manually |

**Target:** 0 interventions. **Actual:** 1. The Firecrawl key was a pre-existing gap, not a plan failure.

---

## Agent Orchestration

### LLMs Consulted (Minimum: 2)

1. **Claude Code (Opus 4.6)** - Primary executor. All infrastructure deployment, config creation, artifact generation.
2. **Qwen3.5-9B (local, Ollama)** - Code review of .mcp.json config. Raised 3 points: 1 valid (firebase version - verified OK), 1 incorrect (package name), 1 style note (version pinning - accepted).
3. **Nemotron Mini 4B (local, Ollama)** - VRAM and response verification test.
4. **GLM-4.6V-Flash-9B (local, Ollama)** - VRAM and response verification test.

### MCP Servers Used

None. This iteration configured the MCP servers. They will be active starting v9.36.

### Key Decisions Influenced by Multi-Agent Input

- Qwen3.5-9B suggested `@firecrawl/mcp` as the correct package name. This was **overridden** after npm verification confirmed `firecrawl-mcp` is the correct package (v3.11.0, MIT license, 72 versions).
- Qwen3.5-9B flagged firebase-tools version requirement. This was **validated** - v15.13.0 is well above the minimum.

### MCP Servers Skipped

| Server | Reason |
|--------|--------|
| Firebase MCP | Infrastructure iteration - configuring, not using |
| Context7 MCP | No Flutter API calls in this iteration |
| Firecrawl MCP | No UI scraping needed |
| Playwright MCP | No deployment to smoke test |
| Dart/Flutter MCP | Package does not exist on npm |

---

## Post-Flight Checklist

- [x] All 3 local LLMs respond to queries
- [x] VRAM fits within 8 GB for each model individually
- [x] .mcp.json created with 4 MCP server configs
- [x] .gemini/settings.json created with 2 MCP server configs
- [x] Dart/Flutter MCP documented as deferred (P3)
- [x] CLAUDE.md updated with correct model names
- [x] GEMINI.md rewritten with v9.35+ orchestration mandate
- [x] docs/install.fish updated with Ollama model pulls
- [x] All 4 IAO artifacts produced (design, plan, build, report)
- [x] Changelog appended
- [x] No Flutter app changes (infrastructure-only iteration)
- [x] flutter analyze: 0 issues
- [x] flutter test: 15/15 pass
- [ ] MCP server connection test (requires session restart)
- [ ] Playwright browser install (requires npx playwright install chromium)

---

*Report generated by Claude Code (Opus 4.6), April 4, 2026.*
