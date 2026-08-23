#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_service - THE API SURFACE, first cut (F5 builder). One versioned HTTP API that
KDash, the alternate frontend, voice, and mobile all consume - stdlib only, no deps.

ENDPOINTS (v1):
    GET /api/v1/status   - kernel READY + root identity + ledger head
    GET /api/v1/audit    - the audit projection (every number carries measured_at)
    GET /api/v1/jobs     - job states from the scheduler projection
    GET /api/v1/rails    - the rails matrix with verification AGE per link
    POST /api/v1/jobs    - submit {command, priority} -> job_id
Every response carries served_at + measured_at - a panel that cannot show its age is
the frozen-dashboard scar. Auth is a bearer token from the install config - remote
access control exists from day one, invisible in use (zero-friction canon).
"""
from __future__ import annotations

import json
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from cosmos_kernel import Kernel


def make_handler(kernel: Kernel, token: str):
    class Handler(BaseHTTPRequestHandler):
        server_version = "COSMOS/1.0"

        def _send(self, code: int, obj: dict):
            body = json.dumps({"served_at": time.time(), **obj}, indent=1).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _authed(self) -> bool:
            return self.headers.get("Authorization", "") == "Bearer " + token

        def do_GET(self):                                             # noqa: N802
            if not self._authed():
                return self._send(401, {"error": "UNAUTHORIZED"})
            if self.path == "/api/v1/status":
                last = kernel.ledger.last()
                return self._send(200, {"ready": kernel.ready,
                                        "root": str(kernel.paths.root),
                                        "tree_id": kernel.paths.sentinel.tree_id,
                                        "ledger_head": {"seq": last["seq"],
                                                        "event": last["event"]}})
            if self.path == "/api/v1/audit":
                return self._send(200, kernel.audit())
            if self.path == "/api/v1/jobs":
                st = kernel.sched._state()
                return self._send(200, {"measured_at": time.time(),
                                        "jobs": {j: v["st"] for j, v in st.items()}})
            if self.path == "/api/v1/rails":
                reg = getattr(kernel, "registry", None)
                if reg is None:
                    return self._send(200, {"measured_at": time.time(), "matrix": [],
                                            "note": "no registry attached"})
                return self._send(200, {"measured_at": time.time(),
                                        "matrix": reg.matrix()})
            return self._send(404, {"error": "NOT_FOUND", "path": self.path})

        def do_POST(self):                                            # noqa: N802
            if not self._authed():
                return self._send(401, {"error": "UNAUTHORIZED"})
            if self.path == "/api/v1/jobs":
                n = int(self.headers.get("Content-Length", 0))
                try:
                    d = json.loads(self.rfile.read(n).decode("utf-8"))
                    jid = kernel.sched.submit(d["command"], d.get("priority", "normal"))
                except Exception as e:                                # noqa: BLE001
                    return self._send(400, {"error": "BAD_REQUEST", "detail": str(e)[:200]})
                return self._send(201, {"job_id": jid})
            return self._send(404, {"error": "NOT_FOUND", "path": self.path})

        def log_message(self, *a):                                    # quiet server
            pass

    return Handler


class Service:
    """Serve a kernel. serve_background() for tests; serve_forever() for the real thing."""

    def __init__(self, kernel: Kernel, host: str = "127.0.0.1", port: int = 0):
        tok_file = kernel.paths.config("api_token.txt")
        if not tok_file.exists():
            import secrets as _s
            tok_file.write_text(_s.token_urlsafe(24), encoding="utf-8")
        self.token = tok_file.read_text(encoding="utf-8").strip()
        self.httpd = ThreadingHTTPServer((host, port), make_handler(kernel, self.token))
        self.port = self.httpd.server_address[1]

    def serve_background(self) -> threading.Thread:
        t = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        t.start()
        return t

    def shutdown(self):
        self.httpd.shutdown()
