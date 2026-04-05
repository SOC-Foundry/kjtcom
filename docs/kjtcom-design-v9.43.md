# kjtcom - Design Document v9.43

**Phase:** 9 - App Optimization
**Iteration:** 43
**Date:** April 5, 2026
**Focus:** Bot Session Memory + Rating Queries + Post-Flight Verification + Architecture HTML + Qwen Report Quality

---

## AMENDMENTS (all prior amendments remain in effect)

### Post-Flight Verification - MANDATORY (v9.43+)

After every iteration, BEFORE the session ends, the executing agent MUST:

1. Verify kylejeromethompson.com loads: `curl -s -o /dev/null -w "%{http_code}" https://kylejeromethompson.com` -> expect 200
2. Run a test query via the Flutter app using Playwright MCP (or verify via curl to Cloud Functions search endpoint if G47 blocks)
3. Send `/status` to @kjtcom_iao_bot via Telegram bot API and verify response
4. Send `/ask how many entities are in the database` and verify count is >= 6,181
5. Log all verification results in the build log under a POST-FLIGHT VERIFICATION section
6. If ANY check fails, log as gotcha and do NOT mark the iteration complete

This is non-negotiable. The v9.42 report claimed 6 workstreams complete but nobody verified the site still worked or that the bot answered correctly.

### Qwen Claim Audit - MANDATORY (v9.43+)

Every workstream Qwen marks "complete" MUST have a verifiable artifact or test result linked in the report:
- File exists on disk (ls -la path)
- Command produced expected output (captured in build log)
- Test passed (flutter test output)
- Bot responded correctly (Telegram API response)
- Site loaded (curl HTTP status)

"Complete" without linked evidence is reclassified as "unverified." The Workstream Scorecard in the report must include an Evidence column.

Qwen is PROHIBITED from inventing MCP server names. The only valid MCP servers are: Firebase, Context7, Firecrawl, Playwright, Dart. If a workstream did not use an MCP, the column is "-", not a fabricated name.

### Qwen Report Quality - MANDATORY (v9.43+)

The evaluator prompt for Qwen must require:
- Specific numbers (entity counts, file counts, chunk counts, test results)
- No "TBD" in Trident evaluation - fill from event log and execution context
- No corporate fluff ("delivered a successful deployment") - state what was built and what it does
- Next iteration candidates must list at least 3 concrete items from execution findings
- Event count must match between build log and report

### Doc Archival - MANDATORY (v9.43+)

Previous iteration docs MUST be moved to docs/archive/, NEVER deleted. The v9.42 build deleted v9.41 docs instead of archiving them. This is a regression. Recovery: `git checkout HEAD~1 -- docs/kjtcom-*-v9.41.md` then `mv docs/kjtcom-*-v9.41.md docs/archive/`

---

## AGENT SESSION BEST PRACTICES (v9.42+ - PERMANENT, reproduced for continuity)

### Pre-Launch Checklist
1. CLAUDE.md and GEMINI.md saved to disk in launch directory BEFORE starting.
2. /quit every session and start fresh between iterations.
3. `set -gx IAO_ITERATION v9.XX` BEFORE launching.
4. Verify Ollama: `ollama list` shows 4 models.
5. Restart Telegram bot systemd service between iterations.
6. Verify Firebase SA: `test -f ~/.config/gcloud/kjtcom-sa.json`.

### Session Discipline
- ONE iteration per session. Never chain.
- If session crashes, /quit and relaunch. Do not recover mid-session.
- Every session ends with artifact production + post-flight verification.
- Drafts cross-checked and promoted before session ends.
- Harness files GROW. Never abbreviate.

---

## WORKSTREAMS

| # | Workstream | Priority | Description |
|---|-----------|----------|-------------|
| W1 | Bot session memory | P1 | Store last query context per Telegram user_id. "those 26" resolves to previous result set. |
| W2 | Rating-aware queries | P1 | Add t_enrichment.google_places.rating to schema reference. Support "highest rated" and "top N" queries. |
| W3 | Post-flight verification implementation | P1 | Add verification script + update evaluator prompt for Qwen claim audit. Recover v9.41 archived docs. |
| W4 | Architecture diagram HTML page | P1 | Standalone HTML renderer for architecture.mmd. Deploy to Firebase. Link from README. |
| W5 | Qwen evaluator prompt overhaul | P2 | Fix MCP hallucination, require specific numbers, eliminate TBD, add Evidence column to scorecard. |
| W6 | Verify v9.42 data integrity | P2 | Confirm county enrichment results (918/1100?), verify Dallas Italian query, audit schema_reference.json accuracy. |

---

## W1: Bot Session Memory (P1)

The Telegram bot is stateless. Each /ask is independent. The screenshot showed: user asks "how many ddd restaurants in los angeles" (26 results), then "out of those 26, what are the 3 highest rated?" - bot dumps all 6,181 entities because it has no concept of "those 26."

### Implementation

Simple in-memory dict keyed by Telegram user_id:

```python
# In telegram_bot.py, module level
user_sessions = {}

# After each /ask that goes to Firestore:
user_sessions[user_id] = {
    "filters": route["filters"],
    "results": docs,  # the actual result set
    "count": len(docs),
    "timestamp": time.time()
}

# Before routing, check for context references:
def resolve_context(question, user_id):
    """Detect references to previous results and inject context."""
    context_words = ["those", "them", "the results", "that list", "from before"]
    if any(word in question.lower() for word in context_words):
        session = user_sessions.get(user_id)
        if session and (time.time() - session["timestamp"]) < 600:  # 10 min TTL
            return session
    return None
```

When context is detected, pass the previous result set to Gemini Flash instead of re-querying Firestore. Gemini can then answer "what are the 3 highest rated" by examining the result set's rating data.

### Session TTL

10 minutes. After that, context expires and questions are treated as fresh. No persistence needed - dict lives in process memory, lost on restart (acceptable for now).

---

## W2: Rating-Aware Queries (P1)

The intent router doesn't know about ratings. When someone asks "highest rated," Gemini Flash has no schema reference to map that to a sortable field.

### Schema Reference Update

Add to data/schema_reference.json:

```json
{
  "sortable_fields": {
    "t_enrichment.google_places.rating": {
      "type": "number",
      "range": "1.0-5.0",
      "description": "Google Places star rating",
      "aliases": ["rating", "rated", "stars", "best", "highest rated", "top"]
    },
    "t_enrichment.google_places.user_ratings_total": {
      "type": "number",
      "description": "Number of Google Places reviews",
      "aliases": ["most reviewed", "popular", "most ratings"]
    }
  }
}
```

### Updated Routing Prompt

Add to the router prompt:
```
- If user asks for "highest rated", "best", "top N" -> add "sort": "t_enrichment.google_places.rating" and "sort_order": "desc" and "limit": N to the response
- If user asks for "most reviewed" or "most popular" -> sort by t_enrichment.google_places.user_ratings_total desc
```

### Firestore Query Update

```python
# In firestore_query.py
if sort_field:
    query = query.order_by(sort_field, direction=firestore.Query.DESCENDING)
if limit:
    query = query.limit(limit)
```

Note: Firestore orderBy on nested fields (t_enrichment.google_places.rating) requires a composite index. May need to create one via firebase.indexes.json or the Firebase console.

---

## W3: Post-Flight Verification + Doc Recovery (P1)

### scripts/post_flight.py (NEW)

```python
"""Post-flight verification for kjtcom iterations."""
import requests
import subprocess
import json
from utils.iao_logger import log_event

def verify_site():
    """Check kylejeromethompson.com returns 200."""
    r = requests.get("https://kylejeromethompson.com", timeout=10)
    return r.status_code == 200

def verify_bot():
    """Send /status to Telegram bot via API."""
    token = os.environ["KJTCOM_TELEGRAM_BOT_TOKEN"]
    # Use getUpdates or sendMessage to a test chat
    # Return True if bot responds within 30 seconds
    ...

def verify_query():
    """Send /ask test query and verify response."""
    # /ask how many entities are in the database
    # Expect: >= 6181
    ...

def run_all():
    results = {}
    results["site_200"] = verify_site()
    results["bot_status"] = verify_bot()
    results["bot_query"] = verify_query()
    for check, passed in results.items():
        status = "PASS" if passed else "FAIL"
        log_event("command", "post-flight", check, status)
        print(f"  {status}: {check}")
    return all(results.values())
```

### Doc Recovery

```fish
# Recover v9.41 docs deleted in v9.42
cd ~/dev/projects/kjtcom
git checkout HEAD~1 -- docs/kjtcom-design-v9.41.md docs/kjtcom-plan-v9.41.md docs/kjtcom-build-v9.41.md docs/kjtcom-report-v9.41.md
mv docs/kjtcom-*-v9.41.md docs/archive/
```

---

## W4: Architecture Diagram HTML Page (P1)

### Standalone HTML Renderer

Create app/web/architecture.html - a dark-themed HTML page that loads Mermaid JS from CDN and renders the architecture.mmd content inline. Deployed alongside the Flutter app on Firebase Hosting.

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>kjtcom Architecture</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <style>
        body {
            background: #0D1117;
            color: #4ADE80;
            font-family: 'Geist Sans', sans-serif;
            margin: 0;
            padding: 20px;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        h1 {
            font-family: 'Cinzel', serif;
            color: #4ADE80;
            border-bottom: 1px solid #4ADE80;
            padding-bottom: 10px;
        }
        .mermaid {
            width: 100%;
            max-width: 1400px;
        }
        .meta {
            color: #6B7280;
            font-size: 0.85rem;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <h1>kjtcom Architecture</h1>
    <div class="meta">Living document - updated every iteration | Phase 9 v9.43</div>
    <div class="mermaid">
        [architecture.mmd content inserted here by build script]
    </div>
    <script>
        mermaid.initialize({
            startOnLoad: true,
            theme: 'dark',
            themeVariables: {
                primaryColor: '#161B22',
                primaryTextColor: '#4ADE80',
                primaryBorderColor: '#4ADE80',
                lineColor: '#4ADE80',
                secondaryColor: '#0D9488',
                tertiaryColor: '#161B22'
            }
        });
    </script>
</body>
</html>
```

### Build Integration

Add a step to the deploy process that reads docs/kjtcom-architecture.mmd and injects the content (minus the %% comment lines) into the HTML template. The HTML file goes into app/web/ so it's included in the Flutter web build output.

### README Update

Add to README.md Architecture section:

```markdown
**[Interactive Architecture Diagram](https://kylejeromethompson.com/architecture.html)** |
[Mermaid Source](docs/kjtcom-architecture.mmd)
```

---

## W5: Qwen Evaluator Prompt Overhaul (P2)

### Updated Evaluator Prompt Requirements

The prompt sent to Qwen for draft generation must include:

1. "Include specific numbers from the event log and execution output. Never write TBD."
2. "The only valid MCP servers are: Firebase, Context7, Firecrawl, Playwright, Dart. If a workstream did not use an MCP, write '-' in the MCP column."
3. "The Workstream Scorecard must include an Evidence column with a file path, command output, or test result that proves the outcome."
4. "Event counts in the build log and report must match exactly."
5. "Next iteration candidates must list at least 3 concrete items."
6. "Do not use corporate language like 'delivered a successful deployment.' State what was built and what it does."

### Updated Scorecard Format

```markdown
| W# | Name | Priority | Outcome | Evidence | Agents | LLMs | MCPs | Score |
|----|------|----------|---------|----------|--------|------|------|-------|
| W1 | ... | P1 | Complete | enrich_counties.py exists, 918 entities enriched | claude-code | gemini-2.5-flash | Firebase | 9/10 |
```

---

## W6: Verify v9.42 Data Integrity (P2)

1. Query Firestore: how many TripleDB entities now have t_any_counties populated? (Expected: ~918 from screenshot)
2. Query: "Italian restaurants in Dallas Texas on DDD" - verify whether 0 results is correct (no Italian-tagged restaurants in Dallas) or a routing bug
3. Verify schema_reference.json accurately reflects which fields are populated per pipeline
4. Run /ask test queries from the design doc testing checklist and document actual results
5. Verify the bot's web route works: /ask does guidepoint global provide professional services

---

## TRIDENT

| Prong | Target |
|-------|--------|
| Cost | $0. <50K Claude tokens. Gemini Flash free tier. |
| Delivery | 6 workstreams. Bot remembers context. Ratings sortable. Architecture rendered as HTML. |
| Performance | /ask "out of those 26, what are the 3 highest rated" returns top 3 by Google Places rating. Post-flight passes. |

---

*Design document v9.43, April 5, 2026.*
