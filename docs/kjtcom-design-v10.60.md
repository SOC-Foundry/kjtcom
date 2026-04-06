# kjtcom - Design Document v10.60

**Phase:** 10 - Pipeline Expansion & Platform Hardening
**Iteration:** 10.60
**Date:** April 06, 2026
**Previous:** v10.59 (Bourdain Phase 4 complete — 351 entities, 114/114 videos. Claw3D chip text shortened. Qwen rich context added. README at 759 lines. BUT: Gemini overwrote design/plan docs, report scored 0/10 on all workstreams despite full delivery, chip text still overflows boards.)

---

## v10.59 POST-MORTEM

**What worked:**
- Bourdain pipeline COMPLETE. 114/114 videos processed, 351 unique entities in staging across 44+ countries. Nested array fix (`make_firestore_safe()`) resolved Firestore 400 errors. Gemini CLI executed the pipeline cleanly.
- Claw3D chip labels shortened, chips widened. G56 still passing (0 fetch+json).
- `build_rich_context()` added to evaluator (few-shot examples, middleware registry, gotcha archive, ADRs). Fuzzy name matching improved.
- README overhauled to 759 lines. 4 pipelines, PCB architecture, 11 ADRs, middleware section.
- 15/15 post-flight. Zero interventions. Cost ~$1.50.

**What failed:**

1. **G58: Gemini overwrote design and plan docs.** `generate_artifacts.py` regenerated all 4 artifacts unconditionally. The carefully authored design doc (with Mermaid trident, v10.58 post-mortem, detailed workstream specs) was replaced with a 50-line summary. The plan doc (with 10 IAO pillars, pre-flight checklist, 5-step execution sequence) was replaced with a bullet list. This destroys the audit trail and the separation between planning and execution.

2. **Report scored 0/10 on everything.** Self-eval tier said "No build log evidence found" for all 4 workstreams, despite the build log existing with detailed evidence (351 entities, Claw3D deployed, README at 759 lines). Root cause: self-eval function either ran before build log was written, or parsed the wrong file path, or couldn't match Gemini's build log format.

3. **Chip text still overflows boards.** v10.59 shortened labels and widened chips, but components still spill outside their parent board boundaries. Need hard containment: max characters, CSS overflow hidden, grid computation that guarantees fit.

---

## WORKSTREAMS

### W1: Fix generate_artifacts.py — G58 Artifact Immutability (P0)
Design and plan docs are INPUT artifacts from the planning session — immutable during execution. `generate_artifacts.py` must skip them if they already exist. Also fix self-eval build log path so it finds evidence. See CLAUDE.md W1.

### W2: Produce Accurate v10.59 Report (P1)
The v10.59 report is factually wrong (0/10 across the board). Produce a corrected report based on the build log evidence: W1 8/10, W2 7/10, W3 7/10, W4 8/10. Update agent_scores.json. See CLAUDE.md W2.

### W3: Restore Original v10.59 Design + Plan Docs (P1)
Recover the original planning-session artifacts from git history or reconstruct from GEMINI.md. The originals had the Mermaid trident, 10 pillars, detailed execution steps. See CLAUDE.md W3.

### W4: Evaluator Harness — ADR-012 + Pattern 17 (P2)
Add ADR-012 (Artifact Immutability During Execution) and Pattern 17 (G58: agent overwrites input artifacts) to `docs/evaluator-harness.md`. See CLAUDE.md W4.

### W5: Claw3D — All Components Must Fit Inside Their Board (P1)
Hard containment: chip labels inside chip boxes (max 8 chars small boards, 10 chars large), chips inside board borders, board titles inside borders, FE/PL horizontal gap, CSS overflow hidden on HTML overlays, programmatic bounds checking. See CLAUDE.md W5.

---

## TRIDENT

| Prong | Target |
|-------|--------|
| Cost | Minimal — no pipeline work, no API calls except evaluator. |
| Delivery | 5/5 workstreams. G58 resolved. v10.59 report corrected. Claw3D contained. |
| Performance | Artifact immutability enforced. Evaluator finds build log. All chips inside boards. |

---

*Design v10.60, April 06, 2026. 5 workstreams. G58 artifact immutability. Claw3D containment. v10.59 report correction.*
