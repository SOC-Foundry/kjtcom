"""Phase 5: Geocode entities via Nominatim (OSM).

Input: pipeline/data/{pipeline}/normalized/*.jsonl
Output: pipeline/data/{pipeline}/geocoded/*.jsonl
Rate limit: 1 req/sec (Nominatim policy)
"""

import argparse
import glob
import json
import os
import sys
import time
import urllib.parse
import urllib.request
import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from scripts.utils.checkpoint import Checkpoint
from scripts.utils.thompson_schema import compute_geohashes


NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
USER_AGENT = "kjtcom-pipeline/0.5 (kylejeromethompson.com)"


def geocode(query: str) -> dict | None:
    """Geocode a location string via Nominatim. Returns dict or None."""
    params = urllib.parse.urlencode({
        "q": query,
        "format": "json",
        "limit": 1,
        "addressdetails": 1,
    })
    url = f"{NOMINATIM_URL}?{params}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            results = json.loads(resp.read().decode())
            if results:
                return results[0]
    except Exception as e:
        print(f"  Geocode error for '{query}': {e}")

    return None


def main():
    parser = argparse.ArgumentParser(description="Geocode entities via Nominatim")
    parser.add_argument("--pipeline", required=True, help="Pipeline ID")
    parser.add_argument("--limit", type=int, default=0, help="Max files to geocode (0=all)")
    args = parser.parse_args()

    base = os.path.dirname(os.path.dirname(__file__))
    normalized_dir = os.path.join(base, "data", args.pipeline, "normalized")
    output_dir = os.path.join(base, "data", args.pipeline, "geocoded")
    os.makedirs(output_dir, exist_ok=True)

    checkpoint = Checkpoint(args.pipeline, "geocode")

    normalized_files = sorted(glob.glob(os.path.join(normalized_dir, "*.jsonl")))
    count = 0

    for norm_path in normalized_files:
        file_id = os.path.splitext(os.path.basename(norm_path))[0]
        if checkpoint.is_done(file_id):
            continue

        if args.limit and count >= args.limit:
            break

        output_path = os.path.join(output_dir, f"{file_id}.jsonl")
        with open(norm_path) as fin, open(output_path, "w") as fout:
            for line in fin:
                entity = json.loads(line)

                # Build geocode query from source fields
                source = entity.get("source", {})

                def get_str(field):
                    val = source.get(field, "")
                    if isinstance(val, list):
                        return ", ".join(str(v) for v in val if v)
                    return str(val) if val else ""

                query_parts = [get_str("name")]
                city = get_str("city")
                if city:
                    query_parts.append(city)

                state = get_str("state") or get_str("state_province")
                if state:
                    query_parts.append(state)

                country = get_str("country")
                if country:
                    query_parts.append(country)

                query = ", ".join(p for p in query_parts if p)

                result = geocode(query)
                time.sleep(1)  # Rate limit: 1 req/sec

                if result:
                    lat = float(result["lat"])
                    lon = float(result["lon"])

                    entity.setdefault("t_any_coordinates", [])
                    entity["t_any_coordinates"].append({"lat": lat, "lon": lon})

                    entity["t_any_geohashes"] = compute_geohashes(lat, lon)

                    # County parsing enhancement (Schema v3)
                    address = result.get("address", {})
                    county = address.get("county")
                    if county:
                        entity.setdefault("t_any_counties", [])
                        if county.lower() not in [c.lower() for c in entity["t_any_counties"]]:
                            entity["t_any_counties"].append(county.lower())

                    entity.setdefault("t_enrichment", {})
                    entity["t_enrichment"]["nominatim"] = {
                        "t_match": query,
                        "latitude": lat,
                        "longitude": lon,
                        "display_name": result.get("display_name", ""),
                        "osm_type": result.get("osm_type", ""),
                        "osm_id": result.get("osm_id"),
                        "geocoded_at": datetime.datetime.now(
                            datetime.timezone.utc
                        ).isoformat(),
                    }
                    print(f"  Geocoded: {query} -> ({lat}, {lon})")
                else:
                    print(f"  MISS: {query}")

                fout.write(json.dumps(entity) + "\n")

        checkpoint.mark_done(file_id)
        count += 1

    print(f"Geocoded {count} new files. Total: {checkpoint.count()}")


if __name__ == "__main__":
    main()
