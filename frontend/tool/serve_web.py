"""Loopback-only Flutter build preview with a same-origin proxy to the REAL API.

No CORS changes, test responses, database imports, credentials on disk, or uploads.
Use only for local development; put production hosting behind a real HTTPS proxy.
"""
import argparse
import json
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urlsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class PreviewHandler(SimpleHTTPRequestHandler):
    api_url = "http://127.0.0.1:8000"

    def log_message(self, format, *args):
        # Cities, query strings, auth headers and response bodies stay out of logs.
        pass

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        super().end_headers()

    def _error(self, status, message):
        data = json.dumps({"detail": message}).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _dispatch(self):
        allowed_hosts = {f"127.0.0.1:{self.server.server_port}", f"localhost:{self.server.server_port}"}
        if self.headers.get("Host") not in allowed_hosts:
            return self._error(403, "Only the local preview host is allowed.")
        origin = self.headers.get("Origin")
        if origin and origin not in {f"http://{host}" for host in allowed_hosts}:
            return self._error(403, "Cross-origin requests are not allowed.")
        path = urlsplit(self.path).path
        if path.startswith("/api/") or path.startswith("/uploads/"):
            return self._proxy(path)
        if self.command != "GET":
            return self._error(405, "Method not allowed.")
        # Do not serve hidden files or symlinks outside build/web.
        target = Path(self.translate_path(path)).resolve()
        root = Path(self.directory).resolve()
        if not target.is_relative_to(root) or any(part.startswith(".") for part in Path(unquote(path)).parts if part not in {"/", "\\"}):
            return self._error(403, "Path not allowed.")
        return super().do_GET()

    def _proxy(self, path):
        api_path = path.removeprefix("/api") if path.startswith("/api/") else path
        allowed = ((self.command == "GET" and api_path in {"/me", "/clothing", "/outfits/generate"})
                   or (self.command == "POST" and api_path in {"/login", "/register"})
                   or (self.command == "GET" and api_path.startswith("/uploads/")))
        if not allowed:
            return self._error(405, "This endpoint is outside the preview scope.")
        if self.headers.get("Transfer-Encoding"):
            return self._error(400, "Chunked requests are not supported.")
        try:
            size = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            return self._error(400, "Invalid content length.")
        if not 0 <= size <= 65536:
            return self._error(413, "Request too large.")
        if self.command == "POST" and self.headers.get_content_type() != "application/json":
            return self._error(415, "Use a JSON request body.")
        headers = {name: self.headers[name] for name in ("Authorization", "Content-Type", "Accept") if name in self.headers}
        query = urlsplit(self.path).query
        target = self.api_url.rstrip("/") + api_path + (f"?{query}" if query else "")
        request = Request(target, data=self.rfile.read(size) if size else None,
                          headers=headers, method=self.command)
        opener = build_opener(ProxyHandler({}), NoRedirect())
        try:
            response = opener.open(request, timeout=30)
        except HTTPError as error:
            response = error  # Preserve real FastAPI errors, including status codes.
        except (URLError, TimeoutError, OSError):
            return self._error(502, "Could not reach the API. Check that your existing backend is running.")
        with response:
            body = response.read(20 * 1024 * 1024 + 1)
            if len(body) > 20 * 1024 * 1024:
                return self._error(502, "API response exceeded the preview limit.")
            self.send_response(response.status)
            self.send_header("Content-Type", response.headers.get("Content-Type", "application/octet-stream"))
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    do_GET = _dispatch
    do_POST = _dispatch
    do_PUT = _dispatch
    do_DELETE = _dispatch

    def list_directory(self, path):
        self._error(403, "Directory listings are disabled.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--api", default="http://127.0.0.1:8000")
    parser.add_argument("--build-dir", type=Path, help="Optional separate Flutter web build for isolated verification.")
    args = parser.parse_args()
    api = urlsplit(args.api)
    if api.scheme not in {"http", "https"} or not api.hostname or api.username or api.password or api.query or api.fragment:
        parser.error("--api must be an HTTP(S) URL without credentials, query or fragment")
    root = (args.build_dir or (Path(__file__).resolve().parents[1] / "build" / "web")).resolve()
    if not (root / "index.html").is_file():
        parser.error("Build the Flutter web app first; see frontend/README.md.")
    PreviewHandler.api_url = args.api
    server = ThreadingHTTPServer(("127.0.0.1", args.port), partial(PreviewHandler, directory=str(root)))
    print(f"Preview: http://127.0.0.1:{server.server_port} (Ctrl+C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
