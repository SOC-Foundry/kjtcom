# kjtcom - Build v7.21 (Phase 7 - Firestore Load + TripleDB Migration)

**Pipeline:** kjtcom (cross-pipeline location intelligence platform)
**Phase:** 7 (Firestore Load)
**Iteration:** 21 (global counter)
**Executor:** Claude Code (Opus)
**Machine:** tsP3-cos (ThinkStation P3 Ultra SFF G2)
**Date:** April 2026

## Implementation Log

### Step 1: Environment Verification

- kjtcom SA: SET (via $GOOGLE_APPLICATION_CREDENTIALS)
- TripleDB SA: SET (~/.config/gcloud/tripledb-sa.json)
- TripleDB project: tripledb-e0f77
- kjtcom project: kjtcom-c78cd
- Python dependencies: firebase-admin, geohash2 - confirmed
- Fish shell throughout (mandatory)

### Step 2: Create migrate_tripledb.py

Created `pipeline/scripts/migrate_tripledb.py` with:
- Two Firestore clients (TripleDB source + kjtcom production destination)
- Full Thompson Indicator Fields schema v3 mapping:
  - Direct mappings: name, city, state, lat/lon, cuisine_type, dishes, owner_chef, visits
  - Hardcoded backfills: t_log_type="tripledb", t_any_actors=["Guy Fieri",...], t_any_shows=["Diners, Drive-Ins and Dives"], t_any_countries=["us"], t_any_continents=["North America"]
  - Derived fields: t_any_keywords (cuisines + ingredients + categories), t_any_categories, t_any_regions (US_STATE_TO_REGION lookup), t_any_geohashes
  - G31 enrichment carry-forward: 14 google_places fields (rating, still_open, website, business_status, match_score, source, formatted_address, current_name, maps_url, place_id, rating_count, photo_references, name_changed, enriched_at) + yelp.rating
- Deterministic t_row_id via SHA-256 hash of (name|city|tripledb) for dedup safety (G33)
- Batch writes (500 docs per batch)
- --dry-run, --limit, --project, --sa-path flags
- Field population summary with rates

### Step 3: Dry Run (--dry-run --limit 5)

```
python3 pipeline/scripts/migrate_tripledb.py \
  --project tripledb-e0f77 \
  --sa-path ~/.config/gcloud/tripledb-sa.json \
  --dry-run --limit 5
```

5 documents transformed. Mapping verified:
- t_any_names: populated (e.g., ["Tacos of Birria, La Nunica"], ["Restaurant 415"])
- t_any_cuisines: split on comma/slash, lowercased (e.g., ["mexican"], ["eclectic"])
- t_any_dishes: flattened from dishes array (e.g., ["queso tacos de chivo", "vampiro de res"])
- t_any_actors: ["Guy Fieri", owner_chef] when present
- t_any_coordinates: lat/lon objects from source
- t_any_geohashes: computed (e.g., ["9q5c", "9q5ct", "9q5ctr"])
- t_any_regions: derived from state (e.g., "ca" -> "pacific", "co" -> "mountain")
- t_enrichment.google_places: 14 fields carried forward including G31 additions
- t_row_id: deterministic hash (e.g., "tripledb-tacos-of-birria-la-unica-49af94c440")

Fix applied: t_source_label fallback from address to name when address is null.

### Step 4: Full TripleDB Migration

```
python3 pipeline/scripts/migrate_tripledb.py \
  --project tripledb-e0f77 \
  --sa-path ~/.config/gcloud/tripledb-sa.json
```

- Read: 1,102 documents from TripleDB restaurants collection
- Written: 1,102 documents to kjtcom production locations collection
- 3 batch commits (500 + 500 + 102)
- Production count: 1,100 (2 deduped via deterministic t_row_id - G33 working)

Field population rates (1,102 source docs):

| Field | Count | Rate |
|-------|-------|------|
| t_any_actors | 1,102 | 100% |
| t_any_categories | 1,102 | 100% |
| t_any_cuisines | 1,102 | 100% |
| t_any_dishes | 1,102 | 100% |
| t_any_keywords | 1,102 | 100% |
| t_any_names | 1,102 | 100% |
| t_any_shows | 1,102 | 100% |
| t_any_states | 1,102 | 100% |
| t_any_urls | 1,102 | 100% |
| t_any_video_ids | 1,102 | 100% |
| t_any_coordinates | 1,006 | 91% |
| t_any_geohashes | 1,006 | 91% |
| t_any_regions | 1,031 | 93% |
| t_any_cities | 980 | 88% |
| t_any_people | 971 | 88% |
| t_enrichment | 697 | 63% |

### Step 5: Create migrate_staging_to_production.py

Created `pipeline/scripts/migrate_staging_to_production.py` with:
- Single Firestore client with staging + production (default) database access
- Direct field copy - no transformation
- Batch writes (500 docs per batch)
- Pipeline and schema version breakdown in summary

### Step 6: Staging -> Production Migration

```
python3 pipeline/scripts/migrate_staging_to_production.py
```

- Read: 5,081 documents from staging locations collection
- Written: 5,081 documents to production (default) locations collection
- 11 batch commits (10x500 + 1x81)
- Pipeline breakdown: CalGold 899 + RickSteves 4,182

### Step 7: Post-Load Verification

Production entity counts:

| Pipeline | Count |
|----------|-------|
| CalGold | 899 |
| RickSteves | 4,182 |
| TripleDB | 1,100 |
| **Total** | **6,181** |

Schema version: 5,858/6,181 (94%) at v3. The 323 non-v3 entities are pre-existing CalGold (121) and RickSteves (202) staging data from earlier pipeline phases (v1/v2 schema entities loaded before schema v3 migration).

TripleDB field population audit (production - 1,100 docs):

| Field | Count | Rate | Target | Status |
|-------|-------|------|--------|--------|
| Cuisines | 1,100 | 100% | >95% | PASS |
| Dishes | 1,100 | 100% | >90% | PASS |
| Actors | 1,100 | 100% | 100% | PASS |
| Coordinates | 1,004 | 91% | >90% | PASS |
| Shows | 1,100 | 100% | 100% | PASS |
| Keywords | 1,100 | 100% | - | PASS |
| Categories | 1,100 | 100% | - | PASS |
| Regions | 1,030 | 93% | - | PASS |
| Geohashes | 1,004 | 91% | - | PASS |
| People | 969 | 88% | - | PASS |
| Enrichment | 695 | 63% | - | INFO |

### Step 8: Security Scan

- `grep -rnI "AIzaSy" .` - all matches are:
  - Firebase Web API key in `app/lib/firebase_options.dart` (public client key, expected)
  - References to the grep command itself in docs/plans
- No SA credentials, API keys, or secrets in migration scripts
- No SA JSON files catted or printed (G11, G20)

## Checklist

- [x] TripleDB dry run (5 docs) - mapping verified
- [x] Full TripleDB migration - 1,102 written, 1,100 in production
- [x] Staging -> production copy - 5,081 copied (899 CalGold + 4,182 RickSteves)
- [x] Production verification - 6,181 total entities
- [x] TripleDB field population - all targets met
- [x] Security scan - clean (Firebase Web key only)
- [x] 4 mandatory artifacts produced
