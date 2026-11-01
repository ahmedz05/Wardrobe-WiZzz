# Wardrobe-WIZzz Flutter milestone

A working client for the **local FastAPI implementation**, with Material 3, a cream/forest design system, adaptive rail/bottom navigation, and explicit loading, retry, error and empty states. Tested with Flutter **3.47.9 / Dart 3.13.7** on Windows.

## Run locally

The SDK downloaded for this workspace is ignored at `../.tools/flutter`. It is not installed globally. From `frontend/`, use `..\.tools\flutter\bin\flutter.bat` in place of `flutter`, or temporarily add that SDK's `bin` directory to your terminal's PATH. No credentials belong in Dart defines.

```powershell
cd D:\Projects\Wardrobe-WIZzz\frontend
..\.tools\flutter\bin\flutter.bat --no-version-check --suppress-analytics pub get
..\.tools\flutter\bin\flutter.bat --no-version-check --suppress-analytics run -d windows --dart-define=API_BASE_URL=http://127.0.0.1:8000 --dart-define=ALLOW_INSECURE_HTTP=true
```

This connects to a backend **you already have running**; there is no development data fallback. No backend is started by the frontend. The current backend does **not** create tables on startup; database selection and JWT signing come from environment variables. For the authorized integration milestone, use `tools/run_backend.py --env-file backend/.env.integration` from the repository root with the existing Python virtual environment. That file must select the dedicated `wardrobe_wizzz_integration_20261030` database and a separate signing key. Never substitute a real-user database for test flows.

| Target | API address for local development |
| --- | --- |
| Windows | `http://127.0.0.1:8000` |
| Android emulator | `http://10.0.2.2:8000` |
| Physical Android device | Your development machine's LAN address, on a trusted network |
| iOS | An HTTPS endpoint; ATS exceptions have deliberately not been added |
| Browser | The same-origin preview below, or an HTTPS backend with explicitly configured CORS |

HTTP requires `--dart-define=ALLOW_INSECURE_HTTP=true` and a **non-release** build. Android permits cleartext only in its debug manifest. Release builds require an explicit HTTPS `API_BASE_URL`; insecure or missing configuration displays a configuration screen. The default non-release address is the Android emulator host on Android, otherwise loopback. API prefixes such as `https://example.com/api` are supported.

## Browser preview without changing the backend

The existing FastAPI app does not configure CORS. The small standard-library preview server serves `build/web`, forwards `/api/` and `/uploads/` to the real backend, and binds **only** to loopback. It checks Host/Origin, restricts endpoint/method scope, limits request size, does not follow redirects, and avoids logging sensitive request details. It never imports the backend, accesses the database, implements uploads, or supplies successful fallback responses. It is a local development utility, not a production web server.

```powershell
..\.tools\flutter\bin\flutter.bat --no-version-check --suppress-analytics build web --debug --dart-define=API_BASE_URL=http://127.0.0.1:8080/api --dart-define=ALLOW_INSECURE_HTTP=true
..\backend\venv\Scripts\python.exe tool/serve_web.py --api http://127.0.0.1:8000
```

Open `http://127.0.0.1:8080`. Stop the server with Ctrl+C. A missing backend produces a real error. Change the compile-time URL too if you change the preview port. Any Python 3.10+ interpreter can run the server; the commands use the repository's existing Python virtual environment.

## Implemented contracts

| Action | Existing endpoint | Handling |
| --- | --- | --- |
| Registration | `POST /register` | JSON `username`, `email`, `password`; reads account response, then asks for sign-in |
| Login | `POST /login` | JSON `email`, `password`; reads `access_token`, `token_type`; never OAuth form data |
| Validate/restore session | `GET /me` | Bearer token; reads `id`, `username`, `email` |
| Wardrobe | `GET /clothing` | Typed clothing array; active pieces, local search/favorites, pull-to-refresh, metadata details |
| Recommendations | `GET /outfits/generate` | `limit`, `include_layers`, and one optional weather source; reads nested `items.top/bottom/shoes/layer`, compatibility/weather scores and returned weather context |

Contracts were inspected in `backend/app/routes/{user,clothing,outfit}_routes.py`, `backend/app/schemas/{user,clothing}_schema.py`, and `backend/app/services/{outfit_generation,weather_provider}_service.py`, including the pre-existing uncommitted weather work. Outfit generation may return a legitimate 400 for missing usable tops/bottoms/shoes; this is shown as an actionable error. No garment names, outfits, weather observations or successful API responses are fabricated in application code. Explicit test fixtures live only in `test/`.

## Architecture and security

- `lib/core/`: validated configuration, JSON HTTP transport, secure token abstraction, reusable request state, theme.
- `lib/data/`: repository translating the exact backend contracts; exclusive, validated weather options.
- `lib/models/`: typed accounts, clothing, outfit pieces, scores and weather results.
- `lib/features/`: authentication/session controller and independent wardrobe/outfit screens. Flutter `ChangeNotifier` and `AnimatedBuilder` provide state management with injectable HTTP/storage dependencies.
- `lib/shared/`: common branding, feedback and empty/error panels. Screens dispose controllers; request generations ignore stale results and responses after disposal.
- Native tokens use `flutter_secure_storage`; the key is scoped to the normalized API URL. iOS uses device-only, unlocked Keychain access. Android backup is disabled; iOS entitlements are configured. Storage failures are visible and never fall back to plain preferences.
- Browsers use **memory only**, losing the session on reload. Passwords are not persisted by the app. Tokens never appear in URLs or logs. Bearer requests reject redirects; a late 401 cannot expire a newer token. Current-session 401 clears storage and returns to sign-in. Transient restore failures preserve the saved token for an explicit retry.
- There is no refresh/revoke endpoint in the current backend. Expiry requires sign-in again; sign-out clears this device's session and does not revoke a copied token server-side.
- Image display is restricted to same-origin `/uploads/` URLs and uses placeholders on failure. The Phase 1 media containment fix now returns **404** for these legacy image URLs and **503** for uploads, before multipart parsing. Existing photos are preserved on disk but unavailable through the API until trusted ownership and private storage are implemented. There are **no upload, camera, location permission, garment mutation or delete flows** in this milestone. The placeholder behavior was verified against a real image 404.
- Android release signing has no debug-key fallback. Distribution signing, identifiers and branding assets still need release configuration.

## Validate

```powershell
..\.tools\flutter\bin\flutter.bat --no-version-check --suppress-analytics analyze --no-pub
..\.tools\flutter\bin\flutter.bat --no-version-check --suppress-analytics test --no-pub --reporter=expanded
..\backend\venv\Scripts\python.exe -m unittest discover -s tool -p 'test_*.py' -v
```

Unit/widget tests use an injected HTTP client, never the real database. They cover route/body/query contracts, nullable metadata, exclusivity and bounds of weather inputs, sanitized failures, timeouts, redirect rejection, token restoration/expiry/storage failures, request races, screen disposal, search, recommendations, sign-out, empty/error/loading states and responsive layouts. Preview proxy tests check real forwarding semantics and its security boundaries with mocked upstream I/O.

See [MILESTONE.md](MILESTONE.md) for commands, measured results, existing backend blockers and next steps. Lockfile changes belong in version control for this application.

## Historical integration verification

Earlier HTTP/PostgreSQL/browser verification is recorded in
[the integration report](../docs/INTEGRATION_MILESTONE.md). The fixture-writing
HTTP/browser runners and database bootstrap are excluded from this publication.
Their old API checks happened after the first write or relied on stale evidence;
least-privilege roles and pre-write server attestation still require review.
Do not use historical runner commands as current setup instructions.

The published launcher reads configuration through a database-independent helper.
Unit/widget, mocked proxy, and configuration-guard tests remain available without
existing PostgreSQL databases. No safe write-based end-to-end runner is claimed.
The preview supports separate ports and `--build-dir` when needed.
