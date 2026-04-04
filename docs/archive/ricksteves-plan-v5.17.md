# RickSteves - Plan v5.17 (Phase 5 - Production Run)

**Pipeline:** ricksteves
**Phase:** 5 (Production Run)
**Iteration:** 17 (global counter)
**Batch:** Videos 151-1865 (~1,715 remaining)
**Date:** March-April 2026

---

## Section A: Pre-Flight (One-Time)

The runner script `group_b_runner.sh` already exists from v5.14. No setup needed.

### Verify Runner

```fish
cd ~/dev/projects/kjtcom
bash -n pipeline/scripts/group_b_runner.sh && echo "Syntax OK"
```

### Verify Environment

```fish
# Disk space (need >100GB free for ~1,715 audio files + transcripts)
df -h /home | tail -1

# CUDA
nvidia-smi | head -5

# Current counts (should be 150 from v4.13)
echo "Audio:    "(command ls pipeline/data/ricksteves/audio/*.mp3 | wc -l)
echo "Trans:    "(command ls pipeline/data/ricksteves/transcripts/*.json | wc -l)
echo "Extract:  "(command ls pipeline/data/ricksteves/extracted/*.json | wc -l)
```

### Archive Previous Docs

```fish
mv docs/ricksteves-*.md docs/archive/ 2>/dev/null
cp ~/Downloads/ricksteves-design-v5.17.md docs/
cp ~/Downloads/ricksteves-plan-v5.17.md docs/
git add docs/
git commit -m "KT 5.17 docs in place"
git push
```

---

## Section B: Pass 1 - 600s Timeout (Standard Episodes)

**Expected:** ~1,200-1,400 of ~1,715 remaining videos (standard 25-min episodes)
**Runtime:** ~5-7 days (continuous, with auto-restart for OOM recovery)

### Auto-Restart Wrapper

CalGold hit CUDA OOM after ~109 videos due to VRAM fragmentation. At 1,715 videos, expect ~10-15 OOM crashes. This wrapper auto-restarts after each crash. Checkpoints skip already-processed videos.

```fish
cd ~/dev/projects/kjtcom
mkdir -p pipeline/data/ricksteves/logs
```

Launch in tmux with auto-restart:

```fish
tmux new -s ricksteves 'cd ~/dev/projects/kjtcom && while true; do echo "=== LAUNCH $(date) ===" >> pipeline/data/ricksteves/logs/prod_5.17_600s.log; ./pipeline/scripts/group_b_runner.sh ricksteves 600 2>&1 | tee -a pipeline/data/ricksteves/logs/prod_5.17_600s.log; EXIT_CODE=$?; if [ $EXIT_CODE -eq 0 ]; then echo "Runner completed successfully"; break; fi; echo "Runner exited with code $EXIT_CODE, restarting in 60s..."; sleep 60; done'
```

### Monitor (from another terminal)

```fish
# Attach to watch live
tmux attach -t ricksteves

# Quick counts without attaching
echo "Audio: "(command ls pipeline/data/ricksteves/audio/*.mp3 | wc -l)
echo "Trans: "(command ls pipeline/data/ricksteves/transcripts/*.json | wc -l)
echo "Extra: "(command ls pipeline/data/ricksteves/extracted/*.json | wc -l)

# Check GPU
nvidia-smi

# Count OOM restarts
grep -c "LAUNCH\|OOM\|CUDA failed" pipeline/data/ricksteves/logs/prod_5.17_600s.log

# Check last 20 lines
tail -20 pipeline/data/ricksteves/logs/prod_5.17_600s.log
```

### Daily Check-In

Since Pass 1 runs for multiple days, do a quick status check each day:

```fish
echo "=== Daily Status $(date) ==="
echo "Audio:    "(command ls pipeline/data/ricksteves/audio/*.mp3 | wc -l)
echo "Trans:    "(command ls pipeline/data/ricksteves/transcripts/*.json | wc -l)
echo "Extract:  "(command ls pipeline/data/ricksteves/extracted/*.json | wc -l)
echo "OOM restarts: "(grep -c "LAUNCH" pipeline/data/ricksteves/logs/prod_5.17_600s.log)
echo "Errors: "(grep -c "ERROR\|FAIL" pipeline/data/ricksteves/logs/prod_5.17_600s.log)
echo "Timeouts: "(grep -c "timed out\|TIMEOUT" pipeline/data/ricksteves/logs/prod_5.17_600s.log)
df -h /home | tail -1
```

### After Pass 1 Completes (runner exits cleanly)

```fish
tail -50 pipeline/data/ricksteves/logs/prod_5.17_600s.log

echo "Audio:    "(command ls pipeline/data/ricksteves/audio/*.mp3 | wc -l)
echo "Trans:    "(command ls pipeline/data/ricksteves/transcripts/*.json | wc -l)
echo "Extract:  "(command ls pipeline/data/ricksteves/extracted/*.json | wc -l)

grep -c "timed out\|Timed out\|TIMEOUT" pipeline/data/ricksteves/logs/prod_5.17_600s.log
grep -c "LAUNCH" pipeline/data/ricksteves/logs/prod_5.17_600s.log

git add .
git commit -m "KT 5.17 pass 1 complete (600s) - $(command ls pipeline/data/ricksteves/transcripts/*.json | wc -l) transcripts"
git push
```

---

## Section C: Pass 2 - 1200s Timeout (Longer Specials)

**Expected:** ~200-400 videos that timed out in Pass 1
**Runtime:** ~1-2 days

### Launch

```fish
cd ~/dev/projects/kjtcom
tmux new -s ricksteves 'cd ~/dev/projects/kjtcom && while true; do echo "=== LAUNCH $(date) ===" >> pipeline/data/ricksteves/logs/prod_5.17_1200s.log; ./pipeline/scripts/group_b_runner.sh ricksteves 1200 2>&1 | tee -a pipeline/data/ricksteves/logs/prod_5.17_1200s.log; EXIT_CODE=$?; if [ $EXIT_CODE -eq 0 ]; then echo "Runner completed successfully"; break; fi; echo "Runner exited with code $EXIT_CODE, restarting in 60s..."; sleep 60; done'
```

### After Completion

```fish
tail -50 pipeline/data/ricksteves/logs/prod_5.17_1200s.log
echo "Trans:    "(command ls pipeline/data/ricksteves/transcripts/*.json | wc -l)
echo "Extract:  "(command ls pipeline/data/ricksteves/extracted/*.json | wc -l)
grep -c "timed out" pipeline/data/ricksteves/logs/prod_5.17_1200s.log

git add .
git commit -m "KT 5.17 pass 2 complete (1200s)"
git push
```

---

## Section D: Pass 3 - 1800s Timeout (Marathons)

**Expected:** ~50-100 remaining marathon/compilation videos
**Runtime:** ~12-24 hours

### Launch

```fish
cd ~/dev/projects/kjtcom
tmux new -s ricksteves 'cd ~/dev/projects/kjtcom && while true; do echo "=== LAUNCH $(date) ===" >> pipeline/data/ricksteves/logs/prod_5.17_1800s.log; ./pipeline/scripts/group_b_runner.sh ricksteves 1800 2>&1 | tee -a pipeline/data/ricksteves/logs/prod_5.17_1800s.log; EXIT_CODE=$?; if [ $EXIT_CODE -eq 0 ]; then echo "Runner completed successfully"; break; fi; echo "Runner exited with code $EXIT_CODE, restarting in 60s..."; sleep 60; done'
```

### After Completion

```fish
tail -50 pipeline/data/ricksteves/logs/prod_5.17_1800s.log
echo "Trans:    "(command ls pipeline/data/ricksteves/transcripts/*.json | wc -l)
echo "Extract:  "(command ls pipeline/data/ricksteves/extracted/*.json | wc -l)

# Identify any remaining unprocessed
python3 -c "
import os
audio = set(f.replace('.mp3','') for f in os.listdir('pipeline/data/ricksteves/audio') if f.endswith('.mp3'))
extracted = set(f.replace('.json','') for f in os.listdir('pipeline/data/ricksteves/extracted') if f.endswith('.json'))
missing = audio - extracted
print(f'Total audio: {len(audio)}')
print(f'Extracted: {len(extracted)}')
print(f'Missing: {len(missing)}')
for m in sorted(missing)[:20]:
    print(f'  {m}')
"

git add .
git commit -m "KT 5.17 pass 3 complete (1800s)"
git push
```

Any videos still unprocessed after 1800s are genuine edge cases (4+ hour compilations or broken audio). Document as gaps and move on.

---

## Section E: Quality Sweep

After all passes complete, re-normalize and re-geocode the FULL dataset:

```fish
cd ~/dev/projects/kjtcom

python3 pipeline/scripts/phase4_normalize.py --pipeline ricksteves --limit 0
python3 pipeline/scripts/phase5_geocode.py --pipeline ricksteves --limit 0

# Quality report
python3 -c "
import json, os, glob

files = glob.glob('pipeline/data/ricksteves/geocoded/*.jsonl')
total_entities = 0
geocoded = 0
schema_v3 = 0
has_actors = 0
has_continents = 0
countries = set()

for f in files:
    for line in open(f):
        e = json.loads(line)
        total_entities += 1
        if e.get('t_any_coordinates'): geocoded += 1
        if e.get('t_schema_version') == 3: schema_v3 += 1
        if e.get('t_any_actors'): has_actors += 1
        if e.get('t_any_continents'): has_continents += 1
        for c in e.get('t_any_countries', []):
            countries.add(c)

print(f'=== RICKSTEVES PRODUCTION QUALITY REPORT ===')
print(f'Total geocoded files: {len(files)}')
print(f'Total entities: {total_entities}')
print(f'Geocoded: {geocoded} ({geocoded*100//max(total_entities,1)}%)')
print(f'Schema v3: {schema_v3} ({schema_v3*100//max(total_entities,1)}%)')
print(f'Has actors: {has_actors} ({has_actors*100//max(total_entities,1)}%)')
print(f'Has continents: {has_continents} ({has_continents*100//max(total_entities,1)}%)')
print(f'Countries: {len(countries)}')
print(f'Country list: {sorted(countries)[:20]}...')
" | tee pipeline/data/ricksteves/logs/quality_report_5.17.txt
```

---

## Section F: Claude Code Execution (Phases 6-7 + Artifacts)

**Launch:** `claude --dangerously-skip-permissions`

```
Read CLAUDE.md, then execute Section F of docs/ricksteves-plan-v5.17.md.

All RickSteves videos have been processed through phases 1-5 via tmux production runs.
Review the quality report at pipeline/data/ricksteves/logs/quality_report_5.17.txt.

Reset enrichment and load checkpoints (G24/G25):
  rm pipeline/data/ricksteves/.checkpoint_enrich.json
  rm pipeline/data/ricksteves/.checkpoint_load.json

Then run phase 6 (enrich) and phase 7 (load) for the FULL RickSteves dataset.
Produce all 4 mandatory artifacts.
Report total entity count, geocoding rate, enrichment rate, country count, and any gaps.

Security: grep -rnI "AIzaSy" . before signaling completion.
Do NOT git commit or push.
```

### Step 6: Enrich ALL

```fish
cd ~/dev/projects/kjtcom
python3 pipeline/scripts/phase6_enrich.py --pipeline ricksteves
```

**Note:** phase6 does NOT accept --database flag (file I/O only).

### Step 7: Load ALL

```fish
python3 pipeline/scripts/phase7_load.py --pipeline ricksteves --database staging
```

**Checkpoint paths (G25):** `.checkpoint_enrich.json` and `.checkpoint_load.json` in `pipeline/data/ricksteves/` root.

### Step 8: Post-Flight

```
CHECKLIST:
[ ] Security: grep -rnI "AIzaSy" . -> only doc references
[ ] Total RickSteves entities in staging (target: significantly more than 1,035)
[ ] All entities at t_schema_version: 3
[ ] Geocoding rate >95%
[ ] Enrichment rate >95%
[ ] Country count (was 33 at v4.13, expect 40+)
[ ] Cross-pipeline search returns both calgold and ricksteves
[ ] Total platform entities (CalGold 899 + RickSteves new total)
```

### Step 9: Produce Artifacts

1. **docs/ricksteves-build-v5.17.md** - include all tmux pass summaries (timing, counts, OOM restarts, timeouts), quality sweep results, enrich/load stats
2. **docs/ricksteves-report-v5.17.md** - full Phase 1-5 cumulative metrics, production throughput stats, comparison to CalGold v5.14
3. **docs/kjtcom-changelog.md** - append v5.17 at top
4. **README.md** - update status table (Phase 5 DONE for RickSteves), entity counts, changelog. Use this phase structure:

```
| Phase | Name                                | Status     | Iteration         |
|-------|-------------------------------------|------------|-------------------|
| 0     | Scaffold & Environment              | DONE       | v0.5              |
| 1     | Discovery (30 videos)               | DONE       | v1.6, v1.7        |
| 2     | Calibration (60 videos)             | DONE       | v2.8, v2.9        |
| 3     | Stress Test (90 videos)             | DONE       | v3.10, v3.11      |
| 4     | Validation + Schema v3 (120 videos) | DONE       | v4.12, v4.13      |
| 5     | Production Run (full datasets)      | DONE       | v5.14, v5.17      |
| 6     | Flutter App                         | IN PROGRESS | v6.15, v6.16     |
| 7     | Firestore Load                      | Pending    | -                 |
| 8     | Enrichment Hardening                | Pending    | -                 |
| 9     | App Optimization                    | Pending    | -                 |
| 10    | Retrospective + Template            | Pending    | -                 |
```

---

## CLAUDE.md for v5.17

```markdown
# kjtcom - Agent Instructions (Claude Code)

## Read Order

1. docs/ricksteves-design-v5.17.md
2. docs/ricksteves-plan-v5.17.md (execute Section F only - tmux completed Sections A-E)

## Context

RickSteves Phase 5 production run. Phases 1-5 were executed via tmux (unattended, auto-restart wrapper).
You are running phases 6-7 (enrich, load) for the FULL RickSteves dataset (~1,865 videos).

CRITICAL: Reset checkpoints before running phases 6-7.
Actual checkpoint paths (G25):
  pipeline/data/ricksteves/.checkpoint_enrich.json
  pipeline/data/ricksteves/.checkpoint_load.json

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

1. docs/ricksteves-build-v5.17.md (include all tmux pass summaries + enrich/load detail)
2. docs/ricksteves-report-v5.17.md (Phase 1-5 cumulative, production throughput, CalGold comparison)
3. docs/kjtcom-changelog.md (append v5.17 at top)
4. README.md (Phase 5 DONE for both pipelines, updated entity counts, correct phase structure)

## Formatting

- No em-dashes. Use " - " instead.
- Use "->" for arrows.
```

---

## Between-Pass Checklist

After each tmux pass completes:

```
[ ] Review log: tail -100 pipeline/data/ricksteves/logs/prod_5.17_XXXs.log
[ ] Count transcripts: command ls pipeline/data/ricksteves/transcripts/*.json | wc -l
[ ] Count extractions: command ls pipeline/data/ricksteves/extracted/*.json | wc -l
[ ] Check errors: grep -c "ERROR\|FAIL" pipeline/data/ricksteves/logs/prod_5.17_XXXs.log
[ ] Check timeouts: grep -c "timed out" pipeline/data/ricksteves/logs/prod_5.17_XXXs.log
[ ] Check OOM restarts: grep -c "LAUNCH" pipeline/data/ricksteves/logs/prod_5.17_XXXs.log
[ ] Check disk space: df -h /home | tail -1
[ ] Commit: git add . && git commit -m "KT 5.17 pass N complete" && git push
[ ] Pull on P3 if needed: git pull (before frontend commits)
[ ] Launch next pass (if needed)
```

---

## Concurrent Frontend Development

While tmux runs on NZXTcos:
- **NZXTcos:** tmux production runs (pipeline/data/ricksteves/). Between-pass git commits.
- **P3:** Flutter frontend development (app/). Regular git commits.
- **Conflict avoidance:** Frontend work touches app/. Pipeline work touches pipeline/ and docs/. No overlap.
- **Before committing on either machine:** `git pull` first.
- **If conflict occurs:** Pipeline data files are gitignored. Only docs/ could conflict - resolve manually.
