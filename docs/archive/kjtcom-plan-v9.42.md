# kjtcom - Execution Plan v9.42

**Executing Agent:** Claude Code (Opus 4.6)
**Estimated Duration:** 4 hours
**Token Target:** <50K

---

## PRE-FLIGHT

- [ ] CLAUDE.md saved to ~/dev/projects/kjtcom/ (this file, v9.42)
- [ ] GEMINI.md saved to ~/dev/projects/kjtcom/ (v9.42)
- [ ] Design doc saved: docs/kjtcom-design-v9.42.md
- [ ] Plan doc saved: docs/kjtcom-plan-v9.42.md
- [ ] v9.41 docs archived: cp docs/kjtcom-*-v9.41.md docs/archive/
- [ ] v9.41 drafts cleaned: rm -rf docs/drafts/*.md (already promoted or discarded)
- [ ] Ollama running, 4 models (ollama list)
- [ ] Telegram bot stopped (systemctl stop kjtcom-telegram-bot 2>/dev/null; tmux kill-session -t telegram-bot 2>/dev/null)
- [ ] set -gx IAO_ITERATION v9.42
- [ ] Firebase SA accessible (~/.config/gcloud/kjtcom-sa.json)

---

## STEP 1: Fix Artifact Workflow (W3 partial) - 20 min

Fix the v9.41 problems first so they don't repeat this iteration.

1. Update scripts/generate_artifacts.py:
   - Add execution cross-check: verify workstream outcomes against exit codes and file existence
   - Add --promote flag: copies validated drafts from docs/drafts/ to docs/
   - Add --validate-only flag
   - Log promotion actions via iao_logger.py
2. Update scripts/utils/ollama_config.py:
   - Add OLLAMA_BATCH_DEFAULTS: timeout 2700 (45 min), num_predict 2048
   - Export merge_batch_defaults() function
3. Update scripts/run_evaluator.py:
   - Accept execution context (exit codes, created files) for ground-truth cross-check
   - Qwen evaluates with reality, not just interpretation

---

## STEP 2: TripleDB County Enrichment (W1) - 60 min

1. Create scripts/enrich_counties.py:
   - Read all TripleDB entities from Firestore (t_log_type == "tripledb")
   - For entities with coordinates: reverse geocode via Nominatim (1 req/sec) to get county
   - For entities without coordinates but with city+state: use a static county lookup
   - Dry-run first: python3 -u scripts/enrich_counties.py --dry-run
   - Review dry-run output for accuracy
   - Production run: python3 -u scripts/enrich_counties.py --write
   - Batch writes to Firestore (500/batch)
   - Log all enrichment via iao_logger.py
2. Verify: query Firestore for TripleDB entities with t_any_counties populated
3. Update data/schema_reference.json: note TripleDB now has counties
4. Cross-pipeline audit: check CalGold and RickSteves for any similar field gaps. Log findings.

```fish
# Dry run
python3 -u scripts/enrich_counties.py --dry-run | tee /tmp/county-enrichment-dry.log
# Review output, then:
python3 -u scripts/enrich_counties.py --write
```

---

## STEP 3: Bot Resiliency (W2) - 30 min

1. Create kjtcom-telegram-bot.service (see design doc W2)
2. pip install sdnotify --break-system-packages
3. Add watchdog ping to telegram_bot.py main loop
4. Create /home/kyle/.config/kjtcom/bot.env (template only - Kyle fills in keys)
5. Install and enable:

```fish
sudo cp kjtcom-telegram-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable kjtcom-telegram-bot
sudo systemctl start kjtcom-telegram-bot
sudo systemctl status kjtcom-telegram-bot
# Verify bot responds
# Kill old tmux session
tmux kill-session -t telegram-bot 2>/dev/null
```

6. Test resiliency:
   - sudo systemctl stop kjtcom-telegram-bot
   - Wait 30 seconds
   - sudo systemctl status kjtcom-telegram-bot (should show restarting)
   - Send /status via Telegram (should respond after restart)

---

## STEP 4: Internet Query Stream (W4) - 20 min

1. Update scripts/intent_router.py:
   - Add "web" route to schema reference prompt
   - Update routing prompt: if question is about external topics (not kjtcom entities, not dev history), route to web
2. Update scripts/telegram_bot.py /ask handler:
   - Add web route handler: call brave_search.py, pass results through Gemini Flash synthesis
   - Log as api_call
3. Test:

```
/ask does guidepoint global provide professional services in washington dc area
  -> web route, Brave Search results, Gemini synthesis

/ask how many Italian restaurants in Orange County in DDD
  -> firestore route (unchanged)

/ask what caused the G45 cursor bug
  -> chromadb route (unchanged)
```

---

## STEP 5: Gotcha Archive + Harness Registry (W5) - 30 min

1. Create data/gotcha_archive.json:
   - Extract all resolved gotchas from KT docs (G2, G23, G31, G36, G37, G39, G41, G42, G46, G49, G50, G51, G52, G54, G55)
   - For each: ID, description, resolution, iteration_resolved, root_cause category, prevention pattern
   - Root cause categories: environment, llm_config, dependency, firestore, flutter, pipeline, mcp, security, timeout
2. Create data/middleware_registry.json:
   - Catalog all harness files, scripts, templates, data stores
   - Version tracking per component
   - Dependency mapping
3. Update scripts/run_evaluator.py to query gotcha_archive.json when evaluating - "has this problem been seen before?"

---

## STEP 6: Registry Rebuild Retry (W3 continued) - 5 min (launch + wait)

With 45-minute timeout:

```fish
set -gx IAO_ITERATION v9.42
timeout 2700 python3 -u scripts/build_registry_v2.py
```

If it completes: verify iteration_registry.json covers v0.5 through v9.41.
If it times out again: log as G56, investigate whether Qwen calls can be parallelized or batched.

---

## STEP 7: Living Docs + Deploy (W5 continued + W6 partial) - 20 min

1. Update docs/kjtcom-architecture.mmd:
   - Add GOTCHA_ARCHIVE, HARNESS_REGISTRY, COUNTY_ENRICHMENT to middleware
   - Add SYSTEMD_SERVICE to user layer
   - Add WEB_SEARCH route from INTENT_ROUTER to BRAVE
   - Update header: "Updated: v9.42"
2. Update docs/install.fish:
   - Add sdnotify pip package
   - Add systemd service setup instructions
   - Add county enrichment script note
3. Build + deploy:

```fish
cd ~/dev/projects/kjtcom/app
flutter analyze
flutter test
flutter build web
cd ~/dev/projects/kjtcom
firebase deploy --only hosting
```

---

## STEP 8: Intranet Update Artifact (W6) - 20 min

Create docs/cross-project/intranet-update-v9.42.md:
- OpenClaw deployment lessons
- Middleware components ready for adoption
- systemd bot pattern
- RBAC approach (Okta groups -> dataset permissions -> Telegram user whitelist)
- Embedded intranet architecture mermaid chart

---

## STEP 9: Workstream Evaluation + Artifact Generation - 15 min

1. Run Qwen evaluator with workstream-level scoring:

```fish
python3 -u scripts/run_evaluator.py --iteration v9.42 --workstreams
```

2. Generate draft artifacts:

```fish
python3 -u scripts/generate_artifacts.py
```

3. Cross-check Qwen draft accuracy against actual execution:

```fish
python3 -u scripts/generate_artifacts.py --validate-only
```

4. Promote validated drafts:

```fish
python3 -u scripts/generate_artifacts.py --promote
```

5. Verify docs/ has final build log, report, and changelog entry.

6. Final artifacts:
- [ ] docs/kjtcom-design-v9.42.md (pre-staged)
- [ ] docs/kjtcom-plan-v9.42.md (pre-staged)
- [ ] docs/kjtcom-build-v9.42.md (generated, cross-checked, promoted)
- [ ] docs/kjtcom-report-v9.42.md (generated with Workstream Scorecard, promoted)
- [ ] docs/kjtcom-changelog.md (append v9.42)
- [ ] agent_scores.json (append v9.42 with workstreams)
- [ ] scripts/enrich_counties.py (NEW)
- [ ] kjtcom-telegram-bot.service (NEW)
- [ ] data/gotcha_archive.json (NEW)
- [ ] data/middleware_registry.json (NEW)
- [ ] docs/cross-project/intranet-update-v9.42.md (NEW)
- [ ] scripts/telegram_bot.py (MODIFIED - web route, systemd watchdog)
- [ ] scripts/intent_router.py (MODIFIED - 3rd route)
- [ ] scripts/generate_artifacts.py (MODIFIED - promote, validate, cross-check)
- [ ] scripts/run_evaluator.py (MODIFIED - execution context, gotcha query)
- [ ] scripts/utils/ollama_config.py (MODIFIED - batch defaults, 45min timeout)
- [ ] data/schema_reference.json (MODIFIED - TripleDB counties)
- [ ] docs/kjtcom-architecture.mmd (MODIFIED)
- [ ] docs/install.fish (MODIFIED)
- [ ] CLAUDE.md (v9.42)
- [ ] GEMINI.md (v9.42)
- [ ] README.md (update if needed)

---

## INTERVENTIONS

Target: 0.

Potential intervention points (pre-mitigated):
- Firebase SA: ~/.config/gcloud/kjtcom-sa.json (hardcoded)
- bot.env: template created, Kyle fills in keys manually (1 expected intervention)
- County enrichment dry-run: review output before --write (planned review, not intervention)
- Nominatim rate limit: 1 req/sec enforced in script (1,100 entities = ~18 min)

---

*Plan v9.42, April 5, 2026.*
