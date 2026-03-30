printf '# kjtcom - Agent Instructions

## Read Order
1. docs/ricksteves-design-v2.9.md
2. docs/ricksteves-plan-v2.9.md

## Shell - MANDATORY
- All commands execute in fish shell
- Environment variables are in ~/.config/fish/config.fish
- NEVER use bash syntax (no ${VAR}, no heredocs, no source ~/.bashrc)

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
  1. docs/ricksteves-build-v2.9.md (session transcript)
  2. docs/ricksteves-report-v2.9.md (metrics + recommendation)
  3. docs/kjtcom-changelog.md (UNIFIED - append entry, never overwrite)
  4. README.md (update project status, pipelines table, changelog section)
- If ANY re-run, fix, or backfill changes metrics, update ALL 4 files
- Do NOT mark a step complete until artifacts reflect the final state

## Living Documents
- If ANY new package is installed (pip, npm, pacman, yay), update docs/install.fish

## Formatting
- No em-dashes. Use " - " instead.
- Use "->" for arrows.
' > GEMINI.md
cp GEMINI.md CLAUDE.md
