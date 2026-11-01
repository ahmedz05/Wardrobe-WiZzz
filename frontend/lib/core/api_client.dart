import 'dart:async';
import 'dart:convert';

import 'package:http/http.dart' as http;

import 'api_config.dart';

class ApiException implements Exception {
  const ApiException(this.message, {this.statusCode});
  final String message;
  final int? statusCode;
  @override
  String toString() => message;
}

class ApiClient {
  ApiClient(
    this.config, {
    http.Client? client,
    this.timeout = const Duration(seconds: 30),
  }) : _client = client ?? http.Client();

  final ApiConfig config;
  final http.Client _client;
  final Duration timeout;
  String? accessToken;
  void Function()? onUnauthorized;

  Future<Object?> get(String path, {Map<String, String>? query}) =>
      _request('GET', path, query: query, authenticated: true);

  Future<Object?> postPublic(String path, Map<String, Object?> body) =>
      _request('POST', path, body: body);

  Future<Object?> _request(
    String method,
    String path, {
    Map<String, String>? query,
    Map<String, Object?>? body,
    bool authenticated = false,
  }) async {
    final token = authenticated ? accessToken : null;
    if (authenticated && token == null) {
      throw const ApiException('Please sign in to continue.', statusCode: 401);
    }
    final request = http.Request(method, config.endpoint(path, query))
      ..followRedirects = false
      ..headers['Accept'] = 'application/json';
    if (token != null) request.headers['Authorization'] = 'Bearer $token';
    if (body != null) {
      request.headers['Content-Type'] = 'application/json';
      request.body = jsonEncode(body);
    }
    try {
      // Apply the deadline to headers AND body. Never automatically retry writes.
      final response = await (() async => http.Response.fromStream(
        await _client.send(request),
      ))().timeout(timeout);
      if (response.statusCode == 401 && token != null && token == accessToken) {
        accessToken = null;
        onUnauthorized?.call();
      }
      Object? payload;
      try {
        payload = jsonDecode(utf8.decode(response.bodyBytes));
      } on FormatException {
        if (response.statusCode >= 200 && response.statusCode < 300) {
          throw const ApiException(
            'The server returned an unreadable response. Please try again.',
          );
        }
      }
      if (response.statusCode < 200 || response.statusCode >= 300) {
        throw ApiException(
          _errorMessage(response.statusCode, payload),
          statusCode: response.statusCode,
        );
      }
      return payload;
    } on TimeoutException {
      throw const ApiException(
        'The request timed out. Check your connection and try again.',
      );
    } on http.ClientException {
      throw const ApiException(
        'Could not reach Wardrobe-WIZzz. Check your connection and API address.',
      );
    }
  }

  String _errorMessage(int status, Object? payload) {
    if (status >= 500) {
      return 'The server could not complete the request. Please try again later.';
    }
    if (status == 401) {
      return 'Your session has expired or your sign-in details are incorrect. Please sign in again.';
    }
    if (status == 403) {
      return 'You do not have permission to access this resource.';
    }
    if (status == 429) {
      return 'Too many requests. Please wait a moment and try again.';
    }
    if (status >= 300 && status < 400) {
      return 'The API address redirected the request. Check your API configuration.';
    }
    if (payload case {'detail': final String detail}) {
      // Only intentional client-facing FastAPI messages, never HTML/stack traces.
      if (detail.length <= 250 && !detail.contains('<')) return detail;
    }
    if (status == 422) {
      return 'Some details were not accepted. Check the form and try again.';
    }
    return 'The request could not be completed (HTTP $status).';
  }

  void close() => _client.close();
}

T decodeModel<T>(Object? value, T Function() parse) {
  try {
    return parse();
  } on FormatException {
    throw const ApiException(
      'The server response did not match the expected format.',
    );
  } on TypeError {
    throw const ApiException(
      'The server response did not match the expected format.',
    );
  }
}
