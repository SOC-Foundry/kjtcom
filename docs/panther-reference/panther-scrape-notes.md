# Panther SIEM -> kjtcom UI Mapping Notes

**Captured:** April 4, 2026
**Source:** tachtech.runpanther.net/investigate/search/
**Method:** CDP scrape via Playwright (port 9222)

## Captures Retained (UI Structure Only)

| File | Contents |
|------|----------|
| panther-query-editor.html | Query results histogram DOM (MUI-based) |
| panther-css-tokens.json | 1,274 CSS custom properties |
| panther-dom-structure.json | Full page DOM tree (6 levels deep) |

**Deleted:** panther-search-full.png, panther-search-viewport.png (contained customer detection data - security policy violation).

## UI Element Mapping: Panther -> kjtcom

### Query Editor
| Panther | kjtcom |
|---------|--------|
| PantherFlow query language (SQL-like) | Piped clause syntax (field operator value) |
| Line-numbered code editor | Line-numbered TextField + syntax highlighting |
| Search button (top right) | Search button (inline right) |
| AI natural language bar (top) | Not implemented |
| Reset / Save As / Help doc links | Clear button only |
| Results + Visualizations tabs | Results tab only (no viz tab) |

### Search Controls
| Panther | kjtcom |
|---------|--------|
| Search / PantherFlow toggle | NoSQL / Logs chips (decorative) |
| Log type dropdown (Crowdstrike FDREvent) | t_log_type field filter |
| Time range dropdown (Last 3 days) | All time chip (decorative) |
| Database selector (Logs) | locations collection (fixed) |

### Field Sidebar
| Panther | kjtcom |
|---------|--------|
| SELECTED FIELDS section | Schema tab (separate tab) |
| AVAILABLE FIELDS section | Schema tab field list |
| Panther Fields / log-type Fields groups | All fields in one list |
| Search columns input | Not implemented |
| Field remove (-) button | Not applicable |

### Results Table
| Panther | kjtcom |
|---------|--------|
| Column headers (TIME UTC, DATABASE, LOG TYPE, EVENT) | Row-based entity cards |
| Event count badge ("2 events") | Pagination info ("Page X of Y") |
| Summarize with AI button | Not implemented |
| Share button | Copy JSON button |
| Table/card view toggle | Card view only |
| Click row -> expand | Click row -> detail panel slide-in |

### Design System
| Panther | kjtcom |
|---------|--------|
| MUI (Material UI) components | Custom Flutter widgets |
| MuiPaper-inverseRaisedToBrand | Tokens.surfaceElevated |
| Dark theme with teal/green accents | Dark gothic theme with green accents |
| css-z3bvxq (dynamic MUI classes) | Static Tokens.* constants |
| ECharts bar chart (histogram) | No result visualization |

## Key Takeaways

1. Panther uses a richer query language (PantherFlow) with regex, aggregations, pipes, and time functions. kjtcom uses simplified field-operator-value clauses.
2. Panther's field sidebar with selected/available fields is a UX pattern worth considering for kjtcom's Schema tab.
3. The "Summarize with AI" button is a notable feature gap.
4. Panther's time-series histogram above results provides temporal context that kjtcom lacks.
5. Both use dark themes with similar accent color palettes (teal/green).
