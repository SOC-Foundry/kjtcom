# kjtcom - Plan v9.34 (Phase 9 - Gemini: Quote Cursor + Inline Autocomplete)

**Pipeline:** kjtcom
**Phase:** 9 (App Optimization)
**Iteration:** 34 (global counter)
**Executor:** Gemini CLI
**Machine:** NZXTcos
**Date:** April 2026

---

## Section A: Pre-Flight (Human)

```fish
cd ~/dev/projects/kjtcom
git add . && git commit -m "KT 9.33 parser fix + quotes + operators" && git push
mv docs/kjtcom-design-v9.33.md docs/kjtcom-plan-v9.33.md docs/kjtcom-build-v9.33.md docs/kjtcom-report-v9.33.md docs/archive/
cp ~/Downloads/kjtcom-design-v9.34.md docs/
cp ~/Downloads/kjtcom-plan-v9.34.md docs/
cp ~/Downloads/GEMINI.md ./GEMINI.md
cd app && flutter pub upgrade && flutter pub get && flutter build web && flutter analyze && flutter test
cd ..
gemini --yolo
```

---

## Section B: Gemini CLI Execution

### Step 1: Read Design + Plan

Read docs/kjtcom-design-v9.34.md and this plan.

### Step 2: W1 - Fix Quote Cursor (P0)

Diagnostic:
```fish
fish -c "cat app/lib/widgets/query_editor.dart"
fish -c "cat app/lib/providers/query_provider.dart"
fish -c "grep -n 'controller\|selection\|cursor\|programmatic' app/lib/widgets/schema_tab.dart"
```

Find every code path that touches controller.text or controller.selection.
Find the ref.listen callback and the programmaticUpdateProvider flag.

The flag approach from v9.33 should work in theory. Diagnose why it doesn't:
- Is the flag being set correctly?
- Is ref.listen actually checking it?
- Is something ELSE resetting the cursor (TextField onChanged, syntax highlighter rebuild)?

Try: set selection via `WidgetsBinding.instance.addPostFrameCallback`:
```dart
WidgetsBinding.instance.addPostFrameCallback((_) {
  controller.selection = TextSelection.collapsed(offset: cursorPos);
});
```

This defers the selection set to AFTER the current frame renders, which should survive any mid-frame cursor resets.

### Step 3: W2 - Inline Autocomplete (P0)

Remove the overlay-based autocomplete (query_autocomplete.dart OverlayEntry approach).

Replace with an inline widget in the query editor Column:
- Rendered BELOW the query lines, ABOVE the help text
- Small container: dark bg, thin border, 2-5 rows
- Each row: suggestion text + type label
- Tab accepts, arrows navigate, Escape dismisses
- Field mode: matches knownFields on t_ prefix
- Value mode: matches value_index.json values after operator

### Step 4: W3 - Fix +filter/-exclude Operators (P1)

In detail_panel.dart:
- Array fields (t_any_*): +filter uses `contains`, -exclude uses `!= contains` (or a NOT clause)
- Scalar fields (t_log_type): +filter uses `==`, -exclude uses `!=`

### Step 5: Build + Deploy + Verify

```fish
fish -c "cd app && flutter build web"
fish -c "cd ~/dev/projects/kjtcom && firebase deploy --only hosting"
```

### Step 6: Artifacts

Produce:
1. docs/kjtcom-build-v9.34.md
2. docs/kjtcom-report-v9.34.md
3. docs/kjtcom-changelog.md (append v9.34)
4. README.md (update if needed)

Do NOT git commit or push.

---

## Section D: Launch Prompt

```
Read GEMINI.md for agent instructions, then read docs/kjtcom-design-v9.34.md and docs/kjtcom-plan-v9.34.md.

Three work items:
1. W1 (P0): Fix quote cursor in query editor. 6 previous attempts with Claude Code failed. The programmaticUpdateProvider flag exists but cursor still resets. Try WidgetsBinding.instance.addPostFrameCallback for deferred selection.
2. W2 (P0): Replace overlay autocomplete with INLINE suggestions below query text (Panther SIEM style). Render as a widget in the Column, not an OverlayEntry.
3. W3 (P1): Fix +filter/-exclude to use correct operator per field type (contains for arrays, == for scalars).

Execute in order. Build + deploy after each fix. Produce 4 mandatory artifacts.
```

---

## Timing Estimate

| Step | Est. Duration |
|------|---------------|
| Pre-flight | ~10 min |
| W1 (cursor fix) | ~45 min |
| W2 (inline autocomplete) | ~60 min |
| W3 (operators) | ~15 min |
| Deploy + verify | ~15 min |
| Artifacts | ~15 min |
| **Total** | **~2.5-3 hours** |
