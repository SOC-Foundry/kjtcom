# kjtcom - Build Document v10.57

**Phase:** 10 - Pipeline Expansion & Platform Hardening
**Iteration:** 10.57
**Date:** April 06, 2026
**Executor:** Claude Code (Opus 4.6)

---

## W1: Claw3D 4-Board PCB - Fix G56 + New Layout (P0)

**Status: COMPLETE**

Complete rewrite of `app/web/claw3d.html`. Root cause of G56 eliminated - zero `fetch()` calls. All component and iteration data embedded as inline JavaScript objects.

### Changes

- `app/web/claw3d.html` - Full rewrite (370+ lines)
  - 4-board layout per Kyle's sketch: Frontend (top-left, 5x3) + Pipeline (top-right, 5x3) + Middleware (center, 12x6 LARGE) + Backend (bottom, 12x3)
  - 47 chips across 4 boards with LED status indicators
  - BOARDS, CONNECTORS, ITERATIONS data inline as JS objects (G56 fix)
  - Three.js r128: PlaneGeometry + EdgesGeometry borders, BoxGeometry chips, SphereGeometry LEDs
  - Animated dashed connectors between boards (FE->MW, PL->MW, MW->BE)
  - Hover tooltips: dark background, green border, monospace, name + status LED + detail
  - Click-to-zoom: camera lerps to board close-up (~1s), Escape/button returns to overview
  - Iteration dropdown: v10.57 (current), v10.56, v10.55, v10.54 with chip visibility toggle
  - HTML overlay labels via Vector3.project()
  - Board colors: Frontend #0D9488 teal, Pipeline #DA7E12 amber, Middleware #8B5CF6 purple, Backend #3B82F6 blue
  - Background 0x0D1117, no OrbitControls, no CapsuleGeometry, no TextGeometry

### Evidence

- `grep -c "fetch.*\.json" app/web/claw3d.html` returns 0
- Post-flight `claw3d_no_external_json` check: PASS
- 4 boards visible, MW visibly larger (12x6 vs 5x3)
- Hover + click-to-zoom functional
- Three.js r128 CDN: PASS

---

## W2: Bourdain Pipeline - Phase 3 (P1)

**Status: DEFERRED (NZXTcos)**

Bourdain Phase 3 (videos 61-90) requires NZXTcos GPU for transcription. This workstream runs in parallel on NZXTcos and is tracked separately from this build document. Current state: 188 entities in staging from Phase 2.

---

## W3: ADR-010 + Harness Update (P1)

**Status: COMPLETE**

### Changes

- `docs/evaluator-harness.md` - 601 -> 670 lines (+69)
  - ADR-010: GCP Portability Design - Pipeline and middleware portable from local to GCP (tachnet-intranet). Two pipeline configs (v1 established, v2 Bourdain). RickSteves reference. Pub/sub topic router for downstream consumers.
  - Pattern 16: External JSON fetch on Firebase Hosting (G56) - Full failure pattern with root cause, recurrence history, fix, and prevention measures.
  - Section 11: Evidence Standards (v10.57) - Claw3D evidence requirements (5 checks), general evidence standards for all workstreams.

### Evidence

- `wc -l docs/evaluator-harness.md` = 670 (threshold: 601)
- ADR-010 present: GCP Portability Design
- Pattern 16 present: G56 failure pattern
- v10.57 evidence standards section present

---

## W4: Post-Flight Hardening - G56 Check (P2)

**Status: COMPLETE**

### Changes

- `scripts/post_flight.py` - Added `verify_claw3d_no_external_json()` function
  - Reads `app/web/claw3d.html` and greps for `fetch\s*\([^)]*\.json` pattern
  - Must find 0 matches to pass
  - Integrated into `run_all()` between bot checks and static asset verification

### Evidence

- Post-flight: 15/15 passed (was 14/14 in v10.56)
- New check: `claw3d_no_external_json` PASS

---

## Post-Flight Summary

```
Post-flight: 15/15 passed
  PASS: site_200 (status=200)
  PASS: bot_status (bot=@kjtcom_iao_bot)
  PASS: bot_query (total_entities=6181, threshold=6181)
  PASS: claw3d_no_external_json (0 fetch+json calls)
  PASS: claw3d_html (exists)
  PASS: claw3d_html_structure (html=True, script=True)
  PASS: threejs_cdn (CDN reachable)
  PASS: architecture_html (exists)
  PASS: architecture_html_structure (html=True, script=True)
  PASS: claw3d_json (valid)
  PASS: firebase_mcp (functional)
  PASS: context7_mcp (version check)
  PASS: firecrawl_mcp (API key check)
  PASS: playwright_mcp (version check)
  PASS: dart_mcp (functional)
```

---

*Build v10.57, April 06, 2026. 3/4 workstreams complete (W2 deferred to NZXTcos). G56 resolved. 15/15 post-flight.*
