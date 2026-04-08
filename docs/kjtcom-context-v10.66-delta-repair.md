# kjtcom — Context Bundle v10.66 Delta-Repair Sidecar

**Purpose:** Repair §6 DELTA STATE of `docs/kjtcom-context-v10.66.md` which shipped with `ERROR: Snapshot data/iteration_snapshots/v10.66.json not found`.

**Authored:** v10.67 W2
**Shipped bundle:** `docs/kjtcom-context-v10.66.md` (UNMODIFIED — immutable artifact policy)
**This sidecar:** corrected §6 content only

---

## Root Cause Analysis

The snapshot `data/iteration_snapshots/v10.66.json` was likely not written to disk before `build_context_bundle.py` was executed in the v10.66 closing sequence, despite the build log indicating it was "saved". The v10.66 regex fallback (which parses the previous build log) also failed to fire, possibly because the build log file was not yet on disk or the pattern did not match.

In v10.67 W2, the snapshot was successfully generated retroactively, allowing for the correct delta table below.

---

## Corrected §6. DELTA STATE

| Metric | v10.65 | v10.66 | Delta |
| :--- | :--- | :--- | :--- |
| Total Production Entities | 6,785 | 6,785 | - |
| Total Staging Entities | 0 | 0 | - |
| Harness Line Count | 1,062 | 1,111 | +49 ↑ |
| Gotcha Count | 60 | 60 | - |
| Script Registry Size | 63 | 67 | +4 ↑ |

---

## Forward Fix

`iao_middleware/context_bundle.py` §6 path resolution now falls through three tiers:

1. `.iao.json` env-configured snapshot path
2. Default `data/iteration_snapshots/<iter>.json`
3. Regex parse of previous build log (`docs/kjtcom-build-<prev>.md`)

All three exhausted → emit `DELTA STATE UNAVAILABLE: <reason>` instead of raw error.

This fix is applied in W3a context_bundle.py refactor and verified in W9 v10.67 closing bundle.
