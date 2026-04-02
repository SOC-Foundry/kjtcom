# kjtcom - Agent Instructions (Claude Code)

## Read Order

1. docs/kjtcom-design-v7.21.md (schema mapping specification)
2. docs/kjtcom-plan-v7.21.md (execute Section B)

## Context

Phase 7 Firestore Load. Two tasks:
1. Migrate ~1,100 TripleDB restaurants from external Firestore project
   to kjtcom production locations collection (Option 4: schema mapping)
2. Copy 5,081 CalGold + RickSteves entities from staging to production

TripleDB SA credentials are at ~/.config/gcloud/tripledb-sa.json
kjtcom SA credentials are at $GOOGLE_APPLICATION_CREDENTIALS
TripleDB project ID: tripledb-e0f77
kjtcom project ID: kjtcom-c78cd

## Shell - MANDATORY

- All commands in fish shell
- NEVER cat config.fish or SA JSON files (G20, G11)

## Security

- grep -rnI "AIzaSy" . before completion
- NEVER print SA credentials or API keys
- Print only SET/NOT SET for key checks

## Migration Script Requirements

- migrate_tripledb.py: --dry-run, --limit, --project, --sa-path flags
- migrate_staging_to_production.py: simple copy, no transformation
- Batch writes (500 docs per batch) for both scripts
- Deterministic t_row_id for dedup safety (G33)
- Print summary with field population rates after each migration

## Permissions

- CANNOT: git add / commit / push
- CANNOT: sudo

## Artifact Rules - MANDATORY

1. docs/kjtcom-build-v7.21.md
2. docs/kjtcom-report-v7.21.md
3. docs/kjtcom-changelog.md (append v7.21)
4. README.md (Phase 7 DONE, updated entity counts)

## Formatting

- No em-dashes. Use " - " instead.
- Use "->" for arrows.
