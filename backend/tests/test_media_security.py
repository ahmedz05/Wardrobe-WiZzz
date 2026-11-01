"""Legacy media must fail closed without reading bodies, writing or exposing files.

Only synthetic temporary files are used; no database or existing wardrobe photo is
opened. Re-enabling the old uploader/static mount must make these tests fail.
"""
import asyncio
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault("DATABASE_URL", "sqlite://")
os.environ.setdefault("JWT_SECRET_KEY", "test-only-key-not-for-deployment-0123456789")

from fastapi.testclient import TestClient
from starlette.routing import Mount

from app.main import app
from app.services import upload_service
from app.services.auth_service import create_access_token


class MediaSecurityTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="wardrobe-media-test-")
        self.folder = Path(self.temporary.name)
        self.photo = self.folder / "private-probe.jpg"
        self.photo.write_bytes(b"synthetic-private-media-marker")
        self.patches = [patch.object(upload_service, "UPLOAD_FOLDER", self.folder)]
        # Redirect any accidentally exposed static mount to synthetic files only.
        for route in app.routes:
            if isinstance(route, Mount) and route.path == "/uploads":
                self.patches.extend([patch.object(route.app, "directory", str(self.folder)),
                                     patch.object(route.app, "all_directories", [str(self.folder)])])
        for replacement in self.patches:
            replacement.start()
        self.client = TestClient(app)

    def tearDown(self):
        self.client.close()
        for replacement in reversed(self.patches):
            replacement.stop()
        self.temporary.cleanup()

    def test_anonymous_upload_cannot_create_a_file(self):
        response = self.client.post("/upload/", files={"file": ("disguised.jpg", b"not-an-image", "image/jpeg")})
        self.assertEqual(response.status_code, 503)
        self.assertEqual(list(self.folder.iterdir()), [self.photo])
        self.assertEqual(response.headers.get("cache-control"), "no-store")

    def test_bearer_header_cannot_reenable_the_legacy_uploader(self):
        token = create_access_token({"sub": "owner@example.test", "user_id": 7})
        response = self.client.post("/upload/", headers={"Authorization": f"Bearer {token}"},
                                    files={"file": ("image.png", b"synthetic-image", "image/png")})
        self.assertEqual(response.status_code, 503)
        self.assertEqual(list(self.folder.iterdir()), [self.photo])

    def test_missing_or_malformed_multipart_is_disabled_instead_of_parsed(self):
        for headers, body in [({}, b""), ({"Content-Type": "multipart/form-data; boundary=missing"}, b"broken-body")]:
            with self.subTest(headers=headers):
                response = self.client.post("/upload/", headers=headers, content=body)
                self.assertEqual(response.status_code, 503)

    def test_upload_rejection_does_not_consume_the_request_body(self):
        messages = []
        reads = []
        body = (b'--probe\r\nContent-Disposition: form-data; name="file"; filename="test.jpg"\r\n'
                b'Content-Type: image/jpeg\r\n\r\nsynthetic\r\n--probe--\r\n')

        async def receive():
            reads.append(True)
            return {"type": "http.request", "body": body, "more_body": False}

        async def send(message):
            messages.append(message)

        scope = {"type": "http", "asgi": {"version": "3.0"}, "http_version": "1.1",
                 "method": "POST", "scheme": "http", "path": "/upload/", "raw_path": b"/upload/",
                 "root_path": "", "query_string": b"", "client": ("127.0.0.1", 1234), "server": ("testserver", 80),
                 "headers": [(b"content-type", b"multipart/form-data; boundary=probe"),
                             (b"content-length", b"1073741824")]}
        asyncio.run(app(scope, receive, send))
        self.assertEqual(next(m["status"] for m in messages if m["type"] == "http.response.start"), 503)
        self.assertEqual(reads, [], "Disabled upload must reject before reading or spooling multipart data.")

    def test_existing_private_file_cannot_be_read_publicly(self):
        response = self.client.get("/uploads/private-probe.jpg")
        self.assertEqual(response.status_code, 404)
        self.assertNotIn(self.photo.read_bytes(), response.content)
        self.assertEqual(self.photo.read_bytes(), b"synthetic-private-media-marker")

    def test_head_range_and_bearer_requests_cannot_disclose_media(self):
        for method, headers in [("HEAD", {}), ("GET", {"Range": "bytes=0-5"}),
                                ("GET", {"Authorization": "Bearer invalid-token"})]:
            with self.subTest(method=method, headers=headers):
                self.assertEqual(self.client.request(method, "/uploads/private-probe.jpg", headers=headers).status_code, 404)


if __name__ == "__main__":
    unittest.main()
