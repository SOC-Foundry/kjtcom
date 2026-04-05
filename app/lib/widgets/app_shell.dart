import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import '../theme/tokens.dart';
import '../providers/selection_provider.dart';
import '../providers/tab_provider.dart';
import 'globe_hero.dart';
import 'query_editor.dart';
import 'results_table.dart';
import 'detail_panel.dart';
import 'kjtcom_tab_bar.dart';
import 'entity_count_row.dart';
import 'map_tab.dart';
import 'globe_tab.dart';
import 'iao_tab.dart';
import 'gotcha_tab.dart';
import 'schema_tab.dart';

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
              // Tab bar + content area
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
                      const Expanded(child: _TabContent()),
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
        // Logo - Cinzel gothic font, tech green
        Text(
          'kjtcom',
          style: GoogleFonts.cinzel(
            fontSize: Tokens.size2xl,
            fontWeight: FontWeight.w600,
            color: Tokens.accentGreen,
            letterSpacing: 1.0,
          ),
        ),
        const SizedBox(width: Tokens.space3),
        // "Investigate" badge - gothic border
        Container(
          padding: const EdgeInsets.symmetric(
            horizontal: Tokens.space2,
            vertical: 2,
          ),
          decoration: BoxDecoration(
            border: Border.all(color: const Color(0x4D4ADE80)),
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
      ],
    );
  }

  Widget _buildSectionHeader() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Search',
          style: GoogleFonts.cinzel(
            fontSize: Tokens.sizeXl,
            fontWeight: FontWeight.w500,
            color: Tokens.textPrimary,
          ),
        ),
        const SizedBox(height: 2),
        const Text(
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

/// Switches content area based on active tab.
class _TabContent extends ConsumerWidget {
  const _TabContent();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final activeTab = ref.watch(activeTabProvider);

    return switch (activeTab) {
      0 => const _ResultsArea(),
      1 => const _TabWithDetailPanel(child: MapTab()),
      2 => const _TabWithDetailPanel(child: GlobeTab()),
      3 => const IaoTab(),
      4 => const GotchaTab(),
      5 => const SchemaTab(),
      _ => const _ResultsArea(),
    };
  }
}

/// Results table + optional detail panel side-by-side.
class _ResultsArea extends ConsumerWidget {
  const _ResultsArea();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final width = MediaQuery.sizeOf(context).width;
    final isWide = width >= Tokens.bpDesktop;

    if (isWide) {
      // Desktop: side-by-side with animated detail panel
      return Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Expanded(child: ResultsTable()),
          const DetailPanel(),
        ],
      );
    }

    // Mobile/tablet: overlay detail panel from right
    final hasSelection = ref.watch(selectedEntityProvider) != null;
    return Stack(
      children: [
        const Positioned.fill(child: ResultsTable()),
        if (hasSelection) ...[
          Positioned.fill(
            child: GestureDetector(
              onTap: () =>
                  ref.read(selectedEntityProvider.notifier).select(null),
              child: const ColoredBox(color: Color(0x80000000)),
            ),
          ),
          const Positioned(
            right: 0,
            top: 0,
            bottom: 0,
            child: DetailPanel(),
          ),
        ],
      ],
    );
  }
}

/// Wraps a tab widget (Map, Globe) with a side detail panel on desktop.
class _TabWithDetailPanel extends ConsumerWidget {
  final Widget child;
  const _TabWithDetailPanel({required this.child});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final width = MediaQuery.sizeOf(context).width;
    final isWide = width >= Tokens.bpDesktop;

    if (isWide) {
      return Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Expanded(child: child),
          const DetailPanel(),
        ],
      );
    }

    final hasSelection = ref.watch(selectedEntityProvider) != null;
    return Stack(
      children: [
        Positioned.fill(child: child),
        if (hasSelection) ...[
          Positioned.fill(
            child: GestureDetector(
              onTap: () =>
                  ref.read(selectedEntityProvider.notifier).select(null),
              child: const ColoredBox(color: Color(0x80000000)),
            ),
          ),
          const Positioned(
            right: 0,
            top: 0,
            bottom: 0,
            child: DetailPanel(),
          ),
        ],
      ],
    );
  }
}
