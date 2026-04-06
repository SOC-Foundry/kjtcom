# kjtcom - Execution Plan v9.50

**Recommended Agent:** Claude Code (Opus 4.6)
**Estimated Duration:** 2.5 hours
**Token Target:** <50K

---

## PRE-FLIGHT

- [ ] CLAUDE.md/GEMINI.md saved (v9.50, >= 200 lines)
- [ ] Design + plan saved to docs/
- [ ] v9.49 docs to archive: mv docs/kjtcom-*-v9.49.md docs/archive/
- [ ] Clean: rm -f docs/drafts/*.md docs/changelog-v*.md
- [ ] Ollama running, 4 models
- [ ] sudo systemctl restart kjtcom-telegram-bot
- [ ] set -gx IAO_ITERATION v9.50

---

## STEP 1: Qwen Harness Bug Fixes (W1) - 30 min

1. Update data/eval_schema.json:
   - MCPs: add maxItems 3, add description "list ONLY MCPs actually used"
   - Add summary field (string, 50-500 chars, no JSON/markdown)
   - Verify schema valid: `python3 -c "import json, jsonschema; jsonschema.Draft7Validator.check_schema(json.load(open('data/eval_schema.json'))); print('OK')"`

2. Update docs/evaluator-harness.md:
   - Add MCP selection rule: "List ONLY MCPs actually invoked. Most workstreams use 0-1."
   - Add agent attribution rule: "You are the EVALUATOR. The executor is in the design doc header."
   - Add narrative rule: "Summary must be plain text, 2-4 sentences. No JSON, no code blocks."

3. Update scripts/run_evaluator.py:
   - Parse design doc header for executing agent name
   - Inject executing agent into Qwen prompt context
   - Validate MCPs field is not the full enum list

4. Update scripts/generate_artifacts.py:
   - Add render_report_markdown() that converts validated JSON to proper markdown
   - Never dump raw JSON into report or build log

5. Test: `python3 -u scripts/run_evaluator.py --iteration v9.49 --workstreams --retroactive`
   - Verify MCPs are selective (not all 5)
   - Verify agent is "claude-code" not "Qwen"
   - Verify summary is plain text

---

## STEP 2: README Overhaul (W2) - 20 min

Full review per design doc W2. Key changes:
- Replace tech stack table with expanded version (21 rows)
- Add Claw3D link in header links
- Add Telegram Bot link
- Update version to v9.50
- Update tab list (MW replacing Gotcha)
- Verify all links work
- Append v9.49 + v9.50 changelog entries

---

## STEP 3: Claw3D Update (W3) - 30 min

1. Read current app/web/claw3d.html
2. Update node data array: add ~13 new nodes (see design doc W3 table)
3. Update connections array: add new relationships
4. Update version text: "kjtcom v9.50" instead of "v9.38"
5. Verify locally: `flutter build web` then open claw3d.html in browser
6. Count: should have ~28 nodes total (15 original + 13 new)

---

## STEP 4: Post-Flight + Deploy (W4) - 15 min

```fish
cd ~/dev/projects/kjtcom/app
flutter analyze && flutter test && flutter build web
cd ~/dev/projects/kjtcom && firebase deploy --only hosting
python3 scripts/post_flight.py
```

Verify: site, bot, architecture.html, claw3d.html (should show new nodes).

---

## STEP 5: Evaluation + Artifacts (corrected order)

```fish
python3 -u scripts/run_evaluator.py --iteration v9.50 --workstreams
python3 -u scripts/generate_artifacts.py
python3 -u scripts/generate_artifacts.py --validate-only
python3 -u scripts/generate_artifacts.py --promote
```

Artifacts:
- [ ] Design, plan, build, report (promoted from drafts)
- [ ] docs/kjtcom-changelog.md (APPENDED)
- [ ] data/eval_schema.json (MODIFIED)
- [ ] docs/evaluator-harness.md (MODIFIED)
- [ ] scripts/run_evaluator.py (MODIFIED)
- [ ] scripts/generate_artifacts.py (MODIFIED)
- [ ] app/web/claw3d.html (MODIFIED - ~28 nodes)
- [ ] README.md (OVERHAULED)
- [ ] CLAUDE.md + GEMINI.md (v9.50, >= 200 lines)

---

*Plan v9.50, April 5, 2026.*
