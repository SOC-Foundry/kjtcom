import 'package:flutter_riverpod/flutter_riverpod.dart';

/// Active tab index: 0=Results, 1=Map, 2=Globe, 3=IAO.
final activeTabProvider = StateProvider<int>((ref) => 0);
