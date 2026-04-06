# kjtcom - Execution Plan v9.53

**Recommended Agent:** Claude Code
**Estimated Duration:** 2 hours
**Token Target:** <50K

---

## PRE-FLIGHT

- [ ] CLAUDE.md/GEMINI.md saved (v9.53, >= 200 lines). Evaluator harness >= 400 lines.
- [ ] Design + plan in docs/. v9.52 docs to archive. Clean drafts + orphaned changelogs.
- [ ] Ollama (4 models). Bot restart. IAO_ITERATION=v9.53.

---

## STEP 1: Claw3D Orbital Fixes (W1) - 40 min

1. Read app/web/claw3d.html
2. Apply 4 fixes from design doc:
   a. Reduce orbit speeds by 75% (multiply by 0.25)
   b. Reduce orbital radii by ~40%
   c. Add connector lines (sun-planet, planet-moon) with subtle green opacity 0.15
   d. Remove axis rotation (tidal lock - orbit but no spin)
3. Verify locally: `flutter build web` then open in browser
4. Check: all planets visible in initial viewport, orbits slow and readable, connectors visible, no spinning

---

## STEP 2: Qwen Harness Tuning (W2) - 30 min

1. Improve schema retry error messages in scripts/run_evaluator.py:
   - Include exact field path + expected vs actual in retry prompt
2. Add Claw3D iteration fallback (50% opacity for unknown iterations)
3. Review evaluator-harness.md for contradictions or gaps
4. Add any v9.52 failure patterns to the catalog
5. Test: `python3 -u scripts/run_evaluator.py --iteration v9.52 --workstreams --retroactive`

---

## STEP 3: Post-Flight + Phase 9 Close-Out (W3) - 20 min

```fish
python3 scripts/post_flight.py  # All checks including MCPs
cd ~/dev/projects/kjtcom/app && flutter analyze && flutter test && flutter build web
cd ~/dev/projects/kjtcom && firebase deploy --only hosting
```

Run close-out checklist from design doc. If all pass, add Phase 9 COMPLETE statement to build log.

---

## STEP 4: Evaluation + Artifacts

```fish
python3 -u scripts/run_evaluator.py --iteration v9.53 --workstreams
python3 -u scripts/generate_artifacts.py
python3 -u scripts/generate_artifacts.py --validate-only
python3 -u scripts/generate_artifacts.py --promote
```

Artifacts: design, plan, build, report, changelog (appended), CLAUDE.md, GEMINI.md.

---

*Plan v9.53, April 5, 2026.*
