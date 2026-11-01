import 'package:flutter/foundation.dart';

import 'api_client.dart';

enum LoadStatus { idle, loading, ready, failed }

/// A request generation prevents older responses from replacing newer results.
class ResourceController<T> extends ChangeNotifier {
  LoadStatus status = LoadStatus.idle;
  T? value;
  String? error;
  int _request = 0;
  bool _disposed = false;

  Future<void> load(Future<T> Function() fetch) async {
    final request = ++_request;
    status = LoadStatus.loading;
    value = null;
    error = null;
    notifyListeners();
    try {
      final result = await fetch();
      if (_disposed || request != _request) return;
      value = result;
      status = LoadStatus.ready;
    } catch (exception) {
      if (_disposed || request != _request) return;
      error = exception is ApiException
          ? exception.message
          : 'Something went wrong. Please try again.';
      status = LoadStatus.failed;
    }
    if (!_disposed) notifyListeners();
  }

  @override
  void dispose() {
    _disposed = true;
    _request++;
    value = null;
    super.dispose();
  }
}
