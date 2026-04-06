# kjtcom - Design Document v10.59

**Phase:** 10 - Pipeline Expansion & Platform Hardening
**Iteration:** 10.59
**Date:** April 06, 2026

---

## High-Level Objective
Complete the Bourdain pipeline (videos 91-114), resolve the Claw3D chip text overflow issue, expand the evaluator's context window for better scoring accuracy, and overhaul the project README to reflect the Phase 10 state.

---

## Workstreams

### W1: Bourdain Pipeline — Phase 4 Final Batch (P1)
**Goal:** Process the final 24 videos of the Bourdain playlist.
**Components:** `yt-dlp`, `faster-whisper`, `Gemini Flash`, `Thompson Schema`, `Google Places`.
**Success Criteria:** 114/114 videos processed, all entities loaded to staging Firestore.

### W2: Claw3D Chip Text Fix (P1)
**Goal:** Fix text overflow in Claw3D IC chips.
**Approach:** Shorten chip labels (e.g., `query_editor` -> `query_ed`) and widen the Three.js box geometry from 1.0 to 1.2.
**Success Criteria:** Labels readable at default zoom with no overlap.

### W3: Qwen Context Expansion (P1)
**Goal:** Provide the evaluator with more project context to resolve schema validation failures (G57).
**Approach:** Add `build_rich_context()` to `run_evaluator.py`, including build logs, design docs, example reports, ADRs, and the middleware registry.
**Success Criteria:** Rich context (50-80KB) passed to Qwen; improved fuzzy name matching.

### W4: README Overhaul (P1)
**Goal:** Bring the README up to date with Phase 10 architecture.
**Approach:** Replace solar system references with PCB layout; document all 11 ADRs; update pipeline stats; target 750+ lines.
**Success Criteria:** README length > 750 lines; accurate project state.

---

## Infrastructure Decisions
- **ADR-011 (Thompson Schema v4):** Introduced candidate fields for intranet extensions.
- **Firestore Safety:** Added recursive list flattening to the normalization utility to prevent 400 InvalidArgument errors in Firestore (nested arrays).
