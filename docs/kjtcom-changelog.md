# kjtcom - Unified Changelog

## v10.65 - 2026-04-07

- NEW: Build-as-Gatekeeper - Mandatory `flutter build` in post-flight to prevent deploy breaks (ADR-020).
- NEW: Evaluator Synthesis Audit - Normalizer tracks coercion and forces Tier fall-through if ratio > 0.5 (ADR-021).
- NEW: Context Bundle Generator - Consolidated Operational State as the 5th artifact (ADR-019).
- NEW: Registry-First Diligence - `scripts/query_registry.py` for component discovery (ADR-022).
- NEW: Deployed Version Verification - Post-flight check `deployed_iteration_matches` closes 4-iteration silent deploy regression.
- UPDATED: Bourdain Production Migration - 604 entities moved from staging to production.
- UPDATED: Script Registry - Upgraded to v2 schema with inputs/outputs/pipeline metadata (60 entries).
- Multi-agent: Gemini CLI (executor) + Gemini 2.5 Flash (evaluator fallback)
- Interventions: 0

## v10.64 - 2026-04-06
- NEW: Script Registry Middleware - Created central `data/script_registry.json` for component discovery (ADR-017).
- NEW: Iteration Delta Tracking - Automated growth measurement across iteration boundaries (ADR-016).
- NEW: Bourdain Parts Unknown Phase 2 - Acquisition and transcription hardening; overnight tmux dispatch.
- UPDATED: Claw3D Connector Labels - Migrated from HTML overlays to 3D canvas textures for zero-drift legibility (G69).
- FIXED: Event Log Iteration Tagging - Resolved G68 bug and retroactively corrected v10.63 events.
- FIXED: Gotcha Registry Consolidation - Merged parallel numbering schemes into unified v2 registry (G67).
- Interventions: 0

## v10.63 - 2026-04-06

- NEW: Evaluator Repair - Restored Qwen Tier 1 passing state via ADR-014 context-over-constraint prompting.
- NEW: Self-Grading Auto-Cap - Enforced ADR-015 to prevent agent bias in scores.
- NEW: G60 detection - Added production data render checks to post-flight.
- UPDATED: Evaluator Harness - Cleaned up stale gotchas, renumbered to 956 lines.
- Interventions: 0

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

## v10.66 - 2026-04-08

- NEW: Phase A Harness Externalization - `kjtcom/iao-middleware/` ships universal components with install.fish (ADR-023).
- NEW: Path-Agnostic Component Resolution - `iao_paths.find_project_root()` single source of truth (ADR-024).
- NEW: Dual Deploy-Gap Detection - three post-flight checks for claw3d and Flutter independently (ADR-025).
- NEW: `iao` CLI with project, init, status subcommands (eval/registry deferred to v10.67).
- NEW: COMPATIBILITY.md data-driven checker read by install.fish.
- FIXED: G97 Synthesis ratio substring overcounting (exact-match semantics).
- FIXED: G98 Tier 2 Gemini Flash workstream hallucination (design-doc anchor).
- FIXED: G101 claw3d.html version stamp stale at v10.64 -> v10.66.
- FIXED: G99 Context bundle cosmetic bugs (ADR dedup, delta state, pipeline count).
- UPDATED: Context bundle expanded to spec §1-§11 (439KB retroactive vs 157KB v10.65).
- Interventions: 0
