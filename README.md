# Wardrobe-WIZzz

Wardrobe management and weather-aware outfit recommendations, with a FastAPI
backend and Flutter client. This is a development checkpoint, not a production
release or a trained fashion-intelligence model.

## Implemented

- JSON account registration/login, JWT bearer authentication, and owner-scoped
  clothing CRUD in the backend.
- Shared category, brand, color, and material catalog reads. All seven exposed
  catalog mutations currently fail closed: unauthenticated requests receive 401;
  active authenticated users receive 403. There is no administrator bypass.
- Heuristic outfit scoring using garment, color, style, occasion, season, warmth,
  and optional manual or city-based weather context. City weather uses Open-Meteo.
- A Flutter client with login/registration, wardrobe listing/search/filtering,
  outfit recommendations, adaptive navigation, and loading/error/empty states.
- Native secure token storage and browser memory-only sessions. The Flutter UI
  does not yet provide clothing creation/editing/deletion or image uploads.
- An offline research validator and lexical query CLI. It preserves source
  references and uncertainty; it does not establish factual truth or training rights.

Legacy image uploads return **503 before body parsing**. Public `/uploads/` access
returns **404**. Existing local photos remain on disk; private image handling is
unfinished.

## Current stack and planned work

The implemented stack is Python, FastAPI, SQLAlchemy, PostgreSQL, Alembic, and
Flutter/Dart. Use the root `requirements.txt` for the backend environment; the older
`backend/requirements.txt` does not include every current dependency. Flutter and
browser-tool dependencies have their own lockfiles.

Computer vision, automatic garment categorization, trained recommendation models,
learned personalization, collection-level fashion reasoning, and an AI stylist
assistant remain planned. OpenCV, YOLO, EasyOCR, and LLM APIs are not implemented
application capabilities in this checkpoint. Native-device validation and release
signing also remain incomplete.

## Local development

See [the Flutter setup guide](frontend/README.md) for client commands, API URLs,
contracts, token behavior, and the loopback preview proxy. The proxy is a development
utility, not a production server. Release builds require an explicit HTTPS API URL.

Backend configuration comes from an ignored local environment file containing
`DATABASE_URL` and `JWT_SECRET_KEY`; [the example](backend/.env.example) contains
placeholders only. Supply your own values locally and restrict file permissions.
Never copy credentials from old commits or place secrets in Flutter defines.

With an existing configured Python environment and an already provisioned database,
the launcher is:

```powershell
backend\venv\Scripts\python.exe -u -B tools/run_backend.py --env-file backend/.env.local --port 8000
```

Choose the environment and a free port deliberately; this command is not an
instruction to interrupt an existing server. Startup does not create tables or run
migrations. Database provisioning, migrations, and data changes need separate review.
The launcher defaults to `.env.local` when no `--env-file` is supplied.

## Verification and integration boundaries

Safe automated suites cover backend routes/ORM against new in-memory SQLite,
Flutter unit/widgets with injected HTTP/storage, mocked proxy I/O, integration
configuration guards, and offline research fixtures. These suites do not modify the
existing PostgreSQL databases.

From `backend/`:

```powershell
venv\Scripts\python.exe -B -m unittest discover -s tests -v
```

From the repository root:

```powershell
backend\venv\Scripts\python.exe -B -m unittest discover -s tools -p 'test_*.py' -v
backend\venv\Scripts\python.exe -B -m unittest discover -s frontend/tool -p 'test_*.py' -v
```

Flutter analysis/test commands are in its setup guide. Local real HTTP/PostgreSQL
and browser flows have also been exercised, but historical milestone results are
not a fresh-clone, production, or native-device certification.

**Write-based integration runners and the database bootstrap are excluded from this
publication.** Their previous guards did not establish the running API's database
before its first write, and local credentials shared superuser access. Safe local
configuration parsing and read-only target checks are retained in separate modules;
they do not authorize fixture writes or prove the API's live database identity.
Reintroducing write runners requires reviewed least-privilege roles and pre-write
attestation. Existing tracked database administration scripts are not startup or
test commands and must not be run without separate authorization.

## Offline fashion research

`tools/fashion_research.py` and its synthetic tests are included. The two local
research JSON collections are deliberately excluded pending redistribution-rights
review. To use separately approved inputs with the required filenames:

```powershell
backend\venv\Scripts\python.exe -B tools/fashion_research.py --research-dir C:\path\to\approved-inputs validate
backend\venv\Scripts\python.exe -B tools/fashion_research.py --research-dir C:\path\to\approved-inputs query "Dior" --kind candidate
```

Without those inputs, corpus queries cannot run; the fixture-based tests still can.
Discovery candidates are not verified brands, and source accessibility is not a
license to redistribute content or train models. See the [research foundation and
proposal](docs/FASHION_INTELLIGENCE_FOUNDATION.md).

## Security and publication status

The previously exposed local database password has been rotated and rejected in
fresh connection checks. The running local API rejects the historical JWT signing
key. That verifies the inspected local instance, not other machines or deployments.
The historical uploaded image was removed from rewritten `main` history at
`0dd5db77bc334b09a96f6c467c5a13df9bdb71a8`. External clones, forks, or GitHub caches
may retain copies. Retired credential literals still exist in historical code;
never reuse them.

Production gaps include mandatory JWT expiration claims, inactive-user login
rejection, registration validation, rate limiting, least-privilege database roles,
integration isolation, private media handling, and recommendation resource bounds.
Do not expose this development checkpoint as a production service.

The [roadmap](docs/ROADMAP.md), [engineering principles](docs/ENGINEERING_PRINCIPLES.md),
and [contributor instructions](AGENTS.md) describe the next review gates. Milestone
reports retain their original dated context and may describe superseded local
processes, counts, or blockers.
