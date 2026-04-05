#!/usr/bin/env python3
"""Semantic search over archive via ChromaDB + nomic-embed-text.

Usage: python3 query_rag.py "your question" [n_results]
"""
import os
import sys
import json
import requests
import chromadb

OLLAMA_URL = 'http://localhost:11434/api/embed'
MODEL = 'nomic-embed-text'


def query(text, chroma_dir='data/chromadb', n_results=5):
    resp = requests.post(OLLAMA_URL, json={'model': MODEL, 'input': [text]}, timeout=30)
    resp.raise_for_status()
    embedding = resp.json()['embeddings'][0]

    client = chromadb.PersistentClient(path=chroma_dir)
    collection = client.get_collection('archive')
    return collection.query(query_embeddings=[embedding], n_results=n_results,
                            include=['documents', 'metadatas', 'distances'])


def main():
    if len(sys.argv) < 2:
        print('Usage: python3 query_rag.py "question" [n_results]')
        sys.exit(1)
    q = sys.argv[1]
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    results = query(q, n_results=n)
    for i in range(len(results['ids'][0])):
        score = 1 - results['distances'][0][i]
        meta = results['metadatas'][0][i]
        doc = results['documents'][0][i]
        print(f'[{i+1}] {score:.3f} | {meta.get("filename","?")} | {doc[:150]}...')


if __name__ == '__main__':
    main()
