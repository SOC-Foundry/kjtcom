# kjtcom - Report v10.58

**Evaluator:** self-eval (fallback) + manual correction
**Date:** April 06, 2026

## Summary

v10.58 delivered all 4 workstreams. Bourdain Phase 3 executed end-to-end (30 videos, 88 new entities, 275 total staging). Claw3D got visible board gaps with animated connectors and a logger chip. Evaluator schema was relaxed and report markdown writer added. ADR-011 defined 30 candidate intranet fields. Qwen and Gemini both failed schema validation again - the name matching is too strict (em-dash vs hyphen, truncated names). Self-eval wrote the report but underscored because it parsed build doc with unchecked boxes.

## Workstream Scores

| # | Workstream | Priority | Outcome | Score | Evidence |
|---|-----------|----------|---------|-------|----------|
| W1 | Claw3D Visual Polish - Gaps + Connectors + Logger | P1 | complete | 8/10 | Board positions adjusted (FE/PL y=5.5, MW y=0, BE y=-6), gaps visible, connectors animated, logger chip added, G56=0 |
| W2 | Bourdain Pipeline - Phase 3 | P1 | complete | 8/10 | 30 videos acquired, 30 transcribed (0 timeouts), 29/30 extracted, 88 entities loaded to staging, total 275, checkpoint updated |
| W3 | Fix Evaluator Schema Validation | P1 | partial | 6/10 | Schema relaxed, JSON repair added, report markdown writer works. But Qwen/Gemini still fail - name matching too strict |
| W4 | Thompson Schema v4 - Intranet Field Identification | P2 | complete | 8/10 | ADR-011 in evaluator-harness.md (727 lines, was 670), 30 candidate fields across 7 source types + 4 universal |

## Trident

- **Cost:** ~50K Claude tokens, Gemini Flash free tier (extraction + eval), Ollama free (Qwen eval attempts)
- **Delivery:** 4/4 workstreams completed (3 complete, 1 partial)
- **Performance:** 88 new Bourdain entities in staging, Claw3D gaps + logger, evaluator writes report markdown

## What Could Be Better

- Qwen still cannot follow the workstream schema after 3 attempts - the 9B model may be too small for complex structured output with 10+ required fields per workstream object
- Gemini Flash had banned-phrase issues ("successfully deployed") - need to either remove banned phrase check or train the prompt to avoid them
- Workstream name matching is too strict - "Claw3D Visual Polish" vs "Claw3D Visual Polish - Gaps + Connectors + Logger" causes validation failure. Should use fuzzy/substring matching
- Extraction failure on video 089 (compilation episode, 38K chars) - long transcripts may exceed Gemini context or produce malformed JSON
- Self-eval scores are unreliable because it parses build doc checkbox state at eval time, not actual filesystem evidence

## Workstream Details

### W1: Claw3D Visual Polish - Gaps + Connectors + Logger
- **Agents:** claude-code
- **LLMs:** Claude Opus 4.6
- **MCPs:** -
- **Improvements:**
  - FE/PL-MW gap is ~1.0 units (target was 1.5) - could push FE/PL higher for more separation
  - Board labels could include chip counts for quick reference

### W2: Bourdain Pipeline - Phase 3
- **Agents:** claude-code
- **LLMs:** Gemini Flash (extraction), faster-whisper large-v3 (transcription)
- **MCPs:** Firebase
- **Improvements:**
  - 1 extraction failure (video 089) - add chunking for transcripts > 20K chars
  - Entity yield (3.09/video) is consistent with Phase 1-2 (3.13/video)
  - Production load deferred per plan - schedule for after Phase 4

### W3: Fix Evaluator Schema Validation
- **Agents:** claude-code
- **LLMs:** Claude Opus 4.6, Qwen3.5-9B (failed), Gemini Flash (failed)
- **MCPs:** -
- **Improvements:**
  - Add fuzzy name matching (Levenshtein or substring) instead of exact string comparison
  - Consider upgrading Qwen to a larger model or using Gemini as primary evaluator
  - The concrete JSON example in the prompt helped (attempt 3 had correct top-level structure) but workstream objects still missing required fields

### W4: Thompson Schema v4 - Intranet Field Identification
- **Agents:** claude-code
- **LLMs:** Claude Opus 4.6
- **MCPs:** -
- **Improvements:**
  - Consider adding field cardinality hints (single-value vs multi-value) to ADR-011
  - Add priority ordering for which source types to implement first

---
*Report v10.58, April 06, 2026. Evaluator: self-eval (fallback) + manual correction. 4/4 workstreams. Bourdain Phase 3 complete (275 staging entities). Claw3D gaps + logger. Evaluator report writer working.*
