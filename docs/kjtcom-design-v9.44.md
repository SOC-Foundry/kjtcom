# kjtcom - Design Document v9.44

**Phase:** 9 - App Optimization
**Iteration:** 44
**Date:** April 5, 2026
**Focus:** Fix v9.43 Failures (Gemini Auth + Firestore Index) + Post-Flight Pass + Changelog Quality

---

## AMENDMENTS (all prior amendments remain in effect)

### Firestore Index Management - NEW (v9.44+)

When adding orderBy on new fields (especially nested fields like t_enrichment.google_places.rating), Firestore requires composite indexes. The agent MUST:
1. Attempt the query
2. If Error 400 with index creation URL, capture the URL
3. Log as a gotcha with the URL
4. Kyle creates the index via Firebase console (1 expected intervention)
5. Re-test after index creation confirms

Do NOT mark a workstream as "complete" if it depends on an index that hasn't been created yet.

### Gemini Flash Model String - UPDATED (v9.44)

The litellm model string for Gemini Flash has caused issues across iterations:
- v9.41: gemini/gemini-2.0-flash -> 404 (deprecated)
- v9.41 fix: gemini/gemini-2.5-flash with thinking disabled
- v9.43: litellm.AuthenticationError 400

The root cause may be litellm version drift, API key scope, or model string format changes. The fix approach:
1. Verify GEMINI_API_KEY is valid: `curl -s "https://generativelanguage.googleapis.com/v1beta/models?key=$GEMINI_API_KEY" | head -5`
2. Test litellm directly: `python3 -c "import litellm; print(litellm.completion(model='gemini/gemini-2.5-flash', messages=[{'role':'user','content':'hello'}], thinking={'type':'disabled'}).choices[0].message.content)"`
3. If model string fails, try alternatives: `gemini/gemini-2.5-flash-preview-04-17`, `gemini/gemini-2.0-flash-001`
4. Once working string confirmed, update intent_router.py and any other litellm callers
5. Add working model string to ollama_config.py as GEMINI_MODEL constant so it's centralized
6. Add to gotcha archive with resolution

### Doc Archival Enforcement - REINFORCED (v9.44)

v9.42 deleted v9.41 docs. v9.43 deleted v9.42 docs. This is the THIRD time it's happened despite explicit instructions. The design doc, plan, CLAUDE.md, GEMINI.md, and launch prompt ALL say "archive, never delete." This iteration:
1. Recover any missing docs from git history
2. Add a pre-flight check to the plan: `ls docs/archive/ | wc -l` must be >= prior count
3. Add explicit instruction to CLAUDE.md: "If you see yourself running `rm` or `git rm` on any docs/kjtcom-*.md file, STOP. Move it to docs/archive/ instead."

### Changelog Quality - NEW (v9.44+)

The changelog entries from generate_artifacts.py have been stubs ("TBD - summarize after review"). The changelog template must require:
- One line per significant change (NEW, UPDATED, FIXED prefix)
- Specific numbers (entity counts, chunk counts, test results)
- List of agents and LLMs used
- Intervention count
- NOT "TBD" anywhere

---

## WORKSTREAMS

| # | Workstream | Priority | Description |
|---|-----------|----------|-------------|
| W1 | Fix Gemini Flash auth error | P1 | Diagnose and fix litellm.AuthenticationError from v9.43 W2/W3. Centralize model string. |
| W2 | Create Firestore composite index | P1 | Create index for orderBy on t_enrichment.google_places.rating. Re-test rating queries. |
| W3 | Re-run bot session memory + rating queries | P1 | The v9.43 code was written but couldn't execute due to W1/W2 blockers. Verify it works now. |
| W4 | Post-flight verification pass | P1 | Run post_flight.py. All checks must pass. This was deferred in v9.43. |
| W5 | Doc recovery + archival enforcement | P2 | Recover any deleted docs from git. Add rm guard to CLAUDE.md. Verify archive integrity. |
| W6 | Changelog and report quality fix | P2 | Update templates to eliminate TBD stubs. Fix Qwen workstream naming (must match design doc W# labels). |

---

## W1: Fix Gemini Flash Auth Error (P1)

### Diagnosis Steps

```fish
# 1. Verify API key is valid
curl -s "https://generativelanguage.googleapis.com/v1beta/models?key=$GEMINI_API_KEY" | python3 -m json.tool | head -10

# 2. Test litellm directly
python3 -c "
import litellm
import os
os.environ['GEMINI_API_KEY'] = os.environ.get('GEMINI_API_KEY', '')
r = litellm.completion(
    model='gemini/gemini-2.5-flash',
    messages=[{'role':'user','content':'respond with just the word hello'}],
    thinking={'type':'disabled'}
)
print(r.choices[0].message.content)
"

# 3. If that fails, check litellm version
pip show litellm | grep Version

# 4. Try alternative model strings
python3 -c "
import litellm
for model in ['gemini/gemini-2.5-flash', 'gemini/gemini-2.0-flash-001', 'gemini/gemini-1.5-flash']:
    try:
        r = litellm.completion(model=model, messages=[{'role':'user','content':'hello'}])
        print(f'SUCCESS: {model}')
        break
    except Exception as e:
        print(f'FAIL: {model} - {e}')
"
```

### Fix

Once working model string is confirmed:
1. Add to scripts/utils/ollama_config.py: `GEMINI_MODEL = "gemini/gemini-2.5-flash"` (or whatever works)
2. Update scripts/intent_router.py to use GEMINI_MODEL
3. Update scripts/telegram_bot.py synthesis calls to use GEMINI_MODEL
4. Add G57 to gotcha archive: "Gemini Flash model string instability - centralize in ollama_config.py"

---

## W2: Firestore Composite Index (P1)

The v9.43 error was:
```
400 The query requires an index. You can create it here: https://console.firebase...
```

### Steps

1. Capture the full index creation URL from the error log or reproduce it:

```fish
python3 -c "
from scripts.firestore_query import execute_query
print(execute_query({'t_log_type': 'tripledb'}, 'list', sort_field='t_enrichment.google_places.rating', limit=3))
"
```

2. The error message will include a Firebase console URL. Kyle clicks it to create the index (1 expected intervention).
3. Wait for index to build (usually 2-5 minutes for small collections).
4. Re-test the query.

### Alternative: Skip orderBy, Sort in Python

If the composite index is too complex (multiple filter + sort combinations), sort in Python instead:

```python
# In firestore_query.py
docs = [doc.to_dict() for doc in query.stream()]
if sort_field:
    # Get nested field value safely
    def get_nested(d, path):
        for key in path.split('.'):
            d = d.get(key, {}) if isinstance(d, dict) else None
            if d is None:
                return 0
        return d if isinstance(d, (int, float)) else 0

    docs.sort(key=lambda d: get_nested(d, sort_field), reverse=(sort_order == 'desc'))

if limit:
    docs = docs[:limit]
```

This avoids needing composite indexes entirely. Trade-off: fetches all matching docs then sorts client-side. For 26 restaurants in LA, this is fine. For 6,181 entities with no filter, it's expensive but still feasible.

Recommend: try Python-side sort first. If performance is acceptable, skip the composite index. One less intervention, one less moving part.

---

## W3: Re-run Session Memory + Rating Queries (P1)

The v9.43 code was written for both features. Once W1 (auth) and W2 (index/sort) are resolved, re-test:

```
/ask how many ddd restaurants in los angeles
  -> Expect: 26 results found (Firestore route)

/ask out of those what are the 3 highest rated
  -> Expect: session memory resolves "those", returns top 3 by rating

/ask what are the highest rated rick steves destinations in italy
  -> Expect: Firestore route with t_log_type=ricksteves, t_any_countries=["it"], sorted by rating

/ask what caused the G45 cursor bug
  -> Expect: ChromaDB route (dev history, unchanged)

/ask does guidepoint global provide professional services
  -> Expect: web route (Brave Search, unchanged)
```

---

## W4: Post-Flight Verification Pass (P1)

Run scripts/post_flight.py. All checks must pass:

1. kylejeromethompson.com returns HTTP 200
2. @kjtcom_iao_bot responds to /status
3. /ask "how many entities are in the database" returns >= 6,181
4. architecture.html loads at kylejeromethompson.com/architecture.html

If any fail, fix and re-run before ending session.

---

## W5: Doc Recovery + Archival Enforcement (P2)

### Recovery

```fish
cd ~/dev/projects/kjtcom
# Check what's in archive
ls docs/archive/ | grep -c "v9\."
# If v9.42 docs are missing (deleted in v9.43 build), recover:
git log --oneline --all | head -10
git checkout HEAD~1 -- docs/kjtcom-build-v9.42.md docs/kjtcom-design-v9.42.md docs/kjtcom-plan-v9.42.md docs/kjtcom-report-v9.42.md 2>/dev/null
mv docs/kjtcom-*-v9.42.md docs/archive/ 2>/dev/null
# Same for v9.41 if still missing
```

### Prevention

Add to CLAUDE.md a bolded rule: "NEVER run rm or git rm on any docs/kjtcom-*.md file. Use mv docs/kjtcom-*-v{X}.md docs/archive/ instead."

---

## W6: Changelog and Report Quality Fix (P2)

### Changelog Template Update

The changelog template in template/artifacts/changelog-template.md must require:
- NEW/UPDATED/FIXED prefix per line
- Specific numbers
- Agent list
- Intervention count
- If any field would be "TBD", the generator must populate it from the event log or leave a specific TODO with what data is missing

### Qwen Workstream Naming

Qwen renamed W1 from "Bot Session Memory" to "App Optimization" in v9.43. The evaluator prompt must include: "Use the EXACT workstream names from the design doc. Do not rename, reorder, or combine workstreams."

---

## TRIDENT

| Prong | Target |
|-------|--------|
| Cost | $0. <50K Claude tokens. Gemini Flash free tier. |
| Delivery | 6 workstreams. v9.43 failures resolved. Post-flight passes. |
| Performance | /ask "top 3 highest rated ddd restaurants in LA" returns real results sorted by rating. Bot remembers session context. |

---

*Design document v9.44, April 5, 2026.*
