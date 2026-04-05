# kjtcom - Iteration Report v9.41

**Phase:** 9 - App Optimization
**Iteration:** 9.41
**Date:** April 05, 2026

---

## SUMMARY

v9.41 adds Firestore as a second retrieval path for the Telegram bot /ask command. Previously /ask only hit ChromaDB (dev history). Now a Gemini Flash intent router classifies each question and routes entity queries to Firestore (6,181 locations) while dev history questions still go to ChromaDB (1,419 chunks). The bot answers questions like "where did Guy Fieri go in Texas" with real Firestore results.

4 of 5 workstreams complete. W4 (registry rebuild) deferred - Qwen takes ~60s per iteration, 33 iterations exceeds timeout. W1 (dual retrieval) is the primary deliverable and works end-to-end. W3 (artifact automation) produced this report via generate_artifacts.py + Qwen drafting.

---

## WORKSTREAM SCORECARD

| W# | Name | Priority | Outcome | Agents | LLMs | MCPs | Score |
|----|------|----------|---------|--------|------|------|-------|
| W1 | Firestore dual retrieval path | P1 | complete | claude-code | gemini-flash | firebase | 9/10 |
| W2 | Re-embed archive with v9.38-v9.40 docs | P1 | complete | claude-code | gemini-flash |  | 8/10 |
| W3 | Artifact automation scaffold | P2 | complete | claude-code | qwen, gemini-flash |  | 9/10 |
| W4 | Rebuild iteration_registry.json | P2 | deferred | claude-code | qwen |  | 0/10 |
| W5 | Living doc updates | P3 | complete | claude-code | - | - | 9/10 |

---

## TRIDENT EVALUATION

| Prong | Target | Result |
|-------|--------|--------|
| Cost | <50K Claude tokens, Gemini free tier | Gemini free tier for routing. Ollama local for eval. |
| Delivery | 5 workstreams complete | 4/5 complete. W4 deferred (timeout). |
| Performance | /ask returns real Firestore counts | /ask "how many entities" -> 6,181. /ask "Guy Fieri Texas" -> 84 locations listed. |

---

## AGENT UTILIZATION

Claude Code (primary executor), Qwen3.5-9B (evaluator), Gemini Flash (intent routing, synthesis)

---

## EVENT LOG SUMMARY

Total events: 116
  api_call: 17
  command: 1
  llm_call: 98
Errors: 2

---

## GOTCHAS

G34: Active - post-filter workaround
G47: Open
G53: Recurring

---

## NEXT ITERATION CANDIDATES

- W4: Registry rebuild with batched Qwen calls or shorter num_predict
- Python-side keyword classification for high-frequency routing patterns (reduce Gemini token spend)
- Firestore county enrichment for tripledb pipeline (currently only calgold has counties)

---

*Report v9.41, April 05, 2026.*
