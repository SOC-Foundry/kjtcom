# kjtcom - Design Document v10.54

**Phase:** 10 - IAO Retrospective + Pipeline Template + Bourdain Prep
**Iteration:** 54
**Date:** April 6, 2026
**Recommended Agent:** Claude Code
**Focus:** Claw3D Static Rebuild + Phase 9 Retrospective + Harness Regression Fix

---

## PHASE 10 BEGINS

Phase 9 (v9.27-v9.53, 27 iterations) is formally complete. Phase 10 focuses on:
1. IAO methodology retrospective and refinement
2. Pipeline template packaging for reuse
3. Bourdain pipeline dry run (114 videos, ~v10.57)
4. IaC packaging for GCP deployment

---

## WORKSTREAMS

| # | Workstream | Priority | Description |
|---|-----------|----------|-------------|
| W1 | Claw3D static rebuild | P1 | Zero animation. Static elliptical disc layout. Rotatable camera. Active=solid+animated connectors. Inactive=outline+static connectors. Hover tooltips. |
| W2 | Phase 9 retrospective analysis | P1 | Read all 27 iterations from docs/archive/. Produce docs/phase9-retrospective.md with patterns, success/fail rates, recommendations. |
| W3 | Evaluator harness regression fix | P1 | Verify line count. If shrank from 528, restore from v9.52 or git. |
| W4 | Post-flight + Phase 10 living docs | P2 | Post-flight pass. Update README for Phase 10. Changelog append. |

---

## W1: Claw3D Static Rebuild (P1)

Complete rebuild of app/web/claw3d.html. The current version is a jumbled animated mess where objects overlap and go off-screen. The new version is an architecture diagram you could screenshot and present.

### Core Principles
1. **ZERO animation on objects.** No orbiting. No spinning. Objects are STATIC.
2. **Rotatable camera** via OrbitControls (drag to orbit, scroll to zoom) - same as v9.38 original.
3. **Everything visible in one viewport.** No objects off-screen at default zoom.
4. **Clear enough to explain architecture** to someone who's never seen the project.

### Layout: Elliptical Disc

All objects arranged on a flat elliptical disc (like Saturn's rings viewed at an angle):

```
                    [Sun: Qwen Evaluator]
                          |
        --------Inner Ring (Agents/LLMs)---------
       /                                          \
  [Nemotron]  [GLM]  [Claude]  [Gemini]  [nomic]
       \                                          /
        --------Asteroid Belt (MCPs)----------
       /                                          \
  [Firebase] [Context7] [Firecrawl] [Playwright] [Dart]
       \                                          /
        --------Outer Ring (Systems)-----------
       /                                          \
  [Jupiter/MW]    [Saturn/FE]    [Uranus/Pipeline]    [Neptune/Backend]
   +10 moons      +8 moons       +7 moons             +6 moons
```

### Object States (per iteration toggle)

**Active objects (used in selected iteration):**
- Solid fill color (green for Claude, blue for Gemini, etc.)
- Full opacity 1.0
- Connector lines between related objects are ANIMATED (flowing dots or pulse, like v9.38 data flow lines)

**Inactive objects (not yet built or not used in selected iteration):**
- OUTLINE only - black fill inside, colored border
- Opacity 0.3 for the outline
- Connector lines are STATIC (thin, dim, no animation)

### Moons: Grouped Facing Sun

Each gas giant's moons are arranged in a cluster on the SUN-FACING side of the planet. Not orbiting. Not scattered. A tight semicircle of small spheres between the planet and the sun, like satellites in formation.

```
                [Sun]
                  |
    moon1  moon2  |
      moon3  [Jupiter/Middleware]
    moon4  moon5
```

### Connectors (Links)

Lines between related objects:
- Sun -> each inner planet (Qwen evaluates all agents)
- Sun -> each gas giant (Qwen evaluates all systems)
- Each gas giant -> its moons (system contains components)
- Specific cross-connections: Intent Router moon -> Firestore MCP, Bot moon -> Gemini inner planet, etc.

**Active links:** animated (flowing particles or pulsing opacity along the line, green #4ADE80)
**Inactive links:** static thin line, dim (#333333)

### Hover Tooltips

When mouse hovers over ANY object (planet, moon, or MCP asteroid):
```
Name: Intent Router
Type: Middleware Component (Jupiter moon)
Function: Gemini Flash classifies /ask queries into firestore/chromadb/web routes
Status: Active since v9.41
File: scripts/intent_router.py
```

Implementation: Three.js Raycaster for hover detection. HTML overlay div positioned at mouse coordinates. Show/hide on mouseenter/mouseleave.

### Iteration Dropdown

Keep the dropdown from v9.52. When iteration changes:
- All objects update their active/inactive state (solid vs outline)
- All connectors update (animated vs static)
- Tooltip shows correct "Active since" version

Data source: data/claw3d_iterations.json (already exists, 12 iterations mapped).

### Node Inventory (complete)

**Sun (1):** Qwen Evaluator

**Inner Ring - Agents/LLMs (5):**
| Node | Color | Since |
|------|-------|-------|
| Claude Code | green #4ADE80 | v9.27 |
| Gemini CLI | blue #3B82F6 | v9.27 |
| Nemotron Mini 4B | orange #F97316 | v9.35 |
| GLM-4.6V-Flash | amber #F59E0B | v9.35 |
| nomic-embed-text | teal #14B8A6 | v9.35 |

**Asteroid Belt - MCPs (5):**
| Node | Color | Since |
|------|-------|-------|
| Firebase MCP | pink #EC4899 | v9.35 |
| Context7 MCP | pink #EC4899 | v9.35 |
| Firecrawl MCP | pink #EC4899 | v9.35 |
| Playwright MCP | pink #EC4899 | v9.36 |
| Dart MCP | pink #EC4899 | v9.37 |

**Jupiter - Middleware (10 moons):**
| Moon | Since | File |
|------|-------|------|
| Intent Router | v9.41 | scripts/intent_router.py |
| Firestore Query | v9.41 | scripts/firestore_query.py |
| Artifact Generator | v9.41 | scripts/generate_artifacts.py |
| Evaluator Harness | v9.46 | docs/evaluator-harness.md |
| Gotcha Archive | v9.42 | data/gotcha_archive.json |
| Middleware Registry | v9.42 | data/middleware_registry.json |
| Event Logger | v9.39 | scripts/utils/iao_logger.py |
| Post-Flight | v9.43 | scripts/post_flight.py |
| Cleanup Docs | v9.48 | scripts/cleanup_docs.py |
| Eval Schema | v9.49 | data/eval_schema.json |

**Saturn - Frontend (8 moons):**
| Moon | Since |
|------|-------|
| Results Tab | v9.27 |
| Map Tab | v9.27 |
| Globe Tab | v9.27 |
| IAO Tab | v9.27 |
| MW Tab | v9.49 |
| Schema Tab | v9.28 |
| Query Editor | v9.27 |
| Detail Panel | v9.27 |

**Uranus - Pipeline (7 moons):**
| Moon | Since | Tool |
|------|-------|------|
| yt-dlp (Acquire) | v0.5 | yt-dlp |
| Transcribe | v1.6 | faster-whisper |
| Extract | v1.6 | Gemini Flash |
| Normalize | v1.6 | Python + schema |
| Geocode | v1.6 | Nominatim |
| Enrich | v1.6 | Google Places |
| Load | v1.6 | Firebase Admin |

**Neptune - Backend/Data (6 moons):**
| Moon | Since |
|------|-------|
| Cloud Firestore | v0.5 |
| Cloud Functions | v0.5 |
| Firebase Hosting | v0.5 |
| ChromaDB | v9.38 |
| Schema Reference | v9.41 |
| Claw3D Iterations | v9.52 |

**Total: 1 sun + 5 inner + 5 asteroids + 4 giants + 31 moons = 46 nodes**

---

## W2: Phase 9 Retrospective (P1)

Read ALL iteration docs from docs/archive/ (v9.27-v9.53). Produce docs/phase9-retrospective.md.

### Analysis Structure

1. **Workstream Inventory:** every workstream from every design doc, mapped to its outcome from the corresponding report. Table format: iteration, W#, name, priority, planned outcome, actual outcome, notes.

2. **Success/Fail Patterns:**
   - Which workstream TYPES consistently succeed? (file creation, script updates, deploy)
   - Which consistently fail or defer? (dependency upgrades, Qwen harness tuning, complex UI)
   - What's the average workstream completion rate per iteration?

3. **Multi-Iteration Workflows:**
   - Which objectives spanned multiple iterations? (Qwen harness: v9.46-v9.53 = 8 iterations)
   - Recommend: which multi-iteration patterns should be combined?
   - Recommend: which need more structure (dedicated iteration vs. bundled)?

4. **Gotcha Analysis:**
   - Which resolutions stuck permanently? (G51 think:false)
   - Which recurred despite "resolution"? (G53 Firebase reauth)
   - Pattern: environment gotchas resolve permanently, LLM gotchas recur

5. **Metrics:**
   - Zero-intervention iterations: count and percentage
   - Average iteration duration (11-18 minutes observed)
   - Token spend trends
   - Agent usage distribution (Claude vs Gemini led)

6. **IAO Methodology Assessment:**
   - What worked: artifact loop, post-flight, Trident
   - What needs refinement: Qwen evaluation reliability, artifact promotion workflow
   - Recommendations for Phase 10

---

## W3: Evaluator Harness Regression Fix (P1)

```fish
wc -l docs/evaluator-harness.md
```

If < 528 (the v9.52 count), restore:
```fish
cp docs/archive/evaluator-harness-v9.52.md docs/evaluator-harness.md
# Or from git:
git log --all --oneline docs/evaluator-harness.md | head -5
git checkout {commit} -- docs/evaluator-harness.md
```

Then verify the content includes all 9 ADRs, 15+ failure patterns, score calibration, and complete templates.

---

## W4: Post-Flight + Phase 10 Living Docs (P2)

1. Post-flight with MCP checks (8/8+)
2. Update README: Phase 10, v10.54
3. Append changelog (single file)
4. Re-embed archive (retrospective is a large new doc)
5. Rebuild architecture HTML
6. Deploy

---

## TRIDENT

| Prong | Target |
|-------|--------|
| Cost | $0. <50K tokens. |
| Delivery | 4 workstreams. Claw3D readable. Retrospective complete. Harness verified. |
| Performance | Claw3D: all 46 nodes visible in one viewport. Screenshot-ready. Hover tooltips work. Iteration toggle changes active/inactive correctly. |

---

*Design document v10.54, April 6, 2026. Phase 10 begins.*
