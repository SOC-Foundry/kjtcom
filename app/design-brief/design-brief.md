# kjtcom - Design Brief

**Phase:** 6b (Design Contract)
**Iteration:** 16 (global counter)
**Token Reference:** `app/design-brief/design-tokens.json`
**Primary Design Reference:** Panther SIEM (`app/design-brief/panther/`)

---

## Aesthetic Direction

kjtcom is a **dark-mode data investigation platform** that presents travel location intelligence with the visual authority of a production SIEM. The aesthetic sits at the intersection of three influences discovered during Phase 6a:

1. **Panther SIEM (primary)** - The query editor, results table, and JSON detail panel are drawn directly from Panther's PantherFlow search UI. Dark surface (#0D1117), line-numbered editor, single-line result rows, slide-in detail panel, filter-by-value interaction.

2. **Pipeline peers (Monad, Scanner.dev, Cribl)** - Modern SaaS data platform polish. Geist typography (from Scanner.dev), green-on-dark terminal aesthetic (Monad), pipeline-as-product terminology (Cribl). These refine and modernize the Panther baseline.

3. **Travel concierge (Black Tomato, A&K)** - Editorial authority for entity presentation. When a user expands an entity, the detail should carry the same visual confidence as a luxury travel card. This influence is subtle - it informs content density and field hierarchy, not the primary surface treatment.

**The rule:** kjtcom looks like a SIEM that queries travel data, not a travel site with a search box.

---

## Color Rules

### Surface Hierarchy

All surfaces use the dark palette derived from Panther and validated across Monad, Scanner.dev, and GreyNoise:

| Layer | Token | Hex | Usage |
|-------|-------|-----|-------|
| Base | `color.surface.base` | #0D1117 | App background, full-bleed |
| Elevated | `color.surface.elevated` | #161B22 | Query editor input, detail panel field cards, column headers |
| Overlay | `color.surface.overlay` | #1B2838 | Badges, chips, tag backgrounds |
| Row active | `color.surface.row-hover` | #1A2332 | Selected table row |

### Text Hierarchy

Three tiers of text contrast, matching Panther's information density pattern:

| Tier | Token | Hex | Usage |
|------|-------|-----|-------|
| Primary | `color.text.primary` | #E2E8F0 | Entity names, headings, query text |
| Secondary | `color.text.secondary` | #94A3B8 | Column headers, field labels, city/country values |
| Muted | `color.text.muted` | #6E7681 | Line numbers, placeholder text, "+ N more results" |

### Accent Colors

Green is the dominant accent. Blue is secondary (links, active states). Orange and red are reserved for data values and negative actions.

- **Green (#4ADE80)** - Logo, entity count, +filter buttons, cursor, success states. The "terminal green" that connects kjtcom to its SIEM heritage. Sourced from Panther and Monad.
- **Blue (#58A6FF)** - Active tab underline, NoSQL badge, hyperlinks. The secondary accent that provides contrast against green. Sourced from Panther's tab treatment.
- **Orange (#FFA657)** - Numeric data values (ratings, coordinates). Borrowed from GitHub's dark theme syntax for numbers.
- **Red (#FF7B72)** - Operators in syntax highlighting, -exclude buttons, error states. Dual-purpose as syntax color and semantic negative.

### Pipeline Colors (LOCKED)

Each pipeline has a unique dot color displayed in results table rows. These are non-negotiable:

| Pipeline | Color | Hex | Badge |
|----------|-------|-----|-------|
| CalGold | Gold | #DA7E12 | CG |
| RickSteves | Blue | #3B82F6 | RS |
| TripleDB | Red | #DD3333 | TD |
| Bourdain | Purple | #8B5CF6 | NR |

### Syntax Highlighting (LOCKED)

The query editor uses a 4-color syntax scheme derived from the Panther screenshots and HTML mockup:

| Element | Token | Hex |
|---------|-------|-----|
| Field names (`t_any_*`) | `color.syntax.field` | #79C0FF |
| Operators (`contains`, `==`, `!=`, `\|`) | `color.syntax.operator` | #FF7B72 |
| String values (`"French"`) | `color.syntax.value` | #A5D6FF |
| Keywords (`where`, `and`, `or`) | `color.syntax.keyword` | #D2A8FF |

---

## Typography

### Font Stack (LOCKED)

Determined during Phase 6a Discovery. Scanner.dev confirmed Geist as the defining typographic choice for modern data platforms.

| Usage | Family | Token |
|-------|--------|-------|
| All UI (headings, body, labels, tabs, navigation, buttons) | Geist Sans | `typography.family.sans` |
| Query editor, field names, data values in detail panel | Geist Mono | `typography.family.mono` |
| Fallback body (if Geist fails to load) | Inter | included in sans stack |

### Size Scale

The type scale is compact and data-dense, matching the information density observed across Panther, Scanner.dev, and Maltego:

- **9px** - Micro labels (+filter/-exclude buttons)
- **10px** - Field labels, badge text, chip text
- **11px** - Column headers, metadata
- **12px** - Table rows, tabs, entity count (primary reading size for data)
- **13px** - Query editor text (slightly larger for editability)
- **14px** - Section headings
- **18px** - Logo / app name

No type size exceeds 18px. This is a data-dense tool, not a marketing page. The concierge sites (Black Tomato, A&K) use large editorial type - kjtcom deliberately rejects this for the primary UI surface.

### Weight

Only two weights are used: 400 (normal) and 500 (medium). No bold (700). The visual hierarchy is achieved through color contrast and size, not weight - matching Panther and Scanner.dev patterns.

---

## Imagery Strategy

### Globe Hero Background

The primary visual element is `app/assets/globe_hero.jpg` - a Nano Banana-generated globe image that serves as the background behind the query editor area.

**Treatment:**
- Positioned behind the query editor, full-width
- Faded to ~15% opacity (`opacity: 0.15`) so it does not compete with the query text
- Clipped to approximately 260px height (hero zone only)
- Object-fit: cover, pointer-events: none
- Phase 6c may upgrade to Three.js interactive globe with slow rotation (`animation.globe-rotation: 60s linear infinite`)

**Why a globe:** kjtcom queries locations across multiple continents. The globe provides immediate spatial context without any UI chrome. It signals "this is geographic data" at a glance.

### No Stock Photography

kjtcom does NOT use stock photography, hero images, or editorial photography in the primary UI. The concierge sites (Black Tomato, A&K) rely heavily on cinematic nature/destination photography. kjtcom rejects this - the data IS the content. Entity detail panels show structured field data, not images.

**Exception:** If Google Places enrichment ever provides photos, they may appear as small thumbnails (48x48) in the detail panel under `t_enrichment.google_places`. This is Phase 8+ territory.

### Pipeline Dot as Visual Identity

The colored pipeline dot (30px column, left-aligned in results rows) is the primary visual differentiator between entities. These dots carry the same role as Panther's log-type colored badges. They are the most important visual element after the query text itself.

---

## Tone

### Voice

kjtcom's interface communicates like a production tool, not a consumer app:

- **Labels are terse:** "Search", "Results", "Map", "Globe", "Entity detail" - not "Search our collection" or "Explore destinations"
- **Counts are precise:** "47 entities across 8 countries" - not "Showing results"
- **Actions are verbs:** "+filter", "-exclude" - not "Add to search" or "Remove from results"
- **Status is factual:** "staging" badge, "NoSQL" badge - borrowed from Panther's environment/mode indicators

### Information Density

High. Every pixel earns its place. Observed across all Pipeline category scrapes (Monad, Scanner.dev, GreyNoise, Palantir) and confirmed in Panther:

- Table rows are single-line, 8px vertical padding
- No whitespace between result rows beyond the 1px border separator
- The detail panel uses compact field cards (10px padding) with no decorative spacing
- Column headers are 11px, not 14px - they are navigation aids, not headings

### Authority Model

kjtcom positions itself as a peer of Panther, Monad, and Scanner.dev - a tool built by someone who operates these platforms professionally. The Thompson Indicator Fields naming convention (`t_any_*`) mirrors Panther's `p_any_*` fields. The query syntax, while NoSQL rather than PantherFlow, follows the same mental model: specify a collection, filter by fields, get results.

The travel content is the dataset, not the product category. kjtcom is a data platform that happens to query travel locations, not a travel site with a fancy search.

---

## Spacing and Layout

### Spacing Scale

Based on a 4px base unit (matching the tight, data-dense patterns across Pipeline scrapes):

| Token | Value | Primary Usage |
|-------|-------|---------------|
| `spacing.1` | 4px | Badge padding-y, inline gaps |
| `spacing.2` | 8px | Tab padding, row padding-y |
| `spacing.3` | 12px | Detail panel padding, card internals |
| `spacing.4` | 16px | Query editor padding, CTA padding-x |
| `spacing.6` | 24px | Section margin, outer content padding |
| `spacing.8` | 32px | Section gaps |
| `spacing.12` | 48px | Major section breaks |

### Border Radius

Minimal rounding. This is a data tool, not a consumer app:

- **3px** - Badges, pipeline dots
- **4px** - Tags, small buttons
- **6px** - Field cards in detail panel, CTA button
- **8px** - Query editor container
- **12px** - Outer app shell only

### Responsive Behavior

| Breakpoint | Behavior |
|------------|----------|
| < 768px (mobile) | Query editor full-width, results stack vertically, detail panel becomes bottom sheet |
| 768-1023px (tablet) | Query editor full-width, results table visible, detail panel overlays from right |
| 1024-1439px (desktop) | Full layout, detail panel may compress results table width |
| >= 1440px (wide) | Reference layout: results + detail panel side-by-side, matching Panther viewport |

---

## What This Brief Does NOT Cover

- **Three.js globe implementation** - Phase 6c
- **Firestore composite index provisioning** - Phase 6c
- **Google Places photo integration** - Phase 8+
- **Map view implementation** - Phase 6c (tab exists in mockup but is not designed here)
- **Dark/light mode toggle** - There is no light mode. kjtcom is dark-only.
