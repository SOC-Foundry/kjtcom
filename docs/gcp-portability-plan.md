# GCP Portability Plan - ADR-013

**Author:** Claude Code (v10.61)
**Date:** 2026-04-06
**Status:** Planning (no infrastructure built)
**Target project:** tachnet-intranet (GCP)

---

## 1. Registry Artifacts to Scrub and Transfer

| Artifact | Location | Scrub needed | Transfer method |
|----------|----------|-------------|-----------------|
| evaluator-harness.md | docs/ | Remove kjtcom-specific entity counts, keep ADRs/patterns/methodology | Copy, parameterize counts |
| middleware_registry.json | data/ | Replace kjtcom component IDs with generic template IDs | Export, parameterize |
| gotcha_archive.json | data/ | Keep universal gotchas (G1,G18,G19,G22), remove kjtcom-specific | Filter by `universal` tag |
| agent_scores.json | root | Do NOT transfer - this is kjtcom's history | Leave behind |
| claw3d_components.json | data/ | Rebuild for intranet board layout | New file |
| eval_schema.json | data/ | Transfer as-is - schema validation is universal | Copy |
| CLAUDE.md / GEMINI.md | root | Template the workstream section, keep rules | Parameterize |
| Pipeline configs | pipeline/config/ | New configs per intranet source type | New files |
| Pipeline scripts | pipeline/scripts/ | Phases 1-7 are universal, extraction prompts are source-specific | Copy scripts, new prompts |

### Scrub notes

- **evaluator-harness.md**: Replace hardcoded counts (e.g., "6,181 entities", "899 CalGold") with `${ENTITY_COUNT}` placeholders. ADR-001 through ADR-013 and all failure patterns apply universally.
- **gotcha_archive.json**: Tag each gotcha as `universal` or `kjtcom`. Universal gotchas include: G1 (heredocs/fish), G18 (CUDA OOM), G19 (fish -c wrappers), G22 (command ls). kjtcom-specific: G53 (Firebase MCP reauth), G56 (Claw3D fetch 404), G58 (artifact overwrite), G59 (chip text overflow).
- **CLAUDE.md / GEMINI.md**: The rules section (NEVER commit, NEVER heredocs, etc.) is universal. The project state table, workstreams, and completion checklist are per-project templates.

---

## 2. GCP Resource Build Order

### Phase A: VPC + IAM (tachnet-intranet project)

```
- VPC with private subnet for Ollama/GPU instances
- IAM roles: pipeline-executor, evaluator, deployer
- Service accounts for each role
- Firewall rules: allow internal traffic, SSH from bastion only
- Cloud NAT for outbound API calls (Gemini, geocoding)
```

### Phase B: Compute

```
- GPU instance for transcription (equivalent to NZXTcos RTX 2080)
  - n1-standard-8 + NVIDIA T4 (or L4 if budget allows)
  - Ollama + faster-whisper pre-installed
  - Spot/preemptible for batch transcription workloads
- CPU instance for middleware (evaluator, RAG, bot)
  - e2-standard-4, always-on
  - ChromaDB, Telegram bot, evaluator harness
- Cloud Run for pipeline scripts (serverless batch)
  - Each pipeline phase as a Cloud Run job
  - Triggered by Pub/Sub or Cloud Scheduler
```

### Phase C: Storage + Database

```
- Firestore (intranet-specific project)
  - Single collection pattern (same as kjtcom)
  - Thompson Schema v4 fields (ADR-011) activated per source
- Cloud Storage buckets:
  - gs://tachnet-audio/ (raw audio/transcripts)
  - gs://tachnet-checkpoints/ (pipeline state)
  - gs://tachnet-artifacts/ (generated docs)
- ChromaDB on CPU instance (or Vertex AI Vector Search if scale demands it)
```

### Phase D: Middleware deployment

```
- Ollama on GPU instance (Qwen 3.5-9B, Nemotron 4B)
- Evaluator harness + fallback chain (Qwen -> Gemini -> self-eval)
- Telegram bot as Cloud Run service (always-on min instance)
- Pub/Sub topic router for downstream consumers:
  - tachnet-entities (new entity events)
  - tachnet-evaluations (scored reports)
  - tachnet-alerts (degraded component notifications)
```

### Phase E: Pipeline configs

```
- Per-source extraction prompts:
  - Gmail threads -> entity extraction
  - Slack channels -> entity extraction
  - CRM records -> entity extraction
  - Internal docs -> entity extraction
  - Meeting recordings -> transcribe + extract
- Thompson Schema v4 fields (ADR-011) activated per source
- t_any_sources field for source differentiation (analogous to t_any_shows)
- Firestore triggers -> Pub/Sub -> tachtrack.com portals
```

---

## 3. Harness Readiness Checklist Before Intranet Buildout

```
[ ] Evaluator produces scored reports without human intervention (G55/G57 fully resolved)
[ ] generate_artifacts.py respects immutability (G58 resolved, ADR-012)
[ ] All gotchas tagged universal vs kjtcom-specific
[ ] Pipeline scripts parameterized (no hardcoded paths, env vars for all config)
[ ] Extraction prompt template documented (how to write one for a new source type)
[ ] Post-flight checks parameterized (site URL, bot handle, MCP list as config)
[ ] ADR registry portable (ADR-001 through ADR-013 apply to any IAO project)
[ ] Thompson Schema v4 fields defined (ADR-011)
[ ] Pub/Sub topic router designed (ADR for intranet, not yet written)
[ ] Claw3D PCB template exportable (board definitions as config, not hardcoded)
[ ] Canvas texture chip rendering approach documented (Pattern 18, G59)
[ ] Agent scoring schema documented (5-dim, append-only pattern)
[ ] Fallback chain order configurable (currently: Qwen -> Gemini -> self-eval)
```

### Blocking items

1. **Pipeline parameterization** - Currently pipeline scripts have hardcoded paths to `pipeline/data/bourdain/`, `pipeline/config/bourdain/`, etc. These must accept env vars or config file paths.
2. **Extraction prompt template** - No documented template for "how to write an extraction prompt for a new source type." The Bourdain prompt is the closest reference but needs generalization.
3. **Pub/Sub topic router ADR** - The event routing design for intranet consumers has not been written. This is a prerequisite for Phase D.

---

## 4. Pipeline Analysis - v1 vs v2

### v1: CalGold / RickSteves / TripleDB (3 separate pipelines)

| Attribute | CalGold | RickSteves | TripleDB |
|-----------|---------|------------|----------|
| Entities | 899 | 4,182 | 1,100 |
| Source | YouTube (Huell Howser) | YouTube (Rick Steves) | CSV import |
| Pipeline runs | Multiple (first pipeline, many hiccups) | Single clean run (reference) | Import script |
| Extraction prompt | `pipeline/config/calgold/` | `pipeline/config/ricksteves/` | N/A (structured import) |
| t_log_type | calgold | ricksteves | tripledb |
| Differentiation | Standalone pipeline | Standalone pipeline | Standalone pipeline |

**Observations:**
- Each pipeline has its own config directory, extraction prompt, and t_log_type.
- No shared infrastructure between pipelines.
- CalGold was the first attempt - most gotchas originated here.
- RickSteves was the cleanest run - use as operational reference.
- TripleDB was a structured import, not a full pipeline run.

### v2: Bourdain (single pipeline, multiple shows)

| Attribute | No Reservations | Parts Unknown |
|-----------|----------------|---------------|
| Entities | 351 (staging) | Phase 1 starting |
| Source | YouTube playlist | YouTube playlist |
| Pipeline | Shared `bourdain` pipeline | Shared `bourdain` pipeline |
| Extraction prompt | Shared, with show override | Shared, with show override |
| t_log_type | bourdain | bourdain |
| Differentiation | `t_any_shows: ["No Reservations"]` | `t_any_shows: ["Parts Unknown"]` |
| Dedup | Merges `t_any_shows` arrays for shared locations |

**Observations:**
- Single pipeline codebase, source-specific differentiation via `t_any_shows`.
- Extraction prompt includes show-specific override for `t_any_shows` field.
- Dedup logic handles cross-show entity merging.
- This is the model for intranet: single pipeline, `t_any_sources` for differentiation.

### Recommendation

Use **v2 (Bourdain)** as the template for intranet pipeline architecture:

1. **Single pipeline codebase** - phases 1-7 are universal (acquire, transcribe, extract, normalize, geocode, enrich, load).
2. **Source-specific extraction prompts** - each intranet source type (Gmail, Slack, CRM, docs, recordings) gets its own extraction prompt, analogous to the show-specific override in Bourdain.
3. **`t_any_sources` field** for differentiation - analogous to `t_any_shows`. An entity found in both Gmail and Slack gets `t_any_sources: ["Gmail", "Slack"]`.
4. **Dedup merges source arrays** - same logic as Bourdain's `t_any_shows` merge.
5. **RickSteves as operational reference** - cleanest execution history, use for pipeline ops documentation and SOP.

### Parts Unknown validation

Parts Unknown (W1, v10.61) validates the v2 model:
- Second show added under existing `bourdain` pipeline.
- `t_any_shows` correctly differentiates No Reservations vs Parts Unknown.
- Dedup merges arrays for locations visited in both shows.
- If this works cleanly, the intranet can confidently use the same pattern for `t_any_sources`.

---

*GCP Portability Plan v10.61 - April 6, 2026. ADR-013 addendum.*
