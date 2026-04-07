#!/usr/bin/env python3
"""Structured event logger for IAO P3 Diligence.

Logs all agent communications (LLM calls, MCP calls, API calls, commands)
to data/iao_event_log.jsonl in append-only JSONL format.
"""
import json
import os
import sys
from datetime import datetime, timezone

LOG_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'iao_event_log.jsonl')

_ITERATION = os.environ.get("IAO_ITERATION")
if not _ITERATION:
    print("[iao_logger] ERROR: IAO_ITERATION environment variable is NOT SET.", file=sys.stderr)
    # We don't raise here to avoid crashing agents on import, but we'll flag it in events
    _ITERATION = "MISSING_ENV_VAR"
else:
    print(f"[iao_logger] iteration={_ITERATION}", file=sys.stderr)


def log_event(event_type, source_agent, target, action,
              input_summary="", output_summary="",
              tokens=None, latency_ms=None,
              status="success", error=None, gotcha_triggered=None):
    """Log a structured event to the JSONL event stream.

    Args:
        event_type: llm_call | mcp_call | api_call | file_op | command | agent_msg
        source_agent: claude-code | qwen3.5-9b | nemotron-mini | openclaw | telegram-bot
        target: model name, MCP server, API endpoint, etc.
        action: chat | embed | query | scrape | screenshot | read | write | search | evaluate
        input_summary: First 200 chars of prompt or command
        output_summary: First 200 chars of response or result
        tokens: dict with prompt, eval, total counts
        latency_ms: Response time in milliseconds
        status: success | error | timeout | empty_response
        error: Error message if applicable
        gotcha_triggered: Gotcha ID if this event triggered a known gotcha
    """
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "iteration": _ITERATION,
        "event_type": event_type,
        "source_agent": source_agent,
        "target": target,
        "action": action,
        "input_summary": str(input_summary)[:200],
        "output_summary": str(output_summary)[:200],
        "tokens": tokens,
        "latency_ms": latency_ms,
        "status": status,
        "error": str(error)[:500] if error else None,
        "gotcha_triggered": gotcha_triggered
    }
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, 'a') as f:
        f.write(json.dumps(event) + '\n')
    return event
