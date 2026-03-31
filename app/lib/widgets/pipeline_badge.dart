import 'package:flutter/material.dart';
import '../theme/tokens.dart';

/// Component-patterns.md Section 4 - Pipeline Badge (SHOW column).
/// Colored chip: overlay bg, pipeline-colored text, 10px, 3px radius.
class PipelineBadge extends StatelessWidget {
  final String logType;
  const PipelineBadge({super.key, required this.logType});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 1),
      decoration: BoxDecoration(
        color: Tokens.surfaceOverlay,
        borderRadius: BorderRadius.circular(Tokens.radiusSm),
      ),
      child: Text(
        Tokens.pipelineBadge(logType),
        style: TextStyle(
          fontFamily: Tokens.fontSans,
          fontSize: Tokens.sizeSm,
          color: Tokens.pipelineColor(logType),
        ),
        textAlign: TextAlign.center,
      ),
    );
  }
}
