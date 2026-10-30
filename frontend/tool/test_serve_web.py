"""Proxy security/forwarding tests; no network or real backend/database access."""
import io
import unittest
from email.message import Message
from types import SimpleNamespace
from unittest.mock import patch

from serve_web import PreviewHandler


class Response(io.BytesIO):
    status = 200
    headers = {"Content-Type": "application/json"}


class ProxyTests(unittest.TestCase):
    def handler(self, path="/api/clothing", method="GET", origin=None):
        handler = object.__new__(PreviewHandler)
        handler.path = path
        handler.command = method
        handler.server = SimpleNamespace(server_port=8080)
        handler.headers = Message()
        handler.headers["Host"] = "127.0.0.1:8080"
        handler.headers["Authorization"] = "Bearer test-token"
        if origin:
            handler.headers["Origin"] = origin
        handler.rfile = io.BytesIO()
        handler.wfile = io.BytesIO()
        handler.send_response = lambda status: setattr(handler, "result_status", status)
        handler.send_header = lambda *_: None
        handler.end_headers = lambda: None
        return handler

    @patch("serve_web.build_opener")
    def test_forwards_real_status_body_query_and_bearer(self, opener):
        opener.return_value.open.return_value = Response(b'[{"id":42}]')
        handler = self.handler("/api/outfits/generate?limit=5&location=Cairo")
        handler._dispatch()
        request = opener.return_value.open.call_args.args[0]
        self.assertEqual(request.full_url, "http://127.0.0.1:8000/outfits/generate?limit=5&location=Cairo")
        self.assertEqual(request.get_header("Authorization"), "Bearer test-token")
        self.assertEqual(handler.result_status, 200)
        self.assertEqual(handler.wfile.getvalue(), b'[{"id":42}]')

    @patch("serve_web.build_opener")
    def test_cross_origin_and_untrusted_hosts_never_reach_api(self, opener):
        handler = self.handler(origin="https://untrusted.example")
        handler._dispatch()
        self.assertEqual(handler.result_status, 403)
        handler = self.handler()
        handler.headers.replace_header("Host", "untrusted.example:8080")
        handler._dispatch()
        self.assertEqual(handler.result_status, 403)
        opener.assert_not_called()

    @patch("serve_web.build_opener")
    def test_uploads_mutations_and_oversized_bodies_are_blocked(self, opener):
        for path, method in [("/api/upload/", "POST"), ("/api/clothing/1", "DELETE"), ("/api/clothing", "POST")]:
            handler = self.handler(path, method)
            handler._dispatch()
            self.assertEqual(handler.result_status, 405)
        handler = self.handler("/api/login", "POST")
        handler.headers["Content-Length"] = "100000"
        handler._dispatch()
        self.assertEqual(handler.result_status, 413)
        opener.assert_not_called()

    @patch("serve_web.build_opener")
    def test_unavailable_backend_returns_failure_not_success(self, opener):
        opener.return_value.open.side_effect = OSError("offline")
        handler = self.handler()
        handler._dispatch()
        self.assertEqual(handler.result_status, 502)
        self.assertIn(b"Could not reach the API", handler.wfile.getvalue())


if __name__ == "__main__":
    unittest.main()
