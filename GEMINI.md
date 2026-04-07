# GEMINI.md — kjtcom Agent Harness (Gemini CLI)

**Launch:** `gemini --yolo` then `Read GEMINI.md and execute 10.62`
**Repo:** SOC-Foundry/kjtcom
**Site:** kylejeromethompson.com
**Firebase:** kjtcom-c78cd (Blaze)
**Shell:** Gemini runs bash. Wrap fish with `fish -c "..."` (G19).
**Executor:** Gemini CLI (full iteration — app, middleware, pipeline)

---

## RULES

1. **NEVER** `git commit`, `git push`. All git = Kyle only.
2. **NEVER** heredocs. `printf` only (G1).
3. **NEVER** `cat ~/.config/fish/config.fish` — Gemini has leaked API keys doing this.
4. **NEVER** simultaneous GPU. Graduated tmux, unload Ollama first (G18).
5. Gemini runs bash by default. Use `fish -c "..."` for fish-specific commands (G19).
6. Use `command ls` to avoid color code pollution (G22).
7. Read ENTIRE files before editing. `grep` all related patterns.
8. **4 ARTIFACTS EVERY ITERATION.** design + plan (INPUT, immutable) + build + report (OUTPUT). The executing agent MUST produce `docs/kjtcom-build-v{X.XX}.md` and `docs/kjtcom-report-v{X.XX}.md` before marking complete. If `generate_artifacts.py` fails, write them manually. **No iteration ends without build + report on disk.**
9. Post-flight MANDATORY. `10/10` prohibited. Harness never shrinks.
10. **G56:** Claw3D data inline. Never fetch() JSON.
11. **G58:** Design/plan immutable during execution. `generate_artifacts.py` must skip them.
12. **G59:** Canvas texture labels. Min font 11px. Truncate label if it doesn't fit at 11px — don't shrink below 11px.
13. Component review every iteration.
14. Do NOT use `--start` flag on pipeline scripts. They use checkpoint resume.

---

## PROJECT STATE

| Pipeline | t_log_type | Color | Entities | Status |
|----------|-----------|-------|----------|--------|
| California's Gold | calgold | #DA7E12 | 899 | Production |
| Rick Steves' Europe | ricksteves | #3B82F6 | 4,182 | Production |
| Diners Drive-Ins and Dives | tripledb | #DD3333 | 1,100 | Production |
| Anthony Bourdain (NR) | bourdain | #8B5CF6 | 351 | Staging (114/114) |
| Anthony Bourdain (PU) | bourdain | #8B5CF6 | 0 | **Parts Unknown Phase 1 (this iteration)** |

**Total:** 6,181 production + 351 staging. Harness: 874 lines, 13 ADRs.

---

## AGENTS

| Agent | Role |
|-------|------|
| Gemini CLI | **Primary executor this iteration** — all 5 workstreams |
| Qwen3.5-9B | Evaluator (local Ollama, post-pipeline) |
| Gemini Flash | Extraction API, evaluator fallback |

**Evaluator fallback:** Qwen (3) → Gemini Flash (2) → self-eval (cap 7/10)

---

## GOTCHAS

| ID | Title | Workaround |
|----|-------|------------|
| G1 | Heredocs | printf only |
| G18 | CUDA OOM RTX 2080 SUPER | Graduated tmux, unload Ollama first |
| G19 | Gemini runs bash | `fish -c "..."` for fish commands |
| G22 | ls color codes | `command ls` |
| G34 | Firestore array-contains | Client-side post-filter |
| G53 | Firebase MCP reauth | Retry wrapper |
| G56 | Claw3D fetch() 404 | Resolved v10.57 — inline data only |
| G58 | Agent overwrites design/plan | Resolved v10.60 — immutability guard |
| G59 | Chip text overflow | Canvas textures v10.61, **font too small — raise min to 11px** |
| **G60** | **Map tab: 0 mapped of 6,181** | **NEW — markers not rendering, was working v9.31** |
| **G61** | **Build/report not generated** | **NEW — v10.61 completed but no build/report on disk** |

**CRITICAL Gemini-specific:** NEVER run `cat ~/.config/fish/config.fish` — leaked API keys in past sessions.

---

## v10.62 WORKSTREAMS

### W1: Fix Map Tab — 0 Mapped Regression (P0)

**Problem:** Map tab shows "0 mapped of 6181 results." Entities exist in Firestore with coordinates but no markers render on the OpenStreetMap. Was confirmed working in v9.31 via Playwright screenshot.

#### Step 1: Read the map widget

```bash
command ls app/lib/widgets/ | grep -i map
wc -l app/lib/widgets/map_tab.dart
cat app/lib/widgets/map_tab.dart
```

#### Step 2: Trace the data path

```bash
grep -n "provider\|ref.watch\|ref.read" app/lib/widgets/map_tab.dart
grep -rn "t_any_coordinates\|coordinates" app/lib/providers/
```

#### Step 3: Sample a real entity

```bash
python3 -c "
import firebase_admin
from firebase_admin import credentials, firestore
firebase_admin.initialize_app()
db = firestore.client()
docs = db.collection('locations').limit(3).get()
for doc in docs:
    data = doc.to_dict()
    coords = data.get('t_any_coordinates', 'MISSING')
    print(f'{doc.id[:20]}: t_any_coordinates={str(coords)[:120]}')
"
```

#### Step 4: Check flutter_map version + git history

```bash
grep "flutter_map" app/pubspec.yaml
git log --oneline -- app/pubspec.yaml | head -10
git log --oneline -- app/lib/widgets/map_tab.dart | head -10
```

#### Step 5: Apply the fix

**Most likely cause: flutter_map 7→8 API change.** In flutter_map 8.x, `Marker.builder` was renamed to `child`:

```dart
// OLD (flutter_map 7.x):
Marker(
  point: LatLng(coord.lat, coord.lon),
  builder: (ctx) => Icon(Icons.location_on, color: pipelineColor),
)

// NEW (flutter_map 8.x):
Marker(
  point: LatLng(coord.lat, coord.lon),
  child: Icon(Icons.location_on, color: pipelineColor),
)
```

**Other possible cause: field name mismatch** (`lat`/`lon` vs `lat`/`lng`). Check what the Firestore sample shows and align the map widget accordingly.

#### Step 6: Build and deploy

```bash
fish -c "cd app && flutter analyze"
fish -c "cd app && flutter build web"
fish -c "firebase deploy --only hosting"
```

#### Step 7: Verify

Open kylejeromethompson.com → Map tab. Markers should render. Header should show count > 0. Take screenshot via Playwright MCP if available.

**Evidence:** Marker count > 0, screenshot, coordinate field contract documented.

---

### W2: Claw3D — Readable Font Size (P1)

**Problem:** v10.61 canvas texture `measureText` auto-shrink loop has `fontSize > 6` as floor. At 6px on a 64px-per-unit canvas, text is unreadable. Fix: raise floor to 11px, truncate label if it still doesn't fit, bump canvas resolution to 96px/unit.

#### Step 1: Locate createChipTexture

```bash
grep -n "createChipTexture\|measureText\|fs > 6" app/web/claw3d.html
```

#### Step 2: Apply the patch

Replace the createChipTexture function with:

```javascript
function createChipTexture(label, status, w, h) {
    const canvas = document.createElement('canvas');
    const res = 96;  // BUMP from 64 → 96 for sharper text
    canvas.width = w * res;
    canvas.height = h * res;
    const ctx = canvas.getContext('2d');
    
    // Background
    ctx.fillStyle = '#1F2937';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Border
    ctx.strokeStyle = status === 'active' ? '#4ADE80' :
                      status === 'degraded' ? '#EF9F27' : '#555';
    ctx.lineWidth = 2;
    ctx.strokeRect(1, 1, canvas.width - 2, canvas.height - 2);
    
    // Label — auto-shrink to 11px floor, then truncate
    ctx.fillStyle = '#C9D1D9';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    let displayLabel = label;
    let fs = 16;
    ctx.font = fs + 'px monospace';
    while (ctx.measureText(displayLabel).width > canvas.width - 12 && fs > 11) {
        fs--;
        ctx.font = fs + 'px monospace';
    }
    // If still doesn't fit at 11px, truncate the label with '..'
    if (ctx.measureText(displayLabel).width > canvas.width - 12) {
        while (ctx.measureText(displayLabel + '..').width > canvas.width - 12 
               && displayLabel.length > 3) {
            displayLabel = displayLabel.slice(0, -1);
        }
        displayLabel = displayLabel + '..';
    }
    ctx.fillText(displayLabel, canvas.width / 2, canvas.height / 2);
    
    // LED dot
    ctx.beginPath();
    ctx.arc(canvas.width - 10, 10, 5, 0, Math.PI * 2);
    ctx.fillStyle = status === 'active' ? '#4ADE80' :
                    status === 'degraded' ? '#EF9F27' : '#555';
    ctx.fill();
    
    const tex = new THREE.CanvasTexture(canvas);
    tex.needsUpdate = true;
    return tex;
}
```

#### Step 3: Update version string to v10.62

Find the title and iterations dropdown. Update v10.61 → v10.62.

#### Step 4: Verify and deploy

```bash
grep -c "fetch.*\.json" app/web/claw3d.html  # Must be 0 (G56)
grep "fs > 11" app/web/claw3d.html  # Must match
grep "res = 96" app/web/claw3d.html  # Must match

fish -c "cd app && flutter build web"
fish -c "firebase deploy --only hosting"
```

**Evidence:** Screenshot of Claw3D — all chip labels readable, no text below 11px, long labels end with `..`.

---

### W3: Fix Build/Report Generation Enforcement (P1)

**Problem:** v10.61 completed all workstreams, passed 15/15 post-flight, but produced no `docs/kjtcom-build-v10.61.md` or `docs/kjtcom-report-v10.61.md`. The iteration has no audit trail.

#### Step 1: Diagnose

```bash
grep -A2 "IMMUTABLE_ARTIFACTS" scripts/generate_artifacts.py
command ls docs/kjtcom-*-v10.61.md 2>/dev/null
command ls docs/drafts/kjtcom-*-v10.61.md 2>/dev/null
grep -n "build\|report\|artifact" scripts/post_flight.py
```

#### Step 2: Fix immutability list if it accidentally blocks build/report

```python
# scripts/generate_artifacts.py — must be EXACTLY this:
IMMUTABLE_ARTIFACTS = ["design", "plan"]
```

If it contains `"build"` or `"report"`, remove them.

#### Step 3: Add post-flight artifact existence check

Append to `scripts/post_flight.py`:

```python
import os, sys

def check_artifacts(iteration):
    failures = []
    for atype in ["build", "report"]:
        path = f"docs/kjtcom-{atype}-{iteration}.md"
        if not os.path.exists(path):
            failures.append(f"FAIL: {path} missing — iteration has no {atype} artifact")
            continue
        size = os.path.getsize(path)
        if size < 100:
            failures.append(f"FAIL: {path} too small ({size} bytes)")
            continue
        print(f"PASS: {atype} artifact exists ({path}, {size} bytes)")
    return failures

artifact_failures = check_artifacts(iteration)
if artifact_failures:
    for f in artifact_failures:
        print(f)
    sys.exit(1)
```

#### Step 4: Produce retroactive v10.61 build + report

Write `docs/kjtcom-build-v10.61.md` documenting:
- W1: Parts Unknown — DEFERRED (Gemini CLI workstream not executed in v10.61)
- W2: GCP portability plan — `docs/gcp-portability-plan.md` created with 4 sections
- W3: Canvas texture rewrite — `createChipTexture()` in `app/web/claw3d.html`, OpenClaw added, 49 chips across 4 boards, G56=0
- W4: Harness updates — ADR-013, Pattern 18, component review section, harness 761→874 lines

Write `docs/kjtcom-report-v10.61.md` with scores:
- W1: 0/10 deferred
- W2: 8/10 (comprehensive plan)
- W3: 7/10 (text inside chips but font too small — G59 partial)
- W4: 8/10 (874 lines, 13 ADRs, 18 patterns)

Update `agent_scores.json` with v10.61 entry.

**Evidence:**
- `IMMUTABLE_ARTIFACTS = ["design", "plan"]` confirmed
- Post-flight has artifact existence checks
- v10.61 build + report files exist on disk
- agent_scores.json has v10.61 entry

---

### W4: Component Review + Harness Update (P2)

**Rule 13 requires component review every iteration.**

#### Step 1: Audit components

```bash
command ls scripts/*.py | sed 's|scripts/||;s|.py$||'
cat .mcp.json 2>/dev/null | python3 -c "import sys, json; d=json.load(sys.stdin); print('\n'.join(d.get('mcpServers', {}).keys()))" 2>/dev/null
ollama list 2>/dev/null

# New components since v10.61?
git log --since="2 days ago" --name-only -- scripts/ | grep -E "scripts/.+\.py$" | sort -u
```

If new components found, add them to the Claw3D middleware chip list.

#### Step 2: Append Pattern 19 to harness

```markdown
### Pattern 19: Iteration completes without build/report artifacts (G61)

- **Failure:** Agent runs all workstreams, passes post-flight, but generate_artifacts.py is never called or silently skips build/report
- **Impact:** Iteration has no audit trail. Scores lost. Cannot evaluate retroactively without filesystem archaeology.
- **Detection:** Post-flight file existence + minimum size check
- **Prevention:** Post-flight FAILS if either kjtcom-build-v{X.XX}.md or kjtcom-report-v{X.XX}.md missing or under 100 bytes
- **Resolution:** Reconstruct from execution log + filesystem evidence
```

**Evidence:** `wc -l docs/evaluator-harness.md` > 874. Pattern 19 present.

---

### W5: Parts Unknown Pipeline — Phase 1 (P1)

**This is Gemini's specialty. Pipeline work, Phases 1-5.** First 30 videos of the second Bourdain show.

**Playlist:** `https://www.youtube.com/watch?v=6PQB1S5sZQ0&list=PLfLND2Lym9knKTVU7lHYROAGWmTH2kEFo`
**Machine:** NZXTcos (GPU required)
**Pipeline:** Existing `bourdain` (single pipeline, multi-show via `t_any_shows`)

#### Step 1: Count playlist size

```bash
yt-dlp --flat-playlist --print "%(playlist_index)s %(title)s" \
  "https://www.youtube.com/watch?v=6PQB1S5sZQ0&list=PLfLND2Lym9knKTVU7lHYROAGWmTH2kEFo" | wc -l
```

#### Step 2: Acquire first 30 (with `pu_` prefix)

```bash
yt-dlp --playlist-items 1-30 -x --audio-format mp3 \
  -o "pipeline/data/bourdain/audio/pu_%(playlist_index)03d_%(title)s.%(ext)s" \
  "https://www.youtube.com/watch?v=6PQB1S5sZQ0&list=PLfLND2Lym9knKTVU7lHYROAGWmTH2kEFo"
```

The `pu_` prefix distinguishes Parts Unknown files from existing No Reservations files.

#### Step 3: Unload Ollama (G18)

```bash
curl -s http://localhost:11434/api/generate -d '{"model":"qwen3.5:9b","keep_alive":0}'
sleep 5
nvidia-smi  # Verify VRAM freed
```

#### Step 4: Transcribe (graduated tmux, SEQUENTIAL)

```bash
# Batch 1: pu_001-pu_010
python3 -u scripts/phase2_transcribe.py --pipeline bourdain --pattern "pu_00*" --timeout 600
# Wait, then batch 2: pu_011-pu_020
python3 -u scripts/phase2_transcribe.py --pipeline bourdain --pattern "pu_01*" --timeout 600
# Wait, then batch 3: pu_021-pu_030
python3 -u scripts/phase2_transcribe.py --pipeline bourdain --pattern "pu_02*" --timeout 600
```

#### Step 5: Update extraction prompt for Parts Unknown

Edit `pipeline/config/bourdain/extraction_prompt.md` (or pass a flag) so entities from `pu_*` files get:
```json
"t_any_shows": ["Parts Unknown"]
```

Existing No Reservations entities keep `t_any_shows: ["No Reservations"]`.

#### Step 6: Extract → Normalize → Geocode → Enrich → Load

```bash
python3 -u scripts/phase3_extract.py --pipeline bourdain --filter "pu_*"
python3 -u scripts/phase4_normalize.py --pipeline bourdain
python3 -u scripts/phase5_geocode.py --pipeline bourdain
python3 -u scripts/phase6_enrich.py --pipeline bourdain
python3 -u scripts/phase7_load.py --pipeline bourdain --database staging
```

**DO NOT load to production. Staging only.**

**Dedup against existing 351 entities.** Locations appearing in both shows get merged `t_any_shows` arrays: `["No Reservations", "Parts Unknown"]`.

#### Step 7: Update checkpoint

```bash
python3 -c "
import json, os
path = 'pipeline/data/bourdain/parts_unknown_checkpoint.json'
cp = json.load(open(path)) if os.path.exists(path) else {}
cp['phase'] = 1
cp['videos_acquired'] = 30
cp['show'] = 'Parts Unknown'
json.dump(cp, open(path, 'w'), indent=2)
"
```

**Evidence:** Entity count increase, `t_any_shows` correctly set, checkpoint updated, dedup verified.

---

## EXECUTION ORDER

1. **W5: Parts Unknown Phase 1** (start first, longest, 3-4 hours GPU work) — NZXTcos
2. **W1: Map tab fix** (P0) — runs while transcription churns — NZXTcos or tsP3-cos
3. **W2: Claw3D font fix** (P1) — quick — same machine as W1
4. **W3: Build/report enforcement** (P1) — fix the meta-problem
5. **W4: Component review + harness** (P2) — closes the loop
6. **MANDATORY:** Post-flight passes including new artifact existence checks
7. **MANDATORY:** `docs/kjtcom-build-v10.62.md` and `docs/kjtcom-report-v10.62.md` exist on disk

---

## POST-FLIGHT + REPORT

```bash
# Post-flight (must include new artifact existence check)
python3 scripts/post_flight.py 10.62

# Archive v10.61 (including retroactive artifacts)
mkdir -p docs/archive
cp docs/kjtcom-design-v10.61.md docs/archive/ 2>/dev/null
cp docs/kjtcom-plan-v10.61.md docs/archive/ 2>/dev/null
cp docs/kjtcom-build-v10.61.md docs/archive/ 2>/dev/null
cp docs/kjtcom-report-v10.61.md docs/archive/ 2>/dev/null

# Update changelog (append v10.62 entry)

# Run evaluator with rich context
python3 -u scripts/run_evaluator.py --iteration v10.62 --verbose

# HARD VERIFICATION
test -f docs/kjtcom-build-v10.62.md && echo "BUILD EXISTS" || echo "BUILD MISSING — FAIL"
test -f docs/kjtcom-report-v10.62.md && echo "REPORT EXISTS" || echo "REPORT MISSING — FAIL"
wc -l docs/kjtcom-build-v10.62.md docs/kjtcom-report-v10.62.md
```

If evaluator fails all 3 tiers, write the report manually based on build log evidence. **The iteration cannot end without both files on disk.**

---

## COMPLETION CHECKLIST

```
[ ] W1: Map tab shows markers (count > 0)
[ ] W1: Coordinate field contract documented
[ ] W2: Claw3D labels readable (min 11px)
[ ] W2: Long labels truncated with '..'
[ ] W2: Canvas resolution 96px/unit
[ ] W2: G56=0 still passing
[ ] W3: IMMUTABLE_ARTIFACTS = ["design", "plan"] only
[ ] W3: Post-flight checks build+report file existence
[ ] W3: docs/kjtcom-build-v10.61.md exists (retroactive)
[ ] W3: docs/kjtcom-report-v10.61.md exists (retroactive)
[ ] W3: agent_scores.json has v10.61 entry
[ ] W4: Component review pass complete
[ ] W4: Pattern 19 in harness
[ ] W4: Harness > 874 lines
[ ] W5: Parts Unknown Phase 1 entities in staging (30 videos)
[ ] W5: t_any_shows: ["Parts Unknown"] verified
[ ] W5: Dedup tested (multi-show merge)
[ ] W5: parts_unknown_checkpoint.json updated
[ ] docs/kjtcom-build-v10.62.md EXISTS ON DISK (size > 100)
[ ] docs/kjtcom-report-v10.62.md EXISTS ON DISK (size > 100)
[ ] Post-flight passes ALL checks including artifact existence
[ ] v10.61 archived to docs/archive/
[ ] Changelog updated with v10.62
[ ] No git operations performed (Rule 1)
```

---

*GEMINI.md v10.62, April 06, 2026. Primary executor: Gemini CLI. 5 workstreams. Map fix, Claw3D font, build/report enforcement, component review, Parts Unknown Phase 1.*
