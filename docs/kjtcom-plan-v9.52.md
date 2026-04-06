# kjtcom - Execution Plan v9.52

**Recommended Agent:** Claude Code
**Estimated Duration:** 3-4 hours (unhurried - harness rebuild is the priority)
**Token Target:** <50K

---

## PRE-FLIGHT

- [ ] CLAUDE.md/GEMINI.md saved (v9.52, >= 200 lines)
- [ ] Design + plan in docs/
- [ ] v9.51 docs to archive: mv docs/kjtcom-*-v9.51.md docs/archive/
- [ ] Clean: rm -f docs/drafts/*.md docs/changelog-v*.md
- [ ] Ollama running, 4 models (ollama list)
- [ ] sudo systemctl restart kjtcom-telegram-bot
- [ ] set -gx IAO_ITERATION v9.52
- [ ] jsonschema installed

---

## STEP 1: Rebuild Evaluator Harness (W1) - 90 min (take your time)

This is the most important deliverable. Build docs/evaluator-harness.md to 400+ lines.

1. Read the current 84-line harness
2. Read the design doc W1 target structure (15 sections)
3. Read the v9.41 through v9.51 reports and build logs (from docs/archive/) to extract failure patterns
4. Build each section:

   a. **Identity and Role** (10-15 lines): who Qwen is, auditor personality
   b. **Output Schema** (20-30 lines): eval_schema.json reference with field explanations
   c. **ADR** (60-80 lines): 5 architectural decisions with context/decision/rationale/consequences
   d. **Scoring Rules with Calibration** (30-40 lines): score meanings + real examples
   e. **Failure Pattern Catalog** (80-100 lines): 11 documented failure patterns from v9.41-v9.51
   f. **Evidence Quality Standards** (20-30 lines): good/bad examples
   g. **MCP Usage Guide** (20-25 lines): when each MCP is actually invoked
   h. **Agent Attribution Guide** (15-20 lines): executor vs evaluator
   i. **Trident Computation** (20-25 lines): rules + worked example
   j. **Report Template** (20-25 lines): complete markdown structure
   k. **Build Log Template** (20-25 lines): complete markdown structure
   l. **Changelog Template** (10-15 lines): format rules
   m. **Banned Phrases** (15-20 lines): comprehensive list
   n. **What Could Be Better** (10 lines): mandate
   o. **Workstream Fidelity** (10-15 lines): absolute rule + examples
   p. **Living Document Notice** (5-10 lines): growth mandate

5. Verify: `wc -l docs/evaluator-harness.md` >= 400
6. Test with retroactive evaluation:

```fish
python3 -u scripts/run_evaluator.py --iteration v9.51 --workstreams --retroactive
```

---

## STEP 2: Claw3D Solar System Redesign (W2) - 60 min

1. Read current app/web/claw3d.html (v9.50, ~300 lines)
2. Create data/claw3d_iterations.json with active node lists for v9.41-v9.52
3. Rebuild claw3d.html:
   - Qwen = sun (center, emissive purple/magenta glow)
   - Inner ring: rocky planets (Claude=green, Gemini=blue, Nemotron=orange, GLM=amber)
   - Asteroid belt: 5 MCPs (pink cubes) + nomic-embed (teal cube)
   - Outer ring: gas giants
     - Jupiter (cyan) = Middleware with 10 component moons
     - Saturn (green with rings) = Frontend with 8 component moons
     - Uranus (orange) = Pipeline with 7 phase moons (yt-dlp as input moon)
     - Neptune (yellow) = Backend/Data with 6 component moons
   - Iteration dropdown at top
   - Active nodes: full color, opacity 1.0
   - Inactive nodes: wireframe outline, opacity 0.3
   - Animation: planets orbit sun, moons orbit planets
   - Legend: updated with solar system metaphor

4. Verify locally:

```fish
cd ~/dev/projects/kjtcom/app
flutter build web
# Open build/web/claw3d.html in browser
# Test iteration dropdown
# Verify all nodes visible at v9.52 (all active)
# Switch to v9.41 - verify only early components are active
```

---

## STEP 3: Phase 10 Systems Check (W3) - 30 min

### MCP Verification (add to post_flight.py)

Test all 5 MCPs:

```fish
# Firebase MCP - test via .mcp.json config
# Context7 MCP - test documentation lookup
# Firecrawl MCP - test config loading
# Playwright MCP - test browser availability
# Dart MCP - test code analysis
```

### LLM Verification

```fish
# All 4 Ollama models
for model in qwen3.5:9b nemotron-mini:4b "haervwe/GLM-4.6V-Flash-9B" nomic-embed-text
    echo "Testing $model..."
    ollama run $model "respond with just OK" 2>/dev/null | head -1
end

# Gemini Flash via litellm
python3 -c "
from scripts.utils.ollama_config import GEMINI_MODEL
import litellm
r = litellm.completion(model=GEMINI_MODEL, messages=[{'role':'user','content':'respond OK'}], thinking={'type':'disabled'})
print(f'Gemini Flash: OK')
"
```

### Intent Router Check (all 3 routes)

```fish
python3 -c "
from scripts.intent_router import route_question
import json
tests = [
    ('how many entities', 'firestore'),
    ('what caused G45 bug', 'chromadb'),
    ('does anthropic have free tier', 'web')
]
for q, expected in tests:
    r = route_question(q)
    route = r.get('route', 'unknown')
    status = 'PASS' if route == expected else 'FAIL'
    print(f'  {status}: \"{q}\" -> {route} (expected {expected})')
"
```

### Bot Check

```fish
sudo systemctl status kjtcom-telegram-bot --no-pager | head -5
```

### Pipeline Script Syntax Check

```fish
cd ~/dev/projects/kjtcom
for f in scripts/phase*_*.py
    python3 -c "import py_compile; py_compile.compile('$f')" 2>/dev/null
    and echo "  PASS: $f"
    or echo "  FAIL: $f"
end
```

Log all results in build log under PHASE 10 SYSTEMS CHECK section.

---

## STEP 4: Post-Flight + Living Docs (W4) - 20 min

1. Enhanced post_flight.py with MCP checks
2. Run full post-flight:

```fish
python3 scripts/post_flight.py
```

3. Verify claw3d.html renders solar system
4. Verify iteration dropdown works
5. Append changelog (single file)
6. README version v9.52
7. Update middleware_registry.json (harness version, claw3d version)
8. Re-embed archive (new 400+ line harness):

```fish
python3 -u scripts/embed_archive.py
```

9. Rebuild architecture HTML:

```fish
python3 scripts/build_architecture_html.py
```

10. Build + deploy:

```fish
cd ~/dev/projects/kjtcom/app
flutter analyze
flutter test
flutter build web
cd ~/dev/projects/kjtcom
firebase deploy --only hosting
```

---

## STEP 5: Evaluation + Artifacts (corrected order)

```fish
python3 -u scripts/run_evaluator.py --iteration v9.52 --workstreams
python3 -u scripts/generate_artifacts.py
python3 -u scripts/generate_artifacts.py --validate-only
python3 -u scripts/generate_artifacts.py --promote
```

Verify: evaluator harness >= 400 lines, scores X/10, 4 workstreams, no hallucinated extras, build log in markdown prose, MCP checks in post-flight results.

Artifacts:
- [ ] docs/kjtcom-design-v9.52.md (pre-staged)
- [ ] docs/kjtcom-plan-v9.52.md (pre-staged)
- [ ] docs/kjtcom-build-v9.52.md (with Phase 10 Systems Check section)
- [ ] docs/kjtcom-report-v9.52.md (from 400+ line harness evaluation)
- [ ] docs/kjtcom-changelog.md (APPENDED)
- [ ] docs/evaluator-harness.md (REBUILT, 400+ lines)
- [ ] app/web/claw3d.html (REBUILT, solar system)
- [ ] data/claw3d_iterations.json (NEW)
- [ ] scripts/post_flight.py (MODIFIED, MCP checks)
- [ ] data/middleware_registry.json (MODIFIED)
- [ ] README.md (v9.52)
- [ ] CLAUDE.md (v9.52, >= 200 lines)
- [ ] GEMINI.md (v9.52, >= 200 lines)

---

## INTERVENTIONS

Target: 0.

MCP checks may surface reauth issues (G53). If Firebase MCP needs reauth, log but don't block.

---

*Plan v9.52, April 5, 2026.*
