# kjtcom - Agent Instructions (Claude Code)

## Read Order

1. docs/kjtcom-design-v9.27.md (5 workstreams with architecture decisions)
2. docs/kjtcom-plan-v9.27.md (execute Section B)

## Context

Phase 9 App Optimization. Five workstreams:
1. Gothic/cyberpunk visual refresh (selective flourishes on dark SIEM base)
2. IAO Pillar tab (trident SVG + 10 pillar cards + stats footer)
3. Map tab fix (flutter_map + OpenStreetMap, entity markers)
4. Globe tab fix (stats dashboard with continent/country breakdown)
5. Search results pagination (20/50/100 dropdown, page navigation)

kjtcom project ID: kjtcom-c78cd
Production: 6,181 entities (899 CalGold + 4,182 RickSteves + 1,100 TripleDB)
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

## New Dependencies

- flutter_map (latest compatible with Flutter 3.41.6) - check pub.dev (G44)
- latlong2
- google_fonts Cinzel already available via existing google_fonts package

## Visual Direction

Gothic + cyberpunk on dark SIEM base:
- Keep: #0D1117 surface, #4ADE80 tech green, Geist Sans/Mono
- Add: Cinzel font (google_fonts) for headers, double-line borders at 30% opacity, corner accents, green glow on hover
- Apply to: card containers, IAO tab, section headers
- Do NOT apply to: query editor input field (keep clean/functional)

## IAO Tab Content

All 10 pillar texts MUST be copied VERBATIM from the design doc. Do not summarize, rephrase, or abbreviate.

## Map Tab

- flutter_map + OpenStreetMap tiles (free, no API key)
- Markers from t_any_coordinates, colored by pipeline
- On marker tap: set selectedEntityProvider
- If CORS issues (G43): try --web-renderer html build flag

## Globe Tab

- Stats dashboard, NOT Three.js
- Continent cards + country grid from t_any_continents/t_any_country_codes
- Click -> appends filter clause, switches to Results tab
- Globe hero background at 15% opacity

## Pagination

- Dropdown: 20 | 50 | 100 (default 20)
- Client-side pagination from Firestore result set
- Page nav: Previous | Page N of M | Next

## Permissions

- CANNOT: git add / commit / push
- CANNOT: sudo

## Artifact Rules - MANDATORY

1. docs/kjtcom-build-v9.27.md
2. docs/kjtcom-report-v9.27.md (must include tab functional test results)
3. docs/kjtcom-changelog.md (append v9.27)
4. README.md (update if needed)

## Formatting

- No em-dashes. Use " - " instead.
- Use "->" for arrows.
