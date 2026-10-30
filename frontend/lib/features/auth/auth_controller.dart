import 'dart:async';

import 'package:flutter/foundation.dart';

import '../../core/api_client.dart';
import '../../core/token_store.dart';
import '../../data/wardrobe_repository.dart';
import '../../models/account.dart';

enum SessionStatus { restoring, signedOut, signedIn, recovery }

class AuthController extends ChangeNotifier {
  AuthController(this.repository, this.store) {
    repository.api.onUnauthorized = () => unawaited(_expire());
  }
  final WardrobeRepository repository;
  final TokenStore store;
  SessionStatus status = SessionStatus.restoring;
  Account? account;
  bool busy = false;
  String? error;
  String? notice;
  int _revision = 0;
  bool _disposed = false;

  void _emit() {
    if (!_disposed) notifyListeners();
  }

  Future<void> restore() async {
    final revision = ++_revision;
    status = SessionStatus.restoring;
    error = null;
    _emit();
    try {
      final token = await store.read();
      if (revision != _revision) return;
      if (token == null) {
        status = SessionStatus.signedOut;
      } else {
        repository.api.accessToken = token;
        final user = await repository.me();
        if (revision != _revision) return;
        account = user;
        status = SessionStatus.signedIn;
      }
    } catch (exception) {
      if (revision != _revision) return;
      repository.api.accessToken = null;
      status = SessionStatus.recovery;
      error = exception is ApiException
          ? exception.message
          : 'Secure storage is unavailable. Unlock your device and try again.';
    }
    _emit();
  }

  Future<void> signIn(String email, String password) async {
    if (busy || status != SessionStatus.signedOut) return;
    final revision = ++_revision;
    var savingToken = false;
    busy = true;
    error = null;
    notice = null;
    _emit();
    try {
      final token = await repository.login(email.trim(), password);
      if (revision != _revision) return;
      repository.api.accessToken = token;
      final user = await repository.me();
      if (revision != _revision) return;
      savingToken = true;
      await store.write(token);
      if (revision != _revision) return;
      account = user;
      status = SessionStatus.signedIn;
    } catch (exception) {
      if (revision != _revision) return;
      repository.api.accessToken = null;
      account = null;
      error = exception is ApiException
          ? exception.message
          : 'Could not save your session securely. Unlock your device and try again.';
      if (savingToken) {
        // A platform write may have partly succeeded before reporting failure.
        try {
          await store.clear();
        } catch (_) {
          if (revision != _revision) return;
          status = SessionStatus.recovery;
          error =
              'Could not save your session securely or remove the saved token. Unlock your device, then choose Clear session.';
        }
      }
    } finally {
      if (revision == _revision) {
        busy = false;
        _emit();
      }
    }
  }

  /// Registration does not return a token. Require a real subsequent login.
  Future<bool> register(String username, String email, String password) async {
    if (busy || status != SessionStatus.signedOut) return false;
    final revision = ++_revision;
    busy = true;
    error = null;
    notice = null;
    _emit();
    try {
      await repository.register(username.trim(), email.trim(), password);
      if (revision != _revision) return false;
      notice = 'Account created. Sign in with your email and password.';
      return true;
    } catch (exception) {
      if (revision == _revision) {
        error = exception is ApiException
            ? exception.message
            : 'Could not create your account. Please try again.';
      }
      return false;
    } finally {
      if (revision == _revision) {
        busy = false;
        _emit();
      }
    }
  }

  Future<void> _expire() async {
    notice = 'Your session has expired. Please sign in again.';
    await signOut(keepNotice: true);
  }

  Future<void> signOut({bool keepNotice = false}) async {
    final revision = ++_revision;
    repository.api.accessToken = null;
    account = null;
    busy = true;
    status = SessionStatus.restoring;
    error = null;
    if (!keepNotice) notice = null;
    _emit();
    try {
      await store.clear();
      if (revision != _revision) return;
      status = SessionStatus.signedOut;
    } catch (_) {
      if (revision != _revision) return;
      status = SessionStatus.recovery;
      error =
          'Could not remove the saved session. Unlock your device, then choose Clear session again.';
    } finally {
      if (revision == _revision) {
        busy = false;
        _emit();
      }
    }
  }

  @override
  void dispose() {
    _disposed = true;
    _revision++;
    repository.api.onUnauthorized = null;
    super.dispose();
  }
}
