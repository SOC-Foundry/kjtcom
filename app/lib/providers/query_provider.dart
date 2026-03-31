import 'package:flutter_riverpod/flutter_riverpod.dart';

/// Holds the current query text in the editor.
class QueryNotifier extends Notifier<String> {
  @override
  String build() => 'locations\n';

  void setText(String text) => state = text;

  void appendClause(String field, String op, String value) {
    final clause = '| where $field $op "$value"\n';
    state = '${state.trimRight()}\n$clause';
  }
}

final queryProvider = NotifierProvider<QueryNotifier, String>(QueryNotifier.new);
