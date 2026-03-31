/// A parsed clause from the query editor.
/// Example: `| where t_any_cuisines contains "French"`
/// -> field: t_any_cuisines, operator: contains, value: French
class QueryClause {
  final String field;
  final String operator;
  final String value;

  const QueryClause({
    required this.field,
    required this.operator,
    required this.value,
  });

  @override
  String toString() => '| where $field $operator "$value"';

  /// Parse a single query line into a clause.
  /// Supports: `| where field op "value"` and `field op "value"`
  static QueryClause? parse(String line) {
    final trimmed = line.trim();
    if (trimmed.isEmpty || trimmed == 'locations') return null;

    // Match: [| where] field operator "value"
    final regex = RegExp(
      r'''(?:\|\s*where\s+)?(\w[\w.]*)\s+(contains|==|!=)\s+"([^"]*)"''',
      caseSensitive: false,
    );
    final match = regex.firstMatch(trimmed);
    if (match == null) return null;

    return QueryClause(
      field: match.group(1)!,
      operator: match.group(2)!,
      value: match.group(3)!,
    );
  }

  /// Parse multi-line query text into a list of clauses.
  static List<QueryClause> parseAll(String queryText) {
    return queryText
        .split('\n')
        .map(parse)
        .whereType<QueryClause>()
        .toList();
  }
}
