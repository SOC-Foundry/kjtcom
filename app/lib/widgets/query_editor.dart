import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/query_clause.dart';
import '../theme/tokens.dart';
import '../providers/query_provider.dart';
import '../providers/selection_provider.dart';
import 'query_autocomplete.dart';

/// Component-patterns.md Section 2 - Query Editor.
/// Dark input area with line-numbered, syntax-highlighted query text.
class QueryEditor extends ConsumerStatefulWidget {
  const QueryEditor({super.key});

  @override
  ConsumerState<QueryEditor> createState() => _QueryEditorState();
}

class _QueryEditorState extends ConsumerState<QueryEditor> {
  late TextEditingController _controller;
  int _selectedIndex = 0;
  List<String> _suggestions = [];
  AutocompleteContext? _acContext;
  bool _showAutocomplete = true;

  @override
  void initState() {
    super.initState();
    _controller = ref.read(queryTextControllerProvider);
    _controller.addListener(_onTextChanged);
  }

  @override
  void dispose() {
    _controller.removeListener(_onTextChanged);
    super.dispose();
  }

  void _onTextChanged() {
    final text = _controller.text;
    final cursorPos = _controller.selection.baseOffset;
    final ctx = AutocompleteContext.detect(text, cursorPos);
    
    List<String> suggestions = [];
    if (ctx != null && _showAutocomplete) {
      if (ctx.mode == AutocompleteMode.field) {
        suggestions = QueryClause.knownFields
            .where((f) => f.startsWith(ctx.prefix) && f != ctx.prefix)
            .toList()
          ..sort();
        if (suggestions.length > 5) suggestions = suggestions.take(5).toList();
      } else if (ctx.mode == AutocompleteMode.value && ctx.fieldName != null) {
        final valueIndex = ref.read(valueIndexProvider).valueOrNull ?? {};
        final values = valueIndex[ctx.fieldName] ?? [];
        suggestions = values
            .where((v) =>
                v.startsWith(ctx.prefix) &&
                (ctx.prefix.isEmpty || v != ctx.prefix))
            .take(5)
            .toList();
      }
    }

    if (suggestions.length != _suggestions.length || 
        (suggestions.isNotEmpty && suggestions[0] != (_suggestions.isNotEmpty ? _suggestions[0] : ''))) {
      setState(() {
        _acContext = ctx;
        _suggestions = suggestions;
        _selectedIndex = 0;
      });
    } else {
      // Still update context even if suggestions are same (cursor moved)
      _acContext = ctx;
    }
  }

  void _acceptSuggestion(int index) {
    if (_acContext == null || index >= _suggestions.length) return;
    final suggestion = _suggestions[index];
    final text = _controller.text;
    final ctx = _acContext!;

    String newText;
    int newCursorPos;

    if (ctx.mode == AutocompleteMode.field) {
      final suffix = ' contains ';
      newText = text.substring(0, ctx.replaceStart) +
          suggestion +
          suffix +
          text.substring(ctx.replaceEnd);
      newCursorPos = ctx.replaceStart + suggestion.length + suffix.length;
    } else {
      newText = text.substring(0, ctx.replaceStart) +
          suggestion +
          text.substring(ctx.replaceEnd);
      newCursorPos = ctx.replaceStart + suggestion.length;
    }

    // Use addPostFrameCallback for cursor placement (W1)
    _controller.text = newText;
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _controller.selection = TextSelection.collapsed(offset: newCursorPos);
    });
    
    ref.read(queryProvider.notifier).setText(newText);
    setState(() {
      _suggestions = [];
      _showAutocomplete = false;
    });
  }

  void _onSearch() {
    setState(() {
      _suggestions = [];
      _showAutocomplete = false;
    });
    ref.read(queryProvider.notifier).setText(_controller.text);
  }

  void _onUserEdit(String text) {
    _showAutocomplete = true;
    // _onTextChanged is already called by the listener
  }

  KeyEventResult _handleKeyEvent(FocusNode node, KeyEvent event) {
    if (event is! KeyDownEvent && event is! KeyRepeatEvent) return KeyEventResult.ignored;
    
    if (_suggestions.isNotEmpty) {
      if (event.logicalKey == LogicalKeyboardKey.tab || event.logicalKey == LogicalKeyboardKey.enter) {
        _acceptSuggestion(_selectedIndex);
        return KeyEventResult.handled;
      }
      if (event.logicalKey == LogicalKeyboardKey.arrowDown) {
        setState(() {
          _selectedIndex = (_selectedIndex + 1) % _suggestions.length;
        });
        return KeyEventResult.handled;
      }
      if (event.logicalKey == LogicalKeyboardKey.arrowUp) {
        setState(() {
          _selectedIndex = (_selectedIndex - 1 + _suggestions.length) % _suggestions.length;
        });
        return KeyEventResult.handled;
      }
      if (event.logicalKey == LogicalKeyboardKey.escape) {
        setState(() {
          _suggestions = [];
          _showAutocomplete = false;
        });
        return KeyEventResult.handled;
      }
    }
    return KeyEventResult.ignored;
  }

  @override
  Widget build(BuildContext context) {
    // Re-trigger suggestions when value index finishes loading (W3 fix)
    ref.listen(valueIndexProvider, (prev, next) {
      if (prev?.valueOrNull == null && next.valueOrNull != null) {
        _onTextChanged();
      }
    });

    // Sync controller when query changes externally (+filter/-exclude)
    ref.listen(queryProvider, (_, next) {
      if (ref.read(programmaticUpdateProvider)) return;
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
          Focus(
            onKeyEvent: _handleKeyEvent,
            child: Stack(
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
          ),
          if (_suggestions.isNotEmpty) _buildInlineSuggestions(),
          _buildFeedback(),
          _buildHelpText(),
        ],
      ),
    );
  }

  Widget _buildInlineSuggestions() {
    return Container(
      margin: const EdgeInsets.only(
        top: Tokens.space2,
        left: Tokens.lineNumberWidth + Tokens.space2,
      ),
      padding: const EdgeInsets.symmetric(vertical: 4),
      decoration: BoxDecoration(
        color: const Color(0xFF1C2128),
        border: Border.all(color: Tokens.accentGreen.withValues(alpha: 0.5), width: 1),
        borderRadius: BorderRadius.circular(Tokens.radiusMd),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          for (int i = 0; i < _suggestions.length; i++)
            _buildSuggestionRow(i),
          Padding(
            padding: const EdgeInsets.fromLTRB(8, 4, 8, 2),
            child: Row(
              children: [
                Text(
                  'Tab to insert',
                  style: TextStyle(
                    fontFamily: Tokens.fontSans,
                    fontSize: 10,
                    color: Tokens.textMuted,
                  ),
                ),
                const Spacer(),
                if (_acContext?.mode == AutocompleteMode.field)
                  const Text(
                    'field',
                    style: TextStyle(
                      fontFamily: Tokens.fontMono,
                      fontSize: 10,
                      color: Tokens.syntaxField,
                    ),
                  )
                else
                  const Text(
                    'value',
                    style: TextStyle(
                      fontFamily: Tokens.fontMono,
                      fontSize: 10,
                      color: Tokens.syntaxValue,
                    ),
                  ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSuggestionRow(int index) {
    final isSelected = index == _selectedIndex;
    return MouseRegion(
      cursor: SystemMouseCursors.click,
      child: GestureDetector(
        onTap: () => _acceptSuggestion(index),
        child: Container(
          width: double.infinity,
          padding: const EdgeInsets.symmetric(
            horizontal: Tokens.space3,
            vertical: 4,
          ),
          color: isSelected ? const Color(0xFF2D333B) : Colors.transparent,
          child: Text(
            _suggestions[index],
            style: TextStyle(
              fontFamily: Tokens.fontMono,
              fontSize: Tokens.sizeMd,
              color: isSelected ? Tokens.accentGreen : Tokens.textPrimary,
            ),
          ),
        ),
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
        'the first array match',
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

  Widget _buildHelpText() {
    if (_controller.text.trim().isNotEmpty) return const SizedBox.shrink();
    return Padding(
      padding: const EdgeInsets.only(top: Tokens.space2),
      child: Text(
        'Examples: t_any_cuisines contains "french"  |  '
        't_any_countries contains "italy"  |  '
        't_any_country_codes contains-any ["fr", "it"]',
        style: TextStyle(
          fontFamily: Tokens.fontMono,
          fontSize: Tokens.sizeSm,
          color: Tokens.textSecondary,
        ),
      ),
    );
  }

  void _onClear() {
    _controller.clear();
    ref.read(queryProvider.notifier).setText('');
    ref.read(selectedEntityProvider.notifier).state = null;
    setState(() {});
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
        if (_controller.text.isNotEmpty)
          Padding(
            padding: const EdgeInsets.only(right: Tokens.space2),
            child: MouseRegion(
              cursor: SystemMouseCursors.click,
              child: GestureDetector(
                onTap: _onClear,
                child: Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: Tokens.space2,
                    vertical: 2,
                  ),
                  decoration: BoxDecoration(
                    color: Tokens.surfaceOverlay,
                    borderRadius: BorderRadius.circular(Tokens.radiusMd),
                    border: Border.all(color: Tokens.accentRed.withValues(alpha: 0.5)),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(Icons.close, size: 12, color: Tokens.accentRed),
                      const SizedBox(width: 4),
                      Text(
                        'Clear',
                        style: TextStyle(
                          fontFamily: Tokens.fontSans,
                          fontSize: Tokens.sizeSm,
                          color: Tokens.accentRed,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ),
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
