# kjtcom - Plan v10.59

**Iteration:** 10.59
**Focus:** Bourdain Completion + README + Evaluator Context

---

## Plan

### W1: Bourdain Pipeline Final Batch
1. Acquire videos 91-114 via `yt-dlp`.
2. Unload Ollama to free GPU memory.
3. Transcribe videos in 3 sequential batches (91-100, 101-110, 111-114) using `faster-whisper`.
4. Extract entities via Gemini Flash.
5. Normalize, geocode, and enrich entities.
6. Load to staging Firestore.
7. Update checkpoint to Phase 4 Complete.

### W2: Claw3D Visual Fixes
1. Edit `app/web/claw3d.html` to shorten chip IDs and labels.
2. Increase chip width from 0.8 to 1.2 in `getChipLayout`.
3. Update version string to v10.59.
4. Deploy to Firebase Hosting.

### W3: Evaluator Context Expansion
1. Implement `build_rich_context()` in `scripts/run_evaluator.py`.
2. Update evaluator prompt to include rich context and example reports.
3. Improve fuzzy name matching in validation logic.
4. Test with previous iteration.

### W4: README Overhaul
1. Rewrite README header and status.
2. Update pipeline table with Bourdain completion stats.
3. Detail the 4-board PCB architecture and link to Claw3D.
4. Expand Middleware and ADR sections.
5. Prepend recent changelogs.
6. Verify line count > 750.

---

## Post-Flight
1. Run `scripts/post_flight.py`.
2. Generate artifacts (Build Log, Report).
3. Archive previous artifacts.
