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
