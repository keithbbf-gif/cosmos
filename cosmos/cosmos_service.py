#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_service - THE API SURFACE, first cut (F5 builder). One versioned HTTP API that
KDash, the alternate frontend, voice, and mobile all consume - stdlib only, no deps.

ENDPOINTS (v1):
    GET /api/v1/status   - kernel READY + root identity + ledger head
    GET /api/v1/audit    - the audit projection (every number carries measured_at)
    GET /api/v1/jobs     - job states from the scheduler projection
    GET /api/v1/rails    - the rails matrix with verification AGE per link
    GET /api/v1/makers   - the maker map (where agents/tools/connectors/skills are made)
    POST /api/v1/jobs    - submit {command, priority} -> job_id
    POST /api/v1/makers  - add a maker entry (unknown kind REFUSES)
STATIC APP SHELL (PWA, no bearer - see _STATIC_ROUTES):
    GET / , /m , /mobile - the phone-first page (mobile is the road default)
    GET /dash            - the desktop KDash page
    GET /kdash_manifest.webmanifest , /kdash_sw.js - installability shell
The shell is an exact-match allowlist of fixed files carrying NO data and NO
token (the bearer is pasted into the page at runtime, memory only); every
/api/v1/* route keeps requiring the bearer exactly as before.
Every response carries served_at + measured_at - a panel that cannot show its age is
the frozen-dashboard scar. Auth is a bearer token from the install config - remote
access control exists from day one, invisible in use (zero-friction canon). A blank
or whitespace token is REFUSED (an open door). A missing token file is minted only
on a loopback bind; a remote bind REFUSES rather than inventing silently.
"""
from __future__ import annotations

import hmac
import json
import os
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from cosmos_kernel import Kernel

# Loopback binds may mint a token (zero-friction local use). A remote bind must
# never invent one - a silently minted secret on 0.0.0.0 is an open door.
_LOOPBACK_HOSTS = frozenset({"127.0.0.1", "localhost", "::1"})

# Per-request body cap for every POST endpoint. All v1 POST bodies are small
# JSON control messages; 1 MiB is generous. An uncapped Content-Length is an
# invitation to allocate arbitrary memory on an authenticated-or-not socket.
_MAX_BODY_BYTES = 1 << 20


def _frontend_file(name: str):
    """Resolve one shell file: kdash/<name> beside (or above) this module in the
    repo layout, or flat kdash_<name> in a spike checkout - the same resolution
    order as cosmos_kdash._find_kdash_index. None if absent (an honest 404)."""
    from pathlib import Path as _P
    here = _P(__file__).resolve().parent
    for cand in (here / "kdash" / name,
                 here.parent / "kdash" / name,
                 here / ("kdash_" + name)):
        if cand.is_file():
            return cand
    return None


# THE STATIC APP SHELL (PWA). Served WITHOUT the bearer, deliberately: these are
# fixed, allowlisted files containing no data and no secret - the token is pasted
# by the user into the page at runtime and lives in page memory only. Serving the
# shell openly is what makes the client installable/reachable from a phone; the
# data behind it still requires the bearer on every /api/v1/* request. The dict
# is an EXACT-MATCH allowlist: no request text ever becomes a filesystem path,
# so there is no traversal surface. Mobile is the default at / (the road case).
_CT_HTML = "text/html; charset=utf-8"
_STATIC_ROUTES = {
    "/": ("mobile.html", _CT_HTML),
    "/m": ("mobile.html", _CT_HTML),
    "/mobile": ("mobile.html", _CT_HTML),
    "/dash": ("index.html", _CT_HTML),
    "/kdash_manifest.webmanifest": ("manifest.webmanifest",
                                    "application/manifest+json"),
    # served at the ROOT path so its default scope ("/") can control /m
    "/kdash_sw.js": ("sw.js", "text/javascript; charset=utf-8"),
}


class ServiceError(RuntimeError):
    """kind in {BLANK_TOKEN, TOKEN_MISSING, REMOTE_CLEARTEXT}."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


def _is_remote_bind(host: str) -> bool:
    return (host or "").strip().lower() not in _LOOPBACK_HOSTS


def _write_private(path, data: bytes) -> None:
    """Create/overwrite a secret-bearing file with owner-only perms (0o600) from
    the first byte - never default perms then a chmod race. On Windows the mode
    is advisory; NTFS ACLs inherit, and 0o600 is still the correct intent."""
    fd = os.open(str(path), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "wb") as fh:
        fh.write(data)


def _load_api_token(tok_file, remote: bool) -> str:
    """Bearer material is install config, not something the service invents on a
    remote bind. Empty/whitespace is always an open door and is REFUSED."""
    from pathlib import Path as _P
    tok_file = _P(tok_file)
    if not tok_file.exists():
        if remote:
            raise ServiceError(
                "TOKEN_MISSING",
                "api_token.txt is missing - refusing to invent authentication "
                "material in a remote context (a silently minted token is an "
                "open door on the LAN)")
        import secrets as _s
        _write_private(tok_file, _s.token_urlsafe(24).encode("utf-8"))
    token = tok_file.read_text(encoding="utf-8").strip()
    if not token:
        raise ServiceError(
            "BLANK_TOKEN",
            "api_token.txt is empty or whitespace - a blank token is an open door")
    return token


def _crucible_dispatchers(kernel, names) -> dict | None:
    """Critics are injected callables on the kernel (name -> packet_text -> return
    text). A requested critic that is not composed is not invented; None means
    the round cannot actually run."""
    pool = getattr(kernel, "crucible_critics", None)
    if not isinstance(pool, dict) or not pool:
        return None
    if not names:
        return dict(pool)
    out = {}
    for n in names:
        fn = pool.get(n)
        if not callable(fn):
            return None
        out[n] = fn
    return out or None


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
            # Constant-time compare: == short-circuits on the first differing
            # byte, which leaks token prefixes to a timing observer.
            got = self.headers.get("Authorization", "")
            return hmac.compare_digest(got.encode("utf-8"),
                                       ("Bearer " + token).encode("utf-8"))

        def _read_body(self, cap: int = _MAX_BODY_BYTES):
            """Read the POST body under a hard cap, or send a controlled refusal
            and return None. A missing/negative/non-int/oversized Content-Length
            is rejected BEFORE any read - rfile.read(N) on an unbounded N is a
            memory DoS, and read(-1) blocks on the open socket."""
            raw = self.headers.get("Content-Length")
            if raw is None:
                self._send(400, {"error": "LENGTH_REQUIRED",
                                 "detail": "Content-Length header is required"})
                return None
            try:
                n = int(raw)
            except ValueError:
                self._send(400, {"error": "BAD_LENGTH",
                                 "detail": f"Content-Length is not an integer: "
                                           f"{raw[:64]!r}"})
                return None
            if n < 0:
                self._send(400, {"error": "BAD_LENGTH",
                                 "detail": "Content-Length must be non-negative"})
                return None
            if n > cap:
                self._send(413, {"error": "BODY_TOO_LARGE",
                                 "detail": f"body of {n} bytes exceeds the "
                                           f"{cap}-byte cap for this endpoint"})
                return None
            return self.rfile.read(n)

        def _send_static(self, name: str, ctype: str):
            """Serve one allowlisted shell file as bytes. A missing file is an
            honest 404 (SHELL_FILE_MISSING), never a silent empty page."""
            path = _frontend_file(name)
            if path is None:
                return self._send(404, {"error": "SHELL_FILE_MISSING",
                                        "file": name})
            body = path.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("X-Content-Type-Options", "nosniff")
            # the service worker does shell caching; the server stays honest
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):                                             # noqa: N802
            # Static app shell FIRST, without the bearer (see _STATIC_ROUTES:
            # fixed files, no data, no token). Everything below this line keeps
            # requiring the bearer exactly as before.
            from urllib.parse import urlparse as _urlparse
            route = _STATIC_ROUTES.get(_urlparse(self.path).path)
            if route is not None:
                return self._send_static(*route)
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
                raw_since = q.get("since_seq", ["0"])[0]
                try:
                    since = int(raw_since)
                except ValueError:
                    return self._send(400, {"error": "BAD_SINCE_SEQ",
                                            "detail": f"since_seq must be an "
                                                      f"integer: {raw_since[:64]!r}"})
                if since < 0 or since > (1 << 62):
                    return self._send(400, {"error": "BAD_SINCE_SEQ",
                                            "detail": "since_seq must be a "
                                                      "non-negative bounded integer"})
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
            if self.path.startswith("/api/v1/makers"):
                from urllib.parse import parse_qs, urlparse
                from cosmos_makers import MakerError
                parsed = urlparse(self.path)
                if parsed.path != "/api/v1/makers":
                    return self._send(404, {"error": "NOT_FOUND", "path": self.path})
                mm = getattr(kernel, "makers", None)
                if mm is None:
                    # M3: "not composed" is not "empty". GET must not seed (B1).
                    return self._send(503, {"error": "MAKERS_NOT_COMPOSED",
                                            "detail": "kernel has no maker map - this is "
                                                      "a composition fault, not an empty "
                                                      "catalog"})
                q = parse_qs(parsed.query)
                kind = q.get("kind", [None])[0]
                tag = q.get("tag", [None])[0]
                text = q.get("text", [None])[0]
                try:
                    rows = mm.find(tag=tag, kind=kind, text=text)
                except MakerError as e:
                    return self._send(400, {"error": e.kind, "detail": str(e)[:300]})
                return self._send(200, {"measured_at": time.time(),
                                        "makers": rows})
            return self._send(404, {"error": "NOT_FOUND", "path": self.path})

        def do_POST(self):                                            # noqa: N802
            if not self._authed():
                return self._send(401, {"error": "UNAUTHORIZED"})
            if self.path == "/api/v1/command":
                # the voice/frontend seam, served: text in, kernel action out
                from cosmos_command import Commander, CommandError
                body = self._read_body()
                if body is None:
                    return
                try:
                    d = json.loads(body.decode("utf-8"))
                    return self._send(200, Commander(kernel).handle(str(d["text"])))
                except CommandError as e:
                    return self._send(400, {"error": e.kind, "detail": str(e)[:300]})
                except Exception as e:                                # noqa: BLE001
                    return self._send(400, {"error": "BAD_REQUEST",
                                            "detail": str(e)[:200]})
            if self.path == "/api/v1/crucible":
                # REMOTE CRUCIBLE (Keith's ruling): a crucible round is a scheduled
                # job. The handler is the worker: submit -> claim -> cosmos_crucible
                # -> returns land on disk -> done. A print stub is not a round; if
                # no critic dispatchers are composed, 501 is the honest answer.
                body = self._read_body()
                if body is None:
                    return
                try:
                    d = json.loads(body.decode("utf-8"))
                except Exception as e:                                # noqa: BLE001
                    return self._send(400, {"error": "BAD_REQUEST",
                                            "detail": str(e)[:200]})
                names = list(d.get("critics") or [])
                dispatchers = _crucible_dispatchers(kernel, names)
                if dispatchers is None:
                    kernel.ledger.append("CRUCIBLE_REFUSED",
                                         {"kind": "CRUCIBLE_NOT_RUNNABLE",
                                          "sources": d.get("sources", []),
                                          "critics": names})
                    return self._send(501, {
                        "error": "CRUCIBLE_NOT_RUNNABLE",
                        "detail": "no composed critic dispatchers for this round - "
                                  "refusing to queue a print stub (a queued print "
                                  "is not a crucible)"})
                from cosmos_crucible import Crucible, CrucibleError
                from cosmos_paths import CosmosPathError
                try:
                    srcs = [kernel.paths.role("docs", s) for s in d["sources"]]
                except CosmosPathError as e:
                    kernel.ledger.append("CRUCIBLE_REFUSED",
                                         {"kind": e.kind, "sources": d.get("sources")})
                    return self._send(400, {"error": e.kind, "detail": str(e)[:300]})
                except Exception as e:                                # noqa: BLE001
                    return self._send(400, {"error": "BAD_REQUEST",
                                            "detail": str(e)[:200]})
                cmd = "crucible:round " + json.dumps(
                    {"sources": list(d["sources"]),
                     "critics": sorted(dispatchers)}, sort_keys=True)
                try:
                    jid = kernel.sched.submit(cmd, d.get("priority", "high"),
                                              lane="crucible")
                except Exception as e:                                # noqa: BLE001
                    return self._send(400, {"error": "BAD_REQUEST",
                                            "detail": str(e)[:200]})
                kernel.ledger.append("CRUCIBLE_REQUESTED",
                                     {"job_id": jid, "sources": d["sources"],
                                      "critics": list(dispatchers)})
                claimed = False
                q = kernel.sched.queued()
                if q and q[0]["job_id"] == jid:
                    kernel.sched.claim_next()
                    claimed = True
                out_dir = kernel.paths.role("work", "crucible", jid)
                try:
                    cru = Crucible(kernel.ledger, out_dir)
                    pkt = cru.build_packet(
                        f"# CRUCIBLE ROUND\njob_id: {jid}\n", srcs)
                    verdict = cru.run_round(pkt, dispatchers)
                    merge = cru.merge_skeleton(verdict)
                    outcome = ("FINDINGS" if (verdict["failed"] or verdict["warning"])
                               else "CLEAN")
                    if claimed:
                        kernel.sched.done(jid, outcome,
                                          f"returned={sorted(verdict['returned'])}")
                    return self._send(201, {
                        "job_id": jid,
                        "sources": [str(s) for s in srcs],
                        "out_dir": str(out_dir),
                        "returned": verdict["returned"],
                        "failed": verdict["failed"],
                        "merge": str(merge),
                        "outcome": outcome if claimed else "QUEUED"})
                except CrucibleError as e:
                    if claimed:
                        kernel.sched.done(jid, "BROKE", f"{e.kind}: {e}"[:200])
                    return self._send(400, {"error": e.kind, "detail": str(e)[:300]})
                except Exception as e:                                # noqa: BLE001
                    if claimed:
                        try:
                            kernel.sched.done(jid, "BROKE", str(e)[:200])
                        except Exception:                             # noqa: BLE001
                            pass
                    return self._send(400, {"error": "BAD_REQUEST",
                                            "detail": str(e)[:200]})
            if self.path == "/api/v1/jobs":
                body = self._read_body()
                if body is None:
                    return
                try:
                    d = json.loads(body.decode("utf-8"))
                    jid = kernel.sched.submit(d["command"], d.get("priority", "normal"))
                except Exception as e:                                # noqa: BLE001
                    return self._send(400, {"error": "BAD_REQUEST", "detail": str(e)[:200]})
                return self._send(201, {"job_id": jid})
            if self.path == "/api/v1/makers":
                from cosmos_makers import MakerError
                body = self._read_body()
                if body is None:
                    return
                try:
                    d = json.loads(body.decode("utf-8"))
                    mm = getattr(kernel, "makers", None)
                    if mm is None:
                        return self._send(503, {"error": "MAKERS_NOT_COMPOSED",
                                                "detail": "kernel has no maker map - this "
                                                          "is a composition fault"})
                    rec = mm.add(d)
                    return self._send(201, {"maker": rec})
                except MakerError as e:
                    return self._send(400, {"error": e.kind, "detail": str(e)[:300]})
                except Exception as e:                                # noqa: BLE001
                    return self._send(400, {"error": "BAD_REQUEST",
                                            "detail": str(e)[:200]})
            return self._send(404, {"error": "NOT_FOUND", "path": self.path})

        def log_message(self, *a):                                    # quiet server
            pass

    return Handler


def _san_entries(host: str) -> tuple[list[str], list]:
    """(dns_names, ip_addresses) the cert must cover so a LAN client can VERIFY,
    not just encrypt. Always: cosmos.local, localhost, this machine's hostname,
    127.0.0.1, ::1. Plus the actual bind host (as IP or DNS), and on a wildcard
    bind (0.0.0.0 / ::) the machine's resolvable local IPs - a cert whose SAN
    names none of the addresses it is served on cannot be verified by anyone."""
    import ipaddress
    import socket
    dns = {"cosmos.local", "localhost"}
    ips = {ipaddress.ip_address("127.0.0.1"), ipaddress.ip_address("::1")}
    try:
        hn = socket.gethostname()
        if hn:
            dns.add(hn)
    except OSError:
        hn = ""
    h = (host or "").strip()
    wildcard = h in ("", "0.0.0.0", "::")
    if h and not wildcard:
        try:
            ips.add(ipaddress.ip_address(h))
        except ValueError:
            dns.add(h)
    if wildcard and hn:
        try:
            for info in socket.getaddrinfo(hn, None):
                try:
                    ips.add(ipaddress.ip_address(info[4][0]))
                except ValueError:
                    pass
        except OSError:
            pass
    return sorted(dns), sorted(ips, key=str)


def _ensure_cert(kernel, host: str = "127.0.0.1") -> tuple[str, str] | None:
    """Self-signed cert for HTTPS, generated into config/. Returns (cert, key)
    paths, or None if the crypto lib is unavailable (then the caller stays HTTP and
    SAYS SO - never a silent downgrade). The SAN covers the ACTUAL bind host/IP
    (plus the documented names) - a cert naming only cosmos.local/localhost cannot
    be verified by a LAN client dialing an IP, which reduces 'HTTPS' to unverified
    encryption. An existing cert that already covers the needed names is reused;
    one that does not is regenerated in place. A self-signed cert on a LAN is real
    transport encryption; a public CA cert is a later cutover step."""
    cfg = kernel.paths.config
    cert, key = str(cfg("cosmos_cert.pem")), str(cfg("cosmos_key.pem"))
    from pathlib import Path as _P
    try:
        import datetime as _dt
        from cryptography import x509
        from cryptography.x509.oid import NameOID
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import rsa
    except Exception:                                                # noqa: BLE001
        # No crypto lib: a pre-provisioned pair still serves; nothing can be minted.
        if _P(cert).exists() and _P(key).exists():
            return cert, key
        return None
    dns_names, ip_addrs = _san_entries(host)
    if _P(cert).exists() and _P(key).exists():
        try:
            existing = x509.load_pem_x509_certificate(_P(cert).read_bytes())
            san = existing.extensions.get_extension_for_class(
                x509.SubjectAlternativeName).value
            have_dns = set(san.get_values_for_type(x509.DNSName))
            have_ip = {str(i) for i in san.get_values_for_type(x509.IPAddress)}
            if (set(dns_names) <= have_dns
                    and {str(i) for i in ip_addrs} <= have_ip):
                return cert, key
            # else: falls through and regenerates with the full SAN set
        except Exception:                                            # noqa: BLE001
            pass                     # unreadable or SAN-less cert: regenerate
    try:
        k = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "cosmos.local")])
        sans = ([x509.DNSName(d) for d in dns_names]
                + [x509.IPAddress(i) for i in ip_addrs])
        cert_obj = (x509.CertificateBuilder()
                    .subject_name(name).issuer_name(name).public_key(k.public_key())
                    .serial_number(x509.random_serial_number())
                    .not_valid_before(_dt.datetime.utcnow())
                    .not_valid_after(_dt.datetime.utcnow() + _dt.timedelta(days=825))
                    .add_extension(x509.SubjectAlternativeName(sans), critical=False)
                    .sign(k, hashes.SHA256()))
        _write_private(key, k.private_bytes(
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
    into config/ (real transport encryption on the LAN; SAN covers the bind host/IP so
    clients can verify). A NON-LOOPBACK bind REFUSES to start unless TLS is actually up
    (REMOTE_CLEARTEXT) - a bearer token over LAN HTTP is captured and replayed by any
    observer. On loopback, if the crypto lib is absent the service stays HTTP and
    RECORDS the downgrade in .scheme - never a silent claim of encryption. A public-CA
    cert for internet exposure is a later cutover step."""

    def __init__(self, kernel: Kernel, host: str = "127.0.0.1", port: int = 0,
                 tls: bool = False):
        remote = _is_remote_bind(host)
        tok_file = kernel.paths.config("api_token.txt")
        self.token = _load_api_token(tok_file, remote=remote)
        self.httpd = ThreadingHTTPServer((host, port), make_handler(kernel, self.token))
        self.scheme = "http"
        if tls:
            pair = _ensure_cert(kernel, host)
            if pair:
                import ssl
                ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
                ctx.load_cert_chain(certfile=pair[0], keyfile=pair[1])
                self.httpd.socket = ctx.wrap_socket(self.httpd.socket, server_side=True)
                self.scheme = "https"
            # else: stayed http; self.scheme records the honest truth
        if remote and self.scheme != "https":
            # A non-loopback bind over cleartext HTTP serves the bearer token to
            # any LAN observer on every request - capture and replay. The honest
            # HTTP fallback is for LOOPBACK only; remotely it is an open door,
            # so the service refuses to start rather than start downgraded.
            self.httpd.server_close()
            raise ServiceError(
                "REMOTE_CLEARTEXT",
                f"refusing to serve a non-loopback bind ({host!r}) without TLS - "
                f"the bearer token would cross the network in the clear; pass "
                f"tls=True (and have the 'cryptography' lib installed), or bind "
                f"loopback")
        self.port = self.httpd.server_address[1]

    def serve_background(self) -> threading.Thread:
        t = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        t.start()
        return t

    def shutdown(self):
        self.httpd.shutdown()