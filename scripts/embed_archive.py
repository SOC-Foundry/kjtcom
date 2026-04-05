#!/usr/bin/env python3
"""Embed docs/archive/ files into ChromaDB using nomic-embed-text via Ollama. P3 logged."""
import os
import json
import re
import sys
import time
import requests
import chromadb

sys.path.insert(0, os.path.dirname(__file__))
from utils.iao_logger import log_event

ARCHIVE_DIR = os.path.join(os.path.dirname(__file__), '..', 'docs', 'archive')
CHROMA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'chromadb')
OLLAMA_URL = 'http://localhost:11434/api/embed'
MODEL = 'nomic-embed-text'
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
BATCH_SIZE = 20


def chunk_text(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    """Split text into overlapping chunks."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
        if start + overlap >= len(text):
            break
    return chunks


def extract_metadata(filename):
    """Extract iteration version and file type from filename."""
    meta = {'filename': filename}
    # Match patterns like kjtcom-build-v9.37.md or kjtcom-design-v1.6.md
    m = re.match(r'kjtcom-(\w+)-v([\d.]+)\.md', filename)
    if m:
        meta['file_type'] = m.group(1)  # design, plan, build, report
        meta['version'] = f'v{m.group(2)}'
    else:
        meta['file_type'] = 'other'
        meta['version'] = 'unknown'
    return meta


def get_embeddings(texts):
    """Get embeddings from Ollama nomic-embed-text."""
    start = time.time()
    resp = requests.post(OLLAMA_URL, json={
        'model': MODEL,
        'input': texts
    }, timeout=120)
    resp.raise_for_status()
    latency = int((time.time() - start) * 1000)
    log_event("llm_call", "claude-code", MODEL, "embed",
              input_summary=f"{len(texts)} texts, first: {texts[0][:100]}",
              output_summary=f"{len(texts)} embeddings returned",
              latency_ms=latency, status="success")
    return resp.json()['embeddings']


def main():
    print(f'Scanning {ARCHIVE_DIR}...')
    files = sorted([f for f in os.listdir(ARCHIVE_DIR) if f.endswith('.md')])
    print(f'Found {len(files)} markdown files')

    # Initialize ChromaDB
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    # Delete existing collection if re-running
    try:
        client.delete_collection('kjtcom_archive')
    except Exception:
        pass
    collection = client.create_collection(
        name='kjtcom_archive',
        metadata={'hnsw:space': 'cosine'}
    )

    total_chunks = 0
    all_ids = []
    all_docs = []
    all_metas = []
    all_embeddings = []

    for i, filename in enumerate(files):
        filepath = os.path.join(ARCHIVE_DIR, filename)
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            text = f.read()

        if not text.strip():
            continue

        meta = extract_metadata(filename)
        chunks = chunk_text(text)

        for j, chunk in enumerate(chunks):
            chunk_id = f'{filename}::chunk_{j}'
            all_ids.append(chunk_id)
            all_docs.append(chunk)
            all_metas.append({**meta, 'chunk_index': j, 'total_chunks': len(chunks)})

        total_chunks += len(chunks)
        if (i + 1) % 20 == 0:
            print(f'  Processed {i + 1}/{len(files)} files ({total_chunks} chunks)')

    print(f'Total: {len(files)} files -> {total_chunks} chunks')
    print(f'Embedding {total_chunks} chunks in batches of {BATCH_SIZE}...')

    # Embed and add in batches
    for start in range(0, len(all_ids), BATCH_SIZE):
        end = min(start + BATCH_SIZE, len(all_ids))
        batch_docs = all_docs[start:end]
        batch_embeddings = get_embeddings(batch_docs)

        collection.add(
            ids=all_ids[start:end],
            documents=batch_docs,
            metadatas=all_metas[start:end],
            embeddings=batch_embeddings
        )

        done = end
        print(f'  Embedded {done}/{total_chunks} chunks')

    print(f'\nDone. {total_chunks} chunks stored in {CHROMA_DIR}')
    print(f'Collection: kjtcom_archive ({collection.count()} documents)')


if __name__ == '__main__':
    main()
