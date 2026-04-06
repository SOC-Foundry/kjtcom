# kjtcom - Comprehensive Local Repository Report (v9.34)

**Generated:** 2026-04-04
**Branch:** main (5dd8ce2)
**Live URL:** kylejeromethompson.com
**Firebase Project:** kjtcom-c78cd

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Repository Structure](#2-repository-structure)
3. [Tech Stack](#3-tech-stack)
4. [Flutter App Architecture](#4-flutter-app-architecture)
5. [Data Models](#5-data-models)
6. [Query System (Deep Dive)](#6-query-system-deep-dive)
7. [State Management (Riverpod Providers)](#7-state-management-riverpod-providers)
8. [Widget Inventory](#8-widget-inventory)
9. [Theme and Design System](#9-theme-and-design-system)
10. [Database Structure (Firestore)](#10-database-structure-firestore)
11. [Thompson Indicator Fields Schema](#11-thompson-indicator-fields-schema)
12. [Data Pipeline](#12-data-pipeline)
13. [Cloud Functions](#13-cloud-functions)
14. [Infrastructure and Deployment](#14-infrastructure-and-deployment)
15. [Test Coverage](#15-test-coverage)
16. [Gotcha Registry](#16-gotcha-registry)
17. [Version History and Changelog](#17-version-history-and-changelog)
18. [Current Progress and Hangups](#18-current-progress-and-hangups)
19. [Future Directions](#19-future-directions)
20. [File Index](#20-file-index)

---

## 1. Project Overview

kjtcom is a cross-pipeline location intelligence platform built on Iterative Agentic Orchestration (IAO). It extracts entities from YouTube playlists via AI transcription and extraction, normalizes them into Thompson Indicator Fields, and serves them through a Flutter Web frontend with a NoSQL query interface.

**Key numbers:**
- 6,181 geocoded entities in production Firestore
- 3 live pipelines (CalGold, RickSteves, TripleDB)
- 22 Thompson Indicator Fields (t_any_* universal schema)
- 6,878 autocomplete values across 21 fields
- 34 iterations (v0.5 through v9.34)
- 25 Dart source files, ~4,200 LOC

**Architecture flow:**

```
YouTube Playlist -> yt-dlp -> MP3 -> faster-whisper (CUDA) -> Transcripts
    -> Gemini 2.5 Flash Extraction -> Thompson Indicator Fields Normalization
    -> Nominatim Geocoding -> Google Places Enrichment
    -> Cloud Firestore -> Flutter Web + Cloud Functions
```

---

## 2. Repository Structure

```
kjtcom/
|-- app/                           # Flutter Web application
|   |-- lib/                       # Dart source (25 files, ~4,200 LOC)
|   |   |-- main.dart              # Entry point, Firebase init, Riverpod
|   |   |-- firebase_options.dart  # Auto-generated Firebase config
|   |   |-- models/                # Data models (2 files)
|   |   |-- providers/             # Riverpod state management (5 files)
|   |   |-- theme/                 # Design tokens and styling (2 files)
|   |   +-- widgets/               # UI components (14 files)
|   |-- test/                      # Widget tests (1 file, 15 test cases)
|   |-- web/                       # Web platform (index.html, manifest, favicon)
|   |-- assets/                    # Static assets
|   |   |-- fonts/                 # Geist Sans/Mono (4 font files)
|   |   |-- globe_hero.jpg         # Background hero image (648 KB)
|   |   +-- value_index.json       # Autocomplete index (169 KB, 6,878 values)
|   |-- build/                     # Flutter build output (~84 MB)
|   |-- pubspec.yaml               # Dependencies
|   +-- analysis_options.yaml      # Linter config
|
|-- pipeline/                      # Data processing orchestration
|   |-- config/                    # Per-pipeline configuration
|   |   |-- calgold/               # California's Gold (390 videos, 899 entities)
|   |   |   |-- pipeline.json      # Pipeline metadata
|   |   |   |-- schema.json        # Thompson field mappings
|   |   |   |-- extraction_prompt.md  # Gemini Flash prompt
|   |   |   +-- playlist_urls.txt  # YouTube video IDs
|   |   +-- ricksteves/            # Rick Steves' Europe (1,865 videos, 4,182 entities)
|   |       +-- [same 4 config files]
|   |-- scripts/                   # Python pipeline scripts (23 files)
|   |   |-- phase1_acquire.py      # Download audio (yt-dlp)
|   |   |-- phase2_transcribe.py   # Transcribe (faster-whisper/CUDA)
|   |   |-- phase3_extract.py      # Extract (Gemini 2.5 Flash)
|   |   |-- phase4_normalize.py    # Normalize to Thompson fields
|   |   |-- phase5_geocode.py      # Geocode (Nominatim)
|   |   |-- phase6_enrich.py       # Enrich (Google Places)
|   |   |-- phase7_load.py         # Load to Firestore
|   |   |-- utils/                 # Utility modules (4 files)
|   |   |-- backfill_*.py          # 3 migration/backfill scripts
|   |   |-- fix_*.py               # 3 data correction scripts
|   |   |-- migrate_*.py           # 2 migration scripts
|   |   +-- generate_value_index.py  # Autocomplete index generator
|   +-- data/                      # Pipeline working data (~11.8 GB, git-ignored)
|       |-- calgold/               # 5.5 GB (audio, transcripts, extracted, normalized, geocoded, enriched)
|       +-- ricksteves/            # 6.3 GB (same structure)
|
|-- functions/                     # Cloud Functions (Node.js/TypeScript)
|   |-- src/index.ts               # Single search endpoint (116 lines)
|   |-- package.json               # Node 20, firebase-admin, firebase-functions
|   +-- tsconfig.json              # TypeScript config
|
|-- docs/                          # IAO artifact loop (living documentation)
|   |-- kjtcom-design-v9.34.md    # Current design contract
|   |-- kjtcom-plan-v9.34.md      # Current execution plan
|   |-- kjtcom-build-v9.34.md     # Current build session log
|   |-- kjtcom-report-v9.34.md    # Current metrics/pass-fail report
|   |-- kjtcom-changelog.md       # Master changelog (all versions)
|   |-- install.fish              # Dependency installation script
|   +-- archive/                  # 128 historical artifacts (v0.5 through v9.33)
|
|-- .firebaserc                    # Firebase project binding: kjtcom-c78cd
|-- firebase.json                  # Firestore, Hosting, Functions config
|-- firestore.rules                # Security rules (public read, no client write)
|-- firestore.indexes.json         # 8 composite indexes
|-- CLAUDE.md                      # Agent instructions (Claude Code)
|-- GEMINI.md                      # Agent instructions (Gemini CLI)
|-- README.md                      # Project overview (479 lines)
+-- .gitignore                     # Pipeline data, node_modules, build excluded
```

---

## 3. Tech Stack

| Layer | Technology | Version/Details |
|-------|-----------|-----------------|
| **Frontend** | Flutter Web (Dart) | SDK ^3.11.4, CanvasKit renderer |
| **State Management** | Riverpod | ^2.6.1 (flutter_riverpod) |
| **Database** | Cloud Firestore | Blaze plan, NoSQL document store |
| **Hosting** | Firebase Hosting | CDN, kylejeromethompson.com |
| **Cloud Functions** | TypeScript / Node 20 | firebase-functions, firebase-admin |
| **Maps** | flutter_map + OSM | ^7.0.2, latlong2 ^0.9.1 |
| **Fonts** | Google Fonts | ^6.2.1 (Geist Sans/Mono, Cinzel) |
| **Transcription** | faster-whisper | CUDA-accelerated, Python |
| **Extraction** | Gemini 2.5 Flash | Google AI API |
| **Geocoding** | Nominatim | OpenStreetMap, free tier |
| **Enrichment** | Google Places API | Coordinates, ratings, metadata |
| **Audio Download** | yt-dlp | YouTube audio extraction |
| **Pipeline Scripts** | Python 3.14 | 7-phase pipeline |
| **Orchestration** | Claude Code (Opus) | Phases 6-9, Flutter/app work |
| **Orchestration** | Gemini CLI | Phases 1-5, pipeline/mechanical work |
| **OS** | CachyOS (Arch) | Linux 6.19.10-1-cachyos |
| **Hardware** | NZXTcos | i9-13900K, 64 GB RAM, RTX 2080 SUPER |

**Dependencies (pubspec.yaml):**

```yaml
dependencies:
  firebase_core: ^3.13.0
  cloud_firestore: ^5.6.0
  flutter_riverpod: ^2.6.1
  google_fonts: ^6.2.1
  flutter_map: ^7.0.2
  latlong2: ^0.9.1

dev_dependencies:
  flutter_test: sdk
  flutter_lints: ^6.0.0
```

---

## 4. Flutter App Architecture

### Entry Point

`app/lib/main.dart` - Initializes Firebase, wraps app in Riverpod `ProviderScope`, mounts `AppShell`.

### Layout

Single-page application with tab-based navigation. No router - all navigation via `activeTabProvider` (Riverpod StateProvider).

```
AppShell (Scaffold)
  +-- Stack
  |   +-- GlobeHero (background image, 15% opacity)
  |   +-- Column
  |       +-- Header ("kjtcom" logo, "Investigate" badge)
  |       +-- QueryEditor (syntax-highlighted multi-line input)
  |       +-- KjtcomTabBar (6 tabs)
  |       +-- EntityCountRow (animated count)
  |       +-- TabContent (switches on activeTab)
  |           +-- 0: ResultsTable + DetailPanel (side-by-side desktop, overlay mobile)
  |           +-- 1: MapTab + DetailPanel
  |           +-- 2: GlobeTab + DetailPanel
  |           +-- 3: IaoTab
  |           +-- 4: GotchaTab
  |           +-- 5: SchemaTab
```

### Responsive Breakpoints

| Breakpoint | Width | Behavior |
|-----------|-------|----------|
| Mobile | 375px | Single column, overlay detail panel |
| Tablet | 768px | Partial columns hidden |
| Desktop | 1024px | Side-by-side results + detail panel |
| Wide | 1440px | Max content width |

---

## 5. Data Models

### LocationEntity (`app/lib/models/location_entity.dart`, 74 lines)

Represents a single Firestore document from the `locations` collection.

```dart
class LocationEntity {
  final String id;        // Firestore document ID
  final String logType;   // Pipeline source (t_log_type)
  final Map<String, dynamic> raw;  // Complete Firestore document

  // Computed properties:
  String get name         // First from t_any_names, fallback to id
  String get city         // First from t_any_cities
  String get country      // First from t_any_countries
  List<String> get countryCodes  // From t_any_country_codes
  (double, double)? get coordinates  // Parsed from t_any_coordinates
  List<String> get continents  // From t_any_continents
  String get show         // First from t_any_shows
  Map<String, dynamic> get displayFields  // Filtered t_any_* + t_enrichment.*
}
```

### QueryClause (`app/lib/models/query_clause.dart`, 131 lines)

Represents a parsed query clause with field, operator, and value.

```dart
class QueryClause {
  final String field;          // e.g. "t_any_cuisines"
  final String operator;       // contains | contains-any | == | !=
  final String value;          // Single value string
  final List<String> values;   // For contains-any: parsed list

  static const knownFields = { ... };  // 22 fields
  static QueryClause? parse(String line);
  static List<QueryClause> parseAll(String queryText);
}
```

**Parse priority order:**
1. `contains-any` regex (different value syntax)
2. Quoted value regex: `field operator "value"`
3. Unquoted fallback regex: `field operator value-to-EOL`

**Supported syntax:**

```
| where t_any_cuisines contains "french"
t_any_keywords contains geology
t_log_type == "calgold"
t_any_countries != "us"
t_any_cities contains-any ["paris", "london", "rome"]
t_any_actors contains-any gordon ramsay, anthony bourdain
```

---

## 6. Query System (Deep Dive)

### Query Flow

```
User types in QueryEditor
    -> _onTextChanged() triggers autocomplete detection
    -> _onSearch() fires on Enter/button click
    -> queryProvider updated with text
    -> queryResultProvider watches queryProvider
    -> QueryClause.parseAll() tokenizes text into clauses
    -> Firestore compound query built (server-side)
    -> Client-side filtering for overflow array ops
    -> Stream<QueryResult> emits to UI
    -> ResultsTable renders paginated results
    -> Click row -> selectedEntityProvider -> DetailPanel
```

### Operators

| Operator | Syntax | Firestore Mapping | Use Case |
|----------|--------|-------------------|----------|
| `contains` | `field contains "val"` | `arrayContains` (1st), client-side (2nd+) | Single value in array field |
| `contains-any` | `field contains-any ["v1","v2"]` | `arrayContainsAny` (max 30, 1st only) | Multiple values, OR logic |
| `==` | `field == "val"` | `isEqualTo` (scalar), client-side (array) | Exact match |
| `!=` | `field != "val"` | `isNotEqualTo` (scalar), client-side (array) | Exclusion |

### Firestore Query Constraints

- **Single array operation limit:** Firestore allows only ONE `arrayContains` or `arrayContainsAny` per compound query. The first array operation goes server-side; all subsequent array operations are applied client-side via `.where()` filtering on the returned snapshot.
- **arrayContainsAny cap:** Maximum 30 values per Firestore call.
- **Scalar operations:** `==` and `!=` on non-`t_any_*` fields (e.g., `t_log_type`) go server-side via `isEqualTo`/`isNotEqualTo`.
- **Case normalization:** All values lowercased before comparison, both server-side and client-side.

### Firestore Provider Logic (`app/lib/providers/firestore_provider.dart`, 109 lines)

```dart
// Simplified logic:
for (clause in clauses) {
  if (clause.operator == 'contains-any' && !usedArrayOp) {
    query = query.where(field, arrayContainsAny: lowered.take(30));
    usedArrayOp = true;
  } else if (clause.operator == 'contains' && !usedArrayOp) {
    query = query.where(field, arrayContains: value.toLowerCase());
    usedArrayOp = true;
  } else if (clause.operator == '==' && !field.startsWith('t_any_')) {
    query = query.where(field, isEqualTo: value.toLowerCase());
  } else if (clause.operator == '!=' && !field.startsWith('t_any_')) {
    query = query.where(field, isNotEqualTo: value.toLowerCase());
  } else {
    clientSideClauses.add(clause);  // overflow -> client-side
  }
}
```

### Autocomplete System

**Two modes:**
1. **Field mode:** Cursor is on a token starting with `t_` - suggests from 22 `knownFields`
2. **Value mode:** Cursor is after `field operator` - suggests from `value_index.json` (6,878 values across 21 fields)

**Value index** (`app/assets/value_index.json`): Pre-computed mapping of field names to all distinct lowercase values across the entire Firestore dataset. Generated by `pipeline/scripts/generate_value_index.py`.

**Autocomplete UX:**
- Max 5 suggestions displayed inline (Panther SIEM-style, not overlay)
- Tab/Enter accepts suggestion
- Arrow Up/Down navigates
- Escape dismisses
- Field acceptance appends ` contains ` suffix automatically

### Syntax Highlighting

Regex-based tokenizer in `query_editor.dart`:
- **Red:** Pipe operators (`|`, `where`)
- **Purple:** Keywords/operators (`contains`, `contains-any`, `==`, `!=`)
- **Cyan/Blue:** Field names (`t_any_*`, `t_log_type`)
- **Light blue:** Values (quoted strings)
- **Green:** Collection names (`locations`)

### +filter / -exclude Buttons (Detail Panel)

When viewing an entity's fields:
- **+filter:** Appends `| where field contains "value"` for array fields, `| where field == "value"` for scalars
- **-exclude:** Appends `| where field != "value"` for all fields
- Both use `programmaticUpdateProvider` flag to prevent cursor override during text update

### Known Query Hangups (Current State)

1. **Parser regression history (v9.32-v9.33):** Unquoted value regex previously broke quoted parsing. Fixed in v9.33 - quoted regex now runs first, unquoted is fallback.
2. **Cursor placement (G45):** Six Claude Code attempts to fix cursor position between quotes after schema builder appends `""`. Finally resolved in v9.34 using `WidgetsBinding.instance.addPostFrameCallback`.
3. **Single array op limit:** Multi-clause queries with 2+ array fields require client-side filtering, which means ALL matching documents for the first clause are fetched before filtering. Performance concern at scale.
4. **No full-text search:** All queries rely on exact array membership. No fuzzy matching, no substring search, no relevance scoring.
5. **No query history or saved queries.**
6. **Autocomplete loads full index on startup** (169 KB JSON asset).

---

## 7. State Management (Riverpod Providers)

| Provider | Type | File | Purpose |
|----------|------|------|---------|
| `queryTextControllerProvider` | `Provider<TextEditingController>` | query_provider.dart | Shared text controller across editor, schema builder, detail panel |
| `queryProvider` | `NotifierProvider<QueryNotifier, String>` | query_provider.dart | Current query text state |
| `programmaticUpdateProvider` | `StateProvider<bool>` | query_provider.dart | Flag to prevent cursor override during programmatic text updates |
| `queryResultProvider` | `StreamProvider<QueryResult>` | firestore_provider.dart | Main Firestore query executor, streams results |
| `resultsProvider` | `StreamProvider<List<LocationEntity>>` | firestore_provider.dart | Backward-compatible entity list wrapper |
| `countryCountProvider` | `Provider<int>` | firestore_provider.dart | Distinct country count from results |
| `selectedEntityProvider` | `StateProvider<LocationEntity?>` | selection_provider.dart | Currently selected entity for detail panel |
| `activeTabProvider` | `StateProvider<int>` | tab_provider.dart | Active tab index (0-5) |
| `pageSizeProvider` | `StateProvider<int>` | pagination_provider.dart | Page size: 20, 50, or 100 |
| `currentPageProvider` | `StateProvider<int>` | pagination_provider.dart | Current page (0-based) |
| `valueIndexProvider` | `FutureProvider<Map<String, List<String>>>` | query_autocomplete.dart | Autocomplete value index loaded from JSON asset |

### Programmatic Update Pattern

Critical pattern for cursor management when code (not the user) updates the query text:

```
1. Set programmaticUpdateProvider = true
2. Update controller.text
3. Use WidgetsBinding.instance.addPostFrameCallback to set controller.selection
4. Sync queryProvider
5. Clear flag via Future.microtask()
6. ref.listen in query_editor checks flag - returns early if true (prevents cursor reset)
```

---

## 8. Widget Inventory

| Widget | File | Lines | Purpose |
|--------|------|-------|---------|
| AppShell | app_shell.dart | ~200 | Root layout, header, tab routing, responsive breakpoints |
| QueryEditor | query_editor.dart | 573 | Syntax-highlighted multi-line query input with inline autocomplete |
| QueryAutocomplete | query_autocomplete.dart | 94 | Autocomplete context detection and value index provider |
| ResultsTable | results_table.dart | ~200 | Paginated results with pipeline dots, responsive columns |
| DetailPanel | detail_panel.dart | ~300 | Entity field cards, +filter/-exclude, copy JSON, slide animation |
| EntityCountRow | entity_count_row.dart | ~80 | Animated entity/country count display |
| KjtcomTabBar | kjtcom_tab_bar.dart | ~60 | 6-tab navigation bar |
| MapTab | map_tab.dart | ~100 | OpenStreetMap with pipeline-colored markers |
| GlobeTab | globe_tab.dart | ~250 | Continent cards, country grid, pipeline distribution |
| IaoTab | iao_tab.dart | ~300 | Trident graphic, 10 IAO pillar cards, stats footer |
| GotchaTab | gotcha_tab.dart | ~350 | 44 failure patterns with status badges and filter toggle |
| SchemaTab | schema_tab.dart | 340 | 22 Thompson fields with "+ Add to query" buttons |
| GlobeHero | globe_hero.dart | ~40 | Background image (globe_hero.jpg at 15% opacity) |
| PipelineBadge | pipeline_badge.dart | ~30 | Pipeline color chip (CG/RS/TD/NR) |

---

## 9. Theme and Design System

### Visual Identity

Gothic/cyberpunk aesthetic with SIEM-inspired information density.

### Color Tokens (`app/lib/theme/tokens.dart`)

| Token | Hex | Use |
|-------|-----|-----|
| surfaceBase | #0D1117 | App background |
| surfaceElevated | #161B22 | Cards, panels |
| surfaceOverlay | #1B2838 | Overlays, popups |
| accentGreen | #4ADE80 | Primary accent, counts, borders |
| accentBlue | #58A6FF | Secondary accent, links |
| accentOrange | #FFA657 | Warnings, numbers |
| accentRed | #FF7B72 | Errors, exclude buttons |
| syntaxField | (cyan) | Query field names |
| syntaxOperator | (purple) | Query operators |
| syntaxValue | (light blue) | Query values |

### Pipeline Colors

| Pipeline | Color | Badge |
|----------|-------|-------|
| CalGold | #DA7E12 (gold) | CG |
| RickSteves | #3B82F6 (blue) | RS |
| TripleDB | #DD3333 (red) | TD |
| Bourdain | #8B5CF6 (purple) | NR |

### Typography

| Font | Use |
|------|-----|
| Cinzel | Headers, gothic elements |
| GeistSans | Body text, UI labels |
| GeistMono | Code, field names, query editor |

### Layout Constants

- Max width: 1440px
- Sidebar (detail panel): 320px
- Line number column: 20px
- Spacing scale: 4px increments (space1 through space8)
- Border radius: 3px (sm) through 12px (2xl)
- Animation: 200ms detail slide, 150ms row highlight, 600ms count-up

---

## 10. Database Structure (Firestore)

### Project

- **Project ID:** kjtcom-c78cd
- **Plan:** Blaze (pay-as-you-go)
- **Cost:** ~$0.50/month (6,181 documents)

### Collections

| Collection | Documents | Purpose |
|-----------|-----------|---------|
| `locations` | 6,181 | Primary entity store (queried by app) |
| `pipelines` | ~3 | Pipeline metadata |
| `videos` | ~2,255 | Video processing state |

### Security Rules

```
locations/{docId}: read = true, write = false
pipelines/{docId}: read = true, write = false
videos/{docId}: read = true, write = false
```

All writes go through Admin SDK (pipeline scripts). No client-side writes.

### Composite Indexes (8 total)

| # | Fields | Purpose |
|---|--------|---------|
| 1 | t_log_type ASC + t_enrichment.google_places.rating DESC | Pipeline + rating sort |
| 2 | t_log_type ASC + t_any_states CONTAINS + rating DESC | Pipeline + state filter + rating |
| 3 | t_any_geohashes CONTAINS + t_log_type ASC | Geohash proximity + pipeline |
| 4 | t_any_geohashes CONTAINS + still_open ASC | Geohash + open status |
| 5 | t_any_countries CONTAINS + t_log_type ASC | Country + pipeline |
| 6 | t_any_countries CONTAINS + rating DESC | Country + rating sort |
| 7 | t_any_regions CONTAINS + t_log_type ASC | Region + pipeline |
| 8 | t_log_type ASC + t_any_countries CONTAINS | Pipeline + country (reversed) |

### Document Schema (locations collection)

```json
{
  "t_log_type": "calgold",
  "t_row_id": "calgold-abc123",
  "t_event_time": "2024-...",
  "t_parse_time": "2025-...",
  "t_source_label": "California's Gold",
  "t_schema_version": "v3",

  "t_any_names": ["Griffith Observatory"],
  "t_any_people": ["huell howser"],
  "t_any_cities": ["los angeles"],
  "t_any_states": ["ca"],
  "t_any_counties": ["los angeles county"],
  "t_any_countries": ["us"],
  "t_any_country_codes": ["US"],
  "t_any_regions": ["southern california"],
  "t_any_keywords": ["observatory", "astronomy", "griffith park"],
  "t_any_categories": ["science", "landmark"],
  "t_any_actors": ["huell howser"],
  "t_any_roles": ["host"],
  "t_any_shows": ["california's gold"],
  "t_any_cuisines": [],
  "t_any_dishes": [],
  "t_any_eras": ["1990s"],
  "t_any_continents": ["north america"],
  "t_any_urls": ["https://youtube.com/watch?v=..."],
  "t_any_video_ids": ["abc123"],
  "t_any_coordinates": [{"lat": 34.1184, "lon": -118.3004}],
  "t_any_geohashes": ["9q5c"],

  "t_enrichment": {
    "google_places": {
      "rating": 4.7,
      "still_open": true,
      "place_id": "ChIJ...",
      "formatted_address": "...",
      "types": ["tourist_attraction", "museum"],
      ...
    }
  }
}
```

---

## 11. Thompson Indicator Fields Schema

22 universal fields applied across all pipelines. Named with `t_any_` prefix to indicate cross-pipeline applicability.

| # | Field | Type | Queryable | Description |
|---|-------|------|-----------|-------------|
| 1 | t_log_type | string | == / != | Pipeline discriminator (calgold, ricksteves, tripledb) |
| 2 | t_any_names | array[string] | contains | Entity/location names |
| 3 | t_any_people | array[string] | contains | People mentioned |
| 4 | t_any_cities | array[string] | contains | City names |
| 5 | t_any_states | array[string] | contains | State/province codes |
| 6 | t_any_counties | array[string] | contains | County names |
| 7 | t_any_countries | array[string] | contains | Country names |
| 8 | t_any_country_codes | array[string] | contains | ISO 3166-1 alpha-2 codes |
| 9 | t_any_regions | array[string] | contains | Sub-country regions |
| 10 | t_any_keywords | array[string] | contains | Searchable terms |
| 11 | t_any_categories | array[string] | contains | Category tags |
| 12 | t_any_actors | array[string] | contains | Featured people |
| 13 | t_any_roles | array[string] | contains | Role types (host, chef, etc.) |
| 14 | t_any_shows | array[string] | contains | Show/series names |
| 15 | t_any_cuisines | array[string] | contains | Cuisine types |
| 16 | t_any_dishes | array[string] | contains | Food/dish items |
| 17 | t_any_eras | array[string] | contains | Historical periods |
| 18 | t_any_continents | array[string] | contains | Continent names |
| 19 | t_any_urls | array[string] | contains | Source URLs |
| 20 | t_any_video_ids | array[string] | contains | YouTube video IDs |
| 21 | t_any_coordinates | array[map] | view-only | Lat/lon pairs |
| 22 | t_any_geohashes | array[string] | view-only | Geohash prefixes for proximity |

**Schema versioning:** Current is v3. Migration from v1/v2 added actors, roles, shows, cuisines, dishes, eras, continents in v4.12/v4.13. All 6,181 entities at v3 since v8.22.

---

## 12. Data Pipeline

### 7-Phase Architecture

```
Phase 1: Acquire    -> yt-dlp downloads audio (MP3) from YouTube
Phase 2: Transcribe -> faster-whisper (CUDA) produces JSON transcripts
Phase 3: Extract    -> Gemini 2.5 Flash extracts structured entities
Phase 4: Normalize  -> Python maps to Thompson Indicator Fields
Phase 5: Geocode    -> Nominatim + Google Places coordinate lookup
Phase 6: Enrich     -> Google Places API (ratings, types, addresses)
Phase 7: Load       -> Admin SDK writes to Firestore (dedup via t_row_id)
```

### Pipeline Configs

Each pipeline has 4 config files in `pipeline/config/{name}/`:

| File | Purpose |
|------|---------|
| `pipeline.json` | Display name, entity type, pipeline color |
| `schema.json` | Thompson field extraction mappings |
| `extraction_prompt.md` | Gemini Flash system prompt (customized per content type) |
| `playlist_urls.txt` | YouTube video IDs to process |

### Live Pipelines

| Pipeline | Videos | Entities | Content | Status |
|----------|--------|----------|---------|--------|
| CalGold | 390 | 899 | California's Gold (Huell Howser) | Phase 7 DONE |
| RickSteves | 1,865 | 4,182 | Rick Steves' Europe | Phase 7 DONE |
| TripleDB | 805 | 1,100 | TripleDB restaurants (migrated) | Phase 7 DONE |
| Bourdain | 104 | - | Anthony Bourdain (pending) | Not started |

### Key Pipeline Scripts

| Script | Purpose |
|--------|---------|
| `phase1_acquire.py` | yt-dlp audio download with checkpoint recovery |
| `phase2_transcribe.py` | faster-whisper CUDA transcription with timeout handling |
| `phase3_extract.py` | Gemini 2.5 Flash structured extraction |
| `phase4_normalize.py` | Thompson field mapping + continent lookup |
| `phase5_geocode.py` | Nominatim + county parsing |
| `phase6_enrich.py` | Google Places API enrichment |
| `phase7_load.py` | Firestore Admin SDK with dedup (t_row_id) |
| `generate_value_index.py` | Builds value_index.json for autocomplete |
| `backfill_country_codes.py` | ISO 3166-1 alpha-2 backfill |
| `fix_lowercase_all.py` | Lowercase all t_any_* values |
| `group_b_runner.sh` | Unattended tmux execution |

### Data Volumes

| Pipeline | Audio | Transcripts | Extracted | Total |
|----------|-------|-------------|-----------|-------|
| CalGold | ~3 GB | ~500 MB | ~200 MB | ~5.5 GB |
| RickSteves | ~4 GB | ~700 MB | ~300 MB | ~6.3 GB |
| **Total** | | | | **~11.8 GB** |

---

## 13. Cloud Functions

### Search Endpoint (`functions/src/index.ts`, 116 lines)

Simple array-contains search function. Phase 0 implementation - largely superseded by client-side Firestore queries in the Flutter app.

```typescript
// Node 20, firebase-admin, firebase-functions
// Single endpoint: basic array-contains search on locations collection
```

**Dependencies:** firebase-admin, firebase-functions, TypeScript 5

---

## 14. Infrastructure and Deployment

### Firebase Configuration

| File | Purpose |
|------|---------|
| `.firebaserc` | Project: kjtcom-c78cd |
| `firebase.json` | Rules, hosting (app/build/web), functions source |
| `firestore.rules` | Public read, admin-only write |
| `firestore.indexes.json` | 8 composite indexes |

### Build and Deploy Commands

```fish
# Build Flutter web
cd app && flutter build web

# Deploy to Firebase Hosting
cd ~/dev/projects/kjtcom && firebase deploy --only hosting

# Deploy Cloud Functions
firebase deploy --only functions

# Run analysis
cd app && flutter analyze

# Run tests
cd app && flutter test
```

### Environments

| Environment | Database | Purpose |
|-------------|----------|---------|
| Production (default) | kjtcom-c78cd (default) | Live app at kylejeromethompson.com |
| Staging | kjtcom-c78cd (staging) | Development/testing |

### CI/CD

No automated CI/CD pipeline. Manual deployment via `firebase deploy`. Agent-orchestrated builds verified with `flutter analyze` + `flutter test` before deploy.

---

## 15. Test Coverage

### Widget Tests (`app/test/widget_test.dart`)

15 test cases covering:

| Area | Tests | Coverage |
|------|-------|----------|
| Query parsing | Quoted values, unquoted values, contains-any, operators | Regression tests for v9.32 parser fix |
| Field validation | Known fields, unknown fields | 22 field set |
| Firestore queries | array-contains, compound queries | Provider logic |
| Pagination | Page size, navigation | State management |
| Result rendering | Entity cards, detail panel | Widget rendering |
| Tab switching | Tab navigation | UI flow |

**Run command:** `cd app && flutter test`

**Analysis:** `cd app && flutter analyze` (0 issues as of v9.34)

---

## 16. Gotcha Registry

44 documented failure patterns (G1-G50, some numbers skipped). Maintained in `gotcha_tab.dart` and design/report docs.

### Active Gotchas (Selected)

| ID | Title | Status |
|----|-------|--------|
| G1 | Fish shell has no heredocs | ACTIVE |
| G11 | API key leaks when catting config files | ACTIVE |
| G20 | Never cat SA JSON files | ACTIVE |
| G34 | Firestore single-arrayContains limit | DOCUMENTED |
| G47 | CanvasKit blocks Playwright DOM interaction | DOCUMENTED |

### Recently Resolved

| ID | Title | Resolved In |
|----|-------|-------------|
| G2 | CUDA LD_LIBRARY_PATH | v3.10 |
| G36 | Case sensitivity in array queries | v9.32 |
| G37 | TripleDB shows not lowercased | v9.32 |
| G42 | Rotating queries overwrite user input | v8.26 |
| G44 | flutter_map version compatibility | v9.27 |
| G45 | Quote cursor placement (6 attempts) | v9.34 |
| G46 | 1000-result Firestore limit | v9.31 |
| G49 | TripleDB t_any_shows capitalization | v9.32 |

---

## 17. Version History and Changelog

### Phase Summary

| Phase | Versions | Description | Status |
|-------|----------|-------------|--------|
| 0 | v0.5 | Scaffold, Firebase, Thompson Schema, pipeline config | DONE |
| 1 | v1.6-v1.7 | Discovery (CalGold + RickSteves, 30 videos each) | DONE |
| 2 | v2.8-v2.9 | Calibration (60-90 videos, schema v2, dedup) | DONE |
| 3 | v3.10-v3.11 | Stress test (90-120 videos, split-agent model) | DONE |
| 4 | v4.12-v4.13 | Validation (schema v3, 7 new fields, 150 videos) | DONE |
| 5 | v5.14 | Production run (390 CalGold, full pipeline) | DONE |
| 6 | v6.15-v6.20 | Flutter app (discovery, design, implementation, QA, deploy) | DONE |
| 7 | v7.21 | Firestore load (TripleDB migration, 6,181 total) | DONE |
| 8 | v8.22-v8.26 | Enrichment hardening (12 defects, query remediation) | DONE |
| 9 | v9.27-v9.34 | App optimization (tabs, autocomplete, operators, cursor) | IN PROGRESS |
| 10 | - | Retrospective + template | PENDING |

### Recent Iteration Summary (Phase 9)

| Version | Focus | Key Changes |
|---------|-------|-------------|
| v9.27 | Visual refresh + tabs | Gothic theme, Map/Globe/IAO tabs, pagination, flutter_map |
| v9.28 | Gotcha + Schema tabs | 25 gotchas, 22 schema fields, copy JSON, query builder |
| v9.29 | UX polish | Removed 1000-result limit, trident labels, schema quotes |
| v9.30 | Autocomplete | Field/value autocomplete, value_index.json, Tab acceptance |
| v9.31 | Bug fixes | Limit verified, cursor hardened, autocomplete value-mode fix, clear button |
| v9.32 | Shows fix + operators | Lowercase all data, != operator, alphabetical detail fields, unquoted values |
| v9.33 | Parser regression | Quoted regex first (fix regression), quotes in schema builder, filter/exclude operators |
| v9.34 | Cursor + inline AC | addPostFrameCallback cursor fix (G45), Panther-style inline autocomplete, operator fixes |

### Full Changelog

See `docs/kjtcom-changelog.md` for complete iteration-by-iteration details (344 lines).

### Git History (Last 20 Commits)

```
5dd8ce2 KT completed 9.34 and updated README
e3e8f18 KT completed 9.33 and updated README
3c4c131 KT completed 9.32 and updated README
e34304a KT completed 9.31 and updated README
15b01c4 KT completed 9.30 and updated README
2030a07 KT completed 9.29 and updated README
b0da0ac KT completed 9.27 and updated README
a16160c KT completed 9.27 and updated README
efbf2d9 KT completed 8.26 and updated README
9c997e3 KT completed 8.25 and updated README
34f9e22 KT completed 8.24 and updated README
fe1d5a6 KT completed 8.23 and updated README
c81343d KT completed 8.22 and updated README
24412c9 KT updated README
4b8cc7f KT completed 7.21 and updated README
a476625 KT completed 5.15 phase B
ae05335 KT repo cleanup
1a99abd KT completed 6.20 and updated README
2c16ecd KT completed 6.19 and updated README
e585bc9 KT completed 6.17 and updated README
```

---

## 18. Current Progress and Hangups

### Status: Phase 9 - App Optimization (IN PROGRESS, v9.34)

**Completed in Phase 9 (v9.27-v9.34):**
- 6-tab layout (Results, Map, Globe, IAO, Gotcha, Schema)
- Gothic/cyberpunk visual refresh
- OpenStreetMap integration with pipeline-colored markers
- Globe stats dashboard (continents, countries, pipeline distribution)
- IAO methodology display (trident, 10 pillars)
- Gotcha registry (44 patterns)
- Schema documentation (22 fields) with query builder
- Field/value autocomplete (6,878 values)
- Inline Panther-style suggestions (replaced overlay)
- contains-any operator
- != operator
- +filter/-exclude from detail panel
- Pagination (20/50/100)
- Copy JSON
- Clear button
- Cursor placement fix (G45 - 7 attempts across v9.29-v9.34)
- Parser regression fix (v9.33)
- Case sensitivity permanently resolved (v9.32)

### Active Hangups and Limitations

**Query System Limitations:**
1. **No full-text search** - Only exact array membership. Cannot search for substrings, fuzzy matches, or relevance-ranked results. "geology" must be an exact value in the array, not a substring of a longer term.
2. **Single server-side array op** - Firestore G34 limitation means compound array queries fetch all docs for the first clause, then filter client-side. At 6,181 entities this is tolerable but won't scale.
3. **No query optimization** - No query plan analysis, no index suggestions, no query cost estimation.
4. **No saved queries or history** - Users cannot save or recall queries.
5. **No boolean logic** - No OR between clauses (all clauses are AND). No grouping with parentheses.
6. **No sorting** - Results come in Firestore document order. No user-selectable sort.
7. **No aggregations** - No count-by, group-by, or statistical queries.
8. **Autocomplete is static** - value_index.json is generated offline, not updated with new data.

**Technical Debt:**
1. **Riverpod 2.x** - StateProvider deprecated in Riverpod 3. Migration deferred (W5 from v9.33) due to >50 lines across 13 files.
2. **CanvasKit DOM limitation** - Playwright cannot interact with CanvasKit-rendered Flutter (G47). Automated UI testing blocked.
3. **Cloud Functions underutilized** - The search endpoint (Phase 0) is superseded by client-side queries but still deployed.
4. **No error boundaries** - No graceful degradation if Firestore connection drops.

**Agent Orchestration Notes:**
- Claude Code (Opus) handles Flutter/app work (Phases 6-9)
- Gemini CLI handles pipeline/mechanical work (Phases 1-5)
- v9.34 was a Gemini CLI iteration that resolved the G45 cursor issue after 6 Claude Code failures
- Split-agent model proven effective across 34 iterations

---

## 19. Future Directions

### Near-Term (Phase 9 continuation / Phase 10)

1. **Query improvements** - The primary focus area. Options being evaluated:
   - PantherFlow-style query language (scrape Panther SIEM for syntax reference)
   - Full-text search via Algolia or Typesense (deferred from v8.22)
   - Query history and saved queries
   - Boolean OR logic and grouping

2. **Qwen 3.6-plus / Meta HyperAgents** - Next-gen model integration for extraction quality benchmarking and agent orchestration improvements.

3. **MCP integration** - Browser scraping MCP for Panther session examination (requires manual MFA login, process ID handoff).

4. **Bourdain pipeline onboarding** - 104 videos ready, config files pending.

5. **Riverpod 3 migration** - StateProvider -> other provider types across 13 files.

### Medium-Term

- Multi-LLM extraction benchmarking (Gemini vs GPT vs Claude vs Qwen on same content)
- SIEM migration tooling (cross-pollination from TachTech work)
- Search optimization at scale (Algolia/Typesense if entity count grows significantly)
- Phase 10: Retrospective + reusable template

---

## 20. File Index

### Dart Source Files (25 files)

| File | Path | Lines | Purpose |
|------|------|-------|---------|
| main.dart | app/lib/ | ~20 | Entry point, Firebase init |
| firebase_options.dart | app/lib/ | ~60 | Firebase web config |
| location_entity.dart | app/lib/models/ | 74 | Firestore document model |
| query_clause.dart | app/lib/models/ | 131 | Query parser |
| query_provider.dart | app/lib/providers/ | 25 | Query state + controller |
| firestore_provider.dart | app/lib/providers/ | 109 | Firestore query executor |
| selection_provider.dart | app/lib/providers/ | 5 | Selected entity state |
| tab_provider.dart | app/lib/providers/ | 4 | Active tab state |
| pagination_provider.dart | app/lib/providers/ | 12 | Page size + page index |
| theme.dart | app/lib/theme/ | ~50 | Material theme builder |
| tokens.dart | app/lib/theme/ | ~120 | Design system constants |
| app_shell.dart | app/lib/widgets/ | ~200 | Root layout |
| query_editor.dart | app/lib/widgets/ | 573 | Query input + highlighting |
| query_autocomplete.dart | app/lib/widgets/ | 94 | Autocomplete detection |
| results_table.dart | app/lib/widgets/ | ~200 | Paginated results |
| detail_panel.dart | app/lib/widgets/ | ~300 | Entity detail panel |
| entity_count_row.dart | app/lib/widgets/ | ~80 | Animated counter |
| kjtcom_tab_bar.dart | app/lib/widgets/ | ~60 | Tab navigation |
| map_tab.dart | app/lib/widgets/ | ~100 | OpenStreetMap view |
| globe_tab.dart | app/lib/widgets/ | ~250 | Stats dashboard |
| iao_tab.dart | app/lib/widgets/ | ~300 | IAO methodology |
| gotcha_tab.dart | app/lib/widgets/ | ~350 | Failure registry |
| schema_tab.dart | app/lib/widgets/ | 340 | Schema documentation |
| globe_hero.dart | app/lib/widgets/ | ~40 | Background image |
| pipeline_badge.dart | app/lib/widgets/ | ~30 | Pipeline chip |

### Configuration Files

| File | Purpose |
|------|---------|
| app/pubspec.yaml | Flutter dependencies |
| app/analysis_options.yaml | Dart linter rules |
| functions/package.json | Cloud Functions dependencies |
| functions/tsconfig.json | TypeScript config |
| .firebaserc | Firebase project binding |
| firebase.json | Firebase service config |
| firestore.rules | Firestore security rules |
| firestore.indexes.json | Composite indexes |
| CLAUDE.md | Claude Code agent instructions |
| GEMINI.md | Gemini CLI agent instructions |

### Documentation (Active)

| File | Purpose |
|------|---------|
| docs/kjtcom-design-v9.34.md | Current design contract |
| docs/kjtcom-plan-v9.34.md | Current execution plan |
| docs/kjtcom-build-v9.34.md | Current build log |
| docs/kjtcom-report-v9.34.md | Current metrics report |
| docs/kjtcom-changelog.md | Master changelog |
| README.md | Project overview |

### Documentation (Archive: 128 files in docs/archive/)

Historical artifacts from v0.5 through v9.33 including design docs, plans, build logs, reports, screenshots, migration docs, and tmux runner logs.

---

*Report generated from local repository state at commit 5dd8ce2 on branch main.*
