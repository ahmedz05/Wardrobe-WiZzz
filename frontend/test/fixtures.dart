// Explicit test-only examples shaped from the local FastAPI routes and serializers.
const accountJson = {
  'id': 7,
  'username': 'Amina',
  'email': 'amina@example.com',
};
const tokenJson = {'access_token': 'test-session', 'token_type': 'bearer'};
const clothingJson = {
  'id': 11,
  'user_id': 7,
  'name': 'Linen shirt',
  'favorite': true,
  'is_active': true,
  'style': 'Casual',
  'season': 'Summer',
  'occasion': null,
  'image_url': null,
  'times_worn': 3,
};
const outfitJson = {
  'wardrobe_items_considered': 3,
  'outfits_generated': 1,
  'scoring_version': '2.2',
  'weather_context': {
    'enabled': true,
    'temperature_c': 24,
    'condition': 'Clear',
  },
  'weather_source': {
    'provider': 'Open-Meteo',
    'location': {'name': 'Cairo'},
    'weather': {'temperature_c': 24, 'condition': 'Clear'},
  },
  'outfits': [
    {
      'score': 88,
      'compatibility_score': 90,
      'weather_score': 80,
      'has_layer': false,
      'items': {
        'top': {
          'id': 11,
          'name': 'Linen shirt',
          'category': 'Tops',
          'subcategory': 'Shirt',
          'color': {'id': 1, 'name': 'White', 'hex_code': '#FFFFFF'},
        },
        'bottom': {
          'id': 12,
          'name': 'Chinos',
          'category': 'Bottoms',
          'subcategory': 'Chinos',
          'color': null,
        },
        'shoes': {
          'id': 13,
          'name': 'Sneakers',
          'category': 'Shoes',
          'subcategory': 'Sneakers',
          'color': null,
        },
        'layer': null,
      },
      'pair_analysis': [],
      'weather_analysis': [],
    },
  ],
};
