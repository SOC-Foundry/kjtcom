# kjtcom - Report v9.28 (Phase 9 - Gotcha Tab + Schema Builder + JSON Copy)

**Pipeline:** kjtcom
**Phase:** 9 (App Optimization)
**Iteration:** 28 (global counter)
**Executor:** Claude Code (Opus)
**Machine:** NZXTcos
**Date:** 2026-04-04

---

## Success Criteria

| Criteria | Target | Result |
|----------|--------|--------|
| Gotcha tab renders all gotchas | Yes, with status badges | PASS - 25 gotchas (G1-G44) |
| Gotcha tab filter (all/active/resolved) works | Yes | PASS |
| Schema tab renders all 22 fields | Yes, with types and examples | PASS |
| Schema field click adds clause to query | Yes, switches to Results tab | PASS |
| t_log_type click uses == operator | Yes | PASS |
| t_any_coordinates/geohashes view-only | Yes | PASS |
| Copy JSON button on detail panel | Yes, copies full entity | PASS |
| SnackBar confirmation on copy | Yes | PASS |
| Live site deployment verified | Yes | PASS - firebase deploy success |
| All 6 tabs functional | Results, Map, Globe, IAO, Gotcha, Schema | PASS |
| flutter analyze | 0 issues | PASS |
| flutter test | All pass | PASS - 9/9 |
| firebase deploy | Success | PASS - 40 files |
| Interventions | 0 | PASS |
| Artifacts | 4 mandatory docs | PASS |

---

## Gotcha Registry (Full - G1-G44)

| ID | Gotcha | Prevention | Status |
|----|--------|-----------|--------|
| G1 | Heredocs in fish shell | Use printf blocks, never heredocs | ACTIVE |
| G2 | CUDA LD_LIBRARY_PATH | source ~/.config/fish/config.fish before transcription | RESOLVED v3.10 |
| G11 | API key leaks in catted files | NEVER cat config.fish or SA JSON files. grep only. | ACTIVE |
| G18 | Gemini 5-minute command timeout | Use background job execution | ACTIVE |
| G19 | Gemini runs bash by default | Wrap in fish -c | ACTIVE |
| G20 | Config.fish contains API keys | grep only, never cat | ACTIVE |
| G21 | CUDA OOM on simultaneous transcription | Sequential processing, graduated timeouts | ACTIVE |
| G22 | Fish ls color codes | Use command ls | ACTIVE |
| G23 | LD_LIBRARY_PATH CUDA path | Set in config.fish | RESOLVED v3.10 (by G2) |
| G24 | Checkpoint staleness on re-extraction | Reset checkpoints for new prompts | ACTIVE |
| G30 | Cross-project SA permissions | Verify both SA files before migration | ACTIVE |
| G31 | TripleDB schema drift | Inspect actual data before migration | RESOLVED v7.21 |
| G32 | Production Firestore rules | Admin SDK bypasses rules, verify IAM | ACTIVE |
| G33 | Duplicate entity IDs | Deterministic t_row_id, check before write | ACTIVE |
| G34 | Firestore single array-contains limit | One per query, client-side for additional | ACTIVE |
| G35 | Production write safety | --dry-run before full run | ACTIVE |
| G36 | Case-sensitive arrayContains | All data + input lowercased | RESOLVED v8.23 |
| G37 | t_any_shows inconsistent casing | All lowercased | RESOLVED v8.23 |
| G38 | Firebase deploy auth expiry | firebase login --reauth, deploy from repo root | ACTIVE |
| G39 | Detail panel provider chain | Must be in widget tree at all viewports | RESOLVED v8.24 |
| G40 | Compound country names | Manual split required, 6 unmapped | DOCUMENTED |
| G41 | Rebuild-triggered event handlers | Dedup + guard flag | RESOLVED v8.25 |
| G42 | Rotating queries overwrite input | Removed rotation | RESOLVED v8.26 |
| G43 | Flutter Web map tile CORS | Test CanvasKit + HTML renderer for OSM tiles | ACTIVE |
| G44 | flutter_map version compatibility | Check pub.dev for Flutter SDK compat | ACTIVE |

**Summary:** 15 ACTIVE, 9 RESOLVED, 1 DOCUMENTED

---

## Phase 9 Status

| Iteration | Work Items | Status |
|-----------|-----------|--------|
| v9.27 | Visual refresh, Map/Globe/IAO tabs, pagination | DONE |
| v9.28 | Gotcha tab, Schema builder, JSON copy, post-flight standard | DONE |

**Phase 9 IN PROGRESS** - additional optimization items possible (Lighthouse, mobile responsive, analytics).

---

## Metrics

| Metric | Value |
|--------|-------|
| Production entities | 6,181 |
| Pipelines | 3 (calgold, ricksteves, tripledb) |
| App tabs | 6 (Results, Map, Globe, IAO, Gotcha, Schema) |
| Thompson Indicator Fields | 22 |
| Gotchas documented | 25 (G1-G44) |
| flutter analyze issues | 0 |
| flutter test pass rate | 9/9 (100%) |
| Deploy count | 1 |
| Interventions | 0 |
| New files | 2 (gotcha_tab.dart, schema_tab.dart) |
| Modified files | 4 |

---

## Recommendation

Phase 9 continues to deliver value. v9.28 adds three portfolio-visible features (Gotcha tab, Schema builder, JSON copy) and establishes post-flight deploy testing as a mandatory standard.

**Next iteration options:**
- v9.29: Lighthouse performance optimization (FCP < 5s target)
- v9.29: Cookie consent + analytics events
- v9.29: Mobile responsiveness polish
- Phase 10: IAO retrospective + template publication
