import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import '../theme/tokens.dart';
import '../providers/query_provider.dart';
import '../providers/tab_provider.dart';

class _SchemaField {
  final String name;
  final String type;
  final String description;
  final String examples;
  final bool viewOnly;

  const _SchemaField({
    required this.name,
    required this.type,
    required this.description,
    required this.examples,
    this.viewOnly = false,
  });
}

const _schemaFields = [
  _SchemaField(
    name: 't_log_type',
    type: 'string',
    description: 'Pipeline ID',
    examples: 'calgold, ricksteves, tripledb',
  ),
  _SchemaField(
    name: 't_any_names',
    type: 'array[string]',
    description: 'Entity names',
    examples: 'eiffel tower, mama\'s soul food',
  ),
  _SchemaField(
    name: 't_any_people',
    type: 'array[string]',
    description: 'People mentioned',
    examples: 'rick steves, huell howser',
  ),
  _SchemaField(
    name: 't_any_cities',
    type: 'array[string]',
    description: 'City names',
    examples: 'paris, memphis',
  ),
  _SchemaField(
    name: 't_any_states',
    type: 'array[string]',
    description: 'State codes',
    examples: 'ca, ny, tn',
  ),
  _SchemaField(
    name: 't_any_counties',
    type: 'array[string]',
    description: 'County names',
    examples: 'los angeles county',
  ),
  _SchemaField(
    name: 't_any_countries',
    type: 'array[string]',
    description: 'Country names',
    examples: 'france, italy, us',
  ),
  _SchemaField(
    name: 't_any_country_codes',
    type: 'array[string]',
    description: 'ISO 3166-1 alpha-2',
    examples: 'fr, it, us',
  ),
  _SchemaField(
    name: 't_any_regions',
    type: 'array[string]',
    description: 'Sub-country regions',
    examples: 'bavaria, tuscany',
  ),
  _SchemaField(
    name: 't_any_keywords',
    type: 'array[string]',
    description: 'Searchable terms',
    examples: 'gothic, museum, barbecue',
  ),
  _SchemaField(
    name: 't_any_categories',
    type: 'array[string]',
    description: 'Category tags',
    examples: 'landmark, restaurant',
  ),
  _SchemaField(
    name: 't_any_actors',
    type: 'array[string]',
    description: 'Featured people',
    examples: 'guy fieri, rick steves',
  ),
  _SchemaField(
    name: 't_any_roles',
    type: 'array[string]',
    description: 'Role types',
    examples: 'host, guide, chef',
  ),
  _SchemaField(
    name: 't_any_shows',
    type: 'array[string]',
    description: 'Show names',
    examples: 'california\'s gold, diners drive-ins and dives',
  ),
  _SchemaField(
    name: 't_any_cuisines',
    type: 'array[string]',
    description: 'Cuisine types',
    examples: 'french, mexican, barbecue',
  ),
  _SchemaField(
    name: 't_any_dishes',
    type: 'array[string]',
    description: 'Food items',
    examples: 'gelato, fried chicken',
  ),
  _SchemaField(
    name: 't_any_eras',
    type: 'array[string]',
    description: 'Historical periods',
    examples: 'medieval, roman',
  ),
  _SchemaField(
    name: 't_any_continents',
    type: 'array[string]',
    description: 'Continents',
    examples: 'europe, north america',
  ),
  _SchemaField(
    name: 't_any_urls',
    type: 'array[string]',
    description: 'URLs',
    examples: 'youtube links, websites',
  ),
  _SchemaField(
    name: 't_any_video_ids',
    type: 'array[string]',
    description: 'YouTube video IDs',
    examples: 'dQw4w9WgXcQ',
  ),
  _SchemaField(
    name: 't_any_coordinates',
    type: 'array[map]',
    description: 'Lat/lon pairs',
    examples: '{"lat": 48.85, "lon": 2.29}',
    viewOnly: true,
  ),
  _SchemaField(
    name: 't_any_geohashes',
    type: 'array[string]',
    description: 'Geohash prefixes',
    examples: 'u09t, u09tv',
    viewOnly: true,
  ),
];

class SchemaTab extends ConsumerWidget {
  const SchemaTab({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return ListView(
      padding: const EdgeInsets.all(Tokens.space4),
      children: [
        // Header
        Text(
          'Thompson Indicator Fields',
          style: GoogleFonts.cinzel(
            fontSize: Tokens.size2xl,
            fontWeight: FontWeight.w700,
            color: Tokens.accentGreen,
          ),
        ),
        const SizedBox(height: Tokens.space1),
        const Text(
          '22 universal fields across all pipeline datasets. '
          'Click any field to build a query.',
          style: TextStyle(
            fontFamily: Tokens.fontSans,
            fontSize: Tokens.sizeBase,
            color: Tokens.textSecondary,
            height: 1.4,
          ),
        ),
        const SizedBox(height: Tokens.space4),
        // Field cards
        ..._schemaFields.map((f) => _FieldCard(field: f)),
        const SizedBox(height: Tokens.space8),
      ],
    );
  }
}

class _FieldCard extends ConsumerWidget {
  final _SchemaField field;
  const _FieldCard({required this.field});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Padding(
      padding: const EdgeInsets.only(bottom: Tokens.space3),
      child: Container(
        padding: const EdgeInsets.all(Tokens.space4),
        decoration: Tokens.gothicCardDecoration(radius: Tokens.radiusXl),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                // Field name
                Expanded(
                  child: Text(
                    field.name,
                    style: const TextStyle(
                      fontFamily: Tokens.fontMono,
                      fontSize: Tokens.sizeMd,
                      fontWeight: FontWeight.w500,
                      color: Tokens.syntaxField,
                    ),
                  ),
                ),
                // Type badge
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 6,
                    vertical: 2,
                  ),
                  decoration: BoxDecoration(
                    border: Border.all(color: const Color(0x4D4ADE80)),
                    borderRadius: BorderRadius.circular(Tokens.radiusSm),
                  ),
                  child: Text(
                    field.type,
                    style: const TextStyle(
                      fontFamily: Tokens.fontMono,
                      fontSize: Tokens.sizeXs,
                      color: Tokens.textSecondary,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: Tokens.space2),
            // Description
            Text(
              field.description,
              style: const TextStyle(
                fontFamily: Tokens.fontSans,
                fontSize: Tokens.sizeBase,
                color: Tokens.textSecondary,
              ),
            ),
            const SizedBox(height: Tokens.space1),
            // Examples
            Text(
              field.examples,
              style: const TextStyle(
                fontFamily: Tokens.fontMono,
                fontSize: Tokens.sizeSm,
                color: Tokens.textMuted,
              ),
            ),
            // Add to query button (unless view-only)
            if (!field.viewOnly) ...[
              const SizedBox(height: Tokens.space3),
              MouseRegion(
                cursor: SystemMouseCursors.click,
                child: GestureDetector(
                  onTap: () {
                    final op =
                        field.name == 't_log_type' ? '==' : 'contains';
                    final controller = ref.read(queryTextControllerProvider);
                    final clause = '| where ${field.name} $op ""';
                    final current = controller.text.trimRight();
                    final newText = current.isEmpty ? clause : '$current\n$clause';
                    // Set flag BEFORE any changes to prevent ref.listen override
                    ref.read(programmaticUpdateProvider.notifier).state = true;
                    controller.text = newText;
                    
                    // Cursor between the quotes (one char before end of clause)
                    // Use addPostFrameCallback to ensure selection survives the rebuild (G45)
                    final cursorPos = newText.length - 1;
                    WidgetsBinding.instance.addPostFrameCallback((_) {
                      controller.selection = TextSelection.collapsed(
                        offset: cursorPos,
                      );
                      debugPrint('[W2] Schema builder: deferred cursor set between quotes at $cursorPos');
                    });
                    
                    ref.read(queryProvider.notifier).setText(newText);
                    ref.read(activeTabProvider.notifier).state = 0;
                    
                    // Clear flag after microtask (next event loop tick)
                    Future.microtask(() {
                      ref.read(programmaticUpdateProvider.notifier).state = false;
                    });
                  },
                  child: Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: Tokens.space3,
                      vertical: Tokens.space1,
                    ),
                    decoration: BoxDecoration(
                      border: Border.all(color: Tokens.accentGreen),
                      borderRadius: BorderRadius.circular(Tokens.radiusMd),
                    ),
                    child: const Text(
                      '+ Add to query',
                      style: TextStyle(
                        fontFamily: Tokens.fontSans,
                        fontSize: Tokens.sizeSm,
                        fontWeight: FontWeight.w500,
                        color: Tokens.accentGreen,
                      ),
                    ),
                  ),
                ),
              ),
            ] else ...[
              const SizedBox(height: Tokens.space2),
              const Text(
                'View only',
                style: TextStyle(
                  fontFamily: Tokens.fontSans,
                  fontSize: Tokens.sizeXs,
                  color: Tokens.textMuted,
                  fontStyle: FontStyle.italic,
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
