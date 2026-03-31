import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../theme/tokens.dart';
import '../providers/firestore_provider.dart';

/// Component-patterns.md Section 3 - Entity Count Row.
/// "47 entities across 8 countries" below tab bar.
class EntityCountRow extends ConsumerWidget {
  const EntityCountRow({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final asyncResults = ref.watch(resultsProvider);
    final countryCount = ref.watch(countryCountProvider);

    return Padding(
      padding: const EdgeInsets.symmetric(vertical: Tokens.space2),
      child: asyncResults.when(
        loading: () => const Text(
          'Loading...',
          style: TextStyle(
            fontFamily: Tokens.fontSans,
            fontSize: Tokens.sizeMd,
            color: Tokens.textMuted,
          ),
        ),
        error: (_, _) => const SizedBox.shrink(),
        data: (entities) => Row(
          children: [
            Text(
              '${entities.length} entities',
              style: const TextStyle(
                fontFamily: Tokens.fontSans,
                fontSize: Tokens.sizeMd,
                fontWeight: FontWeight.w500,
                color: Tokens.accentGreen,
              ),
            ),
            const SizedBox(width: Tokens.space2),
            Text(
              'across $countryCount countries',
              style: const TextStyle(
                fontFamily: Tokens.fontSans,
                fontSize: Tokens.sizeBase,
                color: Tokens.textSecondary,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
