# kjtcom - Execution Plan v9.49

**Recommended Agent:** Claude Code (Opus 4.6)
**Estimated Duration:** 3-4 hours (unhurried - take time with Qwen harness)
**Token Target:** <50K

---

## PRE-FLIGHT

- [ ] CLAUDE.md or GEMINI.md saved (v9.49, verify >= 200 lines: wc -l)
- [ ] docs/kjtcom-design-v9.49.md saved
- [ ] docs/kjtcom-plan-v9.49.md saved
- [ ] v9.48 docs to archive: mv docs/kjtcom-*-v9.48.md docs/archive/
- [ ] Clean drafts: rm -f docs/drafts/*.md
- [ ] Clean orphaned changelogs: rm -f docs/changelog-v*.md
- [ ] Archive integrity: ls docs/archive/ | wc -l
- [ ] Ollama running, 4 models
- [ ] sudo systemctl restart kjtcom-telegram-bot
- [ ] set -gx IAO_ITERATION v9.49
- [ ] pip install jsonschema --break-system-packages

---

## STEP 1: Create Evaluation JSON Schema (W1) - 20 min

1. Create data/eval_schema.json with the strict schema from design doc W1
2. Key constraints:
   - score max 9 (never 10)
   - mcps enum with 5 valid names + "-"
   - outcome enum with 4 values
   - improvements minItems 2
   - what_could_be_better minItems 3
   - delivery pattern "X/Y workstreams"
   - evidence minLength 10
3. Test schema validity:

```fish
python3 -c "
import json, jsonschema
schema = json.load(open('data/eval_schema.json'))
jsonschema.Draft7Validator.check_schema(schema)
print('Schema valid')
"
```

---

## STEP 2: Build Validation + Retry Loop (W1 continued) - 40 min

1. Update scripts/run_evaluator.py:
   - Import jsonschema
   - Add validate_qwen_output() function
   - Add evaluate_with_retry() function (max 3 retries)
   - On validation failure: build specific error feedback and re-prompt Qwen
   - On success: save validated JSON to agent_scores.json
   - NEVER read current iteration build log (W2 fix)
   - Read design doc for workstream list
   - Read event log for execution context

2. Update docs/evaluator-harness.md:
   - Explain the schema-validated approach
   - Qwen must return ONLY a JSON object conforming to the schema
   - List the validation rules so Qwen can self-check before responding

3. Test with retroactive evaluation:

```fish
python3 -u scripts/run_evaluator.py --iteration v9.48 --workstreams --retroactive
```

Verify: valid JSON, exactly 4 workstreams, no 10/10, improvements per workstream.

---

## STEP 3: Fix Execution Order (W2) - 15 min

1. Update scripts/run_evaluator.py:
   - Remove any code that reads docs/kjtcom-build-v{X}.md for current iteration
   - Evaluation inputs: design doc + event log + file existence checks
   - Add clear comment: "Evaluator reads execution context, NOT build log"

2. Update scripts/generate_artifacts.py:
   - Build log generation reads: event log + agent_scores.json + git diff
   - Report generation reads: agent_scores.json (validated JSON)
   - Changelog appends to docs/kjtcom-changelog.md (single file)
   - Remove any changelog-v{X}.md creation

3. Verify the sequence works:

```fish
# Simulate: evaluator runs, THEN artifacts generated
python3 -u scripts/run_evaluator.py --iteration v9.49 --workstreams
python3 -u scripts/generate_artifacts.py
ls docs/drafts/
```

---

## STEP 4: Middleware Tab (W3) - 45 min

1. Create app/lib/widgets/mw_tab.dart:
   - Load middleware_registry.json and gotcha_archive.json from assets
   - Display component registry as a styled table/list
   - Display resolved gotchas as expandable cards
   - Include agent roster section
   - Dark SIEM styling consistent with other tabs

2. Copy data files to assets:

```fish
cp data/middleware_registry.json app/assets/
cp data/gotcha_archive.json app/assets/
```

3. Update pubspec.yaml assets list
4. Update main app scaffold: rename tab 5 from Gotcha to MW
5. Optionally keep gotcha functionality as a section within MW

6. Test:

```fish
cd ~/dev/projects/kjtcom/app
flutter analyze
flutter test
flutter run -d chrome
# Navigate to MW tab, verify data displays
```

---

## STEP 5: README Overhaul (W4) - 20 min

3-iteration cadence. Full review per design doc W4 checklist. Key updates:
- v9.49 version
- MW tab replacing Gotcha tab
- Update tab list in Live App section
- Verify all links work
- Append v9.48 + v9.49 changelog entries

---

## STEP 6: Living Docs + Post-Flight (W5) - 15 min

1. Update middleware_registry.json: add eval_schema.json, update script versions
2. Update architecture.mmd: MW tab in frontend subgraph
3. Rebuild architecture HTML:

```fish
python3 scripts/build_architecture_html.py
```

4. Build + deploy:

```fish
cd ~/dev/projects/kjtcom/app
flutter analyze
flutter test
flutter build web
cd ~/dev/projects/kjtcom
firebase deploy --only hosting
```

---

## STEP 7: Post-Flight Verification (MANDATORY)

```fish
python3 scripts/post_flight.py
```

All checks pass. Additionally verify:
- MW tab renders on live site
- Bot responds to /ask
- architecture.html loads
- claw3d.html loads

---

## STEP 8: Evaluation + Artifacts (CORRECTED ORDER)

```fish
# 1. Evaluate (reads design doc + event log, NOT build log)
python3 -u scripts/run_evaluator.py --iteration v9.49 --workstreams

# 2. Generate artifacts (reads evaluation scores)
python3 -u scripts/generate_artifacts.py

# 3. Validate
python3 -u scripts/generate_artifacts.py --validate-only

# 4. Promote
python3 -u scripts/generate_artifacts.py --promote
```

Verify: schema-valid JSON in agent_scores.json, exactly 5 workstreams, no hallucinated extras, no 10/10 scores, improvements listed, "What Could Be Better" with 3+ items, changelog appended to single file.

Artifacts:
- [ ] docs/kjtcom-design-v9.49.md (pre-staged)
- [ ] docs/kjtcom-plan-v9.49.md (pre-staged)
- [ ] docs/kjtcom-build-v9.49.md (generated AFTER evaluation, promoted)
- [ ] docs/kjtcom-report-v9.49.md (from validated JSON, promoted)
- [ ] docs/kjtcom-changelog.md (APPENDED, single file)
- [ ] data/eval_schema.json (NEW)
- [ ] app/lib/widgets/mw_tab.dart (NEW)
- [ ] scripts/run_evaluator.py (MODIFIED - schema validation, retry loop, no build log read)
- [ ] scripts/generate_artifacts.py (MODIFIED - reads validated JSON, single changelog)
- [ ] docs/evaluator-harness.md (MODIFIED - schema reference)
- [ ] data/middleware_registry.json (MODIFIED)
- [ ] docs/kjtcom-architecture.mmd (MODIFIED - MW tab)
- [ ] app/web/architecture.html (REBUILT)
- [ ] README.md (OVERHAULED)
- [ ] CLAUDE.md (v9.49, >= 200 lines)
- [ ] GEMINI.md (v9.49, >= 200 lines)

---

## INTERVENTIONS

Target: 0.

---

*Plan v9.49, April 5, 2026.*
