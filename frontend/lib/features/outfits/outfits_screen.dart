import 'package:flutter/material.dart';

import '../../core/app_theme.dart';
import '../../core/resource_controller.dart';
import '../../data/wardrobe_repository.dart';
import '../../models/outfit.dart';
import '../../shared/widgets.dart';

class OutfitsScreen extends StatefulWidget {
  const OutfitsScreen({super.key, required this.repository});
  final WardrobeRepository repository;
  @override
  State<OutfitsScreen> createState() => _OutfitsScreenState();
}

class _OutfitsScreenState extends State<OutfitsScreen> {
  final _state = ResourceController<OutfitResult>();
  final _form = GlobalKey<FormState>();
  final _city = TextEditingController();
  final _temperature = TextEditingController();
  WeatherMode _mode = WeatherMode.none;
  String _condition = '';
  bool _layers = true;
  bool _dirty = false;
  int _limit = 5;

  @override
  void dispose() {
    _state.dispose();
    _city.dispose();
    _temperature.dispose();
    super.dispose();
  }

  void _changed(VoidCallback change) => setState(() {
    change();
    _dirty = true;
  });

  Future<void> _generate() async {
    if (!_form.currentState!.validate()) return;
    FocusScope.of(context).unfocus();
    final options = OutfitOptions(
      limit: _limit,
      includeLayers: _layers,
      mode: _mode,
      city: _city.text,
      temperatureC: double.tryParse(_temperature.text.trim()),
      condition: _condition,
    );
    setState(() => _dirty = false);
    await _state.load(() => widget.repository.outfits(options));
  }

  @override
  Widget build(BuildContext context) => AnimatedBuilder(
    animation: _state,
    builder: (context, _) {
      final loading = _state.status == LoadStatus.loading;
      final result = _state.value;
      return ListView(
        primary: false,
        key: const PageStorageKey('outfits-scroll'),
        padding: const EdgeInsets.all(24),
        children: [
          const SectionHeading(
            eyebrow: 'A new way to wear it',
            title: 'Find your next outfit.',
            subtitle: 'Thoughtful combinations. Made from your own pieces.',
          ),
          const SizedBox(height: 26),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(20),
              child: Form(
                key: _form,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Make it work for your day',
                      style: Theme.of(context).textTheme.titleLarge,
                    ),
                    const SizedBox(height: 18),
                    Wrap(
                      spacing: 16,
                      runSpacing: 16,
                      children: [
                        SizedBox(
                          width: 220,
                          child: DropdownButtonFormField<WeatherMode>(
                            isExpanded: true,
                            key: const Key('weather-mode'),
                            initialValue: _mode,
                            decoration: const InputDecoration(
                              labelText: 'Weather context',
                            ),
                            items: const [
                              DropdownMenuItem(
                                value: WeatherMode.none,
                                child: Text('Fashion only'),
                              ),
                              DropdownMenuItem(
                                value: WeatherMode.city,
                                child: Text('Current city weather'),
                              ),
                              DropdownMenuItem(
                                value: WeatherMode.manual,
                                child: Text('Set weather manually'),
                              ),
                            ],
                            onChanged: loading
                                ? null
                                : (mode) => _changed(() => _mode = mode!),
                          ),
                        ),
                        SizedBox(
                          width: 140,
                          child: DropdownButtonFormField<int>(
                            isExpanded: true,
                            initialValue: _limit,
                            decoration: const InputDecoration(
                              labelText: 'Results',
                            ),
                            items: [5, 10, 20]
                                .map(
                                  (n) => DropdownMenuItem(
                                    value: n,
                                    child: Text('Up to $n'),
                                  ),
                                )
                                .toList(),
                            onChanged: loading
                                ? null
                                : (value) => _changed(() => _limit = value!),
                          ),
                        ),
                      ],
                    ),
                    if (_mode == WeatherMode.city) ...[
                      const SizedBox(height: 16),
                      TextFormField(
                        key: const Key('city'),
                        controller: _city,
                        enabled: !loading,
                        maxLength: 120,
                        textInputAction: TextInputAction.done,
                        onChanged: (_) => _changed(() {}),
                        decoration: const InputDecoration(
                          labelText: 'City',
                          hintText: 'For example, Cairo',
                          prefixIcon: Icon(Icons.location_city_outlined),
                        ),
                        validator: (value) =>
                            value == null || value.trim().length < 2
                            ? 'Enter at least 2 characters for your city.'
                            : null,
                      ),
                      const Text(
                        'Your city is sent to the weather provider for this request. No device location is collected.',
                        style: TextStyle(
                          fontSize: 12,
                          color: Color(0xFF52645B),
                        ),
                      ),
                    ],
                    if (_mode == WeatherMode.manual) ...[
                      const SizedBox(height: 16),
                      Wrap(
                        spacing: 16,
                        runSpacing: 16,
                        children: [
                          SizedBox(
                            width: 220,
                            child: TextFormField(
                              key: const Key('temperature'),
                              controller: _temperature,
                              enabled: !loading,
                              keyboardType:
                                  const TextInputType.numberWithOptions(
                                    decimal: true,
                                    signed: true,
                                  ),
                              decoration: const InputDecoration(
                                labelText: 'Temperature (°C)',
                                hintText: '-30 to 60',
                              ),
                              onChanged: (_) => _changed(() {}),
                              validator: (value) {
                                final temp = double.tryParse(
                                  value?.trim() ?? '',
                                );
                                return temp == null ||
                                        !temp.isFinite ||
                                        temp < -30 ||
                                        temp > 60
                                    ? 'Enter a temperature from -30 to 60.'
                                    : null;
                              },
                            ),
                          ),
                          SizedBox(
                            width: 220,
                            child: DropdownButtonFormField<String>(
                              isExpanded: true,
                              initialValue: _condition,
                              decoration: const InputDecoration(
                                labelText: 'Condition',
                              ),
                              items:
                                  [
                                        '',
                                        'Clear',
                                        'Cloudy',
                                        'Rain',
                                        'Snow',
                                        'Windy',
                                      ]
                                      .map(
                                        (value) => DropdownMenuItem(
                                          value: value,
                                          child: Text(
                                            value.isEmpty
                                                ? 'Not specified'
                                                : value,
                                          ),
                                        ),
                                      )
                                      .toList(),
                              onChanged: loading
                                  ? null
                                  : (value) =>
                                        _changed(() => _condition = value!),
                            ),
                          ),
                        ],
                      ),
                    ],
                    const SizedBox(height: 12),
                    SwitchListTile.adaptive(
                      contentPadding: EdgeInsets.zero,
                      title: const Text('Consider layers'),
                      subtitle: const Text(
                        'Include compatible outerwear and layering pieces.',
                      ),
                      value: _layers,
                      onChanged: loading
                          ? null
                          : (value) => _changed(() => _layers = value),
                    ),
                    const SizedBox(height: 14),
                    FilledButton.icon(
                      key: const Key('generate-outfits'),
                      onPressed: loading ? null : _generate,
                      icon: loading
                          ? const SizedBox(
                              width: 18,
                              height: 18,
                              child: CircularProgressIndicator(strokeWidth: 2),
                            )
                          : const Icon(Icons.auto_awesome_outlined),
                      label: Text(
                        loading
                            ? 'Finding your combinations…'
                            : 'Find my outfits',
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
          const SizedBox(height: 24),
          if (_dirty && result != null) ...[
            const MessageBox(
              'Settings changed. Find outfits again to update these results.',
              isError: false,
            ),
            const SizedBox(height: 20),
          ],
          if (_state.status == LoadStatus.idle)
            const StatePanel(
              icon: Icons.auto_awesome_outlined,
              title: 'Your next look is in there',
              message:
                  'We’ll combine your tops, bottoms and shoes, with optional layers and weather context. Choose your settings and find your outfits.',
            )
          else if (loading)
            const Padding(
              padding: EdgeInsets.all(40),
              child: Center(
                child: CircularProgressIndicator(
                  semanticsLabel: 'Generating outfit recommendations',
                ),
              ),
            )
          else if (_state.status == LoadStatus.failed) ...[
            StatePanel(
              icon: Icons.auto_awesome_outlined,
              title: 'We couldn’t find your outfits',
              message: _state.error!,
              action: _generate,
            ),
            const Text(
              'Recommendations need at least one usable top, bottom and pair of shoes, each with a subcategory and color.',
              textAlign: TextAlign.center,
              style: TextStyle(color: Color(0xFF52645B)),
            ),
          ] else if (result != null) ...[
            if (result.weatherEnabled)
              MessageBox(
                [
                  if (result.locationName != null) result.locationName!,
                  if (result.temperatureC != null)
                    '${result.temperatureC!.toStringAsFixed(1)} °C',
                  if (result.condition != null) result.condition!,
                  if (result.provider != null) 'via ${result.provider}',
                ].join(' · '),
                isError: false,
              ),
            const SizedBox(height: 16),
            Text(
              '${result.outfits.length} looks from ${result.itemsConsidered} usable pieces',
              style: Theme.of(context).textTheme.titleMedium,
            ),
            const SizedBox(height: 6),
            const Text(
              'Match scores reflect compatibility, not a prediction of personal preference.',
              style: TextStyle(color: Color(0xFF52645B), fontSize: 12),
            ),
            const SizedBox(height: 20),
            if (result.outfits.isEmpty)
              const StatePanel(
                icon: Icons.checkroom_outlined,
                title: 'No compatible combinations yet',
                message:
                    'Your pieces did not produce an outfit above the compatibility threshold. Review their categories, colors and style metadata, or try different weather settings.',
              ),
            for (final (index, outfit) in result.outfits.indexed) ...[
              _OutfitCard(outfit: outfit, number: index + 1),
              const SizedBox(height: 18),
            ],
          ],
        ],
      );
    },
  );
}

class _OutfitCard extends StatelessWidget {
  const _OutfitCard({required this.outfit, required this.number});
  final Outfit outfit;
  final int number;
  @override
  Widget build(BuildContext context) => Card(
    child: Padding(
      padding: const EdgeInsets.all(22),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Wrap(
            alignment: WrapAlignment.spaceBetween,
            spacing: 18,
            runSpacing: 12,
            children: [
              Text(
                'Combination ${number.toString().padLeft(2, '0')}',
                style: Theme.of(context).textTheme.titleLarge,
              ),
              Chip(
                avatar: const Icon(
                  Icons.auto_awesome,
                  size: 17,
                  color: AppTheme.ink,
                ),
                label: Text('${outfit.score.toStringAsFixed(0)}/100 match'),
                backgroundColor: AppTheme.sage,
                side: BorderSide.none,
              ),
            ],
          ),
          const SizedBox(height: 10),
          for (final entry in outfit.pieces.entries)
            Padding(
              padding: const EdgeInsets.symmetric(vertical: 10),
              child: Row(
                children: [
                  Container(
                    width: 52,
                    height: 58,
                    decoration: BoxDecoration(
                      color: AppTheme.sage,
                      borderRadius: BorderRadius.circular(14),
                    ),
                    child: Icon(
                      entry.key == 'shoes'
                          ? Icons.hiking_outlined
                          : Icons.checkroom_outlined,
                      color: AppTheme.ink,
                    ),
                  ),
                  const SizedBox(width: 14),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          entry.key == 'shoes'
                              ? 'SHOES'
                              : entry.key.toUpperCase(),
                          style: const TextStyle(
                            fontSize: 10,
                            letterSpacing: 1.5,
                            color: Color(0xFF52645B),
                          ),
                        ),
                        const SizedBox(height: 3),
                        Text(
                          entry.value.name,
                          style: const TextStyle(
                            fontWeight: FontWeight.w600,
                            fontSize: 16,
                          ),
                        ),
                        if (entry.value.subcategory != null)
                          Text(entry.value.subcategory!),
                      ],
                    ),
                  ),
                  if (entry.value.colorName != null)
                    Padding(
                      padding: const EdgeInsets.only(left: 10),
                      child: Tooltip(
                        message: entry.value.colorName!,
                        child: Container(
                          width: 24,
                          height: 24,
                          decoration: BoxDecoration(
                            shape: BoxShape.circle,
                            color: _color(entry.value.hexCode),
                            border: Border.all(color: const Color(0xFF8E9E91)),
                          ),
                        ),
                      ),
                    ),
                ],
              ),
            ),
          const Divider(height: 28),
          Wrap(
            spacing: 20,
            runSpacing: 8,
            children: [
              Text(
                'Fashion ${outfit.compatibilityScore.toStringAsFixed(0)}/100',
              ),
              Text(
                outfit.weatherScore == null
                    ? 'Weather not scored'
                    : 'Weather ${outfit.weatherScore!.toStringAsFixed(0)}/100',
              ),
            ],
          ),
        ],
      ),
    ),
  );

  Color _color(String? hex) {
    final value = hex?.replaceFirst('#', '') ?? '';
    if (!RegExp(r'^[0-9a-fA-F]{6}$').hasMatch(value)) return AppTheme.sage;
    return Color(int.parse('FF$value', radix: 16));
  }
}
