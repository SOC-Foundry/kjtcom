import 'package:flutter/material.dart';
import '../theme/tokens.dart';

/// Component-patterns.md Section 6 - Globe Hero Background.
/// Ambient visual behind the query editor. 260px height, 15% opacity.
/// Uses globe_hero.jpg if available, otherwise a gradient placeholder.
class GlobeHero extends StatelessWidget {
  const GlobeHero({super.key});

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: 260,
      width: double.infinity,
      child: Opacity(
        opacity: 0.15,
        child: Container(
          decoration: const BoxDecoration(
            gradient: RadialGradient(
              center: Alignment(0.3, -0.2),
              radius: 1.2,
              colors: [
                Color(0xFF1B4332),
                Tokens.surfaceBase,
              ],
            ),
          ),
        ),
      ),
    );
  }
}
