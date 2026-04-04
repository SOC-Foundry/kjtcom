# kjtcom - Plan v8.26 (Phase 8 - Gotcha Registry + Query UX Fix)

**Pipeline:** kjtcom (cross-pipeline location intelligence platform)
**Phase:** 8 (Enrichment Hardening)
**Iteration:** 26 (global counter)
**Executor:** Claude Code
**Machine:** NZXTcos
**Date:** April 2026

---

## Section A: Pre-Flight (Human)

### IAO Pillar Pre-Flight Checklist

| # | Pillar | Verification | Command/Check |
|---|--------|-------------|---------------|
| P1 | Trident | $0 cost - Dart changes only | No APIs needed |
| P2 | Artifact Loop | v8.25 docs archived | `ls docs/archive/kjtcom-*v8.25*` -> 4 files |
| P2 | Artifact Loop | v8.26 design + plan in docs/ | `ls docs/kjtcom-{design,plan}-v8.26.md` -> 2 files |
| P3 | Diligence | Design doc reviewed | Kyle has reviewed both work items |
| P4 | Pre-Flight | Git clean | `git status` -> clean |
| P4 | Pre-Flight | CLAUDE.md updated | `head -3 CLAUDE.md` -> references v8.26 |
| P4 | Pre-Flight | Flutter builds | `cd app && flutter build web` -> success |
| P4 | Pre-Flight | Firebase auth | `firebase projects:list` -> no error |
| P6 | Zero-Intervention | Both work items pre-specified | No TBD in design doc |
| P9 | Post-Flight | Type a query -> no rotation interrupts | Manual verification |

### A1: Archive v8.25 Docs

```fish
cd ~/dev/projects/kjtcom
mv docs/kjtcom-design-v8.25.md docs/kjtcom-plan-v8.25.md docs/kjtcom-build-v8.25.md docs/kjtcom-report-v8.25.md docs/archive/
```

### A2: Stage v8.26 Docs

```fish
cp ~/Downloads/kjtcom-design-v8.26.md docs/
cp ~/Downloads/kjtcom-plan-v8.26.md docs/
```

### A3: Update CLAUDE.md

Replace CLAUDE.md with the v8.26 version (Section C).

### A4: Verify Flutter + Firebase

```fish
cd ~/dev/projects/kjtcom/app
flutter pub get
flutter build web
flutter analyze
flutter test
cd ..
firebase projects:list
```

---

## Section B: Claude Code Execution

**Launch:** `claude --dangerously-skip-permissions`
**First message:** See Section D (Launch Prompt).

### Step 1: Read Design Doc

Read `docs/kjtcom-design-v8.26.md` for both work items and the full gotcha registry.

### Step 2: W1 - Remove Rotating Example Queries

**Files:** `app/lib/widgets/query_editor.dart`, `app/lib/providers/query_provider.dart`

1. Read `query_editor.dart` completely. Find:
   - The list of 5 example queries
   - The Timer that cycles through them (likely a `Timer.periodic` with 6-second interval)
   - Any `ref.listen` or callback that injects the current example into `queryProvider`

2. Read `query_provider.dart`. Find:
   - `initialExampleQuery` or similar initial state
   - Any rotation-related state

3. Remove:
   - The Timer and its initialization/disposal
   - The example query list (if only used for rotation)
   - The initial query population - query provider should start with empty string `''`
   - Any animation state tied to query rotation (if the blinking cursor was tied to rotation, it may already be removed from v8.24)

4. Add:
   - Static help text below the query editor (NOT in the input field). Use a `Text` widget with reduced opacity:
   ```
   Examples: t_any_cuisines contains "french" | t_any_countries contains "italy" | t_any_country_codes contains-any ["fr", "it"]
   ```
   - Style: Geist Mono, secondary text color, ~12px, positioned below the query editor container

5. Verify the entity count row still displays total counts on load (it should read from a separate provider, not from query results).

6. After changes: `flutter analyze` + `flutter test`

### Step 3: Build and Deploy

```fish
cd ~/dev/projects/kjtcom/app
flutter build web
cd ..
firebase deploy --only hosting
```

Verify on kylejeromethompson.com:
- Page loads with empty query editor
- No queries rotate through the editor
- Static example syntax visible below the editor
- Entity count row shows "6,181 entities across N countries"
- Type a query - no interruption, results load normally
- Detail panel still works on row click

### Step 4: Security Scan + Artifacts

```
CHECKLIST:
[ ] Security: grep -rnI "AIzaSy" . -> only expected references
[ ] Rotating queries removed (no Timer, no auto-injection)
[ ] Query editor starts empty
[ ] Static example syntax shown below editor
[ ] Entity count row displays on load
[ ] User typing not interrupted
[ ] flutter analyze: 0 issues
[ ] flutter test: all pass
[ ] firebase deploy: success
[ ] Full gotcha registry (G1-G42) in report artifact
```

Produce all 4 mandatory artifacts:

1. **docs/kjtcom-build-v8.26.md** - What was removed, what was added
2. **docs/kjtcom-report-v8.26.md** - Success criteria, FULL gotcha registry (G1-G42 with status), Phase 9 recommendation
3. **docs/kjtcom-changelog.md** - Append v8.26 at top
4. **README.md** - Update if needed (remove mention of "rotating queries" if present)

Do NOT git commit or push.

---

## Section C: CLAUDE.md for v8.26

```markdown
# kjtcom - Agent Instructions (Claude Code)

## Read Order

1. docs/kjtcom-design-v8.26.md (2 work items + full gotcha registry)
2. docs/kjtcom-plan-v8.26.md (execute Section B)

## Context

Phase 8 final fix. Two items:
- W1: Remove rotating example queries from query editor. They interrupt user typing. Replace with static help text below the editor.
- W2: Full gotcha registry (G1-G42) included in report artifact.

kjtcom project ID: kjtcom-c78cd
Production: 6,181 entities
Live: kylejeromethompson.com

## Shell - MANDATORY

- All commands in fish shell
- NEVER cat config.fish or SA JSON files (G20, G11)

## Security

- grep -rnI "AIzaSy" . before completion
- NEVER print SA credentials or API keys

## Flutter Requirements

- Run `flutter analyze` after every Dart file change
- Run `flutter test` after every Dart file change
- Build: `cd app && flutter build web`
- Deploy: `cd ~/dev/projects/kjtcom && firebase deploy --only hosting`
- Deploy from repo root, not app/ (G38)

## Rotation Removal (W1)

Remove from query_editor.dart:
- Timer.periodic that cycles example queries
- Example query list (move to static help text)
- Any ref.listen/callback that injects examples into queryProvider

Remove from query_provider.dart:
- Initial example query - start with empty string

Add:
- Static help text below editor: "Examples: t_any_cuisines contains "french" | ..."
- Geist Mono, secondary color, not injected into input field

Verify: entity count row still shows totals on load (separate from query results).

## Permissions

- CANNOT: git add / commit / push
- CANNOT: sudo

## Artifact Rules - MANDATORY

1. docs/kjtcom-build-v8.26.md
2. docs/kjtcom-report-v8.26.md (MUST include full gotcha registry G1-G42)
3. docs/kjtcom-changelog.md (append v8.26)
4. README.md (update if "rotating queries" mentioned)

## Formatting

- No em-dashes. Use " - " instead.
- Use "->" for arrows.
```

---

## Section D: Launch Prompt

```
Read CLAUDE.md, then read docs/kjtcom-design-v8.26.md for both work items (including the full gotcha registry G1-G42) and docs/kjtcom-plan-v8.26.md for execution order.

Execute Section B:
1. Read query_editor.dart and query_provider.dart completely.
2. Remove the rotating example query Timer, the example query list, and the initial query population. Query editor should start empty.
3. Add static help text below the query editor showing 2-3 example query syntaxes (NOT injected into the input field). Use Geist Mono, secondary text color.
4. Verify entity count row still shows totals on load.
5. flutter analyze + flutter test.
6. Build and deploy.
7. Produce all 4 mandatory artifacts. The report MUST include the complete gotcha registry (G1-G42) from the design doc with current status.
```

---

## Timing Estimate

| Step | Est. Duration |
|------|---------------|
| Section A (pre-flight) | ~5 min |
| Step 2 (rotation removal) | ~20 min |
| Step 3 (deploy + verify) | ~10 min |
| Step 4 (artifacts) | ~15 min |
| **Total** | **~50 min** |

---

## After v8.26

1. Commit: `git add . && git commit -m "KT 8.26 remove rotating queries + gotcha registry standard" && git push`
2. Verify kylejeromethompson.com: empty editor, no rotation, help text visible
3. Phase 8 COMPLETE.
4. Next iteration: site aesthetics update (Phase 9 or dedicated design iteration)
