#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Desktop pull-clock: claim desktop, drain phone turns, emit pull_ms/backlog.

Fake Core + in-process Service (no live :8770 required). rc=0 here is a
green log. Stage-6 quotes live_value.audio_owner + cursor + pull_ms from
a true POST /cvm/push → GET /cvm/pull drain cycle.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import tempfile
import threading
import time
import types
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

# Same hop as test_cvm_dt.py (this file lives beside cvm_pull.py / cvm_dt.py).
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "cosmos"))

from cosmos_paths import CosmosPaths, write_sentinel  # noqa: E402
from cosmos_kernel import Kernel, install  # noqa: E402
from cosmos_service import Service  # noqa: E402
from cosmos_cvm_push import (  # noqa: E402
    PULL_CLOCK_ID, PUSH_PATH, cadence_wait, probe_stt,
)

from cvm_dt import (  # noqa: E402
    CLIENT_ID, CoreClient, FAST_READ_S, CvmDtError, RefusalKind,
    core_get, core_post, pull_url,
)

from cvm_pull import (  # noqa: E402
    CONTRACT, DRAIN_IDLE_S, HEAVY_LOCAL_PULL_S, IDLE_BACKOFF_S,
    PULL_INTERVAL_S, SPEECH_BURST_S, DesktopPullClock, cadence_next_s,
)
from cvm_snap import SnapshotConsumer, snapshot_delta  # noqa: E402


TREE_ID = "KMesh-COSMOS-live"
RESULTS = []


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:                                            # noqa: BLE001
        RESULTS.append((label, False, "%s: %s" % (type(e).__name__, e)))


class _FakePull(BaseHTTPRequestHandler):
    """HTTP double of GET /api/v1/cvm/pull. Cursor advances on every GET."""

    token = "test-token"
    n = 0
    tree_id = TREE_ID

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
        _FakePull.n += 1
        cursor = "c0" if _FakePull.n == 1 else "c1"
        return self._send(200, {
            "cvm": 1,
            "tree_id": self.tree_id,
            "issued_epoch": 1787800000.0 + _FakePull.n,
            "pull": True,
            "kinds": ["voice_session", "device", "notifications"],
            "cursor": cursor,
            "audio_owner": "phone",
            "voice_client_timeout_s": 70.0,
            "core_kind": "ok",
            "client_id": CLIENT_ID,
        })


def _serve():
    _FakePull.n = 0
    httpd = HTTPServer(("127.0.0.1", 0), _FakePull)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    return httpd


def _scratch():
    tmp = Path(tempfile.mkdtemp(prefix="cvm-pull-test-"))
    write_sentinel(tmp, TREE_ID)
    (tmp / "config").mkdir()
    (tmp / "state").mkdir()
    (tmp / "config" / "api_token.txt").write_text("test-token", encoding="utf-8")
    return tmp


def test_desktop_pull_clock_claims_owner_and_advances_cursor():
    """The one test this slice ships: claim desktop + cursor moves."""
    tmp = _scratch()
    httpd = _serve()
    base = "http://127.0.0.1:%d" % httpd.server_address[1]
    try:
        paths = CosmosPaths(tmp)
        clock = DesktopPullClock(CoreClient(base, "test-token"), paths)
        t1 = clock.pull_once()
        t2 = clock.pull_once()
        pull_p = paths.state("cvm", "pull.json")
        published = json.loads(pull_p.read_text(encoding="utf-8"))
        audio_json = tmp / "state" / "cvm" / "audio.json"
        return (
            HEAVY_LOCAL_PULL_S == FAST_READ_S == 8.0
            and CONTRACT == (
                "tree_id", "issued_epoch", "kinds", "cursor",
                "audio_owner", "voice_client_timeout_s",
            )
            and t1["audio_owner"] == "desktop"
            and t2["audio_owner"] == "desktop"
            and t1["cursor"] == "c0"
            and t2["cursor"] == "c1"
            and t2["cursor"] != t1["cursor"]
            and t2["cursor_advanced"] is True
            and t1["cursor_prev"] == ""
            and t2["cursor_prev"] == "c0"
            and published["audio_owner"] == "desktop"
            and published["cursor"] == "c1"
            and published["tree_id"] == TREE_ID
            and published["kinds"] == [
                "voice_session", "device", "notifications"]
            and published["voice_client_timeout_s"] == 70.0
            and not audio_json.exists()
            and t1["quoted_from"] == "GET /api/v1/cvm/pull"
            and t1["quoted_audio_owner"] == "phone"
            and isinstance(t1["pull_ms"], (int, float))
            and t1["pull_ms"] >= 0
            and t2["pull_ms"] >= 0
            and published.get("pull_ms") == t2["pull_ms"]
            and published.get("backlog") == 0
            and published.get("last_pull_epoch")
            and published.get("clock_id") == PULL_CLOCK_ID == 18
            and DRAIN_IDLE_S == 2.0
            and PULL_INTERVAL_S == 15.0
            and IDLE_BACKOFF_S == 15.0
            and SPEECH_BURST_S == 0.25
            and t1.get("skipped_http") is False
            and isinstance(t1.get("tick_ms"), (int, float)) and t1["tick_ms"] >= 0
        )
    finally:
        httpd.shutdown()


def _seed_phone(paths: CosmosPaths, rid: str = "r-drain") -> None:
    phone = paths.state("cvm", "phone.json")
    phone.parent.mkdir(parents=True, exist_ok=True)
    phone.write_text(json.dumps(snapshot_delta(rid, "", {
        "device": {"status": "ok", "battery_pct": 80,
                   "net": "tailscale", "audio_route": "none"},
    }, client_id="cvm-dt-pull-test")), encoding="utf-8")


def test_drain_folds_and_zeros_backlog():
    """GET + local fold + stamp: backlog 1→0, pull_ms on pull.json."""
    tmp = _scratch()
    httpd = _serve()
    base = "http://127.0.0.1:%d" % httpd.server_address[1]
    try:
        paths = CosmosPaths(tmp)
        _seed_phone(paths)
        snap = SnapshotConsumer(CoreClient(base, "test-token"), paths,
                                load=False, persist=True)

        def _fold(ticket):
            snap.seed_ticket(ticket)
            return snap.ingest_phone()

        clock = DesktopPullClock(CoreClient(base, "test-token"), paths,
                                 folder=_fold)
        rec = clock.drain()
        published = json.loads(
            paths.state("cvm", "pull.json").read_text(encoding="utf-8"))
        return (
            rec["ok"] is True
            and rec["audio_owner"] == "desktop"
            and rec["folded"] is True
            and rec["cursor_advanced"] is True
            and rec["backlog"] == 0
            and rec["drained"] == 1
            and rec["drain_turns"] == 1
            and rec["pull_ms"] >= 0
            and rec["fold_ms"] >= 0
            and rec["live_value"]["audio_owner"] == "desktop"
            and rec["live_value"]["cursor"] == rec["cursor"]
            and rec["live_value"]["backlog"] == 0
            and rec["live_value"]["pull_ms"] == rec["pull_ms"]
            and published["audio_owner"] == "desktop"
            and published["cursor"] == rec["cursor"]
            and published["backlog"] == 0
            and published["pull_ms"] == rec["pull_ms"]
            and published["last_pull_epoch"] == rec["last_pull_epoch"]
            and published.get("clock_id") == PULL_CLOCK_ID == 18
            and not (tmp / "state" / "cvm" / "audio.json").exists()
        )
    finally:
        httpd.shutdown()


def test_push_then_drain_emits_lag():
    """True pull cycle: POST /cvm/push → drain GET /cvm/pull.

    live_value only this loop emits: audio_owner=desktop, monotonic
    cursor, measured pull_ms, backlog 1→0, drain_lag_ms.
    """
    td = Path(tempfile.mkdtemp(prefix="cvm-pull-drain-"))
    install(td, tree_id=TREE_ID)
    k = Kernel(td, worker="cvm-pull-drain")
    k.paths.config("api_token.txt").write_text("drain-token\n", encoding="utf-8")
    svc = Service(k, host="127.0.0.1", port=0)
    svc.serve_background()
    live = {}
    try:
        base = "http://127.0.0.1:%d" % svc.port
        core = CoreClient(base, "drain-token")
        before = core_get(core, pull_url(CLIENT_ID), FAST_READ_S)
        body = snapshot_delta("phone-drain-1", "", {
            "device": {"status": "ok", "audio_route": "none",
                       "surface": "capture+playback"},
        }, client_id="cvm-phone")
        body["audio_owner"] = "phone"
        pushed = core_post(core, PUSH_PATH, body, FAST_READ_S)
        after_push = json.loads(
            k.paths.state("cvm", "pull.json").read_text(encoding="utf-8"))
        snap = SnapshotConsumer(core, k.paths, load=False, persist=True)

        def _fold(ticket):
            snap.seed_ticket(ticket)
            return snap.ingest_phone()

        clock = DesktopPullClock(core, k.paths, folder=_fold)
        rec = clock.drain()
        pulled = core_get(core, pull_url(CLIENT_ID), FAST_READ_S)
        ticket = json.loads(
            k.paths.state("cvm", "pull.json").read_text(encoding="utf-8"))
        live.update({
            "audio_owner": pulled.get("audio_owner"),
            "cursor": pulled.get("cursor"),
            "cursor_prev": rec.get("cursor_prev"),
            "push_cursor_out": pushed.get("cursor_out"),
            "quoted_from": "GET /api/v1/cvm/pull",
            "pull_ms": rec.get("pull_ms"),
            "pull_cycle_ms": rec.get("pull_cycle_ms"),
            "backlog": rec.get("backlog"),
            "quoted_backlog": rec.get("quoted_backlog"),
            "drain_lag_ms": rec.get("drain_lag_ms"),
            "last_pull_epoch": rec.get("last_pull_epoch"),
            "last_push_epoch": ticket.get("last_push_epoch"),
            "folded": rec.get("folded"),
            "tick_ms": rec.get("tick_ms"),
            "cadence_mode": rec.get("cadence_mode"),
            "skipped_http": rec.get("skipped_http"),
            "speech_live": rec.get("speech_live"),
            "stt_kind": rec.get("stt_kind"),
            "first_word_ms": rec.get("first_word_ms"),
            "clock_id": ticket.get("clock_id"),
        })
        ok = (
            before.get("pull") is False
            and pushed.get("audio_owner") == "desktop"
            and pushed.get("claimed") is False
            and pushed.get("cursor_out")
            and after_push.get("audio_owner") == "desktop"
            and after_push.get("backlog") == 1
            and after_push.get("last_push_epoch")
            and rec.get("ok") is True
            and rec.get("audio_owner") == "desktop"
            and rec.get("folded") is True
            and rec.get("cursor_advanced") is True
            and rec.get("cursor") == pushed.get("cursor_out")
            and rec.get("cursor") != (rec.get("cursor_prev") or "")
            and rec.get("backlog") == 0
            and rec.get("quoted_backlog") == 1
            and isinstance(rec.get("pull_ms"), (int, float))
            and rec.get("pull_ms") >= 0
            and rec.get("pull_cycle_ms") >= rec.get("pull_ms")
            and rec.get("drain_lag_ms") is not None
            and rec.get("drain_lag_ms") >= 0
            and rec.get("last_pull_epoch") >= after_push["last_push_epoch"]
            and pulled.get("pull") is True
            and pulled.get("audio_owner") == "desktop"
            and pulled.get("cursor") == rec.get("cursor")
            and ticket.get("audio_owner") == "desktop"
            and ticket.get("backlog") == 0
            and ticket.get("pull_ms") == rec.get("pull_ms")
            and ticket.get("drain_lag_ms") == rec.get("drain_lag_ms")
            and not k.paths.state("cvm", "audio.json").is_file()
            and isinstance(rec.get("tick_ms"), (int, float))
            and rec.get("tick_ms") >= 0
            and rec.get("skipped_http") is False
            and rec.get("cadence_mode") in ("idle", "burst")
            and rec.get("stt_kind") in ("STT_NONE", "UNREACHABLE", "ok")
            and ticket.get("clock_id") == PULL_CLOCK_ID == 18
        )
        return ok, live
    finally:
        svc.shutdown()


def test_idle_second_drain_skips_http():
    """Idle coalesce: second drain reads phone.json, does not GET Core."""
    tmp = _scratch()
    httpd = _serve()
    base = "http://127.0.0.1:%d" % httpd.server_address[1]
    try:
        paths = CosmosPaths(tmp)
        clock = DesktopPullClock(CoreClient(base, "test-token"), paths)
        r1 = clock.drain()
        n1, gets1 = _FakePull.n, clock.http_gets
        r2 = clock.drain()
        return (
            r1.get("skipped_http") is False
            and n1 == 1 and gets1 == 1
            and r2.get("skipped_http") is True
            and r2.get("cadence_mode") == "coalesced"
            and r2.get("quoted_from") == "local phone.json"
            and r2.get("cursor") == r1.get("cursor")
            and clock.http_gets == 1
            and _FakePull.n == 1
            and isinstance(r2.get("tick_ms"), (int, float))
            and r2["tick_ms"] >= 0
            and cadence_next_s(r2) == DRAIN_IDLE_S
        )
    finally:
        httpd.shutdown()


def test_speech_live_stt_interrupt_skips_get():
    """Speech-live PCM is a local STT interrupt — no extra Core GET."""
    tmp = _scratch()
    httpd = _serve()
    base = "http://127.0.0.1:%d" % httpd.server_address[1]
    try:
        paths = CosmosPaths(tmp)
        clock = DesktopPullClock(CoreClient(base, "test-token"), paths)
        r1 = clock.drain()
        n1, gets1 = _FakePull.n, clock.http_gets
        pcm = b"\x00\x10" * 1600
        sha = hashlib.sha256(pcm).hexdigest()
        cas = paths.state("cvm") / "cas"
        cas.mkdir(parents=True, exist_ok=True)
        (cas / sha).write_bytes(pcm)
        phone = paths.state("cvm", "phone.json")
        phone.parent.mkdir(parents=True, exist_ok=True)
        phone.write_text(json.dumps({
            "cvm": 1, "tree_id": TREE_ID, "cursor": r1.get("cursor") or "",
            "kinds": {"pcm": {"status": "ok", "sha256": sha,
                              "n_bytes": len(pcm), "rate": 16000, "ch": 1},
                      "voice_session": {"status": "ok", "queue_depth": 1,
                                        "last_turn_epoch": time.time()}},
        }), encoding="utf-8")
        t0 = time.perf_counter()
        stt = clock.on_speech()
        interrupt_ms = round((time.perf_counter() - t0) * 1000.0, 3)
        r2 = clock.drain()
        return (
            r1.get("skipped_http") is False
            and n1 == 1 and gets1 == 1
            and stt.get("vad_event") is True
            and stt.get("pcm_sha256") == sha
            and isinstance(stt.get("first_word_ms"), (int, float))
            and stt.get("first_word_ms") >= 0
            and stt.get("first_word_ms") < 500
            and interrupt_ms < 500
            and clock.http_gets == 1
            and _FakePull.n == 1
            and r2.get("skipped_http") is True
            and r2.get("cadence_mode") == "coalesced"
            and r2.get("vad_event") is True
            and isinstance(r2.get("first_word_ms"), (int, float))
            and cadence_next_s(r2) == DRAIN_IDLE_S
            and SPEECH_BURST_S == 0.25
        )
    finally:
        httpd.shutdown()


def test_stale_pcm_pointer_coalesces():
    """Residual cadence hole: leftover pcm sha without recency does NOT burst."""
    tmp = _scratch()
    httpd = _serve()
    base = "http://127.0.0.1:%d" % httpd.server_address[1]
    try:
        paths = CosmosPaths(tmp)
        clock = DesktopPullClock(CoreClient(base, "test-token"), paths)
        r1 = clock.drain()
        phone = paths.state("cvm", "phone.json")
        phone.parent.mkdir(parents=True, exist_ok=True)
        phone.write_text(json.dumps({
            "cvm": 1, "tree_id": TREE_ID, "cursor": r1.get("cursor") or "",
            "kinds": {"pcm": {"status": "ok", "sha256": "a" * 64,
                              "n_bytes": 16, "rate": 16000, "ch": 1}},
        }), encoding="utf-8")
        r2 = clock.drain()
        return (
            r1.get("skipped_http") is False
            and r2.get("skipped_http") is True
            and r2.get("speech_live") is False
            and r2.get("cadence_mode") == "coalesced"
            and clock.http_gets == 1
            and cadence_next_s(r2) == DRAIN_IDLE_S
        )
    finally:
        httpd.shutdown()


def test_cadence_wait_wakes_on_speech():
    """Idle 2s sleep wakes on local phone.json — measured first-word wait."""
    tmp = _scratch()
    paths = CosmosPaths(tmp)
    cvm = paths.state("cvm")
    cvm.mkdir(parents=True, exist_ok=True)
    rec = {"speech_live": False, "backlog": 0, "cadence_mode": "coalesced"}

    def _fire():
        time.sleep(0.08)
        (cvm / "phone.json").write_text(json.dumps({
            "cvm": 1, "tree_id": TREE_ID,
            "kinds": {"voice_session": {
                "status": "ok", "queue_depth": 1,
                "last_turn_epoch": time.time(),
            }},
        }), encoding="utf-8")

    t = threading.Thread(target=_fire, daemon=True)
    t0 = time.perf_counter()
    t.start()
    slept = cadence_wait(rec, default_s=DRAIN_IDLE_S, paths=paths,
                         tree_id=TREE_ID, slice_s=0.05)
    wake_ms = round((time.perf_counter() - t0) * 1000.0, 3)
    t.join(timeout=2.0)
    return (
        slept < 0.6
        and wake_ms < 600
        and wake_ms >= 50
        and slept > 0.04
    )


def _fake_vosk(text: str = "status"):
    fake = types.ModuleType("vosk")
    fake.Model = lambda path: path
    fake.SetLogLevel = lambda *_a, **_k: None

    class _Rec:
        def __init__(self, _m, rate):
            self.rate = rate

        def AcceptWaveform(self, pcm):                                  # noqa: ARG002
            return True

        def FinalResult(self):
            return json.dumps({"text": text})

    fake.KaldiRecognizer = _Rec
    return fake


def test_pcm_cas_binds_local_stt():
    """POST /cvm/push with PCM CAS → drain GET binds VOSK (heavy local).

    live_value.first_word_ms is push→transcript; skipped_http=false;
    clock_id=18. Missing model is typed STT_NONE (not a green log).
    """
    td = Path(tempfile.mkdtemp(prefix="cvm-pull-stt-"))
    install(td, tree_id=TREE_ID)
    k = Kernel(td, worker="cvm-pull-stt")
    k.paths.config("api_token.txt").write_text("stt-token\n", encoding="utf-8")
    pcm = b"\x00\x10" * 1600
    sha = hashlib.sha256(pcm).hexdigest()
    cas = k.paths.state("cvm") / "cas"
    cas.mkdir(parents=True, exist_ok=True)
    (cas / sha).write_bytes(pcm)
    model = td / "vosk-model"
    model.mkdir()
    prev, env = sys.modules.get("vosk"), os.environ.get("COSMOS_VOSK_MODEL")
    sys.modules["vosk"] = _fake_vosk("status")
    os.environ["COSMOS_VOSK_MODEL"] = str(model)
    svc = Service(k, host="127.0.0.1", port=0)
    svc.serve_background()
    live = {}
    try:
        none_probe = None
        os.environ.pop("COSMOS_VOSK_MODEL", None)
        none_probe = probe_stt()
        os.environ["COSMOS_VOSK_MODEL"] = str(model)
        base = "http://127.0.0.1:%d" % svc.port
        core = CoreClient(base, "stt-token")
        body = snapshot_delta("phone-stt-1", "", {
            "device": {"status": "ok", "audio_route": "none"},
            "pcm": {"status": "ok", "sha256": sha, "n_bytes": len(pcm),
                    "rate": 16000, "ch": 1},
            "voice_session": {"status": "ok", "queue_depth": 1,
                              "last_turn_epoch": time.time()},
        }, client_id="cvm-phone")
        pushed = core_post(core, PUSH_PATH, body, FAST_READ_S)
        snap = SnapshotConsumer(core, k.paths, load=False, persist=True)

        def _fold(ticket):
            snap.seed_ticket(ticket)
            return snap.ingest_phone()

        clock = DesktopPullClock(core, k.paths, folder=_fold)
        rec = clock.drain()
        ticket = json.loads(
            k.paths.state("cvm", "pull.json").read_text(encoding="utf-8"))
        live.update({
            "audio_owner": rec.get("audio_owner"),
            "cursor": rec.get("cursor"),
            "push_cursor_out": pushed.get("cursor_out"),
            "quoted_from": "GET /api/v1/cvm/pull",
            "tick_ms": rec.get("tick_ms"),
            "drain_lag_ms": rec.get("drain_lag_ms"),
            "first_word_ms": rec.get("first_word_ms"),
            "stt_kind": rec.get("stt_kind"),
            "stt_engine": rec.get("stt_engine"),
            "skipped_http": rec.get("skipped_http"),
            "clock_id": ticket.get("clock_id"),
            "pcm_sha256": rec.get("pcm_sha256"),
            "speech_live": rec.get("speech_live"),
        })
        ok = (
            none_probe.get("kind") == "STT_NONE"
            and none_probe.get("ok") is False
            and probe_stt().get("ok") is True
            and pushed.get("cursor_out")
            and rec.get("ok") is True
            and rec.get("skipped_http") is False
            and rec.get("folded") is True
            and rec.get("stt_kind") == "ok"
            and rec.get("stt_engine") == "vosk"
            and rec.get("pcm_sha256") == sha
            and isinstance(rec.get("first_word_ms"), (int, float))
            and rec.get("first_word_ms") >= 0
            and rec.get("drain_lag_ms") is not None
            and rec.get("drain_lag_ms") >= 0
            and rec.get("cursor") == pushed.get("cursor_out")
            and ticket.get("clock_id") == PULL_CLOCK_ID == 18
            and ticket.get("stt_kind") == "ok"
            and ticket.get("audio_owner") == "desktop"
            and not k.paths.state("cvm", "audio.json").is_file()
        )
        return ok, live
    finally:
        svc.shutdown()
        if prev is None:
            sys.modules.pop("vosk", None)
        else:
            sys.modules["vosk"] = prev
        if env is None:
            os.environ.pop("COSMOS_VOSK_MODEL", None)
        else:
            os.environ["COSMOS_VOSK_MODEL"] = env


def test_dead_core_drain_is_unreachable():
    """Fail-closed: dead Core is UNREACHABLE; no invented pull.json."""
    tmp = _scratch()
    paths = CosmosPaths(tmp)
    clock = DesktopPullClock(
        CoreClient("http://127.0.0.1:1", "test-token"), paths)
    kind = None
    try:
        clock.drain()
    except CvmDtError as e:
        kind = e.kind
    return (
        kind == RefusalKind.UNREACHABLE
        and not paths.state("cvm", "pull.json").is_file()
        and clock.http_gets == 1
    )


def main() -> int:
    check("desktop pull-clock claims audio_owner==desktop and advances cursor",
          test_desktop_pull_clock_claims_owner_and_advances_cursor)
    check("drain folds phone.json, zeros backlog, writes pull_ms",
          test_drain_folds_and_zeros_backlog)
    check("idle second drain coalesces: skips Core GET, reads phone.json",
          test_idle_second_drain_skips_http)
    check("speech-live PCM is STT interrupt: first_word_ms, no extra GET",
          test_speech_live_stt_interrupt_skips_get)
    check("stale pcm pointer without recency coalesces (no forever-burst)",
          test_stale_pcm_pointer_coalesces)
    check("idle cadence_wait wakes on local phone.json speech",
          test_cadence_wait_wakes_on_speech)
    check("dead Core drain is UNREACHABLE and invents no ticket",
          test_dead_core_drain_is_unreachable)

    live = None
    loop_err = ""

    def _loop_probe():
        nonlocal live, loop_err
        try:
            ok, live = test_push_then_drain_emits_lag()
            return ok
        except Exception as e:                                        # noqa: BLE001
            loop_err = "%s: %s" % (type(e).__name__, e)
            raise

    check("POST /cvm/push then drain GET /cvm/pull: audio_owner=desktop, "
          "monotonic cursor, measured pull_ms, backlog 1->0, drain_lag_ms",
          _loop_probe)
    if loop_err and not any(p for l, p, _ in RESULTS if "POST /cvm/push then drain" in l):
        RESULTS[-1] = (RESULTS[-1][0], False, loop_err)

    stt_live = None
    stt_err = ""

    def _stt_probe():
        nonlocal stt_live, stt_err
        try:
            ok, stt_live = test_pcm_cas_binds_local_stt()
            return ok
        except Exception as e:                                        # noqa: BLE001
            stt_err = "%s: %s" % (type(e).__name__, e)
            raise

    check("POST /cvm/push PCM CAS then drain binds local STT; "
          "first_word_ms + clock_id=18 + skipped_http=false",
          _stt_probe)
    if stt_err and not any(p for l, p, _ in RESULTS if "PCM CAS then drain" in l):
        RESULTS[-1] = (RESULTS[-1][0], False, stt_err)
    if stt_live:
        live = stt_live

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
