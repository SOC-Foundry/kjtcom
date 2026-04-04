# kjtcom - Build Log v8.22 (Phase 8 - Enrichment Hardening + Query Assessment)

**Pipeline:** kjtcom
**Phase:** 8 (Enrichment Hardening)
**Iteration:** 22 (global counter)
**Executor:** Claude Code (Opus 4.6)
**Machine:** NZXTcos
**Date:** 2026-04-03

---

## Pre-Flight State

```
=== PRODUCTION STATE (pre-v8.22) ===
CalGold: 899
RickSteves: 4182
TripleDB: 1100
Total: 6181
Schema v1: 0, v2: 323, v3: 5858
Non-v3: 323 (target for backfill)
TripleDB no enrichment: 405
TripleDB no coords: 96
TripleDB no city: 121
```

SA credentials: SET. GOOGLE_PLACES_API_KEY: SET.

---

## Workstream A: Enrichment Hardening

### Step 1: Schema v3 Backfill Script

Created `pipeline/scripts/backfill_schema_v3.py`:
- Queries all entities with `t_schema_version < 3`
- Applies per-pipeline backfill rules:
  - CalGold: `t_any_actors: ["huell howser"]`, `t_any_roles: ["host"]`, `t_any_continents: ["north america"]`
  - RickSteves: `t_any_actors: ["rick steves"]`, `t_any_roles: ["host"]`, `t_any_continents` derived from `t_any_countries` via COUNTRY_TO_CONTINENT lookup
- Flags: `--dry-run`, `--limit N`
- Batch writes (all 323 in one batch)

### Step 2: Schema v3 Dry Run

```
Querying for non-v3 entities...
Found 323 non-v3 entities
Limited to 5 entities

[DRY RUN] calgold-29-palms-murals-99ab69 (calgold):
  t_any_actors: ['huell howser']
  t_any_continents: ['north america']
  t_any_cuisines: []
  t_any_dishes: []
  t_any_eras: []
  t_any_roles: ['host']
  t_schema_version: 3
```

CalGold entities already had `t_any_shows` populated from v5.14 - backfill correctly skips pre-existing fields.

### Step 3: Schema v3 Full Run

```
Found 323 non-v3 entities
Committed final batch of 323

=== SUMMARY ===
CalGold updated: 121
RickSteves updated: 202
Skipped: 0
Total processed: 323
```

Post-backfill verification: `Non-v3 remaining: 0`

### Step 4: TripleDB Enrichment Backfill Script

Created `pipeline/scripts/backfill_tripledb_enrichment.py`:
- Reads TripleDB entities where `t_enrichment.google_places` is null/empty
- Builds query from `t_any_names[0] + t_any_cities[0] + t_any_states[0]` (source.name was empty for TripleDB entities - data lives in t_any_* fields)
- Google Places text search via Places API (New)
- Enrichment fields: place_id, rating, current_name, still_open, website, phone, total_ratings, enriched_at
- Coordinate backfill from Places response when `t_any_coordinates` is missing
- City backfill via Nominatim reverse geocode when `t_any_cities` is missing
- Rate limit: 1 req/sec (Google Places), 1 req/sec (Nominatim)
- Max 3 retries per entity
- Flags: `--dry-run`, `--limit N`

### Step 5: TripleDB Enrichment Dry Run

```
Found 405 unenriched TripleDB entities
Limited to 5 entities
[DRY RUN 1/5] tripledb-90-miles-cuban-cafe-73973697b7: query='90 Miles Cuban Cafe, chicago, il'
[DRY RUN 2/5] tripledb-a-right-toast-aadf7d5a9a: query='A Right Toast, denver, co'
[DRY RUN 3/5] tripledb-a-sec-b9202fb5f5: query='A Sec, arroyo seco, nm'
[DRY RUN 4/5] tripledb-abe-froman-sausage-king-of-chicago-e7a819d616: query='Abe Froman, ..., nj'
  -> would backfill coordinates
  -> would backfill city
[DRY RUN 5/5] tripledb-aisha-s-7a9f949fd2: query='Aisha's, ocarchee, ok'
  -> would backfill coordinates
```

### Step 6: TripleDB Enrichment Full Run

```
=== SUMMARY ===
Enriched: 391
Missed: 14
Errors: 0
Coordinates backfilled: 88
Cities backfilled: 48
```

Hit rate: 391/405 = 96.5%. 14 misses (niche/closed restaurants that Google Places could not resolve).

### Step 7: Post-Enrichment Verification

```
=== POST-ENRICHMENT VERIFICATION ===
Total: 6181
CalGold: 899
RickSteves: 4182
TripleDB: 1100
Schema v3: 6181/6181 (100%) - target: 100%
TripleDB enriched: 1086/1100 (98%) - target: >85%
TripleDB coords: 1092/1100 (99%) - target: >95%
TripleDB cities: 1027/1100 (93%) - target: >95%
```

---

## Workstream B: NoSQL Query Assessment

### Assessment Scripts

Created `pipeline/scripts/query_assessment.py` and `pipeline/scripts/query_assessment_2.py`:
- Direct Firestore queries testing all 6 categories from design doc
- Flutter app example query simulation (reproducing exact server-side + client-side flow)
- Composite index gap testing
- Limit truncation measurement

### Category 1: Single Field array-contains

| Test | Query | Results | Status |
|------|-------|---------|--------|
| 1.1 | t_any_keywords contains "barbecue" | 76 (2 CalGold, 1 RickSteves, 73 TripleDB) | PASS |
| 1.2 | t_any_countries contains "france" | 402 (all RickSteves) | PASS |
| 1.3 | t_any_shows contains "california's gold" (lowercase) | 0 | FAIL - data is title case |
| 1.4 | t_any_cuisines: "French" vs "french" | 0 vs 80 | FAIL - case sensitive |
| 1.5 | t_any_actors contains "huell howser" | 899 | PASS |
| 1.6 | t_any_actors contains "rick steves" | 4170 | PASS |

### Category 2: Pipeline Filter (equality)

| Test | Query | Results | Status |
|------|-------|---------|--------|
| 2.1 | t_log_type == "tripledb" | 1100 | PASS |
| 2.2 | t_log_type == "calgold" | 899 | PASS |
| 2.3 | t_log_type == "ricksteves" | 4182 | PASS |

### Category 3: Compound Queries

| Test | Query | Results | Status |
|------|-------|---------|--------|
| 3.1 | cuisines contains "mexican" + t_log_type == "tripledb" | 69 | PASS |
| 3.2 | countries contains "italy" + categories contains "restaurant" | FAIL | EXPECTED - Firestore 1 array-contains limit |
| 3.3 | keywords contains "medieval" + t_log_type == "ricksteves" | 653 | PASS |

### Category 4: Multi-value Array Queries

| Test | Query | Results | Status |
|------|-------|---------|--------|
| 4.1 | cuisines contains-any ["mexican", "italian"] | 332 | PASS (Firestore native) |
| 4.2 | countries contains-any ["france", "italy", "spain"] | 1432 | PASS (Firestore native) |

Note: Firestore supports `array-contains-any` natively, but the Flutter parser does not implement the `contains-any` operator.

### Category 5: Result Counts

- Total entities: 6181
- No result count displayed anywhere in the Flutter app UI
- `limit(200)` in `firestore_provider.dart:37` caps all queries

### Category 6: Edge Cases

| Test | Query | Results | Status |
|------|-------|---------|--------|
| 6.1 | No filters (limit 200) | 200 | Returns data (no error) |
| 6.2 | Invalid field "t_any_nonexistent" | 0 | Silent empty (no error shown) |
| 6.3 | "Huell Howser" vs "huell howser" | 0 vs 899 | Case sensitivity bug |
| 6.4 | t_any_shows "rick steves' europe" | 4181 | PASS (lowercase matches) |

### t_any_shows Data Inconsistency

| Pipeline | Title Case | Lowercase | Issue |
|----------|-----------|-----------|-------|
| CalGold | "California's Gold" -> 899 | "california's gold" -> 0 | Data stored in title case |
| RickSteves | "Rick Steves' Europe" -> 0 | "rick steves' europe" -> 4181 | Data stored lowercase |

CalGold shows were set in v5.14 (title case). RickSteves shows were set by pipeline extraction (lowercase). The v8.22 backfill for entities missing t_any_shows used lowercase, but most CalGold entities already had title case from v5.14.

### Flutter Example Query Simulation

| Example | Server-side Query | Server Results | Client-filtered | App Shows |
|---------|-------------------|---------------|----------------|-----------|
| Ex1: French cuisine + Rick Steves show | cuisines contains "French" | 0 | N/A | 0 results - BROKEN |
| Ex2: Huell Howser + CA states | actors contains "Huell Howser" | 0 | N/A | 0 results - BROKEN |
| Ex3: gelato + Europe | dishes contains "gelato" | 6 | 6 (all Europe) | 6 results - WORKS |
| Ex4: landmark + France | categories contains "landmark" | 12 | 1 (France) | 1 result - WORKS |
| Ex5: medieval + roman eras | keywords contains "medieval" | 200 (capped) | 11 (roman era) | 11 results - TRUNCATED |

2 of 5 example queries are completely broken due to case sensitivity. 1 is silently truncated by the 200-result limit.

### Limit Truncation Analysis

| Query | True Count | limit(200) | Hidden |
|-------|-----------|------------|--------|
| keywords contains "medieval" | 653 | 200 | 453 (69%) |
| countries contains "france" | 402 | 200 | 202 (50%) |

### Composite Index Assessment

All tested compound queries (array-contains + equality) executed successfully without needing additional composite indexes. Firestore auto-created single-field indexes are sufficient for the current query patterns.

---

## Security Scan

```
grep -rnI "AIzaSy" . -> only expected references:
  app/lib/firebase_options.dart:13 - Firebase Web API key (public client key, expected)
  docs/ references - grep command itself in prior artifacts
```

No leaked credentials. No SA JSON paths exposed.

---

## Scripts Created

| Script | Purpose | Flags |
|--------|---------|-------|
| pipeline/scripts/backfill_schema_v3.py | Backfill 323 entities to schema v3 | --dry-run, --limit |
| pipeline/scripts/backfill_tripledb_enrichment.py | Google Places enrichment for 405 TripleDB entities | --dry-run, --limit |
| pipeline/scripts/query_assessment.py | NoSQL query assessment (categories 1-6) | N/A |
| pipeline/scripts/query_assessment_2.py | Example query simulation + truncation analysis | N/A |

---

## Interventions

**Claude Code interventions: 0**

All steps executed without human intervention. No ambiguous decision points encountered.
