#!/usr/bin/env python3
"""Run Qwen3.5-9B evaluator against a build log."""
import json
import subprocess
import sys

def run_evaluator(version, build_log_path, active_gotchas):
    with open(build_log_path) as f:
        build_log = f.read()

    with open('docs/archive/evaluator-prompt.md') as f:
        prompt_template = f.read()

    prompt = '/no_think\n' + (prompt_template
        .replace('{version}', version)
        .replace('{active_gotchas}', active_gotchas)
        .replace('{build_log_content}', build_log[:4000]))

    payload = {
        'model': 'qwen3.5:9b',
        'messages': [{'role': 'user', 'content': prompt}],
        'stream': False,
        'options': {'num_predict': 2048}
    }

    result = subprocess.run(
        ['curl', '-s', 'http://localhost:11434/api/chat', '-d', json.dumps(payload)],
        capture_output=True, text=True, timeout=180
    )

    response = json.loads(result.stdout)
    content = response['message']['content']

    # Extract JSON from response (may have thinking tags or markdown)
    # Try to find JSON block
    json_start = content.find('{')
    json_end = content.rfind('}') + 1
    if json_start >= 0 and json_end > json_start:
        json_str = content[json_start:json_end]
        try:
            parsed = json.loads(json_str)
            print(json.dumps(parsed, indent=2))
            return parsed
        except json.JSONDecodeError:
            pass

    # If JSON extraction failed, print raw content
    print("RAW RESPONSE:")
    print(content)
    return None

if __name__ == '__main__':
    version = sys.argv[1] if len(sys.argv) > 1 else 'v9.35'
    build_log_path = sys.argv[2] if len(sys.argv) > 2 else 'docs/archive/kjtcom-build-v9.35.md'
    gotchas = sys.argv[3] if len(sys.argv) > 3 else 'G45,G47,G34,G1,G11'
    run_evaluator(version, build_log_path, gotchas)
