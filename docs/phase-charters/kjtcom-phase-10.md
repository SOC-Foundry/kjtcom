# kjtcom — Phase 10 Charter

**Phase:** 10 — Harness Externalization + Retrospective
**Status:** active (graduating at 10.69.X close)
**Charter author:** iao planning chat (retroactive — Phase 10 was not formally chartered when it began)
**Charter version:** 0.1
**Charter date:** 2026-04-08

### Why This Phase Exists

The IAO methodology was developed inside kjtcom as a working POC. Phase 10 extracts the matured harness from kjtcom into a standalone iao package consumable by other projects and engineers. This phase exists to graduate the methodology from "interesting POC pattern that produces working software" to "consumable product that ships to other engineers and reduces their token spend while improving output quality." Phase 10 ends when iao is ready for first cross-machine consumption (P3) and kjtcom has transitioned from active development lab to steady-state production reference.

### Phase Objectives

1. Extract the working harness from kjtcom into a standalone Python package (`iao`)
2. Establish standalone-repo authoring conventions (README, CHANGELOG, VERSION, pyproject.toml, dedicated docs tree)
3. Harvest reusable kjtcom knowledge into iao base via formal classification taxonomy
4. Establish phase/iteration/run formal numbering for all iao-ecosystem projects
5. Establish 5-character project code system for cross-project provenance tracking
6. Deliver iao to first cross-machine consumer (P3 via zip handoff)
7. Transition kjtcom from active development lab to steady-state production reference
8. Establish iao-the-product as its own authorable project on NZXT with parallel iteration counter

### Phase Entry Criteria (where Phase 10 began)

- kjtcom v10.65 shipped with harness still embedded as `iao-middleware/`
- Evaluator working but fragile (Tier 1 Qwen synthesis sensitivity, Tier 2 Gemini Flash schema issues)
- Single monolithic `docs/evaluator-harness.md` mixing universal pillars with kjtcom-specific ADRs
- No package boundaries — harness was a subdirectory, not an importable module
- No multi-project mental model — everything assumed kjtcom was the only consumer
- No formal phase/iteration framework — iterations were sequential v10.XX numbers without phase context
- 6,785 production entities across 4 pipelines, all stable

### Phase Exit Criteria (Graduation Conditions)

- [x] iao installable as Python package (`pip install -e iao/` works on NZXT) — achieved 10.66
- [x] Standalone-repo voice authoring (README, CHANGELOG, VERSION, pyproject.toml, dedicated docs/adrs) — achieved 10.67
- [x] Phase A duplication eliminated — achieved 10.67
- [x] doctor.py unified across pre/post-flight + iao CLI — achieved 10.67
- [x] iao rename complete (no more dash/underscore inconsistency) — achieved 10.68
- [x] kjtcom knowledge classified and split into base/project harnesses — achieved 10.68
- [x] phase/iteration/run formal numbering adopted — achieved 10.68
- [x] 5-char code taxonomy applied to gotcha archive, script registry, ADR stream — achieved 10.68
- [x] iao delivered to P3 as physical artifact (zip exists) — achieved 10.68
- [ ] Evaluator hardened against `phase.iteration.run` filename layout + Qwen/Gemini Flash failure modes — 10.69 W1
- [ ] Postflight plugin loader refactor to separate iao base checks from project-specific checks — 10.69 W2
- [ ] Build log auto-append hook eliminating retroactive-fill failure mode — 10.69 W3
- [ ] Phase 10 charter retroactively documented and committed to design history — 10.69 W4
- [ ] kjtcom transitioned to steady-state development cadence with documented maintenance mode — 10.69 W5
- [ ] iao authoring environment established on NZXT separate from kjtcom — 10.69 W6
- [ ] Closing Qwen evaluator runs cleanly (real scores, not self-eval fallback) — 10.69 W7

### Phase Charter Revision History

| Version | Date | Iteration | Change |
|---|---|---|---|
| 0.1 | 2026-04-08 | 10.69.0 | Retroactive charter for Phase 10 (W4 commits this to history) |
