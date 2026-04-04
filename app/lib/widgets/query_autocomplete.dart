import 'dart:convert';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/// Provider that loads and caches the value_index.json asset.
final valueIndexProvider = FutureProvider<Map<String, List<String>>>((ref) async {
  final jsonStr = await rootBundle.loadString('assets/value_index.json');
  final Map<String, dynamic> raw = json.decode(jsonStr);
  return raw.map((k, v) => MapEntry(k, List<String>.from(v)));
});

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
    if (cursorPos < 0 || cursorPos > text.length) return null;

    // Check value mode: cursor after field + operator, with or without quotes
    final beforeCursor = text.substring(0, cursorPos);
    // Quoted value: field op "partial
    final quotedMatch = RegExp(
      r'(\w[\w.]*)\s+(?:contains|==|!=)\s+"([^"]*?)$',
    ).firstMatch(beforeCursor);
    if (quotedMatch != null) {
      final field = quotedMatch.group(1)!;
      final partial = quotedMatch.group(2)!;
      return AutocompleteContext(
        mode: AutocompleteMode.value,
        prefix: partial.toLowerCase(),
        fieldName: field,
        replaceStart: cursorPos - partial.length,
        replaceEnd: cursorPos,
      );
    }
    // Unquoted value: field op partial (no quote)
    final unquotedMatch = RegExp(
      r'(\w[\w.]*)\s+(?:contains|==|!=)\s+([^"\s].*?)$',
    ).firstMatch(beforeCursor);
    if (unquotedMatch != null) {
      final field = unquotedMatch.group(1)!;
      final partial = unquotedMatch.group(2)!;
      return AutocompleteContext(
        mode: AutocompleteMode.value,
        prefix: partial.toLowerCase(),
        fieldName: field,
        replaceStart: cursorPos - partial.length,
        replaceEnd: cursorPos,
      );
    }
    // Empty value after operator + space (user just clicked schema field)
    final emptyMatch = RegExp(
      r'(\w[\w.]*)\s+(?:contains|==|!=)\s+$',
    ).firstMatch(beforeCursor);
    if (emptyMatch != null) {
      final field = emptyMatch.group(1)!;
      return AutocompleteContext(
        mode: AutocompleteMode.value,
        prefix: '',
        fieldName: field,
        replaceStart: cursorPos,
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
