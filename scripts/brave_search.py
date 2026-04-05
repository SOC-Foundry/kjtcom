#!/usr/bin/env python3
"""Brave Search API wrapper - returns top 5 web results."""
import os
import sys
import json
import requests

BRAVE_API_URL = 'https://api.search.brave.com/res/v1/web/search'


def search(query, count=5):
    """Search Brave Web Search API. Returns top results with title, URL, snippet."""
    api_key = os.environ.get('KJTCOM_BRAVE_SEARCH_API_KEY')
    if not api_key:
        return {'error': 'KJTCOM_BRAVE_SEARCH_API_KEY not set in environment'}

    headers = {
        'X-Subscription-Token': api_key,
        'Accept': 'application/json'
    }
    params = {
        'q': query,
        'count': count
    }

    resp = requests.get(BRAVE_API_URL, headers=headers, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    results = []
    for item in data.get('web', {}).get('results', [])[:count]:
        results.append({
            'title': item.get('title', ''),
            'url': item.get('url', ''),
            'snippet': item.get('description', '')
        })

    return {'query': query, 'count': len(results), 'results': results}


def main():
    if len(sys.argv) < 2:
        print('Usage: python3 brave_search.py "search query" [count]')
        sys.exit(1)

    query_text = sys.argv[1]
    count = int(sys.argv[2]) if len(sys.argv) > 2 else 5

    result = search(query_text, count)

    if 'error' in result:
        print(f'ERROR: {result["error"]}')
        sys.exit(1)

    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
