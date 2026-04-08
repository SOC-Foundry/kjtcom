# iao P3 Bootstrap Guide

**Target machine:** tsP3-cos (ThinkStation P3 Ultra)
**iao version:** 0.1.0-alpha
**Delivered:** 2026-04-08 from kjtcom 10.68.1
**First iteration on P3:** `iao-design-0.0.0.md` (Phase 0 iteration 0 run 0)

---

## What this is

`iao-v0.1.0-alpha.zip` contains the initial iao template extracted from the kjtcom POC.
This is the bring-up package for starting iao as its own project on P3.

This is Phase B of iao externalization. Phase 0 on P3 begins when you extract
this zip and run `iao status` for the first time.

---

## Prerequisites

- fish shell (>= 3.6)
- Python 3.11+
- git
- A terminal emulator
- ~10 GB disk space
- No CUDA required

---

## Extract

```fish
mkdir -p ~/dev/projects
cd ~/dev/projects
unzip /path/to/iao-v0.1.0-alpha.zip
mv iao-v0.1.0-alpha iao
cd iao
```

---

## Install

```fish
fish install.fish
```

The installer:
1. Copies iao/ package to ~/iao/
2. Adds bin/ to PATH via fish config marker block
3. Runs compatibility checks (some host-specific entries may FAIL - acceptable)
4. Runs `iao --version` to confirm installation

---

## Verify

```fish
iao --version       # should print 0.1.0
iao status          # project, middleware, hooks
iao check config    # resolution map
iao check harness   # alignment (should be clean - no project harness yet)
```

---

## First iteration on P3: `iao-design-0.0.0.md`

Phase 0 on P3 = "iao bring-up and validate on non-originating machine."

Your first iteration objectives:
1. Install iao cleanly from this zip
2. Run `iao status` and `iao check config` successfully
3. Discover sterilization gaps (host-specific assumptions, dangling kjtcom-pipeline references in postflight modules)
4. Initialize iao/ as its own git repo (local only, no remote yet)
5. Create `iao-design-0.0.0.md`, `iao-plan-0.0.0.md` planning artifacts

Produce a bundle at 0.0.1 close that the planning chat can review.

---

## Sterilization round 2 (deferred work)

The following kjtcom-specific items remain in this v0.1.0-alpha drop and are explicit candidates for sterilization on P3:

- `iao/iao/postflight/{claw3d_version_matches,deployed_claw3d_matches,deployed_flutter_matches,map_tab_renders}.py` - need to be moved out into a project plugin set, with iao providing only project-agnostic checks.
- `iao/iao/postflight/artifacts_present.py` - hardcoded prefix, should read .iao.json artifact_prefix.
- `iao/iao/doctor.py` - imports the kjtcom-specific postflight modules.

See the originating iteration's sterilization log for full context.

---

## iao push from P3 (not yet)

In 10.68 the iao push command is a skeleton. It does not push to github. Once
validated locally on P3 (and after iao is manually pushed to its remote as
v0.2.0), the full loop becomes live.

Until then: iterate on P3, collect learnings, bundle them, hand bundles
back to the planning chat for next-iteration planning.

---

*iao-p3-bootstrap.md - delivered with iao-v0.1.0-alpha.zip from kjtcom 10.68.1.*
