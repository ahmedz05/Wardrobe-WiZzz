class OutfitPiece {
  const OutfitPiece({
    required this.id,
    required this.name,
    this.category,
    this.subcategory,
    this.colorName,
    this.hexCode,
  });
  factory OutfitPiece.fromJson(Map<String, dynamic> json) {
    final color = json['color'] as Map<String, dynamic>?;
    return OutfitPiece(
      id: json['id'] as int,
      name: json['name'] as String,
      category: json['category'] as String?,
      subcategory: json['subcategory'] as String?,
      colorName: color?['name'] as String?,
      hexCode: color?['hex_code'] as String?,
    );
  }
  final int id;
  final String name;
  final String? category, subcategory, colorName, hexCode;
}

class Outfit {
  const Outfit({
    required this.score,
    required this.compatibilityScore,
    required this.pieces,
    this.weatherScore,
  });
  factory Outfit.fromJson(Map<String, dynamic> json) {
    final items = json['items'] as Map<String, dynamic>;
    return Outfit(
      score: (json['score'] as num).toDouble(),
      compatibilityScore: (json['compatibility_score'] as num).toDouble(),
      weatherScore: (json['weather_score'] as num?)?.toDouble(),
      pieces: {
        for (final role in ['top', 'bottom', 'shoes', 'layer'])
          if (items[role] != null)
            role: OutfitPiece.fromJson(items[role] as Map<String, dynamic>),
      },
    );
  }
  final double score, compatibilityScore;
  final double? weatherScore;
  final Map<String, OutfitPiece> pieces;
}

class OutfitResult {
  const OutfitResult({
    required this.outfits,
    required this.itemsConsidered,
    required this.generated,
    required this.weatherEnabled,
    this.temperatureC,
    this.condition,
    this.locationName,
    this.provider,
  });
  factory OutfitResult.fromJson(Map<String, dynamic> json) {
    final context = json['weather_context'] as Map<String, dynamic>;
    final source = json['weather_source'] as Map<String, dynamic>?;
    final location = source?['location'] as Map<String, dynamic>?;
    return OutfitResult(
      outfits: (json['outfits'] as List<dynamic>)
          .map((e) => Outfit.fromJson(e as Map<String, dynamic>))
          .toList(growable: false),
      itemsConsidered: json['wardrobe_items_considered'] as int,
      generated: json['outfits_generated'] as int,
      weatherEnabled: context['enabled'] as bool,
      temperatureC: (context['temperature_c'] as num?)?.toDouble(),
      condition: context['condition'] as String?,
      locationName: location?['name'] as String?,
      provider: source?['provider'] as String?,
    );
  }
  final List<Outfit> outfits;
  final int itemsConsidered, generated;
  final bool weatherEnabled;
  final double? temperatureC;
  final String? condition, locationName, provider;
}
