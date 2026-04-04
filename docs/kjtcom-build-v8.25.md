# kjtcom - Build Log v8.25 (Phase 8 - Filter Fix + README Overhaul)

**Pipeline:** kjtcom (cross-pipeline location intelligence platform)
**Phase:** 8 (Enrichment Hardening)
**Iteration:** 25 (global counter)
**Executor:** Claude Code (Opus)
**Machine:** NZXTcos
**Date:** 2026-04-03

---

## Workstream A: Fix +filter/-exclude Duplicate Bug

### Diagnostic

**File:** `app/lib/providers/query_provider.dart`
**Root cause confirmed:** `QueryNotifier.appendClause()` blindly appended clauses without checking for duplicates or guarding against re-entry. When `+filter` modified `queryProvider` state, any ancestor widget watching `queryProvider` triggered a tree rebuild. The `_FieldCard` widget held a `WidgetRef ref` from the parent `ConsumerWidget`, and during rebuild the tap event could re-fire through the reconstructed handler - producing 1-4 duplicate lines per click.

**Original code:**
```dart
void appendClause(String field, String op, String value) {
  final clause = '| where $field $op "$value"\n';
  state = '${state.trimRight()}\n$clause';
}
```

### Fix Applied

**Two-layer protection in `QueryNotifier.appendClause()`:**

1. **Dedup check:** `if (state.contains(clause)) return;` - prevents identical clauses entirely (Option A from design doc)
2. **Guard flag:** `_isAppending` boolean, set true on entry, reset via `Future.microtask()` after the event loop tick completes - prevents rebuild-triggered re-entry

**Fixed code:**
```dart
bool _isAppending = false;

void appendClause(String field, String op, String value) {
  if (_isAppending) return;
  _isAppending = true;
  try {
    final clause = '| where $field $op "$value"';
    if (state.contains(clause)) return;
    state = '${state.trimRight()}\n$clause\n';
  } finally {
    Future.microtask(() => _isAppending = false);
  }
}
```

**Why fix in the notifier, not the widget:**
- `QueryNotifier` is a Riverpod `Notifier` - it persists state naturally (no StatelessWidget -> StatefulWidget conversion needed)
- Both +filter and -exclude route through `appendClause` - single fix point
- Guard flag survives across rebuilds since it lives in the notifier, not the widget tree

### Validation

- `flutter analyze`: 0 issues
- `flutter test`: 9/9 pass
- Build: `flutter build web` -> success (16.3s)
- Deploy #1: `firebase deploy --only hosting` -> success

---

## Workstream B: README Overhaul

### Changes from Previous README

**Added sections:**
- **Live App** - link to kylejeromethompson.com with 5-bullet feature list
- **Query System** - operators, features, 8 example queries
- **App Query Flow** - second architecture diagram showing query editor -> parser -> Firestore -> results

**Updated sections:**
- **Intro paragraph** - rewrote to mention 3 pipelines, 6,181 entities, query system, live link
- **Status line** - `Phase 8 v8.25 | Status: Phase 8 Enrichment Hardening DONE`
- **Thompson Indicator Fields** - `t_any_country_codes` already present (added in v8.24), reordered next to `t_any_countries` for clarity
- **Project Status** - Phase 8 DONE v8.22-v8.25
- **Hardware** - added tsP3-cos (ThinkStation P3 Ultra SFF G2)
- **Future Directions** - updated HyperAgents (deferred to Phase 10), added Algolia/Typesense assessment (deferred), kept SIEM migration paragraph
- **Changelog** - truncated to last 5 iterations (v8.25 through v7.21), added link to full changelog

**Removed sections:**
- **Setup** - moved to developer-only docs (not needed in public README)
- **Running a Pipeline** - same
- **File Structure** - same

**Preserved verbatim:**
- IAO Methodology intro paragraph
- IAO Components table
- Split-Agent Execution section + agent performance table
- Mermaid trident chart
- All 10 IAO pillars (word-for-word)
- Data Architecture section
- Pipelines table (including bourdain pending)
- Tech Stack table
- Cost table
- Author + Citing sections

### Validation

- No em-dashes in README (verified)
- All arrows use "->" format
- Changelog links to docs/kjtcom-changelog.md

---

## Deploy Log

| # | Action | Result |
|---|--------|--------|
| 1 | `flutter analyze` | 0 issues |
| 2 | `flutter test` | 9/9 pass |
| 3 | `flutter build web` (filter fix) | success (18.0s) |
| 4 | `firebase deploy --only hosting` (filter fix) | success |
| 5 | `flutter build web` (final) | success (16.3s) |
| 6 | `firebase deploy --only hosting` (final) | success |
| 7 | Security scan: `grep -rnI "AIzaSy"` | Clean - only Firebase Web API key (public, expected) |

---

## Interventions

| # | Type | Description |
|---|------|-------------|
| - | - | None |

**Total interventions: 0**
