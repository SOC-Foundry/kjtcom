# kjtcom - Plan v9.32 (Phase 9 - Shows Fix + Operators + Detail Sort + Quote Rethink)

**Pipeline:** kjtcom
**Phase:** 9 (App Optimization)
**Iteration:** 32 (global counter)
**Executor:** Claude Code
**Machine:** NZXTcos
**Date:** April 2026

---

## Section A: Pre-Flight (Human)

```fish
cd ~/dev/projects/kjtcom
git add . && git commit -m "KT 9.31 persistent bug fixes" && git push
mv docs/kjtcom-design-v9.31.md docs/kjtcom-plan-v9.31.md docs/kjtcom-build-v9.31.md docs/kjtcom-report-v9.31.md docs/archive/
cp ~/Downloads/kjtcom-design-v9.32.md docs/
cp ~/Downloads/kjtcom-plan-v9.32.md docs/
cp ~/Downloads/CLAUDE.md ./CLAUDE.md
cd app && flutter pub upgrade && flutter pub get && flutter build web && flutter analyze && flutter test
cd ..
claude --dangerously-skip-permissions
```

---

## Section B: Claude Code Execution

### Step 1: Read Design Doc

Read `docs/kjtcom-design-v9.32.md` for all 6 work items.

### Step 2: W1 - TripleDB t_any_shows Data Fix (P0)

Create `pipeline/scripts/fix_tripledb_shows_case.py`:

```fish
python3 -u pipeline/scripts/fix_tripledb_shows_case.py --dry-run --limit 5
python3 -u pipeline/scripts/fix_tripledb_shows_case.py
```

Verify: `t_any_shows contains "diners, drive-ins and dives"` returns 1,100 via Python Firestore query.

### Step 3: W6 - Comprehensive Lowercase Data Fix (P1)

Create `pipeline/scripts/fix_all_lowercase.py`:

```fish
python3 -u pipeline/scripts/fix_all_lowercase.py --dry-run --limit 10
python3 -u pipeline/scripts/fix_all_lowercase.py
```

This permanently resolves G36 for all entities.

### Step 4: W4 - Quote Cursor New Approach (P0)

**File:** `app/lib/widgets/schema_tab.dart`

Change "+ Add to query" to append WITHOUT quotes:
- `| where t_any_cuisines contains ` (trailing space, no quotes)
- `| where t_log_type == ` (trailing space, no quotes)

**File:** `app/lib/models/query_clause.dart`

Update parser regex to accept values with OR without quotes:
- `t_any_cuisines contains "french"` -> value: french
- `t_any_cuisines contains french` -> value: french
- `t_any_cuisines contains french toast` -> value: french toast (to end of line)

flutter analyze + flutter test.

### Step 5: W2 - Add == and != Operators (P1)

**Files:** `app/lib/models/query_clause.dart`, `app/lib/providers/firestore_provider.dart`

Add `!=` to parser regex (alongside existing ==, contains, contains-any).

In firestore_provider:
- `!=` on scalar field (t_log_type): Firestore `isNotEqualTo` server-side
- `!=` on array field (t_any_*): client-side filter (exclude entities where array contains value)

flutter analyze + flutter test.

### Step 6: W3 - Sort Detail Panel Fields (P1)

**File:** `app/lib/widgets/detail_panel.dart`

Sort t_any_* field entries alphabetically by key before rendering cards.

flutter analyze + flutter test.

### Step 7: W5 - Fix Autocomplete (P1)

Diagnostic first:
```fish
ls -la app/assets/value_index.json
grep -A 5 "assets:" app/pubspec.yaml
grep -n "detect\|_showOverlay\|_hideOverlay\|AutocompleteContext" app/lib/widgets/query_autocomplete.dart
grep -n "autocomplete\|_overlayEntry" app/lib/widgets/query_editor.dart
```

Fix based on diagnostic findings. Add debugPrint at detection entry point.

flutter analyze + flutter test.

### Step 8: Post-Flight Deploy + Live Verification (MANDATORY)

```fish
cd ~/dev/projects/kjtcom/app
flutter build web
cd ..
firebase deploy --only hosting
```

**Verify on kylejeromethompson.com:**

| # | Test | Expected |
|---|------|----------|
| 1 | `t_any_shows contains "diners, drive-ins and dives"` | Returns 1,100 results |
| 2 | `t_log_type == "tripledb"` | Returns 1,100 results |
| 3 | `t_log_type != "calgold"` | Returns ~5,282 results (ricksteves + tripledb) |
| 4 | Schema tab -> click t_any_cuisines -> type french | Works without quote issues |
| 5 | Detail panel fields sorted | t_any_actors before t_any_categories before t_any_cities... |
| 6 | Autocomplete on t_any_c | Dropdown appears (or documented blocker) |

### Step 9: Security Scan + Artifacts

Produce all 4 mandatory artifacts. HONEST pass/fail on each test.

Do NOT git commit or push.

---

## Section C: CLAUDE.md for v9.32

```markdown
# kjtcom - Agent Instructions (Claude Code)

## Read Order

1. docs/kjtcom-design-v9.32.md (6 work items + gotcha registry)
2. docs/kjtcom-plan-v9.32.md (execute Section B)

## Context

Phase 9 iteration. Six work items:
- W1 (P0): Lowercase TripleDB t_any_shows (data fix - same as CalGold v8.23 W3)
- W2 (P1): Add == and != operators to parser + provider
- W3 (P1): Sort detail panel fields alphabetically
- W4 (P0): Schema builder appends WITHOUT quotes (user types their own)
- W5 (P1): Fix autocomplete overlay (diagnostic first)
- W6 (P1): Comprehensive lowercase ALL t_any_* data across all entities

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
3. Verify ALL 6 tests on live site
4. HONEST pass/fail in report (G48)

## Key Fix Details

W1: Create fix_tripledb_shows_case.py. --dry-run first. Lowercase 1,100 entities.

W4: Schema builder appends `| where field contains ` (NO QUOTES, trailing space). User types value with their own quotes. Update parser to accept unquoted values too.

W6: Create fix_all_lowercase.py. Lowercase ALL string values in ALL t_any_* arrays across ALL 6,181 entities. Permanent G36 resolution.

## Permissions

- CANNOT: git add / commit / push
- CANNOT: sudo

## Artifact Rules - MANDATORY

1. docs/kjtcom-build-v9.32.md
2. docs/kjtcom-report-v9.32.md (honest pass/fail)
3. docs/kjtcom-changelog.md (append v9.32)
4. README.md (update if needed)

## Formatting

- No em-dashes. Use " - " instead.
- Use "->" for arrows.
```

---

## Section D: Launch Prompt

```
Read CLAUDE.md, then read docs/kjtcom-design-v9.32.md and docs/kjtcom-plan-v9.32.md.

Execute Section B:
1. W1: Create fix_tripledb_shows_case.py, dry-run, full run. Verify via Python Firestore query.
2. W6: Create fix_all_lowercase.py, dry-run, full run. Permanent G36 fix.
3. W4: Change schema_tab.dart to append clauses WITHOUT quotes. Update query_clause.dart regex to accept unquoted values.
4. W2: Add != operator to parser and provider. == should already work.
5. W3: Sort detail_panel.dart t_any_* fields alphabetically.
6. W5: Diagnostic-first autocomplete fix.
7. Build + deploy + verify all 6 tests on live site.
8. Produce artifacts with honest pass/fail.
```

---

## Timing Estimate

| Step | Est. Duration |
|------|---------------|
| Pre-flight | ~10 min |
| W1 + W6 (data fixes) | ~20 min |
| W4 (quote approach) | ~15 min |
| W2 (operators) | ~20 min |
| W3 (sort) | ~5 min |
| W5 (autocomplete) | ~30 min |
| Deploy + verify | ~15 min |
| Artifacts | ~15 min |
| **Total** | **~2-2.5 hours** |
