# First Flutter milestone — 2026-10-30

> Later integration update, 2026-10-30: real HTTP/PostgreSQL and Playwright MCP
> verification now passes. See [the integration report](../docs/INTEGRATION_MILESTONE.md).
> The original delivery notes below are historical: their startup-schema creation,
> hardcoded-auth configuration and unverified-integration blockers predate later fixes.
> Production upload/security and native-device concerns remain open.

## Delivered

The previously empty `frontend/` is now a Flutter application, directly in that folder. A shared Material 3 cream/forest theme, responsive navigation and modular controllers/repository/models support:

- Registration with validation and explicit return to sign-in after the real account response.
- JSON email/password login, `/me` validation, native secure token persistence, browser memory-only sessions, expiry handling, safe recovery and sign-out.
- Real wardrobe listing with active-item filtering, search, favorites filtering, details, refresh and honest empty/error/loading states.
- Outfit generation with result limit, optional layers and exclusive fashion-only/city/manual weather context. Cards display the actual returned pieces and fashion/weather/combined scores.
- A loopback web preview proxy for the existing backend, which has no CORS configuration. All upstream responses remain real; unavailable services remain errors.

There are no image upload controls or garment mutations. App code contains no demo account, wardrobe, weather or outfit data. Mock responses are confined to tests.

## Changed files

Only the root `.gitignore` and files under `frontend/` were changed by this implementation.

| Files | Purpose |
| --- | --- |
| `.gitignore` | Ignore workspace-local `.tools/` SDK/browser tooling |
| `frontend/pubspec.yaml`, `pubspec.lock`, `analysis_options.yaml`, `.gitignore`, `.metadata` | Dependencies, reproducibility, analysis and generated-artifact exclusions |
| `frontend/lib/main.dart`, `app.dart` | Dependency composition, guarded startup, session gate and adaptive navigation |
| `frontend/lib/core/api_config.dart`, `api_client.dart` | Configurable validated URLs, HTTPS enforcement, JSON/bearer transport, timeouts, safe errors and redirect protection |
| `frontend/lib/core/token_store.dart`, `resource_controller.dart`, `app_theme.dart` | Platform storage, request lifecycle and design tokens |
| `frontend/lib/data/wardrobe_repository.dart` | Adapters to inspected FastAPI routes and validated recommendation options |
| `frontend/lib/models/account.dart`, `clothing.dart`, `outfit.dart` | Typed response models |
| `frontend/lib/features/auth/{auth_controller,auth_screen}.dart` | Session and account flows |
| `frontend/lib/features/wardrobe/wardrobe_screen.dart` | Listing, filters, refresh and metadata sheet |
| `frontend/lib/features/outfits/outfits_screen.dart` | Weather controls, generation and score/piece cards |
| `frontend/lib/shared/widgets.dart` | Shared branding, headings and feedback panels |
| `frontend/test/{api_test,auth_test,app_test,resource_controller_test,fixtures}.dart` | 26 unit/widget tests and explicit test-only fixtures |
| `frontend/tool/{serve_web,test_serve_web}.py` | Local same-origin proxy and four security/forwarding tests |
| `frontend/android/`, `ios/`, `web/`, `windows/` | Flutter platform runners and standard launcher assets; native network/storage configuration and app names |
| `frontend/README.md`, `MILESTONE.md` | Setup, contracts, security, validation and delivery record |

Generated `build/`, caches and SDK files remain ignored. The SDK was downloaded into `.tools/flutter`, with no global PATH changes. The initial backend edits remain present: `outfit_routes.py`, `outfit_generation_service.py`, root `requirements.txt`, `backend/app/common/`, and the season/style/weather matching/provider services. No backend source was edited by this milestone.

## Commands and measured results

Commands below ran from `frontend/` unless stated otherwise. Flutter commands used `--no-version-check --suppress-analytics`; the SDK cache required execution outside the workspace sandbox. Initial sandbox cache/network failures were resolved and are not unresolved test failures.

| Command/check | Result |
| --- | --- |
| `git status --short`, branch/structure/route/schema/service inspection (workspace root) | Found an empty frontend; preserved existing backend work on `main` |
| `git clone --depth 1 --branch stable https://github.com/flutter/flutter.git .tools/flutter` (root) | Downloaded workspace-local SDK; Flutter 3.47.9, Dart 3.13.7 |
| `flutter create --no-pub --empty --platforms=android,ios,web,windows --project-name=wardrobe_wizzz --org=com.wardrobewizzz .` | Generated runners in the existing frontend; existing implementation files retained |
| `flutter pub get`; `flutter pub add cupertino_icons`; `dart format lib test` | Dependencies resolved/locked and code formatted |
| `dart fix --apply --code=curly_braces_in_flow_control_structures lib` | Resolved lint warnings exposed by formatting |
| `flutter analyze --no-pub` | **PASS: no issues found** |
| `flutter test --no-pub --reporter=expanded` | **PASS: 26 tests** |
| `..\backend\venv\Scripts\python.exe -m unittest discover -s tool -p 'test_*.py' -v` | **PASS: 4 tests**, no real backend/database access |
| `flutter build windows --debug --no-pub --dart-define=API_BASE_URL=http://127.0.0.1:8000 --dart-define=ALLOW_INSECURE_HTTP=true` | **PASS**, final executable at `build/windows/x64/runner/Debug/wardrobe_wizzz.exe` |
| `flutter build web --debug --no-pub --dart-define=API_BASE_URL=http://127.0.0.1:8080/api --dart-define=ALLOW_INSECURE_HTTP=true` | **PASS**, local preview assets at `build/web` |
| `flutter build web --release --no-pub --output=build/web-release-check --dart-define=API_BASE_URL=https://wardrobe.example.invalid` | **PASS**, including Wasm dry run; uses an intentionally non-routable verification address, not a deployed service |
| `flutter doctor -v` | Windows C++ and Chrome toolchains available; Android SDK missing; SDK is intentionally not on global PATH |
| Run `tool/serve_web.py` and HTTP probes | **PASS:** branded preview page HTTP 200, absent upstream HTTP 502, foreign Origin HTTP 403; preview server stopped after verification |
| Headless Chrome rendering of the local preview | Sign-in screen rendered and visually inspected; screenshot at `build/login-preview.png` |
| Read-only `GET http://127.0.0.1:8000/` | **Blocked:** connection actively refused; no backend listening there |

Early widget tests identified narrow-dropdown and enlarged-brand overflows plus test scroll timing problems. These were corrected and the complete suite passed afterward. Tests cover JSON/body/query contracts, authentication/expiry, storage failures including partial writes, sanitized errors, nullable values, weather input validation, request races/disposal, search, navigation, error retry, loading/empty states, and 360-pixel layouts with 1.5× text scaling.

## Limits and next steps

1. **Live integration verification remains outstanding.** No backend is listening at the default address, and no live credentials were supplied. All 26 Flutter tests use injected test HTTP/storage implementations. No live registration, database mutation, backend startup/import, schema creation or migration was performed. Starting the existing `app/main.py` invokes `Base.metadata.create_all()`; that needs a separately authorized environment. Once a backend is running, use [README.md](README.md) to sign in with an existing account and verify its real clothing and recommendations.
2. **Existing backend security blocks production exposure.** Authentication and database configuration contain hardcoded secrets; replace/rotate them and configure environment-managed values. Uploads lack authentication, ownership checks, content verification and size limits. Registration needs controlled duplicate-account errors/transaction rollback; login database sessions need reliable closure. These were preserved rather than mixed into the frontend milestone.
3. **Native device verification remains.** Windows was compiled; its real OS vault lifecycle still needs an interactive device check. Android needs its SDK/emulator. iOS requires macOS/Xcode and an HTTPS endpoint. Validate native secure storage, restore/expiry/sign-out and TLS on those devices before distribution.
4. **Production hosting and release configuration remain.** Use a real HTTPS API, explicit browser CORS or a production same-origin reverse proxy, release signing, final identifiers/icons, and CI checks. The local Python preview is not a deployment server. The backend has no token refresh/revocation contract; session expiry requires re-login.
5. **Next feature milestone:** safe clothing creation/editing with usable category/color metadata, followed by uploads only after backend upload security is fixed. Fresh empty wardrobes currently require existing backend tooling to populate clothing.

No files were deleted, no database was changed, and nothing was published, deployed, committed or pushed.
