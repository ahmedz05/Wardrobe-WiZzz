"""Safety regressions: these checks never connect to an existing database."""
import os
import subprocess
import sys
import unittest
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]


class StartupTests(unittest.TestCase):
    def run_python(self, source):
        env = {**os.environ, "DATABASE_URL": "sqlite://", "JWT_SECRET_KEY": "test-only-key-not-for-deployment-0123456789"}
        return subprocess.run([sys.executable, "-c", source], cwd=BACKEND,
                              env=env, capture_output=True, text=True)

    def test_import_never_creates_database_tables(self):
        result = self.run_python(
            "from unittest.mock import patch; from sqlalchemy import MetaData; "
            "guard=patch.object(MetaData, 'create_all', side_effect=AssertionError('startup attempted schema creation')); "
            "guard.start(); import app.main"
        )
        self.assertEqual(result.returncode, 0, "Import attempted to create schema; no SQL was executed.")

    def test_database_selection_uses_environment_before_import(self):
        result = self.run_python("from app.database import engine; assert engine.url.get_backend_name() == 'sqlite'")
        self.assertEqual(result.returncode, 0, "DATABASE_URL was ignored.")

    def test_token_signing_uses_the_environment_key(self):
        result = self.run_python(
            "import os; from jose import jwt; from app.services.auth_service import create_access_token; "
            "token=create_access_token({'sub':'account@example.test','user_id':7}); "
            "assert jwt.decode(token, os.environ['JWT_SECRET_KEY'], algorithms=['HS256'])['user_id'] == 7"
        )
        self.assertEqual(result.returncode, 0, "JWT_SECRET_KEY was ignored.")


if __name__ == "__main__":
    unittest.main()
