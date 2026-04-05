#!/usr/bin/env python3
"""Gemini Flash intent router for dual retrieval path. P3 logged.

Routes /ask queries to either Firestore (entity data) or ChromaDB (dev history)
using Gemini Flash via litellm for intent classification.
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))
from utils.iao_logger import log_event

# Load schema reference at import time
_SCHEMA_REF = None
_SCHEMA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'schema_reference.json')


def _load_schema():
    global _SCHEMA_REF
    if _SCHEMA_REF is None:
        with open(_SCHEMA_PATH) as f:
            _SCHEMA_REF = json.load(f)
    return _SCHEMA_REF


def build_routing_prompt(question):
    """Build the routing prompt with schema context."""
    schema = _load_schema()
    schema_str = json.dumps(schema, separators=(',', ':'))

    return f"""You are a query router for a location intelligence database with {schema['entity_count']} entities across 3 pipelines.

Given a user question, return ONLY a JSON object with one of these structures:

For entity/data questions (restaurants, locations, shows, people in the database):
{{"route": "firestore", "filters": {{"field": "value"}}, "intent": "count|list|detail"}}

For development/project history questions (kjtcom iterations, gotchas, builds, agents):
{{"route": "chromadb", "query": "search terms"}}

For external/internet questions (companies, news, general knowledge, things NOT in the database):
{{"route": "web", "query": "search terms"}}

SCHEMA REFERENCE:
{schema_str}

Rules:
- Array fields (t_any_*) take list values: ["italian"]
- Scalar fields (t_log_type, t_name, t_city) take string values
- "DDD" or "Diners Drive-Ins" or "Guy Fieri" or "Triple D" -> t_log_type: "tripledb" (do NOT also add a people/actors filter)
- "Huell Howser" or "California's Gold" -> t_log_type: "calgold" (do NOT also add a people/actors filter)
- "Rick Steves" -> t_log_type: "ricksteves" (do NOT also add a people/actors filter)
- Pipeline name aliases are ONLY used for t_log_type mapping, never for person filters
- State names -> t_any_states as 2-letter lowercase codes: ["tx"] for Texas, ["ca"] for California, ["ny"] for New York
- Country names -> t_any_countries as ISO alpha-2 lowercase: ["us"]
- County names -> t_any_counties with full name: ["orange county"] (mostly calgold pipeline)
- "how many" -> intent: "count"
- "list" or "show" or "where" -> intent: "list"
- specific place name -> intent: "detail"
- If the question is about external companies, products, news, or general knowledge NOT in the database, use "web" route
- If unsure whether entity or dev question, default to firestore
- Return ONLY valid JSON, no markdown, no explanation

USER QUESTION: {question}"""


def route_question(question):
    """Route a question via Gemini Flash. Returns parsed routing dict.

    Falls back to ChromaDB on any error.
    """
    from litellm import completion

    prompt = build_routing_prompt(question)
    start = time.time()

    try:
        response = completion(
            model="gemini/gemini-2.5-flash",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=1024,
            thinking={"type": "disabled"},
        )
        content = response.choices[0].message.content.strip()
        latency = int((time.time() - start) * 1000)

        # Token usage from response
        usage = response.usage
        tokens = {
            "prompt": getattr(usage, 'prompt_tokens', 0),
            "eval": getattr(usage, 'completion_tokens', 0),
            "total": getattr(usage, 'total_tokens', 0),
        }

        log_event("llm_call", "telegram-bot", "gemini/gemini-2.5-flash", "route",
                  input_summary=f"route: {question}"[:200],
                  output_summary=content[:200],
                  tokens=tokens, latency_ms=latency, status="success")

        # Parse JSON - strip markdown fences if present
        cleaned = content
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[-1]
        if cleaned.endswith("```"):
            cleaned = cleaned.rsplit("```", 1)[0]
        cleaned = cleaned.strip()

        parsed = json.loads(cleaned)

        # Validate structure
        if "route" not in parsed:
            raise ValueError("Missing 'route' key")
        if parsed["route"] not in ("firestore", "chromadb", "web"):
            raise ValueError(f"Unknown route: {parsed['route']}")
        if parsed["route"] == "firestore" and "filters" not in parsed:
            parsed["filters"] = {}
        if parsed["route"] == "firestore" and "intent" not in parsed:
            parsed["intent"] = "list"
        if parsed["route"] == "web" and "query" not in parsed:
            parsed["query"] = question

        return parsed

    except Exception as e:
        latency = int((time.time() - start) * 1000)
        log_event("llm_call", "telegram-bot", "gemini/gemini-2.5-flash", "route",
                  input_summary=f"route: {question}"[:200],
                  status="error", error=str(e), latency_ms=latency)
        # Fallback to ChromaDB
        return {"route": "chromadb", "query": question}


if __name__ == '__main__':
    q = sys.argv[1] if len(sys.argv) > 1 else "how many Italian restaurants in Orange County in DDD"
    result = route_question(q)
    print(json.dumps(result, indent=2))
