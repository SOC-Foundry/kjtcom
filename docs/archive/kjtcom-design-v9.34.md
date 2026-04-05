# kjtcom - Design v9.34 (Phase 9 - Gemini: Quote Cursor + Inline Autocomplete)

**Pipeline:** kjtcom (cross-pipeline location intelligence platform)
**Phase:** 9 (App Optimization)
**Iteration:** 34 (global counter)
**Executor:** Gemini CLI (Flutter-native agent for Dart/Flutter work)
**Machine:** NZXTcos
**Date:** April 2026

---

## Why Gemini CLI

Claude Code failed the quote cursor fix across 6 iterations (v9.28-v9.33). The issue is Flutter TextField cursor management — a Dart/Flutter-native problem. Gemini CLI is Google-native for Flutter/Dart and has been proven on kjtcom through phases 1-5 (zero-intervention split-agent model).

The autocomplete overlay approach was also wrong. The reference implementation (Panther SIEM, screenshots provided) uses INLINE suggestions below the cursor text — not a floating overlay box that obscures the query.

---

## Objective

Three focused work items. No data fixes, no new features. Fix what's broken.

1. **(P0) Fix quote cursor placement** - when schema builder or +filter/-exclude appends a clause with `""`, the cursor MUST land between the quotes so the user can type a value. 6 previous attempts failed because ref.listen in query_editor.dart overrides cursor position. A programmaticUpdateProvider flag was added in v9.33 but the cursor still doesn't land correctly. Gemini must diagnose the actual runtime behavior and fix it.

2. **(P0) Inline autocomplete (Panther-style)** - replace the overlay-based autocomplete with inline suggestions rendered BELOW the query text in the editor area. See Panther SIEM reference: suggestions appear as a dropdown anchored directly below the current line, showing field names or values. The suggestions are compact (no borders or heavy styling) and don't obscure the query text. Tab to accept, typing filters.

3. **(P1) Fix == on array fields** - the +filter button now uses `==` but `==` on array fields (t_any_*) matches the ENTIRE array, not membership. For array fields, +filter should use `contains` (exact membership). For scalar fields (t_log_type), +filter should use `==`. -exclude should use `!=` for scalar and a client-side NOT contains for array.

---

## Reference: Panther SIEM Autocomplete

From the Panther screenshots:
- Suggestions appear INLINE, directly below the text being typed
- Small dropdown with a subtle border, dark background matching the editor
- Shows 2-5 suggestions max
- Each suggestion shows the value + type label on the right (e.g., "ta_" and "table")
- "Insert" hint and "show more (Ctrl+Space)" at bottom
- Does NOT obscure the query text above
- Compact — takes minimal vertical space

Implement the same pattern in the kjtcom query editor.

---

## Technical Context

**Query editor architecture:** `app/lib/widgets/query_editor.dart`
- Stack-based: visual line display (Column of syntax-highlighted text) + Positioned.fill TextField (invisible text, visible cursor)
- TextEditingController shared via `queryTextControllerProvider` (Riverpod Provider)
- `ref.listen(queryProvider, ...)` syncs external state changes to the controller
- A `programmaticUpdateProvider` (StateProvider<bool>) was added in v9.33 to prevent ref.listen from overriding cursor position during programmatic updates

**Schema builder:** `app/lib/widgets/schema_tab.dart`
- "+ Add to query" appends `| where field contains ""` and attempts to place cursor between quotes
- Uses programmaticUpdateProvider flag + Future.microtask cleanup

**Autocomplete data:** `app/assets/value_index.json`
- 21 fields, ~6,800 distinct values
- Loaded via rootBundle, cached in a FutureProvider

**Known fields:** `app/lib/models/query_clause.dart` knownFields set (22 fields)

**Gotcha G45:** Quote cursor has failed 6 times. The mechanism (flag + controller.selection) is sound in isolation but something in the Flutter event loop resets the cursor.

**Gotcha G47:** Flutter CanvasKit renders to canvas, not DOM. Playwright can't interact.

---

## Work Items

### W1: Fix Quote Cursor (P0)

**The problem:** After setting `controller.text = newText` and `controller.selection = TextSelection.collapsed(offset: newText.length - 1)`, something resets the cursor to the end of text.

**Diagnostic approach:**
1. Read query_editor.dart COMPLETELY
2. Find EVERY place that touches controller.text or controller.selection
3. Check if the TextField's onChanged fires after controller.text is set (this would trigger a provider update -> ref.listen -> cursor reset)
4. Check if the syntax highlighter rebuild moves the cursor
5. Add print statements at every cursor-related code path

**Possible fixes:**
- Use `WidgetsBinding.instance.addPostFrameCallback` to set selection AFTER the frame renders
- Override TextField.onChanged to not trigger provider sync when programmatic flag is set
- Use a custom TextEditingController that preserves selection during text changes
- Set selection in a `Future.delayed(Duration.zero, ...)` instead of synchronously

### W2: Inline Autocomplete (P0)

**Replace the overlay approach entirely.** Instead of OverlayEntry + CompositedTransformFollower:

Render suggestions as a WIDGET inside the query editor's Column, below the text lines:

```dart
Column(
  children: [
    ...queryLines.map(_buildQueryLine),        // existing syntax-highlighted lines
    if (suggestions.isNotEmpty)
      _buildInlineSuggestions(suggestions),     // NEW: compact suggestion list
    _buildHelpText(),                          // existing help text
  ],
)
```

The suggestion widget:
- Container with dark background (#1C2128), thin border, compact padding
- ListView of 2-5 suggestions max
- Each row: value text (Geist Mono, small) + optional type label on right
- Highlighted current selection
- Tab to accept, Down/Up to navigate, Escape to dismiss, typing filters
- Anchored below the query text, doesn't obscure it

**Two modes:**
1. **Field mode:** cursor on a word starting with `t_` -> suggest matching field names from knownFields
2. **Value mode:** cursor after `contains "` or `== "` -> suggest matching values from value_index.json

### W3: Fix +filter/exclude Operators (P1)

**File:** detail_panel.dart

Logic:
- If field starts with `t_any_` (array field):
  - +filter: use `contains` (array membership)
  - -exclude: use `!= contains` or append a NOT clause (client-side)
- If field is `t_log_type` (scalar field):
  - +filter: use `==`
  - -exclude: use `!=`

---

## Success Criteria

| Criteria | Target |
|----------|--------|
| Cursor lands between quotes after schema builder | User types value inside quotes |
| Inline autocomplete shows below query text | Panther-style, not overlay |
| Field suggestions on t_any_ prefix | Yes |
| Value suggestions inside quotes | Yes |
| Tab accepts suggestion | Yes |
| +filter uses correct operator per field type | contains for array, == for scalar |
| -exclude uses correct operator per field type | Yes |
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
| G18 | Gemini 5-min timeout | Background jobs | ACTIVE |
| G19 | Gemini bash default | Wrap in fish -c | ACTIVE |
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
| G36 | Case-sensitive arrayContains | All lowercased | RESOLVED |
| G37 | t_any_shows casing | All lowercased | RESOLVED |
| G38 | Firebase deploy auth | login --reauth | ACTIVE |
| G39 | Detail panel provider | All viewports | RESOLVED |
| G40 | Compound country names | Manual split | DOCUMENTED |
| G41 | Rebuild handlers | Dedup + guard | RESOLVED |
| G42 | Rotating queries | Removed | RESOLVED |
| G43 | Map tile CORS | Test renderers | ACTIVE |
| G44 | flutter_map compat | Check pub.dev | ACTIVE |
| G45 | Schema cursor | 6 Claude failures. Gemini attempt. | ACTIVE |
| G46 | Firestore limit | Removed | RESOLVED |
| G47 | CanvasKit Playwright | Screenshots only | ACTIVE |
| G48 | Fix without live verify | Require evidence | ACTIVE |
| G49 | TripleDB shows case | Lowercased | RESOLVED |
| G50 | Parser regex order | Quoted first, unquoted fallback | RESOLVED |
