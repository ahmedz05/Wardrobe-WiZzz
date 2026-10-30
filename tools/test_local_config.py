"""Local configuration and launcher checks using synthetic files, never PostgreSQL."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from local_config import read_environment


class LocalConfigurationTests(unittest.TestCase):
    def test_quoted_values_special_characters_and_comments_are_preserved(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / ".env.test"
            values = {"DATABASE_URL": "postgresql://fixture:p%40ss%3Aword@127.0.0.1/test",
                      "JWT_SECRET_KEY": "synthetic-test-key-with-#-and-" + chr(34)}
            text = "# synthetic fixture\n\n" + "".join(
                f"{key}={json.dumps(value)}\n" for key, value in values.items())
            path.write_text(text, encoding="utf-8-sig")
            before = path.read_bytes()
            self.assertEqual(read_environment(path), values)
            self.assertEqual(path.read_bytes(), before)

    def test_unquoted_values_and_whitespace_are_supported(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / ".env.test"
            path.write_text(" DATABASE_URL = sqlite:// \nJWT_SECRET_KEY=test-fixture\n")
            self.assertEqual(read_environment(path),
                             {"DATABASE_URL": "sqlite://", "JWT_SECRET_KEY": "test-fixture"})

    def test_malformed_entries_fail_without_echoing_values(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / ".env.test"
            for text in ("sensitive-fixture-without-separator", 'JWT_SECRET_KEY="unterminated'):
                path.write_text(text)
                with self.assertRaises(ValueError) as caught:
                    read_environment(path)
                self.assertNotIn(text, str(caught.exception))

    def test_launcher_help_needs_no_excluded_bootstrap_or_database(self):
        root = Path(__file__).resolve().parents[1]
        result = subprocess.run([sys.executable, "-B", str(root / "tools/run_backend.py"), "--help"],
                                cwd=root, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("--env-file", result.stdout)


if __name__ == "__main__":
    unittest.main()
