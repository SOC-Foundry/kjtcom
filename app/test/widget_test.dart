import 'package:flutter_test/flutter_test.dart';
import 'package:kjtcom/models/query_clause.dart';

void main() {
  test('QueryClause parses piped syntax', () {
    final clause = QueryClause.parse('| where t_any_cuisines contains "French"');
    expect(clause, isNotNull);
    expect(clause!.field, 't_any_cuisines');
    expect(clause.operator, 'contains');
    expect(clause.value, 'French');
  });

  test('QueryClause returns null for collection name', () {
    expect(QueryClause.parse('locations'), isNull);
  });

  test('QueryClause.parseAll handles multi-line', () {
    const query = 'locations\n| where t_any_shows == "Rick Steves\' Europe"\n';
    final clauses = QueryClause.parseAll(query);
    expect(clauses.length, 1);
    expect(clauses.first.operator, '==');
  });
}
