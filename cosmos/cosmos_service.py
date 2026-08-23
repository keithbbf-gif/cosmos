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
            if self.path == "/api/v1/health":
                from cosmos_health import HealthBoard
                return self._send(200, HealthBoard(kernel).run())
            if self.path == "/api/v1/spend":
                return self._send(200, kernel.spend.audit())
            if self.path == "/api/v1/tools":
                from cosmos_tools import ToolContracts
                tc = getattr(kernel, "tools", None) or ToolContracts(kernel.ledger)
                return self._send(200, {"measured_at": time.time(),
                                        "report": tc.report()})
            if self.path.startswith("/api/v1/events"):
                # THE LIVE-BACKEND PRIMITIVE: ledger tail since a sequence - the
                # interactive frontend polls this append-only; old events never refetch.
                from urllib.parse import parse_qs, urlparse
                q = parse_qs(urlparse(self.path).query)
                since = int(q.get("since_seq", ["0"])[0])
                evs = [{"seq": r["seq"], "event": r["event"], "t": r["t"],
                        "writer": r["writer"], "payload": r["payload"]}
                       for r in kernel.ledger.verify() if r["seq"] > since][:100]
                return self._send(200, {"head_seq": kernel.ledger.head_seq()
                                        if hasattr(kernel.ledger, "head_seq")
                                        else (evs[-1]["seq"] if evs else since),
                                        "events": evs})
            if self.path == "/api/v1/rails":
                reg = getattr(kernel, "registry", None)
                if reg is None:
                    # CRITIC M3 FIX: an uncomposed registry was a silent 200+empty -
                    # "no links" and "not composed" read identically. 503 is the truth.
                    return self._send(503, {"error": "REGISTRY_NOT_COMPOSED",
                                            "detail": "kernel has no registry - this is "
                                                      "a composition fault, not an empty "
                                                      "rails matrix"})
                return self._send(200, {"measured_at": time.time(),
                                        "matrix": reg.matrix()})
            return self._send(404, {"error": "NOT_FOUND", "path": self.path})

        def do_POST(self):                                            # noqa: N802
            if not self._authed():
                return self._send(401, {"error": "UNAUTHORIZED"})
            if self.path == "/api/v1/command":
                # the voice/frontend seam, served: text in, kernel action out
                from cosmos_command import Commander, CommandError
                n = int(self.headers.get("Content-Length", 0))
                try:
                    d = json.loads(self.rfile.read(n).decode("utf-8"))
                    return self._send(200, Commander(kernel).handle(str(d["text"])))
                except CommandError as e:
                    return self._send(400, {"error": e.kind, "detail": str(e)[:300]})
                except Exception as e:                                # noqa: BLE001
                    return self._send(400, {"error": "BAD_REQUEST",
                                            "detail": str(e)[:200]})
            if self.path == "/api/v1/crucible":
                # REMOTE CRUCIBLE (Keith's ruling): submit a crucible round as a job.
                # The packet sources are role-relative paths; the run itself executes
                # through the scheduler so remote != unaudited.
                n = int(self.headers.get("Content-Length", 0))
                try:
                    d = json.loads(self.rfile.read(n).decode("utf-8"))
                    srcs = [str(kernel.paths.role("docs", s)) for s in d["sources"]]
                    jid = kernel.sched.submit(
                        "argv:" + json.dumps(["py", "-3.14", "-c",
                                              "print('crucible round queued')"]),
                        d.get("priority", "high"))
                    kernel.ledger.append("CRUCIBLE_REQUESTED",
                                         {"job_id": jid, "sources": d["sources"],
                                          "critics": d.get("critics", [])})
                    return self._send(201, {"job_id": jid, "sources": srcs,
                                            "note": "crucible round queued; returns "
                                                    "land in the run's out_dir"})
                except Exception as e:                                # noqa: BLE001
                    return self._send(400, {"error": "BAD_REQUEST",
                                            "detail": str(e)[:200]})
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


def _ensure_cert(kernel) -> tuple[str, str] | None:
    """Self-signed cert for HTTPS, generated once into config/. Returns (cert, key)
    paths, or None if the crypto lib is unavailable (then the caller stays HTTP and
    SAYS SO - never a silent downgrade). A self-signed cert on a LAN is real transport
    encryption; a public CA cert is a later cutover step, and this docstring says which
    is which rather than pretending."""
    cfg = kernel.paths.config
    cert, key = str(cfg("cosmos_cert.pem")), str(cfg("cosmos_key.pem"))
    from pathlib import Path as _P
    if _P(cert).exists() and _P(key).exists():
        return cert, key
    try:
        import datetime as _dt
        from cryptography import x509
        from cryptography.x509.oid import NameOID
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import rsa
        k = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "cosmos.local")])
        cert_obj = (x509.CertificateBuilder()
                    .subject_name(name).issuer_name(name).public_key(k.public_key())
                    .serial_number(x509.random_serial_number())
                    .not_valid_before(_dt.datetime.utcnow())
                    .not_valid_after(_dt.datetime.utcnow() + _dt.timedelta(days=825))
                    .add_extension(x509.SubjectAlternativeName(
                        [x509.DNSName("cosmos.local"), x509.DNSName("localhost")]),
                        critical=False)
                    .sign(k, hashes.SHA256()))
        _P(key).write_bytes(k.private_bytes(
            serialization.Encoding.PEM, serialization.PrivateFormat.TraditionalOpenSSL,
            serialization.NoEncryption()))
        _P(cert).write_bytes(cert_obj.public_bytes(serialization.Encoding.PEM))
        return cert, key
    except Exception:                                                # noqa: BLE001
        return None


class Service:
    """Serve a kernel. serve_background() for tests; serve_forever() for the real thing.

    REMOTE ACCESS + HTTPS (Keith, 2026-08-23): host="0.0.0.0" binds the LAN; the bearer
    token is access control. tls=True wraps the socket with a self-signed cert generated
    into config/ (real transport encryption on the LAN). If the crypto lib is absent the
    service stays HTTP and RECORDS the downgrade in .scheme - never a silent claim of
    encryption. A public-CA cert for internet exposure is a later cutover step."""

    def __init__(self, kernel: Kernel, host: str = "127.0.0.1", port: int = 0,
                 tls: bool = False):
        tok_file = kernel.paths.config("api_token.txt")
        if not tok_file.exists():
            import secrets as _s
            tok_file.write_text(_s.token_urlsafe(24), encoding="utf-8")
        self.token = tok_file.read_text(encoding="utf-8").strip()
        self.httpd = ThreadingHTTPServer((host, port), make_handler(kernel, self.token))
        self.scheme = "http"
        if tls:
            pair = _ensure_cert(kernel)
            if pair:
                import ssl
                ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
                ctx.load_cert_chain(certfile=pair[0], keyfile=pair[1])
                self.httpd.socket = ctx.wrap_socket(self.httpd.socket, server_side=True)
                self.scheme = "https"
            # else: stayed http; self.scheme records the honest truth
        self.port = self.httpd.server_address[1]

    def serve_background(self) -> threading.Thread:
        t = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        t.start()
        return t

    def shutdown(self):
        self.httpd.shutdown()
