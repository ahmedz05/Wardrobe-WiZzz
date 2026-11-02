
"""Wardrobe-WIZzz restricted PostgreSQL end-to-end test.

Default: read-only preflight.
--execute: explicitly authorized synthetic API write test.

Never connects to or writes to the original wardrobe database.
"""

import argparse
import json
import subprocess
import sys
import uuid

from datetime import datetime, timezone
from pathlib import Path
from secrets import token_urlsafe
from urllib.error import HTTPError
from urllib.request import (
    ProxyHandler,
    Request,
    build_opener,
)

from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.pool import NullPool

from local_config import read_environment


ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = ROOT / "backend" / ".env.integration"

EXPECTED_DB = "wardrobe_wizzz_integration_20261030"
EXPECTED_OID = 24581
EXPECTED_ROLE = "wardrobe_integration"

BASE_URL = "http://127.0.0.1:8766"
OPENER = build_opener(ProxyHandler({}))


def api_request(method, path, payload=None, token=None):
    headers = {}

    if token:
        headers["Authorization"] = f"Bearer {token}"

    body = None

    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    request = Request(
        BASE_URL + path,
        data=body,
        headers=headers,
        method=method,
    )

    try:
        response = OPENER.open(request, timeout=15)
    except HTTPError as exc:
        response = exc

    with response:
        status = response.status
        raw = response.read()

    try:
        result = json.loads(raw) if raw else {}
    except ValueError:
        result = {}

    return status, result


def verify_server_process():
    """Verify the local API port belongs to our launcher."""

    script = """
    $listener = Get-NetTCPConnection `
        -LocalPort 8766 `
        -State Listen `
        -ErrorAction Stop |
        Select-Object -First 1

    if (-not $listener) {
        throw 'API listener not found.'
    }

    $process = Get-CimInstance Win32_Process `
        -Filter "ProcessId = $($listener.OwningProcess)"

    $process.CommandLine
    """

    result = subprocess.run(
        [
            "powershell.exe",
            "-NoProfile",
            "-NonInteractive",
            "-Command",
            script,
        ],
        capture_output=True,
        text=True,
        timeout=15,
    )

    if result.returncode != 0:
        raise RuntimeError("Unable to verify API process.")

    command = (
        result.stdout
        .lower()
        .replace('"', "")
        .replace("'", "")
    )

    required = [
        "run_backend.py",
        "--env-file backend/.env.integration",
        "--port 8766",
    ]

    if not all(value in command for value in required):
        raise RuntimeError(
            "API launcher does not match the expected configuration."
        )

    print("API launcher: verified")


def verify_database():
    """Read-only database identity and privilege verification."""

    if not ENV_FILE.is_file():
        raise RuntimeError("Integration environment file missing.")

    config = read_environment(ENV_FILE)
    url = make_url(config["DATABASE_URL"])

    if (
        url.drivername not in (
            "postgresql",
            "postgresql+psycopg2",
        )
        or url.host not in ("127.0.0.1", "localhost")
        or url.port not in (None, 5432)
        or url.database != EXPECTED_DB
        or url.username != EXPECTED_ROLE
    ):
        raise RuntimeError("Unapproved database configuration.")

    engine = create_engine(
        config["DATABASE_URL"],
        poolclass=NullPool,
        hide_parameters=True,
        connect_args={
            "options": (
                "-c default_transaction_read_only=on "
                "-c statement_timeout=5000"
            )
        },
    )

    try:
        with engine.connect() as connection:
            row = connection.execute(
                text("""
                    SELECT
                        current_database(),
                        current_user,
                        (
                            SELECT oid
                            FROM pg_database
                            WHERE datname = current_database()
                        ),
                        current_setting('transaction_read_only'),
                        has_database_privilege(
                            current_user,
                            'wardrobe_wizzz',
                            'CONNECT'
                        ),
                        (
                            SELECT rolsuper
                            FROM pg_roles
                            WHERE rolname = current_user
                        )
                """)
            ).one()

            db_name, role, oid, read_only, source, superuser = row

            if (
                db_name != EXPECTED_DB
                or role != EXPECTED_ROLE
                or oid != EXPECTED_OID
                or read_only != "on"
                or source
                or superuser
            ):
                raise RuntimeError(
                    "Database identity or privilege check failed."
                )

            references = connection.execute(
                text("""
                    SELECT c.name, MIN(s.id)
                    FROM public.categories c
                    JOIN public.subcategories s
                        ON s.category_id = c.id
                    WHERE c.name IN ('Tops', 'Bottoms', 'Shoes')
                      AND c.is_active = TRUE
                      AND s.is_active = TRUE
                    GROUP BY c.name
                """)
            ).all()

            category_ids = {
                name: item_id
                for name, item_id in references
            }

            if set(category_ids) != {
                "Tops", "Bottoms", "Shoes"
            }:
                raise RuntimeError(
                    "Required integration categories are missing."
                )

            color_id = connection.execute(
                text("""
                    SELECT id
                    FROM public.colors
                    WHERE is_active = TRUE
                    ORDER BY id
                    LIMIT 1
                """)
            ).scalar_one_or_none()

            if color_id is None:
                raise RuntimeError(
                    "No active integration color exists."
                )

            print("Database identity: verified")
            print("Restricted role: verified")
            print("Original database access: denied")
            print("Integration references: available")

            return category_ids, color_id

    finally:
        engine.dispose()


def verify_public_api():
    """Run requests that cannot modify account or wardrobe data."""

    checks = [
        ("/categories", 200),
        ("/me", 401),
        ("/clothing", 401),
        ("/outfits/generate", 401),
    ]

    for path, expected in checks:
        status, _ = api_request("GET", path)

        if status != expected:
            raise RuntimeError(
                f"{path}: expected {expected}, received {status}"
            )

    print("Read-only API checks: passed")


def save_manifest(path, manifest):
    path.parent.mkdir(parents=True, exist_ok=True)

    path.write_text(
        json.dumps(manifest, indent=2),
        encoding="utf-8",
    )


def require_status(status, expected, operation):
    if status != expected:
        raise RuntimeError(
            f"{operation}: expected HTTP {expected}, received {status}"
        )


def run_write_test(category_ids, color_id):
    """Create synthetic fixtures and exercise real FastAPI routes."""

    run_id = uuid.uuid4().hex[:12]

    username = "integration_" + run_id
    email = username + "@example.test"
    password = token_urlsafe(24)

    manifest_path = (
        ROOT
        / "backend"
        / "backups"
        / f"restricted_integration_{run_id}.json"
    )

    manifest = {
        "run_id": run_id,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "database": EXPECTED_DB,
        "database_oid": EXPECTED_OID,
        "role": EXPECTED_ROLE,
        "username": username,
        "email": email,
        "user_id": None,
        "clothing_ids": [],
        "cleanup_status": "not_started",
    }

    save_manifest(manifest_path, manifest)

    token = None

    try:
        print("\n=== REGISTRATION ===")

        status, registered = api_request(
            "POST",
            "/register",
            {
                "username": username,
                "email": email,
                "password": password,
            },
        )

        require_status(status, 200, "Registration")

        manifest["user_id"] = registered["id"]
        save_manifest(manifest_path, manifest)

        print("Registration: PASS")

        print("\n=== LOGIN ===")

        status, login_result = api_request(
            "POST",
            "/login",
            {
                "email": email,
                "password": password,
            },
        )

        require_status(status, 200, "Login")

        token = login_result["access_token"]

        print("Login: PASS")

        print("\n=== AUTHENTICATED ACCOUNT ===")

        status, account = api_request(
            "GET",
            "/me",
            token=token,
        )

        require_status(status, 200, "Account")

        if account["id"] != manifest["user_id"]:
            raise RuntimeError("Authenticated identity mismatch.")

        print("Authenticated identity: PASS")

        print("\n=== CLOTHING CREATION ===")

        for category in ("Tops", "Bottoms", "Shoes"):
            payload = {
                "name": f"Integration {category} {run_id}",
                "subcategory_id": category_ids[category],
                "color_id": color_id,
                "season": "All Season",
                "style": "Casual",
                "occasion": "Casual",
                "fit": "Regular",
                "silhouette": "Regular",
            }

            status, created = api_request(
                "POST",
                "/clothing",
                payload,
                token,
            )

            require_status(
                status,
                200,
                f"Create {category}",
            )

            if created["user_id"] != manifest["user_id"]:
                raise RuntimeError("Clothing ownership mismatch.")

            manifest["clothing_ids"].append(created["id"])
            save_manifest(manifest_path, manifest)

            print(f"Create {category}: PASS")

        print("\n=== WARDROBE LIST ===")

        status, wardrobe = api_request(
            "GET",
            "/clothing",
            token=token,
        )

        require_status(status, 200, "Wardrobe listing")

        owned_ids = {
            item["id"]
            for item in wardrobe
        }

        if not set(manifest["clothing_ids"]).issubset(owned_ids):
            raise RuntimeError("Created clothing not returned.")

        print("Wardrobe listing: PASS")

        print("\n=== CLOTHING UPDATE ===")

        clothing_id = manifest["clothing_ids"][0]

        status, updated = api_request(
            "PUT",
            f"/clothing/{clothing_id}",
            {"name": f"Updated Integration Top {run_id}"},
            token,
        )

        require_status(status, 200, "Clothing update")

        if updated["id"] != clothing_id:
            raise RuntimeError("Updated clothing identity mismatch.")

        print("Clothing update: PASS")

        print("\n=== OUTFIT GENERATION ===")

        status, outfits = api_request(
            "GET",
            "/outfits/generate",
            token=token,
        )

        require_status(status, 200, "Outfit generation")

        if not outfits.get("outfits"):
            raise RuntimeError("No outfit was generated.")

        print("Outfit generation: PASS")

        print("\nAll integration workflow checks passed.")

    finally:
        print("\n=== FIXTURE CLEANUP ===")

        remaining = []

        for clothing_id in reversed(manifest["clothing_ids"]):
            if token is None:
                remaining.append(clothing_id)
                continue

            try:
                status, _ = api_request(
                    "DELETE",
                    f"/clothing/{clothing_id}",
                    token=token,
                )

                if status != 200:
                    remaining.append(clothing_id)

            except Exception:
                remaining.append(clothing_id)

        manifest["remaining_clothing_ids"] = remaining
        manifest["cleanup_status"] = (
            "clothing_removed"
            if not remaining
            else "manual_review_required"
        )

        manifest["account_cleanup"] = (
            "Synthetic user retained for separately approved cleanup."
        )

        save_manifest(manifest_path, manifest)

        print("Clothing remaining:", len(remaining))
        print("Synthetic account retained.")
        print("Cleanup manifest:", manifest_path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Run synthetic API writes after explicit confirmation.",
    )

    args = parser.parse_args()

    print("=== RESTRICTED API PREFLIGHT ===")

    verify_server_process()
    category_ids, color_id = verify_database()
    verify_public_api()

    if not args.execute:
        print("\nPREFLIGHT PASSED")
        print("No API writes were performed.")
        print("Use --execute only after approving fixture creation.")
        return

    print("\nThis will create:")
    print("- One synthetic account in the integration database")
    print("- Three synthetic clothing items")
    print("- A local cleanup manifest")
    print("The clothing will be deleted after testing.")
    print("The account will remain until separately approved cleanup.")

    confirmation = input(
        "\nType CREATE SYNTHETIC FIXTURES to approve: "
    )

    if confirmation != "CREATE SYNTHETIC FIXTURES":
        raise SystemExit("Write test cancelled.")

    run_write_test(category_ids, color_id)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("Stopped:", type(exc).__name__, str(exc))
        sys.exit(1)
