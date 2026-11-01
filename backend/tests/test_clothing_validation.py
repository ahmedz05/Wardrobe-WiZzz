
"""Clothing input validation and database integrity tests.

Tests run against an isolated in-memory SQLite database.
Existing PostgreSQL data is never accessed or modified.
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
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models.user import User
from app.models.clothing import Clothing
from app.services.auth_service import create_access_token


class ClothingValidationTests(unittest.TestCase):

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
                username="validation_user",
                email="validation@example.test",
                password_hash="unused-test-hash",
                is_active=True,
            )

            db.add(user)
            db.flush()

            clothing = Clothing(
                user_id=user.id,
                name="Original Hoodie",
                purchase_price=40.0,
                times_worn=2,
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
    # DATABASE HELPERS
    # =====================================

    def clothing_count(self):
        with self.factory() as db:
            return db.query(Clothing).count()

    def clothing_snapshot(self):
        with self.factory() as db:
            item = db.get(Clothing, self.clothing_id)

            return {
                "name": item.name,
                "purchase_price": item.purchase_price,
                "times_worn": item.times_worn,
                "subcategory_id": item.subcategory_id,
                "color_id": item.color_id,
            }

    # =====================================
    # TEST 1: REJECT INVALID CREATION DATA
    # =====================================

    def test_invalid_creation_returns_422_without_writing(self):
        invalid_payloads = [
            {"name": ""},
            {"name": "   "},
            {"name": "X" * 121},
            {},
            {"name": "Test Jacket", "purchase_price": -100},
            {"name": "Test Jacket", "times_worn": -5},
            {"name": "Test Jacket", "color_id": 0},
            {"name": "Test Jacket", "brand_id": -1},
            {"name": "Test Jacket", "material_id": 0},
            {"name": "Test Jacket", "subcategory_id": -3},
            {"name": "Test Jacket", "purchase_price": "Infinity"},
        ]

        original_count = self.clothing_count()

        for payload in invalid_payloads:
            with self.subTest(payload=payload):
                response = self.client.post(
                    "/clothing",
                    json=payload,
                    headers=self.headers,
                )

                self.assertEqual(
                    response.status_code,
                    422,
                )

                self.assertEqual(
                    self.clothing_count(),
                    original_count,
                )

    # =====================================
    # TEST 2: REJECT INVALID UPDATES
    # =====================================

    def test_invalid_update_preserves_original_record(self):
        invalid_updates = [
            {"name": ""},
            {"name": "   "},
            {"name": "X" * 121},
            {"name": "Changed", "purchase_price": -20},
            {"name": "Changed", "times_worn": -2},
            {"name": "Changed", "color_id": 0},
            {"name": "Changed", "subcategory_id": -1},
            {"name": "Changed", "purchase_price": "Infinity"},
        ]

        original = self.clothing_snapshot()

        for payload in invalid_updates:
            with self.subTest(payload=payload):
                response = self.client.put(
                    f"/clothing/{self.clothing_id}",
                    json=payload,
                    headers=self.headers,
                )

                self.assertEqual(
                    response.status_code,
                    422,
                )

                self.assertEqual(
                    self.clothing_snapshot(),
                    original,
                )

    # =====================================
    # TEST 3: NORMALIZE CLOTHING NAMES
    # =====================================

    def test_valid_creation_trims_clothing_name(self):
        response = self.client.post(
            "/clothing",
            json={
                "name": "   Denim Jacket   ",
                "purchase_price": 75.50,
                "times_worn": 3,
            },
            headers=self.headers,
        )

        self.assertEqual(response.status_code, 200)

        created = response.json()

        self.assertEqual(
            created["name"],
            "Denim Jacket",
        )

        self.assertEqual(
            created["user_id"],
            self.user_id,
        )

        self.assertEqual(
            created["purchase_price"],
            75.50,
        )

        self.assertEqual(
            created["times_worn"],
            3,
        )

    # =====================================
    # TEST 4: VALID UPDATES STILL WORK
    # =====================================

    def test_valid_update_still_works(self):
        response = self.client.put(
            f"/clothing/{self.clothing_id}",
            json={
                "name": "   Updated Hoodie   ",
                "purchase_price": 55.0,
                "times_worn": 5,
            },
            headers=self.headers,
        )

        self.assertEqual(response.status_code, 200)

        updated = response.json()

        self.assertEqual(
            updated["name"],
            "Updated Hoodie",
        )

        self.assertEqual(
            updated["purchase_price"],
            55.0,
        )

        self.assertEqual(
            updated["times_worn"],
            5,
        )

        with self.factory() as db:
            clothing = db.get(
                Clothing,
                self.clothing_id,
            )

            self.assertEqual(
                clothing.name,
                "Updated Hoodie",
            )

            self.assertEqual(
                clothing.user_id,
                self.user_id,
            )

    # =====================================
    # TEST 5: PRESERVE CURRENT UPDATE CONTRACT
    # =====================================

    def test_update_without_name_is_rejected(self):
        original = self.clothing_snapshot()

        response = self.client.put(
            f"/clothing/{self.clothing_id}",
            json={
                "times_worn": 10,
            },
            headers=self.headers,
        )

        # The current ClothingUpdate schema requires name.
        self.assertEqual(response.status_code, 422)

        self.assertEqual(
            self.clothing_snapshot(),
            original,
        )


if __name__ == "__main__":
    unittest.main()
