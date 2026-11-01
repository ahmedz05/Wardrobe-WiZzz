"""Catalog policy and wardrobe regressions using only new in-memory SQLite.

The real routes, JWT validation, ORM and recommendation scoring run unchanged.
Only database selection is replaced; no existing PostgreSQL database is accessed.
"""
import os
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

os.environ.setdefault("DATABASE_URL", "sqlite://")
os.environ.setdefault("JWT_SECRET_KEY", "test-only-key-not-for-deployment-0123456789")

from fastapi.routing import APIRoute
from fastapi.testclient import TestClient
from jose import jwt
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models.brand import Brand
from app.models.category import Category, SubCategory
from app.models.color import Color
from app.models.material import Material
from app.models.user import User
from app.services import category_service
from app.services.auth_service import ALGORITHM, SECRET_KEY, create_access_token


class CatalogAuthorizationTests(unittest.TestCase):
    def setUp(self):
        engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
        self.addCleanup(engine.dispose)
        self.engine = engine

        @event.listens_for(engine, "connect")
        def foreign_keys(connection, _):
            connection.execute("PRAGMA foreign_keys=ON")

        Base.metadata.create_all(engine)
        self.factory = sessionmaker(bind=engine)

        def isolated_database():
            with self.factory() as db:
                yield db

        self.enterContext(patch.dict(app.dependency_overrides, {get_db: isolated_database}))
        self.enterContext(patch.object(category_service, "SessionLocal", self.factory))
        self.client = self.enterContext(TestClient(app, raise_server_exceptions=False))
        with self.factory() as db:
            users = [User(username=f"catalog_user_{n}", email=f"catalog_{n}@example.test",
                          password_hash="unused-test-fixture", is_active=n != 2) for n in range(3)]
            brand = Brand(name="Read Brand", slug="read-brand", brand_type="Fashion")
            material = Material(name="Read Cotton", slug="read-cotton", material_type="Natural")
            colors = [Color(name=f"Read Neutral {n}", slug=f"read-neutral-{n}", hex_code="#111111",
                            color_family="Black", is_neutral=True) for n in range(2)]
            db.add_all([*users, brand, material, *colors])
            self.subcategories = {}
            for name in ("Tops", "Bottoms", "Shoes", "Outerwear"):
                category = Category(name=name)
                db.add(category)
                db.flush()
                subcategory = SubCategory(name=f"Test {name}", category_id=category.id)
                db.add(subcategory)
                db.flush()
                self.subcategories[name] = subcategory.id
                if name == "Tops":
                    self.category_id = category.id
            db.commit()
            self.user_id, self.other_id, self.inactive_id = [user.id for user in users]
            self.brand_id, self.material_id = brand.id, material.id
            self.color_id, self.second_color_id = [color.id for color in colors]
        self.auth = self.bearer(create_access_token({"user_id": self.user_id}))
        self.other_auth = self.bearer(create_access_token({"user_id": self.other_id}))
        self.garment_ids = self.create_wardrobe()

    @staticmethod
    def bearer(token):
        return {"Authorization": "Bearer " + token}

    def create_wardrobe(self):
        ids = []
        for category, warmth, layering in (("Tops", "Light", "Base"), ("Bottoms", "Medium", None),
                                            ("Shoes", "Light", None), ("Outerwear", "Heavy", "Outer")):
            payload = {"name": f"Synthetic {category}", "subcategory_id": self.subcategories[category],
                       "color_id": self.color_id, "material_id": self.material_id, "brand_id": self.brand_id,
                       "style": "Casual", "occasion": "Casual", "season": "All Season", "fit": "Regular",
                       "silhouette": "Regular", "warmth_level": warmth, "layering_role": layering}
            response = self.client.post("/clothing", json=payload, headers=self.auth)
            self.assertEqual(response.status_code, 200)
            ids.append(response.json()["id"])
        return ids

    def mutations(self):
        color = {"name": "Forbidden Blue", "slug": "forbidden-blue", "hex_code": "#334455", "color_family": "Blue"}
        material = {"name": "Forbidden Wool", "slug": "forbidden-wool", "material_type": "Natural"}
        return [
            ("POST", "/brands/", {"name": "Forbidden Brand", "slug": "forbidden-brand", "brand_type": "Fashion"}),
            ("POST", "/colors/", color),
            ("PUT", f"/colors/{self.color_id}", {**color, "name": "Forbidden Blue edited", "slug": "forbidden-blue-edited"}),
            ("DELETE", f"/colors/{self.color_id}", None),
            ("POST", "/materials/", material),
            ("PUT", f"/materials/{self.material_id}", {**material, "name": "Forbidden Wool edited", "slug": "forbidden-wool-edited"}),
            ("DELETE", f"/materials/{self.material_id}", None),
        ]

    def database_snapshot(self):
        with self.engine.connect() as connection:
            return {table.name: [tuple(row) for row in connection.execute(table.select().order_by(table.c.id))]
                    for table in Base.metadata.sorted_tables if "id" in table.c}

    def assert_mutations_denied(self, headers, expected):
        before = self.database_snapshot()
        for method, path, payload in self.mutations():
            with self.subTest(method=method, path=path):
                response = self.client.request(method, path, headers=headers, json=payload)
                self.assertEqual(response.status_code, expected)
                self.assertEqual(self.database_snapshot(), before, "Denied request changed catalog or user data")

    def test_all_seven_mutations_reject_anonymous_requests(self):
        self.assert_mutations_denied({}, 401)

    def test_all_seven_mutations_reject_invalid_tokens(self):
        self.assert_mutations_denied(self.bearer("not-a-valid-jwt"), 401)

    def test_all_seven_mutations_reject_wrong_signature(self):
        forged = jwt.encode({"user_id": self.user_id, "exp": datetime.now(timezone.utc) + timedelta(minutes=5)},
                            SECRET_KEY + "-wrong-key", algorithm=ALGORITHM)
        self.assert_mutations_denied(self.bearer(forged), 401)

    def test_all_seven_mutations_reject_expired_tokens(self):
        expired = jwt.encode({"user_id": self.user_id, "exp": datetime.now(timezone.utc) - timedelta(minutes=1)},
                             SECRET_KEY, algorithm=ALGORITHM)
        self.assert_mutations_denied(self.bearer(expired), 401)

    def test_all_seven_mutations_forbid_authenticated_ordinary_users(self):
        self.assertEqual(self.client.get("/me", headers=self.auth).status_code, 200)
        self.assert_mutations_denied(self.auth, 403)

    def test_all_seven_mutations_reject_inactive_users(self):
        self.assert_mutations_denied(self.bearer(create_access_token({"user_id": self.inactive_id})), 401)

    def test_all_seven_mutations_reject_nonexistent_users(self):
        self.assert_mutations_denied(self.bearer(create_access_token({"user_id": 999999})), 401)

    def test_admin_claims_cannot_bypass_default_deny(self):
        claimed = create_access_token({"user_id": self.user_id, "admin": True, "is_admin": True, "role": "admin"})
        self.assert_mutations_denied(self.bearer(claimed), 403)

    def test_each_registered_catalog_mutation_is_covered(self):
        actual = {(method, route.path) for route in app.routes if isinstance(route, APIRoute)
                  and route.path.startswith(("/categories", "/subcategories", "/brands", "/colors", "/materials"))
                  for method in route.methods & {"POST", "PUT", "PATCH", "DELETE"}}
        self.assertEqual(actual, {("POST", "/brands/"), ("POST", "/colors/"), ("PUT", "/colors/{color_id}"),
                                  ("DELETE", "/colors/{color_id}"), ("POST", "/materials/"),
                                  ("PUT", "/materials/{material_id}"), ("DELETE", "/materials/{material_id}")})

    def test_catalog_reads_remain_public_and_authenticated(self):
        paths = ["/categories", f"/categories/{self.category_id}/subcategories", "/brands/", f"/brands/{self.brand_id}",
                 "/materials/", f"/materials/{self.material_id}", "/colors/", f"/colors/{self.color_id}",
                 f"/colors/compare?color_1_id={self.color_id}&color_2_id={self.second_color_id}",
                 f"/colors/{self.color_id}/matches"]
        for headers in ({}, self.auth, self.bearer("invalid-public-read-token")):
            for path in paths:
                with self.subTest(path=path, authenticated=bool(headers)):
                    self.assertEqual(self.client.get(path, headers=headers).status_code, 200)
        for path in ("/categories/999999/subcategories", "/brands/999999", "/colors/999999", "/materials/999999"):
            with self.subTest(missing=path):
                self.assertEqual(self.client.get(path).status_code, 404)

    def test_ordinary_users_can_manage_only_their_own_wardrobe(self):
        self.assert_mutations_denied(self.auth, 403)
        listed = self.client.get("/clothing", headers=self.auth)
        self.assertEqual(listed.status_code, 200)
        self.assertEqual({item["id"] for item in listed.json()}, set(self.garment_ids))
        path = f"/clothing/{self.garment_ids[0]}"
        self.assertEqual(self.client.put(path, json={"name": "Owner edited tee"}, headers=self.auth).status_code, 200)
        self.assertEqual(self.client.get("/clothing", headers=self.other_auth).json(), [])
        self.assertEqual(self.client.put(path, json={"name": "Forbidden"}, headers=self.other_auth).status_code, 404)
        self.assertEqual(self.client.delete(path, headers=self.other_auth).status_code, 404)
        self.assertEqual(self.client.delete(path, headers=self.auth).status_code, 200)
        self.assertEqual(len(self.client.get("/clothing", headers=self.auth).json()), 3)

    def test_catalog_denial_preserves_weather_outfits_and_user_isolation(self):
        self.assert_mutations_denied(self.auth, 403)
        results = []
        for params in ({}, {"temperature_c": 5, "condition": "Rain"},
                       {"temperature_c": 35, "condition": "Clear", "include_layers": "false"}):
            response = self.client.get("/outfits/generate", params=params, headers=self.auth)
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.json()["outfits"])
            results.append(response.json())
        self.assertFalse(results[0]["weather_context"]["enabled"])
        self.assertTrue(results[1]["weather_context"]["enabled"])
        self.assertNotEqual(results[1]["outfits"][0]["weather_score"], results[2]["outfits"][0]["weather_score"])
        self.assertTrue(all(outfit["items"].get("layer") is None for outfit in results[2]["outfits"]))
        self.assertEqual(self.client.get("/outfits/generate", headers=self.other_auth).status_code, 400)
        self.assertEqual(self.client.get("/outfits/generate").status_code, 401)


if __name__ == "__main__":
    unittest.main()
