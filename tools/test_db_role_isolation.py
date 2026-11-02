
"""Verify PostgreSQL isolation for Wardrobe-WIZzz.

Uses read-only connections and catalog permission checks.
Never modifies database records or permissions.
"""

from getpass import getpass

import psycopg2
from psycopg2 import OperationalError


HOST = "127.0.0.1"
PORT = 5432

ROLE = "wardrobe_integration"

INTEGRATION_DB = "wardrobe_wizzz_integration_20261030"
ORIGINAL_DB = "wardrobe_wizzz"
MAINTENANCE_DB = "postgres"


def connect(database, password):
    return psycopg2.connect(
        host=HOST,
        port=PORT,
        dbname=database,
        user=ROLE,
        password=password,
        connect_timeout=5,
        options=(
            "-c default_transaction_read_only=on "
            "-c statement_timeout=5000"
        ),
    )


def verify_integration(password):
    print("\n=== TEST 1: INTEGRATION DATABASE ===")

    try:
        connection = connect(INTEGRATION_DB, password)
    except OperationalError:
        print("FAIL: Integration connection unsuccessful.")
        return False

    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT
                    current_database(),
                    current_user,
                    current_setting('transaction_read_only')
            """)

            database, role, read_only = cursor.fetchone()

            if (
                database != INTEGRATION_DB
                or role != ROLE
                or read_only != "on"
            ):
                print("FAIL: Unexpected connection identity.")
                return False

            print("Database:", database)
            print("Role:", role)
            print("Read-only test:", read_only)

            # Verify administrative role attributes.
            cursor.execute("""
                SELECT
                    rolsuper,
                    rolcreatedb,
                    rolcreaterole,
                    rolbypassrls
                FROM pg_roles
                WHERE rolname = current_user
            """)

            privileges = cursor.fetchone()

            if privileges is None or any(privileges):
                print("FAIL: Unexpected administrative privileges.")
                return False

            print("Administrative privileges: none")

            # Check the original and maintenance databases.
            cursor.execute("""
                SELECT
                    has_database_privilege(
                        current_user,
                        %s,
                        'CONNECT'
                    ),
                    has_database_privilege(
                        current_user,
                        %s,
                        'CONNECT'
                    )
            """, (ORIGINAL_DB, MAINTENANCE_DB))

            original_access, maintenance_access = (
                cursor.fetchone()
            )

            print("Original DB CONNECT:", original_access)
            print("Maintenance DB CONNECT:", maintenance_access)

            if original_access:
                print("FAIL: Original database privilege exists.")
                return False

            # Verify necessary application permissions.
            cursor.execute("""
                SELECT
                    has_schema_privilege(
                        current_user,
                        'public',
                        'USAGE'
                    ),
                    has_schema_privilege(
                        current_user,
                        'public',
                        'CREATE'
                    ),
                    has_table_privilege(
                        current_user,
                        'public.users',
                        'INSERT'
                    ),
                    has_table_privilege(
                        current_user,
                        'public.users',
                        'UPDATE'
                    ),
                    has_table_privilege(
                        current_user,
                        'public.clothing',
                        'UPDATE'
                    ),
                    has_table_privilege(
                        current_user,
                        'public.colors',
                        'INSERT'
                    )
            """)

            (
                schema_usage,
                schema_create,
                user_insert,
                user_update,
                clothing_update,
                color_insert,
            ) = cursor.fetchone()

            expected = (
                True,
                False,
                True,
                False,
                True,
                False,
            )

            actual = (
                schema_usage,
                schema_create,
                user_insert,
                user_update,
                clothing_update,
                color_insert,
            )

            if actual != expected:
                print("FAIL: Table or schema privileges differ.")
                print("Observed:", actual)
                return False

            # Verify insert operations can use ID sequences.
            cursor.execute("""
                SELECT
                    has_sequence_privilege(
                        current_user,
                        pg_get_serial_sequence(
                            'public.users',
                            'id'
                        ),
                        'USAGE'
                    ),
                    has_sequence_privilege(
                        current_user,
                        pg_get_serial_sequence(
                            'public.clothing',
                            'id'
                        ),
                        'USAGE'
                    )
            """)

            user_sequence, clothing_sequence = (
                cursor.fetchone()
            )

            if not (user_sequence and clothing_sequence):
                print("FAIL: Required sequence access missing.")
                return False

            print("Table privileges: PASS")
            print("Sequence privileges: PASS")

            return True

    except psycopg2.Error:
        print("FAIL: Database permission query failed.")
        return False

    finally:
        connection.close()


def verify_original_denied(password):
    print("\n=== TEST 2: ORIGINAL DATABASE ===")

    try:
        connection = connect(ORIGINAL_DB, password)

    except OperationalError as exc:
        # Connection-startup errors may have pgcode=None.
        # Inspect only the reason; never print credentials.
        message = str(exc).lower()

        permission_denied = (
            "permission denied for database" in message
            or "does not have connect privilege" in message
        )

        if permission_denied and ORIGINAL_DB in message:
            print("PASS: Original database access denied.")
            return True

        print("INCONCLUSIVE: Connection rejected for another reason.")
        print("SQLSTATE:", exc.pgcode)
        return False

    else:
        connection.close()
        print("FAIL: Original database connection succeeded.")
        return False


def main():
    password = getpass(
        "Enter wardrobe_integration password: "
    )

    integration_passed = verify_integration(password)

    if not integration_passed:
        raise SystemExit(1)

    original_passed = verify_original_denied(password)

    if not original_passed:
        raise SystemExit(1)

    print("\n=== FINAL RESULT ===")
    print("Integration authentication: PASS")
    print("Restricted database privileges: PASS")
    print("Original database isolation: PASS")
    print("Maintenance access: Requires separate hardening")
    print("\nNo database changes were performed.")


if __name__ == "__main__":
    main()
