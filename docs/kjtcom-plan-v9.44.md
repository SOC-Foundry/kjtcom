# kjtcom - Execution Plan v9.44

**Executing Agent:** Claude Code (Opus 4.6)
**Estimated Duration:** 2 hours
**Token Target:** <50K

---

## PRE-FLIGHT

- [ ] CLAUDE.md saved (v9.44)
- [ ] GEMINI.md saved (v9.44)
- [ ] docs/kjtcom-design-v9.44.md saved
- [ ] docs/kjtcom-plan-v9.44.md saved
- [ ] v9.43 docs archived: mv docs/kjtcom-*-v9.43.md docs/archive/ (NOT deleted)
- [ ] Verify archive integrity: ls docs/archive/ | grep -c "v9\." (should show files for v9.35 through v9.43)
- [ ] Ollama running, 4 models
- [ ] sudo systemctl restart kjtcom-telegram-bot
- [ ] set -gx IAO_ITERATION v9.44
- [ ] Firebase SA accessible

---

## STEP 1: Recover Deleted Docs (W5) - 5 min

```fish
cd ~/dev/projects/kjtcom
# Check archive state
echo "Archive count:" (ls docs/archive/ | wc -l)
ls docs/archive/ | grep v9.4

# Recover any missing v9.41/v9.42 docs from git history
for ver in v9.41 v9.42
    for type in build design plan report
        set file "docs/kjtcom-$type-$ver.md"
        if not test -f "docs/archive/kjtcom-$type-$ver.md"
            echo "Recovering: kjtcom-$type-$ver.md"
            git checkout HEAD~5 -- $file 2>/dev/null
            and mv $file docs/archive/ 2>/dev/null
        end
    end
end

echo "Archive count after recovery:" (ls docs/archive/ | wc -l)
```

---

## STEP 2: Fix Gemini Flash Auth (W1) - 15 min

1. Verify API key:

```fish
curl -s "https://generativelanguage.googleapis.com/v1beta/models?key=$GEMINI_API_KEY" | head -5
```

2. Test litellm:

```fish
python3 -c "
import litellm, os
try:
    r = litellm.completion(model='gemini/gemini-2.5-flash', messages=[{'role':'user','content':'say hello'}], thinking={'type':'disabled'})
    print('SUCCESS:', r.choices[0].message.content)
except Exception as e:
    print('FAIL:', e)
    # Try alternatives
    for m in ['gemini/gemini-2.0-flash-001', 'gemini/gemini-1.5-flash']:
        try:
            r = litellm.completion(model=m, messages=[{'role':'user','content':'say hello'}])
            print(f'ALT SUCCESS: {m}')
            break
        except Exception as e2:
            print(f'ALT FAIL: {m} - {e2}')
"
```

3. Check litellm version, upgrade if needed:

```fish
pip show litellm | grep Version
pip install litellm --upgrade --break-system-packages
```

4. Once working model string confirmed:
   - Add GEMINI_MODEL constant to scripts/utils/ollama_config.py
   - Update scripts/intent_router.py to import and use GEMINI_MODEL
   - Update scripts/telegram_bot.py synthesis calls
   - Test: `python3 -c "from scripts.intent_router import route_question; print(route_question('how many entities'))"`

---

## STEP 3: Fix Rating Sort (W2) - 15 min

Recommend Python-side sort (avoids composite index intervention):

1. Update scripts/firestore_query.py:
   - Add sort_field, sort_order, limit parameters to execute_query()
   - After fetching docs, sort in Python using nested field accessor
   - Apply limit after sort

2. Test:

```fish
python3 -c "
from scripts.firestore_query import execute_query
result = execute_query(
    {'t_log_type': 'tripledb', 't_any_cities': ['los angeles']},
    'list',
    sort_field='t_enrichment.google_places.rating',
    sort_order='desc',
    limit=3
)
print(result)
"
```

Expected: top 3 DDD restaurants in LA by Google Places rating.

If Python-side sort works, no Firebase console intervention needed.

---

## STEP 4: Verify Bot Session Memory + Rating Queries (W3) - 15 min

1. Restart bot:

```fish
sudo systemctl restart kjtcom-telegram-bot
sleep 5
sudo systemctl status kjtcom-telegram-bot
```

2. Test from Telegram:

```
/ask how many ddd restaurants in los angeles
  -> 26 results found

/ask out of those what are the 3 highest rated
  -> Session memory resolves "those", returns top 3 with ratings

/ask what is the highest rated rick steves destination in italy
  -> Sorted by rating

/ask what caused the G45 cursor bug
  -> ChromaDB route (unchanged)

/ask does guidepoint global provide professional services
  -> Web route (unchanged)
```

3. Log all test results in build log.

---

## STEP 5: Changelog + Report Template Fix (W6) - 15 min

1. Update template/artifacts/changelog-template.md:
   - Require NEW/UPDATED/FIXED prefix
   - Require specific numbers
   - Require agent list
   - Ban "TBD"

2. Update template/artifacts/report-template.md:
   - Add to evaluator prompt: "Use EXACT workstream names from design doc"
   - Trident results must be filled from event log
   - Evidence column required

3. Update scripts/generate_artifacts.py:
   - Changelog generator pulls from event log for numbers
   - If data missing, write "MISSING: [what data]" not "TBD"

---

## STEP 6: Living Docs + Re-embed - 10 min

1. Update docs/kjtcom-architecture.mmd if any changes
2. Re-embed archive:

```fish
python3 -u scripts/embed_archive.py
```

3. Update data/middleware_registry.json with GEMINI_MODEL constant
4. Add G57 to data/gotcha_archive.json if Gemini model string fix was needed

---

## STEP 7: Build + Deploy - 10 min

```fish
cd ~/dev/projects/kjtcom/app
flutter analyze
flutter test
flutter build web
cd ~/dev/projects/kjtcom
firebase deploy --only hosting
```

---

## STEP 8: Post-Flight Verification (W4 - MANDATORY) - 10 min

```fish
python3 scripts/post_flight.py
```

All checks must pass:
- [ ] site_200: kylejeromethompson.com returns HTTP 200
- [ ] bot_status: /status responds
- [ ] bot_query: /ask returns correct entity count (>= 6,181)
- [ ] architecture_html: kylejeromethompson.com/architecture.html loads

Additionally verify the new features manually from Telegram:
- [ ] Session memory: ask count, then "out of those..."
- [ ] Rating sort: "top 3 highest rated" returns sorted results
- [ ] Web route: external question returns Brave Search results

If ANY check fails: fix, re-deploy, re-verify.

---

## STEP 9: Workstream Evaluation + Artifacts - 15 min

1. Evaluate:

```fish
python3 -u scripts/run_evaluator.py --iteration v9.44 --workstreams
```

2. Generate drafts:

```fish
python3 -u scripts/generate_artifacts.py
```

3. Validate:

```fish
python3 -u scripts/generate_artifacts.py --validate-only
```

4. Promote:

```fish
python3 -u scripts/generate_artifacts.py --promote
```

5. Verify Evidence column populated. Verify workstream names match design doc. Verify changelog is not a stub.

6. Artifacts:
- [ ] docs/kjtcom-design-v9.44.md (pre-staged)
- [ ] docs/kjtcom-plan-v9.44.md (pre-staged)
- [ ] docs/kjtcom-build-v9.44.md (generated, verified, promoted)
- [ ] docs/kjtcom-report-v9.44.md (Evidence column, verified, promoted)
- [ ] docs/kjtcom-changelog.md (append - not a stub)
- [ ] agent_scores.json (append with workstreams)
- [ ] scripts/utils/ollama_config.py (MODIFIED - GEMINI_MODEL constant)
- [ ] scripts/intent_router.py (MODIFIED - use GEMINI_MODEL)
- [ ] scripts/telegram_bot.py (MODIFIED - use GEMINI_MODEL for synthesis)
- [ ] scripts/firestore_query.py (MODIFIED - sort_field/limit params)
- [ ] scripts/generate_artifacts.py (MODIFIED - changelog quality)
- [ ] template/artifacts/*.md (MODIFIED - quality requirements)
- [ ] data/gotcha_archive.json (MODIFIED - G57 if applicable)
- [ ] data/middleware_registry.json (MODIFIED)
- [ ] CLAUDE.md (v9.44)
- [ ] GEMINI.md (v9.44)

---

## INTERVENTIONS

Target: 0.

If Python-side sort doesn't work and Firestore composite index is needed: 1 expected intervention (Kyle clicks Firebase console URL). But design recommends Python-side sort to avoid this.

---

*Plan v9.44, April 5, 2026.*
