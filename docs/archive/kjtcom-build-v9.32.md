# kjtcom - Build Log v9.32 (Phase 9 - Shows Fix + Operators + Detail Sort + Quote Rethink)

**Pipeline:** kjtcom
**Phase:** 9 (App Optimization)
**Iteration:** 32 (global counter)
**Executor:** Claude Code (Opus)
**Machine:** NZXTcos
**Date:** 2026-04-04

---

## Execution Summary

6 work items completed. 2 data fix scripts, 4 code changes, 3 new tests added.

---

## W1: TripleDB t_any_shows Data Fix (P0)

Created `pipeline/scripts/fix_tripledb_shows_case.py` following exact pattern from `fix_calgold_shows_case.py`.

```
Dry-run: 5/5 entities needed update
Full run: 1,100 entities updated (0 already lowercase)
Verification: array_contains "diners, drive-ins and dives" -> 1,100 results
```

Batch writes in 500-doc chunks: 3 batches committed.

## W6: Comprehensive Lowercase Data Fix (P1)

Created `pipeline/scripts/fix_all_lowercase.py` - lowercases ALL string values in ALL t_any_* arrays across ALL entities.

```
Dry-run: 10 entities shown (primarily t_any_urls with mixed-case paths)
Full run: 6,181 scanned, 1,286 updated, 4,895 already lowercase
```

Permanent G36 resolution. Batch writes in 500-doc chunks: 3 batches.

## W4: Quote Cursor - No Quotes Approach (P0)

**schema_tab.dart**: Changed "+ Add to query" to append `| where field op ` (trailing space, NO quotes). Cursor placed at end so user types value directly.

**query_clause.dart**: Added unquoted value parsing. Parser now accepts:
- `field operator "value"` -> value (existing, quoted)
- `field operator value` -> value (new, unquoted to EOL)
- `field operator value with spaces` -> value with spaces (new, multi-word)

**query_autocomplete.dart**: Updated AutocompleteContext.detect to trigger value mode:
- After opening quote (existing): `field op "partial`
- After unquoted text (new): `field op partial`
- After operator + space with empty value (new): `field op ` (immediately shows suggestions)

Also updated field-mode accept to append ` contains ` (no quote) instead of ` contains "`.

## W2: Add != Operator (P1)

**query_clause.dart**: `!=` was already in the parser regex from prior iteration.

**firestore_provider.dart**: Added server-side `isNotEqualTo` for scalar fields:
- `!=` on scalar (t_log_type): Firestore `isNotEqualTo` (server-side)
- `!=` on array (t_any_*): client-side filter (exclude matching, already existed)

Verified: `t_log_type != "calgold"` -> 5,282 results (ricksteves 4,182 + tripledb 1,100).

## W3: Sort Detail Panel Fields Alphabetically (P1)

**detail_panel.dart**: Added `.sort((a, b) => a.key.compareTo(b.key))` on `fields.entries.toList()` before rendering. Fields now appear as: t_any_actors before t_any_categories before t_any_cities, etc.

## W5: Fix Autocomplete (P1 - attempt #2)

**Diagnostic findings:**
1. `value_index.json` exists (169KB), correctly in pubspec.yaml assets
2. Overlay creation logic correct (CompositedTransformFollower + OverlayEntry)
3. Debug prints already at detection entry points

**Root cause:** Value mode detection regex required an opening quote to trigger. With W4's no-quotes approach, autocomplete never fired because there was no quote character.

**Fix:** Already addressed in W4 autocomplete changes - added unquoted value detection and empty-value-after-operator detection. Autocomplete now triggers immediately when schema builder appends `field op ` (trailing space).

---

## Test Results

```
flutter analyze: 0 issues
flutter test: 12/12 pass (3 new tests added)
```

New tests:
- QueryClause parses != operator
- QueryClause parses unquoted value
- QueryClause parses unquoted multi-word value

---

## Files Modified

| File | Change |
|------|--------|
| `pipeline/scripts/fix_tripledb_shows_case.py` | NEW - W1 data fix script |
| `pipeline/scripts/fix_all_lowercase.py` | NEW - W6 comprehensive lowercase script |
| `app/lib/widgets/schema_tab.dart` | W4 - no quotes approach |
| `app/lib/models/query_clause.dart` | W4 - unquoted value parsing |
| `app/lib/widgets/query_autocomplete.dart` | W4/W5 - unquoted value detection |
| `app/lib/providers/firestore_provider.dart` | W2 - server-side != for scalar |
| `app/lib/widgets/detail_panel.dart` | W3 - alphabetical sort |
| `app/test/widget_test.dart` | 3 new tests |

---

## Deploy

```
flutter build web: SUCCESS (23.2s)
firebase deploy --only hosting: SUCCESS
Hosting URL: https://kjtcom-c78cd.web.app
```

---

## Security Scan

```
grep -rnI "AIzaSy" . -> Firebase Web API key only (firebase_options.dart:13)
```

Public client key, expected. No leaked credentials.

---

## Production Data Changes

| Script | Entities Scanned | Entities Updated |
|--------|-----------------|-----------------|
| fix_tripledb_shows_case.py | 1,100 (TripleDB) | 1,100 |
| fix_all_lowercase.py | 6,181 (all) | 1,286 |

Claude Code interventions: 0
