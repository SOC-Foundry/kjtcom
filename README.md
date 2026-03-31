# kjtcom

**Multi-pipeline location intelligence platform built on Iterative Agentic Orchestration (IAO)**

[![Flutter](https://img.shields.io/badge/Flutter-02569B?style=for-the-badge&logo=flutter&logoColor=white)](https://flutter.dev)
[![Firebase](https://img.shields.io/badge/Firebase-FFCA28?style=for-the-badge&logo=firebase&logoColor=black)](https://firebase.google.com)
[![Gemini](https://img.shields.io/badge/Gemini_Flash-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev)
[![Claude](https://img.shields.io/badge/Claude_Code-6B4FBB?style=for-the-badge&logo=anthropic&logoColor=white)](https://claude.ai)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](LICENSE)

---

kjtcom processes YouTube playlists into structured, searchable, geocoded Firestore databases. Each pipeline extracts entities (landmarks, trails, routes, restaurants) from video transcripts using LLM-powered extraction, normalizes them into the Thompson Indicator Fields (`t_any_*` universal indicator fields), enriches with Google Places and Nominatim, and serves them through a unified Flutter Web frontend with cross-dataset search.

The Thompson Indicator Fields are modeled after [Panther SIEM's](https://docs.panther.com/search/panther-fields) `p_any_*` indicator fields and [Elastic Common Schema](https://www.elastic.co/guide/en/ecs/current/index.html) - providing universal queryable fields across disparate data sources. The same normalization patterns power production SIEM migrations at [TachTech Engineering](https://tachtech.net).

Built entirely by LLM agents using IAO (Iterative Agentic Orchestration) - a methodology distilled from 48+ production iterations on [TripleDB](https://github.com/TachTech-Engineering/tripledb).

**kylejeromethompson.com** | **Phase 6b v6.16** | **Status: Phase 6b Design Contract DONE**

---

## Architecture

```
YouTube Playlist (per pipeline)
    | yt-dlp
    v
MP3 Audio
    | faster-whisper (CUDA)
    v
Timestamped Transcripts
    | Gemini 2.5 Flash API + pipeline extraction prompt
    v
Raw Extracted JSON
    | phase4_normalize.py + schema.json (Thompson Indicator Fields)
    v
Normalized JSONL (t_any_* indicator fields populated)
    | Nominatim (1 req/sec)
    v
Geocoded JSONL
    | Google Places API (New)
    v
Enriched JSONL (t_enrichment.google_places + t_enrichment.nominatim)
    | Firebase Admin SDK
    v
Cloud Firestore (kjtcom-c78cd, Blaze)
    | Cloud Functions (search API) + Flutter Web
    v
kylejeromethompson.com
```

---

## Data Architecture

kjtcom utilizes a **single-collection Firestore design** where all entities from all pipelines live together in a single `locations` collection. This allows for unified, cross-dataset search.

- **Discriminator**: The `t_log_type` field acts as the discriminator to filter by pipeline (e.g., `calgold`, `ricksteves`).
- **Querying**: Extensive use of `array-contains` queries enables searching across multiple attributes (keywords, categories, regions) without rigid schemas.
- **Indexes**: Composite indexes are defined in `firestore.indexes.json` to support multi-field filtering and sorting.
- **Environments**: A multi-database setup (`(default)` for production, `staging` for pipeline runs) safely separates work in progress.
- **Pricing**: Powered by the Firebase Blaze plan to support Cloud Functions and multi-database architectures.
- **Enforcement**: The field convention is enforced purely by the pipeline scripts (specifically `phase4_normalize.py`), not by the database itself.

---

## Thompson Indicator Fields (`t_any_*`)

The Thompson Indicator Fields provide universal indicator fields across all pipeline datasets - the same pattern SIEM platforms use to normalize disparate log sources into a single queryable schema.

**Standard Fields** (present on every document):

| Field | Type | Description |
|-------|------|-------------|
| `t_log_type` | string | Pipeline ID (discriminator) |
| `t_row_id` | string | Unique entity ID |
| `t_event_time` | timestamp | Source event time |
| `t_parse_time` | timestamp | Pipeline processing time (UTC) |
| `t_source_label` | string | Human-readable pipeline name |
| `t_schema_version` | int | Schema version for this pipeline |

**Indicator Fields** (universal cross-pipeline arrays):

| Field | Type | Description | Examples |
|-------|------|-------------|----------|
| `t_any_names` | array[string] | All entity names | `["eiffel tower", "la tour eiffel"]` |
| `t_any_people` | array[string] | All people mentioned | `["rick steves", "huell howser"]` |
| `t_any_cities` | array[string] | All city names | `["paris", "los angeles"]` |
| `t_any_states` | array[string] | All state abbreviations | `["ca", "ny"]` |
| `t_any_counties` | array[string] | All county names | `["los angeles county"]` |
| `t_any_countries` | array[string] | All country names (v2) | `["france", "us"]` |
| `t_any_regions` | array[string] | Sub-country regions (v2) | `["bavaria", "tuscany"]` |
| `t_any_coordinates` | array[map] | All lat/lon pairs | `[{"lat": 48.85, "lon": 2.29}]` |
| `t_any_geohashes` | array[string] | Geohash prefixes for proximity | `["u09t", "u09tv"]` |
| `t_any_keywords` | array[string] | All searchable terms | `["gothic", "museum", "art"]` |
| `t_any_categories` | array[string] | Normalized category tags | `["landmark", "restaurant"]` |
| `t_any_actors` | array[string] | Named people featured (v3) | `["rick steves", "local guide"]` |
| `t_any_roles` | array[string] | Normalized role types (v3) | `["host", "guide", "historian"]` |
| `t_any_shows` | array[string] | Show name(s) (v3) | `["rick steves' europe", "california's gold"]` |
| `t_any_cuisines` | array[string] | Cuisine categories (v3) | `["french", "italian"]` |
| `t_any_dishes` | array[string] | Specific food items (v3) | `["croissant", "paella"]` |
| `t_any_eras` | array[string] | Historical periods mentioned (v3) | `["medieval", "roman"]` |
| `t_any_continents` | array[string] | Continent(s) (v3) | `["europe", "asia"]` |
| `t_any_urls` | array[string] | Associated URLs | `["https://example.com"]` |
| `t_any_video_ids` | array[string] | Source YouTube video IDs | `["dQw4w9WgXcQ"]` |

**Enrichment** (`t_enrichment.*`): Google Places ratings, open/closed status, websites. Nominatim geocoding. Extensible to any enrichment source via named keys.

**Source** (`source.*`): Pipeline-specific raw data. Schema varies per pipeline, defined in `pipeline/config/{pipeline_id}/schema.json`.

---

## Pipelines

| Pipeline (`t_log_type`) | Source | Entity Type | Videos | Entities | Status |
|-------------------------|--------|-------------|--------|----------|--------|
| `calgold` | California's Gold (Huell Howser) | landmark | 390 | 899 | Phase 5 Production Run DONE |
| `ricksteves` | Rick Steves' Europe | destination | 1,865 | 1,035 | Phase 4 Validation Complete (Schema v3) |
| `tripledb` | Diners, Drive-Ins and Dives | restaurant | 805 | - | Migration candidate |
| `bourdain` | Anthony Bourdain: Parts Unknown | destination | 104 | - | Pending onboarding |

Each pipeline requires only 4 config files - no code changes to shared scripts:

```
pipeline/config/{pipeline_id}/
  pipeline.json           # metadata (display name, entity type, icon, color)
  schema.json             # Thompson Indicator Fields indicator mappings
  extraction_prompt.md    # Gemini Flash extraction prompt
  playlist_urls.txt       # YouTube video IDs
```

---

## Setup

```fish
# Clone
git clone git@github.com:SOC-Foundry/kjtcom.git
cd kjtcom

# Environment (fish shell)
set -x GEMINI_API_KEY "..."
set -x GOOGLE_PLACES_API_KEY "..."
set -x GOOGLE_APPLICATION_CREDENTIALS "$HOME/.config/gcloud/kjtcom-sa.json"

# Firebase
firebase use kjtcom-c78cd
firebase deploy --only firestore:rules,firestore:indexes

# Validate
yt-dlp --flat-playlist --print "%(id)s %(title)s" \
  "https://www.youtube.com/playlist?list=PLr7fFk3JB5ic-nEyrqLj6MGDox5DO8oMl" | wc -l
```

## Running a Pipeline

```fish
# Phase 1-7: Process 30 videos through the full pipeline
python3 pipeline/scripts/phase1_acquire.py    --pipeline calgold --limit 30
python3 pipeline/scripts/phase2_transcribe.py --pipeline calgold --limit 30
python3 pipeline/scripts/phase3_extract.py    --pipeline calgold --limit 30
python3 pipeline/scripts/phase4_normalize.py  --pipeline calgold --limit 30
python3 pipeline/scripts/phase5_geocode.py    --pipeline calgold --limit 30
python3 pipeline/scripts/phase6_enrich.py     --pipeline calgold --limit 30
python3 pipeline/scripts/phase7_load.py       --pipeline calgold --database staging
```

By default, data is saved in `pipeline/data/{pipeline_id}/` per stage.

---

## File Structure

```
kjtcom/
  app/                    Flutter Web frontend
  pipeline/
    scripts/              Shared pipeline stages (7 phases + utilities)
    config/               Per-pipeline configuration (schema.json, prompts)
    data/                 Per-pipeline data (gitignored)
  functions/              Firebase Cloud Functions (search API)
  docs/                   IAO artifacts (design, plan, build, report, changelog)
  requirements/           Environment manifests + install script
  CLAUDE.md               Agent instructions (Claude Code)
  GEMINI.md               Agent instructions (Gemini CLI)
```

---

## IAO Methodology

kjtcom is built using the Iterative Agentic Orchestration (IAO) methodology - a structured approach to running AI coding agents (Claude Code, Gemini CLI) against multi-phase data pipelines with zero-to-minimal human intervention. Distilled from 48+ production iterations on [TripleDB](https://github.com/TachTech-Engineering/tripledb).

IAO maps directly to the "harness engineering" pattern formalized by LangChain, Anthropic, and the broader agent ecosystem in 2026. The core principle: the model contains the intelligence; the harness makes it useful.

### IAO Components

| Component | Purpose | Implementation |
|-----------|---------|----------------|
| Agent Instructions | System prompt per agent | CLAUDE.md, GEMINI.md |
| Pipeline Scripts | Tool definitions | phase1_acquire.py through phase7_load.py |
| Gotcha Registry | Executable middleware (failure prevention) | G1-G25 documented patterns |
| Checkpoint Files | State persistence across agent handoffs | .checkpoint_enrich.json, handoff JSON |
| 4-Artifact Output | Trace analysis and improvement loop | build log, report, changelog, README |
| Split-Agent Model | Cross-provider subagent delegation | Gemini CLI (phases 1-5) + Claude Code (phases 6-7) |

### Split-Agent Execution

kjtcom uses a two-agent model validated across 5+ iterations with decreasing interventions:

- **Gemini CLI** (`gemini --yolo`): Phases 1-5 (acquire, transcribe, extract, normalize, geocode). Free-tier execution for mechanical pipeline work.
- **Claude Code** (`claude --dangerously-skip-permissions`): Phases 6-7 (enrich, load to Firestore) + post-flight validation and artifact production.
- **tmux runner** (`group_b_runner.sh`): Unattended production runs (Phase 5+) replace Gemini CLI for phases 1-5 when no agent reasoning is needed.
- **Handoff:** Gemini produces a checkpoint JSON consumed by Claude. Cross-provider subagent delegation.

**Agent performance across iterations:**

| Iteration | Phases 1-5 Executor | Ph 1-5 Interventions | Claude Interventions |
|-----------|---------------------|---------------------|---------------------|
| v2.9 | Gemini CLI | 3 | N/A (Gemini only) |
| v3.10 | Gemini CLI | 0 | 0 |
| v3.11 | Gemini CLI | 0 | 0 |
| v4.12 | Gemini CLI | 0 | 1 |
| v4.13 | Gemini CLI | 0 | 1 |
| v5.14 | tmux | 1 (CUDA OOM) | 0 |

Zero Gemini interventions across 4 consecutive iterations. Same model, better harness.

### The Nine Pillars

**Pillar 1 - Artifact Loop.** Every iteration produces four artifacts: design doc (living architecture), plan (execution steps), build log (session transcript), report (metrics + orchestration). Previous artifacts archive to `docs/archive/`. Agents never see outdated instructions.

**Pillar 2 - Agentic Orchestration.** The primary agent (Claude Code or Gemini CLI) orchestrates LLMs, MCP servers, scripts, APIs, and sub-agents. Agents CAN build and deploy. Agents CANNOT git commit or sudo. The human commits at phase boundaries.

**Pillar 3 - Zero-Intervention Target.** Every question the agent asks during execution is a failure in the plan document. Pre-answer every decision point. Measure plan quality by counting interventions - zero is the floor.

**Pillar 4 - Pre-Flight Verification.** Before execution begins, validate: previous docs archived, new design + plan in place, agent instructions updated, git clean, API keys set, build tools verified.

**Pillar 5 - Self-Healing Execution.** Errors are inevitable. Diagnose -> fix -> re-run. Max 3 attempts per error, then log and skip. Checkpoint after every completed step for crash recovery.

**Pillar 6 - Progressive Batching.** Start small. Graduate to production scale only after the small batch achieves zero interventions. 30 -> 100 -> 250 -> full dataset.

**Pillar 7 - Post-Flight Functional Testing.** Three tiers: Tier 1 (app bootstraps, console clean, changelog verified), Tier 2 (iteration-specific automated playbook), Tier 3 (hardening audit - Lighthouse, security headers, browser compat).

**Pillar 8 - Platform Constraints.** Flutter Web + Firebase (Blaze) + Cloud Functions. Google Places enrichment. Nominatim geocoding. CachyOS / fish shell. The non-negotiable architectural decisions that shape every tool choice.

**Pillar 9 - Continuous Improvement.** The methodology evolves alongside the project. Archive reviews, tool efficacy reports, technology radar, retrospectives. Static processes atrophy.

---

## Project Status

| Phase | Name | Status | Iteration |
|-------|------|--------|-----------|
| 0 | Scaffold & Environment | DONE | v0.5 |
| 1 | Discovery (30 videos) | DONE | v1.6, v1.7 |
| 2 | Calibration (60 videos) | DONE | v2.8, v2.9 |
| 3 | Stress Test (90 videos) | DONE | v3.10, v3.11 |
| 4 | Validation + Schema v3 (120 videos) | DONE | v4.12, v4.13 |
| 5 | Production Run (full datasets) | CalGold DONE | v5.14 |
| 6a | Flutter App - Discovery | DONE | v6.15 |
| 6b | Flutter App - Design Contract | DONE | v6.16 |
| 6c | Flutter App - Implementation | Pending | - |
| 6d | Flutter App - QA | Pending | - |
| 6e | Flutter App - Deploy | Pending | - |
| 7 | Firestore Load | Pending | - |
| 8 | Enrichment Hardening | Pending | - |
| 9 | App Optimization | Pending | - |
| 10 | Retrospective + Template | Pending | - |

---

## Tech Stack

| Component | Tool | Purpose |
|-----------|------|---------|
| Audio Download | yt-dlp | YouTube -> mp3 |
| Transcription | faster-whisper (CUDA) | mp3 -> timestamped JSON |
| Extraction | Gemini 2.5 Flash API | Transcript -> structured entity JSON |
| Normalization | Python + schema.json | Raw JSON -> Thompson Indicator Fields (t_any_*) |
| Geocoding | Nominatim (OSM) | Address/name -> lat/lon |
| Enrichment | Google Places API (New) | Rating, open/closed, website, phone |
| Database | Cloud Firestore (Blaze) | Denormalized documents, multi-database |
| Search API | Firebase Cloud Functions | Complex cross-dataset queries |
| Frontend | Flutter Web | Unified search, map, list views |
| Hosting | Firebase Hosting | CDN, preview channels, SSL |
| Orchestration | Claude Code (Opus) / Gemini CLI | IAO agent execution |

---

## Hardware

```
NZXTcos (Primary Dev)
CPU:  Intel Core i9-13900K (24-core, 5.8 GHz)
RAM:  64 GB DDR4
GPU:  NVIDIA GeForce RTX 2080 SUPER (8 GB VRAM)
OS:   CachyOS (Arch-based) / KDE Plasma 6.6.2 / Wayland
```

---

## Cost

| Component | Cost |
|-----------|------|
| All local inference (transcription, normalization) | Free |
| Gemini 2.5 Flash API | Free tier |
| Nominatim geocoding | Free (OSM) |
| Google Places API | Free tier |
| Cloud Firestore (Blaze, pay-as-you-go) | ~$0.50/month |
| Cloud Functions | ~$0.40/month |
| Firebase Hosting | Free |
| **Total** | **~$1-3/month** |

---

## Future Directions

**Meta/Hyperagents integration.** Evaluating [HyperAgents](https://github.com/facebookresearch/Hyperagents) (Meta FAIR) for self-improving pipeline optimization - letting a meta-agent evolve extraction prompts and schema mappings across iterations. The IAO artifact loop provides natural fitness signals (extraction success rate, geocoding hit rate, enrichment match rate) that a hyperagent could optimize against.

**Multi-LLM pipeline stages.** Currently Gemini Flash handles extraction. Future iterations will benchmark extraction quality across Claude Sonnet, Gemini Flash, GPT-4o, and local models (Nemotron, Qwen) per pipeline. The schema.json already decouples extraction from normalization - swapping the LLM requires only changing the extraction prompt, not the normalization pipeline.

**SIEM migration tooling.** The Thompson Indicator Fields normalization pipeline is structurally identical to SIEM log normalization. Each `schema.json` is a field mapping artifact - the same deliverable produced during Splunk-to-Panther or Splunk-to-CrowdStrike migrations. Future work explores generating these mappings automatically from source SIEM configurations.

---

## Changelog

**v6.16 (Phase 6b - Design Contract)**
- Synthesized 8-site scrape archive + Panther SIEM into three-file design contract
- 100+ design tokens, 10 component blueprints, 3 interaction patterns documented
- Locked visual identity: dark SIEM aesthetic, Geist Sans/Mono, pipeline-colored dots
- Zero Flutter code changes. Specification-only phase. 0 interventions.

**v6.15 (Phase 6a - Discovery)**
- Scraped 8 public competitor sites via Playwright MCP (Pipeline, Investigation, Concierge)
- Selected Geist Sans/Mono as primary typographic reference (Scanner.dev)
- Validated dark SIEM aesthetic across Panther, Monad, Scanner.dev, GreyNoise

**v5.14 (CalGold Phase 5 - Production Run)**
- Full production run: 390/431 videos, 829 entities, 899 unique in staging
- Geocoding: 95%, Enrichment: 95%, Schema v3: 100%
- tmux 2-pass execution (600s + 1200s). 1 intervention (CUDA OOM recovery)
- Total platform: 1,934 entities (899 CalGold + 1,035 RickSteves)

**v4.13 (RickSteves Phase 4 - Validation + Schema v3)**
- Schema v3 migration: 7 new t_any_* fields including t_any_shows
- 150 videos (30 new + ALL 150 re-extracted). 1,035 unique RickSteves entities
- Schema v3 field rates: actors 100%, shows 100%, continents 99%, eras 73%
- CalGold backfill: 412 entities updated with t_any_shows
- Gemini: 0 interventions, Claude: 1. 33 countries
- Total platform: 1,447 entities (412 CalGold + 1,035 RickSteves)

**v4.12 (CalGold Phase 4 - Validation + Schema v3)**
- Schema v3 migration: 6 new t_any_* fields (actors, roles, cuisines, dishes, eras, continents)
- 120 videos, 300 unique CalGold entities. ALL re-extracted with v3 prompt
- Schema v3 validation: actors 100%, continents 100%, counties 84.1%, eras 82.4%
- Geocoding: 97.6%, Enrichment: 97.6%. Gemini: 0 interventions, Claude: 1
- Total platform: 969 entities (300 CalGold + 669 RickSteves) across 30 countries

**v3.11 (RickSteves Phase 3 - Stress Test)**
- Videos 91-120 processed via split-agent model: Gemini CLI (phases 1-5) + Claude Code (phases 6-7)
- 120 total videos, 669 unique RickSteves entities in Firestore staging
- Geocoding: 99.3%, Enrichment: 99.3% via Google Places
- New countries: Egypt, Ethiopia, Vatican City (30 total)
- Zero interventions for both agents
- Total platform: 887 entities (218 CalGold + 669 RickSteves) across 30 countries

**v3.10 (CalGold Phase 3 - Stress Test)**
- Videos 61-90 processed via split-agent model: Gemini CLI (phases 1-5) + Claude Code (phases 6-7)
- 90 total videos, 218 unique CalGold entities in Firestore staging
- Geocoding: 98% (Nominatim + Places backfill, 140 coords backfilled)
- Enrichment: 98% via Google Places (222/226)
- Zero interventions for both agents
- Total platform: 777 entities (218 CalGold + 559 RickSteves) across 29 countries

**v2.9 (RickSteves Phase 2 - Calibration)**
- Videos 31-90 processed via Gemini CLI (first Gemini execution on kjtcom)
- 494 new entities, 559 total RickSteves entities across 29 countries
- Geocoding: 99% (Nominatim + Places backfill)
- Enrichment: 99% via Google Places
- Dedup merges: 95 entities with multiple visits (implemented array merge in phase7_load.py)
- 3 interventions (LD_LIBRARY_PATH fix, transcription timeouts, load logic merge)
- Total platform: 777 entities (218 CalGold + 559 RickSteves)

**v2.8 (CalGold Phase 2 - Calibration)**
- 60 videos processed: 218 unique CalGold entities in staging (up from 56)
- Geocoding jumped from 43% to 97% via Google Places coordinate backfill
- Enrichment: 97% via Google Places
- Schema upgraded to v2 with t_any_countries: ["us"]
- 3 dedup merges validated across Phase 1 + Phase 2
- 418 total platform entities (218 CalGold + 200 RickSteves) across 24 countries

**v1.7 (RickSteves Phase 1 - Discovery)**
- Pipeline 2 live: Rick Steves' Europe, 30 videos, 200 unique destinations across 23 countries
- Thompson Indicator Fields evolved to v2: added t_any_countries, t_any_regions
- Geocoding: 98% (68% Nominatim + 66 backfilled from Google Places)
- Enrichment: 98% via Google Places (197/200)
- Cross-pipeline queries validated: keyword, country, geohash queries return results from both CalGold and RickSteves
- CalGold entities backfilled to schema v2 (56/56)
- Migrated phase3_extract.py from google.generativeai to google.genai
- 256 total entities in staging (56 CalGold + 200 RickSteves)
- 1 intervention (LD_LIBRARY_PATH for CUDA)

**v1.6 (CalGold Phase 1 - Discovery)**
- 30-video discovery batch: 30/30 acquired, 30/30 transcribed, 30/30 extracted
- 57 unique California locations normalized via Thompson Indicator Fields
- Geocoding: 43% via Nominatim (niche/historic locations missed)
- Enrichment: 100% match rate via Google Places API (New)
- 56 documents loaded to staging Firestore, all array-contains queries validated
- 3 interventions resolved (CUDA path, pip install, Places API key)

**v0.5 (Phase 0 - Scaffold)**
- Repo: git@github.com:SOC-Foundry/kjtcom.git
- Firebase: kjtcom (kjtcom-c78cd) under socfoundry.com, Blaze billing
- Monorepo scaffolded: app/, pipeline/, functions/, docs/
- Multi-database configured: (default) + staging, both us-central1
- Thompson Indicator Fields (t_any_*) designed and validated with test entity
- CalGold pipeline config: schema.json (14 indicator mappings), extraction_prompt.md
- Cloud Functions search endpoint deployed
- 431 CalGold playlist URLs validated via yt-dlp

---

## Author

**Kyle Thompson** - VP of Engineering & Solutions Architect @ [TachTech Engineering](https://tachtech.net)

Built as a platform for extracting, normalizing, and querying structured data from YouTube content - sharpening the same data pipeline skills used in production SIEM migrations for Fortune 50 customers.

---

## Citing

If you find the IAO methodology or Thompson Indicator Fields useful:

```
@misc{thompson2026iao,
  title={Iterative Agentic Orchestration: A Methodology for Agent-Driven Software Projects},
  author={Kyle Thompson},
  year={2026},
  organization={TachTech Engineering},
  url={https://github.com/TachTech-Engineering/tripledb}
}
```
Thompson Indicator Fields useful:

```
@misc{thompson2026iao,
  title={Iterative Agentic Orchestration: A Methodology for Agent-Driven Software Projects},
  author={Kyle Thompson},
  year={2026},
  organization={TachTech Engineering},
  url={https://github.com/TachTech-Engineering/tripledb}
}
```
