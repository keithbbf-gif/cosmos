#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest: desktop CVM voice client (builds/cvm-dt/cvm_dt_voice.py).

Proves:
  * id18 pull.json is consumed READ-ONLY (clock_id==18)
  * wrong clock_id / missing ticket / core_ready=false / CLOCK_STALE / dead
    Core are typed UNREACHABLE (fail closed; never :8791)
  * local energy VAD distinguishes silence vs speech
  * typed + PTT turns POST the existing /api/v1/voice envelope
  * a real cosmos_service Handler quotes route/rc/brain (the bind fields)
  * pull.json is never written; phone client / pull-clock modules untouched

rc=0 here is a green log. Stage-6 quotes live_value.route + rc + brain/model
from a live POST /api/v1/voice on :8770.
"""
from __future__ import annotations

import json
import os
import re
import sys
import tempfile
import threading
import time
import types
import uuid
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "cosmos"))

from cosmos_cvm_push import (  # noqa: E402
    PULL_CLOCK_ID, STT_NONE_ACK, VOICE_LISTENING, VOICE_READY,
    VOICE_UNAVAILABLE, PlaybackGate, ack_listening, ack_stt_none,
    reset_voice_ack, voice_state,
)
from cosmos_paths import CosmosPaths, write_sentinel  # noqa: E402

from cvm_dt import (  # noqa: E402
    CLIENT_ID, FAST_READ_S, LEASE_REL, VOICE_READ_S, AudioLease, CoreClient,
    CvmDt, CvmDtError, FakeBackend, RefusalKind, make_dt,
)
from cvm_dt_voice import (  # noqa: E402
    HEARTBEAT_NAME, MIC_IDLE, STT_RATE, TITLE, VAD_FRAME_MS, VOICE_ROUTE, WIRE,
    CvmDtVoice, FakeTranscriber, VoskTranscriber, _frame_bytes,
    _resample_chunks, consume_id18_pull, default_transcriber, energy_vad,
    probe_ear, probe_vosk, probe_windows_default, quote_voice,
    resample_pcm16_mono,
    run_selftest, vad_interrupt, voice_main,
)
from wasapi import (  # noqa: E402
    ENDPOINTS_NAME, Endpoint, _LAST, bind_persist, capture_pcm16_mono,
    load_endpoints, pick_endpoint, play_earcon, quote_route, route_status,
    save_endpoints,
)

RESULTS = []
BTS_IMPORT = re.compile(r"^\s*(?:from|import)\s+bts_\w+", re.M)
DRIVE_LIT = re.compile(r"[A-Za-z]:\\")
SRC = (HERE / "cvm_dt_voice.py").read_text(encoding="utf-8")
TREE_ID = "KMesh-COSMOS-live"


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:                                            # noqa: BLE001
        RESULTS.append((label, False, "%s: %s" % (type(e).__name__, e)))


def expect(kind):
    def wrap(f):
        def inner():
            try:
                f()
            except CvmDtError as e:
                return e.kind == kind
            return False
        return inner
    return wrap


def _scratch():
    tmp = Path(tempfile.mkdtemp(prefix="cvm-dt-voice-"))
    write_sentinel(tmp, TREE_ID)
    (tmp / "config").mkdir()
    (tmp / "state").mkdir()
    (tmp / "config" / "api_token.txt").write_text("test-token", encoding="utf-8")
    return tmp


def _ticket(root, **extra):
    p = Path(root) / "state" / "cvm" / "pull.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    d = {
        "cvm": 1,
        "tree_id": TREE_ID,
        "issued_epoch": time.time(),
        "pull": True,
        "audio_owner": "desktop",
        "clock_id": PULL_CLOCK_ID,
        "core_ready": True,
        "core_kind": "ok",
        "voice_client_timeout_s": VOICE_READ_S,
        "cursor": "t0",
        "writer": "cvm-dt-clock",
        "kinds": ["voice_session"],
    }
    d.update(extra)
    p.write_text(json.dumps(d), encoding="utf-8")
    return p


def _loud_pcm(seconds: float = 0.3, rate: int = 16000) -> bytes:
    n = max(1, int(rate * seconds))
    # PCM16 square-ish: amplitude well above energy_vad threshold
    return (b"\x00\x40" * (n // 2)) + (b"\x00\xc0" * (n - n // 2))


class _FakeCore(BaseHTTPRequestHandler):
    token = "test-token"
    blocked = False
    last_body = None
    hits = 0

    def log_message(self, *args):                                     # noqa: ARG002
        return

    def _send(self, code, obj):
        body = json.dumps({"served_at": 1.0, **obj}).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _authed(self):
        return self.headers.get("Authorization") == "Bearer " + self.token

    def do_GET(self):                                                 # noqa: N802
        if not self._authed():
            return self._send(401, {"error": "UNAUTHORIZED"})
        if self.path.startswith("/api/v1/status"):
            return self._send(200, {"ready": True, "tree_id": TREE_ID})
        if self.path.startswith("/api/v1/control"):
            flags = {"pause": self.blocked, "mic_off": False, "clear_queue": False}
            return self._send(200, {"client_id": CLIENT_ID, "global": flags,
                                    "client": None, "effective": flags})
        return self._send(404, {"error": "NO"})

    def do_POST(self):                                                # noqa: N802
        if not self._authed():
            return self._send(401, {"error": "UNAUTHORIZED"})
        n = int(self.headers.get("Content-Length") or 0)
        d = json.loads(self.rfile.read(n).decode("utf-8") or "{}")
        _FakeCore.last_body = d
        if self.path == VOICE_ROUTE:
            _FakeCore.hits += 1
            if self.blocked:
                return self._send(200, {
                    "ok": False, "session_id": d.get("session_id"),
                    "kind": "refused", "reply": "[CONTROL_BLOCKED]",
                    "spoken": "Voice is paused.", "needs_confirm": False,
                    "confirm_id": None, "action": None, "sources": [],
                    "refused": True, "error": "CONTROL_BLOCKED",
                    "brain": "local"})
            sid = str(d.get("session_id") or "") or uuid.uuid4().hex
            spoken = "Ready." if d.get("transcript") == "status" else "Help is available."
            return self._send(200, {
                "ok": True, "session_id": sid, "kind": "command",
                "reply": spoken, "spoken": spoken, "needs_confirm": False,
                "confirm_id": None, "action": d.get("transcript"),
                "sources": [], "refused": False, "brain": "local"})
        return self._send(404, {"error": "NO"})


def _serve():
    httpd = HTTPServer(("127.0.0.1", 0), _FakeCore)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    return httpd


def _voice(root, base, none=False, transcriber=None) -> CvmDtVoice:
    paths = CosmosPaths(root)
    lease = AudioLease(paths.state(*LEASE_REL), paths.sentinel.tree_id)
    dt = CvmDt(paths, CoreClient(base, "test-token"),
               FakeBackend(none=none), lease)
    return CvmDtVoice(dt, transcriber=transcriber)


def test_selftest_green_log():
    rec = run_selftest()
    lv = rec["live_value"]
    return (rec["selftest"] == "ok"
            and lv["clock_id"] == 18
            and lv["mic_state"] == MIC_IDLE
            and lv["stt_kind"] in ("STT_NONE", "ok")
            and bool(lv["device_name"])
            and lv["wrote_pull"] is False
            and lv["route"] == VOICE_ROUTE
            and lv["rc"] == 200
            and lv["brain"] == "local"
            and lv["stt_rate"] == STT_RATE)


def test_timeouts_are_p0():
    return FAST_READ_S == 8.0 and VOICE_READ_S == 70.0


def test_pull_clock_id_is_18():
    return PULL_CLOCK_ID == 18


def test_consume_id18():
    tmp = _scratch()
    p = _ticket(tmp)
    before = p.read_bytes()
    rec = consume_id18_pull(CosmosPaths(tmp))
    return (rec["clock_id"] == 18
            and rec["audio_owner"] == "desktop"
            and p.read_bytes() == before)


def test_missing_ticket_unreachable():
    tmp = _scratch()
    try:
        consume_id18_pull(CosmosPaths(tmp))
        return False
    except CvmDtError as e:
        return e.kind == RefusalKind.UNREACHABLE and "invent" in str(e)


def test_wrong_clock_id_unreachable():
    tmp = _scratch()
    p = _ticket(tmp, clock_id=16)
    before = p.read_bytes()
    try:
        consume_id18_pull(CosmosPaths(tmp))
        return False
    except CvmDtError as e:
        return e.kind == RefusalKind.UNREACHABLE and p.read_bytes() == before


def test_core_ready_false_unreachable():
    tmp = _scratch()
    _ticket(tmp, core_ready=False, core_kind="ok")
    try:
        consume_id18_pull(CosmosPaths(tmp))
        return False
    except CvmDtError as e:
        return e.kind == RefusalKind.UNREACHABLE and "core_ready" in str(e)


def test_clock_stale_unreachable():
    tmp = _scratch()
    _ticket(tmp, issued_epoch=1.0)
    try:
        consume_id18_pull(CosmosPaths(tmp), ttl_s=30.0, now=time.time())
        return False
    except CvmDtError as e:
        return e.kind == RefusalKind.UNREACHABLE and "CLOCK_STALE" in str(e)


def test_dead_core_unreachable_after_id18():
    tmp = _scratch()
    p = _ticket(tmp)
    before = p.read_bytes()
    v = _voice(tmp, "http://127.0.0.1:1")
    try:
        v.say("status", speak=False)
        return False
    except CvmDtError as e:
        return e.kind == RefusalKind.UNREACHABLE and p.read_bytes() == before
    finally:
        v.close()


def test_phone_owner_is_audio_owned_no_write():
    tmp = _scratch()
    p = _ticket(tmp, audio_owner="phone")
    before = p.read_bytes()
    httpd = _serve()
    try:
        v = _voice(tmp, "http://127.0.0.1:%d" % httpd.server_address[1])
        try:
            v.say("status", speak=False)
            return False
        except CvmDtError as e:
            return e.kind == RefusalKind.AUDIO_OWNED and p.read_bytes() == before
        finally:
            v.close()
    finally:
        httpd.shutdown()


def test_vad_silence_vs_speech():
    quiet = energy_vad(b"\x00\x00" * 1600, 16000)
    loud = energy_vad(_loud_pcm(), 16000)
    return quiet["speech"] is False and loud["speech"] is True and loud["rms"] > quiet["rms"]


def test_typed_say_quotes_voice_fields():
    tmp = _scratch()
    p = _ticket(tmp)
    before = p.read_bytes()
    httpd = _serve()
    _FakeCore.hits = 0
    try:
        v = _voice(tmp, "http://127.0.0.1:%d" % httpd.server_address[1])
        rec = v.say("status", speak=False)
        body = _FakeCore.last_body or {}
        lv = rec["live_value"]
        return (
            rec["ok"] is True
            and rec["route"] == VOICE_ROUTE == lv["route"]
            and lv["rc"] == 200
            and lv["brain"] == "local"
            and lv["model"] == "local"
            and lv["kind"] == "command"
            and lv["wrote_pull"] is False
            and p.read_bytes() == before
            and body.get("transcript") == "status"
            and body.get("client_id") == CLIENT_ID
            and body.get("mode") == "voice"
            and "idempotency_key" in body
            and _FakeCore.hits == 1
            and rec["stt"]["engine"] == "typed"
        )
    finally:
        httpd.shutdown()


def test_vad_interrupt_first_word_not_gated_by_get():
    """First-word STT is VAD-event elapsed — no GET, no 15s coalesce."""
    stt = FakeTranscriber("status")
    t0 = time.perf_counter()
    rec = vad_interrupt(_loud_pcm(), STT_RATE, transcribe=stt.transcribe)
    wall_ms = round((time.perf_counter() - t0) * 1000.0, 3)
    silent = vad_interrupt(b"\x00\x00" * 1600, STT_RATE, transcribe=stt.transcribe)
    return (
        rec.get("vad_event") is True
        and rec.get("speech") is True
        and rec.get("transcript") == "status"
        and rec.get("stt_kind") == "ok"
        and isinstance(rec.get("first_word_ms"), (int, float))
        and rec["first_word_ms"] >= 0
        and rec["first_word_ms"] < 250
        and wall_ms < 250
        and rec.get("barge_in") is False
        and silent.get("vad_event") is False
        and silent.get("first_word_ms") is None
        and len(stt.calls) == 1
    )


def test_barge_in_cancels_playback():
    """Interrupt-only: cancel play, no STT success, no follow-up POST, no pull write."""
    tmp = _scratch()
    p = _ticket(tmp)
    before = p.read_bytes()
    httpd = _serve()
    _FakeCore.hits = 0
    try:
        v = _voice(tmp, "http://127.0.0.1:%d" % httpd.server_address[1],
                   transcriber=FakeTranscriber("help"))
        rec = v.barge_in(_loud_pcm(), play_pcm=b"\x00\x10" * 16000)
        v.dt.speak = lambda spoken, cancel=None: (
            v.dt.audio.play_pcm16_mono(b"\x00\x10" * 16000, STT_RATE, cancel=cancel),
            {"engine": "fake"})[1]
        posted = v._post("status", speak=True, barge_pcm=_loud_pcm())
        barge = posted.get("barge") or {}
        body = _FakeCore.last_body or {}
        return (
            rec.get("barge_in") is True
            and rec.get("vad_event") is True
            and rec.get("stt_kind") == "interrupt"
            and rec.get("usable") is False
            and rec.get("transcript") == ""
            and isinstance(rec.get("cancel_ms"), (int, float))
            and 0 <= rec["cancel_ms"] < 400
            and isinstance(rec.get("first_word_ms"), (int, float))
            and 0 <= rec["first_word_ms"] < 400
            and v.dt.audio.cancelled is True
            and barge.get("barge_in") is True
            and barge.get("stt_kind") == "interrupt"
            and barge.get("usable") is False
            and barge.get("transcript") == ""
            and body.get("transcript") == "status"
            and _FakeCore.hits == 1
            and p.read_bytes() == before
            and PlaybackGate().is_set() is False
        )
    finally:
        httpd.shutdown()


def test_ptt_turn_vad_stt_posts_transcript():
    tmp = _scratch()
    p = _ticket(tmp)
    before = p.read_bytes()
    httpd = _serve()
    try:
        stt = FakeTranscriber("status")
        v = _voice(tmp, "http://127.0.0.1:%d" % httpd.server_address[1],
                   transcriber=stt)
        rec = v.turn(pcm=_loud_pcm(), rate=16000, speak=False)
        rec48 = v.turn(pcm=_loud_pcm(0.3, 48000), rate=48000, speak=False)
        body = _FakeCore.last_body or {}
        lv = rec["live_value"]
        return (
            rec["ok"] is True
            and rec["vad"]["speech"] is True
            and rec["stt"]["engine"] == "fake"
            and rec["stt"]["transcript"] == "status"
            and body.get("transcript") == "status"
            and lv["route"] == VOICE_ROUTE
            and lv["rc"] == 200
            and lv["brain"] == "local"
            and p.read_bytes() == before
            and rec48["ok"] is True
            and rec48["rate"] == STT_RATE
            and stt.calls[-1][1] == STT_RATE
            and rec48["device_name"] == "Headphones (FAKE HT3)"
        )
    finally:
        httpd.shutdown()


def test_ptt_silence_is_stt_none():
    tmp = _scratch()
    _ticket(tmp)
    httpd = _serve()
    try:
        v = _voice(tmp, "http://127.0.0.1:%d" % httpd.server_address[1],
                   transcriber=FakeTranscriber("status"))
        try:
            v.turn(pcm=b"\x00\x00" * 1600, rate=16000, speak=False)
            return False
        except CvmDtError as e:
            return e.kind == RefusalKind.STT_NONE and "VAD" in str(e)
    finally:
        httpd.shutdown()


def test_unbound_stt_is_stt_none():
    tmp = _scratch()
    _ticket(tmp)
    httpd = _serve()
    try:
        v = _voice(tmp, "http://127.0.0.1:%d" % httpd.server_address[1],
                   transcriber=None)
        try:
            v.turn(pcm=_loud_pcm(), rate=16000, speak=False)
            return False
        except CvmDtError as e:
            return e.kind == RefusalKind.STT_NONE
    finally:
        httpd.shutdown()


def test_resume_same_sid():
    tmp = _scratch()
    _ticket(tmp)
    httpd = _serve()
    try:
        v = _voice(tmp, "http://127.0.0.1:%d" % httpd.server_address[1])
        a = v.say("status", speak=False)
        sid = a["session_id"]
        b = v.say("help", speak=False)
        return bool(sid) and sid == b["session_id"] and len(sid) == 32
    finally:
        httpd.shutdown()


def test_quote_voice_model_from_sources():
    q = quote_voice({
        "ok": True, "session_id": "s", "kind": "ask", "brain": "local",
        "spoken": "x", "served_at": 2.0, "sources": ["model:grok-4.5", "usd:0.01"],
        "_http": 200,
    })
    return (q["route"] == VOICE_ROUTE and q["rc"] == 200
            and q["brain"] == "local" and q["model"] == "grok-4.5")


def test_reuse_not_bloat():
    """Share the seam via CvmDt.ask; do not fork phone / pull-clock / kernel."""
    return (
        "from cvm_dt import" in SRC
        and "CoreClient" in SRC
        and "AudioLease" in SRC
        and "PULL_CLOCK_ID" in SRC
        and "stamp_desktop_pull" not in SRC
        and "from cvm_pull import" not in SRC
        and "import cvm_pull" not in SRC
        and "from cvm_dt_clock import" not in SRC
        and "cvm_phone" not in SRC
        and "cosmos_kernel" not in SRC
        and "cosmos_dispatch" not in SRC
        and "cosmos_collector" not in SRC
        and "cosmos_index" not in SRC
        and BTS_IMPORT.search(SRC) is None
        and DRIVE_LIT.search(SRC) is None
        and TITLE == "cvm-dt-voice"
        and WIRE == "cvm-dt-voice/1"
        and HEARTBEAT_NAME == "cvm_dt_voice_heartbeat.json"
        and "self.dt.ask(" in SRC
        and "self.dt.core.voice" not in SRC
        and "from cosmos_clock import" in SRC
        and "write_heartbeat" in SRC
        and "def write_heartbeat" not in SRC
        and "def run_bind" not in SRC
        and "def quote_ticket_meta" not in SRC
        and "resample_pcm16_mono" in SRC
        and probe_vosk()["kind"] in ("STT_NONE", "ok")
    )


def test_idle_tick_heartbeats_mic_idle():
    tmp = _scratch()
    p = _ticket(tmp)
    before = p.read_bytes()
    v = _voice(tmp, "http://127.0.0.1:1")
    rec = v.tick(polls=1, speak=False)
    hb_path = Path(rec["heartbeat_path"])
    hb = json.loads(hb_path.read_text(encoding="utf-8"))
    return (
        rec["ok"] is True
        and rec["tick"] == "idle"
        and rec["mic_state"] == MIC_IDLE
        and rec["clock_id"] == PULL_CLOCK_ID == 18
        # The tick reports the BOUND ear, which is VOSK only when a model is
        # handed in and otherwise the on-box SAPI recognizer. Asserting
        # probe_vosk() here made the row mean "no ear" on every box without
        # the vosk wheel -- it passed for the wrong reason. See cvm_dt_stt.
        and rec["stt_kind"] == probe_ear()["kind"]
        and rec["stt_engine"] == probe_ear().get("engine")
        and rec.get("session_id") is None
        and rec.get("device_name") == "Headphones (FAKE HT3)"
        and rec.get("capture_name") == "Headphones (FAKE HT3)"
        and hb["last_run_epoch"]
        and hb["clock_id"] == 18
        and hb["mic_state"] == MIC_IDLE
        and hb.get("device_name") == "Headphones (FAKE HT3)"
        and hb.get("worker") == "cvm-dt-voice"
        and "core_kind" in hb
        and hb_path.name == HEARTBEAT_NAME
        and p.read_bytes() == before
    )


def test_dead_core_say_tick_heartbeats_unreachable():
    tmp = _scratch()
    p = _ticket(tmp)
    before = p.read_bytes()
    v = _voice(tmp, "http://127.0.0.1:1")
    rec = v.tick(polls=1, say="status", speak=False)
    hb = json.loads(Path(rec["heartbeat_path"]).read_text(encoding="utf-8"))
    return (
        rec["ok"] is False
        and rec.get("kind") == str(RefusalKind.UNREACHABLE)
        and rec["core_kind"] == "UNREACHABLE"
        and rec.get("session_id") is None
        and rec["mic_state"] == MIC_IDLE
        and hb["core_kind"] == "UNREACHABLE"
        and hb["last_run_epoch"]
        and hb["clock_id"] == 18
        and ":8791" not in str(rec.get("detail") or "")
        and p.read_bytes() == before
    )


def test_tick_does_not_ptt_without_flag():
    tmp = _scratch()
    _ticket(tmp)
    audio = FakeBackend()
    paths = CosmosPaths(tmp)
    lease = AudioLease(paths.state(*LEASE_REL), paths.sentinel.tree_id)
    dt = CvmDt(paths, CoreClient("http://127.0.0.1:1", "test-token"), audio, lease)
    v = CvmDtVoice(dt, transcriber=FakeTranscriber("status"))
    rec = v.tick(polls=1, speak=False)
    return rec["mic_state"] == MIC_IDLE and audio.played == [] and rec["tick"] == "idle"


def test_cvm_dt_voice_subcommand_selftest():
    import cvm_dt as dtmod
    rc = dtmod.main(["voice", "--selftest"])
    return rc == 0


def test_voice_main_selftest_rc0():
    return voice_main(["--selftest"]) == 0


def test_make_dt_is_the_constructor():
    tmp = _scratch()
    _ticket(tmp)
    dt = make_dt(tmp, "http://127.0.0.1:1", audio=FakeBackend(), token="test-token")
    return isinstance(dt, CvmDt) and dt.core.base.startswith("http://127.0.0.1:1")


def test_vosk_binds_when_model_present():
    tmp = _scratch()
    model = tmp / "vosk-model"
    model.mkdir()
    prev, env = sys.modules.get("vosk"), os.environ.get("COSMOS_VOSK_MODEL")
    fake = types.ModuleType("vosk")
    fake.Model = lambda path: path
    fake.SetLogLevel = lambda *_a, **_k: None

    class _Rec:
        def __init__(self, _m, rate):
            self.rate = rate

        def AcceptWaveform(self, pcm):                                  # noqa: ARG002
            return True

        def FinalResult(self):
            return json.dumps({"text": "status"})

    fake.KaldiRecognizer = _Rec
    sys.modules["vosk"] = fake
    os.environ["COSMOS_VOSK_MODEL"] = str(model)
    httpd = _serve()
    try:
        _ticket(tmp)
        v = _voice(tmp, "http://127.0.0.1:%d" % httpd.server_address[1])
        rec = v.tick(polls=1, ptt=True, pcm=_loud_pcm(), speak=False)
        return (probe_vosk().get("ok") is True
                and isinstance(default_transcriber(), VoskTranscriber)
                and isinstance(v.transcriber, VoskTranscriber)
                and rec["ok"] is True and rec["stt_kind"] == "ok"
                and (_FakeCore.last_body or {}).get("transcript") == "status"
                and bool(probe_windows_default().get("device_name")))
    finally:
        httpd.shutdown()
        if prev is None:
            sys.modules.pop("vosk", None)
        else:
            sys.modules["vosk"] = prev
        if env is None:
            os.environ.pop("COSMOS_VOSK_MODEL", None)
        else:
            os.environ["COSMOS_VOSK_MODEL"] = env


def test_real_service_voice_route_fields():
    """Runtime binding against the REAL cosmos_service /api/v1/voice Handler.

    Not live :8770 (that probe is separate). This is the same route code the
    live Core runs: install -> Service(port=0) -> POST /voice transcript=status
    (read-only commander; brain=local). Quote route, rc, brain, model.
    """
    from cosmos_kernel import Kernel, install
    from cosmos_service import Service

    td = Path(tempfile.mkdtemp(prefix="cvm-dt-voice-svc-"))
    install(td, tree_id=TREE_ID)
    k = Kernel(td, worker="cvm-dt-voice-bind")
    token = "bind-token"
    k.paths.config("api_token.txt").write_text(token + "\n", encoding="utf-8")
    client_root = _scratch()
    (client_root / "config" / "api_token.txt").write_text(token, encoding="utf-8")
    p = _ticket(client_root)
    before = p.read_bytes()
    svc = Service(k, host="127.0.0.1", port=0)
    svc.serve_background()
    try:
        # Service mints/overwrites the token on loopback; use the live one.
        live_tok = svc.token
        (client_root / "config" / "api_token.txt").write_text(live_tok, encoding="utf-8")
        paths = CosmosPaths(client_root)
        lease = AudioLease(paths.state(*LEASE_REL), paths.sentinel.tree_id)
        base = "http://127.0.0.1:%d" % svc.port
        dt = CvmDt(paths, CoreClient(base, live_tok), FakeBackend(), lease)
        v = CvmDtVoice(dt)
        rec = v.say("status", speak=False)
        lv = rec["live_value"]
        quoted = rec["quoted"]
        v.close()
        return (
            rec["ok"] is True
            and quoted["route"] == VOICE_ROUTE == "/api/v1/voice"
            and quoted["rc"] == 200
            and quoted["brain"] in ("local", "opus", "grok")
            and bool(quoted["model"])
            and quoted["kind"] == "command"
            and quoted["ok"] is True
            and bool(quoted["session_id"])
            and quoted["served_at"] is not None
            and lv["wrote_pull"] is False
            and p.read_bytes() == before
            and rec["pull"]["clock_id"] == PULL_CLOCK_ID == 18
        )
    finally:
        svc.shutdown()


def test_voice_state_transitions_and_fallback_report():
    """Explicit voice_state + visible fallback device (not silent reroute).

    Isolates the iter4-fail row: prints actual vs expected on mismatch.
    Mix format is last-open (_LAST); FakeBackend never opens WASAPI so
    mix_* may be empty — do not fabricate a rate to make this green.
    """
    rows = []

    def eq(name, actual, expected):
        good = actual == expected
        rows.append((name, actual, expected, good))
        if not good:
            print("ROW %s actual=%r expected=%r" % (name, actual, expected),
                  flush=True)
        return good

    reset_voice_ack()
    _LAST.clear()
    a = ack_listening()
    b = ack_stt_none(now=0.0)
    c = ack_stt_none(now=0.1)
    default_c = Endpoint("capture", "console", "def-cap", "Mic Default", False)
    default_r = Endpoint("render", "console", "def-rend", "Speakers Default", False)
    tozo = Endpoint("render", "console", "tozo-id", "Headphones (TOZO HT3)", True)
    webcam = Endpoint("capture", "console", "web-id", "Webcam Mic", False)
    cap_ok, cap_fb, _why = pick_endpoint("web-id", [webcam, default_c], default_c)
    cap_miss, cap_miss_fb, cap_miss_why = pick_endpoint(
        "gone-mic", [webcam, default_c], default_c)
    rend_ok, rend_fb, _ = pick_endpoint("tozo-id", [tozo, default_r], default_r)
    init, init_fb, init_why = pick_endpoint("", [tozo], default_r)
    quiet = b"\x00\x00" * 3200
    ev = vad_interrupt(quiet + _loud_pcm(0.3), STT_RATE,
                       transcribe=FakeTranscriber("status").transcribe)
    tmp = _scratch()
    persist = tmp / "config" / ENDPOINTS_NAME
    save_endpoints(persist, "gone-mic", "fake-render-id")
    _ticket(tmp)
    httpd = _serve()
    try:
        audio = FakeBackend()
        paths = CosmosPaths(tmp)
        lease = AudioLease(paths.state(*LEASE_REL), paths.sentinel.tree_id)
        dt = CvmDt(paths, CoreClient(
            "http://127.0.0.1:%d" % httpd.server_address[1], "test-token"),
                   audio, lease)
        v = CvmDtVoice(dt, transcriber=FakeTranscriber("status"))
        reset_voice_ack()
        idle = v.tick(polls=1, speak=False)
        ptt = v.tick(polls=2, ptt=True, pcm=_loud_pcm(), speak=False)
        none_v = _voice(tmp, "http://127.0.0.1:%d" % httpd.server_address[1],
                        transcriber=None)
        reset_voice_ack()
        refused = none_v.tick(polls=3, ptt=True, pcm=_loud_pcm(), speak=False)
        route = quote_route(audio.probe(), persist,
                            caps=[audio.probe().capture],
                            rends=[audio.probe().render])
        loaded = load_endpoints(persist)
        vad = ev.get("vad") or {}
        eq("listen.voice_state", a.get("voice_state"), VOICE_LISTENING)
        eq("listen.ack", a.get("ack"), "listening")
        eq("listen.gated_on_pull", a.get("gated_on_pull"), False)
        eq("listen.gated_on_id18", a.get("gated_on_id18"), False)
        eq("stt_none.voice_state", b.get("voice_state"), VOICE_UNAVAILABLE)
        eq("stt_none.ack", b.get("ack"), STT_NONE_ACK)
        eq("stt_none.ack_emitted", b.get("ack_emitted"), True)
        eq("stt_none.rate_limited", c.get("ack_emitted"), False)
        eq("pick.cap_ok.id", cap_ok.device_id, "web-id")
        eq("pick.cap_ok.fb", cap_fb, False)
        eq("pick.cap_miss.id", cap_miss.device_id, "def-cap")
        eq("pick.cap_miss.fb", cap_miss_fb, True)
        eq("pick.cap_miss.why", cap_miss_why, "requested_missing")
        eq("pick.rend_ok.id", rend_ok.device_id, "tozo-id")
        eq("pick.rend_ok.fb", rend_fb, False)
        eq("pick.init.id", init.device_id, "def-rend")
        eq("pick.init.fb", init_fb, False)
        eq("pick.init.why", init_why, "windows_default_initial")
        eq("vad.lead_kept", ev.get("lead_kept"), True)
        eq("vad.usable", ev.get("usable"), True)
        eq("vad.transcript", ev.get("transcript"), "status")
        eq("vad.start_le_first",
           (vad.get("start_ms") or 0) <= (vad.get("first_voiced_ms") or 0), True)
        eq("vad.first_word_bound",
           isinstance(ev.get("first_word_ms"), (int, float))
           and ev["first_word_ms"] < 500, True)
        eq("idle.voice_state", idle.get("voice_state"), VOICE_READY)
        eq("idle.device_name", idle.get("device_name"), "Headphones (FAKE HT3)")
        eq("ptt.ok", ptt.get("ok"), True)
        eq("ptt.listen_ack", ptt.get("listen_ack"), "listening")
        eq("ptt.gated_on_pull", ptt.get("gated_on_pull"), False)
        eq("ptt.voice_state", ptt.get("voice_state") in (
            VOICE_READY, VOICE_LISTENING), True)
        eq("route.capture_fallback", route.get("capture_fallback"), True)
        eq("route.render_opened_requested",
           route.get("render_opened_requested"), True)
        eq("route.capture_opened_requested",
           route.get("capture_opened_requested"), False)
        eq("route.input_device_id", route.get("input_device_id"),
           "fake-capture-id")
        eq("route.output_device_id", route.get("output_device_id"),
           "fake-render-id")
        eq("route.capture_fallback_reason",
           route.get("capture_fallback_reason"), "requested_missing")
        eq("route.has_mix_keys",
           isinstance(route.get("mix_capture"), dict)
           and isinstance(route.get("mix_render"), dict), True)
        eq("persist.input", loaded.get("input_device_id"), "gone-mic")
        eq("persist.output", loaded.get("output_device_id"), "fake-render-id")
        eq("refused.ok", refused.get("ok"), False)
        eq("refused.voice_state", refused.get("voice_state"), VOICE_UNAVAILABLE)
        eq("refused.ack", refused.get("ack"), STT_NONE_ACK)
        eq("refused.stt_kind", refused.get("stt_kind"), "STT_NONE")
        eq("persist.file", persist.is_file(), True)
        eq("runtime.voice_state_fn", voice_state(), VOICE_UNAVAILABLE)
    finally:
        httpd.shutdown()
        _LAST.clear()
        bind_persist(None)
    failed = [(n, a, e) for n, a, e, g in rows if not g]
    if failed:
        raise AssertionError("mismatches: " + "; ".join(
            "%s actual=%r expected=%r" % (n, a, e) for n, a, e in failed))
    return True


def test_com_init_is_per_thread():
    """Worker thread CoInitializeEx after main-thread init (COM is per-thread)."""
    import wasapi as w
    calls = []

    class _Ole:
        def CoInitializeEx(self, _p, _mode):
            calls.append(threading.get_ident())
            return 0

        def CoUninitialize(self):
            return None

    old, old_tls = w._ole32, w._tls
    w._ole32, w._tls = _Ole(), threading.local()
    try:
        w._com_init()
        main_id = threading.get_ident()

        def worker():
            w._com_init()
            w._com_uninit()

        t = threading.Thread(target=worker)
        t.start()
        t.join(2)
        w._com_uninit()
        return (not t.is_alive()
                and calls.count(main_id) == 1
                and len(calls) == 2
                and any(i != main_id for i in calls))
    finally:
        w._ole32, w._tls = old, old_tls


def test_endpoint_open_and_fallback_report():
    """SELECTED endpoints are ACTUALLY OPENED; missing id is a visible fallback.

    Isolates GAP 1. Prints actual vs expected. Live WASAPI Initialize, not picker.
    """
    rows = []

    def eq(name, actual, expected):
        good = actual == expected
        rows.append((name, actual, expected, good))
        if not good:
            print("ROW %s actual=%r expected=%r" % (name, actual, expected),
                  flush=True)
        return good

    tmp = Path(tempfile.mkdtemp(prefix="cvm-open-"))
    persist = tmp / ENDPOINTS_NAME
    _LAST.clear()
    bind_persist(persist)
    try:
        live = route_status(persist)
        eq("pre.capture_opened_on", live.get("capture_opened_on"), "")
        eq("pre.render_opened_on", live.get("render_opened_on"), "")
        req_in = str(live.get("windows_default_capture_id") or "")
        req_out = str(live.get("windows_default_render_id") or "")
        eq("pre.has_default_capture", bool(req_in), True)
        eq("pre.has_default_render", bool(req_out), True)
        save_endpoints(persist, req_in, req_out)
        bind_persist(persist)
        capture_pcm16_mono(0.12)
        play_earcon(ms=40)
        hit = route_status(persist)
        eq("hit.capture_opened_on", hit.get("capture_opened_on"), req_in)
        eq("hit.render_opened_on", hit.get("render_opened_on"), req_out)
        eq("hit.opened_on_eq_requested.cap",
           hit.get("capture_opened_on") == hit.get("requested_input_device_id"),
           True)
        eq("hit.opened_on_eq_requested.rend",
           hit.get("render_opened_on") == hit.get("requested_output_device_id"),
           True)
        eq("hit.capture_opened_requested",
           hit.get("capture_opened_requested"), True)
        eq("hit.render_opened_requested",
           hit.get("render_opened_requested"), True)
        eq("hit.capture_fallback", hit.get("capture_fallback"), False)
        eq("hit.render_fallback", hit.get("render_fallback"), False)
        eq("hit.mix_capture.rate",
           bool((hit.get("mix_capture") or {}).get("rate")), True)
        eq("hit.mix_render.rate",
           bool((hit.get("mix_render") or {}).get("rate")), True)
        save_endpoints(persist, "gone-mic-id", "gone-spk-id")
        bind_persist(persist)
        _LAST.clear()
        capture_pcm16_mono(0.12)
        play_earcon(ms=40)
        miss = route_status(persist)
        eq("miss.capture_fallback", miss.get("capture_fallback"), True)
        eq("miss.render_fallback", miss.get("render_fallback"), True)
        eq("miss.capture_fallback_reason",
           miss.get("capture_fallback_reason"), "requested_missing")
        eq("miss.render_fallback_reason",
           miss.get("render_fallback_reason"), "requested_missing")
        eq("miss.capture_opened_on", miss.get("capture_opened_on"),
           miss.get("windows_default_capture_id"))
        eq("miss.render_opened_on", miss.get("render_opened_on"),
           miss.get("windows_default_render_id"))
        eq("miss.opened_not_gone.cap",
           miss.get("capture_opened_on") != "gone-mic-id", True)
        eq("miss.opened_not_gone.rend",
           miss.get("render_opened_on") != "gone-spk-id", True)
        eq("miss.capture_opened_requested",
           miss.get("capture_opened_requested"), False)
        eq("miss.render_opened_requested",
           miss.get("render_opened_requested"), False)
        eq("miss.capture_name", bool(miss.get("capture_name")), True)
        eq("miss.render_name", bool(miss.get("device_name")), True)
    finally:
        _LAST.clear()
        bind_persist(None)
    failed = [(n, a, e) for n, a, e, g in rows if not g]
    if failed:
        raise AssertionError("mismatches: " + "; ".join(
            "%s actual=%r expected=%r" % (n, a, e) for n, a, e in failed))
    return True


def test_stt_none_completion_unavailable():
    """vad_interrupt STT_NONE completion: voice_state=unavailable, no false transcript.

    Isolates GAP 2 + preroll actuals + native-rate VAD (silence not resampled).
    """
    rows = []

    def eq(name, actual, expected):
        good = actual == expected
        rows.append((name, actual, expected, good))
        if not good:
            print("ROW %s actual=%r expected=%r" % (name, actual, expected),
                  flush=True)
        return good

    reset_voice_ack()
    rec = vad_interrupt(_loud_pcm(), STT_RATE, transcribe=None)
    eq("speech", rec.get("speech"), True)
    eq("stt_kind", rec.get("stt_kind"), "STT_NONE")
    eq("transcript", rec.get("transcript"), "")
    eq("usable", rec.get("usable"), False)
    eq("voice_state", rec.get("voice_state"), VOICE_UNAVAILABLE)
    eq("ack", rec.get("ack"), STT_NONE_ACK)
    eq("runtime.voice_state", voice_state(), VOICE_UNAVAILABLE)
    silent = vad_interrupt(b"\x00\x00" * 4800, 48000, transcribe=None)
    eq("silence.speech", silent.get("speech"), False)
    eq("silence.rate_native", silent.get("rate"), 48000)
    eq("silence.transcript", silent.get("transcript"), "")
    eq("silence.first_word_ms", silent.get("first_word_ms"), None)
    reset_voice_ack()
    loud48 = vad_interrupt(_loud_pcm(0.3, 48000), 48000, transcribe=None)
    eq("loud48.vad_rate", (loud48.get("vad") or {}).get("rate"), 48000)
    eq("loud48.out_rate", loud48.get("rate"), STT_RATE)
    eq("loud48.voice_state", loud48.get("voice_state"), VOICE_UNAVAILABLE)
    eq("loud48.transcript", loud48.get("transcript"), "")
    eq("loud48.usable", loud48.get("usable"), False)
    lead = energy_vad((b"\x00\x00" * 3200) + _loud_pcm(0.3), STT_RATE)
    eq("preroll.lead_kept", lead.get("lead_kept"), True)
    eq("preroll.ms_gt_0", (lead.get("preroll_ms") or 0) > 0, True)
    eq("preroll.bytes_gt_0", (lead.get("preroll_bytes") or 0) > 0, True)
    at_start = energy_vad(_loud_pcm(0.3), STT_RATE)
    eq("start.preroll_ms", at_start.get("preroll_ms"), 0.0)
    eq("start.preroll_bytes", at_start.get("preroll_bytes"), 0)
    eq("start.lead_kept", at_start.get("lead_kept"), True)
    failed = [(n, a, e) for n, a, e, g in rows if not g]
    if failed:
        raise AssertionError("mismatches: " + "; ".join(
            "%s actual=%r expected=%r" % (n, a, e) for n, a, e in failed))
    return True


def _legacy_resample_pcm16_mono(pcm: bytes, src_rate: int,
                                dst_rate: int = STT_RATE) -> bytes:
    """iter5 whole-segment linear resample. Oracle only — not production."""
    import struct as _st
    src_rate = int(src_rate) or dst_rate
    dst_rate = int(dst_rate) or src_rate
    if not pcm or src_rate == dst_rate:
        return pcm
    n_src = len(pcm) // 2
    if n_src <= 0:
        return pcm
    src = _st.unpack("<%dh" % n_src, pcm[: n_src * 2])
    n_dst = max(1, int(round(n_src * dst_rate / float(src_rate))))
    out = bytearray(n_dst * 2)
    for i in range(n_dst):
        pos = i * src_rate / float(dst_rate)
        i0 = int(pos)
        frac = pos - i0
        s0 = src[i0] if i0 < n_src else 0
        s1 = src[i0 + 1] if (i0 + 1) < n_src else s0
        _st.pack_into("<h", out, i * 2, int(s0 + (s1 - s0) * frac))
    return bytes(out)


def test_streaming_resample_parity_and_stt_chunks():
    """Streaming native->STT resample == iter5 whole-segment; STT gets chunks.

    Isolates the GEM stage-5 PARTIAL: post-VAD resample was one blocking
    whole-segment call. Prints ROW actual vs expected on mismatch. No skip.
    """
    rows = []

    def eq(name, actual, expected):
        good = actual == expected
        rows.append((name, actual, expected, good))
        if not good:
            print("ROW %s actual=%r expected=%r" % (name, actual, expected),
                  flush=True)
        return good

    src_rate = 48000
    pcm = _loud_pcm(2.0, src_rate)
    vad = energy_vad(pcm, src_rate)
    speech = vad["pcm"]
    eq("vad.speech", vad.get("speech"), True)
    eq("silence_not_in_slice",
       energy_vad(b"\x00\x00" * 4800, src_rate).get("speech"), False)

    legacy = _legacy_resample_pcm16_mono(speech, src_rate, STT_RATE)
    streamed = b"".join(_resample_chunks(speech, src_rate, STT_RATE))
    via_api = resample_pcm16_mono(speech, src_rate, STT_RATE)
    eq("parity.stream_eq_legacy", streamed == legacy, True)
    eq("parity.api_eq_legacy", via_api == legacy, True)
    eq("parity.len", len(streamed), len(legacy))

    # Time the iter5 blocking resample vs first streamed dest frame.
    whole_ms = []
    for _ in range(5):
        t0 = time.perf_counter()
        _legacy_resample_pcm16_mono(speech, src_rate, STT_RATE)
        whole_ms.append((time.perf_counter() - t0) * 1000.0)
    t_whole = min(whole_ms)

    first_ms = []
    step = _frame_bytes(src_rate)
    for _ in range(5):
        t0 = time.perf_counter()
        got = next(_resample_chunks(speech[:step], src_rate, STT_RATE))
        first_ms.append((time.perf_counter() - t0) * 1000.0)
        assert got  # first frame must emit dest bytes
    t_first = min(first_ms)

    stt = FakeTranscriber("status")
    rec = vad_interrupt(pcm, src_rate, transcribe=stt.transcribe)
    joined = b"".join(stt.chunks)
    n_chunks = rec.get("resample_chunks")
    chunk_b = rec.get("resample_chunk_bytes")
    handoff = rec.get("handoff_ms")

    print("MEASURE whole_resample_ms=%.3f first_frame_ms=%.3f "
          "handoff_ms=%s chunks=%s chunk_bytes=%s dest_bytes=%s "
          "parity=%s stt_incremental=%s" % (
              t_whole, t_first, handoff, n_chunks, chunk_b, len(joined),
              joined == legacy, len(stt.chunks) > 1), flush=True)

    eq("stt.chunks_gt_1", len(stt.chunks) > 1, True)
    eq("stt.joined_eq_legacy", joined == legacy, True)
    eq("rec.chunks_gt_1", isinstance(n_chunks, int) and n_chunks > 1, True)
    eq("rec.chunk_bytes", chunk_b, step)
    eq("rec.chunk_bytes_bound", chunk_b, max(2, int(src_rate * VAD_FRAME_MS / 1000.0) * 2))
    eq("rec.handoff_is_ms", isinstance(handoff, (int, float)), True)
    eq("rec.handoff_lt_whole",
       isinstance(handoff, (int, float)) and handoff < t_whole, True)
    eq("first_frame_lt_whole", t_first < t_whole, True)
    eq("rec.rate_stt", rec.get("rate"), STT_RATE)
    eq("rec.transcript", rec.get("transcript"), "status")
    eq("stt.calls_once", len(stt.calls), 1)
    eq("stt.calls_rate", stt.calls[-1][1], STT_RATE)
    # Silence is never resampled: 48 kHz quiet stays native.
    silent = vad_interrupt(b"\x00\x00" * 4800, src_rate, transcribe=stt.transcribe)
    eq("silence.rate_native", silent.get("rate"), src_rate)
    eq("silence.chunks", silent.get("resample_chunks"), 0)
    eq("silence.handoff", silent.get("handoff_ms"), None)

    failed = [(n, a, e) for n, a, e, g in rows if not g]
    if failed:
        raise AssertionError("mismatches: " + "; ".join(
            "%s actual=%r expected=%r" % (n, a, e) for n, a, e in failed))
    return True


def main() -> int:
    check("selftest green log", test_selftest_green_log)
    check("P0 timeout split 8 vs 70", test_timeouts_are_p0)
    check("PULL_CLOCK_ID is 18", test_pull_clock_id_is_18)
    check("consume id18 pull read-only", test_consume_id18)
    check("missing ticket is UNREACHABLE", test_missing_ticket_unreachable)
    check("clock_id 16 is UNREACHABLE", test_wrong_clock_id_unreachable)
    check("core_ready=false is UNREACHABLE", test_core_ready_false_unreachable)
    check("CLOCK_STALE is UNREACHABLE", test_clock_stale_unreachable)
    check("dead Core is UNREACHABLE (no :8791)", test_dead_core_unreachable_after_id18)
    check("phone owner AUDIO_OWNED, no write", test_phone_owner_is_audio_owned_no_write)
    check("energy VAD silence vs speech", test_vad_silence_vs_speech)
    check("VAD interrupt first_word_ms is not GET/coalesce-gated",
          test_vad_interrupt_first_word_not_gated_by_get)
    check("barge-in is interrupt-only: cancel play, no STT POST, no pull write",
          test_barge_in_cancels_playback)
    check("typed say quotes route/rc/brain", test_typed_say_quotes_voice_fields)
    check("PTT turn VAD+STT POSTs transcript (16 kHz bind from 48 kHz)",
          test_ptt_turn_vad_stt_posts_transcript)
    check("PTT silence is STT_NONE", test_ptt_silence_is_stt_none)
    check("unbound STT is STT_NONE", test_unbound_stt_is_stt_none)
    check("resume carries the same sid", test_resume_same_sid)
    check("quote_voice reads model: from sources", test_quote_voice_model_from_sources)
    check("reuse not bloat (no phone/clock/kernel fork)", test_reuse_not_bloat)
    check("idle tick heartbeats, mic idle, no pull write",
          test_idle_tick_heartbeats_mic_idle)
    check("dead Core say-tick heartbeats UNREACHABLE (no sid, no :8791)",
          test_dead_core_say_tick_heartbeats_unreachable)
    check("tick does not PTT unless asked", test_tick_does_not_ptt_without_flag)
    check("cvm_dt.py voice --selftest rc=0", test_cvm_dt_voice_subcommand_selftest)
    check("voice_main --selftest rc=0", test_voice_main_selftest_rc0)
    check("make_dt is the one constructor", test_make_dt_is_the_constructor)
    check("VOSK binds when model dir is present (not just STT_NONE)",
          test_vosk_binds_when_model_present)
    check("REAL Service POST /api/v1/voice quotes route/rc/brain",
          test_real_service_voice_route_fields)
    check("voice_state transitions + fallback-device report (requested vs default)",
          test_voice_state_transitions_and_fallback_report)
    check("COM CoInitializeEx is per-thread; CoUninitialize pairs",
          test_com_init_is_per_thread)
    check("endpoint OPEN on requested ids, or visible fallback+reason (live WASAPI)",
          test_endpoint_open_and_fallback_report)
    check("STT_NONE completion -> voice_state=unavailable, no false transcript",
          test_stt_none_completion_unavailable)
    check("streaming resample byte-identical to whole-segment; STT gets chunks",
          test_streaming_resample_parity_and_stt_chunks)
    failed = [(l, err) for l, ok, err in RESULTS if not ok]
    for label, ok, err in RESULTS:
        print("%s  %s%s" % ("PASS" if ok else "FAIL", label, ("  " + err) if err else ""))
    print("result: %d/%d" % (len(RESULTS) - len(failed), len(RESULTS)))
    print("note: this suite is a green log except the real-Service bind row")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
