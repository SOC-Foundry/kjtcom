# CalGold - Design v0.5

**ADR-001 | Living Architecture Document**
**Project:** kylejeromethompson.com - Multi-Pipeline Location Intelligence Platform
**Pipeline 1:** CalGold (California's Gold with Huell Howser)
**Author:** Kyle Thompson, VP of Engineering & Solutions Architect @ TachTech Engineering
**Date:** March 29, 2026

---

## Project Identity

| Key | Value |
|-----|-------|
| Domain | kylejeromethompson.com |
| Repository | `git@github.com:SOC-Foundry/kjtcom.git` |
| Firebase Project Name | kjtcom |
| Firebase Project ID | `kjtcom-c78cd` |
| Firebase Project Number | 703812044891 |
| GCP Parent Org | socfoundry.com |
| Primary Dev Machine | NZXTcos (Intel i9-13900K, RTX 2080 SUPER, 64 GB DDR4, CachyOS) |

---

# Table of Contents

1. [Project Vision](#1-project-vision)
2. [Platform Constraints - Pillar 8](#2-platform-constraints---pillar-8)
3. [Thompson Schema (t_any)](#3-thompson-schema-t_any)
4. [Data Model](#4-data-model)
5. [Pipeline Architecture](#5-pipeline-architecture)
6. [CalGold Pipeline Config](#6-calgold-pipeline-config)
7. [Firestore Database Design](#7-firestore-database-design)
8. [Cloud Functions Search API](#8-cloud-functions-search-api)
9. [Flutter App Architecture](#9-flutter-app-architecture)
10. [Repo Structure](#10-repo-structure)
11. [Locked Decisions](#11-locked-decisions)
12. [Gotchas Registry](#12-gotchas-registry)
13. [Future Pipelines](#13-future-pipelines)
14. [Changelog](#14-changelog)

---

# 1. Project Vision

kylejeromethompson.com is a multi-pipeline location intelligence platform. Each pipeline processes a different YouTube playlist through the IAO pipeline (yt-dlp -> faster-whisper CUDA -> Gemini Flash extraction -> normalization -> Nominatim geocoding -> Google Places enrichment -> Firestore). The Flutter Web frontend provides a unified query interface across all pipeline datasets simultaneously.

The platform serves two purposes:

**Showcase:** A portfolio piece demonstrating data normalization, enrichment, and cross-dataset query architecture to investors and employers. The Thompson Schema (t_any_* indicator fields) mirrors the normalization patterns used in production SIEM migrations at TachTech Engineering.

**Skill development:** The extraction, normalization, and enrichment pipeline is structurally identical to the SIEM migration pipelines TachTech builds for Fortune 50 customers. Each schema.json mapping file is the same artifact type as a Splunk-to-Panther detection rule migration mapping. The t_any_* pattern directly parallels Panther's p_any_* indicator fields and Elastic Common Schema's base field sets.

**Pipeline 1 - CalGold:** 431 YouTube videos of Huell Howser's "California's Gold" and "Visiting with Huell Howser" - every episode visits specific California locations (landmarks, towns, parks, restaurants, historical sites, natural wonders). Near-100% geocodable.

**Playlist URL:** `https://www.youtube.com/playlist?list=PLr7fFk3JB5ic-nEyrqLj6MGDox5DO8oMl`
**Video Count:** 431
**Curator:** Wrestling Ernest Hemingway (YouTube user)
**Source Channels:** PBS SoCal, KCET, Ramcharged Adventures, Island Vibez TV, others

---

# 2. Platform Constraints - Pillar 8

Non-negotiable. Applies to all pipelines on kylejeromethompson.com.

| Layer | Tool | Rationale |
|-------|------|-----------|
| Frontend | Flutter Web | Single codebase for web + mobile. Cross-platform. |
| Database | Cloud Firestore (Blaze) | Denormalized document store. Pay-as-you-go. Cloud Functions. Multi-database. |
| Hosting | Firebase Hosting | Static CDN. Preview channels for staging. SSL auto. |
| Search | Cloud Functions + Firestore native queries | Complex cross-dataset queries. Fuzzy matching. Geo-radius. |
| Billing | Firebase Blaze (pay-as-you-go) | Removes daily caps. Enables Cloud Functions. Estimated $1-5/month. |
| Pipeline Orchestration | Claude Code (Opus) dev / Gemini CLI UAT | Proven across 48 TripleDB iterations. |
| LLM Extraction | Gemini 2.5 Flash API (free tier) | 1M token context. No chunking. $0. |
| Transcription | faster-whisper (CUDA) | Local. RTX 2080 SUPER or RTX 2000 Ada. |
| Geocoding | Nominatim (OSM) | Free. 1 req/sec rate limit. |
| Enrichment | Google Places API (New) | Free tier. Rating, open/closed, website, coordinates. |
| OS | CachyOS (Arch-based) | KDE Plasma 6 / Wayland. fish shell. |
| IDE | Antigravity (VS Code fork) | NOT Visual Studio Code. |
| Browsers | google-chrome-stable + firefox-esr from yay | NEVER chromium from pacman. |
| Shell | fish | No heredocs. Use printf or echo-append. |

---

# 3. Thompson Schema (t_any)

## 3.1 Design Philosophy

The Thompson Schema applies the same normalization pattern used by Panther SIEM's `p_any_*` indicator fields and Elastic Common Schema's base field sets. Regardless of which pipeline produced an entity, universal indicator fields provide cross-dataset query capability without knowing source schemas.

**Core principle:** If you want to query it across datasets, it goes in a `t_any_*` array. If you only need it within one pipeline, it goes in `source.*`. If it comes from enrichment, it goes in `t_enrichment.*`.

**Naming convention:** All Thompson Schema fields begin with `t_`. Standard fields use `t_` prefix. Indicator fields use `t_any_` prefix. This mirrors Panther's `p_` / `p_any_` convention.

## 3.2 Standard Fields (required on every document)

| Field | Type | Description |
|-------|------|-------------|
| `t_log_type` | string | Pipeline ID (discriminator). e.g., "calgold", "trails", "routes" |
| `t_row_id` | string | Unique entity ID. Format: `{pipeline}-{slug}-{seq}` |
| `t_event_time` | timestamp | When the source event occurred (episode air date, video upload) |
| `t_parse_time` | timestamp | When the pipeline processed it (UTC) |
| `t_source_label` | string | Human-readable pipeline name. e.g., "California's Gold" |
| `t_schema_version` | int | Schema version for this pipeline. Starts at 1. |

## 3.3 Indicator Fields (universal cross-pipeline arrays)

All `t_any_*` fields are arrays. Values are lowercased during normalization for consistent matching. Display-quality values are preserved in `source.*`.

| Field | Type | Description | Queryable Via |
|-------|------|-------------|---------------|
| `t_any_names` | array[string] | All names for this entity (primary, AKA, google_current_name) | array-contains |
| `t_any_people` | array[string] | All people mentioned (host, owner, chef, builder, historical figures) | array-contains |
| `t_any_cities` | array[string] | All city names | array-contains |
| `t_any_states` | array[string] | All state abbreviations | array-contains |
| `t_any_counties` | array[string] | All county names | array-contains |
| `t_any_coordinates` | array[map] | All lat/lon pairs. Each: `{ "lat": num, "lon": num }` | nested query |
| `t_any_geohashes` | array[string] | Geohash prefixes at multiple precisions (4, 5, 6 chars) for proximity | array-contains |
| `t_any_keywords` | array[string] | All searchable terms (tokenized descriptions, tags, features) | array-contains / array-contains-any |
| `t_any_categories` | array[string] | Normalized category tags (art, history, food, nature, architecture...) | array-contains |
| `t_any_urls` | array[string] | Associated URLs (website, Google Maps, Wikipedia) | array-contains |
| `t_any_video_ids` | array[string] | All source YouTube video IDs | array-contains |

### Adding Future t_any Fields

The schema is extensible. New `t_any_*` indicator fields can be added at any time:

1. Define the new field in the pipeline's `schema.json` indicator mapping
2. Increment `t_schema_version`
3. Run a backfill script on existing documents to populate the new field
4. Add the composite index to Firestore if needed
5. Update the Flutter search widget to query the new field

Candidate future fields: `t_any_addresses`, `t_any_phone_numbers`, `t_any_zip_codes`, `t_any_seasons` (for TV season queries), `t_any_cuisines` (if TripleDB migrates in), `t_any_trails` (if hiking pipeline added), `t_any_roads` (if motorcycle route pipeline added).

## 3.4 Enrichment Fields

Mirrors Panther's `p_enrichment` pattern. Each enrichment source is a named key containing the lookup result and the `t_match` value that triggered it.

```
"t_enrichment": {
  "google_places": {
    "t_match": "Watts Towers of Simon Rodia",
    "place_id": "ChIJ...",
    "rating": 4.7,
    "current_name": "Watts Towers of Simon Rodia State Historic Park",
    "still_open": true,
    "website": "https://...",
    "phone": "+1-213-847-4646",
    "total_ratings": 4200,
    "enriched_at": "2026-04-02T..."
  },
  "nominatim": {
    "t_match": "Watts Towers, Los Angeles, CA",
    "latitude": 33.9387,
    "longitude": -118.2420,
    "display_name": "Watts Towers, 1727 E 107th St...",
    "osm_type": "way",
    "osm_id": 123456,
    "geocoded_at": "2026-04-01T..."
  }
}
```

## 3.5 Source Fields

Pipeline-specific raw extracted data. Schema varies by pipeline. Defined in each pipeline's `schema.json`. Not queryable cross-dataset - only queryable when filtered to a specific `t_log_type`.

```
"source": {
  // Schema defined by pipeline config - see Section 6
  // CalGold: name, description, historical_period, builder, designation, etc.
  // Trails: trail_name, distance_miles, elevation_gain_ft, difficulty, etc.
  // Routes: road_name, road_number, distance_miles, start_point, end_point, etc.
}
```

## 3.6 Firestore Query Capabilities

| Operation | Supported? | Notes |
|-----------|-----------|-------|
| Equality on t_* standard fields | YES | Native. e.g., `t_log_type == 'calgold'` |
| Inequality on nested source fields | YES | Native. e.g., `source.elevation_gain_ft > 3000` |
| Inequality on enrichment fields | YES | Native. e.g., `t_enrichment.google_places.rating >= 4.5` |
| `array-contains` on t_any fields | YES | Native. Primary search mechanism. |
| `array-contains-any` on t_any fields | YES | Native. Up to 30 values. Multi-keyword search. |
| Two `array-contains` in one query | NO | Firestore limitation. Use Cloud Function or merge t_any fields. |
| Count / Sum / Average aggregation | YES | Native server-side aggregation (2023+). |
| Full-text fuzzy search | NO | Cloud Function required. |
| Geo-radius queries | NO | Cloud Function with geohash prefix ranges. |
| Query into arrays of maps (source.visits) | NO | Promote queryable fields to t_any arrays or top-level. |
| Cross-field OR | NO | Multiple queries + client-side merge, or Cloud Function. |

---

# 4. Data Model

## 4.1 Full Document Example - CalGold Entity

```json
{
  "t_log_type": "calgold",
  "t_row_id": "calgold-watts-towers-001",
  "t_event_time": "1996-03-15T00:00:00Z",
  "t_parse_time": "2026-04-01T12:00:00Z",
  "t_source_label": "California's Gold",
  "t_schema_version": 1,

  "t_any_names": ["watts towers", "watts towers of simon rodia", "nuestro pueblo"],
  "t_any_people": ["simon rodia", "huell howser"],
  "t_any_cities": ["los angeles"],
  "t_any_states": ["ca"],
  "t_any_counties": ["los angeles"],
  "t_any_coordinates": [{ "lat": 33.9387, "lon": -118.2420 }],
  "t_any_geohashes": ["9q5c", "9q5cs", "9q5cs7"],
  "t_any_keywords": ["folk art", "sculpture", "architecture", "national historic landmark",
                      "italian immigrant", "watts", "south los angeles", "mosaic", "towers"],
  "t_any_categories": ["art", "architecture", "history", "landmark"],
  "t_any_urls": ["https://www.wattstowers.org"],
  "t_any_video_ids": ["abc123"],

  "t_enrichment": {
    "google_places": {
      "t_match": "Watts Towers of Simon Rodia",
      "place_id": "ChIJ...",
      "rating": 4.7,
      "current_name": "Watts Towers of Simon Rodia State Historic Park",
      "still_open": true,
      "website": "https://www.wattstowers.org",
      "total_ratings": 4200,
      "enriched_at": "2026-04-02T12:00:00Z"
    },
    "nominatim": {
      "t_match": "Watts Towers, Los Angeles, CA",
      "latitude": 33.9387,
      "longitude": -118.2420,
      "display_name": "Watts Towers, 1727 E 107th St, Los Angeles, CA 90002",
      "geocoded_at": "2026-04-01T12:00:00Z"
    }
  },

  "source": {
    "name": "Watts Towers",
    "description": "17 interconnected sculptural towers built by Italian immigrant Simon Rodia over 33 years using steel pipes, mortar, and found objects",
    "historical_period": "1921-1954",
    "builder": "Simon Rodia",
    "designation": "National Historic Landmark",
    "address": "1727 E 107th St, Los Angeles, CA 90002",
    "huell_quote": "This is AMAZING!",
    "episode_categories": ["art", "architecture", "history"],
    "visits": [
      {
        "video_id": "abc123",
        "video_title": "Watts Towers - California's Gold",
        "host_intro": "Huell visits the incredible Watts Towers in South Los Angeles...",
        "timestamp_start": 45.0,
        "season": 2,
        "episode_number": 204
      }
    ]
  }
}
```

## 4.2 Pipeline Registry Document

```
Collection: pipelines

Document: calgold
{
  "display_name": "California's Gold",
  "host": "Huell Howser",
  "source_network": "PBS SoCal / KCET",
  "playlist_url": "https://youtube.com/playlist?list=PLr7fFk3JB5ic-nEyrqLj6MGDox5DO8oMl",
  "video_count": 431,
  "entity_count": 0,
  "entity_type": "landmark",
  "icon": "castle",
  "color": "#C4A000",
  "t_schema_version": 1,
  "last_run": null,
  "phases_complete": []
}
```

## 4.3 Video Bookkeeping Document

```
Collection: videos

Document: {video_id}
{
  "t_log_type": "calgold",
  "title": "Watts Towers - California's Gold",
  "channel": "PBS SoCal",
  "status": "pending",
  "duration_seconds": 1656,
  "downloaded_at": null,
  "transcribed_at": null,
  "extracted_at": null,
  "normalized_at": null,
  "geocoded_at": null,
  "enriched_at": null,
  "loaded_at": null
}
```

---

# 5. Pipeline Architecture

## 5.1 Pipeline Stages

```
YouTube Playlist (431 videos)
    | yt-dlp
    v
MP3 Audio (pipeline/data/calgold/audio/)
    | faster-whisper (CUDA, RTX 2080 SUPER)
    v
Timestamped Transcripts (pipeline/data/calgold/transcripts/)
    | Gemini 2.5 Flash API + config/calgold/extraction_prompt.md
    v
Raw Extracted JSON (pipeline/data/calgold/extracted/)
    | phase4_normalize.py + config/calgold/schema.json
    v
Normalized JSONL with t_any_* fields (pipeline/data/calgold/normalized/)
    | Nominatim API (1 req/sec)
    v
Geocoded JSONL (pipeline/data/calgold/geocoded/)
    | Google Places API (New)
    v
Enriched JSONL (pipeline/data/calgold/enriched/)
    | Firebase Admin SDK -> Firestore (staging, then production)
    v
Cloud Firestore (kjtcom-c78cd Firebase project)
    | Flutter Web
    v
kylejeromethompson.com
```

## 5.2 Shared vs Per-Pipeline Components

| Component | Shared or Per-Pipeline | Location |
|-----------|----------------------|----------|
| `phase1_acquire.py` | Shared | `pipeline/scripts/` |
| `phase2_transcribe.py` | Shared | `pipeline/scripts/` |
| `phase3_extract.py` | Shared (reads per-pipeline prompt) | `pipeline/scripts/` |
| `phase4_normalize.py` | Shared (reads per-pipeline schema.json) | `pipeline/scripts/` |
| `phase5_geocode.py` | Shared | `pipeline/scripts/` |
| `phase6_enrich.py` | Shared | `pipeline/scripts/` |
| `phase7_load.py` | Shared (target database configurable) | `pipeline/scripts/` |
| `extraction_prompt.md` | Per-Pipeline | `pipeline/config/{pipeline_id}/` |
| `schema.json` | Per-Pipeline | `pipeline/config/{pipeline_id}/` |
| `pipeline.json` | Per-Pipeline | `pipeline/config/{pipeline_id}/` |
| `playlist_urls.txt` | Per-Pipeline | `pipeline/config/{pipeline_id}/` |
| Audio / transcript / data | Per-Pipeline | `pipeline/data/{pipeline_id}/` |

## 5.3 Normalization Script Logic

`phase4_normalize.py` is the heart of the Thompson Schema. It reads `schema.json`, takes raw extracted JSON, and produces normalized JSONL with all `t_*` and `t_any_*` fields populated.

Pseudocode:

```python
def normalize(raw_entity: dict, schema: dict) -> dict:
    normalized = {}

    # 1. Standard fields
    normalized['t_log_type'] = schema['pipeline_id']
    normalized['t_row_id'] = generate_row_id(schema['pipeline_id'], raw_entity)
    normalized['t_event_time'] = extract_event_time(raw_entity)
    normalized['t_parse_time'] = utc_now()
    normalized['t_source_label'] = schema['display_name']
    normalized['t_schema_version'] = schema['t_schema_version']

    # 2. Indicator fields - driven by schema.json mappings
    for source_field, mapping in schema['indicators'].items():
        target_field = mapping['extract_into']
        method = mapping.get('method', 'direct')
        value = raw_entity.get(source_field)

        if value is None:
            continue

        if target_field not in normalized:
            normalized[target_field] = []

        if method == 'direct':
            if isinstance(value, list):
                normalized[target_field].extend([v.lower() for v in value])
            else:
                normalized[target_field].append(value.lower())
        elif method == 'tokenize':
            tokens = tokenize_for_search(value)
            normalized[target_field].extend(tokens)

    # 3. Deduplicate all t_any arrays
    for key in normalized:
        if key.startswith('t_any_') and isinstance(normalized[key], list):
            normalized[key] = sorted(set(normalized[key]))

    # 4. Source fields - preserve original schema
    normalized['source'] = raw_entity

    return normalized
```

---

# 6. CalGold Pipeline Config

## 6.1 schema.json

```json
{
  "pipeline_id": "calgold",
  "display_name": "California's Gold",
  "entity_type": "landmark",
  "t_schema_version": 1,

  "indicators": {
    "name":              { "extract_into": "t_any_names" },
    "aka_names":         { "extract_into": "t_any_names" },
    "host":              { "extract_into": "t_any_people", "default": "huell howser" },
    "builder":           { "extract_into": "t_any_people" },
    "owner":             { "extract_into": "t_any_people" },
    "historical_figures": { "extract_into": "t_any_people" },
    "city":              { "extract_into": "t_any_cities" },
    "state":             { "extract_into": "t_any_states", "default": "ca" },
    "county":            { "extract_into": "t_any_counties" },
    "episode_categories": { "extract_into": "t_any_categories" },
    "designation":       { "extract_into": "t_any_keywords" },
    "description":       { "extract_into": "t_any_keywords", "method": "tokenize" },
    "address":           { "extract_into": "t_any_keywords", "method": "tokenize" },
    "video_ids":         { "extract_into": "t_any_video_ids" }
  },

  "enrichment_sources": ["nominatim", "google_places"],

  "source_schema": {
    "name": { "type": "string", "required": true },
    "description": { "type": "string", "required": true },
    "city": { "type": "string", "required": true },
    "state": { "type": "string", "required": false, "default": "CA" },
    "county": { "type": "string", "required": false },
    "address": { "type": "string", "required": false },
    "historical_period": { "type": "string", "required": false },
    "builder": { "type": "string", "required": false },
    "owner": { "type": "string", "required": false },
    "historical_figures": { "type": "array", "required": false },
    "designation": { "type": "string", "required": false },
    "huell_quote": { "type": "string", "required": false },
    "episode_categories": { "type": "array", "required": true },
    "aka_names": { "type": "array", "required": false },
    "visits": { "type": "array", "required": true }
  }
}
```

## 6.2 extraction_prompt.md

```
You are extracting structured location data from a transcript of a "California's Gold" or
"Visiting with Huell Howser" episode. Huell Howser visits specific California locations -
landmarks, parks, restaurants, historical sites, natural wonders, museums, and communities.

For each distinct location visited in this episode, extract:

{
  "name": "Primary location name",
  "description": "2-3 sentence description of what this place is",
  "city": "City name",
  "state": "CA",
  "county": "County if mentioned",
  "address": "Street address if mentioned",
  "historical_period": "Time period if relevant (e.g., '1921-1954')",
  "builder": "Person who built/founded it if mentioned",
  "owner": "Current owner/operator if mentioned",
  "historical_figures": ["People associated with this location"],
  "designation": "Official designation if any (National Historic Landmark, State Park, etc.)",
  "huell_quote": "Most memorable Huell quote about this location",
  "episode_categories": ["art", "history", "food", "nature", "architecture", "community",
                          "industry", "agriculture", "science", "transportation", "military",
                          "sports", "music", "religion"],
  "aka_names": ["Alternative names for this location"],
  "visits": [
    {
      "video_id": "{VIDEO_ID}",
      "video_title": "{VIDEO_TITLE}",
      "host_intro": "First 1-2 sentences Huell says about arriving at this location",
      "timestamp_start": 0.0
    }
  ]
}

Return a JSON array of location objects. One episode may visit multiple locations.
If no specific geocodable location is identifiable, return an empty array.
```

---

# 7. Firestore Database Design

## 7.1 Multi-Database Layout

```
Firebase Project: kjtcom (kjtcom-c78cd)
GCP Org: socfoundry.com
├── (default)     # Production - all pipeline data, live app reads from here
│   ├── locations/     # All entities, all pipelines, t_any schema
│   ├── pipelines/     # Pipeline registry metadata
│   └── videos/        # Pipeline bookkeeping
│
└── staging        # Pipeline development - same schema, disposable
    ├── locations/
    ├── pipelines/
    └── videos/
```

Pipeline development loads to `staging`. Validated data promotes to `(default)`. Staging can be wiped freely without touching production.

## 7.2 Firestore Security Rules

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Public read on all collections - app is read-only
    match /locations/{docId} {
      allow read: if true;
      allow write: if false;  // Pipeline loads via Admin SDK (bypasses rules)
    }
    match /pipelines/{docId} {
      allow read: if true;
      allow write: if false;
    }
    match /videos/{docId} {
      allow read: if true;
      allow write: if false;
    }
  }
}
```

## 7.3 Composite Indexes Required

| Collection | Fields | Query Use Case |
|------------|--------|---------------|
| locations | `t_log_type` ASC, `t_enrichment.google_places.rating` DESC | "CalGold locations sorted by rating" |
| locations | `t_log_type` ASC, `t_any_states` ARRAY, `t_enrichment.google_places.rating` DESC | "CalGold in CA sorted by rating" |
| locations | `t_any_geohashes` ARRAY, `t_log_type` ASC | "Nearby entities from specific pipeline" |
| locations | `t_any_geohashes` ARRAY, `t_enrichment.google_places.still_open` ASC | "Nearby open locations" |
| locations | `t_log_type` ASC, `source.difficulty` ASC | "Trails by difficulty" (future pipeline) |

Auto-created single-field indexes cover: all `t_any_*` arrays, `t_log_type`, `t_event_time`.

## 7.4 Estimated Cost (Blaze)

| Component | Monthly Estimate |
|-----------|-----------------|
| Firestore reads (500K/mo estimate) | ~$0.30 |
| Firestore writes (pipeline loads, rare) | ~$0.05 |
| Firestore storage (15 MB across all pipelines) | ~$0.00 |
| Cloud Functions invocations (search API) | ~$0.40 |
| Firebase Hosting (Flutter Web, CDN) | ~$0.00 |
| **Total** | **$1-3/month** |

Budget alert set at $10/month.

---

# 8. Cloud Functions Search API

## 8.1 Search Endpoint

A single Cloud Function handles complex queries that exceed native Firestore capabilities.

```
POST /api/search
{
  "query": "historical sites near Mission Viejo",
  "filters": {
    "t_log_type": null,                    // null = all pipelines
    "t_any_states": "ca",                  // optional state filter
    "t_enrichment.google_places.still_open": true,  // optional
    "geo_near": { "lat": 33.5963, "lon": -117.6581, "radius_miles": 25 }
  },
  "sort": "t_enrichment.google_places.rating",
  "sort_order": "desc",
  "limit": 20
}
```

## 8.2 What the Cloud Function Handles

- Multi-array queries (two `array-contains` conditions)
- Full-text fuzzy search (Levenshtein distance on `t_any_keywords`)
- Geo-radius filtering (geohash prefix range calculation)
- Cross-field OR conditions
- Result merging and relevance ranking
- Optional Gemini Flash natural language query interpretation

## 8.3 What Native Firestore Handles (no Cloud Function)

- Single `array-contains` or `array-contains-any` queries
- Equality / inequality / range on any field (nested OK)
- Count / sum / average aggregations
- Pagination with `startAfter` / `limit`

The Flutter app tries native Firestore first. Falls back to the Cloud Function for complex queries.

---

# 9. Flutter App Architecture

Phase 8 deliverable. Design tokens and component patterns TBD at Phase 8.

**Core features (MVP):**

- Unified search bar querying `t_any_keywords` across all pipelines
- Map view with pins for all geocoded entities (color-coded by pipeline)
- List view with pipeline filter tabs
- Entity detail page rendering `source.*` and `t_enrichment.*` dynamically
- YouTube deep links (video_id + timestamp_start)
- "Nearby" using browser geolocation + geohash queries
- Pipeline selector (show/hide individual datasets)
- Cookie consent + Firebase Analytics (consent mode v2)

**Design direction:** TBD. Will use Firecrawl MCP to crawl 4 reference sites for inspiration during Phase 8.

---

# 10. Repo Structure

```
kjtcom/
├── app/                              # Flutter Web
│   ├── lib/
│   │   ├── models/                   # Thompson Schema Dart models
│   │   ├── providers/                # Riverpod providers
│   │   ├── screens/                  # Map, List, Search, Detail
│   │   ├── widgets/                  # Shared components
│   │   └── main.dart
│   ├── web/
│   ├── pubspec.yaml
│   └── GEMINI.md
│
├── pipeline/
│   ├── scripts/                      # SHARED pipeline stages
│   │   ├── phase1_acquire.py
│   │   ├── phase2_transcribe.py
│   │   ├── phase3_extract.py
│   │   ├── phase4_normalize.py       # Thompson Schema normalization
│   │   ├── phase5_geocode.py
│   │   ├── phase6_enrich.py
│   │   ├── phase7_load.py
│   │   └── utils/
│   │       ├── thompson_schema.py    # t_any field population logic
│   │       ├── geohash.py            # geohash encoding
│   │       └── checkpoint.py         # resume support
│   │
│   ├── config/                       # PER-PIPELINE configuration
│   │   └── calgold/
│   │       ├── pipeline.json         # pipeline metadata
│   │       ├── schema.json           # indicator field mappings
│   │       ├── extraction_prompt.md  # Gemini extraction prompt
│   │       └── playlist_urls.txt     # YouTube playlist URL(s)
│   │
│   ├── data/                         # PER-PIPELINE data (gitignored)
│   │   └── calgold/
│   │       ├── audio/
│   │       ├── transcripts/
│   │       ├── extracted/
│   │       ├── normalized/
│   │       ├── geocoded/
│   │       └── enriched/
│   │
│   ├── agents/
│   └── GEMINI.md
│
├── functions/                        # Firebase Cloud Functions
│   ├── src/
│   │   └── search.ts                 # Search API endpoint
│   ├── package.json
│   └── tsconfig.json
│
├── docs/
│   ├── calgold-design-v0.4.md        # This file
│   ├── calgold-plan-v0.4.md          # Execution plan
│   └── archive/
│
├── requirements/
│   └── install.fish
│
├── firebase.json
├── firestore.rules
├── firestore.indexes.json
├── .firebaserc
├── .gitignore
├── CLAUDE.md
├── GEMINI.md
└── README.md
```

---

# 11. Locked Decisions

| Decision | Value | Locked At | Rationale |
|----------|-------|-----------|-----------|
| Repository | `git@github.com:SOC-Foundry/kjtcom.git` | v0.5 | SOC-Foundry org. Short repo name. |
| Firebase project | kjtcom (`kjtcom-c78cd`) under socfoundry.com | v0.5 | GCP org-level billing and IAM. |
| Domain | kylejeromethompson.com | v0.5 | Personal showcase site. |
| Schema namespace | `t_` / `t_any_` (Thompson Schema) | v0.4 | Parallels Panther p_any pattern. Professional showcase. |
| Firebase billing | Blaze (pay-as-you-go) | v0.4 | Cloud Functions. No daily caps. Multi-database. |
| Database pattern | Single flat collection + discriminator | v0.4 | Cross-dataset queries via t_any arrays. Native Firestore. |
| Multi-database | (default) + staging | v0.4 | Fearless pipeline dev. Same schema, disposable staging. |
| Search strategy | Native Firestore + Cloud Function fallback | v0.4 | Start simple, add complexity only where needed. |
| Primary dev machine | NZXTcos (i9-13900K, RTX 2080 SUPER, CachyOS) | v0.5 | CUDA transcription. 8 GB VRAM. 64 GB RAM. |
| Em-dash prohibition | Never. Use " - " instead. | TripleDB v10.44 | Carried forward from TripleDB. |
| Git write commands | Human only. Agent never commits. | IAO Pillar 2 | Carried forward from IAO methodology. |
| Shell | fish. No heredocs. | IAO template | Carried forward. |
| IDE | Antigravity (VS Code fork) | IAO template | Carried forward. |
| Browsers | google-chrome-stable + firefox-esr | IAO template | NEVER chromium. Carried forward. |
| TripleDB migration | Undecided | v0.4 | Revisit after CalGold pipeline 1 runs. |

---

# 12. Gotchas Registry

| ID | Gotcha | Prevention | Source |
|----|--------|-----------|--------|
| G1 | fish has no heredocs | Use printf or echo-append | TripleDB v0.7 |
| G2 | LD_LIBRARY_PATH must be set at shell level for CUDA | Set in fish config, not Python | TripleDB v2.11 |
| G3 | Gemini Flash API timeouts on marathon transcripts | 300-second timeout for extraction | TripleDB v2.11 |
| G4 | Null-name entities collapse during dedup | Input validation before normalization | TripleDB v5.14 |
| G5 | dart:html crashes before framework init | Lazy init, deferred DOM access | TripleDB v9.36 |
| G6 | Claude Code crashes in IDE terminal | Run from Konsole, not Antigravity terminal | KT v10.48 |
| G7 | Cloudflare WARP requires NODE_EXTRA_CA_CERTS | Set env var for Node.js MCP servers | TripleDB |
| G8 | Firestore array-contains limited to ONE per query | Merge arrays or use Cloud Function | v0.4 |
| G9 | Cannot query into arrays of maps | Promote queryable fields to t_any arrays | v0.4 |
| G10 | Blaze billing can surprise if misconfigured | Set $10/month budget alert in Firebase Console | v0.4 |

---

# 13. Future Pipelines

| Pipeline ID | Source | Entity Type | Video Count | Status |
|-------------|--------|-------------|-------------|--------|
| `calgold` | California's Gold (Huell Howser) | landmark | 431 | Phase 0 |
| TBD | Hiking / trail content | trail | 400-1000 | Candidate |
| TBD | Motorcycle touring / routes | route | 400-1000 | Candidate |
| TBD | Historical California | historical_site | 400-1000 | Candidate |
| `tripledb` | Diners, Drive-Ins and Dives | restaurant | 805 | Migration candidate |

Each new pipeline requires:
1. `pipeline/config/{id}/schema.json` - indicator mappings
2. `pipeline/config/{id}/extraction_prompt.md` - Gemini prompt
3. `pipeline/config/{id}/playlist_urls.txt` - YouTube URL
4. `pipeline/config/{id}/pipeline.json` - metadata
5. Composite indexes for any new source.* field queries

No code changes to shared pipeline scripts.

---

# 14. Changelog

**v0.5 (Phase 0 - Architecture + Project Identity)**
- Firebase project locked: kjtcom (`kjtcom-c78cd`) under socfoundry.com GCP org.
- Repository locked: `git@github.com:SOC-Foundry/kjtcom.git`
- Domain locked: kylejeromethompson.com
- Primary dev machine locked: NZXTcos (i9-13900K, RTX 2080 SUPER, CachyOS).
- All v0.4 architecture decisions carried forward.

**v0.4 (Phase 0 - Architecture)**
- Thompson Schema (t_any_*) designed - Panther p_any pattern adapted for location intelligence.
- Firebase Blaze selected. Cloud Functions search API designed.
- Multi-database: (default) production + staging.
- CalGold pipeline config: schema.json, extraction_prompt.md.
- Repo structure defined for multi-pipeline monorepo.
- 10 gotchas carried forward from TripleDB + 3 new for Firestore.
- Future pipelines identified: trails, routes, historical, TripleDB migration.
