"""Backfill pre-v3 entities to schema v3.

Reads all entities from production where t_schema_version < 3,
applies v3 backfill rules per t_log_type, and writes back.
"""

import argparse
import sys
import os

from google.cloud import firestore


COUNTRY_TO_CONTINENT = {
    "albania": "Europe", "andorra": "Europe", "armenia": "Europe",
    "austria": "Europe", "azerbaijan": "Europe", "belarus": "Europe",
    "belgium": "Europe", "bosnia and herzegovina": "Europe", "bosnia": "Europe",
    "bulgaria": "Europe", "croatia": "Europe", "cyprus": "Europe",
    "czech republic": "Europe", "czechia": "Europe", "denmark": "Europe",
    "england": "Europe", "estonia": "Europe", "finland": "Europe",
    "france": "Europe", "georgia": "Europe", "germany": "Europe",
    "greece": "Europe", "hungary": "Europe", "iceland": "Europe",
    "ireland": "Europe", "italy": "Europe", "kosovo": "Europe",
    "latvia": "Europe", "liechtenstein": "Europe", "lithuania": "Europe",
    "luxembourg": "Europe", "malta": "Europe", "moldova": "Europe",
    "monaco": "Europe", "montenegro": "Europe", "netherlands": "Europe",
    "north macedonia": "Europe", "norway": "Europe", "poland": "Europe",
    "portugal": "Europe", "romania": "Europe", "russia": "Europe",
    "san marino": "Europe", "scotland": "Europe", "serbia": "Europe",
    "slovakia": "Europe", "slovenia": "Europe", "spain": "Europe",
    "sweden": "Europe", "switzerland": "Europe", "turkey": "Europe",
    "uk": "Europe", "ukraine": "Europe", "united kingdom": "Europe",
    "vatican": "Europe", "wales": "Europe",
    # Africa
    "egypt": "Africa", "ethiopia": "Africa", "ghana": "Africa",
    "kenya": "Africa", "morocco": "Africa", "nigeria": "Africa",
    "south africa": "Africa", "tanzania": "Africa", "tunisia": "Africa",
    # Asia
    "cambodia": "Asia", "china": "Asia", "india": "Asia",
    "indonesia": "Asia", "iran": "Asia", "iraq": "Asia",
    "israel": "Asia", "japan": "Asia", "jordan": "Asia",
    "south korea": "Asia", "lebanon": "Asia", "malaysia": "Asia",
    "myanmar": "Asia", "nepal": "Asia", "pakistan": "Asia",
    "philippines": "Asia", "singapore": "Asia", "sri lanka": "Asia",
    "syria": "Asia", "taiwan": "Asia", "thailand": "Asia",
    "vietnam": "Asia",
    # North America
    "canada": "North America", "mexico": "North America",
    "us": "North America", "usa": "North America",
    "united states": "North America",
    # South America
    "argentina": "South America", "brazil": "South America",
    "chile": "South America", "colombia": "South America",
    "peru": "South America",
    # Oceania
    "australia": "Oceania", "new zealand": "Oceania",
}


def derive_continents(countries: list[str]) -> list[str]:
    """Derive continent list from country list using lookup table."""
    continents = set()
    for country in countries:
        c = country.lower().strip()
        continent = COUNTRY_TO_CONTINENT.get(c)
        if continent:
            continents.add(continent.lower())
    return sorted(continents)


def backfill_calgold(data: dict) -> dict:
    """Apply CalGold v3 backfill rules."""
    updates = {}
    if "t_any_actors" not in data or not data["t_any_actors"]:
        updates["t_any_actors"] = ["huell howser"]
    if "t_any_roles" not in data or not data["t_any_roles"]:
        updates["t_any_roles"] = ["host"]
    if "t_any_shows" not in data or not data["t_any_shows"]:
        updates["t_any_shows"] = ["california's gold"]
    if "t_any_cuisines" not in data or not data["t_any_cuisines"]:
        updates["t_any_cuisines"] = []
    if "t_any_dishes" not in data or not data["t_any_dishes"]:
        updates["t_any_dishes"] = []
    if "t_any_eras" not in data or not data["t_any_eras"]:
        updates["t_any_eras"] = []
    if "t_any_continents" not in data or not data["t_any_continents"]:
        updates["t_any_continents"] = ["north america"]
    updates["t_schema_version"] = 3
    return updates


def backfill_ricksteves(data: dict) -> dict:
    """Apply RickSteves v3 backfill rules."""
    updates = {}
    if "t_any_actors" not in data or not data["t_any_actors"]:
        updates["t_any_actors"] = ["rick steves"]
    if "t_any_roles" not in data or not data["t_any_roles"]:
        updates["t_any_roles"] = ["host"]
    if "t_any_shows" not in data or not data["t_any_shows"]:
        updates["t_any_shows"] = ["rick steves' europe"]
    if "t_any_cuisines" not in data or not data["t_any_cuisines"]:
        updates["t_any_cuisines"] = []
    if "t_any_dishes" not in data or not data["t_any_dishes"]:
        updates["t_any_dishes"] = []
    if "t_any_eras" not in data or not data["t_any_eras"]:
        updates["t_any_eras"] = []
    if "t_any_continents" not in data or not data["t_any_continents"]:
        countries = data.get("t_any_countries", [])
        updates["t_any_continents"] = derive_continents(countries)
    updates["t_schema_version"] = 3
    return updates


def main():
    parser = argparse.ArgumentParser(description="Backfill entities to schema v3")
    parser.add_argument("--dry-run", action="store_true", help="Print changes without writing")
    parser.add_argument("--limit", type=int, default=0, help="Max entities to process (0=all)")
    args = parser.parse_args()

    db = firestore.Client(project="kjtcom-c78cd")
    collection = db.collection("locations")

    print("Querying for non-v3 entities...")
    docs = list(collection.where(filter=firestore.FieldFilter("t_schema_version", "<", 3)).stream())
    print(f"Found {len(docs)} non-v3 entities")

    if args.limit:
        docs = docs[:args.limit]
        print(f"Limited to {args.limit} entities")

    calgold_count = 0
    ricksteves_count = 0
    skipped = 0
    batch = db.batch()
    batch_count = 0

    for i, doc in enumerate(docs):
        data = doc.to_dict()
        log_type = data.get("t_log_type", "")

        if log_type == "calgold":
            updates = backfill_calgold(data)
            calgold_count += 1
        elif log_type == "ricksteves":
            updates = backfill_ricksteves(data)
            ricksteves_count += 1
        else:
            print(f"  SKIP: {doc.id} (unknown type: {log_type})")
            skipped += 1
            continue

        if args.dry_run:
            print(f"\n[DRY RUN] {doc.id} ({log_type}):")
            for k, v in sorted(updates.items()):
                print(f"  {k}: {v}")
        else:
            batch.update(collection.document(doc.id), updates)
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
    print(f"CalGold updated: {calgold_count}")
    print(f"RickSteves updated: {ricksteves_count}")
    print(f"Skipped: {skipped}")
    print(f"Total processed: {calgold_count + ricksteves_count}")
    if args.dry_run:
        print("(DRY RUN - no writes performed)")


if __name__ == "__main__":
    main()
