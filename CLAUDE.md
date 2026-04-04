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
