# kjtcom - Agent Instructions (Gemini CLI)

## Read Order

1. docs/kjtcom-design-v9.34.md (3 work items: quote cursor, inline autocomplete, operators)
2. docs/kjtcom-plan-v9.34.md (execute Section B)

## Context

Flutter Web app at kylejeromethompson.com. Location intelligence platform with 6,181 entities.
This is a Gemini CLI iteration because Claude Code failed the quote cursor fix 6 times.

Three work items:
- W1 (P0): Fix cursor placement between quotes when schema builder appends a clause
- W2 (P0): Replace overlay autocomplete with inline Panther-style suggestions
- W3 (P1): Fix +filter/-exclude operators per field type

Project: kjtcom-c78cd
App code: app/lib/
Production: Firebase Hosting

## Shell

- NZXTcos uses fish shell
- All shell commands MUST be wrapped in `fish -c "..."`  (G19)
- NEVER cat ~/.config/fish/config.fish (G20)
- NEVER cat SA credential JSON files (G11)
- Use `python3 -u` for unbuffered stdout

## Key Files

- app/lib/widgets/query_editor.dart - query editor with TextField + syntax highlighting
- app/lib/providers/query_provider.dart - query state + TextEditingController provider + programmaticUpdateProvider
- app/lib/widgets/schema_tab.dart - schema builder with "+ Add to query" button
- app/lib/widgets/query_autocomplete.dart - current overlay autocomplete (REPLACE with inline)
- app/lib/widgets/detail_panel.dart - +filter/-exclude buttons
- app/lib/models/query_clause.dart - parser + knownFields
- app/assets/value_index.json - precomputed distinct values per field

## Quote Cursor (W1)

A programmaticUpdateProvider (StateProvider<bool>) exists. Schema builder sets it true, sets controller.text with quotes, sets controller.selection between quotes, syncs provider, clears flag via Future.microtask.

ref.listen in query_editor checks the flag and skips when true.

THIS STILL DOESN'T WORK. Something resets cursor after the flag clears. Try:
- WidgetsBinding.instance.addPostFrameCallback for deferred selection
- Or wrap selection in Future.delayed(Duration.zero, ...)
- Or find what ELSE touches cursor (onChanged? syntax highlighter rebuild?)

## Inline Autocomplete (W2)

REMOVE the OverlayEntry approach. Render suggestions as a widget INSIDE the query editor Column, below query lines. See design doc for Panther SIEM reference. Compact, 2-5 rows, dark bg, Tab to accept.

## Operators (W3)

Array fields (t_any_*): +filter = contains, -exclude = custom NOT
Scalar fields (t_log_type): +filter = ==, -exclude = !=

## Flutter Build + Deploy

- Build: fish -c "cd app && flutter build web"
- Deploy: fish -c "cd ~/dev/projects/kjtcom && firebase deploy --only hosting"
- Deploy from repo root, not app/ (G38)
- flutter analyze + flutter test after every change

## Permissions

- CANNOT: git add / commit / push
- CANNOT: sudo

## Artifacts - MANDATORY

1. docs/kjtcom-build-v9.34.md
2. docs/kjtcom-report-v9.34.md (HONEST pass/fail)
3. docs/kjtcom-changelog.md (append v9.34)
4. README.md (update if needed)

## Formatting

- No em-dashes. Use " - " instead.
- Use "->" for arrows.
