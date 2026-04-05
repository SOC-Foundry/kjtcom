# kjtcom - Execution Plan v9.43

**Executing Agent:** Claude Code (Opus 4.6)
**Estimated Duration:** 3 hours
**Token Target:** <50K

---

## PRE-FLIGHT

- [ ] CLAUDE.md saved to ~/dev/projects/kjtcom/ (v9.43)
- [ ] GEMINI.md saved to ~/dev/projects/kjtcom/ (v9.43)
- [ ] Design doc saved: docs/kjtcom-design-v9.43.md
- [ ] Plan doc saved: docs/kjtcom-plan-v9.43.md
- [ ] v9.42 docs archived: mv docs/kjtcom-*-v9.42.md docs/archive/ (do NOT delete)
- [ ] Recover v9.41 docs if missing: git checkout HEAD~2 -- docs/kjtcom-*-v9.41.md; mv docs/kjtcom-*-v9.41.md docs/archive/
- [ ] Ollama running, 4 models
- [ ] systemctl restart kjtcom-telegram-bot
- [ ] set -gx IAO_ITERATION v9.43
- [ ] Firebase SA accessible

---

## STEP 1: Recover v9.41 Docs + Verify Archive (W3 partial) - 5 min

```fish
cd ~/dev/projects/kjtcom
# Check if v9.41 docs exist in archive
ls docs/archive/kjtcom-*-v9.41.md 2>/dev/null
# If missing, recover from git history
git log --oneline -5  # Find the commit before deletion
git checkout HEAD~2 -- docs/kjtcom-design-v9.41.md docs/kjtcom-plan-v9.41.md docs/kjtcom-build-v9.41.md docs/kjtcom-report-v9.41.md 2>/dev/null
mv docs/kjtcom-*-v9.41.md docs/archive/ 2>/dev/null
# Verify v9.42 docs are archived too
mv docs/kjtcom-*-v9.42.md docs/archive/ 2>/dev/null
ls docs/archive/ | grep v9.4
```

---

## STEP 2: Bot Session Memory (W1) - 30 min

1. Edit scripts/telegram_bot.py:
   - Add module-level `user_sessions = {}` dict
   - Add `resolve_context(question, user_id)` function (see design doc)
   - In /ask handler: after Firestore query, store filters + results + count + timestamp in user_sessions[user_id]
   - Before routing: check for context references ("those", "them", "the results")
   - If context found and < 10 min old: pass previous result set to Gemini Flash for follow-up analysis
   - Log context resolution via iao_logger.py
2. Test:

```
/ask how many ddd restaurants in los angeles
  -> 26 results found

/ask out of those 26 what are the 3 highest rated
  -> Should resolve "those 26" from session, pass to Gemini with rating data
```

---

## STEP 3: Rating-Aware Queries (W2) - 20 min

1. Update data/schema_reference.json:
   - Add sortable_fields section with t_enrichment.google_places.rating and user_ratings_total
   - Add aliases: "highest rated", "best", "top", "most reviewed", "popular"
2. Update scripts/intent_router.py routing prompt:
   - Add sort/limit rules for rating queries
   - Update JSON response format to include "sort" and "limit" fields
3. Update scripts/firestore_query.py:
   - Accept sort_field, sort_order, limit parameters
   - Apply Firestore orderBy + limit
   - Check if composite index is needed (may need to create via Firebase console)
4. Test:

```
/ask what are the 3 highest rated ddd restaurants in los angeles
  -> Firestore route with sort by rating desc, limit 3
```

---

## STEP 4: Architecture HTML Page (W4) - 30 min

1. Read docs/kjtcom-architecture.mmd (latest version from v9.42)
2. Create scripts/build_architecture_html.py:
   - Reads the .mmd file
   - Strips %% comment lines
   - Injects into HTML template with Mermaid JS CDN, dark theme matching kjtcom identity
   - Outputs to app/web/architecture.html
3. Run the builder:

```fish
python3 scripts/build_architecture_html.py
```

4. Verify locally:

```fish
cd ~/dev/projects/kjtcom/app
flutter build web
# Check app/build/web/architecture.html exists
```

5. Update README.md:
   - Add link to interactive diagram: `[Interactive Architecture Diagram](https://kylejeromethompson.com/architecture.html)`
   - Keep existing link to Mermaid source

---

## STEP 5: Qwen Evaluator Prompt Overhaul (W5) - 20 min

1. Edit scripts/run_evaluator.py:
   - Update the Qwen evaluation prompt with all 6 requirements from design doc
   - Add Evidence column to scorecard template
   - Enforce MCP whitelist: Firebase, Context7, Firecrawl, Playwright, Dart
   - Require specific numbers from event log
   - Ban "TBD" in Trident evaluation
2. Edit scripts/generate_artifacts.py:
   - Update report template with Evidence column
   - Update build template to require POST-FLIGHT VERIFICATION section
   - Changelog template must include concrete numbers

---

## STEP 6: Post-Flight Verification Script (W3 continued) - 20 min

1. Create scripts/post_flight.py:
   - verify_site(): curl kylejeromethompson.com, expect 200
   - verify_bot_status(): send /status via Telegram Bot API
   - verify_bot_query(): send /ask test query, verify response
   - run_all(): run all checks, log results, return pass/fail
2. Test:

```fish
python3 scripts/post_flight.py
```

Expected output:
```
  PASS: site_200
  PASS: bot_status
  PASS: bot_query
  Post-flight: 3/3 passed
```

---

## STEP 7: Verify v9.42 Data Integrity (W6) - 15 min

```fish
# County enrichment results
python3 -c "
from firebase_admin import firestore
import firebase_admin
from firebase_admin import credentials
cred = credentials.Certificate('~/.config/gcloud/kjtcom-sa.json')
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)
db = firestore.client()
tripledb = db.collection('locations').where('t_log_type', '==', 'tripledb').stream()
total = 0
has_counties = 0
for doc in tripledb:
    d = doc.to_dict()
    total += 1
    if d.get('t_any_counties'):
        has_counties += 1
print(f'TripleDB: {has_counties}/{total} have counties')
"

# Italian restaurants in Dallas
python3 -c "
from scripts.intent_router import route_question
import json
print(json.dumps(route_question('italian restaurants in dallas texas on ddd'), indent=2))
"
# Then execute the query to see if 0 is correct
```

---

## STEP 8: Re-embed Archive + Living Docs (W3 continued) - 15 min

1. Re-embed archive with v9.41/v9.42 docs:

```fish
python3 -u scripts/embed_archive.py
```

2. Update docs/kjtcom-architecture.mmd with any new components from this iteration
3. Rebuild architecture HTML:

```fish
python3 scripts/build_architecture_html.py
```

4. Update docs/install.fish if needed
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

## STEP 9: Post-Flight Verification (MANDATORY) - 10 min

```fish
python3 scripts/post_flight.py
```

If any check fails: log as gotcha, investigate, fix, re-deploy, re-verify.

Additionally test the new features:
```
/ask how many ddd restaurants in los angeles
/ask out of those what are the 3 highest rated
/ask what is the highest rated rick steves destination in italy
```

---

## STEP 10: Workstream Evaluation + Artifact Promotion - 15 min

1. Run evaluator:

```fish
python3 -u scripts/run_evaluator.py --iteration v9.43 --workstreams
```

2. Generate drafts:

```fish
python3 -u scripts/generate_artifacts.py
```

3. Validate Qwen accuracy (new v9.43 audit):

```fish
python3 -u scripts/generate_artifacts.py --validate-only
```

4. Promote:

```fish
python3 -u scripts/generate_artifacts.py --promote
```

5. Verify docs/ has all artifacts. Verify Evidence column is populated in report scorecard.

6. Final artifacts:
- [ ] docs/kjtcom-design-v9.43.md (pre-staged)
- [ ] docs/kjtcom-plan-v9.43.md (pre-staged)
- [ ] docs/kjtcom-build-v9.43.md (generated, cross-checked, promoted)
- [ ] docs/kjtcom-report-v9.43.md (with Evidence column, promoted)
- [ ] docs/kjtcom-changelog.md (append v9.43)
- [ ] agent_scores.json (append with workstreams)
- [ ] scripts/post_flight.py (NEW)
- [ ] scripts/build_architecture_html.py (NEW)
- [ ] app/web/architecture.html (NEW - deployed to Firebase)
- [ ] scripts/telegram_bot.py (MODIFIED - session memory)
- [ ] scripts/intent_router.py (MODIFIED - sort/limit)
- [ ] scripts/firestore_query.py (MODIFIED - orderBy/limit)
- [ ] scripts/run_evaluator.py (MODIFIED - prompt overhaul, Evidence column)
- [ ] scripts/generate_artifacts.py (MODIFIED - post-flight section, Evidence column)
- [ ] data/schema_reference.json (MODIFIED - sortable_fields)
- [ ] README.md (MODIFIED - architecture HTML link)
- [ ] docs/kjtcom-architecture.mmd (MODIFIED if needed)
- [ ] CLAUDE.md (v9.43)
- [ ] GEMINI.md (v9.43)

---

## INTERVENTIONS

Target: 0.

Potential intervention: Firestore composite index for orderBy on nested field (t_enrichment.google_places.rating). May require Firebase console action if the SDK doesn't auto-create.

---

*Plan v9.43, April 5, 2026.*
