import 'dart:math' as math;
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../theme/tokens.dart';
import '../models/location_entity.dart';
import '../providers/firestore_provider.dart';
import '../providers/selection_provider.dart';
import '../providers/pagination_provider.dart';
import 'pipeline_badge.dart';

/// Component-patterns.md Section 4 - Results Table.
/// Single-line rows, 5-column grid, pipeline-colored dots.
/// Paginated with 20/50/100 dropdown and page navigation.
class ResultsTable extends ConsumerWidget {
  const ResultsTable({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final asyncResult = ref.watch(queryResultProvider);
    final selected = ref.watch(selectedEntityProvider);

    return asyncResult.when(
      loading: () => const Center(
        child: CircularProgressIndicator(color: Tokens.accentGreen),
      ),
      error: (err, _) => Center(
        child: Text(
          'Query error: $err',
          style: const TextStyle(color: Tokens.accentRed, fontSize: Tokens.sizeMd),
        ),
      ),
      data: (queryResult) {
        final pageSize = ref.watch(pageSizeProvider);
        final currentPage = ref.watch(currentPageProvider);
        final totalEntities = queryResult.entities.length;
        final totalPages = totalEntities == 0
            ? 1
            : (totalEntities / pageSize).ceil();
        // Clamp current page to valid range.
        final page = currentPage.clamp(0, totalPages - 1);
        final start = page * pageSize;
        final end = math.min(start + pageSize, totalEntities);
        final pageEntities = totalEntities == 0
            ? <LocationEntity>[]
            : queryResult.entities.sublist(start, end);

        return Container(
          decoration: BoxDecoration(
            border: Border.all(
              color: const Color(0x4D4ADE80),
              width: 1,
            ),
            borderRadius: BorderRadius.circular(Tokens.radiusLg),
          ),
          clipBehavior: Clip.antiAlias,
          child: Column(
            children: [
              // Result count + pagination dropdown
              _buildResultBar(queryResult, ref, pageSize),
              // Column headers
              _buildHeader(context),
              // Data rows (paginated)
              Expanded(
                child: ListView.builder(
                  itemCount: pageEntities.length,
                  itemBuilder: (context, index) {
                    final entity = pageEntities[index];
                    final isSelected = selected?.id == entity.id;
                    return _buildRow(context, ref, entity, isSelected);
                  },
                ),
              ),
              // Page navigation
              if (totalEntities > 0)
                _buildPageNav(ref, page, totalPages),
            ],
          ),
        );
      },
    );
  }

  Widget _buildResultBar(QueryResult queryResult, WidgetRef ref, int pageSize) {
    final count = queryResult.entities.length;

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(
        horizontal: Tokens.space2,
        vertical: Tokens.space2 - 2,
      ),
      decoration: const BoxDecoration(
        border: Border(bottom: BorderSide(color: Tokens.borderSubtle)),
      ),
      child: Row(
        children: [
          Text.rich(
            TextSpan(children: [
              TextSpan(
                text: _formatCount(count),
                style: const TextStyle(
                  fontFamily: Tokens.fontMono,
                  fontSize: Tokens.sizeMd,
                  color: Tokens.accentGreen,
                  fontWeight: FontWeight.w600,
                ),
              ),
              const TextSpan(
                text: ' results',
                style: TextStyle(
                  fontFamily: Tokens.fontMono,
                  fontSize: Tokens.sizeMd,
                  color: Tokens.textSecondary,
                ),
              ),
            ]),
          ),
          const Spacer(),
          // Pagination dropdown
          const Text(
            'Show: ',
            style: TextStyle(
              fontFamily: Tokens.fontMono,
              fontSize: Tokens.sizeSm,
              color: Tokens.textSecondary,
            ),
          ),
          _PageSizeDropdown(pageSize: pageSize, ref: ref),
        ],
      ),
    );
  }

  Widget _buildPageNav(WidgetRef ref, int page, int totalPages) {
    return Container(
      padding: const EdgeInsets.symmetric(
        horizontal: Tokens.space2,
        vertical: Tokens.space2,
      ),
      decoration: const BoxDecoration(
        color: Tokens.surfaceElevated,
        border: Border(top: BorderSide(color: Tokens.borderSubtle)),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          _PageButton(
            label: '\u2039 Previous',
            enabled: page > 0,
            onTap: () =>
                ref.read(currentPageProvider.notifier).state = page - 1,
          ),
          const SizedBox(width: Tokens.space4),
          Text(
            'Page ${page + 1} of $totalPages',
            style: const TextStyle(
              fontFamily: Tokens.fontMono,
              fontSize: Tokens.sizeSm,
              color: Tokens.textSecondary,
            ),
          ),
          const SizedBox(width: Tokens.space4),
          _PageButton(
            label: 'Next \u203A',
            enabled: page < totalPages - 1,
            onTap: () =>
                ref.read(currentPageProvider.notifier).state = page + 1,
          ),
        ],
      ),
    );
  }

  String _formatCount(int count) {
    if (count < 1000) return '$count';
    final thousands = count ~/ 1000;
    final remainder = count % 1000;
    if (remainder == 0) return '$thousands,000';
    return '$thousands,${remainder.toString().padLeft(3, '0')}';
  }

  Widget _buildHeader(BuildContext context) {
    final isWide = MediaQuery.sizeOf(context).width >= Tokens.bpTablet;
    return Container(
      decoration: const BoxDecoration(
        color: Tokens.surfaceElevated,
        border: Border(bottom: BorderSide(color: Tokens.borderSubtle)),
      ),
      padding: const EdgeInsets.symmetric(
        horizontal: Tokens.space2,
        vertical: Tokens.space2 - 2,
      ),
      child: Row(
        children: [
          const SizedBox(width: 30), // dot column
          const Expanded(
            child: Text('NAME', style: _headerStyle),
          ),
          if (isWide)
            const SizedBox(
              width: 100,
              child: Text('CITY', style: _headerStyle),
            ),
          if (MediaQuery.sizeOf(context).width >= Tokens.bpDesktop)
            const SizedBox(
              width: 100,
              child: Text('COUNTRY', style: _headerStyle),
            ),
          const SizedBox(
            width: 80,
            child: Text('SHOW', style: _headerStyle, textAlign: TextAlign.center),
          ),
        ],
      ),
    );
  }

  Widget _buildRow(
    BuildContext context,
    WidgetRef ref,
    LocationEntity entity,
    bool isSelected,
  ) {
    final isWide = MediaQuery.sizeOf(context).width >= Tokens.bpTablet;
    return MouseRegion(
      cursor: SystemMouseCursors.click,
      child: GestureDetector(
        onTap: () {
          ref.read(selectedEntityProvider.notifier).state =
              isSelected ? null : entity;
        },
        child: AnimatedContainer(
          duration: Tokens.rowHighlight,
          decoration: BoxDecoration(
            color: isSelected ? Tokens.surfaceRowHover : Colors.transparent,
            border: const Border(
              bottom: BorderSide(color: Tokens.borderSubtle),
            ),
          ),
          padding: const EdgeInsets.all(Tokens.space2),
          child: Row(
            children: [
              // Pipeline dot - 30px column
              SizedBox(
                width: 30,
                child: Text(
                  '\u25CF',
                  style: TextStyle(
                    color: Tokens.pipelineColor(entity.logType),
                    fontSize: Tokens.sizeMd,
                  ),
                ),
              ),
              // NAME - 1fr
              Expanded(
                child: Text(
                  entity.name,
                  overflow: TextOverflow.ellipsis,
                  style: const TextStyle(
                    fontFamily: Tokens.fontSans,
                    fontSize: Tokens.sizeMd,
                    color: Tokens.textPrimary,
                  ),
                ),
              ),
              // CITY - 100px (tablet+)
              if (isWide)
                SizedBox(
                  width: 100,
                  child: Text(
                    entity.city,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(
                      fontFamily: Tokens.fontSans,
                      fontSize: Tokens.sizeMd,
                      color: Tokens.textSecondary,
                    ),
                  ),
                ),
              // COUNTRY - 100px (desktop+)
              if (MediaQuery.sizeOf(context).width >= Tokens.bpDesktop)
                SizedBox(
                  width: 100,
                  child: Text(
                    entity.country,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(
                      fontFamily: Tokens.fontSans,
                      fontSize: Tokens.sizeMd,
                      color: Tokens.textSecondary,
                    ),
                  ),
                ),
              // SHOW badge - 80px
              SizedBox(
                width: 80,
                child: Center(
                  child: PipelineBadge(logType: entity.logType),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  static const _headerStyle = TextStyle(
    fontFamily: Tokens.fontSans,
    fontSize: Tokens.sizeBase,
    color: Tokens.textSecondary,
  );
}

class _PageSizeDropdown extends StatelessWidget {
  final int pageSize;
  final WidgetRef ref;
  const _PageSizeDropdown({required this.pageSize, required this.ref});

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 24,
      padding: const EdgeInsets.symmetric(horizontal: Tokens.space2),
      decoration: BoxDecoration(
        color: Tokens.surfaceOverlay,
        borderRadius: BorderRadius.circular(Tokens.radiusMd),
        border: Border.all(color: Tokens.borderDefault),
      ),
      child: DropdownButtonHideUnderline(
        child: DropdownButton<int>(
          value: pageSize,
          dropdownColor: Tokens.surfaceElevated,
          style: const TextStyle(
            fontFamily: Tokens.fontMono,
            fontSize: Tokens.sizeSm,
            color: Tokens.accentGreen,
          ),
          icon: const Icon(Icons.expand_more, size: 14, color: Tokens.textMuted),
          isDense: true,
          items: const [
            DropdownMenuItem(value: 20, child: Text('20')),
            DropdownMenuItem(value: 50, child: Text('50')),
            DropdownMenuItem(value: 100, child: Text('100')),
          ],
          onChanged: (value) {
            if (value != null) {
              ref.read(pageSizeProvider.notifier).state = value;
            }
          },
        ),
      ),
    );
  }
}

class _PageButton extends StatelessWidget {
  final String label;
  final bool enabled;
  final VoidCallback onTap;
  const _PageButton({
    required this.label,
    required this.enabled,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return MouseRegion(
      cursor: enabled ? SystemMouseCursors.click : SystemMouseCursors.basic,
      child: GestureDetector(
        onTap: enabled ? onTap : null,
        child: Text(
          label,
          style: TextStyle(
            fontFamily: Tokens.fontMono,
            fontSize: Tokens.sizeSm,
            color: enabled ? Tokens.accentGreen : Tokens.textMuted,
          ),
        ),
      ),
    );
  }
}
