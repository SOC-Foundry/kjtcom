# GEMINI.md — kjtcom 10.69.1 Execution Brief

**Iteration:** 10.69.1 (phase 10, iteration 69, run 1)
**Phase:** 10 (Harness Externalization + Retrospective) — **FINAL ITERATION**
**Date:** April 08, 2026
**Repo:** SOC-Foundry/kjtcom
**Machine:** NZXTcos
**Working directory:** `~/dev/projects/kjtcom`
**Wall clock target:** ~4-6 hours, no hard cap
**Run mode:** Sequential, bounded, no tmux
**Executor:** Gemini CLI (`gemini --yolo`)
**Launch trigger:** "read gemini and execute 10.69"

---

## 1. Who You Are and What You're Doing

You are Gemini CLI executing the **final iteration of kjtcom Phase 10**. This iteration closes 10.68.1's blocked conditions, retroactively charters Phase 10, transitions kjtcom from active development lab to steady-state production reference, and establishes the iao authoring environment on NZXT.

This iteration matters because:
- It's the **last full Phase 10 iteration** — Phase 10 graduates at the end of this run if all deliverables ship green
- It establishes **`iao log workstream-complete`** as the new build-log discipline (you must use it from W4 onward)
- It creates the **iao authoring environment** at `~/dev/projects/iao/` separate from kjtcom — the next planning session works on iao 0.2.0, not on kjtcom
- It hardens the **evaluator** so W7's closing run actually produces real Qwen scores instead of falling back to self-eval

**kjtcom is graduating from active development to steady-state reference, NOT shutting down.** It continues running production at kylejeromethompson.com indefinitely. What ends is the daily-to-weekly iteration cadence.

---

## 2. The Three Hard Rules

### Pillar 0 — No Git Writes
You **never** run `git commit`, `git push`, or `git add`. Read-only git only. `git mv` for tracked renames is acceptable. `git checkout --` for rollback during failure recovery is acceptable. All commits are manual by Kyle after iteration close.

**A `git add` or `git commit` attempt is a Pillar 0 violation. Halt immediately if you find yourself about to do this.**

### Pillar 6 — Zero Intervention
You **never** ask Kyle for permission. You log discrepancies, choose the safest forward path, and proceed. You halt only on hard pre-flight BLOCKERS or destructive irreversible operations.

If you're tempted to ask "should I do X?" — the answer is: log the situation in the build log under `## Discrepancies Encountered`, make the safest choice, and continue.

### W7 Closing Evaluator Is Non-Negotiable
The closing Qwen evaluator at W7 is **mandatory**. Wall clock pressure is not a valid reason to skip. The W1 evaluator hardening fixes earlier in this iteration should make Tier 1 work cleanly. If the evaluator legitimately falls through both tiers despite W1's fixes, document tier-by-tier outcomes per the v10.67/10.68 acceptable failure pattern — but **never CHOOSE to skip the attempt**.

**Skipping W7 = iteration failure.** Legitimate fallback is acceptable. Choosing not to run is forbidden.

---

## 3. The Failure Modes You Must NOT Repeat

**v10.66:** the agent skipped the closing evaluator to save wall clock. **This is forbidden.**

**v10.67:** the evaluator ran, both tiers fell back legitimately due to iaomw-G097 (Qwen synthesis ratio sensitivity) and iaomw-G098 (Gemini Flash schema validation), agent honestly produced self-eval fallback. **This is acceptable.**

**10.68.1:** the evaluator ran, both tiers fell back for the same reasons, agent honestly produced self-eval fallback AND self-identified that batching the build-log writes (instead of appending per workstream) caused the first evaluator pass to fail with empty narrative. **This is acceptable but exposed two debts that 10.69 W1 and W3 close.**

**The pattern:** skipping is a choice, failing is a circumstance. You may never choose to skip. You may document a legitimate failure honestly.

**The build-log discipline is W3's specific target.** Once W3 ships the `iao log workstream-complete` command, you MUST use it at the end of every workstream from W4 through W7. Do not batch build log writes. Do not save them for the end. The 10.68.1 retroactive-fill failure mode is exactly what W3 makes structurally impossible.

For W0-W3, before the `iao log` command exists, manually append a build-log entry after each workstream completes. Same discipline, slightly different mechanism.

---

## 4. Reading Order (Do This First, In Order)

When Kyle says **"read gemini and execute 10.69"**:

1. **Acknowledge in one line.** Example: "Reading 10.69.1 brief, design, and plan."
2. **Read this file (`GEMINI.md`) end-to-end.** That's what you're doing right now.
3. **Read `docs/kjtcom-design-10.69.0.md` end-to-end.** This is the design doc. It is **immutable**. You do not edit it. You execute against it.
4. **Read `docs/kjtcom-plan-10.69.0.md` end-to-end.** This is the plan doc. It is **immutable**. It contains the workstream procedures with full code blocks. You execute its procedures.
5. **Create `docs/kjtcom-build-10.69.1.md`** from the template in plan §5. This is your execution narrative — you append to it continuously throughout the run.
6. **Run pre-flight from plan §4.** Capture results to the build log's Pre-Flight section.
7. **Begin W0** (the .iao.json current_iteration update).
8. Proceed sequentially through W1 → W7.
9. **W7 is mandatory.** Run the closing evaluator no matter what.
10. Emit the dual graduation handback (iteration + Phase 10) per plan §6 W7 step 13.
11. **STOP.** Do not commit. Do not push.

---

## 5. Critical Gotchas (Reread These Before You Start)

- **iaomw-G001:** Heredocs break Gemini CLI. Use `printf` for any multi-line file write. The plan doc shows `cat > file << EOF` blocks in some places — when executing, prefer `printf` if the content is short, or use Python's `pathlib.write_text()` for longer content. Do not use bash heredocs.
- **iaomw-G022:** `ls` color codes break agent output parsing. Always use `command ls`.
- **iaomw-G083:** Design and plan docs are **immutable during execution**. Do not edit `docs/kjtcom-design-10.69.0.md` or `docs/kjtcom-plan-10.69.0.md` for any reason. If the design is wrong, log a discrepancy and execute the closest reasonable interpretation.
- **iaomw-G097 / G098:** These are the evaluator failure modes that W1 fixes. After W1 ships, the closing evaluator at W7 should produce real Qwen output. If it doesn't, that's a deeper issue and you mark D7 `blocked-by-evaluator-still`.
- **iaomw-G102:** The iao_logger was hardcoded to "v9.39" before 10.68.1 W0 fixed it. W0 of this iteration sets `current_iteration` to `10.69.1` so the logger picks up the right tag. Do W0 first.
- **Security: NEVER `cat ~/.config/fish/config.fish`.** Gemini CLI has historically leaked API keys when running this command. If you need to verify the iao marker is present in fish config, use `grep -c "# >>> iao" ~/.config/fish/config.fish` instead — that returns a count, not content.

---

## 6. Execution Rules (Quick Reference)

1. `printf` or Python `pathlib.write_text()` for multi-line file writes (G1)
2. `command ls` for directory listings (G22)
3. Bash defaults to bash; wrap fish commands with `fish -c "..."`
4. **No tmux** in 10.69 — synchronous only
5. Max 3 retries per error (Pillar 7)
6. `iao registry query "<topic>"` first for any diligence
7. Update build log incrementally — **never batch at end**
8. **Never edit design or plan docs** (G83)
9. **Never run git writes** (Pillar 0)
10. **Set `IAO_ITERATION=10.69.1`** in pre-flight (no `v` prefix)
11. **Set `IAO_WORKSTREAM_ID=W<N>`** at start of each workstream
12. Wall clock awareness at each workstream boundary
13. **Never `cat ~/.config/fish/config.fish`** — use grep for marker checks
14. `pip install --break-system-packages` always
15. **W0 runs first** (.iao.json current_iteration update)
16. **W3 enables `iao log workstream-complete`; from W4 onward, use it at every workstream boundary**

---

## 7. Workstream Sequence (One-Line Summaries)

| W# | Title | Est. | D# |
|---|---|---|---|
| W0 | Update `.iao.json current_iteration` to 10.69.1 | 2 min | (pre-flight) |
| W1 | Evaluator tooling hardening (3 fixes + tests + 10.68.1 regression) | 60 min | D1 |
| W2 | Postflight plugin loader refactor (move kjtcom checks to kjtco/postflight/) | 50 min | D2 |
| W3 | Build log auto-append hook (`iao log workstream-complete` command) | 35 min | D3 |
| W4 | Phase 10 charter retrofit (extract design §1 to standalone, add iaomw-Pattern-31) | 25 min | D4 |
| W5 | kjtcom steady-state transition (.iao.json mode flag, maintenance guide, inaugural note) | 30 min | D5 |
| W6 | iao authoring environment setup (`~/dev/projects/iao/` with own .iao.json) | 40 min | D6 |
| W7 | **Closing sequence with hardened evaluator (MANDATORY)** | 25 min | D7 |

**Sum:** ~4h 27min estimated. W1 is highest-risk (touches the evaluator script you depend on for W7). W7 is non-negotiable.

For full step-by-step procedures with code blocks, **read plan §6**. Do not execute from this brief — execute from the plan.

---

## 8. Pre-Flight BLOCKERS (Halt If Any Fail)

Run plan §4 in full. The BLOCKERs you must verify:

1. `IAO_ITERATION=10.69.1` is set (no `v` prefix)
2. `docs/kjtcom-design-10.69.0.md` and `docs/kjtcom-plan-10.69.0.md` exist (immutable inputs)
3. `docs/kjtcom-design-10.68.0.md`, `docs/kjtcom-plan-10.68.0.md`, `docs/kjtcom-build-10.68.1.md`, `docs/kjtcom-report-10.68.1.md`, `docs/kjtcom-bundle-10.68.1.md` exist
4. `docs/classification-10.68.json` and `iao/docs/sterilization-log-10.68.md` exist
5. `iao/iao/__init__.py`, `iao/iao/cli.py`, `iao/iao/doctor.py`, `iao/iao/postflight/` exist
6. `pip show iao` returns version 0.1.0
7. `iao --version` returns 0.1.0
8. `iao status` works
9. `curl -s http://localhost:11434/api/tags` returns (ollama up)
10. `ollama list | grep -i qwen` returns matches (qwen pulled)
11. `python3 -c "import litellm, jsonschema"` works
12. `df -h ~ | tail -1` shows > 10G free
13. `scripts/run_evaluator.py` exists

**Any BLOCKER fails → halt with `PRE-FLIGHT BLOCKED: <reason>`. Exit. Do not proceed.**

---

## 9. Build Log Discipline

Create `docs/kjtcom-build-10.69.1.md` immediately after pre-flight passes. Use the template in plan §5.

**Append to it continuously throughout execution.** After each workstream:

- **For W0-W3** (before `iao log` exists): manually append to the `## Execution Log` section using printf or pathlib.write_text in append mode. Format: `### W<N> — <title>` followed by 3-5 bullet points and wall clock.
- **For W4-W7** (after W3 ships the `iao log` command): use `iao log workstream-complete W<N> <pass|partial|fail> "<one-sentence summary>"` at the end of each workstream. This appends a structured entry automatically.

**Do not batch.** Do not save build-log writes for the end. The evaluator at W7 reads the build log as its primary evidence — if it's incomplete or empty, the evaluator falls through to self-eval and the iteration's grade is at risk.

The build log sections you must populate by W7:

- `## Pre-Flight` — pre-flight results
- `## Discrepancies Encountered` — anything weird that didn't halt
- `## Execution Log` — W0-W7 entries
- `## Files Changed` / `## New Files Created` / `## Files Deleted`
- `## Wall Clock Log` — start/end times per workstream
- `## W1 Evaluator Hardening Outcomes` — what worked, what didn't
- `## W2 Postflight Refactor Summary` — moved checks, plugin loader status
- `## W7 Closing Evaluator Findings` — tier used, scores, graduation assessment
- `## Iteration Deliverables Verification (D1-D7)` — table from plan §6 W7 step 7
- `## Phase 10 Exit Criteria Verification` — table from design §1 Phase Charter Exit Criteria
- `## Iteration Graduation Recommendation` — your recommendation
- `## Phase 10 Graduation Recommendation` — your dual-level recommendation
- `## Files Changed Summary` — final summary
- `## What Could Be Better` — honest retrospective notes
- `## Next Iteration Candidates` — iao 0.2.0 + Phase 1 launch

---

## 10. Closing Handback (W7 Step 13)

After W7 completes, emit this to stdout via printf:

```
==============================================
10.69.1 COMPLETE — PHASE 10 GRADUATION ASSESSMENT
==============================================

Iteration 10.69.1 Deliverables: <N>/7 green

  D1 Evaluator hardening:        <PASS|PARTIAL|FAIL>
  D2 Postflight plugin loader:    <PASS|PARTIAL|FAIL>
  D3 Build log auto-append:       <PASS|PARTIAL|FAIL>
  D4 Phase 10 charter retrofit:   <PASS|PARTIAL|FAIL>
  D5 kjtcom steady-state:         <PASS|PARTIAL|FAIL>
  D6 iao authoring environment:   <PASS|PARTIAL|FAIL>
  D7 Closing evaluator ran:       <PASS|PARTIAL|FAIL>

Qwen tier used: <tier>
Qwen graduation_assessment: <value>

PHASE 10 EXIT CRITERIA:
  [Each criterion from design §1 Phase Charter, marked PASS/FAIL]

ITERATION RECOMMENDATION: <GRADUATE 10.69 | RERUN 10.69.2 | BLOCKED>
PHASE 10 RECOMMENDATION: <GRADUATE PHASE 10 | REQUIRES 10.69.X | BLOCKED>

Next phase context:
  - iao authoring at ~/dev/projects/iao/ (iteration 0.1.0 stub on disk)
  - kjtcom in steady-state mode (mode flag set, maintenance guide written)
  - First iao 0.2.0 candidate scope: bridge files + Universal Consumer launch

Awaiting human review of bundle and dual graduation decision (iteration + phase).
```

Then **STOP.** Do not commit. Do not push. Hand back to Kyle.

---

## 11. Failure Mode Quick Reference

| Failure | Action |
|---|---|
| Pre-flight BLOCKER | Halt. `PRE-FLIGHT BLOCKED: <reason>`. Exit. |
| W0 .iao.json edit fails | `git checkout -- .iao.json`, retry with python json module |
| W1 evaluator fixes break further | Revert specific fix, mark D1 PARTIAL, continue |
| W1 unit tests fail | 3-retry, revert specific fix |
| W2 import break after move | `git checkout -- <file>`, mark check as not-yet-moved |
| W3 `iao log` command fails | Manual append, mark D3 PARTIAL, document |
| W4 charter writing fails | Path issue, retry with absolute paths |
| W5 mode flag breaks `iao check config` | Revert flag, mark D5 PARTIAL, document |
| W6 cp fails (disk/permissions) | Investigate, retry. If unresolvable, mark D6 FAIL but iao environment can be set up post-iteration manually |
| W6 `iao status` from iao dir fails | Debug PYTHONPATH or pip install. Mark D6 PARTIAL if unresolvable |
| **W7 evaluator falls back AGAIN despite W1 fixes** | Mark D7 `blocked-by-evaluator-still`. Phase 10 graduation deferred. Recommend 10.69.2 |
| W7 build_gatekeeper FAIL | Real failure. Debug. Phase 10 graduation blocked until resolved |
| Wall clock > 7 hours | Triage: W4/W5 can become lighter. W1/W2/W3/W6/W7 MUST run |
| **Tempted to skip W7 evaluator** | Re-read §2 and §3 of this brief. Not acceptable. Run it. |
| Any git write attempted | Pillar 0 violation. Halt immediately |

---

## 12. Significance (Why This Run Matters)

**This iteration closes Phase 10.** Three concrete debts resolved (W1-W3), strategic structure formalized (W4 charter), kjtcom transitioned with dignity to steady-state (W5), iao given its own authoring home (W6), and Phase 10 closed honestly with a real evaluator pass (W7).

**kjtcom continues running.** Production stays at 6,785 entities across 4 pipelines. The site at kylejeromethompson.com keeps serving show-browsing requests indefinitely. Future kjtcom development happens at much lower cadence with lighter ceremony — schema migrations, query tweaks, occasional pipeline updates, possibly new feature work eventually. **kjtcom is graduating from active collaboration in the planning chat, not graduating from existence.**

**iao becomes the active artifact.** After 10.69.X graduates, the next iteration the planning chat collaborates on is **iao 0.2.0** — Phase 1 launch, Universal Consumer, bridge files, `iao operator run`. iao becomes its own thing.

**If all 7 deliverables ship green**, kjtcom Phase 10 graduates and the planning chat moves to iao Phase 0/1 work in the next session.

**If anything blocks**, 10.69.2 closes the gap — same iteration number, incremented run, targeted scope. No drama, no scope creep, no lost progress.

You are executing the cleanest possible Phase 10 close. Run it cleanly, log honestly, and hand back to Kyle for the dual graduation decision.

---

## 13. Final Reminders

- **CLAUDE.md is for Claude Code, GEMINI.md is for you.** This brief is yours.
- **Read the plan, not just this brief.** This brief is operational context. The plan has the actual procedures.
- **`iao log workstream-complete` from W4 onward.** Manual append for W0-W3.
- **W7 is mandatory.** Skipping is forbidden. Failing is acceptable if documented.
- **Zero git writes.** Ever.
- **Zero permission asks.** Log discrepancies, choose safest path, proceed.
- **Zero `cat ~/.config/fish/config.fish`.** Use grep for marker checks.
- **STOP at the end.** Hand back to Kyle. Do not commit.

**When Kyle says "read gemini and execute 10.69" — acknowledge in one line, read this brief, read the design, read the plan, and begin.**

---

*GEMINI.md for kjtcom 10.69.1 — April 08, 2026. Final iteration of Phase 10. Authored by the planning chat. Execute against the immutable design + plan.*
