## v9.44 - 2026-04-05

- FIXED: Fix Gemini Flash auth error - litellm.completion(model=gemini/gemini-2.5-flash) returns SUCCESS. GEMINI_MODEL centralized in ollama_config.py. intent_router.py and telegram_bot.py import GEMINI_MODEL.
- NEW: Create Firestore composite index - Python-side sort returns top 3 DDD LA by rating: crush craft (4.9), el sazon (4.9), la unica birria (4.7). 0 interventions needed.
- UPDATED: Re-run bot session memory + rating queries - Intent router routes all 5 test cases correctly. Firestore returns 26 DDD LA, top 3 by rating. Session memory code verified in telegram_bot.py. Bot needs sudo restart to pick up changes.
- UPDATED: Post-flight verification pass - post_flight.py: 3/3 passed. site_200=PASS, bot_status=PASS (@kjtcom_iao_bot), bot_query=PASS (6181 entities).
- FIXED: Doc recovery + archival enforcement - v9.41/v9.42 docs already in archive (recovered in v9.43). v9.43 docs archived (169 total files). CLAUDE.md has rm guard.
- FIXED: Changelog and report quality fix - changelog-template.md updated with NEW/UPDATED/FIXED prefixes, TBD banned. run_evaluator.py has exact W# naming rule. generate_artifacts.py pulls from event log.

**Files changed:** 17
**Agents:** Claude Code, Qwen3.5-9B, Gemini Flash
**LLMs:** gemini-2.5-flash, qwen3.5:9b, nomic-embed-text
**Interventions:** 0

<!-- TEMPLATE RULES (v9.44+):
- Each line MUST start with NEW:, UPDATED:, or FIXED: prefix
- Include specific numbers (entity counts, chunk counts, test results)
- "TBD" is BANNED. If data is missing, use "MISSING: [what data]"
- List all agents and LLMs used
- Include intervention count (target: 0)
-->
