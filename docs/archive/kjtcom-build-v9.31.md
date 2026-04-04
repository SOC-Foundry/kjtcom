# kjtcom - Build Log v9.31 (Phase 9 - Persistent Bug Fix + Playwright Verification)

**Pipeline:** kjtcom
**Phase:** 9 (App Optimization)
**Iteration:** 31 (global counter)
**Executor:** Claude Code (Opus)
**Machine:** NZXTcos
**Date:** 2026-04-04

---

## Pre-Flight

- [x] Previous artifacts archived to docs/archive/
- [x] Design + plan docs in place (v9.31)
- [x] CLAUDE.md updated
- [x] flutter pub upgrade (pre-flight by human)
- [x] flutter analyze: 0 issues
- [x] flutter test: 9/9 pass

---

## W1: 1000-Result Limit - DIAGNOSTIC

### Grep Output (all app/lib/ files)

```
grep -rn "1000|limit|truncat|isTruncated|serverCount|totalCount|_queryLimit" app/lib/
```

Results:
```
firestore_provider.dart:10:  final int totalCount;
firestore_provider.dart:14:    required this.totalCount,
firestore_provider.dart:22:/// Firestore limitation: only ONE arrayContains per query.
firestore_provider.dart:39:      // Firestore limits arrayContainsAny to 30 values
firestore_provider.dart:82:      totalCount: entities.length,
gotcha_tab.dart:111:    title: 'Firestore single array-contains limit',
results_table.dart:175:    if (count < 1000) return '$count';
results_table.dart:176:    final thousands = count ~/ 1000;
results_table.dart:177:    final remainder = count % 1000;
```

### Diagnostic Analysis

1. **firestore_provider.dart**: NO `.limit()` call anywhere. `totalCount: entities.length` uses actual entity count. Query streams ALL matching docs.
2. **entity_count_row.dart**: Uses same `resultsProvider` (derived from `queryResultProvider`). NO separate query. Shows `entities.length`.
3. **results_table.dart**: `_formatCount()` is just comma formatting (1000 -> "1,000"). NOT a limit. No "1000+" or "of X" text.
4. **No other file** contains any `.limit()` call on a Firestore query.

### Python Firestore Verification

```
Total documents in locations collection: 6181
TripleDB documents: 1100
Barbecue cuisine documents: 60
```

### Conclusion

The 1000-result limit was successfully removed in v9.29. The code has NO limit anywhere. The default query returns all 6,181 documents. **NO CODE CHANGE NEEDED.**

---

## W2: Quote Cursor Placement - DIAGNOSTIC

### Full File Analysis

**schema_tab.dart** onTap flow (lines 273-285):
1. `controller.text = newText` - sets text on shared controller
2. `controller.selection = collapsed(offset: newText.length - 1)` - sets cursor before closing quote
3. `ref.read(queryProvider.notifier).setText(newText)` - updates provider state
4. `ref.read(activeTabProvider.notifier).state = 0` - switches to Results tab

**query_editor.dart** ref.listen (lines 94-99):
```dart
ref.listen(queryProvider, (_, next) {
  if (_controller.text != next) {
    _controller.text = next;
    _controller.selection = TextSelection.collapsed(offset: next.length);
    setState(() {});
  }
});
```

### Root Cause Analysis

The guard `_controller.text != next` should prevent cursor override because schema_tab sets `controller.text` BEFORE calling `queryProvider.setText()`. When the listener fires, text already matches, so the body is skipped.

However, a frame-timing edge case exists: setting `controller.text` triggers `_updateAutocomplete` -> `setState()` -> rebuild. Between the rebuild and the selection being set, the cursor position could be lost.

### Fix Applied

Moved cursor set into `addPostFrameCallback` in schema_tab.dart to guarantee it runs AFTER all rebuilds from text/provider/tab changes complete. Added debugPrint traces to both schema_tab and query_editor ref.listen.

---

## W3: Autocomplete Not Showing - DIAGNOSTIC

### Asset Verification

- `value_index.json` registered in pubspec.yaml: line 30 `- assets/value_index.json`
- File exists: 169,146 bytes
- Content valid: JSON with 21 field keys, 6,878+ values

### Code Analysis

**query_autocomplete.dart** `_onTextChanged()` (line 124):
```dart
final valueIndex = ref.read(valueIndexProvider).valueOrNull ?? {};
```

**Issue Found:** `valueIndexProvider` is a `FutureProvider` that loads from `rootBundle`. On first access, `.valueOrNull` returns `null` because the asset hasn't loaded yet. The overlay uses `ref.read()` (non-reactive) in a callback, so it never re-triggers when the data loads.

### Fix Applied

Added `ref.listen(valueIndexProvider, ...)` in the overlay's `build()` method. When the FutureProvider transitions from loading to loaded, `_onTextChanged()` is re-triggered, picking up the now-available value index data.

Added debugPrint traces to `_updateAutocomplete` in query_editor.dart and `_onTextChanged` in the overlay.

---

## W4: TripleDB Results - DIAGNOSTIC

### Python Firestore Verification

```python
# Sample tripledb docs
ID: tripledb-10th-street-diner-88d861cf88
  t_log_type: tripledb
  t_any_names: ['10th Street Diner']
  t_any_cuisines: ['vegan diner']
  t_any_countries: ['us']
  t_any_cities: ['indianapolis']

ID: tripledb-11th-street-diner-3b641bdafb
  t_log_type: tripledb
  t_any_names: ['11th Street Diner']
  t_any_cuisines: ['american diner']
  t_any_countries: ['us']
  t_any_cities: ['miami']

Distinct t_log_type values: ['calgold', 'ricksteves', 'tripledb']
Total tripledb: 1,100
Barbecue cuisines: 60
```

### Code Analysis

**firestore_provider.dart** correctly handles `t_log_type == "tripledb"`:
- `clause.operator == '=='` AND `!clause.field.startsWith('t_any_')` -> server-side `isEqualTo`
- Value lowercased: `clause.value.toLowerCase()` -> matches `"tripledb"` in Firestore

**LocationEntity.fromFirestore** correctly maps all fields including `logType` for pipeline badges.

**Conclusion:** TripleDB data exists (1,100 docs), schema matches, query parsing is correct. Results should render with red TD pipeline dots. **NO CODE CHANGE NEEDED.**

---

## W5: Clear Button

### Implementation

Added clear button to query_editor.dart `_buildChipRow()`:
- Conditionally visible when query text is non-empty
- Position: between "locations" and "All time" chips
- Red border accent with X icon + "Clear" label
- On tap: clears controller, resets queryProvider to empty string, clears selectedEntityProvider

---

## Build + Deploy

```
flutter analyze: No issues found! (ran in 1.0s)
flutter test: 9/9 pass
flutter build web: Built build/web (23.7s)
firebase deploy --only hosting: Deploy complete! (41 files)
```

---

## Security Scan

```
grep -rnI "AIzaSy" . -> Firebase Web API key only (firebase_options.dart:13)
```

All other matches are doc references to the scan command itself. **CLEAN.**

---

## Playwright Post-Flight Verification

### Screenshot: Landing Page (v9.31-landing.png)

- **Entity count: "6181 entities across 82 countries"** - CONFIRMED no 1000 limit
- **Result bar: "6,181 results"** - correct total
- **Pagination: "Page 1 of 310"** (20 per page) - working
- **All pipeline dots visible** with CG (CalGold) badges on first page
- **Tab bar**: Results | Map | Globe | IAO | Gotcha | Schema - all visible

### Screenshot: TripleDB Query Attempt (v9.31-tripledb-results.png)

**G47 CONFIRMED:** Flutter CanvasKit renders the entire app to a single `<canvas>` element. Playwright `page.mouse.click()` and `page.keyboard.type()` do not reach Flutter's text input system. The typed query did not appear in the editor.

**Limitation:** Playwright can capture screenshots of the rendered canvas but cannot interact with Flutter Web CanvasKit apps. Live verification of W2 (cursor), W3 (autocomplete), W4 (tripledb query results), and W5 (clear button) requires manual testing.

### Manual Test Script for Kyle

1. Open https://kylejeromethompson.com
2. Verify entity count shows 6,181 (not 1000)
3. Click Schema tab -> click "+ Add to query" on t_any_cuisines
4. Verify cursor is between quotes in `| where t_any_cuisines contains ""`
5. Type "barbecue" - verify text appears between quotes
6. Open browser console (F12) - look for `[W2]` and `[W3]` debugPrint messages
7. Click Search - verify results appear (should be ~60 barbecue results)
8. Look for red TD dots (TripleDB results)
9. Clear the query field and type `t_log_type == "tripledb"` -> Search
10. Verify ~1,100 results with all red TD dots
11. Verify Clear button appears when query text is present
12. Click Clear - verify query clears, results reset to all 6,181

---

## Files Modified

| File | Change |
|------|--------|
| app/lib/widgets/schema_tab.dart | W2: cursor set via addPostFrameCallback |
| app/lib/widgets/query_editor.dart | W2: debugPrint in ref.listen, W5: clear button + import |
| app/lib/widgets/query_autocomplete.dart | W3: ref.listen for valueIndex reload + debugPrint |

## Files Created

| File | Purpose |
|------|---------|
| docs/v9.31-landing.png | Playwright screenshot - landing page |
| docs/v9.31-query-typed.png | Playwright screenshot - query attempt (G47) |
| docs/v9.31-tripledb-results.png | Playwright screenshot - results (G47) |
| docs/kjtcom-build-v9.31.md | This file |
| docs/kjtcom-report-v9.31.md | Iteration report |
