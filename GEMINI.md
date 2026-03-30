# kjtcom - Agent Instructions (Gemini CLI)

## Read Order

1. docs/calgold-design-v3.10.md
2. docs/calgold-plan-v3.10.md (execute Section A only - stop at handoff checkpoint)

## Context

This is a split-agent iteration. You execute phases 1-5 (acquire, transcribe, extract, normalize, geocode) for CalGold Phase 3 - Stress Test (videos 61-90). After completing Section A, produce the handoff checkpoint file and STOP. Claude Code will execute phases 6-7.

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

## Gotcha G2 - CUDA LD_LIBRARY_PATH (READ THIS)

- faster-whisper/ctranslate2 WILL fail if LD_LIBRARY_PATH is not set
- LD_LIBRARY_PATH is set in ~/.config/fish/config.fish (added by Gemini CLI in v2.9, G23)
- LD_LIBRARY_PATH is also embedded in phase2_transcribe.py as a fallback
- Check: fish -c "echo \$LD_LIBRARY_PATH" (must be non-empty and include cuda/cublas/cudnn)
- If empty: fish -c "source ~/.config/fish/config.fish"
- This has caused interventions in EVERY phase. Do not skip this check.

## Transcription - CRITICAL (G18, G21)

- Gemini CLI has a 5-minute stdout timeout. Long transcriptions WILL be killed.
- ALL transcription MUST run as a background job with stdout polling.
- Use: fish -c "cd ~/dev/projects/kj
