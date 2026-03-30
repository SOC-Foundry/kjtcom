# RickSteves - Plan v3.11 (Phase 3 - Stress Test)

**Pipeline:** ricksteves
**Phase:** 3 (Stress Test)
**Iteration:** 11 (global counter)
**Batch:** Videos 91-120 (30 new videos)
**Date:** March 2026

---

## Section A: Gemini CLI Execution (Phases 1-5)

**Launch:** `gemini --yolo`
**First message:** "Read GEMINI.md, then execute Section A of docs/ricksteves-plan-v3.11.md. You are running RickSteves phases 1-5 only for videos 91-120. Stop at the handoff checkpoint."

### Step 0: Pre-Flight Verification

```
CHECKLIST (verify each, do NOT skip):
[ ] Previous docs archived: docs/archive/ contains v3.10 artifacts
[ ] Current docs in place: docs/ricksteves-design-v3.11.md and docs/ricksteves-plan-v3.11.md exist
[ ] GEMINI.md updated with v3.11 references
[ ] Git status clean (no uncommitted changes)
[ ] API keys (print SET/NOT SET only, NEVER print values, NEVER cat config.fish):
    - fish -c "test -n \$GEMINI_API_KEY && echo SET || echo NOT SET"
    - fish -c "test -n \$GOOGLE_PLACES_API_KEY && echo SET || echo NOT SET"
    - fish -c "test -n \$GOOGLE_APPLICATION_CREDENTIALS && echo SET || echo NOT SET"
[ ] CUDA visible: fish -c "nvidia-smi | head -5"
[ ] LD_LIBRARY_PATH set: fish -c "echo \$LD_LIBRARY_PATH" (expect non-empty)
[ ] Disk space: df -h /home | tail -1 (need >50GB free)
[ ] Python deps: fish -c "python3 -c 'import faster_whisper; import google.genai; print(\"OK\")'"
[ ] Places API valid: fish -c "curl -s 'https://places.googleapis.com/v1/places:searchText' -H 'Content-Type: application/json' -H 'X-Goog-Api-Key: '\$GOOGLE_PLACES_API_KEY -H 'X-Goog-FieldMask: places.displayName' -d '{\"textQuery\": \"Colosseum Rome\"}' | head -3"
[ ] Current audio count: fish -c "command ls pipeline/data/ricksteves/audio/*.mp3 2>/dev/null | wc -l" (expect 90)
[ ] Current transcript count: fish -c "command ls pipeline/data/ricksteves/transcripts/*.json 2>/dev/null | wc -l" (expect 90)
```

**All checks must pass before proceeding. If any fail, diagnose and fix. Do NOT skip.**

### Step 1: Acquire (phase1_acquire.py)

```fish
fish -c "cd ~/dev/projects/kjtcom && python3 pipeline/scripts/phase1_acquire.py --pipeline ricksteves --start 91 --limit 30"
```

**Expected:** 30 new MP3 files. Total: 120.
**Verify:** `fish -c "command ls pipeline/data/ricksteves/audio/*.mp3 | wc -l"` -> 120
**On failure:** Check yt-dlp version. Update if needed: `fish -c "pip install -U yt-dlp --break-system-packages"`. Retry.

### Step 2: Transcribe (phase2_transcribe.py)

**CRITICAL: Gemini CLI has a 5-minute stdout timeout (G18). Run as background job.**

```fish
fish -c "cd ~/dev/projects/kjtcom && nohup python3 -u pipeline/scripts/phase2_transcribe.py --pipeline ricksteves --start 91 --limit 30 > transcribe_v3.11.log 2>&1 &"
```

**Poll for completion every 60 seconds:**
```fish
fish -c "command ls ~/dev/projects/kjtcom/pipeline/data/ricksteves/transcripts/*.json | wc -l"
```

**Expected:** Count increases from 90 to 120 over ~30 minutes (Rick Steves episodes are 30-60 min, longer than CalGold).
**Wait until count reaches 120 before proceeding.**
**NEVER start a second transcription process (G21 - CUDA OOM on 8GB VRAM).**
**On stall:** Check GPU: `fish -c "nvidia-smi"`. If GPU at 97%+, it's working. Wait. If GPU idle with count < 120, check `transcribe_v3.11.log` for errors.

### Step 3: Extract (phase3_extract.py)

```fish
fish -c "cd ~/dev/projects/kjtcom && python3 pipeline/scripts/phase3_extract.py --pipeline ricksteves --start 91 --limit 30"
```

**Expected:** 30 new JSON files in pipeline/data/ricksteves/extracted/.
**Verify:** `fish -c "command ls pipeline/data/ricksteves/extracted/*.json | wc -l"` -> 120

### Step 4: Normalize (phase4_normalize.py)

```fish
fish -c "cd ~/dev/projects/kjtcom && python3 pipeline/scripts/phase4_normalize.py --pipeline ricksteves --start 91 --limit 30"
```

**Expected:** Normalized JSONL with t_any_countries populated (multi-value for international), t_schema_version: 2.
**Verify:** `fish -c "tail -1 pipeline/data/ricksteves/normalized/normalized.jsonl | python3 -c 'import json,sys; d=json.loads(sys.stdin.readline()); print(d.get(\"t_any_countries\"), d.get(\"t_schema_version\"))'"` -> e.g. ['france'] 2

### Step 5: Geocode (phase5_geocode.py)

```fish
fish -c "cd ~/dev/projects/kjtcom && python3 pipeline/scripts/phase5_geocode.py --pipeline ricksteves --start 91 --limit 30"
```

**Expected:** >90% geocoded via Nominatim (international entities geocode better than CalGold niche California locations).
**Verify geocoding rate on new batch.**

### Handoff Checkpoint

**Produce handoff file:**
```fish
fish -c "cd ~/dev/projects/kjtcom && python3 -c \"
import json, glob
checkpoint = {
    'iteration': 'v3.11',
    'agent': 'gemini-cli',
    'phases_completed': [1,2,3,4,5],
    'audio_count': len(glob.glob('pipeline/data/ricksteves/audio/*.mp3')),
    'transcript_count': len(glob.glob('pipeline/data/ricksteves/transcripts/*.json')),
    'extracted_count': len(glob.glob('pipeline/data/ricksteves/extracted/*.json')),
    'status': 'ready_for_phase_6_7'
}
json.dump(checkpoint, open('pipeline/data/ricksteves/handoff-v3.11.json','w'), indent=2)
print(json.dumps(checkpoint, indent=2))
\""
```

**STOP HERE. Human reviews checkpoint, then launches Claude Code for phases 6-7.**

---

## Section B: Claude Code Execution (Phases 6-7 + Post-Flight)

**Launch:** `claude --dangerously-skip-permissions`
**First message:** "Read CLAUDE.md, then execute Section B of docs/ricksteves-plan-v3.11.md. Gemini CLI has completed phases 1-5. Verify the handoff checkpoint at pipeline/data/ricksteves/handoff-v3.11.json before proceeding."

### Step 6: Enrich (phase6_enrich.py)

```fish
cd ~/dev/projects/kjtcom
python3 pipeline/scripts/phase6_enrich.py --pipeline ricksteves
```

**Expected:** >95% enrichment via Google Places API (New). Coordinate backfill for any Nominatim misses.
**Note:** phase6 does NOT accept --database flag (learned in v3.10). It operates on files only.

### Step 7: Load (phase7_load.py)

```fish
python3 pipeline/scripts/phase7_load.py --pipeline ricksteves --database staging
```

**Expected:** All entities loaded with array merge. Multi-visit entities (Colosseum, Eiffel Tower, etc.) preserve all visit data from all episodes.
**Verify total RickSteves entities:** Query Firestore staging for t_log_type == "ricksteves" document count.
**Verify cross-pipeline queries:** Search for "museum" should return results from both calgold and ricksteves.

### Step 8: Post-Flight

```
CHECKLIST:
[ ] Security: grep -rnI "AIzaSy" . -> only plan checklist references
[ ] Entity count: Firestore staging ricksteves document count
[ ] Cross-pipeline: keyword search returns both pipelines
[ ] Schema: spot-check 3 new entities have t_schema_version: 2 and t_any_countries populated
[ ] Country distribution: check if any new countries were added beyond the current 29
[ ] Geocoding rate: calculate from enriched data
[ ] Enrichment rate: calculate from enriched data
```

### Step 9: Produce Artifacts

**All 4 mandatory artifacts:**

1. **docs/ricksteves-build-v3.11.md** - Session transcript with timing. Include both Gemini Section A summary and Claude Section B detail.
2. **docs/ricksteves-report-v3.11.md** - Metrics table (Phase 1 vs Phase 2 vs Phase 3 vs Cumulative), agent comparison, recommendation for Phase 4.
3. **docs/kjtcom-changelog.md** - Append v3.11 entry at top.
4. **README.md** - Update Project Status table, Pipelines table (entity count, status), Changelog section.

**Artifact format rules:**
- No em-dashes (use -- or hyphens)
- Dates in ISO format
- Entity counts must match Firestore actuals
- Report must include interventions count for each agent separately

---

## Timing Estimate

| Phase | Agent | Est. Duration |
|-------|-------|---------------|
| Step 0 (pre-flight) | Gemini | ~3 min |
| Step 1 (acquire 30) | Gemini | ~5 min |
| Step 2 (transcribe 30) | Gemini | ~30 min |
| Step 3 (extract 30) | Gemini | ~5 min |
| Step 4 (normalize) | Gemini | ~1 min |
| Step 5 (geocode) | Gemini | ~3 min |
| Handoff review | Human | ~5 min |
| Step 6 (enrich) | Claude | ~5 min |
| Step 7 (load) | Claude | ~3 min |
| Step 8-9 (post-flight + artifacts) | Claude | ~5 min |
| **Total** | **Split** | **~65 min** |
