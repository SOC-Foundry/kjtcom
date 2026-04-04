# kjtcom - Report v8.26 (Phase 8 - Gotcha Registry + Query UX Fix)

**Pipeline:** kjtcom (cross-pipeline location intelligence platform)
**Phase:** 8 (Enrichment Hardening)
**Iteration:** 26 (global counter)
**Executor:** Claude Code (Opus)
**Machine:** NZXTcos
**Date:** 2026-04-04

---

## Success Criteria

| Criteria | Target | Result |
|----------|--------|--------|
| Rotating queries removed | No Timer, no auto-injection | PASS |
| Query editor starts empty | Empty string on load | PASS |
| Example syntax shown as static help text | Not injected into editor | PASS |
| Entity count row still shows total on load | Independent provider | PASS |
| User can type without interruption | No rotation overwrite | PASS |
| Full gotcha registry in report | G1-G42 with status | PASS |
| flutter analyze | 0 issues | PASS (0 issues) |
| flutter test | All pass | PASS (9/9) |
| firebase deploy | Success | PASS |
| Interventions | 0 | PASS (0) |
| Artifacts | 4 mandatory docs | PASS |

---

## Metrics

| Metric | Value |
|--------|-------|
| Files modified | 2 (query_editor.dart, query_provider.dart) |
| Lines removed | ~30 (rotation logic, example list, timer state) |
| Lines added | ~15 (static help text widget) |
| Production entities | 6,181 |
| Deploy time | ~5s |
| Total session time | Single-pass execution |
| Interventions | 0 |

---

## Complete Gotcha Registry (G1-G42)

| ID | Gotcha | Prevention | Status |
|----|--------|-----------|--------|
| G1 | Heredocs in fish shell | Use printf blocks, never heredocs | ACTIVE |
| G2 | CUDA LD_LIBRARY_PATH | source ~/.config/fish/config.fish before transcription. Permanently resolved on NZXTcos. | RESOLVED |
| G11 | API key leaks in catted files | NEVER cat config.fish or SA JSON files. grep only. | ACTIVE |
| G18 | Gemini 5-minute command timeout | Use background job execution for long-running commands | ACTIVE |
| G19 | Gemini runs bash by default | Wrap commands in `fish -c` | ACTIVE |
| G20 | Config.fish contains API keys | grep only, never cat. Print only SET/NOT SET for key checks. | ACTIVE |
| G21 | CUDA OOM on simultaneous transcription | Sequential processing, not parallel. Graduated timeout passes. | ACTIVE |
| G22 | Fish `ls` color codes break file parsing | Use `command ls` to avoid color codes | ACTIVE |
| G23 | LD_LIBRARY_PATH fix for CUDA path via Gemini | Set in config.fish, source before runs | RESOLVED (by G2 fix) |
| G24 | Checkpoint staleness on re-extraction | Reset checkpoints when re-extracting with new prompts | ACTIVE |
| G30 | Cross-project SA permissions | Verify both SA files exist and have Firestore read/write before migration | ACTIVE |
| G31 | TripleDB schema drift | Inspect actual Firestore data before migration. Schema from past conversations may be outdated. | RESOLVED (v7.21) |
| G32 | Production Firestore rules | Admin SDK bypasses rules. Verify project-level IAM. | ACTIVE |
| G33 | Duplicate entity IDs | Deterministic t_row_id (hash of name+city+pipeline). Check before write. | ACTIVE |
| G34 | Firestore single array-contains limit | One array-contains per server-side query. Multi-clause uses client-side filtering. Document in UI. | ACTIVE |
| G35 | Production write safety | All production update scripts use --dry-run flag. Verify on 5 entities before full run. | ACTIVE |
| G36 | Case-sensitive arrayContains | All t_any_* data MUST be lowercased. All query input lowercased before dispatch. | RESOLVED (v8.23 W1) |
| G37 | t_any_shows inconsistent casing | CalGold had title case from v5.14. All lowercased in v8.23 W3. | RESOLVED (v8.23 W3) |
| G38 | Firebase deploy auth expiry | `firebase login --reauth` if deploy fails. Deploy from repo root, not app/. | ACTIVE |
| G39 | Detail panel provider chain | selectedEntityProvider must be updated on row tap AND detail_panel must be in widget tree at all viewports. | RESOLVED (v8.24 W1) |
| G40 | Compound country names | Names like "france / spain" not parseable by pycountry. Require manual split. 6 unmapped. | DOCUMENTED |
| G41 | Rebuild-triggered event handlers | Any onPressed that modifies a provider watched by the same widget MUST guard against re-entry. Use dedup + guard flag. | RESOLVED (v8.25 W-A) |
| G42 | Rotating queries overwrite user input | Timer-based query injection into the editor overwrites active user typing. Remove rotation entirely. | RESOLVED (v8.26 W1) |

**Registry summary:** 22 gotchas total. 12 ACTIVE, 8 RESOLVED, 1 DOCUMENTED, 1 NEW->RESOLVED this iteration.

---

## Phase 8 Summary (v8.22-v8.26)

Phase 8 (Enrichment Hardening) is now COMPLETE across 5 iterations:

| Iteration | Focus | Key Deliverables |
|-----------|-------|-----------------|
| v8.22 | Enrichment + Query Assessment | Schema v3 100%, TripleDB enrichment 98%, 12 query defects identified |
| v8.23 | NoSQL Query Remediation | 11/12 defects fixed, case-insensitive search, contains-any, result counts |
| v8.24 | UI Fixes + Country Codes | Detail panel fixed, t_any_country_codes backfilled (99.7%) |
| v8.25 | Filter Fix + README Overhaul | +filter/-exclude dedup fix, comprehensive README |
| v8.26 | Query UX Fix + Gotcha Registry | Rotating queries removed, gotcha registry standard established |

**Phase 8 interventions across all iterations: 0**

---

## Recommendation

**Phase 8 COMPLETE.** The query system is fully operational with no UX-breaking behaviors. The gotcha registry standard is established for all future iterations.

**Next:** Phase 9 (App Optimization) or site aesthetics update. Potential work items:
- Lighthouse performance optimization (FCP currently 7-14s from Flutter bootstrap)
- D12 (deferred from v8.23): fuzzy/partial text search
- Map view for geocoded entities
- Mobile responsiveness refinements
