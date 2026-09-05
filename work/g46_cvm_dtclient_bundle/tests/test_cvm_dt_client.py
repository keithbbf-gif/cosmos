#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Loopback tests: pull → fold → handoff under audio_owner=desktop.

Proves:
  * one cycle yields a single owner==desktop and an advanced cursor
  * a replayed handoff is ignored (not a second owner)
  * HOLD pause does not pull Core (tick composed from cvm_dt_clock)
  * dead Core is UNREACHABLE yet the client still heartbeats

No live :8770. rc=0 here is a green log. Stage-6 quotes
live_value.audio_owner from a real GET /api/v1/cvm/pull after a
contested desktop handoff against a restarted :8770; live_value.cursor
on that same GET must be advanced vs the pre-cycle ticket.
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
if (HERE / "cvm_dt.py").is_file() or (HERE / "cvm_dt_client.py").is_file():
    DT_DIR = HERE
    COSMOS_DIR = HERE.parents[1] / "cosmos"
    sys.path.insert(0, str(DT_DIR))
    if COSMOS_DIR.is_dir():
        sys.path.insert(0, str(COSMOS_DIR))
    CLIENT_SRC = DT_DIR / "cvm_dt_client.py"
else:
    BUNDLE = HERE.parent
    REPO = BUNDLE.parent.parent
    LIVE_DT = REPO / "builds" / "cvm-dt"
    COSMOS_DIR = REPO / "cosmos"
    BUNDLE_DT = BUNDLE / "builds" / "cvm-dt"
    if LIVE_DT.is_dir():
        sys.path.insert(0, str(LIVE_DT))
    if COSMOS_DIR.is_dir():
        sys.path.insert(0, str(COSMOS_DIR))
    if BUNDLE_DT.is_dir():
        sys.path.insert(0, str(BUNDLE_DT))
    CLIENT_SRC = BUNDLE_DT / "cvm_dt_client.py"

from cosmos_paths import CosmosPaths, write_sentinel  # noqa: E402

from cvm_dt import (  # noqa: E402
    CLIENT_ID, CoreClient, CvmDtError, FAST_READ_S, RefusalKind,
    audio_owner_of, core_get, refuse_http,
)
from cvm_pull import CONTRACT  # noqa: E402
from cvm_snap import snapshot_delta  # noqa: E402

import cvm_dt_clock as clk  # noqa: E402
from cvm_dt_client import CvmDtClient  # noqa: E402

TREE_ID = "KMesh-COSMOS-live"
RESULTS = []
BTS_IMPORT = re.compile(r"^\s*(?:from|import)\s+bts_\w+", re.M)


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:                                            # noqa: BLE001
        RESULTS.append((label, False, "%s: %s" % (type(e).__name__, e)))


class _FakeCore(BaseHTTPRequestHandler):
    """HTTP double of GET /api/v1/cvm/pull. Owner starts on the phone."""

    token = "test-token"
    tree_id = TREE_ID
    pulls = 0

    def log_message(self, *args):                                     # noqa: ARG002
        return

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
        return self._send(200, {
            "cvm": 1,
            "tree_id": self.tree_id,
            "issued_epoch": 1787800000.0,
            "pull": True,
            "kinds": ["voice_session", "device", "notifications"],
            "cursor": "",
            "audio_owner": "phone",
            "voice_client_timeout_s": 70.0,
            "core_kind": "ok",
            "client_id": CLIENT_ID,
        })


class _FakeNot200(BaseHTTPRequestHandler):
    """HTTP double that answers !=200 on GET /cvm/pull."""

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


class _BoomCore(BaseHTTPRequestHandler):
    """Must not be hit on a HOLD tick."""

    def log_message(self, *args):                                     # noqa: ARG002
        return

    def do_GET(self):                                                 # noqa: N802
        raise AssertionError("paused tick must not GET Core")


def _serve(handler):
    httpd = HTTPServer(("127.0.0.1", 0), handler)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    return httpd


def _scratch():
    tmp = Path(tempfile.mkdtemp(prefix="cvm-dt-client-test-"))
    write_sentinel(tmp, TREE_ID)
    (tmp / "config").mkdir()
    (tmp / "state").mkdir()
    (tmp / "logs").mkdir()
    (tmp / "config" / "api_token.txt").write_text("test-token", encoding="utf-8")
    return tmp


def _seed_phone(paths: CosmosPaths) -> None:
    phone = paths.state("cvm", "phone.json")
    phone.parent.mkdir(parents=True, exist_ok=True)
    phone.write_text(json.dumps(snapshot_delta("r-snap", "", {
        "device": {"status": "ok", "battery_pct": 80,
                   "net": "tailscale", "audio_route": "none"},
    }, client_id="cvm-dt-client-test")), encoding="utf-8")


def _src() -> str:
    return CLIENT_SRC.read_text(encoding="utf-8")


def test_pull_fold_handoff_single_desktop_owner():
    """Runtime-binding test: cycle + contest + replay, one owner."""
    tmp = _scratch()
    httpd = _serve(_FakeCore)
    bad = _serve(_FakeNot200)
    base = "http://127.0.0.1:%d" % httpd.server_address[1]
    bad_base = "http://127.0.0.1:%d" % bad.server_address[1]
    try:
        paths = CosmosPaths(tmp)
        _seed_phone(paths)

        client = CvmDtClient(
            CoreClient(base, "test-token"), paths,
            handoff_request_id="r-desk")
        rec1 = client.cycle_once()

        lose_kind = None
        try:
            client.handoff.claim("phone", "r-contest")
        except CvmDtError as e:
            lose_kind = e.kind

        rec2 = client.cycle_once()

        pull_p = paths.state("cvm", "pull.json")
        published = json.loads(pull_p.read_text(encoding="utf-8"))
        handoff_p = paths.state("cvm", "handoff.json")
        stored = json.loads(handoff_p.read_text(encoding="utf-8"))
        turn_p = paths.state("cvm", "dt_turn.json")
        turn = json.loads(turn_p.read_text(encoding="utf-8"))
        audio_json = tmp / "state" / "cvm" / "audio.json"

        owners = {
            rec1["audio_owner"], rec2["audio_owner"],
            client.handoff.owner, audio_owner_of(published),
            audio_owner_of(stored),
        }

        dead_kind = None
        try:
            CvmDtClient(
                CoreClient("http://127.0.0.1:1", "test-token"),
                paths, handoff_request_id="r-dead").cycle_once()
        except CvmDtError as e:
            dead_kind = e.kind

        bad_kind = None
        try:
            CvmDtClient(
                CoreClient(bad_base, "test-token"),
                paths, handoff_request_id="r-bad").cycle_once()
        except CvmDtError as e:
            bad_kind = e.kind

        src = _src()
        return (
            FAST_READ_S == 8.0
            and CONTRACT == (
                "tree_id", "issued_epoch", "kinds", "cursor",
                "audio_owner", "voice_client_timeout_s",
            )
            and rec1["audio_owner"] == "desktop"
            and rec1["folded"] is True
            and rec1["cursor_advanced"] is True
            and rec1["cursor"]
            and rec1["cursor"] != rec1["cursor_prev"]
            and rec1["handoff_granted"] is True
            and rec1["handoff_replayed"] is False
            and rec1["grant_count"] == 1
            and rec1["quoted_from"] == "GET /api/v1/cvm/pull"
            and rec1["quoted_audio_owner"] == "phone"
            and rec1["live_value"]["audio_owner"] == "desktop"
            and rec1["live_value"]["cursor"] == rec1["cursor"]
            and lose_kind == RefusalKind.OWNER_CONTESTED
            and rec2["audio_owner"] == "desktop"
            and rec2["handoff_replayed"] is True
            and rec2["handoff_granted"] is False
            and rec2["grant_count"] == 1
            and rec2["cursor"] == rec1["cursor"]
            and client.handoff.owner == "desktop"
            and client.handoff.granted == ["r-desk"]
            and owners == {"desktop"}
            and published["audio_owner"] == "desktop"
            and stored["audio_owner"] == "desktop"
            and turn["cursor"] == rec1["cursor"]
            and not audio_json.exists()
            and dead_kind == RefusalKind.UNREACHABLE
            and bad_kind == RefusalKind.BAD_CORE
            and callable(core_get) and callable(refuse_http)
            and CLIENT_ID == "cvm-dt"
            and BTS_IMPORT.search(src) is None
            and "def pause_flag" not in src
            and "def write_heartbeat" not in src
            and "V:\\" not in src
            and client.tick.__func__ is CvmDtClient.tick
        )
    finally:
        httpd.shutdown()
        bad.shutdown()


def test_replayed_handoff_not_second_owner():
    tmp = _scratch()
    httpd = _serve(_FakeCore)
    base = "http://127.0.0.1:%d" % httpd.server_address[1]
    try:
        paths = CosmosPaths(tmp)
        _seed_phone(paths)
        client = CvmDtClient(
            CoreClient(base, "test-token"), paths,
            handoff_request_id="r-desk")
        rec1 = client.cycle_once()
        rec2 = client.cycle_once()
        replay = client.handoff.claim("desktop", "r-desk")
        owners = {rec1["audio_owner"], rec2["audio_owner"],
                  client.handoff.owner, replay["audio_owner"]}
        return (
            rec1["handoff_granted"] is True
            and rec1["grant_count"] == 1
            and rec2["handoff_replayed"] is True
            and rec2["handoff_granted"] is False
            and rec2["grant_count"] == 1
            and replay["replayed"] is True
            and replay["granted"] is False
            and replay["grant_count"] == 1
            and client.handoff.granted == ["r-desk"]
            and owners == {"desktop"}
        )
    finally:
        httpd.shutdown()


def test_hold_pause_does_not_pull_core():
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
        client = CvmDtClient(
            CoreClient(base, "test-token"), paths,
            handoff_request_id="r-hold")
        rec = client.tick(polls=1)
        hb = json.loads(paths.logs(clk.HEARTBEAT_NAME).read_text(
            encoding="utf-8"))
        pull = paths.state("cvm", "pull.json")
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
            and clk.is_paused(paused) is True
            and flag.exists()
        )
    finally:
        httpd.shutdown()


def test_dead_core_unreachable_still_heartbeats():
    tmp = _scratch()
    paths = CosmosPaths(tmp)
    client = CvmDtClient(
        CoreClient("http://127.0.0.1:1", "test-token"),
        paths, handoff_request_id="r-dead")
    rec = client.tick(polls=1, drain=True)
    hb = json.loads(Path(rec["heartbeat_path"]).read_text(encoding="utf-8"))
    return (
        rec["ok"] is False
        and rec["kind"] == str(RefusalKind.UNREACHABLE)
        and rec["tick"] == "error"
        and hb["last_run_epoch"] == rec["last_run_epoch"]
        and hb["clock_id"] == clk.CLOCK_ID
        and rec["last_run_epoch"]
    )


def main() -> int:
    check("pull→fold→handoff: single desktop owner, advanced cursor, "
          "replayed handoff is not a second owner",
          test_pull_fold_handoff_single_desktop_owner)
    check("replayed handoff is ignored (not a second owner)",
          test_replayed_handoff_not_second_owner)
    check("HOLD pause does not pull Core",
          test_hold_pause_does_not_pull_core)
    check("dead Core is UNREACHABLE yet the client still heartbeats",
          test_dead_core_unreachable_still_heartbeats)
    ok = all(p for _, p, _ in RESULTS)
    for label, passed, err in RESULTS:
        print(("PASS" if passed else "FAIL") + "  " + label
              + (("  " + err) if err else ""))
    print("result: " + ("ok" if ok else "FAIL")
          + "  %d/%d" % (sum(1 for _, p, _ in RESULTS if p), len(RESULTS)))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
