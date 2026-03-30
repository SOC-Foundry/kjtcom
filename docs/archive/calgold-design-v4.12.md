# CalGold - Design v4.12 (Phase 4 - Validation + Schema v3)

**Pipeline:** calgold (California's Gold - Huell Howser)
**Phase:** 4 (Validation)
**Iteration:** 12 (global counter)
**Executor:** Gemini CLI (Schema prep + Phases 1-5) + Claude Code (Phases 6-7 + Backfill)
**Date:** March 2026

---

## Objective

Two objectives in one iteration:

1. **Schema v3 Migration.** Add 6 new universal indicator fields to the Thompson Schema: t_any_actors, t_any_roles, t_any_cuisines, t_any_dishes, t_any_eras, t_any_continents. Update extraction prompts, schema.json, normalize and geocode scripts. Re-extract ALL 120 CalGold transcripts with the new prompt so every entity gets the new fields. Backfill t_any_continents and t_any_counties from geocode data.

2. **Phase 4 Validation.** Process CalGold videos 91-120 (30 new videos) through the full pipeline. Validate that zero interventions hold at the 120-video mark with the new schema. This is the last gate before Phase 5 production runs.

---

## Schema v3 - New Fields

| Field | Type | Description | CalGold Example |
|-------|------|-------------|-----------------|
| t_any_actors | array[string] | Named people featured | ["Huell Howser", "John Smith"] |
| t_any_roles | array[string] | Normalized role types | ["host", "park ranger", "historian"] |
| t_any_cuisines | array[string] | Cuisine categories | ["Mexican", "BBQ", "Bakery"] |
| t_any_dishes | array[string] | Specific food items | ["fish tacos", "date shake", "tri-tip"] |
| t_any_eras | array[string] | Historical periods mentioned | ["Gold Rush", "1920s", "Spanish Colonial"] |
| t_any_continents | array[string] | Continent(s) | ["North America"] |

**Existing field enhancement:**
- t_any_counties: Already in schema v2 but likely unpopulated. phase5_geocode.py will be enhanced to parse county from Nominatim address response.

**Cross-pipeline governance rule:** A t_any_* field must be meaningfully populated by at least 2 of 3 pipelines (calgold, ricksteves, tripledb). All 6 new fields pass this test at 3/3.

---

## Architecture Decisions

[DECISION] **Full Re-Extraction.** ALL 120 CalGold transcripts (videos 1-120) get re-extracted with the updated extraction_prompt.md. This ensures every entity has the 6 new fields populated from the transcript, not just the new batch. Phases 1-2 (acquire, transcribe) are incremental (only new videos 91-120). Phases 3-7 re-process ALL 120.

[DECISION] **Geocode Script Enhancement.** phase5_geocode.py enhanced to parse address.county from Nominatim response into t_any_counties. Also add continent lookup: a simple country-to-continent dictionary mapping applied during normalization or geocoding. No additional API calls needed - this data is already in the Nominatim response.

[DECISION] **Continent Lookup in Normalization.** phase4_normalize.py enhanced with a country-to-continent dictionary. When t_any_countries is populated, t_any_continents is auto-derived. CalGold always gets ["North America"]. RickSteves gets the correct continent per country.

[DECISION] **Schema Version Bump.** t_schema_version incremented from 2 to 3 for all entities. The schema.json config file updated with the new field mappings.

[DECISION] **Split-Agent Model (Proven x3).** Gemini CLI runs schema prep + phases 1-5 with `gemini --yolo`. Claude Code runs phases 6-7, backfill validation, and artifacts with `claude --dangerously-skip-permissions`.

[DECISION] **New Firestore Indexes.** Composite indexes added for each new t_any_* field + t_log_type after load completes.

[DECISION] **Extraction Prompt v3.** The extraction_prompt.md for CalGold is rewritten to include actors, roles, cuisines, dishes, and eras in the JSON output format. Every entity extracted must include these fields (empty arrays if not applicable).

---

## Success Criteria

| Criteria | Target | Measurement |
|----------|--------|-------------|
| Acquisition (new) | 30/30 (100%) | Audio file count delta |
| Transcription (new) | 30/30 (100%) | Transcript file count delta |
| Re-extraction (all) | 120/120 (100%) | All extracted JSON contains new fields |
| Geocoding | >95% | Nominatim + Places backfill |
| Enrichment | >95% | Google Places API |
| t_any_actors populated | >90% of entities | Spot-check |
| t_any_continents populated | 100% of entities | All CalGold = ["North America"] |
| t_any_counties populated | >80% of geocoded entities | Parsed from Nominatim |
| t_schema_version | 3 on ALL entities | Firestore query |
| Interventions (Gemini) | 0 | Count |
| Interventions (Claude) | 0 | Count |
| Security | Zero API keys in repo | grep scan |
| Artifacts | 4 mandatory docs | build, report, changelog, README |

---

## Gotchas Active

| ID | Gotcha | Prevention |
|----|--------|-----------|
| G2 | LD_LIBRARY_PATH for CUDA | RESOLVED - embedded in script + config.fish |
| G11 | API key leaks | NEVER cat config.fish |
| G13 | Nominatim misses niche names | Google Places backfill |
| G18 | Gemini 5-min timeout | Background transcription |
| G19 | Gemini runs bash | fish -c wrappers |
| G20 | Config.fish contains keys | grep only, never cat |
| G21 | CUDA OOM dual process | ONE transcription at a time |
| G22 | fish ls color codes | command ls or Python |

---

## Execution Flow

```
Gemini CLI (Section A):
  Step 0: Pre-flight
  Step 0.5: Schema v3 config changes
    - Update pipeline/config/calgold/schema.json (add 6 fields)
    - Update pipeline/config/calgold/extraction_prompt.md (add 6 fields to output)
    - Enhance phase4_normalize.py (continent lookup dictionary)
    - Enhance phase5_geocode.py (parse county from Nominatim)
  Step 1: Acquire videos 91-120 (30 new, checkpoint skips 1-90)
  Step 2: Transcribe videos 91-120 (30 new, background job)
  Step 3: Re-extract ALL 120 videos with v3 prompt (overwrite existing)
  Step 4: Re-normalize ALL 120 (new fields + continents)
  Step 5: Re-geocode ALL 120 (county parsing active)
  Handoff checkpoint

Claude Code (Section B):
  Step 6: Re-enrich ALL 120
  Step 7: Re-load ALL 120 (merge pattern, schema v3)
  Step 8: Post-flight (validate new fields populated)
  Step 9: Artifacts (4 mandatory)
```

---

## RickSteves v4.13 Dependency

After v4.12 completes and validates the schema v3 changes on CalGold, v4.13 will apply the same schema to RickSteves. The script enhancements (continent lookup, county parsing) made in v4.12 will carry forward. Only the extraction_prompt.md needs per-pipeline customization.

---

## TripleDB Migration Prep

Schema v3 is designed with TripleDB in mind. When TripleDB enters at v1.16:
- t_any_actors maps to owner_chef + "Guy Fieri"
- t_any_roles maps to role types from DDD
- t_any_cuisines maps to cuisine_type
- t_any_dishes maps to dishes[].dish_name
- t_any_eras: likely sparse for DDD
- t_any_continents: always ["North America"]
- t_any_counties: parsed from geocode

No schema changes will be needed for TripleDB onboarding.
