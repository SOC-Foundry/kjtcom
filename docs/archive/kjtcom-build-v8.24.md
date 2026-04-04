# kjtcom - Build Log v8.24 (Phase 8 - UI Fixes + Country Codes)

**Pipeline:** kjtcom
**Phase:** 8 (Enrichment Hardening)
**Iteration:** 24 (global counter)
**Executor:** Claude Code (Opus)
**Machine:** NZXTcos
**Date:** 2026-04-03

---

## Pre-Flight

- Git clean, CLAUDE.md pointing to v8.24 docs
- v8.23 docs archived to docs/archive/
- Flutter builds verified, Firebase auth valid
- pycountry installed

---

## W1: Fix Detail Panel (P0)

### Diagnostic

Read 5 files in the selection chain:
1. `detail_panel.dart` - watches `selectedEntityProvider`, renders t_any_* field cards
2. `results_table.dart` - row tap sets `selectedEntityProvider.notifier.state = entity`
3. `selection_provider.dart` - simple `StateProvider<LocationEntity?>`
4. `app_shell.dart` - `_ResultsArea` layout
5. `firestore_provider.dart` - `QueryResult` wrapper, streams entities

### Root Cause

Two issues found in the provider -> render chain:

**Issue 1: `_ResultsArea` only includes DetailPanel on desktop (>= 1024px)**
`app_shell.dart:169` - `if (isWide) const DetailPanel()` means the detail panel is never in the widget tree on tablet or mobile viewports. Clicking a row updates the provider, but no widget is listening.

**Issue 2: Widget type switching prevents animation**
`detail_panel.dart:16` - returns `SizedBox.shrink()` when null, then `AnimatedContainer` when selected. Different widget types mean Flutter tears down and rebuilds rather than animating.

### Fix

**app_shell.dart:**
- Added `flutter_riverpod` and `selection_provider` imports
- Converted `_ResultsArea` from `StatelessWidget` to `ConsumerWidget`
- Desktop (>= 1024px): Row with ResultsTable (Expanded) + DetailPanel (always present, animates width)
- Mobile/tablet (< 1024px): Stack with ResultsTable + overlay DetailPanel with scrim. Tapping scrim closes panel.

**detail_panel.dart:**
- Always returns `AnimatedContainer` with `width: entity != null ? Tokens.sidebarWidth : 0`
- Added `clipBehavior: Clip.hardEdge` to hide content during width animation
- Inner `SizedBox(width: Tokens.sidebarWidth)` ensures content is laid out at full width even during transition

### Verification
- flutter analyze: 0 issues
- flutter test: 6/6 pass

---

## W2: Remove "staging" Badge (P0)

### Fix

Removed the "staging" badge container from `app_shell.dart:105-125`. The app queries the production (default) database since v7.21 - the badge was incorrect.

Widget removed:
```dart
Container(
  // "staging" badge with green border + text
  child: Text('staging'),
)
```

### Verification
- flutter analyze: 0 issues
- flutter test: 6/6 pass

---

## Mid-Iteration Deploy

```
firebase deploy --only hosting
Hosting URL: https://kjtcom-c78cd.web.app
39 files deployed
```

P0 fixes (detail panel + staging badge removal) live.

---

## W3: Fix Cursor Alignment (P1)

### Diagnostic

Read `query_editor.dart` - Stack-based architecture:
1. Column of syntax-highlighted lines (visual display with line numbers)
2. Positioned.fill TextField (invisible text, visible cursor)
3. Positioned Search button on right

### Root Cause

**Issue 1: Multiple cursors**
Custom blinking cursor (`_buildCursorLine` with `_cursorTimer`) renders a `|_` character on empty last lines. The TextField also renders its native cursor. Two cursors visible simultaneously.

**Issue 2: Per-line vertical padding drift**
Each visual display line has `padding: EdgeInsets.symmetric(vertical: 3)` (6px per line). The TextField has no per-line padding - only `height: 1.75` line-height. After N lines, the visual text and cursor drift apart by N*6px.

### Fix

- Removed custom cursor: `_cursorVisible`, `_cursorTimer`, `_startCursorBlink()`, `_buildCursorLine()`
- Removed `padding: const EdgeInsets.symmetric(vertical: 3)` from `_buildQueryLine`
- Added `height: 1.75` to line number text style for consistent baseline
- Removed unused `showCursor` parameter from `_syntaxHighlight`
- TextField's native cursor now handles all cursor display - single cursor, aligned with text

### Verification
- flutter analyze: 0 issues
- flutter test: 6/6 pass

---

## W4: Country Codes Backfill (P1)

### Script

Created `pipeline/scripts/backfill_country_codes.py`:
- Uses `pycountry` as primary lookup (name, fuzzy search)
- Hardcoded fallback table for 40+ edge cases (scotland -> gb, uk -> gb, palestine -> ps, etc.)
- Batch writes (500 per batch) with `--dry-run` and `--limit` flags
- Stores codes as lowercase: `["fr", "it", "us"]`

### Dry Run (10 entities)
```
Mode: DRY RUN
Limit: 10 entities
Updated: 10, Skipped: 0
```

### Full Run (6,181 entities)
```
Mode: LIVE WRITE
Fetched: 6,181 entities
13 batches committed
Updated: 6,161
Skipped (no countries): 20
Unmapped country names (6):
  - (empty string)
  - bosnia-herzegovina
  - denmark, sweden
  - france / spain
  - palestinian territories
  - united kingdom, france
```

6 unmapped names are compound/malformed entries from source data. 99.7% coverage.

### Dart Updates

- `query_clause.dart`: Added `t_any_country_codes` to `knownFields` set
- `location_entity.dart`: Added `List<String> get countryCodes` getter

### Test Updates

Added 3 new tests to `widget_test.dart`:
1. `t_any_country_codes` recognized as valid field
2. `contains-any` with country codes parses correctly
3. Typo field (`t_any_country_codez`) rejected as invalid

### Verification
- flutter analyze: 0 issues
- flutter test: 9/9 pass

---

## Final Deploy

```
firebase deploy --only hosting
Hosting URL: https://kjtcom-c78cd.web.app
39 files deployed
```

All 4 work items live.

---

## Security Scan

```
grep -rnI "AIzaSy" .
```

Results: Only expected references:
- `firebase_options.dart` - Firebase Web API key (public client key by design)
- Build artifacts (compiled JS)
- Documentation references to the scan command itself

No leaked credentials.

---

## Regression Results

| # | Test | Result |
|---|------|--------|
| 1 | flutter analyze | 0 issues |
| 2 | flutter test | 9/9 pass |
| 3 | firebase deploy (mid-iteration) | Success |
| 4 | firebase deploy (final) | Success |
| 5 | t_any_country_codes backfill | 6,161/6,181 |
| 6 | t_any_country_codes in knownFields | Yes |
| 7 | Security scan | Clean |
| 8 | Detail panel in widget tree (all viewports) | Yes |
| 9 | "staging" badge removed | Yes |

---

## Files Modified

| File | Change |
|------|--------|
| `app/lib/widgets/detail_panel.dart` | Always return AnimatedContainer, animate width 0 -> sidebarWidth |
| `app/lib/widgets/app_shell.dart` | ConsumerWidget _ResultsArea, narrow-screen overlay, removed staging badge |
| `app/lib/widgets/query_editor.dart` | Removed custom cursor, removed per-line padding, single TextField cursor |
| `app/lib/models/query_clause.dart` | Added t_any_country_codes to knownFields |
| `app/lib/models/location_entity.dart` | Added countryCodes getter |
| `app/test/widget_test.dart` | Added 3 country code tests (9 total) |
| `pipeline/scripts/backfill_country_codes.py` | NEW - country code backfill script |

---

## Interventions

**0** - Zero-intervention execution.
