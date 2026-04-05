# kjtcom - Build Log v9.36

**Phase:** 9 - App Optimization
**Iteration:** 36
**Date:** April 4, 2026
**Executing Agent:** Claude Code (Opus 4.6)
**Focus:** Panther SIEM Scrape + Agent Evaluator Middleware + MCP Validation

---

## PRE-FLIGHT

- Ollama 0.20.2: running (active for 1h 30min)
- 3 models available: qwen3.5:9b (6.6 GB), nemotron-mini:4b (2.7 GB), haervwe/GLM-4.6V-Flash-9B (8.0 GB)
- .mcp.json present with 4 servers (Firebase, Context7, Firecrawl, Playwright)
- v9.35 docs pre-archived by Kyle to docs/archive/
- Chrome open with Panther Search tab (Process ID 151239)
- Chrome remote debugging port 9222: NOT ACTIVE (expected intervention #1)
- Working directory: ~/dev/projects/kjtcom
- flutter analyze/test: deferred (no Flutter changes in this iteration)

---

## STEP 1: Install Playwright Browsers (COMPLETED)

```
npx playwright install chromium
```

Downloaded Chrome for Testing 147.0.7727.15 (170.4 MiB) and Chrome Headless Shell (112 MiB) to `~/.cache/ms-playwright/chromium-1217`.

**Warning:** OS (CachyOS/Arch) is not officially supported by Playwright - downloaded fallback build for ubuntu24.04-x64. No functional issues observed.

Python playwright package: already installed (verified via pip).

---

## STEP 2: MCP Server Validation (COMPLETED)

First live test of all 4 MCP servers from v9.35 .mcp.json configuration.

### 2a. Firebase MCP - FAIL

**Test:** List 3 documents from locations collection.
**Result:** `Authentication Error: Your credentials are no longer valid. Please run firebase login --reauth`
**Root cause:** Firebase token expired since last session. Requires interactive reauth.
**New gotcha:** G53 - Firebase MCP requires fresh `firebase login --reauth` each session.

### 2b. Context7 MCP - PASS

**Test 1:** Resolve library ID for Playwright.
**Result:** Found `/microsoft/playwright` with 4,366 code snippets, High reputation, benchmark score 92.05.

**Test 2:** Query Playwright CDP connection docs.
**Result:** Returned `connectOverCDP('http://localhost:9222')` API reference with examples in JS, Python, Java, C#. Confirmed the CDP connection approach for W1.

### 2c. Firecrawl MCP - NOT LOADED

**Test:** Attempted to search for Firecrawl tools in deferred tool list.
**Result:** No matching deferred tools found. Firecrawl MCP server did not start/load despite being in .mcp.json.
**API key:** Verified SET in fish environment.
**Root cause:** Unknown - likely npx startup failure or package issue. Requires investigation.
**New gotcha:** G52 - Firecrawl MCP not loading - tools not in deferred list despite .mcp.json config.

### 2d. Playwright MCP - PASS

**Test:** Navigate to kylejeromethompson.com and take screenshot.
**Result:** Successfully navigated, page title "kjtcom - Location Intelligence", screenshot captured showing 6,181 entities across 62 countries with full SIEM UI. Saved to `docs/panther-reference/kjtcom-playwright-test.png`.

### MCP Validation Summary

| Server | Status | Notes |
|--------|--------|-------|
| Firebase MCP | FAIL | Needs `firebase login --reauth` (G53) |
| Context7 MCP | PASS | Resolved library + queried CDP docs |
| Firecrawl MCP | NOT LOADED | Server did not start (G52) |
| Playwright MCP | PASS | Nav + screenshot successful |

**Result:** 2/4 servers operational. Firebase needs reauth, Firecrawl needs investigation.

---

## STEP 5: Agent Evaluator Middleware Setup (COMPLETED)

### 5a. Created evaluator prompt template

Created `docs/evaluator-prompt.md` with:
- 5 scoring dimensions (Problem Analysis, Code Correctness, Efficiency, Gotcha Avoidance, Novel Contribution)
- 0-10 scale per dimension, 50 max total
- JSON output schema for agent_scores.json
- Placeholders for version, build log content, and active gotchas

### 5b. Created agent_scores.json

Initialized at repo root with empty array. Append-only - never overwrite.

### 5c. Created run_evaluator.py

Automation script at `scripts/run_evaluator.py`:
- Reads build log and evaluator prompt template
- Fills placeholders and calls Qwen3.5-9B via Ollama API
- Extracts JSON from response and validates
- Supports command-line args: version, build_log_path, active_gotchas

### 5d. Ran evaluator against v9.35

**Discovery:** Qwen3.5-9B's default thinking mode produces empty responses when combined with JSON output format. The thinking tokens consume the entire num_predict budget, leaving no tokens for the actual response.

**Fix:** Use `/no_think` prefix in prompts to disable verbose thinking mode. This is now documented as G51.

**Evaluator result (v9.35):**

| Agent | Role | PA | CC | EF | GA | NC | Total |
|-------|------|----|----|----|----|-----|-------|
| Claude Code (Opus 4.6) | Primary executor | 7 | 7 | 7 | 7 | 4 | 32/50 |
| Qwen3.5-9B | Code reviewer | 6 | 6 | 6 | 6 | 4 | 28/50 |
| Nemotron Mini 4B | Verification | 3 | 3 | 3 | 3 | 2 | 14/50 |
| GLM-4.6V-Flash-9B | Verification | 3 | 3 | 3 | 3 | 2 | 14/50 |

Scores saved to agent_scores.json.

---

## STEP 6: Consult Qwen3.5-9B on Panther Strategy (COMPLETED)

**Prompt:** DOM selector strategies for Panther SIEM React app query editor, field sidebar, and autocomplete dropdown.

**Response (8 key points, extracted from garbled terminal output):**

1. **Use Official API:** Recommended Panther API for programmatic queries (noted but not applicable - we want UI structure, not data)
2. **Generic React Selectors:** Target stable attributes like `aria-label`, `data-testid`, `role` instead of CSS classes
3. **Input Areas:** Look for `input[type="text"]` wrapped in `.input-container` or `.query-bar` divs
4. **Field Sidebar:** Inspect for sidebar panes with `role="list"`, `role="tablist"`, or `log-field` keywords
5. **Autocomplete:** Target `role="combobox"`, `role="listbox"`, or `aria-expanded="true"`
6. **CDP Implementation:** Use `page.locator` with `.getByLabel()` or `.getByTestId()` for stability
7. **Timing:** Use `page.waitForTimeout()` or `expect(locator).toBeVisible()` after React state updates
8. **Security:** Session security warning noted

**Impact on approach:** Updated `scripts/panther_scrape.py` to prioritize `data-testid`, `aria-label`, and `role` selectors before falling back to CSS class-based selectors. Added React-aware waiting patterns.

**Terminal output issue:** `ollama run` command produces garbled output due to terminal escape sequences mixing with content. API approach (`curl localhost:11434/api/chat`) produces clean output. Use API for all future Qwen consultations.

---

## STEPS 3-4: Panther SIEM CDP Scrape (BLOCKED - PENDING INTERVENTION)

### 3a. Chrome Debug Port Check

```fish
curl -s http://localhost:9222/json/version
```

**Result:** Connection refused. Chrome was not launched with `--remote-debugging-port=9222`.

**Intervention requested:** Kyle must restart Chrome with debug flag:
```fish
google-chrome-stable --remote-debugging-port=9222
```
Then navigate back to tachtech.runpanther.net -> Investigate -> Search.

Cookie session persists across restart. No MFA needed. This is expected intervention #1.

### Scrape Script Prepared

Created `scripts/panther_scrape.py` with:
- CDP connection to existing Chrome on port 9222
- Automatic Panther tab detection by URL
- 6 capture targets: full screenshot, viewport screenshot, query editor DOM, field sidebar DOM, CSS tokens, DOM structure tree
- Selector strategy informed by Qwen3.5-9B recommendations
- Security: no customer data capture, DOM structure only

**Status:** Script ready. Awaiting Chrome debug port activation.

---

## Agent Orchestration

### LLMs Consulted

| # | Agent | Role | Consultation |
|---|-------|------|-------------|
| 1 | Claude Code (Opus 4.6) | Primary executor | All steps |
| 2 | Qwen3.5-9B (local, Ollama) | DOM selector advisor + evaluator | Panther selector strategy (Step 6) + v9.35 scoring (Step 5d) |

### Qwen3.5-9B Consultation Details

**Consultation 1 - Panther Selectors:**
- Provided 8 recommendations for DOM selector strategy
- Key influence: prioritize `data-testid` and `aria-label` over CSS classes
- Updated scrape script accordingly

**Consultation 2 - v9.35 Evaluation:**
- Scored 4 agents across 5 dimensions
- Claude Code: 32/50, Qwen: 28/50, Nemotron: 14/50, GLM: 14/50
- Noted limitation of not being able to independently verify claims

### MCP Servers Used

| Server | Used | Purpose | Notes |
|--------|------|---------|-------|
| Firebase MCP | ATTEMPTED | Validate Firestore state | FAIL - needs reauth (G53) |
| Context7 MCP | YES | Playwright CDP API docs | PASS - confirmed connect_over_cdp API |
| Firecrawl MCP | NOT LOADED | Panther docs scrape | Server failed to start (G52) |
| Playwright MCP | YES | kjtcom screenshot test | PASS - captured live site |

### Decisions Influenced by Multi-Agent Input

1. **Selector strategy:** Qwen recommended `data-testid` and `aria-label` over CSS classes for React apps. Adopted in panther_scrape.py.
2. **CDP connection pattern:** Context7 MCP confirmed `connect_over_cdp('http://localhost:9222')` as the correct API. Used in scrape script.
3. **Qwen /no_think discovery:** Discovered that Qwen3.5-9B needs `/no_think` prefix for JSON output. Documented as G51.

---

## New Gotchas

| ID | Description | Status | Cause |
|----|-------------|--------|-------|
| G51 | Qwen3.5-9B thinking mode produces empty responses without /no_think prefix | ACTIVE | Default thinking consumes num_predict budget |
| G52 | Firecrawl MCP not loading - tools not in deferred list despite .mcp.json | ACTIVE | npx startup failure or package issue |
| G53 | Firebase MCP requires fresh login (firebase login --reauth) each session | ACTIVE | Token expiration |

---

*Build log generated by Claude Code (Opus 4.6), April 4, 2026.*
