# Phase 1: catalog authorization and integration database review

Publication note: this is a historical milestone record. The write runners and
bootstrap named below are excluded from this checkpoint; commands referring to
`tools/check_integration.py`, `tools/integration_database.py`, or
`tools/browser/verify_integration.mjs` are not supported publication setup steps.
Safe configuration/guard tests are separate and do not contact existing databases.

Completed 2026-10-30 against local source. The user approved temporary default-deny
after [the authorization review](PHASE1_CATALOG_AUTHORIZATION_REVIEW.md). This report
distinguishes updated-source tests from the existing, older server on port 8000.
No existing PostgreSQL data/schema, credentials, running servers or Git index changed.

## Implemented access policy

One dependency, `require_catalog_write_access`, first resolves the existing
`get_current_user`, then always raises 403. There is no administrator success path,
identity allowlist, role claim bypass or migration. It is attached to these seven
mutation operations only:

| Operation | Anonymous | Invalid / expired credentials | Active ordinary user |
| --- | --- | --- | --- |
| `POST /brands/` | 401 | 401 | 403 |
| `POST /colors/` | 401 | 401 | 403 |
| `PUT /colors/{color_id}` | 401 | 401 | 403 |
| `DELETE /colors/{color_id}` | 401 | 401 | 403 |
| `POST /materials/` | 401 | 401 | 403 |
| `PUT /materials/{material_id}` | 401 | 401 | 403 |
| `DELETE /materials/{material_id}` | 401 | 401 | 403 |

Regression tests also cover incorrectly signed tokens, inactive/nonexistent users
(401), and active-user tokens carrying `admin`, `is_admin` and `role` claims (403).
Every denied operation checks that the in-memory database contents remain unchanged,
including shared references and owned clothing. Tests enumerate registered mutation
routes so an unaccounted-for catalog operation cannot silently escape test coverage.

The ten existing catalog GET operations remain public, including with an irrelevant
invalid bearer header; authenticated reads and missing-record 404s are preserved.
Owner wardrobe creation/list/update/delete, cross-user denial and fashion-only/cold/
hot weather outfit scoring pass against the real routes and ORM. Existing media
containment tests remain green. No Flutter contract or implementation changed.

Compatibility impact: **all catalog HTTP writers are intentionally blocked** until a
reviewed privilege model exists. The current Flutter client has no catalog mutations.
Wardrobe reference selection is separate from modifying catalog records. Future
catalog privileges and in-use reference deletion rules require separate review.

## Additional database: actual identity and purpose

On the configured local PostgreSQL server, port 5432, the exact name supplied by the
user, `Wardrobe_Wizzz_Integeration_20102630`, does **not** exist, including a
case-insensitive name check. The two Wardrobe-related databases actually found are:

| Database | OID | Purpose |
| --- | --- | --- |
| `wardrobe_wizzz` | 16388 | Original development data; read-only during this work |
| `wardrobe_wizzz_integration_20261030` | 24581 | Existing isolated Flutter/FastAPI test fixtures |

This does not establish what another PostgreSQL instance or a GUI display label
might contain. Do not silently rename or treat a similar spelling as an alias.

The canonical integration name matches the previous approved integration setup:
`tools/integration_database.py` defines `TEST_DATABASE` and contains the explicit
creation/bootstrap logic. Existing integration reports and matching fixtures support
its provenance as the prior Flutter/FastAPI test database. PostgreSQL's database
catalog alone does not provide a creation audit trail or timestamp proving who ran it.
No bootstrap or initialization command was run in this milestone.

References and dependencies:

- Ignored `backend/.env.local` selects the original database; ignored
  `backend/.env.integration` selects the canonical integration database. Values were
  parsed in memory; no credentials or tokens were printed or copied into this report.
- `tools/integration_database.py` owns the literal name and read-only snapshot helper.
  `tools/check_integration.py` imports it, validates target configuration/OIDs, seeds
  reference fixtures and runs HTTP account/wardrobe/recommendation checks.
- `tools/run_backend.py --env-file backend/.env.integration` loads test configuration.
  Its default env file is `.env.local`, so callers must select the intended target.
- `tools/browser/verify_integration.mjs` relies on prior HTTP evidence and the matching
  API/preview origins; its registration and garment fixtures still depend on the
  integration API/database. It does not independently attest the current server's DB.
- AGENTS.md and `docs/INTEGRATION_MILESTONE.md` document the approved name. No script or
  configuration was found referencing the user-supplied misspelling. This report
  records that spelling only to explain the investigation.

Current write-based HTTP/browser tests still depend on this database. The backend
unit/route tests, Flutter unit/widget tests and integration guard/proxy tests do not.

## Contents classification and preservation

Inspection used PostgreSQL connections with `default_transaction_read_only=on`,
verified by `SHOW transaction_read_only`. Only catalog/schema queries and aggregate
classification/count queries were reported; no account details, hashes, photographs
or private garment content were displayed.

| Canonical integration table | Rows | Classification |
| --- | --- | --- |
| users | 16 | All match the HTTP/other/browser generated-name patterns and `example.test` addresses |
| clothing | 48 | All match the four known synthetic garment payloads, synthetic owners and expected references/default metadata |
| categories | 4 | Exact integration reference set |
| subcategories | 4 | Exact integration reference set |
| colors | 1 | Known neutral-black integration fixture |
| brands / materials / user_profiles | 0 each | Empty |

There are no unclassified account or garment rows. Image references are absent or
the known synthetic disabled-media probe path. **The inspected data is classified as
synthetic fixtures**, based on exact fixture attributes and generated identity
patterns; this is not an independent audit history proving every historical write.
No `alembic_version` table exists in this integration schema, consistent with the
earlier metadata bootstrap. Future migration testing must use an explicitly approved
disposable target rather than changing this retained evidence database automatically.

Source and integration schema/row-count snapshots matched before and after review.
The original development database also matches the pre-integration read-only baseline.
Neither database was renamed, recreated, deleted, seeded or otherwise modified here.

## Isolation assessment: separate databases, incomplete enforcement

Controls already present and verified:

- Distinct database names and PostgreSQL OIDs; configuration selects the intended
  canonical integration target. Source and integration JWT signing keys differ.
- HTTP runner rejects the source DB as target, an unapproved test DB, a remote host
  and identical signing keys before connecting. Four existing guard tests pass.
- It additionally checks connected database names/OIDs, restricts loopback API URLs,
  guards direct reference seeding and compares source schema/counts after requests.

**These are not complete protection against accidental source writes.** Both local
configurations use the same PostgreSQL superuser identity. It can create databases
and roles and can connect to/write the source database. Naming and separate JWT keys
do not establish least privilege.

`tools/check_integration.py` validates the *configured* target before HTTP requests,
but performs `POST /register` before proving where the *running API* writes. A server
accidentally connected to the original DB could therefore change it before the runner
detects the problem. Its source comparison is detection after the write, not
prevention. The browser runner can also rely on stale HTTP evidence while a server's
configuration has changed. No such write-based runner was executed during this review.

`tools/integration_database.py` can create the integration database even without
`--initialize` (that flag controls schema initialization only). It must not be used
as a generic read-only inspection command. Only its `--verify-source` branch was run.
These risks remain documented for the next focused integration-safety improvement;
no credential/role/bootstrap redesign was mixed into catalog authorization.

## Recommended database lifecycle policy

1. Retain `wardrobe_wizzz_integration_20261030` for the reviewed milestone. Do not
   rename it or create a similarly spelled replacement. For future campaigns, use
   one exact configured/allowlisted name: `wardrobe_wizzz_integration_<YYYYMMDD>`.
   Name checks are one control, not sufficient authorization for writes or cleanup.
2. Before future write-based runs, provision a separately approved non-superuser test
   role with no write privileges on the original DB and no role/database creation
   privileges, or use a separate disposable PostgreSQL instance. Verify effective
   privileges, including inherited/PUBLIC grants; different usernames alone do not
   prove isolation. Role/grant/credential changes require separate approval.
3. Launch an owned test API on a dedicated free loopback port with explicitly validated
   integration configuration. Establish its database identity and least-privilege
   boundary **before any HTTP mutation**. Check source/target names, server identity,
   OIDs and separate JWT keys. Refuse an arbitrary pre-existing server or stale browser
   evidence. Do not treat a token signature alone as proof of database selection.
4. Record a run ID, exact target identity, account/garment IDs, source snapshots and
   schema/migration version in an ignored manifest. Keep only synthetic inputs and
   redacted test evidence; no user-photo copies or plaintext passwords/tokens.
5. Retain local fixtures until review is complete. Cleanup is an explicit, separately
   approved operation with a dry-run manifest and expected counts, target identity
   checks and transactional deletion of only that run's fixture IDs. Preserve shared
   reference rows used by other runs. Refuse mismatched IDs/identity and roll back on
   unexpected counts. No automatic local DROP/TRUNCATE/reset or deletion of the main
   database. Ephemeral CI teardown needs its own reviewed automation and boundaries.

This is a recommendation, not a claim these additional controls or cleanup tools
already exist. No database lifecycle operation is authorized by this report.

## Existing backend on port 8000

Read-only Windows listener/process inspection identified Python PID **22084**, bound
to `127.0.0.1:8000`, using `tools/run_backend.py --env-file backend/.env.integration`,
without reload enabled. Full command lines and environment values were not printed.
The process started before the security fixes.

Its current `/openapi.json` still declares an upload body and no authentication on
all seven catalog mutations. A zero-body `POST /upload/` returns **422**, rather than
the source's 503. No file, catalog mutation or private image was sent/read against it.
The running server has **not loaded either security fix** and needs an explicitly
approved restart/reload, followed by runtime verification. It was not interrupted.
The command-line env-file argument is evidence of launch configuration, not a new
runtime database attestation. No updated live-server success is claimed.

## Tests, commands and limitations

| Verification | Result |
| --- | --- |
| New catalog route/ORM tests | 12 passed; observed missing-authorization failures before the fix |
| Complete backend unittest suite | 26 passed, including accounts, startup and media protections |
| Integration-target safety tests | 4 passed; no database connections |
| Development proxy tests | 4 passed; no live API mutations |
| Flutter tests | 26 passed |
| Flutter analyze | No issues |
| Python syntax / Git whitespace | 62 app/test files parsed; `git diff --check` passed |
| Read-only PostgreSQL inspection and original baseline comparison | Passed |

Backend route tests use a fresh in-memory SQLite database with foreign keys enabled;
real route/authentication/ORM/scoring logic runs via TestClient. They do not modify
either existing PostgreSQL database. The initial pre-fix run failed with authorization
assertions; the full final suite passed. The existing Starlette/httpx test-client
deprecation warning remains. Flutter needed approved access to its user-level SDK
cache; no dependencies/tools were installed or upgraded.

No write-based PostgreSQL E2E, external weather-provider or Playwright flow was rerun:
those flows create fixtures and conflict with this milestone's read-only database
investigation. Cold/hot scoring was tested using manual weather through real routes.
Flutter unit/widget tests and the in-process route integration tests are not a claim
of a new live PostgreSQL/browser end-to-end run.

```powershell
# backend/
venv\Scripts\python.exe -B -m unittest tests.test_catalog_authorization -v
venv\Scripts\python.exe -B -m unittest discover -s tests -v
# frontend/
..\.tools\flutter\bin\flutter.bat --no-version-check --suppress-analytics analyze --no-pub
..\.tools\flutter\bin\flutter.bat --no-version-check --suppress-analytics test --no-pub --reporter=expanded
# repository root
backend\venv\Scripts\python.exe -B -m unittest discover -s tools -p test_check_integration.py -v
backend\venv\Scripts\python.exe -B -m unittest discover -s frontend/tool -p 'test_*.py' -v
backend\venv\Scripts\python.exe -B .tools/security/catalog-implementation-20261030T110201Z/review_databases.py
backend\venv\Scripts\python.exe -B tools/integration_database.py --verify-source
git diff --check
```

Ignored local evidence in `.tools/security/catalog-implementation-20261030T110201Z/`
includes the pre-change file inventory, failing test log, reproducible read-only DB
review, aggregate classifications, snapshots, sanitized process/HTTP evidence and
final verification. No real photo, credential or token is included.

## Files changed and remaining risks

- Production: `backend/app/services/auth_dependencies.py` and the brand/color/material
  route modules. Existing identity validation and every GET handler are preserved.
- Tests: `backend/tests/test_catalog_authorization.py`.
- Documentation: this report, the earlier authorization review's status banner,
  `AGENTS.md` and `docs/ROADMAP.md`. Existing unrelated work is preserved.

Remaining work: credential rotation/history review; mandatory JWT `exp`; inactive-user
login rejection; registration validation; rate limiting and recommendation work bounds;
test-role/pre-write isolation; approved runtime reload; and a future private-media
lifecycle. Actual catalog administrator capabilities and destructive catalog-reference
policies remain deferred. No administrator bypass, migration, credential rotation,
commit, push, deployment or unrelated refactoring was performed.

Stop after this milestone for review. Do not automatically implement the next risk.
