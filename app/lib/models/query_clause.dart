/// A parsed clause from the query editor.
/// Example: `| where t_any_cuisines contains "French"`
/// -> field: t_any_cuisines, operator: contains, value: French
class QueryClause {
  final String field;
  final String operator;
  final String value;

  /// For contains-any: parsed list of values.
  final List<String> values;

  const QueryClause({
    required this.field,
    required this.operator,
    required this.value,
    this.values = const [],
  });

  @override
  String toString() => '| where $field $operator "$value"';

  /// Known queryable fields.
  static const knownFields = {
    't_log_type',
    't_any_names',
    't_any_people',
    't_any_cities',
    't_any_states',
    't_any_counties',
    't_any_countries',
    't_any_regions',
    't_any_keywords',
    't_any_categories',
    't_any_actors',
    't_any_roles',
    't_any_shows',
    't_any_cuisines',
    't_any_dishes',
    't_any_eras',
    't_any_continents',
    't_any_urls',
    't_any_video_ids',
    't_any_coordinates',
    't_any_geohashes',
  };

  /// Whether the field is a recognized queryable field.
  bool get isValidField => knownFields.contains(field);

  /// Parse a single query line into a clause.
  /// Supports: `| where field op "value"` and `field op "value"`
  /// Also supports: `field contains-any ["v1", "v2"]` and `field contains-any v1, v2`
  static QueryClause? parse(String line) {
    final trimmed = line.trim();
    if (trimmed.isEmpty || trimmed == 'locations') return null;

    // Try contains-any first (has different value syntax)
    final containsAnyRegex = RegExp(
      r'(?:\|\s*where\s+)?(\w[\w.]*)\s+contains-any\s+(.+)',
      caseSensitive: false,
    );
    final caMatch = containsAnyRegex.firstMatch(trimmed);
    if (caMatch != null) {
      final field = caMatch.group(1)!;
      final rawValues = caMatch.group(2)!.trim();
      final values = _parseValueList(rawValues);
      if (values.isEmpty) return null;
      return QueryClause(
        field: field,
        operator: 'contains-any',
        value: values.join(', '),
        values: values,
      );
    }

    // Standard: field operator "value"
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

  /// Parse a value list from contains-any syntax.
  /// Supports: `["v1", "v2"]` or `v1, v2` or `"v1", "v2"`
  static List<String> _parseValueList(String raw) {
    // JSON array style: ["v1", "v2"]
    if (raw.startsWith('[') && raw.endsWith(']')) {
      raw = raw.substring(1, raw.length - 1);
    }
    // Extract quoted values
    final quoted = RegExp(r'"([^"]*)"');
    final matches = quoted.allMatches(raw);
    if (matches.isNotEmpty) {
      return matches.map((m) => m.group(1)!).toList();
    }
    // Fallback: comma-separated unquoted
    return raw.split(',').map((s) => s.trim()).where((s) => s.isNotEmpty).toList();
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
