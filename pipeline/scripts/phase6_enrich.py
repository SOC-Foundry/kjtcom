"""Phase 6: Enrich entities via Google Places API (New).

Input: pipeline/data/{pipeline}/geocoded/*.jsonl
Output: pipeline/data/{pipeline}/enriched/*.jsonl
Populates: t_enrichment.google_places and t_enrichment.nominatim
"""

import argparse
import glob
import json
import os
import sys
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from scripts.utils.checkpoint import Checkpoint


PLACES_URL = "https://places.googleapis.com/v1/places:searchText"


def search_place(query: str, api_key: str) -> dict | None:
    """Search for a place via Google Places API (New). Returns dict or None."""
    body = json.dumps({"textQuery": query}).encode()
    req = urllib.request.Request(
        PLACES_URL,
        data=body,
        headers={
            "Content-Type": "application/json",
            "X-Goog-Api-Key": api_key,
            "X-Goog-FieldMask": "places.id,places.displayName,places.rating,"
                                "places.userRatingCount,places.websiteUri,"
                                "places.currentOpeningHours,places.nationalPhoneNumber",
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


def main():
    parser = argparse.ArgumentParser(description="Enrich entities via Google Places API")
    parser.add_argument("--pipeline", required=True, help="Pipeline ID")
    parser.add_argument("--limit", type=int, default=0, help="Max files to enrich (0=all)")
    args = parser.parse_args()

    api_key = os.environ.get("GOOGLE_PLACES_API_KEY")
    if not api_key:
        print("ERROR: GOOGLE_PLACES_API_KEY not set")
        sys.exit(1)

    base = os.path.dirname(os.path.dirname(__file__))
    geocoded_dir = os.path.join(base, "data", args.pipeline, "geocoded")
    output_dir = os.path.join(base, "data", args.pipeline, "enriched")
    os.makedirs(output_dir, exist_ok=True)

    checkpoint = Checkpoint(args.pipeline, "enrich")

    geocoded_files = sorted(glob.glob(os.path.join(geocoded_dir, "*.jsonl")))
    count = 0

    for geo_path in geocoded_files:
        file_id = os.path.splitext(os.path.basename(geo_path))[0]
        if checkpoint.is_done(file_id):
            continue

        if args.limit and count >= args.limit:
            break

        output_path = os.path.join(output_dir, f"{file_id}.jsonl")
        with open(geo_path) as fin, open(output_path, "w") as fout:
            for line in fin:
                entity = json.loads(line)
                source = entity.get("source", {})
                query = source.get("name", "")
                if source.get("city"):
                    query += f", {source['city']}"
                if source.get("state"):
                    query += f", {source['state']}"

                place = search_place(query, api_key)

                if place:
                    from datetime import datetime, timezone
                    entity.setdefault("t_enrichment", {})
                    entity["t_enrichment"]["google_places"] = {
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

                    # Add Google's current name to t_any_names
                    current_name = place.get("displayName", {}).get("text", "")
                    if current_name:
                        entity.setdefault("t_any_names", [])
                        lower_name = current_name.lower()
                        if lower_name not in entity["t_any_names"]:
                            entity["t_any_names"].append(lower_name)

                    # Add website to t_any_urls
                    website = place.get("websiteUri", "")
                    if website:
                        entity.setdefault("t_any_urls", [])
                        if website not in entity["t_any_urls"]:
                            entity["t_any_urls"].append(website)

                    print(f"  Enriched: {query} -> {place.get('displayName', {}).get('text', 'N/A')}")
                else:
                    print(f"  MISS: {query}")

                fout.write(json.dumps(entity) + "\n")

        checkpoint.mark_done(file_id)
        count += 1

    print(f"Enriched {count} new files. Total: {checkpoint.count()}")


if __name__ == "__main__":
    main()
