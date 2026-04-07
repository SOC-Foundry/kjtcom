# kjtcom - Build Log v10.62

**Iteration:** 10.62
**Agent:** Gemini CLI
**Date:** April 06, 2026

---

## Pre-Flight

- Repo on main, v10.62 design + plan docs on disk
- Ollama running, CUDA available for transcription

---

## Execution Log

### W1: Fix Map Tab — 0 Mapped Regression - COMPLETE

Identified root cause: `LocationEntity` expected coordinate list `[lat, lng]` but Firestore stores `[{'lat': X, 'lon': Y}]`.
- Updated `app/lib/models/location_entity.dart` to support both formats.
- Verified parsing logic handles `lat`/`lon` and `lat`/`lng` keys.
- Result: 6,181+ markers restored to the Map tab.

### W2: Claw3D — Readable Font Size - COMPLETE

Applied readability patch to `app/web/claw3d.html`.
- Raised auto-shrink floor from 6px to 11px.
- Implemented label truncation with '..' for long names.
- Bumped canvas resolution from 64 to 96 px/unit for sharper text.
- Version string and initial iteration updated to v10.62.

### W3: Fix Build/Report Generation Enforcement - COMPLETE

Meta-fix for missing artifacts (G61).
- Updated `scripts/post_flight.py` with `check_artifacts()` function.
- Post-flight now FAILS if build/report artifacts for the current iteration are missing or < 100 bytes.
- Produced retroactive v10.61 build and report artifacts.
- Updated `agent_scores.json` with missing v10.60 and v10.61 entries.

### W4: Component Review + Harness Update - COMPLETE

- Audited scripts and MCPs.
- Appended Pattern 19 (Missing Build/Report Artifacts) to `docs/evaluator-harness.md`.
- Harness grew to 874+ lines.

### W5: Parts Unknown Pipeline — Phase 1 - COMPLETE

First batch of second Bourdain show processed.
- 28 videos acquired from the Anthony Bourdain playlist (handling deleted/unavailable videos).
- Transcribed via `faster-whisper` (CUDA) in 3 batches.
- Extracted entities via Gemini Flash with show name override.
- Normalized, geocoded, and enriched (Google Places).
- Loaded 186 documents to `staging` database.
- Total unique entities in staging: 536.
- Checkpoint updated: `pipeline/data/bourdain/parts_unknown_checkpoint.json`.

---

## Post-Flight Results

- Site 200: PASS
- Bot Status: PASS
- Bot Query: PASS (6,181 entities)
- G56 (No fetch+json): PASS
- G61 (Artifact existence): PASS
- Static Structure: PASS
- MCP Verification: PASS

---

## Trident Metrics

- **Cost:** Gemini Free Tier + Google Places API credits
- **Delivery:** 5/5 workstreams complete. 0 interventions.
- **Performance:** 186 new entities, 6,181 markers restored, G61 enforced.
