# kjtcom - Design v7.21 (Phase 7 - Firestore Load + TripleDB Migration)

**Pipeline:** kjtcom (cross-pipeline location intelligence platform)
**Phase:** 7 (Firestore Load)
**Iteration:** 21 (global counter)
**Executor:** Claude Code (schema mapping script + staging migration)
**Machine:** tsP3-cos (ThinkStation P3 Ultra SFF G2)
**Date:** April 2026

---

## Objective

Populate the production (default) Firestore `locations` collection with data from two sources:

1. **CalGold + RickSteves (staging -> production):** Copy 5,081 entities already in Thompson Indicator Fields format from the staging database to the production (default) database.
2. **TripleDB (cross-project import):** Read ~1,100 restaurant documents from TripleDB's Firestore project, transform to Thompson Indicator Fields schema v3, and write to kjtcom's production `locations` collection.

After this iteration, kylejeromethompson.com will display ~6,200+ entities from 3 pipelines (CalGold, RickSteves, TripleDB) with zero app-side changes. The live Firestore frontend decision from v6.15 makes this possible - new data surfaces immediately.

---

## Architecture Decisions

[DECISION] **Option 4: Hybrid migration for TripleDB.** Cross-project Admin SDK script reads from TripleDB's Firestore, transforms to Thompson Indicator Fields, writes to kjtcom's production Firestore. No re-processing of videos. No GPU time. No Gemini API calls. Carries forward existing geocoding, ratings, and enrichment data.

[DECISION] **Two SA credentials in one script.** The migration script uses two Firebase Admin SDK clients - one authenticated against the TripleDB project, one against kjtcom. Kyle is admin in both GCP orgs (TachTech-Engineering for TripleDB, socfoundry.com for kjtcom). Both SA JSON files are present on tsP3-cos.

[DECISION] **Staging -> production is a simple copy.** CalGold and RickSteves entities in kjtcom's staging database are already in Thompson Indicator Fields v3 format. A Firestore script reads from staging, writes to production (default). No transformation needed.

[DECISION] **TripleDB schema mapping, not re-extraction.** TripleDB's existing Firestore schema has rich data (restaurants, dishes, cuisines, ratings, coordinates, visit metadata) that maps cleanly to Thompson Indicator Fields. The mapping script transforms field names and structures while preserving all existing data quality.

[DECISION] **Composite indexes provisioned after load.** Firestore composite indexes for `t_any_*` array queries are created after data is loaded, based on the query patterns exposed in the Flutter app's query editor.

---

## Source: TripleDB Firestore Schema

**Project:** TachTech-Engineering/tripledb-e0f77 (separate Firebase project)
**Collection:** `restaurants`
**Document count:** ~1,100+
**Pipeline status:** v6.28 (production run complete, enrichment done)

### TripleDB Document Structure

```json
{
  "restaurant_id": "r_<uuid4>",
  "name": "Mama's Soul Food",
  "city": "Memphis",
  "state": "TN",
  "address": "123 Main St",
  "latitude": 35.1495,
  "longitude": -90.0490,
  "location": "<GeoPoint>",
  "cuisine_type": "Soul Food",
  "owner_chef": "Tyrone Washington",
  "still_open": true,
  "google_rating": 4.5,
  "yelp_rating": 4.0,
  "website_url": "https://mamassoul.com",
  "visits": [
    {
      "video_id": "Q2fk6b-hEbc",
      "youtube_url": "https://youtube.com/watch?v=Q2fk6b-hEbc",
      "video_title": "Top #DDD Videos in Memphis",
      "video_type": "compilation",
      "guy_intro": "Here at Mama's Soul Food...",
      "timestamp_start": 200.0,
      "timestamp_end": 480.0
    }
  ],
  "dishes": [
    {
      "dish_name": "Famous Fried Chicken",
      "description": "Brined overnight in buttermilk, double-dredged",
      "ingredients": ["chicken", "buttermilk", "seasoned flour"],
      "dish_category": "entree",
      "guy_response": "Now THAT is what I'm talking about!"
    }
  ],
  "created_at": "2026-03-17T00:00:00Z",
  "updated_at": "2026-03-17T00:00:00Z"
}
```

---

## Schema Mapping: TripleDB -> Thompson Indicator Fields

### Direct Field Mappings

| TripleDB Field | Thompson Field | Transform |
|----------------|---------------|-----------|
| name | t_any_names | Wrap in array: [name] |
| city | t_any_cities | Wrap in array: [city.lower()] |
| state | t_any_states | Wrap in array: [state.lower()] |
| latitude, longitude | t_any_coordinates | Object: {"lat": latitude, "lon": longitude} |
| cuisine_type | t_any_cuisines | Split on comma/slash, lowercase, wrap in array |
| dishes[].dish_name | t_any_dishes | Flatten: [dish.dish_name.lower() for dish in dishes] |
| owner_chef | t_any_people | Wrap in array: [owner_chef] (if not null) |
| visits[].video_id | t_any_video_ids | Flatten: [v.video_id for v in visits] |
| visits[].youtube_url | t_any_urls | Flatten: [v.youtube_url for v in visits] |
| address | t_source_label | Direct copy (address as source label) |
| restaurant_id | t_row_id | Direct copy or generate new hash |

### Hardcoded Backfills

| Thompson Field | Value | Rationale |
|----------------|-------|-----------|
| t_log_type | "tripledb" | Pipeline discriminator |
| t_any_actors | ["Guy Fieri", owner_chef] | Guy is always present; owner_chef added if not null |
| t_any_roles | ["host", "chef"] or ["host", "owner", "chef"] | Derived from owner_chef presence |
| t_any_shows | ["Diners, Drive-Ins and Dives"] | Single show for all TripleDB entities |
| t_any_countries | ["us"] | All DDD locations are US-based |
| t_any_continents | ["North America"] | Derived from country |
| t_any_eras | [] | Not applicable to DDD content (modern show) |
| t_schema_version | 3 | Current locked schema |
| t_event_time | created_at or first visit timestamp | Earliest known timestamp |
| t_parse_time | Now (migration timestamp) | When the migration ran |

### Derived Fields

| Thompson Field | Derivation |
|----------------|-----------|
| t_any_keywords | Combine: cuisine_type + dish categories + dish ingredients (flattened, deduped) |
| t_any_categories | From cuisine_type + dish_category values (e.g., "restaurant", "diner", cuisine_type) |
| t_any_counties | Requires Nominatim reverse geocode from lat/lon (if not already in TripleDB) |
| t_any_regions | From state code via US_STATE_TO_REGION lookup |
| t_any_geohashes | Computed from lat/lon via geohash library |

### Enrichment Carry-Forward

| TripleDB Field | Thompson Enrichment Field |
|----------------|--------------------------|
| google_rating | t_enrichment.google_places.rating |
| still_open | t_enrichment.google_places.still_open |
| website_url | t_enrichment.google_places.website |
| yelp_rating | t_enrichment.yelp.rating (new enrichment source) |

### Fields Intentionally Dropped

| TripleDB Field | Reason |
|----------------|--------|
| location (GeoPoint) | kjtcom uses t_any_coordinates (lat/lon object), not Firestore GeoPoints |
| visits[] (full array) | Individual visit metadata stored as t_any_video_ids + t_any_urls. Full visit objects not needed in Thompson schema. |
| dishes[] (full array) | Dish names flattened to t_any_dishes. Full dish objects (ingredients, guy_response) not carried. Could be revisited in Phase 8. |

---

## Source: CalGold + RickSteves (Staging Database)

**Database:** kjtcom-c78cd, database "staging"
**Collection:** `locations`
**Document count:** 5,081 (899 CalGold + 4,182 RickSteves)
**Schema:** Thompson Indicator Fields v3 (no transformation needed)

Migration is a direct copy: read from staging, write to production (default). Preserve all fields exactly.

---

## Composite Index Requirements

After data is loaded, the following Firestore composite indexes must be provisioned to support the query patterns in the Flutter app:

| Index | Fields | Purpose |
|-------|--------|---------|
| 1 | t_any_cuisines (array-contains) + t_log_type (==) | Filter cuisines by pipeline |
| 2 | t_any_actors (array-contains) + t_log_type (==) | Filter actors by pipeline |
| 3 | t_any_countries (array-contains) + t_log_type (==) | Filter countries by pipeline |
| 4 | t_any_dishes (array-contains) + t_log_type (==) | Filter dishes by pipeline |
| 5 | t_any_shows (array-contains) | Filter by show |
| 6 | t_any_keywords (array-contains) | Full-text keyword search |

Firestore auto-creates single-field indexes. Composite indexes are created via `firestore.indexes.json` or the Firebase Console when a query first fails.

---

## Success Criteria

| Criteria | Target |
|----------|--------|
| CalGold entities in production | 899 |
| RickSteves entities in production | 4,182 |
| TripleDB entities in production | ~1,100+ |
| Total entities in production | ~6,281+ |
| t_log_type values | calgold, ricksteves, tripledb |
| t_schema_version | 3 on all entities |
| t_any_shows values | California's Gold, Rick Steves' Europe, Diners Drive-Ins and Dives |
| TripleDB t_any_actors | All include "Guy Fieri" |
| TripleDB t_any_cuisines | >95% populated |
| TripleDB t_any_dishes | >90% populated |
| TripleDB geocoding | Carried from source (verify >90%) |
| kylejeromethompson.com | Displays results from all 3 pipelines |
| Pipeline-colored dots | CalGold gold, RickSteves blue, TripleDB red |
| Composite indexes | Provisioned for t_any_* query patterns |
| GCP cost | ~$0 (free tier reads/writes) |
| Interventions | 0 |
| Artifacts | 4 mandatory docs |

---

## Gotchas Active

| ID | Gotcha | Prevention |
|----|--------|-----------|
| G11 | API key leaks | NEVER cat config.fish or SA JSON files |
| G20 | Config.fish contains keys | grep only, never cat |
| G30 | Cross-project SA permissions | Verify both SA files exist and have Firestore read/write before running migration |
| G31 | TripleDB schema drift | Step 0 inspects actual TripleDB schema before writing mapping code. Schema from past conversations may be outdated. |
| G32 | Production Firestore rules | Verify Firestore rules allow Admin SDK writes to production (default) database. Admin SDK bypasses rules, but verify project-level IAM. |
| G33 | Duplicate entity IDs | Use deterministic t_row_id generation (hash of name+city+pipeline) to prevent dupes if script is re-run |

---

## Phase Structure Reference

| Phase | Name | Status | Iteration |
|-------|------|--------|-----------|
| 0 | Scaffold & Environment | DONE | v0.5 |
| 1 | Discovery (30 videos) | DONE | v1.6, v1.7 |
| 2 | Calibration (60 videos) | DONE | v2.8, v2.9 |
| 3 | Stress Test (90 videos) | DONE | v3.10, v3.11 |
| 4 | Validation + Schema v3 (120 videos) | DONE | v4.12, v4.13 |
| 5 | Production Run (full datasets) | CalGold DONE, RickSteves IN PROGRESS | v5.14, v5.15 |
| 6 | Flutter App | DONE | v6.15-v6.20 |
| 7 | Firestore Load | IN PROGRESS | v7.21 |
| 8 | Enrichment Hardening | Pending | - |
| 9 | App Optimization | Pending | - |
| 10 | Retrospective + Template | Pending | - |
