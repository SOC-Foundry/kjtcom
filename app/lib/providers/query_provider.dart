import 'package:flutter_riverpod/flutter_riverpod.dart';

/// Holds the current query text in the editor.
class QueryNotifier extends Notifier<String> {
  bool _isAppending = false;

  @override
  String build() => '';

  void setText(String text) => state = text;

  void appendClause(String field, String op, String value) {
    if (_isAppending) return;
    _isAppending = true;
    try {
      final clause = '| where $field $op "$value"';
      // Dedup: if this exact clause already exists, no-op
      if (state.contains(clause)) return;
      state = '${state.trimRight()}\n$clause\n';
    } finally {
      Future.microtask(() => _isAppending = false);
    }
  }
}

final queryProvider = NotifierProvider<QueryNotifier, String>(QueryNotifier.new);
