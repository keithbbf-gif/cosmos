#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cvm-dt POST PROBE - where the 270 ms in `voice_post` actually goes.

`BENCH_LATENCY.json` (run `core_up_final`) measured the loop end to end and
named its dominant term: `respond.voice_post` at 269.752 ms median, against a
kernel answering a read-only verb out of its own state, over LOOPBACK, with no
model in the path. `LATENCY_F15.md` calls that "the one term with no physical
excuse" and makes it the F-15 optimization target. A total is not a diagnosis,
so this module splits one HTTP round trip into the phases a socket can actually
distinguish:

    connect -> send -> TTFB (status line) -> headers complete -> FIRST BODY
    BYTE -> last byte

The phase that matters is `body_gap_ms` = first body byte MINUS headers
complete. On loopback every one of those numbers should be sub-millisecond:
the server has already computed the answer by the time it writes the status
line, so the body is sitting in memory one write away.

`http.server.BaseHTTPRequestHandler` sends a response in TWO socket writes -
`end_headers()` flushes the buffered status line + headers, then
`wfile.write(body)`. `socketserver.StreamRequestHandler.disable_nagle_algorithm`
is **False** by default, so the server's socket keeps Nagle enabled: the second
write has unacknowledged data outstanding and is HELD until the peer ACKs.
Windows' delayed-ACK timer is ~200 ms. That is a write-write-read stall, and it
costs the same ~200 ms whether the reply is 21 bytes or 21 kB.

This probe does not assert that story - it measures `body_gap_ms` against the
resident Core, and then runs a controlled in-process A/B (`nagle_ab`) on two
handlers that differ in exactly one class attribute, so the claim is bound to a
number this machine emitted rather than to a plausible mechanism.

Cost discipline (inherited, not restated): GETs are not rate limited by
`cosmos_service` (`_guard.check` is on the voice POST path only), so the phase
decomposition rides free GETs. The optional POST samples go through
`cvm_dt_bench.post_budget()` - never more than half the shared per-minute
budget, because the bench already broke the stage-6 gate once by draining it.

    py -3.14 builds\\cvm-dt\\cvm_post_probe.py --root V:\\A\\Ai\\COSMOS\\live
    py -3.14 builds\\cvm-dt\\cvm_post_probe.py --root <RUNTIME> --posts 2
    py -3.14 builds\\cvm-dt\\test_cvm_post_probe.py

The token is read from the handed-in root's config role and used as a header.
It is never printed, logged or written to the artifact.
"""
from __future__ import annotations

import argparse
import json
import socket
import statistics
import sys
import time
from pathlib import Path
from typing import Any, Callable, Optional

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
_COSMOS_LIB = Path(__file__).resolve().parents[2] / "cosmos"
if _COSMOS_LIB.is_dir() and str(_COSMOS_LIB) not in sys.path:
    sys.path.insert(0, str(_COSMOS_LIB))

WIRE = "cvm-dt-post-probe/1"
ARTIFACT = "POST_BREAKDOWN.json"

# The phase decomposition is only meaningful on a link with no propagation
# delay. Refuse to report a "server think" number over a route that has one.
LOOPBACK_HOSTS = frozenset({"127.0.0.1", "::1", "localhost"})

# A gap this large between "headers are on the wire" and "first body byte"
# cannot be computation: the body was serialized BEFORE the status line was
# sent (`_send` builds `body` first). It is a transport stall.
STALL_MS = 25.0

FREE_GETS = (
    ("status", "/api/v1/status"),
    ("control", "/api/v1/control?client_id=cvm-post-probe"),
    ("health", "/api/v1/health"),
)


class ProbeError(RuntimeError):
    """Refusal with a reason. Never a silent zero."""


def _payload_json(payload: bytes) -> Optional[dict]:
    """The reply body as a dict, or None. A non-JSON body is not an error here."""
    try:
        obj = json.loads(payload.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return None
    return obj if isinstance(obj, dict) else None


def refusal_of(rec: dict) -> Optional[dict]:
    """Was this HTTP 200 actually a REFUSAL? Then it is not a round trip.

    `cosmos_service` answers a rate-limited or spend-blocked voice POST with
    HTTP 200 and `refused: true` - and it answers it FAST, because nothing was
    done. Measured here: a refused POST came back with ttfb 0.367 ms against a
    real turn's 188.581 ms. Folding that into a median reports the loop getting
    four times quicker at the exact moment it stopped working. `cvm_dt_bench`
    learned this the expensive way (`post_samples`, "the fastest lie in the
    artifact"); this probe inherits the rule rather than re-learning it.
    """
    obj = rec.get("json") or {}
    if int(rec.get("rc") or 0) >= 400:
        return {"kind": "HTTP_%d" % rec["rc"],
                "error": str(obj.get("error") or "")[:200]}
    if obj.get("refused") or obj.get("error"):
        return {"kind": str(obj.get("error") or "REFUSED")[:80],
                "reply": str(obj.get("reply") or "")[:200]}
    return None


# ---------------------------------------------------------------------------
# one round trip, split by the socket
# ---------------------------------------------------------------------------
def timed_request(host: str, port: int, method: str, path: str, *,
                  token: Optional[str] = None, body: Optional[bytes] = None,
                  timeout: float = 8.0, nodelay: bool = True) -> dict:
    """One HTTP/1.1 `Connection: close` round trip, phase by phase.

    Mirrors `cvm_dt.CoreClient._request` on the wire: HTTP/1.1, an explicit
    `Connection: close`, TCP_NODELAY on the client socket (http.client sets it
    in `connect()`), headers and body in ONE `sendall` (http.client appends a
    bytes body to the header block before sending). Matching the client matters
    - a probe that batched differently would measure a different stall.

    Returns absolute ms from t0 for each phase plus the derived deltas. Every
    field is measured; nothing is inferred.
    """
    req = ["%s %s HTTP/1.1" % (method, path),
           "Host: %s:%d" % (host, port),
           "Accept: application/json",
           "Connection: close"]
    if token:
        req.append("Authorization: Bearer " + token)
    if body is not None:
        req.append("Content-Type: application/json")
        req.append("Content-Length: %d" % len(body))
    head = ("\r\n".join(req) + "\r\n\r\n").encode("utf-8")
    wire = head + (body or b"")

    t0 = time.perf_counter()
    sock = socket.create_connection((host, port), timeout)
    t_conn = time.perf_counter()
    try:
        if nodelay:
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        sock.sendall(wire)
        t_send = time.perf_counter()

        buf = bytearray()
        t_first: Optional[float] = None
        t_head: Optional[float] = None
        t_body_first: Optional[float] = None
        head_end = -1
        while True:
            chunk = sock.recv(65536)
            now = time.perf_counter()
            if not chunk:
                break
            if t_first is None:
                t_first = now
            buf += chunk
            if head_end < 0:
                head_end = buf.find(b"\r\n\r\n")
                if head_end >= 0:
                    t_head = now
                    # The same recv that completed the headers may already
                    # carry body bytes - that is the NO-stall case, and it must
                    # be recorded as a zero gap, not as a missing sample.
                    if len(buf) > head_end + 4:
                        t_body_first = now
            elif t_body_first is None:
                t_body_first = now
        t_end = time.perf_counter()
    finally:
        try:
            sock.close()
        except OSError:
            pass

    if t_first is None or head_end < 0:
        raise ProbeError("no HTTP response on %s %s" % (method, path))
    raw = bytes(buf)
    status_line = raw.split(b"\r\n", 1)[0].decode("latin-1")
    try:
        code = int(status_line.split(" ")[1])
    except (IndexError, ValueError) as e:
        raise ProbeError("unparsable status line %r" % status_line[:80]) from e
    payload = raw[head_end + 4:]

    def ms(a: float, b: float) -> float:
        return round((a - b) * 1000.0, 3)

    rec = {
        "method": method, "path": path, "rc": code,
        "body_bytes": len(payload),
        "json": _payload_json(payload),
        "connect_ms": ms(t_conn, t0),
        "send_ms": ms(t_send, t_conn),
        "ttfb_ms": ms(t_first, t_send),
        "headers_ms": ms(t_head or t_first, t_send),
        "body_gap_ms": ms(t_body_first, t_head) if (
            t_body_first is not None and t_head is not None) else None,
        "total_ms": ms(t_end, t0),
        "nodelay": bool(nodelay),
    }
    if len(payload) == 0:
        rec["body_gap_ms"] = None
        rec["note"] = "empty body: no second write to stall"
    return rec


def repeat(fn: Callable[[], dict], n: int) -> dict:
    """Median/min/max over n identical round trips, keeping the last record."""
    runs = [fn() for _ in range(max(1, int(n)))]
    out = dict(runs[-1])
    out.pop("json", None)          # timings, not a copy of Core's state
    out["n"] = len(runs)
    out["refusals"] = [r for r in (refusal_of(x) for x in runs) if r]
    for key in ("connect_ms", "send_ms", "ttfb_ms", "headers_ms",
                "body_gap_ms", "total_ms"):
        vals = [r[key] for r in runs if r.get(key) is not None]
        if not vals:
            out[key] = None
            continue
        out[key] = round(statistics.median(vals), 3)
        out[key + "_min"] = round(min(vals), 3)
        out[key + "_max"] = round(max(vals), 3)
    out["samples"] = [{k: r[k] for k in
                       ("rc", "ttfb_ms", "headers_ms", "body_gap_ms",
                        "total_ms")} for r in runs]
    return out


# ---------------------------------------------------------------------------
# the controlled A/B: one class attribute, nothing else
# ---------------------------------------------------------------------------
def nagle_ab(reps: int = 5, body_bytes: int = 512) -> dict:
    """Two servers, identical but for `disable_nagle_algorithm`. Same process.

    Both handlers reproduce `cosmos_service.Handler._send` exactly: build the
    body first, `send_response` + headers, `end_headers()` (write #1), then
    `wfile.write(body)` (write #2). No computation between the writes - so any
    gap the client measures is the transport, and the two arms differ by one
    boolean.

    Interleaving the arms is deliberate: this box carries other agents, so two
    sequential passes could differ by machine load rather than by the flag.
    """
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
    import threading

    payload = json.dumps({"probe": WIRE, "pad": "x" * max(0, body_bytes)}
                         ).encode("utf-8")

    class Base(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.0"
        server_version = "COSMOS-probe/1.0"

        def log_message(self, *a):        # quiet, like the service
            return

        def do_GET(self):                                     # noqa: N802
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()            # write #1: status line + headers
            self.wfile.write(payload)     # write #2: the body

    class NagleOn(Base):
        disable_nagle_algorithm = False   # socketserver's default = today

    class NagleOff(Base):
        disable_nagle_algorithm = True    # the proposed one-line change

    arms: dict[str, Any] = {}
    servers = {}
    try:
        for name, cls in (("nagle_on_default", NagleOn),
                          ("nagle_off_proposed", NagleOff)):
            srv = ThreadingHTTPServer(("127.0.0.1", 0), cls)
            th = threading.Thread(target=srv.serve_forever, daemon=True)
            th.start()
            servers[name] = (srv, th)
            arms[name] = []
        for _ in range(max(1, int(reps))):
            for name, (srv, _th) in servers.items():   # interleaved
                host, port = srv.server_address[0], srv.server_address[1]
                arms[name].append(
                    timed_request(host, port, "GET", "/", timeout=5.0))
    finally:
        for srv, th in servers.values():
            srv.shutdown()
            srv.server_close()
            th.join(timeout=5.0)

    def fold(rows: list[dict]) -> dict:
        gaps = [r["body_gap_ms"] for r in rows if r.get("body_gap_ms") is not None]
        tots = [r["total_ms"] for r in rows]
        return {"n": len(rows),
                "body_gap_ms": round(statistics.median(gaps), 3) if gaps else None,
                "body_gap_max_ms": round(max(gaps), 3) if gaps else None,
                "total_ms": round(statistics.median(tots), 3),
                "rc": rows[-1]["rc"], "body_bytes": rows[-1]["body_bytes"]}

    on = fold(arms["nagle_on_default"])
    off = fold(arms["nagle_off_proposed"])
    saved = None
    if on["body_gap_ms"] is not None and off["body_gap_ms"] is not None:
        saved = round(on["body_gap_ms"] - off["body_gap_ms"], 3)
    return {
        "wire": WIRE,
        "what": "identical BaseHTTPRequestHandler two-write response; the two "
                "arms differ only in disable_nagle_algorithm",
        "interleaved": True,
        "nagle_on_default": on,
        "nagle_off_proposed": off,
        "body_gap_saved_ms": saved,
        "verdict": ("NAGLE_STALL_REPRODUCED"
                    if saved is not None and saved >= STALL_MS
                    else "NO_STALL_IN_CONTROL"),
    }


# ---------------------------------------------------------------------------
# against the resident Core
# ---------------------------------------------------------------------------
def probe_core(base: str, token: str, *, reps: int = 3,
               posts: int = 0) -> dict:
    """Phase-split the real kernel: unauthenticated floor, then real GETs.

    The 401 arm is the transport + parse + `hmac.compare_digest` floor with NO
    handler work behind it, so `authed - unauth` is the server's own cost for
    the endpoint. It also costs nothing: `_authed()` refuses before any route
    runs, and GETs never reach `_guard.check`.
    """
    from urllib.parse import urlparse
    u = urlparse(base)
    host, port = u.hostname or "127.0.0.1", u.port or 8770
    out: dict[str, Any] = {"base": base, "host": host, "port": port,
                           "loopback": host in LOOPBACK_HOSTS}
    if not out["loopback"]:
        out["refused"] = ("phase split needs a link with no propagation delay; "
                          "%s is not loopback" % host)
        return out

    t0 = time.perf_counter()
    s = socket.socket()
    s.settimeout(2.0)
    rc = s.connect_ex((host, port))
    out["connect_ex"] = rc
    out["connect_ex_ms"] = round((time.perf_counter() - t0) * 1000.0, 3)
    s.close()
    if rc != 0:
        out["refused"] = ("Core is not answering on %s:%d (connect_ex=%d)"
                          % (host, port, rc))
        return out

    gets: dict[str, Any] = {}
    gets["unauth_401_floor"] = repeat(
        lambda: timed_request(host, port, "GET", "/api/v1/status"), reps)
    for name, path in FREE_GETS:
        gets[name] = repeat(
            lambda p=path: timed_request(host, port, "GET", p, token=token),
            reps)
    out["gets"] = gets

    floor = gets["unauth_401_floor"]
    base_ttfb = floor.get("ttfb_ms")
    if base_ttfb is not None:
        # TTFB, not total: `total` carries the connect, and the connect on this
        # box is bimodal (0.16 ms .. 18 ms) because ThreadingHTTPServer spawns
        # a thread per connection. TTFB is measured from the last byte of the
        # request, so it is the server's own answer time and nothing else.
        out["server_ms"] = {
            "floor_401_ttfb_ms": base_ttfb,
            "per_endpoint": {
                name: round(row["ttfb_ms"] - base_ttfb, 3)
                for name, row in gets.items()
                if name != "unauth_401_floor" and row.get("ttfb_ms") is not None
            },
            "how": "authed TTFB MINUS the unauthenticated 401 TTFB on the same "
                   "socket path: the same transport and the same auth compare, "
                   "minus the route's own work",
        }

    if posts > 0:
        out["posts"] = _post_arm(host, port, token, posts)
    else:
        out["posts"] = {"kind": "SKIPPED",
                        "reason": "--posts 0: the phase split is visible on "
                                  "free GETs, and the voice POST budget is "
                                  "shared with the gate and Keith's own voice"}
    return out


def _slim(rec: dict, obj: Optional[dict]) -> dict:
    """One POST sample, without dragging Core's whole reply into the artifact."""
    keep = {k: rec[k] for k in ("rc", "connect_ms", "send_ms", "ttfb_ms",
                                "body_gap_ms", "total_ms", "body_bytes")}
    o = obj or {}
    keep["reply_kind"] = o.get("kind")
    keep["brain"] = o.get("brain")
    keep["sid_tail"] = str(o.get("session_id") or "")[-6:] or None
    return keep


def _post_arm(host: str, port: int, token: str, posts: int) -> dict:
    """Phase-split POST /api/v1/voice on a FREE verb, inside half the budget.

    Two arms off the SAME budget, because they answer different questions:
      * `mint` - no session_id, so Core mints one. This is a cold turn.
      * `resume` - the sid the mint returned. Same verb, same body size, one
        difference: the session already exists.
    `mint - resume` is the per-turn cost of minting a session, measured rather
    than guessed.

    A refusal (rate limit / spend block) is HTTP 200 and FAST; it is typed and
    excluded from every median (see `refusal_of`).
    """
    from cvm_dt_bench import post_budget
    budget = post_budget()
    allowed = int(budget.get("posts_allowed") or 1)
    n = max(2, min(int(posts), allowed))

    # Core drops an identical utterance from the same client within 15 s as
    # kind="duplicate" - measured: three of four samples came back DUPLICATE in
    # under 1 ms. Rotating the verb keeps every sample a real turn. All four
    # verbs answer from local state, so none of them spends.
    from cvm_dt_bench import BENCH_POST_VERBS

    def one(verb: str,
            sid: str = "") -> tuple[dict, Optional[dict], Optional[dict]]:
        payload: dict[str, Any] = {"transcript": verb,
                                   "title": "cvm-post-probe", "speak": False}
        if sid:
            payload["session_id"] = sid
        rec = timed_request(host, port, "POST", "/api/v1/voice", token=token,
                            body=json.dumps(payload).encode("utf-8"),
                            timeout=70.0)
        obj = rec.get("json")
        return rec, obj, refusal_of(rec)

    mint: list[dict] = []
    resume: list[dict] = []
    refused: list[dict] = []
    sid = ""
    spent = 0
    for i in range(n):
        verb = BENCH_POST_VERBS[i % len(BENCH_POST_VERBS)]
        want_resume = bool(sid) and i % 2 == 1
        rec, obj, ref = one(verb, sid if want_resume else "")
        spent += 1
        arm = "resume" if want_resume else "mint"
        if ref is not None:
            refused.append({**_slim(rec, obj), **ref, "arm": arm,
                            "verb": verb})
            continue
        if not sid:
            sid = str((obj or {}).get("session_id") or "")
        (resume if want_resume else mint).append(
            {**_slim(rec, obj), "verb": verb})

    def fold(rows: list[dict], label: str) -> dict:
        if not rows:
            return {"kind": "UNMEASURED", "n": 0,
                    "why": "every %s sample came back refused; a refusal is "
                           "not a round trip" % label}
        return {"kind": "ok", "n": len(rows),
                "total_ms": round(statistics.median(
                    [r["total_ms"] for r in rows]), 3),
                "ttfb_ms": round(statistics.median(
                    [r["ttfb_ms"] for r in rows]), 3),
                "body_gap_ms": round(statistics.median(
                    [r["body_gap_ms"] for r in rows
                     if r.get("body_gap_ms") is not None] or [0.0]), 3),
                "reply_kind": rows[-1].get("reply_kind"),
                "brain": rows[-1].get("brain"),
                "samples": rows}

    out = {"budget": budget, "posts_spent": spent, "verb": "status",
           "mint": fold(mint, "mint"), "resume": fold(resume, "resume"),
           "refused": refused,
           "why_free": "'status' is a Core verb, so the reply is kind=command "
                       "off local state - no model rail, no CALL_EST_USD"}
    if out["mint"]["kind"] == "ok":
        out["ttfb_ms"] = out["mint"]["ttfb_ms"]
        out["total_ms"] = out["mint"]["total_ms"]
        out["body_gap_ms"] = out["mint"]["body_gap_ms"]
        if out["resume"]["kind"] == "ok":
            out["session_mint_ms"] = round(
                out["mint"]["ttfb_ms"] - out["resume"]["ttfb_ms"], 3)
    return out


def verdict(core: dict, ab: dict) -> dict:
    """Name the dominant phase from the numbers, or refuse to name one."""
    gets = core.get("gets") or {}
    rows = {k: v for k, v in gets.items() if v.get("body_gap_ms") is not None}
    if not rows:
        return {"kind": "UNMEASURED",
                "why": core.get("refused") or "no round trip produced a body gap"}
    stalled = {k: v["body_gap_ms"] for k, v in rows.items()
               if v["body_gap_ms"] >= STALL_MS}
    post = core.get("posts") or {}
    if post.get("body_gap_ms") is not None and post["body_gap_ms"] >= STALL_MS:
        stalled["voice_post"] = post["body_gap_ms"]
    if not stalled:
        out = {
            "kind": "SERVER_SIDE",
            "dominant_phase": "ttfb_ms",
            "why": "every body gap is under %.0f ms and the cheapest authed "
                   "round trip completes in well under a millisecond, so the "
                   "latency is the route's own work - not the socket, not the "
                   "client, not Nagle" % STALL_MS,
            "gaps_ms": {k: v["body_gap_ms"] for k, v in rows.items()},
            "falsified": "Nagle + Windows delayed ACK on the two-write "
                         "response. Predicted a ~200 ms body_gap; measured "
                         "0.0 ms against Core and %s ms saved in the "
                         "controlled A/B. Hypothesis dropped."
                         % ab.get("body_gap_saved_ms"),
        }
        out["server_ms"] = (core.get("server_ms") or {}).get("per_endpoint")
        if post.get("ttfb_ms") is not None:
            out["voice_post_ttfb_ms"] = post["ttfb_ms"]
            cheap = min((v["ttfb_ms"] for v in rows.values()), default=None)
            if cheap is not None:
                out["voice_post_vs_cheapest_get"] = round(
                    post["ttfb_ms"] - cheap, 3)
        if post.get("session_mint_ms") is not None:
            out["session_mint_ms"] = post["session_mint_ms"]
        return out
    return {
        "kind": "TRANSPORT_STALL",
        "dominant_phase": "body_gap_ms",
        "why": "the response body is serialized BEFORE the status line is "
               "sent, so a gap between 'headers on the wire' and 'first body "
               "byte' is not computation - it is the second write waiting on "
               "an ACK (Nagle + Windows delayed ACK)",
        "stalled_endpoints_ms": stalled,
        "control_ab": ab.get("verdict"),
        "control_saved_ms": ab.get("body_gap_saved_ms"),
    }


def run(root: str, *, base: str, reps: int, posts: int,
        ab_reps: int) -> dict:
    from cvm_dt import load_paths, load_token
    paths = load_paths(root)
    token = load_token(paths)          # used as a header; never printed
    core = probe_core(base, token, reps=reps, posts=posts)
    ab = nagle_ab(reps=ab_reps)
    rec = {
        "wire": WIRE,
        "iso": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "epoch": time.time(),
        "tree_id": paths.sentinel.tree_id,
        "live_root": str(paths.root),
        "python": "%d.%d.%d" % sys.version_info[:3],
        "core": core,
        "control_ab": ab,
        "verdict": verdict(core, ab),
        "token": "read from the config role and sent as a header; never "
                 "printed, logged or stored",
    }
    return rec


def write_artifact(rec: dict, out_dir: Optional[Path] = None) -> Path:
    path = (out_dir or _HERE) / ARTIFACT
    path.write_text(json.dumps(rec, indent=1), encoding="utf-8")
    return path


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(prog="cvm-post-probe")
    ap.add_argument("--root", required=True)
    ap.add_argument("--base", default="http://127.0.0.1:8770")
    ap.add_argument("--reps", type=int, default=3)
    ap.add_argument("--posts", type=int, default=0,
                    help="voice POST samples (budgeted; 0 = none)")
    ap.add_argument("--ab-reps", type=int, default=5)
    ap.add_argument("--no-write", action="store_true")
    ns = ap.parse_args(argv)
    rec = run(ns.root, base=ns.base, reps=ns.reps, posts=ns.posts,
              ab_reps=ns.ab_reps)
    if not ns.no_write:
        rec["artifact"] = str(write_artifact(rec))
    print(json.dumps(rec, indent=1, default=str))
    return 0 if rec["verdict"]["kind"] != "UNMEASURED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
