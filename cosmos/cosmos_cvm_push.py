#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Core POST /api/v1/cvm/push — phone turn landing surface (P10 propose-only).

The thin phone clock POSTs the SS8.3 snapshot_delta envelope at this path
(docs/CVM_ARCH.md §8.3). Core already stores that body via
cosmos_service._cvm_store_snapshot (state/cvm/phone.json). This module
COMPOSES that helper and cosmos_service._cvm_pull_response — it does not
copy kinds-filter, idempotency, cursor hash, or pull assembly.

stamp_desktop_pull is the ONE pull.json writer helper (desktop owner +
phone cursor + drain metrics). DesktopPullClock (CLOCK_ID 18) is the
sole authoritative pull.json clock; cosmos_cvm_clock (id 16) calls
merge_satellite_pull which NEVER clobbers DRAIN_KEYS. pull.json.clock_id
is always PULL_CLOCK_ID (18) — one truth.

A phone push sets backlog=1 + last_push_epoch; the desktop drain loop
folds, then stamps backlog=0 + pull_ms + last_pull_epoch so drain_lag_ms
is a value only a true pull cycle can emit. Command initiation is NOT
that cycle: stt_interrupt (VAD/PCM -> local STT) is event-driven, never
waits on idle-GET coalesce. Idle loops sleep in slices and wake on
local phone.json. A stale pcm pointer is not speech-live — coalesce
resumes. PlaybackGate is the barge-in cancel token (independent of GET).

Contract:
  * Body is the §8.3 snapshot_delta envelope. No second schema.
  * Auth is the existing /api/v1 bearer (wired in cosmos_service.do_POST).
  * A phone push NEVER claims audio ownership: any body audio_owner is
    stripped, pull.json is stamped audio_owner=desktop, and the composed
    GET /cvm/pull view is refused if it is not desktop.
  * GET /cvm/pull then overlays cursor from phone.json (existing P3
    behaviour), so the pull ticket reflects the pushed turn.

Resolver paths only (kernel.paths.state). No drive literals. No bts_ imports.
Does not write audio.json or handoff.json. Does not append the ledger.

    py -3.14 tests\\test_cvm_push.py
"""
from __future__ import annotations

import json
import os
import threading
import time
from pathlib import Path

PUSH_PATH = "/api/v1/cvm/push"
SNAP_PATH = "/api/v1/cvm/snapshot"
WRITER = "cosmos-service-cvm-push"
# DesktopPullClock is the sole pull.json clock. Id 16 (audio/ux satellite)
# is registered in CLOCKS; it does not own this file.
PULL_CLOCK_ID = 18
DRAIN_WRITERS = ("cvm-dt-pull", "cvm-dt-client", "cvm-dt-handoff", "cvm-dt-clock")
# Drain metrics. merge_satellite_pull never drops these; stamp copies
# them from overlay when the drain cycle measured them.
DRAIN_KEYS = (
    "pull_ms", "fold_ms", "pull_cycle_ms", "backlog", "drained",
    "last_pull_epoch", "last_push_epoch", "drain_lag_ms",
    "cadence_mode", "speech_live", "skipped_http", "tick_ms",
    "first_word_ms", "stt_kind", "stt_engine", "stt_pcm_sha256",
)
# Satellite cadence (id16 merge). Distinct from DRAIN_KEYS.
SATELLITE_KEYS = (
    "issued_epoch", "voice_client_timeout_s", "core_ready",
    "core_kind", "blob_max_bytes", "pcm_wanted", "ticket_seq",
)
# One cadence (was duplicated on id16 + id18). Heartbeat stays 2s;
# HTTP GET coalesces when idle. Speech is a local interrupt (stt_interrupt
# / PlaybackGate), not a GET burst. Burst sleep is backlog-fold only.
PULL_INTERVAL_S = 15.0
DRAIN_IDLE_S = 2.0
SPEECH_BURST_S = 0.25
IDLE_BACKOFF_S = 15.0
SPEECH_LIVE_S = 8.0
STT_RATE = 16000
VOICE_READY = "ready"
VOICE_LISTENING = "listening"
VOICE_TRANSCRIBING = "transcribing"
VOICE_UNAVAILABLE = "unavailable"
VOICE_STATES = (VOICE_READY, VOICE_LISTENING, VOICE_TRANSCRIBING, VOICE_UNAVAILABLE)
STT_NONE_ACK = "speech recognition unavailable"
STT_NONE_ACK_S = 8.0
# Extra keys stamp_desktop_pull copies from overlay onto pull.json.
STAMP_OVERLAY = SATELLITE_KEYS + (
    "pushed_via",
) + DRAIN_KEYS
_voice = {"state": VOICE_READY, "last_stt_none": None}
_voice_lock = threading.Lock()


def phone_state(paths, tree_id: str):
    """Local phone.json (kinds + cursor + pcm pointer). None if absent/mismatch.

    Identity mismatch (tree_id set and wrong) is None. A seed without
    tree_id still returns the body so local STT can see pcm/voice_session.
    """
    path = paths.state("cvm", "phone.json")
    try:
        phone = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else None
    except (OSError, ValueError):
        return None
    if not isinstance(phone, dict):
        return None
    got = str(phone.get("tree_id") or "")
    if got and got != tree_id:
        return None
    return phone


def phone_cursor(paths, tree_id: str) -> str:
    """Cursor of the last POST /cvm/snapshot|/cvm/push (phone.json)."""
    phone = phone_state(paths, tree_id)
    if not phone or str(phone.get("tree_id") or "") != tree_id:
        return ""
    return str(phone.get("cursor_out") or phone.get("cursor") or "")


def _kinds_of(phone) -> dict:
    if not isinstance(phone, dict):
        return {}
    k = phone.get("kinds")
    return k if isinstance(k, dict) else {}


def pcm_pointer(phone) -> str:
    blob = _kinds_of(phone).get("pcm")
    if not isinstance(blob, dict):
        return ""
    if str(blob.get("status") or "ok").startswith("PERM"):
        return ""
    return str(blob.get("sha256") or blob.get("sha") or "")


def speech_live(phone=None, ticket=None, *, now: float | None = None) -> bool:
    """True when a phone turn is in flight — wake cadence_wait, pcm_wanted.

    Recency / backlog / queue_depth only. Does NOT force a Core GET
    (command initiation is stt_interrupt). A stale pcm pointer is NOT
    live: after the turn window the idle coalesce must resume.
    """
    now = time.time() if now is None else float(now)
    for src in (ticket, phone):
        if not isinstance(src, dict):
            continue
        try:
            if int(src.get("backlog") or 0) > 0:
                return True
        except (TypeError, ValueError):
            pass
        for key in ("last_push_epoch", "last_turn_epoch"):
            try:
                ep = float(src.get(key) or 0.0)
            except (TypeError, ValueError):
                ep = 0.0
            if ep and (now - ep) <= SPEECH_LIVE_S:
                return True
    vs = _kinds_of(phone).get("voice_session")
    if isinstance(vs, dict):
        try:
            ep = float(vs.get("last_turn_epoch") or vs.get("t") or 0.0)
        except (TypeError, ValueError):
            ep = 0.0
        if ep and (now - ep) <= SPEECH_LIVE_S:
            return True
        try:
            if int(vs.get("queue_depth") or 0) > 0:
                return True
        except (TypeError, ValueError):
            pass
    return False


def cadence_mode(*, speech: bool, backlog: int = 0,
                 skipped_http: bool = False) -> str:
    if speech or backlog > 0:
        return "burst"
    if skipped_http:
        return "coalesced"
    return "idle"


def cadence_next_s(rec=None, default_s: float = DRAIN_IDLE_S) -> float:
    rec = rec or {}
    try:
        backlog = int(rec.get("backlog") or 0)
    except (TypeError, ValueError):
        backlog = 0
    # Burst GET sleep is backlog-fold only. Speech wakes cadence_wait
    # via phone.json; it does not retune the idle-GET schedule.
    if backlog > 0:
        return SPEECH_BURST_S
    return float(default_s)


def cadence_wait(rec=None, default_s: float = DRAIN_IDLE_S, *,
                 paths=None, tree_id: str = "",
                 slice_s: float = SPEECH_BURST_S) -> float:
    """Idle sleep that wakes when local phone.json goes speech-live.

    GET fallback loop only. First-word STT is stt_interrupt, not this
    sleep. Does not GET Core (local file only).
    """
    rec = rec or {}
    next_s = cadence_next_s(rec, default_s)
    if next_s <= 0:
        return 0.0
    step = max(0.01, float(slice_s))
    if paths is None or next_s <= step:
        time.sleep(next_s)
        return next_s
    deadline = time.time() + next_s
    slept = 0.0
    while True:
        remain = deadline - time.time()
        if remain <= 0:
            return slept
        chunk = min(step, remain)
        time.sleep(chunk)
        slept += chunk
        if speech_live(phone_state(paths, tree_id), rec, now=time.time()):
            return slept


def load_cas_pcm(paths, sha: str):
    """Read state/cvm/cas/<sha256>. None if missing/unreadable. Never invent."""
    hexd = str(sha or "").strip().lower()
    if len(hexd) != 64 or any(c not in "0123456789abcdef" for c in hexd):
        return None
    path = paths.state("cvm") / "cas" / hexd
    try:
        return path.read_bytes() if path.is_file() else None
    except OSError:
        return None


def voice_state() -> str:
    with _voice_lock:
        return str(_voice["state"])


def reset_voice_ack() -> None:
    with _voice_lock:
        _voice["state"] = VOICE_READY
        _voice["last_stt_none"] = None


def set_voice_state(state: str) -> dict:
    """ONE runtime voice state. Local — never waits on GET or pull.json."""
    if state not in VOICE_STATES:
        raise ValueError("unknown voice_state %r" % (state,))
    with _voice_lock:
        _voice["state"] = state
    return {"voice_state": state, "gated_on_pull": False,
            "gated_on_get": False, "gated_on_id18": False}


def ack_listening(*, now: float | None = None) -> dict:  # noqa: ARG001
    """Immediate local listening ack. Not gated on idle-GET / drain-GET / id18."""
    rec = set_voice_state(VOICE_LISTENING)
    rec.update(ack="listening", ack_kind="listening", ack_emitted=True)
    return rec


def ack_stt_none(*, now: float | None = None, audible=None) -> dict:
    """Rate-limited audible/text STT_NONE ack. Does not silently accept PCM."""
    now = time.time() if now is None else float(now)
    rec = set_voice_state(VOICE_UNAVAILABLE)
    with _voice_lock:
        last = _voice["last_stt_none"]
        due = last is None or ((now - float(last)) >= STT_NONE_ACK_S)
        if due:
            _voice["last_stt_none"] = now
    rec.update(ack=STT_NONE_ACK, ack_kind="stt_none", ack_emitted=due,
               stt_kind="STT_NONE")
    if due and callable(audible):
        audible()
    return rec


def probe_stt() -> dict:
    """VOSK via cosmos_stt: vendor site + provisioned model, or STT_NONE.

    COSMOS_VOSK_MODEL still wins when set. Otherwise the F-21 provisioned
    dir under builds/cvm-dt/vendor/models is bound. Default ``import vosk``
    remaining ModuleNotFoundError is not this function — cosmos_stt puts
    the vendor site on sys.path. Empty / missing stays typed STT_NONE.
    """
    from cosmos_stt import probe as _stt_probe
    rec = _stt_probe()
    if rec.get("ok"):
        return {"ok": True, "engine": "vosk", "kind": "ok",
                "model": rec.get("model")}
    return {"ok": False, "engine": "vosk",
            "kind": rec.get("kind") or "STT_NONE",
            "detail": rec.get("detail") or "vosk not bound"}


def transcribe_pcm(pcm: bytes, rate: int = STT_RATE, *, model: str) -> dict:
    """Resident VOSK (F-21). Empty text is STT_NONE, not a fabricated word.

    Predecessor built Model() inside every utterance (F21_STT_LOCAL.json
    model_load_ms paid per phone turn). cosmos_stt holds one Model + one
    KaldiRecognizer and Reset()s between turns.
    """
    from cosmos_stt import transcribe as _stt_transcribe
    rec = _stt_transcribe(pcm, rate=rate, model=model)
    return {
        "transcript": rec.get("transcript") or "",
        "engine": rec.get("engine") or "vosk",
        "ear_ms": rec.get("ear_ms"),
        "rate": rec.get("rate") or rate,
        "kind": rec.get("kind") or "STT_NONE",
    }


def bind_phone_stt(paths, phone, ticket=None, *, now: float | None = None) -> dict:
    """Carry pulled phone PCM into local STT. Never writes pull.json.

    Missing CAS → UNREACHABLE (Core/phone did not land bytes). Missing
    VOSK model dir → STT_NONE. Unconsumed sha is transcribed once, then
    stamped stt_pcm_sha256 so a stale pointer cannot re-burst.
    first_word_ms is THIS call (interrupt elapsed), not drain-GET wait.
    """
    now = time.time() if now is None else float(now)  # noqa: ARG001
    sha = pcm_pointer(phone)
    prev = ticket if isinstance(ticket, dict) else {}
    out = {
        "pcm_sha256": sha, "stt_kind": "STT_NONE", "stt_engine": None,
        "first_word_ms": None, "ear_ms": None, "transcript": "",
        "stt_pcm_sha256": str(prev.get("stt_pcm_sha256") or ""),
        "vad_event": False,
    }
    if not sha or sha == out["stt_pcm_sha256"]:
        if sha and sha == out["stt_pcm_sha256"]:
            out["stt_kind"] = str(prev.get("stt_kind") or "STT_NONE")
            out["stt_engine"] = prev.get("stt_engine")
            out["first_word_ms"] = prev.get("first_word_ms")
            out["ear_ms"] = prev.get("ear_ms")
            out["vad_event"] = True
        return out
    t0 = time.perf_counter()
    pcm = load_cas_pcm(paths, sha)
    probed = probe_stt()
    blob = _kinds_of(phone).get("pcm")
    blob = blob if isinstance(blob, dict) else {}
    try:
        rate = int(blob.get("rate") or STT_RATE)
    except (TypeError, ValueError):
        rate = STT_RATE
    if pcm is None:
        out["stt_kind"] = "UNREACHABLE"
        out["ear_ms"] = round((time.perf_counter() - t0) * 1000.0, 3)
        # Do not consume the sha — blob may still land inside the live window.
    else:
        out["stt_pcm_sha256"] = sha
        set_voice_state(VOICE_TRANSCRIBING)
        if not probed.get("ok"):
            out["stt_kind"] = "STT_NONE"
            out["stt_engine"] = "vosk"
            out["ear_ms"] = round((time.perf_counter() - t0) * 1000.0, 3)
            out.update(ack_stt_none(now=now))
        else:
            rec = transcribe_pcm(pcm, rate, model=str(probed["model"]))
            out["stt_kind"] = rec.get("kind") or "STT_NONE"
            out["stt_engine"] = rec.get("engine")
            out["ear_ms"] = rec.get("ear_ms")
            out["transcript"] = rec.get("transcript") or ""
            if out["stt_kind"] != "ok":
                out.update(ack_stt_none(now=now))
            else:
                set_voice_state(VOICE_READY)
    out["vad_event"] = True
    out["first_word_ms"] = round((time.perf_counter() - t0) * 1000.0, 3)
    out.setdefault("voice_state", voice_state())
    return out


class PlaybackGate:
    """Abort token for in-flight WASAPI render. Independent of idle-GET."""

    def __init__(self):
        self.event = threading.Event()
        self.t0 = 0.0
        self.cancel_ms = None
        self.playing = False

    def arm(self):
        self.event.clear()
        self.playing, self.cancel_ms, self.t0 = True, None, time.perf_counter()
        return self

    def is_set(self) -> bool:
        return self.event.is_set()

    def cancel(self):
        if self.playing and not self.event.is_set():
            self.event.set()
            self.cancel_ms = round((time.perf_counter() - self.t0) * 1000.0, 3)
        self.playing = False
        return self.cancel_ms

    def finish(self):
        self.playing = False
        return self.cancel_ms


def stt_interrupt(paths, phone=None, ticket=None, *, now: float | None = None) -> dict:
    """Event-driven local STT. Never GETs Core. Never writes pull.json."""
    if phone is None:
        phone = phone_state(paths, paths.sentinel.tree_id)
    return bind_phone_stt(paths, phone, ticket, now=now)


def ticket_due(issued_epoch, now: float, *, speech: bool = False,
               interval_s: float = PULL_INTERVAL_S) -> bool:
    if speech:
        return True
    try:
        issued = float(issued_epoch or 0.0)
    except (TypeError, ValueError):
        issued = 0.0
    return (not issued) or ((now - issued) >= float(interval_s))


def _load_ticket(paths):
    pull_path = paths.state("cvm", "pull.json")
    try:
        ticket = json.loads(pull_path.read_text(encoding="utf-8")) if pull_path.is_file() else None
    except (OSError, ValueError) as e:
        raise ValueError("UNPARSEABLE: %s" % str(e)[:300]) from e
    if ticket is not None and not isinstance(ticket, dict):
        raise ValueError("UNPARSEABLE: pull.json is not an object")
    return ticket, pull_path


def _seed_ticket(tree_id: str, overlay: dict, writer: str) -> dict:
    vto = overlay.get("voice_client_timeout_s")
    if vto is None:
        try:
            from cosmos_brain import voice_client_timeout_s as _vto
            vto = _vto()
        except Exception:                                             # noqa: BLE001
            vto = 70.0
    return {
        "cvm": 1, "tree_id": tree_id, "pull": True, "kinds": [],
        "issued_epoch": time.time(), "voice_client_timeout_s": float(vto),
        "writer": writer, "clock_id": PULL_CLOCK_ID,
    }


def _drain_owned(ticket: dict) -> bool:
    writer = str(ticket.get("writer") or "")
    if writer in DRAIN_WRITERS or writer.startswith("cvm-dt"):
        return True
    return any(k in ticket for k in DRAIN_KEYS)


def _apply_lag(ticket: dict) -> None:
    if "last_pull_epoch" in ticket and "last_push_epoch" in ticket:
        try:
            lag = ((float(ticket["last_pull_epoch"])
                    - float(ticket["last_push_epoch"])) * 1000.0)
            ticket["drain_lag_ms"] = round(max(0.0, lag), 3)
        except (TypeError, ValueError):
            pass


def _store_ticket(pull_path, ticket: dict) -> dict:
    from cosmos_clock import atomic_json
    ticket["clock_id"] = PULL_CLOCK_ID
    _apply_lag(ticket)
    try:
        atomic_json(pull_path, ticket)
    except OSError as e:
        raise ValueError("UNREADABLE: %s" % str(e)[:300]) from e
    return ticket


def stamp_desktop_pull(paths, overlay=None, *, writer: str = WRITER) -> dict:
    """ONE writer of the desktop-owned pull ticket. Kernel-free (clock-safe).

    Starts from the existing ticket (drain metrics survive unless overlay
    measured new ones). clock_id is always PULL_CLOCK_ID.
    """
    overlay = dict(overlay or {})
    tree_id = paths.sentinel.tree_id
    ticket, pull_path = _load_ticket(paths)
    if not isinstance(ticket, dict):
        ticket = _seed_ticket(tree_id, overlay, writer)
    else:
        ticket = dict(ticket)
        if str(ticket.get("tree_id") or "") != tree_id:
            raise ValueError(
                "IDENTITY_MISMATCH: pull.json tree_id does not match the sentinel")
    kinds = overlay.get("kinds") or overlay.get("stored") or []
    if isinstance(kinds, dict):
        kinds = list(kinds)
    kinds = [str(k) for k in kinds if str(k)] if isinstance(kinds, list) else []
    cursor = (overlay.get("cursor_out") or overlay.get("cursor")
              or phone_cursor(paths, tree_id) or ticket.get("cursor") or "")
    ticket.update(cvm=1, tree_id=tree_id, pull=True,
                  audio_owner="desktop", claimed=False, writer=writer)
    if cursor:
        ticket["cursor"] = cursor
    if kinds:
        ticket["kinds"] = kinds
    for k in STAMP_OVERLAY:
        if k == "drain_lag_ms":
            continue
        if k in overlay:
            ticket[k] = overlay[k]
    return _store_ticket(pull_path, ticket)


def merge_satellite_pull(paths, overlay=None, *, writer: str = "cosmos-cvm-clock") -> dict:
    """Id16 cadence merge. Never replaces pull.json; never drops DRAIN_KEYS.

    DesktopPullClock remains the authoritative writer. This path updates
    satellite fields (kinds / issued_epoch / core_* / ticket_seq) onto the
    existing ticket. Desktop owner, drain cursor, drain writer, and the
    drain-metric block survive. clock_id stays PULL_CLOCK_ID.
    """
    overlay = dict(overlay or {})
    tree_id = paths.sentinel.tree_id
    ticket, pull_path = _load_ticket(paths)
    if not isinstance(ticket, dict):
        ticket = _seed_ticket(tree_id, overlay, writer)
        if overlay.get("audio_owner"):
            ticket["audio_owner"] = overlay["audio_owner"]
        if overlay.get("cursor"):
            ticket["cursor"] = overlay["cursor"]
        if overlay.get("kinds"):
            kinds = overlay["kinds"]
            ticket["kinds"] = [str(k) for k in kinds if str(k)] if isinstance(kinds, list) else []
        for k in SATELLITE_KEYS:
            if k in overlay:
                ticket[k] = overlay[k]
        return _store_ticket(pull_path, ticket)

    ticket = dict(ticket)
    if str(ticket.get("tree_id") or "") != tree_id:
        raise ValueError(
            "IDENTITY_MISMATCH: pull.json tree_id does not match the sentinel")
    kept = {k: ticket[k] for k in DRAIN_KEYS if k in ticket}
    drain = _drain_owned(ticket)
    prev_cursor = ticket.get("cursor")
    prev_owner = ticket.get("audio_owner")
    prev_writer = ticket.get("writer")
    for k in SATELLITE_KEYS:
        if k in overlay:
            ticket[k] = overlay[k]
    kinds = overlay.get("kinds")
    if isinstance(kinds, list) and kinds:
        ticket["kinds"] = [str(k) for k in kinds if str(k)]
    ticket.update(cvm=1, tree_id=tree_id, pull=True)
    ticket.update(kept)
    if prev_cursor:
        ticket["cursor"] = prev_cursor
    elif overlay.get("cursor"):
        ticket["cursor"] = overlay["cursor"]
    if prev_owner == "desktop" or drain:
        ticket["audio_owner"] = "desktop"
        ticket["claimed"] = False
    elif overlay.get("audio_owner"):
        ticket["audio_owner"] = overlay["audio_owner"]
    if drain and prev_writer:
        ticket["writer"] = prev_writer
    else:
        ticket["writer"] = writer
    return _store_ticket(pull_path, ticket)


def cvm_store_push(kernel, d: dict) -> dict:
    """Land a phone turn. Compose snapshot store + pull publish.

    `_cvm_store_snapshot` validates the §8.3 envelope, is idempotent on
    request_id, and replaces state/cvm/phone.json. This function then
    stamps audio_owner=desktop and quotes `_cvm_pull_response` so the
    subsequent GET /api/v1/cvm/pull is the same view.
    """
    from cosmos_service import (
        CvmError, _cvm_pull_response, _cvm_store_snapshot,
    )

    if not isinstance(d, dict):
        raise CvmError("BAD_SNAPSHOT", "body must be a JSON object")
    body = dict(d)
    body.pop("audio_owner", None)

    rec = _cvm_store_snapshot(kernel, body)
    overlay = {
        "cursor": rec.get("cursor_out") or rec.get("cursor"),
        "kinds": rec.get("stored") or rec.get("kinds") or [],
        "pushed_via": PUSH_PATH,
    }
    if not rec.get("idempotent"):
        overlay["backlog"] = 1
        overlay["last_push_epoch"] = time.time()
    try:
        stamp_desktop_pull(kernel.paths, overlay)
    except ValueError as e:
        kind, _, detail = str(e).partition(": ")
        if kind in ("IDENTITY_MISMATCH", "UNPARSEABLE", "UNREADABLE"):
            raise CvmError(kind, detail) from e
        raise

    client_id = str(body.get("client_id") or "").strip()
    pulled = _cvm_pull_response(kernel, client_id)
    owner = str(pulled.get("audio_owner") or "none") or "none"
    if owner != "desktop":
        raise CvmError(
            "OWNER_CONTESTED",
            "phone push must not become audio owner (got %r)" % owner)
    if pulled.get("pull") is False:
        raise CvmError(
            "UNREACHABLE",
            "GET /cvm/pull published no ticket after POST /cvm/push")

    out = dict(rec)
    out["audio_owner"] = "desktop"
    out["claimed"] = False
    if "idempotent" not in out:
        out["idempotent"] = False
    out["cursor"] = pulled.get("cursor") or rec.get("cursor_out")
    return out


def cvm_post(kernel, path: str, d: dict) -> dict:
    """One POST dispatcher: snapshot stays the P3 helper; push composes it."""
    from cosmos_service import _cvm_store_snapshot

    if path == PUSH_PATH:
        return cvm_store_push(kernel, d)
    if path == SNAP_PATH:
        return _cvm_store_snapshot(kernel, d)
    from cosmos_service import CvmError
    raise CvmError("NOT_FOUND", path)
