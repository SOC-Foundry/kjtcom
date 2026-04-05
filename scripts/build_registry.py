#!/usr/bin/env python3
"""Build iteration_registry.json by feeding docs/archive/ to Qwen3.5-9B.

Groups archive files by iteration, feeds each batch to Qwen via Ollama API,
and merges structured JSON into iteration_registry.json.
"""
import json
import os
import re
import sys
import time
import requests
from pathlib import Path

ARCHIVE_DIR = Path('docs/archive')
OUTPUT_FILE = Path('iteration_registry.json')
OLLAMA_URL = 'http://localhost:11434/api/chat'
MODEL = 'qwen3.5:9b'

# Extraction prompt for Qwen
EXTRACTION_PROMPT = """/no_think
Extract from these IAO iteration artifacts into valid JSON. Output ONLY the JSON object, no markdown fences.

Schema: {"version":"","date":"","phase":0,"focus":"","agents":{"primary":"","consulted":[],"local_llms":[],"mcp_servers":[]},"outcomes":{"interventions":0,"gotchas_created":[],"gotchas_resolved":[],"flutter_analyze":"","flutter_test":"","deploys":0},"failures":[],"successes":[],"improvements":[]}"""


def find_iterations():
    """Group archive files by iteration version."""
    iterations = {}
    for f in sorted(ARCHIVE_DIR.glob('*.md')):
        # Match version patterns like v0.5, v9.34
        match = re.search(r'v(\d+\.\d+)', f.name)
        if not match:
            continue
        version = f'v{match.group(1)}'
        if version not in iterations:
            iterations[version] = []
        iterations[version].append(f)
    return dict(sorted(iterations.items(), key=lambda x: [int(p) for p in x[0][1:].split('.')]))


def read_iteration_files(files):
    """Concatenate iteration files, capping total size."""
    content = []
    total = 0
    max_chars = 5000  # Smaller chunks for faster Qwen processing
    for f in sorted(files):
        text = f.read_text(errors='replace')
        if total + len(text) > max_chars:
            # Truncate this file
            remaining = max_chars - total
            if remaining > 500:
                text = text[:remaining] + '\n[TRUNCATED]'
            else:
                continue
        content.append(f'=== {f.name} ===\n{text}')
        total += len(text)
    return '\n\n'.join(content)


def query_qwen(content):
    """Send content to Qwen and get structured JSON back."""
    payload = {
        'model': MODEL,
        'messages': [
            {'role': 'user', 'content': f'{EXTRACTION_PROMPT}\n\n{content}'}
        ],
        'stream': False,
    }
    try:
        resp = requests.post(OLLAMA_URL, json=payload, timeout=300)
        resp.raise_for_status()
        text = resp.json()['message']['content']
        # Try to extract JSON from response
        text = text.strip()
        # Remove markdown fences if present
        if text.startswith('```'):
            text = re.sub(r'^```(?:json)?\s*', '', text)
            text = re.sub(r'\s*```$', '', text)
        return json.loads(text)
    except json.JSONDecodeError as e:
        print(f'    JSON parse error: {e}', file=sys.stderr)
        print(f'    Raw response: {text[:200]}', file=sys.stderr)
        return None
    except Exception as e:
        print(f'    Qwen query error: {e}', file=sys.stderr)
        return None


def build_gotcha_registry(iterations_data):
    """Extract gotcha events from iteration data to build registry."""
    gotchas = {}
    for it in iterations_data:
        version = it.get('version', '')
        for g in it.get('outcomes', {}).get('gotchas_created', []):
            if g not in gotchas:
                gotchas[g] = {
                    'id': g,
                    'status': 'OPEN',
                    'created_in': version,
                    'resolved_in': None,
                    'agents_involved': [],
                }
            agent = it.get('agents', {}).get('primary', 'unknown')
            if agent not in gotchas[g]['agents_involved']:
                gotchas[g]['agents_involved'].append(agent)
        for g in it.get('outcomes', {}).get('gotchas_resolved', []):
            if g not in gotchas:
                gotchas[g] = {
                    'id': g,
                    'status': 'RESOLVED',
                    'created_in': 'unknown',
                    'resolved_in': version,
                    'agents_involved': [],
                }
            else:
                gotchas[g]['status'] = 'RESOLVED'
                gotchas[g]['resolved_in'] = version
            agent = it.get('agents', {}).get('primary', 'unknown')
            if agent not in gotchas[g]['agents_involved']:
                gotchas[g]['agents_involved'].append(agent)
    return list(gotchas.values())


def main():
    iterations = find_iterations()
    print(f'Found {len(iterations)} iterations in docs/archive/')

    results = []
    failed = []

    for i, (version, files) in enumerate(iterations.items()):
        print(f'[{i+1}/{len(iterations)}] Processing {version} ({len(files)} files)...')
        content = read_iteration_files(files)

        data = query_qwen(content)
        if data:
            # Ensure version is set correctly
            data['version'] = version
            results.append(data)
            print(f'    OK - focus: {data.get("focus", "?")[:60]}')
        else:
            failed.append(version)
            print(f'    FAILED - skipping')

        # Brief pause between requests to avoid overwhelming Ollama
        if i < len(iterations) - 1:
            time.sleep(1)

    # Build gotcha registry from extracted data
    gotcha_registry = build_gotcha_registry(results)

    # Assemble final registry
    registry = {
        'metadata': {
            'generated': time.strftime('%Y-%m-%dT%H:%M:%S'),
            'generator': 'build_registry.py',
            'model': MODEL,
            'total_iterations': len(results),
            'failed_iterations': failed,
        },
        'iterations': results,
        'gotcha_registry': gotcha_registry,
    }

    with open(OUTPUT_FILE, 'w') as f:
        json.dump(registry, f, indent=2)
    print(f'\nWrote {OUTPUT_FILE} with {len(results)} iterations and {len(gotcha_registry)} gotchas')
    if failed:
        print(f'Failed iterations: {", ".join(failed)}')


if __name__ == '__main__':
    main()
