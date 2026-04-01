import 'package:flutter_riverpod/flutter_riverpod.dart';

/// First example query - shared between provider and editor for sync.
const initialExampleQuery =
    'locations\n| where t_any_cuisines contains "French"\n| where t_any_shows == "Rick Steves\' Europe"\n';

/// Holds the current query text in the editor.
class QueryNotifier extends Notifier<String> {
  @override
  String build() => initialExampleQuery;

  void setText(String text) => state = text;

  void appendClause(String field, String op, String value) {
    final clause = '| where $field $op "$value"\n';
    state = '${state.trimRight()}\n$clause';
  }
}

final queryProvider = NotifierProvider<QueryNotifier, String>(QueryNotifier.new);
