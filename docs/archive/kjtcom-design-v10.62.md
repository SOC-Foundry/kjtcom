# kjtcom - Design Document v10.62

**Phase:** 10 - Pipeline Expansion & Platform Hardening
**Iteration:** 10.62
**Date:** April 06, 2026
**Executor:** Gemini CLI (`gemini --yolo`)
**Previous:** v10.61 (Canvas textures resolved G59 containment but font too small at 6px min. GCP portability plan produced. Harness at 874 lines. OpenClaw added. Parts Unknown deferred. Build/report artifacts NOT produced — G61.)

---

## v10.61 POST-MORTEM

**Delivered:** Canvas texture Claw3D rewrite — text inside chips for the first time in 5 iterations after G59 was registered. GCP portability plan with 4 sections (registry scrub, build order, readiness checklist, pipeline analysis). ADR-013 (Pipeline Configuration Portability), Pattern 18 (G59), component review pass (49 chips across 4 boards, 23 on middleware). OpenClaw chip added. Harness grew from 761 to 874 lines. 15/15 post-flight. 10m 42s execution.

**Failed:**

1. **G60: Map tab regression — 0 mapped of 6,181.** Production map shows entity count but renders zero markers. Was working in v9.31 (Playwright verified). Most likely cause: flutter_map 7→8 upgrade in v9.37 changed the `Marker.builder` to `Marker.child`. Could also be a `lat`/`lon` vs `lat`/`lng` field name mismatch.

2. **G59 partial: Canvas texture font too small.** The `measureText` auto-shrink loop has `fs > 6` as the floor. At 6px on a 64-pixel-per-unit canvas, text is technically inside the chip but visually unreadable. Containment achieved at the cost of legibility. Fix: raise floor to 11px and TRUNCATE labels that don't fit at 11px instead of shrinking further.

3. **G61: No build/report artifacts produced.** v10.61 completed all workstreams and passed 15/15 post-flight, but `docs/kjtcom-build-v10.61.md` and `docs/kjtcom-report-v10.61.md` were never written to disk. The iteration has no audit trail. Either `generate_artifacts.py` was not called, or the G58 immutability guard accidentally blocked build/report alongside design/plan, or the script ran but failed silently.

4. **Parts Unknown not executed in v10.61.** Was a Gemini CLI workstream; v10.61 was Claude Code. Now reactivated in v10.62 since this iteration is Gemini.

---

## ITERATION SCOPE

**This iteration is Gemini CLI executor.** Full stack — app fixes, middleware enforcement, harness updates, AND pipeline work. NZXTcos primary (GPU for Parts Unknown), tsP3-cos for app deploys.

---

## WORKSTREAMS

### W1: Fix Map Tab — 0 Mapped Regression (P0)
Production regression. Map tab shows 0 markers despite 6,181 entities with coordinates. Diagnosis: trace coordinates from Firestore → Riverpod → flutter_map. Likely flutter_map 8.x API change (`builder` → `child`) or field name mismatch. See GEMINI.md W1.

### W2: Claw3D Readable Font (P1)
Raise canvas texture min font from 6px to 11px. Truncate label with `..` if it still doesn't fit at 11px. Bump canvas resolution from 64 to 96 pixels per Three.js unit for sharper text. See GEMINI.md W2.

### W3: Fix Build/Report Generation Enforcement (P1)
The meta-problem from v10.61. Add post-flight check requiring `docs/kjtcom-build-v{X.XX}.md` and `docs/kjtcom-report-v{X.XX}.md` to exist on disk and exceed 100 bytes. Diagnose why v10.61 didn't produce them. Verify `IMMUTABLE_ARTIFACTS` only contains `["design", "plan"]`. Produce retroactive v10.61 build + report from execution evidence. See GEMINI.md W3.

### W4: Component Review + Harness Update (P2)
Run component review pass (Rule 13). Add Pattern 19 (G61) to harness. See GEMINI.md W4.

### W5: Parts Unknown Pipeline — Phase 1 (P1)
**Gemini's specialty.** First 30 videos of the second Bourdain show. Single `bourdain` pipeline, `t_any_shows: ["Parts Unknown"]` differentiates from existing 351 No Reservations entities. Dedup merges arrays for cross-show locations. Validates the multi-show pattern that intranet will use for `t_any_sources`. See GEMINI.md W5.

---

## TRIDENT

| Prong | Target |
|-------|--------|
| Cost | < $2. Gemini free tier for extraction. Ollama free for evaluator. Google Places enrichment. |
| Delivery | 5/5 workstreams. Map fixed. Font readable. Build/report enforced. Parts Unknown started. |
| Performance | Production map renders markers. Claw3D legible at 11px+. Build+report guaranteed on disk. ~70-80 new entities (Parts Unknown × 30 videos × ~2.5/video yield). |

---

*Design v10.62, April 06, 2026. Gemini CLI executor. 5 workstreams. Map fix, Claw3D font, build/report enforcement, component review, Parts Unknown Phase 1.*
