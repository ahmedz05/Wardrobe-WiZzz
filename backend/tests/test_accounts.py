
"""Account and authentication tests using an isolated in-memory database."""

import os
import unittest
from unittest.mock import patch

# Synthetic configuration for testing only.
os.environ.setdefault("DATABASE_URL", "sqlite://")
os.environ.setdefault(
    "JWT_SECRET_KEY",
    "test-only-key-not-for-deployment-0123456789"
)

from fastapi.testclient import TestClient
from jose import jwt
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app import database
from app.services import auth_service

# Ensure importing the API cannot create database tables.
with patch.object(database.Base.metadata, "create_all"):
    from app.main import app

from app.models.user import User
from app.routes import user_routes
from app.services import auth_dependencies, user_service


class AccountTests(unittest.TestCase):

    def setUp(self):
        # Create a fresh in-memory SQLite database for each test.
        self.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool
        )

        database.Base.metadata.create_all(self.engine)

        self.open_sessions = set()
        open_sessions = self.open_sessions
        self_engine = self.engine

        class TrackedSession(Session):

            def __init__(self):
                super().__init__(
                    bind=self_engine,
                    expire_on_commit=False
                )
                open_sessions.add(self)

            def close(self):
                super().close()
                open_sessions.discard(self)

        self.factory = TrackedSession

        self.patches = [
            patch.object(
                module,
                "SessionLocal",
                self.factory,
                create=True
            )
            for module in (
                database,
                user_routes,
                user_service,
                auth_dependencies
            )
        ]

        for replacement in self.patches:
            replacement.start()

        self.client = TestClient(
            app,
            raise_server_exceptions=False
        )

        self.account = {
            "username": "integration_account",
            "email": "account@example.test",
            "password": "Test-only-pass-2026"
        }

    def tearDown(self):
        self.client.close()

        for session in list(self.open_sessions):
            session.close()

        for replacement in reversed(self.patches):
            replacement.stop()

        self.engine.dispose()

    # =====================================
    # TEST 1: REGISTRATION, LOGIN, AND ME
    # =====================================

    def test_registration_login_and_me_keep_the_real_contract(self):
        registered = self.client.post(
            "/register",
            json=self.account
        )

        self.assertEqual(registered.status_code, 200)
        self.assertEqual(
            set(registered.json()),
            {"id", "username", "email"}
        )

        logged_in = self.client.post(
            "/login",
            json={
                "email": self.account["email"],
                "password": self.account["password"]
            }
        )

        self.assertEqual(logged_in.status_code, 200)
        self.assertEqual(
            logged_in.json()["token_type"],
            "bearer"
        )

        token = logged_in.json()["access_token"]

        me = self.client.get(
            "/me",
            headers={
                "Authorization": f"Bearer {token}"
            }
        )

        self.assertEqual(me.status_code, 200)
        self.assertEqual(
            me.json(),
            registered.json()
        )

    # =====================================
    # TEST 2: DUPLICATE REGISTRATION
    # =====================================

    def test_duplicate_registration_is_a_controlled_conflict(self):
        first = self.client.post(
            "/register",
            json=self.account
        )

        self.assertEqual(first.status_code, 200)

        duplicate = self.client.post(
            "/register",
            json=self.account
        )

        self.assertEqual(duplicate.status_code, 409)

        with Session(self.engine) as session:
            self.assertEqual(
                session.query(User).count(),
                1
            )

    # =====================================
    # TEST 3: SUCCESSFUL LOGIN SESSION
    # =====================================

    def test_successful_login_closes_its_database_session(self):
        self.client.post(
            "/register",
            json=self.account
        )

        response = self.client.post(
            "/login",
            json={
                "email": self.account["email"],
                "password": self.account["password"]
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(self.open_sessions), 0)

    # =====================================
    # TEST 4: REJECTED LOGIN SESSION
    # =====================================

    def test_rejected_login_closes_its_database_session(self):
        response = self.client.post(
            "/login",
            json={
                "email": "missing@example.test",
                "password": "wrong-password"
            }
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(len(self.open_sessions), 0)

    # =====================================
    # TEST 5: INVALID USER IDENTITY
    # =====================================

    def test_invalid_identity_claim_returns_401_not_500(self):
        token = auth_service.create_access_token({
            "sub": "account@example.test"
        })

        response = self.client.get(
            "/me",
            headers={
                "Authorization": f"Bearer {token}"
            }
        )

        self.assertEqual(response.status_code, 401)

    # =====================================
    # TEST 6: MISSING JWT EXPIRATION
    # =====================================

    def test_missing_expiration_returns_http_401(self):
        registered = self.client.post(
            "/register",
            json=self.account
        )

        self.assertEqual(registered.status_code, 200)

        user_id = registered.json()["id"]

        # Valid signature but no expiration claim.
        token = jwt.encode(
            {
                "user_id": user_id
            },
            auth_service.SECRET_KEY,
            algorithm=auth_service.ALGORITHM
        )

        response = self.client.get(
            "/me",
            headers={
                "Authorization": f"Bearer {token}"
            }
        )

        self.assertEqual(response.status_code, 401)

    # =====================================
    # TEST 7: NULL JWT EXPIRATION
    # =====================================

    def test_null_expiration_returns_http_401(self):
        registered = self.client.post(
            "/register",
            json=self.account
        )

        self.assertEqual(registered.status_code, 200)

        user_id = registered.json()["id"]

        # A malformed expiration value must not crash FastAPI.
        token = jwt.encode(
            {
                "user_id": user_id,
                "exp": None
            },
            auth_service.SECRET_KEY,
            algorithm=auth_service.ALGORITHM
        )

        response = self.client.get(
            "/me",
            headers={
                "Authorization": f"Bearer {token}"
            }
        )

        self.assertEqual(response.status_code, 401)


if __name__ == "__main__":
    unittest.main()
