# kjtcom - Design Document v9.46

**Phase:** 9 - App Optimization
**Iteration:** 46
**Date:** April 5, 2026
**Focus:** Qwen Evaluator Harness + README Overhaul + Phase 9 Final Polish

---

## AMENDMENTS (all prior amendments remain in effect)

### Qwen Evaluator Harness - NEW (v9.46+)

Qwen3.5-9B gets a dedicated harness file: docs/evaluator-harness.md. This file is loaded by run_evaluator.py and generate_artifacts.py every time Qwen is invoked for evaluation or artifact drafting. The harness enforces skeptical, fact-based assessment.

Core principles:
1. **Glass half empty.** Every iteration has room for improvement. Even a perfect execution had risk, took too long, or missed an optimization opportunity. If you can't find a flaw, you aren't looking hard enough.
2. **Never score 10/10.** 10/10 means perfect - nothing in software is perfect. Max realistic score is 9/10 for exceptional work. 7-8/10 is a strong delivery. 5-6/10 is acceptable with issues. Below 5 is a failure.
3. **Evidence or it didn't happen.** Every score must cite a specific file, command output, test result, or error message. "Complete" without a file path is "unverified."
4. **Name two improvements** for every workstream, even successful ones. What could have been done better, faster, or more robustly?
5. **No corporate language.** Ban: "successfully deployed", "robust validation", "clean release", "strategic shift", "healthy system." Use: "deployed with 0 errors", "15/15 tests passed", "3 files created."
6. **Contradict when warranted.** If the build log says "complete" but the evidence shows a timeout, Qwen must flag the discrepancy. The evaluator's job is truth, not agreement.
7. **Trident values are computed, not described.** Cost: actual token count. Delivery: X/Y workstreams. Performance: measured metric with number.
8. **Flag what was NOT tested.** Every iteration has untested paths. Name them.

### README Refresh Cadence - NEW (v9.46+)

- **Every iteration:** append to changelog section, update version/phase number
- **Every 3 iterations:** full README review and overhaul (content accuracy, section relevance, stale descriptions, badge versions, link verification). Next overhaul: v9.46, then v9.49 (Phase 10), etc.
- The README is the public face of the project. It must accurately reflect current state, not trail 5 iterations behind.

---

## WORKSTREAMS

| # | Workstream | Priority | Description |
|---|-----------|----------|-------------|
| W1 | Qwen evaluator harness | P1 | Create docs/evaluator-harness.md. Update run_evaluator.py and generate_artifacts.py to load it. Test with retroactive v9.45 evaluation. |
| W2 | README overhaul | P1 | Full review of all sections. Update stale content, fix incorrect numbers, verify links, refresh changelog. |
| W3 | Phase 9 final audit | P2 | Compare v9.27 (first Phase 9) to v9.46 (last). Document what Phase 9 achieved. Identify any remaining gaps before Phase 10. |
| W4 | Post-flight + middleware registry update | P2 | Post-flight pass. Update middleware_registry.json with evaluator harness and any new components. |

---

## W1: Qwen Evaluator Harness (P1)

### docs/evaluator-harness.md

This is the instruction file Qwen reads before every evaluation. It is NOT a template - it is a personality and methodology directive.

```markdown
# Qwen Evaluator Harness

You are the permanent evaluator for the kjtcom IAO project. Your job is honest, skeptical assessment. You are not a cheerleader. You are an auditor.

## Scoring Rules

- NEVER give 10/10. Maximum is 9/10 for exceptional work with minor nitpicks.
- 7-8/10 is a strong, solid delivery.
- 5-6/10 is acceptable but has meaningful gaps.
- Below 5/10 is a failure that needs rework.
- 0/10 means the workstream was not attempted or fully failed.

## For Every Workstream, You Must:

1. State the outcome: complete / partial / failed / deferred
2. Cite specific evidence (file path, command output, test result, error message)
3. Name at least 2 things that could have been done better, even if the workstream succeeded
4. Flag anything that was claimed but not verified
5. Flag anything that was not tested

## Banned Phrases

- "successfully deployed" -> use "deployed with X errors"
- "robust validation" -> use "N tests passed, M failed"
- "clean release" -> use "0 errors in event log"
- "strategic shift" -> describe what actually happened
- "healthy system" -> cite specific metrics
- "Review..." -> compute the actual value
- "TBD" -> find the data or write "MISSING: [what]"

## Trident Rules

- Cost: state actual token count from event log. If missing, count LLM call events.
- Delivery: "X/Y workstreams complete" - count from scorecard, not a description.
- Performance: state the specific measured result with a number.

## Report Summary Rules

- First sentence: what was the iteration's primary objective and did it succeed?
- Second sentence: what specific deliverables were produced (with counts)?
- Third sentence: what failed or was deferred and why?
- Fourth sentence: what's the honest overall assessment?
- Do NOT write more than 6 sentences in the summary.

## Changelog Rules

- Every line starts with NEW:, UPDATED:, or FIXED:
- Include specific numbers
- List agents, LLMs, MCPs used
- Include intervention count
- NEVER write "TBD"

## Improvement Mandate

Even if every workstream scores 8+, your report must include a section called "What Could Be Better" with at least 3 concrete suggestions. These feed into next iteration planning.
```

### Integration

Update scripts/run_evaluator.py:
- Load docs/evaluator-harness.md as system prompt prefix before the workstream evaluation prompt
- The harness is the personality; the workstream data is the input

Update scripts/generate_artifacts.py:
- Load evaluator-harness.md when generating report and changelog drafts
- Apply the same skeptical lens to artifact generation

### Validation

Re-evaluate v9.45 using the new harness. Compare the old v9.45 report (which gave W5 9/10 and W6 10/10) with the new harness output. The new evaluation should:
- Score W5 no higher than 8/10 (readiness checklist was useful but didn't resolve the blocker)
- Score W6 no higher than 8/10 (Trident fix was needed but should have been done 3 iterations ago)
- Name improvements for both
- Not give any workstream 10/10

---

## W2: README Overhaul (P1)

### Review Checklist

1. **Header section:** badges current? Phase number correct? Version correct?
2. **Live App section:** all features listed accurately? Any new features missing (session memory, rating sort, web route)?
3. **Architecture section:** architecture.html link works? Description matches current state (3-route retrieval, systemd bot, session memory)?
4. **Data Architecture section:** entity count correct (6,181)? Schema version correct?
5. **Thompson Indicator Fields table:** all 22 fields listed? Types correct? Examples current?
6. **Methodology section (if exists):** 10 pillars accurate? Trident described?
7. **Telegram Bot section (should exist):** @kjtcom_iao_bot link, command list, how to access
8. **Changelog section:** all iterations through v9.45 present? v9.46 entry added?
9. **Author section:** current role, TachTech link works?
10. **Citing section:** still accurate?

### New Sections Needed

- **Telegram Bot** section: link to @kjtcom_iao_bot, supported commands (/ask, /status, /help, /search), example queries, note about session memory and rating sort
- **Middleware** section: brief description of the middleware layer as portable IAO infrastructure, link to middleware_registry.json
- **Phase 10 Roadmap** section: brief note on what's coming (Bourdain pipeline, IaC packaging)

### Sections to Update

- Architecture description needs: dual retrieval, 3-route intent router, systemd bot, session memory, rating-aware queries, artifact automation, gotcha archive
- Gotcha tab reference should say G1-G57 (not G1-G44)
- Changelog should include v9.41 through v9.46

---

## W3: Phase 9 Final Audit (P2)

Document what Phase 9 (v9.27 through v9.46) accomplished. This goes in the build log and feeds the Phase 10 retrospective.

### Phase 9 Summary (v9.27-v9.46, 20 iterations)

Key deliverables to catalog:
- Flutter app polish: 6 tabs, pagination, detail panel, gothic visual identity
- Query system: NoSQL parser, syntax highlighting, autocomplete, operators
- Multi-agent orchestration: 4 local LLMs, 5 MCP servers, agent evaluator
- Middleware layer: RAG, intent router, Firestore query, event logging, artifact automation
- Telegram bot: dual retrieval, session memory, rating sort, web route, systemd
- County enrichment: TripleDB 918/1100 entities enriched
- Documentation: architecture HTML, gotcha archive, middleware registry, install.fish
- Dependency upgrade: Riverpod 2->3, firebase_core 3->4, cloud_firestore 5->6, google_fonts 6->8, flutter_map 7->8

### Remaining Phase 9 Gaps

- 10 transitive deps outdated (not actionable, upstream blocked)
- Bot conversational memory is in-memory only (lost on restart)
- Qwen report quality still improving (harness will help)
- README was stale (fixed in W2)

---

## W4: Post-Flight + Middleware Registry (P2)

- Run post_flight.py
- Update data/middleware_registry.json: add evaluator-harness.md
- Re-embed archive if new docs added
- Rebuild architecture HTML if mmd changed

---

## TRIDENT

| Prong | Target |
|-------|--------|
| Cost | $0. <50K Claude tokens. |
| Delivery | 4 workstreams. Evaluator harness operational. README current. Phase 9 audited. |
| Performance | Qwen re-evaluation of v9.45 produces meaningfully different (lower, more honest) scores than original. |

---

*Design document v9.46, April 5, 2026.*
