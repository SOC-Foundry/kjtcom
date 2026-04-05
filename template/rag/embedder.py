#!/usr/bin/env python3
"""Embed docs/archive/ files into ChromaDB using nomic-embed-text via Ollama.

Usage: python3 embedder.py [archive_dir] [chromadb_dir]
Defaults: docs/archive/ -> data/chromadb/

Prerequisites:
    ollama pull nomic-embed-text
    pip install chromadb --break-system-packages
"""
import os
import sys
import re
import requests
import chromadb

OLLAMA_URL = 'http://localhost:11434/api/embed'
MODEL = 'nomic-embed-text'
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
BATCH_SIZE = 20


def chunk_text(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
        if start + overlap >= len(text):
            break
    return chunks


def get_embeddings(texts):
    resp = requests.post(OLLAMA_URL, json={'model': MODEL, 'input': texts}, timeout=120)
    resp.raise_for_status()
    return resp.json()['embeddings']


def main():
    archive_dir = sys.argv[1] if len(sys.argv) > 1 else 'docs/archive'
    chroma_dir = sys.argv[2] if len(sys.argv) > 2 else 'data/chromadb'

    files = sorted([f for f in os.listdir(archive_dir) if f.endswith('.md')])
    print(f'Found {len(files)} files in {archive_dir}')

    client = chromadb.PersistentClient(path=chroma_dir)
    try:
        client.delete_collection('archive')
    except Exception:
        pass
    collection = client.create_collection(name='archive', metadata={'hnsw:space': 'cosine'})

    all_ids, all_docs, all_metas = [], [], []
    for filename in files:
        with open(os.path.join(archive_dir, filename), 'r', errors='replace') as f:
            text = f.read()
        if not text.strip():
            continue
        for j, chunk in enumerate(chunk_text(text)):
            all_ids.append(f'{filename}::chunk_{j}')
            all_docs.append(chunk)
            all_metas.append({'filename': filename, 'chunk_index': j})

    print(f'Embedding {len(all_ids)} chunks...')
    for start in range(0, len(all_ids), BATCH_SIZE):
        end = min(start + BATCH_SIZE, len(all_ids))
        embeddings = get_embeddings(all_docs[start:end])
        collection.add(ids=all_ids[start:end], documents=all_docs[start:end],
                       metadatas=all_metas[start:end], embeddings=embeddings)
        print(f'  {end}/{len(all_ids)}')

    print(f'Done. {collection.count()} chunks in {chroma_dir}')


if __name__ == '__main__':
    main()
