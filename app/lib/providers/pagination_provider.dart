import 'package:flutter_riverpod/flutter_riverpod.dart';

/// Page size options: 20, 50, 100. Default 20.
class PageSizeNotifier extends Notifier<int> {
  @override
  int build() => 20;

  void setSize(int size) => state = size;
}

final pageSizeProvider = NotifierProvider<PageSizeNotifier, int>(PageSizeNotifier.new);

/// Current page index (0-based). Resets to 0 when page size changes.
class CurrentPageNotifier extends Notifier<int> {
  @override
  int build() {
    // Watch page size so changing it resets page to 0.
    ref.watch(pageSizeProvider);
    return 0;
  }

  void setPage(int page) => state = page;
}

final currentPageProvider = NotifierProvider<CurrentPageNotifier, int>(CurrentPageNotifier.new);
