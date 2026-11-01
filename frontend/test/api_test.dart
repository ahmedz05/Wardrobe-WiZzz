import 'dart:async';
import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:wardrobe_wizzz/core/api_client.dart';
import 'package:wardrobe_wizzz/core/api_config.dart';
import 'package:wardrobe_wizzz/data/wardrobe_repository.dart';

import 'fixtures.dart';

void main() {
  final config = ApiConfig('https://wardrobe.example/api');

  test(
    'base URLs preserve a proxy prefix and require explicit insecure development',
    () {
      expect(
        config.endpoint('login').toString(),
        'https://wardrobe.example/api/login',
      );
      for (final value in [
        'http://localhost:8000',
        'ftp://example.com',
        'https://u:p@example.com',
        'https://example.com?key=secret',
        'invalid',
      ]) {
        expect(() => ApiConfig(value), throwsArgumentError);
      }
      expect(
        ApiConfig(
          'http://localhost:8000',
          allowInsecureHttp: true,
        ).baseUri.scheme,
        'http',
      );
    },
  );

  test(
    'images only resolve to backend uploads without credentials or tracking parameters',
    () {
      expect(
        config.imageUri('/uploads/shirt.png')?.toString(),
        'https://wardrobe.example/uploads/shirt.png',
      );
      for (final value in [
        'https://tracker.example/photo.jpg',
        '//tracker.example/a',
        'file:///secret',
        '/uploads/../secret',
        '/uploads/a?token=secret',
        '/elsewhere/a',
      ]) {
        expect(config.imageUri(value), isNull, reason: value);
      }
    },
  );

  test(
    'login is JSON, public requests omit bearer tokens, protected requests send bearer',
    () async {
      final seen = <String>[];
      final api = ApiClient(
        config,
        client: MockClient((request) async {
          seen.add(request.url.path);
          expect(request.followRedirects, isFalse);
          if (request.url.path.endsWith('/login')) {
            expect(request.headers['Authorization'], isNull);
            expect(
              request.headers['Content-Type'],
              contains('application/json'),
            );
            expect(jsonDecode(request.body), {
              'email': 'amina@example.com',
              'password': 'a password',
            });
            return http.Response(jsonEncode(tokenJson), 200);
          }
          expect(request.headers['Authorization'], 'Bearer test-session');
          return http.Response(jsonEncode(accountJson), 200);
        }),
      );
      addTearDown(api.close);
      final repository = WardrobeRepository(api);
      api.accessToken = await repository.login(
        'amina@example.com',
        'a password',
      );
      expect((await repository.me()).username, 'Amina');
      expect(seen, ['/api/login', '/api/me']);
    },
  );

  test(
    'clothing decodes nullable metadata and excludes inactive pieces',
    () async {
      final api = ApiClient(
        config,
        client: MockClient(
          (_) async => http.Response(
            jsonEncode([
              clothingJson,
              {...clothingJson, 'id': 99, 'is_active': false},
            ]),
            200,
          ),
        ),
      )..accessToken = 'test-session';
      addTearDown(api.close);
      final items = await WardrobeRepository(api).clothing();
      expect(items.single.name, 'Linen shirt');
      expect(items.single.occasion, isNull);
      expect(items.single.timesWorn, 3);
    },
  );

  test(
    'recommendations use the actual query and nested response contract',
    () async {
      final api = ApiClient(
        config,
        client: MockClient((request) async {
          expect(request.url.path, '/api/outfits/generate');
          expect(request.url.queryParameters, {
            'limit': '10',
            'include_layers': 'false',
            'location': 'Cairo',
          });
          return http.Response(jsonEncode(outfitJson), 200);
        }),
      )..accessToken = 'test-session';
      addTearDown(api.close);
      final result = await WardrobeRepository(api).outfits(
        const OutfitOptions(
          limit: 10,
          includeLayers: false,
          mode: WeatherMode.city,
          city: ' Cairo ',
        ),
      );
      expect(result.outfits.single.pieces.keys, ['top', 'bottom', 'shoes']);
      expect(result.outfits.single.weatherScore, 80);
      expect(result.locationName, 'Cairo');
      expect(result.temperatureC, 24);
    },
  );

  test('weather options are exclusive and validated against route bounds', () {
    expect(const OutfitOptions(city: 'ignored', temperatureC: 25).toQuery(), {
      'limit': '5',
      'include_layers': 'true',
    });
    expect(
      const OutfitOptions(
        mode: WeatherMode.manual,
        temperatureC: 0,
        condition: 'Snow',
        city: 'ignored',
      ).toQuery(),
      {
        'limit': '5',
        'include_layers': 'true',
        'temperature_c': '0.0',
        'condition': 'Snow',
      },
    );
    for (final option in [
      const OutfitOptions(limit: 21),
      const OutfitOptions(mode: WeatherMode.city, city: 'A'),
      const OutfitOptions(mode: WeatherMode.manual),
      const OutfitOptions(mode: WeatherMode.manual, temperatureC: 61),
      const OutfitOptions(mode: WeatherMode.manual, temperatureC: double.nan),
    ]) {
      expect(option.toQuery, throwsArgumentError);
    }
  });

  test('401 invalidates only the session used for that request', () async {
    final response = Completer<http.Response>();
    final api = ApiClient(config, client: MockClient((_) => response.future))
      ..accessToken = 'old-token';
    addTearDown(api.close);
    var expired = 0;
    api.onUnauthorized = () => expired++;
    final pending = api.get('clothing');
    api.accessToken = 'new-token';
    response.complete(http.Response('{"detail":"Invalid token"}', 401));
    await expectLater(pending, throwsA(isA<ApiException>()));
    expect(expired, 0);
    expect(api.accessToken, 'new-token');
  });

  test('current-session 401 clears the in-memory token', () async {
    final api = ApiClient(
      config,
      client: MockClient((_) async => http.Response('{}', 401)),
    )..accessToken = 'expired';
    addTearDown(api.close);
    var expired = 0;
    api.onUnauthorized = () => expired++;
    await expectLater(api.get('me'), throwsA(isA<ApiException>()));
    expect(api.accessToken, isNull);
    expect(expired, 1);
  });

  test(
    'server errors, validation arrays, and malformed success responses are safe errors',
    () async {
      for (final (status, body) in [
        (500, '<html>private server details</html>'),
        (422, '{"detail":[{"msg":"bad input","input":"secret-password"}]}'),
        (200, 'not JSON'),
        (200, '{"unexpected":true}'),
        (302, '{}'),
      ]) {
        final api = ApiClient(
          config,
          client: MockClient((_) async => http.Response(body, status)),
        )..accessToken = 't';
        addTearDown(api.close);
        await expectLater(
          WardrobeRepository(api).clothing(),
          throwsA(
            isA<ApiException>().having(
              (e) => e.message,
              'safe message',
              isNot(
                anyOf(contains('secret-password'), contains('private server')),
              ),
            ),
          ),
        );
      }
    },
  );

  test('connection failures and deadlines produce actionable errors', () async {
    final offline = ApiClient(
      config,
      client: MockClient(
        (_) async => throw http.ClientException('socket details'),
      ),
    )..accessToken = 't';
    addTearDown(offline.close);
    await expectLater(
      offline.get('me'),
      throwsA(
        isA<ApiException>().having(
          (e) => e.message,
          'message',
          contains('Could not reach'),
        ),
      ),
    );
    final slow = ApiClient(
      config,
      timeout: const Duration(milliseconds: 5),
      client: MockClient((_) async {
        await Future<void>.delayed(const Duration(milliseconds: 20));
        return http.Response('{}', 200);
      }),
    )..accessToken = 't';
    addTearDown(slow.close);
    await expectLater(
      slow.get('me'),
      throwsA(
        isA<ApiException>().having(
          (e) => e.message,
          'message',
          contains('timed out'),
        ),
      ),
    );
  });
}
