# kjtcom - Design v8.22 (Phase 8 - Enrichment Hardening + Query Assessment)

**Pipeline:** kjtcom (cross-pipeline location intelligence platform)
**Phase:** 8 (Enrichment Hardening)
**Iteration:** 22 (global counter)
**Executor:** Claude Code (enrichment scripts + Flutter assessment)
**Machine:** NZXTcos (primary) or tsP3-cos
**Date:** April 2026

---

## Objective

Phase 8.22 has two workstreams:

**Workstream A - Enrichment Hardening:** Backfill the 323 pre-v3 CalGold/RickSteves entities and the 405 under-enriched TripleDB entities identified in the v7.21 report. Close coordinate, city, and schema gaps so all 6,181 production entities are at schema v3 with maximum enrichment coverage.

**Workstream B - NoSQL Query Assessment:** Perform a comprehensive audit of the Flutter app's query editor functionality against the production Firestore dataset. The rotating example queries and the NoSQL search bar are non-functional - they display faux results or fail silently. This workstream documents every broken query path, maps the gap between what the UI promises and what Firestore actually supports, and produces a remediation spec for v8.23.

After this iteration: all entities at schema v3, enrichment coverage above 90% across all pipelines, and a complete defect inventory for the query system with a scoped remediation plan.

---

## IAO Pillar Compliance Matrix

Every design decision in this document has been evaluated against the 10 IAO Pillars:

| Pillar | Check | Status |
|--------|-------|--------|
| P1 - Trident | Cost: $0 (free-tier APIs, local scripts). Speed: single iteration, parallelizable workstreams. Performance: targeted backfill, not full re-extraction. | PASS |
| P2 - Artifact Loop | 4 mandatory artifacts (build, report, changelog, README). Previous v7.21 docs archived. | PASS |
| P3 - Diligence | This design doc is revision 1. Plan doc pre-answers all decision points including Firestore query limitations. | PASS |
| P4 - Pre-Flight | Section A of plan verifies production counts, SA credentials, schema version distribution, and Flutter app state before execution. | PASS |
| P5 - Agentic Harness | CLAUDE.md updated for v8.22. Playwright MCP for Flutter testing. Pipeline scripts as tools. Gotcha registry current. | PASS |
| P6 - Zero-Intervention | All enrichment paths pre-specified. Query assessment is read-only (no app changes). No ambiguous decision points. | PASS |
| P7 - Self-Healing | Checkpoint resume for enrichment. Max 3 retries per geocode/Places call. Skip and log on persistent failure. | PASS |
| P8 - Phase Graduation | Phase 8 is hardening - iterating on production data quality, not introducing new pipeline phases. | PASS |
| P9 - Post-Flight Testing | Tier 1: production entity counts verified. Tier 2: schema v3 rate = 100%, enrichment rate > 90%. Tier 3: query defect inventory complete. | PASS |
| P10 - Continuous Improvement | Query assessment findings feed directly into v8.23 remediation plan. Gotcha registry updated with any new patterns. | PASS |

---

## Architecture Decisions

[DECISION] **Workstream A: In-place Firestore update, not re-extraction.** The 323 non-v3 entities need their Thompson Indicator Fields upgraded to v3 (adding t_any_actors, t_any_roles, t_any_shows, t_any_cuisines, t_any_dishes, t_any_eras, t_any_continents). This is done via a Python script that reads each entity from production, applies v3 backfill rules based on t_log_type, and writes back. No re-extraction from YouTube transcripts. No Gemini API calls.

[DECISION] **Workstream A: TripleDB enrichment via Google Places API.** The 405 TripleDB entities missing enrichment will be run through the existing phase6_enrich.py pattern adapted for production reads. Coordinates and cities will be backfilled simultaneously using Google Places + Nominatim reverse geocoding.

[DECISION] **Workstream B: Playwright MCP for query assessment.** The Flutter app will be tested programmatically via Playwright MCP to document which queries work, which fail, and which return incorrect results. This produces a structured defect inventory, not code fixes. Code fixes are scoped to v8.23.

[DECISION] **Workstream B: No app code changes in v8.22.** The query assessment is diagnostic only. The report artifact will contain a complete defect table with severity, root cause, and recommended fix for each issue. v8.23 implements the fixes.

---

## Workstream A: Enrichment Hardening

### A1: Schema v3 Backfill (323 entities)

**Source:** v7.21 report identified 121 CalGold + 202 RickSteves entities at schema v1/v2.

**Backfill rules by pipeline:**

CalGold (121 entities):
- t_any_actors: ["Huell Howser"] (hardcoded - host of every episode)
- t_any_roles: ["host"]
- t_any_shows: ["California's Gold"]
- t_any_cuisines: [] (not a food show)
- t_any_dishes: [] (not a food show)
- t_any_eras: [] (skip - requires transcript re-analysis)
- t_any_continents: ["North America"] (all California locations)
- t_schema_version: 3

RickSteves (202 entities):
- t_any_actors: ["Rick Steves"] (hardcoded - host of every episode)
- t_any_roles: ["host"]
- t_any_shows: ["Rick Steves' Europe"]
- t_any_cuisines: [] (skip - requires transcript re-analysis)
- t_any_dishes: [] (skip - requires transcript re-analysis)
- t_any_eras: [] (skip - requires transcript re-analysis)
- t_any_continents: derive from t_any_countries using COUNTRY_TO_CONTINENT lookup
- t_schema_version: 3

### A2: TripleDB Enrichment Backfill (405 entities)

**Source:** v7.21 report: 405 TripleDB entities (37%) lack Google Places enrichment.

Script reads TripleDB entities from production where t_enrichment.google_places is null/empty, runs Google Places text search (name + city + state), and writes enrichment data back to production. Same enrichment pattern as phase6_enrich.py.

### A3: Coordinate + City Backfill (96 + 120 entities)

**Source:** v7.21 report: 96 TripleDB entities missing lat/lon, 120 missing city.

For entities with address but no coordinates: Nominatim geocode from address.
For entities with coordinates but no city: Nominatim reverse geocode from lat/lon.
For entities with neither: Google Places text search to get both.

---

## Workstream B: NoSQL Query Assessment

### B1: Current Query Architecture

The Flutter app's query system (built in v6.17) uses:
- `query_editor.dart`: syntax-highlighted text input with 5-color tokenizer
- `query_clause.dart`: parses user input into QueryClause objects (field, operator, value)
- `firestore_provider.dart`: converts QueryClause objects into Firestore queries
- Firestore query: server-side `arrayContains` for the first clause, client-side filtering for additional clauses

**Known limitations from v6.17 build log:**
- Firestore only supports ONE `array-contains` per query - multi-clause array queries require client-side filtering
- No `array-contains-any` support implemented
- No inequality filters (>, <, >=, <=) on t_any_* fields
- No compound queries combining array-contains with equality filters on different fields
- No full-text search (Firestore doesn't support it natively)
- Rotating example queries may reference query syntax the parser doesn't implement

### B2: Assessment Methodology

The assessment will test every query pattern the UI implies is possible:

**Category 1 - Single field array-contains:**
- `t_any_keywords contains "barbecue"` -> should return TripleDB results
- `t_any_countries contains "france"` -> should return RickSteves results
- `t_any_shows contains "california's gold"` -> should return CalGold results

**Category 2 - Pipeline filter (equality):**
- `t_log_type == "tripledb"` -> should return all 1,100 TripleDB entities
- `t_log_type == "calgold"` -> should return all 899 CalGold entities

**Category 3 - Compound queries (array-contains + equality):**
- `t_any_cuisines contains "mexican" AND t_log_type == "tripledb"` -> should work server-side (composite index)
- `t_any_countries contains "italy" AND t_any_categories contains "restaurant"` -> requires client-side for second clause

**Category 4 - Multi-value array queries:**
- `t_any_cuisines contains-any ["mexican", "italian"]` -> Firestore supports array-contains-any (max 30 values)
- `t_any_countries contains-any ["france", "italy", "spain"]` -> same

**Category 5 - Result counts:**
- Every query result must display the total count of matching entities
- Currently no count is shown in the UI

**Category 6 - Edge cases:**
- Empty query -> should show all entities or clear results
- Invalid field name -> should show error, not silent failure
- Case sensitivity -> t_any_* values are lowercased, but user input may not be

### B3: Composite Index Requirements

Based on the query patterns above, the following composite indexes may be needed:

| Index | Fields | Purpose |
|-------|--------|---------|
| 1 | t_any_cuisines (array-contains) + t_log_type (==) | Filter cuisines by pipeline |
| 2 | t_any_actors (array-contains) + t_log_type (==) | Filter actors by pipeline |
| 3 | t_any_countries (array-contains) + t_log_type (==) | Filter countries by pipeline |
| 4 | t_any_dishes (array-contains) + t_log_type (==) | Filter dishes by pipeline |
| 5 | t_any_shows (array-contains) | Filter by show |
| 6 | t_any_keywords (array-contains) | Full-text keyword search |

### B4: MCP Server + Tool Assessment for v8.23

The following MCP servers and tools should be evaluated for the v8.23 query remediation iteration:

**Playwright MCP** (already available): Automated UI testing of query editor against live site. Can type queries, verify results, capture screenshots. Used in v8.22 for assessment, reusable in v8.23 for regression testing.

**Firebase MCP** (evaluate availability): If a Firebase/Firestore MCP server exists, it could enable Claude Code to directly query Firestore during development without writing throwaway Python scripts. Check the MCP registry.

**Meta HyperAgents** (evaluate for v8.23+): The query assessment will produce structured test cases (input query -> expected result count -> actual result count). This is a natural fitness signal for a HyperAgent to optimize the query parser and Firestore provider against. Evaluate whether HyperAgents can consume the defect inventory and propose code fixes that pass the test suite. Note: HyperAgents may be premature for a single-iteration fix but valuable for ongoing query optimization.

**Algolia/Typesense** (architectural evaluation): If Firestore's native query limitations are fundamental blockers (e.g., full-text search, multi-array-contains), evaluate whether adding a lightweight search index (Algolia Firebase Extension or self-hosted Typesense) is worth the cost/complexity tradeoff. Document in report but do not implement in v8.22.

---

## Success Criteria

| Criteria | Target |
|----------|--------|
| Schema v3 rate | 100% (all 6,181 entities) |
| TripleDB enrichment rate | >85% (up from 63%) |
| TripleDB coordinate rate | >95% (up from 91%) |
| TripleDB city rate | >95% (up from 88%) |
| Query defect inventory | Complete (all 6 categories tested) |
| Result count display | Assessed and documented (fix in v8.23) |
| Composite index gaps | Identified and documented |
| v8.23 remediation spec | Included in report artifact |
| Interventions | 0 |
| Artifacts | 4 mandatory docs |

---

## Gotchas Active

| ID | Gotcha | Prevention |
|----|--------|-----------|
| G11 | API key leaks | NEVER cat config.fish or SA JSON files |
| G20 | Config.fish contains keys | grep only, never cat |
| G31 | Schema drift | Inspect actual production data before writing update scripts |
| G33 | Duplicate entity IDs | Deterministic t_row_id, check before write |
| G34 (NEW) | Firestore single array-contains limit | Only one array-contains per server-side query. Multi-clause requires client-side filtering or query restructuring. |
| G35 (NEW) | Production write safety | All production updates use batch writes with dry-run flag. Verify on 5 entities before full run. |

---

## Phase Structure Reference

| Phase | Name | Status | Iteration |
|-------|------|--------|-----------|
| 0 | Scaffold & Environment | DONE | v0.5 |
| 1 | Discovery (30 videos) | DONE | v1.6, v1.7 |
| 2 | Calibration (60 videos) | DONE | v2.8, v2.9 |
| 3 | Stress Test (90 videos) | DONE | v3.10, v3.11 |
| 4 | Validation + Schema v3 (120 videos) | DONE | v4.12, v4.13 |
| 5 | Production Run (full datasets) | DONE | v5.14, v5.17 |
| 6 | Flutter App | DONE | v6.15-v6.20 |
| 7 | Firestore Load | DONE | v7.21 |
| 8 | Enrichment Hardening | IN PROGRESS | v8.22 |
| 9 | App Optimization | Pending | - |
| 10 | Retrospective + Template | Pending | - |
