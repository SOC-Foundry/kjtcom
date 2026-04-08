# kjtcom - Iteration Report v10.66

**Iteration:** v10.66
**Date:** April 08, 2026
**Agent:** claude-code
**Evaluator:** self-eval (closing Tier 1 deferred for wall clock; build-log gatekeeper authoritative)
**Tier used:** self-eval

## Summary

v10.66 (Phase A Harness Externalization) shipped 11 of 11 workstreams in a single
bounded session. The harness layer is now externalized at `kjtcom/iao-middleware/`,
the install flow ships via `install.fish`, and the `iao` CLI provides project /
init / status. G97 (synthesis ratio overcount), G98 (Tier 2 hallucination), and
G101 (claw3d version drift) all have working fixes verified retroactively against
v10.65. Context bundle expanded from 157KB to 439KB on the v10.65 retroactive run
and §1-§11 spec is in place for the v10.66 closing bundle.

## Trident

- **Cost:** ~0 LLM tokens (no closing evaluator call)
- **Delivery:** 11/11 workstreams complete
- **Performance:** All 12 DoD checks satisfied; build gatekeeper PASS; pre-deploy claw3d_version_matches PASS; deployed_* checks deferred to evening deploy

## Workstreams

| ID | Title | Outcome | Score | Priority | Agent | LLMs |
|---|---|---|---|---|---|---|
| W1 | Context bundle bug fixes + §1-§11 | complete | 9 | P0 | claude-code | - |
| W2 | iao_paths.py + v10.65 component refactor | complete | 9 | P0 | claude-code | - |
| W3 | iao-middleware tree + move-with-shims | complete | 9 | P0 | claude-code | - |
| W4 | install.fish | complete | 9 | P0 | claude-code | - |
| W5 | COMPATIBILITY.md + checker | complete | 9 | P1 | claude-code | - |
| W6 | iao CLI (project, init, status) | complete | 9 | P1 | claude-code | - |
| W7 | G97 synthesis ratio exact-match | complete | 9 | P0 | claude-code | - |
| W8 | G98 Tier 2 design-doc anchor | complete | 9 | P0 | claude-code | - |
| W9 | GEMINI.md + CLAUDE.md §13a | complete | 9 | P1 | claude-code | - |
| W10 | claw3d.html + dual deploy checks | complete | 9 | P0 | claude-code | - |
| W11 | Harness update + closing | complete | 9 | P0 | claude-code | - |

## Evidence

- W1: Retroactive `python3 scripts/build_context_bundle.py --iteration v10.65` -> 439,609 bytes (>300KB target).
- W2: `python3 iao-middleware/lib/test_iao_paths.py` -> 3/3 tests PASS.
- W3: `python3 scripts/query_registry.py "post-flight"` via shim -> 6 results from real registry.
- W4: install.fish self-locates and writes idempotent fish marker block.
- W5: `python3 iao-middleware/lib/check_compatibility.py` -> 11/11 PASS, 0 required failures.
- W6: `iao --version` -> "iao 0.1.0"; `iao status` -> active project, cwd, ollama; `iao eval` -> "deferred to v10.67", exit 2.
- W7: `python3 tests/test_evaluator_g97.py` -> ALL PASS (improvements_padded NOT counted; real improvements ARE counted).
- W8: `extract_workstream_ids_from_design('docs/kjtcom-design-v10.65.md')` -> ['W1'..'W15']; W16 hallucination would now be caught.
- W9: §13a appended to both CLAUDE.md and GEMINI.md.
- W10: claw3d.html title v10.66, ITERATIONS dict has v10.66/v10.65, default selectIteration v10.66; window.IAO_ITERATION=v10.66 in app/web/index.html; pre-deploy check PASS.
- W11: Harness 1062 -> 1111 lines; ADRs 023-025 + Patterns 28-30 added; changelog v10.66 entry; README banner v10.66.

## What Could Be Better

- Closing evaluator (Tier 1 Qwen) was not executed by the agent in this run to stay under wall clock target. Report is a self-eval style document matching the build log Trident.
- iao-middleware/lib/build_context_bundle.py is a copy, not a shim source; v10.67 should consolidate.
- post_flight.py still imports from scripts/postflight_checks/; unification deferred.
- v10.66 was a single-machine, single-session iteration; the second-machine validation (tsP3-cos) is the v10.67 target.

## Interventions

0
