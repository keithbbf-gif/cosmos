#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""passenger_wsgi — run the TokenCenter gateway under Passenger / CloudLinux
"Setup Python App" (cPanel) without a listening socket.

The gateway is a stdlib BaseHTTPRequestHandler. This adapter rebuilds the raw
HTTP request from the WSGI environ, feeds it to the SAME handler class through
in-memory streams (handle_one_request), and parses the raw response back into
WSGI. Request bodies pass through byte-for-byte, so Stripe signature
verification on raw bytes is unchanged.

Limits (documented, deliberate):
  * Responses are buffered, so SSE chat streams arrive in one piece.
  * Requests are serialised by a process lock; run the app as ONE process
    (the Founding cap lock is in-process).
"""
from __future__ import annotations

import io
import os
import sys
import threading

# LSWSGI/Passenger often run with an ASCII locale; the gateway prints status
# lines containing non-ASCII (em dash). Never let a log line kill startup.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    except Exception:
        pass

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
os.environ.setdefault("COSMOS_PAY_ROOT", os.path.join(os.path.expanduser("~"), ".cosmos_pay"))

import cosmos_pay_gateway as _gw_mod  # noqa: E402

_LOCK = threading.Lock()
_HANDLER = None
_INIT_ERR = None

# Canonical spellings for headers the gateway reads from a plain dict (case-sensitive).
_CANON = {
    "CF_CONNECTING_IP": "CF-Connecting-IP", "TRUE_CLIENT_IP": "True-Client-IP",
    "CF_TURNSTILE_TOKEN": "CF-Turnstile-Token", "X_FORWARDED_FOR": "X-Forwarded-For",
    "PAYPAL_WEBHOOK_ID": "PayPal-Webhook-Id", "PAYPAL_TRANSMISSION_ID": "PayPal-Transmission-Id",
    "PAYPAL_TRANSMISSION_TIME": "PayPal-Transmission-Time", "PAYPAL_TRANSMISSION_SIG": "PayPal-Transmission-Sig",
    "PAYPAL_CERT_URL": "PayPal-Cert-Url", "PAYPAL_AUTH_ALGO": "PayPal-Auth-Algo", "X_TEST_MOCK": "X-Test-Mock",
}

_HOP = {"connection", "keep-alive", "transfer-encoding", "proxy-connection", "upgrade", "te", "trailer",
        "server", "date"}


def _handler_cls():
    global _HANDLER, _INIT_ERR
    if _HANDLER is None and _INIT_ERR is None:
        try:
            import contextlib
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                gw, api, _config = _gw_mod.build_app()
            try:
                sys.stderr.write(buf.getvalue().encode("ascii", "backslashreplace").decode("ascii"))
            except Exception:
                pass
            base = _gw_mod.make_handler(gw, api)

            class _MemHandler(base):  # type: ignore[misc, valid-type]
                def __init__(self, raw: bytes, client_ip: str):
                    # Do NOT call BaseRequestHandler.__init__ (it needs a socket).
                    self.rfile = io.BytesIO(raw)
                    self.wfile = io.BytesIO()
                    self.client_address = (client_ip, 0)
                    self.server = None
                    self.close_connection = True

            _HANDLER = _MemHandler
        except Exception as e:  # fail closed, surface a non-secret reason
            _INIT_ERR = f"{type(e).__name__}: {str(e).split(' — ')[0][:200]}"
    return _HANDLER


def _raw_request(environ) -> tuple[bytes, str]:
    method = environ.get("REQUEST_METHOD", "GET")
    path = environ.get("PATH_INFO", "/") or "/"
    script = environ.get("SCRIPT_NAME", "")
    if script and script != "/":
        path = script.rstrip("/") + path
    qs = environ.get("QUERY_STRING", "")
    target = path + ("?" + qs if qs else "")
    try:
        length = int(environ.get("CONTENT_LENGTH") or 0)
    except ValueError:
        length = 0
    body = environ["wsgi.input"].read(length) if length > 0 else b""

    lines = [f"{method} {target} HTTP/1.1"]
    for k, v in environ.items():
        if k.startswith("HTTP_") and k not in ("HTTP_CONTENT_LENGTH", "HTTP_CONTENT_TYPE",
                                               "HTTP_CONNECTION", "HTTP_TRANSFER_ENCODING"):
            name = _CANON.get(k[5:]) or "-".join(p.capitalize() for p in k[5:].split("_"))
            lines.append(f"{name}: {v}")
    if environ.get("CONTENT_TYPE"):
        lines.append(f"Content-Type: {environ['CONTENT_TYPE']}")
    lines.append(f"Content-Length: {len(body)}")
    lines.append("Connection: close")
    head = ("\r\n".join(lines) + "\r\n\r\n").encode("latin-1", "replace")
    ip = (environ.get("HTTP_CF_CONNECTING_IP")
          or (environ.get("HTTP_X_FORWARDED_FOR", "").split(",")[0].strip())
          or environ.get("REMOTE_ADDR", "127.0.0.1"))
    return head + body, ip


def _parse_response(raw: bytes):
    head, sep, body = raw.partition(b"\r\n\r\n")
    if not sep:
        return "502 Bad Gateway", [("Content-Type", "application/json")], b'{"error":{"code":"empty_response"}}'
    lines = head.decode("latin-1").split("\r\n")
    parts = lines[0].split(" ", 2)
    status = f"{parts[1]} {parts[2] if len(parts) > 2 else ''}".strip() if len(parts) > 1 else "502 Bad Gateway"
    headers = []
    for ln in lines[1:]:
        if ":" in ln:
            k, v = ln.split(":", 1)
            if k.strip().lower() not in _HOP:
                headers.append((k.strip(), v.strip()))
    if not any(k.lower() == "content-length" for k, _ in headers):
        headers.append(("Content-Length", str(len(body))))
    return status, headers, body


def application(environ, start_response):
    cls = _handler_cls()
    if cls is None:
        body = ('{"error":{"code":"gateway_init_failed","message":%s}}'
                % __import__("json").dumps(_INIT_ERR or "unknown")).encode("utf-8")
        start_response("503 Service Unavailable", [("Content-Type", "application/json"),
                                                   ("Content-Length", str(len(body))),
                                                   ("Access-Control-Allow-Origin", "*")])
        return [body]
    raw, ip = _raw_request(environ)
    with _LOCK:
        h = cls(raw, ip)
        try:
            h.handle_one_request()
        except Exception as e:  # never leak internals
            body = b'{"error":{"code":"internal_error"}}'
            sys.stderr.write(f"passenger_wsgi: {type(e).__name__}\n")
            start_response("500 Internal Server Error", [("Content-Type", "application/json"),
                                                         ("Content-Length", str(len(body))),
                                                         ("Access-Control-Allow-Origin", "*")])
            return [body]
        out = h.wfile.getvalue()
    status, headers, body = _parse_response(out)
    start_response(status, headers)
    return [body]
