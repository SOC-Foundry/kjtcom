# kjtcom - Build Log v9.40

**Phase:** 9 - App Optimization
**Iteration:** 40
**Date:** April 5, 2026
**Agent:** Claude Code (Opus 4.6)

---

## PRE-FLIGHT

- [x] Ollama running, 4 models
- [x] v9.39 docs archived (already in docs/archive/)
- [x] IAO_ITERATION set to v9.40

---

## W1: Fix /ask RAG Context (P1) - COMPLETE

**Root cause:** subprocess call `query_rag.py question 3 --json` passed `--json` as argv[3], which `main()` treated as `version_filter='--json'`. ChromaDB filtered by `version='--json'` -> 0 results -> empty context -> Gemini said "results are empty."

**Fix:** Replaced subprocess with direct `from query_rag import query as rag_query`. Extracts `results['documents']` and `results['metadatas']` directly. Builds context string with source attribution (filename, version, score). Passes full context into Gemini prompt:

```python
synth_prompt = (
    f"Based on this context from the kjtcom project archive:\n\n"
    f"{context_text[:3000]}\n\n"
    f"Answer this question concisely: {question}"
)
```

Fallback: if Gemini/OpenClaw fails, returns formatted RAG chunks directly.

---

## W2: Telegram Event Logging (P1) - COMPLETE

Added `log_event()` calls to ALL 9 handlers (status, query, evaluate, gotcha, scores, ask, search, start, help) + default text handler. Both inbound (telegram-user -> telegram-bot) and outbound (telegram-bot -> telegram-user) logged.

Pattern:
```python
log_event("agent_msg", "telegram-user", "telegram-bot", "command", input_summary="/command args")
# ... handler logic ...
log_event("agent_msg", "telegram-bot", "telegram-user", "response", output_summary=response[:200])
```

---

## W3: Telegram UX (P2) - COMPLETE

- `/start` - Welcome message with full command list
- `/help` - Same as /start
- `handle_text` - Default handler for non-command messages: "Unknown command. Try /status, /ask [question], or /help for all commands."
- Added `MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text)` to handler list

---

## W4: Dependency Freshness (P1) - COMPLETE

- `flutter pub upgrade`: no changes needed, all direct deps current
- `flutter pub outdated`: 10 transitive deps have major version bumps blocked by constraints (expected)
- `flutter analyze`: 0 issues
- `flutter test`: 15/15 pass
- `flutter build web`: success (24.0s compile, tree-shaken icons)
- SDK constraint `^3.11.4` is correct for Dart MCP (requires >=3.9)

---

## W5: G51 Permanent Fix (P2) - COMPLETE

Created `scripts/utils/ollama_config.py`:
- `OLLAMA_DEFAULTS`: stream=False, think=False, num_predict=512
- `OLLAMA_EVAL_DEFAULTS`: stream=False, think=False, num_predict=2048
- `merge_defaults(payload, evaluation=False)`: merges defaults with caller overrides

Updated consumers:
- `scripts/utils/ollama_logged.py`: uses `merge_defaults()` in `chat_logged()`
- `scripts/telegram_bot.py`: evaluate handler uses `merge_defaults(..., evaluation=True)`
- `scripts/run_evaluator.py`: uses `merge_defaults(..., evaluation=True)`

All Ollama calls now inherit think=False + num_predict limits automatically.

---

## DEPLOY

- Firebase hosting deployed: https://kjtcom-c78cd.web.app (41 files)
- Telegram bot restarted in tmux session `telegram-bot`
- Bot confirmed running with all 9 commands + default text handler

---

## FILES MODIFIED

| File | Change |
|------|--------|
| scripts/telegram_bot.py | W1 fix + W2 logging + W3 UX handlers + W5 ollama_config |
| scripts/run_evaluator.py | W5 ollama_config integration |
| scripts/utils/ollama_logged.py | W5 merge_defaults import |
| scripts/utils/ollama_config.py | NEW - G51 permanent fix |

---

*Build log v9.40, April 5, 2026.*
