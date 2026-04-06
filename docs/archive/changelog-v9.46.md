## v9.46 - 2026-04-05

- NEW: docs/evaluator-harness.md - Qwen personality file enforcing skeptical scoring (max 9/10, banned phrases, evidence required, "What Could Be Better" mandatory with >= 3 items)
- UPDATED: scripts/run_evaluator.py - loads evaluator harness as system prompt for all Qwen evaluations (both standard and workstream)
- UPDATED: scripts/generate_artifacts.py - loads evaluator harness for narrative generation, fixed NoneType tokens bug
- UPDATED: scripts/utils/ollama_logged.py - added system_prompt parameter to chat_logged()
- UPDATED: README.md - full overhaul: Telegram Bot section, Middleware section, Phase 10 Roadmap, G1-G57, v9.44-v9.46 changelog, version/phase updated
- UPDATED: data/middleware_registry.json - added evaluator-harness.md component, version bumps for modified scripts
- UPDATED: ChromaDB re-embedded - 1,590 chunks (up from 1,524)
- NEW: Phase 9 audit in build log - 20 iterations documented, 16/20 zero-intervention

**Files changed:** 13
**Agents:** Claude Code, Qwen3.5-9B, Gemini Flash
**LLMs:** gemini-2.5-flash, qwen3.5:9b, nomic-embed-text
**Interventions:** 0
