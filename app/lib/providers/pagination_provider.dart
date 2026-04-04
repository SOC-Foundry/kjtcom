import 'package:flutter_riverpod/flutter_riverpod.dart';

/// Page size options: 20, 50, 100. Default 20.
final pageSizeProvider = StateProvider<int>((ref) => 20);

/// Current page index (0-based). Resets to 0 when page size changes.
final currentPageProvider = StateProvider<int>((ref) {
  // Watch page size so changing it resets page to 0.
  ref.watch(pageSizeProvider);
  return 0;
});
