import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../theme/tokens.dart';
import '../providers/query_provider.dart';

/// Example queries that rotate on idle to showcase syntax highlighting.
const _exampleQueries = [
  'locations\n| where t_any_cuisines contains "French"\n| where t_any_shows == "Rick Steves\' Europe"\n',
  'locations\n| where t_any_actors contains "Huell Howser"\n| where t_any_states contains "ca"\n',
  'locations\n| where t_any_dishes contains "gelato"\n| where t_any_continents == "Europe"\n',
  'locations\n| where t_any_categories contains "landmark"\n| where t_any_countries == "France"\n',
  'locations\n| where t_any_keywords contains "medieval"\n| where t_any_eras contains "roman"\n',
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

  // Blinking cursor state
  bool _cursorVisible = true;
  Timer? _cursorTimer;

  @override
  void initState() {
    super.initState();
    // Provider starts with initialExampleQuery, so controller matches.
    _controller = TextEditingController(text: ref.read(queryProvider));
    _startRotation();
    _startCursorBlink();
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

  void _startCursorBlink() {
    _cursorTimer = Timer.periodic(const Duration(milliseconds: 530), (_) {
      if (mounted) setState(() => _cursorVisible = !_cursorVisible);
    });
  }

  @override
  void dispose() {
    _rotationTimer?.cancel();
    _cursorTimer?.cancel();
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
                    _buildQueryLine(
                      i + 1,
                      lines[i],
                      isLast: i == lines.length - 1,
                    ),
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
        ],
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

  Widget _buildQueryLine(int lineNumber, String content, {bool isLast = false}) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 3),
      child: Row(
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
              ),
            ),
          ),
          const SizedBox(width: Tokens.space2),
          Expanded(
            child: isLast && content.trim().isEmpty
                ? _buildCursorLine()
                : _syntaxHighlight(content, showCursor: isLast),
          ),
        ],
      ),
    );
  }

  /// Empty last line with blinking green underscore cursor.
  Widget _buildCursorLine() {
    return Text.rich(
      TextSpan(children: [
        const TextSpan(
          text: '|',
          style: TextStyle(color: Tokens.textMuted),
        ),
        TextSpan(
          text: '_',
          style: TextStyle(
            color: _cursorVisible ? Tokens.syntaxCursor : Colors.transparent,
          ),
        ),
      ]),
      style: const TextStyle(
        fontFamily: Tokens.fontMono,
        fontSize: Tokens.sizeLg,
        height: 1.75,
      ),
    );
  }

  /// Syntax highlighting per component-patterns.md Section 2.
  Widget _syntaxHighlight(String line, {bool showCursor = false}) {
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
        r'''(\|)|(\bwhere\b|\band\b|\bor\b)|(t_\w[\w.]*)|(\bcontains\b|==|!=)|("[^"]*")|(\S+)''',
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
