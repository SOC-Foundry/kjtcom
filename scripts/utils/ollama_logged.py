#!/usr/bin/env python3
"""Auto-logging wrapper around Ollama API calls.

Every chat or embed call is automatically logged to the IAO event stream.
"""
import json
import time
import requests

from utils.iao_logger import log_event
from utils.ollama_config import merge_defaults

OLLAMA_URL = 'http://localhost:11434'


def chat_logged(model, prompt, source_agent="unknown", stream=False,
                options=None, think=None, evaluation=False):
    """Send a chat request to Ollama and log the event.

    Returns dict with keys: content, prompt_eval_count, eval_count, raw_response
    """
    payload = {
        'model': model,
        'messages': [{'role': 'user', 'content': prompt}],
    }
    if stream:
        payload['stream'] = stream
    if options:
        payload['options'] = options
    if think is not None:
        payload['think'] = think
    payload = merge_defaults(payload, evaluation=evaluation)

    start = time.time()
    status = "success"
    content = ""
    tokens = {"prompt": 0, "eval": 0, "total": 0}
    error = None

    try:
        resp = requests.post(f'{OLLAMA_URL}/api/chat',
                             json=payload, timeout=300)
        resp.raise_for_status()
        data = resp.json()
        content = data.get('message', {}).get('content', '')
        tokens = {
            "prompt": data.get('prompt_eval_count', 0),
            "eval": data.get('eval_count', 0),
            "total": data.get('prompt_eval_count', 0) + data.get('eval_count', 0)
        }
        if not content.strip():
            status = "empty_response"
    except requests.Timeout:
        status = "timeout"
        error = "Request timed out after 300s"
    except Exception as e:
        status = "error"
        error = str(e)

    latency = int((time.time() - start) * 1000)

    log_event("llm_call", source_agent, model, "chat",
              input_summary=prompt[:200],
              output_summary=content[:200],
              tokens=tokens,
              latency_ms=latency,
              status=status,
              error=error)

    return {
        'content': content,
        'prompt_eval_count': tokens['prompt'],
        'eval_count': tokens['eval'],
        'raw_response': data if status == "success" else None
    }


def embed_logged(model, texts, source_agent="unknown"):
    """Get embeddings from Ollama and log the event.

    Returns list of embedding vectors.
    """
    start = time.time()
    status = "success"
    error = None
    embeddings = []

    try:
        resp = requests.post(f'{OLLAMA_URL}/api/embed',
                             json={'model': model, 'input': texts},
                             timeout=120)
        resp.raise_for_status()
        embeddings = resp.json()['embeddings']
    except requests.Timeout:
        status = "timeout"
        error = "Request timed out after 120s"
    except Exception as e:
        status = "error"
        error = str(e)

    latency = int((time.time() - start) * 1000)

    input_desc = f"{len(texts)} texts, first: {texts[0][:100]}" if texts else "empty"
    log_event("llm_call", source_agent, model, "embed",
              input_summary=input_desc,
              output_summary=f"{len(embeddings)} embeddings returned",
              latency_ms=latency,
              status=status,
              error=error)

    return embeddings
