# kjtcom - Execution Plan v9.41

**Executing Agent:** Claude Code (Opus 4.6)
**Estimated Duration:** 3 hours
**Token Target:** <50K

---

## PRE-FLIGHT

- [ ] Ollama running, 4 models (ollama list)
- [ ] Telegram bot killed (tmux kill-session -t telegram-bot)
- [ ] v9.40 docs archived (cp docs/kjtcom-*-v9.40.md docs/archive/)
- [ ] set -gx IAO_ITERATION v9.41
- [ ] Firebase SA accessible (~/.config/gcloud/kjtcom-sa.json)
- [ ] Gemini Flash API key in env (GEMINI_API_KEY)

---

## STEP 1: Create Schema Reference File - 20 min

1. Read app/lib/models/query_clause.dart -> extract knownFields (22 fields)
2. Read Firestore collection structure from pipeline scripts (phase7_load.py)
3. Create data/schema_reference.json:
   - 22 t_any_* field names + types (array vs scalar)
   - 3 t_log_type values with display name aliases
   - 5-10 example values per high-cardinality field
   - Pipeline name aliases (DDD/Guy Fieri/Triple D, Huell Howser/California's Gold, Rick Steves)
4. Keep it compact - target <500 tokens when serialized

---

## STEP 2: Build Firestore Query Module - 30 min

1. Create scripts/firestore_query.py:
   - Firebase Admin SDK init (reuse pattern from phase7_load.py)
   - execute_query(filters: dict, intent: str) -> str
   - G34 workaround: single array-contains, post-filter for extras
   - format_entity_list(docs, limit=20) -> readable Telegram output
   - format_entity_count(docs) -> "{count} results found"
2. Test standalone:

```fish
python3 -c "
from scripts.firestore_query import execute_query
print(execute_query({'t_log_type': 'tripledb'}, 'count'))
"
```

Expected: "1100 results found" (or close)

---

## STEP 3: Build Intent Router - 30 min

1. Create scripts/intent_router.py:
   - load_schema_reference() -> loads data/schema_reference.json at import
   - build_routing_prompt(question: str) -> prompt string with schema context
   - route_question(question: str) -> dict (parsed JSON from Gemini Flash)
   - Gemini Flash call via litellm (already installed for OpenClaw)
   - Response parsing: extract JSON, validate structure
   - Fallback: if JSON parse fails, return {"route": "chromadb", "query": question}
   - All calls logged via iao_logger.py
2. Test standalone:

```fish
python3 -c "
from scripts.intent_router import route_question
import json
print(json.dumps(route_question('how many Italian restaurants in Orange County in DDD'), indent=2))
"
```

Expected: {"route": "firestore", "filters": {"t_log_type": "tripledb", "t_any_cuisines": ["italian"], "t_any_counties": ["orange"]}, "intent": "count"}

---

## STEP 4: Wire Into Telegram Bot - 30 min

1. Edit scripts/telegram_bot.py /ask handler:
   - Import intent_router.route_question and firestore_query.execute_query
   - Stage 1: route = route_question(user_question)
   - Stage 2a (firestore): result = execute_query(route["filters"], route["intent"])
   - Stage 2b (chromadb): existing query_rag.query() path (v9.40 fix)
   - Stage 3 (optional synthesis): if intent not in ["count", "list"], pass results through Gemini Flash
   - Log all stages via iao_logger.py (routing decision, query execution, synthesis)
2. Error handling:
   - Gemini routing fails -> fall back to ChromaDB
   - Firestore query fails -> log error, report to user
   - 0 results -> honest "0 results found" message

---

## STEP 5: Test Full Pipeline - 20 min

Restart bot:

```fish
tmux kill-session -t telegram-bot 2>/dev/null
tmux new-session -d -s telegram-bot "fish -c 'source ~/.config/fish/config.fish; set -gx IAO_ITERATION v9.41; cd ~/dev/projects/kjtcom; python3 scripts/telegram_bot.py'"
```

Test from Telegram (all 6 cases from design doc):

```
/ask how many Italian restaurants in Orange County in DDD
/ask where did Guy Fieri go in Texas
/ask what countries does Rick Steves visit
/ask what caused the G45 cursor bug
/ask how many entities are in the database
/ask show me Huell Howser locations in Los Angeles County
```

Edge cases:
```
/ask hello
/ask restaurants
/status
/help
```

---

## STEP 6: Re-embed Archive (W2) - 10 min

```fish
cd ~/dev/projects/kjtcom
python3 -u scripts/embed_archive.py
```

Verify: chunk count > 1,307.

Test: `/ask what was fixed in v9.40` -> ChromaDB route, references /ask RAG fix.

---

## STEP 7: Artifact Automation Scaffold (W3) - 30 min

1. Create template/artifacts/ directory:
   - build-template.md
   - report-template.md (Workstream Scorecard baked in)
   - changelog-template.md
2. Create scripts/generate_artifacts.py:
   - Reads IAO_ITERATION env var
   - Reads prior docs from docs/archive/
   - Reads git diff --stat, flutter analyze, flutter test output
   - Reads iao_event_log.jsonl filtered to current iteration
   - Reads agent_scores.json (including workstreams array)
   - Calls Qwen (via ollama_config merge_defaults) for narrative sections
   - Outputs drafts to docs/drafts/
3. Update scripts/run_evaluator.py to score per-workstream:
   - Read workstream list from design doc or plan doc
   - Score each W# individually (outcome, agents, LLMs, MCPs, 0-10)
   - Append workstreams array to agent_scores.json entry
4. Test with v9.40 data (retroactive):

```fish
set -gx IAO_ITERATION v9.40
python3 -u scripts/generate_artifacts.py --retroactive
```

---

## STEP 8: Rebuild Registry (W4) - 10 min

```fish
set -gx IAO_ITERATION v9.41
cd ~/dev/projects/kjtcom
python3 -u scripts/build_registry_v2.py
```

If OOM or timeout: log as gotcha, defer to v9.42. Do not block.

---

## STEP 9: Living Docs + Deploy (W5) - 20 min

1. Update docs/kjtcom-architecture.mmd (see design doc W5)
2. Update docs/install.fish if firebase-admin not listed
3. Build + deploy:

```fish
cd ~/dev/projects/kjtcom/app
flutter analyze
flutter test
flutter build web
cd ~/dev/projects/kjtcom
firebase deploy --only hosting
```

---

## STEP 10: Workstream Evaluation + Artifacts - 15 min

1. Run Qwen evaluator with workstream-level scoring:

```fish
python3 -u scripts/run_evaluator.py --iteration v9.41
```

2. Verify agent_scores.json has workstreams array for v9.41
3. Run artifact generator for build log + report drafts:

```fish
python3 -u scripts/generate_artifacts.py
```

4. Final artifacts:
- [ ] docs/kjtcom-design-v9.41.md (pre-staged)
- [ ] docs/kjtcom-plan-v9.41.md (pre-staged)
- [ ] docs/kjtcom-build-v9.41.md (generated draft, reviewed)
- [ ] docs/kjtcom-report-v9.41.md (generated draft with Workstream Scorecard, reviewed)
- [ ] docs/kjtcom-changelog.md (append v9.41)
- [ ] agent_scores.json (append v9.41 with workstreams)
- [ ] data/schema_reference.json (NEW)
- [ ] scripts/intent_router.py (NEW)
- [ ] scripts/firestore_query.py (NEW)
- [ ] scripts/generate_artifacts.py (NEW)
- [ ] template/artifacts/ (NEW directory)
- [ ] scripts/telegram_bot.py (MODIFIED - dual retrieval)
- [ ] scripts/run_evaluator.py (MODIFIED - workstream scoring)
- [ ] docs/kjtcom-architecture.mmd (MODIFIED)
- [ ] docs/install.fish (MODIFIED if needed)
- [ ] CLAUDE.md (v9.41)
- [ ] GEMINI.md (v9.41)

---

## INTERVENTIONS

Target: 0. All decisions pre-answered in design doc.

Potential intervention points (pre-mitigated):
- Firebase SA path: ~/.config/gcloud/kjtcom-sa.json (same as phase7)
- Gemini Flash model string: gemini/gemini-2.0-flash (via litellm)
- G34: design doc specifies post-filter workaround
- Schema reference: design doc specifies 22 fields + 3 pipelines

---

*Plan v9.41, April 5, 2026.*
