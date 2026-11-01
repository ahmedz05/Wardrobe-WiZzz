"""Real route/ORM tests in a separate in-memory database, never the local wardrobe."""
import os
import unittest
from unittest.mock import patch

os.environ.setdefault("DATABASE_URL", "sqlite://")
os.environ.setdefault("JWT_SECRET_KEY", "test-only-key-not-for-deployment-0123456789")

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app import database

# The original app creates schema on import. Block that side effect until it is fixed.
with patch.object(database.Base.metadata, "create_all"):
    from app.main import app

from app.models.user import User
from app.routes import user_routes
from app.services import auth_dependencies, user_service


class AccountTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
        database.Base.metadata.create_all(self.engine)
        self.open_sessions = set()
        open_sessions = self.open_sessions

        class TrackedSession(Session):
            def __init__(self):
                super().__init__(bind=self_engine, expire_on_commit=False)
                open_sessions.add(self)

            def close(self):
                super().close()
                open_sessions.discard(self)

        self_engine = self.engine
        self.factory = TrackedSession
        self.patches = [patch.object(module, "SessionLocal", self.factory, create=True)
                        for module in (database, user_routes, user_service, auth_dependencies)]
        for replacement in self.patches:
            replacement.start()
        self.client = TestClient(app, raise_server_exceptions=False)
        self.account = {"username": "integration_account", "email": "account@example.test", "password": "Test-only-pass-2026"}

    def tearDown(self):
        self.client.close()
        for session in list(self.open_sessions):
            session.close()
        for replacement in reversed(self.patches):
            replacement.stop()
        self.engine.dispose()

    def test_registration_login_and_me_keep_the_real_contract(self):
        registered = self.client.post("/register", json=self.account)
        self.assertEqual(registered.status_code, 200)
        self.assertEqual(set(registered.json()), {"id", "username", "email"})
        logged_in = self.client.post("/login", json={k: self.account[k] for k in ("email", "password")})
        self.assertEqual(logged_in.status_code, 200)
        self.assertEqual(logged_in.json()["token_type"], "bearer")
        me = self.client.get("/me", headers={"Authorization": f"Bearer {logged_in.json()['access_token']}"})
        self.assertEqual(me.json(), registered.json())

    def test_duplicate_registration_is_a_controlled_conflict(self):
        self.assertEqual(self.client.post("/register", json=self.account).status_code, 200)
        duplicate = self.client.post("/register", json=self.account)
        self.assertEqual(duplicate.status_code, 409)
        with Session(self.engine) as session:
            self.assertEqual(session.query(User).count(), 1)

    def test_successful_login_closes_its_database_session(self):
        self.client.post("/register", json=self.account)
        response = self.client.post("/login", json={k: self.account[k] for k in ("email", "password")})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(self.open_sessions), 0)

    def test_rejected_login_closes_its_database_session(self):
        response = self.client.post("/login", json={"email": "missing@example.test", "password": "wrong-password"})
        self.assertEqual(response.status_code, 401)
        self.assertEqual(len(self.open_sessions), 0)

    def test_invalid_identity_claim_returns_401_not_500(self):
        from app.services.auth_service import create_access_token
        token = create_access_token({"sub": "account@example.test"})
        self.assertEqual(self.client.get("/me", headers={"Authorization": f"Bearer {token}"}).status_code, 401)


if __name__ == "__main__":
    unittest.main()
