# kjtcom - Execution Plan v9.39

**Phase:** 9 - App Optimization
**Iteration:** 39
**Date:** April 5, 2026
**Executing Agent:** Claude Code (Opus 4.6)
**Estimated Duration:** 3-4 hours

---

## PRE-FLIGHT

- [ ] Ollama running with 4 models (qwen3.5:9b, nemotron-mini:4b, GLM, nomic-embed-text)
- [ ] .mcp.json with 5 servers
- [ ] v9.38 docs archived
- [ ] KJTCOM_TELEGRAM_BOT_TOKEN set
- [ ] KJTCOM_BRAVE_SEARCH_API_KEY set
- [ ] GEMINI_API_KEY set (for OpenClaw engine)
- [ ] set -gx IAO_ITERATION v9.39

---

## STEP 1: Fix G54 + Install OpenClaw (W1) - 30 min

```fish
# 1a. Pre-install tiktoken 0.12.0 (has CP314 wheels)
pip install tiktoken==0.12.0 --break-system-packages

# 1b. Install open-interpreter
pip install open-interpreter --break-system-packages

# 1c. If 1b fails, try no-deps approach
pip install open-interpreter --no-deps --break-system-packages
pip install litellm pyyaml rich prompt_toolkit --break-system-packages

# 1d. If STILL fails, Python 3.13 venv approach (P7 self-healing)
python3.13 -m venv ~/venvs/openclaw
source ~/venvs/openclaw/bin/activate.fish
pip install open-interpreter
# Document venv path in install.fish

# 1e. Verify
python3 -c "from interpreter import interpreter; print('OpenClaw OK')"
```

### Configure Gemini Flash Engine

```fish
# 1f. Test OpenClaw with Gemini
python3 -c "
from interpreter import interpreter
interpreter.llm.model = 'gemini/gemini-2.5-flash'
interpreter.auto_run = False
interpreter.chat('What is 2+2?')
"
# Expected: Gemini Flash responds through OpenClaw
```

### NemoClaw (if available)

```fish
pip install nemoclaw --break-system-packages 2>/dev/null
# If unavailable, document as deferred. NemoClaw is alpha.
```

---

## STEP 2: G51 Investigation - 15 min

```fish
# 2a. Check Ollama version
ollama --version

# 2b. Fresh Qwen pull
ollama rm qwen3.5:9b
ollama pull qwen3.5:9b

# 2c. Test /no_think
curl -s http://localhost:11434/api/chat -d '{
  "model": "qwen3.5:9b",
  "messages": [{"role": "user", "content": "/no_think What is 2+2?"}],
  "stream": false,
  "options": {"num_predict": 100}
}' | python3 -c "
import sys,json
r=json.load(sys.stdin)
print(f'Content: [{r[\"message\"][\"content\"]}]')
print(f'Eval tokens: {r.get(\"eval_count\",0)}')
"

# 2d. Try think:false API option (newer Ollama feature)
curl -s http://localhost:11434/api/chat -d '{
  "model": "qwen3.5:9b",
  "messages": [{"role": "user", "content": "What is 2+2?"}],
  "stream": false,
  "think": false
}' | python3 -c "
import sys,json
r=json.load(sys.stdin)
print(f'Content: [{r[\"message\"][\"content\"]}]')
"

# 2e. Document findings
# If fixed: mark G51 RESOLVED, note fix method
# If not: escalate, consider Qwen3-8B or Qwen3.5-4B as evaluator fallback
```

---

## STEP 3: Create iao_logger.py (W2) - 30 min

### 3a. Create the logger module

Create `scripts/utils/iao_logger.py` with the event schema from design doc.

### 3b. Create helper wrappers

Create `scripts/utils/ollama_logged.py`:
```python
# Wrapper around Ollama API calls that automatically logs events
def chat_logged(model, prompt, source_agent="unknown"):
    start = time.time()
    response = ollama_chat(model, prompt)
    latency = int((time.time() - start) * 1000)
    log_event("llm_call", source_agent, model, "chat",
              input_summary=prompt[:200],
              output_summary=response.get("content", "")[:200],
              tokens={"prompt": response.get("prompt_eval_count", 0),
                      "eval": response.get("eval_count", 0)},
              latency_ms=latency,
              status="success" if response.get("content") else "empty_response")
    return response
```

### 3c. Wrap existing scripts

Add logging calls to:
- run_evaluator.py (Qwen chat calls)
- query_rag.py (embed + ChromaDB query)
- embed_archive.py (embed calls)
- build_registry_v2.py (Qwen chat + ChromaDB query)
- brave_search.py (HTTP API call)
- telegram_bot.py (all command handlers)

### 3d. Create analyze_events.py

Create `scripts/analyze_events.py`:
- Read data/iao_event_log.jsonl
- Output: total events, by type, by agent, error rate, token totals
- Machine-readable JSON output option for report integration

### 3e. Set iteration env var

Add to CLAUDE.md and GEMINI.md:
```fish
set -gx IAO_ITERATION v9.39
```

---

## STEP 4: IAO Tab Update (W3) - 30 min

### 4a. Update iao_tab.dart

Modify `app/lib/widgets/iao_tab.dart`:

- P3 Diligence: expand description to include event logging
- P5 Agentic Harness: mention OpenClaw + Telegram
- P9 Post-Flight: mention event log analysis
- P10 Continuous Improvement: mention evaluator + leaderboard + registry

### 4b. Update gotcha count if new gotchas from this iteration

### 4c. Build and deploy

```fish
cd ~/dev/projects/kjtcom/app && flutter analyze
cd ~/dev/projects/kjtcom/app && flutter test
cd ~/dev/projects/kjtcom/app && flutter build web
cd ~/dev/projects/kjtcom && firebase deploy --only hosting
```

---

## STEP 5: README Update (W4) - 15 min

Update README.md:
- IAO Methodology section: revised P3 with logging mandate
- P5: OpenClaw + Telegram + Brave Search
- P10: evaluator + leaderboard
- Project Status table: v9.39, current state
- Architecture chart link confirmed

---

## STEP 6: Update Telegram Bot for OpenClaw - 20 min

Update `scripts/telegram_bot.py`:
- /ask and /search now route through OpenClaw (Gemini Flash) for answer synthesis
- /status includes event log stats (total events, last event timestamp)
- All handlers wrapped with iao_logger calls

---

## STEP 7: Living Documents + Scoring - 20 min

### 7a. Update architecture.mmd
- Add OpenClaw node to agent roster
- Add event log to middleware layer
- Add Brave Search to API connections

### 7b. Update install.fish
- Add tiktoken 0.12.0, open-interpreter, nemoclaw (if available)
- Add IAO_ITERATION env var note

### 7c. Run evaluator
```fish
set -gx IAO_ITERATION v9.39
python3 scripts/run_evaluator.py --version v9.39 \
  --build-log docs/kjtcom-build-v9.39.md
```

### 7d. Run event log analysis
```fish
python3 scripts/analyze_events.py
```

Include output in report's Event Log Summary section.

---

## STEP 8: Artifacts - 15 min

- [ ] docs/kjtcom-design-v9.39.md (pre-staged)
- [ ] docs/kjtcom-plan-v9.39.md (pre-staged)
- [ ] docs/kjtcom-build-v9.39.md (you create)
- [ ] docs/kjtcom-report-v9.39.md (with Agent Scorecard + Event Log Summary)
- [ ] docs/kjtcom-changelog.md (append)
- [ ] scripts/utils/iao_logger.py (NEW)
- [ ] scripts/utils/ollama_logged.py (NEW)
- [ ] scripts/analyze_events.py (NEW)
- [ ] data/iao_event_log.jsonl (NEW - created by first logged event)
- [ ] agent_scores.json (append v9.39)
- [ ] docs/kjtcom-architecture.mmd (update)
- [ ] docs/install.fish (update)
- [ ] README.md (update pillars)
- [ ] app/lib/widgets/iao_tab.dart (update P3, P5, P10)
- [ ] CLAUDE.md (update read order, add IAO_ITERATION)
- [ ] GEMINI.md (update read order)

Archive v9.38 docs: `mv docs/kjtcom-*-v9.38.md docs/archive/`

---

## POST-FLIGHT

- [ ] OpenClaw installed and Gemini Flash responds through it
- [ ] G51 investigated (resolved or escalated with findings)
- [ ] iao_logger.py created and integrated into all scripts
- [ ] data/iao_event_log.jsonl has entries from this iteration
- [ ] analyze_events.py produces summary
- [ ] IAO tab updated with revised P3, deployed to production
- [ ] README pillars updated
- [ ] architecture.mmd updated with OpenClaw + event log
- [ ] install.fish updated
- [ ] flutter analyze: 0 issues, flutter test: 15/15 pass
- [ ] Agent Scorecard + Event Log Summary in report

---

## INTERVENTIONS

| # | Trigger | Resolution |
|---|---------|------------|
| 1 | G51 (Qwen empty responses) | May need manual Ollama/Qwen debugging |
| 2 | G54 (OpenClaw tiktoken) | Pre-install tiktoken 0.12.0, or Python 3.13 venv |
| 3 | Firebase reauth (G53) | firebase login --reauth if expired |

Target: 0-2 interventions.

---

*Plan document generated from claude.ai Opus 4.6 session, April 5, 2026.*
