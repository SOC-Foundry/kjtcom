# CalGold - Plan v5.14 (Phase 5 - Production Run)

**Pipeline:** calgold
**Phase:** 5 (Production Run)
**Iteration:** 14 (global counter)
**Batch:** Videos 121-431 (~311 remaining)
**Date:** March 2026

---

## Section A: Runner Script Setup (One-Time)

Create `pipeline/scripts/group_b_runner.sh`:

```bash
#!/usr/bin/env bash
# group_b_runner.sh -- Graduated production run for kjtcom pipelines.
# Usage: ./pipeline/scripts/group_b_runner.sh PIPELINE [TIMEOUT_SECONDS]
# Default timeout: 600
#
# Run in tmux:
#   tmux new -s calgold './pipeline/scripts/group_b_runner.sh calgold 600 2>&1 | tee pipeline/data/calgold/logs/prod_5.14_600s.log'

set -euo pipefail
cd "$(dirname "$0")/../.."  # Navigate to repo root (kjtcom/)

PIPELINE=${1:?Usage: group_b_runner.sh PIPELINE [TIMEOUT]}
TIMEOUT=${2:-600}
TOTAL_START=$(date +%s)
LOG_DIR="pipeline/data/${PIPELINE}/logs"
mkdir -p "$LOG_DIR"

echo "=========================================="
echo "kjtcom Production Run"
echo "Pipeline: ${PIPELINE}"
echo "Timeout: ${TIMEOUT}s"
echo "Started: $(date)"
echo "=========================================="

# -- Kill any GPU-hogging processes --
pkill -f "ollama" 2>/dev/null || true
sleep 2
nvidia-smi --query-compute-apps=pid --format=csv,noheader 2>/dev/null | while read pid; do
    if [ -n "$pid" ]; then
        echo "WARNING: GPU process $pid still running, killing..."
        kill "$pid" 2>/dev/null || true
    fi
done
sleep 2

# -- Ensure LD_LIBRARY_PATH is set --
export LD_LIBRARY_PATH="/usr/local/lib/ollama/mlx_cuda_v13:/usr/local/lib/ollama/cuda_v12:${LD_LIBRARY_PATH:-}"

# -- Phase 1: Acquire --
echo ""
echo "=== Phase 1: Acquire ==="
python3 pipeline/scripts/phase1_acquire.py --pipeline "$PIPELINE" --limit 0
PHASE1_END=$(date +%s)
echo "Acquire complete: $(date) ($(( (PHASE1_END - TOTAL_START) / 60 )) min)"

# -- Phase 2: Transcribe --
echo ""
echo "=== Phase 2: Transcribe (timeout: ${TIMEOUT}s) ==="
TRANSCRIBE_TIMEOUT=$TIMEOUT python3 -u pipeline/scripts/phase2_transcribe.py --pipeline "$PIPELINE" --limit 0
PHASE2_END=$(date +%s)
echo "Transcribe complete: $(date) ($(( (PHASE2_END - PHASE1_END) / 60 )) min)"

# -- Phase 3: Extract --
echo ""
echo "=== Phase 3: Extract ==="
python3 pipeline/scripts/phase3_extract.py --pipeline "$PIPELINE" --limit 0
PHASE3_END=$(date +%s)
echo "Extract complete: $(date) ($(( (PHASE3_END - PHASE2_END) / 60 )) min)"

# -- Phase 4: Normalize --
echo ""
echo "=== Phase 4: Normalize ==="
python3 pipeline/scripts/phase4_normalize.py --pipeline "$PIPELINE" --limit 0
PHASE4_END=$(date +%s)
echo "Normalize complete: $(date) ($(( (PHASE4_END - PHASE3_END) / 60 )) min)"

# -- Phase 5: Geocode --
echo ""
echo "=== Phase 5: Geocode ==="
python3 pipeline/scripts/phase5_geocode.py --pipeline "$PIPELINE" --limit 0
PHASE5_END=$(date +%s)
echo "Geocode complete: $(date) ($(( (PHASE5_END - PHASE4_END) / 60 )) min)"

# -- Summary --
TOTAL_END=$(date +%s)
ELAPSED_MIN=$(( (TOTAL_END - TOTAL_START) / 60 ))
ELAPSED_HR=$(( ELAPSED_MIN / 60 ))

echo ""
echo "=========================================="
echo "Production Run Complete"
echo "Pipeline: ${PIPELINE}"
echo "Timeout: ${TIMEOUT}s"
echo "Finished: $(date)"
echo "Total runtime: ${ELAPSED_HR}h ${ELAPSED_MIN}m"
echo "=========================================="
echo ""
echo "Counts:"
echo "  Audio files:  $(ls pipeline/data/${PIPELINE}/audio/*.mp3 2>/dev/null | wc -l)"
echo "  Transcripts:  $(ls pipeline/data/${PIPELINE}/transcripts/*.json 2>/dev/null | wc -l)"
echo "  Extractions:  $(ls pipeline/data/${PIPELINE}/extracted/*.json 2>/dev/null | wc -l)"
echo "  Normalized:   $(ls pipeline/data/${PIPELINE}/normalized/*.jsonl 2>/dev/null | wc -l)"
echo "  Geocoded:     $(ls pipeline/data/${PIPELINE}/geocoded/*.jsonl 2>/dev/null | wc -l)"
echo ""
echo "NEXT: Review log, then relaunch with higher timeout or proceed to Phase 6-7."
```

### Pre-Requisite: Verify Timeout Env Vars

Before first launch, confirm the scripts respect `TRANSCRIBE_TIMEOUT`:

```bash
grep -n "TRANSCRIBE_TIMEOUT\|signal.alarm\|timeout" pipeline/scripts/phase2_transcribe.py
```

Should show `TRANSCRIBE_TIMEOUT` being read from env. If hardcoded, update:

```python
timeout_seconds = int(os.environ.get("TRANSCRIBE_TIMEOUT", "600"))
```

Also check extract timeout:

```bash
grep -n "EXTRACT_TIMEOUT\|timeout" pipeline/scripts/phase3_extract.py
```

### Make Runner Executable

```bash
chmod +x pipeline/scripts/group_b_runner.sh
bash -n pipeline/scripts/group_b_runner.sh && echo "Syntax OK"
```

---

## Section B: Pass 1 -- 600s Timeout (Clips + Regular Episodes)

**Expected:** Processes ~250-280 of ~311 remaining videos (everything under ~20 min audio)
**Runtime:** ~8-12 hours

### Launch

```fish
cd ~/dev/projects/kjtcom
mkdir -p pipeline/data/calgold/logs
tmux new -s calgold './pipeline/scripts/group_b_runner.sh calgold 600 2>&1 | tee pipeline/data/calgold/logs/prod_5.14_600s.log'
```

### Monitor (from another terminal)

```fish
# Attach to watch live
tmux attach -t calgold

# Or check counts without attaching
echo "Audio: "(ls pipeline/data/calgold/audio/*.mp3 | wc -l)
echo "Trans: "(ls pipeline/data/calgold/transcripts/*.json | wc -l)
echo "Extra: "(ls pipeline/data/calgold/extracted/*.json | wc -l)

# Check GPU utilization
nvidia-smi

# Check for errors
grep -c "ERROR\|FAIL\|error\|timed out" pipeline/data/calgold/logs/prod_5.14_600s.log
```

### After Completion

```fish
# Review results
tail -50 pipeline/data/calgold/logs/prod_5.14_600s.log

# Count processed
echo "Audio:    "(command ls pipeline/data/calgold/audio/*.mp3 | wc -l)
echo "Trans:    "(command ls pipeline/data/calgold/transcripts/*.json | wc -l)
echo "Extract:  "(command ls pipeline/data/calgold/extracted/*.json | wc -l)

# Count timeouts
grep -c "timed out\|Timed out\|TIMEOUT" pipeline/data/calgold/logs/prod_5.14_600s.log

# Commit checkpoint
cd ~/dev/projects/kjtcom
git add pipeline/scripts/group_b_runner.sh docs/
git commit -m "KT 5.14 pass 1 complete (600s) - $(command ls pipeline/data/calgold/transcripts/*.json | wc -l) transcripts"
git push
```

---

## Section C: Pass 2 -- 1200s Timeout (Longer Episodes)

**Expected:** Processes ~20-40 videos that timed out in pass 1
**Runtime:** ~4-8 hours

### Launch

```fish
cd ~/dev/projects/kjtcom
tmux new -s calgold './pipeline/scripts/group_b_runner.sh calgold 1200 2>&1 | tee pipeline/data/calgold/logs/prod_5.14_1200s.log'
```

### After Completion

```fish
tail -50 pipeline/data/calgold/logs/prod_5.14_1200s.log
echo "Trans:    "(command ls pipeline/data/calgold/transcripts/*.json | wc -l)
echo "Extract:  "(command ls pipeline/data/calgold/extracted/*.json | wc -l)
grep -c "timed out" pipeline/data/calgold/logs/prod_5.14_1200s.log

git add .
git commit -m "KT 5.14 pass 2 complete (1200s)"
git push
```

---

## Section D: Pass 3 -- 1800s Timeout (Marathons)

**Expected:** Processes ~5-10 remaining marathon videos
**Runtime:** ~2-4 hours

### Launch

```fish
cd ~/dev/projects/kjtcom
tmux new -s calgold './pipeline/scripts/group_b_runner.sh calgold 1800 2>&1 | tee pipeline/data/calgold/logs/prod_5.14_1800s.log'
```

### After Completion

```fish
tail -50 pipeline/data/calgold/logs/prod_5.14_1800s.log
echo "Trans:    "(command ls pipeline/data/calgold/transcripts/*.json | wc -l)
echo "Extract:  "(command ls pipeline/data/calgold/extracted/*.json | wc -l)

# Identify any remaining unprocessed
python3 -c "
import os
audio = set(f.replace('.mp3','') for f in os.listdir('pipeline/data/calgold/audio') if f.endswith('.mp3'))
extracted = set(f.replace('.json','') for f in os.listdir('pipeline/data/calgold/extracted') if f.endswith('.json'))
missing = audio - extracted
print(f'Total audio: {len(audio)}')
print(f'Extracted: {len(extracted)}')
print(f'Missing: {len(missing)}')
for m in sorted(missing)[:20]:
    print(f'  {m}')
"

git add .
git commit -m "KT 5.14 pass 3 complete (1800s)"
git push
```

Any videos still unprocessed after 1800s are genuine edge cases (4+ hour marathons or broken audio). Document them as gaps and move on.

---

## Section E: Quality Sweep

After all 3 passes, run normalize and geocode across the FULL dataset:

```fish
cd ~/dev/projects/kjtcom

# Re-normalize all (catches any stragglers)
python3 pipeline/scripts/phase4_normalize.py --pipeline calgold --limit 0

# Re-geocode all
python3 pipeline/scripts/phase5_geocode.py --pipeline calgold --limit 0

# Quality report
python3 -c "
import json, os, glob

files = glob.glob('pipeline/data/calgold/geocoded/*.jsonl')
total_entities = 0
geocoded = 0
schema_v3 = 0
has_actors = 0
has_continents = 0

for f in files:
    for line in open(f):
        e = json.loads(line)
        total_entities += 1
        if e.get('t_any_coordinates'): geocoded += 1
        if e.get('t_schema_version') == 3: schema_v3 += 1
        if e.get('t_any_actors'): has_actors += 1
        if e.get('t_any_continents'): has_continents += 1

print(f'=== CALGOLD PRODUCTION QUALITY REPORT ===')
print(f'Total geocoded files: {len(files)}')
print(f'Total entities: {total_entities}')
print(f'Geocoded: {geocoded} ({geocoded*100//total_entities}%)')
print(f'Schema v3: {schema_v3} ({schema_v3*100//total_entities}%)')
print(f'Has actors: {has_actors} ({has_actors*100//total_entities}%)')
print(f'Has continents: {has_continents} ({has_continents*100//total_entities}%)')
" | tee pipeline/data/calgold/logs/quality_report_5.14.txt
```

---

## Section F: Claude Code Execution (Phases 6-7 + Artifacts)

**Launch:** `claude --dangerously-skip-permissions`

```
Read CLAUDE.md, then execute Section F of docs/calgold-plan-v5.14.md.

All CalGold videos have been processed through phases 1-5 via tmux production runs.
Review the quality report at pipeline/data/calgold/logs/quality_report_5.14.txt.

Reset enrichment and load checkpoints (G24/G25):
  rm pipeline/data/calgold/.checkpoint_enrich.json
  rm pipeline/data/calgold/.checkpoint_load.json

Then run phase 6 (enrich) and phase 7 (load) for the FULL CalGold dataset.
Produce all 4 mandatory artifacts.
Report total entity count, geocoding rate, enrichment rate, and any gaps.

Security: grep -rnI "AIzaSy" . before signaling completion.
Do NOT git commit or push.
```

### Step 6: Enrich ALL

```fish
cd ~/dev/projects/kjtcom
python3 pipeline/scripts/phase6_enrich.py --pipeline calgold
```

**Note:** phase6 does NOT accept --database flag (file I/O only).

### Step 7: Load ALL

```fish
python3 pipeline/scripts/phase7_load.py --pipeline calgold --database staging
```

**Checkpoint paths (G25):** `.checkpoint_enrich.json` and `.checkpoint_load.json` in `pipeline/data/calgold/` root.

### Step 8: Post-Flight

```
CHECKLIST:
[ ] Security: grep -rnI "AIzaSy" . -> only doc references
[ ] Total CalGold entities in staging (target: ~431 videos worth)
[ ] All entities at t_schema_version: 3
[ ] Geocoding rate >95%
[ ] Enrichment rate >95%
[ ] Cross-pipeline search returns both calgold and ricksteves
```

### Step 9: Produce Artifacts

1. **docs/calgold-build-v5.14.md** -- include all 3 tmux pass summaries (timing, counts, timeouts), quality sweep results, enrich/load stats
2. **docs/calgold-report-v5.14.md** -- full Phase 1-5 cumulative metrics, production throughput stats, recommendation for RickSteves Phase 5
3. **docs/kjtcom-changelog.md** -- append v5.14 at top
4. **README.md** -- update status table (Phase 5 DONE for CalGold), entity counts, changelog. Use this phase structure:

```
| Phase | Name                                | Status     | Iteration         |
|-------|-------------------------------------|------------|-------------------|
| 0     | Scaffold & Environment              | DONE       | v0.5              |
| 1     | Discovery (30 videos)               | DONE       | v1.6, v1.7        |
| 2     | Calibration (60 videos)             | DONE       | v2.8, v2.9        |
| 3     | Stress Test (90 videos)             | DONE       | v3.10, v3.11      |
| 4     | Validation + Schema v3 (120 videos) | DONE       | v4.12, v4.13      |
| 5     | Production Run (full datasets)      | CalGold DONE | v5.14            |
| 6     | Flutter App                         | Pending    | -                 |
| 7     | Firestore Load                      | Pending    | -                 |
| 8     | Enrichment Hardening                | Pending    | -                 |
| 9     | App Optimization                    | Pending    | -                 |
| 10    | Retrospective + Template            | Pending    | -                 |
```

---

## CLAUDE.md for v5.14

```markdown
# kjtcom - Agent Instructions (Claude Code)

## Read Order

1. docs/calgold-design-v5.14.md
2. docs/calgold-plan-v5.14.md (execute Section F only -- tmux completed Sections A-E)

## Context

CalGold Phase 5 production run. Phases 1-5 were executed via tmux (unattended, no agent).
You are running phases 6-7 (enrich, load) for the FULL CalGold dataset (~431 videos).

CRITICAL: Reset checkpoints before running phases 6-7.
Actual checkpoint paths (G25):
  pipeline/data/calgold/.checkpoint_enrich.json
  pipeline/data/calgold/.checkpoint_load.json

## Shell - MANDATORY

- claude config set preferredShell fish (one-time)
- All commands in fish shell
- NEVER cat config.fish (G20)

## Security

- grep -rnI "AIzaSy" . before completion
- Print only SET/NOT SET for key checks

## Enrichment Note

- phase6_enrich.py does NOT accept --database flag
- phase7_load.py DOES accept --database staging

## Permissions

- CANNOT: git add / commit / push
- CANNOT: sudo

## Database Rules

- Load to "staging" only
- fetch-and-merge for array fields

## Artifact Rules - MANDATORY

1. docs/calgold-build-v5.14.md (include tmux pass summaries + enrich/load detail)
2. docs/calgold-report-v5.14.md (Phase 1-5 cumulative, production throughput)
3. docs/kjtcom-changelog.md (append v5.14 at top)
4. README.md (Phase 5 CalGold DONE, updated entity counts, correct phase structure)

## Formatting

- No em-dashes. Use " - " instead.
- Use "->" for arrows.
```

---

## Between-Pass Checklist

After each tmux pass:

```
[ ] Review log: tail -100 pipeline/data/calgold/logs/prod_5.14_XXXs.log
[ ] Count transcripts: command ls pipeline/data/calgold/transcripts/*.json | wc -l
[ ] Count extractions: command ls pipeline/data/calgold/extracted/*.json | wc -l
[ ] Check errors: grep -c "ERROR\|FAIL" pipeline/data/calgold/logs/prod_5.14_XXXs.log
[ ] Check timeouts: grep -c "timed out" pipeline/data/calgold/logs/prod_5.14_XXXs.log
[ ] Commit: git add . && git commit -m "KT 5.14 pass N complete" && git push
[ ] Launch next pass (if needed)
```

---

## Timing Estimate

| Pass | Timeout | Expected Videos | Runtime |
|------|---------|-----------------|---------|
| Pass 1 | 600s | ~250-280 | 8-12 hours |
| Pass 2 | 1200s | ~20-40 | 4-8 hours |
| Pass 3 | 1800s | ~5-10 | 2-4 hours |
| Quality sweep | N/A | All | ~30 min |
| Enrich + load (Claude) | N/A | All | ~1-2 hours |
| **Total** | | **~311 videos** | **~24-36 hours** |
