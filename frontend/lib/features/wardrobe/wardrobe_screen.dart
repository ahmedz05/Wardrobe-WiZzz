import 'package:flutter/material.dart';

import '../../core/api_config.dart';
import '../../core/app_theme.dart';
import '../../core/resource_controller.dart';
import '../../data/wardrobe_repository.dart';
import '../../models/clothing.dart';
import '../../shared/widgets.dart';

class WardrobeScreen extends StatefulWidget {
  const WardrobeScreen({super.key, required this.repository});
  final WardrobeRepository repository;
  @override
  State<WardrobeScreen> createState() => _WardrobeScreenState();
}

class _WardrobeScreenState extends State<WardrobeScreen> {
  final _state = ResourceController<List<Clothing>>();
  final _search = TextEditingController();
  bool _favorites = false;
  @override
  void initState() {
    super.initState();
    _reload();
  }

  Future<void> _reload() => _state.load(widget.repository.clothing);
  @override
  void dispose() {
    _state.dispose();
    _search.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => AnimatedBuilder(
    animation: _state,
    builder: (context, _) {
      final items = _state.value ?? [];
      final query = _search.text.trim().toLowerCase();
      final filtered = items
          .where(
            (item) =>
                (!_favorites || item.favorite) &&
                [item.name, item.style, item.season, item.occasion]
                    .whereType<String>()
                    .any((text) => text.toLowerCase().contains(query)),
          )
          .toList();
      return RefreshIndicator(
        onRefresh: _reload,
        child: CustomScrollView(
          primary: false,
          key: const PageStorageKey('wardrobe-scroll'),
          physics: const AlwaysScrollableScrollPhysics(),
          slivers: [
            SliverToBoxAdapter(
              child: Padding(
                padding: const EdgeInsets.fromLTRB(24, 28, 24, 24),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const SectionHeading(
                      eyebrow: 'The everyday collection',
                      title: 'Your wardrobe.',
                      subtitle: 'A little inspiration, already in your closet.',
                    ),
                    const SizedBox(height: 26),
                    TextField(
                      key: const Key('wardrobe-search'),
                      controller: _search,
                      onChanged: (_) => setState(() {}),
                      decoration: InputDecoration(
                        hintText: 'Search pieces, styles, seasons…',
                        prefixIcon: const Icon(Icons.search),
                        suffixIcon: _search.text.isEmpty
                            ? null
                            : IconButton(
                                tooltip: 'Clear search',
                                onPressed: () => setState(_search.clear),
                                icon: const Icon(Icons.close),
                              ),
                      ),
                    ),
                    const SizedBox(height: 16),
                    Wrap(
                      spacing: 10,
                      runSpacing: 8,
                      crossAxisAlignment: WrapCrossAlignment.center,
                      children: [
                        ChoiceChip(
                          label: const Text('All pieces'),
                          selected: !_favorites,
                          onSelected: (_) => setState(() => _favorites = false),
                        ),
                        ChoiceChip(
                          label: const Text('Favorites'),
                          avatar: const Icon(Icons.favorite_border, size: 17),
                          selected: _favorites,
                          onSelected: (_) => setState(() => _favorites = true),
                        ),
                        if (_state.status == LoadStatus.ready)
                          Text(
                            '${filtered.length} pieces',
                            style: const TextStyle(color: Color(0xFF52645B)),
                          ),
                        IconButton(
                          tooltip: 'Refresh wardrobe',
                          onPressed: _state.status == LoadStatus.loading
                              ? null
                              : _reload,
                          icon: const Icon(Icons.refresh),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
            if (_state.status == LoadStatus.loading)
              const SliverToBoxAdapter(
                child: Padding(
                  padding: EdgeInsets.all(60),
                  child: Center(
                    child: CircularProgressIndicator(
                      semanticsLabel: 'Loading wardrobe',
                    ),
                  ),
                ),
              )
            else if (_state.status == LoadStatus.failed)
              SliverToBoxAdapter(
                child: StatePanel(
                  icon: Icons.cloud_off_outlined,
                  title: 'Your wardrobe couldn’t load',
                  message: _state.error!,
                  action: _reload,
                ),
              )
            else if (filtered.isEmpty)
              SliverToBoxAdapter(
                child: StatePanel(
                  icon: Icons.checkroom_outlined,
                  title: items.isEmpty
                      ? 'A little room for possibility'
                      : 'No matching pieces',
                  message: items.isEmpty
                      ? 'Your wardrobe is empty. Existing pieces added through the backend will appear here. Pull down to refresh.'
                      : 'Try another search or switch to All pieces.',
                ),
              )
            else
              SliverPadding(
                padding: const EdgeInsets.fromLTRB(24, 0, 24, 32),
                sliver: SliverLayoutBuilder(
                  builder: (context, constraints) {
                    final columns = (constraints.crossAxisExtent / 240)
                        .floor()
                        .clamp(1, 4);
                    return SliverGrid.builder(
                      itemCount: filtered.length,
                      gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                        crossAxisCount: columns,
                        mainAxisSpacing: 18,
                        crossAxisSpacing: 18,
                        mainAxisExtent: 310,
                      ),
                      itemBuilder: (context, index) => _ClothingCard(
                        item: filtered[index],
                        config: widget.repository.api.config,
                        onTap: () => _showDetails(filtered[index]),
                      ),
                    );
                  },
                ),
              ),
          ],
        ),
      );
    },
  );

  void _showDetails(Clothing item) => showModalBottomSheet<void>(
    context: context,
    showDragHandle: true,
    isScrollControlled: true,
    useSafeArea: true,
    builder: (context) => SingleChildScrollView(
      padding: const EdgeInsets.fromLTRB(24, 8, 24, 40),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(item.name, style: Theme.of(context).textTheme.headlineMedium),
          const SizedBox(height: 20),
          for (final entry in {
            'Style': item.style,
            'Season': item.season,
            'Occasion': item.occasion,
            'Fit': item.fit,
            'Warmth': item.warmthLevel,
            'Times worn': '${item.timesWorn}',
            'Notes': item.notes,
          }.entries)
            if (entry.value != null && entry.value!.isNotEmpty)
              Padding(
                padding: const EdgeInsets.only(bottom: 14),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      entry.key,
                      style: const TextStyle(fontWeight: FontWeight.w700),
                    ),
                    const SizedBox(height: 3),
                    Text(entry.value!),
                  ],
                ),
              ),
        ],
      ),
    ),
  );
}

class _ClothingCard extends StatelessWidget {
  const _ClothingCard({
    required this.item,
    required this.config,
    required this.onTap,
  });
  final Clothing item;
  final ApiConfig config;
  final VoidCallback onTap;
  @override
  Widget build(BuildContext context) {
    final image = config.imageUri(item.imageUrl);
    final placeholder = Container(
      color: AppTheme.sage,
      child: const Center(
        child: Icon(Icons.checkroom_rounded, color: AppTheme.ink, size: 72),
      ),
    );
    return Card(
      clipBehavior: Clip.antiAlias,
      child: InkWell(
        onTap: onTap,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Expanded(
              child: Stack(
                fit: StackFit.expand,
                children: [
                  if (image == null)
                    placeholder
                  else
                    Image.network(
                      image.toString(),
                      fit: BoxFit.cover,
                      excludeFromSemantics: true,
                      errorBuilder: (_, _, _) => placeholder,
                      loadingBuilder: (_, child, progress) =>
                          progress == null ? child : placeholder,
                    ),
                  if (item.favorite)
                    const Positioned(
                      right: 12,
                      top: 12,
                      child: Tooltip(
                        message: 'Favorite',
                        child: CircleAvatar(
                          radius: 17,
                          backgroundColor: Colors.white,
                          child: Icon(
                            Icons.favorite,
                            size: 17,
                            color: AppTheme.rust,
                          ),
                        ),
                      ),
                    ),
                ],
              ),
            ),
            Padding(
              padding: const EdgeInsets.all(18),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    item.name,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(
                      fontWeight: FontWeight.w700,
                      fontSize: 17,
                    ),
                  ),
                  const SizedBox(height: 6),
                  Text(
                    [item.style, item.season]
                            .whereType<String>()
                            .where((s) => s.isNotEmpty)
                            .join(' · ')
                            .isEmpty
                        ? 'Wardrobe essential'
                        : [item.style, item.season]
                              .whereType<String>()
                              .where((s) => s.isNotEmpty)
                              .join(' · '),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(color: Color(0xFF52645B)),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
