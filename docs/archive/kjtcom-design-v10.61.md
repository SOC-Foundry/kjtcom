# kjtcom - Design Document v10.61

**Phase:** 10 - Pipeline Expansion & Platform Hardening
**Iteration:** 10.61
**Date:** April 06, 2026
**Previous:** v10.60 (G58 resolved, v10.59 report corrected, harness 761 lines, Claw3D containment attempted but chips still overflow — 4th consecutive failure)

---

## v10.60 POST-MORTEM

**Delivered:** 5/5 workstreams, zero interventions, 8m 38s execution. G58 (artifact immutability) resolved — `generate_artifacts.py` now skips existing design/plan docs. v10.59 corrected report produced (8/7/7/8 replacing 0/0/0/0). Original v10.59 docs reconstructed from GEMINI.md. ADR-012 + Pattern 17 added to harness (761 lines). 15/15 post-flight. Cost $0.

**Still broken:** Claw3D chip text overflow. v10.57 shortened labels. v10.58 widened chips. v10.59 shortened more. v10.60 added containment logic. Text STILL overflows. Root cause: HTML overlay text positioned via `Vector3.project()` has no relationship to Three.js geometry boundaries. The text just floats wherever the coordinate projects to screen space. No amount of label shortening fixes this because the text rendering is fundamentally decoupled from the geometry it's supposed to sit inside.

**New this iteration:** Parts Unknown playlist starts under the existing Bourdain pipeline. GCP portability planning begins. OpenClaw added to middleware component registry.

---

## WORKSTREAMS

### W1: Parts Unknown Pipeline — Phase 1 Discovery (P1)

Start the second Bourdain show. Single `bourdain` pipeline, `t_any_shows: ["Parts Unknown"]` differentiates from existing `["No Reservations"]` entities. Dedup merges shows arrays for locations appearing in both series. Gemini CLI executes on NZXTcos. First 30 videos. Staging only. See CLAUDE.md W1.

**Playlist:** `https://www.youtube.com/watch?v=6PQB1S5sZQ0&list=PLfLND2Lym9knKTVU7lHYROAGWmTH2kEFo`

**Pipeline analysis value:** This is the first multi-show test within a single pipeline. Validates that `t_any_shows` differentiation works at scale, which is the exact pattern intranet will use with `t_any_sources` to differentiate Gmail vs Slack vs CRM within a single pipeline infrastructure.

### W2: GCP Portability Planning — ADR-013 (P1)

Produce `docs/gcp-portability-plan.md` with 4 sections: registry artifacts to scrub/transfer, GCP resource build order (VPC → Compute → Storage → Middleware → Pipeline configs), harness readiness checklist, and pipeline configuration analysis (v1 vs v2, Bourdain as intranet template, RickSteves as operational reference). See CLAUDE.md W2.

### W3: Claw3D — Hard Chip Containment via Canvas Textures (P0)

**G59: 4 consecutive failures demand a fundamentally different approach.** Replace HTML overlay labels with canvas texture rendering. Text is painted directly onto the chip face material using `CanvasTexture` with `ctx.measureText()` to auto-shrink font until it fits. Text physically cannot overflow because it IS the chip surface. Keep hover tooltips as HTML overlays (those are temporary popups that should float). Add OpenClaw to middleware board. Run component review pass. See CLAUDE.md W3.

### W4: Harness + ADR Updates (P2)

ADR-013 (Pipeline Configuration Portability), Pattern 18 (G59: chip text overflow despite repeated fixes), component review checklist section. See CLAUDE.md W4.

---

## TRIDENT

| Prong | Target |
|-------|--------|
| Cost | < $2. Gemini free tier for pipeline. Ollama free. |
| Delivery | 4/4. Parts Unknown Phase 1. GCP plan. Claw3D fixed for real. |
| Performance | Canvas textures guarantee containment. Multi-show pipeline validated. Portability plan documented. |

---

*Design v10.61, April 06, 2026. 4 workstreams. Parts Unknown, GCP portability, canvas texture Claw3D, OpenClaw.*
