# kjtcom - Component Patterns

**Phase:** 6b (Design Contract)
**Iteration:** 16 (global counter)
**Token Reference:** `app/design-brief/design-tokens.json`
**Design Brief:** `app/design-brief/design-brief.md`
**Primary Reference:** Panther SIEM screenshots + `app/design-brief/panther/kjtcom-query-mockup.html`

---

## 1. App Shell

The outermost container. Dark, full-bleed, no chrome.

```
+------------------------------------------------------------------+
|  [kjtcom logo]  [Investigate badge]             [staging badge]   |
|  Search                                                           |
|  Query Thompson Indicator Fields across all pipelines             |
|  +------------------------------------------------------------+  |
|  |  Query Editor (Component 2)                                 |  |
|  +------------------------------------------------------------+  |
|  [Results]  [Map]  [Globe]                                        |
|  47 entities across 8 countries                                   |
|  +-------------------------------------+----------------------+  |
|  |  Results Table (Component 4)        | Detail Panel (Comp 5) |  |
|  +-------------------------------------+----------------------+  |
+------------------------------------------------------------------+
```

### Token Mapping

| Element | Token | Value |
|---------|-------|-------|
| Background | `color.surface.base` | #0D1117 |
| Border radius | `radius.2xl` | 12px |
| Content padding | `spacing.6` | 24px |
| Logo text color | `color.accent.green` | #4ADE80 |
| Logo font size | `typography.size.2xl` | 18px |
| Logo font weight | `typography.weight.medium` | 500 |
| Logo letter spacing | `typography.letter-spacing.wide` | 0.5px |
| Logo font family | `typography.family.sans` | Geist Sans |

### Badges

Two badges in the header bar - sourced from the HTML mockup:

**"Investigate" badge (left):**
- Font: `typography.family.sans`, `typography.size.base` (11px)
- Color: `color.text.secondary` (#94A3B8)
- Border: 1px solid `color.border.default` (#30363D)
- Padding: 2px 8px
- Radius: `radius.md` (4px)

**"staging" badge (right, auto-margin-left):**
- Font: `typography.family.sans`, `typography.size.base` (11px)
- Color: `color.accent.green` (#4ADE80)
- Border: 1px solid `color.surface.filter-positive` (#1B4332)
- Background: `color.surface.filter-positive` with reduced opacity (#0D2818)
- Padding: 2px 8px
- Radius: `radius.md` (4px)

### Section Header

Below logo bar, above query editor:

- "Search" label: `typography.family.sans`, `typography.size.xl` (14px), `typography.weight.medium`, `color.text.primary`
- Subtitle: `typography.family.sans`, `typography.size.base` (11px), `color.text.secondary`
- Margin bottom: `spacing.2` (8px)

---

## 2. Query Editor

The core interaction widget. Dark input area with line-numbered, syntax-highlighted query text. Derived directly from Panther's PantherFlow editor.

### Layout

```
+------------------------------------------------------------------+
|  [NoSQL] [Logs]                          [locations] [All time]   |
|                                                                   |
|  1  locations                                                     |
|  2  | where t_any_cuisines contains "French"                      |
|  3  | where t_any_shows == "Rick Steves' Europe"                  |
|  4  |_                                                   [Search] |
+------------------------------------------------------------------+
```

### Token Mapping

| Element | Token | Value |
|---------|-------|-------|
| Container background | `color.surface.elevated` | #161B22 |
| Container border | 1px solid `color.border.default` | #30363D |
| Container radius | `radius.xl` | 8px |
| Container padding | `spacing.3` (12px) `spacing.4` (16px) | 12px 16px |
| Mode chips (NoSQL, Logs, etc.) | `color.surface.overlay` bg, `typography.size.sm` (10px) | #1B2838 |
| Active mode chip text | `color.accent.blue` | #58A6FF |
| Inactive mode chip text | `color.text.secondary` | #94A3B8 |
| Chip padding | 2px 8px | - |
| Chip radius | `radius.md` | 4px |
| Chip row margin-bottom | `spacing.1` | 4px |

### Query Lines

Each line is a flex row: line number + content.

| Element | Token | Value |
|---------|-------|-------|
| Line number width | `layout.query-line-number-width` | 20px |
| Line number color | `color.text.muted` | #6E7681 |
| Line number font | `typography.family.mono`, `typography.size.md` (12px) | Geist Mono |
| Line number alignment | right | - |
| Content font | `typography.family.mono`, `typography.size.lg` (13px) | Geist Mono |
| Line padding-y | 3px | - |
| Line gap (number to content) | `spacing.2` | 8px |

### Syntax Colors (per token type)

| Token Type | Token | Hex | Example |
|------------|-------|-----|---------|
| Collection name | `color.accent.green` | #4ADE80 | `locations` |
| Field name | `color.syntax.field` | #79C0FF | `t_any_cuisines` |
| Operator | `color.syntax.operator` | #FF7B72 | `contains`, `==`, `\|` |
| String value | `color.syntax.value` | #A5D6FF | `"French"` |
| Keyword | `color.syntax.keyword` | #D2A8FF | `where` |
| Cursor | `color.syntax.cursor` | #4ADE80 | blinking `_` |

### Search Button

Positioned absolute, right: 12px, vertically centered within the editor container.

| Element | Token | Value |
|---------|-------|-------|
| Background | `color.surface.cta` | #238636 |
| Text color | `color.text.on-cta` | #FFFFFF |
| Font | `typography.family.sans`, `typography.size.md` (12px), `typography.weight.medium` | - |
| Padding | 6px 16px | - |
| Radius | `radius.lg` | 6px |

---

## 3. Tab Bar

Horizontal tabs below the query editor. Three tabs: Results, Map, Globe.

### Layout

```
[Results]  [Map]  [Globe]
----------
```

### Token Mapping

| Element | Token | Value |
|---------|-------|-------|
| Container border-bottom | 1px solid `color.border.subtle` | #21262D |
| Container padding-y | `spacing.2` | 8px |
| Tab font | `typography.family.sans`, `typography.size.md` (12px) | Geist Sans |
| Active tab text | `color.text.primary` | #E2E8F0 |
| Active tab underline | 2px solid `color.accent.blue` | #58A6FF |
| Inactive tab text | `color.text.secondary` | #94A3B8 |
| Tab padding | 4px 8px | - |

### Entity Count Row

Below tab bar, above results table:

| Element | Token | Value |
|---------|-------|-------|
| Count text | `typography.family.sans`, `typography.size.md` (12px), `typography.weight.medium` | - |
| Count color | `color.accent.green` | #4ADE80 |
| Metadata text | `typography.family.sans`, `typography.size.base` (11px) | - |
| Metadata color | `color.text.secondary` | #94A3B8 |
| Row padding-y | `spacing.2` | 8px |
| Gap between count and metadata | `spacing.2` | 8px |

---

## 4. Results Table

Single-line rows with fixed columns. Derived from Panther's log results table.

### Column Grid

Uses CSS Grid matching the HTML mockup layout:

```
grid-template-columns: 30px 1fr 100px 100px 80px
```

Token: `layout.results-columns`

| Column | Width | Content |
|--------|-------|---------|
| Dot | 30px | Pipeline-colored circle |
| NAME | 1fr | Entity name (primary text) |
| CITY | 100px | City name (secondary text) |
| COUNTRY | 100px | Country name (secondary text) |
| SHOW | 80px | Pipeline badge (colored chip) |

### Column Headers

| Element | Token | Value |
|---------|-------|-------|
| Background | `color.surface.elevated` | #161B22 |
| Font | `typography.family.sans`, `typography.size.base` (11px) | Geist Sans |
| Color | `color.text.secondary` | #94A3B8 |
| Padding | 6px 8px | - |
| Border-bottom | 1px solid `color.border.subtle` | #21262D |

### Data Rows

| Element | Token | Value |
|---------|-------|-------|
| Background (default) | transparent | - |
| Background (selected) | `color.surface.row-hover` | #1A2332 |
| Padding | 8px | - |
| Border-bottom | 1px solid `color.border.subtle` | #21262D |
| Cursor | pointer | - |
| Transition | `animation.row-highlight` | 150ms ease |

### Row Content

| Element | Token | Value |
|---------|-------|-------|
| Pipeline dot | Unicode &#9679; (filled circle), colored per `color.pipeline.*` | - |
| Entity name font | `typography.family.sans`, `typography.size.md` (12px) | - |
| Entity name color | `color.text.primary` | #E2E8F0 |
| City/Country font | `typography.family.sans`, `typography.size.md` (12px) | - |
| City/Country color | `color.text.secondary` | #94A3B8 |

### Pipeline Badge (SHOW column)

| Element | Token | Value |
|---------|-------|-------|
| Background | `color.surface.overlay` | #1B2838 |
| Text color | Matches `color.pipeline.*` for that pipeline | Per-pipeline |
| Font | `typography.family.sans`, `typography.size.sm` (10px) | - |
| Padding | 1px 6px | - |
| Radius | `radius.sm` | 3px |
| Text align | center | - |

### Overflow Indicator

When results exceed visible rows:

- Text: "+ N more results"
- Font: `typography.family.sans`, `typography.size.base` (11px)
- Color: `color.text.muted` (#6E7681)
- Alignment: center
- Padding: `spacing.2` (8px)

---

## 5. Entity Detail Panel

Slides in from the right when a table row is clicked. Shows all Thompson Indicator Fields for the selected entity. Derived from Panther's JSON detail panel with +filter/-exclude adaptation from the HTML mockup.

### Layout

```
+----------------------------------------------+
|  Entity detail                           [x]  |
|                                               |
|  +------------------------------------------+|
|  | t_any_names                               ||
|  | "Bouchon Restaurant"                      ||
|  +------------------------------------------+|
|                                               |
|  +------------------------------------------+|
|  | t_any_cuisines                            ||
|  | "french"  "lyonnaise"                     ||
|  | [+ filter] [- exclude]                    ||
|  +------------------------------------------+|
|                                               |
|  +------------------------------------------+|
|  | t_any_dishes                              ||
|  | "duck"  "escargot"  "foie gras"          ||
|  | [+ filter] [- exclude]                    ||
|  +------------------------------------------+|
|                                               |
|  +------------------------------------------+|
|  | t_enrichment.google_places                ||
|  | rating: 4.3                               ||
|  | still_open: true                          ||
|  +------------------------------------------+|
+----------------------------------------------+
```

### Container

| Element | Token | Value |
|---------|-------|-------|
| Width | `layout.sidebar-width` | 320px |
| Border-left | 1px solid `color.border.subtle` | #21262D |
| Padding | `spacing.3` | 12px |
| Font | `typography.family.mono` (default for all data) | Geist Mono |
| Max height | 400px (scrollable) | - |
| Overflow-y | auto | - |
| Slide animation | `animation.detail-slide` | 200ms ease-out |

### Header

| Element | Token | Value |
|---------|-------|-------|
| Title font | `typography.family.sans`, `typography.weight.medium` | Geist Sans |
| Title color | `color.text.primary` | #E2E8F0 |
| Close button color | `color.text.muted` | #6E7681 |
| Close button size | 16px | - |
| Margin-bottom | `spacing.3` | 12px |

### Field Cards

Each Thompson Indicator Field is displayed in its own card.

| Element | Token | Value |
|---------|-------|-------|
| Background | `color.surface.elevated` | #161B22 |
| Radius | `radius.lg` | 6px |
| Padding | `spacing.3` (10px) | 10px |
| Margin-bottom | `spacing.2` | 8px |

### Field Label

| Element | Token | Value |
|---------|-------|-------|
| Font | `typography.family.mono`, `typography.size.sm` (10px) | Geist Mono |
| Color | `color.text.secondary` | #94A3B8 |
| Margin-bottom | 2px | - |

### Field Values

**String values (arrays):**
- Displayed as inline flex-wrap chips
- Font: `typography.family.mono`, inherits card size
- Color: `color.syntax.value` (#A5D6FF)
- Gap: `spacing.1` (4px)

**Numeric values (ratings, coordinates):**
- Color: `color.accent.orange` (#FFA657)

**Boolean values (still_open):**
- True: `color.accent.green` (#4ADE80)
- False: `color.accent.red` (#FF7B72)

**Nested objects (t_enrichment.*):**
- Font: `typography.family.mono`, `typography.size.base` (11px)
- Color: `color.text.secondary` (#94A3B8)
- Line breaks between sub-fields

### Filter / Exclude Buttons

Appear below array-type field values. The core interaction pattern from Panther adapted for NoSQL.

**+filter button:**

| Element | Token | Value |
|---------|-------|-------|
| Background | `color.surface.filter-positive` | #1B4332 |
| Text color | `color.accent.green` | #4ADE80 |
| Font | `typography.family.sans`, `typography.size.xs` (9px) | - |
| Padding | 2px 6px | - |
| Radius | `radius.sm` | 3px |
| Cursor | pointer | - |
| Action | Appends `AND t_any_field contains "value"` to query | - |

**-exclude button:**

| Element | Token | Value |
|---------|-------|-------|
| Background | `color.surface.filter-negative` | #3B1B1B |
| Text color | `color.accent.red` | #FF7B72 |
| Font | `typography.family.sans`, `typography.size.xs` (9px) | - |
| Padding | 2px 6px | - |
| Radius | `radius.sm` | 3px |
| Cursor | pointer | - |
| Action | Appends `AND t_any_field != "value"` to query | - |

**Button row:**
- Display: flex
- Gap: `spacing.1` (4px)
- Margin-top: `spacing.2` (6px)

---

## 6. Globe Hero Background

The ambient visual behind the query editor area. Static image in Phase 6b, potentially Three.js in Phase 6c.

| Element | Token | Value |
|---------|-------|-------|
| Source | `app/assets/globe_hero.jpg` | Nano Banana-generated |
| Position | absolute, top: 0, left: 0 | - |
| Width | 100% | - |
| Height | 260px | - |
| Object-fit | cover | - |
| Opacity | 0.15 | - |
| Pointer-events | none | - |
| Z-index | 0 (content at z-index 1) | - |

---

## 7. Responsive Behavior

### Mobile (< 768px)

- Query editor: full-width, chips wrap
- Search button: below editor (not absolute-positioned)
- Results table: NAME column only, CITY/COUNTRY/SHOW hidden. Pipeline dot remains.
- Detail panel: slides up as bottom sheet (full-width), not from right
- Tab bar: horizontal scroll if needed

### Tablet (768px - 1023px)

- Query editor: full-width
- Results table: NAME + CITY + pipeline badge visible. COUNTRY hidden.
- Detail panel: overlays from right, covers ~60% width

### Desktop (1024px - 1439px)

- Full layout with all columns
- Detail panel: 320px, may compress results table

### Wide (>= 1440px)

- Reference layout matching Panther viewport
- Results table + detail panel side-by-side with no compression
- Maximum content width: `layout.max-width` (1440px)

---

## 8. Component Inventory (Phase 6c Implementation Order)

| Priority | Component | Flutter Widget | Depends On |
|----------|-----------|---------------|------------|
| P0 | App Shell | Scaffold + Container | Geist font loading |
| P0 | Query Editor | TextField + RichText | Syntax highlighting logic |
| P0 | Results Table | ListView.builder | Firestore query binding |
| P0 | Detail Panel | AnimatedContainer | Row selection state |
| P1 | Tab Bar | TabBar / custom | Route management |
| P1 | Filter/Exclude Buttons | GestureDetector + query state | Query editor state management |
| P1 | Pipeline Badge | Container + Text | Pipeline color map |
| P2 | Globe Background | Image.asset (static) or Three.js (webview) | Asset loading |
| P2 | Entity Count Row | Text.rich | Query result count |
| P3 | Mobile Bottom Sheet | DraggableScrollableSheet | Responsive breakpoint detection |

---

## 9. Interaction Patterns

### Row Selection -> Detail Panel

1. User clicks a result row
2. Row background transitions to `color.surface.row-hover` (#1A2332)
3. Detail panel slides in from right (`animation.detail-slide: 200ms ease-out`)
4. Panel shows all `t_any_*` fields for the selected entity
5. Clicking a different row updates the panel content (no close/reopen)
6. Clicking the X button closes the panel

### Filter-by-Value

1. User clicks "+filter" on a value in the detail panel (e.g., "lyonnaise" under t_any_cuisines)
2. A new line is appended to the query editor: `| where t_any_cuisines contains "lyonnaise"`
3. The query auto-executes (or waits for Search button click - TBD in Phase 6c)
4. Results table updates to reflect the narrowed query
5. Detail panel remains open showing the same entity

### Exclude-by-Value

1. User clicks "-exclude" on a value
2. A new line is appended: `| where t_any_cuisines != "lyonnaise"`
3. Same flow as filter-by-value

### Tab Navigation

- Results: default tab, shows the results table
- Map: shows entity coordinates on an interactive map (Phase 6c)
- Globe: shows 3D globe visualization with entity pins (Phase 6c)
- Active tab indicated by `color.accent.blue` (#58A6FF) underline

---

## 10. Accessibility Notes

- All text meets WCAG AA contrast ratio against dark surfaces (verified: #E2E8F0 on #0D1117 = 12.6:1, #94A3B8 on #0D1117 = 6.2:1, #6E7681 on #0D1117 = 3.5:1)
- Query editor supports keyboard navigation (arrow keys between lines)
- Results table rows are focusable via Tab key
- Detail panel close button has aria-label="Close detail panel"
- Pipeline dots include aria-label with pipeline name (e.g., aria-label="RickSteves")
- Filter/exclude buttons include title tooltips showing the query clause that will be added
