# kjtcom - Execution Plan v9.51

**Recommended Agent:** Claude Code
**Estimated Duration:** 2 hours
**Token Target:** <50K

---

## PRE-FLIGHT

- [ ] CLAUDE.md/GEMINI.md saved (v9.51, >= 200 lines)
- [ ] Design + plan in docs/. v9.50 docs to archive. Clean drafts + orphaned changelogs.
- [ ] Ollama, bot restart, IAO_ITERATION=v9.51

---

## STEP 1: Fix Search Button + Add 3D Button (W1) - 20 min

1. Debug search button layout - check query_editor.dart, app_shell.dart
2. Add 3D button/link in app bar - IconButton linking to /claw3d.html
3. flutter analyze, flutter test, verify visually

---

## STEP 2: Fix Score Scale (W2) - 10 min

1. Update data/eval_schema.json: score description "X/10 not X/9"
2. Update docs/evaluator-harness.md: "Always X/10. Never X/9."
3. Update scripts/generate_artifacts.py: format_score() always outputs "{score}/10"

---

## STEP 3: Fix Build Log Rendering (W3) - 15 min

1. Add render_build_markdown() to scripts/generate_artifacts.py
2. Build template uses rendered markdown, not raw JSON
3. Test: generate a draft build log, verify no JSON in output

---

## STEP 4: Harness Hardening (W4) - 20 min

1. Add LLM name rules to evaluator-harness.md (exact Ollama model names)
2. Add Trident cost rule (count llm_call events, don't say "0 tokens")
3. Create scripts/test_eval_schema.py with valid/invalid test payloads
4. Run tests: `python3 scripts/test_eval_schema.py`

---

## STEP 5: Build + Deploy + Post-Flight (W5) - 15 min

```fish
cd ~/dev/projects/kjtcom/app && flutter analyze && flutter test && flutter build web
cd ~/dev/projects/kjtcom && firebase deploy --only hosting
python3 scripts/post_flight.py
```

Verify: search button, 3D button, MW tab, bot, site.

---

## STEP 6: Evaluation + Artifacts (corrected order)

```fish
python3 -u scripts/run_evaluator.py --iteration v9.51 --workstreams
python3 -u scripts/generate_artifacts.py
python3 -u scripts/generate_artifacts.py --validate-only
python3 -u scripts/generate_artifacts.py --promote
```

Verify: scores as X/10, no raw JSON in build log, 5 workstreams, no hallucinated extras.

---

*Plan v9.51, April 5, 2026.*
