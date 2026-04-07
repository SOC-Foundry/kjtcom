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

  List<String> get countryCodes => _stringList('t_any_country_codes');

  /// Returns [lat, lng] if t_any_coordinates is present and valid.
  /// Supports both List of numbers [lat, lng] and List of maps [{"lat": X, "lon": Y}].
  (double, double)? get coordinates {
    final val = raw['t_any_coordinates'];
    if (val is! List || val.isEmpty) return null;

    // Format 1: [lat, lon, ...]
    if (val.length >= 2 && val[0] is! Map) {
      final lat = val[0] is num ? (val[0] as num).toDouble() : double.tryParse(val[0].toString());
      final lng = val[1] is num ? (val[1] as num).toDouble() : double.tryParse(val[1].toString());
      if (lat != null && lng != null) return (lat, lng);
    }

    // Format 2: [{"lat": 33.1, "lon": -117.3}]
    if (val[0] is Map) {
      final map = val[0] as Map;
      final latVal = map['lat'] ?? map['latitude'];
      final lngVal = map['lon'] ?? map['lng'] ?? map['longitude'];

      final lat = latVal is num ? latVal.toDouble() : double.tryParse(latVal.toString());
      final lng = lngVal is num ? lngVal.toDouble() : double.tryParse(lngVal.toString());

      if (lat != null && lng != null) return (lat, lng);
    }

    return null;
  }

  List<String> get continents => _stringList('t_any_continents');
  List<String> get countries => _stringList('t_any_countries');

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
