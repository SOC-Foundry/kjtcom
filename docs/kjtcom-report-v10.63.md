# kjtcom - Report v10.63

**Evaluator:** qwen3.5:9b
**Date:** April 06, 2026

## Summary

Implemented ADR-014: Switched evaluator prompt strategy to 'context-rich, constraint-light'. Added `normalize_llm_output()` in `scripts/run_evaluator.py` to handle schema deviations (priority strings, missing fields, malformed tridents) by coercing them to canonical values. Codified ADR-015: Auto-cap self-graded scores (self-eval) to the Tier 3 limit of 7/10. Enforced G61 artifact immutability in `generate_artifacts.py`. Updated Changelog to v10.63.

## Workstream Scores

| # | Workstream | Priority | Outcome | Score | Evidence |
|---|-----------|----------|---------|-------|----------|
| W1 | Qwen Evaluator Repair via Rich Context | P1 | partial | 5/10 | Evaluator did not return per-workstream evidence; see build log for W1. |
| W2 | Evaluator Harness Cleanup, Renumbering, and Pattern 20 | P1 | partial | 5/10 | Evaluator did not return per-workstream evidence; see build log for W2. |
| W3 | Post-Flight Production Data Render Check | P1 | partial | 5/10 | Evaluator did not return per-workstream evidence; see build log for W3. |
| W4 | Query Editor Migration to flutter_code_editor (G45) | P1 | partial | 5/10 | Evaluator did not return per-workstream evidence; see build log for W4. |
| W5 | Parts Unknown Acquisition Hardening + Phase 2 | P1 | partial | 5/10 | Evaluator did not return per-workstream evidence; see build log for W5. |
| W6 | README Sync + Component Review + Pattern 20 Embed | P1 | partial | 5/10 | Evaluator did not return per-workstream evidence; see build log for W6. |

## Trident

- **Cost:** Low (Context expansion vs. schema tightening)
- **Delivery:** 0/6 workstreams complete (normalized from 'Compliant (Normalized via code)')
- **Performance:** High (Robust to model drift)

## What Could Be Better

- Normalize priority strings ('high'->'P0') earlier in the pipeline to reduce normalization load in `run_evaluator.py`.
- Implement a unit test for `normalize_llm_output()` against known bad-input scenarios (e.g., empty reports, malformed JSON) to prevent silent data loss.
- Extend `--rich-context` bundle to include the 'Gotcha Archive' as few-shot examples for pattern recognition in reports.

## Workstream Details

### W1: Qwen Evaluator Repair via Rich Context
- **Agents:** claude-code
- **LLMs:** qwen3.5:9b
- **MCPs:** -
- **Improvements:**
  - Evaluator returned fewer than two improvements; consider re-running with a richer build log.
  - Add a unit test fixture for normalize_llm_output() covering all coercion paths.

### W2: Evaluator Harness Cleanup, Renumbering, and Pattern 20
- **Agents:** claude-code
- **LLMs:** qwen3.5:9b
- **MCPs:** -
- **Improvements:**
  - Evaluator returned fewer than two improvements; consider re-running with a richer build log.
  - Add a unit test fixture for normalize_llm_output() covering all coercion paths.

### W3: Post-Flight Production Data Render Check
- **Agents:** claude-code
- **LLMs:** qwen3.5:9b
- **MCPs:** -
- **Improvements:**
  - Evaluator returned fewer than two improvements; consider re-running with a richer build log.
  - Add a unit test fixture for normalize_llm_output() covering all coercion paths.

### W4: Query Editor Migration to flutter_code_editor (G45)
- **Agents:** claude-code
- **LLMs:** qwen3.5:9b
- **MCPs:** -
- **Improvements:**
  - Evaluator returned fewer than two improvements; consider re-running with a richer build log.
  - Add a unit test fixture for normalize_llm_output() covering all coercion paths.

### W5: Parts Unknown Acquisition Hardening + Phase 2
- **Agents:** claude-code
- **LLMs:** qwen3.5:9b
- **MCPs:** -
- **Improvements:**
  - Evaluator returned fewer than two improvements; consider re-running with a richer build log.
  - Add a unit test fixture for normalize_llm_output() covering all coercion paths.

### W6: README Sync + Component Review + Pattern 20 Embed
- **Agents:** claude-code
- **LLMs:** qwen3.5:9b
- **MCPs:** -
- **Improvements:**
  - Evaluator returned fewer than two improvements; consider re-running with a richer build log.
  - Add a unit test fixture for normalize_llm_output() covering all coercion paths.

---
*Report v10.63, April 06, 2026. Evaluator: qwen3.5:9b.*
