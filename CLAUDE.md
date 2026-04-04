# kjtcom - Agent Instructions (Claude Code)

## Read Order

1. docs/kjtcom-design-v9.33.md (CRITICAL: parser regression + quotes + operators)
2. docs/kjtcom-plan-v9.33.md (execute Section B in STRICT order)

## Context

v9.32 introduced a PARSER REGRESSION: unquoted value regex broke quoted parsing. t_any_keywords contains "geology" returns parse error. This is the #1 priority.

Phase 9 iteration. Five work items in strict order:
- W1 (P0): Fix parser regex - quoted first, unquoted fallback. DEPLOY IMMEDIATELY.
- W2 (P0): Restore quotes in schema builder + fix cursor via programmaticUpdateProvider flag
- W3 (P0): +filter uses ==, -exclude uses !=
- W4 (P1): Fix feedback message
- W5 (P1): Flutter dependency upgrade (defer if >50 breaking changes)

## CRITICAL: PARSER FIX FIRST

1. cat query_clause.dart COMPLETELY
2. Write a test for `t_any_keywords contains "geology"` that FAILS (proving regression)
3. Fix regex: quoted pattern FIRST, unquoted as FALLBACK
4. Test passes
5. Build + deploy IMMEDIATELY
6. Verify on live site BEFORE proceeding to W2

## CRITICAL: QUOTES CURSOR FIX

Create programmaticUpdateProvider (StateProvider<bool>).
ref.listen in query_editor: if (ref.read(programmaticUpdateProvider)) return;
Schema builder: set flag true, set controller.text, set controller.selection, sync provider, clear flag via Future.microtask.
Add debugPrint in ref.listen to trace.

## +filter/exclude OPERATORS

+filter: append `== "value"` (not contains)
-exclude: append `!= "value"` (not contains)

## Shell - MANDATORY

- All commands in fish shell
- NEVER cat config.fish or SA JSON files (G20, G11)

## Security

- grep -rnI "AIzaSy" . before completion

## Flutter Requirements

- flutter analyze + flutter test after every change
- Build: cd app && flutter build web
- Deploy: cd ~/dev/projects/kjtcom && firebase deploy --only hosting

## Post-Flight (MANDATORY)

Verify ALL 7 tests on live site. If quotes cursor doesn't work, mark FAIL.

## Permissions

- CANNOT: git add / commit / push
- CANNOT: sudo

## Artifact Rules

1. docs/kjtcom-build-v9.33.md (include parser regression diagnosis + live verification)
2. docs/kjtcom-report-v9.33.md (HONEST pass/fail)
3. docs/kjtcom-changelog.md
4. README.md

## Formatting

- No em-dashes. Use " - " instead.
- Use "->" for arrows.
