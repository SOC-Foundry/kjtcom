# kjtcom - Design Document v9.41

**Phase:** 9 - App Optimization
**Iteration:** 41
**Date:** April 5, 2026
**Focus:** Firestore Dual Retrieval Path + Archive Re-embed + Artifact Automation Scaffold

---

## AMENDMENTS (all prior amendments remain in effect)

### Workstream-Level Evaluator Tracking - MANDATORY (v9.41+)

Qwen evaluator scores EACH workstream (W#) individually, not just the iteration as a whole. For every workstream, the evaluator records: outcome (complete/partial/failed/deferred), agents employed, MCP servers used, LLMs invoked, and a per-workstream score (0-10). This data appends to agent_scores.json under a new `workstreams` key per iteration entry. The iteration_registry.json also consumes workstream-level data. The report artifact MUST include a Workstream Scorecard table.

agent_scores.json entry structure (v9.41+):

```json
{
  "iteration": "v9.41",
  "date": "2026-04-05",
  "agents": { ... },
  "workstreams": [
    {
      "id": "W1",
      "name": "Firestore dual retrieval path",
      "priority": "P1",
      "outcome": "complete",
      "agents": ["claude-code"],
      "llms": ["gemini-flash"],
      "mcps": ["firebase"],
      "score": 9,
      "notes": "Intent router + Firestore query module operational"
    }
  ]
}
```

### Gemini Flash Intent Router - NEW (v9.41+)

All Telegram bot /ask queries route through a Gemini Flash intent classification stage before retrieval. Gemini parses user intent against the Thompson Schema field reference and returns a structured JSON routing decision. Future optimization: migrate high-frequency patterns to Python-side classification to reduce token spend (not this iteration - many iterations away).

### Artifact Automation - NEW (v9.41+)

Post-iteration artifact generation (build log, report, changelog entry) should be drafted by local LLM (Qwen) or Gemini Flash from structured inputs (git diff, test output, event log, agent_scores.json). Drafts land in docs/drafts/ for human review before promotion. Design and plan docs remain human-directed via claude.ai session with templated boilerplate.

### Standard Deliverables - MANDATORY (v9.41+)

Every iteration produces 4 artifacts (design, plan, build, report) + updated CLAUDE.md + updated GEMINI.md + launch prompt. All produced in the claude.ai planning session before execution begins.

---

## WORKSTREAMS

| # | Workstream | Priority | Description |
|---|-----------|----------|-------------|
| W1 | Firestore dual retrieval path | P1 | Gemini Flash routes /ask to ChromaDB (dev history) or Firestore (entity data). The bot becomes actually usable. |
| W2 | Re-embed archive with v9.38-v9.40 docs | P1 | Run embed_archive.py so ChromaDB path is current. |
| W3 | Artifact automation scaffold | P2 | generate_artifacts.py + templates. Qwen/Gemini draft post-iteration docs. |
| W4 | Rebuild iteration_registry.json | P2 | Re-run build_registry_v2.py. OOM blocker gone (RAG + think:false). |
| W5 | Living doc updates | P3 | architecture.mmd, install.fish, changelog for W1-W4 changes. |

---

## W1: Firestore Dual Retrieval Path (P1)

This is the primary deliverable. The /ask handler currently only hits ChromaDB, which contains development archive files (design docs, build logs) but NOT the 6,181 Firestore entities. Questions like "how many Italian restaurants in Orange County in DDD" fail because that data lives in Firestore.

### Architecture: 3-Stage Intent Router

**Stage 1 - Route + Structure (Gemini Flash)**

Send user question + compact schema reference to Gemini Flash. Returns structured JSON:

```json
// Entity data question -> Firestore
{
  "route": "firestore",
  "filters": {
    "t_log_type": "tripledb",
    "t_any_cuisines": ["italian"],
    "t_any_counties": ["orange"]
  },
  "intent": "count"
}

// Development history question -> ChromaDB
{
  "route": "chromadb",
  "query": "what caused the G45 cursor bug"
}
```

**Stage 2 - Execution (Python, no LLM)**

For Firestore route: build query from filters using Firebase Admin SDK. Execute against locations collection. Format results.

For ChromaDB route: existing query_rag.query() path (fixed in v9.40).

```python
def execute_firestore_query(filters, intent):
    db = firestore.client()
    query = db.collection("locations")

    for field, value in filters.items():
        if isinstance(value, list):
            # G34: single array-contains limit
            query = query.where(field, "array_contains", value[0])
        else:
            query = query.where(field, "==", value)

    results = query.stream()
    docs = [doc.to_dict() for doc in results]

    # Post-filter for additional array values (G34 workaround)
    for field, value in filters.items():
        if isinstance(value, list) and len(value) > 1:
            for extra_val in value[1:]:
                docs = [d for d in docs if extra_val in d.get(field, [])]

    if intent == "count":
        return f"{len(docs)} results found."
    elif intent == "list":
        return format_entity_list(docs[:20])
    else:
        return format_entity_summary(docs)
```

**Stage 3 - Synthesis (conditional)**

If user asked a conversational question (not "how many" or "list"), pass Firestore results back through Gemini Flash for natural language summary. If count/list intent, return formatted data directly - no token spend.

### Schema Reference File

New file: `data/schema_reference.json`

Compact reference loaded at bot startup. Contains:
- 22 t_any_* field names with descriptions and types (array vs scalar)
- 3 t_log_type values (calgold, ricksteves, tripledb)
- Pipeline display names and aliases ("California's Gold"/"Huell Howser", "Rick Steves' Europe"/"Rick Steves", "Diners, Drive-Ins and Dives"/"DDD"/"Guy Fieri"/"Triple D")
- 5-10 example values per high-cardinality field (cuisines, states, countries)

Target: <500 tokens serialized so routing calls stay cheap.

### Schema Reference Prompt Template

```
You are a query router for a location intelligence database with 6,181 entities across 3 pipelines.

Given a user question, return ONLY a JSON object with one of these structures:

For entity/data questions:
{"route": "firestore", "filters": {field: value, ...}, "intent": "count|list|detail"}

For development/project history questions:
{"route": "chromadb", "query": "search terms"}

SCHEMA REFERENCE:
[contents of data/schema_reference.json]

Rules:
- Array fields (t_any_*) take list values: ["italian"]
- Scalar fields (t_log_type, t_name, t_city) take string values
- "DDD" or "Diners Drive-Ins" or "Guy Fieri" or "Triple D" -> t_log_type: "tripledb"
- "Huell Howser" or "California's Gold" -> t_log_type: "calgold"
- "Rick Steves" -> t_log_type: "ricksteves"
- State names -> t_any_states (lowercased)
- Country names -> t_any_countries (ISO alpha-2 lowercase)
- "how many" -> intent: "count"
- "list" or "show" or "where" -> intent: "list"
- specific place name -> intent: "detail"
- If unsure whether entity or dev question, default to firestore
- Return ONLY valid JSON, no markdown, no explanation

USER QUESTION: {question}
```

### Firebase Admin SDK Init

```python
import firebase_admin
from firebase_admin import credentials, firestore

if not firebase_admin._apps:
    cred = credentials.Certificate(os.path.expanduser(
        "~/.config/gcloud/kjtcom-sa.json"
    ))
    firebase_admin.initialize_app(cred)

db = firestore.client()
```

### G34 Workaround

Firestore allows only ONE array-contains per query. Use array-contains for the first array field, post-filter in Python for additional array fields. Scalar fields have no such limit.

### Error Handling

- Gemini Flash returns invalid JSON -> fall back to ChromaDB with raw question
- Firestore query returns 0 results -> report "0 results" honestly, suggest broadening
- Firestore query returns >100 results -> cap at 20, report total count
- Firebase Admin SDK init fails -> log error, fall back to ChromaDB-only mode
- All errors logged via iao_logger.py

### Testing Checklist

```
/ask how many Italian restaurants in Orange County in DDD
  -> Firestore route, count response

/ask where did Guy Fieri go in Texas
  -> Firestore route, t_log_type=tripledb, t_any_states=["texas"], list

/ask what countries does Rick Steves visit
  -> Firestore route, t_log_type=ricksteves, unique countries list

/ask what caused the G45 cursor bug
  -> ChromaDB route, RAG-powered answer

/ask how many entities are in the database
  -> Firestore route, no filters, count of all 6,181

/ask show me Huell Howser locations in Los Angeles County
  -> Firestore route, t_log_type=calgold, t_any_counties=["los angeles"]
```

---

## W2: Re-embed Archive (P1)

Run embed_archive.py to index v9.38/v9.39/v9.40 docs into ChromaDB. The index was built during v9.38 from 130 files but the last 3 iterations' docs aren't in it.

```fish
set -gx IAO_ITERATION v9.41
cd ~/dev/projects/kjtcom
python3 -u scripts/embed_archive.py
```

Verify chunk count increased from 1,307.

---

## W3: Artifact Automation Scaffold (P2)

### scripts/generate_artifacts.py

**Inputs:**
- IAO_ITERATION env var
- Prior iteration docs from docs/archive/
- git diff --stat output
- flutter analyze + flutter test output
- data/iao_event_log.jsonl filtered to current iteration
- agent_scores.json (with workstream-level data per v9.41+ amendment)

**Outputs (to docs/drafts/):**
- kjtcom-build-v{X}.md
- kjtcom-report-v{X}.md (includes Workstream Scorecard)
- Changelog entry

### template/artifacts/

- build-template.md
- report-template.md (Workstream Scorecard table baked in)
- changelog-template.md

### Workstream Scorecard in Report

```markdown
## WORKSTREAM SCORECARD

| W# | Name | Priority | Outcome | Agents | LLMs | MCPs | Score |
|----|------|----------|---------|--------|------|------|-------|
| W1 | ... | P1 | Complete | ... | ... | ... | 9/10 |
```

---

## W4: Rebuild iteration_registry.json (P2)

Re-run build_registry_v2.py. If OOM or timeout, log as gotcha, defer to v9.42.

---

## W5: Living Doc Updates (P3)

### architecture.mmd
- Add SCHEMA_REF, INTENT_ROUTER, ARTIFACT_GEN to MIDDLEWARE subgraph
- Add connections: TELEGRAM -> INTENT_ROUTER -> FIRESTORE and INTENT_ROUTER -> CHROMADB
- Update header: "Updated: v9.41"

### install.fish
- Add firebase-admin pip package to Step 5d if not already present

### changelog
- Append v9.41 entry after build completes

---

## TRIDENT

| Prong | Target |
|-------|--------|
| Cost | $0. <50K Claude tokens. Gemini Flash free tier for routing. |
| Delivery | 5 workstreams. Bot answers entity questions. Artifact scaffold operational. |
| Performance | /ask "how many Italian restaurants in OC in DDD" returns a real count. |

---

## FUTURE OPTIMIZATION (NOT THIS ITERATION)

Python-side keyword classification for high-frequency routing patterns. Many iterations away. Get it working with Gemini first, measure token spend, then optimize.

---

*Design document v9.41, April 5, 2026.*
