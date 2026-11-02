
"""Read-only PostgreSQL privilege audit for Wardrobe-WIZzz.

Only the approved integration database is inspected.
No database records, roles, permissions, or passwords are changed.
"""

import argparse
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.pool import NullPool

from local_config import read_environment


# =====================================
# APPROVED CONFIGURATION
# =====================================

ROOT = Path(__file__).resolve().parents[1]

ORIGINAL_INTEGRATION_ENV = (
    ROOT.parent
    / "Wardrobe-WIZzz"
    / "backend"
    / ".env.integration"
).resolve()

PUBLICATION_INTEGRATION_ENV = (
    ROOT
    / "backend"
    / ".env.integration"
).resolve()

APPROVED_FILES = {
    ORIGINAL_INTEGRATION_ENV,
    PUBLICATION_INTEGRATION_ENV,
}

EXPECTED_DATABASE = "wardrobe_wizzz_integration_20261030"

ALLOWED_HOSTS = {
    "localhost",
    "127.0.0.1",
    "::1",
}


# =====================================
# PRINT HELPERS
# =====================================

def section(title):
    print(f"\n=== {title} ===")


def print_record(record):
    for key, value in record.items():
        print(f"{key}: {value}")


# =====================================
# DATABASE AUDIT
# =====================================

def audit_database(database_url):

    url = make_url(database_url)

    if url.drivername not in (
        "postgresql",
        "postgresql+psycopg2",
    ):
        raise ValueError("Expected a PostgreSQL connection.")

    if url.host not in ALLOWED_HOSTS:
        raise ValueError("Remote hosts are not approved.")

    if url.port not in (None, 5432):
        raise ValueError("Unexpected PostgreSQL port.")

    if url.database != EXPECTED_DATABASE:
        raise ValueError(
            "Refusing to inspect an unapproved database."
        )

    # Enforce read-only transactions at connection startup.
    engine = create_engine(
        database_url,
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

            read_only = connection.execute(
                text("SHOW transaction_read_only")
            ).scalar_one()

            if read_only != "on":
                raise RuntimeError(
                    "Read-only transaction was not verified."
                )

            # =====================================
            # CONNECTION IDENTITY
            # =====================================

            identity = connection.execute(
                text("""
                    SELECT
                        current_database() AS database_name,
                        current_user AS role_name,
                        (
                            SELECT oid
                            FROM pg_database
                            WHERE datname = current_database()
                        ) AS database_oid
                """)
            ).mappings().one()

            if identity["database_name"] != EXPECTED_DATABASE:
                raise RuntimeError(
                    "Connected database does not match expected target."
                )

            section("DATABASE IDENTITY")
            print_record(identity)
            print("transaction_read_only:", read_only)

            # =====================================
            # ROLE CAPABILITIES
            # =====================================

            role = connection.execute(
                text("""
                    SELECT
                        rolsuper,
                        rolcreatedb,
                        rolcreaterole,
                        rolreplication,
                        rolbypassrls,
                        rolinherit,
                        rolcanlogin
                    FROM pg_roles
                    WHERE rolname = current_user
                """)
            ).mappings().one()

            section("ROLE CAPABILITIES")
            print_record(role)

            # =====================================
            # DATABASE ACCESS
            # =====================================

            databases = connection.execute(
                text("""
                    SELECT
                        datname AS database_name,
                        has_database_privilege(
                            current_user,
                            oid,
                            'CONNECT'
                        ) AS can_connect,
                        has_database_privilege(
                            current_user,
                            oid,
                            'CREATE'
                        ) AS can_create
                    FROM pg_database
                    WHERE datname IN (
                        'wardrobe_wizzz',
                        'wardrobe_wizzz_integration_20261030'
                    )
                    ORDER BY datname
                """)
            ).mappings().all()

            section("DATABASE ACCESS")

            for database in databases:
                print_record(database)
                print("---")

            # =====================================
            # SCHEMA PRIVILEGES
            # =====================================

            schema = connection.execute(
                text("""
                    SELECT
                        has_schema_privilege(
                            current_user,
                            'public',
                            'USAGE'
                        ) AS can_use_schema,
                        has_schema_privilege(
                            current_user,
                            'public',
                            'CREATE'
                        ) AS can_create_in_schema
                """)
            ).mappings().one()

            section("PUBLIC SCHEMA PRIVILEGES")
            print_record(schema)

            # =====================================
            # TABLE PRIVILEGES
            # =====================================

            tables = connection.execute(
                text("""
                    SELECT
                        COUNT(*) AS table_count,

                        COUNT(*) FILTER (
                            WHERE has_table_privilege(
                                current_user,
                                c.oid,
                                'SELECT'
                            )
                        ) AS readable_tables,

                        COUNT(*) FILTER (
                            WHERE has_table_privilege(
                                current_user,
                                c.oid,
                                'INSERT'
                            )
                        ) AS insertable_tables,

                        COUNT(*) FILTER (
                            WHERE has_table_privilege(
                                current_user,
                                c.oid,
                                'UPDATE'
                            )
                        ) AS updatable_tables,

                        COUNT(*) FILTER (
                            WHERE has_table_privilege(
                                current_user,
                                c.oid,
                                'DELETE'
                            )
                        ) AS deletable_tables

                    FROM pg_class c
                    JOIN pg_namespace n
                        ON n.oid = c.relnamespace

                    WHERE n.nspname = 'public'
                      AND c.relkind IN ('r', 'p')
                """)
            ).mappings().one()

            section("EFFECTIVE TABLE PRIVILEGES")
            print_record(tables)

            # =====================================
            # SECURITY RESULT
            # =====================================

            section("SECURITY ASSESSMENT")

            if role["rolsuper"]:
                print(
                    "WARNING: Application connection uses "
                    "a PostgreSQL superuser."
                )

                print(
                    "A separate least-privilege application "
                    "role is recommended."
                )

            else:
                print(
                    "The connected role is not a superuser."
                )

                print(
                    "Further inherited-role and grant "
                    "review is still required."
                )

            print("\nRead-only audit completed.")
            print("No database changes were performed.")

    finally:
        engine.dispose()


# =====================================
# COMMAND-LINE ENTRY POINT
# =====================================

def main():

    parser = argparse.ArgumentParser(
        description="Read-only PostgreSQL security audit."
    )

    parser.add_argument(
        "--env-file",
        required=True,
        type=Path,
    )

    args = parser.parse_args()

    config_path = args.env_file.resolve()

    if config_path not in APPROVED_FILES:
        parser.error(
            "Only approved integration environment files are allowed."
        )

    if not config_path.is_file():
        parser.error("Environment file does not exist.")

    config = read_environment(config_path)

    database_url = config.get("DATABASE_URL")

    if not database_url:
        parser.error("DATABASE_URL is missing.")

    try:
        audit_database(database_url)

    except Exception as exc:
        # Avoid accidentally displaying credential-bearing
        # connection strings in diagnostic messages.
        print(
            "\nAudit stopped:",
            type(exc).__name__,
        )
        raise SystemExit(1) from None


if __name__ == "__main__":
    main()
