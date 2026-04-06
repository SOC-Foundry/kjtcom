# kjtcom - Design Document v10.57

**Phase:** 10 - Pipeline Expansion & Platform Hardening
**Iteration:** 10.57
**Date:** April 06, 2026
**Previous:** v10.56 (G55 evaluator fixed with fallback chain, Bourdain Phase 2 complete at 188 entities, PCB Claw3D rewritten but broken on deploy — G56)

---

## v10.56 POST-MORTEM

v10.56 was the most productive iteration since Phase 9. Four root causes found and fixed in the evaluator pipeline. Self-eval fallback produced the first scored report in 4 iterations (4/4 workstreams, scores 6-7/10). 188 Bourdain entities in staging. README overhauled. Evaluator harness grew to 601 lines.

But Claw3D broke for the 3rd consecutive iteration. Same symptom: "Error loading data. Check console." Same root cause class: the HTML fetches external JSON files that don't exist on Firebase Hosting. v10.54 had a TypeError in moon positioning. v10.55 fixed the TypeError but animate was broken. v10.56 rewrote the whole thing as PCB but used `fetch()` for component data. Firebase Hosting only serves `app/web/` build output — `data/*.json` files are not deployed. This is now G56.

Post-flight passed 14/14 including `PASS: claw3d_json (valid)` — because the JSON file exists locally on disk. The check doesn't verify it's accessible on the hosted site. Post-flight for Claw3D must check that the HTML does NOT contain external fetch calls.

**Additional feedback from Kyle:**
- 4-board layout required: FE (top-left) + PL (top-right) side by side, MW (center, LARGE), BE (bottom)
- Middleware is the hub — significantly larger than other boards
- All agents, LLMs, MCPs, harness, ADRs live in middleware
- Pipeline board for local GPU extraction scripts
- Backend = Firestore + log sources (processed pipeline data)
- ADR-010 needed for GCP portability (intranet deployment target)
- Intranet vision: different log sources, same normalization, pub/sub topic router for downstream consumers

---

## WORKSTREAMS

### W1: Claw3D 4-Board PCB — Fix G56 + New Layout (P0)

See CLAUDE.md W1 for complete specification including inline data schema, 4-board layout, chip assignments per board, connector definitions, interaction model, and Three.js r128 constraints. The critical fix is Rule 12: ALL data inline as JS objects, zero `fetch()` calls for JSON.

### W2: Bourdain Pipeline — Phase 3 (P1)

Videos 61-90 from playlist. Continue toward production. See CLAUDE.md W2.

### W3: ADR-010 (GCP Portability) + Harness Update (P1)

New ADR documenting the portability design for pipeline/middleware to GCP (tachnet-intranet). Two pipeline configs tracked (v1 established, v2 Bourdain). RickSteves as reference. Intranet pub/sub vision noted. G56 failure pattern added. See CLAUDE.md W3.

### W4: Post-Flight Hardening — G56 Prevention (P2)

Add `grep` check for external JSON fetches in claw3d.html. See CLAUDE.md W4.

---

## TRIDENT TARGETS

| Prong | Target |
|-------|--------|
| Cost | <100K Claude tokens. Gemini free tier. Ollama free. |
| Delivery | 4/4 workstreams. Claw3D loads on live site (3rd attempt). |
| Performance | G56 resolved. 4-board PCB with hover/zoom. Bourdain Phase 3 in staging. |

---

*Design v10.57, April 06, 2026. 4 workstreams. 4-board PCB layout. G56 fix. ADR-010.*
