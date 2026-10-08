#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Loopback tests: thin-phone GET-first + idle skip-POST, never a second owner.

Proves:
  * one cycle GETs /cvm/pull then POSTs /cvm/push; audio_owner stays desktop
  * a replayed / idle second cycle skips the identical POST (not a second owner)
  * HOLD pause does not hit Core (tick composed from cvm_dt_clock.poll_once)
  * RESUME-GATE idles and does not self-clear; dead Core is UNREACHABLE
    yet the clock still heartbeats

No live :8770. rc=0 here is a green log. Stage-6 quotes
live_value.tick_ms + skipped_http + http_posts from a real GET
/api/v1/cvm/pull after this clock POSTs /cvm/push against a restarted
:8770 — audio_owner remains the desktop-owned token and an idle second
tick skips the replay POST. An exit code is not evidence.
"""
from __future__ import annotations

import json
import re
import sys
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
if (HERE / "cvm_phone_clock.py").is_file() or (HERE / "cvm_dt.py").is_file():
    PHONE_DIR = HERE
    DT_DIR = HERE.parent / "cvm-dt" if not (HERE / "cvm_dt.py").is_file() else HERE
    COSMOS_DIR = HERE.parents[1] / "cosmos"
    sys.path.insert(0, str(PHONE_DIR))
    if DT_DIR.is_dir():
        sys.path.insert(0, str(DT_DIR))
    if COSMOS_DIR.is_dir():
        sys.path.insert(0, str(COSMOS_DIR))
    CLOCK_SRC = PHONE_DIR / "cvm_phone_clock.py"
else:
    BUNDLE = HERE.parent
    REPO = BUNDLE.parent.parent
    LIVE_DT = REPO / "builds" / "cvm-dt"
    COSMOS_DIR = REPO / "cosmos"
    BUNDLE_PHONE = BUNDLE / "builds" / "cvm-phone"
    if LIVE_DT.is_dir():
        sys.path.insert(0, str(LIVE_DT))
    if COSMOS_DIR.is_dir():
        sys.path.insert(0, str(COSMOS_DIR))
    if BUNDLE_PHONE.is_dir():
        sys.path.insert(0, str(BUNDLE_PHONE))
    CLOCK_SRC = BUNDLE_PHONE / "cvm_phone_clock.py"

from cosmos_paths import CosmosPaths, write_sentinel  # noqa: E402

from cvm_dt import (  # noqa: E402
    CoreClient, CvmDtError, FAST_READ_S, RefusalKind,
    audio_owner_of, core_get, core_post, refuse_http,
)
from cvm_pull import CONTRACT  # noqa: E402

import cvm_dt_clock as clk  # noqa: E402
from cvm_phone_clock import (  # noqa: E402
    PHONE_ID, PUSH_PATH, WRITER, CvmPhoneClock,
)

TREE_ID = "KMesh-COSMOS-live"
RESULTS = []
BTS_IMPORT = re.compile(r"^\s*(?:from|import)\s+bts_\w+", re.M)
CLAIM_DESKTOP = re.compile(r"\bclaim_desktop\b")
HANDOFF_IMPORT = re.compile(r"^\s*(?:from|import)\s+cvm_handoff\b", re.M)
ASSIGN_PHONE_OWNER = re.compile(
    r"""audio_owner["']\s*\]\s*=\s*["']phone["']"""
    r"""|audio_owner\s*=\s*["']phone["']""")


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:                                            # noqa: BLE001
        RESULTS.append((label, False, "%s: %s" % (type(e).__name__, e)))


class _FakeCore(BaseHTTPRequestHandler):
    """HTTP double: POST /cvm/push + GET /cvm/pull. Owner stays desktop."""

    token = "test-token"
    tree_id = TREE_ID
    pulls = 0
    pushes = 0
    last_push = None
    last_rid = ""
    push_audio_keys = []
    owners_quoted = []
    audio_owner = "desktop"
    cursor = "desk-1"

    def log_message(self, *args):                                     # noqa: ARG002
        return

    @classmethod
    def reset(cls):
        cls.pulls = 0
        cls.pushes = 0
        cls.last_push = None
        cls.last_rid = ""
        cls.push_audio_keys = []
        cls.owners_quoted = []
        cls.audio_owner = "desktop"
        cls.cursor = "desk-1"

    def _send(self, code, obj):
        body = json.dumps(obj).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):                                                 # noqa: N802
        if self.headers.get("Authorization") != "Bearer " + self.token:
            return self._send(401, {"error": "UNAUTHORIZED"})
        if not self.path.startswith("/api/v1/cvm/pull"):
            return self._send(404, {"error": "NOT_FOUND", "path": self.path})
        type(self).pulls += 1
        owner = type(self).audio_owner
        type(self).owners_quoted.append(owner)
        return self._send(200, {
            "cvm": 1,
            "tree_id": self.tree_id,
            "issued_epoch": 1787800000.0,
            "pull": True,
            "kinds": ["voice_session", "device", "notifications"],
            "cursor": type(self).cursor,
            "audio_owner": owner,
            "voice_client_timeout_s": 70.0,
            "core_kind": "ok",
            "client_id": PHONE_ID,
        })

    def do_POST(self):                                                # noqa: N802
        if self.headers.get("Authorization") != "Bearer " + self.token:
            return self._send(401, {"error": "UNAUTHORIZED"})
        parsed = self.path.split("?", 1)[0]
        if parsed != PUSH_PATH:
            return self._send(404, {"error": "NOT_FOUND", "path": self.path})
        n = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(n) if n else b"{}"
        try:
            body = json.loads(raw.decode("utf-8") or "{}")
        except ValueError:
            return self._send(400, {"error": "BAD_SNAPSHOT"})
        if not isinstance(body, dict):
            return self._send(400, {"error": "BAD_SNAPSHOT"})
        rid = str(body.get("request_id") or "")
        replayed = bool(type(self).last_rid) and rid == type(self).last_rid
        type(self).pushes += 1
        type(self).last_push = body
        type(self).last_rid = rid
        type(self).push_audio_keys.append(
            "audio_owner" if "audio_owner" in body else None)
        cursor_out = "phone-turn-" + (rid or "x")[:12]
        if not replayed:
            type(self).cursor = cursor_out
        return self._send(200, {
            "ok": True,
            "cvm": 1,
            "cursor_out": type(self).cursor,
            "idempotent": replayed,
            "stored": list((body.get("kinds") or {}).keys()),
            "audio_owner": type(self).audio_owner,
            "claimed": False,
        })


class _FakeNot200(BaseHTTPRequestHandler):
    """HTTP double that answers !=200 on GET /cvm/pull and POST /cvm/push."""

    token = "test-token"

    def log_message(self, *args):                                     # noqa: ARG002
        return

    def do_GET(self):                                                 # noqa: N802
        body = json.dumps({"error": "BAD_CORE", "detail": "HTTP_503"}).encode("utf-8")
        self.send_response(503)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):                                                # noqa: N802
        return self.do_GET()


class _BoomCore(BaseHTTPRequestHandler):
    """Must not be hit on a HOLD tick."""

    def log_message(self, *args):                                     # noqa: ARG002
        return

    def do_GET(self):                                                 # noqa: N802
        raise AssertionError("paused tick must not GET Core")

    def do_POST(self):                                                # noqa: N802
        raise AssertionError("paused tick must not POST Core")


def _serve(handler):
    httpd = HTTPServer(("127.0.0.1", 0), handler)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    return httpd


def _scratch():
    tmp = Path(tempfile.mkdtemp(prefix="cvm-phone-clock-test-"))
    write_sentinel(tmp, TREE_ID)
    (tmp / "config").mkdir()
    (tmp / "state").mkdir()
    (tmp / "logs").mkdir()
    (tmp / "config" / "api_token.txt").write_text("test-token", encoding="utf-8")
    return tmp


def _src() -> str:
    return CLOCK_SRC.read_text(encoding="utf-8")


def _kinds():
    return {"device": {"status": "ok", "battery_pct": 80,
                       "net": "tailscale", "audio_route": "none"}}


def test_thin_phone_never_second_audio_owner():
    """Runtime-binding test: push + pull, owner stays desktop, no claim."""
    _FakeCore.reset()
    tmp = _scratch()
    httpd = _serve(_FakeCore)
    bad = _serve(_FakeNot200)
    base = "http://127.0.0.1:%d" % httpd.server_address[1]
    bad_base = "http://127.0.0.1:%d" % bad.server_address[1]
    try:
        paths = CosmosPaths(tmp)
        client = CvmPhoneClock(
            CoreClient(base, "test-token"), paths,
            push_request_id="r-phone", kinds=_kinds())
        rec1 = client.cycle_once()
        rec2 = client.cycle_once()

        turn_p = paths.state("cvm", "phone_turn.json")
        turn = json.loads(turn_p.read_text(encoding="utf-8"))
        pull_p = paths.state("cvm", "pull.json")
        handoff_p = paths.state("cvm", "handoff.json")
        audio_json = tmp / "state" / "cvm" / "audio.json"

        owners = {
            rec1["audio_owner"], rec2["audio_owner"],
            rec1["live_value"]["audio_owner"],
            rec2["quoted_audio_owner"],
            turn["quoted_audio_owner"],
            audio_owner_of(_FakeCore.last_push or {}),
        }
        owners.discard("none")

        dead_kind = None
        try:
            CvmPhoneClock(
                CoreClient("http://127.0.0.1:1", "test-token"),
                paths, push_request_id="r-dead").cycle_once()
        except CvmDtError as e:
            dead_kind = e.kind

        bad_kind = None
        try:
            CvmPhoneClock(
                CoreClient(bad_base, "test-token"),
                paths, push_request_id="r-bad").cycle_once()
        except CvmDtError as e:
            bad_kind = e.kind

        src = _src()
        push_body = _FakeCore.last_push or {}
        return (
            FAST_READ_S == 8.0
            and CONTRACT == (
                "tree_id", "issued_epoch", "kinds", "cursor",
                "audio_owner", "voice_client_timeout_s",
            )
            and rec1["audio_owner"] == "desktop"
            and rec1["claimed"] is False
            and rec1["writer"] == WRITER
            and rec1["client_id"] == PHONE_ID
            and rec1["pushed_to"] == "POST /api/v1/cvm/push"
            and rec1["quoted_from"] == "GET /api/v1/cvm/pull"
            and rec1["quoted_audio_owner"] == "desktop"
            and rec1["live_value"]["audio_owner"] == "desktop"
            and rec1["live_value"]["claimed"] is False
            and rec1["cursor_advanced"] is True
            and rec1["cursor"]
            and rec1["cursor"] != rec1["cursor_prev"]
            and rec1["push_replayed"] is False
            and rec2["audio_owner"] == "desktop"
            and rec2["claimed"] is False
            and rec2["push_replayed"] is True
            and rec2["cursor"] == rec1["cursor"]
            and owners == {"desktop"}
            and set(_FakeCore.owners_quoted) == {"desktop"}
            and _FakeCore.audio_owner == "desktop"
            and rec2["skipped_http"] is True
            and rec2["push_replayed"] is True
            and _FakeCore.pushes == 1
            and _FakeCore.pulls == 1
            and "audio_owner" not in push_body
            and push_body.get("cvm") == 1
            and push_body.get("client_id") == PHONE_ID
            and push_body.get("request_id") == "r-phone"
            and all(k is None for k in _FakeCore.push_audio_keys)
            and turn["claimed"] is False
            and turn["writer"] == WRITER
            and "audio_owner" not in turn
            and turn["quoted_audio_owner"] == "desktop"
            and not pull_p.exists()
            and not handoff_p.exists()
            and not audio_json.exists()
            and dead_kind == RefusalKind.UNREACHABLE
            and bad_kind == RefusalKind.BAD_CORE
            and callable(core_get) and callable(core_post) and callable(refuse_http)
            and PHONE_ID == "cvm-phone"
            and PUSH_PATH == "/api/v1/cvm/push"
            and BTS_IMPORT.search(src) is None
            and CLAIM_DESKTOP.search(src) is None
            and HANDOFF_IMPORT.search(src) is None
            and ASSIGN_PHONE_OWNER.search(src) is None
            and "def pause_flag" not in src
            and "def write_heartbeat" not in src
            and "def is_paused" not in src
            and "CvmDtClient(" not in src
            and ".loop(" not in src
            and "V:\\" not in src
            and "poll_once" in src
            and client.tick.__func__ is CvmPhoneClock.tick
        )
    finally:
        httpd.shutdown()
        bad.shutdown()


def test_replayed_push_not_second_owner():
    _FakeCore.reset()
    tmp = _scratch()
    httpd = _serve(_FakeCore)
    base = "http://127.0.0.1:%d" % httpd.server_address[1]
    try:
        paths = CosmosPaths(tmp)
        client = CvmPhoneClock(
            CoreClient(base, "test-token"), paths,
            push_request_id="r-phone", kinds=_kinds())
        rec1 = client.cycle_once()
        rec2 = client.cycle_once()
        owners = {rec1["audio_owner"], rec2["audio_owner"],
                  rec1["live_value"]["audio_owner"],
                  rec2["live_value"]["audio_owner"]}
        return (
            rec1["push_replayed"] is False
            and rec2["push_replayed"] is True
            and rec1["claimed"] is False
            and rec2["claimed"] is False
            and rec2["cursor"] == rec1["cursor"]
            and rec2["skipped_http"] is True
            and owners == {"desktop"}
            and _FakeCore.audio_owner == "desktop"
            and _FakeCore.pushes == 1
            and _FakeCore.pulls == 1
            and all(k is None for k in _FakeCore.push_audio_keys)
        )
    finally:
        httpd.shutdown()


def test_idle_second_cycle_skips_replay_post():
    """Isolates GET-first + idle skip-POST. Prints actual vs expected.

    Failed on the POST-then-GET baseline (http_posts=2, http_gets=2,
    skipped_http=false, cycle2 wall ~16ms). Passes when the idle tick
    posts 0 extra bytes and quotes desktop without a second owner.
    """
    _FakeCore.reset()
    tmp = _scratch()
    httpd = _serve(_FakeCore)
    base = "http://127.0.0.1:%d" % httpd.server_address[1]
    try:
        paths = CosmosPaths(tmp)
        client = CvmPhoneClock(
            CoreClient(base, "test-token"), paths,
            push_request_id="r-phone", kinds=_kinds())
        rec1 = client.cycle_once()
        rec2 = client.cycle_once()
        expected = {
            "http_gets": 1,
            "http_posts": 1,
            "skipped_http": True,
            "push_bytes_idle": 0,
            "cursor_stable": True,
            "audio_owner": "desktop",
            "claimed": False,
            "core_gets": 1,
            "core_posts": 1,
        }
        actual = {
            "http_gets": rec2.get("http_gets"),
            "http_posts": rec2.get("http_posts"),
            "skipped_http": rec2.get("skipped_http"),
            "push_bytes_idle": rec2.get("push_bytes"),
            "cursor_stable": rec2.get("cursor") == rec1.get("cursor"),
            "audio_owner": rec2.get("audio_owner"),
            "claimed": rec2.get("claimed"),
            "core_gets": _FakeCore.pulls,
            "core_posts": _FakeCore.pushes,
        }
        mismatches = [k for k in expected if actual.get(k) != expected[k]]
        tick1 = rec1.get("tick_ms")
        tick2 = rec2.get("tick_ms")
        print("actual vs expected: " + json.dumps({
            "actual": actual, "expected": expected,
            "mismatches": mismatches,
            "tick_ms_first": tick1, "tick_ms_idle": tick2,
            "push_bytes_first": rec1.get("push_bytes"),
            "pull_ms_first": rec1.get("pull_ms"),
            "quoted_from_idle": rec2.get("quoted_from"),
        }, sort_keys=True))
        return (
            not mismatches
            and rec1.get("skipped_http") is False
            and rec1.get("push_bytes") > 0
            and rec1.get("cursor_advanced") is True
            and rec2.get("push_replayed") is True
            and isinstance(tick1, (int, float)) and tick1 >= 0
            and isinstance(tick2, (int, float)) and tick2 >= 0
            and tick2 < tick1
            and rec2.get("quoted_from") == "local phone_turn.json"
            and rec2.get("live_value", {}).get("skipped_http") is True
            and rec2.get("live_value", {}).get("http_posts") == 1
        )
    finally:
        httpd.shutdown()


def test_hold_pause_does_not_hit_core():
    tmp = _scratch()
    httpd = _serve(_BoomCore)
    base = "http://127.0.0.1:%d" % httpd.server_address[1]
    try:
        paths = CosmosPaths(tmp)
        flag = paths.state("control", "PAUSE.flag")
        flag.parent.mkdir(parents=True, exist_ok=True)
        flag.write_text(json.dumps({
            "state": "PAUSED", "mode": "hold",
            "reason": "test-hold", "set_by": "test",
        }), encoding="utf-8")
        client = CvmPhoneClock(
            CoreClient(base, "test-token"), paths,
            push_request_id="r-hold")
        rec = client.tick(polls=1)
        hb = json.loads(paths.logs(clk.HEARTBEAT_NAME).read_text(
            encoding="utf-8"))
        pull = paths.state("cvm", "pull.json")
        turn = paths.state("cvm", "phone_turn.json")
        paused = clk.pause_flag(paths)
        return (
            rec["ok"] is True
            and rec["tick"] == "paused"
            and rec["state"] == "PAUSED"
            and rec["pause_present"] is True
            and rec["pause_mode"] == "hold"
            and hb["state"] == "PAUSED"
            and hb["last_run_epoch"] == rec["last_run_epoch"]
            and not pull.exists()
            and not turn.exists()
            and clk.is_paused(paused) is True
            and flag.exists()
        )
    finally:
        httpd.shutdown()


def test_resume_gate_idles_dead_core_heartbeats():
    tmp = _scratch()
    paths = CosmosPaths(tmp)
    flag = paths.state("control", "PAUSE.flag")
    flag.parent.mkdir(parents=True, exist_ok=True)
    flag.write_text(json.dumps({
        "state": "PAUSED", "mode": "resume_gate",
        "auto_resume_at": "2099-01-01T00:00:00-05:00",
        "reason": "test-gate",
    }), encoding="utf-8")
    client = CvmPhoneClock(
        CoreClient("http://127.0.0.1:1", "test-token"),
        paths, push_request_id="r-gate")
    paused = clk.pause_flag(paths)
    rec = client.tick(polls=1)
    still = flag.exists()

    flag.unlink()
    rec_dead = client.tick(polls=2, drain=True)
    hb = json.loads(Path(rec_dead["heartbeat_path"]).read_text(encoding="utf-8"))
    return (
        clk.is_paused(paused) is True
        and paused.get("mode") == "resume_gate"
        and rec["tick"] == "paused"
        and rec["pause_mode"] == "resume_gate"
        and rec["auto_resume_at"]
        and still
        and rec_dead["ok"] is False
        and rec_dead["kind"] == str(RefusalKind.UNREACHABLE)
        and rec_dead["tick"] == "refused"
        and hb["last_run_epoch"] == rec_dead["last_run_epoch"]
        and hb["clock_id"] == clk.CLOCK_ID
        and rec_dead["last_run_epoch"]
    )


def main() -> int:
    check("thin phone never becomes a second audio owner "
          "(GET-first, idle skip-POST, quotes desktop, no claim, "
          "no pull/audio/handoff write)",
          test_thin_phone_never_second_audio_owner)
    check("replayed push is ignored (not a second owner)",
          test_replayed_push_not_second_owner)
    check("idle second cycle skips replay POST (GET-first; prints "
          "actual vs expected http_gets/http_posts/tick_ms)",
          test_idle_second_cycle_skips_replay_post)
    check("HOLD pause does not hit Core",
          test_hold_pause_does_not_hit_core)
    check("RESUME-GATE idles and does not self-clear; dead Core is "
          "UNREACHABLE yet the clock still heartbeats",
          test_resume_gate_idles_dead_core_heartbeats)
    ok = all(p for _, p, _ in RESULTS)
    for label, passed, err in RESULTS:
        print(("PASS" if passed else "FAIL") + "  " + label
              + (("  " + err) if err else ""))
    print("result: " + ("ok" if ok else "FAIL")
          + "  %d/%d" % (sum(1 for _, p, _ in RESULTS if p), len(RESULTS)))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
