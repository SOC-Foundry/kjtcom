# kjtcom — Retroactive Report v10.66

**Iteration:** v10.66 (retroactively evaluated in v10.67 W1)
**Date of original iteration:** 2026-04-08
**Date of retroactive eval:** 2026-04-08
**Evaluator:** Gemini Flash (Qwen synthesis fallback)
**Purpose:** Close the v10.66 self-eval gap. Validate G97/G98 on live data.

## Summary

Iteration v10.66 successfully completed all 11 planned workstreams. The retroactive evaluation by Gemini Flash (triggered after Qwen exceeded the synthesis threshold) confirms strong performance, though slightly lower than the original self-eval 9s. The externalization of the IAO harness into `iao-middleware/` was a key success, along with fixes for evaluator synthesis ratio (G97) and hallucination (G98). The context bundle §1-§11 spec was implemented, though §6 DELTA STATE was functionally broken in the shipped artifact (to be repaired via sidecar in v10.67 W2).

## Comparison to Original Self-Eval

| Workstream | Self-Eval (v10.66 original) | Retroactive (v10.67 W1) |
|---|---|---|
| W1 | 9 | 8 |
| W2 | 9 | 8 |
| W3 | 9 | 8 |
| W4 | 9 | 7 |
| W5 | 9 | 8 |
| W6 | 9 | 8 |
| W7 | 9 | 8 |
| W8 | 9 | 8 |
| W9 | 9 | 7 |
| W10 | 9 | 9 |
| W11 | 9 | 9 |

## G97 Live-Data Validation

**Status: PARTIAL.** Qwen raised `EvaluatorSynthesisExceeded` (Ratio 1.00 > 0.5 for W1). While the exact-match logic from v10.66 W7 is present, the synthesis ratio for the first workstream was calculated as 1.00 by Qwen, triggering the fallback. Gemini Flash (Tier 2) used a lower ratio (0.17). This suggests the Qwen synthesis check is either too sensitive or the v10.66 build log lacked sufficient unique evidence for W1.

## G98 Live-Data Validation

**Status: VALIDATED.** Gemini Flash (Tier 2) successfully processed the 11 workstreams without raising `EvaluatorHallucinatedWorkstream`. The `extract_workstream_ids_from_design` logic was active.

## Findings

- Qwen Tier 1 is highly sensitive to synthesis ratios in early workstreams.
- v10.66 §6 DELTA STATE error was confirmed: `data/iteration_snapshots/v10.66.json` was indeed missing.
- The G97 fix prevents substring overcounting but doesn't necessarily lower the ratio if the evidence provided is considered "generic" by the model.

## Conclusion

Fixes for G97/G98 are functionally present but G97 requires further tuning in v10.67 to ensure Qwen Tier 1 stability on live data. v10.66's self-eval gap is now closed with a realistic 8.1 average score.
