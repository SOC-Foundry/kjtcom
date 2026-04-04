import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../theme/tokens.dart';
import '../providers/selection_provider.dart';
import '../providers/query_provider.dart';

/// Component-patterns.md Section 5 - Entity Detail Panel.
/// Slides in from right on row click. Shows t_any_* fields with
/// +filter/-exclude buttons. 320px width, border-left.
class DetailPanel extends ConsumerWidget {
  const DetailPanel({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final entity = ref.watch(selectedEntityProvider);
    final fields = entity?.displayFields;

    return AnimatedContainer(
      duration: Tokens.detailSlide,
      curve: Curves.easeOut,
      width: entity != null ? Tokens.sidebarWidth : 0,
      clipBehavior: Clip.hardEdge,
      decoration: const BoxDecoration(
        color: Tokens.surfaceBase,
        border: Border(
          left: BorderSide(color: Color(0x4D4ADE80), width: 1),
        ),
      ),
      child: entity == null
          ? null
          : SizedBox(
              width: Tokens.sidebarWidth,
              child: Column(
                children: [
                  // Header
                  Padding(
                    padding: const EdgeInsets.all(Tokens.space3),
                    child: Row(
                      children: [
                        const Text(
                          'Entity detail',
                          style: TextStyle(
                            fontFamily: Tokens.fontSans,
                            fontWeight: FontWeight.w500,
                            color: Tokens.textPrimary,
                          ),
                        ),
                        const Spacer(),
                        MouseRegion(
                          cursor: SystemMouseCursors.click,
                          child: GestureDetector(
                            onTap: () {
                              final json = const JsonEncoder.withIndent('  ')
                                  .convert(entity.raw);
                              Clipboard.setData(ClipboardData(text: json));
                              ScaffoldMessenger.of(context).showSnackBar(
                                const SnackBar(
                                  content: Text('JSON copied to clipboard'),
                                  duration: Duration(seconds: 2),
                                  backgroundColor: Tokens.surfaceCta,
                                ),
                              );
                            },
                            child: const Padding(
                              padding: EdgeInsets.only(right: Tokens.space2),
                              child: Icon(
                                Icons.copy,
                                size: 14,
                                color: Tokens.textMuted,
                              ),
                            ),
                          ),
                        ),
                        MouseRegion(
                          cursor: SystemMouseCursors.click,
                          child: GestureDetector(
                            onTap: () => ref
                                .read(selectedEntityProvider.notifier)
                                .state = null,
                            child: const Text(
                              '\u00D7',
                              style: TextStyle(
                                fontSize: 16,
                                color: Tokens.textMuted,
                              ),
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                  // Field cards
                  Expanded(
                    child: ListView(
                      padding: const EdgeInsets.symmetric(
                          horizontal: Tokens.space3),
                      children: [
                        for (final entry in (fields!.entries.toList()
                              ..sort((a, b) => a.key.compareTo(b.key))))
                          _FieldCard(
                            fieldName: entry.key,
                            value: entry.value,
                            ref: ref,
                          ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
    );
  }
}

class _FieldCard extends StatelessWidget {
  final String fieldName;
  final dynamic value;
  final WidgetRef ref;

  const _FieldCard({
    required this.fieldName,
    required this.value,
    required this.ref,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: Tokens.space2),
      padding: const EdgeInsets.all(10),
      decoration: Tokens.gothicCardDecoration(),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Field label
          Text(
            fieldName,
            style: const TextStyle(
              fontFamily: Tokens.fontMono,
              fontSize: Tokens.sizeSm,
              color: Tokens.textSecondary,
            ),
          ),
          const SizedBox(height: 2),
          // Field value(s)
          _buildValue(),
          // +filter / -exclude buttons for array fields
          if (_isFilterable) ...[
            const SizedBox(height: 6),
            _buildFilterButtons(),
          ],
        ],
      ),
    );
  }

  bool get _isFilterable =>
      fieldName.startsWith('t_any_') && value is List && (value as List).isNotEmpty;

  Widget _buildValue() {
    if (value is List) {
      return Wrap(
        spacing: Tokens.space1,
        runSpacing: Tokens.space1,
        children: [
          for (final item in value as List)
            Text(
              '"${item.toString()}"',
              style: const TextStyle(
                fontFamily: Tokens.fontMono,
                fontSize: Tokens.sizeMd,
                color: Tokens.syntaxValue,
              ),
            ),
        ],
      );
    }
    if (value is Map) {
      return Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          for (final entry in (value as Map).entries)
            Padding(
              padding: const EdgeInsets.only(bottom: 2),
              child: Text.rich(
                TextSpan(children: [
                  TextSpan(
                    text: '${entry.key}: ',
                    style: const TextStyle(color: Tokens.textSecondary),
                  ),
                  TextSpan(
                    text: '${entry.value}',
                    style: TextStyle(
                      color: entry.value is num
                          ? Tokens.accentOrange
                          : entry.value == true
                              ? Tokens.accentGreen
                              : entry.value == false
                                  ? Tokens.accentRed
                                  : Tokens.textSecondary,
                    ),
                  ),
                ]),
                style: const TextStyle(
                  fontFamily: Tokens.fontMono,
                  fontSize: Tokens.sizeBase,
                ),
              ),
            ),
        ],
      );
    }
    if (value is num) {
      return Text(
        value.toString(),
        style: const TextStyle(
          fontFamily: Tokens.fontMono,
          fontSize: Tokens.sizeMd,
          color: Tokens.accentOrange,
        ),
      );
    }
    if (value is bool) {
      return Text(
        value.toString(),
        style: TextStyle(
          fontFamily: Tokens.fontMono,
          fontSize: Tokens.sizeMd,
          color: value == true ? Tokens.accentGreen : Tokens.accentRed,
        ),
      );
    }
    return Text(
      '"$value"',
      style: const TextStyle(
        fontFamily: Tokens.fontMono,
        fontSize: Tokens.sizeMd,
        color: Tokens.syntaxValue,
      ),
    );
  }

  Widget _buildFilterButtons() {
    return Wrap(
      spacing: Tokens.space1,
      children: [
        _FilterButton(
          label: '+ filter',
          bgColor: Tokens.surfaceFilterPositive,
          textColor: Tokens.accentGreen,
          onTap: () {
            final val = (value as List).last.toString();
            final controller = ref.read(queryTextControllerProvider);
            final clause = '| where $fieldName contains "$val"';
            final current = controller.text.trimRight();
            final newText = current.isEmpty ? clause : '$current\n$clause';
            controller.text = newText;
            controller.selection = TextSelection.collapsed(
              offset: newText.length,
            );
            ref.read(queryProvider.notifier).setText(newText);
          },
        ),
        _FilterButton(
          label: '- exclude',
          bgColor: Tokens.surfaceFilterNegative,
          textColor: Tokens.accentRed,
          onTap: () {
            final val = (value as List).last.toString();
            final controller = ref.read(queryTextControllerProvider);
            final clause = '| where $fieldName != "$val"';
            final current = controller.text.trimRight();
            final newText = current.isEmpty ? clause : '$current\n$clause';
            controller.text = newText;
            controller.selection = TextSelection.collapsed(
              offset: newText.length,
            );
            ref.read(queryProvider.notifier).setText(newText);
          },
        ),
      ],
    );
  }
}

class _FilterButton extends StatelessWidget {
  final String label;
  final Color bgColor;
  final Color textColor;
  final VoidCallback onTap;

  const _FilterButton({
    required this.label,
    required this.bgColor,
    required this.textColor,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return MouseRegion(
      cursor: SystemMouseCursors.click,
      child: GestureDetector(
        onTap: onTap,
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
          decoration: BoxDecoration(
            color: bgColor,
            borderRadius: BorderRadius.circular(Tokens.radiusSm),
          ),
          child: Text(
            label,
            style: TextStyle(
              fontFamily: Tokens.fontSans,
              fontSize: Tokens.sizeXs,
              color: textColor,
            ),
          ),
        ),
      ),
    );
  }
}
