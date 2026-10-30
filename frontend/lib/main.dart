import 'package:flutter/material.dart';

import 'app.dart';
import 'core/api_client.dart';
import 'core/api_config.dart';
import 'core/app_theme.dart';
import 'core/token_store.dart';
import 'data/wardrobe_repository.dart';
import 'features/auth/auth_controller.dart';
import 'shared/widgets.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  try {
    final config = ApiConfig.fromEnvironment();
    final repository = WardrobeRepository(ApiClient(config));
    runApp(
      WardrobeApp(
        repository: repository,
        auth: AuthController(repository, createTokenStore(config.baseUri)),
      ),
    );
  } on ArgumentError {
    runApp(
      MaterialApp(
        theme: AppTheme.light,
        home: const Scaffold(
          body: SafeArea(
            child: StatePanel(
              icon: Icons.settings_outlined,
              title: 'Configure your connection',
              message:
                  'Set an HTTPS API_BASE_URL when starting the app. Local development over HTTP also requires ALLOW_INSECURE_HTTP=true. See frontend/README.md for commands.',
            ),
          ),
        ),
      ),
    );
  }
}
