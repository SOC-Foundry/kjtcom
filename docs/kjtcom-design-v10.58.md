# kjtcom - Design Document v10.58

**Phase:** 10 - Pipeline Expansion & Platform Hardening
**Iteration:** 10.58
**Date:** April 06, 2026
**Previous:** v10.57 (Claw3D 4-board PCB loaded successfully — first working deploy in 4 iterations. G56 resolved. ADR-010 added. Evaluator schema still failing all 3 tiers. Bourdain Phase 3 not executed.)

---

## v10.57 POST-MORTEM

**What worked:**
- Claw3D 4-board PCB layout deployed and loads at kylejeromethompson.com/claw3d.html. All 4 boards visible. Pipeline-colored log sources on backend board. Hover tooltips functional. Iteration dropdown works. G56 resolved by inlining all data.
- ADR-010 (GCP Portability) added to evaluator harness (601+ lines).
- G56 post-flight check added (`grep` for fetch+json = 0).

**What failed:**
1. **Evaluator schema validation:** All 3 tiers failed. Qwen couldn't match schema, Gemini had banned-phrase issues, self-eval wrote `agent_scores.json` but not the report markdown. Claude Code manually produced the report. The `eval_schema.json` is too rigid for the LLMs' actual output format — needs relaxing or the prompt needs a concrete JSON example.
2. **Bourdain Phase 3 not executed:** Pipeline work didn't happen. Must run in v10.58.
3. **Claw3D layout needs gaps:** FE and PL boards sit directly on top of MW. Need visible gaps with animated trace connectors between all board pairs (like BE→MW already has).
4. **No logger chip on middleware:** Event logging is a middleware function but has no chip representation.

---

## WORKSTREAMS

### W1: Claw3D Visual Polish — Gaps + Connectors + Logger (P1)
Adjust board positions to create gaps. Add animated trace connectors between all board pairs. Add iao_logger chip to middleware. See CLAUDE.md W1 for positions and connector labels.

### W2: Bourdain Pipeline — Phase 3 (P1)
Videos 61-90. Did not execute in v10.57. See CLAUDE.md W2.

### W3: Fix Evaluator Schema Validation (P1)
All 3 evaluator tiers failing schema validation. Diagnose `eval_schema.json` constraints, relax or provide concrete JSON example, ensure self-eval produces report markdown (not just agent_scores.json). See CLAUDE.md W3.

### W4: Thompson Schema v4 — Intranet Field Identification (P2)
New ADR-011 identifying `t_any_*` fields needed for intranet log sources (docs, spreadsheets, meeting transcripts, Gmail, Slack, CRM, contractor portal). Also defines universal fields (`t_any_tags`, `t_any_record_ids`, `t_any_sources`, `t_any_sensitivity`). Design decision only — no implementation. See CLAUDE.md W4 for full field mapping table.

---

## TRIDENT

| Prong | Target |
|-------|--------|
| Cost | <100K Claude tokens. Gemini free. Ollama free. |
| Delivery | 4/4 workstreams. Bourdain Phase 3 must execute. |
| Performance | Claw3D with gaps + connectors. Evaluator produces valid report. |

---

*Design v10.58, April 06, 2026. 4 workstreams. Claw3D polish, Bourdain Phase 3, evaluator fix, schema v4 design.*
