# kjtcom - Plan v9.29 (Phase 9 - UX Polish: Trident, Limits, Schema, Quotes)

**Pipeline:** kjtcom (cross-pipeline location intelligence platform)
**Phase:** 9 (App Optimization)
**Iteration:** 29 (global counter)
**Executor:** Claude Code
**Machine:** NZXTcos
**Date:** April 2026

---

## Section A: Pre-Flight (Human)

### A1: Archive v9.28 Docs

```fish
cd ~/dev/projects/kjtcom
mv docs/kjtcom-design-v9.28.md docs/kjtcom-plan-v9.28.md docs/kjtcom-build-v9.28.md docs/kjtcom-report-v9.28.md docs/archive/
```

### A2: Stage v9.29 Docs

```fish
cp ~/Downloads/kjtcom-design-v9.29.md docs/
cp ~/Downloads/kjtcom-plan-v9.29.md docs/
cp ~/Downloads/CLAUDE.md ./CLAUDE.md
cd app && flutter pub get && flutter build web && flutter analyze && flutter test
cd ..
claude --dangerously-skip-permissions
```

---

## Section B: Claude Code Execution

### Step 1: Read Design Doc

Read `docs/kjtcom-design-v9.29.md` for all 4 work items.

### Step 2: W2 - Remove Firestore Query Limit (P0)

**File:** `app/lib/providers/firestore_provider.dart`

Remove `.limit(1000)` from the Firestore query. With 6,181 total entities this is safe. Update or remove the truncation indicator since `isTruncated` will always be false.

flutter analyze + flutter test.

### Step 3: W4 - Fix Quote Cursor Placement (P0)

**Files:** `app/lib/widgets/schema_tab.dart`, `app/lib/providers/query_provider.dart`, `app/lib/models/query_clause.dart`

Change schema builder to append clause WITHOUT closing quote:
```
| where t_any_states contains "
```

Update `query_clause.dart` parser regex to accept unclosed quotes at end of line.

flutter analyze + flutter test.

### Step 4: W1 - Shorten Trident Labels (P1)

**File:** `app/lib/widgets/iao_tab.dart`

Change prong labels: "Minimal cost" -> "Cost", "Speed of delivery" -> "Delivery", "Optimized performance" -> "Performance"

flutter analyze + flutter test.

### Step 5: W3 - Fix Missing Schema Fields (P1)

**File:** `app/lib/widgets/schema_tab.dart`

Audit field list against the 22 fields in the design doc. Add any missing fields (t_any_cuisines confirmed missing). Ensure all have type, description, and examples.

flutter analyze + flutter test.

### Step 6: Post-Flight Deploy + Live Verification (MANDATORY)

```fish
cd ~/dev/projects/kjtcom/app
flutter build web
cd ..
firebase deploy --only hosting
```

**Verify on kylejeromethompson.com:**

| # | Test | Expected |
|---|------|----------|
| 1 | `t_any_keywords contains "medieval"` | Shows 653 results (not capped at 1000) |
| 2 | `t_any_actors contains "rick steves"` | Shows 4170+ results (full count) |
| 3 | Click Schema tab | All 22 fields present including t_any_cuisines |
| 4 | Click "+ Add to query" on t_any_cuisines | Clause appended without closing quote, cursor ready |
| 5 | Type "french" after the open quote | Value appears correctly inside the clause |
| 6 | IAO tab on mobile | Trident shows "Cost", "Delivery", "Performance" |
| 7 | Pagination still works | Show 20/50/100 dropdown |

### Step 7: Security Scan + Artifacts

Produce all 4 mandatory artifacts. Do NOT git commit or push.

---

## Section C: CLAUDE.md for v9.29

```markdown
# kjtcom - Agent Instructions (Claude Code)

## Read Order

1. docs/kjtcom-design-v9.29.md (4 fixes + full gotcha registry)
2. docs/kjtcom-plan-v9.29.md (execute Section B)

## Context

Phase 9 UX polish. Four fixes:
- W1: Shorten trident labels for mobile ("Cost", "Delivery", "Performance")
- W2: Remove Firestore .limit(1000) - fetch all results, paginate client-side
- W3: Fix missing schema fields (audit against 22 known fields)
- W4: Fix schema builder quote placement - append without closing quote, update parser

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
3. Verify on kylejeromethompson.com
4. Document results in build log

## Key Fix Details

W2 (limit removal): Remove .limit(1000) from firestore_provider.dart. Simplify or remove truncation indicator.

W4 (quotes): Schema builder appends `| where field contains "` (NO closing quote). Parser must accept unclosed quotes at end of line (G45). User types value and optionally closes quote.

## Permissions

- CANNOT: git add / commit / push
- CANNOT: sudo

## Artifact Rules - MANDATORY

1. docs/kjtcom-build-v9.29.md
2. docs/kjtcom-report-v9.29.md
3. docs/kjtcom-changelog.md (append v9.29)
4. README.md (update if needed)

## Formatting

- No em-dashes. Use " - " instead.
- Use "->" for arrows.
```

---

## Section D: Launch Prompt

```
Read CLAUDE.md, then read docs/kjtcom-design-v9.29.md for all 4 work items and docs/kjtcom-plan-v9.29.md for execution order.

Execute Section B:
1. W2: Remove .limit(1000) from firestore_provider.dart. Simplify truncation indicator.
2. W4: Fix schema builder to append clause WITHOUT closing quote. Update query_clause.dart parser to accept unclosed quotes at end of line.
3. W1: Shorten trident prong labels in iao_tab.dart to "Cost", "Delivery", "Performance".
4. W3: Audit schema_tab.dart field list against design doc's 22 fields. Add any missing (t_any_cuisines confirmed missing).
5. flutter analyze + flutter test after each fix.
6. MANDATORY: flutter build web + firebase deploy --only hosting + verify all 7 tests on live site.
7. Produce all 4 mandatory artifacts.
```

---

## Timing Estimate

| Step | Est. Duration |
|------|---------------|
| Pre-flight | ~5 min |
| W2 (limit removal) | ~10 min |
| W4 (quote fix) | ~20 min |
| W1 (trident labels) | ~5 min |
| W3 (schema audit) | ~10 min |
| Deploy + verify | ~10 min |
| Artifacts | ~15 min |
| **Total** | **~1-1.5 hours** |
