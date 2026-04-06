# kjtcom - Design Document v9.47

**Phase:** 9 - App Optimization (FINAL)
**Iteration:** 47
**Date:** April 5, 2026
**Executing Agent:** Gemini CLI
**Focus:** Qwen Harness Refinement + Claw3D Deploy + Pipeline Phase Review for Bourdain Prep

---

## AMENDMENTS (all prior amendments remain in effect)

### Gemini-Led Iterations - NEW (v9.47)

Gemini CLI is the primary executor for this iteration. Claude Code has run 6 consecutive iterations (v9.41-v9.46). Fresh agent provides fresh perspective and validates that the harness files are comprehensive enough for any agent to execute from.

This is also a validation test of the IAO methodology: if GEMINI.md is written well enough, Gemini should execute without context loss. If Gemini struggles, the harness needs more detail.

### Workstream Fidelity Rule - NEW (v9.47+)

Qwen MUST use the EXACT workstream list from the design doc. No adding workstreams (v9.46 hallucinated W5 "Architecture documentation" and W6 "Utilities" which were not in the design doc). No renaming. No reordering. If the design doc has 4 workstreams, the scorecard has 4 rows. Period.

### Claw3D Deployment - OVERDUE (v9.38)

The Claw3D Three.js prototype has been sitting undeployed since v9.38 (9 iterations ago). It is a standalone HTML file at docs/claw3d-prototype/index.html. Deploy to app/web/claw3d.html for access at kylejeromethompson.com/claw3d.html. Add link to README.

---

## WORKSTREAMS

| # | Workstream | Priority | Description |
|---|-----------|----------|-------------|
| W1 | Qwen harness refinement + validation | P1 | Fix workstream fidelity (no hallucinated W#s). Re-run v9.46 evaluation with refined harness. Validate scores are honest and workstreams match design doc exactly. |
| W2 | Pipeline phase review for Bourdain | P1 | Review all 7 pipeline phases (acquire -> load) and document improvements needed for a 114-video Bourdain dry run. What middleware enhancements would make each phase more reliable? |
| W3 | Deploy Claw3D to Firebase | P2 | Copy docs/claw3d-prototype/index.html to app/web/claw3d.html. Deploy. Link from README. Verify at kylejeromethompson.com/claw3d.html. |
| W4 | Post-flight + Phase 9 close-out | P2 | Post-flight pass. Final Phase 9 changelog entry. Archive v9.46 docs. Verify all living docs current. |

---

## W1: Qwen Harness Refinement (P1)

### Problems from v9.46

1. **Qwen hallucinated workstreams.** Design doc had W1-W4. Qwen report had W1-W6, inventing "Architecture documentation" (W5) and "Utilities" (W6). These were not in the design doc.
2. **Qwen claimed W1 (evaluator harness) was "deferred" with 0/10.** But the changelog shows evaluator-harness.md WAS created, run_evaluator.py WAS updated, and generate_artifacts.py WAS updated. Qwen contradicted the actual build evidence.
3. **W2 scored 8/10 but Qwen said it was "1 append entry rather than the requested full review."** The changelog shows 70 lines changed in README.md with Telegram Bot section, Middleware section, and Phase 10 Roadmap added. Qwen undersold the work.

### Harness Additions

Add to docs/evaluator-harness.md:

```markdown
## Workstream Fidelity (ABSOLUTE RULE)

You MUST evaluate ONLY the workstreams listed in the design document. Do not add, rename, reorder, or combine workstreams. If the design doc lists W1 through W4, your scorecard has exactly 4 rows. If you see work that doesn't fit a workstream, note it in a "Additional Work" section below the scorecard, but do NOT create phantom workstreams.

Count the workstreams in the design doc. Your scorecard row count MUST match.

## Evidence Cross-Check

Before scoring, read the changelog entry for this iteration. If the changelog says a file was created but your analysis says it wasn't, re-check. Qwen's file system queries can miss files that were created earlier in the session. Default to the changelog and git diff over your own file existence checks when they conflict.
```

### Validation

Re-evaluate v9.46 with refined harness:

```fish
python3 -u scripts/run_evaluator.py --iteration v9.46 --workstreams --retroactive
```

Check:
- Exactly 4 workstreams in scorecard (matching design doc W1-W4)
- W1 (evaluator harness) should NOT be 0/10 - the file exists and scripts were updated
- No banned phrases
- "What Could Be Better" section with >= 3 items

---

## W2: Pipeline Phase Review for Bourdain (P1)

Review each of the 7 pipeline phases and document:
1. Current script name and location
2. What it does
3. Known issues / gotchas from CalGold, RickSteves, and TripleDB runs
4. What middleware could improve reliability for a 114-video batch
5. Estimated runtime for 114 videos
6. Recommended enhancements before Phase 10

### Phase-by-Phase Review

**Phase 1: Acquire (yt-dlp)**
- Script: scripts/phase1_acquire.py
- Gotchas: unavailable videos, age-restricted content, playlist ordering
- For 114 videos: ~30 min download time
- Enhancement: checkpoint resumption, skip already-downloaded

**Phase 2: Transcribe (faster-whisper, CUDA)**
- Script: scripts/phase2_transcribe.py
- Gotchas: G2 (CUDA LD_LIBRARY_PATH), G21 (CUDA OOM), timeout scaling
- For 114 videos: ~4-6 hours (CUDA dependent), must run on NZXTcos (NVIDIA GPU)
- Enhancement: tmux graduated timeouts (clips 120s, episodes 600s, marathons 1200s)

**Phase 3: Extract (Gemini Flash API)**
- Script: scripts/phase3_extract.py
- Gotchas: prompt engineering per pipeline, rate limits
- For 114 videos: ~2-3 hours (API rate limited)
- Enhancement: pipeline-specific extraction prompt template in template/

**Phase 4: Normalize (Thompson Schema)**
- Script: scripts/phase4_normalize.py
- Gotchas: schema drift between pipelines, field validation
- For 114 videos: ~10 min (CPU only)
- Enhancement: schema validation against schema_reference.json

**Phase 5: Geocode (Nominatim)**
- Script: scripts/phase5_geocode.py
- Gotchas: 1 req/sec rate limit, niche locations miss
- For 114 videos: ~30-60 min depending on entity count
- Enhancement: Google Places coordinate backfill (already exists)

**Phase 6: Enrich (Google Places API)**
- Script: scripts/phase6_enrich.py
- Gotchas: API cost (free credits), Places API field selection
- For 114 videos: ~20-30 min
- Enhancement: cache enrichment results to avoid re-querying

**Phase 7: Load (Firebase Admin SDK)**
- Script: scripts/phase7_load.py
- Gotchas: G33 (duplicate entity IDs), G35 (production write safety)
- For 114 videos: ~5 min (batch writes)
- Enhancement: dry-run mode, dedup validation, t_any_counties enrichment post-load

### Output

Produce: docs/pipeline-review-v9.47.md with the full review, estimated Bourdain timeline, and recommended middleware enhancements. This becomes the input for Phase 10 planning.

---

## W3: Deploy Claw3D (P2)

```fish
cd ~/dev/projects/kjtcom
cp docs/claw3d-prototype/index.html app/web/claw3d.html
```

Verify locally:
```fish
cd app
flutter build web
# Check app/build/web/claw3d.html exists
```

Deploy:
```fish
cd ~/dev/projects/kjtcom
firebase deploy --only hosting
```

Verify: https://kylejeromethompson.com/claw3d.html loads with the Three.js IAO visualization.

Add to README.md Architecture section:
```markdown
**[3D IAO Visualization](https://kylejeromethompson.com/claw3d.html)** |
```

---

## W4: Post-Flight + Phase 9 Close-Out (P2)

1. Run post_flight.py - all checks pass
2. Verify claw3d.html loads
3. Archive v9.46 docs to docs/archive/
4. Verify all living docs current:
   - architecture.mmd reflects v9.47 state
   - install.fish complete
   - middleware_registry.json includes evaluator-harness.md
   - gotcha_archive.json complete
   - README.md reflects v9.47
5. Final Phase 9 changelog entry
6. Phase 9 close-out statement in build log

---

## TRIDENT

| Prong | Target |
|-------|--------|
| Cost | $0. <50K Gemini tokens. |
| Delivery | 4 workstreams. Qwen harness refined. Pipeline review complete. Claw3D live. |
| Performance | Qwen re-evaluation of v9.46 produces exactly 4 workstream rows matching design doc. No hallucinated workstreams. |

---

*Design document v9.47, April 5, 2026.*
