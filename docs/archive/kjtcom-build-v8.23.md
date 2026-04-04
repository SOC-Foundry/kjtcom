# kjtcom - Build Log v8.23 (Phase 8 - NoSQL Query Remediation)

**Pipeline:** kjtcom
**Phase:** 8 (Enrichment Hardening)
**Iteration:** 23 (global counter)
**Executor:** Claude Code (Opus 4.6)
**Machine:** NZXTcos
**Date:** 2026-04-03

---

## Pre-Flight

- v8.22 docs archived to docs/archive/
- v8.23 design + plan in docs/
- CLAUDE.md updated for v8.23
- SA credentials: SET
- Flutter build: SUCCESS
- Firebase auth: VALID

---

## W1: Lowercase Query Values (P0 - D1, D3, D4)

**File:** `app/lib/providers/firestore_provider.dart`

Added `.toLowerCase()` to `arrayContains` and `isEqualTo` query value dispatch (lines 26, 30).

- flutter analyze: 0 issues
- flutter test: 3/3 pass

## W2: Update Example Queries (P0 - D3, D4)

**File:** `app/lib/widgets/query_editor.dart`

Replaced 5 compound example queries with single-clause validated lowercase queries.

Validation results (production Firestore):
| Query | Count |
|-------|-------|
| `t_any_cuisines contains "french"` | 80 |
| `t_any_actors contains "huell howser"` | 899 |
| `t_any_countries contains "italy"` | 791 |
| `t_any_dishes contains "gelato"` | 6 |
| `t_any_keywords contains "medieval"` | 653 |

Also updated `initialExampleQuery` in `app/lib/providers/query_provider.dart`.

- flutter analyze: 0 issues
- flutter test: 3/3 pass

## Mid-Iteration Deploy (P0 live)

```
flutter build web -> SUCCESS (18.6s)
firebase deploy --only hosting -> SUCCESS
Hosting URL: https://kjtcom-c78cd.web.app
```

## W3: CalGold t_any_shows Data Fix (P1 - D2)

**Script:** `pipeline/scripts/fix_calgold_shows_case.py`

Created one-time data fix script following backfill_schema_v3.py pattern:
- `--dry-run` flag for safe preview
- `--limit` flag for incremental testing
- Batch writes (500 per batch)

Execution:
```
--dry-run --limit 5: 5 entities previewed
  calgold-101-cafe: ["California's Gold"] -> ["california's gold"]
Full run: 899/899 entities updated (2 batches: 500 + 399)
```

Verification:
```
t_any_shows contains "california's gold" -> 899 results (PASS)
```

## W5+W6: Result Count Badge + Truncation Indicator (P1 - D8, D9)

**Files:** `app/lib/providers/firestore_provider.dart`, `app/lib/widgets/results_table.dart`

Refactored `firestore_provider.dart`:
- Added `QueryResult` class with `entities`, `serverCount`, `limit`, `isTruncated`
- Added `queryResultProvider` (new primary provider)
- Kept `resultsProvider` as backward-compatible wrapper for `entity_count_row.dart`

Updated `results_table.dart`:
- Switched from `resultsProvider` to `queryResultProvider`
- Added `_buildResultBar()` - displays count in tech green (#4ADE80) Geist Mono
- Truncation warning in accent orange (#FFA657) when `serverCount >= limit`

- flutter analyze: 0 issues
- flutter test: 3/3 pass

## W4: Implement `contains-any` Operator (P1 - D7)

**Files:** `app/lib/models/query_clause.dart`, `app/lib/providers/firestore_provider.dart`, `app/lib/widgets/query_editor.dart`

Parser (`query_clause.dart`):
- Added `contains-any` regex match before standard operators
- Added `values` field (List<String>) to `QueryClause`
- Added `_parseValueList()` supporting JSON array `["a", "b"]` and comma-separated syntax
- Added `knownFields` set and `isValidField` getter (for W8)

Provider (`firestore_provider.dart`):
- Added `contains-any` -> `arrayContainsAny` server-side dispatch
- Enforces Firestore 30-value limit via `.take(30)`
- Added `contains-any` to client-side filter switch

Syntax highlighter (`query_editor.dart`):
- Updated regex to match `contains-any` keyword and `[...]` array values
- Both styled with appropriate syntax colors

Verification:
```
t_any_cuisines contains-any ["mexican", "italian"] -> 332 results (PASS)
```

- flutter analyze: 0 issues
- flutter test: 6/6 pass (3 new tests added)

## W7: Increase Result Limit to 1000 (P1 - D6)

**File:** `app/lib/providers/firestore_provider.dart`

Changed `_queryLimit` from 200 to 1000. Design doc recommendation: Option A (simpler). Covers all current query scenarios (max observed: 653 for "medieval").

- flutter analyze: 0 issues
- flutter test: 6/6 pass

## W8+W9: Field Validation + Error Feedback (P2 - D10, D11, D5)

**Files:** `app/lib/models/query_clause.dart`, `app/lib/widgets/query_editor.dart`

W8 - Field validation (`query_clause.dart`):
- `knownFields` set with 21 valid field names
- `isValidField` getter checks field membership

W9 - Error feedback (`query_editor.dart`):
- Added `_buildFeedback()` widget below query editor
- Parse error (red): shown when non-empty input produces no clauses
- Invalid field (orange): shown when field name not in `knownFields`
- Multi-array note (secondary): shown when >1 array-contains clause, informing user of client-side filtering from first 1,000 results

- flutter analyze: 0 issues
- flutter test: 6/6 pass

## Final Deploy

```
flutter build web -> SUCCESS (18.9s)
firebase deploy --only hosting -> SUCCESS
Hosting URL: https://kjtcom-c78cd.web.app
```

## Security Scan

```
grep -rnI "AIzaSy" . -> Firebase Web API key only (public client key, expected)
No leaked credentials.
```

## Final State

- flutter analyze: 0 issues
- flutter test: 6/6 pass (3 original + 3 new)
- Deploys: 2 (mid-iteration P0 + final)
- Files modified: 5 Dart files + 1 Python script
- Interventions: 0
