import '../core/api_client.dart';
import '../models/account.dart';
import '../models/clothing.dart';
import '../models/outfit.dart';

class WardrobeRepository {
  WardrobeRepository(this.api);
  final ApiClient api;

  Future<String> login(String email, String password) async {
    final value = await api.postPublic('login', {
      'email': email,
      'password': password,
    });
    return decodeModel(value, () {
      final data = value as Map<String, dynamic>;
      final token = data['access_token'] as String;
      if (token.isEmpty ||
          (data['token_type'] as String).toLowerCase() != 'bearer') {
        throw const FormatException('Expected bearer token.');
      }
      return token;
    });
  }

  Future<Account> register(
    String username,
    String email,
    String password,
  ) async {
    final value = await api.postPublic('register', {
      'username': username,
      'email': email,
      'password': password,
    });
    return decodeModel(
      value,
      () => Account.fromJson(value as Map<String, dynamic>),
    );
  }

  Future<Account> me() async {
    final value = await api.get('me');
    return decodeModel(
      value,
      () => Account.fromJson(value as Map<String, dynamic>),
    );
  }

  Future<List<Clothing>> clothing() async {
    final value = await api.get('clothing');
    return decodeModel(
      value,
      () => (value as List<dynamic>)
          .map((e) => Clothing.fromJson(e as Map<String, dynamic>))
          .where((item) => item.isActive)
          .toList(growable: false),
    );
  }

  Future<OutfitResult> outfits(OutfitOptions options) async {
    final value = await api.get('outfits/generate', query: options.toQuery());
    return decodeModel(
      value,
      () => OutfitResult.fromJson(value as Map<String, dynamic>),
    );
  }
}

enum WeatherMode { none, city, manual }

class OutfitOptions {
  const OutfitOptions({
    this.limit = 5,
    this.includeLayers = true,
    this.mode = WeatherMode.none,
    this.city,
    this.temperatureC,
    this.condition,
  });
  final int limit;
  final bool includeLayers;
  final WeatherMode mode;
  final String? city, condition;
  final double? temperatureC;

  Map<String, String> toQuery() {
    if (limit < 1 || limit > 20) {
      throw ArgumentError('Limit must be between 1 and 20.');
    }
    final query = {'limit': '$limit', 'include_layers': '$includeLayers'};
    switch (mode) {
      case WeatherMode.none:
        break;
      case WeatherMode.city:
        final cleaned = city?.trim() ?? '';
        if (cleaned.length < 2 || cleaned.length > 120) {
          throw ArgumentError('Enter a city between 2 and 120 characters.');
        }
        query['location'] = cleaned;
      case WeatherMode.manual:
        final temp = temperatureC;
        if (temp == null || !temp.isFinite || temp < -30 || temp > 60) {
          throw ArgumentError('Temperature must be between -30 and 60 °C.');
        }
        query['temperature_c'] = '$temp';
        if (condition != null && condition!.trim().isNotEmpty) {
          query['condition'] = condition!.trim();
        }
    }
    return query;
  }
}
