# RickSteves - Design v1.7

**ADR-002 | Living Architecture Document**
**Project:** kylejeromethompson.com - Multi-Pipeline Location Intelligence Platform
**Pipeline 2:** RickSteves (Rick Steves' Europe)
**Author:** Kyle Thompson, VP of Engineering & Solutions Architect @ TachTech Engineering
**Date:** March 29, 2026

---

## Project Identity

| Key | Value |
|-----|-------|
| Domain | kylejeromethompson.com |
| Repository | `git@github.com:SOC-Foundry/kjtcom.git` |
| Firebase Project ID | `kjtcom-c78cd` |
| GCP Parent Org | socfoundry.com |
| Primary Dev Machine | NZXTcos (Intel i9-13900K, RTX 2080 SUPER, 64 GB DDR4, CachyOS) |

---

# 1. What This Pipeline Delivers

RickSteves is the second pipeline on kylejeromethompson.com. It processes 1,865 filtered YouTube videos from Rick Steves' Europe channel through the same IAO pipeline as CalGold. The critical difference: Rick Steves content is international (30+ European countries plus Egypt, Ethiopia, Iceland, Turkey, Iran) while CalGold is California-only.

This forces the first Thompson Schema evolution: adding `t_any_countries` and `t_any_regions` to the universal indicator fields. These new fields benefit ALL pipelines retroactively - CalGold entities get `t_any_countries: ["us"]` via backfill.

**Source Channel:** Rick Steves' Europe (`https://www.youtube.com/c/RickSteves`)
**Video Count:** 1,865 (filtered from 2,010 total - removed previews, trailers, packing tips, political content)
**Content Types:** Travel Bites (514 location clips), Travel Guide compilations (620), Art content (179), Full episodes (~100), Travel talks, country specials
**Entity Type:** `destination` (museum, church, castle, palace, restaurant, neighborhood, ruin, market, viewpoint, ancient site, park)

---

# 2. Thompson Schema Evolution (v2)

## 2.1 New Universal Indicator Fields

Added in v1.7. Apply to ALL pipelines (CalGold, RickSteves, future).

| Field | Type | Description | CalGold Value | RickSteves Value |
|-------|------|-------------|---------------|------------------|
| `t_any_countries` | array[string] | ISO country names, lowercase | ["us"] | ["italy", "france", "spain", ...] |
| `t_any_regions` | array[string] | Sub-country regions | ["southern california", "yosemite"] | ["tuscany", "burgundy", "the alps", "peloponnese"] |

## 2.2 Updated Schema Version

All new documents from v1.7+ use `t_schema_version: 2`. Existing CalGold documents (v1) get backfilled with `t_any_countries: ["us"]` and version bumped.

## 2.3 Complete Indicator Field List (v2)

| Field | Type | v1 | v2 | Description |
|-------|------|----|----|-------------|
| `t_any_names` | array[string] | YES | YES | All entity names |
| `t_any_people` | array[string] | YES | YES | All people mentioned |
| `t_any_cities` | array[string] | YES | YES | All city names |
| `t_any_states` | array[string] | YES | YES | State/province abbreviations or names |
| `t_any_counties` | array[string] | YES | YES | County/district names |
| `t_any_countries` | - | **NEW** | All country names (lowercase) |
| `t_any_regions` | - | **NEW** | Sub-country regions (Tuscany, The Alps, etc.) |
| `t_any_coordinates` | array[map] | YES | YES | All lat/lon pairs |
| `t_any_geohashes` | array[string] | YES | YES | Geohash prefixes (4/5/6 chars) |
| `t_any_keywords` | array[string] | YES | YES | All searchable terms |
| `t_any_categories` | array[string] | YES | YES | Normalized category tags |
| `t_any_urls` | array[string] | YES | YES | Associated URLs |
| `t_any_video_ids` | array[string] | YES | YES | Source YouTube video IDs |

## 2.4 Geocoding Fix: Google Places as Primary Coordinate Source

CalGold Phase 1 showed 43% Nominatim geocoding but 100% Google Places enrichment. Google Places returns coordinates. The pipeline should populate `t_any_coordinates` and `t_any_geohashes` from enrichment results when Nominatim fails.

New geocoding priority:
1. Nominatim (free, no API key cost)
2. If Nominatim misses: use Google Places coordinates from phase6_enrich
3. After enrichment: backfill any remaining coordinate gaps from Google Places response

This should push geocoding rates above 80% for both pipelines.

## 2.5 Security Rules (CRITICAL)

Added to CLAUDE.md and enforced across all pipelines:

```
## Security - ABSOLUTE RULES
- NEVER write API keys, tokens, or credentials into ANY file in the repo
- NEVER include API keys in build logs, reports, or changelog artifacts
- NEVER echo or print API key values in commands that get logged
- Read keys from environment variables ONLY
- If a key needs to be tested, print only "SET" or "NOT SET", never the value
- .gitignore MUST cover: *.sa.json, *-sa.json, .env
- Violation of these rules is a BLOCKING failure - stop and alert Kyle
```

---

# 3. RickSteves Pipeline Config

## 3.1 schema.json

```json
{
  "pipeline_id": "ricksteves",
  "display_name": "Rick Steves' Europe",
  "entity_type": "destination",
  "t_schema_version": 2,

  "indicators": {
    "name":              { "extract_into": "t_any_names" },
    "aka_names":         { "extract_into": "t_any_names" },
    "host":              { "extract_into": "t_any_people", "default": "rick steves" },
    "artist":            { "extract_into": "t_any_people" },
    "architect":         { "extract_into": "t_any_people" },
    "historical_figures": { "extract_into": "t_any_people" },
    "city":              { "extract_into": "t_any_cities" },
    "country":           { "extract_into": "t_any_countries" },
    "region":            { "extract_into": "t_any_regions" },
    "state_province":    { "extract_into": "t_any_states" },
    "categories":        { "extract_into": "t_any_categories" },
    "description":       { "extract_into": "t_any_keywords", "method": "tokenize" },
    "architectural_style": { "extract_into": "t_any_keywords" },
    "era":               { "extract_into": "t_any_keywords" },
    "address":           { "extract_into": "t_any_keywords", "method": "tokenize" },
    "video_ids":         { "extract_into": "t_any_video_ids" }
  },

  "enrichment_sources": ["nominatim", "google_places"],

  "source_schema": {
    "name": { "type": "string", "required": true },
    "description": { "type": "string", "required": true },
    "city": { "type": "string", "required": true },
    "country": { "type": "string", "required": true },
    "region": { "type": "string", "required": false },
    "state_province": { "type": "string", "required": false },
    "address": { "type": "string", "required": false },
    "architectural_style": { "type": "string", "required": false },
    "era": { "type": "string", "required": false },
    "artist": { "type": "string", "required": false },
    "architect": { "type": "string", "required": false },
    "historical_figures": { "type": "array", "required": false },
    "admission_info": { "type": "string", "required": false },
    "rick_tip": { "type": "string", "required": false },
    "categories": { "type": "array", "required": true },
    "aka_names": { "type": "array", "required": false },
    "visits": { "type": "array", "required": true }
  }
}
```

## 3.2 extraction_prompt.md

```
You are extracting structured destination data from a transcript of "Rick Steves' Europe"
content. Rick Steves visits specific European (and occasionally non-European) destinations -
museums, churches, castles, palaces, restaurants, neighborhoods, ancient ruins, markets,
viewpoints, parks, and cultural sites.

For each distinct destination visited or discussed in this video, extract:

{
  "name": "Primary destination name (in English)",
  "description": "2-3 sentence description of what this place is and why it matters",
  "city": "City name (in English)",
  "country": "Country name (in English)",
  "region": "Sub-country region if mentioned (e.g., Tuscany, Burgundy, Bavaria, The Peloponnese)",
  "state_province": "State or province if applicable",
  "address": "Street address if mentioned",
  "architectural_style": "Architectural style if relevant (Gothic, Baroque, Renaissance, etc.)",
  "era": "Historical era if relevant (Roman, Medieval, Renaissance, etc.)",
  "artist": "Primary artist if this is an art site (e.g., Michelangelo, Bernini)",
  "architect": "Architect if mentioned",
  "historical_figures": ["People historically associated with this place"],
  "admission_info": "Admission cost or hours if mentioned",
  "rick_tip": "Rick's practical travel tip about this place if he gives one",
  "categories": ["museum", "church", "castle", "palace", "restaurant", "neighborhood",
                  "ancient_ruin", "market", "viewpoint", "park", "monastery", "cemetery",
                  "bridge", "square", "fountain", "theater", "library", "university",
                  "fortification", "island", "beach", "mountain", "lake", "wine_region",
                  "food", "festival", "art", "architecture", "history", "nature"],
  "aka_names": ["Alternative names, local language names"],
  "visits": [
    {
      "video_id": "{VIDEO_ID}",
      "video_title": "{VIDEO_TITLE}",
      "host_intro": "First 1-2 sentences Rick says about this destination",
      "timestamp_start": 0.0
    }
  ]
}

Return a JSON array of destination objects. One video may discuss multiple destinations.
If the video is a general travel tips video with no specific geocodable destinations,
return an empty array.
Do NOT extract countries or cities as entities - only specific visitable places within them.
```

## 3.3 pipeline.json

```json
{
  "pipeline_id": "ricksteves",
  "display_name": "Rick Steves' Europe",
  "host": "Rick Steves",
  "source_network": "PBS / Rick Steves' Europe",
  "source_url": "https://www.youtube.com/c/RickSteves",
  "video_count": 1865,
  "entity_count": 0,
  "entity_type": "destination",
  "icon": "location_city",
  "color": "#1565C0",
  "t_schema_version": 2,
  "last_run": null,
  "phases_complete": []
}
```

---

# 4. Full Document Example - RickSteves Entity

```json
{
  "t_log_type": "ricksteves",
  "t_row_id": "ricksteves-uffizi-gallery-001",
  "t_event_time": "2019-09-15T00:00:00Z",
  "t_parse_time": "2026-04-05T12:00:00Z",
  "t_source_label": "Rick Steves' Europe",
  "t_schema_version": 2,

  "t_any_names": ["uffizi gallery", "galleria degli uffizi"],
  "t_any_people": ["rick steves", "botticelli", "leonardo da vinci", "michelangelo"],
  "t_any_cities": ["florence"],
  "t_any_states": [],
  "t_any_counties": [],
  "t_any_countries": ["italy"],
  "t_any_regions": ["tuscany"],
  "t_any_coordinates": [{ "lat": 43.7687, "lon": 11.2559 }],
  "t_any_geohashes": ["sr2y", "sr2yk", "sr2ykj"],
  "t_any_keywords": ["renaissance", "art museum", "botticelli birth of venus",
                      "medici", "florence", "gallery", "painting"],
  "t_any_categories": ["museum", "art", "architecture"],
  "t_any_urls": ["https://www.uffizi.it"],
  "t_any_video_ids": ["abc456"],

  "t_enrichment": {
    "google_places": {
      "t_match": "Uffizi Gallery Florence",
      "place_id": "ChIJ...",
      "rating": 4.7,
      "current_name": "Uffizi Gallery",
      "still_open": true,
      "website": "https://www.uffizi.it",
      "total_ratings": 98000,
      "enriched_at": "2026-04-05T12:00:00Z"
    },
    "nominatim": {
      "t_match": "Uffizi Gallery, Florence, Italy",
      "latitude": 43.7687,
      "longitude": 11.2559,
      "display_name": "Galleria degli Uffizi, Piazzale degli Uffizi, Florence, Tuscany, Italy",
      "geocoded_at": "2026-04-05T12:00:00Z"
    }
  },

  "source": {
    "name": "Uffizi Gallery",
    "description": "World-class Renaissance art museum housing masterpieces by Botticelli, Leonardo, and Michelangelo. The Medici family's former administrative offices transformed into one of Europe's greatest art collections.",
    "city": "Florence",
    "country": "Italy",
    "region": "Tuscany",
    "architectural_style": "Renaissance",
    "era": "Renaissance",
    "artist": "Botticelli",
    "architect": "Giorgio Vasari",
    "historical_figures": ["Medici family", "Cosimo I de' Medici"],
    "admission_info": "Book ahead to skip the line",
    "rick_tip": "Go early or late to avoid cruise ship crowds. The Birth of Venus is worth the wait.",
    "categories": ["museum", "art", "architecture"],
    "aka_names": ["Galleria degli Uffizi"],
    "visits": [
      {
        "video_id": "abc456",
        "video_title": "Florence, Italy: Renaissance Treasures",
        "host_intro": "The Uffizi Gallery is ground zero for Renaissance art...",
        "timestamp_start": 312.0
      }
    ]
  }
}
```

---

# 5. Cross-Pipeline Query Examples

With both CalGold and RickSteves in staging, these queries demonstrate the Thompson Schema's cross-dataset power:

```dart
// "Show me everything with 'cathedral' across ALL pipelines"
db.collection('locations')
  .where('t_any_keywords', arrayContains: 'cathedral')
// Returns: California missions (CalGold) + Notre-Dame, St. Peter's (RickSteves)

// "Everything in Italy"
db.collection('locations')
  .where('t_any_countries', arrayContains: 'italy')

// "Everything in California" 
db.collection('locations')
  .where('t_any_states', arrayContains: 'ca')

// "Renaissance sites worldwide"
db.collection('locations')
  .where('t_any_keywords', arrayContains: 'renaissance')

// "Everything in Tuscany"
db.collection('locations')
  .where('t_any_regions', arrayContains: 'tuscany')

// "Rick Steves destinations rated 4.5+"
db.collection('locations')
  .where('t_log_type', isEqualTo: 'ricksteves')
  .where('t_enrichment.google_places.rating', isGreaterThanOrEqualTo: 4.5)
```

---

# 6. Composite Indexes Required (Additions for v1.7)

Added to firestore.indexes.json:

| Collection | Fields | Query Use Case |
|------------|--------|---------------|
| locations | `t_any_countries` ARRAY, `t_log_type` ASC | "Rick Steves destinations in Italy" |
| locations | `t_any_countries` ARRAY, `t_enrichment.google_places.rating` DESC | "Highest-rated destinations in France" |
| locations | `t_any_regions` ARRAY, `t_log_type` ASC | "Rick Steves in Tuscany" |
| locations | `t_log_type` ASC, `t_any_countries` ARRAY | "All CalGold entities (US only)" |

---

# 7. Content Type Handling

Rick Steves' 1,865 videos include several content types. The extraction prompt handles all of them:

| Content Type | Count | Expected Entities/Video | Handling |
|--------------|-------|------------------------|----------|
| Travel Bite (location clip) | 514 | 1-2 | High yield. Location in title. |
| Travel Guide (compilation) | 620 | 3-10 | High yield. Multiple locations per video. |
| Art content (museums, churches) | 179 | 1-3 | Good yield. Specific buildings/artworks. |
| Full country/city episodes | ~100 | 5-15 | Highest yield. Many named places. |
| Travel talks/lectures | ~29 | 0-5 | Variable. Some reference specific places, some don't. |
| Music/symphonic specials | ~10 | 0 | Empty array expected. No geocodable content. |

Expected total unique entities after dedup: 2,500-4,000 (Rick visits many places per video and revisits popular destinations across episodes).

---

# 8. Migration Notes

## 8.1 google-generativeai -> google.genai

CalGold Phase 1 flagged a deprecation warning on the `google-generativeai` Python package. Before RickSteves Phase 1, migrate phase3_extract.py to use `google.genai` (the new SDK). This is a code change to the shared script that benefits both pipelines.

## 8.2 CalGold Schema v1 -> v2 Backfill

After RickSteves Phase 1 validates schema v2, backfill CalGold entities:

```python
# Backfill script (one-time)
for doc in db.collection('locations').where('t_log_type', '==', 'calgold').stream():
    doc.reference.update({
        't_any_countries': ['us'],
        't_any_regions': [],  # or extract from source if available
        't_schema_version': 2
    })
```

---

# 9. Locked Decisions

All previous locked decisions carried forward, plus:

| Decision | Value | Locked At | Rationale |
|----------|-------|-----------|-----------|
| RickSteves video count | 1,865 (filtered) | v1.7 | Removed previews, trailers, packing tips, political. |
| RickSteves source | youtube.com/c/RickSteves channel uploads | v1.7 | Channel URL, not curated playlist. |
| Thompson Schema v2 | Added t_any_countries, t_any_regions | v1.7 | International content requires country-level indicators. |
| Geocode priority | Nominatim first, Google Places coordinates fallback | v1.7 | Raises geocoding from 43% to 80%+. |
| API key security | CLAUDE.md security section, never write keys to files | v1.7 | CalGold Phase 1 exposed risk. |
| google.genai migration | Before RickSteves Phase 1 | v1.7 | Deprecated package warning from CalGold. |
| Gotcha G11 | API keys must never appear in build logs or repo files | v1.7 | New gotcha from CalGold Phase 1. |

---

# 10. Gotchas Registry (Additions)

| ID | Gotcha | Prevention | Source |
|----|--------|-----------|--------|
| G11 | API keys leaked into build logs via shell export commands | Security section in CLAUDE.md. Test keys with SET/NOT SET only. | CalGold v1.6 |
| G12 | google-generativeai package deprecated | Migrate to google.genai before next extraction run | CalGold v1.6 |
| G13 | Nominatim struggles with niche/non-English location names | Use Google Places coordinates as fallback after enrichment | CalGold v1.6 |
| G14 | International locations need country-level indicator fields | t_any_countries and t_any_regions added in schema v2 | RickSteves v1.7 |
| G15 | Rick Steves channel has 2010 videos including non-location content | Pre-filtered to 1865. Extraction prompt returns empty array for tip videos. | RickSteves v1.7 |

---

# 11. Changelog

**v1.7 (RickSteves Phase 1 - Design)**
- Pipeline 2 designed: Rick Steves' Europe, 1,865 filtered videos.
- Thompson Schema evolved to v2: added t_any_countries, t_any_regions.
- Geocoding fix: Google Places coordinates as fallback for Nominatim misses.
- API key security section added to CLAUDE.md.
- google.genai migration planned (deprecated google-generativeai).
- RickSteves schema.json: 16 indicator mappings, extraction_prompt.md for European destinations.
- 5 new gotchas (G11-G15) from CalGold Phase 1 lessons.
- Cross-pipeline query examples documented.

**v1.6 (CalGold Phase 1 - Discovery)**
- 30-video discovery batch: 30/30 acquired, 30/30 transcribed, 30/30 extracted.
- 57 unique California locations. 43% geocoded. 100% enriched.
- Thompson Schema v1 validated at scale.

**v0.5 (Phase 0 - Scaffold)**
- Repo, Firebase, multi-database, Thompson Schema v1, CalGold pipeline config.
