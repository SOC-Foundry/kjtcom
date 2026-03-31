import 'package:flutter/material.dart';
import '../theme/tokens.dart';

/// Component-patterns.md Section 3 - Tab Bar.
/// Results / Map / Globe tabs. Only Results is functional in Phase 6c.
class KjtcomTabBar extends StatelessWidget {
  const KjtcomTabBar({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: const BoxDecoration(
        border: Border(bottom: BorderSide(color: Tokens.borderSubtle)),
      ),
      padding: const EdgeInsets.symmetric(vertical: Tokens.space2),
      child: const Row(
        children: [
          _Tab(label: 'Results', active: true),
          _Tab(label: 'Map', active: false),
          _Tab(label: 'Globe', active: false),
        ],
      ),
    );
  }
}

class _Tab extends StatelessWidget {
  final String label;
  final bool active;
  const _Tab({required this.label, required this.active});

  @override
  Widget build(BuildContext context) {
    return Container(
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
    );
  }
}
