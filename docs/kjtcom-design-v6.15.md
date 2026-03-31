# kjtcom - Design v6.15 (Phase 6a - Discovery)

**Pipeline:** kjtcom (cross-pipeline Flutter app)
**Phase:** 6a (Discovery - Playwright competitor scraping)
**Iteration:** 15 (global counter)
**Executor:** Gemini CLI (Playwright MCP scraping)
**Machine:** tsP3-cos (ThinkStation P3 Ultra SFF G2)
**Date:** March 2026

---

## Objective

Scrape 8 public competitor/inspiration sites via Playwright MCP across 3 categories (pipeline/SIEM platforms, investigation tools, boutique travel concierge). Capture desktop and mobile screenshots, accessibility snapshots, and UX patterns. Produce a raw scrape archive with per-site analysis and a cross-category UX synthesis document.

The PRIMARY design reference is Panther SIEM (tachtech.runpanther.net) - a production SIEM platform that kjtcom's query UX should closely mimic. Panther is behind Okta MFA with short session timeouts, and even with successful authentication Playwright would not navigate to the correct saved search page. Three screenshots and an HTML mockup are pre-staged in `app/design-brief/panther/` as static reference material.

This is the first kjtcom iteration on tsP3-cos. Full environment setup is included.

---

## Machine Context

tsP3-cos is a dedicated development machine that has NOT been used for kjtcom before. All environment setup (SSH keys, repo clone, API keys, Flutter, Gemini CLI, Claude Code) must be completed before agent execution.

| Component | Value |
|-----------|-------|
| Machine | Lenovo ThinkStation P3 Ultra SFF G2 |
| CPU | Intel Core Ultra 9 285 (24 cores) @ 6.50 GHz |
| GPU | NVIDIA RTX 2000 / 2000E Ada Generation |
| RAM | 62.10 GiB |
| Disk | 911.79 GiB ext4 (12% used) |
| OS | CachyOS x86_64, kernel 6.19.10-1-cachyos |
| Shell | fish 4.5.0 |
| DE | KDE Plasma 6.6.3 (KWin/Wayland) |
| Terminal | Konsole 25.12.3 |
| Hostname | tsP3-cos |
| User | kthompson |

---

## Architecture Decisions

[DECISION] **Panther is the primary site to mimic.** tachtech.runpanther.net is the #1 design reference for kjtcom's query module. The dark query editor, results table with single-line rows, click-to-expand JSON detail panel, and filter-by-value interaction are all drawn directly from Panther's PantherFlow search UI. Screenshots, and an HTML mockup translating the Panther patterns to kjtcom's data model, are pre-staged at `app/design-brief/panther/`.

[DECISION] **Screenshots + mockup for Panther, Playwright for public sites.** Panther is behind Okta MFA with short session timeouts. Even with successful auth, Playwright would land on the Okta dashboard, not the specific saved search page needed. The correct page (a saved PantherFlow query with results) requires manual navigation through Panther's UI. Three production screenshots and one HTML mockup are provided instead. The 8 public competitor sites are scraped via Playwright normally.

[DECISION] **NoSQL query syntax, not PantherFlow.** The query module uses Firestore NoSQL syntax (`t_any_cuisines contains "French" AND t_any_shows == "Rick Steves' Europe"`), not Panther's piped PantherFlow syntax. The LAYOUT and INTERACTION patterns come from Panther. The SYNTAX is kjtcom's own.

[DECISION] **Live Firestore frontend.** The NoSQL query box queries the production (default) Firestore `locations` collection directly in real time. Every search hits the live database - there is no local copy, cached subset, search index replica, or intermediate API layer. When new pipeline data is loaded (TripleDB, Bourdain), those entities surface in query results immediately with zero app-side changes. The result count displayed in the UI is the real document count, not an approximation. This means Firestore composite indexes on `t_any_*` fields must be provisioned to support the query patterns exposed in the UI. Index provisioning is Phase 6c territory.

[DECISION] **P3 for app development, NZXTcos for pipeline throughput.** Phase 5 production runs (transcription, extraction) continue on NZXTcos (RTX 2080 SUPER for CUDA). Phase 6 app work runs on tsP3-cos. No CUDA dependency for Playwright scraping or Flutter development.

[DECISION] **Gemini CLI for 6a Discovery.** Playwright scraping is mechanical work. Gemini CLI handles MCP tool calls well and is free-tier. Same agent assignment as the methodology doc specifies.

[DECISION] **globe_hero.jpg as static splash.** The Nano Banana-generated globe image (`app/assets/globe_hero.jpg`) serves as the static background behind the query box. Three.js interactive globe is Phase 6c territory. For 6a, the image informs the visual direction during scraping.

---

## Environment Setup (One-Time, tsP3-cos)

### Prerequisites

The plan includes complete setup steps for tsP3-cos. These run BEFORE the Gemini CLI agent launches.

| Dependency | Purpose | Install Method |
|------------|---------|---------------|
| SSH key | GitHub push/pull | ssh-keygen + GitHub deploy key |
| Git | Version control | pacman (likely pre-installed) |
| Node.js + npm | Gemini CLI, Playwright, tooling | pacman or nvm |
| Gemini CLI | Agent executor for 6a | npm install -g @anthropic-ai/gemini-cli (verify current package name) |
| Claude Code | Agent executor for 6c-6e | npm install -g @anthropic-ai/claude-code (verify current package name) |
| Flutter | App development (6c+) | yay -S flutter (AUR) or manual install |
| Chromium | Playwright browser target | pacman -S chromium |
| Python 3 | Pipeline scripts (not needed for 6a but needed for full repo) | pacman (likely pre-installed) |
| Firebase CLI | Deployment (6e) | npm install -g firebase-tools |
| API keys | Gemini API, Google Places, Firebase SA | config.fish env vars |

### API Keys Required

| Key | Env Var | Purpose |
|-----|---------|---------|
| Gemini API Key | GEMINI_API_KEY | Gemini CLI agent + Flash API |
| Google Places API Key | GOOGLE_PLACES_API_KEY | Enrichment (Phase 6-7) |
| Firebase SA credentials | GOOGLE_APPLICATION_CREDENTIALS | Firestore access |
| Anthropic API Key | ANTHROPIC_API_KEY | Claude Code (Phase 6c+) |

All keys go in `~/.config/fish/config.fish` as `set -gx` exports. NEVER cat this file (G20).

---

## Primary Design Reference: Panther SIEM

**Site:** tachtech.runpanther.net
**Access:** Okta MFA (not scrapeable - even with auth, Playwright cannot reach the saved search page)
**Location:** `app/design-brief/panther/`

### Pre-Staged Materials

| File | What It Shows |
|------|---------------|
| panther-search-results.png | PantherFlow query editor (line-numbered, syntax-highlighted), results table with single-line rows, column headers (TIME, DATABASE, LOG TYPE, EVENT), pipeline-colored log type badges |
| panther-json-detail.png | Click-to-expand JSON payload on right panel. Nested field display (geographicalContext, debugContext). "Filter by value" tooltip on field values. |
| panther-filter-by-value.png | After clicking "Filter by value" on a field, new query line appended (line 3: `where client.userAgent.os == 'Mac OS X'`). Shows the add-filter-from-detail UX pattern. |
| kjtcom-query-mockup.html | HTML mockup translating Panther patterns to kjtcom's data model. Dark query editor with Thompson Indicator Field syntax, entity results rows with pipeline-colored dots, JSON detail panel with +filter/-exclude buttons. |

### What to Mimic From Panther

- **Query editor:** Dark background, line-numbered, syntax-highlighted input area
- **Results table:** Single-line rows with fixed columns, colored badges per log type
- **JSON detail panel:** Slides in from right on row click, hierarchical field display
- **Filter-by-value:** Click a value in the JSON panel to append it as a query clause
- **Search button:** Green CTA, right-aligned in query editor
- **Tab navigation:** Results / Visualizations tabs below the query editor

### What Changes for kjtcom

- **Syntax:** PantherFlow piped queries -> NoSQL flat syntax (`field operator "value" AND ...`)
- **Data:** Log events -> location entities
- **Columns:** TIME/DATABASE/LOG TYPE/EVENT -> NAME/CITY/COUNTRY/SHOW
- **Badges:** Log type badges -> pipeline-colored dots (CalGold gold, RickSteves blue, TripleDB red, Bourdain purple)
- **Tabs:** Results/Visualizations -> Results/Map/Globe
- **Detail panel:** Add +filter/-exclude buttons on each field value

---

## Scraping Targets (8 Public Sites)

### Category 1: Pipeline / SIEM Platforms (Primary Inspiration)

These define the core visual identity. kjtcom is a peer of these tools.

| # | Site | URL | What to Capture |
|---|------|-----|-----------------|
| 1 | Monad | https://www.monad.com/ | Security data pipeline UX. Normalize, filter, enrich, route - identical to kjtcom's 7-phase pipeline. Dark theme, clean layout. Highest priority peer. |
| 2 | Scanner.dev | https://scanner.dev/ | SIEM data lake with query-first UX. Geist font family (Sans + Mono) - carry this into kjtcom. Product section layout. |
| 3 | GreyNoise Viz | https://viz.greynoise.io/ | Globe visualization, threat intel dashboard, green-on-dark aesthetic. Font treatment and data density. |
| 4 | Palantir Foundry | https://www.palantir.com/platforms/foundry/ | Enterprise data platform aesthetic. Entity relationship graphs, map overlays on dark tiles. |

### Category 2: Investigation / Intelligence Tools

These inform the query and exploration UX.

| # | Site | URL | What to Capture |
|---|------|-----|-----------------|
| 5 | Maltego | https://www.maltego.com/ | Entity graph visualization, connection lines between data points, investigation-style UX. |
| 6 | Cribl | https://cribl.io/ | Observability pipeline, data routing visualization, pipeline-as-product UX. |

### Category 3: Boutique Travel Concierge

These inform the content presentation layer - how entities look to end users.

| # | Site | URL | What to Capture |
|---|------|-----|-----------------|
| 7 | Black Tomato | https://www.blacktomato.com/ | Bespoke adventure travel, cinematic hero imagery, editorial storytelling. |
| 8 | Abercrombie & Kent | https://www.abercrombiekent.com/ | Expedition-grade travel, expert guide profiles, curated collections. |

---

## Scraping Process

For each of the 8 public sites, Playwright captures:

1. **Desktop screenshot** (1440x900) - full page
2. **Mobile screenshot** (375x812) - full page
3. **Accessibility snapshot** - DOM structure, ARIA labels, semantic elements
4. **Scrolled sections** - hero, navigation, product sections, footer

Per-site scrape output: `app/scrape-archive/{site-name}/`
- `desktop.png`
- `mobile.png`
- `accessibility.json`
- `scrape.md` (agent's analysis: fonts, colors, spacing, card layouts, search UX, navigation)

### Per-Site scrape.md Template

Each scrape.md should document:
- **Font stack** (inspect primary headings, body, mono/code)
- **Color tokens** (background, text primary/secondary, accent, border)
- **Spacing system** (padding, margins, gaps between sections)
- **Card/tile layouts** (if present)
- **Search/query UX** (if present - bar placement, autocomplete, results layout)
- **Navigation patterns** (header, sidebar, tabs)
- **Hero treatment** (imagery, gradient overlays, text positioning)
- **Category tag:** [PIPELINE] or [INVESTIGATION] or [CONCIERGE]

---

## Synthesis Document

After all 8 sites are scraped + Panther reference is reviewed, produce:

**`app/scrape-archive/ux-analysis.md`** - Cross-category synthesis with:

1. **Panther (primary reference):** NoSQL query editor layout specification, results table format, JSON detail panel, filter-by-value interaction pattern, adaptation notes for kjtcom. Reference the mockup at `app/design-brief/panther/kjtcom-query-mockup.html` as the target UX.
2. **Layer 1 (Pipeline tools - Monad, Scanner, GreyNoise, Palantir):** Common dark surface patterns, typography choices, data confidence indicators. How these support or refine the Panther-derived patterns.
3. **Layer 2 (Investigation tools - Maltego, Cribl):** Entity relationship patterns, data routing visualization, connection line styles.
4. **Layer 3 (Travel concierge - Black Tomato, A&K):** Editorial card layouts, imagery treatment, destination presentation authority.
5. **Convergence points:** Where 2+ categories agree (dark surfaces, card patterns, green accents).
6. **Conflicts:** Where categories diverge and which direction kjtcom should take.
7. **Preliminary token recommendations:** Font stacks, color palette direction, spacing scale.

---

## Success Criteria

| Criteria | Target |
|----------|--------|
| Public sites scraped | 8/8 |
| Desktop screenshots captured | 8/8 |
| Mobile screenshots captured | 8/8 |
| Accessibility snapshots | 8/8 |
| Per-site scrape.md | 8/8 |
| Panther reference archived in design-brief | 3 screenshots + 1 mockup |
| ux-analysis.md produced (Panther as primary) | Yes |
| Interventions (Gemini) | 0 |
| Artifacts | 4 mandatory docs |

---

## Gotchas Active

| ID | Gotcha | Prevention |
|----|--------|-----------|
| G11 | API key leaks | NEVER cat config.fish (G20 also) |
| G18 | Gemini 5-min timeout | Scraping is fast, should not hit timeout. If a site takes >60s, skip and note in scrape.md. |
| G19 | Gemini runs bash | fish -c wrappers for all commands |
| G20 | Config.fish contains keys | grep only, never cat |
| G26 | Playwright bot detection | Some sites (Palantir, GreyNoise) may block headless browsers. Capture what's available, document failures. |
| G27 | P3 first-run setup | Full environment setup in plan Section A. Verify BEFORE agent launch. |
| G28 | Firecrawl cert failures | NOT USING Firecrawl for 6a. Playwright only. |
| G29 | Panther MFA blocks scraping | Pre-staged screenshots + mockup in app/design-brief/panther/. Do NOT attempt to scrape Panther. |

---

## Phase Structure Reference

| Phase | Name | Status | Iteration |
|-------|------|--------|-----------|
| 0 | Scaffold & Environment | DONE | v0.5 |
| 1 | Discovery (30 videos) | DONE | v1.6, v1.7 |
| 2 | Calibration (60 videos) | DONE | v2.8, v2.9 |
| 3 | Stress Test (90 videos) | DONE | v3.10, v3.11 |
| 4 | Validation + Schema v3 (120 videos) | DONE | v4.12, v4.13 |
| 5 | Production Run (full datasets) | CalGold IN PROGRESS | v5.14 |
| 6a | Flutter App - Discovery | IN PROGRESS | v6.15 |
| 6b | Flutter App - Design Contract | Pending | - |
| 6c | Flutter App - Implementation | Pending | - |
| 6d | Flutter App - QA | Pending | - |
| 6e | Flutter App - Deploy | Pending | - |
| 7 | Firestore Load | Pending | - |
| 8 | Enrichment Hardening | Pending | - |
| 9 | App Optimization | Pending | - |
| 10 | Retrospective + Template | Pending | - |

---

## Query Module Design Direction (Locked for 6b)

The primary module of kylejeromethompson.com is a NoSQL query box. The Panther screenshots and HTML mockup in `app/design-brief/panther/` define the target UX.

**Data architecture:** The query box is a live, real-time frontend to the entire production (default) Firestore `locations` collection. Every query translates directly to a Firestore compound query - no intermediate API, no cached subset, no search replica. The full database is the app's data source. When new pipelines are loaded, their entities appear in results immediately.

**Layout (from Panther):**
- Black/dark background (#0D1117) for the query editor area
- Green terminal font (Geist Mono, #4ADE80) for query text
- Syntax highlighting: field names in blue (#79C0FF), operators in red (#FF7B72), values in light blue (#A5D6FF)
- Green "Search" button right-aligned

**Results (from Panther):**
- Single-line rows below the query editor
- Pipeline-colored dot per row (CalGold #DA7E12, RickSteves #3B82F6, TripleDB #DD3333, Bourdain #8B5CF6)
- Columns: NAME, CITY, COUNTRY, SHOW
- Click a row to expand full entity JSON on the right panel

**JSON Detail Panel (from Panther):**
- Slides in from the right on row click
- Shows all t_any_* fields with values
- "+" filter and "-" exclude buttons on each field value
- Clicking "+" appends `AND t_any_field contains "value"` to the query
- Clicking "-" appends `AND t_any_field != "value"` to the query

**Background:**
- globe_hero.jpg behind the query box area, faded to ~15% opacity
- Slow animation (CSS rotation, parallax, or Three.js in 6c)

**Query syntax (NoSQL, NOT piped):**
```
t_any_cuisines contains "French" AND t_any_shows == "Rick Steves' Europe"
t_any_actors contains "Guy Fieri"
t_any_dishes contains "gelato" AND t_any_continents == "Europe"
```

This direction is LOCKED. Phase 6b (Design Contract) will formalize these patterns into design-tokens.json and component-patterns.md.

---

## Typography (LOCKED)

| Usage | Font | Source |
|-------|------|--------|
| Headings, body, UI | Geist Sans | Scanner.dev / Vercel |
| Query bar, field names, data values | Geist Mono | Scanner.dev / Vercel |
| Fallback body | Inter | GreyNoise |
