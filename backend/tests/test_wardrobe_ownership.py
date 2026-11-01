
"""Security tests for wardrobe ownership and user isolation.

These tests use an isolated in-memory SQLite database.
They never modify the existing PostgreSQL database.
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
from app.models.category import Category, SubCategory
from app.models.color import Color

from app.services.auth_service import create_access_token


class WardrobeOwnershipTests(unittest.TestCase):

    def setUp(self):

        # =====================================
        # ISOLATED DATABASE
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
        # CREATE TWO USERS
        # =====================================

        with self.factory() as db:

            owner = User(
                username="wardrobe_owner",
                email="owner@example.test",
                password_hash="unused-test-hash",
                is_active=True,
            )

            other = User(
                username="wardrobe_other",
                email="other@example.test",
                password_hash="unused-test-hash",
                is_active=True,
            )

            tops = Category(name="Tops")
            bottoms = Category(name="Bottoms")

            black = Color(
                name="Ownership Test Black",
                slug="ownership-test-black",
                hex_code="#111111",
                color_family="Black",
                is_neutral=True,
            )

            db.add_all([
                owner,
                other,
                tops,
                bottoms,
                black,
            ])

            db.flush()

            top_subcategory = SubCategory(
                name="T-Shirt",
                category_id=tops.id,
            )

            bottom_subcategory = SubCategory(
                name="Jeans",
                category_id=bottoms.id,
            )

            db.add_all([
                top_subcategory,
                bottom_subcategory,
            ])

            db.flush()

            # User A owns two clothing items.
            owner_top = Clothing(
                user_id=owner.id,
                name="Owner T-Shirt",
                subcategory_id=top_subcategory.id,
                color_id=black.id,
            )

            owner_bottom = Clothing(
                user_id=owner.id,
                name="Owner Jeans",
                subcategory_id=bottom_subcategory.id,
                color_id=black.id,
            )

            # User B owns a separate clothing item.
            foreign_item = Clothing(
                user_id=other.id,
                name="Other User Jeans",
                subcategory_id=bottom_subcategory.id,
                color_id=black.id,
            )

            db.add_all([
                owner_top,
                owner_bottom,
                foreign_item,
            ])

            db.flush()

            self.owner_id = owner.id
            self.other_id = other.id

            self.owner_top_id = owner_top.id
            self.owner_bottom_id = owner_bottom.id
            self.foreign_item_id = foreign_item.id

            db.commit()

        # =====================================
        # AUTHENTICATION
        # =====================================

        self.owner_headers = {
            "Authorization": (
                "Bearer "
                + create_access_token(
                    {"user_id": self.owner_id}
                )
            )
        }

        self.other_headers = {
            "Authorization": (
                "Bearer "
                + create_access_token(
                    {"user_id": self.other_id}
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
    # TEST 1: WARDROBE ISOLATION
    # =====================================

    def test_users_only_see_their_own_wardrobe(self):

        owner_response = self.client.get(
            "/clothing",
            headers=self.owner_headers,
        )

        other_response = self.client.get(
            "/clothing",
            headers=self.other_headers,
        )

        self.assertEqual(owner_response.status_code, 200)
        self.assertEqual(other_response.status_code, 200)

        owner_ids = {
            item["id"]
            for item in owner_response.json()
        }

        other_ids = {
            item["id"]
            for item in other_response.json()
        }

        self.assertEqual(
            owner_ids,
            {self.owner_top_id, self.owner_bottom_id},
        )

        self.assertEqual(
            other_ids,
            {self.foreign_item_id},
        )

    # =====================================
    # TEST 2: UNAUTHORIZED UPDATE
    # =====================================

    def test_user_cannot_update_another_users_clothing(self):

        response = self.client.put(
            f"/clothing/{self.owner_top_id}",
            json={
                "name": "Unauthorized Modification",
            },
            headers=self.other_headers,
        )

        self.assertEqual(response.status_code, 404)

        with self.factory() as db:
            clothing = db.get(
                Clothing,
                self.owner_top_id,
            )

            self.assertIsNotNone(clothing)
            self.assertEqual(
                clothing.name,
                "Owner T-Shirt",
            )
            self.assertEqual(
                clothing.user_id,
                self.owner_id,
            )

    # =====================================
    # TEST 3: UNAUTHORIZED DELETION
    # =====================================

    def test_user_cannot_delete_another_users_clothing(self):

        response = self.client.delete(
            f"/clothing/{self.owner_top_id}",
            headers=self.other_headers,
        )

        self.assertEqual(response.status_code, 404)

        with self.factory() as db:
            clothing = db.get(
                Clothing,
                self.owner_top_id,
            )

            self.assertIsNotNone(clothing)
            self.assertEqual(
                clothing.user_id,
                self.owner_id,
            )

    # =====================================
    # TEST 4: MATCHING PRIVACY
    # =====================================

    def test_matching_does_not_expose_other_users_items(self):

        owner_response = self.client.get(
            f"/clothing/{self.owner_top_id}/matches",
            headers=self.owner_headers,
        )

        self.assertEqual(owner_response.status_code, 200)

        result = owner_response.json()

        self.assertEqual(
            result["base_item"]["id"],
            self.owner_top_id,
        )

        match_ids = {
            match["clothing"]["id"]
            for match in result["matches"]
        }

        self.assertEqual(
            match_ids,
            {self.owner_bottom_id},
        )

        self.assertNotIn(
            self.foreign_item_id,
            match_ids,
        )

        # User B must not access User A's matches.
        unauthorized = self.client.get(
            f"/clothing/{self.owner_top_id}/matches",
            headers=self.other_headers,
        )

        self.assertEqual(
            unauthorized.status_code,
            404,
        )

        # User A must not access User B's matches.
        reverse = self.client.get(
            f"/clothing/{self.foreign_item_id}/matches",
            headers=self.owner_headers,
        )

        self.assertEqual(
            reverse.status_code,
            404,
        )

    # =====================================
    # TEST 5: OWNERSHIP SPOOFING
    # =====================================

    def test_create_clothing_cannot_assign_another_owner(self):

        # User B tries to assign new clothing to User A.
        response = self.client.post(
            "/clothing",
            json={
                "name": "Ownership Spoof Attempt",
                "user_id": self.owner_id,
            },
            headers=self.other_headers,
        )

        self.assertEqual(response.status_code, 200)

        created = response.json()

        # The backend must use the authenticated user.
        self.assertEqual(
            created["user_id"],
            self.other_id,
        )

        with self.factory() as db:
            clothing = db.get(
                Clothing,
                created["id"],
            )

            self.assertIsNotNone(clothing)
            self.assertEqual(
                clothing.user_id,
                self.other_id,
            )


if __name__ == "__main__":
    unittest.main()
