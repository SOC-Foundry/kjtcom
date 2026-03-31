import 'package:flutter/material.dart';
import 'tokens.dart';

ThemeData buildTheme() {
  return ThemeData(
    brightness: Brightness.dark,
    scaffoldBackgroundColor: Tokens.surfaceBase,
    fontFamily: Tokens.fontSans,
    colorScheme: const ColorScheme.dark(
      surface: Tokens.surfaceBase,
      primary: Tokens.accentGreen,
      secondary: Tokens.accentBlue,
      error: Tokens.accentRed,
      onSurface: Tokens.textPrimary,
      onPrimary: Tokens.textOnCta,
    ),
    textTheme: const TextTheme(
      bodyLarge: TextStyle(
        fontFamily: Tokens.fontSans,
        fontSize: Tokens.sizeMd,
        fontWeight: FontWeight.w400,
        color: Tokens.textPrimary,
      ),
      bodyMedium: TextStyle(
        fontFamily: Tokens.fontSans,
        fontSize: Tokens.sizeBase,
        fontWeight: FontWeight.w400,
        color: Tokens.textSecondary,
      ),
      bodySmall: TextStyle(
        fontFamily: Tokens.fontSans,
        fontSize: Tokens.sizeSm,
        fontWeight: FontWeight.w400,
        color: Tokens.textMuted,
      ),
      titleMedium: TextStyle(
        fontFamily: Tokens.fontSans,
        fontSize: Tokens.sizeXl,
        fontWeight: FontWeight.w500,
        color: Tokens.textPrimary,
      ),
      labelSmall: TextStyle(
        fontFamily: Tokens.fontMono,
        fontSize: Tokens.sizeSm,
        fontWeight: FontWeight.w400,
        color: Tokens.textSecondary,
      ),
    ),
    dividerColor: Tokens.borderSubtle,
    dividerTheme: const DividerThemeData(
      color: Tokens.borderSubtle,
      thickness: 1,
      space: 0,
    ),
  );
}
