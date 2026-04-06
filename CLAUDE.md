# CLAUDE.md — kjtcom Agent Harness (Claude Code)

**Launch:** `read claude and execute 10.60`
**Repo:** SOC-Foundry/kjtcom
**Site:** kylejeromethompson.com
**Firebase:** kjtcom-c78cd (Blaze)
**Shell:** fish + tmux on NZXTcos and tsP3-cos

---

## RULES

1. **NEVER** `git commit`, `git push`. All git = Kyle only.
2. **NEVER** heredocs. `printf` only (G1). `command ls` (G22). `fish -c` wrappers (G19).
3. **NEVER** simultaneous GPU. Graduated tmux, unload Ollama first (G18).
4. Read ENTIRE files before editing. `grep` all related patterns across `app/`.
5. 4 artifacts per iteration. Post-flight MANDATORY. `10/10` prohibited. Harness never shrinks.
6. **REPORTS MANDATORY.** Fallback: Qwen → Gemini → self-eval. No empty scorecards.
7. **G56: ALL Claw3D data INLINE. NEVER fetch() external JSON.**
8. **G57: Qwen needs more context, not tighter rules.**
9. **G58: DESIGN AND PLAN DOCS ARE IMMUTABLE DURING EXECUTION.**
   - Design doc and plan doc are INPUT artifacts written by the planning session (Claude chat)
   - The executing agent (Claude Code or Gemini CLI) reads them — NEVER rewrites them
   - The executing agent produces ONLY the build log and report
   - `generate_artifacts.py` must SKIP design and plan docs if they already exist
   - If the agent overwrites design/plan docs, the iteration is compromised
   - Build log = agent's record of what happened. Report = evaluator's assessment.
   - Design doc = what was planned. Plan doc = how to execute. These are READ-ONLY.

---

## PROJECT STATE

| Pipeline | t_log_type | Color | Entities | Status |
|----------|-----------|-------|----------|--------|
| California's Gold | calgold | #DA7E12 | 899 | Production |
| Rick Steves' Europe | ricksteves | #3B82F6 | 4,182 | Production |
| Diners Drive-Ins and Dives | tripledb | #DD3333 | 1,100 | Production |
| Anthony Bourdain | bourdain | #8B5CF6 | 351 | **Staging (Phase 4 complete, 114/114 videos)** |

**Total:** 6,181 production + 351 staging. Bourdain playlist COMPLETE.

---

## AGENTS

| Agent | Role |
|-------|------|
| Claude Code | Executor: app, middleware, docs (Phases 6-7) |
| Gemini CLI | Executor: pipeline (Phases 1-5) |
| Qwen3.5-9B | Evaluator (local Ollama) |
| Gemini Flash | Intent routing, extraction, evaluator fallback |

**Evaluator fallback:** Qwen (3) → Gemini (2) → self-eval (cap 7/10)

---

## GOTCHAS

| ID | Title | Status |
|----|-------|--------|
| G1 | Heredocs | Active |
| G18 | CUDA OOM | Active |
| G53 | Firebase MCP reauth | Recurring |
| G56 | Claw3D fetch() 404 | Resolved v10.57 |
| G57 | Qwen needs context not rules | Active — rich context added v10.59 |
| **G58** | **Agent overwrites design/plan docs** | **NEW — generate_artifacts.py must skip existing design/plan** |

---

## v10.60 WORKSTREAMS

### W1: Fix generate_artifacts.py — G58 Artifact Immutability (P0)

**Problem:** In v10.59, Gemini CLI's `generate_artifacts.py` overwrote the design and plan docs that were carefully authored in the planning session. The design doc lost its Mermaid trident, detailed workstream specs, and v10.58 post-mortem. The plan doc lost the 10 IAO pillars, detailed execution steps, and pre-flight checklist. This destroys the audit trail.

**Root cause:** `generate_artifacts.py` generates ALL 4 artifacts (design, plan, build, report) unconditionally. It should only generate build and report. Design and plan are INPUT artifacts.

**Fix `scripts/generate_artifacts.py`:**
```python
# At the top of the generation loop, add:
IMMUTABLE_ARTIFACTS = ["design", "plan"]
for artifact_type in ["design", "plan", "build", "report"]:
    output_path = f"docs/kjtcom-{artifact_type}-{iteration}.md"
    if artifact_type in IMMUTABLE_ARTIFACTS and os.path.exists(output_path):
        print(f"[ARTIFACT] SKIP {artifact_type} — already exists (immutable, G58)")
        continue
    # ... generate only build and report
```

**Also fix `run_evaluator.py` self-eval build log path:**
The v10.59 self-eval scored 0/10 on all workstreams with "No build log evidence found." The build log exists at `docs/kjtcom-build-v10.59.md` but the self-eval function looked in the wrong place or ran before the build log was written.

Diagnose:
```bash
grep -n "build.*log\|build.*path\|kjtcom-build" scripts/run_evaluator.py
grep -n "build.*log\|build.*path\|kjtcom-build" scripts/generate_artifacts.py
```

The self-eval function must:
1. Read the build log from `docs/kjtcom-build-{iteration}.md`
2. Parse workstream sections (look for `## W1:`, `## W2:`, etc. OR `### W1:` headings)
3. If build log doesn't exist yet, check `docs/drafts/` as fallback
4. If neither exists, note "build log not yet written" but still score based on filesystem evidence (check if files changed, entity counts, etc.)

**Restore v10.59 original design and plan docs:**
The original docs are the ones uploaded to this conversation. Copy them back:
```bash
# The originals from the planning session need to be restored
# Kyle will provide them or they can be reconstructed from GEMINI.md
```

**Evidence:**
- `generate_artifacts.py` has the immutability check
- Running `generate_artifacts.py` with existing design/plan docs prints "SKIP"
- Self-eval finds build log evidence and scores > 0

---

### W2: Produce Accurate v10.59 Report (P1)

**The v10.59 report is wrong.** It scored 0/10 on all 4 workstreams despite the build log showing:
- W1: 351 Bourdain entities (114 videos, Phase 4 complete, nested array fix)
- W2: Claw3D chips widened, labels shortened, deployed
- W3: `build_rich_context()` added, fuzzy name matching improved
- W4: README at 759 lines, 4 pipelines, PCB architecture, 11 ADRs

**Produce a corrected report** based on the actual build log evidence. Score honestly:
- W1: 8/10 — all 114 videos processed, 351 entities, nested array fix was a real contribution, 1 video skip (089 compilation)
- W2: 7/10 — labels shortened, chips widened, but need to verify readability at live URL
- W3: 7/10 — rich context implemented, fuzzy matching added, but Qwen/Gemini still failed schema validation (self-eval triggered)
- W4: 8/10 — 759 lines, comprehensive, all required sections present

**Save as `docs/kjtcom-report-v10.59-corrected.md` and also update `agent_scores.json`** with the corrected scores.

---

### W3: Restore Original v10.59 Design + Plan Docs (P1)

**The originals were uploaded to this chat session.** They are the authoritative versions.

The original design doc (from our planning session) contained:
- v10.58 post-mortem with specific metrics
- Detailed workstream specs referencing GEMINI.md
- Trident targets with specific metrics
- 4-board PCB context

The original plan doc contained:
- Mermaid trident chart (graph BT with shaft/prong classDefs)
- All 10 IAO pillars (verbatim)
- Pre-flight checklist
- Detailed 5-step execution sequence with timing estimates
- Post-flight + report verification steps
- Full completion checklist

Restore these from the uploaded files (they're in `kjtcom-design-v10.59.md` and `kjtcom-plan-v10.59.md` as uploaded to this session, which are the originals from our planning session — NOT the overwritten versions from Gemini).

**If the originals can't be recovered from git:** Reconstruct from the GEMINI.md content which was not overwritten (GEMINI.md is the launch artifact and was read-only during execution).

---

### W4: Evaluator Harness — G58 ADR + Pattern (P2)

**Append to `docs/evaluator-harness.md`:**

1. **ADR-012: Artifact Immutability**
```
### ADR-012: Artifact Immutability During Execution
- **Context:** In v10.59, generate_artifacts.py overwrote the design and plan docs
  authored during the planning session. The design doc lost its Mermaid trident,
  detailed specs, and post-mortem. The plan doc lost the 10 pillars, execution
  steps, and pre-flight checklist.
- **Decision:** Design and plan docs are INPUT artifacts. They are immutable once
  the iteration begins. The executing agent produces only the build log and report.
  generate_artifacts.py must check for existing design/plan files and skip them.
- **Rationale:** The planning session (Claude chat + human review) produces the spec.
  The execution session (Claude Code or Gemini CLI) implements it. Mixing authorship
  destroys the separation of concerns and the audit trail. The design doc is the
  "what was planned" record. The build log is the "what actually happened" record.
  Overwriting the plan with a summary of what happened collapses these into one.
- **Consequences:** generate_artifacts.py gains an immutability check. CLAUDE.md and
  GEMINI.md must state this rule explicitly. The evaluator checks for artifact
  integrity as part of post-flight.
```

2. **Pattern 17: Agent overwrites input artifacts (G58)**
```
- **Failure:** generate_artifacts.py regenerates all 4 artifacts unconditionally
- **Impact:** Design and plan docs lose planning-session content (trident, pillars, specs)
- **Prevention:** Immutability check in generate_artifacts.py. Post-flight verifies
  design/plan docs haven't been modified since iteration start.
```

**Evidence:** ADR-012 present, Pattern 17 present, `wc -l` shows growth (currently 727).

---

### W5: Claw3D — Horizontal Gap Between FE and PL Boards (P1)

### W5: Claw3D — All Components Must Fit Inside Their Board (P1)

**Problem:** Chip labels and chips still overflow their parent board boundaries. Every chip label must fit inside its chip box, and every chip must fit inside its board border. Nothing should spill outside its containing rectangle.

**Requirements:**
1. **Chip labels inside chip boxes.** If a label is too wide, truncate further. Full name lives in hover tooltip — the on-board label just needs to be identifiable. Max 8 chars on small boards (FE/PL), max 10 on large boards (MW/BE).
2. **All chips inside their board.** The chip grid must fit entirely within the board border. If too many chips, enlarge the board OR shrink chips.
3. **Board titles inside boards.** "Frontend", "Pipeline", "Middleware", "Backend" must sit inside the top edge, not floating above.
4. **FE and PL horizontal gap.** Push FE left (x=-3.8) and PL right (x=3.8) so they're visually distinct. They both connect down to MW — no direct FE↔PL connection.

**HTML overlay text clamping:**
```css
.chip-label {
    font: 10px monospace;
    color: #C9D1D9;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 70px;
    text-align: center;
    pointer-events: none;
}
```

**Chip grid layout — compute before placing:**
```javascript
function layoutChips(board) {
    const chipW = 1.2, chipH = 0.6;
    const gapX = 0.3, gapZ = 0.4;
    const padX = 0.5, padZ = 0.8;
    const usableW = board.size[0] - 2 * padX;
    const cols = Math.floor((usableW + gapX) / (chipW + gapX));
    const rows = Math.ceil(board.chips.length / cols);
    // Verify rows * (chipH + gapZ) <= board.size[1] - 2*padZ
}
```

**Bounds check after placement:**
```javascript
board.chips.forEach(chip => {
    const cx = chip.mesh.position.x, cz = chip.mesh.position.z;
    console.assert(
        cx - 0.6 >= boardLeft && cx + 0.6 <= boardRight &&
        cz - 0.3 >= boardTop && cz + 0.3 <= boardBottom,
        `Chip ${chip.id} overflows board ${board.id}`
    );
});
```

**Evidence:**
- Screenshot: all labels inside chips, all chips inside boards, board titles inside borders
- Visible horizontal gap between FE and PL
- Hover tooltips still show full names
- 0 console errors

---

## EXECUTION ORDER

1. **W1: Fix generate_artifacts.py** (P0) — prevents future overwrites
2. **W3: Restore original v10.59 docs** (P1) — fix the damage
3. **W5: Claw3D chip containment** (P1) — all components inside boards
4. **W2: Produce corrected v10.59 report** (P1) — accurate scoring
5. **W4: Harness update** (P2) — ADR-012 + Pattern 17
6. Post-flight + living docs + report for v10.60

---

## COMPLETION CHECKLIST

```
[ ] W1: generate_artifacts.py has immutability check for design/plan
[ ] W1: Self-eval finds build log evidence (path fix)
[ ] W2: kjtcom-report-v10.59-corrected.md has scored workstreams
[ ] W2: agent_scores.json v10.59 entry updated with real scores
[ ] W3: Original v10.59 design doc restored (has Mermaid trident)
[ ] W3: Original v10.59 plan doc restored (has 10 pillars, execution steps)
[ ] W4: ADR-012 in evaluator-harness.md
[ ] W4: Pattern 17 (G58) in failure catalog
[ ] W5: All chip labels fit inside chip boxes (screenshot)
[ ] W5: All chips fit inside parent board boundaries
[ ] W5: Board titles inside board borders
[ ] W5: FE/PL horizontal gap visible
[ ] W5: Hover tooltips show full component names
[ ] Report for v10.60 has scored workstreams
[ ] Post-flight passes, changelog updated, 4 artifacts
```
