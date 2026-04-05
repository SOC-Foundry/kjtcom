import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../theme/tokens.dart';
import '../providers/tab_provider.dart';

/// Tab bar: Results | Map | Globe | IAO | Gotcha | Schema.
/// Active tab controlled via activeTabProvider.
class KjtcomTabBar extends ConsumerWidget {
  const KjtcomTabBar({super.key});

  static const _labels = ['Results', 'Map', 'Globe', 'IAO', 'Gotcha', 'Schema'];

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final activeIndex = ref.watch(activeTabProvider);

    return Container(
      decoration: const BoxDecoration(
        border: Border(bottom: BorderSide(color: Tokens.borderSubtle)),
      ),
      padding: const EdgeInsets.symmetric(vertical: Tokens.space2),
      child: Row(
        children: [
          for (int i = 0; i < _labels.length; i++)
            _Tab(
              label: _labels[i],
              active: i == activeIndex,
              onTap: () => ref.read(activeTabProvider.notifier).setTab(i),
            ),
        ],
      ),
    );
  }
}

class _Tab extends StatelessWidget {
  final String label;
  final bool active;
  final VoidCallback onTap;
  const _Tab({required this.label, required this.active, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return MouseRegion(
      cursor: SystemMouseCursors.click,
      child: GestureDetector(
        onTap: onTap,
        child: Container(
          padding: const EdgeInsets.symmetric(
            horizontal: Tokens.space2,
            vertical: Tokens.space1,
          ),
          decoration: BoxDecoration(
            border: Border(
              bottom: BorderSide(
                color: active ? Tokens.accentBlue : Colors.transparent,
                width: 2,
              ),
            ),
          ),
          child: Text(
            label,
            style: TextStyle(
              fontFamily: Tokens.fontSans,
              fontSize: Tokens.sizeMd,
              color: active ? Tokens.textPrimary : Tokens.textSecondary,
            ),
          ),
        ),
      ),
    );
  }
}
