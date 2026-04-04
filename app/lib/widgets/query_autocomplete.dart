import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/query_clause.dart';
import '../theme/tokens.dart';

/// Provider that loads and caches the value_index.json asset.
final valueIndexProvider = FutureProvider<Map<String, List<String>>>((ref) async {
  final jsonStr = await rootBundle.loadString('assets/value_index.json');
  final Map<String, dynamic> raw = json.decode(jsonStr);
  return raw.map((k, v) => MapEntry(k, List<String>.from(v)));
});

/// Sorted list of known field names for field-mode autocomplete.
final _sortedFields = QueryClause.knownFields.toList()..sort();

/// Determines autocomplete mode and context from cursor position.
class AutocompleteContext {
  final AutocompleteMode mode;
  final String prefix;
  final String? fieldName;
  final int replaceStart;
  final int replaceEnd;

  const AutocompleteContext({
    required this.mode,
    required this.prefix,
    this.fieldName,
    required this.replaceStart,
    required this.replaceEnd,
  });

  static AutocompleteContext? detect(String text, int cursorPos) {
    if (cursorPos <= 0 || cursorPos > text.length) return null;

    // Check value mode: cursor inside quotes after a field + operator
    final beforeCursor = text.substring(0, cursorPos);
    final valueMatch = RegExp(
      r'(\w[\w.]*)\s+(?:contains|==|!=)\s+"([^"]*?)$',
    ).firstMatch(beforeCursor);
    if (valueMatch != null) {
      final field = valueMatch.group(1)!;
      final partial = valueMatch.group(2)!;
      return AutocompleteContext(
        mode: AutocompleteMode.value,
        prefix: partial.toLowerCase(),
        fieldName: field,
        replaceStart: cursorPos - partial.length,
        replaceEnd: cursorPos,
      );
    }

    // Check field mode: current word starts with t_ on a new clause line
    final wordMatch = RegExp(r'(t_\w*)$').firstMatch(beforeCursor);
    if (wordMatch != null) {
      final partial = wordMatch.group(1)!;
      return AutocompleteContext(
        mode: AutocompleteMode.field,
        prefix: partial.toLowerCase(),
        replaceStart: cursorPos - partial.length,
        replaceEnd: cursorPos,
      );
    }

    return null;
  }
}

enum AutocompleteMode { field, value }

/// Autocomplete overlay widget positioned below the query editor.
class QueryAutocompleteOverlay extends ConsumerStatefulWidget {
  final TextEditingController controller;
  final LayerLink layerLink;
  final VoidCallback onDismiss;
  final VoidCallback onAccept;

  const QueryAutocompleteOverlay({
    super.key,
    required this.controller,
    required this.layerLink,
    required this.onDismiss,
    required this.onAccept,
  });

  @override
  ConsumerState<QueryAutocompleteOverlay> createState() =>
      QueryAutocompleteOverlayState();
}

class QueryAutocompleteOverlayState
    extends ConsumerState<QueryAutocompleteOverlay> {
  int _selectedIndex = 0;
  List<String> _suggestions = [];
  AutocompleteContext? _context;

  @override
  void initState() {
    super.initState();
    widget.controller.addListener(_onTextChanged);
    _onTextChanged();
  }

  @override
  void dispose() {
    widget.controller.removeListener(_onTextChanged);
    super.dispose();
  }

  void _onTextChanged() {
    final text = widget.controller.text;
    final cursorPos = widget.controller.selection.baseOffset;
    final ctx = AutocompleteContext.detect(text, cursorPos);

    List<String> suggestions = [];
    if (ctx != null) {
      if (ctx.mode == AutocompleteMode.field) {
        suggestions = _sortedFields
            .where((f) => f.startsWith(ctx.prefix) && f != ctx.prefix)
            .take(8)
            .toList();
      } else if (ctx.mode == AutocompleteMode.value && ctx.fieldName != null) {
        final valueIndex = ref.read(valueIndexProvider).valueOrNull ?? {};
        final values = valueIndex[ctx.fieldName] ?? [];
        suggestions = values
            .where((v) =>
                v.startsWith(ctx.prefix) &&
                (ctx.prefix.isEmpty || v != ctx.prefix))
            .take(8)
            .toList();
      }
    }

    debugPrint('[W3] overlay suggestions: mode=${ctx?.mode}, count=${suggestions.length}, prefix=${ctx?.prefix}');
    setState(() {
      _context = ctx;
      _suggestions = suggestions;
      _selectedIndex = 0;
    });
  }

  void acceptSuggestion(int index) {
    if (_context == null || index >= _suggestions.length) return;
    final suggestion = _suggestions[index];
    final text = widget.controller.text;
    final ctx = _context!;

    String newText;
    int newCursorPos;

    if (ctx.mode == AutocompleteMode.field) {
      // Replace partial field name with full field + operator + open quote
      final suffix = ' contains "';
      newText = text.substring(0, ctx.replaceStart) +
          suggestion +
          suffix +
          text.substring(ctx.replaceEnd);
      newCursorPos = ctx.replaceStart + suggestion.length + suffix.length;
    } else {
      // Replace partial value with full value
      newText = text.substring(0, ctx.replaceStart) +
          suggestion +
          text.substring(ctx.replaceEnd);
      newCursorPos = ctx.replaceStart + suggestion.length;
    }

    widget.controller.text = newText;
    widget.controller.selection =
        TextSelection.collapsed(offset: newCursorPos);
    widget.onAccept();
  }

  bool handleKey(KeyEvent event) {
    if (event is! KeyDownEvent && event is! KeyRepeatEvent) return false;
    if (_suggestions.isEmpty) return false;

    if (event.logicalKey == LogicalKeyboardKey.tab) {
      acceptSuggestion(_selectedIndex);
      return true;
    }
    if (event.logicalKey == LogicalKeyboardKey.arrowDown) {
      setState(() {
        _selectedIndex = (_selectedIndex + 1) % _suggestions.length;
      });
      return true;
    }
    if (event.logicalKey == LogicalKeyboardKey.arrowUp) {
      setState(() {
        _selectedIndex =
            (_selectedIndex - 1 + _suggestions.length) % _suggestions.length;
      });
      return true;
    }
    if (event.logicalKey == LogicalKeyboardKey.escape) {
      widget.onDismiss();
      return true;
    }
    return false;
  }

  @override
  Widget build(BuildContext context) {
    // Re-trigger suggestions when value index finishes loading (W3 fix)
    ref.listen(valueIndexProvider, (prev, next) {
      if (prev?.valueOrNull == null && next.valueOrNull != null) {
        debugPrint('[W3] Value index loaded, re-triggering suggestions');
        _onTextChanged();
      }
    });

    if (_suggestions.isEmpty) return const SizedBox.shrink();

    return CompositedTransformFollower(
      link: widget.layerLink,
      showWhenUnlinked: false,
      offset: const Offset(0, 40),
      child: Material(
        color: Colors.transparent,
        child: Container(
          constraints: const BoxConstraints(maxWidth: 400, maxHeight: 280),
          decoration: BoxDecoration(
            color: const Color(0xFF1C2128),
            border: Border.all(color: Tokens.accentGreen, width: 1),
            borderRadius: BorderRadius.circular(Tokens.radiusMd),
            boxShadow: const [
              BoxShadow(
                color: Color(0x40000000),
                blurRadius: 8,
                offset: Offset(0, 4),
              ),
            ],
          ),
          child: ListView.builder(
            shrinkWrap: true,
            padding: const EdgeInsets.symmetric(vertical: 4),
            itemCount: _suggestions.length,
            itemBuilder: (context, index) {
              final isSelected = index == _selectedIndex;
              return MouseRegion(
                cursor: SystemMouseCursors.click,
                child: GestureDetector(
                  onTap: () => acceptSuggestion(index),
                  child: Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: Tokens.space3,
                      vertical: Tokens.space2,
                    ),
                    color: isSelected
                        ? const Color(0xFF2D333B)
                        : Colors.transparent,
                    child: Text(
                      _suggestions[index],
                      style: TextStyle(
                        fontFamily: Tokens.fontMono,
                        fontSize: Tokens.sizeMd,
                        color: isSelected
                            ? Tokens.accentGreen
                            : Tokens.textPrimary,
                      ),
                    ),
                  ),
                ),
              );
            },
          ),
        ),
      ),
    );
  }
}
