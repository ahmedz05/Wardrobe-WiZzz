# Phase 1 baseline review and first security checkpoint

Publication note: this is a historical milestone record. The write runners and
bootstrap named below are excluded from this checkpoint; commands referring to
`tools/check_integration.py`, `tools/integration_database.py`, or
`tools/browser/verify_integration.mjs` are not supported publication setup steps.
Safe configuration/guard tests are separate and do not contact existing databases.

Reviewed 2026-10-30 against the authoritative local workspace. No staging, commit,
push, deployment, history rewrite, schema change or destructive database operation
was performed. Existing work was preserved. This pass implements one boundary:
**fail-closed containment of legacy media uploads and public photograph serving**.

## Baseline inventory and checkpoint structure

The pre-change inventory covered 227 nonignored repository files, including all
151 untracked files; nothing was staged. Tracked diffs, new code/tests/tools,
configuration, source/secret markers and native/generated file paths were inspected.
The security-critical paths were reviewed in detail. This is not a declaration that
all dependencies, native build targets or every recommendation edge case are certified.

Recommended future checkpoints, in dependency order, after explicit approval:

| # | Proposed checkpoint | Files/scope and review boundary |
| --- | --- | --- |
| 1 | `chore(dev): establish reviewed development toolkit` | `.gitignore`; `AGENTS.md` and engineering/toolkit/roadmap guidance; `tools/install_node.ps1`, `configure_mcp.py`, skill installer/verifiers/manifests/source licenses; browser package/lockfile, MCP client and verification. Include scripts and provenance, not SDK/cache binaries or copies of personal Codex configuration. |
| 2 | `fix(backend): configure runtime and close auth sessions` | Environment-driven `database.py`/`auth_service.py`, `.env.example`, account/auth dependency/service/route changes, account/startup tests, the earlier startup `create_all` removal, pinned requirements and local backend launcher. Keep actual env files out. The current media changes to `main.py` belong to checkpoint 6. |
| 3 | `feat(outfits): add weather-aware recommendation scoring` | Existing uncommitted `outfit_routes.py`, `outfit_generation_service.py`, season/style/weather matching and provider services. This substantial pre-existing logic change is separate from auth/security. Happy-path integration passes; dedicated deterministic scoring edge-case tests remain desirable before treating it as fully reviewed for release. |
| 4 | `feat(flutter): deliver authenticated wardrobe client` | Flutter `lib/`, tests, pubspec/lockfile, lint settings, native/web scaffolding, icons, platform secure-storage/release settings, original preview/proxy utility and delivery docs. Keep native verification/signing limitations explicit; no debug-key release fallback. |
| 5 | `test(integration): verify real Flutter FastAPI flows` | HTTP/database isolation runner and safety tests, Playwright MCP flow, integration database helper and `docs/INTEGRATION_MILESTONE.md`; related README/milestone updates. Label mocked, SQLite, PostgreSQL and actual browser results separately. |
| 6 | `fix(security): contain unsafe legacy wardrobe media` | This pass: upload 503 without body parsing, remove public mount, six regression tests, media-specific integration mode and isolated ports/build support, updated security/frontend guidance and this report. |

Shared files such as `main.py`, requirements, AGENTS/roadmap/README and browser tools
need deliberate hunk selection when staging is later authorized. Documents should
travel with the milestone they describe. Verify each proposed checkpoint can run its
relevant checks; this table is a recommendation, not an executed history split. Do not
use a blanket add/commit to collect SDKs, private fixtures or unfinished helpers.

`backend/app/common/` is **unfinished, unused scaffolding**, not a dependency of the
verified milestones: its CRUD/response/enums/constants have no production imports.
The apparent 10 MB upload constant is not enforcement. Enum terminology also differs
from some current free-text metadata. Preserve these files and leave them out of a
completed-feature checkpoint until their intended use is reviewed; do not delete them.

## Secrets, artifacts and incomplete work

- Current backend runtime credentials/signing come from environment variables. The
  ignored local env files, downloaded SDKs, browser `node_modules`, Flutter build/cache
  output, browser artifacts and local fixture/evidence folders are excluded by Git.
  No executable/archive/log/database/keystore/cache artifact appeared among candidate
  tracked/untracked files. No files were discarded.
- A location-only secret scan found no provider token/private-key markers in current
  candidate files. Hits in `.env.example`, `backend/alembic.ini`, a URL rejection test
  and an incorrect-password test were classified as placeholders/fixtures. The Alembic
  URL is the standard template; `alembic/env.py` replaces it using the runtime URL.
  Heuristic scans cannot prove the absence of every secret.
- **Historical credentials remain a publication blocker.** HEAD contains a database
  credential literal and an old JWT signing literal. The database password still
  matches the local environment; the current local signing key differs and is at
  least 32 characters. Rotate/revoke exposed credentials before publication. No
  credential value is reproduced here, and no rotation or history rewrite was attempted.
  An initial diff displayed historical literals in tool output; subsequent scans
  returned only locations/classification. Treat those old values as exposed.
- Existing ignored working-diff backups can contain historical literals. Keep them
  private/ignored; do not attach raw patches or env/config backups to a PR/report.
- Flutter's checked-in scaffolding, `.metadata`, platform assets and Windows generated
  plugin registrants are expected project sources. Keep pubspec and npm lockfiles;
  generated build outputs, ephemeral registrants/Pods/Gradle caches remain excluded.
- The root README's computer-vision/AI feature list is aspirational. The verified
  baseline is wardrobe management and rule/weather-based recommendations, not trained
  recognition models. Keep these descriptions distinct in release documentation.
- No accidental `frontend/frontend` project, CI secret file or added telemetry service
  was found. Native device/vault testing, final release identifiers/signing and hosting
  remain incomplete. Several earlier milestone notes are historical, not release claims.
- Tools are local development utilities: the integration helper can explicitly create
  the separately approved test DB/schema; no initializer was run here. MCP origin
  lists/roots are not a security sandbox, and direct MCP advertisement remains an
  existing client limitation. No tools were reinstalled or permissions broadened.

## Confirmed backend security findings

| Priority | Finding and local evidence | Disposition |
| --- | --- | --- |
| Critical | Legacy `POST /upload/` required no login, accepted nonimage bytes with a permitted extension, read the full stream and wrote a file. `/uploads` used a public StaticFiles mount without ownership. Synthetic tests reproduced public GET/HEAD 200 and range 206. | **Contained in this pass**; see below. |
| High | Historical DB credential remains usable locally. Removing a source literal does not invalidate its earlier Git versions. | Rotate before any publishing; separate operational approval/work. |
| High | Color/material/brand catalog mutations lack authentication/administrator policy. An anonymous `POST /colors/` succeeded in isolated in-memory SQLite; local routes expose other mutations similarly. These shared records affect multiple users' recommendations. | Open; no catalog policy or schema change mixed into media work. |
| Medium | `verify_token()` verifies an expiration when present but does not require it. A correctly signed token without `exp` reached `/me` with HTTP 200 in isolated tests. Existing algorithm restriction and malformed user-id checks are useful but incomplete. | Open; possession of the signing key is needed to mint such a token. Require claims in a later auth fix. |
| Medium | Login issues a token to inactive users (200), while the authenticated dependency subsequently rejects `/me` (401). | Open; consistent active-user rejection at login needs regression tests. |
| Medium | Registration accepts empty username, malformed email and a one-character password (200 in isolated tests). Clothing strings, image references, numeric metadata and relationship IDs lack comprehensive bounds/constraints. | Open; server-side validation must enforce policy independently of Flutter. |
| Medium | Account/clothing/auth sessions use DI/finally; duplicate registration rolls back. Category helpers manually close only on success and can leak sessions on exceptions. Other mutation services commit without consistently translating DB errors/rolling back before reuse. | Open; isolate transaction/error-handling improvements. |
| Medium | No application rate limiter was found for public auth or expensive recommendations/weather calls. Generation enumerates all candidate combinations before slicing results; `limit` is not a work budget. | Open; measure and bound work/abuse without introducing unnecessary infrastructure. |
| Medium | Weather provider code catches HTTP failures but not malformed JSON/type/missing-key cases. Error responses/field validation and outage behavior need more targeted tests. | Open; a live 502 occurred here, followed by a successful direct provider check and successful retry. No response was faked. |

Positive isolation evidence: clothing list/update/delete lookup paths filter by the
authenticated user; outfit generation filters by owner and active status. Prior and
current integration checks verify another account cannot list/access the first
wardrobe. This is evidence for these paths, not every possible authorization policy.

Auth characterizations above used new in-memory SQLite only. They created no real
accounts, sent no email and changed no PostgreSQL/source records. Broad security
coverage remains missing for mandatory claims, inactive login, input bounds, catalog
permissions, error rollback, rate limits and a future private media lifecycle.

## Implemented improvement and compatibility

`backend/app/routes/upload_routes.py` now returns HTTP **503**, with `Cache-Control:
no-store`, for all clients. It has no `File`/`UploadFile` parameter, so multipart
parsing/spooling does not happen before rejection. A direct ASGI test verifies no
request-body reads even with a synthetic 1 GiB declared length; no huge body is sent.

`backend/app/main.py` no longer mounts `/uploads` or initializes its directory. Existing
files are not moved, deleted, read or assigned guessed ownership. Legacy image GET,
HEAD and range requests return **404**, regardless of a bearer header. The old save
helper is retained as unreachable legacy code; it must not be enabled as-is.

This deliberately makes old wardrobe image URLs unavailable, including to legitimate
clients, until a trusted upload ownership/private retrieval design exists. It does
not implement an authenticated upload feature. Client-supplied `image_url` cannot
establish ownership, so it was not used to grant access to legacy files. Future secure
media needs reviewed metadata/migrations, per-owner access, size/decode limits,
validation/re-encoding, retention and negative authorization tests. No migration is
authorized or implemented by this containment fix.

Flutter has no upload flow and already renders a placeholder when an image fails.
The full real browser flow used a synthetic legacy image reference, observed its
actual 404, and retained usable wardrobe cards, search, outfits, login and sign-out.
Application Dart code/dependencies did not need a change. A separate preview build
and API used 8081/8001 so existing servers and web build were preserved.

The approach follows OWASP guidance to separate private storage, authorization,
content checks and upload limits, rather than treating an extension/UUID as protection:
[OWASP File Upload Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html).

## Verification

| Check | Result |
| --- | --- |
| New media regressions before fix | Six methods failed as expected (nine failing subcases); synthetic uploads/public retrieval demonstrated the defect. |
| Complete backend suite after fix | **14 passed**, including six new media methods. |
| Flutter analysis/tests | **No issues; 26 passed**. |
| Proxy tests and integration safety guards | **4 + 4 passed**. |
| Real HTTP/PostgreSQL | **39 checks passed** against patched API 8001, including upload 503, image 404, ownership, auth and manual/live weather. |
| Playwright MCP | **13 checks passed**, including real legacy-image 404 fallback, desktop/mobile navigation, provider weather and session rejection/sign-out. |
| Separate Flutter web debug build | **Passed**, under ignored security evidence directory. |
| Python/JavaScript syntax and diff whitespace | **Passed**. |
| Preservation | Source schema/row counts match read-only baseline; one pre-existing uploaded file's size/mtime unchanged; no existing files removed; index remains unstaged. |

The first HTTP integration attempt failed only its live weather assertion with HTTP
502. The failed evidence is retained. A direct public provider check succeeded, then
the complete HTTP/browser reruns passed. Backend tests retain an existing
Starlette/httpx deprecation warning; dependencies were not upgraded to hide it.

Evidence: `.tools/security/baseline-20261030T021908Z/` contains initial hashes,
location-only secret scan/classification and isolated security characterizations.
`.tools/integration/run-20261030T022647Z-a30e6d/` contains successful HTTP/browser
reports and screenshots; the preceding run retains the 502. No real photo was opened
for testing; existing-file preservation used metadata only. SQLite tests use synthetic
temporary files; PostgreSQL flow fixtures remain only in the approved integration DB.

Commands used, from the named directories:

```powershell
# backend/
venv\Scripts\python.exe -B -m unittest tests.test_media_security -v
venv\Scripts\python.exe -B -m unittest discover -s tests -v
# frontend/
..\.tools\flutter\bin\flutter.bat --no-version-check --suppress-analytics analyze --no-pub
..\.tools\flutter\bin\flutter.bat --no-version-check --suppress-analytics test --no-pub --reporter=expanded
# repository root; isolated API and separate preview already started on 8001/8081
backend\venv\Scripts\python.exe -B -m unittest discover -s tools -p test_check_integration.py -v
backend\venv\Scripts\python.exe -B -m unittest discover -s frontend/tool -p 'test_*.py' -v
backend\venv\Scripts\python.exe -B tools/check_integration.py --run --api http://127.0.0.1:8001 --verify-media-disabled
$runtime = Get-Content -LiteralPath .tools/node/runtime.json | ConvertFrom-Json
& (Join-Path $runtime.directory 'node.exe') tools/browser/verify_integration.mjs
backend\venv\Scripts\python.exe -B tools/integration_database.py --verify-source
git diff --check
```

The separate debug build used `API_BASE_URL=http://127.0.0.1:8081/api`, explicit
development HTTP and `--output=<security-evidence>/web`. The preview's new optional
`--build-dir` points there; default preview behavior remains unchanged. MCP/HTTP tools
allow only the two explicit loopback port pairs; no remote-target permission was added.

Files changed for this checkpoint: `backend/app/main.py`, `backend/app/routes/upload_routes.py`,
`backend/tests/test_media_security.py`, `frontend/tool/serve_web.py`, `tools/check_integration.py`,
`tools/browser/mcp_client.mjs`, `tools/browser/verify_integration.mjs`, `AGENTS.md`,
`docs/ROADMAP.md`, `frontend/README.md` and this report. Earlier changes are preserved
and assigned separately above.

## Next action and deployment boundary

Review the checkpoint plan and this containment change. Before publishing any history,
rotate the historical DB credential and decide separately how to address existing Git
history; no reset/force-push is authorized. The next code boundary should restrict
shared-catalog mutations, after reviewing who may administer global records. Do not
invent an administrator role or migration implicitly. Mandatory JWT expiry and
inactive-user login rejection should follow as separate tested auth work. Catalog
authorization and a secure private media lifecycle remain release blockers.

Existing development processes on 8000/8080 were left untouched and may still hold
the old in-memory application. Source changes do not update running processes, external
static servers or already-cached/downloaded images. Reloading the intended runtime
and checking any proxy/CDN media exposure are required before claiming an operational
privacy fix. No deployment/restart of an existing runtime occurred here.
The two temporary test processes on 8001/8081 were stopped after verification; their
build, reports, fixtures and screenshots were retained. Original 8000/8080 processes
were not stopped or changed.

Stop after this tested improvement. No other security issue, broad refactor, model
development or release action was implemented.
