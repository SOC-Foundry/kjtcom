# kjtcom - Design Document v9.40

**Phase:** 9 - App Optimization
**Iteration:** 40
**Date:** April 5, 2026
**Focus:** Telegram Bot Fixes + Dependency Freshness + Token Efficiency Mandate

---

## AMENDMENTS (all prior amendments remain in effect)

### Token Efficiency - MANDATORY (v9.40+)

Minimize token spend across all agents. Prefer local LLM for simple tasks, limit num_predict, use direct file reads over LLM interpretation for structured data. Target: <50K Claude Code tokens per infrastructure iteration. Log all token usage via iao_logger.py.

---

## WORKSTREAMS

| # | Workstream | Priority | Description |
|---|-----------|----------|-------------|
| W1 | Fix /ask RAG context | P1 | ChromaDB chunks not reaching Gemini prompt. Bot retrieves but doesn't pass context. |
| W2 | Telegram event logging | P1 | All inbound messages + outbound responses logged to iao_event_log.jsonl |
| W3 | Telegram UX | P2 | Default handler for plain text (respond with command list). /start handler. |
| W4 | Dependency freshness | P1 | flutter pub upgrade, verify Dart MCP SDK constraint >=3.9 |
| W5 | G51 permanent fix | P2 | Bake think:false into ALL Ollama calls project-wide, not just evaluator |

---

## W1: Fix /ask RAG Context Passing

The bug: `telegram_bot.py` calls `query_rag.py` which returns chunks, but the chunks are not injected into the Gemini/OpenClaw prompt. Gemini receives an empty context and says "results are empty."

Fix in `/ask` handler:

```python
# Current (broken):
chunks = query_rag(question)  # Returns relevant chunks
response = interpreter.chat(question)  # Gemini gets no context

# Fixed:
chunks = query_rag(question)  # Returns relevant chunks
context = "\n".join([c["text"] for c in chunks])
prompt = f"Based on this context from the kjtcom project archive:\n\n{context}\n\nAnswer: {question}"
response = interpreter.chat(prompt)  # Gemini gets full context
```

Also verify `query_rag.py` returns actual text content, not just metadata.

---

## W2: Telegram Event Logging

Every Telegram interaction logged via iao_logger:

```python
# Inbound message
log_event("agent_msg", "telegram-user", "telegram-bot", "command",
          input_summary=update.message.text[:200])

# Outbound response
log_event("agent_msg", "telegram-bot", "telegram-user", "response",
          output_summary=response_text[:200])

# LLM calls within handlers
log_event("llm_call", "telegram-bot", "gemini-flash", "ask",
          input_summary=prompt[:200], output_summary=answer[:200],
          tokens=token_counts, latency_ms=latency)
```

---

## W3: Telegram UX

Add handlers:
- `/start` - "kjtcom IAO Bot. Commands: /status /query /evaluate /gotcha /scores /ask /search"
- Default (plain text) - "Unknown command. Try /status or /ask [question]"
- `/help` - Same as /start

---

## W4: Dependency Freshness

```fish
cd ~/dev/projects/kjtcom/app
flutter pub upgrade
flutter pub outdated  # Log what changed
flutter analyze
flutter test
flutter build web
```

Verify pubspec.yaml SDK constraint: `sdk: '>=3.9.0 <4.0.0'`

Dart MCP server requires 3.9+. Current SDK is 3.11.4 which is fine, but the constraint must reflect it.

---

## W5: G51 Permanent Fix

Create a single Ollama config that ALL scripts use:

```python
# scripts/utils/ollama_config.py
OLLAMA_DEFAULTS = {
    "stream": False,
    "think": False,  # G51 fix - permanent
    "options": {
        "num_predict": 512  # Token efficiency - default conservative
    }
}
```

Update ollama_logged.py to merge these defaults into every call.

---

## TRIDENT

| Prong | Target |
|-------|--------|
| Cost | $0. <50K Claude tokens. |
| Delivery | 5 workstreams. Bot fully functional. |
| Performance | /ask returns real answers. All deps current. |

---

*Design document v9.40, April 5, 2026.*
