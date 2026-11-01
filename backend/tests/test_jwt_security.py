import os
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from jose import jwt

# A synthetic key used only by this test process.
os.environ.setdefault(
    "JWT_SECRET_KEY",
    "unit-test-secret-not-for-production-2026"
)

from app.services import auth_service


class JWTExpirationTests(unittest.TestCase):

    def setUp(self):
        self.test_key = "isolated-jwt-test-key-2026"

        secret_patch = patch.object(
            auth_service,
            "SECRET_KEY",
            self.test_key
        )

        secret_patch.start()
        self.addCleanup(secret_patch.stop)

    def sign_token(self, payload, key=None):
        return jwt.encode(
            payload,
            key or self.test_key,
            algorithm="HS256"
        )

    def test_valid_token(self):
        token = auth_service.create_access_token({
            "user_id": 1
        })

        payload = auth_service.verify_token(token)

        self.assertIsNotNone(payload)
        self.assertEqual(payload["user_id"], 1)
        self.assertIn("exp", payload)

    def test_missing_expiration(self):
        token = self.sign_token({
            "user_id": 1
        })

        self.assertIsNone(
            auth_service.verify_token(token)
        )

    def test_expired_token(self):
        expired = datetime.now(timezone.utc) - timedelta(
            minutes=5
        )

        token = self.sign_token({
            "user_id": 1,
            "exp": expired
        })

        self.assertIsNone(
            auth_service.verify_token(token)
        )

    def test_malformed_expiration(self):
        token = self.sign_token({
            "user_id": 1,
            "exp": "invalid-date"
        })

        self.assertIsNone(
            auth_service.verify_token(token)
        )

    def test_null_expiration(self):
        token = self.sign_token({
            "user_id": 1,
            "exp": None
        })

        self.assertIsNone(
            auth_service.verify_token(token)
        )

    def test_invalid_signature(self):
        token = self.sign_token(
            {
                "user_id": 1,
                "exp": datetime.now(timezone.utc)
                       + timedelta(hours=1)
            },
            key="incorrect-signing-key"
        )

        self.assertIsNone(
            auth_service.verify_token(token)
        )


if __name__ == "__main__":
    unittest.main()