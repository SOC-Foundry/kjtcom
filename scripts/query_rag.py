#!/usr/bin/env python3
"""Semantic search over kjtcom archive via ChromaDB + nomic-embed-text."""
import os
import sys
import json
import requests
import chromadb

CHROMA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'chromadb')
OLLAMA_URL = 'http://localhost:11434/api/embed'
MODEL = 'nomic-embed-text'


def get_embedding(text):
    """Get embedding for a single query."""
    resp = requests.post(OLLAMA_URL, json={
        'model': MODEL,
        'input': [text]
    }, timeout=30)
    resp.raise_for_status()
    return resp.json()['embeddings'][0]


def query(text, n_results=5, version_filter=None):
    """Search ChromaDB for chunks matching the query."""
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    collection = client.get_collection('kjtcom_archive')

    embedding = get_embedding(text)

    where_filter = None
    if version_filter:
        where_filter = {'version': version_filter}

    results = collection.query(
        query_embeddings=[embedding],
        n_results=n_results,
        where=where_filter,
        include=['documents', 'metadatas', 'distances']
    )

    return results


def main():
    if len(sys.argv) < 2:
        print('Usage: python3 query_rag.py "your question" [n_results] [version_filter]')
        sys.exit(1)

    q = sys.argv[1]
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    version = sys.argv[3] if len(sys.argv) > 3 else None

    print(f'Query: "{q}" (top {n})')
    if version:
        print(f'Filter: version={version}')
    print('---')

    results = query(q, n_results=n, version_filter=version)

    for i in range(len(results['ids'][0])):
        doc_id = results['ids'][0][i]
        distance = results['distances'][0][i]
        meta = results['metadatas'][0][i]
        doc = results['documents'][0][i]

        print(f'\n[{i+1}] Score: {1 - distance:.3f} | {meta.get("filename", "?")} '
              f'| {meta.get("version", "?")} | {meta.get("file_type", "?")}')
        print(f'    {doc[:200]}...' if len(doc) > 200 else f'    {doc}')

    # Also output as JSON for programmatic use
    if '--json' in sys.argv:
        output = []
        for i in range(len(results['ids'][0])):
            output.append({
                'id': results['ids'][0][i],
                'score': 1 - results['distances'][0][i],
                'metadata': results['metadatas'][0][i],
                'text': results['documents'][0][i]
            })
        print('\n---JSON---')
        print(json.dumps(output, indent=2))


if __name__ == '__main__':
    main()
