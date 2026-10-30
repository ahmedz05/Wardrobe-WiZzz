"""Read-only target diagnostics, never database setup or permission to run writes.

Configured database separation does not attest a running API or replace
least-privilege roles. Publication tests mock all filesystem/database I/O here.
"""
from contextlib import closing

import psycopg2
from sqlalchemy.engine import make_url

from local_config import ROOT, read_environment

TEST_DATABASE = "wardrobe_wizzz_integration_20261030"


def connect(url, *, readonly=True):
    if not readonly:
        raise RuntimeError("This helper permits read-only connections only.")
    if url.get_backend_name() != "postgresql" or url.host not in {"localhost", "127.0.0.1"}:
        raise RuntimeError("Only local PostgreSQL targets are supported.")
    return psycopg2.connect(host=url.host, port=url.port or 5432, user=url.username,
                            password=url.password, dbname=url.database,
                            options="-c statement_timeout=10000 -c default_transaction_read_only=on",
                            connect_timeout=5)


def environment():
    source_values = read_environment(ROOT / "backend/.env.local")
    target_values = read_environment(ROOT / "backend/.env.integration")
    source = make_url(source_values["DATABASE_URL"])
    target = make_url(target_values["DATABASE_URL"])
    if source.database != "wardrobe_wizzz" or target.database != TEST_DATABASE:
        raise RuntimeError("Unexpected source or integration database.")
    if any(url.get_backend_name() != "postgresql" or
           url.host not in {"localhost", "127.0.0.1"} for url in (source, target)):
        raise RuntimeError("Only local PostgreSQL targets are supported.")
    if not source_values["JWT_SECRET_KEY"] or not target_values["JWT_SECRET_KEY"]:
        raise RuntimeError("Signing keys must be configured.")
    if source_values["JWT_SECRET_KEY"] == target_values["JWT_SECRET_KEY"]:
        raise RuntimeError("Integration and source signing keys must be separate.")
    identities = []
    for url in (source, target):
        with closing(connect(url, readonly=True)) as db, db, db.cursor() as cursor:
            cursor.execute("SELECT current_database(), oid FROM pg_database WHERE datname=current_database()")
            name, oid = cursor.fetchone()
            if name != url.database:
                raise RuntimeError("Unexpected connected database.")
            identities.append((url.host, url.port or 5432, oid))
    if identities[0] == identities[1]:
        raise RuntimeError("Database identities are not isolated.")
    return source, target, target_values
