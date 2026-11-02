
"""Read-only audit of PostgreSQL database access boundaries."""

from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.pool import NullPool

from local_config import read_environment


ROOT = Path(__file__).resolve().parents[1]

CONFIG_PATH = (
    ROOT.parent
    / "Wardrobe-WIZzz"
    / "backend"
    / ".env.integration"
).resolve()

EXPECTED_DATABASE = "wardrobe_wizzz_integration_20261030"
EXPECTED_DATABASE_OID = 24581


def main():
    if not CONFIG_PATH.is_file():
        raise SystemExit("Integration environment file not found.")

    config = read_environment(CONFIG_PATH)
    database_url = config["DATABASE_URL"]
    url = make_url(database_url)

    if (
        url.drivername not in (
            "postgresql",
            "postgresql+psycopg2",
        )
        or url.host not in ("localhost", "127.0.0.1", "::1")
        or url.port not in (None, 5432)
        or url.database != EXPECTED_DATABASE
    ):
        raise SystemExit("Database configuration not approved.")

    engine = create_engine(
        database_url,
        poolclass=NullPool,
        hide_parameters=True,
        connect_args={
            "options": (
                "-c default_transaction_read_only=on "
                "-c statement_timeout=5000"
            ),
        },
    )

    try:
        with engine.connect() as connection:
            read_only = connection.execute(
                text("SHOW transaction_read_only")
            ).scalar_one()

            if read_only != "on":
                raise RuntimeError("Read-only mode not verified.")

            identity = connection.execute(
                text("""
                    SELECT
                        current_database() AS database_name,
                        (
                            SELECT oid
                            FROM pg_database
                            WHERE datname = current_database()
                        ) AS database_oid
                """)
            ).mappings().one()

            if (
                identity["database_name"] != EXPECTED_DATABASE
                or identity["database_oid"] != EXPECTED_DATABASE_OID
            ):
                raise RuntimeError("Unexpected database identity.")

            print("\n=== DATABASE ACCESS BOUNDARY ===")

            rows = connection.execute(
                text("""
                    SELECT
                        d.datname AS database_name,
                        pg_get_userbyid(d.datdba) AS owner,
                        d.datacl IS NULL AS default_acl,

                        EXISTS (
                            SELECT 1
                            FROM aclexplode(
                                COALESCE(
                                    d.datacl,
                                    acldefault('d', d.datdba)
                                )
                            ) AS a
                            WHERE a.grantee = 0
                              AND a.privilege_type = 'CONNECT'
                        ) AS public_connect,

                        EXISTS (
                            SELECT 1
                            FROM aclexplode(
                                COALESCE(
                                    d.datacl,
                                    acldefault('d', d.datdba)
                                )
                            ) AS a
                            WHERE a.grantee = 0
                              AND a.privilege_type = 'CREATE'
                        ) AS public_create

                    FROM pg_database d
                    WHERE d.datname IN (
                        'wardrobe_wizzz',
                        'wardrobe_wizzz_integration_20261030'
                    )
                    ORDER BY d.datname
                """)
            ).mappings().all()

            for row in rows:
                print("\nDatabase:", row["database_name"])
                print("Owner:", row["owner"])
                print("Default ACL:", row["default_acl"])
                print("PUBLIC CONNECT:", row["public_connect"])
                print("PUBLIC CREATE:", row["public_create"])

            print("\n=== INTEGRATION SCHEMA ACCESS ===")

            schemas = connection.execute(
                text("""
                    SELECT
                        n.nspname AS schema_name,
                        pg_get_userbyid(n.nspowner) AS owner,

                        EXISTS (
                            SELECT 1
                            FROM aclexplode(
                                COALESCE(
                                    n.nspacl,
                                    acldefault('n', n.nspowner)
                                )
                            ) AS a
                            WHERE a.grantee = 0
                              AND a.privilege_type = 'CREATE'
                        ) AS public_create

                    FROM pg_namespace n
                    WHERE n.nspname = 'public'
                """)
            ).mappings().all()

            for row in schemas:
                print(dict(row))

            print("\n=== INTEGRATION SEQUENCES ===")

            sequence_count = connection.execute(
                text("""
                    SELECT COUNT(*)
                    FROM pg_class c
                    JOIN pg_namespace n
                        ON n.oid = c.relnamespace
                    WHERE n.nspname = 'public'
                      AND c.relkind = 'S'
                """)
            ).scalar_one()

            print("Sequence count:", sequence_count)

            print("\nRead-only boundary audit completed.")

    except Exception as exc:
        print("Audit stopped:", type(exc).__name__)
        raise SystemExit(1) from None

    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
