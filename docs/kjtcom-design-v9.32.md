# kjtcom - Design v9.32 (Phase 9 - Shows Fix + Operators + Detail Sort + Quote Rethink)

**Pipeline:** kjtcom (cross-pipeline location intelligence platform)
**Phase:** 9 (App Optimization)
**Iteration:** 32 (global counter)
**Executor:** Claude Code
**Machine:** NZXTcos
**Date:** April 2026

---

## Objective

Six work items:

1. **TripleDB t_any_shows casing data fix** - TripleDB entities store t_any_shows as title case. Lowercase all values.
2. **Add == and != operators** - equality and exclusion operators for the query parser.
3. **Sort detail panel fields alphabetically** - t_any_* field cards render in alphabetical order.
4. **Quote cursor: new approach (attempt #5)** - schema builder appends WITHOUT quotes. User types their own.
5. **Fix autocomplete (attempt #2)** - diagnostic-first to find why overlay doesn't show.
6. **Comprehensive lowercase ALL t_any_* data** - permanent G36 resolution across all 6,181 entities.

---

## Work Items

### W1: TripleDB t_any_shows Data Fix (P0)

**Script:** `pipeline/scripts/fix_tripledb_shows_case.py`

Same pattern as CalGold fix from v8.23 W3. Read TripleDB entities, lowercase t_any_shows, batch write.
Expected: "Diners, Drive-Ins and Dives" -> "diners, drive-ins and dives" on 1,100 entities.

### W2: Add == and != Operators (P1)

**Files:** `app/lib/models/query_clause.dart`, `app/lib/providers/firestore_provider.dart`

- `==` on scalar: Firestore isEqualTo (server-side)
- `!=` on scalar: Firestore isNotEqualTo (server-side)
- `!=` on array: client-side filter (exclude matching entities)
- Show hint if user uses `==` on t_any_* field (suggest contains instead)

### W3: Sort Detail Panel Fields Alphabetically (P1)

**File:** `app/lib/widgets/detail_panel.dart`

Sort t_any_* entries by key before rendering. Simple `.sort()` on the map entries.

### W4: Quote Cursor - No Quotes Approach (P0)

**Files:** `app/lib/widgets/schema_tab.dart`, `app/lib/models/query_clause.dart`

Schema builder appends: `| where t_any_cuisines contains ` (trailing space, NO quotes)
User types: `"french"` or just `french`

Update parser regex to accept unquoted values:
- `field operator "value"` -> value (existing)
- `field operator value` -> value (to end of line, new)

### W5: Fix Autocomplete (P1 - attempt #2)

Diagnostic-first:
1. Verify value_index.json in pubspec assets and build output
2. Check overlay creation and detection logic
3. Add debugPrint at detection entry point
4. Fix based on findings

### W6: Comprehensive Lowercase Data Fix (P1)

**Script:** `pipeline/scripts/fix_all_lowercase.py`

Lowercase ALL string values in ALL t_any_* array fields across ALL 6,181 entities. Permanent G36 resolution.

---

## Success Criteria

| Criteria | Target |
|----------|--------|
| t_any_shows "diners, drive-ins and dives" returns 1,100 | Yes |
| == works on t_log_type | Yes |
| != works (server for scalar, client for array) | Yes |
| Detail panel fields sorted alphabetically | Yes |
| Schema builder appends without quotes, user types value | Yes |
| Autocomplete appears | Yes (or documented blocker) |
| All t_any_* data lowercase | Yes |
| flutter analyze | 0 issues |
| flutter test | All pass |
| firebase deploy + live verify | Success |

---

## Complete Gotcha Registry

| ID | Gotcha | Prevention | Status |
|----|--------|-----------|--------|
| G1 | Heredocs in fish | printf blocks | ACTIVE |
| G2 | CUDA LD_LIBRARY_PATH | config.fish | RESOLVED |
| G11 | API key leaks | NEVER cat | ACTIVE |
| G18 | Gemini timeout | Background jobs | ACTIVE |
| G19 | Gemini bash default | fish -c | ACTIVE |
| G20 | Config.fish keys | grep only | ACTIVE |
| G21 | CUDA OOM | Sequential | ACTIVE |
| G22 | Fish ls colors | command ls | ACTIVE |
| G23 | LD_LIBRARY_PATH | config.fish | RESOLVED |
| G24 | Checkpoint staleness | Reset | ACTIVE |
| G30 | Cross-project SA | Verify files | ACTIVE |
| G31 | TripleDB schema drift | Inspect data | RESOLVED |
| G32 | Production rules | Verify IAM | ACTIVE |
| G33 | Duplicate IDs | Deterministic t_row_id | ACTIVE |
| G34 | Single array-contains | Client-side additional | ACTIVE |
| G35 | Production write safety | --dry-run | ACTIVE |
| G36 | Case-sensitive arrayContains | W6 permanent fix | RESOLVING |
| G37 | t_any_shows casing | CalGold v8.23, TripleDB W1 | RESOLVING |
| G38 | Firebase deploy auth | login --reauth | ACTIVE |
| G39 | Detail panel provider | All viewports | RESOLVED |
| G40 | Compound country names | Manual split | DOCUMENTED |
| G41 | Rebuild handlers | Dedup + guard | RESOLVED |
| G42 | Rotating queries | Removed | RESOLVED |
| G43 | Map tile CORS | Test renderers | ACTIVE |
| G44 | flutter_map compat | Check pub.dev | ACTIVE |
| G45 | Schema cursor | ABANDONED - no quotes approach | RESOLVED |
| G46 | Firestore limit | Removed v9.31 | RESOLVED |
| G47 | CanvasKit Playwright | mouse.click or screenshots | ACTIVE |
| G48 | Fix without live verify | Require evidence | ACTIVE |
| G49 | TripleDB shows title case | W1 data fix | RESOLVING |
