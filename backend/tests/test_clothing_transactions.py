
"""Test clothing database transactions and rollback behavior.

All tests use an isolated in-memory SQLite database.
No existing PostgreSQL data is accessed or modified.
"""

import os
import unittest

os.environ.setdefault("DATABASE_URL", "sqlite://")
os.environ.setdefault(
    "JWT_SECRET_KEY",
    "test-only-key-not-for-deployment-0123456789",
)

from sqlalchemy import create_engine, event
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
import app.models

from app.models.user import User
from app.models.clothing import Clothing

from app.schemas.clothing_schema import (
    ClothingCreate,
    ClothingUpdate,
)

from app.services.clothing_service import (
    create_clothing,
    update_clothing,
)


class ClothingTransactionTests(unittest.TestCase):

    def setUp(self):

        # =====================================
        # CREATE AN ISOLATED TEST DATABASE
        # =====================================

        self.engine = create_engine(
            "sqlite://",
            connect_args={
                "check_same_thread": False,
            },
            poolclass=StaticPool,
        )

        self.addCleanup(self.engine.dispose)

        # Enable foreign key validation in SQLite.
        @event.listens_for(self.engine, "connect")
        def enable_foreign_keys(connection, _):
            connection.execute("PRAGMA foreign_keys=ON")

        Base.metadata.create_all(self.engine)

        self.factory = sessionmaker(bind=self.engine)

        # =====================================
        # CREATE TEST USER AND CLOTHING
        # =====================================

        with self.factory() as db:

            user = User(
                username="transaction_user",
                email="transaction@example.test",
                password_hash="unused-test-hash",
                is_active=True,
            )

            db.add(user)
            db.flush()

            self.user_id = user.id

            clothing = Clothing(
                user_id=self.user_id,
                name="Original Hoodie",
                purchase_price=50.0,
                times_worn=2,
            )

            db.add(clothing)
            db.flush()

            self.clothing_id = clothing.id

            db.commit()

    # =====================================
    # TEST 1: FAILED CREATION ROLLS BACK
    # =====================================

    def test_failed_creation_rolls_back_transaction(self):

        with self.factory() as db:

            # This brand does not exist in our test DB.
            invalid_clothing = ClothingCreate(
                name="Invalid Brand Jacket",
                brand_id=999999,
            )

            # The database should reject the foreign key.
            with self.assertRaises(IntegrityError):

                create_clothing(
                    db=db,
                    user_id=self.user_id,
                    clothing=invalid_clothing,
                )

            # The session should be usable after rollback.
            self.assertTrue(
                db.is_active,
                "Session was not rolled back after failure.",
            )

            # No invalid clothing was saved.
            self.assertEqual(
                db.query(Clothing).count(),
                1,
            )

            # Verify a valid creation still works.
            valid_clothing = ClothingCreate(
                name="Valid Jacket",
            )

            created = create_clothing(
                db=db,
                user_id=self.user_id,
                clothing=valid_clothing,
            )

            self.assertIsNotNone(created.id)

            self.assertEqual(
                db.query(Clothing).count(),
                2,
            )

    # =====================================
    # TEST 2: FAILED UPDATE ROLLS BACK
    # =====================================

    def test_failed_update_preserves_original_clothing(self):

        with self.factory() as db:

            # Attempt to assign a nonexistent brand.
            invalid_update = ClothingUpdate(
                name="Modified Hoodie",
                brand_id=999999,
            )

            with self.assertRaises(IntegrityError):

                update_clothing(
                    db=db,
                    clothing_id=self.clothing_id,
                    user_id=self.user_id,
                    clothing_data=invalid_update,
                )

            # The session should recover from the error.
            self.assertTrue(
                db.is_active,
                "Session was not rolled back after failure.",
            )

            # The original clothing data must be preserved.
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

            # A valid update should still succeed.
            valid_update = ClothingUpdate(
                name="Recovered Hoodie",
            )

            updated = update_clothing(
                db=db,
                clothing_id=self.clothing_id,
                user_id=self.user_id,
                clothing_data=valid_update,
            )

            self.assertIsNotNone(updated)

            self.assertEqual(
                updated.name,
                "Recovered Hoodie",
            )


if __name__ == "__main__":
    unittest.main()
