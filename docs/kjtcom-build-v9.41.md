# kjtcom - Build Log v9.41

**Phase:** 9 - App Optimization
**Iteration:** 9.41
**Date:** April 05, 2026
**Executing Agent:** Claude Code (Opus 4.6)

---

## PRE-FLIGHT

All pre-flight checks passed.

---

## EXECUTION LOG

**W1 (P1) - Firestore Dual Retrieval: COMPLETE**
- Created `data/schema_reference.json` - 22 fields, 3 pipelines, <500 tokens serialized
- Created `scripts/intent_router.py` - Gemini 2.5 Flash classifies /ask queries as entity (Firestore) or dev history (ChromaDB)
- Created `scripts/firestore_query.py` - Firebase Admin SDK with G34 workaround (single array-contains + Python post-filter)
- Rewired `scripts/telegram_bot.py` /ask handler for 3-stage dual retrieval (route -> execute -> synthesize)
- Discovery: gemini/gemini-2.0-flash deprecated (404) - switched to gemini/gemini-2.5-flash with thinking disabled
- Discovery: t_any_states stored as 2-letter codes (ca, tx), not full names - updated schema reference and routing prompt
- Discovery: tripledb entities lack t_any_counties data - accurate 0-result behavior
- Tested: 6,181 total entities, 84 TX tripledb locations listed, 20+ LA County calgold locations listed

**W2 (P1) - Re-embed Archive: COMPLETE**
- Copied v9.40 docs to archive (4 files)
- Ran embed_archive.py: 1,307 -> 1,419 chunks, 130 -> 142 files

**W3 (P2) - Artifact Automation Scaffold: COMPLETE**
- Created `template/artifacts/` with 3 templates (build, report with Workstream Scorecard, changelog)
- Created `scripts/generate_artifacts.py` - reads event log, agent_scores, git diff, generates drafts via Qwen
- Updated `scripts/run_evaluator.py` with `--workstreams` flag for per-W# scoring

**W4 (P2) - Rebuild Registry: DEFERRED**
- build_registry_v2.py timed out at iteration 3/33 (each Qwen call ~60s with num_predict 2048)
- Deferred to v9.42 per plan

**W5 (P3) - Living Doc Updates: COMPLETE**
- Updated `docs/kjtcom-architecture.mmd` - added INTENT_ROUTER, SCHEMA_REF, ARTIFACT_GEN to middleware subgraph
- Updated `docs/install.fish` - added firebase-admin to Step 5d
- Appended v9.41 entry to `docs/kjtcom-changelog.md`
- Updated `GEMINI.md` to reference v9.41 docs
- Flutter: 0 analyze issues, 15/15 tests pass
- Deployed to kjtcom-c78cd.web.app (41 files)

---

## FILES CHANGED

CLAUDE.md                    | 174 +++++++++++++++++++++++++++++++++++--------
 GEMINI.md                    |   4 +-
 agent_scores.json            |  84 +++++++++++++++++++++
 data/chromadb/chroma.sqlite3 | Bin 15253504 -> 20484096 bytes
 data/iao_event_log.jsonl     | 127 +++++++++++++++++++++++++++++++
 docs/install.fish            |   1 +
 docs/kjtcom-architecture.mmd |  18 ++++-
 docs/kjtcom-changelog.md     |  18 +++++
 scripts/run_evaluator.py     | 140 ++++++++++++++++++++++++++++++++--
 scripts/telegram_bot.py      | 140 ++++++++++++++++++++++------------
 10 files changed, 614 insertions(+), 92 deletions(-)

---

## TEST RESULTS

See flutter analyze and flutter test output.

---

## GOTCHA LOG

G34: Single array-contains limit - workaround active.
G47: CanvasKit DOM - open.
G53: Firebase MCP reauth - recurring.

---

## EVENT LOG SUMMARY

Total events: 115
  api_call: 17
  command: 1
  llm_call: 97
Errors: 2

---

*Build log v9.41, April 05, 2026.*
