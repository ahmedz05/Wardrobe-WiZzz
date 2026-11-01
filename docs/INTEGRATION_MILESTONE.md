# Flutter-FastAPI integration — 2026-10-30

Publication note: this is a historical milestone record. The write runners and
bootstrap named below are excluded from this checkpoint; commands referring to
`tools/check_integration.py`, `tools/integration_database.py`, or
`tools/browser/verify_integration.mjs` are not supported publication setup steps.
Safe configuration/guard tests are separate and do not contact existing databases.

The existing Flutter web app completed real registration, login, wardrobe retrieval
and weather-aware recommendations through the preview proxy, FastAPI and isolated
PostgreSQL. No successful responses, outfits or weather observations were mocked in
the integration checks. This is local development verification, not production or
native-device certification. Stop for user review before the next product milestone.

## Tool activation

| Tool | Observed status |
| --- | --- |
| Superpowers 7.0.1 | Installed skill files read directly; systematic debugging and verification guidance used. Automatic skill advertisement remains absent. |
| Taste | `design-taste-frontend` advertised and accessible. No redesign or design milestone started. |
| Context7 | CLI reports enabled with the configured HTTP endpoint. Fresh anonymous library lookup and documentation query passed through the existing MCP SDK bridge. |
| Playwright MCP 0.0.83 | CLI reports enabled with valid Node/package paths. Discovery returned 25 tools; isolated Chrome and actual app flows succeeded through the existing MCP SDK bridge. |

**Unresolved direct activation limitation:** Context7 and Playwright are absent from
this running chat's direct tool catalog. Local registration/server operation passed;
no invalid path, disabled server or required authentication was found. The precise
host-side exposure cause remains unresolved. Inspect loading diagnostics in the
intended local client; a working bridge is not proof of direct activation. No tools
were reinstalled/upgraded and Codex configuration was not changed speculatively.
See the official [MCP configuration/surface guide](https://learn.chatgpt.com/docs/extend/mcp).

The browser runner used supported MCP click/type/evaluate/wait/resize/screenshot
operations. It did not use the arbitrary server-code tool. An initial probe requested
an unavailable `browser_run_code` name; discovery identified the actual supported
operations before the flow was implemented.

## Isolation and preservation

- Read-only connections verified distinct source and integration database names/OIDs.
  Only `wardrobe_wizzz_integration_20261030` received test writes; `wardrobe_wizzz`
  remained read-only. No database/schema creation, migration, deletion or reset occurred.
- Signing keys are separate. A real registration was found in the integration DB;
  the running API's JWT verified using the integration key before further test writes.
- Existing loopback API 8000 uses `.env.integration`; existing preview 8080 proxies to
  it. Both processes were reused. An extra API launch exited because 8000 was occupied;
  its owner/configuration were inspected before testing. Existing servers were not stopped.
- Source schema and row counts match the original baseline and the current run's
  snapshot after all HTTP/browser activity. No personal source row contents were exported.
- Final test DB inventory: **11 synthetic `.test` accounts, 36 synthetic garments,
  zero non-test accounts/garments, zero images**. Counts include retained fixtures from
  browser-harness development attempts. No cleanup/deletion was performed.
- **101 existing backend/client implementation and test files** match their pre-task
  SHA-256 hashes. Existing uncommitted code/functionality was preserved. No confirmed
  product defect required an implementation change.

Database separation uses explicit test configuration and guards; this task did not
provision a least-privilege PostgreSQL role or separately secured server.

## Contracts and behavior verified

Actual route/schema files and the running OpenAPI document agree with the client:

| Endpoint | Verified behavior |
| --- | --- |
| `POST /register` | JSON username/email/password; account object, HTTP 200. Duplicate returns 409. Registration returns no token. |
| `POST /login` | JSON email/password; bearer token. Incorrect credentials return 401. |
| `GET /me` | Bearer authorization; account matches registration. |
| `GET /clothing` | Owned active items; new account empty; populated account returns exact fixture IDs. Another account cannot list/access those items. |
| `GET /outfits/generate` | Limit/layer options, exclusive weather sources, nested pieces/scores, returned weather context and provider. Missing usable pieces returns 400; invalid bounds returns 422. |

Category/color reference fixtures were inserted directly into the isolated DB because
their creation endpoints do not exist. Accounts and garments used actual HTTP routes.
No upload/UI mutation feature was introduced. Missing images retain honest placeholders.

Manual cold/hot weather affected actual suitability scores; disabling layers excluded
layers. Live Cairo weather returned HTTP 200 with Open-Meteo provenance and outfits.
Browser storage inspection found no persisted JWT. An actual expired JWT was rejected
over HTTP. The browser 401 check replaced one request's bearer header with an invalid
token and forwarded it to the real API; the real rejection cleared the UI session.
No fake 401 response was supplied. Native storage behavior was reviewed in code/tests,
not certified on a physical device.

## Results

| Check | Result |
| --- | --- |
| Backend route/auth/startup tests | **8 passed**, isolated SQLite; separate from PostgreSQL checks. |
| Flutter analysis | **No issues found**. |
| Flutter unit/widget tests | **26 passed**, injected HTTP/storage; separate from browser checks. |
| Preview proxy tests | **4 passed**, mocked upstream I/O and forwarding/security boundaries. |
| New integration safety tests | **4 passed**; reject real/unapproved DB targets, remote hosts and shared signing keys before connection. |
| Real HTTP/PostgreSQL | **37 assertions passed**, including ownership, expiry, weather validation/scoring and live provider. |
| Playwright MCP browser | **12 checks passed**, desktop 1280x1000 and mobile browser viewport 390x844. |
| Flutter debug web build | **Passed**; preview HTTP 200. |
| Python/JavaScript syntax; `git diff --check` | **Passed**. |

Browser coverage: registration, incorrect login, login plus `/me`, honest empty
wardrobe, refresh/search, manual weather, actual city weather, server-rejected session,
reload after invalidation, mobile login/navigation and sign-out. Desktop/mobile
screenshots were inspected. A mobile browser viewport is not an Android/iOS device.

Failures during runner development were investigated and corrected: the first backend
test invocation used the wrong working directory. Browser automation needed Flutter
focus handoff, hint-dependent accessible names, tab-position labels, animation/frame
synchronization, grouped card labels and an unambiguous mobile Account-tab selector.
The final whole-flow run passed. These failures did not establish a product bug, so
no unrelated app changes/refactor were introduced.

## Evidence

Ignored local evidence directory: `.tools/integration/run-20261030T020535Z-58be98/`:

- `http-verification.json`: 37 assertions, provider HTTP 200 and source comparison.
- `browser-verification.json`: successful 12-check flow and sanitized request statuses.
- `browser-verification-*.json`: retained troubleshooting attempts.
- `api-contracts.json`: live OpenAPI operation/schema projection.
- `source-before.json`, `final-preservation.json`: isolation/preservation evidence.
- `outfits-desktop.png`, `wardrobe-mobile.png`: actual UI with synthetic fixtures.

Pre-task working-tree hashes/diffs are retained in
`.tools/integration/run-20261030T015303Z/`. Reports contain no signing keys, passwords,
bearer tokens or source user records. Earlier browser attempts are retained in those
local run folders. No real garment photos were loaded or transmitted.

## Commands

From `backend/`:

```powershell
venv\Scripts\python.exe -B -m unittest discover -s tests -v
```

From `frontend/`:

```powershell
..\.tools\flutter\bin\flutter.bat --no-version-check --suppress-analytics analyze --no-pub
..\.tools\flutter\bin\flutter.bat --no-version-check --suppress-analytics test --no-pub --reporter=expanded
..\.tools\flutter\bin\flutter.bat --no-version-check --suppress-analytics build web --debug --no-pub --dart-define=API_BASE_URL=http://127.0.0.1:8080/api --dart-define=ALLOW_INSECURE_HTTP=true
```

From the repository root with the verified integration API/preview running:

```powershell
backend\venv\Scripts\python.exe -B -m unittest discover -s tools -p test_check_integration.py -v
backend\venv\Scripts\python.exe -B -m unittest discover -s frontend/tool -p 'test_*.py' -v
backend\venv\Scripts\python.exe -B tools/check_integration.py --run
$runtime = Get-Content -LiteralPath .tools/node/runtime.json | ConvertFrom-Json
& (Join-Path $runtime.directory 'node.exe') tools/browser/verify_integration.mjs
backend\venv\Scripts\python.exe -B tools/integration_database.py --verify-source
git diff --check
```

Each HTTP run creates an ignored evidence folder; the browser runner requires its
successful isolation/HTTP evidence. Re-running deliberately appends new synthetic
data without resetting fixtures. Live weather depends on current provider/network
availability; a past pass does not guarantee a future provider response.

## Changed files and stop boundary

Added `tools/check_integration.py`, `tools/test_check_integration.py`, and
`tools/browser/verify_integration.mjs`. Updated `AGENTS.md`, `frontend/README.md`,
`frontend/MILESTONE.md` and `docs/ROADMAP.md`; added this report. Application source,
installed dependencies and Codex configuration were unchanged.

Remaining production concerns: existing insecure upload/public-image serving,
broader backend/auth validation, refresh/revocation design, dependency review, HTTPS
hosting and native device/vault verification. Backend tests retain an existing
Starlette/httpx deprecation warning; dependencies were not upgraded here. Taste's
premium UI assessment remains pending.

Stop for user review before backend refactoring, recommendation-engine changes,
AI training or deployment. No commit, push, deployment, destructive database action
or unrelated feature work was performed.
