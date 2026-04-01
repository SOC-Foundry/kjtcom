# kjtcom - Build v6.17 (Phase 6c - Implementation)

**Pipeline:** kjtcom (cross-pipeline Flutter app)
**Phase:** 6c (Implementation)
**Iteration:** 17 (global counter)
**Executor:** Claude Code (Opus)
**Machine:** tsP3-cos (ThinkStation P3 Ultra SFF G2)
**Date:** March 2026

## Implementation Log

### Step 1: Flutter Project Scaffold

- `flutter create app --project-name kjtcom --platforms web` in repo root
- Flutter 3.41.6 (stable), Dart SDK ^3.11.4
- Added dependencies: firebase_core ^3.13.0, cloud_firestore ^5.6.0, flutter_riverpod ^2.6.1, google_fonts ^6.2.1
- Downloaded Geist Sans + Geist Mono fonts from npm (`geist@1.7.0`), bundled as TTF assets (Regular 400, Medium 500)
- Declared font families in pubspec.yaml: `GeistSans`, `GeistMono`
- Updated firebase.json hosting public to `app/build/web`

### Step 2: Design Tokens -> Dart Constants

- `lib/theme/tokens.dart`: Every color, size, spacing, radius, breakpoint, and animation duration from design-tokens.json expressed as `static const` values
- `lib/theme/theme.dart`: ThemeData built from tokens - dark brightness, surfaceBase background, Geist Sans default font
- Pipeline color + badge helper methods on Tokens class

### Step 3: Data Layer

- `lib/models/location_entity.dart`: Firestore document model mapping t_any_* fields. Factory constructor from `DocumentSnapshot<Map<String, dynamic>>`. Computed properties: name, city, country, show, displayFields
- `lib/models/query_clause.dart`: Regex parser for `| where field op "value"` syntax. Static parseAll for multi-line queries.
- `lib/providers/query_provider.dart`: Riverpod Notifier holding query text. `appendClause` method for +filter/-exclude buttons.
- `lib/providers/firestore_provider.dart`: StreamProvider that watches query text, parses clauses, builds Firestore compound query (one arrayContains server-side, rest client-side). Limit 200.
- `lib/providers/selection_provider.dart`: StateProvider for selected entity.

### Step 4: P0 Components (App Shell + Query Editor)

- `lib/widgets/app_shell.dart`: Scaffold with base surface background, 1440px max width, header bar (logo, Investigate badge, staging badge), section header, query editor, tab bar, results area with detail panel
- `lib/widgets/query_editor.dart`: Container with elevated surface, border, 8px radius. Chip row (NoSQL active, Logs, locations, All time). Line-numbered syntax-highlighted display. Transparent TextField overlay for editing. Search button (CTA green, 6px radius). Regex tokenizer for syntax highlighting (field/operator/value/keyword colors)

### Step 5: P0 Components (Results Table + Detail Panel)

- `lib/widgets/results_table.dart`: Column headers (elevated bg, 11px secondary text). Data rows with pipeline dot, NAME/CITY/COUNTRY/SHOW columns. Responsive - CITY hidden below tablet, COUNTRY hidden below desktop. Row selection with hover highlight animation.
- `lib/widgets/detail_panel.dart`: 320px width, border-left. Entity detail header with close button. Field cards for each t_any_* and t_enrichment.* field. Value rendering: arrays as blue chips, numbers as orange, booleans as green/red, maps as nested key-value. +filter/-exclude buttons on array fields that call queryProvider.appendClause.
- `lib/widgets/pipeline_badge.dart`: Overlay bg chip with pipeline-colored text.

### Step 6: P1/P2 Components

- `lib/widgets/kjtcom_tab_bar.dart`: Results (active), Map, Globe tabs with blue underline on active
- `lib/widgets/entity_count_row.dart`: Watches resultsProvider for entity count + countryCountProvider for distinct countries
- `lib/widgets/globe_hero.dart`: 260px height, radial gradient placeholder at 15% opacity (globe_hero.jpg not yet generated)

### Step 7: Firebase Configuration

- Firebase CLI logged in as kthompson@tachtech.net - but kjtcom-c78cd is under socfoundry.com org
- SA file at ~/.config/gcloud/kjtcom-sa.json is MISSING on tsP3-cos
- Created placeholder firebase_options.dart with projectId kjtcom-c78cd
- BLOCKER: Need `firebase login` with socfoundry account, then `flutterfire configure` to generate real config

### Step 8: Verification

- `flutter analyze` -> 0 issues
- `flutter build web` -> success (17.0s, CanvasKit default)
- `flutter test` -> 3/3 pass (QueryClause parser tests)
- Build output at app/build/web/ matching firebase.json hosting public

## File Inventory

```
app/lib/
  main.dart                         # Entry point, Firebase init, ProviderScope
  firebase_options.dart             # PLACEHOLDER - needs flutterfire configure
  theme/
    tokens.dart                     # Design tokens from design-tokens.json
    theme.dart                      # ThemeData from tokens
  models/
    location_entity.dart            # Firestore document model
    query_clause.dart               # Query syntax parser
  providers/
    query_provider.dart             # Query text state (Riverpod)
    firestore_provider.dart         # Firestore stream + country count
    selection_provider.dart         # Selected entity state
  widgets/
    app_shell.dart                  # Outer container + layout
    query_editor.dart               # Syntax-highlighted editor
    results_table.dart              # 5-column entity list
    detail_panel.dart               # Entity fields + filter/exclude
    pipeline_badge.dart             # Colored pipeline chip
    kjtcom_tab_bar.dart             # Results/Map/Globe tabs
    entity_count_row.dart           # "N entities across M countries"
    globe_hero.dart                 # Background gradient placeholder
app/assets/fonts/
  Geist-Regular.ttf                 # 126KB
  Geist-Medium.ttf                  # 128KB
  GeistMono-Regular.ttf             # 148KB
  GeistMono-Medium.ttf              # 149KB
app/test/
  widget_test.dart                  # 3 QueryClause parser tests
```

## Technical Notes

- Firestore query limitation: only one `arrayContains` per compound query. First `contains` clause is server-side, additional are client-side filtered on the 200-doc result set.
- Flutter 3.41 deprecated `--web-renderer canvaskit` flag. CanvasKit is the default renderer.
- Geist font files sourced from npm `geist@1.7.0`, SIL Open Font License.
- No `cupertino_icons` usage - tree-shaking warning is cosmetic.
