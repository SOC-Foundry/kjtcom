import 'package:flutter/material.dart';

/// Design tokens from app/design-brief/design-tokens.json (Phase 6b).
/// Every value traces to a specific token in the design contract.
abstract final class Tokens {
  // -- color.surface --
  static const Color surfaceBase = Color(0xFF0D1117);
  static const Color surfaceElevated = Color(0xFF161B22);
  static const Color surfaceOverlay = Color(0xFF1B2838);
  static const Color surfaceRowHover = Color(0xFF1A2332);
  static const Color surfaceFilterPositive = Color(0xFF1B4332);
  static const Color surfaceFilterNegative = Color(0xFF3B1B1B);
  static const Color surfaceCta = Color(0xFF238636);

  // -- color.border --
  static const Color borderDefault = Color(0xFF30363D);
  static const Color borderSubtle = Color(0xFF21262D);

  // -- color.text --
  static const Color textPrimary = Color(0xFFE2E8F0);
  static const Color textSecondary = Color(0xFF94A3B8);
  static const Color textMuted = Color(0xFF6E7681);
  static const Color textOnCta = Color(0xFFFFFFFF);

  // -- color.accent --
  static const Color accentGreen = Color(0xFF4ADE80);
  static const Color accentBlue = Color(0xFF58A6FF);
  static const Color accentOrange = Color(0xFFFFA657);
  static const Color accentRed = Color(0xFFFF7B72);

  // -- color.syntax --
  static const Color syntaxField = Color(0xFF79C0FF);
  static const Color syntaxOperator = Color(0xFFFF7B72);
  static const Color syntaxValue = Color(0xFFA5D6FF);
  static const Color syntaxKeyword = Color(0xFFD2A8FF);
  static const Color syntaxCursor = Color(0xFF4ADE80);

  // -- color.pipeline --
  static const Color pipelineCalGold = Color(0xFFDA7E12);
  static const Color pipelineRickSteves = Color(0xFF3B82F6);
  static const Color pipelineTripleDB = Color(0xFFDD3333);
  static const Color pipelineBourdain = Color(0xFF8B5CF6);

  static Color pipelineColor(String logType) => switch (logType) {
        'calgold' => pipelineCalGold,
        'ricksteves' => pipelineRickSteves,
        'tripledb' => pipelineTripleDB,
        'bourdain' => pipelineBourdain,
        _ => textSecondary,
      };

  static String pipelineBadge(String logType) => switch (logType) {
        'calgold' => 'CG',
        'ricksteves' => 'RS',
        'tripledb' => 'TD',
        'bourdain' => 'NR',
        _ => '??',
      };

  // -- typography.family --
  static const String fontSans = 'GeistSans';
  static const String fontMono = 'GeistMono';

  // -- typography.size --
  static const double sizeXs = 9;
  static const double sizeSm = 10;
  static const double sizeBase = 11;
  static const double sizeMd = 12;
  static const double sizeLg = 13;
  static const double sizeXl = 14;
  static const double size2xl = 18;

  // -- spacing --
  static const double space1 = 4;
  static const double space2 = 8;
  static const double space3 = 12;
  static const double space4 = 16;
  static const double space5 = 20;
  static const double space6 = 24;
  static const double space8 = 32;

  // -- radius --
  static const double radiusSm = 3;
  static const double radiusMd = 4;
  static const double radiusLg = 6;
  static const double radiusXl = 8;
  static const double radius2xl = 12;

  // -- layout --
  static const double maxWidth = 1440;
  static const double sidebarWidth = 320;
  static const double lineNumberWidth = 20;

  // -- breakpoint --
  static const double bpMobile = 375;
  static const double bpTablet = 768;
  static const double bpDesktop = 1024;
  static const double bpWide = 1440;

  // -- animation --
  static const Duration detailSlide = Duration(milliseconds: 200);
  static const Duration rowHighlight = Duration(milliseconds: 150);
}
