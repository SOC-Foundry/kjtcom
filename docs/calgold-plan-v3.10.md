# CalGold - Plan v3.10 (Phase 3 - Stress Test)

**Pipeline:** calgold
**Phase:** 3 (Stress Test)
**Iteration:** 10 (global counter)
**Batch:** Videos 61-90 (30 new videos)
**Date:** March 2026

---

## Section A: Gemini CLI Execution (Phases 1-5)

**Launch:** `gemini --sandbox=none --yolo`
**First message:** "Read GEMINI.md, then execute Section A of docs/calgold-plan-v3.10.md."

### Step 0: Pre-Flight Verification

```
CHECKLIST (verify each, do NOT skip):
[ ] Previous docs archived: docs/archive/ contains v2.8 and v2.9 artifacts
[ ] Current docs in place: docs/calgold-design-v3.10.md and docs/calgold-plan-v3.10.md exist
[ ] GEMINI.md updated with v3.10 references
[ ] Git status clean (no uncommitted changes)
[ ] API keys (print SET/NOT SET only, NEVER print values, NEVER cat config.fish):
    - fish -c "test -n \$GEMINI_API_KEY && echo SET || echo NOT SET"
    - fish -c "test -n \$GOOGLE_PLACES_API_KEY && echo SET || echo NOT SET"
    - fish -c "test -n \$GOOGLE_APPLICATION_CREDENTIALS && echo SET || echo NOT SET"
[ ] CUDA visible: fish -c "nvidia-smi | head -5"
[ ] LD_LIBRARY_PATH set: fish -c "echo \$LD_LIBRARY_PATH" (expect non-empty)
[ ] Disk space: df -h /home | tail -1 (need >50GB free)
[ ] Python deps: fish -c "python3 -c 'import faster_whisper; import google.genai; print(\"OK\")'"
[ ] Places API valid: fish -c "curl -s 'https://places.googleapis.com/v1/places:searchText' -H 'Content-Type: application/json' -H 'X-Goog-Api-Key: '\$GOOGLE_PLACES_API_KEY -H 'X-Goog-FieldMask: places.displayName' -d '{\"textQuery\": \"Watts Towers Los Angeles\"}' | head -3"
[ ] Current audio count: fish -c "command ls pipeline/data/calgold/audio/*.mp3 2>/dev/null | wc -l" (expect 60)
[ ] Current transcript count: fish -c "command ls pipeline/data/calgold/transcripts/*.json 2>/dev/null | wc -l" (expect 60)
```

**All checks must pass before proceeding. If any fail, diagnose and fix. Do NOT skip.**

### Step 1: Acquire (phase1_acquire.py)

```fish
fish -c "cd ~/dev/projects/kjtcom && python3 pipeline/scripts/phase1_acquire.py --pipeline calgold --start 61 --limit 30"
```

**Expected:** 30 new MP3 files in `pipeline/data/calgold/audio/`. Total: 90.
**Verify:** `fish -c "command ls pipeline/data/calgold/audio/*.mp3 | wc -l"` → 90
**On failure:** Check yt-dlp version (`yt-dlp --version`). Update if needed (`pip install -U yt-dlp --break-system-packages`). Retry.

### Step 2: Transcribe (phase2_transcribe.py)

**CRITICAL: Gemini CLI has a 5-minute stdout timeout (G18). Run transcription as a background job.**

```fish
fish -c "cd ~/dev/projects/kjtcom && nohup python3 -u pipeline/scripts/phase2_transcribe.py --pipeline calgold --start 61 --limit 30 > transcribe_v3.10.log 2>&1 &"
```

**Poll for completion every 60 seconds:**
```fish
fish -c "command ls ~/dev/projects/kjtcom/pipeline/data/calgold/transcripts/*.json | wc -l"
```

**Expected:** Count increases from 60 to 90 over ~20 minutes (30 videos, shorter CalGold episodes).
**Wait until count reaches 90 before proceeding.**
**NEVER start a second transcription process (G21 - CUDA OOM on 8GB VRAM).**
**On stall:** Check GPU: `fish -c "nvidia-smi"`. If GPU at 97%+, it's working. Wait. If GPU idle with count < 90, check `transcribe_v3.10.log` for errors.

### Step 3: Extract (phase3_extract.py)

```fish
fish -c "cd ~/dev/projects/kjtcom && python3 pipeline/scripts/phase3_extract.py --pipeline calgold --start 61 --limit 30"
```

**Expected:** 30 new JSON files in `pipeline/data/calgold/extracted/`.
**Verify:** `fish -c "command ls pipeline/data/calgold/extracted/*.json | wc -l"` → 90
**Spot-check:** `fish -c "python3 -c \"import json; d=json.load(open('pipeline/data/calgold/extracted/'+(import os; os.listdir('pipeline/data/calgold/extracted/'))[60])); print(len(d.get('locations',[])), 'entities')\""` → should be 1-10 entities.

### Step 4: Normalize (phase4_normalize.py)

```fish
fish -c "cd ~/dev/projects/kjtcom && python3 pipeline/scripts/phase4_normalize.py --pipeline calgold --start 61 --limit 30"
```

**Expected:** Normalized JSONL with all t_any_* fields populated, t_any_countries: ["us"], t_schema_version: 2.
**Verify:** `fish -c "head -1 pipeline/data/calgold/normalized/normalized.jsonl | python3 -c 'import json,sys; d=json.loads(sys.stdin.readline()); print(d.get(\"t_any_countries\"), d.get(\"t_schema_version\"))'"` → `['us'] 2`

### Step 5: Geocode (phase5_geocode.py)

```fish
fish -c "cd ~/dev/projects/kjtcom && python3 pipeline/scripts/phase5_geocode.py --pipeline calgold --start 61 --limit 30"
```

**Expected:** >95% geocoded via Nominatim. Misses will be backfilled in Phase 6.
**Verify geocoding rate:** `fish -c "python3 -c \"import json; lines=open('pipeline/data/calgold/geocoded/geocoded.jsonl').readlines()[-30:]; geo=[l for l in lines if json.loads(l).get('t_any_coordinates')]; print(f'{len(geo)}/30 geocoded ({len(geo)*100//30}%)')\""

### Handoff Checkpoint

**Produce handoff file:**
```fish
fish -c "cd ~/dev/projects/kjtcom && python3 -c \"
import json
checkpoint = {
    'iteration': 'v3.10',
    'agent': 'gemini-cli',
    'phases_completed': [1,2,3,4,5],
    'audio_count': len(__import__('glob').glob('pipeline/data/calgold/audio/*.mp3')),
    'transcript_count': len(__import__('glob').glob('pipeline/data/calgold/transcripts/*.json')),
    'extracted_count': len(__import__('glob').glob('pipeline/data/calgold/extracted/*.json')),
    'status': 'ready_for_phase_6_7'
}
json.dump(checkpoint, open('pipeline/data/calgold/handoff-v3.10.json','w'), indent=2)
print(json.dumps(checkpoint, indent=2))
\""
```

**STOP HERE. Human reviews checkpoint, then launches Claude Code for phases 6-7.**

---

## Section B: Claude Code Execution (Phases 6-7 + Post-Flight)

**Launch:** `claude --dangerously-skip-permissions`
**First message:** "Read CLAUDE.md, then execute Section B of docs/calgold-plan-v3.10.md. Gemini CLI has completed phases 1-5. Verify the handoff checkpoint at pipeline/data/calgold/handoff-v3.10.json before proceeding."

### Step 6: Enrich (phase6_enrich.py)

```fish
cd ~/dev/projects/kjtcom
python3 pipeline/scripts/phase6_enrich.py --pipeline calgold --database staging
```

**Expected:** >95% enrichment via Google Places API (New). Coordinate backfill for Nominatim misses.
**Verify:** Check enrichment rate and coordinate backfill stats in script output.

### Step 7: Load (phase7_load.py)

```fish
python3 pipeline/scripts/phase7_load.py --pipeline calgold --database staging
```

**Expected:** All entities loaded with array merge (fetch-and-merge, not overwrite). Multi-visit entities preserve all visit data.
**Verify total entities:** Query Firestore staging for `t_log_type == "calgold"` document count. Expect ~248+ (218 existing + new unique entities minus dedup merges).
**Verify cross-pipeline queries:** Search for "museum" should return results from both calgold and ricksteves.

### Step 8: Post-Flight

```
CHECKLIST:
[ ] Security: grep -rnI "AIzaSy" . → only plan checklist references (this file)
[ ] Entity count: Firestore staging calgold document count
[ ] Cross-pipeline: keyword search returns both pipelines
[ ] Schema: spot-check 3 new entities have t_schema_version: 2 and t_any_countries: ["us"]
[ ] Geocoding rate: calculate from enriched data
[ ] Enrichment rate: calculate from enriched data
```

### Step 9: Produce Artifacts

**All 4 mandatory artifacts:**

1. **docs/calgold-build-v3.10.md** - Session transcript with timing, commands, errors, resolutions. Include both Gemini and Claude sections.
2. **docs/calgold-report-v3.10.md** - Metrics table (Phase 2 vs Phase 3 vs Cumulative), agent comparison (Gemini phases 1-5 vs Claude phases 6-7), recommendation for Phase 4.
3. **docs/kjtcom-changelog.md** - Append v3.10 entry at top.
4. **README.md** - Update Project Status table, Pipelines table (entity count), Changelog section.

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
| Step 2 (transcribe 30) | Gemini | ~15 min |
| Step 3 (extract 30) | Gemini | ~5 min |
| Step 4 (normalize) | Gemini | ~1 min |
| Step 5 (geocode) | Gemini | ~3 min |
| Handoff review | Human | ~5 min |
| Step 6 (enrich) | Claude | ~5 min |
| Step 7 (load) | Claude | ~3 min |
| Step 8-9 (post-flight + artifacts) | Claude | ~5 min |
| **Total** | **Split** | **~50 min** |
