# kjtcom - Execution Plan v9.36

**Phase:** 9 - App Optimization
**Iteration:** 36
**Date:** April 4, 2026
**Executing Agent:** Claude Code (Opus 4.6)
**Estimated Duration:** 2-3 hours

---

## PRE-FLIGHT CHECKLIST

- [ ] Ollama running (`systemctl status ollama`)
- [ ] 3 models available (`ollama list` -> qwen3.5:9b, nemotron-mini:4b, haervwe/GLM-4.6V-Flash-9B)
- [ ] .mcp.json present at repo root with 4 servers
- [ ] MCP servers loading in Claude Code (check tool list)
- [ ] v9.35 docs archived (`ls docs/archive/*v9.35*`)
- [ ] Chrome open with Panther Search tab (Process ID 151239)
- [ ] Working directory: ~/dev/projects/kjtcom

---

## STEP 1: Install Playwright Browsers (5 min)

Deferred from v9.35. Required for W1 and W3.

```fish
npx playwright install chromium
```

**Verification:** `npx playwright --version` returns version number.

---

## STEP 2: MCP Server Validation (15 min)

First live test of all 4 MCP servers. This is your first session with .mcp.json loaded.

| # | Server | Test | Expected Result |
|---|--------|------|-----------------|
| 2a | Firebase MCP | Get 3 docs from locations collection | 3 Firestore documents with t_any_* fields |
| 2b | Context7 MCP | Look up flutter_riverpod StateProvider | Current Riverpod API reference |
| 2c | Firecrawl MCP | Scrape docs.panther.com/search | Panther search documentation text |
| 2d | Playwright MCP | Screenshot kylejeromethompson.com | PNG of live site |

Log each result in build doc. If a server fails, note the error and continue.

---

## STEP 3: Panther CDP Connection (20 min)

### 3a. Check if Chrome remote debugging is active

```fish
curl -s http://localhost:9222/json/version 2>/dev/null
```

- If returns JSON -> debug port is active. Proceed to 3b.
- If connection refused -> Kyle must restart Chrome with debug flag:
  ```fish
  # Kyle runs this. Cookie session persists. No MFA needed.
  google-chrome-stable --remote-debugging-port=9222
  # Navigate back to tachtech.runpanther.net -> Investigate -> Search
  ```
  This is the ONLY expected intervention.

### 3b. List available tabs

```fish
curl -s http://localhost:9222/json/list | python3 -c "
import sys, json
tabs = json.load(sys.stdin)
for t in tabs:
    print(f'{t.get(\"id\", \"?\")} | {t.get(\"title\", \"?\")} | {t.get(\"url\", \"?\")}')" 
```

Find the tab with "panther" or "Search" in title/URL. Note its webSocketDebuggerUrl.

### 3c. Connect via Playwright MCP

Use Playwright MCP to connect to the existing Chrome via CDP and navigate to the Panther Search tab. If Playwright MCP does not support CDP directly, use a script:

```fish
python3 -c "
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp('http://localhost:9222')
        contexts = browser.contexts
        for ctx in contexts:
            for page in ctx.pages:
                if 'panther' in page.url.lower() or 'search' in page.url.lower():
                    print(f'Found Panther tab: {page.url}')
                    # Capture full screenshot
                    await page.screenshot(path='docs/panther-reference/panther-search-full.png', full_page=True)
                    print('Screenshot saved')
                    break

asyncio.run(main())
"
```

**Self-healing:** If CDP connection fails entirely, Kyle takes manual screenshots and saves to docs/panther-reference/. Log as intervention.

---

## STEP 4: Panther UI Capture (30 min)

With CDP connection established, capture each target:

### 4a. Full page screenshot
```python
await page.screenshot(path='docs/panther-reference/panther-search-full.png', full_page=True)
```

### 4b. Query editor DOM
```python
# Try common selectors - inspect page first
editor = await page.query_selector('[class*="search"], [class*="editor"], [class*="query"]')
if editor:
    html = await editor.inner_html()
    # Save to file
```

### 4c. Field sidebar
```python
# Look for SELECTED FIELDS / AVAILABLE FIELDS sections
sidebar = await page.query_selector('[class*="field"], [class*="sidebar"]')
```

### 4d. CSS custom properties
```python
tokens = await page.evaluate('''() => {
    const styles = getComputedStyle(document.documentElement);
    const result = {};
    for (let i = 0; i < styles.length; i++) {
        const prop = styles[i];
        if (prop.startsWith('--')) {
            result[prop] = styles.getPropertyValue(prop).trim();
        }
    }
    return result;
}''')
```

### 4e. Autocomplete capture
```python
# Click into search bar, type a character to trigger autocomplete
search_input = await page.query_selector('input[type="text"], [contenteditable], textarea')
if search_input:
    await search_input.click()
    await search_input.type('p_')
    await page.wait_for_timeout(1000)
    # Capture any dropdown/popup that appeared
    await page.screenshot(path='docs/panther-reference/panther-autocomplete.png')
```

### 4f. Scrape notes
Create `docs/panther-reference/panther-scrape-notes.md` mapping Panther UI elements to kjtcom equivalents:

| Panther Element | kjtcom Equivalent | Notes |
|----------------|-------------------|-------|
| Search bar | QueryEditor | TextField vs code editor |
| p_any_* fields | t_any_* fields | Same pattern |
| Field sidebar | Schema tab | Different placement |
| Time range picker | Not implemented | Future feature |
| "Summarize with AI" | Not implemented | Future feature |
| 100 events count | EntityCountRow | Similar animated count |

**SECURITY:** Before saving any screenshot, verify no customer alert data is visible. If it is, crop the screenshot to show only UI chrome.

---

## STEP 5: Agent Evaluator Middleware Setup (30 min)

### 5a. Create evaluator prompt template

Create `docs/evaluator-prompt.md`:

```markdown
You are the Agent Evaluator for the kjtcom project (IAO methodology).

Review the following iteration artifacts and score each agent.

ITERATION: {version}
BUILD LOG:
{build_log_content}

GOTCHA REGISTRY ACTIVE:
{active_gotchas}

Score each agent 0-10 on:
1. Problem Analysis - Correctly identified the problem and proposed viable approaches?
2. Code Correctness - Code suggestions accurate, functional, regression-free?
3. Efficiency - Tokens consumed vs value delivered?
4. Gotcha Avoidance - Avoided repeating known failure patterns?
5. Novel Contribution - Surfaced approaches or insights others missed?

Output ONLY valid JSON matching this schema:
{
  "iteration": "vX.XX",
  "date": "YYYY-MM-DD",
  "evaluator": "qwen3.5:9b",
  "scores": [
    {
      "agent": "agent-name",
      "role": "role-in-iteration",
      "problem_analysis": 0,
      "code_correctness": 0,
      "efficiency": 0,
      "gotcha_avoidance": 0,
      "novel_contribution": 0,
      "total": 0,
      "notes": "Brief justification"
    }
  ],
  "gotcha_events": []
}
```

### 5b. Run evaluator against v9.35

Feed the v9.35 build log to Qwen3.5-9B via Ollama API:

```fish
# Read build log, pipe to evaluator
set BUILD_LOG (cat docs/archive/kjtcom-build-v9.35.md)
set PROMPT (cat docs/evaluator-prompt.md | sed "s|{version}|v9.35|" | sed "s|{build_log_content}|$BUILD_LOG|" | sed "s|{active_gotchas}|G45,G47,G34,G1,G11|")

curl -s http://localhost:11434/api/chat -d "{
  \"model\": \"qwen3.5:9b\",
  \"messages\": [{\"role\": \"user\", \"content\": $(echo $PROMPT | python3 -c 'import sys,json; print(json.dumps(sys.stdin.read()))')}],
  \"stream\": false,
  \"options\": {\"num_predict\": 2048}
}" | python3 -c "import sys,json; print(json.load(sys.stdin)['message']['content'])"
```

### 5c. Create agent_scores.json

Take the Qwen output, validate it's proper JSON, save to `agent_scores.json` at repo root.

### 5d. Also score v9.36 at end of iteration

After all workstreams complete, run the evaluator again against the v9.36 build log. Append to agent_scores.json.

---

## STEP 6: Consult Qwen3.5-9B on Panther Strategy (10 min)

MANDATORY orchestration step. Before starting Step 3, ask Qwen:

```fish
ollama run qwen3.5:9b "I need to scrape the Panther SIEM query editor UI from an existing authenticated Chrome session via Playwright CDP on port 9222. What DOM selectors should I try for: 1) the search/query input area, 2) the field sidebar showing available log fields, 3) any autocomplete dropdown? Panther is a React app. Give me specific CSS selector strategies." --verbose
```

Document the response and whether it influenced the capture approach.

---

## STEP 7: Produce Artifacts (15 min)

- [ ] docs/kjtcom-design-v9.36.md (from claude.ai session)
- [ ] docs/kjtcom-plan-v9.36.md (from claude.ai session)
- [ ] docs/kjtcom-build-v9.36.md (session transcript)
- [ ] docs/kjtcom-report-v9.36.md (metrics + Agent Scorecard)
- [ ] docs/kjtcom-changelog.md (append v9.36)
- [ ] agent_scores.json (new - v9.35 + v9.36 scores)
- [ ] docs/evaluator-prompt.md (new)
- [ ] docs/panther-reference/ (new directory with captures)
- [ ] docs/install.fish (update if any new deps added)

---

## POST-FLIGHT CHECKLIST

- [ ] All 4 MCP servers tested and results logged
- [ ] Panther screenshots and DOM captures saved
- [ ] No customer data in saved captures
- [ ] agent_scores.json created with v9.35 + v9.36 scores
- [ ] evaluator-prompt.md created
- [ ] All 4 IAO artifacts produced
- [ ] Changelog appended
- [ ] install.fish updated (or confirmed no new deps)
- [ ] flutter analyze: 0 issues
- [ ] flutter test: 15/15 pass
- [ ] Agent Scorecard included in report

---

## INTERVENTION POINTS

| # | Trigger | Expected Resolution |
|---|---------|---------------------|
| 1 | Chrome debug port not active | Kyle restarts Chrome with --remote-debugging-port=9222. Cookies persist. No MFA. |

All other decisions pre-answered. Zero-intervention target: 1.

---

*Plan document generated from claude.ai Opus 4.6 session, April 4, 2026.*
