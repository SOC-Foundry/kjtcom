import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/location_entity.dart';
import '../models/query_clause.dart';
import 'query_provider.dart';

/// Streams results from the Firestore `locations` collection on the
/// production (default) database. Translates parsed query clauses into
/// Firestore compound queries.
///
/// Firestore limitation: only ONE arrayContains per query. Additional
/// array filters are applied client-side.
final resultsProvider = StreamProvider<List<LocationEntity>>((ref) {
  final queryText = ref.watch(queryProvider);
  final clauses = QueryClause.parseAll(queryText);

  Query<Map<String, dynamic>> query =
      FirebaseFirestore.instance.collection('locations');

  // Separate: one server-side arrayContains, rest client-side
  final List<QueryClause> clientSideClauses = [];
  bool usedArrayContains = false;

  for (final clause in clauses) {
    if (clause.operator == 'contains' && !usedArrayContains) {
      query = query.where(clause.field, arrayContains: clause.value);
      usedArrayContains = true;
    } else if (clause.operator == '==' && !clause.field.startsWith('t_any_')) {
      // Scalar field equality -> server-side
      query = query.where(clause.field, isEqualTo: clause.value);
    } else {
      clientSideClauses.add(clause);
    }
  }

  // Limit to 200 to control Firestore reads
  query = query.limit(200);

  return query.snapshots().map((snapshot) {
    var entities = snapshot.docs
        .map((doc) => LocationEntity.fromFirestore(doc))
        .toList();

    // Apply client-side filters
    for (final clause in clientSideClauses) {
      entities = entities.where((e) {
        final val = e.raw[clause.field];
        final values = val is List
            ? val.map((v) => v.toString().toLowerCase()).toList()
            : <String>[];
        final target = clause.value.toLowerCase();

        return switch (clause.operator) {
          'contains' => values.contains(target),
          '==' => values.contains(target) ||
              (val is String && val.toLowerCase() == target),
          '!=' => !values.contains(target),
          _ => true,
        };
      }).toList();
    }

    return entities;
  });
});

/// Distinct country count from current results.
final countryCountProvider = Provider<int>((ref) {
  final results = ref.watch(resultsProvider);
  return results.when(
    data: (entities) =>
        entities.map((e) => e.country.toLowerCase()).toSet().length,
    loading: () => 0,
    error: (_, _) => 0,
  );
});
