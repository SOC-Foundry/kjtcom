# kjtcom - Plan v9.33 (Phase 9 - Parser Regression + Quotes + Operators)

**Pipeline:** kjtcom
**Phase:** 9 (App Optimization)
**Iteration:** 33 (global counter)
**Executor:** Claude Code
**Machine:** NZXTcos
**Date:** April 2026

---

## Section A: Pre-Flight (Human)

```fish
cd ~/dev/projects/kjtcom
git add . && git commit -m "KT 9.32 shows fix + operators + detail sort" && git push
mv docs/kjtcom-design-v9.32.md docs/kjtcom-plan-v9.32.md docs/kjtcom-build-v9.32.md docs/kjtcom-report-v9.32.md docs/archive/
cp ~/Downloads/kjtcom-design-v9.33.md docs/
cp ~/Downloads/kjtcom-plan-v9.33.md docs/
cp ~/Downloads/CLAUDE.md ./CLAUDE.md
cd app && flutter pub get && flutter build web && flutter analyze && flutter test
cd ..
claude --dangerously-skip-permissions
```

---

## Section B: Claude Code Execution

### Step 1: Read Design Doc

Read `docs/kjtcom-design-v9.33.md`. Note: W1 (parser fix) MUST deploy before anything else.

### Step 2: W1 - Fix Parser Regression (P0 - DEPLOY IMMEDIATELY)

```fish
cat app/lib/models/query_clause.dart
```

Read the ENTIRE file. Find the regex. The v9.32 unquoted value regex is matching before the quoted regex.

**Fix:** Two separate regex patterns. Try quoted FIRST, unquoted as FALLBACK.

**Write a test FIRST:**
```dart
// In widget_test.dart
test('QueryClause parses quoted value', () {
  final clause = QueryClause.parse('| where t_any_keywords contains "geology"');
  expect(clause, isNotNull);
  expect(clause!.field, 't_any_keywords');
  expect(clause.operator, 'contains');
  expect(clause.value, 'geology');
});

test('QueryClause parses unquoted value', () {
  final clause = QueryClause.parse('| where t_any_keywords contains geology');
  expect(clause, isNotNull);
  expect(clause!.value, 'geology');
});
```

Run `flutter test` - the quoted test should FAIL (confirming the regression).
Fix the regex. Run `flutter test` - both tests should PASS.

```fish
cd ~/dev/projects/kjtcom/app
flutter build web
cd ..
firebase deploy --only hosting
```

**STOP. Verify on live site:** `t_any_keywords contains "geology"` returns results.
If it doesn't, DO NOT proceed. Fix until it works.

### Step 3: W2 - Restore Quotes + Fix Cursor (P0)

```fish
cat app/lib/widgets/query_editor.dart
```

Read ENTIRE file. Find the ref.listen callback. Print the exact code.

**Implement programmaticUpdateProvider flag:**

1. Add to query_provider.dart: `final programmaticUpdateProvider = StateProvider<bool>((ref) => false);`

2. In query_editor.dart ref.listen:
```dart
ref.listen(queryProvider, (_, next) {
  if (ref.read(programmaticUpdateProvider)) return;
  if (controller.text != next) {
    controller.text = next;
  }
});
```

3. In schema_tab.dart, restore quotes and set cursor:
```dart
ref.read(programmaticUpdateProvider.notifier).state = true;
controller.text = newText;  // includes ""
controller.selection = TextSelection.collapsed(offset: newText.length - 1);
ref.read(queryProvider.notifier).setText(newText);
Future.microtask(() => ref.read(programmaticUpdateProvider.notifier).state = false);
```

4. Add debugPrint in ref.listen to trace behavior.

flutter analyze + flutter test.

### Step 4: W3 - +filter ==, -exclude != (P0)

```fish
grep -n "appendClause\|contains\|filter\|exclude" app/lib/widgets/detail_panel.dart
```

Change +filter to use `==` operator.
Change -exclude to use `!=` operator.
Both must use programmaticUpdateProvider flag.

flutter analyze + flutter test.

### Step 5: W5 - Flutter Dependency Upgrade (P1)

```fish
cd ~/dev/projects/kjtcom/app
flutter pub upgrade --major-versions
flutter analyze
```

If >50 analyzer errors: REVERT pubspec.yaml changes and DEFER.
If manageable: fix errors, flutter test, proceed.

### Step 6: Final Deploy + Live Verification (MANDATORY)

```fish
cd ~/dev/projects/kjtcom/app
flutter build web
cd ..
firebase deploy --only hosting
```

**Verify on kylejeromethompson.com:**

| # | Test | Expected |
|---|------|----------|
| 1 | `t_any_keywords contains "geology"` | Returns results (NOT parse error) |
| 2 | `t_any_cuisines contains "barbecue"` | Returns 60 results with TD dots |
| 3 | `t_any_shows contains "diners, drive-ins and dives"` | Returns 1,100 |
| 4 | Schema tab -> t_any_cuisines -> cursor between quotes | User can type "french" inside quotes |
| 5 | Click entity -> +filter on a field | Appends `== "value"` |
| 6 | Click entity -> -exclude on a field | Appends `!= "value"` |
| 7 | debugPrint in console shows flag behavior | programmatic=true when schema builder fires |

### Step 7: Artifacts

Produce 4 mandatory artifacts. HONEST pass/fail. If quotes cursor still doesn't work, mark FAIL and recommend Gemini CLI for next iteration.

Do NOT git commit or push.

---

## Section D: Launch Prompt

```
Read CLAUDE.md, then read docs/kjtcom-design-v9.33.md (CRITICAL: parser regression section) and docs/kjtcom-plan-v9.33.md.

v9.32 introduced a parser regression: the unquoted value regex broke quoted value parsing. Valid queries like t_any_keywords contains "geology" now fail.

Execute Section B in STRICT order:
1. W1 FIRST: cat query_clause.dart completely. Find the regex. Write a test for quoted values that FAILS. Fix the regex (quoted pattern first, unquoted fallback). Test passes. Build + deploy IMMEDIATELY. Verify "geology" query works on live site before proceeding.
2. W2: cat query_editor.dart completely. Find ref.listen. Create programmaticUpdateProvider flag. Restore quotes in schema builder. Set cursor between quotes. ref.listen skips when flag is true.
3. W3: Change +filter to ==, -exclude to !=. Use the flag.
4. W5: flutter pub upgrade --major-versions. If >50 errors, revert and defer.
5. Final deploy + verify all 7 tests.
6. Produce artifacts. If quotes cursor STILL doesn't work after the flag approach, mark FAIL and recommend Gemini CLI.
```
