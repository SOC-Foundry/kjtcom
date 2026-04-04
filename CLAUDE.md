# kjtcom - Agent Instructions (Claude Code)

## Read Order

1. docs/kjtcom-design-v8.25.md (filter fix + README overhaul spec)
2. docs/kjtcom-plan-v8.25.md (execute Section B)

## Context

Phase 8 final cleanup. Two workstreams:
- W-A: Fix +filter/-exclude duplicate bug in detail_panel.dart (adds 1-4 lines per click, should add exactly 1)
- W-B: Comprehensive README overhaul - full rewrite to reflect current state

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

## Filter Fix (W-A)

Root cause: +filter handler modifies queryProvider, which triggers a detail panel rebuild, which re-fires the handler. Fix with:
1. Dedup: check if clause already exists in current query before appending
2. Guard flag: prevent re-entry during same event loop tick
3. May need to convert StatelessWidget to ConsumerStatefulWidget for the guard flag

Test: click +filter 3 times on same field -> only 1 line added (dedup). Click +filter on 3 different fields -> 3 lines added.

## README Overhaul (W-B)

Complete rewrite following the exact structure in the design doc. Key requirements:
- NEW "Live App" section with kylejeromethompson.com link and feature list
- NEW "Query System" section documenting operators, features, examples
- Add t_any_country_codes to indicator fields table
- Update Project Status: Phase 8 DONE
- Keep IAO section EXACTLY as-is (mermaid chart + 10 pillars verbatim)
- Truncate changelog to last 5 iterations, link to full changelog
- Add tsP3-cos to Hardware section

## Permissions

- CANNOT: git add / commit / push
- CANNOT: sudo

## Artifact Rules - MANDATORY

1. docs/kjtcom-build-v8.25.md
2. docs/kjtcom-report-v8.25.md (include Phase 8 complete summary + Phase 9 recommendation)
3. docs/kjtcom-changelog.md (append v8.25)
4. README.md (COMPLETE OVERHAUL - this is the primary deliverable)

## Formatting

- No em-dashes. Use " - " instead.
- Use "->" for arrows.
