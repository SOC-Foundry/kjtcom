# kjtcom - Agent Instructions (Claude Code)

## Read Order

1. docs/calgold-design-v3.10.md
2. docs/calgold-plan-v3.10.md (execute Section B only - Gemini CLI completed Section A)

## Context

This is a split-agent iteration. Gemini CLI executed phases 1-5 (acquire, transcribe, extract, normalize, geocode). You are executing phases 6-7 (enrich, load) plus post-flight and artifacts. Verify the handoff checkpoint at pipeline/data/calgold/handoff-v3.10.json before starting any work.

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

## Gotcha G2 - CUDA LD_LIBRARY_PATH (READ THIS)

- faster-whisper/ctranslate2 WILL fail if LD_LIBRARY_PATH is not set
- The path MUST include CUDA libs BEFORE calling any transcription
- Check: echo $LD_LIBRARY_PATH (must be non-empty and include cuda/cublas/cudnn)
- If empty: source ~/.config/fish/config.fish
- LD_LIBRARY_PATH is now also embedded in phase2_transcribe.py as a fallback
- This has caused interventions in EVERY phase so far. Do not skip this check.

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

1. docs/calgold-build-v3.10.md (session transcript - include both Gemini Section A summary and Claude Section B detail)
2. docs/calgold-report-v3.10.md (metrics + recommendation for Phase 4, report interventions per agent separately)
3. docs/kjtcom-changelog.md (UNIFIED - append v3.10 entry at top, never overwrite)
4. README.md (update Project Status table, Pipelines table entity count, Changelog section)

- If ANY re-run, fix, or backfill changes metrics, update ALL 4 files
- Do NOT mark a step complete until artifacts reflect the final state

## Living Documents

- If ANY new package is installed (pip, npm, pacman, yay), update docs/install.fish

## Formatting

- No em-dashes. Use " - " instead.
- Use "->" for arrows.
