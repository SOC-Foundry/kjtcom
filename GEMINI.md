# kjtcom - Agent Instructions (Gemini CLI)

## Read Order

1. docs/ricksteves-design-v3.11.md
2. docs/ricksteves-plan-v3.11.md (execute Section A only - stop at handoff checkpoint)

## Context

This is a split-agent iteration. You execute phases 1-5 (acquire, transcribe, extract, normalize, geocode) for RickSteves Phase 3 - Stress Test (videos 91-120). After completing Section A, produce the handoff checkpoint file and STOP. Claude Code will execute phases 6-7.

## Shell - MANDATORY

- Gemini CLI runs bash by default. All commands MUST be wrapped in fish -c "..." (G19)
- Environment variables are in ~/.config/fish/config.fish
- NEVER use bare bash commands - always wrap: fish -c "your command here"
- NEVER use bash syntax (no ${VAR}, no heredocs, no source ~/.bashrc)
- For multi-line commands, use fish -c with semicolons or && between commands
- Use "command ls" or Python for file listing - fish ls alias adds ANSI color codes that break parsing (G22)

## Security - ABSOLUTE RULES

- NEVER write API keys, tokens, or credentials into ANY file in the repo
- NEVER include API keys in build logs, reports, or changelog artifacts
- NEVER echo or print API key values in commands that get logged
- NEVER cat or read ~/.config/fish/config.fish - IT CONTAINS API KEYS (G20)
- To check a specific variable, use: fish -c "grep VARIABLE_NAME ~/.config/fish/config.fish | wc -l" (count only, never print value)
- If a key needs to be tested, print only "SET" or "NOT SET", never the value
- Read keys from environment variables ONLY
- Violation of these rules is a BLOCKING failure - stop and alert Kyle

## Gotcha G2 - CUDA LD_LIBRARY_PATH

- RESOLVED in v3.10. LD_LIBRARY_PATH is embedded in phase2_transcribe.py AND config.fish.
- Still verify in pre-flight: fish -c "echo \$LD_LIBRARY_PATH" (must be non-empty)

## Transcription - CRITICAL (G18, G21)

- Gemini CLI has a 5-minute stdout timeout. Long transcriptions WILL be killed.
- ALL transcription MUST run as a background job with stdout polling.
- Use: fish -c "cd ~/dev/projects/kjtcom && nohup python3 -u pipeline/scripts/phase2_transcribe.py --pipeline ricksteves --start 91 --limit 30 > transcribe_v3.11.log 2>&1 &"
- Poll every 60 seconds: fish -c "command ls ~/dev/projects/kjtcom/pipeline/data/ricksteves/transcripts/*.json | wc -l"
- NEVER start a second transcription process (G21 - CUDA OOM on 8GB VRAM)
- Rick Steves episodes are 30-60 min. Budget ~30 minutes for transcription to complete.

## Permissions

- CAN: pip install, npm install (project-level)
- CANNOT: git add / commit / push (human commits at phase boundaries)
- CANNOT: sudo (ask Kyle)
- CANNOT: flutter build web, firebase deploy (Claude Code handles deployment)

## Database Rules

- Do NOT load to Firestore in Section A. Phase 7 (load) is handled by Claude Code in Section B.
- Your scope ends at phase 5 (geocoded JSONL output).

## Handoff Protocol

After completing phases 1-5, produce the handoff checkpoint:
- File: pipeline/data/ricksteves/handoff-v3.11.json
- Contents: iteration, agent, phases completed, file counts for audio/transcripts/extracted
- Print the checkpoint contents to stdout
- STOP. Do not proceed to phases 6-7.

## Formatting

- No em-dashes. Use " - " instead.
- Use "->" for arrows.
