# kjtcom - Agent Instructions (Claude Code)

## Read Order

1. docs/kjtcom-design-v8.24.md (4 work items with diagnostics)
2. docs/kjtcom-plan-v8.24.md (execute Section B)

## Context

Phase 8 UI Fixes + Country Codes. Four work items:
- W1 (P0): Fix detail panel - clicking a result row must open entity detail with t_any_* fields
- W2 (P0): Remove "staging" badge from app_shell
- W3 (P1): Fix cursor alignment in query editor (multiple cursors, misaligned position)
- W4 (P1): Backfill t_any_country_codes (ISO 3166-1 alpha-2) on all 6,181 entities

Deploy TWICE: after P0 fixes (Step 4), after all fixes (Step 7).

kjtcom project ID: kjtcom-c78cd
SA credentials: $GOOGLE_APPLICATION_CREDENTIALS
Production database: (default)
Production collection: locations
Total entities: 6,181

## Shell - MANDATORY

- All commands in fish shell
- Use python3 -u for unbuffered stdout
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

## Detail Panel Diagnostic (W1)

Read these files first to trace the break:
1. detail_panel.dart - what it renders
2. results_table.dart - row tap handler
3. selection_provider.dart - state management
4. app_shell.dart - widget tree layout
5. firestore_provider.dart - did v8.23 QueryResult refactor break selection?

The detail panel MUST show: entity name, pipeline badge, all t_any_* field cards, +filter/-exclude buttons, enrichment data.

## Data Fix Requirements

- backfill_country_codes.py: --dry-run, --limit flags
- Use pycountry library + hardcoded fallback for edge cases
- Store codes as lowercase: ["fr", "it", "us"]
- Dry-run before full run (G35)

## Permissions

- CANNOT: git add / commit / push
- CANNOT: sudo

## Artifact Rules - MANDATORY

1. docs/kjtcom-build-v8.24.md
2. docs/kjtcom-report-v8.24.md
3. docs/kjtcom-changelog.md (append v8.24)
4. README.md (Phase 8 DONE, add t_any_country_codes to field table)

## Formatting

- No em-dashes. Use " - " instead.
- Use "->" for arrows.
