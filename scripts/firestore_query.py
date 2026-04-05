#!/usr/bin/env python3
"""Firestore query execution for dual retrieval path. P3 logged.

Executes structured queries against the locations collection using Firebase Admin SDK.
Handles G34 (single array-contains limit) via post-filtering.
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))
from utils.iao_logger import log_event

# Firebase Admin SDK - lazy init
_db = None


def _get_db():
    """Initialize Firebase Admin SDK and return Firestore client."""
    global _db
    if _db is not None:
        return _db

    import firebase_admin
    from firebase_admin import credentials, firestore

    if not firebase_admin._apps:
        sa_path = os.path.expanduser("~/.config/gcloud/kjtcom-sa.json")
        cred = credentials.Certificate(sa_path)
        firebase_admin.initialize_app(cred)

    _db = firestore.client()
    return _db


def execute_query(filters, intent, sort_field=None, sort_order="desc", limit=None,
                  return_docs=False):
    """Execute a Firestore query with filters and return formatted results.

    Args:
        filters: dict of field->value pairs from intent router
        intent: "count", "list", or "detail"
        sort_field: optional field path for orderBy (v9.43 rating-aware)
        sort_order: "desc" or "asc" (default "desc")
        limit: optional int to limit results
        return_docs: if True, return (formatted_text, raw_docs) tuple

    Returns:
        Formatted string response for Telegram, or (text, docs) if return_docs=True
    """
    start = time.time()
    try:
        db = _get_db()
        from google.cloud.firestore_v1.base_query import FieldFilter

        query = db.collection("locations")
        array_filters = []

        for field, value in filters.items():
            if isinstance(value, list):
                # G34: only one array-contains per query
                if not array_filters:
                    query = query.where(filter=FieldFilter(field, "array_contains", value[0]))
                array_filters.append((field, value))
            else:
                query = query.where(filter=FieldFilter(field, "==", value))

        # Always fetch without server-side orderBy (v9.44 - avoids composite index requirement)
        results = query.stream()
        docs = [doc.to_dict() for doc in results]
        latency = int((time.time() - start) * 1000)

        # G34 post-filter: additional array values beyond the first
        for field, value in array_filters:
            for extra_val in value[1:]:
                docs = [d for d in docs if extra_val in d.get(field, [])]
        # Post-filter for array fields that weren't the primary array-contains
        for field, value in array_filters[1:]:
            docs = [d for d in docs if value[0] in d.get(field, [])]

        # Python-side sort (v9.44 - always client-side, avoids composite index dependency)
        if sort_field:
            def _get_nested(doc, path):
                """Navigate nested dict by dot-separated path."""
                parts = path.split('.')
                val = doc
                for p in parts:
                    if isinstance(val, dict):
                        val = val.get(p)
                    else:
                        return None
                return val

            docs.sort(key=lambda d: _get_nested(d, sort_field) or 0,
                      reverse=(sort_order == "desc"))
            if limit and isinstance(limit, int):
                docs = docs[:limit]

        total = len(docs)

        log_event("api_call", "telegram-bot", "firestore", "query",
                  input_summary=f"filters={filters}, intent={intent}, sort={sort_field}, limit={limit}"[:200],
                  output_summary=f"{total} docs returned",
                  latency_ms=latency, status="success")

        if intent == "count":
            text = format_entity_count(docs, filters)
        elif intent == "list":
            text = format_entity_list(docs, limit=20)
        else:
            text = format_entity_detail(docs, limit=10)

        if return_docs:
            return text, docs
        return text

    except Exception as e:
        latency = int((time.time() - start) * 1000)
        log_event("api_call", "telegram-bot", "firestore", "query",
                  input_summary=f"filters={filters}"[:200],
                  status="error", error=str(e), latency_ms=latency)
        error_text = f"Firestore query error: {e}"
        if return_docs:
            return error_text, []
        return error_text


def format_entity_count(docs, filters=None):
    """Format count response."""
    total = len(docs)
    if total == 0:
        return "0 results found. Try broadening your search."
    return f"{total} results found."


def format_entity_list(docs, limit=20):
    """Format list of entities for Telegram."""
    total = len(docs)
    if total == 0:
        return "0 results found. Try broadening your search."

    lines = []
    for doc in docs[:limit]:
        name = _get_name(doc)
        city = _get_first(doc, 't_any_cities')
        state = _get_first(doc, 't_any_states')
        location = ", ".join(filter(None, [city, state]))
        line = f"- {name}"
        if location:
            line += f" ({location})"
        lines.append(line)

    result = "\n".join(lines)
    if total > limit:
        result += f"\n\n...and {total - limit} more ({total} total)"
    else:
        result += f"\n\n{total} results."
    return result


def format_entity_detail(docs, limit=10):
    """Format detailed entity info."""
    total = len(docs)
    if total == 0:
        return "0 results found. Try broadening your search."

    lines = []
    for doc in docs[:limit]:
        name = _get_name(doc)
        parts = [f"**{name}**"]
        for key in ['t_any_cities', 't_any_states', 't_any_countries',
                     't_any_cuisines', 't_any_categories']:
            val = doc.get(key, [])
            if val:
                label = key.replace('t_any_', '')
                parts.append(f"  {label}: {', '.join(val[:5])}")
        lines.append("\n".join(parts))

    result = "\n\n".join(lines)
    if total > limit:
        result += f"\n\n...and {total - limit} more ({total} total)"
    return result


def _get_name(doc):
    """Get display name from doc."""
    names = doc.get('t_any_names', [])
    if names:
        return names[0]
    return doc.get('t_name', 'Unknown')


def _get_first(doc, field):
    """Get first value from an array field."""
    val = doc.get(field, [])
    return val[0] if val else ''


if __name__ == '__main__':
    # Standalone test
    import json
    test_filters = {'t_log_type': 'tripledb'}
    test_intent = 'count'
    if len(sys.argv) > 1:
        test_filters = json.loads(sys.argv[1])
    if len(sys.argv) > 2:
        test_intent = sys.argv[2]
    print(execute_query(test_filters, test_intent))
