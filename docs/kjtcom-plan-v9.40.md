# kjtcom - Execution Plan v9.40

**Executing Agent:** Claude Code (Opus 4.6)
**Estimated Duration:** 2 hours
**Token Target:** <50K

---

## PRE-FLIGHT

- [ ] Ollama running, 4 models
- [ ] Telegram bot in tmux (kill and restart after fixes)
- [ ] v9.39 docs archived
- [ ] set -gx IAO_ITERATION v9.40

---

## STEP 1: Fix /ask RAG Context (W1) - 30 min

1. Read scripts/telegram_bot.py - find /ask handler
2. Read scripts/query_rag.py - verify it returns chunk text (not just metadata)
3. Fix: inject ChromaDB chunks as context into Gemini prompt
4. Test locally: `python3 -c "from scripts.query_rag import ...; print(query('G45 cursor bug'))"`
5. Verify chunks contain actual text content

---

## STEP 2: Telegram Logging + UX (W2, W3) - 20 min

1. Add iao_logger calls to every handler in telegram_bot.py
2. Add /start handler (welcome + command list)
3. Add /help handler (same as /start)
4. Add default handler for plain text ("Unknown command. Try /status or /ask")
5. Log inbound messages and outbound responses

---

## STEP 3: G51 Permanent Fix (W5) - 10 min

1. Create scripts/utils/ollama_config.py with think:false + num_predict:512 defaults
2. Update ollama_logged.py to merge defaults
3. Verify all Ollama-calling scripts inherit the config

---

## STEP 4: Dependency Freshness (W4) - 30 min

```fish
cd ~/dev/projects/kjtcom/app
flutter pub upgrade
flutter pub outdated
# Fix any analysis issues
flutter analyze
flutter test
# Update pubspec SDK constraint if needed
flutter build web
```

---

## STEP 5: Restart Bot + Test - 15 min

```fish
tmux kill-session -t telegram-bot
tmux new-session -d -s telegram-bot "fish -c 'source ~/.config/fish/config.fish; set -gx IAO_ITERATION v9.40; cd ~/dev/projects/kjtcom; python3 scripts/telegram_bot.py'"
```

Test from Telegram:
- /start (should show welcome)
- /status (system health)
- /ask What caused the G45 cursor bug? (should return RAG-powered answer)
- /search flutter_code_editor (Brave Search)
- /scores (leaderboard)
- Plain text message (should get "Unknown command" response)

---

## STEP 6: Deploy + Artifacts - 15 min

```fish
cd ~/dev/projects/kjtcom && firebase deploy --only hosting
```

- [ ] docs/kjtcom-design-v9.40.md (pre-staged)
- [ ] docs/kjtcom-plan-v9.40.md (pre-staged)
- [ ] docs/kjtcom-build-v9.40.md
- [ ] docs/kjtcom-report-v9.40.md (Agent Scorecard + Event Log Summary)
- [ ] docs/kjtcom-changelog.md (append)
- [ ] agent_scores.json (append)
- [ ] scripts/utils/ollama_config.py (NEW)
- [ ] scripts/telegram_bot.py (MODIFIED)
- [ ] scripts/query_rag.py (verify/fix)
- [ ] docs/install.fish, architecture.mmd, README (if changes)
- [ ] CLAUDE.md, GEMINI.md (update read order)

---

## INTERVENTIONS

Target: 0. All decisions pre-answered.

---

*Plan v9.40, April 5, 2026.*
