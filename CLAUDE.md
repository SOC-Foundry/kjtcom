# kjtcom - Agent Instructions (Claude Code)

## Read Order

1. docs/ricksteves-design-v4.13.md
2. docs/ricksteves-plan-v4.13.md (execute Section B only)

## Context

Schema v3 migration for RickSteves. Gemini CLI completed schema config changes + phases 1-5 with re-extraction of ALL 150 videos. Verify handoff checkpoint at pipeline/data/ricksteves/handoff-v4.13.json. Confirm schema_version: 3 and 7 new_fields.

CRITICAL (G24): Reset enrichment and load checkpoints BEFORE running phases 6-7. The v3.11 checkpoints are stale (schema v2, 120 files). Step 5.5 in the plan covers this.

## Shell - MANDATORY

- claude config set preferredShell fish (one-time)
- All commands in fish shell
- NEVER cat config.fish (G20)

## Security - ABSOLUTE RULES

- grep -rnI "AIzaSy" . before signaling completion
- Print only "SET" or "NOT SET" for key checks

## Enrichment Note

- phase6_enrich.py does NOT accept --database flag
- phase7_load.py DOES accept --database staging

## CalGold t_any_shows Backfill

After RickSteves load, backfill all CalGold entities with t_any_shows: ["California's Gold"]. Script provided in plan Step 7.5. If it fails, defer -- not blocking.

## Permissions

- CAN: flutter build web, firebase deploy
- CANNOT: git add / commit / push
- CANNOT: sudo

## Database Rules

- Load to "staging" only
- fetch-and-merge for array fields

## README updates

Also update README.md with these structural changes:

- Rename "Thompson Schema" to "Thompson Indicator Fields" throughout
- Add a "Data Architecture" section before the indicator fields section explaining the single-collection Firestore design (t_log_type discriminator, array-contains queries, composite indexes, multi-database staging/default, Blaze pricing)
- Show all 4 pipelines (calgold, ricksteves, tripledb, bourdain) in the Pipelines table with t_log_type column
- Add an Examples column to the indicator fields table
- Note that the field convention is enforced by pipeline scripts, not the database

## Artifact Rules - MANDATORY

1. docs/ricksteves-build-v4.13.md (include checkpoint reset detail, CalGold backfill status)
2. docs/ricksteves-report-v4.13.md (v3 field population rates, Phase 5 readiness)
3. docs/kjtcom-changelog.md (append v4.13 at top)
4. README.md - Use this phase structure:

| Phase | Name | Status | Iteration |
|-------|------|--------|-----------|
| 0 | Scaffold & Environment | DONE | v0.5 |
| 1 | Discovery (30 videos) | DONE | v1.6, v1.7 |
| 2 | Calibration (60 videos) | DONE | v2.8, v2.9 |
| 3 | Stress Test (90 videos) | DONE | v3.10, v3.11 |
| 4 | Validation + Schema v3 | DONE | v4.12, v4.13 |
| 5 | Production Run | Pending | - |
| 6 | Flutter App | Pending | - |
| 7 | Firestore Load | Pending | - |
| 8 | Enrichment Hardening | Pending | - |
| 9 | App Optimization | Pending | - |
| 10 | Retrospective + Template | Pending | - |

## Formatting

- No em-dashes. Use " - " instead.
- Use "->" for arrows.
