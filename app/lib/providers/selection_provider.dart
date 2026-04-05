import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/location_entity.dart';

/// Holds the currently selected entity for the detail panel.
class SelectedEntityNotifier extends Notifier<LocationEntity?> {
  @override
  LocationEntity? build() => null;

  void select(LocationEntity? entity) => state = entity;
}

final selectedEntityProvider = NotifierProvider<SelectedEntityNotifier, LocationEntity?>(SelectedEntityNotifier.new);
