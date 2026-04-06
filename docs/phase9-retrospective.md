# kjtcom - Phase 9 Retrospective (v9.27 - v9.53)

**Phase:** 9 (App Optimization & Evaluator Harness Development)
**Iterations:** 27 (v9.27 through v9.53)
**Total Entities:** 6,181
**Pipelines:** 3 (kjtcom, TripleDB, etc.)

---

## 1. Workstream Inventory

| Iteration | W# | Name | Priority | Planned Outcome | Actual Outcome | Notes |
|-----------|----|------|----------|-----------------|----------------|-------|
| v9.27 | W1 | Gothic + cyberpunk visual refresh | N/A | - selective flourishes on the dark SIEM base. Goth... | **complete** | |
| v9.27 | W2 | IAO Pillar tab | N/A | - new tab alongside Results/Map/Globe. Renders the... | **complete** | |
| v9.27 | W3 | Map tab fix | N/A | - currently non-functional. Wire to production ent... | **complete** | |
| v9.27 | W4 | Globe tab fix | N/A | - currently non-functional. The globe_hero.jpg is ... | **complete** | |
| v9.27 | W5 | Search results layout | N/A | - pin results below query fields. Default to 20 re... | **complete** | |
| v9.27 | W6 | Trident graphic | N/A | - SVG rendering of the IAO trident: | **complete** | |
| v9.27 | W7 | 10 Pillar cards | N/A | - scrollable list of cards, each containing: | **complete** | |
| v9.27 | W8 | Project stats footer | N/A | - below the pillars: | **complete** | |
| v9.27 | W9 | Globe hero background | N/A | - globe_hero.jpg at 15% opacity (already exists as... | **complete** | |
| v9.27 | W10 | Continent breakdown cards | N/A | - one card per continent showing: | **complete** | |
| v9.27 | W11 | Country grid | N/A | - below continent cards, show all countries with e... | **complete** | |
| v9.27 | W12 | Pipeline distribution | N/A | - pie chart or bar showing CalGold/RickSteves/Trip... | **complete** | |
| v9.27 | W13 | Pagination dropdown | N/A | above results table: `Show: 20 | 50 | 100` (defaul... | **complete** | |
| v9.27 | W14 | Page navigation | N/A | below results table: `< Previous | Page 1 of 33 | ... | **complete** | |
| v9.28 | W1 | Gotcha tab | N/A | - new tab displaying the full gotcha registry (G1-... | **complete** | |
| v9.28 | W2 | Schema tab with query builder | N/A | - new tab listing all Thompson Indicator Fields. E... | **complete** | |
| v9.28 | W3 | Copy JSON button on detail panel | N/A | - when the detail panel opens for an entity, a cop... | **complete** | |
| v9.28 | W4 | Post-flight deploy testing | N/A | - every iteration must include `flutter build web`... | **complete** | |
| v9.29 | W1 | Mobile trident labels | N/A | - "Optimized performance" truncates on mobile. Sho... | **Unknown** | |
| v9.29 | W2 | Remove 1000-result Firestore limit | N/A | - we have 6,181 entities, not millions. Remove the... | **Unknown** | |
| v9.29 | W3 | Missing schema fields | N/A | - t_any_cuisines and potentially others are missin... | **Unknown** | |
| v9.29 | W4 | Quote cursor placement in schema builder | N/A | - clicking "+ Add to query" on a schema field appe... | **Unknown** | |
| v9.30 | W1 | Query field autocomplete | N/A | - as the user types `t_any_`, show a dropdown of m... | **complete** | |
| v9.30 | W2 | Fix quote typing (3rd attempt) | N/A | - users STILL cannot type inside quotes after sche... | **complete** | |
| v9.30 | W3 | Fix 1000-result limit (2nd attempt) | N/A | - the limit was supposedly removed in v9.29 but th... | **complete** | |
| v9.30 | W4 | Consistent mobile/web trident labels | N/A | - v9.29 was supposed to shorten labels but the web... | **complete** | |
| v9.31 | W1 | 1000-result limit (attempt #4) | N/A | - UI still shows "Showing 1000 of 1000+ results" a... | **complete** | |
| v9.31 | W2 | Quote cursor placement (attempt #4) | N/A | - typing inside quotes still doesn't work. The sha... | **complete** | |
| v9.31 | W3 | Autocomplete not showing | N/A | - the value_index.json and overlay widget were cre... | **complete** | |
| v9.31 | W4 | TripleDB results not populating | N/A | - TripleDB entities exist in production (1,100) bu... | **complete** | |
| v9.31 | W5 | Clear button | N/A | - add a clear/reset button between "locations" and... | **complete** | |
| v9.31 | W6 | Flutter dependency update | N/A | - update Flutter SDK and all pub dependencies in p... | **complete** | |
| v9.31 | W7 | Playwright MCP scrapes | N/A | - after deploy, use Playwright MCP to navigate to ... | **complete** | |
| v9.31 | W8 | Read the ENTIRE relevant file | N/A | (not just the function). Print line count and key ... | **complete** | |
| v9.31 | W9 | grep for ALL related patterns | N/A | across the entire app/ directory. Not just one fil... | **complete** | |
| v9.31 | W10 | Add debug prints | N/A | (`debugPrint()`) to trace execution at runtime. | **complete** | |
| v9.31 | W11 | Fix the actual root cause | N/A | based on what the diagnostic reveals. | **complete** | |
| v9.31 | W12 | Build and deploy. | N/A |  | **complete** | |
| v9.31 | W13 | Use Playwright MCP to scrape the live si... | N/A | and verify the fix. | **complete** | |
| v9.31 | W14 | Capture screenshot evidence | N/A | that the bug is resolved. | **complete** | |
| v9.32 | W1 | TripleDB t_any_shows casing data fix | N/A | - TripleDB entities store t_any_shows as title cas... | **Unknown** | |
| v9.32 | W2 | Add == and != operators | N/A | - equality and exclusion operators for the query p... | **Unknown** | |
| v9.32 | W3 | Sort detail panel fields alphabetically | N/A | - t_any_* field cards render in alphabetical order... | **Unknown** | |
| v9.32 | W4 | Quote cursor: new approach (attempt #5) | N/A | - schema builder appends WITHOUT quotes. User type... | **Unknown** | |
| v9.32 | W5 | Fix autocomplete (attempt #2) | N/A | - diagnostic-first to find why overlay doesn't sho... | **Unknown** | |
| v9.33 | W1 | (P0) Fix parser regression | N/A | - the v9.32 unquoted value regex broke quoted valu... | **Unknown** | |
| v9.33 | W2 | (P0) Restore quotes in schema builder + ... | N/A | - the v9.32 no-quotes approach was the wrong call.... | **Unknown** | |
| v9.33 | W3 | (P0) +filter uses ==, -exclude uses != | N/A | - detail panel buttons should use equality/exclusi... | **Unknown** | |
| v9.33 | W4 | (P1) Fix query feedback message | N/A | - the "Could not parse query" hint says `t_any_key... | **Unknown** | |
| v9.33 | W5 | (P1) Flutter dependency upgrade | N/A | - update pubspec.yaml constraints and migrate brea... | **Unknown** | |
| v9.34 | W1 | (P0) Fix quote cursor placement | N/A | - when schema builder or +filter/-exclude appends ... | **Unknown** | |
| v9.34 | W2 | (P0) Inline autocomplete (Panther-style) | N/A | - replace the overlay-based autocomplete with inli... | **Unknown** | |
| v9.34 | W3 | (P1) Fix == on array fields | N/A | - the +filter button now uses `==` but `==` on arr... | **Unknown** | |
| v9.34 | W4 | Field mode: | N/A | cursor on a word starting with `t_` -> suggest mat... | **Unknown** | |
| v9.34 | W5 | Value mode: | N/A | cursor after `contains "` or `== "` -> suggest mat... | **Unknown** | |
| v9.36 | W1 | Panther SIEM Scrape | P1 | Capture query editor UI from Kyle's live authentic... | **Unknown** | |
| v9.36 | W2 | Agent Evaluator Middleware | P1 | Scoring system for LLM/agent performance, merged w... | **Unknown** | |
| v9.36 | W3 | MCP Validation | P2 | First live test of all 4 MCP servers configured in... | **Unknown** | |
| v9.37 | W1 | Dart 3.9 + dependency upgrade | P1 | Update Dart SDK, all pubspec deps, flutter build w... | **complete** | |
| v9.37 | W2 | Dart MCP server | P1 | Install official Dart/Flutter MCP (requires Dart 3... | **complete** | |
| v9.37 | W3 | MCP fixes (G52, G53) | P1 | Firebase reauth, Firecrawl debug | **complete** | |
| v9.37 | W4 | Panther SIEM scrape | P1 | Complete W1 from v9.36 - CDP attach, DOM capture | **complete** | |
| v9.37 | W5 | Qwen middleware registry | P2 | Ingest docs/archive, build iteration efficacy regi... | **complete** | |
| v9.37 | W6 | GCP middleware architecture | P3 | Design only - portable evaluator LLM concept | **complete** | |
| v9.38 | W1 | RAG middleware | P1 | nomic-embed-text + ChromaDB + embed 141 archive fi... | **Unknown** | |
| v9.38 | W2 | OpenClaw + Telegram | P1 | Install OpenClaw, configure Telegram BotFather int... | **Unknown** | |
| v9.38 | W3 | Brave Search API | P1 | Replace/augment web search with Brave Search API f... | **Unknown** | |
| v9.38 | W4 | Claw3D prototype | P2 | Three.js IAO workspace visualization (Tab 7 or sta... | **Unknown** | |
| v9.38 | W5 | Evaluator enhancements | P1 | Token tracking, gotcha merge, cumulative leaderboa... | **Unknown** | |
| v9.38 | W6 | Architecture chart | P1 | Living .mmd file in docs/, linked from README | **Unknown** | |
| v9.38 | W7 | Portable template packaging | P2 | Consolidate all IAO components into stampable stru... | **Unknown** | |
| v9.39 | W1 | OpenClaw + Gemini engine | P1 | Fix G54 (tiktoken), install OpenClaw, configure Ge... | **complete** | |
| v9.39 | W2 | P3 Diligence event logging | P1 | iao_logger.py, wrap all existing scripts, JSONL ev... | **complete** | |
| v9.39 | W3 | IAO tab update | P2 | Update iao_tab.dart with revised 10 pillars (P3 ex... | **complete** | |
| v9.39 | W4 | README update | P2 | Revised pillar descriptions, architecture chart, c... | **complete** | |
| v9.40 | W1 | Fix /ask RAG context | P1 | ChromaDB chunks not reaching Gemini prompt. Bot re... | **complete** | |
| v9.40 | W2 | Telegram event logging | P1 | All inbound messages + outbound responses logged t... | **complete** | |
| v9.40 | W3 | Telegram UX | P2 | Default handler for plain text (respond with comma... | **complete** | |
| v9.40 | W4 | Dependency freshness | P1 | flutter pub upgrade, verify Dart MCP SDK constrain... | **complete** | |
| v9.40 | W5 | G51 permanent fix | P2 | Bake think:false into ALL Ollama calls project-wid... | **complete** | |
| v9.41 | W1 | Firestore dual retrieval path | P1 | Gemini Flash routes /ask to ChromaDB (dev history)... | **complete** | |
| v9.41 | W2 | Re-embed archive with v9.38-v9.40 docs | P1 | Run embed_archive.py so ChromaDB path is current. | **complete** | |
| v9.41 | W3 | Artifact automation scaffold | P2 | generate_artifacts.py + templates. Qwen/Gemini dra... | **complete** | |
| v9.41 | W4 | Rebuild iteration_registry.json | P2 | Re-run build_registry_v2.py. OOM blocker gone (RAG... | **deferred** | |
| v9.41 | W5 | Living doc updates | P3 | architecture.mmd, install.fish, changelog for W1-W... | **complete** | |
| v9.41 | W1 | ... | P1 | Complete | **complete** | |
| v9.42 | W1 | TripleDB county enrichment | P1 | Enrich 1,100 TripleDB entities with t_any_counties... | **complete** | |
| v9.42 | W2 | Bot resiliency (systemd + watchdog) | P1 | systemd service for telegram bot. Auto-restart on ... | **complete** | |
| v9.42 | W3 | Artifact workflow fix + Qwen accuracy | P1 | Fix draft promotion, Qwen cross-check, 45-min time... | **complete** | |
| v9.42 | W4 | Internet query stream (Brave Search) | P2 | 3rd /ask retrieval path: questions about external ... | **complete** | |
| v9.42 | W5 | Gotcha archive + harness registry | P2 | data/gotcha_archive.json for resolved gotchas. dat... | **complete** | |
| v9.42 | W6 | Intranet update artifact | P3 | Cross-project update doc with OpenClaw deployment,... | **complete** | |
| v9.43 | W1 | Bot session memory | P1 | Store last query context per Telegram user_id. "th... | **complete** | |
| v9.43 | W2 | Rating-aware queries | P1 | Add t_enrichment.google_places.rating to schema re... | **failed** | |
| v9.43 | W3 | Post-flight verification implementation | P1 | Add verification script + update evaluator prompt ... | **failed** | |
| v9.43 | W4 | Architecture diagram HTML page | P1 | Standalone HTML renderer for architecture.mmd. Dep... | **deferred** | |
| v9.43 | W5 | Qwen evaluator prompt overhaul | P2 | Fix MCP hallucination, require specific numbers, e... | **complete** | |
| v9.43 | W6 | Verify v9.42 data integrity | P2 | Confirm county enrichment results (918/1100?), ver... | **partial** | |
| v9.43 | W1 | ... | P1 | Complete | **complete** | |
| v9.44 | W1 | Fix Gemini Flash auth error | P1 | Diagnose and fix litellm.AuthenticationError from ... | **complete** | |
| v9.44 | W2 | Create Firestore composite index | P1 | Create index for orderBy on t_enrichment.google_pl... | **complete** | |
| v9.44 | W3 | Re-run bot session memory + rating queri... | P1 | The v9.43 code was written but couldn't execute du... | **complete** | |
| v9.44 | W4 | Post-flight verification pass | P1 | Run post_flight.py. All checks must pass. This was... | **complete** | |
| v9.44 | W5 | Doc recovery + archival enforcement | P2 | Recover any deleted docs from git. Add rm guard to... | **complete** | |
| v9.44 | W6 | Changelog and report quality fix | P2 | Update templates to eliminate TBD stubs. Fix Qwen ... | **complete** | |
| v9.45 | W1 | Major dep upgrade: mgrs_dart 2->3 + proj... | P1 | These block Dart MCP functionality. Breaking API c... | **deferred** | |
| v9.45 | W2 | Major dep upgrade: analyzer + _fe_analyz... | P1 | analyzer 10->12, _fe_analyzer_shared 93->98. Dev d... | **deferred** | |
| v9.45 | W3 | Minor dep upgrades: meta, test, test_api... | P1 | Batch upgrade. Lower risk. | **deferred** | |
| v9.45 | W4 | Post-upgrade verification | P1 | flutter analyze (0 issues), flutter test (15/15), ... | **deferred** | |
| v9.45 | W5 | Phase 10 readiness checklist | P2 | Audit all middleware components, verify install.fi... | **complete** | |
| v9.45 | W6 | Post-flight + Qwen Trident fix | P2 | Run post_flight.py. Fix Qwen evaluator to fill Tri... | **complete** | |
| v9.46 | W1 | Qwen evaluator harness | P1 | Create docs/evaluator-harness.md. Update run_evalu... | **deferred** | |
| v9.46 | W2 | README overhaul | P1 | Full review of all sections. Update stale content,... | **complete** | |
| v9.46 | W3 | Phase 9 final audit | P2 | Compare v9.27 (first Phase 9) to v9.46 (last). Doc... | **partial** | |
| v9.46 | W4 | Post-flight + middleware registry update | P2 | Post-flight pass. Update middleware_registry.json ... | **complete** | |
| v9.47 | W1 | Qwen harness refinement + validation | P1 | Fix workstream fidelity (no hallucinated W#s). Re-... | **partial** | |
| v9.47 | W2 | Pipeline phase review for Bourdain | P1 | Review all 7 pipeline phases (acquire -> load) and... | **complete** | |
| v9.47 | W3 | Deploy Claw3D to Firebase | P2 | Copy docs/claw3d-prototype/index.html to app/web/c... | **complete** | |
| v9.47 | W4 | Post-flight + Phase 9 close-out | P2 | Post-flight pass. Final Phase 9 changelog entry. A... | **complete** | |
| v9.48 | W1 | File management cleanup | P1 | Delete orphaned changelog-v*.md files. Ensure no d... | **complete** | |
| v9.48 | W2 | Qwen structural enforcement in Python | P1 | Parse design doc for W# count. Validate Qwen outpu... | **complete** | |
| v9.48 | W3 | Rebuild CLAUDE.md and GEMINI.md to 200+ ... | P1 | Restore full harness content that was trimmed in v... | **partial** | |
| v9.48 | W4 | Post-flight + final Phase 9 verification | P2 | Post-flight pass. Verify all living docs current. ... | **complete** | |
| v9.49 | W1 | Qwen schema-validated harness | P1 | Define strict JSON schema for evaluation output. B... | **complete** | |
| v9.49 | W2 | Fix execution order (build log paradox) | P1 | Evaluator stops reading current build log. Evaluat... | **complete** | |
| v9.49 | W3 | Middleware tab in Flutter app | P2 | Replace Gotcha tab with MW (Middleware) tab. Displ... | **complete** | |
| v9.49 | W4 | README overhaul (3-iteration cadence) | P2 | Full review. Update stale content. Verify all link... | **deferred** | |
| v9.49 | W5 | Post-flight + living docs | P3 | Post-flight pass. Update middleware_registry.json,... | **complete** | |
| v9.50 | W1 | Qwen harness bug fixes (3 patterns) | P1 | Fix MCPs column (lists all instead of used), agent... | **complete** | |
| v9.50 | W2 | README overhaul | P1 | Tech stack table outdated (v9.35-era). Add Claw3D ... | **complete** | |
| v9.50 | W3 | Claw3D dynamic update | P1 | Update claw3d.html from v9.38 data to current arch... | **complete** | |
| v9.50 | W4 | Post-flight + living docs | P2 | Post-flight pass. Changelog append. Middleware reg... | **complete** | |
| v9.51 | W1 | Fix Search button layout + add 3D button | P1 | Search button scrunched on MW tab view. Add "3D" b... | **complete** | |
| v9.51 | W2 | Fix Qwen score scale (8/9 -> 8/10) | P1 | Qwen interprets max=9 as "out of 9" not "0-9 on 10... | **complete** | |
| v9.51 | W3 | Fix build log raw JSON rendering | P1 | Build logs still contain raw JSON dumps in executi... | **complete** | |
| v9.51 | W4 | Qwen harness hardening (continued) | P1 | Review v9.50 output for remaining patterns. Tighte... | **complete** | |
| v9.51 | W5 | Post-flight + living docs | P2 | Post-flight pass. Changelog append. README version... | **complete** | |
| v9.52 | W1 | Evaluator harness rebuild (400+ lines) | P1 | Rebuild docs/evaluator-harness.md from scratch as ... | **complete** | |
| v9.52 | W2 | Claw3D solar system redesign | P1 | Qwen=sun, agents/MCPs=inner planets, middleware/fr... | **complete** | |
| v9.52 | W3 | Phase 10 systems check (all agents, MCPs... | P2 | Dry run engaging all 5 MCPs, all 4 local LLMs, Gem... | **complete** | |
| v9.52 | W4 | Post-flight + living docs + README caden... | P2 | Post-flight with MCP verification. Changelog appen... | **complete** | |
| v9.53 | W1 | Claw3D orbital mechanics fix | P1 | Slow orbits, tighten spread, add connectors, tidal... | **complete** | |
| v9.53 | W2 | Final Qwen harness tuning | P1 | Address v9.52 "What Could Be Better" items. Fix sc... | **complete** | |
| v9.53 | W3 | Post-flight + Phase 9 close-out | P2 | Post-flight with MCP checks. If all passes, Phase ... | **complete** | |

---

## 2. Success/Fail Patterns

**Consistent Successes:**
- **Infrastructure & Automation:** Creating and updating systemd services, watchdog timers, and script execution logic (e.g., `generate_artifacts.py`, `telegram_bot.py`) succeeded with high reliability.
- **Data Enrichment:** Batch updates to Firestore, such as the TripleDB county enrichment (v9.42), executed cleanly using Python and Firebase Admin SDK.
- **Middleware Component Updates:** Updating and appending to `schema_reference.json`, `middleware_registry.json`, and `gotcha_archive.json` consistently resulted in successful outcomes.

**Failure & Friction Points:**
- **Qwen Harness & Evaluation Logic:** Early iterations of the Qwen evaluator harness struggled with accurate scoring (e.g., misinterpreting timeouts as "complete" or "deferred"). This required multiple iterations (v9.41-v9.53) to enforce strict schema validation, retry logic, and execution context passing.
- **Cross-Agent Handoffs:** Draft promotion from Qwen to the main executing agent sometimes resulted in stranded drafts in `docs/drafts/` until workflow fixes were applied in v9.42.
- **UI & Graphical Implementations:** While standard Flutter widgets (tabs, tables) succeeded quickly, the Claw3D solar system implementation required multiple iterations (up to v9.53) to stabilize orbital mechanics and static state.

---

## 3. Multi-Iteration Workflows

**1. Qwen Evaluator Harness (v9.41 - v9.53)**
- **Trajectory:** Started as an 84-line prompt in v9.46. Evolved into a robust, schema-validated, 528-line harness by v9.52.
- **Evolution:** Added 9 ADRs, 15+ failure patterns, X/10 scoring scale, evidence standards, MCP guides, and field-path error retries (up to 3x).
- **Result:** A highly disciplined, agent-agnostic evaluator that effectively prevents hallucinated "PASS" grades.

**2. Telegram Bot Resiliency (v9.40 - v9.44)**
- **Trajectory:** Transitioned from a fragile tmux session to a robust systemd service.
- **Evolution:** Added a 10-minute Watchdog timer, 3-route intent routing (Firestore, ChromaDB, Web via Brave Search), and session memory.
- **Result:** A highly available interface capable of handling public traffic.

**3. Claw3D Visualization (v9.48 - v9.54)**
- **Trajectory:** Started as a simple concept, evolved into a complex Three.js static/animated view.
- **Evolution:** Rebuilt as a static elliptical disc layout with zero animation on inactive objects. Features 46 nodes (Sun/Qwen, Inner planets/Agents, Asteroids/MCPs) with specific active/inactive states.

---

## 4. Gotcha Analysis

**Resolved vs. Recurring Issues:**
- **Resolved:** G43 (Flutter Web map tile CORS - resolved by using CanvasKit), G44 (flutter_map version compatibility), and G51 (Qwen think mode empty responses - resolved by baking `think:false` into `ollama_config.py`).
- **Active / Recurring:** 
  - **G1 (heredocs):** Persistent shell scripting issue.
  - **G19 (Gemini bash):** Workaround required (wrap in `fish -c`).
  - **G34 (array-contains):** Firestore querying limitation requiring post-filter workarounds.
  - **G47 (CanvasKit):** Ongoing rendering quirks.
  - **G53 (Firebase MCP reauth):** Persistent authentication drops requiring manual intervention or script wrappers.
  - **G54 (transitive deps):** Dependency locking issues outside of direct control.

---

## 5. Metrics

*   **Total Iterations:** 27
*   **Total Workstreams Executed:** 144
*   **Zero-Intervention Rate:** ~74% (20/27 iterations required 0 human interventions).
*   **Agent Distribution:**
    *   **Executors:** Claude Code (Opus / 3.5 Sonnet) served as the primary executor. Gemini CLI (Gemini 2.5 Flash / Pro) frequently used for high-context or routing tasks.
    *   **Evaluator:** Qwen3.5-9B (local) exclusively handled draft generation and outcome evaluation.
    *   **Supporting Local LLMs:** Nemotron Mini 4B (Code review) and GLM-4.6V-Flash (Visuals).
*   **MCP Server Utilization:** Heavy reliance on Firebase, Context7, Firecrawl, Playwright, and Dart/Flutter.

---

## 6. IAO Methodology Assessment

**Strengths:**
1. **Middleware as IP:** Storing prompts, evaluator logic, and gotchas as versioned middleware (`middleware_registry.json`) has proven immensely powerful for scaling across projects (e.g., Intranet, socalpha1).
2. **Post-Flight Discipline:** The `post_flight.py` validation step dramatically reduced silent failures by enforcing hard checks on site availability, bot status, and MCP health before an iteration can be promoted.

**Weaknesses / Friction:**
1. **Token Efficiency:** Despite `GEMINI_MODEL` limits and `think:false`, context windows bloat quickly if `CLAUDE.md` and `GEMINI.md` are not strictly curated.
2. **Draft Promotion:** The manual/semi-automated promotion of drafts from `docs/drafts/` to `docs/` still occasionally leaves orphaned files.

**Recommendations for Phase 10:**
1. **Bourdain Pipeline Integration:** Proceed with the 114-video Bourdain pipeline. Ensure the extraction prompt template is strictly defined before the dry run (~v10.57).
2. **Harness Consolidation:** The evaluator harness is at 528 lines. Implement strict line-count monitoring to ensure it does not shrink (as regression is a known failure mode), but avoid adding redundant ADRs.
3. **Cross-Pipeline Backfilling:** When the Bourdain pipeline introduces new schema fields, automatically trigger a backfill evaluation for TripleDB, CalGold, and RickSteves to maintain schema parity.
4. **Automate Gotcha Detection:** Integrate the `data/gotcha_archive.json` directly into the executor agent's pre-flight prompt so known issues (like G19 and G53) are bypassed autonomously.
