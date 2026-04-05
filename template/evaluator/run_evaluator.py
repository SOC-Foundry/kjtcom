#!/usr/bin/env python3
"""Qwen3.5-9B evaluator - scores agent performance per iteration.

Usage: python3 run_evaluator.py [version] [build_log_path] [active_gotchas]
       python3 run_evaluator.py v1.0 docs/build-v1.0.md "G1,G2" --append
"""
import json
import subprocess
import sys
import time

OLLAMA_URL = 'http://localhost:11434/api/chat'
SCORES_PATH = 'agent_scores.json'

EVALUATOR_PROMPT = """/no_think
You are evaluating agent performance for iteration {version}.
Active gotchas: {active_gotchas}

Score each agent on these dimensions (1-10 each, 50 max):
- problem_analysis: Understanding the problem correctly
- code_correctness: Producing working, bug-free code
- efficiency: Minimal wasted effort, good tool usage
- gotcha_avoidance: Avoiding known failure patterns
- novel_contribution: New insights, patterns, or solutions

Build log excerpt:
{build_log_content}

Return ONLY valid JSON:
{{
  "iteration": "{version}",
  "date": "{date}",
  "evaluator": "qwen3.5:9b",
  "scores": [
    {{
      "agent": "Agent Name",
      "role": "Role description",
      "problem_analysis": 0,
      "code_correctness": 0,
      "efficiency": 0,
      "gotcha_avoidance": 0,
      "novel_contribution": 0,
      "total": 0,
      "prompt_tokens": 0,
      "eval_tokens": 0,
      "total_tokens": 0,
      "notes": "Brief assessment"
    }}
  ],
  "gotcha_events": []
}}
"""


def run_evaluator(version, build_log_path, active_gotchas):
    with open(build_log_path) as f:
        build_log = f.read()

    prompt = EVALUATOR_PROMPT.format(
        version=version,
        active_gotchas=active_gotchas,
        build_log_content=build_log[:4000],
        date=time.strftime('%Y-%m-%d')
    )

    payload = {
        'model': 'qwen3.5:9b',
        'messages': [{'role': 'user', 'content': prompt}],
        'stream': False,
        'options': {'num_predict': 2048}
    }

    result = subprocess.run(
        ['curl', '-s', OLLAMA_URL, '-d', json.dumps(payload)],
        capture_output=True, text=True, timeout=180
    )

    response = json.loads(result.stdout)
    content = response['message']['content']
    tokens = {
        'prompt_tokens': response.get('prompt_eval_count', 0),
        'eval_tokens': response.get('eval_count', 0),
        'total_tokens': response.get('prompt_eval_count', 0) + response.get('eval_count', 0)
    }

    print(f'Tokens: prompt={tokens["prompt_tokens"]}, eval={tokens["eval_tokens"]}, total={tokens["total_tokens"]}')

    json_start = content.find('{')
    json_end = content.rfind('}') + 1
    if json_start >= 0 and json_end > json_start:
        try:
            parsed = json.loads(content[json_start:json_end])
            parsed['evaluator_tokens'] = tokens
            print(json.dumps(parsed, indent=2))
            return parsed, tokens
        except json.JSONDecodeError:
            pass

    print("RAW RESPONSE:")
    print(content)
    return None, tokens


def append_to_scores(entry, tokens):
    try:
        with open(SCORES_PATH) as f:
            scores = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        scores = []

    if entry:
        entry['evaluator_tokens'] = tokens
        scores.append(entry)
    else:
        scores.append({
            'iteration': 'unknown',
            'date': time.strftime('%Y-%m-%d'),
            'evaluator': 'qwen3.5:9b',
            'scores': [],
            'evaluator_tokens': tokens,
            'error': 'Failed to parse Qwen response'
        })

    with open(SCORES_PATH, 'w') as f:
        json.dump(scores, f, indent=2)
    print(f'\nAppended to {SCORES_PATH}')


if __name__ == '__main__':
    version = sys.argv[1] if len(sys.argv) > 1 else 'v1.0'
    build_log_path = sys.argv[2] if len(sys.argv) > 2 else 'docs/build-v1.0.md'
    gotchas = sys.argv[3] if len(sys.argv) > 3 else ''
    entry, tokens = run_evaluator(version, build_log_path, gotchas)
    if '--append' in sys.argv:
        append_to_scores(entry, tokens)
