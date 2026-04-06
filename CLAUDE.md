# CLAUDE.md — kjtcom Agent Harness (Claude Code)

**Launch:** `read claude and execute 10.58`
**Repo:** SOC-Foundry/kjtcom
**Site:** kylejeromethompson.com
**Firebase:** kjtcom-c78cd (Blaze)
**Shell:** fish + tmux on NZXTcos and tsP3-cos

---

## RULES

1. **NEVER** `git commit`, `git push`, or any git write. All git = Kyle only.
2. **NEVER** heredocs. `printf` only (G1). `command ls` (G22). `fish -c` wrappers (G19).
3. **NEVER** simultaneous GPU. Graduated tmux batches, unload Ollama first (G18).
4. Read ENTIRE files before editing. `grep` all related patterns across `app/`.
5. 4 artifacts per iteration: design, plan, build, report. No exceptions.
6. Post-flight MANDATORY. `10/10` prohibited. Harness never shrinks. Scores append-only.
7. Changelog: `NEW:` / `UPDATED:` / `FIXED:` prefixes. No fluff.
8. **REPORTS MANDATORY.** Fallback: Qwen → Gemini → self-eval. Empty scorecards = failure.
9. **G56: ALL Claw3D data INLINE as JS objects. NEVER fetch() external JSON.**

---

## PROJECT STATE

| Pipeline | t_log_type | Color | Entities | Status |
|----------|-----------|-------|----------|--------|
| California's Gold | calgold | #DA7E12 | 899 | Production |
| Rick Steves' Europe | ricksteves | #3B82F6 | 4,182 | Production |
| Diners Drive-Ins and Dives | tripledb | #DD3333 | 1,100 | Production |
| Anthony Bourdain | bourdain | #8B5CF6 | 188 | **Staging (Phase 2)** |

**Total:** 6,181 production + 188 staging. Bourdain Phase 3 not yet executed.

---

## AGENTS & EVALUATOR

| Agent | Role |
|-------|------|
| Claude Code | Executor (Phases 6-7, app, docs) |
| Gemini CLI | Executor (Phases 1-5) |
| Qwen3.5-9B | Evaluator (local Ollama) |
| Gemini Flash | Intent routing, extraction, evaluator fallback |

**Evaluator fallback:** Qwen (3) → Gemini (2) → self-eval (always succeeds, cap 7/10)

**v10.57 evaluator issue:** All 3 tiers failed schema validation. Root cause: `eval_schema.json` constraints are too tight for the actual LLM output format. The schema needs to be relaxed OR the prompt needs a concrete JSON example that matches the schema exactly. Fix in W3.

---

## GOTCHAS

| ID | Title | Workaround |
|----|-------|------------|
| G1 | Heredocs | printf only |
| G18 | CUDA OOM | Graduated tmux, unload Ollama |
| G34 | Firestore array-contains | Post-filter |
| G45 | Query editor cursor | flutter_code_editor pending |
| G53 | Firebase MCP reauth | Retry wrapper |
| G55 | Qwen empty reports | Fallback chain (resolved v10.56) |
| G56 | Claw3D fetch() 404 | Inline all data (resolved v10.57) |

---

## v10.58 WORKSTREAMS

### W1: Claw3D Visual Polish — Gaps + Connectors + Logger (P1)

**v10.57 delivered the layout but boards are directly touching middleware.** Fix:

**Gap + connector requirement:** All 4 boards must have visible gaps between them with animated dashed trace connectors crossing the gaps — exactly like the Backend→Middleware connector already works. Specifically:
- Frontend board (top-left) has a gap below it, with animated traces going down to Middleware
- Pipeline board (top-right) has a gap below it, with animated traces going down to Middleware
- Middleware board (center) has a gap below it, with animated traces going down to Backend
- The gap should be ~1.5 Three.js units (enough to see the animated dashes and read the connector label)

**Board positions (adjusted for gaps):**
```
Frontend:   [-3, 5, 0]   size [5, 3]
Pipeline:   [3, 5, 0]    size [5, 3]
  ↕ gap ~1.5 units with animated connectors
Middleware: [0, 0, 0]    size [12, 6]   ← LARGE, centered
  ↕ gap ~1.5 units with animated connectors
Backend:    [0, -5.5, 0] size [12, 3]
```

**Connector labels in gaps:**
- FE→MW gap: "Riverpod / Firestore stream"
- PL→MW gap: "Pipeline scripts / checkpoint"
- MW→BE gap: "Admin SDK / Ollama / ChromaDB"

**Logger chip:** Add a `logger` chip to the Middleware board. All event logging (`data/iao_event_log.jsonl`) is managed by middleware. The logger chip should show:
- id: "iao_logger"
- status: "active"
- detail: "JSONL event log, P3 diligence"

Claw3D itself does not log — it reads component data that's been logged by middleware. The logger chip on the middleware board represents this.

**Evidence:**
- Visible gaps between all board pairs
- Animated traces crossing each gap
- Connector labels readable
- Logger chip present on middleware board
- 0 console errors, hover/zoom still work

---

### W2: Bourdain Pipeline — Phase 3 (P1)

**This did not execute in v10.57.** Videos 61-90.

**Machine:** NZXTcos (GPU required)
**Playlist:** `https://www.youtube.com/playlist?list=PLEVfhwFNb44fPn5N3OXk-aEHFvLOPzXKo`

```
yt-dlp --playlist-items 61-90 -x --audio-format mp3
# Unload Ollama: curl -s http://localhost:11434/api/generate -d '{"model":"qwen3.5:9b","keep_alive":0}'
# Graduated tmux: 3 batches of 10, sequential, timeout 600s
faster-whisper (CUDA)
Gemini Flash extraction (pipeline/config/bourdain/extraction_prompt.md)
phase4_normalize.py --pipeline bourdain
phase5_geocode.py --pipeline bourdain
phase6_enrich.py --pipeline bourdain
phase7_load.py --pipeline bourdain --database staging
```

**DO NOT load to production. Staging only.**
**Dedup against 188 existing entities.**
**Update `data/bourdain/checkpoint.json`.**

---

### W3: Fix Evaluator Schema Validation (P1)

**Problem:** In v10.57, all 3 evaluator tiers failed schema validation. The `eval_schema.json` constraints don't match what the LLMs actually produce. Self-eval saved scores to `agent_scores.json` but didn't generate the report markdown file.

**Diagnosis:**
1. `cat data/eval_schema.json` — what constraints exist?
2. Run evaluator with `--verbose` and capture the raw LLM output
3. Compare raw output structure to schema requirements
4. Identify mismatches (field names? types? enum values? string length limits?)

**Fix options (try in order):**
1. **Relax the schema** — if constraints are unnecessarily tight (e.g. summary max 500 chars, priority enum missing values), loosen them to match realistic LLM output
2. **Add a concrete JSON example to the prompt** — show Qwen/Gemini exactly what the output should look like, field by field, so there's no ambiguity
3. **Add a JSON repair step** — after getting LLM output, attempt to fix common issues (strip markdown fences, fix trailing commas, coerce types) before validation
4. **Ensure self-eval writes both `agent_scores.json` AND the report markdown** — the self-eval tier must produce `docs/kjtcom-report-v{version}.md` not just the JSON scores

**Evidence:**
- Run evaluator against v10.57 build log: `python3 -u scripts/run_evaluator.py --iteration v10.57 --verbose`
- At least one tier produces valid output (Qwen preferred)
- Report markdown file is generated (not just agent_scores.json)
- `grep -c "^| W" docs/kjtcom-report-v10.58.md` >= 1

---

### W4: Thompson Schema — Intranet Field Identification (P2)

**Context:** The intranet deployment will process different log sources than kjtcom. Each new source type may require new Thompson Indicator Fields. Identify these now so the schema can grow intentionally.

**Current schema v3 fields (kjtcom — YouTube content):**
`t_any_names`, `t_any_people`, `t_any_cities`, `t_any_states`, `t_any_counties`, `t_any_countries`, `t_any_country_codes`, `t_any_regions`, `t_any_coordinates`, `t_any_geohashes`, `t_any_keywords`, `t_any_categories`, `t_any_actors`, `t_any_roles`, `t_any_shows`, `t_any_cuisines`, `t_any_dishes`, `t_any_eras`, `t_any_continents`

**New intranet log sources and candidate fields:**

| Log Source | New t_any_* Fields | Rationale |
|-----------|-------------------|-----------|
| Documents (docx, pdf) | `t_any_authors`, `t_any_titles`, `t_any_dates`, `t_any_orgs`, `t_any_topics` | Author attribution, document metadata, organizational tagging |
| Spreadsheets (xlsx, csv) | `t_any_columns`, `t_any_metrics`, `t_any_units` | Column headers as searchable fields, numeric context |
| Meeting transcripts (mp3) | `t_any_speakers`, `t_any_action_items`, `t_any_decisions` | Who said what, what was decided, what needs follow-up |
| Gmail / Calendar | `t_any_senders`, `t_any_recipients`, `t_any_subjects`, `t_any_attachments` | Email graph, calendar event metadata |
| Slack channels | `t_any_channels`, `t_any_threads`, `t_any_reactions` | Channel-level context, thread grouping |
| CRM API pulls | `t_any_accounts`, `t_any_contacts`, `t_any_deals`, `t_any_stages`, `t_any_values` | Sales pipeline, account hierarchy |
| Contractor portal | `t_any_certifications`, `t_any_skills`, `t_any_projects`, `t_any_contractors` | Contractor qualification data |

**Universal fields (apply to ALL intranet sources):**
- `t_any_tags` — user-applied tags (manual taxonomy)
- `t_any_record_ids` — external system IDs for cross-referencing (Salesforce IDs, Jira ticket numbers, etc.)
- `t_any_sources` — which system the entity originated from (gmail, slack, crm, etc.)
- `t_any_sensitivity` — classification level (public, internal, confidential)

**Output:** Append to `docs/evaluator-harness.md` as ADR-011 (Thompson Schema v4 — Intranet Extensions). This is a design decision, not implementation — the fields don't get created until intranet pipelines are built.

**Also note in ADR-011:** When pipeline consumes a new log source, the extraction prompt for that source defines which `t_any_*` fields it populates. Fields not relevant to a source are left empty (not omitted). The schema grows monotonically — fields are never removed, only added. This mirrors how SIEM platforms (Panther `p_any_*`, ECS) evolve their schemas.

---

## EXECUTION ORDER

1. **W2: Bourdain Phase 3** (P1, NZXTcos) — longest, start first
2. **W1: Claw3D gaps + connectors** (P1, tsP3-cos) — parallel with W2
3. **W3: Fix evaluator schema** (P1, after W1/W2) — needs working evaluator for report
4. **W4: Schema field identification** (P2) — ADR-011 append to harness
5. Post-flight + living docs + report

---

## COMPLETION CHECKLIST

```
[ ] W1: Visible gaps between all board pairs with animated connectors
[ ] W1: Connector labels readable in gaps
[ ] W1: Logger chip on middleware board
[ ] W1: 0 console errors, hover/zoom work
[ ] W2: Bourdain Phase 3 entities in staging (videos 61-90)
[ ] W2: checkpoint.json updated
[ ] W3: Evaluator produces valid report markdown
[ ] W3: grep -c "^| W" docs/kjtcom-report-v10.58.md >= 1
[ ] W4: ADR-011 in evaluator-harness.md
[ ] Post-flight passes (including G56 check)
[ ] Changelog updated
[ ] 4 artifacts: design, plan, build, report
```
