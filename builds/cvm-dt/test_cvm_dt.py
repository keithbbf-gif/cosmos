#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest for cvm-dt PR-2 (lease honorer). No live Core required: FakeBackend + a local
HTTP double of /status /control /voice. Refusals asserted BY KIND.

The Motif stage-6 proof is the LIVE `cvm_dt.py gate` run, not this check.
rc=0 here is a green log.
"""
from __future__ import annotations

import ctypes
import json
import os
import struct
import sys
import tempfile
import threading
import time
import uuid
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "cosmos"))

from cosmos_paths import CosmosPaths, write_sentinel  # noqa: E402

from wasapi import (  # noqa: E402
    Endpoint, MixFormat, _pcm16_mono_to_mix, parse_wav_pcm16_mono,
)

from cvm_dt import (  # noqa: E402
    CLIENT_ID, DISPATCH_PROPERTYPUT, DISPATCH_PROPERTYPUTREF, DISPATCH_PUT_ANY,
    FAST_READ_S, PULL_CLOCK_ID, VARIANT_ABI_BYTES, VOICE_READ_S, LEASE_REL,
    AudioLease, CoreClient, CvmDt, CvmDtError, FakeBackend, RefusalKind,
    _sapi_wav, load_paths, run_gate, run_selftest, variant_abi_bytes, voice_body,
)

RESULTS = []


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
    tmp = Path(tempfile.mkdtemp(prefix="cvm-dt-test-"))
    write_sentinel(tmp, "KMesh-COSMOS-live")
    (tmp / "config").mkdir()
    (tmp / "state").mkdir()
    (tmp / "config" / "api_token.txt").write_text("test-token", encoding="utf-8")
    return tmp


# ---------------- HTTP double of Core (not a second COSMOS) ----------------
class _FakeCore(BaseHTTPRequestHandler):
    minted = None
    token = "test-token"
    blocked = False

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
            return self._send(200, {"ready": True, "tree_id": "KMesh-COSMOS-live",
                                    "root": "scratch",
                                    "ledger_head": {"seq": 321, "event": "VOICE_BRAIN"}})
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
        if self.path == "/api/v1/voice":
            if self.blocked:
                return self._send(200, {
                    "ok": False, "session_id": d.get("session_id"),
                    "kind": "refused", "reply": "[CONTROL_BLOCKED]",
                    "spoken": "Voice is paused.", "needs_confirm": False,
                    "confirm_id": None, "action": None, "sources": [],
                    "refused": True, "error": "CONTROL_BLOCKED"})
            sid = str(d.get("session_id") or "") or uuid.uuid4().hex
            _FakeCore.minted = sid
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


def _write_ticket(root, audio_owner="none", **extra):
    p = Path(root) / "state" / "cvm" / "pull.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    d = {
        "cvm": 1,
        "tree_id": "KMesh-COSMOS-live",
        "issued_epoch": time.time(),
        "pull": True,
        "audio_owner": audio_owner,
        "clock_id": PULL_CLOCK_ID,
        "kinds": ["voice_session", "device", "notifications"],
    }
    d.update(extra)
    p.write_text(json.dumps(d), encoding="utf-8")
    return p


def _dt(root, base, none=False, arm=False):
    paths = CosmosPaths(root)
    lease = AudioLease(paths.state(*LEASE_REL), paths.sentinel.tree_id)
    return CvmDt(paths, CoreClient(base, "test-token"),
                 FakeBackend(none=none), lease, arm=arm)


# ---------------- cases ----------------
def test_selftest_green_log():
    rec = run_selftest()
    lv = rec["live_value"]
    return (rec["selftest"] == "ok" and lv["AUDIO_NONE"] == "AUDIO_NONE"
            and lv["wrote_owner"] is False)


def test_timeouts_are_the_p0_split():
    return FAST_READ_S == 8.0 and VOICE_READ_S == 70.0 and VOICE_READ_S > FAST_READ_S


def test_voice_body_resume_carries_sid():
    a = voice_body("status")
    b = voice_body("help", session_id="abcd" * 8)
    return "session_id" not in a and b["session_id"] == "abcd" * 8 and b["client_id"] == CLIENT_ID


@expect(RefusalKind.AUDIO_NONE)
def test_missing_default_is_audio_none():
    FakeBackend(none=True).probe()


def test_no_write_surface():
    return (not hasattr(AudioLease, "acquire")
            and not hasattr(AudioLease, "release")
            and not hasattr(AudioLease, "_write"))


def test_lease_rel_is_pull_ticket():
    return LEASE_REL == ("cvm", "pull.json")


def test_audio_owned_by_other_backs_off():
    tmp = _scratch()
    p = _write_ticket(tmp, "phone", AUDIO_OWNER="AUDIO_OWNED", owner="phone")
    before = p.read_bytes()
    dt = _dt(tmp, "http://127.0.0.1:1")
    try:
        dt.ensure_can_speak()
        return False
    except CvmDtError as e:
        return e.kind == RefusalKind.AUDIO_OWNED and p.read_bytes() == before


def test_dt_never_writes_owner():
    tmp = _scratch()
    pull = _write_ticket(tmp, "desktop")
    before = pull.read_bytes()
    httpd = _serve()
    base = "http://127.0.0.1:%d" % httpd.server_address[1]
    try:
        dt = _dt(tmp, base)
        dt.ask("status", speak=False)
        dt.listen(0.05)
        dt.close()
        audio_json = Path(tmp) / "state" / "cvm" / "audio.json"
        return pull.read_bytes() == before and not audio_json.exists()
    finally:
        httpd.shutdown()


def test_unclaimed_sink_unarmed_refuses():
    """CVM_ARCH §6.2: owner=none is DT's ONLY with an explicit arm."""
    tmp = _scratch()
    p = _write_ticket(tmp, "none")
    before = p.read_bytes()
    try:
        _dt(tmp, "http://127.0.0.1:1").ensure_can_speak()
        return False
    except CvmDtError as e:
        return e.kind == RefusalKind.AUDIO_UNARMED and p.read_bytes() == before


def test_audio_none_ticket_allows_when_armed():
    tmp = _scratch()
    p = _write_ticket(tmp, "none")
    before = p.read_bytes()
    rec = _dt(tmp, "http://127.0.0.1:1", arm=True).ensure_can_speak()
    return (rec["AUDIO_OWNER"] == "AUDIO_NONE"
            and rec["audio_owner"] == "none"
            and p.read_bytes() == before)


def test_missing_ticket_is_audio_none_and_silent_on_disk():
    tmp = _scratch()
    rec = _dt(tmp, "http://127.0.0.1:1", arm=True).ensure_can_speak()
    audio_json = Path(tmp) / "state" / "cvm" / "audio.json"
    pull = Path(tmp) / "state" / "cvm" / "pull.json"
    return (rec["AUDIO_OWNER"] == "AUDIO_NONE"
            and not audio_json.exists()
            and not pull.exists())


def test_audio_owned_desktop_allows():
    tmp = _scratch()
    p = _write_ticket(tmp, "desktop", AUDIO_OWNER="AUDIO_OWNED", owner="desktop")
    before = p.read_bytes()
    rec = _dt(tmp, "http://127.0.0.1:1").ensure_can_speak()
    return (rec["owner"] == "desktop"
            and rec["AUDIO_OWNER"] == "AUDIO_OWNED"
            and p.read_bytes() == before)


def test_unknown_owner_is_audio_owned():
    tmp = _scratch()
    p = _write_ticket(tmp, "both")
    before = p.read_bytes()
    dt = _dt(tmp, "http://127.0.0.1:1")
    try:
        dt.ensure_can_speak()
        return False
    except CvmDtError as e:
        return e.kind == RefusalKind.AUDIO_OWNED and p.read_bytes() == before


def test_paths_refuse_nonsentinel():
    tmp = Path(tempfile.mkdtemp())
    try:
        load_paths(tmp)
        return False
    except CvmDtError as e:
        return e.kind in (RefusalKind.ROOT_MISSING, RefusalKind.IDENTITY_MISMATCH)


def test_voice_resume_same_sid_against_http_double():
    tmp = _scratch()
    httpd = _serve()
    base = "http://127.0.0.1:%d" % httpd.server_address[1]
    try:
        dt = _dt(tmp, base, arm=True)
        mint = dt.ask("status", speak=False)
        sid = mint["session_id"]
        nxt = dt.resume(sid, "help", speak=False)
        return sid and sid == nxt["session_id"] and len(sid) == 32
    finally:
        httpd.shutdown()


def test_control_blocked_is_typed():
    tmp = _scratch()
    httpd = _serve()
    base = "http://127.0.0.1:%d" % httpd.server_address[1]
    _FakeCore.blocked = True
    try:
        dt = _dt(tmp, base, arm=True)
        dt.ask("status", speak=False)
        return False
    except CvmDtError as e:
        return e.kind == RefusalKind.CONTROL_BLOCKED
    finally:
        _FakeCore.blocked = False
        httpd.shutdown()


def test_unreachable_is_typed():
    tmp = _scratch()
    dt = _dt(tmp, "http://127.0.0.1:1")
    try:
        dt.honor_control()
        return False
    except CvmDtError as e:
        return e.kind == RefusalKind.UNREACHABLE


def test_isolated_gate_quotes_sid_and_device():
    """Isolated gate against FakeBackend + HTTP double. NOT Motif stage 6."""
    tmp = _scratch()
    httpd = _serve()
    base = "http://127.0.0.1:%d" % httpd.server_address[1]
    proof = tmp / "STAGE6_GATE.json"
    try:
        _write_ticket(tmp, "desktop")
        rec = run_gate(tmp, base, proof_path=str(proof), audio=FakeBackend(),
                       speak=False)
        lv = rec["live_value"]
        return (
            rec["ok"] is True
            and lv["audio_owner"] == "desktop"
            and lv["device_name"] == "Headphones (FAKE HT3)"
            and lv["device_name_matches_windows_default"] is True
            and lv["session_id"] == lv["resume_session_id"]
            and lv["session_resumed_same_sid"] is True
            and rec["emitted"].startswith("cvm-dt:KMesh-COSMOS-live:")
            and proof.is_file()
        )
    finally:
        httpd.shutdown()


class _DriftBackend(FakeBackend):
    """Default flipped under the gate: opened endpoint != Windows default."""

    def windows_default(self):
        return Endpoint("render", "console", "other-id", "Speakers (OTHER)", False)


def test_gate_reads_windows_default_independently():
    """A self-compared probe would report match=True. It must not."""
    tmp = _scratch()
    httpd = _serve()
    base = "http://127.0.0.1:%d" % httpd.server_address[1]
    proof = tmp / "GATE_DRIFT.json"
    try:
        _write_ticket(tmp, "desktop")
        rec = run_gate(tmp, base, proof_path=str(proof), audio=_DriftBackend(),
                       speak=False)
        lv = rec["live_value"]
        return (
            lv["device_name_matches_windows_default"] is False
            and lv["windows_default_name"] == "Speakers (OTHER)"
            and lv["device_name"] == "Headphones (FAKE HT3)"
            and lv["session_resumed_same_sid"] is True
            and rec["ok"] is False
        )
    finally:
        httpd.shutdown()


def test_isolated_gate_audio_none_still_resumes_sid():
    tmp = _scratch()
    httpd = _serve()
    base = "http://127.0.0.1:%d" % httpd.server_address[1]
    proof = tmp / "GATE_NONE.json"
    try:
        rec = run_gate(tmp, base, proof_path=str(proof),
                       audio=FakeBackend(none=True), speak=False)
        lv = rec["live_value"]
        audio_json = tmp / "state" / "cvm" / "audio.json"
        return (
            rec["ok"] is True
            and lv["AUDIO_NONE"] == "AUDIO_NONE"
            and lv["audio_owner"] == "none"
            and lv["session_resumed_same_sid"] is True
            and not audio_json.exists()
        )
    finally:
        httpd.shutdown()


# ---- mouth ABI: the two defects that made DT mute (measured 2026-08-30) ----
def test_variant_is_tagvariant_width():
    """A short VARIANT misaligns rgvarg[1]: DISP_E_BADVARTYPE on 2-arg Invoke."""
    return (variant_abi_bytes() == VARIANT_ABI_BYTES
            == 8 + 2 * ctypes.sizeof(ctypes.c_void_p))


def test_property_put_mask_covers_putref():
    """PUTREF is 8; a `flags & DISPATCH_PROPERTYPUT` guard skips its named
    DISPID and SAPI answers DISP_E_PARAMNOTFOUND. Both puts must match."""
    return (bool(DISPATCH_PROPERTYPUT & DISPATCH_PUT_ANY)
            and bool(DISPATCH_PROPERTYPUTREF & DISPATCH_PUT_ANY)
            and not (DISPATCH_PROPERTYPUTREF & DISPATCH_PROPERTYPUT))


def test_sapi_synthesizes_a_real_wav():
    """Runtime bind of the mouth: SAPI must emit PCM this machine can play.

    Windows has no excuse — a typed TTS_NONE is only acceptable off-Windows.
    """
    try:
        wav = _sapi_wav("cosmos desktop voice")
    except CvmDtError as e:
        return os.name != "nt" and e.kind == RefusalKind.TTS_NONE
    pcm, rate = parse_wav_pcm16_mono(wav)
    return (wav[:4] == b"RIFF" and wav[8:12] == b"WAVE"
            and len(wav) > 44 and len(pcm) > 0 and rate > 0)


def _reference_pcm16_mono_to_mix(pcm, src_rate, mix):
    """The per-frame writer the bulk converter replaced. Golden model only."""
    if not pcm:
        return b""
    n_src = len(pcm) // 2
    src = memoryview(pcm).cast("h")
    n_dst = max(1, int(round(n_src * mix.rate / float(src_rate))))
    frames = bytearray(n_dst * mix.block_align)
    for i in range(n_dst):
        pos = i * src_rate / float(mix.rate)
        i0 = int(pos)
        s0 = src[i0] if i0 < n_src else 0
        s1 = src[i0 + 1] if (i0 + 1) < n_src else s0
        sample = s0 + (s1 - s0) * (pos - i0)
        off = i * mix.block_align
        if mix.is_float:
            packed = struct.pack("<f", max(-1.0, min(1.0, sample / 32768.0)))
            for ch in range(mix.channels):
                frames[off + ch * 4:off + ch * 4 + 4] = packed
        else:
            packed = struct.pack("<h", int(max(-32768, min(32767, sample))))
            bps = mix.bits // 8
            for ch in range(mix.channels):
                frames[off + ch * bps:off + ch * bps + 2] = packed
    return bytes(frames)


def test_mix_conversion_is_byte_identical_to_the_per_frame_writer():
    """Faster is only an improvement if it is the SAME audio (all four paths)."""
    shapes = (
        (22050, MixFormat(2, 48000, 32, True, 8, b"")),    # resample + stereo f32
        (16000, MixFormat(2, 16000, 32, True, 8, b"")),    # equal-rate fast path
        (44100, MixFormat(1, 48000, 16, False, 2, b"")),   # mono int16
        (8000, MixFormat(2, 48000, 32, False, 8, b"")),    # exotic 4-byte slots
    )
    pcm = b"".join(struct.pack("<h", (i * 977) % 65536 - 32768) for i in range(1500))
    for src_rate, mix in shapes:
        if _pcm16_mono_to_mix(pcm, src_rate, mix) != _reference_pcm16_mono_to_mix(
                pcm, src_rate, mix):
            return False
    return _pcm16_mono_to_mix(b"", 16000, shapes[0][1]) == b""


def main() -> int:
    check("selftest green log", test_selftest_green_log)
    check("P0 timeout split 8 vs 70", test_timeouts_are_the_p0_split)
    check("voice body resume carries sid", test_voice_body_resume_carries_sid)
    check("missing default is AUDIO_NONE", test_missing_default_is_audio_none)
    check("no owner-write surface", test_no_write_surface)
    check("lease path is pull.json", test_lease_rel_is_pull_ticket)
    check("AUDIO_OWNED by other backs off", test_audio_owned_by_other_backs_off)
    check("DT never writes the owner", test_dt_never_writes_owner)
    check("unclaimed sink unarmed refuses AUDIO_UNARMED", test_unclaimed_sink_unarmed_refuses)
    check("AUDIO_NONE ticket allows when armed", test_audio_none_ticket_allows_when_armed)
    check("missing ticket is AUDIO_NONE, no files", test_missing_ticket_is_audio_none_and_silent_on_disk)
    check("AUDIO_OWNED desktop allows without write", test_audio_owned_desktop_allows)
    check("unknown owner is AUDIO_OWNED", test_unknown_owner_is_audio_owned)
    check("paths refuse nonsentinel", test_paths_refuse_nonsentinel)
    check("voice resume same sid (http double)", test_voice_resume_same_sid_against_http_double)
    check("CONTROL_BLOCKED typed", test_control_blocked_is_typed)
    check("UNREACHABLE typed", test_unreachable_is_typed)
    check("isolated gate quotes sid+device", test_isolated_gate_quotes_sid_and_device)
    check("gate reads the Windows default independently",
          test_gate_reads_windows_default_independently)
    check("isolated gate AUDIO_NONE + sid", test_isolated_gate_audio_none_still_resumes_sid)
    check("VARIANT is tagVARIANT width", test_variant_is_tagvariant_width)
    check("property-put mask covers PUTREF", test_property_put_mask_covers_putref)
    check("SAPI synthesizes a real WAV", test_sapi_synthesizes_a_real_wav)
    check("mix conversion is byte-identical",
          test_mix_conversion_is_byte_identical_to_the_per_frame_writer)
    failed = [(l, err) for l, ok, err in RESULTS if not ok]
    for label, ok, err in RESULTS:
        print("%s  %s%s" % ("PASS" if ok else "FAIL", label, ("  " + err) if err else ""))
    print("result: %d/%d" % (len(RESULTS) - len(failed), len(RESULTS)))
    print("note: this suite is a green log, not Motif stage 6")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
