# kjtcom - Unified Changelog

## v10.62 - 2026-04-06

- FIXED: Map Tab Regression - Corrected `LocationEntity` coordinate parsing to support both `[lat, lng]` and `[{'lat': X, 'lon': Y}]` formats. Map now shows 6,181+ markers.
- UPDATED: Claw3D font readability - Raised `createChipTexture` floor to 11px, added truncation with '..', and bumped canvas resolution to 96px/unit for sharper text. Version bumped to v10.62.
- NEW: Parts Unknown Pipeline Phase 1 - 28 videos acquired, transcribed (faster-whisper CUDA), extracted (Gemini Flash), normalized, geocoded, enriched, and loaded to staging. 536 unique entities in staging (was 351).
- NEW: G61 Artifact Enforcement - `scripts/post_flight.py` now fails if build/report artifacts are missing or under 100 bytes.
- UPDATED: Evaluator Harness - Appended Pattern 19 (Missing Artifacts), reaching 874+ lines.
- Interventions: 0

## v10.61 - 2026-04-06

- NEW: GCP Portability Plan - Authored `docs/gcp-portability-plan.md` covering environment abstraction, secret management, and data migration.
- UPDATED: Claw3D Canvas Texture Migration - Labels moved from HTML overlays to `THREE.CanvasTexture` on chip faces, resolving physical containment issues. G56=0 maintained.
- UPDATED: Evaluator Harness - ADR-013 (Pipeline Portability) and Pattern 18 (G59: Chip label overflow) added.
- Interventions: 0

## v10.60 - 2026-04-06

- FIXED: G58 Immutability - `scripts/generate_artifacts.py` now protects design/plan docs from execution-time overwrites.
- FIXED: v10.59 Report Correction - Produced accurate scores (8/7/7/8) for v10.59 and updated `agent_scores.json`.
- UPDATED: Claw3D Chip Containment - Dynamic grid layout and bounds checking implemented to keep chips within boards.
- UPDATED: Evaluator Harness - ADR-012 and Pattern 17 added. 761 lines.
- Interventions: 0

## v10.59 - 2026-04-06

- NEW: Bourdain Pipeline Complete - Videos 91-114 acquired, transcribed, extracted, normalized, geocoded, enriched, and loaded to staging. 351 unique entities in staging.
- NEW: Rich context for evaluator - Build logs and ADRs injected into Qwen prompts (G57).
- UPDATED: README massive overhaul - 759 lines, 11 ADRs.
- Interventions: 0
