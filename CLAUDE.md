# kjtcom - Agent Instructions

## Read Order
1. docs/calgold-design-v2.8.md
2. docs/calgold-plan-v2.8.md

## Shell - MANDATORY
- Run: claude config set preferredShell fish (before first launch)
- All commands execute in fish shell
- Environment variables are in ~/.config/fish/config.fish
- NEVER use bash syntax (no ${VAR}, no heredocs, no source ~/.bashrc)
- If a command fails with "not a valid variable", you are in bash. Switch to fish.

## Security - ABSOLUTE RULES
- NEVER write API keys, tokens, or credentials into ANY file in the repo
- NEVER include API keys in build logs, reports, or changelog artifacts
- NEVER echo or print API key values in commands that get logged
- Read keys from environment variables ONLY
- If a key needs to be tested, print only "SET" or "NOT SET", never the value
- Violation of these rules is a BLOCKING failure - stop and alert Kyle

## Gotcha G2 - CUDA LD_LIBRARY_PATH (READ THIS)
- faster-whisper/ctranslate2 WILL fail if LD_LIBRARY_PATH is not set
- The path MUST include CUDA libs BEFORE calling any transcription
- Check: echo $LD_LIBRARY_PATH (must be non-empty and include cuda/cublas/cudnn)
- If empty: source ~/.config/fish/config.fish
- This has caused interventions in EVERY phase so far. Do not skip this check.

## Permissions
- CAN: flutter build web, firebase deploy --only hosting/firestore/functions
- CAN: pip install, npm install (project-level)
- CANNOT: git add / commit / push
- CANNOT: sudo (ask Kyle)

## Database Rules
- Load to "staging" database only
- NEVER write to "(default)" without Kyle approval

## Changelog
- Write all changes to docs/kjtcom-changelog.md (unified, not per-pipeline)
- APPEND entries - never overwrite previous entries

## Artifact Rules - MANDATORY
- Every iteration MUST produce/update these 4 files before completing:
  1. docs/calgold-build-v2.8.md (session transcript)
  2. docs/calgold-report-v2.8.md (metrics + recommendation)
  3. docs/kjtcom-changelog.md (UNIFIED - append entry, never overwrite)
  4. README.md (update project status, pipelines table, changelog section)
- If ANY re-run, fix, or backfill changes metrics, update ALL 4 files
- Do NOT mark a step complete until artifacts reflect the final state

## Formatting
- No em-dashes. Use " - " instead.
- Use "->" for arrows.
