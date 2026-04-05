#!/usr/bin/env python3
"""Enrich TripleDB entities with t_any_counties via reverse geocoding.

W1 (v9.42): 1,100 TripleDB entities have coordinates but no county data.
Uses Nominatim reverse geocoding (1 req/sec rate limit) as primary method.
Falls back to formatted_address parsing from Google Places enrichment data.

Usage:
  python3 -u scripts/enrich_counties.py --dry-run   # Preview changes
  python3 -u scripts/enrich_counties.py --write      # Write to Firestore
"""
import argparse
import json
import os
import sys
import time

import requests

sys.path.insert(0, os.path.dirname(__file__))
from utils.iao_logger import log_event

# Firebase Admin SDK - lazy init
_db = None


def _get_db():
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


def fetch_tripledb_entities():
    """Fetch all TripleDB entities from Firestore."""
    db = _get_db()
    from google.cloud.firestore_v1.base_query import FieldFilter
    query = db.collection("locations").where(
        filter=FieldFilter("t_log_type", "==", "tripledb")
    )
    docs = []
    for doc in query.stream():
        data = doc.to_dict()
        data['__doc_id__'] = doc.id
        docs.append(data)
    return docs


def reverse_geocode_nominatim(lat, lon):
    """Reverse geocode coordinates to county via Nominatim. Returns county name or None."""
    url = "https://nominatim.openstreetmap.org/reverse"
    params = {
        "lat": lat,
        "lon": lon,
        "format": "json",
        "addressdetails": 1,
        "zoom": 12,
    }
    headers = {"User-Agent": "kjtcom-iao/9.42 (county-enrichment)"}
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        address = data.get("address", {})
        county = address.get("county", "")
        if county:
            # Normalize: lowercase, ensure "county" suffix
            county = county.lower().strip()
            if not county.endswith("county") and not county.endswith("parish") and not county.endswith("borough"):
                county = county + " county"
            return county
    except Exception as e:
        log_event("api_call", "enrich-counties", "nominatim", "reverse_geocode",
                  input_summary=f"lat={lat}, lon={lon}",
                  status="error", error=str(e))
    return None


def extract_county_from_address(enrichment):
    """Try to extract county from Google Places formatted_address. Fallback method."""
    if not enrichment:
        return None
    gp = enrichment.get("google_places", {})
    addr = gp.get("formatted_address", "")
    # Google Places formatted_address rarely includes county directly
    # This is a weak fallback - mostly returns None
    return None


def enrich_entities(entities, dry_run=True):
    """Enrich entities with county data. Returns list of (doc_id, counties) tuples."""
    results = []
    already_have = 0
    no_coords = 0
    enriched = 0
    failed = 0
    non_us = 0
    total = len(entities)

    for i, entity in enumerate(entities):
        doc_id = entity.get('__doc_id__', '?')
        name = (entity.get('t_any_names', ['?']) or ['?'])[0]

        # Skip if already has counties
        existing = entity.get('t_any_counties', [])
        if existing:
            already_have += 1
            continue

        # Skip non-US entities (Nominatim county lookup is US-focused)
        countries = entity.get('t_any_countries', [])
        if countries and 'us' not in countries:
            non_us += 1
            continue

        # Get coordinates
        coords = entity.get('t_any_coordinates', [])
        if not coords:
            no_coords += 1
            continue

        lat = coords[0].get('lat')
        lon = coords[0].get('lon')
        if lat is None or lon is None:
            no_coords += 1
            continue

        # Rate limit: 1 req/sec for Nominatim
        county = reverse_geocode_nominatim(lat, lon)

        if county:
            results.append((doc_id, [county]))
            enriched += 1
            print(f"[{i+1}/{total}] {name} ({lat:.4f}, {lon:.4f}) -> {county}")
        else:
            # Fallback: try address parsing
            county_fb = extract_county_from_address(entity.get('t_enrichment'))
            if county_fb:
                results.append((doc_id, [county_fb]))
                enriched += 1
                print(f"[{i+1}/{total}] {name} (address fallback) -> {county_fb}")
            else:
                failed += 1
                print(f"[{i+1}/{total}] {name} ({lat:.4f}, {lon:.4f}) -> FAILED")

        # Nominatim rate limit
        time.sleep(1.1)

        # Progress checkpoint every 100
        if (i + 1) % 100 == 0:
            print(f"--- Progress: {i+1}/{total} processed, {enriched} enriched, {failed} failed ---")
            log_event("command", "enrich-counties", "local", "checkpoint",
                      input_summary=f"Progress: {i+1}/{total}",
                      output_summary=f"enriched={enriched}, failed={failed}")

    print(f"\n=== Enrichment Summary ===")
    print(f"Total entities: {total}")
    print(f"Already had counties: {already_have}")
    print(f"Non-US (skipped): {non_us}")
    print(f"No coordinates: {no_coords}")
    print(f"Enriched: {enriched}")
    print(f"Failed: {failed}")
    print(f"Mode: {'DRY RUN' if dry_run else 'WRITE'}")

    log_event("command", "enrich-counties", "local", "summary",
              input_summary=f"total={total}, mode={'dry_run' if dry_run else 'write'}",
              output_summary=f"enriched={enriched}, failed={failed}, skipped_existing={already_have}")

    return results


def write_to_firestore(results):
    """Batch write county enrichments to Firestore. 500 per batch."""
    db = _get_db()
    total = len(results)
    written = 0
    batch_size = 500

    for batch_start in range(0, total, batch_size):
        batch_end = min(batch_start + batch_size, total)
        batch = db.batch()

        for doc_id, counties in results[batch_start:batch_end]:
            ref = db.collection("locations").document(doc_id)
            batch.update(ref, {"t_any_counties": counties})

        batch.commit()
        written += (batch_end - batch_start)
        print(f"Batch committed: {written}/{total}")

    log_event("api_call", "enrich-counties", "firestore", "batch_write",
              input_summary=f"Writing t_any_counties to {total} docs",
              output_summary=f"Written: {written}/{total}",
              status="success")

    print(f"Firestore write complete: {written} documents updated.")
    return written


def main():
    parser = argparse.ArgumentParser(description="Enrich TripleDB entities with county data.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true", help="Preview enrichments without writing")
    group.add_argument("--write", action="store_true", help="Write enrichments to Firestore")
    args = parser.parse_args()

    iteration = os.environ.get("IAO_ITERATION", "unknown")
    print(f"=== TripleDB County Enrichment ({iteration}) ===")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'WRITE'}")

    log_event("command", "enrich-counties", "local", "start",
              input_summary=f"mode={'dry_run' if args.dry_run else 'write'}, iteration={iteration}")

    print("\nFetching TripleDB entities from Firestore...")
    entities = fetch_tripledb_entities()
    print(f"Fetched {len(entities)} TripleDB entities.")

    # Filter to only those missing counties
    missing = [e for e in entities if not e.get('t_any_counties')]
    print(f"{len(missing)} entities missing t_any_counties.")

    results = enrich_entities(entities, dry_run=args.dry_run)

    if args.write and results:
        print(f"\nWriting {len(results)} enrichments to Firestore...")
        write_to_firestore(results)
    elif args.dry_run and results:
        print(f"\nDry run complete. {len(results)} entities would be enriched.")
        print("Run with --write to apply changes.")


if __name__ == '__main__':
    main()
