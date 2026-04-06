# kjtcom - Execution Plan v9.47

**Executing Agent:** Gemini CLI
**Estimated Duration:** 2.5 hours
**Token Target:** <50K

---

## PRE-FLIGHT

- [ ] GEMINI.md saved to ~/dev/projects/kjtcom/ (v9.47 - PRIMARY HARNESS)
- [ ] CLAUDE.md saved to ~/dev/projects/kjtcom/ (v9.47)
- [ ] docs/kjtcom-design-v9.47.md saved
- [ ] docs/kjtcom-plan-v9.47.md saved
- [ ] v9.46 docs archived: mv docs/kjtcom-*-v9.46.md docs/archive/
- [ ] Archive integrity: ls docs/archive/ | wc -l (>= 179)
- [ ] Ollama running, 4 models
- [ ] sudo systemctl restart kjtcom-telegram-bot
- [ ] set -gx IAO_ITERATION v9.47

---

## STEP 1: Refine Qwen Harness (W1) - 30 min

1. Read current docs/evaluator-harness.md
2. Add workstream fidelity rule (from design doc W1)
3. Add evidence cross-check rule (from design doc W1)
4. Test with retroactive v9.46 re-evaluation:

```fish
python3 -u scripts/run_evaluator.py --iteration v9.46 --workstreams --retroactive
```

5. Verify output:
   - Exactly 4 workstreams (W1-W4 from v9.46 design doc)
   - No hallucinated W5/W6
   - W1 (evaluator harness) NOT 0/10 (file was created)
   - "What Could Be Better" section exists
   - No banned phrases

If validation fails, refine harness text and re-run.

---

## STEP 2: Pipeline Phase Review (W2) - 45 min

1. Read each pipeline script:

```fish
cd ~/dev/projects/kjtcom
for script in scripts/phase1_acquire.py scripts/phase2_transcribe.py scripts/phase3_extract.py scripts/phase4_normalize.py scripts/phase5_geocode.py scripts/phase6_enrich.py scripts/phase7_load.py
    echo "=== $script ==="
    head -30 $script
    echo ""
end
```

2. Review gotcha archive for pipeline-related gotchas:

```fish
python3 -c "
import json
g = json.load(open('data/gotcha_archive.json'))
for gotcha in g.get('resolved_gotchas', []):
    if gotcha.get('root_cause') in ['pipeline', 'environment']:
        print(f\"{gotcha['id']}: {gotcha['description']} -> {gotcha['resolution']}\")
"
```

3. Review CalGold, RickSteves, TripleDB iteration histories for pipeline lessons
4. Estimate Bourdain runtime (114 videos through 7 phases)
5. Document middleware enhancements that would improve each phase

6. Produce: docs/pipeline-review-v9.47.md

---

## STEP 3: Deploy Claw3D (W3) - 10 min

```fish
cd ~/dev/projects/kjtcom
cp docs/claw3d-prototype/index.html app/web/claw3d.html
cd app
flutter build web
cd ~/dev/projects/kjtcom
firebase deploy --only hosting
```

Verify: curl -s -o /dev/null -w "%{http_code}" https://kylejeromethompson.com/claw3d.html -> 200

Add link to README.md in Architecture section.

---

## STEP 4: Post-Flight + Phase 9 Close-Out (W4) - 20 min

1. Post-flight:

```fish
python3 scripts/post_flight.py
```

2. Verify claw3d.html loads
3. Update living docs:
   - architecture.mmd if needed
   - middleware_registry.json (harness refinement)
   - README.md (claw3d link, v9.47 version)
4. Re-embed archive:

```fish
python3 -u scripts/embed_archive.py
```

5. Rebuild architecture HTML:

```fish
python3 scripts/build_architecture_html.py
```

6. Deploy:

```fish
cd ~/dev/projects/kjtcom/app
flutter analyze
flutter test
flutter build web
cd ~/dev/projects/kjtcom
firebase deploy --only hosting
```

7. Phase 9 close-out statement in build log.

---

## STEP 5: Workstream Evaluation + Artifacts - 15 min

```fish
python3 -u scripts/run_evaluator.py --iteration v9.47 --workstreams
python3 -u scripts/generate_artifacts.py
python3 -u scripts/generate_artifacts.py --validate-only
python3 -u scripts/generate_artifacts.py --promote
```

Verify: exactly 4 workstream rows. No hallucinated extras. "What Could Be Better" exists.

Artifacts:
- [ ] docs/kjtcom-design-v9.47.md (pre-staged)
- [ ] docs/kjtcom-plan-v9.47.md (pre-staged)
- [ ] docs/kjtcom-build-v9.47.md (with Phase 9 close-out)
- [ ] docs/kjtcom-report-v9.47.md (first refined-harness report)
- [ ] docs/pipeline-review-v9.47.md (NEW - Bourdain prep)
- [ ] docs/evaluator-harness.md (MODIFIED - fidelity + cross-check rules)
- [ ] docs/kjtcom-changelog.md (append)
- [ ] app/web/claw3d.html (NEW - deployed)
- [ ] agent_scores.json (append)
- [ ] README.md (MODIFIED - claw3d link)
- [ ] data/middleware_registry.json (MODIFIED)
- [ ] GEMINI.md (v9.47)
- [ ] CLAUDE.md (v9.47)

---

## INTERVENTIONS

Target: 0.

---

*Plan v9.47, April 5, 2026.*
