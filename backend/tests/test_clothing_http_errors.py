
"""API-level tests for safe clothing database error handling.

Tests run using an isolated in-memory SQLite database.
No existing PostgreSQL database is accessed.
"""

import os
import unittest
from unittest.mock import patch

os.environ.setdefault("DATABASE_URL", "sqlite://")
os.environ.setdefault(
    "JWT_SECRET_KEY",
    "test-only-key-not-for-deployment-0123456789",
)

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

from app.models.user import User
from app.models.clothing import Clothing

from app.services.auth_service import create_access_token


class ClothingHTTPErrorTests(unittest.TestCase):

    def setUp(self):

        # =====================================
        # ISOLATED TEST DATABASE
        # =====================================

        self.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )

        self.addCleanup(self.engine.dispose)

        @event.listens_for(self.engine, "connect")
        def enable_foreign_keys(connection, _):
            connection.execute("PRAGMA foreign_keys=ON")

        Base.metadata.create_all(self.engine)

        self.factory = sessionmaker(bind=self.engine)

        def isolated_database():
            with self.factory() as db:
                yield db

        self.enterContext(
            patch.dict(
                app.dependency_overrides,
                {get_db: isolated_database},
            )
        )

        # =====================================
        # CREATE TEST USER AND CLOTHING
        # =====================================

        with self.factory() as db:

            user = User(
                username="http_error_user",
                email="http_errors@example.test",
                password_hash="unused-test-hash",
                is_active=True,
            )

            db.add(user)
            db.flush()

            clothing = Clothing(
                user_id=user.id,
                name="Original Hoodie",
                purchase_price=45.0,
            )

            db.add(clothing)
            db.flush()

            self.user_id = user.id
            self.clothing_id = clothing.id

            db.commit()

        self.headers = {
            "Authorization": (
                "Bearer "
                + create_access_token(
                    {"user_id": self.user_id}
                )
            )
        }

        self.client = self.enterContext(
            TestClient(
                app,
                raise_server_exceptions=False,
            )
        )

    # =====================================
    # TEST 1: FAILED CREATION RETURNS 409
    # =====================================

    def test_invalid_foreign_key_creation_returns_409(self):

        response = self.client.post(
            "/clothing",
            json={
                "name": "Invalid Brand Jacket",
                "brand_id": 999999,
            },
            headers=self.headers,
        )

        # Expected database constraint conflict.
        self.assertEqual(response.status_code, 409)

        # The response must not expose SQL details.
        self.assertEqual(
            response.json()["detail"],
            "Clothing data violates database constraints.",
        )

        self.assertNotIn(
            "FOREIGN KEY",
            response.text,
        )

        # Failed creation must leave database unchanged.
        with self.factory() as db:
            self.assertEqual(
                db.query(Clothing).count(),
                1,
            )

        # A subsequent valid request should succeed.
        valid_response = self.client.post(
            "/clothing",
            json={
                "name": "Valid Jacket",
            },
            headers=self.headers,
        )

        self.assertEqual(valid_response.status_code, 200)

    # =====================================
    # TEST 2: FAILED UPDATE RETURNS 409
    # =====================================

    def test_invalid_foreign_key_update_returns_409(self):

        response = self.client.put(
            f"/clothing/{self.clothing_id}",
            json={
                "name": "Modified Hoodie",
                "brand_id": 999999,
            },
            headers=self.headers,
        )

        self.assertEqual(response.status_code, 409)

        self.assertEqual(
            response.json()["detail"],
            "Clothing data violates database constraints.",
        )

        self.assertNotIn(
            "FOREIGN KEY",
            response.text,
        )

        # Original clothing data must be preserved.
        with self.factory() as db:

            clothing = db.get(
                Clothing,
                self.clothing_id,
            )

            self.assertEqual(
                clothing.name,
                "Original Hoodie",
            )

            self.assertIsNone(
                clothing.brand_id,
            )

        # A valid update must still work.
        valid_response = self.client.put(
            f"/clothing/{self.clothing_id}",
            json={
                "name": "Recovered Hoodie",
            },
            headers=self.headers,
        )

        self.assertEqual(valid_response.status_code, 200)

        self.assertEqual(
            valid_response.json()["name"],
            "Recovered Hoodie",
        )


if __name__ == "__main__":
    unittest.main()
