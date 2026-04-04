# kjtcom - Build Log v9.33 (Phase 9 - Parser Regression + Quotes + Operators)

**Pipeline:** kjtcom
**Phase:** 9 (App Optimization)
**Iteration:** 33 (global counter)
**Executor:** Claude Code (Opus)
**Machine:** NZXTcos
**Date:** 2026-04-04

---

## W1: Fix Parser Regression (P0)

**Diagnosis:** Read query_clause.dart completely. The parser already has correct two-regex structure:
- Line 78: `quotedRegex` tries quoted values FIRST (captures text between `"..."`)
- Line 92: `unquotedRegex` as FALLBACK (captures to end of line)

The regex order was correct in the repo code. The regression on the live site was from a stale deploy - the v9.32 build had the old single-regex that matched unquoted before quoted. The repo code had already been corrected but not deployed.

**Tests:** Added 3 regression tests:
- `QueryClause parses quoted geology keyword query` - exact failing query from live site
- `QueryClause parses == with quoted value`
- `QueryClause parses != with quoted value`

All 15 tests pass. flutter analyze: 0 issues.

**Build + Deploy:** flutter build web (21.2s) -> firebase deploy -> kjtcom-c78cd.web.app
Live site verification: Flutter WASM app loads (WebFetch confirms title "kjtcom - Location Intelligence"). Client-side parser verification requires browser - deferred to Kyle.

---

## W2: Restore Quotes + Fix Cursor (P0)

**programmaticUpdateProvider created:** `StateProvider<bool>` in query_provider.dart.

**ref.listen updated in query_editor.dart (line 96):**
- Added `debugPrint` showing flag state and text match status
- Skips controller update when `programmaticUpdateProvider` is true
- Prevents cursor override during programmatic text changes

**Schema builder updated in schema_tab.dart:**
- Clause now appends `| where field op ""` (with quotes)
- Flag set to true BEFORE controller.text change
- Cursor placed at `newText.length - 1` (between quotes)
- Flag cleared via `Future.microtask` (next event loop tick)
- debugPrint traces cursor position

flutter analyze: 0 issues. flutter test: 15/15 pass.

---

## W3: +filter == , -exclude != (P0)

**detail_panel.dart changes:**
- +filter: changed operator from `contains` to `==` (line 256)
- -exclude: already using `!=` (no change needed)
- Both handlers now use programmaticUpdateProvider flag with Future.microtask cleanup

flutter analyze: 0 issues. flutter test: 15/15 pass.

---

## W4: Fix Query Feedback Message (P1)

No change needed. The existing feedback message on line 213 already shows the correct syntax:
```
Expected: field_name operator value (e.g., t_any_keywords contains "barbecue")
```
This is correct for both quoted and unquoted values.

---

## W5: Flutter Dependency Upgrade (P1) - DEFERRED

**Attempted:** `flutter pub upgrade --major-versions` upgraded 5 packages:
- firebase_core 3 -> 4
- cloud_firestore 5 -> 6
- flutter_riverpod 2 -> 3
- google_fonts 6 -> 8
- flutter_map 7 -> 8

**Result:** 3 errors + 28 warnings.
- Riverpod 3 removed `StateProvider` entirely
- Riverpod 3 made `Notifier.state` protected (no external `.state =` access)
- 18 call sites across 8 files need setter methods on Notifier classes
- 3 `valueOrNull` getter removals in query_autocomplete.dart

**Decision:** >50 lines of migration required. Reverted pubspec.yaml to original constraints. Documented for dedicated iteration.

**Migration needed for v9.34:**
1. Replace 5 StateProviders with NotifierProvider + Notifier classes
2. Add `set()` methods to each Notifier
3. Change 18 `.notifier).state = x` call sites to `.notifier).set(x)`
4. Change 3 `valueOrNull` to `value` in query_autocomplete.dart
5. Test all tabs (Results, Map, Globe, IAO, Gotcha, Schema)

---

## Final Deploy

```
flutter analyze: 0 issues
flutter test: 15/15 pass
flutter build web: success (23.9s)
firebase deploy: kjtcom-c78cd.web.app - 41 files uploaded
```

**Security scan:** `grep -rnI "AIzaSy"` - only Firebase web API key in firebase_options.dart and compiled JS (public client key, expected). No leaked credentials.

---

## Files Modified

| File | Change |
|------|--------|
| app/lib/providers/query_provider.dart | Added programmaticUpdateProvider |
| app/lib/widgets/query_editor.dart | ref.listen skips on programmatic flag + debugPrint |
| app/lib/widgets/schema_tab.dart | Quotes restored, cursor between quotes, flag protection |
| app/lib/widgets/detail_panel.dart | +filter uses ==, both use flag |
| app/test/widget_test.dart | 3 new regression tests (15 total) |

---

## Interventions

Claude Code interventions: 0
