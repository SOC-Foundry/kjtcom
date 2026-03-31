import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../theme/tokens.dart';
import '../models/location_entity.dart';
import '../providers/firestore_provider.dart';
import '../providers/selection_provider.dart';
import 'pipeline_badge.dart';

/// Component-patterns.md Section 4 - Results Table.
/// Single-line rows, 5-column grid, pipeline-colored dots.
class ResultsTable extends ConsumerWidget {
  const ResultsTable({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final asyncResults = ref.watch(resultsProvider);
    final selected = ref.watch(selectedEntityProvider);

    return asyncResults.when(
      loading: () => const Center(
        child: CircularProgressIndicator(color: Tokens.accentGreen),
      ),
      error: (err, _) => Center(
        child: Text(
          'Query error: $err',
          style: const TextStyle(color: Tokens.accentRed, fontSize: Tokens.sizeMd),
        ),
      ),
      data: (entities) => Column(
        children: [
          // Column headers
          _buildHeader(context),
          // Data rows
          Expanded(
            child: ListView.builder(
              itemCount: entities.length,
              itemBuilder: (context, index) {
                final entity = entities[index];
                final isSelected = selected?.id == entity.id;
                return _buildRow(context, ref, entity, isSelected);
              },
            ),
          ),
        ],
      ),
    );
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
