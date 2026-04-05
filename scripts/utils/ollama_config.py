#!/usr/bin/env python3
"""Ollama default configuration for all kjtcom scripts.

G51 permanent fix: think=False on all calls.
Token efficiency: num_predict=512 default, 2048 for evaluations only.
"""

OLLAMA_DEFAULTS = {
    "stream": False,
    "think": False,
    "options": {
        "num_predict": 512,
    },
}

OLLAMA_EVAL_DEFAULTS = {
    "stream": False,
    "think": False,
    "options": {
        "num_predict": 2048,
    },
}


def merge_defaults(payload, evaluation=False):
    """Merge OLLAMA_DEFAULTS into a request payload. Caller values take priority."""
    defaults = OLLAMA_EVAL_DEFAULTS if evaluation else OLLAMA_DEFAULTS
    merged = dict(defaults)
    merged.update(payload)
    # Merge nested options
    if "options" in defaults and "options" in payload:
        merged_opts = dict(defaults["options"])
        merged_opts.update(payload["options"])
        merged["options"] = merged_opts
    return merged
