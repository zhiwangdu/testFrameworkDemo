from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse


class State:
    written = False


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args: object) -> None:
        return

    def send_json(self, payload: dict, code: int = 200) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/query":
            self.send_json({"results": [{"statement_id": 0}]})
            return
        if parsed.path == "/write":
            length = int(self.headers.get("Content-Length", "0") or "0")
            if length:
                self.rfile.read(length)
            State.written = True
            self.send_response(204)
            self.end_headers()
            return
        self.send_json({"error": "not found"}, 404)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path != "/query":
            self.send_json({"error": "not found"}, 404)
            return
        query = parse_qs(parsed.query).get("q", [""])[0].upper()
        if "SELECT" in query and State.written:
            self.send_json(
                {
                    "results": [
                        {
                            "series": [
                                {
                                    "name": "rw_smoke",
                                    "columns": ["time", "value"],
                                    "values": [["2026-06-28T00:00:00Z", 1]],
                                }
                            ]
                        }
                    ]
                }
            )
            return
        self.send_json({"results": [{"statement_id": 0}]})


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=18086)
    args = parser.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"mock Influx/openGemini API listening on http://{args.host}:{args.port}", flush=True)
    server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
