import 'package:flutter/foundation.dart';

class ApiConfig {
  ApiConfig(String value, {bool allowInsecureHttp = false}) {
    final uri = Uri.tryParse(value);
    if (uri == null ||
        !uri.hasAuthority ||
        uri.host.isEmpty ||
        uri.userInfo.isNotEmpty ||
        uri.hasQuery ||
        uri.hasFragment ||
        !['http', 'https'].contains(uri.scheme)) {
      throw ArgumentError(
        'API_BASE_URL must be an HTTP(S) URL without credentials, query, or fragment.',
      );
    }
    if (uri.scheme != 'https' && !allowInsecureHttp) {
      throw ArgumentError(
        'HTTPS is required. For development, explicitly allow local HTTP.',
      );
    }
    baseUri = uri.replace(
      path: '${uri.path.replaceFirst(RegExp(r'/+$'), '')}/',
    );
  }

  factory ApiConfig.fromEnvironment() {
    const configured = String.fromEnvironment('API_BASE_URL');
    const allowHttp = bool.fromEnvironment('ALLOW_INSECURE_HTTP');
    if (kReleaseMode && configured.isEmpty) {
      throw ArgumentError(
        'Release builds require an explicit HTTPS API_BASE_URL.',
      );
    }
    final fallback = !kIsWeb && defaultTargetPlatform == TargetPlatform.android
        ? 'http://10.0.2.2:8000'
        : 'http://127.0.0.1:8000';
    return ApiConfig(
      configured.isEmpty ? fallback : configured,
      allowInsecureHttp: !kReleaseMode && allowHttp,
    );
  }

  late final Uri baseUri;

  Uri endpoint(String path, [Map<String, String>? query]) =>
      baseUri.resolve(path).replace(queryParameters: query);

  /// Only backend-hosted uploaded images are loaded. No third-party tracking URLs.
  Uri? imageUri(String? value) {
    if (value == null || value.trim().isEmpty) return null;
    final parsed = Uri.tryParse(value);
    if (parsed == null ||
        parsed.userInfo.isNotEmpty ||
        parsed.hasQuery ||
        parsed.hasFragment) {
      return null;
    }
    final resolved = baseUri.resolveUri(parsed);
    if (resolved.scheme != baseUri.scheme ||
        resolved.host != baseUri.host ||
        resolved.port != baseUri.port ||
        !resolved.path.startsWith('/uploads/') ||
        resolved.pathSegments.any((segment) => segment == '..')) {
      return null;
    }
    return resolved;
  }
}
