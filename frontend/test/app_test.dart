import 'dart:async';
import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:wardrobe_wizzz/app.dart';
import 'package:wardrobe_wizzz/core/api_client.dart';
import 'package:wardrobe_wizzz/core/api_config.dart';
import 'package:wardrobe_wizzz/core/token_store.dart';
import 'package:wardrobe_wizzz/data/wardrobe_repository.dart';
import 'package:wardrobe_wizzz/features/auth/auth_controller.dart';

import 'fixtures.dart';

Future<void> mountApp(
  WidgetTester tester,
  Future<http.Response> Function(http.Request) handler, {
  bool signedIn = false,
}) async {
  final store = MemoryTokenStore();
  if (signedIn) await store.write('test-session');
  final repository = WardrobeRepository(
    ApiClient(ApiConfig('https://example.com'), client: MockClient(handler)),
  );
  await tester.pumpWidget(
    WardrobeApp(
      repository: repository,
      auth: AuthController(repository, store),
    ),
  );
  await tester.pumpAndSettle();
}

http.Response jsonResponse(Object? value) => http.Response(
  jsonEncode(value),
  200,
  headers: {'content-type': 'application/json'},
);

void main() {
  testWidgets(
    'small screens with enlarged text keep navigation and outfit controls usable',
    (tester) async {
      tester.view.physicalSize = const Size(360, 800);
      tester.view.devicePixelRatio = 1;
      tester.platformDispatcher.textScaleFactorTestValue = 1.5;
      addTearDown(tester.view.reset);
      addTearDown(tester.platformDispatcher.clearTextScaleFactorTestValue);
      await mountApp(
        tester,
        (request) async =>
            jsonResponse(request.url.path == '/me' ? accountJson : []),
        signedIn: true,
      );
      await tester.tap(find.text('Outfits'));
      await tester.pumpAndSettle();
      final outfitScroll = find
          .descendant(
            of: find.byKey(const PageStorageKey('outfits-scroll')),
            matching: find.byType(Scrollable),
          )
          .first;
      await tester.scrollUntilVisible(
        find.byKey(const Key('weather-mode')),
        150,
        scrollable: outfitScroll,
      );
      await tester.pumpAndSettle();
      await tester.tap(find.byKey(const Key('weather-mode')));
      await tester.pumpAndSettle();
      await tester.tap(find.text('Set weather manually').last);
      await tester.pumpAndSettle();
      await tester.scrollUntilVisible(
        find.byKey(const Key('temperature')),
        150,
        scrollable: outfitScroll,
      );
      await tester.pumpAndSettle();
      await tester.enterText(find.byKey(const Key('temperature')), 'NaN');
      await tester.scrollUntilVisible(
        find.byKey(const Key('generate-outfits')),
        150,
        scrollable: outfitScroll,
      );
      await tester.pumpAndSettle();
      await tester.tap(find.byKey(const Key('generate-outfits')));
      await tester.pumpAndSettle();
      expect(find.text('Enter a temperature from -30 to 60.'), findsOneWidget);
      expect(tester.takeException(), isNull);
    },
  );

  testWidgets(
    'real login flow renders wardrobe, search, recommendations and sign-out',
    (tester) async {
      tester.view.reset();
      tester.view.physicalSize = const Size(430, 932);
      tester.view.devicePixelRatio = 1;
      addTearDown(tester.view.reset);
      await mountApp(
        tester,
        (request) async => switch (request.url.path) {
          '/login' => jsonResponse(tokenJson),
          '/me' => jsonResponse(accountJson),
          '/clothing' => jsonResponse([clothingJson]),
          '/outfits/generate' => jsonResponse(outfitJson),
          _ => http.Response('{}', 404),
        },
      );
      await tester.enterText(
        find.byKey(const Key('email')),
        'amina@example.com',
      );
      await tester.enterText(
        find.byKey(const Key('password')),
        'correct password',
      );
      await tester.ensureVisible(find.byKey(const Key('auth-submit')));
      await tester.pumpAndSettle();
      await tester.tap(find.byKey(const Key('auth-submit')));
      await tester.pumpAndSettle();
      expect(find.text('Your wardrobe.'), findsOneWidget);
      expect(find.text('Linen shirt'), findsOneWidget);
      await tester.enterText(
        find.byKey(const Key('wardrobe-search')),
        'missing piece',
      );
      await tester.pumpAndSettle();
      expect(find.text('No matching pieces'), findsOneWidget);
      await tester.tap(find.text('Outfits'));
      await tester.pumpAndSettle();
      await tester.ensureVisible(find.byKey(const Key('generate-outfits')));
      await tester.pumpAndSettle();
      await tester.tap(find.byKey(const Key('generate-outfits')));
      await tester.pumpAndSettle();
      await tester.scrollUntilVisible(
        find.text('Combination 01'),
        200,
        scrollable: find
            .descendant(
              of: find.byType(ListView).first,
              matching: find.byType(Scrollable),
            )
            .first,
      );
      expect(find.text('Combination 01'), findsOneWidget);
      expect(find.text('88/100 match'), findsOneWidget);
      await tester.tap(find.text('Account'));
      await tester.pumpAndSettle();
      expect(find.text('amina@example.com'), findsOneWidget);
      await tester.ensureVisible(find.text('Sign out'));
      await tester.pumpAndSettle();
      await tester.tap(find.text('Sign out'));
      await tester.pumpAndSettle();
      expect(find.text('Sign in'), findsOneWidget);
      expect(find.text('Linen shirt'), findsNothing);
    },
  );

  testWidgets('invalid registration stays local and makes no API call', (
    tester,
  ) async {
    var calls = 0;
    await mountApp(tester, (_) async {
      calls++;
      return http.Response('{}', 500);
    });
    await tester.ensureVisible(find.text('New here? Create an account'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('New here? Create an account'));
    await tester.pumpAndSettle();
    await tester.ensureVisible(find.byKey(const Key('auth-submit')));
    await tester.pumpAndSettle();
    await tester.tap(find.byKey(const Key('auth-submit')));
    await tester.pumpAndSettle();
    expect(find.text('Enter a valid email address.'), findsOneWidget);
    expect(find.text('Enter a username.'), findsOneWidget);
    expect(calls, 0);
  });

  testWidgets('wardrobe error retries and recovers to an honest empty state', (
    tester,
  ) async {
    var attempts = 0;
    await mountApp(tester, (request) async {
      if (request.url.path == '/me') return jsonResponse(accountJson);
      attempts++;
      return attempts == 1 ? http.Response('{}', 500) : jsonResponse([]);
    }, signedIn: true);
    expect(find.text('Your wardrobe couldn’t load'), findsOneWidget);
    await tester.ensureVisible(find.text('Try again'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Try again'));
    await tester.pumpAndSettle();
    expect(find.text('A little room for possibility'), findsOneWidget);
    expect(attempts, 2);
  });

  testWidgets('pending clothing requests show a loading state', (tester) async {
    final pending = Completer<http.Response>();
    final store = MemoryTokenStore();
    await store.write('test-session');
    final repository = WardrobeRepository(
      ApiClient(
        ApiConfig('https://example.com'),
        client: MockClient((request) async {
          if (request.url.path == '/me') return jsonResponse(accountJson);
          return pending.future;
        }),
      ),
    );
    await tester.pumpWidget(
      WardrobeApp(
        repository: repository,
        auth: AuthController(repository, store),
      ),
    );
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 100));
    expect(find.bySemanticsLabel('Loading wardrobe'), findsOneWidget);
    pending.complete(jsonResponse([]));
    await tester.pumpAndSettle();
    expect(find.text('A little room for possibility'), findsOneWidget);
  });

  testWidgets('wide layout offers rail navigation without overflow', (
    tester,
  ) async {
    tester.view.physicalSize = const Size(1440, 1000);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.reset);
    await mountApp(
      tester,
      (request) async => jsonResponse(
        request.url.path == '/me' ? accountJson : [clothingJson],
      ),
      signedIn: true,
    );
    expect(find.byType(NavigationRail), findsOneWidget);
    expect(tester.takeException(), isNull);
  });
}
