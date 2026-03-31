# kjtcom - Report v6.16 (Phase 6b - Design Contract)

**Pipeline:** kjtcom (cross-pipeline Flutter app)
**Phase:** 6b (Design Contract)
**Iteration:** 16 (global counter)
**Executor:** Claude Code (Opus)
**Status:** SUCCESS

---

## Design Contract Summary

Phase 6b synthesized the Phase 6a scrape archive (8 public sites + Panther SIEM reference) into a three-file design contract that fully specifies the visual system for kjtcom's Flutter Web frontend. No code was written - this is a specification-only phase.

### Deliverables Produced

| File | Location | Content |
|------|----------|---------|
| design-tokens.json | app/design-brief/ | 100+ tokens: colors, typography, spacing, elevation, breakpoints, layout, animation |
| design-brief.md | app/design-brief/ | Aesthetic direction, color rules, imagery strategy, tone, spacing/layout, responsive behavior |
| component-patterns.md | app/design-brief/ | 10 component blueprints with token mappings, interaction patterns, accessibility notes |

### Key Design Decisions

1. **"SIEM that queries travel data"** - kjtcom's visual identity is rooted in Panther SIEM's query UI, not travel site aesthetics. Dark surfaces, mono fonts for data, terse labels, high information density.

2. **Three-tier surface hierarchy** - Base (#0D1117) -> Elevated (#161B22) -> Overlay (#1B2838). Every UI element maps to one of these three layers. Derived from Panther and validated across Monad, Scanner.dev, GreyNoise.

3. **Geist typography (LOCKED)** - Geist Sans for all UI, Geist Mono for all data. Two weights only (400, 500). Max font size 18px. Confirmed by Scanner.dev scrape in Phase 6a.

4. **Pipeline dots as visual identity** - The colored dot (CalGold gold, RickSteves blue, TripleDB red, Bourdain purple) in each result row is the primary visual differentiator. Equivalent to Panther's log-type colored badges.

5. **Filter-by-value as core interaction** - Clicking a value in the detail panel appends a query clause. This is Panther's signature UX pattern, adapted for NoSQL syntax instead of PantherFlow.

6. **Dark-only, no theme toggle** - kjtcom is dark mode only. The concierge sites (Black Tomato, A&K) informed content density and field hierarchy, not surface treatment.

7. **Globe hero at 15% opacity** - The Nano Banana globe image provides ambient geographic context without competing with query text. Phase 6c may upgrade to Three.js.

### Source Influence Map

| Design Element | Primary Source | Supporting Sources |
|----------------|---------------|-------------------|
| Query editor layout | Panther screenshots | Scanner.dev (Geist font), Monad (green accent) |
| Results table format | Panther search-results.png | Maltego (data density) |
| JSON detail panel | Panther json-detail.png | - |
| Filter-by-value UX | Panther filter-by-value.png | HTML mockup (+filter/-exclude adaptation) |
| Surface colors | Panther/Monad (#0D1117, #161B22) | GreyNoise (#111111) |
| Typography | Scanner.dev (Geist Sans/Mono) | GreyNoise (Inter fallback) |
| Pipeline dot colors | Design doc (locked) | - |
| Syntax highlighting | HTML mockup (locked) | - |
| Globe background | Design doc (globe_hero.jpg) | GreyNoise (globe viz reference) |
| Responsive patterns | Panther (wide reference viewport) | Cribl (mobile treatment) |

### Metrics

| Metric | Value |
|--------|-------|
| Design tokens defined | 100+ |
| Component blueprints | 10 |
| Interaction patterns documented | 3 (row select, +filter, -exclude) |
| Breakpoints defined | 4 (375, 768, 1024, 1440) |
| WCAG AA contrast verified | 3 text tiers |
| Flutter code changes | 0 |
| Interventions | 0 |

### Conflicts Resolved

| Conflict | Resolution |
|----------|-----------|
| Concierge sites use light backgrounds + serif fonts | Rejected for primary UI. Travel concierge influence limited to content density in detail panel. |
| Scanner.dev uses cyan accent (#00F0FF) vs Panther's green (#4ADE80) | Green wins. It connects kjtcom to SIEM heritage and matches Monad + GreyNoise. |
| Palantir uses expansive enterprise padding | Rejected. kjtcom follows Panther's tight data density with 8px row padding. |
| Maltego uses gold accent (#FFB300) | Not adopted. Gold is reserved for CalGold pipeline color only. |

## Next Steps

- **Phase 6c:** Flutter UI Scaffolding - implement the design contract in Flutter Web
  - Load Geist fonts
  - Build App Shell, Query Editor, Results Table, Detail Panel
  - Connect to Firestore locations collection (live queries)
  - Provision composite indexes for t_any_* query patterns
