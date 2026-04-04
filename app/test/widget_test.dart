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

  test('QueryClause parses contains-any with JSON array', () {
    final clause = QueryClause.parse(
        '| where t_any_cuisines contains-any ["mexican", "italian"]');
    expect(clause, isNotNull);
    expect(clause!.field, 't_any_cuisines');
    expect(clause.operator, 'contains-any');
    expect(clause.values, ['mexican', 'italian']);
  });

  test('QueryClause parses contains-any with comma list', () {
    final clause = QueryClause.parse(
        '| where t_any_cuisines contains-any "mexican", "italian"');
    expect(clause, isNotNull);
    expect(clause!.operator, 'contains-any');
    expect(clause.values, ['mexican', 'italian']);
  });

  test('QueryClause validates known fields', () {
    final valid = QueryClause.parse('| where t_any_cuisines contains "french"');
    expect(valid!.isValidField, true);

    final invalid = QueryClause.parse('| where t_any_nonexistent contains "test"');
    expect(invalid!.isValidField, false);
  });

  test('QueryClause recognizes t_any_country_codes as valid field', () {
    final clause =
        QueryClause.parse('| where t_any_country_codes contains "fr"');
    expect(clause, isNotNull);
    expect(clause!.field, 't_any_country_codes');
    expect(clause.isValidField, true);
  });

  test('QueryClause parses country code contains-any', () {
    final clause = QueryClause.parse(
        '| where t_any_country_codes contains-any ["fr", "it"]');
    expect(clause, isNotNull);
    expect(clause!.operator, 'contains-any');
    expect(clause.values, ['fr', 'it']);
    expect(clause.isValidField, true);
  });

  test('QueryClause rejects unknown field with country_codes-like name', () {
    final clause =
        QueryClause.parse('| where t_any_country_codez contains "fr"');
    expect(clause!.isValidField, false);
  });

  test('QueryClause parses != operator', () {
    final clause = QueryClause.parse('| where t_log_type != "calgold"');
    expect(clause, isNotNull);
    expect(clause!.field, 't_log_type');
    expect(clause.operator, '!=');
    expect(clause.value, 'calgold');
  });

  test('QueryClause parses unquoted value', () {
    final clause = QueryClause.parse('| where t_any_cuisines contains french');
    expect(clause, isNotNull);
    expect(clause!.field, 't_any_cuisines');
    expect(clause.operator, 'contains');
    expect(clause.value, 'french');
  });

  test('QueryClause parses unquoted multi-word value', () {
    final clause =
        QueryClause.parse('| where t_any_cuisines contains french toast');
    expect(clause, isNotNull);
    expect(clause!.value, 'french toast');
  });

  // v9.33 regression test: exact query that failed on live site
  test('QueryClause parses quoted geology keyword query', () {
    final clause =
        QueryClause.parse('| where t_any_keywords contains "geology"');
    expect(clause, isNotNull);
    expect(clause!.field, 't_any_keywords');
    expect(clause.operator, 'contains');
    expect(clause.value, 'geology');
  });

  test('QueryClause parses == with quoted value', () {
    final clause =
        QueryClause.parse('| where t_any_cuisines == "french"');
    expect(clause, isNotNull);
    expect(clause!.operator, '==');
    expect(clause.value, 'french');
  });

  test('QueryClause parses != with quoted value', () {
    final clause =
        QueryClause.parse('| where t_log_type != "calgold"');
    expect(clause, isNotNull);
    expect(clause!.operator, '!=');
    expect(clause.value, 'calgold');
  });
}
