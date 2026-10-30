"""Safety-boundary tests; never connect to PostgreSQL or call the API."""
import unittest
from unittest.mock import MagicMock, patch

from integration_safety import TEST_DATABASE, environment


class IntegrationSafetyTests(unittest.TestCase):
    def values(self, database, key="isolated-signing-key", host="localhost"):
        return {"DATABASE_URL": f"postgresql://test_only@{host}/{database}", "JWT_SECRET_KEY": key}

    def refused_before_connection(self, source, target):
        with patch("integration_safety.read_environment", side_effect=[source, target]), \
                patch("integration_safety.connect") as connection:
            with self.assertRaises(RuntimeError):
                environment()
            connection.assert_not_called()

    def test_refuses_real_database_as_target(self):
        self.refused_before_connection(self.values("wardrobe_wizzz", "source-key"),
                                       self.values("wardrobe_wizzz"))

    def test_refuses_unapproved_test_database(self):
        self.refused_before_connection(self.values("wardrobe_wizzz", "source-key"),
                                       self.values("another_database"))

    def test_refuses_remote_host(self):
        self.refused_before_connection(self.values("wardrobe_wizzz", "source-key"),
                                       self.values(TEST_DATABASE, host="remote.example.test"))

    def test_refuses_shared_signing_key(self):
        self.refused_before_connection(self.values("wardrobe_wizzz"), self.values(TEST_DATABASE))


    @staticmethod
    def connection(name, oid):
        db = MagicMock()
        db.__enter__.return_value = db
        cursor = db.cursor.return_value
        cursor.__enter__.return_value = cursor
        cursor.fetchone.return_value = (name, oid)
        return db

    def test_valid_target_checks_are_read_only_and_close_both_connections(self):
        source = self.values("wardrobe_wizzz", "source-key")
        target = self.values(TEST_DATABASE)
        databases = [self.connection("wardrobe_wizzz", 1), self.connection(TEST_DATABASE, 2)]
        with patch("integration_safety.read_environment", side_effect=[source, target]), \
                patch("integration_safety.connect", side_effect=databases) as connection:
            actual = environment()
            self.assertEqual(actual[1].database, TEST_DATABASE)
            self.assertTrue(all(call.kwargs == {"readonly": True} for call in connection.call_args_list))
        for db in databases:
            db.close.assert_called_once()

    def test_connected_identity_mismatch_closes_connection_and_stops(self):
        db = self.connection("unexpected", 1)
        with patch("integration_safety.read_environment", side_effect=[
                self.values("wardrobe_wizzz", "source-key"), self.values(TEST_DATABASE)]), \
                patch("integration_safety.connect", return_value=db):
            with self.assertRaises(RuntimeError):
                environment()
        db.close.assert_called_once()

    def test_non_postgresql_configuration_is_refused_before_connection(self):
        source = {"DATABASE_URL": "sqlite://", "JWT_SECRET_KEY": "source-key"}
        self.refused_before_connection(source, self.values(TEST_DATABASE))

    def test_read_write_connections_are_never_opened(self):
        from integration_safety import connect
        from sqlalchemy.engine import make_url
        with patch("integration_safety.psycopg2.connect") as database:
            with self.assertRaises(RuntimeError):
                connect(make_url(self.values(TEST_DATABASE)["DATABASE_URL"]), readonly=False)
            database.assert_not_called()



if __name__ == "__main__":
    unittest.main()
