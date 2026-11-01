# Phase 1, security milestone 2: catalog authorization decision

Status update: the user approved temporary default-deny, and it is now implemented
and tested in local source. See [the implementation and database review](PHASE1_CATALOG_AUTHORIZATION_RESULTS.md).
The inspection and pending-decision statements below describe the earlier review,
preserved as the approved design and historical verification record.

Reviewed 2026-10-30 against authoritative local files. **Inspection and baseline
verification complete; catalog containment is not implemented.** The user's stop
condition applies: no trustworthy administrator identity or policy exists, so an
access-policy decision is required before changing mutation behavior. No schema
change, account privilege, hardcoded administrator or client-trusted role was added.

## Confirmed exposure

These are all seven registered shared-catalog mutation operations:

| Operation | Local route | Service behavior | Current authorization |
| --- | --- | --- | --- |
| Create brand | `POST /brands/` | Insert and commit | None |
| Create color | `POST /colors/` | Insert and commit | None |
| Update color | `PUT /colors/{color_id}` | Update and commit | None |
| Delete color | `DELETE /colors/{color_id}` | Hard delete and commit | None |
| Create material | `POST /materials/` | Insert and commit | None |
| Update material | `PUT /materials/{material_id}` | Update and commit | None |
| Delete material | `DELETE /materials/{material_id}` | Hard delete and commit | None |

The routes have only database dependencies. Their services do not authorize callers.
All seven operations succeeded with valid synthetic payloads as an anonymous caller
and as a real-token, active ordinary user, for **14 unauthorized successes** in a
new in-memory SQLite database. This characterizes a vulnerability; it is not a
passing security acceptance suite. The two DELETE operations were exercised only
against records created in that ephemeral database, never existing PostgreSQL data.

Category and subcategory HTTP routes are read-only. No shared-catalog PATCH,
deactivation or additional mutation routes are registered. The mutation schemas do
not accept `is_active`; inheriting that database field does not expose an API for
changing it. Brand update/delete service functions exist but have no route/caller.
Generic `BaseService`/`CRUDService` helpers are also unregistered and unused.
`backend/scripts/seed_categories.py` is an offline writer, not an API endpoint; it
was inspected and not executed. Existing integration reference seeding is confined
by its guards to the approved synthetic database and was not executed here.

The public read contract comprises ten operations: category list and subcategory
list; brand list/detail; material list/detail; color list/detail/compare/matches.
All ten returned 200 with synthetic fixtures for both anonymous and ordinary callers
(20 checks). Do not add a router-wide authentication restriction that changes reads.

## Identity and privilege findings

`User` has username, email, password hash and inherited ID/active/timestamps;
`UserProfile` contains profile attributes. Neither models nor Alembic revisions
define an administrator role, membership, permission or provisioning policy.
`get_current_user` verifies a signed token, an integer user ID and a currently active
database user. It establishes identity only. Registration creates ordinary users;
login issues no catalog privilege. There is no trustworthy source from which to
identify an authorized catalog administrator. A claim named `admin` or `role`, a
particular email/user ID, or being the first registered account cannot establish one.

Clothing mutation, wardrobe retrieval and outfit generation use `get_current_user`
and server-derived user ownership. Changing a garment's catalog reference does not
create or modify a catalog record. Keep those legitimate operations independent of
the shared-catalog write policy.

## Specific decision required

**Recommended immediate decision:** approve temporary default-deny for all seven
catalog mutations, with no supported HTTP writer until a real privilege model is
approved. This requires no schema change and appoints no administrator.

| Request with valid route payload | Proposed result |
| --- | --- |
| Missing, invalid or expired credentials; inactive/nonexistent identity | 401 |
| Valid active ordinary user, including a token carrying an unrecognized admin claim | 403 |
| Authorized catalog administrator | Not supported by the current model; nobody is granted this status |
| Existing catalog GET operations | Preserve current public access and responses |
| Owner's wardrobe CRUD and outfit recommendations | Preserve current authenticated ownership rules |

Implement this as one shared dependency on mutation operations only: resolve the
existing authenticated identity, then deny catalog writes with 403. Denial must
precede catalog service execution and leave records unchanged. No special token,
environment identity allowlist or hidden bypass is proposed. Existing JWT weaknesses
remain separately tracked; this change does not claim to fix authentication generally.

Compatibility impact: every external catalog writer would be blocked, including any
manual authenticated API consumer. The current Flutter repository has no catalog
mutation calls, so no Dart contract change is expected. Read operations and existing
wardrobe references remain available. Confirm this no-writer period is acceptable
before implementation; it is a deliberate product policy, not an inferred admin role.

The smallest long-term option is a backend-controlled boolean capability such as
`can_manage_catalog`, NOT NULL with default false, checked from the active database
user on every mutation. This requires a separately approved/rehearsed Alembic
migration and an explicit, audited out-of-band grant/revoke process for selected
existing user IDs. Registration/profile inputs must never assign it; JWT role claims
must not override it. Avoid a general role framework until more permissions require
one. Administrator deletion/in-use reference rules and audit events also need review
before enabling privileged catalog writes. None of this design is implemented or
authorized as a schema operation by this report.

Choose temporary default-deny now, or first approve a persistent privilege design
and migration. Implementation remains paused at the user's requested decision gate.

## Regression acceptance criteria after that decision

- Exercise all seven mutation operations with anonymous, invalid/expired-token,
  inactive-user and active ordinary-user callers; verify 401/403 as applicable and
  unchanged catalog and wardrobe records. A forged privilege claim must not bypass
  the gate. Enumerate registered catalog mutation routes so additions cannot silently
  omit the dependency.
- Preserve all ten public catalog read operations, including matching and missing-ID
  behavior. Prove allowed owner wardrobe creation/updates/retrieval and weather-aware
  outfit generation still work, with cross-user denial.
- If a persistent administrator capability is approved later, test grants,
  revocation, inactive administrators, allowed mutations and referential integrity.
  There is no administrator success path to test in temporary default-deny.
- Rerun backend, Flutter and integration checks against a separately started patched
  API using only the approved synthetic database; never test destructive mutations
  against the existing wardrobe database.

## Verification performed now

| Check | Result | Scope |
| --- | --- | --- |
| Backend unittest discovery | 14 passed | Accounts/session closure/startup/media; new SQLite and synthetic temporary files |
| Catalog authorization characterization | 14 unauthorized mutations succeeded | Seven operations, anonymous + active ordinary user; vulnerability confirmed |
| Catalog reads | 20 passed | Ten routes, both caller types; new SQLite |
| Wardrobe/outfit characterization | 7 grouped checks passed | Anonymous denial, four owner-created garments/list, normal/cold/hot manual-weather outfits, second-account isolation |
| Integration-target safety tests | 4 passed | No database connections |
| Development proxy tests | 4 passed | In-process transport, no live backend |
| Flutter analyze | No issues | Existing dependencies, no install |
| Flutter tests | 26 passed | Existing unit/widget tests |
| Backend Python syntax | 61 files parsed | App and tests; syntax only, not type checking |
| `git diff --check` | Passed | Current tracked work |

The first sandboxed Flutter analysis failed because the SDK could not clean its
user-level telemetry log. Retrying with escalated cache access passed, followed by
the passing Flutter tests. The existing Starlette/httpx test-client deprecation
warning remains; dependencies were not upgraded.

No live PostgreSQL integration, external weather-provider or Playwright browser run
was performed in this decision-only review. The manual-weather characterization
uses the real route/scoring implementation in-process, not a live weather service.
No new security regression suite or production fix is claimed while policy approval
is outstanding. Previous milestone integration evidence remains historical evidence.

Commands (backend tests from `backend/`, Flutter from `frontend/`, others from root):

```powershell
venv\Scripts\python.exe -B -m unittest discover -s tests -v
..\.tools\flutter\bin\flutter.bat --no-version-check --suppress-analytics analyze --no-pub
..\.tools\flutter\bin\flutter.bat --no-version-check --suppress-analytics test --no-pub --reporter=expanded
backend\venv\Scripts\python.exe -B -m unittest discover -s tools -p test_check_integration.py -v
backend\venv\Scripts\python.exe -B -m unittest discover -s frontend/tool -p 'test_*.py' -v
backend\venv\Scripts\python.exe -B .tools/security/catalog-review-20261030T104651Z/characterize.py
git diff --check
```

Ignored local evidence in `.tools/security/catalog-review-20261030T104651Z/` includes
the reproducible characterization script, its response-status/dependency report,
pre-review file hashes and initial Git status. Tokens and real configuration secrets
are not included. The only nonignored file added by this review is this document;
all pre-existing candidate file contents were preserved. No staging or server restart
was performed.

## Running backend: media fix not loaded

Two read-only-schema/bodyless-request checks confirmed port 8000 is still serving an
older application: `POST /upload/` with zero body returns **422**, and `/openapi.json`
still declares an upload request body and no 503 response. The corrected local source
returns 503 without consuming a body, as freshly verified by the media tests.
Port 8001 had no responding API (connection error).

No file was submitted and no existing photograph was accessed. Public image exposure
on the running process was not tested by reading user images. The backend on 8000
has **not** loaded the completed media containment fix; do not claim runtime media
privacy from source/test results. The existing server was left untouched as required.
Restart/reload of that existing process requires the user's explicit approval and
subsequent runtime verification; no such approval is inferred here.

## Remaining tracked risks

| Risk | Status / separate next action |
| --- | --- |
| Historical credentials | Rotation/history review remains outstanding; no credential changed or disclosed here. |
| JWT expiration | Issued tokens expire, but verification does not require an `exp` claim; implement required-expiry regression separately. |
| Inactive users | `/login` can issue a token to an inactive user although protected identity lookup rejects it; fix login separately. |
| Registration validation | Plain string inputs lack sufficient server-side email/password/length validation; separate contract-aware fix. |
| Rate limiting | Login/registration and costly recommendation/weather operations lack abuse controls; separate bounded design. |
| Catalog integrity | Shared mutations remain exposed pending this decision; hard deletion and in-use references need policy before any future administrator success path. |
| Media runtime and lifecycle | Local fail-closed fix retained; existing server needs approved reload. Private upload ownership/validation remains a future reviewed design. |

Stop here for the catalog access-policy decision. No unrelated backend refactoring,
AI work, database mutation/migration, commit, push or deployment was performed.
