# kjtcom - Execution Plan v9.46

**Executing Agent:** Claude Code (Opus 4.6)
**Estimated Duration:** 2.5 hours
**Token Target:** <50K

---

## PRE-FLIGHT

- [ ] CLAUDE.md saved (v9.46)
- [ ] GEMINI.md saved (v9.46)
- [ ] docs/kjtcom-design-v9.46.md saved
- [ ] docs/kjtcom-plan-v9.46.md saved
- [ ] v9.45 docs archived: mv docs/kjtcom-*-v9.45.md docs/archive/
- [ ] Archive integrity: ls docs/archive/ | wc -l (>= 175)
- [ ] Ollama running, 4 models
- [ ] sudo systemctl restart kjtcom-telegram-bot
- [ ] set -gx IAO_ITERATION v9.46

---

## STEP 1: Create Qwen Evaluator Harness (W1) - 30 min

1. Create docs/evaluator-harness.md with full content from design doc W1
2. Update scripts/run_evaluator.py:
   - Read docs/evaluator-harness.md at startup
   - Prepend harness content to every Qwen evaluation prompt as system context
   - The harness is the personality directive; workstream data is the input
3. Update scripts/generate_artifacts.py:
   - Load evaluator-harness.md when generating report and changelog drafts
   - Apply same harness rules to artifact generation

4. Test: retroactive v9.45 evaluation

```fish
python3 -u scripts/run_evaluator.py --iteration v9.45 --workstreams --retroactive
```

5. Compare output:
   - Old v9.45 report: W5 = 9/10, W6 = 10/10
   - New evaluation should: W5 <= 8/10, W6 <= 8/10
   - Should include "What Could Be Better" section
   - Should have 0 instances of "Review..." or "TBD"
   - Should have 0 instances of banned phrases

If the re-evaluation still gives 10/10 or uses banned phrases, refine the harness and re-test.

---

## STEP 2: README Overhaul (W2) - 45 min

Full review. Read the entire README top to bottom. Fix every stale item.

### Section-by-Section

1. **Header badges:** verify Flutter, Firebase, Gemini, Claude badge versions
2. **Intro paragraph:** entity count (6,181), pipeline count (3), iteration count (update to 46)
3. **Phase/version line:** Phase 9 v9.46
4. **Live App section:**
   - Add: session memory, rating-aware queries, web search route
   - Update Gotcha tab reference: G1-G57 (not G1-G44)
   - Add: Telegram bot link (@kjtcom_iao_bot)
5. **Architecture section:**
   - Verify architecture.html link works
   - Update description: 3-route intent router, systemd bot, session memory, rating sort, artifact automation, gotcha archive, middleware registry
6. **Data Architecture:** verify accuracy
7. **Thompson Indicator Fields:** verify 22 fields, examples current
8. **Add new section: Telegram Bot**
   ```markdown
   ## Telegram Bot

   **[@kjtcom_iao_bot](https://t.me/kjtcom_iao_bot)** - Query 6,181 entities via Telegram:

   - `/ask [question]` - natural language queries routed to Firestore, ChromaDB, or web
   - `/status` - system health check
   - `/search [query]` - Brave Search web lookup
   - `/help` - command reference

   Features: session memory (10-min context window), rating-aware queries ("top 3 highest rated in LA"), 3-route intent classification via Gemini Flash.
   ```
9. **Add new section: Middleware**
   ```markdown
   ## Middleware

   The middleware layer is the portable IAO infrastructure that stamps onto new projects. See [middleware_registry.json](data/middleware_registry.json) for the full component catalog.

   Key components: intent router, Firestore query module, artifact generator, evaluator harness, gotcha archive, event logging, bot framework, RAG pipeline.
   ```
10. **Changelog section:** add v9.41 through v9.46 entries (concise)
11. **Author section:** verify current
12. **Citing section:** verify current

---

## STEP 3: Phase 9 Audit (W3) - 20 min

Document Phase 9 achievements in the build log. Count:
- Total iterations in Phase 9 (v9.27 through v9.46 = 20)
- Zero-intervention iterations
- Key deliverables produced
- Middleware components created
- Dependencies upgraded
- Gotchas resolved

Write as a PHASE 9 SUMMARY section in the build log.

---

## STEP 4: Post-Flight + Middleware Update (W4) - 15 min

1. Run post_flight.py - all checks pass
2. Update data/middleware_registry.json: add evaluator-harness.md component
3. Re-embed archive:

```fish
python3 -u scripts/embed_archive.py
```

4. Rebuild architecture HTML if mmd changed:

```fish
python3 scripts/build_architecture_html.py
```

5. Build + deploy:

```fish
cd ~/dev/projects/kjtcom/app
flutter analyze
flutter test
flutter build web
cd ~/dev/projects/kjtcom
firebase deploy --only hosting
```

---

## STEP 5: Post-Flight Verification (MANDATORY) - 10 min

```fish
python3 scripts/post_flight.py
```

All checks pass. Additionally verify README renders correctly on GitHub (after Kyle pushes).

---

## STEP 6: Workstream Evaluation + Artifacts - 15 min

This is the FIRST evaluation using the new harness. Verify the output is meaningfully different from prior iterations.

```fish
python3 -u scripts/run_evaluator.py --iteration v9.46 --workstreams
python3 -u scripts/generate_artifacts.py
python3 -u scripts/generate_artifacts.py --validate-only
python3 -u scripts/generate_artifacts.py --promote
```

Verify:
- [ ] No workstream scored 10/10
- [ ] "What Could Be Better" section exists with >= 3 items
- [ ] No banned phrases in summary or scorecard
- [ ] Trident has actual values (token count, X/Y workstreams, measured metric)
- [ ] Evidence column populated
- [ ] Changelog uses NEW/UPDATED/FIXED with numbers

Artifacts:
- [ ] docs/kjtcom-design-v9.46.md (pre-staged)
- [ ] docs/kjtcom-plan-v9.46.md (pre-staged)
- [ ] docs/kjtcom-build-v9.46.md (with Phase 9 Summary)
- [ ] docs/kjtcom-report-v9.46.md (first harness-guided report)
- [ ] docs/kjtcom-changelog.md (append)
- [ ] docs/evaluator-harness.md (NEW)
- [ ] agent_scores.json (append)
- [ ] scripts/run_evaluator.py (MODIFIED - loads harness)
- [ ] scripts/generate_artifacts.py (MODIFIED - loads harness)
- [ ] README.md (OVERHAULED)
- [ ] data/middleware_registry.json (MODIFIED)
- [ ] CLAUDE.md (v9.46)
- [ ] GEMINI.md (v9.46)

---

## INTERVENTIONS

Target: 0.

---

*Plan v9.46, April 5, 2026.*
