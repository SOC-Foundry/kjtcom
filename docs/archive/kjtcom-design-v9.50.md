# kjtcom - Design Document v9.50

**Phase:** 9 - App Optimization
**Iteration:** 50
**Date:** April 5, 2026
**Recommended Agent:** Claude Code
**Focus:** Qwen Harness Bug Fixes + README Overhaul + Claw3D Dynamic Update

---

## WORKSTREAMS

| # | Workstream | Priority | Description |
|---|-----------|----------|-------------|
| W1 | Qwen harness bug fixes (3 patterns) | P1 | Fix MCPs column (lists all instead of used), agent attribution (says "Qwen" not executor), raw JSON in narrative. |
| W2 | README overhaul | P1 | Tech stack table outdated (v9.35-era). Add Claw3D link. Update all sections to v9.50 state. |
| W3 | Claw3D dynamic update | P1 | Update claw3d.html from v9.38 data to current architecture. Add intent router, gotcha archive, middleware registry, systemd bot, schema validation nodes. |
| W4 | Post-flight + living docs | P2 | Post-flight pass. Changelog append. Middleware registry update. |

---

## W1: Qwen Harness Bug Fixes (P1)

Three specific patterns observed in v9.49 that need targeted fixes.

### Bug 1: MCPs Column Lists All Instead of Used

Qwen dumps the entire MCP enum ["Firebase", "Context7", "Firecrawl", "Playwright", "Dart", "-"] for every workstream instead of selecting which were actually used.

**Fix in eval_schema.json:**
Change mcps from requiring all enum values to allowing selection:
```json
"mcps": {
  "type": "array",
  "items": {"type": "string", "enum": ["Firebase", "Context7", "Firecrawl", "Playwright", "Dart", "-"]},
  "maxItems": 3,
  "description": "List ONLY the MCP servers actually invoked during this workstream. Use '-' ONLY if no MCPs were used. Most workstreams use 0-1 MCPs."
}
```

**Fix in evaluator-harness.md:**
Add explicit instruction: "For each workstream, list ONLY the MCP servers that were actually called during execution. If a workstream involved writing a Python script with no MCP interaction, the MCPs value is ['-']. Do NOT list all possible MCPs - list only the ones used."

### Bug 2: Agent Column Says "Qwen" Instead of Executor

Qwen lists herself as the agent for every workstream. The actual executor is specified in the design doc header.

**Fix in evaluator-harness.md:**
Add: "You (Qwen) are the EVALUATOR, not the executor. The executing agent is specified in the design document header ('Recommended Agent' or 'Executing Agent'). For the agents field, list the agent that PERFORMED the work, not the agent EVALUATING it. Typical values: 'claude-code' or 'gemini-cli'. You are never the agent."

**Fix in run_evaluator.py:**
Parse the design doc header for the executing agent name and inject it into the prompt context.

### Bug 3: Raw JSON in Narrative Sections

The report summary contained truncated JSON instead of markdown prose. The build log execution section had raw JSON dumps.

**Fix in eval_schema.json:**
Add a `summary` field requirement:
```json
"summary": {
  "type": "string",
  "minLength": 50,
  "maxLength": 500,
  "description": "Plain text summary. NO JSON, NO markdown headers, NO code blocks. 2-4 sentences describing what was built, what worked, and what failed."
}
```

**Fix in generate_artifacts.py:**
The report template must render Qwen's JSON into markdown tables and prose - never dump raw JSON into the final artifact. Add a `render_report_markdown()` function that takes the validated JSON and produces the final markdown.

---

## W2: README Overhaul (P1)

The tech stack table in the screenshot shows v9.35-era content. Missing: Ollama, ChromaDB, Telegram bot, intent router, systemd, Brave Search, artifact automation.

### Updated Tech Stack Table

```markdown
| Component | Tool | Purpose |
|-----------|------|---------|
| Audio Download | yt-dlp | YouTube -> mp3 |
| Transcription | faster-whisper (CUDA) | mp3 -> timestamped JSON |
| Extraction | Gemini 2.5 Flash API | Transcript -> structured entity JSON |
| Normalization | Python + schema.json | Raw JSON -> Thompson Indicator Fields |
| Geocoding | Nominatim (OSM) | Address/name -> lat/lon |
| Enrichment | Google Places API (New) | Rating, reviews, website, phone |
| County Enrichment | Nominatim reverse geocode | Coordinates -> county (v9.42) |
| Database | Cloud Firestore (Blaze) | Denormalized documents, multi-database |
| Search API | Firebase Cloud Functions | Complex cross-dataset queries |
| Frontend | Flutter Web (6 tabs + MW) | Unified search, map, middleware dashboard |
| Hosting | Firebase Hosting | CDN, preview channels, SSL |
| Orchestration | Claude Code / Gemini CLI | IAO agent execution |
| Intent Router | Gemini 2.5 Flash (litellm) | 3-route query classification |
| RAG | ChromaDB + nomic-embed-text | Semantic search over project archive |
| Telegram Bot | python-telegram-bot (systemd) | @kjtcom_iao_bot, 3-route retrieval |
| Web Search | Brave Search API | External query routing |
| Local LLMs | Ollama (4 models) | Evaluation, triage, vision, embeddings |
| Evaluation | Qwen3.5-9B (schema-validated) | Workstream scoring, artifact drafting |
| Event Logging | iao_logger.py | P3 Diligence event stream |
| Artifact Automation | generate_artifacts.py | Post-iteration doc generation |
| 3D Visualization | Three.js (Claw3D) | IAO workspace visualization |
```

### Links to Add

```markdown
**[Live App](https://kylejeromethompson.com)** |
**[Architecture Diagram](https://kylejeromethompson.com/architecture.html)** |
**[3D IAO Visualization](https://kylejeromethompson.com/claw3d.html)** |
**[Telegram Bot](https://t.me/kjtcom_iao_bot)** |
**[Mermaid Source](docs/kjtcom-architecture.mmd)**
```

---

## W3: Claw3D Dynamic Update (P1)

The current claw3d.html was built in v9.38 with 15 nodes. The architecture has grown significantly. Update the Three.js scene to reflect current state.

### New Nodes to Add (since v9.38)

| Node | Type | Color | Added In |
|------|------|-------|----------|
| Intent Router | Middleware | cyan | v9.41 |
| Firestore Query | Middleware | cyan | v9.41 |
| Schema Reference | Data | teal | v9.41 |
| Gotcha Archive | Data | teal | v9.42 |
| Middleware Registry | Data | teal | v9.42 |
| systemd Bot Service | Infrastructure | blue | v9.42 |
| Brave Search | Middleware | cyan | v9.42 |
| County Enrichment | Middleware | cyan | v9.42 |
| Artifact Generator | Middleware | cyan | v9.41 |
| Evaluator Harness | Middleware | cyan | v9.46 |
| Post-Flight | Middleware | cyan | v9.43 |
| Eval Schema | Data | teal | v9.49 |
| MW Tab | Frontend | green | v9.49 |

### Connections to Add

- Telegram Bot -> Intent Router -> Firestore / ChromaDB / Brave Search
- Evaluator Harness -> Qwen -> Eval Schema -> Agent Scores
- systemd -> Telegram Bot
- Post-Flight -> Site / Bot / Architecture HTML / Claw3D

### Implementation

Update the node data array and connection array in claw3d.html. Keep the Three.js rendering logic (planet/orbit style). Add the new nodes with appropriate positions, colors, and sizes. The scene should now have ~28 nodes instead of 15.

Consider: read nodes from architecture.mmd programmatically via a build script (scripts/build_claw3d.py) so the 3D view stays in sync with the architecture diagram. This would be a future enhancement - for now, manual update is fine.

---

## W4: Post-Flight + Living Docs (P2)

1. Post-flight pass
2. Append changelog to single file
3. Update middleware_registry.json
4. Rebuild architecture HTML
5. Deploy

---

## TRIDENT

| Prong | Target |
|-------|--------|
| Cost | $0. <50K tokens. |
| Delivery | 4 workstreams. Qwen bugs fixed. README current. Claw3D reflects v9.50. |
| Performance | Qwen evaluation produces MCPs=["-"] for workstreams that didn't use MCPs. Agent column says "claude-code" not "Qwen." No raw JSON in narrative. |

---

*Design document v9.50, April 5, 2026.*
