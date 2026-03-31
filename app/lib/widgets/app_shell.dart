import 'package:flutter/material.dart';
import '../theme/tokens.dart';
import 'globe_hero.dart';
import 'query_editor.dart';
import 'results_table.dart';
import 'detail_panel.dart';
import 'kjtcom_tab_bar.dart';
import 'entity_count_row.dart';

/// Outermost container - component-patterns.md Section 1.
/// Dark, full-bleed, 24px content padding, 12px outer radius.
class AppShell extends StatelessWidget {
  const AppShell({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Tokens.surfaceBase,
      body: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: Tokens.maxWidth),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Globe hero behind header + query editor
              Stack(
                children: [
                  const GlobeHero(),
                  Padding(
                    padding: const EdgeInsets.symmetric(
                      horizontal: Tokens.space6,
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        const SizedBox(height: Tokens.space5),
                        _buildHeaderBar(),
                        const SizedBox(height: Tokens.space2),
                        _buildSectionHeader(),
                        const SizedBox(height: Tokens.space2),
                        const QueryEditor(),
                      ],
                    ),
                  ),
                ],
              ),
              // Tab bar + entity count + results
              Expanded(
                child: Padding(
                  padding: const EdgeInsets.symmetric(
                    horizontal: Tokens.space6,
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      const KjtcomTabBar(),
                      const EntityCountRow(),
                      const Expanded(child: _ResultsArea()),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildHeaderBar() {
    return Row(
      children: [
        // Logo - token: color.accent.green, typography.size.2xl
        const Text(
          'kjtcom',
          style: TextStyle(
            fontFamily: Tokens.fontSans,
            fontSize: Tokens.size2xl,
            fontWeight: FontWeight.w500,
            color: Tokens.accentGreen,
            letterSpacing: 0.5,
          ),
        ),
        const SizedBox(width: Tokens.space3),
        // "Investigate" badge
        Container(
          padding: const EdgeInsets.symmetric(
            horizontal: Tokens.space2,
            vertical: 2,
          ),
          decoration: BoxDecoration(
            border: Border.all(color: Tokens.borderDefault),
            borderRadius: BorderRadius.circular(Tokens.radiusMd),
          ),
          child: const Text(
            'Investigate',
            style: TextStyle(
              fontFamily: Tokens.fontSans,
              fontSize: Tokens.sizeBase,
              color: Tokens.textSecondary,
            ),
          ),
        ),
        const Spacer(),
        // "staging" badge
        Container(
          padding: const EdgeInsets.symmetric(
            horizontal: Tokens.space2,
            vertical: 2,
          ),
          decoration: BoxDecoration(
            color: const Color(0xFF0D2818),
            border: Border.all(color: Tokens.surfaceFilterPositive),
            borderRadius: BorderRadius.circular(Tokens.radiusMd),
          ),
          child: const Text(
            'staging',
            style: TextStyle(
              fontFamily: Tokens.fontSans,
              fontSize: Tokens.sizeBase,
              color: Tokens.accentGreen,
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildSectionHeader() {
    return const Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Search',
          style: TextStyle(
            fontFamily: Tokens.fontSans,
            fontSize: Tokens.sizeXl,
            fontWeight: FontWeight.w500,
            color: Tokens.textPrimary,
          ),
        ),
        SizedBox(height: 2),
        Text(
          'Query Thompson Indicator Fields across all pipelines',
          style: TextStyle(
            fontFamily: Tokens.fontSans,
            fontSize: Tokens.sizeBase,
            color: Tokens.textSecondary,
          ),
        ),
      ],
    );
  }
}

/// Results table + optional detail panel side-by-side.
class _ResultsArea extends StatelessWidget {
  const _ResultsArea();

  @override
  Widget build(BuildContext context) {
    final width = MediaQuery.sizeOf(context).width;
    final isWide = width >= Tokens.bpDesktop;

    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Expanded(child: ResultsTable()),
        if (isWide) const DetailPanel(),
      ],
    );
  }
}
