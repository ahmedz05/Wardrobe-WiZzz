import 'package:flutter/material.dart';

class AppTheme {
  static const ink = Color(0xFF203E35);
  static const canvas = Color(0xFFF7F6F0);
  static const sage = Color(0xFFE4EBDE);
  static const rust = Color(0xFF9D482C);

  static ThemeData get light {
    final scheme = ColorScheme.fromSeed(
      seedColor: ink,
      primary: ink,
      secondary: rust,
      surface: canvas,
    );
    final base = ThemeData(
      useMaterial3: true,
      colorScheme: scheme,
      scaffoldBackgroundColor: canvas,
    );
    return base.copyWith(
      textTheme: base.textTheme.copyWith(
        headlineLarge: const TextStyle(
          fontFamily: 'Georgia',
          fontSize: 40,
          fontWeight: FontWeight.w500,
          color: ink,
          letterSpacing: -1.2,
        ),
        headlineMedium: const TextStyle(
          fontFamily: 'Georgia',
          fontSize: 30,
          fontWeight: FontWeight.w500,
          color: ink,
          letterSpacing: -.6,
        ),
        titleLarge: const TextStyle(
          fontSize: 21,
          fontWeight: FontWeight.w600,
          color: ink,
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: Colors.white,
        contentPadding: const EdgeInsets.symmetric(
          horizontal: 18,
          vertical: 18,
        ),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: const BorderSide(color: Color(0xFFD5DBD3)),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: const BorderSide(color: Color(0xFFD5DBD3)),
        ),
      ),
      filledButtonTheme: FilledButtonThemeData(
        style: FilledButton.styleFrom(
          minimumSize: const Size(48, 52),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(14),
          ),
        ),
      ),
      cardTheme: CardThemeData(
        color: Colors.white,
        elevation: 0,
        margin: EdgeInsets.zero,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(22),
          side: const BorderSide(color: Color(0xFFE2E5DC)),
        ),
      ),
      navigationBarTheme: const NavigationBarThemeData(
        backgroundColor: Colors.white,
        indicatorColor: sage,
      ),
      dividerTheme: const DividerThemeData(
        color: Color(0xFFE2E5DC),
        thickness: 1,
      ),
    );
  }
}
