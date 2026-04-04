import 'package:flutter/widgets.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/// Shared TextEditingController for the query editor.
/// Schema builder and detail panel use this to set text + cursor position (G45).
final queryTextControllerProvider = Provider<TextEditingController>((ref) {
  final controller = TextEditingController();
  ref.onDispose(() => controller.dispose());
  return controller;
});

/// Holds the current query text in the editor.
class QueryNotifier extends Notifier<String> {
  @override
  String build() => '';

  void setText(String text) => state = text;
}

final queryProvider = NotifierProvider<QueryNotifier, String>(QueryNotifier.new);

/// Flag to suppress ref.listen cursor override during programmatic updates (G45).
/// Set true before schema builder / +filter / -exclude sets controller.text,
/// cleared via Future.microtask after the update completes.
final programmaticUpdateProvider = StateProvider<bool>((ref) => false);
