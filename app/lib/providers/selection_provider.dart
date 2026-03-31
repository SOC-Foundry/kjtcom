import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/location_entity.dart';

/// Holds the currently selected entity for the detail panel.
final selectedEntityProvider = StateProvider<LocationEntity?>((ref) => null);
