import 'package:cloud_firestore/cloud_firestore.dart';

/// A single entity from the Firestore `locations` collection.
/// Maps Thompson Indicator Fields (t_any_*) to typed Dart fields.
class LocationEntity {
  final String id;
  final String logType;
  final Map<String, dynamic> raw;

  LocationEntity({required this.id, required this.logType, required this.raw});

  factory LocationEntity.fromFirestore(DocumentSnapshot<Map<String, dynamic>> doc) {
    final data = doc.data() ?? {};
    return LocationEntity(
      id: doc.id,
      logType: (data['t_log_type'] as String?) ?? '',
      raw: data,
    );
  }

  String get name {
    final names = _stringList('t_any_names');
    return names.isNotEmpty ? names.first : id;
  }

  String get city {
    final cities = _stringList('t_any_cities');
    return cities.isNotEmpty ? cities.first : '';
  }

  String get country {
    final countries = _stringList('t_any_countries');
    return countries.isNotEmpty ? countries.first : '';
  }

  String get show {
    final shows = _stringList('t_any_shows');
    return shows.isNotEmpty ? shows.first : '';
  }

  /// Returns all t_any_* and t_enrichment.* fields for the detail panel.
  Map<String, dynamic> get displayFields {
    final result = <String, dynamic>{};
    for (final entry in raw.entries) {
      if (entry.key.startsWith('t_any_') || entry.key.startsWith('t_enrichment')) {
        result[entry.key] = entry.value;
      }
    }
    return result;
  }

  List<String> _stringList(String key) {
    final val = raw[key];
    if (val is List) return val.map((e) => e.toString()).toList();
    if (val is String) return [val];
    return [];
  }
}
