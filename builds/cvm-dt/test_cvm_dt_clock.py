#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Loopback tests for the CVM DT native own-clock.

No live :8770. rc=0 here is a green log. Stage-6 quotes
live/logs/cvm_dt_clock_heartbeat.json last_run_epoch advancing across
two native ticks AND state/cvm/pull.json cursor advancing under the
clock with no human turn and no Claude process.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from threading import Thread

sys.path.insert(0, str(Path(__file__).resolve().parent))
_COSMOS = Path(__file__).resolve().parents[2] / "cosmos"
if _COSMOS.is_dir() and str(_COSMOS) not in sys.path:
    sys.path.insert(0, str(_COSMOS))

from cosmos_own_clocks import CLOCKS  # noqa: E402
from cosmos_paths import CosmosPaths, write_sentinel  # noqa: E402

from cosmos_kernel import Kernel, install  # noqa: E402
from cosmos_service import Service  # noqa: E402
from cosmos_clock import acquire_lock, atomic_json, write_heartbeat  # noqa: E402
from cosmos_cvm_push import (  # noqa: E402
    DRAIN_KEYS, PULL_CLOCK_ID, PUSH_PATH, stamp_desktop_pull,
)
import cosmos_cvm_clock as sat  # noqa: E402

from cvm_dt import (  # noqa: E402
    CLIENT_ID, CoreClient, FAST_READ_S, RefusalKind, pull_url,
    core_get, core_post,
)
from cvm_snap import snapshot_delta  # noqa: E402

import cvm_dt_clock as clk  # noqa: E402

TREE_ID = "KMesh-COSMOS-live"
RESULTS = []
TAKEN = {int(c["id"]) for c in CLOCKS if c.get("id") is not None}


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
            and rec1["clock_id"] == clk.CLOCK_ID == PULL_CLOCK_ID == 18
            and clk.CLOCK_ID not in TAKEN
            and 16 in TAKEN and 17 in TAKEN
            and sat.CLOCK_ID == 16
            and e2 > e1
            and hb["last_run_epoch"] == e2
            and hb["worker"] == clk.WORKER
            and hb["clock_id"] == clk.CLOCK_ID
            and "last_run" in hb and "last_run_utc" in hb
            and hb["pid"] == os.getpid()
            and pull["audio_owner"] == "desktop"
            and pull.get("clock_id") == PULL_CLOCK_ID == 18
            and isinstance(pull.get("pull_ms"), (int, float))
            and pull["cursor"] == rec1["cursor"]
            and turn["cursor"] == rec1["cursor"]
            and rec1["live_value"]["cursor"] == rec1["cursor"]
            and callable(stamp_desktop_pull)
            and not hasattr(clk, "REUSED")
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
            and hb["last_run_epoch"] == rec["last_run_epoch"]
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


def test_skip_alive_and_once_lock():
    tmp = _scratch()
    paths = CosmosPaths(tmp)
    hb = paths.logs(clk.HEARTBEAT_NAME)
    write_heartbeat(hb, clk.WORKER, extra={"clock_id": clk.CLOCK_ID})
    mine = clk.skip_alive(paths)
    write_heartbeat(hb, clk.WORKER, extra={"clock_id": 16})
    foreign = clk.skip_alive(paths)
    write_heartbeat(hb, clk.WORKER, extra={"clock_id": clk.CLOCK_ID})
    fd = acquire_lock(paths.logs(clk.LOCK_NAME))
    try:
        rc = clk.main(["--root", str(tmp), "--once",
                       "--base", "http://127.0.0.1:1"])
    finally:
        if fd is not None:
            os.close(fd)
    return (
        mine is not None
        and mine.get("clock_id") == clk.CLOCK_ID
        and mine.get("pid") == os.getpid()
        and foreign is None
        and fd is not None and rc == 0
        and not paths.state("cvm", "pull.json").exists()
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
        and rec.get("task_name") == clk.TASK_NAME
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
        and rec["tick"] == "refused"
        and rec["state"] == "REFUSED"
        and hb["last_run_epoch"] == rec["last_run_epoch"]
        and hb["clock_id"] == clk.CLOCK_ID
        and hb.get("kind") == str(RefusalKind.UNREACHABLE)
    )


def _typed(rec, kind):
    hb = json.loads(Path(rec["heartbeat_path"]).read_text(encoding="utf-8"))
    return (rec["ok"] is False and rec["kind"] == str(kind)
            and rec["state"] == "REFUSED" and rec["tick"] == "refused"
            and hb["last_run_epoch"] == rec["last_run_epoch"]
            and hb.get("kind") == str(kind))


def test_push_then_clock_pulls_phone_turn():
    """True loop: POST /cvm/push → CLOCK_ID 18 poll_once → GET /cvm/pull.

    The value only this loop emits: the pushed cursor in the desktop-owned
    pull view, advanced vs the pre-push ticket, folded locally by the clock.
    """
    td = Path(tempfile.mkdtemp(prefix="cvm-dt-clock-loop-"))
    install(td, tree_id=TREE_ID)
    k = Kernel(td, worker="cvm-pull-loop")
    k.paths.config("api_token.txt").write_text("loop-token\n", encoding="utf-8")
    svc = Service(k, host="127.0.0.1", port=0)
    svc.serve_background()
    live = {}
    try:
        base = "http://127.0.0.1:%d" % svc.port
        core = CoreClient(base, "loop-token")
        before = core_get(core, pull_url(CLIENT_ID), FAST_READ_S)
        body = snapshot_delta("phone-loop-1", "", {
            "device": {"status": "ok", "audio_route": "none",
                       "surface": "capture+playback"},
        }, client_id="cvm-phone")
        body["audio_owner"] = "phone"
        pushed = core_post(core, PUSH_PATH, body, FAST_READ_S)
        rec = clk.poll_once(str(td), polls=1, base=base, drain=True)
        pulled = core_get(core, pull_url(CLIENT_ID), FAST_READ_S)
        ticket = json.loads(
            k.paths.state("cvm", "pull.json").read_text(encoding="utf-8"))
        live.update({
            "audio_owner": pulled.get("audio_owner"),
            "cursor": pulled.get("cursor"),
            "push_cursor_out": pushed.get("cursor_out"),
            "clock_cursor": rec.get("cursor"),
            "clock_cursor_advanced": rec.get("cursor_advanced"),
            "clock_audio_owner": rec.get("audio_owner"),
            "clock_folded": (rec.get("cycle") or {}).get("folded"),
            "clock_id": rec.get("clock_id"),
            "pull_ticket_owner": ticket.get("audio_owner"),
            "pull_ticket_cursor": ticket.get("cursor"),
            "pull_before": before.get("pull"),
            "quoted_from": "GET /api/v1/cvm/pull",
            "tick_ms": rec.get("tick_ms"),
            "cadence_mode": rec.get("cadence_mode"),
            "skipped_http": rec.get("skipped_http"),
            "first_word_ms": rec.get("first_word_ms"),
            "stt_kind": rec.get("stt_kind"),
        })
        ok = (
            rec.get("ok") is True
            and rec.get("tick") == "pulled"
            and rec.get("audio_owner") == "desktop"
            and rec.get("cursor_advanced") is True
            and rec.get("clock_id") == clk.CLOCK_ID == PULL_CLOCK_ID == 18
            and ticket.get("clock_id") == PULL_CLOCK_ID
            and (rec.get("cycle") or {}).get("folded") is True
            and pushed.get("audio_owner") == "desktop"
            and pushed.get("claimed") is False
            and pushed.get("cursor_out")
            and pulled.get("pull") is True
            and pulled.get("audio_owner") == "desktop"
            and pulled.get("cursor") == pushed.get("cursor_out")
            and pulled.get("cursor") == rec.get("cursor")
            and pulled.get("cursor") != (before.get("cursor") or "")
            and ticket.get("audio_owner") == "desktop"
            and ticket.get("cursor") == rec.get("cursor")
            and before.get("pull") is False
            and isinstance(rec.get("tick_ms"), (int, float))
            and rec.get("tick_ms") >= 0
            and rec.get("skipped_http") is False
        )
        return ok, live
    finally:
        svc.shutdown()


def test_unread_pause_and_internal_failure_are_typed_refusals():
    tmp = _scratch()
    flag = CosmosPaths(tmp).state("control", "PAUSE.flag")
    flag.parent.mkdir(parents=True, exist_ok=True)
    flag.write_text("{}", encoding="utf-8")
    orig = Path.read_text

    def _boom(self, *a, **k):
        if self.name == "PAUSE.flag":
            raise OSError("permission denied")
        return orig(self, *a, **k)

    Path.read_text = _boom                                            # type: ignore[method-assign]
    try:
        unread = clk.poll_once(str(tmp), polls=1, base="http://127.0.0.1:1")
    finally:
        Path.read_text = orig                                         # type: ignore[method-assign]
    unread_ok = (_typed(unread, RefusalKind.CONTROL_BLOCKED)
                 and unread["pause_present"] is True)

    class _BoomClient:
        def cycle_once(self):
            raise RuntimeError("injected-internal")

    boom = clk.poll_once(str(tmp), polls=2, base="http://127.0.0.1:1",
                         client=_BoomClient(), drain=True)
    return (
        unread_ok
        and _typed(boom, RefusalKind.BAD_CORE)
        and "injected-internal" in boom["detail"]
    )


def test_id16_tick_preserves_drain_metrics():
    """Drain writes pull_ms/fold_ms/backlog/drain_lag_ms/last_push_epoch;
    a DUE id16 tick must MERGE cadence and leave those keys intact.
    """
    td = Path(tempfile.mkdtemp(prefix="cvm-id16-survive-"))
    install(td, tree_id=TREE_ID)
    k = Kernel(td, worker="cvm-id16-survive")
    k.paths.config("api_token.txt").write_text("survive-token\n", encoding="utf-8")
    svc = Service(k, host="127.0.0.1", port=0)
    svc.serve_background()
    try:
        base = "http://127.0.0.1:%d" % svc.port
        core = CoreClient(base, "survive-token")
        body = snapshot_delta("phone-survive-1", "", {
            "device": {"status": "ok", "audio_route": "none",
                       "surface": "capture+playback"},
        }, client_id="cvm-phone")
        body["audio_owner"] = "phone"
        pushed = core_post(core, PUSH_PATH, body, FAST_READ_S)
        rec = clk.poll_once(str(td), polls=1, base=base, drain=True)
        after_drain = json.loads(
            k.paths.state("cvm", "pull.json").read_text(encoding="utf-8"))
        after_drain["issued_epoch"] = time.time() - (sat.PULL_INTERVAL_S + 1.0)
        atomic_json(k.paths.state("cvm", "pull.json"), after_drain)
        sat.poll_once(str(td), polls=1)
        after_id16 = json.loads(
            k.paths.state("cvm", "pull.json").read_text(encoding="utf-8"))
        hb_p = k.paths.logs(clk.HEARTBEAT_NAME)
        hb = json.loads(hb_p.read_text(encoding="utf-8")) if hb_p.is_file() else {}
        survived = all(after_id16.get(k) == after_drain.get(k) for k in DRAIN_KEYS)
        return (
            rec.get("ok") is True
            and rec.get("tick") == "pulled"
            and rec.get("clock_id") == PULL_CLOCK_ID == 18
            and pushed.get("cursor_out")
            and after_drain.get("audio_owner") == "desktop"
            and after_drain.get("backlog") == 0
            and after_drain.get("last_push_epoch")
            and after_drain.get("last_pull_epoch")
            and after_drain.get("pull_ms") is not None
            and after_drain.get("clock_id") == PULL_CLOCK_ID
            and survived
            and after_id16.get("pull_ms") == after_drain.get("pull_ms")
            and after_id16.get("fold_ms") == after_drain.get("fold_ms")
            and after_id16.get("backlog") == after_drain.get("backlog")
            and after_id16.get("drain_lag_ms") == after_drain.get("drain_lag_ms")
            and after_id16.get("last_push_epoch") == after_drain.get("last_push_epoch")
            and after_id16.get("last_pull_epoch") == after_drain.get("last_pull_epoch")
            and after_id16.get("clock_id") == PULL_CLOCK_ID == 18
            and after_id16.get("audio_owner") == "desktop"
            and after_id16.get("cursor") == after_drain.get("cursor")
            and after_id16.get("writer", "").startswith("cvm-dt")
            and hb.get("clock_id") == clk.CLOCK_ID == 18
            and sat.CLOCK_ID == 16
        )
    finally:
        svc.shutdown()


def test_id16_speech_bursts_pcm_ticket():
    """Speech-live phone.json forces a due id16 rewrite with pcm wanted.

    tick_ms is a value only this poll_once tick emits.
    """
    tmp = _scratch()
    paths = CosmosPaths(tmp)
    cvm = paths.state("cvm")
    cvm.mkdir(parents=True, exist_ok=True)
    atomic_json(paths.state("health", "board.json"), {
        "measured_epoch": time.time(),
        "rows": {"serve_8770": {"ok": True}},
    })
    atomic_json(cvm / "pull.json", {
        "cvm": 1, "tree_id": TREE_ID, "pull": True,
        "kinds": ["device"], "cursor": "c0", "audio_owner": "desktop",
        "voice_client_timeout_s": 70.0, "issued_epoch": time.time(),
        "writer": "cvm-dt-pull", "clock_id": PULL_CLOCK_ID,
        "ticket_seq": 3, "pull_ms": 7.5, "backlog": 0,
    })
    sha = "b" * 64
    atomic_json(cvm / "phone.json", {
        "cvm": 1, "tree_id": TREE_ID, "cursor": "c0",
        "kinds": {"pcm": {"status": "ok", "sha256": sha,
                          "n_bytes": 16, "rate": 16000, "ch": 1},
                  "voice_session": {"status": "ok", "queue_depth": 1,
                                    "last_turn_epoch": time.time()}},
    })
    rec = sat.poll_once(str(tmp), polls=1)
    ticket = json.loads((cvm / "pull.json").read_text(encoding="utf-8"))
    return (
        rec.get("speech_live") is True
        and rec.get("pcm_wanted") is True
        and rec.get("cadence_mode") == "burst"
        and rec.get("pcm_sha256") == sha
        and "pcm" in (ticket.get("kinds") or [])
        and ticket.get("pcm_wanted") is True
        and ticket.get("clock_id") == PULL_CLOCK_ID == 18
        and ticket.get("pull_ms") == 7.5
        and ticket.get("writer", "").startswith("cvm-dt")
        and isinstance(rec.get("tick_ms"), (int, float))
        and rec.get("tick_ms") >= 0
        and rec.get("core_ready") is True
    )


def main() -> int:
    check("tick writes last_run_epoch; fold cursor + desktop claim land",
          test_tick_heartbeat_and_cursor)
    check("HOLD pause heartbeats without pulling Core",
          test_pause_hold_heartbeats_without_pull)
    check("RESUME-GATE idles and does not self-clear",
          test_resume_gate_idles_until_cleared)
    check("skip_alive unique clock_id; --once no-ops under lock",
          test_skip_alive_and_once_lock)
    check("register emits schtasks /Create and does not run it",
          test_register_emits_does_not_run)
    check("dead Core is UNREACHABLE and still heartbeats",
          test_dead_core_refuses_and_heartbeats)
    check("unread PAUSE.flag + internal failure are typed refusals",
          test_unread_pause_and_internal_failure_are_typed_refusals)
    check("id16 due tick MERGES and does not clobber drain metrics "
          "(pull_ms/fold_ms/backlog/drain_lag_ms/last_push_epoch survive)",
          test_id16_tick_preserves_drain_metrics)
    check("id16 speech-live burst rewrites ticket with pcm; tick_ms emitted",
          test_id16_speech_bursts_pcm_ticket)

    live = None
    loop_err = ""

    def _loop_probe():
        nonlocal live, loop_err
        try:
            ok, live = test_push_then_clock_pulls_phone_turn()
            return ok
        except Exception as e:                                        # noqa: BLE001
            loop_err = "%s: %s" % (type(e).__name__, e)
            raise

    check("POST /cvm/push then CLOCK_ID 18 poll_once: pushed phone turn "
          "in desktop-owned GET /cvm/pull with the advanced cursor",
          _loop_probe)
    if loop_err and not any(p for l, p, _ in RESULTS if "POST /cvm/push then" in l):
        RESULTS[-1] = (RESULTS[-1][0], False, loop_err)

    ok = all(p for _, p, _ in RESULTS)
    for label, passed, err in RESULTS:
        print(("PASS" if passed else "FAIL") + "  " + label
              + (("  " + err) if err else ""))
    if live:
        print("live_value: " + json.dumps(live, sort_keys=True))
    print("result: " + ("ok" if ok else "FAIL")
          + "  %d/%d" % (sum(1 for _, p, _ in RESULTS if p), len(RESULTS)))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
