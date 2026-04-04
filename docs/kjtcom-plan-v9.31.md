# kjtcom - Plan v9.31 (Phase 9 - Persistent Bug Fix + Playwright Verification)

**Pipeline:** kjtcom (cross-pipeline location intelligence platform)
**Phase:** 9 (App Optimization)
**Iteration:** 31 (global counter)
**Executor:** Claude Code
**Machine:** NZXTcos
**Date:** April 2026

---

## Section A: Pre-Flight (Human)

```fish
cd ~/dev/projects/kjtcom
git add . && git commit -m "KT 9.30 autocomplete + quote fix + limit fix" && git push
mv docs/kjtcom-design-v9.30.md docs/kjtcom-plan-v9.30.md docs/kjtcom-build-v9.30.md docs/kjtcom-report-v9.30.md docs/archive/
cp ~/Downloads/kjtcom-design-v9.31.md docs/
cp ~/Downloads/kjtcom-plan-v9.31.md docs/
cp ~/Downloads/CLAUDE.md ./CLAUDE.md

# Flutter dependency update (NEW STANDARD - every iteration)
cd app
flutter pub upgrade
flutter pub get
flutter build web
flutter analyze
flutter test
cd ..

firebase projects:list
claude --dangerously-skip-permissions
```

---

## Section B: Claude Code Execution

### Step 1: Read Design Doc

Read `docs/kjtcom-design-v9.31.md`. Note the DIAGNOSTIC-FIRST approach: read files, grep, add debugPrint, THEN fix.

### Step 2: W1 - Fix 1000-Result Limit (DIAGNOSTIC FIRST)

**DO NOT write any fix code until diagnostics are complete.**

```fish
# Grep EVERY file in app/lib for limit-related patterns
grep -rn "1000\|limit\|truncat\|isTruncated\|serverCount\|totalCount\|_queryLimit" app/lib/

# Print the complete firestore_provider.dart
cat app/lib/providers/firestore_provider.dart

# Print the complete entity_count_row.dart (likely has its own query)
cat app/lib/widgets/entity_count_row.dart

# Print the complete results_table.dart result count section
grep -n "result\|count\|entities\|1000\|truncat" app/lib/widgets/results_table.dart
```

**Read the output. Identify EVERY line that references 1000 or limit.** The entity count row ("1000 entities across 30 countries") almost certainly uses a DIFFERENT Firestore query or provider than the results table. Find it. Fix ALL instances.

After fixing: flutter analyze + flutter test.

### Step 3: W2 - Fix Quote Cursor (DIAGNOSTIC FIRST)

**DO NOT write any fix code until diagnostics are complete.**

```fish
# Print the ENTIRE query_editor.dart
wc -l app/lib/widgets/query_editor.dart
cat app/lib/widgets/query_editor.dart

# Print the ENTIRE query_provider.dart
cat app/lib/providers/query_provider.dart

# Print the schema_tab.dart add-to-query handler
grep -A 20 "Add to query\|addField\|appendClause\|controller" app/lib/widgets/schema_tab.dart
```

**Trace the exact sequence:**
1. User clicks "+ Add to query" on schema tab
2. What function runs? What does it set on the controller?
3. Does it set controller.selection?
4. Does query_editor's ref.listen fire AFTER the selection is set?
5. If yes: add `debugPrint('ref.listen fired, text match: ${controller.text == next}')` to trace

The fix must ensure that after the schema builder sets cursor position, NO OTHER CODE moves the cursor. If ref.listen is the culprit, add a guard: `if (controller.text == next) return;` BEFORE setting controller.text in the listener.

After fixing: flutter analyze + flutter test.

### Step 4: W3 - Fix Autocomplete (DIAGNOSTIC FIRST)

```fish
# Check if value_index.json is in pubspec assets
grep -n "value_index" app/pubspec.yaml

# Check if the file exists and has content
ls -la app/assets/value_index.json
head -5 app/assets/value_index.json

# Print the autocomplete widget
cat app/lib/widgets/query_autocomplete.dart

# Check if it's imported and used in query_editor
grep -n "autocomplete\|AutocompleteOverlay\|valueIndex" app/lib/widgets/query_editor.dart
```

If the overlay is created but not showing: check z-index, check if it's positioned correctly, check if the condition to show it is ever true. Add `debugPrint` at the detection point.

After fixing: flutter analyze + flutter test.

### Step 5: W4 - Fix TripleDB Results

```fish
# Verify TripleDB data exists in production
python3 -u -c "
from google.cloud import firestore
import os
os.environ.setdefault('GOOGLE_APPLICATION_CREDENTIALS', os.path.expanduser('~/.config/gcloud/kjtcom-sa.json'))
db = firestore.Client(project='kjtcom-c78cd')
count = sum(1 for _ in db.collection('locations').where('t_log_type', '==', 'tripledb').stream())
print(f'Total tripledb in production: {count}')
bbq = sum(1 for _ in db.collection('locations').where('t_any_cuisines', 'array_contains', 'barbecue').stream())
print(f'Barbecue cuisines: {bbq}')
"
```

If data exists but doesn't render: the issue is in the Flutter app's Firestore query or rendering. Check if `t_log_type == "tripledb"` as a query clause is being parsed and dispatched correctly.

### Step 6: W5 - Add Clear Button

**File:** `app/lib/widgets/query_editor.dart`

Add a clear/X button in the chrome bar. Implementation:
- Icon: `Icons.clear` or `Icons.close`, sized to match existing chrome
- Position: between "locations" and "All time" (or next to Search button)
- On tap:
  ```dart
  ref.read(queryTextControllerProvider).clear();
  ref.read(queryProvider.notifier).setText('');
  ref.read(selectedEntityProvider.notifier).state = null;
  ```

flutter analyze + flutter test.

### Step 7: Build + Deploy

```fish
cd ~/dev/projects/kjtcom/app
flutter build web
cd ..
firebase deploy --only hosting
```

### Step 8: Playwright MCP Post-Flight Verification

**Use Playwright MCP to verify on live site.** If Flutter CanvasKit blocks DOM interaction (G47), capture screenshots at each step and document what's visible.

```
1. Navigate to https://kylejeromethompson.com
2. Wait 10 seconds for Flutter bootstrap
3. Screenshot: "v9.31-landing.png"
4. Verify: entity count does NOT say "1000" (should be larger or show real count)
5. Screenshot the Schema tab
6. Screenshot the Results tab after a query
7. Look for TripleDB (red) dots in results
```

If Playwright can't interact with the canvas, document the limitation clearly and provide the manual test script for Kyle.

### Step 9: Security Scan + Artifacts

```
CHECKLIST:
[ ] grep -rnI "AIzaSy" . -> only expected
[ ] Result count NOT showing 1000 (true total)
[ ] Quote cursor between quotes (or documented limitation)
[ ] Autocomplete dropdown appears (or documented blocker)
[ ] TripleDB results appear
[ ] Clear button works
[ ] Playwright screenshots captured
[ ] flutter analyze: 0 issues
[ ] flutter test: all pass
[ ] firebase deploy: success
```

Produce all 4 mandatory artifacts:

1. **docs/kjtcom-build-v9.31.md** - MUST include diagnostic grep output, debugPrint traces, and Playwright screenshots
2. **docs/kjtcom-report-v9.31.md** - MUST include honest assessment of what's fixed vs what remains broken
3. **docs/kjtcom-changelog.md** - Append v9.31
4. **README.md** - Update if needed

**CRITICAL: If a bug is NOT verifiably fixed on the live site, do NOT mark it as PASS. Mark it as FAIL with root cause analysis and next steps.**

Do NOT git commit or push.

---

## Section C: CLAUDE.md for v9.31

```markdown
# kjtcom - Agent Instructions (Claude Code)

## Read Order

1. docs/kjtcom-design-v9.31.md (DIAGNOSTIC-FIRST approach for persistent bugs)
2. docs/kjtcom-plan-v9.31.md (execute Section B)

## Context

Phase 9 bug fix iteration. FOUR PERSISTENT BUGS that failed 2-3 previous fix attempts:
- W1: 1000-result limit (attempt #4) - grep EVERY file, not just firestore_provider
- W2: Quote cursor (attempt #4) - trace ref.listen behavior, add debugPrint
- W3: Autocomplete not showing - verify asset registration, overlay creation, detection logic
- W4: TripleDB results not populating - verify data exists, query dispatches correctly

Plus: W5 clear button, W6 dependency update (pre-flight only)

## CRITICAL RULE: DIAGNOSTIC FIRST

For EACH persistent bug:
1. Read the ENTIRE relevant file (cat it, not just grep)
2. grep ALL files in app/lib/ for related patterns
3. Add debugPrint at decision points
4. THEN write the fix based on what you found
5. If you cannot verify the fix works on live site, mark it FAIL not PASS

## CRITICAL RULE: POST-FLIGHT VERIFICATION

After deploy, use Playwright MCP to navigate to kylejeromethompson.com and capture screenshots.
If CanvasKit blocks DOM interaction (G47), document the limitation honestly.
NEVER mark a fix as confirmed without live evidence (G48).

## Shell - MANDATORY

- All commands in fish shell
- NEVER cat config.fish or SA JSON files (G20, G11)

## Security

- grep -rnI "AIzaSy" . before completion

## Flutter Requirements

- flutter analyze + flutter test after every change
- Build: cd app && flutter build web
- Deploy: cd ~/dev/projects/kjtcom && firebase deploy --only hosting

## Permissions

- CANNOT: git add / commit / push
- CANNOT: sudo

## Artifact Rules - MANDATORY

1. docs/kjtcom-build-v9.31.md (MUST include diagnostic grep output + Playwright screenshots)
2. docs/kjtcom-report-v9.31.md (MUST honestly mark PASS/FAIL per bug)
3. docs/kjtcom-changelog.md (append v9.31)
4. README.md (update if needed)

## Formatting

- No em-dashes. Use " - " instead.
- Use "->" for arrows.
```

---

## Section D: Launch Prompt

```
Read CLAUDE.md, then read docs/kjtcom-design-v9.31.md (especially the DIAGNOSTIC-FIRST section) and docs/kjtcom-plan-v9.31.md.

THIS ITERATION IS DIFFERENT. Four bugs have failed 2-3 previous fix attempts. Do NOT guess at fixes. For each bug:
1. Read the ENTIRE relevant file (cat it)
2. grep ALL files in app/lib/ for related patterns (1000, limit, controller, selection, autocomplete, tripledb)
3. Print diagnostic output showing exactly where the bug originates
4. THEN write the fix

Execute Section B in order:
1. W1: Diagnostic grep for 1000/limit across ALL app/lib/ files. cat entity_count_row.dart and firestore_provider.dart completely. Fix every limit reference.
2. W2: cat query_editor.dart, query_provider.dart, schema_tab.dart completely. Trace the cursor flow. Fix ref.listen if it overrides selection.
3. W3: Verify value_index.json asset registration, check overlay creation in query_editor.dart, add debugPrint to autocomplete detection.
4. W4: Run Python Firestore query to verify TripleDB data. Check t_log_type == "tripledb" parsing.
5. W5: Add clear button to query editor.
6. Build + deploy.
7. Use Playwright MCP to verify on kylejeromethompson.com. Capture screenshots.
8. Produce artifacts with HONEST pass/fail assessment. If a bug isn't fixed, say so.
```

---

## Timing Estimate

| Step | Est. Duration |
|------|---------------|
| Pre-flight (with dependency update) | ~10 min |
| W1 diagnostic + fix | ~30 min |
| W2 diagnostic + fix | ~30 min |
| W3 diagnostic + fix | ~30 min |
| W4 diagnostic + fix | ~15 min |
| W5 clear button | ~10 min |
| Deploy + Playwright verification | ~20 min |
| Artifacts | ~15 min |
| **Total** | **~2.5-3 hours** |
