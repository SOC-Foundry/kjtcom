import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import '../theme/tokens.dart';
import '../providers/firestore_provider.dart';
import '../providers/query_provider.dart';
import '../providers/tab_provider.dart';

/// Globe tab - stats dashboard with continent cards + country grid.
/// Globe hero background at 15% opacity. Click filters to Results tab.
class GlobeTab extends ConsumerWidget {
  const GlobeTab({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final asyncResult = ref.watch(queryResultProvider);

    return asyncResult.when(
      loading: () => const Center(
        child: CircularProgressIndicator(color: Tokens.accentGreen),
      ),
      error: (err, _) => Center(
        child: Text('Globe error: $err',
            style: const TextStyle(color: Tokens.accentRed)),
      ),
      data: (queryResult) {
        final entities = queryResult.entities;

        // Build continent -> country -> count breakdown.
        final Map<String, Map<String, int>> continentData = {};
        final Map<String, int> countryTotals = {};
        final Map<String, int> pipelineCounts = {};

        for (final e in entities) {
          // Pipeline counts
          final pipe = e.logType;
          pipelineCounts[pipe] = (pipelineCounts[pipe] ?? 0) + 1;

          // Continent/country breakdown
          final continents = e.continents;
          final countries = e.countries;
          final continent =
              continents.isNotEmpty ? continents.first : 'Unknown';
          final country = countries.isNotEmpty ? countries.first : 'Unknown';

          continentData.putIfAbsent(continent, () => {});
          continentData[continent]![country] =
              (continentData[continent]![country] ?? 0) + 1;
          countryTotals[country] = (countryTotals[country] ?? 0) + 1;
        }

        // Sort continents by entity count descending.
        final sortedContinents = continentData.entries.toList()
          ..sort((a, b) {
            final aCount =
                a.value.values.fold<int>(0, (s, v) => s + v);
            final bCount =
                b.value.values.fold<int>(0, (s, v) => s + v);
            return bCount.compareTo(aCount);
          });

        // Sort countries by count descending.
        final sortedCountries = countryTotals.entries.toList()
          ..sort((a, b) => b.value.compareTo(a.value));

        return Stack(
          children: [
            // Globe hero background
            Positioned.fill(
              child: Opacity(
                opacity: 0.15,
                child: Image.asset(
                  'assets/globe_hero.jpg',
                  fit: BoxFit.cover,
                  errorBuilder: (_, _, _) => const SizedBox.shrink(),
                ),
              ),
            ),
            // Content
            ListView(
              padding: const EdgeInsets.all(Tokens.space4),
              children: [
                // Title
                Text(
                  'Global Distribution',
                  style: GoogleFonts.cinzel(
                    fontSize: 20,
                    fontWeight: FontWeight.w600,
                    color: Tokens.textPrimary,
                  ),
                ),
                const SizedBox(height: Tokens.space1),
                Text(
                  '${entities.length} entities across '
                  '${countryTotals.length} countries, '
                  '${continentData.length} continents',
                  style: const TextStyle(
                    fontFamily: Tokens.fontMono,
                    fontSize: Tokens.sizeSm,
                    color: Tokens.textSecondary,
                  ),
                ),
                const SizedBox(height: Tokens.space4),

                // Pipeline distribution bar
                _buildPipelineBar(pipelineCounts, entities.length),
                const SizedBox(height: Tokens.space4),

                // Continent cards
                Text(
                  'Continents',
                  style: GoogleFonts.cinzel(
                    fontSize: Tokens.sizeXl,
                    fontWeight: FontWeight.w500,
                    color: Tokens.textPrimary,
                  ),
                ),
                const SizedBox(height: Tokens.space2),
                ...sortedContinents.map((entry) => _ContinentCard(
                      continent: entry.key,
                      countryCounts: entry.value,
                      ref: ref,
                    )),

                const SizedBox(height: Tokens.space4),

                // Country grid
                Text(
                  'Countries',
                  style: GoogleFonts.cinzel(
                    fontSize: Tokens.sizeXl,
                    fontWeight: FontWeight.w500,
                    color: Tokens.textPrimary,
                  ),
                ),
                const SizedBox(height: Tokens.space2),
                Wrap(
                  spacing: Tokens.space2,
                  runSpacing: Tokens.space2,
                  children: sortedCountries.map((entry) {
                    return _CountryChip(
                      country: entry.key,
                      count: entry.value,
                      ref: ref,
                    );
                  }).toList(),
                ),
                const SizedBox(height: Tokens.space8),
              ],
            ),
          ],
        );
      },
    );
  }

  Widget _buildPipelineBar(Map<String, int> counts, int total) {
    if (total == 0) return const SizedBox.shrink();
    final pipelines = [
      ('calgold', 'CalGold', Tokens.pipelineCalGold),
      ('ricksteves', 'RickSteves', Tokens.pipelineRickSteves),
      ('tripledb', 'TripleDB', Tokens.pipelineTripleDB),
    ];

    return Container(
      padding: const EdgeInsets.all(Tokens.space3),
      decoration: Tokens.gothicCardDecoration(),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Pipeline Distribution',
            style: TextStyle(
              fontFamily: Tokens.fontSans,
              fontSize: Tokens.sizeMd,
              color: Tokens.textPrimary,
              fontWeight: FontWeight.w500,
            ),
          ),
          const SizedBox(height: Tokens.space2),
          // Stacked bar
          ClipRRect(
            borderRadius: BorderRadius.circular(Tokens.radiusSm),
            child: SizedBox(
              height: 8,
              child: Row(
                children: pipelines
                    .where((p) => (counts[p.$1] ?? 0) > 0)
                    .map((p) => Expanded(
                          flex: counts[p.$1]!,
                          child: Container(color: p.$3),
                        ))
                    .toList(),
              ),
            ),
          ),
          const SizedBox(height: Tokens.space2),
          // Legend
          Row(
            children: pipelines.map((p) {
              final count = counts[p.$1] ?? 0;
              if (count == 0) return const SizedBox.shrink();
              return Padding(
                padding: const EdgeInsets.only(right: Tokens.space4),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Container(
                      width: 8,
                      height: 8,
                      decoration: BoxDecoration(
                        color: p.$3,
                        shape: BoxShape.circle,
                      ),
                    ),
                    const SizedBox(width: Tokens.space1),
                    Text(
                      '${p.$2} ($count)',
                      style: const TextStyle(
                        fontFamily: Tokens.fontMono,
                        fontSize: Tokens.sizeSm,
                        color: Tokens.textSecondary,
                      ),
                    ),
                  ],
                ),
              );
            }).toList(),
          ),
        ],
      ),
    );
  }
}

class _ContinentCard extends StatefulWidget {
  final String continent;
  final Map<String, int> countryCounts;
  final WidgetRef ref;
  const _ContinentCard({
    required this.continent,
    required this.countryCounts,
    required this.ref,
  });

  @override
  State<_ContinentCard> createState() => _ContinentCardState();
}

class _ContinentCardState extends State<_ContinentCard> {
  bool _hovering = false;

  @override
  Widget build(BuildContext context) {
    final total = widget.countryCounts.values.fold<int>(0, (s, v) => s + v);
    final sorted = widget.countryCounts.entries.toList()
      ..sort((a, b) => b.value.compareTo(a.value));
    final top3 = sorted.take(3).toList();

    return Padding(
      padding: const EdgeInsets.only(bottom: Tokens.space2),
      child: MouseRegion(
        cursor: SystemMouseCursors.click,
        onEnter: (_) => setState(() => _hovering = true),
        onExit: (_) => setState(() => _hovering = false),
        child: GestureDetector(
          onTap: () {
            widget.ref.read(queryProvider.notifier).appendClause(
                  't_any_continents',
                  'contains',
                  widget.continent.toLowerCase(),
                );
            widget.ref.read(activeTabProvider.notifier).state = 0;
          },
          child: AnimatedContainer(
            duration: Tokens.rowHighlight,
            padding: const EdgeInsets.all(Tokens.space3),
            decoration: Tokens.gothicCardDecoration().copyWith(
              boxShadow: _hovering ? Tokens.glowGreen : null,
            ),
            child: Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        widget.continent,
                        style: GoogleFonts.cinzel(
                          fontSize: Tokens.sizeLg,
                          fontWeight: FontWeight.w600,
                          color: Tokens.textPrimary,
                        ),
                      ),
                      const SizedBox(height: Tokens.space1),
                      Text(
                        '$total entities - ${widget.countryCounts.length} countries',
                        style: const TextStyle(
                          fontFamily: Tokens.fontMono,
                          fontSize: Tokens.sizeSm,
                          color: Tokens.textSecondary,
                        ),
                      ),
                    ],
                  ),
                ),
                // Top 3 countries
                Column(
                  crossAxisAlignment: CrossAxisAlignment.end,
                  children: top3
                      .map((e) => Text(
                            '${e.key} (${e.value})',
                            style: const TextStyle(
                              fontFamily: Tokens.fontMono,
                              fontSize: Tokens.sizeSm,
                              color: Tokens.textMuted,
                            ),
                          ))
                      .toList(),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _CountryChip extends StatefulWidget {
  final String country;
  final int count;
  final WidgetRef ref;
  const _CountryChip({
    required this.country,
    required this.count,
    required this.ref,
  });

  @override
  State<_CountryChip> createState() => _CountryChipState();
}

class _CountryChipState extends State<_CountryChip> {
  bool _hovering = false;

  @override
  Widget build(BuildContext context) {
    return MouseRegion(
      cursor: SystemMouseCursors.click,
      onEnter: (_) => setState(() => _hovering = true),
      onExit: (_) => setState(() => _hovering = false),
      child: GestureDetector(
        onTap: () {
          widget.ref.read(queryProvider.notifier).appendClause(
                't_any_countries',
                'contains',
                widget.country.toLowerCase(),
              );
          widget.ref.read(activeTabProvider.notifier).state = 0;
        },
        child: AnimatedContainer(
          duration: Tokens.rowHighlight,
          padding: const EdgeInsets.symmetric(
            horizontal: Tokens.space3,
            vertical: Tokens.space2,
          ),
          decoration: BoxDecoration(
            color: Tokens.surfaceElevated,
            borderRadius: BorderRadius.circular(Tokens.radiusMd),
            border: Border.all(
              color: _hovering
                  ? const Color(0x4D4ADE80)
                  : Tokens.borderDefault,
            ),
            boxShadow: _hovering ? Tokens.glowGreen : null,
          ),
          child: Text.rich(
            TextSpan(children: [
              TextSpan(
                text: widget.country,
                style: const TextStyle(
                  fontFamily: Tokens.fontSans,
                  fontSize: Tokens.sizeSm,
                  color: Tokens.textPrimary,
                ),
              ),
              TextSpan(
                text: ' ${widget.count}',
                style: const TextStyle(
                  fontFamily: Tokens.fontMono,
                  fontSize: Tokens.sizeSm,
                  color: Tokens.accentGreen,
                ),
              ),
            ]),
          ),
        ),
      ),
    );
  }
}
