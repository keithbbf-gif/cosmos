#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Loopback tests for the CVM DT native own-clock.

No live :8770. rc=0 here is a green log. Stage-6 quotes
live/logs/cvm_dt_clock_heartbeat.json last_run_epoch advancing across
two native ticks AND state/cvm/pull.json cursor advancing under the
clock with no human turn and no Claude process.

Software proof this slice (named): heartbeat is emitted with a fresh
epoch and CLOCK_ID is a single value that does not collide with CLOCKS
15/16/17.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from threading import Thread

HERE = Path(__file__).resolve().parent
if (HERE / "cvm_dt.py").is_file():
    sys.path.insert(0, str(HERE))
    _COSMOS = HERE.parents[1] / "cosmos"
    if _COSMOS.is_dir():
        sys.path.insert(0, str(_COSMOS))
    CLOCK_SRC = HERE / "cvm_dt_clock.py"
else:
    BUNDLE = HERE.parent if HERE.name == "tests" else HERE.parents[1]
    REPO = BUNDLE.parent.parent
    LIVE_DT = REPO / "builds" / "cvm-dt"
    COSMOS_DIR = REPO / "cosmos"
    BUNDLE_DT = BUNDLE / "builds" / "cvm-dt"
    for p in (LIVE_DT, COSMOS_DIR, BUNDLE_DT):
        if p.is_dir():
            sys.path.insert(0, str(p))
    CLOCK_SRC = BUNDLE_DT / "cvm_dt_clock.py"

from cosmos_clock import write_heartbeat  # noqa: E402
from cosmos_own_clocks import CLOCKS  # noqa: E402
from cosmos_paths import CosmosPaths, write_sentinel  # noqa: E402

from cvm_dt import (  # noqa: E402
    CLIENT_ID, CoreClient, RefusalKind, pull_url,
)
from cvm_snap import snapshot_delta  # noqa: E402

import cvm_dt_clock as clk  # noqa: E402

TREE_ID = "KMesh-COSMOS-live"
RESULTS = []
BTS_IMPORT = re.compile(r"^\s*(?:from|import)\s+bts_\w+", re.M)
CLOCK_ASSIGN = re.compile(r"^CLOCK_ID\s*=\s*(.+)$", re.M)
DRIVE_LIT = re.compile(r"V:\\A\\")


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:                                            # noqa: BLE001
        RESULTS.append((label, False, "%s: %s" % (type(e).__name__, e)))


class _FakeCore(BaseHTTPRequestHandler):
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
            return self._send(404, {"error": "NOT_FOUND"})
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
            "clock_id": 16,
        })


class _BoomCore(BaseHTTPRequestHandler):
    """Must not be hit on a PAUSED tick."""

    def log_message(self, *args):                                     # noqa: ARG002
        return

    def do_GET(self):                                                 # noqa: N802
        raise AssertionError("paused tick must not GET Core")


def _serve(handler):
    httpd = HTTPServer(("127.0.0.1", 0), handler)
    t = Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    return httpd


def _scratch():
    tmp = Path(tempfile.mkdtemp(prefix="cvm-dt-clock-test-"))
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
    }, client_id="cvm-dt-clock-test")), encoding="utf-8")


def _src() -> str:
    return CLOCK_SRC.read_text(encoding="utf-8")


def test_heartbeat_emitted_fresh_epoch_clock_id_single_valued():
    """Named software proof: heartbeat lands, epoch is fresh, CLOCK_ID is one."""
    tmp = _scratch()
    before = time.time()
    rec = clk.poll_once(str(tmp), polls=1, base="http://127.0.0.1:1",
                        drain=True)
    after = time.time()
    paths = CosmosPaths(tmp)
    hb_p = paths.logs(clk.HEARTBEAT_NAME)
    hb = json.loads(hb_p.read_text(encoding="utf-8"))
    src = _src()
    assigns = CLOCK_ASSIGN.findall(src)
    taken = {int(c["id"]) for c in CLOCKS if c.get("id") is not None}
    epoch = int(hb["last_run_epoch"])
    return (
        hb_p.is_file()
        and hb_p.name == "cvm_dt_clock_heartbeat.json"
        and hb["worker"] == clk.WORKER == "cvm-dt-clock"
        and hb["clock_id"] == rec["clock_id"] == clk.CLOCK_ID
        and clk.CLOCK_ID == 18
        and len(assigns) == 1
        and assigns[0].strip() == "18"
        and clk.CLOCK_ID not in taken
        and 16 in taken
        and 17 in taken
        and clk.CLOCK_ID != 16
        and clk.CLOCK_ID != 17
        and rec["ok"] is False
        and rec["kind"] == str(RefusalKind.UNREACHABLE)
        and hb.get("core_kind") == "UNREACHABLE"
        and hb.get("core_ready") is False
        and hb.get("state") == "REFUSED"
        and rec["last_run_epoch"] == epoch
        and before - 1 <= epoch <= after + 1
        and "last_run" in hb and "last_run_utc" in hb
        and hb["pid"] == os.getpid()
        and hb.get("polls") == 1
        and "REUSED" not in src
        and BTS_IMPORT.search(src) is None
        and DRIVE_LIT.search(src) is None
        and "from bts_" not in src
        and "import bts_" not in src
    )


def test_tick_heartbeat_and_cursor():
    tmp = _scratch()
    httpd = _serve(_FakeCore)
    base = "http://127.0.0.1:%d" % httpd.server_address[1]
    try:
        paths = CosmosPaths(tmp)
        _seed_phone(paths)
        client = clk.CvmDtClient(
            CoreClient(base, "test-token"), paths,
            handoff_request_id="r-clock")
        rec1 = clk.poll_once(str(tmp), polls=1, base=base, client=client)
        time.sleep(1.1)
        rec2 = clk.poll_once(str(tmp), polls=2, base=base, client=client)
        hb_p = paths.logs(clk.HEARTBEAT_NAME)
        hb = json.loads(hb_p.read_text(encoding="utf-8"))
        pull = json.loads(paths.state("cvm", "pull.json").read_text(
            encoding="utf-8"))
        turn = json.loads(paths.state("cvm", "dt_turn.json").read_text(
            encoding="utf-8"))
        e1 = int(rec1["last_run_epoch"])
        e2 = int(rec2["last_run_epoch"])
        return (
            rec1["ok"] is True
            and rec2["ok"] is True
            and rec1["tick"] == "pulled"
            and rec1["audio_owner"] == "desktop"
            and rec1["cursor_advanced"] is True
            and rec1["cursor"]
            and rec1["cursor"] != rec1.get("cursor_prev")
            and rec1["quoted_from"] == pull_url(CLIENT_ID)
            and rec1["clock_id"] == clk.CLOCK_ID
            and e2 > e1
            and hb["last_run_epoch"] == e2
            and hb["worker"] == clk.WORKER
            and hb["clock_id"] == clk.CLOCK_ID == 18
            and "last_run" in hb and "last_run_utc" in hb
            and hb["pid"] == os.getpid()
            and pull["audio_owner"] == "desktop"
            and pull.get("clock_id") == 16
            and turn["cursor"] == rec1["cursor"]
            and rec1["live_value"]["cursor"] == rec1["cursor"]
        )
    finally:
        httpd.shutdown()


def test_pause_hold_heartbeats_without_pull():
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
        rec = clk.poll_once(str(tmp), polls=1, base=base)
        hb = json.loads(paths.logs(clk.HEARTBEAT_NAME).read_text(
            encoding="utf-8"))
        pull = paths.state("cvm", "pull.json")
        return (
            rec["ok"] is True
            and rec["tick"] == "paused"
            and rec["state"] == "PAUSED"
            and rec["pause_present"] is True
            and rec["pause_mode"] == "hold"
            and hb["state"] == "PAUSED"
            and hb["clock_id"] == clk.CLOCK_ID
            and hb["last_run_epoch"] == rec["last_run_epoch"]
            and hb.get("core_kind") is None
            and not pull.exists()
        )
    finally:
        httpd.shutdown()


def test_resume_gate_idles_until_cleared():
    tmp = _scratch()
    paths = CosmosPaths(tmp)
    flag = paths.state("control", "PAUSE.flag")
    flag.parent.mkdir(parents=True, exist_ok=True)
    flag.write_text(json.dumps({
        "state": "PAUSED", "mode": "resume_gate",
        "auto_resume_at": "2099-01-01T00:00:00-05:00",
        "reason": "test-gate",
    }), encoding="utf-8")
    paused = clk.pause_flag(paths)
    rec = clk.poll_once(str(tmp), polls=1, base="http://127.0.0.1:1")
    still = flag.exists()
    return (
        clk.is_paused(paused) is True
        and paused.get("mode") == "resume_gate"
        and rec["tick"] == "paused"
        and rec["pause_mode"] == "resume_gate"
        and rec["auto_resume_at"]
        and still
    )


def test_skip_alive_same_clock_id():
    tmp = _scratch()
    paths = CosmosPaths(tmp)
    hb = paths.logs(clk.HEARTBEAT_NAME)
    write_heartbeat(hb, clk.WORKER, extra={"clock_id": clk.CLOCK_ID})
    mine = clk.skip_alive(paths)
    write_heartbeat(hb, clk.WORKER, extra={"clock_id": 16})
    foreign = clk.skip_alive(paths)
    return (
        mine is not None
        and mine.get("clock_id") == clk.CLOCK_ID
        and mine.get("pid") == os.getpid()
        and foreign is None
    )


def test_register_emits_does_not_run():
    tmp = _scratch()
    ran = []

    def _boom(*a, **k):                                               # noqa: ARG001
        ran.append(a)
        raise AssertionError("register must not run schtasks")

    orig = subprocess.run
    subprocess.run = _boom                                            # type: ignore[assignment]
    try:
        rec = clk.register(str(tmp))
    finally:
        subprocess.run = orig                                         # type: ignore[assignment]
    cmds = rec.get("keith_cmds") or []
    blob = " ".join(cmds).lower()
    return (
        rec.get("ok") is True
        and rec.get("ran") is False
        and rec.get("clock_id") == clk.CLOCK_ID == 18
        and len(cmds) == 2
        and "schtasks" in blob
        and "/create" in blob
        and clk.TASK_NAME.lower() in blob
        and "--loop" in blob
        and "pythonw" in rec.get("tr", "").lower()
        and not ran
        and RefusalKind.UNREACHABLE
    )


def test_dead_core_refuses_and_heartbeats():
    tmp = _scratch()
    rec = clk.poll_once(str(tmp), polls=1, base="http://127.0.0.1:1",
                        drain=True)
    hb = json.loads(Path(rec["heartbeat_path"]).read_text(encoding="utf-8"))
    return (
        rec["ok"] is False
        and rec["kind"] == str(RefusalKind.UNREACHABLE)
        and rec["tick"] == "error"
        and rec["core_kind"] == "UNREACHABLE"
        and hb["last_run_epoch"] == rec["last_run_epoch"]
        and hb["clock_id"] == clk.CLOCK_ID
        and hb["worker"] == clk.WORKER
        and hb.get("core_kind") == "UNREACHABLE"
        and hb.get("state") == "REFUSED"
    )


def test_unread_pause_is_control_blocked_yet_heartbeats():
    tmp = _scratch()
    paths = CosmosPaths(tmp)
    flag = paths.state("control", "PAUSE.flag")
    flag.parent.mkdir(parents=True, exist_ok=True)
    flag.write_text("{}", encoding="utf-8")
    orig = Path.read_text

    def _boom(self, *a, **k):
        if self.name == "PAUSE.flag":
            raise OSError("permission denied")
        return orig(self, *a, **k)

    Path.read_text = _boom                                            # type: ignore[method-assign]
    try:
        rec = clk.poll_once(str(tmp), polls=1, base="http://127.0.0.1:1")
    finally:
        Path.read_text = orig                                         # type: ignore[method-assign]
    hb = json.loads(paths.logs(clk.HEARTBEAT_NAME).read_text(encoding="utf-8"))
    return (
        rec["ok"] is False
        and rec["kind"] == str(RefusalKind.CONTROL_BLOCKED)
        and rec["state"] == "REFUSED"
        and rec["tick"] == "error"
        and rec["pause_present"] is True
        and hb["last_run_epoch"] == rec["last_run_epoch"]
        and hb["clock_id"] == clk.CLOCK_ID
        and hb.get("kind") == str(RefusalKind.CONTROL_BLOCKED)
    )


def main() -> int:
    check("heartbeat emitted with fresh epoch; CLOCK_ID is single-valued 18",
          test_heartbeat_emitted_fresh_epoch_clock_id_single_valued)
    check("tick writes last_run_epoch; fold cursor + desktop claim land",
          test_tick_heartbeat_and_cursor)
    check("HOLD pause heartbeats without pulling Core",
          test_pause_hold_heartbeats_without_pull)
    check("RESUME-GATE idles and does not self-clear",
          test_resume_gate_idles_until_cleared)
    check("skip_alive matches unique clock_id + live pid",
          test_skip_alive_same_clock_id)
    check("register emits schtasks /Create and does not run it",
          test_register_emits_does_not_run)
    check("dead Core is UNREACHABLE and still heartbeats",
          test_dead_core_refuses_and_heartbeats)
    check("unread PAUSE.flag is CONTROL_BLOCKED yet heartbeats",
          test_unread_pause_is_control_blocked_yet_heartbeats)
    ok = all(p for _, p, _ in RESULTS)
    for label, passed, err in RESULTS:
        print(("PASS" if passed else "FAIL") + "  " + label
              + (("  " + err) if err else ""))
    print("result: " + ("ok" if ok else "FAIL")
          + "  %d/%d" % (sum(1 for _, p, _ in RESULTS if p), len(RESULTS)))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
