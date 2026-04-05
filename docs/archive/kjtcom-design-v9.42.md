# kjtcom - Design Document v9.42

**Phase:** 9 - App Optimization
**Iteration:** 42
**Date:** April 5, 2026
**Focus:** TripleDB County Enrichment + Bot Resiliency + Artifact Workflow Fixes + Internet Query Stream + Gotcha Archive + Harness Registry

---

## AMENDMENTS (all prior amendments remain in effect)

### Agent Session Best Practices - MANDATORY (v9.42+)

This section is permanent in all future design docs. These are hard-won operational patterns from 41 iterations.

**Pre-Launch Checklist (before typing anything into claude/gemini):**
1. CLAUDE.md and GEMINI.md MUST be saved to disk in the directory you launch from BEFORE starting the agent session. The agent reads these on first prompt. If they are stale or missing, the entire session runs on wrong context.
2. /quit every session and start fresh between iterations. Token context degrades over long sessions - early tokens carry more weight than late ones. A fresh session with good harness files outperforms a stale session every time.
3. set -gx IAO_ITERATION v9.XX BEFORE launching. Scripts key on this env var.
4. Verify Ollama is running (ollama list) and all models are loaded.
5. Kill and restart the Telegram bot tmux session between iterations.
6. Verify Firebase SA is accessible: test -f ~/.config/gcloud/kjtcom-sa.json

**Environment Architecture:**
- GCP service account keys: ~/.config/gcloud/{project}-sa.json (NEVER in repo, NEVER in env vars)
- API keys: fish shell config (~/.config/fish/config.fish), broken down per project with KJTCOM_ prefix
- Agent launches: `claude --dangerously-skip-permissions` (Claude Code), `gemini --yolo` (Gemini CLI)
- tmux for persistent processes: `tmux new-session -d -s {name} "fish -c '...'"
- Sleep mask on dev machines: `systemctl mask suspend` (NZXTcos)

**Session Discipline:**
- One iteration per session. Do not chain iterations in a single session.
- If a session crashes or stalls, /quit and relaunch with the same launch prompt. Do not try to recover mid-session.
- Harness files (CLAUDE.md, GEMINI.md) should GROW over time. Never abbreviate or shorten them. The depth and specificity of these files is the primary competitive advantage of the IAO methodology.
- Every session ends with artifact production. No exceptions.

**Artifact Discipline (v9.42+ fix):**
- generate_artifacts.py outputs to docs/drafts/ for Qwen draft generation
- After human review, drafts MUST be promoted: cp docs/drafts/kjtcom-*.md docs/
- The executing agent should prompt for promotion at end of session, not leave drafts sitting
- Qwen draft accuracy must be validated - v9.41 showed W4 marked "complete" when it timed out, W5 marked "deferred" when it was done. The agent must cross-check Qwen's assessment against actual execution results before promoting.

### Middleware as Primary IP - MANDATORY (v9.42+)

The middleware layer (scripts/, template/, data/) is the primary intellectual property of this project. kjtcom is the lab; the middleware is the product that stamps onto intranet, socalpha1, and future customer deployments. Every iteration should ask: "what did we add to the middleware that makes the next project easier?"

Middleware components:
- **Harnesses:** CLAUDE.md, GEMINI.md (agent instructions - these grow, never shrink)
- **Harness Registry:** middleware_registry.json (NEW v9.42) - catalogs all harness files, templates, and middleware scripts with versioning
- **Evaluator:** run_evaluator.py, agent_scores.json, workstream scoring
- **RAG:** embed_archive.py, query_rag.py, ChromaDB
- **Intent Router:** intent_router.py, schema_reference.json
- **Event Logging:** iao_logger.py, iao_event_log.jsonl, analyze_events.py
- **Artifact Generator:** generate_artifacts.py, template/artifacts/
- **Gotcha Archive:** gotcha_archive.json (NEW v9.42) - resolved gotchas with resolution patterns
- **Bot:** telegram_bot.py with dual retrieval + internet query stream
- **Config:** ollama_config.py, ollama_logged.py

### Resolved Gotcha Archive - NEW (v9.42+)

Resolved gotchas must NOT be discarded. They contain resolution patterns that the middleware can learn from. New file: data/gotcha_archive.json stores every resolved gotcha with: ID, description, resolution, iteration resolved, root cause category, and prevention pattern. The evaluator and future agents can query this archive to avoid repeating mistakes.

### Qwen Timeout - UPDATED (v9.42)

Qwen timeout increased from 5 minutes to 45 minutes for registry builds and batch operations. Individual calls still use ollama_config.py defaults (num_predict 512/2048). The registry builder specifically needs extended time because each of 40+ iterations requires a separate Qwen evaluation call.

### Cross-Pipeline Schema Enrichment - NEW (v9.42+)

When a new pipeline is added or a field is enriched on one pipeline, ALL pipelines must be evaluated for the same enrichment. If CalGold has t_any_counties and TripleDB does not, that is a schema gap that must be closed. The schema_reference.json should reflect which fields are populated per pipeline and flag gaps.

---

## WORKSTREAMS

| # | Workstream | Priority | Description |
|---|-----------|----------|-------------|
| W1 | TripleDB county enrichment | P1 | Enrich 1,100 TripleDB entities with t_any_counties from coordinates/city/state data. Update Firestore. |
| W2 | Bot resiliency (systemd + watchdog) | P1 | systemd service for telegram bot. Auto-restart on crash. Watchdog timer for 10-minute health check. |
| W3 | Artifact workflow fix + Qwen accuracy | P1 | Fix draft promotion, Qwen cross-check, 45-min timeout. Retry registry rebuild. |
| W4 | Internet query stream (Brave Search) | P2 | 3rd /ask retrieval path: questions about external topics route to Brave Search API. |
| W5 | Gotcha archive + harness registry | P2 | data/gotcha_archive.json for resolved gotchas. data/middleware_registry.json for harness catalog. |
| W6 | Intranet update artifact | P3 | Cross-project update doc with OpenClaw deployment, middleware updates, updated intranet mmd. |

---

## W1: TripleDB County Enrichment (P1)

TripleDB has 1,100 entities with t_any_cities and t_any_states but NO t_any_counties. When someone asks "Italian restaurants in Orange County in DDD," the intent router correctly builds the Firestore query but gets 0 results because the field is empty. This is a data gap, not a code bug.

### Enrichment Approach

1. Read all 1,100 TripleDB entities from Firestore (t_log_type == "tripledb")
2. For each entity with t_any_cities and t_any_states populated:
   - Use Google Places API (already in pipeline) or a county lookup table to map city+state -> county
   - A static US county lookup (city -> county) is cheaper than API calls. ~30K US cities map to ~3,200 counties.
   - For entities with coordinates, reverse geocode to county via Nominatim (free, 1 req/sec)
3. Write t_any_counties back to Firestore via Firebase Admin SDK (batch writes, 500 per batch)
4. Update data/schema_reference.json to reflect TripleDB now has counties
5. Log all enrichment via iao_logger.py

### Script

New: scripts/enrich_counties.py
- Reads from production Firestore (default database)
- Uses reverse geocoding (coordinates -> county) as primary method
- Falls back to city+state static lookup table for entities without coordinates
- Dry-run mode (--dry-run) for validation before write
- Batch writes to Firestore (500/batch)
- Progress logging and checkpoint support

### Cross-Pipeline Audit

After TripleDB enrichment, audit CalGold and RickSteves for any similar gaps. Log findings in build log. If gaps found, create workstreams for next iteration.

---

## W2: Bot Resiliency (P1)

The Telegram bot currently runs in a tmux session and dies when the machine suspends or the session ends. This is the "P2: Telegram bot tmux persistence" item from the v9.40 KT.

### systemd Service

Create: /etc/systemd/system/kjtcom-telegram-bot.service

```ini
[Unit]
Description=kjtcom IAO Telegram Bot
After=network.target ollama.service
Wants=ollama.service

[Service]
Type=simple
User=kyle
WorkingDirectory=/home/kyle/dev/projects/kjtcom
Environment=IAO_ITERATION=v9.42
EnvironmentFile=/home/kyle/.config/kjtcom/bot.env
ExecStart=/usr/bin/python3 scripts/telegram_bot.py
Restart=always
RestartSec=30
WatchdogSec=600

[Install]
WantedBy=multi-user.target
```

### Watchdog

WatchdogSec=600 (10 minutes). The bot must call sd_notify(WATCHDOG=1) periodically or systemd will restart it. Add a simple watchdog ping in the bot's main loop:

```python
import sdnotify
n = sdnotify.SystemdNotifier()

# In the bot's polling loop or via a periodic job:
n.notify("WATCHDOG=1")
```

pip install sdnotify --break-system-packages

### bot.env

```
KJTCOM_TELEGRAM_BOT_TOKEN=...
KJTCOM_BRAVE_SEARCH_API_KEY=...
GEMINI_API_KEY=...
GOOGLE_APPLICATION_CREDENTIALS=/home/kyle/.config/gcloud/kjtcom-sa.json
```

### Deployment

```fish
sudo cp kjtcom-telegram-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable kjtcom-telegram-bot
sudo systemctl start kjtcom-telegram-bot
sudo systemctl status kjtcom-telegram-bot
# Kill the old tmux session
tmux kill-session -t telegram-bot 2>/dev/null
```

---

## W3: Artifact Workflow Fix + Qwen Accuracy (P1)

### Problems from v9.41:
1. Qwen marked W4 as "complete" when it timed out (exit code 124)
2. Qwen marked W5 as "deferred" when it was actually complete
3. Drafts sat in docs/drafts/ and were not promoted to docs/
4. Registry builder timed out at 5 minutes - needs 45 minutes

### Fixes:

**generate_artifacts.py update:**
- After Qwen generates drafts, cross-check workstream outcomes against actual execution signals:
  - Check for timeout exit codes (124, 137) -> mark as "deferred" not "complete"
  - Check for file existence (did the expected output files get created?) -> mark as "complete" only if true
  - Check flutter analyze/test output for failures
- Add `--promote` flag that copies validated drafts from docs/drafts/ to docs/
- Add `--validate-only` flag that checks drafts against execution reality without generating

**run_evaluator.py update:**
- Pass execution context (exit codes, file existence checks) to Qwen alongside the workstream list
- Qwen evaluates with ground truth, not just its own interpretation

**ollama_config.py update:**
- Add OLLAMA_BATCH_DEFAULTS with num_predict:2048 and timeout of 45 minutes (2700 seconds)
- build_registry_v2.py uses batch defaults

**Registry rebuild retry:**
- With 45-minute timeout, 40 iterations at ~60s each = ~40 minutes. Should complete.

---

## W4: Internet Query Stream (P2)

Add a 3rd retrieval path to the /ask handler. The intent router currently routes to Firestore (entity data) or ChromaDB (dev history). Add a "web" route for questions about external topics.

### Updated Router Logic:

```json
// External/internet question -> Brave Search
{
  "route": "web",
  "query": "guidepoint var professional services washington dc"
}
```

### Implementation:
- Update schema reference prompt to include a 3rd route option
- When route == "web", call scripts/brave_search.py (already exists from v9.38)
- Pass Brave results through Gemini Flash for synthesis
- Log as api_call via iao_logger.py

### Security Discussion (for intranet, not kjtcom):

kjtcom is a public project - no RBAC needed now. But the intranet bot WILL need:
- Telegram user whitelist: only approved user IDs can query
- Dataset-level RBAC: different Okta groups see different data
- Outbound response filtering: sensitive data redacted before sending to Telegram
- Audit logging: who queried what, when

For v9.42: document the RBAC approach in the intranet update artifact (W6). Implementation happens when intranet gets its own bot.

---

## W5: Gotcha Archive + Harness Registry (P2)

### data/gotcha_archive.json

Structure:
```json
{
  "resolved_gotchas": [
    {
      "id": "G2",
      "description": "CUDA LD_LIBRARY_PATH not set",
      "resolution": "Set LD_LIBRARY_PATH in fish config to /usr/lib",
      "iteration_resolved": "v3.10",
      "root_cause": "environment",
      "prevention": "install.fish Step 8 sets CUDA paths automatically"
    },
    {
      "id": "G51",
      "description": "Qwen think mode empty responses",
      "resolution": "think:false baked into ollama_config.py",
      "iteration_resolved": "v9.40",
      "root_cause": "llm_config",
      "prevention": "All Ollama calls go through ollama_config.py merge_defaults()"
    }
  ]
}
```

Root cause categories: environment, llm_config, dependency, firestore, flutter, pipeline, mcp, security, timeout

### data/middleware_registry.json

Catalogs all middleware components:
```json
{
  "harnesses": [
    {"name": "CLAUDE.md", "version": "v9.42", "type": "agent_instructions", "target": "claude-code"},
    {"name": "GEMINI.md", "version": "v9.42", "type": "agent_instructions", "target": "gemini-cli"}
  ],
  "scripts": [
    {"name": "intent_router.py", "version": "v9.41", "type": "routing", "dependencies": ["litellm", "schema_reference.json"]},
    {"name": "firestore_query.py", "version": "v9.41", "type": "data_access", "dependencies": ["firebase-admin"]},
    {"name": "generate_artifacts.py", "version": "v9.41", "type": "automation", "dependencies": ["ollama_config.py", "iao_logger.py"]}
  ],
  "templates": [
    {"name": "template/artifacts/build-template.md", "version": "v9.41", "type": "artifact_template"},
    {"name": "template/artifacts/report-template.md", "version": "v9.41", "type": "artifact_template"}
  ],
  "data_stores": [
    {"name": "data/chromadb/", "type": "vector_store", "records": 1419},
    {"name": "data/gotcha_archive.json", "type": "knowledge_base", "version": "v9.42"},
    {"name": "data/schema_reference.json", "type": "schema", "version": "v9.41"},
    {"name": "agent_scores.json", "type": "evaluation", "version": "v9.41"}
  ]
}
```

This registry is updated every iteration that adds or modifies middleware components. It becomes the manifest for stamping middleware onto new projects (intranet, customer deployments).

---

## W6: Intranet Update Artifact (P3)

Produce: docs/cross-project/intranet-update-v9.42.md

Contents:
- OpenClaw deployment status and lessons learned (Gemini Flash engine, tiktoken workaround)
- Middleware components ready for intranet adoption (intent router, Firestore query module, artifact generator, gotcha archive)
- Telegram bot systemd pattern (portable to intranet bot)
- RBAC approach recommendation for intranet (Okta groups -> dataset permissions -> Telegram user whitelist)
- Updated intranet architecture mermaid chart showing where kjtcom middleware slots in
- Harness registry as the stamping manifest

### Intranet Mermaid Update

The intranet mmd should show:
- kjtcom middleware imports (intent_router, firestore_query, artifact generator)
- Okta SSO integration point
- RBAC layer between Telegram bot and Firestore
- Dataset-level permissions (company_knowledge, customer_data, internal_docs)

---

## TRIDENT

| Prong | Target |
|-------|--------|
| Cost | $0. <50K Claude tokens. Gemini Flash free tier. Google Places free credits for enrichment. |
| Delivery | 6 workstreams. TripleDB counties enriched. Bot resilient. Artifact workflow fixed. |
| Performance | /ask "Italian restaurants in Orange County in DDD" returns real results (not 0). Bot survives machine restart. |

---

*Design document v9.42, April 5, 2026.*
