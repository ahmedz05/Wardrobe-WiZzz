
"""Configure the restricted Wardrobe-WIZzz integration backend.

Verifies PostgreSQL identity and privileges before saving
a new, Git-ignored environment configuration.

Does not change PostgreSQL records or permissions.
"""

from getpass import getpass
from pathlib import Path
from secrets import token_urlsafe

from sqlalchemy import URL, create_engine, text
from sqlalchemy.pool import NullPool


ROOT = Path(__file__).resolve().parents[1]

ENV_FILE = ROOT / "backend" / ".env.integration"

DATABASE = "wardrobe_wizzz_integration_20261030"
DATABASE_OID = 24581
ROLE = "wardrobe_integration"


def main():
    if ENV_FILE.exists():
        raise SystemExit(
            "Integration configuration already exists. "
            "Refusing to overwrite it."
        )

    password = getpass(
        "Enter wardrobe_integration password: "
    )

    if not password:
        raise SystemExit("Password cannot be empty.")

    url = URL.create(
        "postgresql+psycopg2",
        username=ROLE,
        password=password,
        host="127.0.0.1",
        port=5432,
        database=DATABASE,
    )

    engine = create_engine(
        url,
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
            identity = connection.execute(
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
                        )
                """)
            ).one()

            database, role, oid, read_only, source_access = (
                identity
            )

            if (
                database != DATABASE
                or role != ROLE
                or oid != DATABASE_OID
                or read_only != "on"
                or source_access
            ):
                raise RuntimeError(
                    "Database security verification failed."
                )

            print("Database identity: verified")
            print("Restricted role: verified")
            print("Original database access: denied")

    except Exception as exc:
        print(
            "Configuration stopped:",
            type(exc).__name__
        )
        raise SystemExit(1) from None

    finally:
        engine.dispose()

    # Use a separate, randomly generated JWT signing key
    # rather than copying production or historical secrets.
    jwt_secret = token_urlsafe(48)

    connection_url = url.render_as_string(
        hide_password=False
    )

    # The file is ignored by the repository's .gitignore.
    # Exclusive creation prevents overwriting existing secrets.
    with ENV_FILE.open(
        "x",
        encoding="utf-8",
    ) as file:
        file.write(
            f"DATABASE_URL={connection_url}\n"
            f"JWT_SECRET_KEY={jwt_secret}\n"
        )

    print("\nRestricted integration configuration created.")
    print("Location: backend/.env.integration")
    print("Password and JWT key: not displayed")
    print("No database records were modified.")


if __name__ == "__main__":
    main()
