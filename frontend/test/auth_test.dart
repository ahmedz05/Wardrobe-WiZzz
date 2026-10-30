import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:wardrobe_wizzz/core/api_client.dart';
import 'package:wardrobe_wizzz/core/api_config.dart';
import 'package:wardrobe_wizzz/core/token_store.dart';
import 'package:wardrobe_wizzz/data/wardrobe_repository.dart';
import 'package:wardrobe_wizzz/features/auth/auth_controller.dart';

import 'fixtures.dart';

AuthController controller(
  TokenStore store,
  Future<http.Response> Function(http.Request) handler,
) {
  final api = ApiClient(
    ApiConfig('https://example.com'),
    client: MockClient(handler),
  );
  final auth = AuthController(WardrobeRepository(api), store);
  addTearDown(() {
    auth.dispose();
    api.close();
  });
  return auth;
}

void main() {
  test(
    'partially written tokens are removed when secure persistence fails',
    () async {
      final store = PartialWriteStore();
      final auth = controller(
        store,
        (request) async => http.Response(
          jsonEncode(request.url.path == '/login' ? tokenJson : accountJson),
          200,
        ),
      );
      await auth.restore();
      await auth.signIn('amina@example.com', 'password');
      expect(auth.status, SessionStatus.signedOut);
      expect(await store.read(), isNull);
      expect(auth.repository.api.accessToken, isNull);
      expect(auth.error, contains('securely'));
    },
  );

  test(
    'login validates /me, persists only the token, and sign-out removes it',
    () async {
      final store = MemoryTokenStore();
      final auth = controller(
        store,
        (request) async => http.Response(
          jsonEncode(request.url.path == '/login' ? tokenJson : accountJson),
          200,
        ),
      );
      await auth.restore();
      expect(auth.status, SessionStatus.signedOut);
      await auth.signIn(' amina@example.com ', 'password');
      expect(auth.status, SessionStatus.signedIn);
      expect(auth.account?.id, 7);
      expect(await store.read(), 'test-session');
      await auth.signOut();
      expect(await store.read(), isNull);
      expect(auth.account, isNull);
      expect(auth.repository.api.accessToken, isNull);
    },
  );

  test(
    'registration confirms creation without inventing an authenticated session',
    () async {
      final store = MemoryTokenStore();
      final auth = controller(store, (request) async {
        expect(request.url.path, '/register');
        expect(jsonDecode(request.body), {
          'username': 'Amina',
          'email': 'amina@example.com',
          'password': 'password',
        });
        return http.Response(jsonEncode(accountJson), 200);
      });
      await auth.restore();
      expect(
        await auth.register(' Amina ', ' amina@example.com ', 'password'),
        isTrue,
      );
      expect(auth.status, SessionStatus.signedOut);
      expect(auth.notice, contains('Account created'));
      expect(await store.read(), isNull);
    },
  );

  test('invalid credentials never persist a session', () async {
    final store = MemoryTokenStore();
    final auth = controller(
      store,
      (_) async => http.Response('{"detail":"Invalid email or password"}', 401),
    );
    await auth.restore();
    await auth.signIn('amina@example.com', 'wrong');
    expect(auth.status, SessionStatus.signedOut);
    expect(auth.error, isNotNull);
    expect(auth.busy, isFalse);
    expect(await store.read(), isNull);
  });

  test('an expired stored token is cleared and returns to sign-in', () async {
    final store = MemoryTokenStore();
    await store.write('expired');
    final auth = controller(store, (_) async => http.Response('{}', 401));
    await auth.restore();
    await Future<void>.delayed(Duration.zero);
    expect(auth.status, SessionStatus.signedOut);
    expect(await store.read(), isNull);
    expect(auth.notice, contains('expired'));
  });

  test(
    'offline restore preserves the saved token for explicit retry',
    () async {
      final store = MemoryTokenStore();
      await store.write('valid-but-offline');
      final auth = controller(
        store,
        (_) async => throw http.ClientException('offline'),
      );
      await auth.restore();
      expect(auth.status, SessionStatus.recovery);
      expect(await store.read(), 'valid-but-offline');
      expect(auth.repository.api.accessToken, isNull);
    },
  );

  test(
    'secure-storage failures cannot claim login or logout success',
    () async {
      final store = FailingStore();
      final auth = controller(
        store,
        (request) async => http.Response(
          jsonEncode(request.url.path == '/login' ? tokenJson : accountJson),
          200,
        ),
      );
      await auth.restore();
      await auth.signIn('amina@example.com', 'password');
      expect(auth.status, SessionStatus.recovery);
      expect(auth.account, isNull);
      expect(auth.repository.api.accessToken, isNull);
      expect(auth.error, contains('securely'));
      await auth.signOut();
      expect(auth.status, SessionStatus.recovery);
      expect(auth.error, contains('remove'));
    },
  );
}

class PartialWriteStore extends MemoryTokenStore {
  @override
  Future<void> write(String token) async {
    await super.write(token);
    throw Exception('platform reported failure after writing');
  }
}

class FailingStore implements TokenStore {
  @override
  Future<String?> read() async => null;
  @override
  Future<void> write(String token) async =>
      throw Exception('secure storage failure');
  @override
  Future<void> clear() async => throw Exception('secure storage failure');
}
