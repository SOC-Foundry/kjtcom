"""Thompson Schema normalization utility.

Provides core functions for normalizing raw extracted entities into the
Thompson Schema (t_any_*) format for cross-dataset querying.
"""

import hashlib
import re
from datetime import datetime, timezone


# Stop words excluded from keyword tokenization
STOP_WORDS = {
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "is", "it", "as", "was", "are", "be",
    "this", "that", "which", "who", "whom", "has", "had", "have", "been",
    "its", "his", "her", "their", "our", "my", "your", "not", "no", "do",
    "does", "did", "will", "would", "could", "should", "may", "might",
    "shall", "can", "over", "into", "about", "up", "out", "than", "then",
    "so", "if", "when", "where", "how", "all", "each", "every", "both",
    "few", "more", "most", "other", "some", "such", "only", "own", "same",
    "too", "very", "just", "because", "through", "during", "before", "after",
    "above", "below", "between", "under", "again", "further", "once",
}


def tokenize_for_search(text: str) -> list[str]:
    """Tokenize text into lowercase search terms, removing stop words and short tokens."""
    if not text:
        return []
    # Remove punctuation, split on whitespace
    tokens = re.findall(r"[a-z0-9]+", text.lower())
    # Filter stop words and very short tokens
    return [t for t in tokens if t not in STOP_WORDS and len(t) > 1]


def generate_row_id(pipeline_id: str, entity: dict) -> str:
    """Generate a deterministic row ID from pipeline ID and entity name."""
    name = entity.get("name", "unknown")
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    # Add hash suffix for uniqueness
    hash_input = f"{pipeline_id}-{name.lower()}"
    short_hash = hashlib.md5(hash_input.encode()).hexdigest()[:6]
    return f"{pipeline_id}-{slug}-{short_hash}"


def lowercase_array(arr: list) -> list[str]:
    """Lowercase all string elements in an array."""
    return [v.lower() if isinstance(v, str) else v for v in arr]


def compute_geohashes(lat: float, lon: float) -> list[str]:
    """Compute geohash prefixes at precisions 4, 5, and 6 for proximity queries."""
    # Base32 encoding for geohash
    base32 = "0123456789bcdefghjkmnpqrstuvwxyz"
    min_lat, max_lat = -90.0, 90.0
    min_lon, max_lon = -180.0, 180.0
    geohash = []
    is_lon = True
    bit = 0
    ch_idx = 0

    while len(geohash) < 6:
        if is_lon:
            mid = (min_lon + max_lon) / 2
            if lon >= mid:
                ch_idx = ch_idx * 2 + 1
                min_lon = mid
            else:
                ch_idx = ch_idx * 2
                max_lon = mid
        else:
            mid = (min_lat + max_lat) / 2
            if lat >= mid:
                ch_idx = ch_idx * 2 + 1
                min_lat = mid
            else:
                ch_idx = ch_idx * 2
                max_lat = mid

        is_lon = not is_lon
        bit += 1

        if bit == 5:
            geohash.append(base32[ch_idx])
            bit = 0
            ch_idx = 0

    full = "".join(geohash)
    return [full[:4], full[:5], full[:6]]


def flatten_nested_lists(val):
    """Recursively flatten nested lists to ensure Firestore compatibility (no arrays of arrays)."""
    if not isinstance(val, list):
        return val
    
    needs_flattening = any(isinstance(i, list) for i in val)
    if not needs_flattening:
        return val
        
    flat = []
    for item in val:
        if isinstance(item, list):
            # Recursively flatten the sub-list
            sub_flat = flatten_nested_lists(item)
            if isinstance(sub_flat, list):
                flat.extend(sub_flat)
            else:
                flat.append(sub_flat)
        else:
            flat.append(item)
    return flat


def make_firestore_safe(data):
    """Recursively process a dictionary or list to ensure it's Firestore-safe."""
    if isinstance(data, dict):
        return {k: make_firestore_safe(v) for k, v in data.items()}
    elif isinstance(data, list):
        # First, flatten if it's a nested list
        flattened = flatten_nested_lists(data)
        # Then, recursively process items (for cases like list of dicts)
        return [make_firestore_safe(i) for i in flattened]
    else:
        return data


def normalize_entity(raw: dict, schema: dict) -> dict:
    """Normalize a raw extracted entity into Thompson Schema format.

    Args:
        raw: Raw extracted entity dict from Gemini extraction.
        schema: Pipeline schema.json dict with indicator mappings.

    Returns:
        Normalized dict with all t_* and t_any_* fields populated.
    """
    normalized = {}

    # 1. Standard fields
    normalized["t_log_type"] = schema["pipeline_id"]
    normalized["t_row_id"] = generate_row_id(schema["pipeline_id"], raw)
    normalized["t_event_time"] = raw.get("event_time", datetime.now(timezone.utc).isoformat())
    normalized["t_parse_time"] = datetime.now(timezone.utc).isoformat()
    normalized["t_source_label"] = schema["display_name"]
    normalized["t_schema_version"] = schema["t_schema_version"]

    # 2. Indicator fields - driven by schema.json mappings
    for source_field, mapping in schema["indicators"].items():
        target_field = mapping["extract_into"]
        method = mapping.get("method", "direct")
        value = raw.get(source_field)

        if target_field not in normalized:
            normalized[target_field] = []

        # Apply default if value is missing and default is specified
        if value is None and "default" in mapping:
            value = mapping["default"]

        if value is None:
            continue

        if method == "direct":
            if isinstance(value, list):
                # Flatten first, then stringify
                flat_value = flatten_nested_lists(value)
                normalized[target_field].extend([str(v).lower() for v in flat_value])
            else:
                normalized[target_field].append(str(value).lower())
        elif method == "tokenize":
            # Flatten first, then tokenize
            if isinstance(value, list):
                value = " ".join([str(v) for v in flatten_nested_lists(value)])
            tokens = tokenize_for_search(str(value))
            normalized[target_field].extend(tokens)

    # 3. Deduplicate all t_any arrays
    for key in list(normalized.keys()):
        if key.startswith("t_any_") and isinstance(normalized[key], list):
            normalized[key] = sorted(set(normalized[key]))
            # Remove empty arrays
            if not normalized[key]:
                del normalized[key]

    # 4. Source fields - preserve original but ensure Firestore-safe
    normalized["source"] = make_firestore_safe(raw)

    return normalized
