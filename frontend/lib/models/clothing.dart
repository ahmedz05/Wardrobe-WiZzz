class Clothing {
  const Clothing({
    required this.id,
    required this.name,
    required this.favorite,
    required this.isActive,
    this.style,
    this.season,
    this.occasion,
    this.imageUrl,
    this.fit,
    this.warmthLevel,
    this.notes,
    this.timesWorn = 0,
  });

  factory Clothing.fromJson(Map<String, dynamic> json) => Clothing(
    id: json['id'] as int,
    name: json['name'] as String,
    favorite: json['favorite'] as bool,
    isActive: json['is_active'] as bool,
    style: json['style'] as String?,
    season: json['season'] as String?,
    occasion: json['occasion'] as String?,
    imageUrl: json['image_url'] as String?,
    fit: json['fit'] as String?,
    warmthLevel: json['warmth_level'] as String?,
    notes: json['notes'] as String?,
    timesWorn: json['times_worn'] as int,
  );

  final int id;
  final String name;
  final bool favorite;
  final bool isActive;
  final String? style, season, occasion, imageUrl, fit, warmthLevel, notes;
  final int timesWorn;
}
