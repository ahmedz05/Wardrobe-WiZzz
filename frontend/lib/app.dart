import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';

import 'core/app_theme.dart';
import 'data/wardrobe_repository.dart';
import 'features/auth/auth_controller.dart';
import 'features/auth/auth_screen.dart';
import 'features/outfits/outfits_screen.dart';
import 'features/wardrobe/wardrobe_screen.dart';
import 'shared/widgets.dart';

class WardrobeApp extends StatefulWidget {
  const WardrobeApp({super.key, required this.auth, required this.repository});
  final AuthController auth;
  final WardrobeRepository repository;
  @override
  State<WardrobeApp> createState() => _WardrobeAppState();
}

class _WardrobeAppState extends State<WardrobeApp> {
  @override
  void initState() {
    super.initState();
    unawaited(widget.auth.restore());
  }

  @override
  void dispose() {
    widget.auth.dispose();
    widget.repository.api.close();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => MaterialApp(
    title: 'Wardrobe-WIZzz',
    debugShowCheckedModeBanner: false,
    theme: AppTheme.light,
    home: AnimatedBuilder(
      animation: widget.auth,
      builder: (context, _) => switch (widget.auth.status) {
        SessionStatus.restoring => const Scaffold(
          body: Center(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Brand(),
                SizedBox(height: 32),
                CircularProgressIndicator(
                  semanticsLabel: 'Checking your session',
                ),
              ],
            ),
          ),
        ),
        SessionStatus.recovery => Scaffold(
          body: SafeArea(
            child: Center(
              child: SingleChildScrollView(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    StatePanel(
                      icon: Icons.lock_outline,
                      title: 'Let’s reconnect safely',
                      message: widget.auth.error!,
                      action: widget.auth.restore,
                      actionLabel: 'Retry session',
                    ),
                    TextButton(
                      onPressed: widget.auth.signOut,
                      child: const Text('Clear session'),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
        SessionStatus.signedOut => AuthScreen(auth: widget.auth),
        SessionStatus.signedIn => _AppShell(
          key: ValueKey(widget.auth.account!.id),
          auth: widget.auth,
          repository: widget.repository,
        ),
      },
    ),
  );
}

class _AppShell extends StatefulWidget {
  const _AppShell({super.key, required this.auth, required this.repository});
  final AuthController auth;
  final WardrobeRepository repository;
  @override
  State<_AppShell> createState() => _AppShellState();
}

class _AppShellState extends State<_AppShell> {
  int _selected = 0;
  static const _destinations = [
    NavigationDestination(
      icon: Icon(Icons.checkroom_outlined),
      selectedIcon: Icon(Icons.checkroom),
      label: 'Wardrobe',
    ),
    NavigationDestination(
      icon: Icon(Icons.auto_awesome_outlined),
      selectedIcon: Icon(Icons.auto_awesome),
      label: 'Outfits',
    ),
    NavigationDestination(
      icon: Icon(Icons.person_outline),
      selectedIcon: Icon(Icons.person),
      label: 'Account',
    ),
  ];
  @override
  Widget build(BuildContext context) => LayoutBuilder(
    builder: (context, constraints) {
      final wide = constraints.maxWidth >= 900;
      return Scaffold(
        appBar: AppBar(
          title: const Brand(),
          backgroundColor: AppTheme.canvas,
          scrolledUnderElevation: 0,
          toolbarHeight: 76,
          actions: [
            Padding(
              padding: const EdgeInsets.only(right: 20),
              child: IconButton(
                tooltip: 'Account',
                onPressed: () => setState(() => _selected = 2),
                icon: const CircleAvatar(
                  backgroundColor: AppTheme.sage,
                  child: Icon(Icons.person_outline, color: AppTheme.ink),
                ),
              ),
            ),
          ],
        ),
        body: SafeArea(
          top: false,
          child: Row(
            children: [
              if (wide) ...[
                NavigationRail(
                  extended: constraints.maxWidth >= 1150,
                  backgroundColor: AppTheme.canvas,
                  selectedIndex: _selected,
                  onDestinationSelected: (value) =>
                      setState(() => _selected = value),
                  destinations: _destinations
                      .map(
                        (d) => NavigationRailDestination(
                          icon: d.icon,
                          selectedIcon: d.selectedIcon,
                          label: Text(d.label),
                        ),
                      )
                      .toList(),
                ),
                const VerticalDivider(width: 1),
              ],
              Expanded(
                child: Center(
                  child: ConstrainedBox(
                    constraints: const BoxConstraints(maxWidth: 1280),
                    child: IndexedStack(
                      index: _selected,
                      children: [
                        WardrobeScreen(repository: widget.repository),
                        OutfitsScreen(repository: widget.repository),
                        _AccountScreen(auth: widget.auth),
                      ],
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
        bottomNavigationBar: wide
            ? null
            : NavigationBar(
                selectedIndex: _selected,
                onDestinationSelected: (value) =>
                    setState(() => _selected = value),
                destinations: _destinations,
              ),
      );
    },
  );
}

class _AccountScreen extends StatelessWidget {
  const _AccountScreen({required this.auth});
  final AuthController auth;
  @override
  Widget build(BuildContext context) {
    final user = auth.account!;
    return ListView(
      key: const PageStorageKey('account-scroll'),
      primary: false,
      padding: const EdgeInsets.all(24),
      children: [
        const SectionHeading(
          eyebrow: 'Your space',
          title: 'A wardrobe that’s yours.',
          subtitle: 'Your account and session.',
        ),
        const SizedBox(height: 28),
        Card(
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const CircleAvatar(
                  radius: 32,
                  backgroundColor: AppTheme.sage,
                  child: Icon(
                    Icons.person_outline,
                    size: 32,
                    color: AppTheme.ink,
                  ),
                ),
                const SizedBox(height: 18),
                Text(
                  user.username,
                  style: Theme.of(context).textTheme.titleLarge,
                ),
                const SizedBox(height: 6),
                SelectableText(user.email),
                const Divider(height: 40),
                const Text(
                  'Private by design',
                  style: TextStyle(fontWeight: FontWeight.w700),
                ),
                const SizedBox(height: 8),
                Text(
                  kIsWeb
                      ? 'This browser session stays in memory and ends when you reload or close the app.'
                      : 'Your sign-in token is saved in your device’s secure storage. Your password is never saved by this app.',
                ),
                const SizedBox(height: 12),
                const Text(
                  'Signing out clears your saved session on this device. Other devices stay signed in.',
                ),
                const SizedBox(height: 24),
                OutlinedButton.icon(
                  onPressed: auth.signOut,
                  icon: const Icon(Icons.logout),
                  label: const Text('Sign out'),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }
}
