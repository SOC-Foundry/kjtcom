#!/usr/bin/env python3
"""Rebuild iteration_registry.json using RAG (ChromaDB) + Qwen3.5-9B scoring.

Key fix over v1: nomic-embed-text embeds (tiny, no OOM), Qwen scores with
limited context (2-4K tokens per iteration, no OOM).
"""
import os
import sys
import json
import time
import subprocess
import requests
import chromadb

CHROMA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'chromadb')
REGISTRY_PATH = os.path.join(os.path.dirname(__file__), '..', 'iteration_registry.json')
OLLAMA_EMBED_URL = 'http://localhost:11434/api/embed'
OLLAMA_CHAT_URL = 'http://localhost:11434/api/chat'
EMBED_MODEL = 'nomic-embed-text'
SCORE_MODEL = 'qwen3.5:9b'

# All known iterations in chronological order
ITERATIONS = [
    'v0.5', 'v1.6', 'v1.7', 'v2.8', 'v2.9', 'v3.10', 'v3.11',
    'v4.12', 'v4.13', 'v5.14', 'v6.15', 'v6.16', 'v6.17', 'v6.18',
    'v6.19', 'v6.20', 'v7.21', 'v8.22', 'v8.23', 'v8.24', 'v8.25',
    'v8.26', 'v9.27', 'v9.28', 'v9.29', 'v9.30', 'v9.31', 'v9.32',
    'v9.33', 'v9.34', 'v9.35', 'v9.36', 'v9.37'
]

PHASES = {
    'v0.5': 0, 'v1.6': 1, 'v1.7': 1, 'v2.8': 2, 'v2.9': 2,
    'v3.10': 3, 'v3.11': 3, 'v4.12': 4, 'v4.13': 4, 'v5.14': 5,
    'v6.15': 6, 'v6.16': 6, 'v6.17': 6, 'v6.18': 6, 'v6.19': 6,
    'v6.20': 6, 'v7.21': 7, 'v8.22': 8, 'v8.23': 8, 'v8.24': 8,
    'v8.25': 8, 'v8.26': 8, 'v9.27': 9, 'v9.28': 9, 'v9.29': 9,
    'v9.30': 9, 'v9.31': 9, 'v9.32': 9, 'v9.33': 9, 'v9.34': 9,
    'v9.35': 9, 'v9.36': 9, 'v9.37': 9
}

QWEN_PROMPT = """/no_think
You are analyzing a kjtcom project iteration. Based on the context chunks below, extract structured data for iteration {version}.

Return ONLY valid JSON (no markdown, no explanation) with this schema:
{{
  "version": "{version}",
  "phase": {phase},
  "focus": "one-line summary of iteration focus",
  "agents": {{
    "primary": "agent name",
    "consulted": ["other agents"],
    "local_llms": ["model names if any"],
    "mcp_servers": ["server names if any"]
  }},
  "outcomes": {{
    "interventions": 0,
    "gotchas_created": ["G##"],
    "gotchas_resolved": ["G##"],
    "flutter_analyze": "0 issues or N/A",
    "flutter_test": "X/Y pass or N/A",
    "deploys": 0
  }},
  "failures": ["list of failures"],
  "successes": ["list of successes"],
  "improvements": ["list of improvements or recommendations"]
}}

Context chunks for {version}:
{chunks}
"""


def get_embedding(text):
    resp = requests.post(OLLAMA_EMBED_URL, json={
        'model': EMBED_MODEL,
        'input': [text]
    }, timeout=30)
    resp.raise_for_status()
    return resp.json()['embeddings'][0]


def query_chromadb(collection, version, n_results=8):
    """Get relevant chunks for a specific iteration version."""
    # Search by version filter AND semantic query
    try:
        # First try version-filtered results
        results = collection.get(
            where={'version': version},
            include=['documents', 'metadatas'],
            limit=20
        )
        if results['ids']:
            # Combine chunks into context, cap at ~3000 chars
            combined = ''
            for doc in results['documents']:
                if len(combined) + len(doc) < 3000:
                    combined += doc + '\n---\n'
            return combined
    except Exception:
        pass

    # Fallback: semantic search
    embedding = get_embedding(f'kjtcom iteration {version} build report outcomes')
    results = collection.query(
        query_embeddings=[embedding],
        n_results=n_results,
        include=['documents', 'metadatas']
    )

    combined = ''
    for doc in results['documents'][0]:
        if len(combined) + len(doc) < 3000:
            combined += doc + '\n---\n'
    return combined


def score_with_qwen(version, phase, chunks):
    """Ask Qwen to extract structured data from chunks."""
    prompt = QWEN_PROMPT.format(
        version=version,
        phase=phase,
        chunks=chunks[:3500]
    )

    payload = {
        'model': SCORE_MODEL,
        'messages': [{'role': 'user', 'content': prompt}],
        'stream': False,
        'options': {'num_predict': 2048}
    }

    result = subprocess.run(
        ['curl', '-s', OLLAMA_CHAT_URL, '-d', json.dumps(payload)],
        capture_output=True, text=True, timeout=300
    )

    response = json.loads(result.stdout)
    content = response['message']['content']
    tokens = {
        'prompt_tokens': response.get('prompt_eval_count', 0),
        'eval_tokens': response.get('eval_count', 0)
    }

    # Strip markdown code fences if present
    import re
    content = re.sub(r'```json\s*', '', content)
    content = re.sub(r'```\s*', '', content)
    content = content.strip()

    # Extract JSON from response
    json_start = content.find('{')
    json_end = content.rfind('}') + 1
    if json_start >= 0 and json_end > json_start:
        try:
            parsed = json.loads(content[json_start:json_end])
            return parsed, tokens
        except json.JSONDecodeError:
            pass

    # Return minimal entry on parse failure
    return {
        'version': version,
        'phase': phase,
        'focus': 'Parse failed - manual review needed',
        'agents': {'primary': 'unknown', 'consulted': [], 'local_llms': [], 'mcp_servers': []},
        'outcomes': {'interventions': -1, 'gotchas_created': [], 'gotchas_resolved': [],
                     'flutter_analyze': 'N/A', 'flutter_test': 'N/A', 'deploys': 0},
        'failures': ['Qwen JSON parse failed'],
        'successes': [],
        'improvements': []
    }, tokens


def main():
    print('=== RAG-Augmented Registry Builder v2 ===')
    print(f'Processing {len(ITERATIONS)} iterations')

    # Connect to ChromaDB
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    try:
        collection = client.get_collection('kjtcom_archive')
        print(f'ChromaDB collection: {collection.count()} documents')
    except Exception as e:
        print(f'ERROR: ChromaDB collection not found. Run embed_archive.py first.')
        print(f'  {e}')
        sys.exit(1)

    registry = {
        'metadata': {
            'generated': time.strftime('%Y-%m-%dT%H:%M:%S'),
            'generator': 'build_registry_v2.py (RAG + Qwen)',
            'model': f'{SCORE_MODEL} (evaluator) + {EMBED_MODEL} (embedder)',
            'total_iterations': len(ITERATIONS),
            'failed_iterations': [],
            'total_prompt_tokens': 0,
            'total_eval_tokens': 0
        },
        'iterations': [],
        'gotcha_registry': []
    }

    total_prompt = 0
    total_eval = 0

    for i, version in enumerate(ITERATIONS):
        phase = PHASES.get(version, -1)
        print(f'\n[{i+1}/{len(ITERATIONS)}] Processing {version} (Phase {phase})...')

        # Get relevant chunks from ChromaDB
        chunks = query_chromadb(collection, version)
        if not chunks.strip():
            print(f'  WARNING: No chunks found for {version}, using minimal entry')
            registry['iterations'].append({
                'version': version,
                'phase': phase,
                'focus': 'No archive data found',
                'agents': {'primary': 'unknown', 'consulted': [], 'local_llms': [], 'mcp_servers': []},
                'outcomes': {'interventions': -1, 'gotchas_created': [], 'gotchas_resolved': [],
                             'flutter_analyze': 'N/A', 'flutter_test': 'N/A', 'deploys': 0},
                'failures': [],
                'successes': [],
                'improvements': []
            })
            registry['metadata']['failed_iterations'].append(version)
            continue

        # Score with Qwen
        entry, tokens = score_with_qwen(version, phase, chunks)
        total_prompt += tokens.get('prompt_tokens', 0)
        total_eval += tokens.get('eval_tokens', 0)

        registry['iterations'].append(entry)
        print(f'  OK: {entry.get("focus", "?")[:60]}')
        print(f'  Tokens: prompt={tokens.get("prompt_tokens", 0)}, eval={tokens.get("eval_tokens", 0)}')

    registry['metadata']['total_prompt_tokens'] = total_prompt
    registry['metadata']['total_eval_tokens'] = total_eval

    # Write registry
    with open(REGISTRY_PATH, 'w') as f:
        json.dump(registry, f, indent=2)

    print(f'\n=== Done ===')
    print(f'Registry written to {REGISTRY_PATH}')
    print(f'{len(registry["iterations"])} iterations processed')
    print(f'Failed: {registry["metadata"]["failed_iterations"]}')
    print(f'Total tokens: prompt={total_prompt}, eval={total_eval}')


if __name__ == '__main__':
    main()
