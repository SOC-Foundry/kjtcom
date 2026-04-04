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
