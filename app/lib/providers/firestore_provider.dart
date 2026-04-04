import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/location_entity.dart';
import '../models/query_clause.dart';
import 'query_provider.dart';

/// Query result metadata: entities + truncation info.
class QueryResult {
  final List<LocationEntity> entities;
  final int serverCount;
  final int limit;

  const QueryResult({
    required this.entities,
    required this.serverCount,
    required this.limit,
  });

  bool get isTruncated => serverCount >= limit;
}

/// The Firestore query limit.
const _queryLimit = 1000;

/// Streams results from the Firestore `locations` collection on the
/// production (default) database. Translates parsed query clauses into
/// Firestore compound queries.
///
/// Firestore limitation: only ONE arrayContains per query. Additional
/// array filters are applied client-side.
final queryResultProvider = StreamProvider<QueryResult>((ref) {
  final queryText = ref.watch(queryProvider);
  final clauses = QueryClause.parseAll(queryText);

  Query<Map<String, dynamic>> query =
      FirebaseFirestore.instance.collection('locations');

  // Separate: one server-side array op, rest client-side.
  // Firestore allows one arrayContains OR one arrayContainsAny per query.
  final List<QueryClause> clientSideClauses = [];
  bool usedArrayOp = false;

  for (final clause in clauses) {
    if (clause.operator == 'contains-any' && !usedArrayOp) {
      final lowered = clause.values.map((v) => v.toLowerCase()).toList();
      // Firestore limits arrayContainsAny to 30 values
      query = query.where(clause.field,
          arrayContainsAny: lowered.take(30).toList());
      usedArrayOp = true;
    } else if (clause.operator == 'contains' && !usedArrayOp) {
      query = query.where(clause.field, arrayContains: clause.value.toLowerCase());
      usedArrayOp = true;
    } else if (clause.operator == '==' && !clause.field.startsWith('t_any_')) {
      // Scalar field equality -> server-side
      query = query.where(clause.field, isEqualTo: clause.value.toLowerCase());
    } else {
      clientSideClauses.add(clause);
    }
  }

  query = query.limit(_queryLimit);

  return query.snapshots().map((snapshot) {
    final serverCount = snapshot.docs.length;

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
          'contains-any' => clause.values.any(
              (v) => values.contains(v.toLowerCase())),
          '==' => values.contains(target) ||
              (val is String && val.toLowerCase() == target),
          '!=' => !values.contains(target),
          _ => true,
        };
      }).toList();
    }

    return QueryResult(
      entities: entities,
      serverCount: serverCount,
      limit: _queryLimit,
    );
  });
});

/// Backward-compatible provider that exposes just the entity list.
final resultsProvider = StreamProvider<List<LocationEntity>>((ref) {
  final asyncResult = ref.watch(queryResultProvider);
  return asyncResult.when(
    data: (qr) => Stream.value(qr.entities),
    loading: () => const Stream.empty(),
    error: (e, st) => Stream.error(e, st),
  );
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
