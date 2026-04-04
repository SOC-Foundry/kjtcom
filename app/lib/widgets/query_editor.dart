import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/query_clause.dart';
import '../theme/tokens.dart';
import '../providers/query_provider.dart';

/// Example queries that rotate on idle to showcase syntax highlighting.
const _exampleQueries = [
  'locations\n| where t_any_cuisines contains "french"\n',
  'locations\n| where t_any_actors contains "huell howser"\n',
  'locations\n| where t_any_countries contains "italy"\n',
  'locations\n| where t_any_dishes contains "gelato"\n',
  'locations\n| where t_any_keywords contains "medieval"\n',
];

/// Component-patterns.md Section 2 - Query Editor.
/// Dark input area with line-numbered, syntax-highlighted query text.
/// Features: blinking cursor, rotating example queries on idle.
class QueryEditor extends ConsumerStatefulWidget {
  const QueryEditor({super.key});

  @override
  ConsumerState<QueryEditor> createState() => _QueryEditorState();
}

class _QueryEditorState extends ConsumerState<QueryEditor> {
  late TextEditingController _controller;
  bool _userHasEdited = false;
  int _exampleIndex = 0;
  Timer? _rotationTimer;

  @override
  void initState() {
    super.initState();
    // Provider starts with initialExampleQuery, so controller matches.
    _controller = TextEditingController(text: ref.read(queryProvider));
    _startRotation();
  }

  void _startRotation() {
    _rotationTimer = Timer.periodic(const Duration(seconds: 6), (_) {
      if (_userHasEdited) return;
      setState(() {
        _exampleIndex = (_exampleIndex + 1) % _exampleQueries.length;
        final query = _exampleQueries[_exampleIndex];
        _controller.text = query;
        ref.read(queryProvider.notifier).setText(query);
      });
    });
  }

  @override
  void dispose() {
    _rotationTimer?.cancel();
    _controller.dispose();
    super.dispose();
  }

  void _onSearch() {
    ref.read(queryProvider.notifier).setText(_controller.text);
  }

  void _onUserEdit(String text) {
    if (!_userHasEdited) {
      _userHasEdited = true;
      _rotationTimer?.cancel();
    }
    setState(() {});
  }

  @override
  Widget build(BuildContext context) {
    // Sync controller when query changes externally (+filter/-exclude, rotation)
    ref.listen(queryProvider, (_, next) {
      if (_controller.text != next) {
        _controller.text = next;
        _controller.selection = TextSelection.collapsed(offset: next.length);
        setState(() {});
      }
    });

    final lines = _controller.text.split('\n');

    return Container(
      decoration: BoxDecoration(
        color: Tokens.surfaceElevated,
        border: Border.all(color: Tokens.borderDefault),
        borderRadius: BorderRadius.circular(Tokens.radiusXl),
      ),
      padding: const EdgeInsets.fromLTRB(
        Tokens.space4,
        Tokens.space3,
        Tokens.space4,
        Tokens.space3,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisSize: MainAxisSize.min,
        children: [
          _buildChipRow(),
          const SizedBox(height: Tokens.space2),
          Stack(
            children: [
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  for (int i = 0; i < lines.length; i++)
                    _buildQueryLine(i + 1, lines[i]),
                ],
              ),
              Positioned.fill(
                child: TextField(
                  controller: _controller,
                  onChanged: _onUserEdit,
                  onSubmitted: (_) => _onSearch(),
                  maxLines: null,
                  style: const TextStyle(
                    fontFamily: Tokens.fontMono,
                    fontSize: Tokens.sizeLg,
                    color: Colors.transparent,
                    height: 1.75,
                  ),
                  decoration: const InputDecoration(
                    border: InputBorder.none,
                    contentPadding: EdgeInsets.only(
                      left: Tokens.lineNumberWidth + Tokens.space2,
                    ),
                    isDense: true,
                  ),
                  cursorColor: Tokens.syntaxCursor,
                ),
              ),
              Positioned(
                right: 0,
                top: 0,
                bottom: 0,
                child: Center(
                  child: MouseRegion(
                    cursor: SystemMouseCursors.click,
                    child: GestureDetector(
                      onTap: _onSearch,
                      child: Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: Tokens.space4,
                          vertical: Tokens.space2 - 2,
                        ),
                        decoration: BoxDecoration(
                          color: Tokens.surfaceCta,
                          borderRadius: BorderRadius.circular(Tokens.radiusLg),
                        ),
                        child: const Text(
                          'Search',
                          style: TextStyle(
                            fontFamily: Tokens.fontSans,
                            fontSize: Tokens.sizeMd,
                            fontWeight: FontWeight.w500,
                            color: Tokens.textOnCta,
                          ),
                        ),
                      ),
                    ),
                  ),
                ),
              ),
            ],
          ),
          _buildFeedback(),
        ],
      ),
    );
  }

  Widget _buildFeedback() {
    final text = _controller.text;
    final clauses = QueryClause.parseAll(text);
    final hasContent = text.split('\n').any(
        (l) => l.trim().isNotEmpty && l.trim() != 'locations');

    // Parse error: non-empty input but no clauses parsed
    if (hasContent && clauses.isEmpty) {
      return _feedbackRow(
        'Could not parse query. Expected: field_name operator value '
        '(e.g., t_any_keywords contains "barbecue")',
        Tokens.accentRed,
      );
    }

    // Invalid field name
    final invalidFields = clauses.where((c) => !c.isValidField).toList();
    if (invalidFields.isNotEmpty) {
      final names = invalidFields.map((c) => c.field).join(', ');
      return _feedbackRow(
        'Unknown field: $names',
        Tokens.accentOrange,
      );
    }

    // Multi-array-contains note (D5)
    final arrayOps = clauses.where(
        (c) => c.operator == 'contains' || c.operator == 'contains-any');
    if (arrayOps.length > 1) {
      return _feedbackRow(
        'Note: Multiple array queries are filtered client-side from '
        'the first 1,000 results',
        Tokens.textSecondary,
      );
    }

    return const SizedBox.shrink();
  }

  Widget _feedbackRow(String message, Color color) {
    return Padding(
      padding: const EdgeInsets.only(top: Tokens.space2),
      child: Text(
        message,
        style: TextStyle(
          fontFamily: Tokens.fontMono,
          fontSize: Tokens.sizeSm,
          color: color,
        ),
      ),
    );
  }

  Widget _buildChipRow() {
    return Row(
      children: [
        _chip('NoSQL', active: true),
        const SizedBox(width: Tokens.space2),
        _chip('Logs'),
        const Spacer(),
        _chip('locations'),
        const SizedBox(width: Tokens.space2),
        _chip('All time'),
      ],
    );
  }

  Widget _chip(String label, {bool active = false}) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: Tokens.space2, vertical: 2),
      decoration: BoxDecoration(
        color: Tokens.surfaceOverlay,
        borderRadius: BorderRadius.circular(Tokens.radiusMd),
      ),
      child: Text(
        label,
        style: TextStyle(
          fontFamily: Tokens.fontSans,
          fontSize: Tokens.sizeSm,
          color: active ? Tokens.accentBlue : Tokens.textSecondary,
        ),
      ),
    );
  }

  Widget _buildQueryLine(int lineNumber, String content) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.baseline,
      textBaseline: TextBaseline.alphabetic,
      children: [
        SizedBox(
          width: Tokens.lineNumberWidth,
          child: Text(
            '$lineNumber',
            textAlign: TextAlign.right,
            style: const TextStyle(
              fontFamily: Tokens.fontMono,
              fontSize: Tokens.sizeMd,
              color: Tokens.textMuted,
              height: 1.75,
            ),
          ),
        ),
        const SizedBox(width: Tokens.space2),
        Expanded(
          child: _syntaxHighlight(content),
        ),
      ],
    );
  }

  /// Syntax highlighting per component-patterns.md Section 2.
  Widget _syntaxHighlight(String line) {
    final spans = <TextSpan>[];
    final trimmed = line.trim();

    if (trimmed == 'locations') {
      spans.add(const TextSpan(
        text: 'locations',
        style: TextStyle(color: Tokens.accentGreen),
      ));
    } else if (trimmed.isEmpty) {
      spans.add(const TextSpan(text: ' '));
    } else {
      final regex = RegExp(
        r'''(\|)|(\bwhere\b|\band\b|\bor\b)|(t_\w[\w.]*)|(\bcontains-any\b|\bcontains\b|==|!=)|("[^"]*")|(\[.*?\])|(\S+)''',
        caseSensitive: false,
      );
      for (final match in regex.allMatches(trimmed)) {
        final text = match.group(0)!;
        Color color;
        if (match.group(1) != null) {
          color = Tokens.syntaxOperator;
        } else if (match.group(2) != null) {
          color = Tokens.syntaxKeyword;
        } else if (match.group(3) != null) {
          color = Tokens.syntaxField;
        } else if (match.group(4) != null) {
          color = Tokens.syntaxOperator;
        } else if (match.group(5) != null) {
          color = Tokens.syntaxValue;
        } else if (match.group(6) != null) {
          color = Tokens.syntaxValue;
        } else {
          color = Tokens.textPrimary;
        }
        spans.add(TextSpan(text: '$text ', style: TextStyle(color: color)));
      }
    }

    return Text.rich(
      TextSpan(children: spans),
      style: const TextStyle(
        fontFamily: Tokens.fontMono,
        fontSize: Tokens.sizeLg,
        height: 1.75,
      ),
    );
  }
}
