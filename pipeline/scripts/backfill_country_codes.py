"""Backfill t_any_country_codes with ISO 3166-1 alpha-2 codes.

Reads t_any_countries from all entities, maps to lowercase alpha-2 codes,
and writes t_any_country_codes array. Uses pycountry as primary lookup
with hardcoded fallback for edge cases.
"""

import argparse
import sys
import os

import pycountry
from google.cloud import firestore

# Hardcoded fallback for names pycountry doesn't resolve
FALLBACK_CODES = {
    "us": "us",
    "usa": "us",
    "uk": "gb",
    "united kingdom": "gb",
    "england": "gb",
    "scotland": "gb",
    "wales": "gb",
    "northern ireland": "gb",
    "czech republic": "cz",
    "vatican city": "va",
    "vatican": "va",
    "palestine": "ps",
    "iran": "ir",
    "south korea": "kr",
    "north korea": "kp",
    "russia": "ru",
    "syria": "sy",
    "tanzania": "tz",
    "venezuela": "ve",
    "vietnam": "vn",
    "bolivia": "bo",
    "taiwan": "tw",
    "ivory coast": "ci",
    "congo": "cd",
    "laos": "la",
    "brunei": "bn",
    "macau": "mo",
    "kosovo": "xk",
    "turkey": "tr",
}


def resolve_code(country_name: str) -> str | None:
    """Map a country name to lowercase ISO 3166-1 alpha-2 code."""
    lowered = country_name.strip().lower()
    if not lowered:
        return None

    # Check hardcoded fallback first (handles edge cases)
    if lowered in FALLBACK_CODES:
        return FALLBACK_CODES[lowered]

    # Try pycountry name lookup
    result = pycountry.countries.get(name=country_name.strip().title())
    if result:
        return result.alpha_2.lower()

    # Try fuzzy search
    try:
        results = pycountry.countries.search_fuzzy(country_name.strip())
        if results:
            return results[0].alpha_2.lower()
    except LookupError:
        pass

    return None


def main():
    parser = argparse.ArgumentParser(
        description="Backfill t_any_country_codes on all entities"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Print changes without writing"
    )
    parser.add_argument(
        "--limit", type=int, default=0, help="Limit number of entities to process (0=all)"
    )
    args = parser.parse_args()

    db = firestore.Client()
    collection = db.collection("locations")

    print(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE WRITE'}")
    if args.limit:
        print(f"Limit: {args.limit} entities")

    # Read all entities
    query = collection.select(["t_any_countries"])
    if args.limit:
        query = query.limit(args.limit)

    docs = list(query.stream())
    print(f"Fetched {len(docs)} entities")

    updated = 0
    skipped = 0
    unmapped = set()
    batch_size = 500
    batch = db.batch()
    batch_count = 0

    for doc in docs:
        data = doc.to_dict() or {}
        countries = data.get("t_any_countries", [])
        if not isinstance(countries, list):
            countries = [countries] if countries else []

        codes = []
        for country in countries:
            code = resolve_code(str(country))
            if code:
                if code not in codes:
                    codes.append(code)
            else:
                unmapped.add(str(country))

        if not codes:
            skipped += 1
            continue

        if args.dry_run:
            print(f"  {doc.id}: {countries} -> {codes}")
            updated += 1
        else:
            batch.update(doc.reference, {"t_any_country_codes": codes})
            batch_count += 1
            updated += 1

            if batch_count >= batch_size:
                batch.commit()
                print(f"  Committed batch ({updated} entities so far)")
                batch = db.batch()
                batch_count = 0

    # Commit remaining
    if not args.dry_run and batch_count > 0:
        batch.commit()
        print(f"  Committed final batch")

    print(f"\nResults:")
    print(f"  Updated: {updated}")
    print(f"  Skipped (no countries): {skipped}")
    print(f"  Total processed: {updated + skipped}")

    if unmapped:
        print(f"\n  Unmapped country names ({len(unmapped)}):")
        for name in sorted(unmapped):
            print(f"    - {name}")


if __name__ == "__main__":
    main()
