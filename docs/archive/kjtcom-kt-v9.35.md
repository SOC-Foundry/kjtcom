# kjtcom - Knowledge Transfer v9.35

**Date:** April 4, 2026
**Author:** Claude (Opus 4.6) via claude.ai project session
**Purpose:** Full project state handoff for continuation in a new chat session. This document captures 34 iterations of development so a fresh agent session can resume without re-learning the project.

---

## 1. PROJECT IDENTITY

**kjtcom** is a multi-pipeline location intelligence platform built by Kyle Jerome Thompson (sole developer). It extracts geocoded entities from travel/food TV shows, enriches them via Google Places API, stores them in Firestore, and exposes them through a Flutter Web app with a SIEM-inspired NoSQL query editor.

- **Live site:** https://kylejeromethompson.com
- **GitHub:** SOC-Foundry/kjtcom
- **Firebase project:** kjtcom-c78cd (production default database)
- **Collection:** locations (single collection, t_log_type discriminates pipelines)

Kyle is VP Engineering and Solutions Architect at TachTech Engineering (a SIEM services provider). The project architecture mirrors SIEM pipeline patterns - Thompson Indicator Fields parallel Panther SIEM p_any_* indicator fields.

**Hard contract:** Neither Claude Code nor Gemini CLI can ever git commit, git push, or be contributors to the repo.

---

## 2. PRODUCTION STATE (as of v9.34)

| Pipeline | Source | Entities | t_log_type |
|----------|--------|----------|------------|
| CalGold | California's Gold (Huell Howser) | 899 | calgold |
| RickSteves | Rick Steves' Europe | 4,182 | ricksteves |
| TripleDB | Diners, Drive-Ins and Dives | 1,100 | tripledb |
| **Total** | | **6,181** | |

Schema v3: 100%. All t_any_* values lowercased. Country codes (ISO 3166-1 alpha-2) on 99.7%.

**Flutter Web App - 6 tabs:** Results, Map, Globe, IAO, Gotcha, Schema
**Visual identity:** dark SIEM (#0D1117), tech green (#4ADE80), Cinzel headers, Geist Sans/Mono, gothic borders

---

## 3. PERSISTENT BUGS (UNRESOLVED)

### BUG 1: Quote Cursor - 7 FAILED ATTEMPTS

When schema builder appends | where field contains "", cursor should land between quotes. It doesn't. ref.listen in query_editor.dart overrides cursor position.

| Iter | Approach | Failure |
|------|----------|---------|
| v9.28 | Set selection after text | ref.listen overrides |
| v9.29 | No closing quote | Parser breaks |
| v9.30 | Shared controller | ref.listen still fires |
| v9.31 | Diagnostic-first | Same issue identified |
| v9.32 | Remove quotes entirely | Wrong decision, broke UX |
| v9.33 | programmaticUpdateProvider flag | Flag exists, cursor still resets |
| v9.34 | Gemini + addPostFrameCallback | Claimed fixed, still broken |

**ROOT CAUSE:** TextField + Stack architecture. RECOMMENDED FIX: Replace with flutter_code_editor package.

### BUG 2: Autocomplete Broken

Overlay approach (v9.30) never showed. Inline approach (v9.34) shows but wrong UX. Need Panther-style compact inline suggestions.

### BUG 3: +filter Uses Wrong Operator

Should use contains for array fields, == for scalar fields. Still uses contains for everything.

---

## 4. IAO METHODOLOGY - 10 PILLARS

P1-Trident (Cost/Delivery/Performance), P2-Artifact Loop, P3-Diligence, P4-Pre-Flight, P5-Agentic Harness, P6-Zero-Intervention, P7-Self-Healing, P8-Phase Graduation, P9-Post-Flight Testing, P10-Continuous Improvement.

Mermaid trident chart uses graph BT with shaft (#0D9488) and prong (#161B22 stroke #4ADE80).

---

## 5. COMPLETE GOTCHA REGISTRY (G1-G50)

| ID | Gotcha | Status |
|----|--------|--------|
| G1 | Heredocs in fish - use printf | ACTIVE |
| G2 | CUDA LD_LIBRARY_PATH | RESOLVED |
| G11 | Never cat config.fish or SA JSON | ACTIVE |
| G18 | Gemini 5-min timeout - background jobs | ACTIVE |
| G19 | Gemini runs bash - wrap in fish -c | ACTIVE |
| G20 | Config.fish has keys - grep only | ACTIVE |
| G21 | CUDA OOM - sequential processing | ACTIVE |
| G22 | Fish ls colors - command ls | ACTIVE |
| G23 | LD_LIBRARY_PATH | RESOLVED |
| G24 | Checkpoint staleness | ACTIVE |
| G30 | Cross-project SA permissions | ACTIVE |
| G31 | TripleDB schema drift | RESOLVED |
| G32 | Production Firestore rules | ACTIVE |
| G33 | Duplicate entity IDs | ACTIVE |
| G34 | Single array-contains limit | ACTIVE |
| G35 | Production write safety - dry-run | ACTIVE |
| G36 | Case-sensitive arrayContains | RESOLVED (v9.32) |
| G37 | t_any_shows casing | RESOLVED (v9.32) |
| G38 | Firebase deploy auth | ACTIVE |
| G39 | Detail panel provider chain | RESOLVED |
| G40 | Compound country names | DOCUMENTED |
| G41 | Rebuild-triggered handlers | RESOLVED |
| G42 | Rotating queries | RESOLVED |
| G43 | Map tile CORS | ACTIVE |
| G44 | flutter_map compat | ACTIVE |
| G45 | Schema cursor - 7 failures | ACTIVE CRITICAL |
| G46 | Firestore limit | RESOLVED |
| G47 | CanvasKit blocks Playwright | ACTIVE |
| G48 | Fix without live verify | ACTIVE |
| G49 | TripleDB shows title case | RESOLVED |
| G50 | Parser regex order | RESOLVED |

---

## 6. INFRASTRUCTURE

- **NZXTcos:** Primary dev, i9-13900K, fish shell, ~/dev/projects/kjtcom
- **tsP3-cos:** Secondary, ThinkStation P3 Ultra
- **Flutter:** 3.41.6, 16 packages need major upgrades (Riverpod 2->3 is blocking)
- **Firebase:** kjtcom-c78cd, SA at ~/.config/gcloud/kjtcom-sa.json
- **Agents:** claude --dangerously-skip-permissions, gemini --yolo
- **Deploy:** cd ~/dev/projects/kjtcom && firebase deploy --only hosting

---

## 7. WHAT MUST HAPPEN NEXT

### Priority 1: Replace TextField with Code Editor Package
flutter_code_editor or re_editor. Eliminates ALL cursor/autocomplete bugs. ~3-4 hour migration.

### Priority 2: MCP Servers + HyperAgents
Kyle has requested these for over a week. Evaluate Firebase MCP, Playwright MCP, Flutter/Dart MCP. Consider HyperAgents for multi-agent orchestration.

### Priority 3: Flutter Dependency Upgrade
Riverpod 2->3 (~60 lines across 13 files). Dedicated iteration.

### Priority 4: Remaining Phase 9 Polish
Lighthouse, cookie consent, analytics, mobile responsiveness.

### Priority 5: Phase 10
IAO retrospective + template publication. Bourdain pipeline (acquisition TBD).

---

## 8. KEY FILES

- app/lib/widgets/query_editor.dart - THE PROBLEM WIDGET
- app/lib/providers/query_provider.dart - queryProvider, queryTextControllerProvider, programmaticUpdateProvider
- app/lib/models/query_clause.dart - parser + knownFields (22 fields)
- app/lib/widgets/schema_tab.dart - query builder
- app/lib/widgets/detail_panel.dart - +filter/-exclude
- app/assets/value_index.json - autocomplete data (21 fields, ~6,800 values)

---

## 9. CONVENTIONS

- Fish shell throughout. pip --break-system-packages. python3 -u.
- No em-dashes. Use " - " instead. Use "->" for arrows.
- "pipelines" and "log types," never "tables" or "datasets"
- Deploy from repo root, never app/
- Kyle manually handles all git. Agents never touch git.
- Terse, direct communication. No padding.
- 4 artifacts per iteration. Mermaid + 10 pillars in every design doc.

---

## 10. PROMPT TO CONTINUE

```
I'm continuing development on kjtcom, a multi-pipeline location intelligence platform. Please read the knowledge transfer document I'm uploading (kjtcom-kt-v9.35.md) for full project state.

Current situation:
- Phase 9 App Optimization, iteration 34 complete
- THREE PERSISTENT BUGS: quote cursor (7 fails), autocomplete (broken), +filter operators (wrong)
- Root cause: TextField + Stack architecture in query_editor.dart

My direction for v9.35:
- OPTION B: Evaluate MCP servers (Firebase MCP, Playwright MCP, Flutter/Dart MCP) and HyperAgents
- OPTION C: Replace TextField query editor with flutter_code_editor package (Gemini CLI)
- Combine: MCP for diagnosis/verification, Gemini for Flutter execution

Please recommend the v9.35 approach: which MCP servers, whether HyperAgents, and whether code editor migration goes before or after MCP setup.

Also scope the Riverpod 2->3 upgrade - separate iteration or bundled?
```

---

## 11. REFERENCE SITES

Panther SIEM (tachtech.runpanther.net) - primary query editor reference
Monad, Scanner.dev, GreyNoise, Palantir Foundry - pipeline/SIEM aesthetics
Maltego, Cribl - investigation tools
Black Tomato, Abercrombie & Kent - boutique travel

---

## 12. COST

Entire project built at near-zero marginal cost. Firebase free tier, Google Places free credits, Gemini CLI free, Claude Code via Pro subscription. No paid SaaS, no cloud compute.
