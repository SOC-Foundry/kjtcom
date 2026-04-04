"""Backfill TripleDB entities with Google Places enrichment.

Reads TripleDB entities missing google_places enrichment from production,
runs Google Places text search, and writes enrichment data back.
Also backfills coordinates and cities where missing.
"""

import argparse
import json
import os
import sys
import time
import urllib.parse
import urllib.request

from datetime import datetime, timezone
from google.cloud import firestore

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from scripts.utils.thompson_schema import compute_geohashes


PLACES_URL = "https://places.googleapis.com/v1/places:searchText"
NOMINATIM_URL = "https://nominatim.openstreetmap.org/reverse"


def search_place(query: str, api_key: str) -> dict | None:
    """Search for a place via Google Places API (New)."""
    body = json.dumps({"textQuery": query}).encode()
    req = urllib.request.Request(
        PLACES_URL,
        data=body,
        headers={
            "Content-Type": "application/json",
            "X-Goog-Api-Key": api_key,
            "X-Goog-FieldMask": "places.id,places.displayName,places.rating,"
                                "places.userRatingCount,places.websiteUri,"
                                "places.currentOpeningHours,places.nationalPhoneNumber,"
                                "places.location",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
            places = data.get("places", [])
            if places:
                return places[0]
    except Exception as e:
        print(f"  Places error for '{query}': {e}")
    return None


def reverse_geocode(lat: float, lon: float) -> str | None:
    """Reverse geocode coordinates to city name via Nominatim."""
    params = urllib.parse.urlencode({
        "lat": lat, "lon": lon, "format": "json", "zoom": 10
    })
    url = f"{NOMINATIM_URL}?{params}"
    req = urllib.request.Request(url, headers={"User-Agent": "kjtcom-backfill/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
            addr = data.get("address", {})
            return (addr.get("city") or addr.get("town") or
                    addr.get("village") or addr.get("municipality"))
    except Exception as e:
        print(f"  Nominatim error for ({lat}, {lon}): {e}")
    return None


def build_query(data: dict) -> str:
    """Build a Places text search query from entity data."""
    parts = []
    names = data.get("t_any_names", [])
    if names:
        parts.append(names[0])
    cities = data.get("t_any_cities", [])
    if cities:
        parts.append(cities[0])
    states = data.get("t_any_states", [])
    if states:
        parts.append(states[0])
    return ", ".join(parts)


def main():
    parser = argparse.ArgumentParser(description="Backfill TripleDB enrichment")
    parser.add_argument("--dry-run", action="store_true", help="Print changes without writing")
    parser.add_argument("--limit", type=int, default=0, help="Max entities to process (0=all)")
    args = parser.parse_args()

    api_key = os.environ.get("GOOGLE_PLACES_API_KEY")
    if not api_key:
        print("ERROR: GOOGLE_PLACES_API_KEY not set")
        sys.exit(1)

    db = firestore.Client(project="kjtcom-c78cd")
    collection = db.collection("locations")

    print("Querying for unenriched TripleDB entities...")
    docs = []
    for doc in collection.where(filter=firestore.FieldFilter("t_log_type", "==", "tripledb")).stream():
        d = doc.to_dict()
        if not d.get("t_enrichment", {}).get("google_places"):
            docs.append((doc.id, d))

    print(f"Found {len(docs)} unenriched TripleDB entities")

    if args.limit:
        docs = docs[:args.limit]
        print(f"Limited to {args.limit} entities")

    enriched = 0
    missed = 0
    coords_backfilled = 0
    cities_backfilled = 0
    errors = 0
    batch = db.batch()
    batch_count = 0

    for i, (doc_id, data) in enumerate(docs):
        query = build_query(data)
        if not query:
            print(f"  SKIP (no query): {doc_id}")
            missed += 1
            continue

        if args.dry_run:
            print(f"[DRY RUN {i+1}/{len(docs)}] {doc_id}: query='{query}'")
            if not data.get("t_any_coordinates"):
                print(f"  -> would backfill coordinates")
            if not data.get("t_any_cities"):
                print(f"  -> would backfill city")
            enriched += 1
            continue

        # Rate limit: 1 req/sec
        if i > 0:
            time.sleep(1)

        retries = 0
        place = None
        while retries < 3:
            place = search_place(query, api_key)
            if place is not None:
                break
            retries += 1
            if retries < 3:
                print(f"  Retry {retries}/3 for {doc_id}")
                time.sleep(2)

        updates = {}

        if place:
            enrichment_data = {
                "t_match": query,
                "place_id": place.get("id", ""),
                "rating": place.get("rating"),
                "current_name": place.get("displayName", {}).get("text", ""),
                "still_open": bool(place.get("currentOpeningHours")),
                "website": place.get("websiteUri", ""),
                "phone": place.get("nationalPhoneNumber", ""),
                "total_ratings": place.get("userRatingCount", 0),
                "enriched_at": datetime.now(timezone.utc).isoformat(),
            }
            updates["t_enrichment.google_places"] = enrichment_data

            # Add Google's current name to t_any_names
            current_name = place.get("displayName", {}).get("text", "")
            if current_name:
                existing_names = data.get("t_any_names", [])
                lower_name = current_name.lower()
                if lower_name not in existing_names:
                    existing_names.append(lower_name)
                    updates["t_any_names"] = existing_names

            # Add website to t_any_urls
            website = place.get("websiteUri", "")
            if website:
                existing_urls = data.get("t_any_urls", [])
                if website not in existing_urls:
                    existing_urls.append(website)
                    updates["t_any_urls"] = existing_urls

            # Backfill coordinates from Places if missing
            loc = place.get("location")
            if loc and not data.get("t_any_coordinates"):
                lat = loc.get("latitude")
                lon = loc.get("longitude")
                if lat and lon:
                    updates["t_any_coordinates"] = [{"lat": lat, "lon": lon}]
                    updates["t_any_geohashes"] = compute_geohashes(lat, lon)
                    coords_backfilled += 1
                    print(f"  Backfilled coords: ({lat:.4f}, {lon:.4f})")

            # Backfill city via reverse geocode if missing
            if not data.get("t_any_cities"):
                coord_source = None
                if data.get("t_any_coordinates"):
                    coord_source = data["t_any_coordinates"][0]
                elif loc:
                    coord_source = {"lat": loc.get("latitude"), "lon": loc.get("longitude")}

                if coord_source:
                    time.sleep(1)  # Rate limit for Nominatim
                    city = reverse_geocode(coord_source["lat"], coord_source["lon"])
                    if city:
                        updates["t_any_cities"] = [city.lower()]
                        cities_backfilled += 1
                        print(f"  Backfilled city: {city}")

            enriched += 1
            print(f"  [{i+1}/{len(docs)}] Enriched: {query} -> {place.get('displayName', {}).get('text', 'N/A')}")
        else:
            missed += 1
            print(f"  [{i+1}/{len(docs)}] MISS: {query}")

        if updates:
            batch.update(collection.document(doc_id), updates)
            batch_count += 1

            if batch_count >= 500:
                batch.commit()
                print(f"  Committed batch of {batch_count}")
                batch = db.batch()
                batch_count = 0

    if not args.dry_run and batch_count > 0:
        batch.commit()
        print(f"  Committed final batch of {batch_count}")

    print(f"\n=== SUMMARY ===")
    print(f"Enriched: {enriched}")
    print(f"Missed: {missed}")
    print(f"Errors: {errors}")
    print(f"Coordinates backfilled: {coords_backfilled}")
    print(f"Cities backfilled: {cities_backfilled}")
    if args.dry_run:
        print("(DRY RUN - no writes performed)")


if __name__ == "__main__":
    main()
