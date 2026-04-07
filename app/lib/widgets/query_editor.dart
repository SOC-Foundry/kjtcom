import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_code_editor/flutter_code_editor.dart' hide Tokens;
import '../models/query_clause.dart';
import '../theme/tokens.dart';
import '../theme/tql_language.dart';
import '../providers/query_provider.dart';
import '../providers/selection_provider.dart';
import 'query_autocomplete.dart';

/// Component-patterns.md Section 2 - Query Editor.
/// Dark input area with line-numbered, syntax-highlighted query text.
/// Migrated to flutter_code_editor (v10.64, G45) to resolve cursor drift.
class QueryEditor extends ConsumerStatefulWidget {
  const QueryEditor({super.key});

  @override
  ConsumerState<QueryEditor> createState() => _QueryEditorState();
}

class _QueryEditorState extends ConsumerState<QueryEditor> {
  late CodeController _codeController;
  int _selectedIndex = 0;
  List<String> _suggestions = [];
  AutocompleteContext? _acContext;
  bool _showAutocomplete = true;

  @override
  void initState() {
    super.initState();
    final initialText = ref.read(queryProvider);
    _codeController = CodeController(
      text: initialText,
      language: tql,
    );
    _codeController.addListener(_onTextChanged);
  }

  @override
  void dispose() {
    _codeController.removeListener(_onTextChanged);
    _codeController.dispose();
    super.dispose();
  }

  void _onTextChanged() {
    final text = _codeController.text;
    final cursorPos = _codeController.selection.baseOffset;
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
        final valueIndex = ref.read(valueIndexProvider).value ?? {};
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
      _acContext = ctx;
    }
  }

  void _acceptSuggestion(int index) {
    if (_acContext == null || index >= _suggestions.length) return;
    final suggestion = _suggestions[index];
    final text = _codeController.text;
    final ctx = _acContext!;

    String insertion;
    if (ctx.mode == AutocompleteMode.field) {
      insertion = suggestion + ' contains ';
    } else {
      insertion = suggestion;
    }

    // Replace the prefix with the suggestion
    final newText = text.replaceRange(ctx.replaceStart, ctx.replaceEnd, insertion);
    _codeController.text = newText;
    
    final newCursorPos = ctx.replaceStart + insertion.length;
    _codeController.selection = TextSelection.collapsed(offset: newCursorPos);
    
    ref.read(queryProvider.notifier).setText(_codeController.text);
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
    ref.read(queryProvider.notifier).setText(_codeController.text);
  }

  KeyEventResult _handleKeyEvent(FocusNode node, KeyEvent event) {
    if (event is! KeyDownEvent && event is! KeyRepeatEvent) return KeyEventResult.ignored;
    
    // Handle Enter key for search if no suggestions
    if (_suggestions.isEmpty && event.logicalKey == LogicalKeyboardKey.enter) {
      _onSearch();
      return KeyEventResult.handled;
    }

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
    // Sync controller when query changes externally
    ref.listen(queryProvider, (_, next) {
      if (ref.read(programmaticUpdateProvider)) return;
      if (_codeController.text != next) {
        _codeController.text = next;
        _codeController.selection = TextSelection.collapsed(offset: next.length);
        setState(() {});
      }
    });

    final tqlTheme = {
      'root': const TextStyle(color: Tokens.textPrimary, backgroundColor: Colors.transparent),
      'keyword': const TextStyle(color: Tokens.syntaxKeyword),
      'operator': const TextStyle(color: Tokens.syntaxOperator),
      'type': const TextStyle(color: Tokens.syntaxField),
      'string': const TextStyle(color: Tokens.syntaxValue),
      'number': const TextStyle(color: Tokens.syntaxValue),
    };

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
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Expanded(
                  child: CodeTheme(
                    data: CodeThemeData(styles: tqlTheme),
                    child: CodeField(
                      controller: _codeController,
                      textStyle: const TextStyle(
                        fontFamily: Tokens.fontMono,
                        fontSize: Tokens.sizeLg,
                        height: 1.75,
                      ),
                      gutterStyle: const GutterStyle(
                        showLineNumbers: true,
                        width: Tokens.lineNumberWidth,
                        textStyle: TextStyle(
                          fontFamily: Tokens.fontMono,
                          fontSize: Tokens.sizeMd,
                          color: Tokens.textMuted,
                        ),
                        margin: Tokens.space2,
                      ),
                      decoration: const BoxDecoration(
                        color: Colors.transparent,
                      ),
                      onChanged: (text) => _showAutocomplete = true,
                    ),
                  ),
                ),
                const SizedBox(width: Tokens.space2),
                MouseRegion(
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
    final text = _codeController.text;
    final clauses = QueryClause.parseAll(text);
    final hasContent = text.split('\n').any(
        (l) => l.trim().isNotEmpty && l.trim() != 'locations');

    if (hasContent && clauses.isEmpty) {
      return _feedbackRow(
        'Could not parse query. Expected: field_name operator value '
        '(e.g., t_any_keywords contains "barbecue")',
        Tokens.accentRed,
      );
    }

    final invalidFields = clauses.where((c) => !c.isValidField).toList();
    if (invalidFields.isNotEmpty) {
      final names = invalidFields.map((c) => c.field).join(', ');
      return _feedbackRow(
        'Unknown field: $names',
        Tokens.accentOrange,
      );
    }

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
    if (_codeController.text.trim().isNotEmpty) return const SizedBox.shrink();
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
    _codeController.clear();
    ref.read(queryProvider.notifier).setText('');
    ref.read(selectedEntityProvider.notifier).select(null);
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
        if (_codeController.text.isNotEmpty)
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
}
