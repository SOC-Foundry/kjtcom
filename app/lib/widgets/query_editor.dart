import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../theme/tokens.dart';
import '../providers/query_provider.dart';

/// Component-patterns.md Section 2 - Query Editor.
/// Dark input area with line-numbered, syntax-highlighted query text.
/// container: color.surface.elevated, border: color.border.default, radius.xl
class QueryEditor extends ConsumerStatefulWidget {
  const QueryEditor({super.key});

  @override
  ConsumerState<QueryEditor> createState() => _QueryEditorState();
}

class _QueryEditorState extends ConsumerState<QueryEditor> {
  late TextEditingController _controller;

  @override
  void initState() {
    super.initState();
    _controller = TextEditingController(text: ref.read(queryProvider));
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void _onSearch() {
    ref.read(queryProvider.notifier).setText(_controller.text);
  }

  @override
  Widget build(BuildContext context) {
    // Sync controller when query changes externally (+filter/-exclude)
    ref.listen(queryProvider, (_, next) {
      if (_controller.text != next) {
        _controller.text = next;
        _controller.selection = TextSelection.collapsed(offset: next.length);
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
          // Mode chips row
          _buildChipRow(),
          const SizedBox(height: Tokens.space2),
          // Query lines + Search button
          Stack(
            children: [
              // Syntax-highlighted display overlay
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  for (int i = 0; i < lines.length; i++)
                    _buildQueryLine(i + 1, lines[i]),
                ],
              ),
              // Invisible text field on top for editing
              Positioned.fill(
                child: TextField(
                  controller: _controller,
                  onChanged: (_) => setState(() {}),
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
              // Search button - positioned right
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

  Widget _buildQueryLine(int lineNumber, String content) {
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
          Expanded(child: _syntaxHighlight(content)),
        ],
      ),
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
      // Tokenize: pipe, keyword, field, operator, quoted value
      final regex = RegExp(
        r'''(\|)|(\bwhere\b|\band\b|\bor\b)|(t_\w[\w.]*)|(\bcontains\b|==|!=)|("[^"]*")|(\S+)''',
        caseSensitive: false,
      );
      for (final match in regex.allMatches(trimmed)) {
        final text = match.group(0)!;
        Color color;
        if (match.group(1) != null) {
          color = Tokens.syntaxOperator; // pipe
        } else if (match.group(2) != null) {
          color = Tokens.syntaxKeyword; // where, and, or
        } else if (match.group(3) != null) {
          color = Tokens.syntaxField; // t_any_* field
        } else if (match.group(4) != null) {
          color = Tokens.syntaxOperator; // contains, ==, !=
        } else if (match.group(5) != null) {
          color = Tokens.syntaxValue; // "quoted string"
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
