# kjtcom - Agent Instructions (Claude Code)

## Read Order

1. docs/ricksteves-design-v3.11.md
2. docs/ricksteves-plan-v3.11.md (execute Section B only - Gemini CLI completed Section A)

## Context

This is a split-agent iteration. Gemini CLI executed phases 1-5 (acquire, transcribe, extract, normalize, geocode). You are executing phases 6-7 (enrich, load) plus post-flight and artifacts. Verify the handoff checkpoint at pipeline/data/ricksteves/handoff-v3.11.json before starting any work.

## Shell - MANDATORY

- Run: claude config set preferredShell fish (before first launch, one-time)
- All commands execute in fish shell
- Environment variables are in ~/.config/fish/config.fish
- NEVER use bash syntax (no ${VAR}, no heredocs, no source ~/.bashrc)
- If a command fails with "not a valid variable", you are in bash. Switch to fish.

## Security - ABSOLUTE RULES

- NEVER write API keys, tokens, or credentials into ANY file in the repo
- NEVER include API keys in build logs, reports, or changelog artifacts
- NEVER echo or print API key values in commands that get logged
- NEVER cat or read ~/.config/fish/config.fish (it contains API keys - G20)
- Read keys from environment variables ONLY
- If a key needs to be tested, print only "SET" or "NOT SET", never the value
- Before signaling completion: grep -rnI "AIzaSy" . must return only plan checklist references
- Violation of these rules is a BLOCKING failure - stop and alert Kyle

## Gotcha G2 - CUDA LD_LIBRARY_PATH

- RESOLVED in v3.10. LD_LIBRARY_PATH is embedded in phase2_transcribe.py AND config.fish.
- Not relevant for phases 6-7 but verify if needed: echo $LD_LIBRARY_PATH

## Enrichment Note (Learned in v3.10)

- phase6_enrich.py does NOT accept --database flag. It operates on files only. Do not pass --database staging to phase 6.
- phase7_load.py DOES accept --database staging. Use it.

## Permissions

- CAN: flutter build web, firebase deploy --only hosting/firestore/functions
- CAN: pip install, npm install (project-level)
- CANNOT: git add / commit / push (human commits at phase boundaries)
- CANNOT: sudo (ask Kyle)

## Database Rules

- Load to "staging" database only
- NEVER write to "(default)" without Kyle approval
- phase7_load.py uses fetch-and-merge (not .set()) for array fields

## Changelog

- Write all changes to docs/kjtcom-changelog.md (unified, not per-pipeline)
- APPEND entries at the TOP - never overwrite previous entries

## Artifact Rules - MANDATORY

Every iteration MUST produce/update these 4 files before completing:

1. docs/ricksteves-build-v3.11.md (session transcript - include both Gemini Section A summary and Claude Section B detail)
2. docs/ricksteves-report-v3.11.md (metrics + recommendation for Phase 4, report interventions per agent separately)
3. docs/kjtcom-changelog.md (UNIFIED - append v3.11 entry at top, never overwrite)
4. README.md (update Project Status table, Pipelines table entity count, Changelog section)

- If ANY re-run, fix, or backfill changes metrics, update ALL 4 files
- Do NOT mark a step complete until artifacts reflect the final state

## Living Documents

- If ANY new package is installed (pip, npm, pacman, yay), update docs/install.fish

## Formatting

- No em-dashes. Use " - " instead.
- Use "->" for arrows.
