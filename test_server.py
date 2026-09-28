"""Lightweight local development test server for BuildSuite Core mobile testing.
Responds to ping, login, mobile token generation, access context, and mock doctypes
over http://localhost:8000. Combined with `adb reverse tcp:8000 tcp:8000`, your phone
can connect directly using http://localhost:8000!
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse

PORT = 8000

class FrappeMockHandler(BaseHTTPRequestHandler):
    def _send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Access-Control-Allow-Credentials", "true")

    def do_OPTIONS(self):
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/api/method/ping":
            self.send_json({"message": "pong"})
            return

        if path == "/api/method/buildsuite_core.api.permission.get_access_context":
            self.send_json({
                "message": {
                    "allowed": True,
                    "user": "supervisor@buildsuite.io",
                    "roles": ["BuildSuite Site Engineer", "BuildSuite PM", "System Manager"],
                    "persona": "BuildSuite Site Engineer",
                    "developer_mode": True,
                    "resource_permissions": {
                        "project": {"c": True, "r": True, "e": True, "d": True, "x": True},
                        "task": {"c": True, "r": True, "e": True, "d": True, "x": True},
                        "taskProgressEntry": {"c": True, "r": True, "e": True, "d": True, "x": True},
                        "fieldAttendance": {"c": True, "r": True, "e": True, "d": True, "x": True},
                        "pettyCash": {"c": True, "r": True, "e": True, "d": True, "x": True},
                        "expense": {"c": True, "r": True, "e": True, "d": True, "x": True},
                    },
                    "report_routes": ["/labour-attendance", "/overtime-attendance"],
                    "reason": "ok",
                }
            })
            return

        # Default fallback
        self.send_json({"message": "ok"})

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        content_len = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_len) if content_len > 0 else b""
        data = {}
        try:
            data = json.loads(body.decode("utf-8")) if body else {}
        except Exception:
            pass

        if path == "/api/method/login":
            user = data.get("usr", "supervisor@buildsuite.io")
            self.send_json({
                "message": "Logged In",
                "home_page": "/app",
                "full_name": "Site Supervisor",
                "user": user,
            })
            return

        if path == "/api/method/buildsuite_core.api.mobile_auth.get_or_create_api_keys":
            self.send_json({
                "message": {
                    "user": "supervisor@buildsuite.io",
                    "api_key": "buildsuite_test_key_8849",
                    "api_secret": "buildsuite_test_secret_9912",
                }
            })
            return

        if path == "/api/method/buildsuite_core.api.company.company_context" or "list_companies" in path:
            self.send_json({
                "message": [
                    {"name": "BuildSuite Construction Ltd", "abbr": "BSCL"}
                ]
            })
            return

        if path == "/api/method/upload_file":
            self.send_json({
                "message": {
                    "file_name": "site_photo.jpg",
                    "file_url": "/files/site_photo.jpg"
                }
            })
            return

        self.send_json({"message": "success"})

    def send_json(self, payload, code=200):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self._send_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode("utf-8"))

if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", PORT), FrappeMockHandler)
    print(f"Mock Frappe server listening on port {PORT}...")
    server.serve_forever()
