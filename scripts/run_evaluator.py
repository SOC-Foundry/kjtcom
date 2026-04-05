#!/usr/bin/env python3
"""Run Qwen3.5-9B evaluator against a build log. v2: with token tracking + P3 logging."""
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))
from utils.iao_logger import log_event
from utils.ollama_config import merge_defaults

OLLAMA_URL = 'http://localhost:11434/api/chat'
SCORES_PATH = 'agent_scores.json'


def run_evaluator(version, build_log_path, active_gotchas):
    with open(build_log_path) as f:
        build_log = f.read()

    with open('docs/archive/evaluator-prompt.md') as f:
        prompt_template = f.read()

    prompt = '/no_think\n' + (prompt_template
        .replace('{version}', version)
        .replace('{active_gotchas}', active_gotchas)
        .replace('{build_log_content}', build_log[:4000]))

    payload = merge_defaults({
        'model': 'qwen3.5:9b',
        'messages': [{'role': 'user', 'content': prompt}],
    }, evaluation=True)

    start_time = time.time()
    result = subprocess.run(
        ['curl', '-s', OLLAMA_URL, '-d', json.dumps(payload)],
        capture_output=True, text=True, timeout=180
    )

    response = json.loads(result.stdout)
    content = response['message']['content']
    latency = int((time.time() - start_time) * 1000)

    # Token tracking from Ollama response metadata
    tokens = {
        'prompt_tokens': response.get('prompt_eval_count', 0),
        'eval_tokens': response.get('eval_count', 0),
        'total_tokens': response.get('prompt_eval_count', 0) + response.get('eval_count', 0)
    }

    log_event("llm_call", "qwen3.5-9b", "qwen3.5:9b", "evaluate",
              input_summary=prompt[:200],
              output_summary=content[:200],
              tokens={"prompt": tokens['prompt_tokens'], "eval": tokens['eval_tokens'],
                      "total": tokens['total_tokens']},
              latency_ms=latency,
              status="success" if content.strip() else "empty_response")

    print(f'Tokens: prompt={tokens["prompt_tokens"]}, '
          f'eval={tokens["eval_tokens"]}, '
          f'total={tokens["total_tokens"]}')

    # Extract JSON from response
    json_start = content.find('{')
    json_end = content.rfind('}') + 1
    if json_start >= 0 and json_end > json_start:
        json_str = content[json_start:json_end]
        try:
            parsed = json.loads(json_str)
            # Inject token tracking into each score entry
            if 'scores' in parsed:
                for score in parsed['scores']:
                    if 'prompt_tokens' not in score:
                        score['prompt_tokens'] = 0
                        score['eval_tokens'] = 0
                        score['total_tokens'] = 0
            # Add evaluator token usage
            parsed['evaluator_tokens'] = tokens
            print(json.dumps(parsed, indent=2))
            return parsed, tokens
        except json.JSONDecodeError:
            pass

    print("RAW RESPONSE:")
    print(content)
    return None, tokens


def append_to_scores(entry, tokens):
    """Append evaluation entry to agent_scores.json with token tracking."""
    try:
        with open(SCORES_PATH) as f:
            scores = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        scores = []

    if entry:
        # Add token tracking to the entry
        entry['evaluator_tokens'] = tokens
        scores.append(entry)
    else:
        # Minimal entry if parse failed
        scores.append({
            'iteration': 'unknown',
            'date': time.strftime('%Y-%m-%d'),
            'evaluator': 'qwen3.5:9b',
            'scores': [],
            'gotcha_events': [],
            'evaluator_tokens': tokens,
            'error': 'Failed to parse Qwen response'
        })

    with open(SCORES_PATH, 'w') as f:
        json.dump(scores, f, indent=2)

    print(f'\nAppended to {SCORES_PATH}')


if __name__ == '__main__':
    version = sys.argv[1] if len(sys.argv) > 1 else 'v9.38'
    build_log_path = sys.argv[2] if len(sys.argv) > 2 else 'docs/kjtcom-build-v9.38.md'
    gotchas = sys.argv[3] if len(sys.argv) > 3 else 'G47,G51,G52,G53'

    entry, tokens = run_evaluator(version, build_log_path, gotchas)

    if '--append' in sys.argv:
        append_to_scores(entry, tokens)
