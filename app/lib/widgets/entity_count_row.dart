import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../theme/tokens.dart';
import '../providers/firestore_provider.dart';

/// Component-patterns.md Section 3 - Entity Count Row.
/// "47 entities across 8 countries" with animated count-up.
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
            _AnimatedCount(
              value: entities.length,
              suffix: ' entities',
              style: const TextStyle(
                fontFamily: Tokens.fontSans,
                fontSize: Tokens.sizeMd,
                fontWeight: FontWeight.w500,
                color: Tokens.accentGreen,
              ),
            ),
            const SizedBox(width: Tokens.space2),
            Text(
              'across ',
              style: const TextStyle(
                fontFamily: Tokens.fontSans,
                fontSize: Tokens.sizeBase,
                color: Tokens.textSecondary,
              ),
            ),
            _AnimatedCount(
              value: countryCount,
              suffix: ' countries',
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

/// Animates an integer count from its previous value to the new value.
class _AnimatedCount extends StatefulWidget {
  final int value;
  final String suffix;
  final TextStyle style;

  const _AnimatedCount({
    required this.value,
    required this.suffix,
    required this.style,
  });

  @override
  State<_AnimatedCount> createState() => _AnimatedCountState();
}

class _AnimatedCountState extends State<_AnimatedCount>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _animation;
  int _previousValue = 0;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: const Duration(milliseconds: 600),
      vsync: this,
    );
    _animation = Tween<double>(
      begin: 0,
      end: widget.value.toDouble(),
    ).animate(CurvedAnimation(parent: _controller, curve: Curves.easeOut));
    _controller.forward();
  }

  @override
  void didUpdateWidget(_AnimatedCount oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.value != widget.value) {
      _previousValue = oldWidget.value;
      _animation = Tween<double>(
        begin: _previousValue.toDouble(),
        end: widget.value.toDouble(),
      ).animate(CurvedAnimation(parent: _controller, curve: Curves.easeOut));
      _controller
        ..reset()
        ..forward();
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _animation,
      builder: (context, child) {
        return Text(
          '${_animation.value.round()}${widget.suffix}',
          style: widget.style,
        );
      },
    );
  }
}
