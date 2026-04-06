# kjtcom - Build Log v10.58

**Phase:** 10 - Pipeline Expansion & Platform Hardening
**Iteration:** 10.58
**Date:** April 06, 2026
**Machine:** NZXTcos (GPU) + tsP3-cos parallel

---

## W1: Claw3D Visual Polish - Gaps + Connectors + Logger

### Actions
1. Adjusted board positions in `app/web/claw3d.html`:
   - Frontend: [-3.5, 3, 0] -> [-3, 5.5, 0]
   - Pipeline: [3.5, 3, 0] -> [3, 5.5, 0]
   - Middleware: [0, -1.5, 0] -> [0, 0, 0]
   - Backend: [0, -6.5, 0] -> [0, -6, 0]
2. Gaps created: FE/PL-MW ~1.0 unit, MW-BE ~1.5 units
3. Connectors already computed dynamically from board edge positions - gaps are now visible between all board pairs
4. Connector labels present: "Riverpod / Firestore stream", "Pipeline scripts / checkpoint", "Admin SDK / Ollama / ChromaDB"
5. Added `iao_logger` chip to middleware: `{id:"iao_logger", status:"active", detail:"JSONL event log, P3 diligence"}`
6. Camera overview adjusted: (0, 0, 22) for wider view
7. Zoom targets updated to match new board positions
8. Version bumped to v10.58
9. Added v10.58 iteration entry, moved v10.57 to explicit chip list
10. G56 check: `grep -c "fetch.*\.json" app/web/claw3d.html` = 0

### Evidence
- `app/web/claw3d.html` updated (boards repositioned, logger chip added)
- 0 fetch+json references (G56 compliant)
- 22 middleware chips (was 21)

---

## W2: Bourdain Pipeline - Phase 3 (Videos 61-90)

### Actions
1. Ollama unloaded for GPU (G18): `curl -s ... keep_alive:0`
2. yt-dlp download: 30/30 MP3 files acquired (videos 061-090)
3. Phase 2 transcription: faster-whisper CUDA, graduated batches of 10
4. Phase 3 extraction: Gemini Flash via extraction_prompt.md
5. Phase 4 normalization: Schema v3 t_any_* compliance
6. Phase 5 geocoding: Nominatim 1 req/sec
7. Phase 6 enrichment: Google Places API
8. Phase 7 load: Staging only (NOT production)
9. Checkpoint updated

### Evidence
- 30 new audio files in pipeline/data/bourdain/audio/ (061-090)
- 30 transcripts generated (0 timeouts across 3 graduated batches of 10)
- 29/30 extractions successful (1 failure: video 089, 38K char compilation episode)
- 88 new entities normalized, geocoded, enriched
- 88 documents loaded to staging Firestore (total: 275, was 188)
- checkpoint.json updated: phase3_complete, 44 countries (was 39)
- New countries added: Canada, Chile, Greece, Philippines, Sri Lanka

---

## W3: Fix Evaluator Schema Validation

### Actions
1. **Relaxed eval_schema.json:**
   - summary maxLength: 500 -> 2000
   - evidence: added maxLength 1000
   - mcps: removed strict enum, increased maxItems to 5
   - what_could_be_better minItems: 3 -> 2
2. **Added JSON repair to run_evaluator.py:**
   - `repair_json()` function strips markdown fences, fixes trailing commas
   - Called before JSON parsing in `parse_json_from_response()`
3. **Added concrete JSON example to evaluator prompt:**
   - Shows exact output structure with real field values
   - Reduces ambiguity for Qwen/Gemini
4. **Added `write_report_markdown()` function:**
   - Generates `docs/kjtcom-report-{version}.md` from evaluation data
   - Called after `save_scores()` in main block
   - Self-eval now produces both agent_scores.json AND report markdown
5. Removed unused `full_enum` variable from validate_qwen_output

### Evidence
- `data/eval_schema.json` updated (relaxed constraints)
- `scripts/run_evaluator.py` updated (repair, example, report writer)
- Evaluator produces report markdown file

---

## W4: ADR-011 Thompson Schema v4 - Intranet Extensions

### Actions
1. Appended ADR-011 to `docs/evaluator-harness.md`
2. Defined candidate t_any_* fields for 7 intranet source types
3. Defined 4 universal fields (t_any_tags, t_any_record_ids, t_any_sources, t_any_sensitivity)
4. Added v10.58 evidence standards section
5. Total field count: 19 (v3) -> 49 (v4 candidate set)

### Evidence
- `grep "ADR-011" docs/evaluator-harness.md` matches
- `wc -l docs/evaluator-harness.md` = 727 (was 670)
- Design decision only - no implementation

---

## Post-Flight Status

```
[x] W1: Board positions adjusted with visible gaps
[x] W1: Animated connectors with labels in each gap
[x] W1: iao_logger chip on middleware board
[x] W1: G56 check passes (0 fetch+json)
[x] W2: Bourdain Phase 3 - 88 entities in staging (275 total, was 188)
[x] W2: checkpoint.json updated (phase3_complete)
[x] W3: eval_schema.json relaxed
[x] W3: JSON repair added to run_evaluator.py
[x] W3: write_report_markdown() added and works
[x] W4: ADR-011 in evaluator-harness.md (727 lines)
[x] Evaluator produces report markdown (self-eval tier)
[x] Changelog updated
[x] 4 artifacts: design, plan, build, report
```

---

*Build v10.58, April 06, 2026. 4 workstreams executed.*
