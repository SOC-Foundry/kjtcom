#!/usr/bin/env python3
"""Migrate TripleDB restaurants to kjtcom production Firestore.

Reads ~1,100 restaurant documents from TripleDB's Firestore project,
transforms to Thompson Indicator Fields schema v3, and writes to
kjtcom's production (default) locations collection.

Usage:
    python3 pipeline/scripts/migrate_tripledb.py \
        --project tripledb-e0f77 \
        --sa-path ~/.config/gcloud/tripledb-sa.json \
        --dry-run --limit 5
"""

import argparse
import hashlib
import os
import re
import sys
from datetime import datetime, timezone

import firebase_admin
from firebase_admin import credentials, firestore

# ---------------------------------------------------------------------------
# US state -> region lookup
# ---------------------------------------------------------------------------
US_STATE_TO_REGION = {
    "al": "southeast", "ak": "pacific", "az": "southwest", "ar": "southeast",
    "ca": "pacific", "co": "mountain", "ct": "northeast", "de": "mid-atlantic",
    "fl": "southeast", "ga": "southeast", "hi": "pacific", "id": "mountain",
    "il": "midwest", "in": "midwest", "ia": "midwest", "ks": "midwest",
    "ky": "southeast", "la": "southeast", "me": "northeast", "md": "mid-atlantic",
    "ma": "northeast", "mi": "midwest", "mn": "midwest", "ms": "southeast",
    "mo": "midwest", "mt": "mountain", "ne": "midwest", "nv": "mountain",
    "nh": "northeast", "nj": "mid-atlantic", "nm": "southwest", "ny": "mid-atlantic",
    "nc": "southeast", "nd": "midwest", "oh": "midwest", "ok": "southwest",
    "or": "pacific", "pa": "mid-atlantic", "ri": "northeast", "sc": "southeast",
    "sd": "midwest", "tn": "southeast", "tx": "southwest", "ut": "mountain",
    "vt": "northeast", "va": "mid-atlantic", "wa": "pacific", "wv": "mid-atlantic",
    "wi": "midwest", "wy": "mountain", "dc": "mid-atlantic",
}


def compute_geohashes(lat: float, lon: float) -> list[str]:
    """Compute geohash prefixes at precisions 4, 5, and 6."""
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


def generate_row_id(name: str, city: str) -> str:
    """Deterministic t_row_id from name + city + 'tripledb' (G33)."""
    hash_input = f"{(name or 'unknown').lower()}|{(city or 'unknown').lower()}|tripledb"
    digest = hashlib.sha256(hash_input.encode()).hexdigest()[:10]
    slug = re.sub(r"[^a-z0-9]+", "-", (name or "unknown").lower()).strip("-")
    return f"tripledb-{slug}-{digest}"


def split_cuisines(cuisine_type: str) -> list[str]:
    """Split cuisine_type on comma, slash, or ampersand and lowercase."""
    if not cuisine_type:
        return []
    parts = re.split(r"[,/&]+", cuisine_type)
    return sorted(set(p.strip().lower() for p in parts if p.strip()))


def transform_document(doc_id: str, data: dict) -> dict:
    """Transform a TripleDB restaurant document to Thompson Indicator Fields v3."""
    now = datetime.now(timezone.utc).isoformat()

    name = data.get("name", "")
    city = data.get("city", "")
    state = data.get("state", "")
    lat = data.get("latitude")
    lon = data.get("longitude")
    cuisine_type = data.get("cuisine_type", "")
    owner_chef = data.get("owner_chef")
    visits = data.get("visits", []) or []
    dishes = data.get("dishes", []) or []
    created_at = data.get("created_at")

    # --- Direct mappings ---
    t_any_names = [name] if name else []
    t_any_cities = [city.lower()] if city else []
    t_any_states = [state.lower()] if state else []
    t_any_coordinates = [{"lat": lat, "lon": lon}] if lat is not None and lon is not None else []
    t_any_cuisines = split_cuisines(cuisine_type)
    t_any_dishes = sorted(set(
        d.get("dish_name", "").lower()
        for d in dishes if d.get("dish_name")
    ))
    t_any_people = [owner_chef] if owner_chef else []
    t_any_video_ids = [v.get("video_id") for v in visits if v.get("video_id")]
    t_any_urls = [v.get("youtube_url") for v in visits if v.get("youtube_url")]

    # --- Hardcoded backfills ---
    t_any_actors = ["Guy Fieri"]
    if owner_chef:
        t_any_actors.append(owner_chef)

    t_any_roles = ["host", "chef"]
    if owner_chef:
        t_any_roles = ["host", "owner", "chef"]

    t_any_shows = ["Diners, Drive-Ins and Dives"]
    t_any_countries = ["us"]
    t_any_continents = ["North America"]
    t_any_eras = []

    # --- Derived fields ---
    # t_any_keywords: cuisine terms + dish ingredients + dish categories
    keywords = set()
    for c in t_any_cuisines:
        keywords.update(c.split())
    for d in dishes:
        if d.get("dish_category"):
            keywords.add(d["dish_category"].lower())
        for ing in d.get("ingredients", []) or []:
            if isinstance(ing, str) and len(ing) > 1:
                keywords.add(ing.lower())
    t_any_keywords = sorted(keywords) if keywords else []

    # t_any_categories: "restaurant" + cuisine_type terms
    categories = {"restaurant"}
    if t_any_cuisines:
        categories.update(t_any_cuisines)
    t_any_categories = sorted(categories)

    # t_any_regions: from state via lookup
    t_any_regions = []
    if state:
        region = US_STATE_TO_REGION.get(state.lower())
        if region:
            t_any_regions = [region]

    # t_any_geohashes: from lat/lon
    t_any_geohashes = []
    if lat is not None and lon is not None:
        t_any_geohashes = compute_geohashes(lat, lon)

    # t_event_time: created_at or earliest visit or now
    t_event_time = now
    if created_at:
        if hasattr(created_at, "isoformat"):
            t_event_time = created_at.isoformat()
        else:
            t_event_time = str(created_at)

    # --- Enrichment carry-forward ---
    google_places = {}

    # Design doc enrichment fields
    if data.get("google_rating") is not None:
        google_places["rating"] = data["google_rating"]
    if data.get("still_open") is not None:
        google_places["still_open"] = data["still_open"]
    if data.get("website_url"):
        google_places["website"] = data["website_url"]

    # G31 additional enrichment fields from actual TripleDB schema
    if data.get("business_status"):
        google_places["business_status"] = data["business_status"]
    if data.get("enrichment_match_score") is not None:
        google_places["match_score"] = data["enrichment_match_score"]
    if data.get("enrichment_source"):
        google_places["source"] = data["enrichment_source"]
    if data.get("formatted_address"):
        google_places["formatted_address"] = data["formatted_address"]
    if data.get("google_current_name"):
        google_places["current_name"] = data["google_current_name"]
    if data.get("google_maps_url"):
        google_places["maps_url"] = data["google_maps_url"]
    if data.get("google_place_id"):
        google_places["place_id"] = data["google_place_id"]
    if data.get("google_rating_count") is not None:
        google_places["rating_count"] = data["google_rating_count"]
    if data.get("photo_references"):
        google_places["photo_references"] = data["photo_references"]
    if data.get("name_changed") is not None:
        google_places["name_changed"] = data["name_changed"]
    if data.get("enriched_at"):
        enriched_at = data["enriched_at"]
        if hasattr(enriched_at, "isoformat"):
            google_places["enriched_at"] = enriched_at.isoformat()
        else:
            google_places["enriched_at"] = str(enriched_at)

    t_enrichment = {}
    if google_places:
        t_enrichment["google_places"] = google_places

    # Yelp enrichment
    if data.get("yelp_rating") is not None:
        t_enrichment["yelp"] = {"rating": data["yelp_rating"]}

    # --- Assemble Thompson document ---
    thompson = {
        "t_log_type": "tripledb",
        "t_row_id": generate_row_id(name, city),
        "t_event_time": t_event_time,
        "t_parse_time": now,
        "t_source_label": data.get("address") or name or "",
        "t_schema_version": 3,
        "t_any_names": t_any_names,
        "t_any_cities": t_any_cities,
        "t_any_states": t_any_states,
        "t_any_coordinates": t_any_coordinates,
        "t_any_cuisines": t_any_cuisines,
        "t_any_dishes": t_any_dishes,
        "t_any_people": t_any_people,
        "t_any_video_ids": t_any_video_ids,
        "t_any_urls": t_any_urls,
        "t_any_actors": t_any_actors,
        "t_any_roles": t_any_roles,
        "t_any_shows": t_any_shows,
        "t_any_countries": t_any_countries,
        "t_any_continents": t_any_continents,
        "t_any_eras": t_any_eras,
        "t_any_keywords": t_any_keywords,
        "t_any_categories": t_any_categories,
        "t_any_regions": t_any_regions,
        "t_any_geohashes": t_any_geohashes,
    }

    if t_enrichment:
        thompson["t_enrichment"] = t_enrichment

    # Remove empty arrays (except t_any_eras which is intentionally empty)
    for key in list(thompson.keys()):
        if key.startswith("t_any_") and key != "t_any_eras" and isinstance(thompson[key], list) and not thompson[key]:
            del thompson[key]

    return thompson


def print_document(doc_id: str, thompson: dict, index: int):
    """Pretty-print a transformed document for dry-run review."""
    print(f"\n{'='*60}")
    print(f"Document {index}: {doc_id}")
    print(f"{'='*60}")
    for key in sorted(thompson.keys()):
        val = thompson[key]
        if isinstance(val, list) and len(val) > 5:
            print(f"  {key}: [{len(val)} items] {val[:3]}...")
        elif isinstance(val, dict):
            print(f"  {key}:")
            for k2, v2 in val.items():
                if isinstance(v2, dict):
                    print(f"    {k2}:")
                    for k3, v3 in v2.items():
                        print(f"      {k3}: {v3}")
                else:
                    print(f"    {k2}: {v2}")
        else:
            print(f"  {key}: {val}")


def main():
    parser = argparse.ArgumentParser(description="Migrate TripleDB restaurants to kjtcom production Firestore")
    parser.add_argument("--project", default="tripledb-e0f77", help="TripleDB project ID")
    parser.add_argument("--sa-path", default=os.path.expanduser("~/.config/gcloud/tripledb-sa.json"),
                        help="Path to TripleDB service account JSON")
    parser.add_argument("--dry-run", action="store_true", help="Print mapping without writing")
    parser.add_argument("--limit", type=int, default=0, help="Process only N documents (0 = all)")
    args = parser.parse_args()

    # --- Initialize source client (TripleDB) ---
    print(f"[1/4] Connecting to TripleDB project: {args.project}")
    tripledb_cred = credentials.Certificate(args.sa_path)
    tripledb_app = firebase_admin.initialize_app(tripledb_cred, {"projectId": args.project}, name="tripledb")
    source_db = firestore.client(app=tripledb_app)

    # --- Initialize destination client (kjtcom production) ---
    kjtcom_sa = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "")
    if not kjtcom_sa:
        print("ERROR: GOOGLE_APPLICATION_CREDENTIALS not set for kjtcom")
        sys.exit(1)
    print(f"[2/4] Connecting to kjtcom production (default) database")
    kjtcom_cred = credentials.Certificate(kjtcom_sa)
    kjtcom_app = firebase_admin.initialize_app(kjtcom_cred, {"projectId": "kjtcom-c78cd"}, name="kjtcom")
    dest_db = firestore.client(app=kjtcom_app)

    # --- Read source documents ---
    print(f"[3/4] Reading from TripleDB 'restaurants' collection...")
    query = source_db.collection("restaurants")
    if args.limit:
        query = query.limit(args.limit)

    docs = list(query.stream())
    print(f"  Read {len(docs)} documents")

    if not docs:
        print("No documents found. Exiting.")
        return

    # --- Transform and write ---
    print(f"[4/4] {'DRY RUN - ' if args.dry_run else ''}Transforming and writing...")

    # Field population counters
    field_counts = {
        "t_any_names": 0, "t_any_cities": 0, "t_any_states": 0,
        "t_any_coordinates": 0, "t_any_cuisines": 0, "t_any_dishes": 0,
        "t_any_people": 0, "t_any_video_ids": 0, "t_any_urls": 0,
        "t_any_actors": 0, "t_any_shows": 0, "t_any_keywords": 0,
        "t_any_categories": 0, "t_any_regions": 0, "t_any_geohashes": 0,
        "t_enrichment": 0,
    }

    transformed = []
    for i, doc in enumerate(docs):
        data = doc.to_dict()
        thompson = transform_document(doc.id, data)
        transformed.append((thompson["t_row_id"], thompson))

        # Count populated fields
        for field in field_counts:
            if field == "t_enrichment":
                if thompson.get("t_enrichment"):
                    field_counts[field] += 1
            elif thompson.get(field):
                field_counts[field] += 1

        if args.dry_run:
            print_document(doc.id, thompson, i + 1)

    total = len(transformed)

    if args.dry_run:
        print(f"\n{'='*60}")
        print(f"DRY RUN COMPLETE - {total} documents transformed (not written)")
    else:
        # Batch write to production
        batch_size = 500
        written = 0
        for start in range(0, total, batch_size):
            batch = dest_db.batch()
            chunk = transformed[start:start + batch_size]
            for row_id, thompson in chunk:
                doc_ref = dest_db.collection("locations").document(row_id)
                batch.set(doc_ref, thompson)
            batch.commit()
            written += len(chunk)
            print(f"  Batch committed: {written}/{total}")

        print(f"\nMIGRATION COMPLETE - {written} documents written to production")

    # --- Summary ---
    print(f"\n{'='*60}")
    print(f"FIELD POPULATION SUMMARY ({total} documents)")
    print(f"{'='*60}")
    for field, count in sorted(field_counts.items()):
        pct = count * 100 // total if total else 0
        print(f"  {field:30s} {count:5d}/{total} ({pct}%)")


if __name__ == "__main__":
    main()
