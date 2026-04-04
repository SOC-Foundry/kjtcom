# kjtcom - Agent Instructions (Claude Code)

## Read Order

1. docs/kjtcom-design-v9.28.md (4 work items + full gotcha registry G1-G44)
2. docs/kjtcom-plan-v9.28.md (execute Section B)

## Context

Phase 9 App Optimization. Four work items:
- W1: Gotcha tab (full registry G1-G42, status badges, filter toggle)
- W2: Schema tab with query builder (22 fields, click to add clause to query)
- W3: Copy JSON button on detail panel (clipboard + snackbar confirmation)
- W4: Post-flight deploy testing standard (MANDATORY build + deploy + live verify)

Tab order: Results | Map | Globe | IAO | Gotcha | Schema

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

## Post-Flight Deploy (MANDATORY - W4)

After all code changes:
1. flutter build web
2. firebase deploy --only hosting
3. Open kylejeromethompson.com in browser
4. Verify EVERY new feature on the live site
5. Document results in build log
6. If any feature fails live: fix, rebuild, redeploy

## Gotcha Tab (W1)

- Hardcode all 42 gotchas as Dart objects (from design doc registry table)
- Cards: ID badge, title, prevention, status badge (ACTIVE green / RESOLVED dimmed / DOCUMENTED orange)
- Filter toggle: All | Active | Resolved
- Gothic border treatment, Cinzel header

## Schema Tab (W2)

- 22 Thompson Indicator Fields from knownFields + descriptions/examples
- Each field card: name (Geist Mono), type, description, examples
- "+ Add to query" button -> appends clause to queryProvider, switches to Results tab
- t_log_type uses == operator, all t_any_* use contains
- t_any_coordinates and t_any_geohashes are view-only (no add button)

## JSON Copy (W3)

- Copy icon in detail panel header (next to entity name / close)
- Copies full entity rawData as indented JSON
- SnackBar confirmation: "JSON copied to clipboard"
- LocationEntity must have rawData: Map<String, dynamic> from Firestore snapshot

## Permissions

- CANNOT: git add / commit / push
- CANNOT: sudo

## Artifact Rules - MANDATORY

1. docs/kjtcom-build-v9.28.md (must include live verification results)
2. docs/kjtcom-report-v9.28.md (full gotcha registry + success criteria)
3. docs/kjtcom-changelog.md (append v9.28)
4. README.md (update tab list if changed)

## Formatting

- No em-dashes. Use " - " instead.
- Use "->" for arrows.
