# kjtcom - Report v10.64

**Evaluator:** self-eval (fallback)
**Date:** April 06, 2026

## Summary

Self-evaluation fallback for v10.64. Qwen and Gemini Flash both failed schema validation. 14 workstreams parsed from design doc. Scores capped at 7/10 to avoid self-grading bias.

## Workstream Scores

| # | Workstream | Priority | Outcome | Score | Evidence |
|---|-----------|----------|---------|-------|----------|
| W1 | Bourdain Parts Unknown Phase 2 — Acquisition + Transcription | P0 | partial | 6/10 | ### W1: Bourdain Parts Unknown Phase 2 — Acquisition + Transcription (P0) — [out |
| W2 | Bourdain Production Load | P0 | partial | 6/10 | - **Ollama Loaded:** empty (PASS); ### W1: Bourdain Parts Unknown Phase 2 — Acqu |
| W3 | Query Editor Migration to flutter_code_editor (G45) | P1 | partial | 6/10 | ### W14: Claw3D connector label canvas texture migration (G69) — [outcome]; ###  |
| W4 | Visual Baseline Diff Post-Flight Check (ADR-018) | P0 | partial | 6/10 | - **Resolution:** Dead data in `data/` replaced with current truth from live vis |
| W5 | Parts Unknown Checkpoint Dashboard + Failure Histogram | P2 | partial | 6/10 | ### W1: Bourdain Parts Unknown Phase 2 — Acquisition + Transcription (P0) — [out |
| W6 | Script Registry Middleware (ADR-017) | P1 | partial | 6/10 | - **Diligence Read:** scripts/utils/iao_logger.py, data/iao_event_log.jsonl (tai |
| W7 | Iteration Delta Tracking Script (ADR-016) | P1 | partial | 6/10 | **Iteration:** 10.64; - **Iteration Env:** IAO_ITERATION=v10.64 (PASS); ### W9:  |
| W8 | Gotcha Registry Consolidation (G67) | P1 | partial | 6/10 | ### W6: Script Registry Middleware — [complete]; - **Script:** Created `scripts/ |
| W9 | Event Log Iteration Tag Bug Fix (G68) | P1 | partial | 6/10 | **Iteration:** 10.64; - **Iteration Env:** IAO_ITERATION=v10.64 (PASS); ### W9:  |
| W10 | Stale Data File Cleanup (G66) | P2 | partial | 6/10 | - **Diligence Read:** scripts/utils/iao_logger.py, data/iao_event_log.jsonl (tai |
| W11 | Pre-Flight Zero-Intervention Hardening (G71) | P1 | partial | 6/10 | ## Pre-Flight; ### W11: Pre-flight zero-intervention hardening (G71) — [outcome] |
| W12 | Post-Flight MCP Functional Probes (G70) | P1 | partial | 6/10 | - **Stats:** Detected 47 scripts (Active: 0, Stale: 47, Dead: 0). Heuristic for  |
| W13 | README Sync + Harness Expansion | P2 | partial | 6/10 | - **Script:** Created `scripts/sync_script_registry.py` to walk codebase and ind |
| W14 | Claw3D Connector Label Canvas Texture Migration (G69) | P0 | partial | 6/10 | ### W10: Stale claw3d data file cleanup (G66) — [outcome]; ### W10: Stale claw3d |

## Trident

- **Cost:** Minimal - self-eval required no LLM tokens
- **Delivery:** 0/14 workstreams completed (self-eval)
- **Performance:** Self-eval fallback triggered - evaluator pipeline needs repair

## What Could Be Better

- Qwen failed schema validation after 3 attempts - prompt or model issue
- Gemini Flash failed schema validation after 2 attempts - schema may be too strict
- Self-eval cannot provide the same quality as an independent evaluator

## Workstream Details

### W1: Bourdain Parts Unknown Phase 2 — Acquisition + Transcription
- **Agents:** claude-code
- **LLMs:** qwen3.5:9b
- **MCPs:** -
- **Improvements:**
  - Self-eval fallback used - Qwen and Gemini both failed schema validation
  - Manual review recommended for accurate scoring

### W2: Bourdain Production Load
- **Agents:** claude-code
- **LLMs:** qwen3.5:9b
- **MCPs:** -
- **Improvements:**
  - Self-eval fallback used - Qwen and Gemini both failed schema validation
  - Manual review recommended for accurate scoring

### W3: Query Editor Migration to flutter_code_editor (G45)
- **Agents:** claude-code
- **LLMs:** qwen3.5:9b
- **MCPs:** -
- **Improvements:**
  - Self-eval fallback used - Qwen and Gemini both failed schema validation
  - Manual review recommended for accurate scoring

### W4: Visual Baseline Diff Post-Flight Check (ADR-018)
- **Agents:** claude-code
- **LLMs:** qwen3.5:9b
- **MCPs:** -
- **Improvements:**
  - Self-eval fallback used - Qwen and Gemini both failed schema validation
  - Manual review recommended for accurate scoring

### W5: Parts Unknown Checkpoint Dashboard + Failure Histogram
- **Agents:** claude-code
- **LLMs:** qwen3.5:9b
- **MCPs:** -
- **Improvements:**
  - Self-eval fallback used - Qwen and Gemini both failed schema validation
  - Manual review recommended for accurate scoring

### W6: Script Registry Middleware (ADR-017)
- **Agents:** claude-code
- **LLMs:** qwen3.5:9b
- **MCPs:** -
- **Improvements:**
  - Self-eval fallback used - Qwen and Gemini both failed schema validation
  - Manual review recommended for accurate scoring

### W7: Iteration Delta Tracking Script (ADR-016)
- **Agents:** claude-code
- **LLMs:** qwen3.5:9b
- **MCPs:** -
- **Improvements:**
  - Self-eval fallback used - Qwen and Gemini both failed schema validation
  - Manual review recommended for accurate scoring

### W8: Gotcha Registry Consolidation (G67)
- **Agents:** claude-code
- **LLMs:** qwen3.5:9b
- **MCPs:** -
- **Improvements:**
  - Self-eval fallback used - Qwen and Gemini both failed schema validation
  - Manual review recommended for accurate scoring

### W9: Event Log Iteration Tag Bug Fix (G68)
- **Agents:** claude-code
- **LLMs:** qwen3.5:9b
- **MCPs:** -
- **Improvements:**
  - Self-eval fallback used - Qwen and Gemini both failed schema validation
  - Manual review recommended for accurate scoring

### W10: Stale Data File Cleanup (G66)
- **Agents:** claude-code
- **LLMs:** qwen3.5:9b
- **MCPs:** -
- **Improvements:**
  - Self-eval fallback used - Qwen and Gemini both failed schema validation
  - Manual review recommended for accurate scoring

### W11: Pre-Flight Zero-Intervention Hardening (G71)
- **Agents:** claude-code
- **LLMs:** qwen3.5:9b
- **MCPs:** -
- **Improvements:**
  - Self-eval fallback used - Qwen and Gemini both failed schema validation
  - Manual review recommended for accurate scoring

### W12: Post-Flight MCP Functional Probes (G70)
- **Agents:** claude-code
- **LLMs:** qwen3.5:9b
- **MCPs:** -
- **Improvements:**
  - Self-eval fallback used - Qwen and Gemini both failed schema validation
  - Manual review recommended for accurate scoring

### W13: README Sync + Harness Expansion
- **Agents:** claude-code
- **LLMs:** qwen3.5:9b
- **MCPs:** -
- **Improvements:**
  - Self-eval fallback used - Qwen and Gemini both failed schema validation
  - Manual review recommended for accurate scoring

### W14: Claw3D Connector Label Canvas Texture Migration (G69)
- **Agents:** claude-code
- **LLMs:** qwen3.5:9b
- **MCPs:** -
- **Improvements:**
  - Self-eval fallback used - Qwen and Gemini both failed schema validation
  - Manual review recommended for accurate scoring

---
*Report v10.64, April 06, 2026. Evaluator: self-eval (fallback).*
