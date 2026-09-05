#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cvm-dt VOICE — desktop ear/mouth on the existing Core voice seam.

Wishlist #2 (docs/WISHLIST.md, docs/arch/DT_CVM.md): a PC voice client that
uses the same WASAPI default device as the phone (the TOZO the moment
Windows owns it). One path:

    WASAPI default probe (quoted every tick)
         -> explicit PTT (space/enter on the idle loop, or --ptt)
         -> hangover capture -> native-rate energy VAD -> stream-resample
            speech frames to 16 kHz (silence never resampled; STT is fed
            incrementally; first-word is VAD-event, not idle-GET)
         -> POST /api/v1/voice  (CvmDt.ask; same convo/itc seam)
         -> SAPI + WASAPI play; VAD ear is interrupt-only (PlaybackGate cancel)

Consumes DesktopPullClock state (PULL_CLOCK_ID=18) READ-ONLY. Never writes
pull.json / audio.json. Dead Core / core_ready=false / CLOCK_STALE / wrong
clock_id -> typed UNREACHABLE (fail closed; never :8791). Voice is not a
clock: heartbeat worker=cvm-dt-voice quotes consumed clock_id, does not
issue one.

    py -3.14 builds\\cvm-dt\\cvm_dt.py voice --selftest
    py -3.14 builds\\cvm-dt\\cvm_dt.py voice --root <RUNTIME> [--once|--ptt|--say]
    py -3.14 builds\\cvm-dt\\test_cvm_dt_voice.py

rc=0 is not the gate. Quote live_value.clock_id, mic_state, stt_kind, and
the selected WASAPI device_name (plus route/rc/brain on a real POST).
"""
from __future__ import annotations

import argparse
import json
import os
import struct
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Any, Optional, Protocol

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
_COSMOS_LIB = Path(__file__).resolve().parents[2] / "cosmos"
if _COSMOS_LIB.is_dir() and str(_COSMOS_LIB) not in sys.path:
    sys.path.insert(0, str(_COSMOS_LIB))

from cosmos_clock import (  # noqa: E402
    acquire_lock, heartbeat_age_s, pid_alive, plan_create, pythonw_exe,
    query_task, read_heartbeat, tr_cmdline, write_heartbeat,
)
from cosmos_cvm_push import (  # noqa: E402
    PULL_CLOCK_ID, VOICE_READY, VOICE_TRANSCRIBING, VOICE_UNAVAILABLE,
    PlaybackGate, ack_listening, ack_stt_none, probe_stt as probe_vosk,
    set_voice_state, voice_state,
)
from cosmos_paths import CosmosPaths  # noqa: E402

from wasapi import (  # noqa: E402
    ENDPOINTS_NAME, PREROLL_MS, AudioNoneError, bind_persist, pcm16_rms,
    quote_route, route_status,
)
from cvm_dt import (  # noqa: E402
    BUILD as DT_BUILD, CLIENT_ID, FAST_READ_S, LEASE_REL, LEASE_TTL_S,
    ROAD_KINDS, VOICE_READ_S, AudioLease, CoreClient, CvmDt, CvmDtError,
    FakeBackend, RefusalKind, make_dt,
)

WIRE = "cvm-dt-voice/1"
VOICE_ROUTE = "/api/v1/voice"
TITLE = "cvm-dt-voice"
HEARTBEAT_NAME = "cvm_dt_voice_heartbeat.json"
WORKER = "cvm-dt-voice"
# Daemon vehicle. Absent until 2026-08-30: voice had no task name, no lock and
# no --register, so NOTHING in the repo could ever schedule it. Its heartbeat
# froze 2026-08-27T09:59 after a one-shot and no clock existed to run it again
# (CLOCK_POSTMORTEM.md). Mirrors cvm_dt_clock; emits, never registers.
TASK_NAME = "COSMOS CVM DT Voice"
TASK_NAME_LOGON = "COSMOS CVM DT Voice Logon"
LOCK_NAME = "cvm_dt_voice.lock"
OUT_NAME = "cvm_dt_voice.out"
FRESH_S = 60.0
VOICE_IDLE_S = 2.0
MIC_IDLE = "idle"
MIC_PTT = "ptt"
STT_RATE = 16000
VAD_FRAME_MS = 30
VAD_THRESHOLD = 400.0
VAD_MIN_SPEECH_MS = 80.0
VAD_HANGOVER_MS = 200.0
_DEV_KEYS = (
    "device_name", "capture_name", "device_id", "input_device_id",
    "output_device_id", "capture_opened_requested", "render_opened_requested",
    "capture_opened_on", "render_opened_on", "capture_fallback", "render_fallback",
    "capture_fallback_reason", "render_fallback_reason",
)


class Transcriber(Protocol):
    def transcribe(self, pcm: bytes, rate: int) -> dict: ...


class FakeTranscriber:
    """Injected STT for selftest — never touches a model or a network."""

    def __init__(self, text: str = "status"):
        self.text = text
        self.calls: list[tuple[int, int]] = []
        self.chunks: list[bytes] = []
        self._done = False

    def accept(self, pcm: bytes, rate: int = STT_RATE) -> None:
        if self._done:
            self.chunks, self._done = [], False
        if pcm:
            self.chunks.append(pcm)

    def finish(self) -> dict:
        self._done = True
        pcm = b"".join(self.chunks)
        self.calls.append((len(pcm), STT_RATE))
        return {"transcript": self.text, "engine": "fake", "ear_ms": 0.0}

    def transcribe(self, pcm: bytes, rate: int) -> dict:
        if not self.chunks and pcm:
            self.accept(pcm, rate)
        return self.finish()


def _frame_bytes(rate: int) -> int:
    n = max(2, int(int(rate) * VAD_FRAME_MS / 1000.0) * 2)
    return n - (n & 1)


def _resample_chunks(pcm: bytes, src_rate: int, dst_rate: int = STT_RATE,
                     frame_bytes: int = 0):
    """Yield dest PCM16 frames. Same samples as whole-segment linear resample."""
    sr = int(src_rate) or int(dst_rate) or STT_RATE
    dr = int(dst_rate) or sr
    step = int(frame_bytes) or _frame_bytes(sr)
    if not pcm:
        return
    if sr == dr:
        for off in range(0, len(pcm), step):
            yield pcm[off:off + step]
        return
    src: list[int] = []
    idx = off = 0
    n = len(pcm)
    while off < n:
        piece = pcm[off:off + step]
        off += step
        if len(piece) >= 2:
            k = len(piece) // 2
            src.extend(struct.unpack("<%dh" % k, piece[:k * 2]))
        n_src = len(src)
        n_dst = max(1, int(round(n_src * dr / float(sr)))) if n_src else 0
        flush = off >= n
        out = bytearray()
        while idx < n_dst:
            pos = idx * sr / float(dr)
            i0 = int(pos)
            if not flush and i0 + 1 >= n_src:
                break
            s0 = src[i0] if i0 < n_src else 0
            s1 = src[i0 + 1] if (i0 + 1) < n_src else s0
            out += struct.pack("<h", int(s0 + (s1 - s0) * (pos - i0)))
            idx += 1
        if out:
            yield bytes(out)


def resample_pcm16_mono(pcm: bytes, src_rate: int,
                        dst_rate: int = STT_RATE) -> bytes:
    """Linear resample PCM16 mono to the STT rate. No-op if rates match."""
    sr = int(src_rate) or dst_rate
    dr = int(dst_rate) or sr
    if not pcm or sr == dr or len(pcm) < 2:
        return pcm
    return b"".join(_resample_chunks(pcm, sr, dr))


def energy_vad(pcm: bytes, rate: int = STT_RATE, *,
               frame_ms: int = VAD_FRAME_MS,
               threshold: float = VAD_THRESHOLD,
               min_speech_ms: float = VAD_MIN_SPEECH_MS,
               hangover_ms: float = VAD_HANGOVER_MS,
               preroll_ms: float = PREROLL_MS) -> dict:
    """Local energy VAD. Speech slice includes preroll so command start is kept."""
    rate = int(rate) or STT_RATE
    frame_n = max(1, int(rate * float(frame_ms) / 1000.0))
    frame_bytes = frame_n * 2
    hang_frames = max(0, int(float(hangover_ms) / float(frame_ms)))
    speech_ms = 0.0
    voiced = hang = n_frames = 0
    first = last = None
    i = 0
    while i + frame_bytes <= len(pcm):
        rms = pcm16_rms(pcm[i:i + frame_bytes])
        if rms >= float(threshold):
            if first is None:
                first = n_frames
            last = n_frames
            voiced += 1
            hang = hang_frames
            speech_ms += float(frame_ms)
        elif hang > 0:
            hang -= 1
            voiced += 1
            speech_ms += float(frame_ms)
            last = n_frames
        n_frames += 1
        i += frame_bytes
    if n_frames == 0 and pcm:
        speech_ms = (len(pcm) / 2) * 1000.0 / rate if pcm16_rms(pcm) >= threshold else 0.0
        voiced = 1 if speech_ms else 0
        n_frames = 1
        if voiced:
            first = last = 0
    speech = speech_ms >= float(min_speech_ms) and voiced > 0
    preroll_frames = max(0, int(float(preroll_ms) / float(frame_ms)))
    start_frame = 0 if first is None else max(0, int(first) - preroll_frames)
    end_frame = n_frames if last is None else min(n_frames, int(last) + 1)
    start_byte = start_frame * frame_bytes
    end_byte = min(len(pcm), end_frame * frame_bytes) if frame_bytes else len(pcm)
    first_voiced_ms = None if first is None else round(first * float(frame_ms), 1)
    start_ms = round(start_frame * float(frame_ms), 1)
    kept_ms = 0.0 if first is None else round((first_voiced_ms or 0) - start_ms, 1)
    kept_b = 0 if first is None else max(0, int(first) * frame_bytes - start_byte)
    return {
        "speech": bool(speech), "engine": "energy",
        "rms": round(pcm16_rms(pcm), 3), "speech_ms": round(speech_ms, 1),
        "frames": n_frames, "rate": rate, "pcm_bytes": len(pcm),
        "pcm": pcm[start_byte:end_byte] if speech else b"",
        "start_ms": start_ms, "first_voiced_ms": first_voiced_ms,
        "preroll_ms": kept_ms, "preroll_bytes": kept_b,
        "lead_kept": first_voiced_ms is None or start_ms <= first_voiced_ms,
    }


def vad_interrupt(pcm: bytes, rate: int = STT_RATE, *,
                  gate: Optional[PlaybackGate] = None,
                  transcribe=None) -> dict:
    """Native-rate VAD -> stream-resample speech frames -> STT. No HTTP/GET."""
    t0 = time.perf_counter()
    rate = int(rate) or STT_RATE
    vad = energy_vad(pcm, rate)
    out = {"vad_event": vad["speech"], "speech": vad["speech"],
           "barge_in": False, "cancel_ms": None, "first_word_ms": None,
           "stt_kind": "STT_NONE", "transcript": "", "engine": None,
           "vad": vad, "rate": rate, "lead_kept": bool(vad.get("lead_kept")),
           "usable": False, "resample_chunks": 0, "handoff_ms": None,
           "resample_chunk_bytes": _frame_bytes(rate)}
    if not vad["speech"]:
        return out
    if gate is not None and gate.playing:
        out["cancel_ms"] = gate.cancel()
        out["barge_in"] = True
        out["stt_kind"] = "interrupt"
        out["first_word_ms"] = round((time.perf_counter() - t0) * 1000.0, 3)
        return out
    speech = vad.get("pcm") or b""
    obj = getattr(transcribe, "__self__", None) if transcribe else None
    sink = (obj if obj is not None and hasattr(obj, "accept")
            else getattr(obj, "transcriber", None) if obj is not None else None)
    acc = getattr(sink, "accept", None) if sink else None
    chunks: list[bytes] = []
    t_vad = time.perf_counter()
    for got in _resample_chunks(speech, rate, STT_RATE):
        chunks.append(got)
        if out["handoff_ms"] is None:
            out["handoff_ms"] = round((time.perf_counter() - t_vad) * 1000.0, 3)
        if acc:
            acc(got, STT_RATE)
    pcm_stt = b"".join(chunks)
    out["resample_chunks"] = len(chunks)
    if rate != STT_RATE:
        out["rate"] = rate = STT_RATE
    if transcribe is not None:
        fin = getattr(sink, "finish", None) if acc else None
        stt = (fin() if callable(fin) else transcribe(pcm_stt, rate)) or {}
        out["transcript"] = str(stt.get("transcript") or "")
        out["engine"] = stt.get("engine")
        out["ear_ms"] = stt.get("ear_ms")
        out["stt_kind"] = "ok" if out["transcript"] else "STT_NONE"
    out["first_word_ms"] = round((time.perf_counter() - t0) * 1000.0, 3)
    out["usable"] = bool(out["transcript"])
    if out["stt_kind"] == "ok":
        set_voice_state(VOICE_READY)
    else:
        out.update(ack_stt_none())
    return out


class VoskTranscriber:
    """Optional on-box STT. Nothing that can run out. Fail-closed if unbound."""

    def __init__(self, model_path: str):
        self.model_path = model_path
        self._model = self._rec = None
        self._rate, self._t0 = STT_RATE, 0.0

    def accept(self, pcm: bytes, rate: int = STT_RATE) -> None:
        try:
            from vosk import KaldiRecognizer, Model, SetLogLevel
        except ImportError as e:
            raise CvmDtError(RefusalKind.STT_NONE, "vosk not importable") from e
        SetLogLevel(-1)
        rate = int(rate) or STT_RATE
        if self._model is None:
            self._model = Model(self.model_path)
        if self._rec is None:
            self._rec = KaldiRecognizer(self._model, rate)
            self._rate, self._t0 = rate, time.perf_counter()
        if pcm:
            self._rec.AcceptWaveform(pcm)

    def finish(self) -> dict:
        rec, self._rec = self._rec, None
        got: dict = {}
        if rec is not None:
            try:
                got = json.loads(rec.FinalResult() or "{}")
            except ValueError:
                got = {}
        text = str(got.get("text") or "").strip()
        if rec is None or not text:
            raise CvmDtError(RefusalKind.STT_NONE,
                             "vosk returned empty transcript")
        return {"transcript": text, "engine": "vosk", "rate": self._rate,
                "ear_ms": round((time.perf_counter() - self._t0) * 1000.0, 3)}

    def transcribe(self, pcm: bytes, rate: int) -> dict:
        self.accept(pcm, rate)
        return self.finish()


def default_transcriber() -> Optional[Transcriber]:
    p = probe_vosk()
    return VoskTranscriber(str(p["model"])) if p.get("ok") else None


def quote_voice(out: dict, *, rc: Optional[int] = None) -> dict:
    """Quote route/rc/brain/model:<name> from a /api/v1/voice response."""
    sources = out.get("sources") or []
    model = None
    for s in sources:
        if isinstance(s, str) and s.startswith("model:"):
            model = s[6:] or None
            break
    try:
        http = int(out["_http"]) if "_http" in out else int(rc if rc is not None else 200)
    except (TypeError, ValueError):
        http = int(rc) if rc is not None else 200
    brain = out.get("brain")
    return {
        "route": VOICE_ROUTE, "rc": http, "ok": out.get("ok"),
        "kind": out.get("kind"), "brain": brain, "model": model or brain,
        "session_id": out.get("session_id"), "served_at": out.get("served_at"),
        "error": out.get("error"), "spoken": out.get("spoken"),
        "refused": out.get("refused"), "brain_note": out.get("brain_note"),
    }


def consume_id18_pull(paths: CosmosPaths, *,
                      ttl_s: float = LEASE_TTL_S,
                      now: Optional[float] = None) -> dict:
    """Read-only consume of DesktopPullClock's ticket. Never writes."""
    path = paths.state(*LEASE_REL)
    if not path.is_file():
        raise CvmDtError(
            RefusalKind.UNREACHABLE,
            "id18 pull.json missing — refusing to invent a ticket")
    lease = AudioLease(path, paths.sentinel.tree_id, ttl_s=ttl_s)
    # AudioLease.read is the sole-writer choke point: a foreign clock_id is
    # UNREACHABLE before any of the ticket's other fields are trusted.
    raw = lease.read()
    cid = int(raw["clock_id"])
    tid = raw.get("tree_id")
    if tid and tid != paths.sentinel.tree_id:
        raise CvmDtError(
            RefusalKind.IDENTITY_MISMATCH,
            "pull ticket tree_id=%r != %r" % (tid, paths.sentinel.tree_id))
    try:
        epoch = float(raw.get("issued_epoch") or raw.get("measured_epoch") or 0.0)
    except (TypeError, ValueError):
        epoch = 0.0
    tnow = float(now if now is not None else time.time())
    if epoch and (tnow - epoch) > float(ttl_s):
        raise CvmDtError(
            RefusalKind.UNREACHABLE,
            "CLOCK_STALE id18 ticket (issued_epoch age > %.0fs)" % ttl_s)
    kind = str(raw.get("core_kind") or "").strip().upper()
    if kind in ROAD_KINDS:
        raise CvmDtError(
            RefusalKind.UNREACHABLE,
            "id18 ticket core_kind=%s" % (raw.get("core_kind"),))
    if raw.get("core_ready") is False:
        raise CvmDtError(
            RefusalKind.UNREACHABLE,
            "id18 ticket core_ready=false")
    view = lease.current()
    view["clock_id"] = cid
    view["voice_client_timeout_s"] = raw.get(
        "voice_client_timeout_s", VOICE_READ_S)
    view["core_ready"] = raw.get("core_ready")
    view["core_kind"] = raw.get("core_kind")
    view["cursor"] = raw.get("cursor")
    view["writer"] = raw.get("writer")
    view["pull_path"] = str(path)
    return view


_AUDIO_NONE_DEV = {
    "device_name": "AUDIO_NONE", "capture_name": "AUDIO_NONE",
    "device_id": "", "input_device_id": "", "output_device_id": "",
    "is_bt": False, "capture_fallback": False, "render_fallback": False,
    "capture_opened_requested": False, "render_opened_requested": False,
    "capture_opened_on": "", "render_opened_on": "",
}


def probe_windows_default() -> dict:
    """Live WASAPI selected vs default, or typed AUDIO_NONE."""
    try:
        return {**route_status(), "kind": "ok"}
    except AudioNoneError:
        return {**_AUDIO_NONE_DEV, "kind": "AUDIO_NONE"}


def wait_for_ptt(interval_s: float) -> bool:
    """Wait up to interval_s. True if space/enter (explicit PTT). Never auto."""
    deadline = time.time() + max(0.0, float(interval_s))
    msvcrt = None
    if os.name == "nt":
        try:
            import msvcrt as _m
            msvcrt = _m
        except ImportError:
            pass
    while time.time() < deadline:
        if msvcrt is not None:
            try:
                if msvcrt.kbhit():
                    ch = msvcrt.getwch()
                    if ch in (" ", "\r", "\n"):
                        return True
                    if ch == "\x03":
                        raise KeyboardInterrupt
            except OSError:
                msvcrt = None
        time.sleep(min(0.05, max(0.0, deadline - time.time())))
    return False


def _print_tick(rec: dict) -> None:
    print(json.dumps({k: rec[k] for k in rec if k != "heartbeat"},
                     indent=1, default=str), flush=True)


class CvmDtVoice:
    """One desktop voice turn over the existing /api/v1/voice seam."""

    def __init__(self, dt: CvmDt, transcriber: Optional[Transcriber] = None):
        self.dt = dt
        self.transcriber = transcriber
        self.last_pull: Optional[dict] = None
        bind_persist(dt.paths.config(ENDPOINTS_NAME))

    def consume_pull(self) -> dict:
        rec = consume_id18_pull(self.dt.paths)
        self.last_pull = rec
        return rec

    def _quote_device(self) -> dict:
        persist = self.dt.paths.config(ENDPOINTS_NAME)
        try:
            if isinstance(self.dt.audio, FakeBackend):
                rec = quote_route(self.dt.probe(), persist)
            else:
                rec = route_status(persist)
        except (AudioNoneError, CvmDtError) as e:
            if isinstance(e, CvmDtError) and e.kind != RefusalKind.AUDIO_NONE:
                raise
            return dict(_AUDIO_NONE_DEV)
        rec.setdefault("device_name", rec.get("render_name"))
        rec.setdefault("device_id", rec.get("output_device_id"))
        return rec

    def _bind_stt(self) -> dict:
        vosk = probe_vosk()
        if self.transcriber is None and vosk.get("ok"):
            self.transcriber = VoskTranscriber(str(vosk["model"]))
        return vosk

    def _transcribe(self, pcm: bytes, rate: int) -> dict:
        stt = self.transcriber
        if stt is None:
            raise CvmDtError(
                RefusalKind.STT_NONE,
                "no local transcriber bound (vosk OVERFLOW until COSMOS_VOSK_MODEL)")
        out = stt.transcribe(pcm, rate)
        text = str((out or {}).get("transcript") or "").strip()
        if not text:
            raise CvmDtError(RefusalKind.STT_NONE, "empty transcript")
        return dict(out)

    def _post(self, transcript: str, *, speak: bool = True,
              barge_pcm: Optional[bytes] = None) -> dict:
        """POST through CvmDt.ask. speak=True arms interrupt-only barge ear."""
        gate = PlaybackGate().arm() if speak else None
        barge: dict = {}
        ear = None
        if speak:
            def _ear():
                pcm, rate = barge_pcm, STT_RATE
                if barge_pcm is None:
                    try:
                        pcm, rate, _ep = self.dt.audio.capture(
                            2.0, hangover_ms=VAD_HANGOVER_MS)
                    except CvmDtError:
                        return
                barge.update(vad_interrupt(pcm or b"", rate, gate=gate))
            ear = threading.Thread(target=_ear, daemon=True)
            ear.start()
        try:
            out = self.dt.ask(transcript, speak=speak, title=TITLE, cancel=gate)
        finally:
            if gate is not None:
                gate.finish()
            if ear is not None:
                ear.join(timeout=2.5)
        out["quoted"] = quote_voice(out, rc=int(out.get("rc") or out.get("_http") or 200))
        if barge:
            out["barge"] = barge
        return out

    def say(self, transcript: str, *, speak: bool = True) -> dict:
        """Typed turn: skip mic/VAD/STT. Still consumes id18 and POSTs /voice."""
        ticket = self.consume_pull()
        before = Path(ticket["pull_path"]).read_bytes()
        out = self._post(transcript, speak=speak)
        after = Path(ticket["pull_path"]).read_bytes()
        rec = _wrap(out, ticket, stt={"engine": "typed", "transcript": transcript},
                    vad=None, wrote=(after != before))
        rec.update(self._quote_device())
        return rec

    def turn(self, *, seconds: float = 2.0, pcm: Optional[bytes] = None,
             rate: int = STT_RATE, speak: bool = True) -> dict:
        """PTT: capture (or injected PCM) -> 16 kHz -> VAD -> STT -> /voice."""
        listen = ack_listening()
        ticket = self.consume_pull()
        self.dt.ensure_can_speak()
        self.dt.honor_control()
        ep_name = ""
        if pcm is None:
            pcm, rate, ep = self.dt.audio.capture(
                float(seconds), hangover_ms=VAD_HANGOVER_MS)
            ep_name = ep.device_name or ""
        rate = int(rate) or STT_RATE
        set_voice_state(VOICE_TRANSCRIBING)
        ev = vad_interrupt(pcm, rate, transcribe=self._transcribe)
        vad = ev.get("vad") or {}
        if not ev["speech"]:
            raise CvmDtError(
                RefusalKind.STT_NONE,
                "VAD heard no speech (rms=%s speech_ms=%s)"
                % (vad.get("rms"), vad.get("speech_ms")))
        if ev.get("stt_kind") != "ok" or not ev.get("transcript"):
            raise CvmDtError(RefusalKind.STT_NONE, "empty transcript")
        stt = {"transcript": ev["transcript"], "engine": ev.get("engine"),
               "ear_ms": ev.get("ear_ms")}
        before = Path(ticket["pull_path"]).read_bytes()
        out = self._post(str(stt["transcript"]), speak=speak)
        after = Path(ticket["pull_path"]).read_bytes()
        rec = _wrap(out, ticket, stt=stt, vad=vad, wrote=(after != before))
        rec.update(self._quote_device())
        rec["device_name"] = ep_name or rec.get("device_name")
        rec["pcm_bytes"] = len(pcm)
        rec["rate"] = ev.get("rate") or STT_RATE
        rec["first_word_ms"] = ev.get("first_word_ms")
        rec["handoff_ms"] = ev.get("handoff_ms")
        rec["resample_chunks"] = ev.get("resample_chunks")
        rec["resample_chunk_bytes"] = ev.get("resample_chunk_bytes")
        rec["vad_event"] = True
        rec["listen_ack"] = listen.get("ack")
        rec["gated_on_pull"] = False
        rec["lead_kept"] = bool(ev.get("lead_kept"))
        rec["usable"] = bool(ev.get("usable"))
        rec["preroll_ms"] = vad.get("preroll_ms")
        rec["preroll_bytes"] = vad.get("preroll_bytes")
        rec["voice_state"] = voice_state()
        rec["stt_kind"] = "ok"
        return rec

    def barge_in(self, pcm: bytes, rate: int = STT_RATE, *,
                 play_pcm: Optional[bytes] = None,
                 play_rate: int = STT_RATE) -> dict:
        """Interrupt-only: VAD during play cancels TTS. No STT, no GET, no POST."""
        self.dt.ensure_can_speak()
        gate = PlaybackGate().arm()
        got: dict = {}
        t = threading.Thread(
            target=lambda: (time.sleep(0.02),
                            got.update(vad_interrupt(pcm, rate, gate=gate))),
            daemon=True)
        t.start()
        self.dt.audio.play_pcm16_mono(
            play_pcm if play_pcm is not None else b"\x00\x10" * 8000,
            int(play_rate) or STT_RATE, cancel=gate)
        t.join(timeout=2.0)
        gate.finish()
        got.setdefault("cancel_ms", gate.cancel_ms)
        return got

    def emit_heartbeat(self, extra: dict, *, polls: int = 0,
                       interval_s: Optional[float] = None) -> dict:
        """Native heartbeat on EVERY tick (pass / idle / refused). Not a clock."""
        hb_path = self.dt.paths.logs(HEARTBEAT_NAME)
        payload = {"schema": WIRE, "tree_id": self.dt.paths.sentinel.tree_id,
                   "clock_id": extra.get("clock_id", PULL_CLOCK_ID)}
        for k in ("mic_state", "core_kind", "stt_kind", "tick", "ok", "kind",
                  "ticket_clock_id", "audio_owner", "voice_state") + _DEV_KEYS:
            payload[k] = extra.get(k, MIC_IDLE if k == "mic_state" else None)
        hb = write_heartbeat(hb_path, WORKER, extra=payload,
                             polls=polls, interval_s=interval_s)
        extra["heartbeat"] = hb
        extra["heartbeat_path"] = str(hb_path)
        extra["last_run_epoch"] = hb["last_run_epoch"]
        return extra

    def tick(self, *, polls: int = 0, interval_s: float = VOICE_IDLE_S,
             say: Optional[str] = None, ptt: bool = False,
             seconds: float = 2.0, speak: bool = True,
             pcm: Optional[bytes] = None, rate: int = STT_RATE) -> dict:
        """One loop tick. Heartbeat ALWAYS. Mic never auto-starts."""
        vosk = self._bind_stt()
        extra: dict[str, Any] = {
            "ok": True, "tick": "idle", "state": "RUNNING", "wire": WIRE,
            "route": VOICE_ROUTE, "clock_id": PULL_CLOCK_ID,
            "mic_state": MIC_IDLE, "core_kind": None,
            "stt_kind": vosk.get("kind"), "ticket_clock_id": None,
            "audio_owner": None, "session_id": None, "spoken": None,
            "device_name": None, "capture_name": None, "device_id": None,
            "voice_state": (
                VOICE_UNAVAILABLE if (self.transcriber is None and not vosk.get("ok"))
                else VOICE_READY),
        }
        extra.update(self._quote_device())
        try:
            if say:
                extra["mic_state"] = MIC_IDLE
                rec = self.say(str(say), speak=speak)
                extra["tick"] = "say"
                extra.update(_tick_from_turn(rec))
                extra["voice_state"] = rec.get("voice_state") or voice_state()
            elif ptt or pcm is not None:
                extra["mic_state"] = MIC_PTT
                rec = self.turn(seconds=seconds, pcm=pcm, rate=rate, speak=speak)
                extra["tick"] = "ptt"
                extra["mic_state"] = MIC_IDLE
                extra.update(_tick_from_turn(rec))
                extra["voice_state"] = rec.get("voice_state") or voice_state()
            else:
                if extra["voice_state"] != VOICE_UNAVAILABLE:
                    extra["voice_state"] = set_voice_state(VOICE_READY)["voice_state"]
                ticket = self.consume_pull()
                extra["tick"] = "idle"
                extra["mic_state"] = MIC_IDLE
                extra["clock_id"] = ticket.get("clock_id") or PULL_CLOCK_ID
                extra["ticket_clock_id"] = ticket.get("clock_id")
                extra["core_kind"] = ticket.get("core_kind") or "ok"
                extra["audio_owner"] = ticket.get("audio_owner")
                extra["note"] = "mic never auto-starts; space/enter is PTT"
        except CvmDtError as e:
            extra["ok"] = False
            extra["tick"] = "refused"
            extra["kind"] = str(e.kind)
            extra["detail"] = str(e)[:300]
            extra["route"] = VOICE_ROUTE
            extra["session_id"] = None
            extra["spoken"] = None
            if e.kind == RefusalKind.UNREACHABLE or str(e.kind) in ROAD_KINDS:
                extra["core_kind"] = "UNREACHABLE"
            if e.kind == RefusalKind.STT_NONE:
                extra["stt_kind"] = "STT_NONE"
                extra.update(ack_stt_none(
                    audible=self.dt.audio.play_earcon if speak else None))
            extra["mic_state"] = MIC_IDLE
            extra["voice_state"] = extra.get("voice_state") or voice_state()
            if self.last_pull:
                extra["ticket_clock_id"] = extra.get("ticket_clock_id") or self.last_pull.get("clock_id")
                extra["audio_owner"] = extra.get("audio_owner") or self.last_pull.get("audio_owner")
        lv = {k: extra.get(k) for k in (
            "rc", "model", "spoken", "clock_id", "ok", "session_id",
            "mic_state", "core_kind", "stt_kind") + _DEV_KEYS + (
            "mix_capture", "mix_render", "preroll_ms", "preroll_bytes",
            "voice_state", "handoff_ms", "resample_chunks",
            "resample_chunk_bytes")}
        lv["route"] = extra.get("route", VOICE_ROUTE)
        lv["kind"] = extra.get("kind") or extra.get("core_kind")
        extra["live_value"] = lv
        return self.emit_heartbeat(extra, polls=polls, interval_s=interval_s)

    def close(self) -> None:
        self.dt.close()


def _wrap(out: dict, ticket: dict, *, stt: dict, vad: Optional[dict],
          wrote: bool) -> dict:
    quoted = out.get("quoted") or quote_voice(out)
    return {
        "ok": bool(out.get("ok")), "wire": WIRE, "client_id": CLIENT_ID,
        "build": DT_BUILD, "route": VOICE_ROUTE, "quoted": quoted,
        "session_id": out.get("session_id"), "kind": out.get("kind"),
        "brain": out.get("brain"), "spoken": out.get("spoken"),
        "reply": out.get("reply"), "tts": out.get("tts"), "stt": stt,
        "vad": vad,
        "pull": {
            "clock_id": ticket.get("clock_id"),
            "audio_owner": ticket.get("audio_owner"),
            "core_ready": ticket.get("core_ready"),
            "core_kind": ticket.get("core_kind"),
            "cursor": ticket.get("cursor"), "wrote_pull": bool(wrote),
        },
        "live_value": {
            "route": quoted.get("route"), "rc": quoted.get("rc"),
            "brain": quoted.get("brain"), "model": quoted.get("model"),
            "kind": quoted.get("kind"), "ok": quoted.get("ok"),
            "session_id": quoted.get("session_id"),
            "served_at": quoted.get("served_at"),
            "clock_id": ticket.get("clock_id"),
            "audio_owner": ticket.get("audio_owner"),
            "wrote_pull": bool(wrote),
        },
    }


def _tick_from_turn(rec: dict) -> dict:
    quoted = rec.get("quoted") or rec.get("live_value") or {}
    pull = rec.get("pull") or {}
    out = {
        "ok": bool(rec.get("ok")), "rc": quoted.get("rc"),
        "model": quoted.get("model"),
        "spoken": rec.get("spoken") or quoted.get("spoken"),
        "session_id": rec.get("session_id") or quoted.get("session_id"),
        "kind": rec.get("kind") or quoted.get("kind"),
        "brain": rec.get("brain") or quoted.get("brain"),
        "clock_id": pull.get("clock_id") or PULL_CLOCK_ID,
        "ticket_clock_id": pull.get("clock_id"),
        "core_kind": pull.get("core_kind") or "ok",
        "audio_owner": pull.get("audio_owner"), "quoted": quoted,
    }
    for k in _DEV_KEYS + (
            "voice_state", "listen_ack", "gated_on_pull", "usable",
            "lead_kept", "preroll_ms", "preroll_bytes", "stt_kind",
            "handoff_ms", "resample_chunks", "resample_chunk_bytes"):
        if rec.get(k) is not None:
            out[k] = rec[k]
    return out


def run_selftest() -> dict:
    import tempfile
    from cosmos_paths import CosmosPaths as _CP
    tmp = Path(tempfile.mkdtemp(prefix="cvm-dt-voice-selftest-"))
    sent = {"system": "COSMOS", "tree_id": "KMesh-COSMOS-live", "schema_version": 1}
    (tmp / ".cosmos-root.json").write_text(json.dumps(sent), encoding="utf-8")
    (tmp / "config").mkdir()
    (tmp / "state").mkdir()
    (tmp / "config" / "api_token.txt").write_text("selftest-token-not-live",
                                                  encoding="utf-8")
    paths = _CP(tmp)
    pull_p = paths.state(*LEASE_REL)
    pull_p.parent.mkdir(parents=True, exist_ok=True)
    ticket = {
        "cvm": 1, "tree_id": paths.sentinel.tree_id,
        "issued_epoch": time.time(), "pull": True, "audio_owner": "desktop",
        "clock_id": PULL_CLOCK_ID, "core_ready": True, "core_kind": "ok",
        "voice_client_timeout_s": VOICE_READ_S, "cursor": "selftest",
        "writer": "cvm-dt-clock",
    }
    pull_p.write_text(json.dumps(ticket), encoding="utf-8")
    before = pull_p.read_bytes()
    rec = consume_id18_pull(paths)
    wrote = pull_p.read_bytes() != before
    silence = energy_vad(b"\x00\x00" * 1600, STT_RATE)
    loud = energy_vad(b"\x00\x40" * 1600, STT_RATE)
    ticket["clock_id"] = 16
    pull_p.write_text(json.dumps(ticket), encoding="utf-8")
    wrong_kind = None
    try:
        consume_id18_pull(paths)
    except CvmDtError as e:
        wrong_kind = str(e.kind)
    ticket["clock_id"] = PULL_CLOCK_ID
    ticket["core_ready"] = False
    ticket["core_kind"] = "UNREACHABLE"
    pull_p.write_text(json.dumps(ticket), encoding="utf-8")
    dead_kind = None
    try:
        consume_id18_pull(paths)
    except CvmDtError as e:
        dead_kind = str(e.kind)
    q = quote_voice({
        "ok": True, "session_id": "abc", "kind": "command",
        "brain": "local", "spoken": "Ready.", "served_at": 1.0,
        "sources": [], "_http": 200,
    })
    ticket["clock_id"] = PULL_CLOCK_ID
    ticket["core_ready"] = True
    ticket["core_kind"] = "ok"
    ticket["issued_epoch"] = time.time()
    pull_p.write_text(json.dumps(ticket), encoding="utf-8")
    dt = CvmDt(paths, CoreClient("http://127.0.0.1:1", "selftest-token-not-live"),
               FakeBackend(), AudioLease(pull_p, paths.sentinel.tree_id))
    voice = CvmDtVoice(dt, transcriber=FakeTranscriber("status"))
    idle = voice.tick(polls=1, interval_s=VOICE_IDLE_S, speak=False)
    hb = json.loads(Path(idle["heartbeat_path"]).read_text(encoding="utf-8"))
    dead = voice.tick(polls=2, say="status", speak=False)
    hb2 = json.loads(Path(dead["heartbeat_path"]).read_text(encoding="utf-8"))
    vosk_kind = probe_vosk()["kind"]
    win = probe_windows_default()
    # 48 kHz capture must land at STT_RATE before VAD/STT (the VOSK bind).
    pcm48 = b"\x00\x40" * 4800
    rs = resample_pcm16_mono(pcm48, 48000, STT_RATE)
    ok = (
        rec["clock_id"] == PULL_CLOCK_ID == 18
        and rec["audio_owner"] == "desktop" and not wrote
        and wrong_kind == dead_kind == RefusalKind.UNREACHABLE
        and silence["speech"] is False and loud["speech"] is True
        and q["route"] == VOICE_ROUTE and q["rc"] == 200
        and q["brain"] == q["model"] == "local"
        and FAST_READ_S == 8.0 and VOICE_READ_S == 70.0
        and idle["mic_state"] == MIC_IDLE
        and idle["clock_id"] == PULL_CLOCK_ID
        and idle["stt_kind"] == vosk_kind
        and idle.get("device_name") == "Headphones (FAKE HT3)"
        and (vosk_kind == "STT_NONE" or probe_vosk().get("ok") is True)
        and hb["last_run_epoch"] and hb["clock_id"] == 18
        and hb["mic_state"] == MIC_IDLE
        and hb.get("device_name") == "Headphones (FAKE HT3)"
        and hb.get("worker") == WORKER and "core_kind" in hb
        and dead["ok"] is False
        and dead.get("kind") == str(RefusalKind.UNREACHABLE)
        and dead.get("session_id") is None
        and hb2["last_run_epoch"] >= hb["last_run_epoch"]
        and hb2["core_kind"] == "UNREACHABLE"
        and hb2["mic_state"] == MIC_IDLE and win.get("device_name")
        and len(rs) != len(pcm48)
        and energy_vad(rs, STT_RATE)["speech"] is True
        and wait_for_ptt(0.0) is False
    )
    return {
        "selftest": "ok" if ok else "FAIL",
        "live_value": {
            "clock_id": idle.get("clock_id") or rec.get("clock_id"),
            "mic_state": idle.get("mic_state"), "stt_kind": vosk_kind,
            "device_name": win.get("device_name"),
            "capture_name": win.get("capture_name"),
            "device_id": win.get("device_id"),
            "loop_device_name": idle.get("device_name"),
            "audio_owner": rec.get("audio_owner"),
            "wrote_pull": bool(wrote), "wrong_clock": wrong_kind,
            "dead_core": dead_kind, "vad_silence": silence["speech"],
            "vad_loud": loud["speech"], "route": q["route"], "rc": q["rc"],
            "brain": q["brain"], "last_run_epoch": hb.get("last_run_epoch"),
            "dead_core_kind": dead.get("kind"), "heartbeat": HEARTBEAT_NAME,
            "stt_rate": STT_RATE, "resampled_48k_bytes": len(rs),
        },
        "note": "loopback selftest is a green log, not stage 6. "
                "device_name is the live WASAPI default (or AUDIO_NONE).",
    }


def skip_alive(paths: CosmosPaths) -> dict | None:
    """Second launch no-ops while the heartbeat's holder pid is alive."""
    rec = read_heartbeat(paths.logs(HEARTBEAT_NAME))
    if not rec or rec.get("worker") != WORKER:
        return None
    try:
        pid = int(rec.get("pid") or 0)
    except (TypeError, ValueError):
        return None
    return rec if pid_alive(pid) else None


def _locked(paths: CosmosPaths):
    """acquire_lock. On conflict: skip_alive no-op (None, 0) or refuse (None, 2)."""
    fd = acquire_lock(paths.logs(LOCK_NAME))
    if fd is not None:
        return fd, None
    rec = skip_alive(paths)
    if rec is None:
        print("cvm-dt-voice lock held and holder not skip_alive - refusing",
              flush=True)
        return None, 2
    age = heartbeat_age_s(rec)
    print(json.dumps({"already_running": True, "pid": rec.get("pid"),
                      "age_s": None if age is None else round(age, 3)},
                     indent=1, default=str), flush=True)
    return None, 0


def loop(root: str, interval_s: float = VOICE_IDLE_S, *,
         base: str = "http://127.0.0.1:8770", arm: bool = False,
         speak: bool = False) -> int:
    """Idle ear/mouth loop. Space/enter = PTT. Heartbeat every tick.

    Windowless-safe, same vehicle as cvm_dt_clock.loop: stdout/stderr land in
    logs/cvm_dt_voice.out (under pythonw sys.stdout is None and print() is a
    silent no-op — measured — so an unredirected loop is undiagnosable), and
    the OS lock keeps a 1-min self-heal schtask from stacking processes.
    """
    dt = make_dt(root, base, arm=arm)
    paths = dt.paths
    out_path = paths.logs(OUT_NAME)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    log_fh = open(out_path, "a", encoding="utf-8", buffering=1)
    sys.stdout = log_fh
    sys.stderr = log_fh
    fd, rc = _locked(paths)
    if fd is None:
        return rc
    voice = CvmDtVoice(dt)
    polls = 0
    print(json.dumps({"loop": True, "pid": os.getpid(),
                      "interval_s": interval_s, "worker": WORKER,
                      "consumes_clock_id": PULL_CLOCK_ID}, indent=1),
          flush=True)
    try:
        while True:
            polls += 1
            rec = voice.tick(polls=polls, interval_s=interval_s, speak=speak)
            _print_tick(rec)
            if wait_for_ptt(interval_s):
                polls += 1
                _print_tick(voice.tick(polls=polls, interval_s=interval_s,
                                       ptt=True, speak=speak))
    finally:
        voice.close()
        os.close(fd)
    return 0


def register(root: str) -> dict:
    """Emit schtasks /Create lines. Do NOT run them (no bats; Keith does)."""
    paths = CosmosPaths(root)
    tr = tr_cmdline(Path(__file__).resolve(), str(paths.root), "--loop")
    cmds = [subprocess.list2cmdline(a) for a in (
        plan_create(TASK_NAME, tr, "minute", mo=1),
        plan_create(TASK_NAME_LOGON, tr, "onlogon"))]
    return {
        "ok": True,
        "ran": False,
        "worker": WORKER,
        "consumes_clock_id": PULL_CLOCK_ID,
        "task_name": TASK_NAME,
        "task_logon": TASK_NAME_LOGON,
        "tr": tr,
        "pythonw": pythonw_exe(),
        "keith_cmds": cmds,
        "keith_cmd": " & ".join(cmds),
        "heartbeat": str(paths.logs(HEARTBEAT_NAME)),
        "note": ("EMITTED, not executed. Keith runs COSMOS himself. "
                 "No bats. pythonw --loop + 1-min self-heal + onlogon."),
    }


def status(root: str) -> dict:
    """Freshness AND registration. A never-registered worker reads as such."""
    paths = CosmosPaths(root)
    rec = read_heartbeat(paths.logs(HEARTBEAT_NAME))
    age = heartbeat_age_s(rec)
    registered = bool(query_task(TASK_NAME).get("ok"))
    return {
        "path": str(paths.logs(HEARTBEAT_NAME)),
        "worker": WORKER,
        "age_s": age,
        "fresh": age is not None and age < FRESH_S,
        "task_name": TASK_NAME,
        "registered": registered,
        "logon_registered": bool(query_task(TASK_NAME_LOGON).get("ok")),
        "skip_alive": skip_alive(paths) is not None,
        "heartbeat": rec,
    }


def voice_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        prog="cvm-dt voice",
        description="Desktop CVM ear/mouth loop (WASAPI + POST /api/v1/voice)")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--root", default="")
    ap.add_argument("--base", default="http://127.0.0.1:8770")
    ap.add_argument("--arm", action="store_true")
    ap.add_argument("--no-speak", action="store_true")
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--interval", type=float, default=VOICE_IDLE_S)
    ap.add_argument("--say", default="")
    ap.add_argument("--ptt", action="store_true")
    ap.add_argument("--seconds", type=float, default=2.0)
    ap.add_argument("--bind", action="store_true")
    ap.add_argument("--loop", action="store_true",
                    help="windowless daemon body (the --register vehicle)")
    ap.add_argument("--register", action="store_true",
                    help="emit schtasks /Create; do not run it")
    ap.add_argument("--status", action="store_true",
                    help="heartbeat age + schtasks registration")
    return ap


def voice_main(argv: Optional[list[str]] = None) -> int:
    ap = voice_parser()
    ns = ap.parse_args(argv)
    if ns.selftest:
        rec = run_selftest()
        print(json.dumps(rec, indent=1))
        return 0 if rec["selftest"] == "ok" else 1
    if not ns.root:
        ap.error("--root is required (except --selftest)")
    if ns.register:
        print(json.dumps(register(ns.root), indent=1, default=str))
        return 0
    if ns.status:
        rec = status(ns.root)
        print(json.dumps(rec, indent=1, default=str))
        # Fail closed: unregistered is a REFUSAL, not a quiet stale reading.
        return 0 if (rec["fresh"] and rec["registered"]) else 2
    if ns.bind:
        ns.say = ns.say or "status"
        ns.once = True
    try:
        if ns.once or ns.say or ns.ptt:
            dt = make_dt(ns.root, ns.base, arm=ns.arm)
            voice = CvmDtVoice(dt)
            try:
                rec = voice.tick(
                    polls=1, interval_s=ns.interval,
                    say=ns.say or None, ptt=ns.ptt,
                    seconds=ns.seconds, speak=not ns.no_speak)
                _print_tick(rec)
                return 0 if rec.get("ok") else 2
            finally:
                voice.close()
        return loop(ns.root, ns.interval, base=ns.base, arm=ns.arm,
                    speak=not ns.no_speak)
    except CvmDtError as e:
        print(json.dumps({"ok": False, "status": "refused",
                          "kind": str(e.kind), "detail": str(e),
                          "route": VOICE_ROUTE, "session_id": None}))
        return 2


def main(argv: Optional[list[str]] = None) -> int:
    """One flag-form parser. `cvm_dt.py voice` is the CLI."""
    return voice_main(list(sys.argv[1:] if argv is None else argv))


if __name__ == "__main__":
    sys.exit(main())
