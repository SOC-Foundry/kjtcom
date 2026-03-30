# kjtcom - Agent Instructions (Gemini CLI)

## Read Order

1. docs/ricksteves-design-v4.13.md
2. docs/ricksteves-plan-v4.13.md (execute Section A only - stop at handoff checkpoint)

## Context

Schema v3 migration for RickSteves. The shared script enhancements (continent lookup, county parsing) already exist from v4.12. You need to:
1. Update RickSteves-specific config files (schema.json, extraction_prompt.md) with 7 new fields (including t_any_shows)
2. Acquire + transcribe 30 new videos (121-150)
3. Re-extract, re-normalize, re-geocode ALL 150 videos with v3 prompt

Stop at handoff checkpoint. Claude Code handles phases 6-7.

## Shell - MANDATORY

- All commands MUST be wrapped in fish -c "..." (G19)
- Use "command ls" or Python for file listing (G22)

## Security - ABSOLUTE RULES

- NEVER cat or read ~/.config/fish/config.fish (G20)
- Print only "SET" or "NOT SET" for key checks
- Violation is a BLOCKING failure

## Transcription - CRITICAL (G18, G21)

- ALL transcription as background job with polling
- Rick Steves episodes are 30-60 min. Budget ~30 min for 30 videos.
- ONE process only (G21)

## Re-Extraction Note

Step 3 re-extracts ALL 150 RickSteves transcripts (not just 121-150). Use --limit 150. This overwrites previous extracted JSON. Every entity needs the 7 new v3 fields.

## Permissions

- CAN: pip install, edit pipeline config files and scripts
- CANNOT: git add / commit / push
- CANNOT: sudo

## Database Rules

- Do NOT load to Firestore. Phase 7 is Claude Code's job.

## README updates

Also update README.md with these structural changes:

- Rename "Thompson Schema" to "Thompson Indicator Fields" throughout
- Add a "Data Architecture" section before the indicator fields section explaining the single-collection Firestore design (t_log_type discriminator, array-contains queries, composite indexes, multi-database staging/default, Blaze pricing)
- Show all 4 pipelines (calgold, ricksteves, tripledb, bourdain) in the Pipelines table with t_log_type column
- Add an Examples column to the indicator fields table
- Note that the field convention is enforced by pipeline scripts, not the database


## Handoff Protocol

Produce checkpoint at pipeline/data/ricksteves/handoff-v4.13.json with schema_version: 3 and all 7 new_fields listed.
STOP. Do not proceed to phases 6-7.

## Formatting

- No em-dashes. Use " - " instead.
- Use "->" for arrows.
