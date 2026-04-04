# kjtcom - Plan v9.30 (Phase 9 - Autocomplete + Quote Fix + Limit Fix)

**Pipeline:** kjtcom (cross-pipeline location intelligence platform)
**Phase:** 9 (App Optimization)
**Iteration:** 30 (global counter)
**Executor:** Claude Code
**Machine:** NZXTcos
**Date:** April 2026

---

## Section A: Pre-Flight (Human)

```fish
cd ~/dev/projects/kjtcom
mv docs/kjtcom-design-v9.29.md docs/kjtcom-plan-v9.29.md docs/kjtcom-build-v9.29.md docs/kjtcom-report-v9.29.md docs/archive/
cp ~/Downloads/kjtcom-design-v9.30.md docs/
cp ~/Downloads/kjtcom-plan-v9.30.md docs/
cp ~/Downloads/CLAUDE.md ./CLAUDE.md
cd app && flutter pub get && flutter build web && flutter analyze && flutter test
cd ..
claude --dangerously-skip-permissions
```

---

## Section B: Claude Code Execution

### Step 1: Read Design Doc

Read `docs/kjtcom-design-v9.30.md` for all 4 work items.

### Step 2: W1 - Fix 1000-Result Limit (P0)

**DIAGNOSTIC FIRST - do not skip this:**

```fish
grep -rn "limit\|\.limit\|_queryLimit\|1000" app/lib/providers/firestore_provider.dart
```

Read the ENTIRE file. Identify EVERY line that caps results. Remove ALL of them.

Also check:
```fish
grep -rn "1000\|isTruncated\|truncat" app/lib/widgets/results_table.dart
```

After removing limits:
- `QueryResult.isTruncated` should always be false or the field should be removed
- Result count badge shows `entities.length` (the true count)
- Remove the orange "Showing 1000 of 1000+ results" indicator entirely

flutter analyze + flutter test.

**Verify:** Run a Firestore query via Python to confirm true count, then compare with app:
```fish
python3 -u -c "
from google.cloud import firestore
import os
os.environ.setdefault('GOOGLE_APPLICATION_CREDENTIALS', os.path.expanduser('~/.config/gcloud/kjtcom-sa.json'))
db = firestore.Client(project='kjtcom-c78cd')
count = sum(1 for _ in db.collection('locations').where('t_any_keywords', 'array_contains', 'medieval').stream())
print(f'medieval: {count}')
count = sum(1 for _ in db.collection('locations').where('t_any_states', 'array_contains', 'ca').stream())
print(f'ca: {count}')
"
```

### Step 3: W2 - Fix Quote Typing (P0)

**Files:** `app/lib/widgets/query_editor.dart`, `app/lib/providers/query_provider.dart`, `app/lib/widgets/schema_tab.dart`, `app/lib/widgets/detail_panel.dart`

1. Create or expose the TextEditingController via a provider:

```dart
// In query_provider.dart or a new file
final queryTextControllerProvider = Provider<TextEditingController>((ref) {
  final controller = TextEditingController();
  // Sync controller text with queryProvider state
  ref.listen(queryProvider, (_, next) {
    if (controller.text != next) {
      controller.text = next;
    }
  });
  return controller;
});
```

2. Update `query_editor.dart` to use this shared controller instead of its own.

3. Update `schema_tab.dart` "+ Add to query" handler:

```dart
void _addFieldToQuery(String field, String op, WidgetRef ref) {
  final controller = ref.read(queryTextControllerProvider);
  final clause = op == '==' ? '| where $field == ""' : '| where $field contains ""';
  final current = controller.text.trimRight();
  final newText = current.isEmpty ? clause : '$current\n$clause';
  controller.text = newText;
  // Place cursor between quotes (1 char before end)
  final cursorPos = newText.length - 1;
  controller.selection = TextSelection.collapsed(offset: cursorPos);
  // Sync provider
  ref.read(queryProvider.notifier).state = newText;
  // Switch to Results tab
  ref.read(activeTabProvider.notifier).state = 0;
}
```

4. Update `detail_panel.dart` +filter/-exclude to also use the shared controller for proper cursor positioning.

flutter analyze + flutter test.

### Step 4: W4 - Consistent Trident Labels (P1)

**File:** `app/lib/widgets/iao_tab.dart`

Search for "Minimal cost", "Speed of delivery", "Optimized performance" in the file. Replace ALL instances with "Cost", "Delivery", "Performance" regardless of viewport/breakpoint logic.

flutter analyze + flutter test.

### Step 5: W3 - Generate Value Index (P1)

**New script:** `pipeline/scripts/generate_value_index.py`

```fish
python3 -u pipeline/scripts/generate_value_index.py
```

The script:
1. Reads all 6,181 entities from production
2. For each t_any_* array field, collects distinct values
3. Also collects t_log_type distinct values
4. Sorts each value list alphabetically
5. Caps at 500 values per field
6. Outputs to `app/assets/value_index.json`

After generating, verify the file:
```fish
python3 -c "import json; d=json.load(open('app/assets/value_index.json')); print(f'Fields: {len(d)}'); [print(f'  {k}: {len(v)} values') for k,v in sorted(d.items())]"
```

### Step 6: W3 - Autocomplete Widget (P1)

**New file:** `app/lib/widgets/query_autocomplete.dart`
**Update:** `app/lib/widgets/query_editor.dart`

1. Create `query_autocomplete.dart`:
   - Loads value_index.json via rootBundle on first use, caches in a provider
   - `AutocompleteOverlay` widget: positioned below cursor line
   - Two modes:
     - **Field mode:** active when current word starts with `t_` or `t_any_`. Suggestions from knownFields.
     - **Value mode:** active when cursor is inside quotes after a known field + operator. Suggestions from value_index for that field.
   - Filter by prefix as user types
   - Tab or click to accept (replaces current partial with full suggestion)
   - Down/Up arrow to navigate, Escape to dismiss
   - Max 8 visible suggestions, scrollable
   - Styled: dark bg (#1C2128), tech green border, Geist Mono

2. Integrate into `query_editor.dart`:
   - On each keystroke, determine if autocomplete should show
   - Position overlay relative to cursor
   - Handle Tab key for acceptance

flutter analyze + flutter test.

### Step 7: Post-Flight Deploy + Live Verification (MANDATORY)

```fish
cd ~/dev/projects/kjtcom/app
flutter build web
cd ..
firebase deploy --only hosting
```

**Verify on kylejeromethompson.com:**

| # | Test | Expected |
|---|------|----------|
| 1 | `t_any_keywords contains "medieval"` | Shows true count (653), NOT "1000+" |
| 2 | `t_any_states contains "ca"` | Shows true count, NOT capped |
| 3 | Schema tab -> click t_any_cuisines | Clause appended, cursor BETWEEN quotes |
| 4 | Type "french" between quotes | Text appears correctly |
| 5 | Type `t_any_c` on new line | Autocomplete dropdown shows matching fields |
| 6 | Tab to accept field suggestion | Full field name inserted |
| 7 | Type `t_any_cuisines contains "me` | Value suggestions: mexican, mediterranean |
| 8 | IAO tab trident | "Cost", "Delivery", "Performance" on desktop |
| 9 | IAO tab trident (resize to mobile) | Same short labels |

### Step 8: Security Scan + Artifacts

Produce all 4 mandatory artifacts. Do NOT git commit or push.

---

## Section C: CLAUDE.md for v9.30

```markdown
# kjtcom - Agent Instructions (Claude Code)

## Read Order

1. docs/kjtcom-design-v9.30.md (4 work items + gotcha registry)
2. docs/kjtcom-plan-v9.30.md (execute Section B)

## Context

Phase 9 iteration. Four work items:
- W1 (P0): Remove Firestore 1000-result limit (2nd attempt - grep for ALL limit references)
- W2 (P0): Fix quote cursor placement (3rd attempt - TextEditingController via provider)
- W3 (P1): Query autocomplete (field names + values from precomputed index)
- W4 (P1): Consistent trident labels ("Cost", "Delivery", "Performance" all viewports)

kjtcom project ID: kjtcom-c78cd
Production: 6,181 entities
Live: kylejeromethompson.com

## Shell - MANDATORY

- All commands in fish shell
- NEVER cat config.fish or SA JSON files (G20, G11)

## Security

- grep -rnI "AIzaSy" . before completion

## Flutter Requirements

- flutter analyze + flutter test after every change
- Build: cd app && flutter build web
- Deploy: cd ~/dev/projects/kjtcom && firebase deploy --only hosting

## Post-Flight Deploy (MANDATORY)

1. flutter build web
2. firebase deploy --only hosting
3. Verify ALL 9 tests on live site
4. Document in build log

## CRITICAL: Limit Fix (W1)

Run `grep -rn "limit\|\.limit\|_queryLimit\|1000" app/lib/providers/firestore_provider.dart` FIRST.
Read the ENTIRE file. Remove EVERY limit. The result count must show the true total.
Also verify with a Python Firestore query to confirm expected counts.

## CRITICAL: Quote Fix (W2)

Expose TextEditingController via provider. Schema builder and +filter/-exclude must use this controller to:
1. Set controller.text with the new clause
2. Set controller.selection to place cursor between quotes
3. Sync queryProvider.state to match

## Autocomplete (W3)

Generate value_index.json via pipeline/scripts/generate_value_index.py first.
Then build autocomplete overlay: field mode (t_any_ prefix) + value mode (inside quotes).
Tab to accept, Escape to dismiss.

## Permissions

- CANNOT: git add / commit / push
- CANNOT: sudo

## Artifact Rules - MANDATORY

1. docs/kjtcom-build-v9.30.md (include live verification results)
2. docs/kjtcom-report-v9.30.md
3. docs/kjtcom-changelog.md (append v9.30)
4. README.md (update if needed)

## Formatting

- No em-dashes. Use " - " instead.
- Use "->" for arrows.
```

---

## Section D: Launch Prompt

```
Read CLAUDE.md, then read docs/kjtcom-design-v9.30.md for all 4 work items and docs/kjtcom-plan-v9.30.md for execution order.

Execute Section B:
1. W1 (P0): grep for ALL limit/1000 references in firestore_provider.dart. Read the entire file. Remove EVERY limit. Also grep results_table.dart for truncation logic. Verify expected counts via Python Firestore query.
2. W2 (P0): Create a shared TextEditingController provider. Update query_editor.dart to use it. Update schema_tab.dart to set cursor position between quotes after appending clause. Update detail_panel.dart similarly.
3. W4 (P1): Replace all trident label strings in iao_tab.dart with "Cost", "Delivery", "Performance".
4. W3 (P1): Create generate_value_index.py, run it to produce app/assets/value_index.json. Create query_autocomplete.dart overlay widget. Integrate into query_editor.dart with field mode + value mode.
5. flutter analyze + flutter test after each work item.
6. MANDATORY: flutter build web + firebase deploy + verify ALL 9 tests on live site.
7. Produce all 4 mandatory artifacts with live verification results.
```

---

## Timing Estimate

| Step | Est. Duration |
|------|---------------|
| Pre-flight | ~5 min |
| W1 (limit fix) | ~15 min |
| W2 (quote fix) | ~30 min |
| W4 (trident labels) | ~5 min |
| W3 (value index + autocomplete) | ~90 min |
| Deploy + verify | ~15 min |
| Artifacts | ~15 min |
| **Total** | **~3-3.5 hours** |
