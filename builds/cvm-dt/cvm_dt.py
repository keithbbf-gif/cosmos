#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cvm-dt — COSMOS Voice desktop client, PR-2 (lease honorer).

A Windows PC voice CLIENT of Core (docs/CVM_ARCH.md direction #2). It is not a
server, not a second ledger writer, and not a cDeck panel.

  * Capture + TTS render go through the Windows DEFAULT device via WASAPI, so
    the same Bluetooth headphones the phone uses are the DT sink the moment
    Windows owns them.
  * HTTP client of POST /api/v1/voice (sid continuity = resume). Control is
    GET /api/v1/control only — pull/audio never ride the off-switch (H7).
  * AUDIO_OWNER is read from the CVM pull-clock ticket (state/cvm/pull.json).
    Clock is the sole writer (PR-1, H13). DT captures/plays only when the
    ticket is AUDIO_NONE or AUDIO_OWNED by desktop — never writes the owner.
    Missing default → AUDIO_NONE, never a silent fallback (H3).
  * Timeouts: FAST GET 8 s, VOICE POST 70 s (P0). Mic never auto-starts.

--root is the COSMOS runtime root, HANDED IN. No drive literal, no parent-walk.
rc=0 is not complete; the stage-6 proof is STAGE6_GATE.json live_value.
"""
from __future__ import annotations

import argparse
import ctypes
import hashlib
import http.client
import json
import os
import sys
import threading
import time
import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from pathlib import Path
from typing import Any, Callable, Optional, Protocol
from urllib.parse import quote, urlparse

# Source-layout import of the in-tree resolver. The LIVE root is still handed
# in via --root and verified by sentinel content — this is not a root search.
_COSMOS_LIB = Path(__file__).resolve().parents[2] / "cosmos"
if str(_COSMOS_LIB) not in sys.path:
    sys.path.insert(0, str(_COSMOS_LIB))

from cosmos_paths import CosmosPathError, CosmosPaths  # noqa: E402
from cosmos_cvm_push import PULL_CLOCK_ID  # noqa: E402

from wasapi import (  # noqa: E402
    AudioNoneError, Endpoint, Probe, capture_pcm16_mono, ensure_com,
    play_earcon, play_pcm16_mono, play_wav, probe_defaults, route_status,
    windows_default_render,
)

WIRE = "cvm-dt/1"
CLIENT_ID = "cvm-dt"
BUILD = "cvm-dt-pr2"
OWNERS = frozenset({"phone", "desktop", "none"})
LEASE_TTL_S = 30.0
CONNECT_TIMEOUT_S = 10.0
FAST_READ_S = 8.0          # GET status / control
VOICE_READ_S = 70.0        # POST /api/v1/voice  (45 Opus + 20 Grok + 5 slack)
PROOF_NAME = "STAGE6_GATE.json"
LEASE_REL = ("cvm", "pull.json")
PULL_PATH = "/api/v1/cvm/pull"
SNAP_PATH = "/api/v1/cvm/snapshot"
ROAD_KINDS = frozenset({"UNREACHABLE", "CLOCK_STALE", "AUTH_REQUIRED"})


class RefusalKind(StrEnum):
    AUDIO_NONE = "AUDIO_NONE"
    AUDIO_OWNED = "AUDIO_OWNED"
    AUDIO_UNARMED = "AUDIO_UNARMED"
    UNREACHABLE = "UNREACHABLE"
    AUTH_REQUIRED = "AUTH_REQUIRED"
    CONTROL_BLOCKED = "CONTROL_BLOCKED"
    ROOT_MISSING = "ROOT_MISSING"
    IDENTITY_MISMATCH = "IDENTITY_MISMATCH"
    STOPPED = "STOPPED"
    TTS_NONE = "TTS_NONE"
    STT_NONE = "STT_NONE"
    UNAUTHORIZED = "UNAUTHORIZED"
    BAD_CORE = "BAD_CORE"
    BAD_REQUEST = "BAD_REQUEST"
    BAD_SNAPSHOT = "BAD_SNAPSHOT"
    CURSOR_GAP = "CURSOR_GAP"
    OWNER_CONTESTED = "OWNER_CONTESTED"


class CvmDtError(RuntimeError):
    """Typed refusal. kind is a RefusalKind (also a str)."""

    def __init__(self, kind: RefusalKind | str, detail: str):
        if not isinstance(kind, RefusalKind):
            try:
                kind = RefusalKind(kind)
            except ValueError as e:
                raise ValueError("unknown CvmDtError kind %r" % (kind,)) from e
        self.kind: RefusalKind = kind
        super().__init__("[%s] %s" % (kind, detail))


def _now() -> tuple[float, int]:
    dt = datetime.now().astimezone()
    off = dt.utcoffset()
    return dt.timestamp(), int(off.total_seconds()) if off is not None else 0


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def _atomic_install(final_p: Path, payload: dict) -> None:
    final_p.parent.mkdir(parents=True, exist_ok=True)
    tmp = final_p.with_name(final_p.name + ".part")
    tmp.write_text(json.dumps(payload, indent=1), encoding="utf-8")
    os.replace(tmp, final_p)


def load_paths(root: str | os.PathLike) -> CosmosPaths:
    """Verify the handed-in runtime root. Existence is not identity."""
    try:
        return CosmosPaths(root)
    except CosmosPathError as e:
        kind = (RefusalKind.IDENTITY_MISMATCH
                if e.kind == "IDENTITY_MISMATCH"
                else RefusalKind.ROOT_MISSING)
        raise CvmDtError(kind, str(e)) from e


def load_token(paths: CosmosPaths) -> str:
    p = paths.config("api_token.txt")
    try:
        token = p.read_text(encoding="utf-8").strip()
    except OSError as e:
        raise CvmDtError(RefusalKind.AUTH_REQUIRED,
                         "api_token.txt unreadable: %s" % e) from e
    if not token:
        raise CvmDtError(RefusalKind.AUTH_REQUIRED,
                         "api_token.txt missing or blank — refusing to invent a bearer")
    return token


# ---------------- WASAPI backend (injectable) ----------------
class AudioBackend(Protocol):
    def probe(self) -> Probe: ...
    def windows_default(self) -> Endpoint: ...
    def play_wav(self, wav: bytes, cancel=None) -> Endpoint: ...
    def play_pcm16_mono(self, pcm: bytes, rate: int, cancel=None) -> Endpoint: ...
    def play_earcon(self) -> Endpoint: ...
    def capture(self, seconds: float, hangover_ms: float = 0.0
                ) -> tuple[bytes, int, Endpoint]: ...


class WasapiBackend:
    def probe(self) -> Probe:
        try:
            return probe_defaults()
        except AudioNoneError as e:
            raise CvmDtError(RefusalKind.AUDIO_NONE, str(e)) from e

    def windows_default(self) -> Endpoint:
        """SECOND, independent GetDefaultAudioEndpoint read (gate evidence).

        The gate asks whether the endpoint DT opened IS the Windows default.
        Answering it from the same probe record compares a value to itself.
        """
        try:
            return windows_default_render()
        except AudioNoneError as e:
            raise CvmDtError(RefusalKind.AUDIO_NONE, str(e)) from e

    def play_wav(self, wav: bytes, cancel=None) -> Endpoint:
        try:
            return play_wav(wav, cancel=cancel)
        except AudioNoneError as e:
            raise CvmDtError(RefusalKind.AUDIO_NONE, str(e)) from e

    def play_pcm16_mono(self, pcm: bytes, rate: int, cancel=None) -> Endpoint:
        try:
            return play_pcm16_mono(pcm, rate, cancel=cancel)
        except AudioNoneError as e:
            raise CvmDtError(RefusalKind.AUDIO_NONE, str(e)) from e

    def play_earcon(self) -> Endpoint:
        try:
            return play_earcon()
        except AudioNoneError as e:
            raise CvmDtError(RefusalKind.AUDIO_NONE, str(e)) from e

    def capture(self, seconds: float, hangover_ms: float = 0.0
                ) -> tuple[bytes, int, Endpoint]:
        try:
            return capture_pcm16_mono(seconds, hangover_ms=hangover_ms)
        except AudioNoneError as e:
            raise CvmDtError(RefusalKind.AUDIO_NONE, str(e)) from e


@dataclass
class FakeProbe:
    render: Endpoint
    capture: Endpoint
    communications_render_name: str = ""


class FakeBackend:
    """Injected backend for selftest — never touches a real device."""

    def __init__(self, name: str = "Headphones (FAKE HT3)", none: bool = False):
        self.none = none
        self.name = name
        self.played: list[tuple[str, int]] = []
        self.cancelled = False
        ep_r = Endpoint("render", "console", "fake-render-id", name, True)
        ep_c = Endpoint("capture", "console", "fake-capture-id", name, True)
        self._probe = Probe(ep_r, ep_c, name)

    def probe(self) -> Probe:
        if self.none:
            raise CvmDtError(RefusalKind.AUDIO_NONE, "fake: no default device")
        return self._probe

    def windows_default(self) -> Endpoint:
        """The fake IS its own default — it never queries the real machine."""
        return self.probe().render

    def play_wav(self, wav: bytes, cancel=None) -> Endpoint:
        self.probe()
        self.played.append(("wav", len(wav)))
        if cancel is None:
            return self._probe.render
        return self.play_pcm16_mono(b"\x00\x00" * 16, 16000, cancel=cancel)

    def play_pcm16_mono(self, pcm: bytes, rate: int, cancel=None) -> Endpoint:
        self.probe()
        self.played.append(("pcm", len(pcm)))
        if cancel is not None:
            deadline = time.time() + 0.5
            while time.time() < deadline:
                fn = getattr(cancel, "is_set", None)
                if callable(fn) and fn():
                    self.cancelled = True
                    break
                time.sleep(0.005)
        return self._probe.render

    def play_earcon(self) -> Endpoint:
        return self.play_pcm16_mono(b"\x00\x00" * 16, 16000)

    def capture(self, seconds: float, hangover_ms: float = 0.0
                ) -> tuple[bytes, int, Endpoint]:
        self.probe()
        n = max(1, int(16000 * seconds))
        return b"\x00\x00" * n, 16000, self._probe.capture


# ---------------- AUDIO_OWNER honorer (clock is the sole writer) ----------------
def _ticket_default(tree_id: str, epoch: float) -> dict:
    return {
        "cvm": 1,
        "tree_id": tree_id,
        "audio_owner": "none",
        "AUDIO_OWNER": "AUDIO_NONE",
        "owner": "",
        "issued_epoch": epoch,
        "reason": "unclaimed",
    }


def require_sole_writer(d: dict) -> int:
    """H13 one-truth: PULL_CLOCK_ID stamps state/cvm/pull.json, nothing else.

    The CLOCKS registry has 15=pool and 16=CVM satellite (audio/ux); both
    DEFER this file — `cosmos_cvm_push.stamp_desktop_pull` forces
    clock_id=PULL_CLOCK_ID on every write. A ticket carrying any other id (or
    none) was not written by the clock, and an unauthoritative ticket must not
    grant the mic/sink. Refused UNREACHABLE: a foreign ticket is no ticket.
    ONE helper — honor, gate and the voice loop all read through it.
    """
    try:
        cid = int(d.get("clock_id") or 0)
    except (TypeError, ValueError):
        cid = 0
    if cid != int(PULL_CLOCK_ID):
        raise CvmDtError(
            RefusalKind.UNREACHABLE,
            "pull.json clock_id=%r is not id%s sole writer"
            % (d.get("clock_id"), PULL_CLOCK_ID))
    return cid


def _owner_fields(d: dict) -> tuple[str, str]:
    """Map a pull ticket to (AUDIO_NONE|AUDIO_OWNED, owner id).

    PR-1 clock writes audio_owner in {none, desktop, phone} on pull.json.
    Also accept AUDIO_OWNER in {AUDIO_NONE, AUDIO_OWNED} plus owner id.
    """
    kind = str(d.get("AUDIO_OWNER") or "").strip()
    who = str(d.get("owner") or d.get("owner_id") or "").strip()
    raw = str(d.get("audio_owner") or "").strip()
    if kind == "AUDIO_NONE":
        return "AUDIO_NONE", ""
    if kind == "AUDIO_OWNED":
        oid = who or (raw if raw not in ("", "none", "AUDIO_NONE", "AUDIO_OWNED") else "")
        return "AUDIO_OWNED", oid
    if raw in OWNERS:
        return ("AUDIO_NONE", "") if raw == "none" else ("AUDIO_OWNED", raw)
    if not raw:
        return "AUDIO_NONE", ""
    return "AUDIO_OWNED", raw


def audio_owner_of(d: dict) -> str:
    """Canonical AUDIO_OWNER token. ONE helper (H9) for honor + handoff.

    Returns phone|desktop|none, or a non-canonical occupied holder (never
    silently free). Honor and contest both call this; do not re-parse.
    """
    if not isinstance(d, dict):
        return "none"
    kind, who = _owner_fields(d)
    if kind == "AUDIO_NONE":
        return "none"
    return who or "none"


def require_single_owner(current: str, want: str) -> str:
    """H6 grant. Occupied by another holder → OWNER_CONTESTED (never two)."""
    w = str(want or "").strip()
    if w not in OWNERS:
        raise CvmDtError(
            RefusalKind.BAD_REQUEST,
            "audio_owner must be phone|desktop|none, not %r" % (want,))
    cur = str(current or "none").strip() or "none"
    if cur == "none" or cur == w:
        return w
    raise CvmDtError(
        RefusalKind.OWNER_CONTESTED,
        "audio_owner=%s contested by %s (H6 single owner)" % (cur, w))


class AudioLease:
    """Read-only AUDIO_OWNER honorer. The CVM clock is the sole writer.

    Slice-1 acquire/release/_write are gone (H13 / PR-2). DT never stamps
    holder_pid or audio_owner onto the ticket. Capture/play only when the
    ticket is AUDIO_NONE or AUDIO_OWNED by desktop, and only when the ticket
    came from the sole writer — `read` refuses a foreign clock_id, so no
    consumer ever sees an unauthoritative ticket's fields.
    """

    def __init__(self, path: Path, tree_id: str, client_id: str = CLIENT_ID,
                 clock: Callable[[], float] = time.time, ttl_s: float = LEASE_TTL_S):
        self.path = Path(path)
        self.tree_id = tree_id
        self.client_id = client_id
        self._clock = clock
        self.ttl_s = float(ttl_s)

    def read(self) -> dict:
        if not self.path.exists():
            return _ticket_default(self.tree_id, 0.0)
        try:
            d = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as e:
            raise CvmDtError(RefusalKind.AUDIO_OWNED,
                             "pull ticket unreadable (fail closed): %s" % e) from e
        if not isinstance(d, dict):
            raise CvmDtError(RefusalKind.AUDIO_OWNED,
                             "pull ticket is not an object (fail closed)")
        require_sole_writer(d)
        return d

    def current(self) -> dict:
        d = self.read()
        now = float(self._clock())
        tid = d.get("tree_id")
        if tid and tid != self.tree_id:
            raise CvmDtError(
                RefusalKind.IDENTITY_MISMATCH,
                "pull ticket tree_id=%r != %r" % (tid, self.tree_id))
        try:
            epoch = float(d.get("issued_epoch") or d.get("measured_epoch") or 0.0)
        except (TypeError, ValueError):
            epoch = 0.0
        if epoch and (now - epoch) > self.ttl_s:
            d = _ticket_default(self.tree_id, now)
            d["reason"] = "CLOCK_STALE"
        else:
            d = dict(d)
        kind, who = _owner_fields(d)
        d["AUDIO_OWNER"] = kind
        d["owner"] = who
        d["audio_owner"] = who if kind == "AUDIO_OWNED" else "none"
        return d

    def allows(self, d: Optional[dict] = None, *, armed: bool = False) -> bool:
        """H6/§6.2: desktop always; an UNCLAIMED sink only when DT is armed."""
        cur = d if isinstance(d, dict) else self.current()
        who = audio_owner_of(cur)
        return who == "desktop" or (who == "none" and bool(armed))


# ---------------- Core HTTP client ----------------
class CoreClient:
    """HTTP CLIENT of Core. No listen socket. Abort closes the in-flight conn."""

    def __init__(self, base: str, token: str):
        u = urlparse(base)
        if u.scheme not in ("http", "https") or not u.hostname:
            raise CvmDtError(RefusalKind.BAD_REQUEST, "core base is not an http(s) URL")
        self.base = base.rstrip("/")
        self.host = u.hostname
        self.port = u.port or (443 if u.scheme == "https" else 80)
        self.tls = u.scheme == "https"
        self._token = token
        self._conn: Optional[http.client.HTTPConnection] = None
        self._lock = threading.Lock()
        self._aborted = threading.Event()

    def abort(self) -> None:
        self._aborted.set()
        with self._lock:
            if self._conn is not None:
                try:
                    self._conn.close()
                except OSError:
                    pass
                self._conn = None

    def reset_stop(self) -> None:
        self._aborted.clear()

    def _headers(self, extra: Optional[dict] = None) -> dict:
        h = {
            "Authorization": "Bearer " + self._token,
            "Accept": "application/json",
            "Connection": "close",
        }
        if extra:
            h.update(extra)
        return h

    def _request(self, method: str, path: str, body: Optional[bytes],
                 timeout: float) -> dict:
        if self._aborted.is_set():
            raise CvmDtError(RefusalKind.STOPPED, "in-flight request aborted")
        klass = http.client.HTTPSConnection if self.tls else http.client.HTTPConnection
        conn = klass(self.host, self.port, timeout=float(timeout))
        with self._lock:
            self._conn = conn
        try:
            headers = self._headers({"Content-Type": "application/json"} if body is not None else None)
            if body is not None:
                headers["Content-Length"] = str(len(body))
            conn.request(method, path, body=body, headers=headers)
            resp = conn.getresponse()
            raw = resp.read()
            try:
                data = json.loads(raw.decode("utf-8")) if raw else {}
            except ValueError as e:
                raise CvmDtError(RefusalKind.BAD_CORE,
                                 "non-JSON from %s %s: %s" % (method, path, e)) from e
            if not isinstance(data, dict):
                raise CvmDtError(RefusalKind.BAD_CORE, "JSON object required from Core")
            data["_http"] = int(resp.status)
            if resp.status == 401:
                raise CvmDtError(RefusalKind.UNAUTHORIZED, "Core returned 401 UNAUTHORIZED")
            return data
        except CvmDtError:
            raise
        except TimeoutError as e:   # socket.timeout IS TimeoutError (3.10+)
            if self._aborted.is_set():
                raise CvmDtError(RefusalKind.STOPPED, "aborted during %s %s" % (method, path)) from e
            raise CvmDtError(RefusalKind.UNREACHABLE,
                             "timeout after %.0fs on %s %s" % (timeout, method, path)) from e
        except (ConnectionError, OSError) as e:
            if self._aborted.is_set():
                raise CvmDtError(RefusalKind.STOPPED, "aborted during %s %s" % (method, path)) from e
            raise CvmDtError(RefusalKind.UNREACHABLE,
                             "Core %s: %s" % (self.base, e)) from e
        finally:
            try:
                conn.close()
            except OSError:
                pass
            with self._lock:
                if self._conn is conn:
                    self._conn = None

    def get(self, path: str, timeout: float = FAST_READ_S) -> dict:
        return self._request("GET", path, None, timeout)

    def post(self, path: str, obj: dict, timeout: float) -> dict:
        body = json.dumps(obj).encode("utf-8")
        return self._request("POST", path, body, timeout)

    def status(self) -> dict:
        return self.get("/api/v1/status", FAST_READ_S)

    def control(self, client_id: str = CLIENT_ID) -> dict:
        return self.get("/api/v1/control?client_id=" + client_id, FAST_READ_S)

    def voice(self, body: dict) -> dict:
        return self.post("/api/v1/voice", body, VOICE_READ_S)


def pull_url(client_id: str) -> str:
    """GET /api/v1/cvm/pull?client_id=… — one builder, no second query string."""
    return PULL_PATH + "?client_id=" + quote(str(client_id), safe="")


def refuse_http(data: dict, *, default_400: Optional[RefusalKind] = None) -> None:
    """Typed refusal on non-2xx. ONE mapping for GET /cvm/pull and POST /cvm/snapshot.

    Never silent. Dead/missing route → UNREACHABLE (H3). 400 on snapshot
    defaults to BAD_SNAPSHOT; 400 on pull defaults to BAD_REQUEST.
    """
    try:
        code = int(data.get("_http") or 0)
    except (TypeError, ValueError):
        code = 0
    if 200 <= code < 300:
        return
    err = str(data.get("error") or "").strip()
    detail = str(data.get("detail") or err or ("HTTP_%s" % code))[:300]
    if code == 401 or err in ("UNAUTHORIZED", "AUTH_REQUIRED"):
        raise CvmDtError(RefusalKind.UNAUTHORIZED, detail)
    if err == "IDENTITY_MISMATCH":
        raise CvmDtError(RefusalKind.IDENTITY_MISMATCH, detail)
    if err == "OWNER_CONTESTED":
        raise CvmDtError(RefusalKind.OWNER_CONTESTED, detail)
    if err == "BAD_SNAPSHOT":
        raise CvmDtError(RefusalKind.BAD_SNAPSHOT, detail)
    if err == "CURSOR_GAP":
        raise CvmDtError(RefusalKind.CURSOR_GAP, detail)
    if err == "CLIENT_ID_REQUIRED":
        raise CvmDtError(RefusalKind.BAD_REQUEST, detail)
    if code == 400:
        kind = default_400 or RefusalKind.BAD_REQUEST
        raise CvmDtError(kind, detail or "HTTP_400")
    if code == 404 or err in ROAD_KINDS or code == 0:
        raise CvmDtError(RefusalKind.UNREACHABLE,
                         detail or "CVM Core route failed")
    raise CvmDtError(RefusalKind.BAD_CORE, detail)


def core_get(core: CoreClient, path: str, timeout: float = FAST_READ_S) -> dict:
    """GET JSON object. Dead Core / !=200 → typed refusal. Never silent."""
    try:
        data = core.get(path, timeout)
    except CvmDtError:
        raise
    except OSError as e:
        raise CvmDtError(RefusalKind.UNREACHABLE,
                         "GET %s: %s" % (path, e)) from e
    if not isinstance(data, dict):
        raise CvmDtError(RefusalKind.BAD_CORE,
                         "GET %s did not return an object" % path)
    refuse_http(data)
    return data


def core_post(core: CoreClient, path: str, obj: dict,
              timeout: float = FAST_READ_S, *,
              default_400: Optional[RefusalKind] = None) -> dict:
    """POST JSON object. Dead Core / !=200 → typed refusal. Never silent."""
    try:
        data = core.post(path, obj, timeout)
    except CvmDtError:
        raise
    except OSError as e:
        raise CvmDtError(RefusalKind.UNREACHABLE,
                         "POST %s: %s" % (path, e)) from e
    if not isinstance(data, dict):
        raise CvmDtError(RefusalKind.BAD_CORE,
                         "POST %s did not return an object" % path)
    refuse_http(data, default_400=default_400)
    return data


def voice_body(transcript: str, session_id: Optional[str] = None,
               confirm_id: Optional[str] = None, action: str = "",
               stream: str = "", title: str = "cvm-dt") -> dict:
    """The same envelope the phone sends. request_id is telemetry; Core uses
    idempotency_key for the 15 s dedupe window."""
    rid = uuid.uuid4().hex
    d: dict[str, Any] = {
        "transcript": transcript,
        "mode": "voice",
        "client_id": CLIENT_ID,
        "build": BUILD,
        "idempotency_key": rid,
        "request_id": rid,
        "title": title[:200],
    }
    if session_id:
        d["session_id"] = session_id
    if confirm_id:
        d["confirm_id"] = confirm_id
    if action:
        d["action"] = action
    if stream:
        d["stream"] = stream
    return d


# ---------------- SAPI TTS → WAV (stdlib COM IDispatch) ----------------
# Module level, not rebuilt per utterance, and reachable from the tests — the
# two ABI defects below were invisible while this lived inside the function.
class _GUID(ctypes.Structure):
    _fields_ = (("Data1", ctypes.c_ulong), ("Data2", ctypes.c_ushort),
                ("Data3", ctypes.c_ushort), ("Data4", ctypes.c_ubyte * 8))


class _BRECORD(ctypes.Structure):
    """tagVARIANT's widest union member: two pointers.

    Omitting it makes VARIANT 16 bytes on x64 instead of 24, so the array
    stride is short and rgvarg[1] of every TWO-argument Invoke is read 8
    bytes early. Measured 2026-08-30: SpFileStream.Open(path, 3) answered
    DISP_E_BADVARTYPE and the desktop mouth was mute on every utterance.
    """
    _fields_ = (("pvRecord", ctypes.c_void_p), ("pRecInfo", ctypes.c_void_p))


class _VARIANT(ctypes.Structure):
    class _U(ctypes.Union):
        _fields_ = (("llVal", ctypes.c_longlong), ("bstrVal", ctypes.c_void_p),
                    ("pdispVal", ctypes.c_void_p), ("lVal", ctypes.c_int),
                    ("brecord", _BRECORD))
    _anonymous_ = ("u",)
    _fields_ = (("vt", ctypes.c_ushort), ("r1", ctypes.c_ushort),
                ("r2", ctypes.c_ushort), ("r3", ctypes.c_ushort), ("u", _U))


class _DISPPARAMS(ctypes.Structure):
    _fields_ = (("rgvarg", ctypes.POINTER(_VARIANT)),
                ("rgdispidNamedArgs", ctypes.POINTER(ctypes.c_int)),
                ("cArgs", ctypes.c_uint), ("cNamedArgs", ctypes.c_uint))


# 8 header bytes (vt + 3 reserved) + the widest union member (BRECORD).
VARIANT_ABI_BYTES = 8 + 2 * ctypes.sizeof(ctypes.c_void_p)
VT_I4, VT_BSTR, VT_DISPATCH = 3, 8, 9
DISPATCH_METHOD, DISPATCH_PROPERTYPUT, DISPATCH_PROPERTYPUTREF = 1, 4, 8
# BOTH put forms need rgdispidNamedArgs=[DISPID_PROPERTYPUT]. Testing only the
# PUTREF-less mask left AudioOutputStream answering DISP_E_PARAMNOTFOUND.
DISPATCH_PUT_ANY = DISPATCH_PROPERTYPUT | DISPATCH_PROPERTYPUTREF
DISPID_PROPERTYPUT = -3
LOCALE_USER_DEFAULT = 0x0400
_COM: dict[str, Any] = {}


def variant_abi_bytes() -> int:
    """Size of this build's VARIANT. Must equal VARIANT_ABI_BYTES."""
    return ctypes.sizeof(_VARIANT)


def _com() -> dict:
    """ole32 + oleaut32 with argtypes bound ONCE (was re-bound per utterance)."""
    if not _COM:
        if os.name != "nt":
            raise CvmDtError(RefusalKind.TTS_NONE, "SAPI is Windows-only")
        if variant_abi_bytes() != VARIANT_ABI_BYTES:
            raise CvmDtError(
                RefusalKind.TTS_NONE,
                "VARIANT is %d bytes, tagVARIANT is %d on this ABI — a short "
                "VARIANT misaligns rgvarg[1] on every 2-argument Invoke"
                % (variant_abi_bytes(), VARIANT_ABI_BYTES))
        # PRIVATE handles: ctypes.windll.ole32 is shared with wasapi, and
        # binding argtypes on it rebinds them for that module too (its GUID is
        # a different ctypes type — the call then dies on argument 1).
        ole, oleaut = ctypes.WinDLL("ole32"), ctypes.WinDLL("oleaut32")
        ole.CLSIDFromProgID.argtypes = [ctypes.c_wchar_p, ctypes.POINTER(_GUID)]
        ole.CLSIDFromProgID.restype = ctypes.HRESULT
        ole.CoCreateInstance.argtypes = [
            ctypes.POINTER(_GUID), ctypes.c_void_p, ctypes.c_ulong,
            ctypes.POINTER(_GUID), ctypes.POINTER(ctypes.c_void_p)]
        ole.CoCreateInstance.restype = ctypes.HRESULT
        oleaut.SysAllocString.argtypes = [ctypes.c_wchar_p]
        oleaut.SysAllocString.restype = ctypes.c_void_p
        oleaut.SysFreeString.argtypes = [ctypes.c_void_p]
        _COM.update(
            ole=ole, oleaut=oleaut,
            iid_null=_GUID(0, 0, 0, (ctypes.c_ubyte * 8)()),
            iid_dispatch=_GUID(
                0x00020400, 0, 0,
                (ctypes.c_ubyte * 8).from_buffer_copy(
                    bytes.fromhex("C000000000000046"))))
    return _COM


def _vtbl(punk, idx: int):
    lp = ctypes.cast(punk, ctypes.POINTER(ctypes.c_void_p))[0]
    return ctypes.cast(lp, ctypes.POINTER(ctypes.c_void_p))[idx]


def _com_create(progid: str):
    com = _com()
    clsid = _GUID()
    hr = com["ole"].CLSIDFromProgID(progid, ctypes.byref(clsid))
    if int(hr) < 0:
        raise CvmDtError(RefusalKind.TTS_NONE, "CLSIDFromProgID %s hr=0x%08X"
                         % (progid, int(hr) & 0xFFFFFFFF))
    punk = ctypes.c_void_p()
    hr = com["ole"].CoCreateInstance(
        ctypes.byref(clsid), None, 0x17, ctypes.byref(com["iid_dispatch"]),
        ctypes.byref(punk))
    if int(hr) < 0 or not punk.value:
        raise CvmDtError(RefusalKind.TTS_NONE, "CoCreate %s hr=0x%08X"
                         % (progid, int(hr) & 0xFFFFFFFF))
    return punk


def _com_dispid(punk, name: str) -> int:
    com = _com()
    names = (ctypes.c_wchar_p * 1)(name)
    ids = (ctypes.c_int * 1)()
    proto = ctypes.WINFUNCTYPE(
        ctypes.HRESULT, ctypes.c_void_p, ctypes.POINTER(_GUID),
        ctypes.POINTER(ctypes.c_wchar_p), ctypes.c_uint, ctypes.c_ulong,
        ctypes.POINTER(ctypes.c_int))
    proto(_vtbl(punk, 5))(punk, ctypes.byref(com["iid_null"]), names, 1,
                          LOCALE_USER_DEFAULT, ids)
    return int(ids[0])


def _com_invoke(punk, name: str, args: list,
                flags: int = DISPATCH_METHOD) -> None:
    """IDispatch::Invoke. rgvarg is REVERSE order; puts carry the named DISPID."""
    com = _com()
    did = _com_dispid(punk, name)
    n = len(args)
    arr = (_VARIANT * max(n, 1))()
    bstrs = []
    for i, a in enumerate(reversed(args)):
        if isinstance(a, int):
            arr[i].vt, arr[i].lVal = VT_I4, int(a)
        elif isinstance(a, ctypes.c_void_p):
            # Borrowed interface pointer (SAPI.AudioOutputStream putref).
            # Never VariantClear'd: we did not AddRef it.
            arr[i].vt, arr[i].pdispVal = VT_DISPATCH, a
        else:
            arr[i].vt = VT_BSTR
            arr[i].bstrVal = com["oleaut"].SysAllocString(str(a))
            bstrs.append(arr[i].bstrVal)
    named = ctypes.c_int(DISPID_PROPERTYPUT)
    dp = _DISPPARAMS()
    if n:
        dp.rgvarg, dp.cArgs = arr, n
    if flags & DISPATCH_PUT_ANY:
        dp.rgdispidNamedArgs, dp.cNamedArgs = ctypes.pointer(named), 1
    proto = ctypes.WINFUNCTYPE(
        ctypes.HRESULT, ctypes.c_void_p, ctypes.c_int, ctypes.POINTER(_GUID),
        ctypes.c_ulong, ctypes.c_ushort, ctypes.POINTER(_DISPPARAMS),
        ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p)
    try:
        proto(_vtbl(punk, 6))(punk, did, ctypes.byref(com["iid_null"]),
                              LOCALE_USER_DEFAULT, flags, ctypes.byref(dp),
                              None, None, None)
    finally:
        for b in bstrs:
            com["oleaut"].SysFreeString(b)


def _com_release(punk) -> None:
    if punk and punk.value:
        ctypes.WINFUNCTYPE(ctypes.c_ulong, ctypes.c_void_p)(_vtbl(punk, 2))(punk)


def _sapi_wav(text: str) -> bytes:
    """Synthesize `text` to a PCM WAV via SAPI.SpVoice / SpFileStream.

    Playback is WASAPI (caller plays the bytes). Named engine, not a silent
    Web-Speech fallback. Absence is TTS_NONE.
    """
    if os.name != "nt":
        raise CvmDtError(RefusalKind.TTS_NONE, "SAPI is Windows-only")
    text = (text or "").strip()
    if not text:
        return b""
    ensure_com()
    _com()
    import tempfile
    fd, wav_path = tempfile.mkstemp(prefix="cvm-dt-tts-", suffix=".wav")
    os.close(fd)
    voice = stream = None
    try:
        stream = _com_create("SAPI.SpFileStream")
        # Open(filename, SSFMCreateForWrite=3)
        _com_invoke(stream, "Open", [wav_path, 3])
        voice = _com_create("SAPI.SpVoice")
        _com_invoke(voice, "AudioOutputStream", [stream],
                    DISPATCH_PROPERTYPUTREF)
        _com_invoke(voice, "Speak", [text, 0])
        _com_invoke(stream, "Close", [])
        data = Path(wav_path).read_bytes()
        if len(data) < 44:
            raise CvmDtError(RefusalKind.TTS_NONE, "SAPI wrote an empty WAV")
        return data
    except CvmDtError:
        raise
    except OSError as e:
        raise CvmDtError(RefusalKind.TTS_NONE, "SAPI COM failed: %s" % e) from e
    finally:
        if voice is not None:
            _com_release(voice)
        if stream is not None:
            _com_release(stream)
        try:
            os.unlink(wav_path)
        except OSError:
            pass


# ---------------- Facade ----------------
class CvmDt:
    def __init__(self, paths: CosmosPaths, core: CoreClient,
                 audio: AudioBackend, lease: AudioLease,
                 arm: bool = False):
        self.paths = paths
        self.core = core
        self.audio = audio
        self.lease = lease
        self.arm = bool(arm)
        self.session_id: Optional[str] = None

    def probe(self) -> Probe:
        return self.audio.probe()

    def honor_audio(self) -> dict:
        """Read the pull-clock ticket and probe WASAPI. Never writes the owner."""
        rec = self.ensure_can_speak()
        p = self.audio.probe()
        out = dict(rec)
        out["device_name"] = p.render.device_name
        out["device_id"] = p.render.device_id
        out["is_bt"] = p.render.is_bt
        return out

    def ensure_can_speak(self) -> dict:
        cur = self.lease.current()
        if self.lease.allows(cur, armed=self.arm):
            return cur
        if audio_owner_of(cur) == "none":
            raise CvmDtError(
                RefusalKind.AUDIO_UNARMED,
                "refusing to capture/play; AUDIO_OWNER=none and DT is not "
                "armed: pass --arm to speak on an unclaimed sink (H6)")
        raise CvmDtError(
            RefusalKind.AUDIO_OWNED,
            "refusing to capture/play; AUDIO_OWNER=%s owner=%s (H6 exclusive)"
            % (cur.get("AUDIO_OWNER"), cur.get("owner") or cur.get("audio_owner")))

    def honor_control(self) -> dict:
        st = self.core.control(self.lease.client_id)
        eff = st.get("effective") or {}
        if eff.get("mic_off") or eff.get("pause"):
            why = "MIC_OFF" if eff.get("mic_off") else "PAUSED"
            raise CvmDtError(
                RefusalKind.CONTROL_BLOCKED,
                "voice is %s — GET /api/v1/control; resume is POST /api/v1/control/resume"
                % why)
        if eff.get("clear_queue"):
            self.core.abort()
        return st

    def ask(self, transcript: str, session_id: Optional[str] = None,
            speak: bool = True, title: str = "cvm-dt", cancel=None) -> dict:
        """POST /api/v1/voice and optionally speak. One HTTP+TTS authority.

        Keeps `_http` and sets `rc` so the voice loop can quote the bind
        without forking CoreClient. `cvm_dt_voice` calls this — it does not
        reimplement the POST / Piper-or-SAPI path. cancel is the barge-in token.
        """
        self.ensure_can_speak()
        self.honor_control()
        sid = session_id if session_id is not None else self.session_id
        body = voice_body(transcript, session_id=sid, title=title)
        out = self.core.voice(body)
        http = int(out.get("_http") or 200)
        out["rc"] = http
        if http == 400:
            raise CvmDtError(RefusalKind.BAD_CORE,
                             "voice 400 %s" % out.get("error"))
        sid_out = out.get("session_id")
        if sid_out:
            self.session_id = str(sid_out)
        if out.get("error") == "CONTROL_BLOCKED":
            raise CvmDtError(RefusalKind.CONTROL_BLOCKED, str(out.get("reply") or ""))
        spoken = str(out.get("spoken") or "")
        kind = str(out.get("kind") or "")
        played = None
        if speak and spoken and kind != "dictation":
            played = self.speak(spoken, cancel=cancel)
        out["tts"] = played
        return out

    def resume(self, session_id: str, transcript: str, speak: bool = True) -> dict:
        """Continue the same COSMOS sid — this is voice resume, not control/resume."""
        if not session_id:
            raise CvmDtError(RefusalKind.BAD_REQUEST, "resume requires session_id")
        return self.ask(transcript, session_id=session_id, speak=speak)

    def speak(self, spoken: str, cancel=None) -> dict:
        self.ensure_can_speak()
        engine = "sapi"
        voice_id = "SAPI"
        wav = b""
        try:
            import cvm_tts_piper as _piper
            if _piper.ready():
                wav = _piper.synthesize_wav(spoken)
                engine = "piper"
                voice_id = _piper.VOICE_ID
        except Exception:
            wav = b""
        if not wav:
            wav = _sapi_wav(spoken)
            engine = "sapi"
            voice_id = "SAPI"
        ep = self.audio.play_wav(wav, cancel=cancel)
        return {"engine": engine + "+wasapi", "voice_id": voice_id,
                "device_name": ep.device_name,
                "device_id": ep.device_id, "bytes": len(wav)}

    def listen(self, seconds: float = 2.0) -> dict:
        """Capture-only. STT + POST live on CvmDtVoice.turn (one ear path)."""
        self.ensure_can_speak()
        self.honor_control()
        pcm, rate, ep = self.audio.capture(seconds)
        return {
            "device_name": ep.device_name,
            "device_id": ep.device_id,
            "rate": rate,
            "pcm_bytes": len(pcm),
        }

    def stop(self) -> None:
        self.core.abort()

    def close(self) -> None:
        self.core.abort()


def make_dt(root: str | os.PathLike, base: str, *,
            arm: bool = False, audio: Optional[AudioBackend] = None,
            token: Optional[str] = None) -> CvmDt:
    """One constructor for the CLI and cvm_dt_voice. Not a second client."""
    paths = load_paths(root)
    lease = AudioLease(paths.state(*LEASE_REL), paths.sentinel.tree_id)
    return CvmDt(paths, CoreClient(base, token if token is not None else load_token(paths)),
                 audio or WasapiBackend(), lease, arm=bool(arm))


# ---------------- selftest (green log, not stage 6) ----------------
def run_selftest() -> dict:
    import tempfile
    tmp = Path(tempfile.mkdtemp(prefix="cvm-dt-selftest-"))
    sent = {"system": "COSMOS", "tree_id": "KMesh-COSMOS-live", "schema_version": 1}
    (tmp / ".cosmos-root.json").write_text(json.dumps(sent), encoding="utf-8")
    (tmp / "config").mkdir()
    (tmp / "state").mkdir()
    (tmp / "config" / "api_token.txt").write_text("selftest-token-not-live", encoding="utf-8")
    paths = CosmosPaths(tmp)
    pull_p = paths.state(*LEASE_REL)
    pull_p.parent.mkdir(parents=True, exist_ok=True)
    ticket = {
        "cvm": 1,
        "tree_id": paths.sentinel.tree_id,
        "issued_epoch": time.time(),
        "pull": True,
        "audio_owner": "desktop",
        "clock_id": PULL_CLOCK_ID,
    }
    pull_p.write_text(json.dumps(ticket), encoding="utf-8")
    before = pull_p.read_bytes()
    audio = FakeBackend(name="Headphones (FAKE HT3)")
    lease = AudioLease(pull_p, paths.sentinel.tree_id)
    rec = lease.current()
    desktop_ok = lease.allows(rec) and rec["audio_owner"] == "desktop"
    wrote = pull_p.read_bytes() != before
    none_audio = FakeBackend(none=True)
    none_kind = None
    try:
        none_audio.probe()
    except CvmDtError as e:
        none_kind = str(e.kind)
    ticket["audio_owner"] = "phone"
    pull_p.write_text(json.dumps(ticket), encoding="utf-8")
    phone_bytes = pull_p.read_bytes()
    owned_kind = None
    try:
        CvmDt(paths, CoreClient("http://127.0.0.1:1", "x"), audio, lease).ensure_can_speak()
    except CvmDtError as e:
        owned_kind = str(e.kind)
    phone_untouched = pull_p.read_bytes() == phone_bytes
    # NEGATIVE: an id16-stamped ticket is not the sole writer's. It must be
    # refused even though it says audio_owner=desktop (H13 one truth).
    ticket["audio_owner"], ticket["clock_id"] = "desktop", 16
    pull_p.write_text(json.dumps(ticket), encoding="utf-8")
    foreign_kind = None
    try:
        lease.current()
    except CvmDtError as e:
        foreign_kind = str(e.kind)
    audio_json = tmp / "state" / "cvm" / "audio.json"
    body1 = voice_body("status")
    body2 = voice_body("help", session_id="deadbeef" * 4)
    t, off = _now()
    ok = (
        desktop_ok
        and rec["AUDIO_OWNER"] == "AUDIO_OWNED"
        and rec["owner"] == "desktop"
        and none_kind == RefusalKind.AUDIO_NONE
        and owned_kind == RefusalKind.AUDIO_OWNED
        and foreign_kind == RefusalKind.UNREACHABLE
        and not wrote
        and phone_untouched
        and not audio_json.exists()
        and not hasattr(AudioLease, "acquire")
        and not hasattr(AudioLease, "release")
        and "session_id" not in body1
        and body2["session_id"] == "deadbeef" * 4
        and FAST_READ_S == 8.0
        and VOICE_READ_S == 70.0
        and VOICE_READ_S > FAST_READ_S
    )
    return {
        "selftest": "ok" if ok else "FAIL",
        "live_value": {
            "audio_owner": rec["audio_owner"],
            "AUDIO_OWNER": rec["AUDIO_OWNER"],
            "AUDIO_NONE": none_kind,
            "AUDIO_OWNED": owned_kind,
            "sole_writer_clock_id": PULL_CLOCK_ID,
            "foreign_clock_id_16": foreign_kind,
            "wrote_owner": bool(wrote or (not phone_untouched) or audio_json.exists()),
            "voice_timeout_s": VOICE_READ_S,
            "fast_timeout_s": FAST_READ_S,
        },
        "epoch": t,
        "utc_offset_s": off,
        "note": "loopback selftest is a green log, not stage 6",
    }


# ---------------- stage-6 gate ----------------
def _opened_mix(backend: AudioBackend) -> dict:
    """WAVEFORMATEX the render endpoint just opened on (hardware-measured).

    A device NAME can be typed by anyone; the shared-mode mix format comes
    out of IAudioClient::GetMixFormat on the endpoint this process opened.
    Empty for an injected backend — the fake never opened Windows audio.
    """
    if not isinstance(backend, WasapiBackend):
        return {}
    try:
        return dict(route_status().get("mix_render") or {})
    except AudioNoneError:
        return {}


def _mix_sig(mix: dict) -> str:
    """One-token mix signature for `emitted` (rate x channels x bits)."""
    if not mix:
        return "NO_MIX"
    return "%sx%sx%s%s" % (mix.get("rate"), mix.get("channels"),
                           mix.get("bits"), "f" if mix.get("is_float") else "i")


#: AUDIO_OWNER tokens under which an ARMED desktop may drive the sink.
#: "desktop" is our own claim; "none" is an UNCLAIMED sink, which arming takes.
#: Any other token is somebody else's hold and is honored (fail-closed).
SINK_OWNERS_OK = frozenset({"desktop", "none"})


def sink_granted(a: dict) -> bool:
    """Did HALF A prove THIS desktop drives the Windows default sink?

    The ONE predicate both gates ask, so they cannot drift. `cvm_gate.py`
    (split gate) and `run_gate` (whole-record gate) disagreed on exactly one
    token: run_gate demanded `audio_owner == "desktop"` and so scored an
    UNCLAIMED sink as a failed gate, while the split half scored the same
    reading PASS ("unclaimed sink, explicitly armed"). Two gates, one box,
    opposite verdicts off one string — the drift this collapses.

    `device_name_matches_windows_default` is NOT a bare probe comparison: it
    is re-asserted against the endpoint the earcon actually rendered on
    (gate_audio), so a True here means audio really came out of the device
    Windows calls default. An unreadable or foreign-clock ticket
    (`lease_kind`) never grants, whatever the owner token says.
    """
    return bool(a.get("device_name_matches_windows_default")
                and not a.get("lease_kind")
                and (a.get("audio_owner") or "none") in SINK_OWNERS_OK)


def gate_audio(backend: AudioBackend, lease: AudioLease,
               *, armed: bool = True) -> dict:
    """HALF A of stage 6 — WASAPI identity + the earcon. NO Core, ever.

    Split out of `run_gate` so the half that needs nothing but this box is
    not blocked by the half that needs the resident authority. `run_gate`
    and `cvm_gate local` call THIS function, so the two cannot drift.

    A missing default device is AUDIO_NONE (passing refusal, never a
    fabricated device_name); a ticket held by the phone, or stamped by a
    foreign clock, is a typed `lease_kind` — legible, and it still cannot
    grant the sink.
    """
    out = {
        "device_name": "", "device_id": "",
        "windows_default_name": "", "windows_default_id": "",
        "device_name_matches_windows_default": False,
        "earcon_device_name": "", "mix_render": {},
        "audio_owner": "none", "audio_kind": None, "lease_kind": None,
    }
    try:
        p = backend.probe()
        out["device_name"] = p.render.device_name
        out["device_id"] = p.render.device_id
        # SECOND, independent read of the Windows default. Quoting one probe
        # twice compares a value to itself and always "matches".
        wd = backend.windows_default()
        out["windows_default_name"] = wd.device_name
        out["windows_default_id"] = wd.device_id
        match = (out["device_id"] == wd.device_id
                 and out["device_name"] == wd.device_name
                 and bool(out["device_name"]))
        out["device_name_matches_windows_default"] = match
        try:
            cur = lease.current()
            out["audio_owner"] = cur.get("audio_owner") or "none"
            allowed = lease.allows(cur, armed=armed)
        except CvmDtError as e:
            # Unreadable / foreign-clock / wrong-tree ticket: fail closed and
            # SAY WHICH. A refusal we cannot name is a refusal we cannot fix.
            out["lease_kind"] = str(e.kind)
            allowed = False
        if not allowed and out["lease_kind"] is None:
            out["audio_kind"] = str(RefusalKind.AUDIO_OWNED)
        elif allowed:
            try:
                ep = backend.play_earcon()
                out["earcon_device_name"] = ep.device_name
                out["device_name_matches_windows_default"] = (
                    match and ep.device_id == wd.device_id)
                out["mix_render"] = _opened_mix(backend)
            except CvmDtError as e:
                if e.kind != RefusalKind.AUDIO_NONE:
                    raise
                out["audio_kind"] = str(e.kind)
    except CvmDtError as e:
        if e.kind != RefusalKind.AUDIO_NONE:
            raise
        out["audio_kind"] = str(e.kind)
        out["audio_owner"] = "none"
    return out


def gate_core(core: CoreClient, tree_id: str, *,
              on_spoken: Optional[Callable[[str], None]] = None) -> dict:
    """HALF B of stage 6 — the part that genuinely needs the resident Core.

    /status tree_id, /control, then a `/voice` sid that `resume` keeps. A
    dead Core is `core_kind=UNREACHABLE` — a typed, legible absence. There
    is NO substitute server: a trial kernel answering on another port would
    prove that the trial kernel is up, which is not the claim.
    """
    out = {"status": None, "control": None, "mint": None, "resumed": None,
           "session_id": None, "resume_session_id": None,
           "session_ok": False, "core_kind": None, "spoken": ""}
    try:
        status = core.status()
        out["status"] = status
        if str(status.get("tree_id") or "") != tree_id:
            raise CvmDtError(
                RefusalKind.IDENTITY_MISMATCH,
                "GET /status tree_id=%r != sentinel %r"
                % (status.get("tree_id"), tree_id))
        control = core.control(CLIENT_ID)
        out["control"] = control
        eff = control.get("effective") or {}
        if eff.get("mic_off") or eff.get("pause"):
            raise CvmDtError(RefusalKind.CONTROL_BLOCKED,
                             "control blocks voice: %s" % eff)
        # Read-only commander verbs: no Opus spend, still a real /voice sid.
        nonce = uuid.uuid4().hex[:12]
        mint = core.voice(voice_body("status", title="cvm-dt-gate-" + nonce))
        out["mint"] = mint
        session_id = str(mint.get("session_id") or "")
        out["session_id"] = session_id
        if not session_id:
            raise CvmDtError(RefusalKind.BAD_CORE, "minted /voice returned no session_id")
        resumed = core.voice(voice_body("help", session_id=session_id,
                                        title="cvm-dt-gate-" + nonce))
        out["resumed"] = resumed
        out["resume_session_id"] = str(resumed.get("session_id") or "")
        out["session_ok"] = session_id == out["resume_session_id"]
        if not out["session_ok"]:
            raise CvmDtError(
                RefusalKind.BAD_CORE,
                "resume sid %r != mint sid %r"
                % (out["resume_session_id"], session_id))
        out["spoken"] = str(resumed.get("spoken") or mint.get("spoken") or "")
        if on_spoken is not None and out["spoken"] and resumed.get("kind") != "dictation":
            on_spoken(out["spoken"])
    except CvmDtError as e:
        out["core_kind"] = str(e.kind)
    return out


def run_gate(root: str | os.PathLike, base: str,
             proof_path: Optional[str] = None,
             audio: Optional[AudioBackend] = None,
             speak: bool = True) -> dict:
    """Runtime-binding: WASAPI default device_name + /voice sid that resume keeps.

    The WHOLE stage-6 record — both halves in one artifact. When Core is
    down this refuses; `cvm_gate.py` runs the halves separately so half A
    still lands its numbers. Both call gate_audio/gate_core, not a copy.

    rc=0 is not the gate. Quote live_value. AUDIO_NONE is a passing refusal
    when the default device is missing — never a fabricated device_name.
    Core down is UNREACHABLE, not a trial kernel on another port.
    """
    src = Path(__file__).resolve()
    paths = load_paths(root)
    tree_id = paths.sentinel.tree_id
    token = load_token(paths)
    backend = audio or WasapiBackend()
    lease = AudioLease(paths.state(*LEASE_REL), tree_id)
    core = CoreClient(base, token)
    t, off = _now()

    a = gate_audio(backend, lease, armed=True)   # gate IS the arming act
    audio_kind = a["audio_kind"]
    earcon_name = a["earcon_device_name"]

    def _say(spoken: str) -> None:
        nonlocal earcon_name
        if not speak or audio_kind is not None:
            return
        try:
            ep = backend.play_wav(_sapi_wav(spoken))
            earcon_name = ep.device_name or earcon_name
        except CvmDtError as e:
            # TTS_NONE is not a failed gate if WASAPI already rendered an earcon
            if e.kind not in (RefusalKind.TTS_NONE, RefusalKind.AUDIO_NONE):
                raise

    c = gate_core(core, tree_id, on_spoken=_say)
    status, mint, resumed = c["status"], c["mint"], c["resumed"]
    session_ok = c["session_ok"]

    device_ok = sink_granted(a)          # the shared predicate, not a copy
    none_ok = audio_kind == RefusalKind.AUDIO_NONE
    ok = bool((device_ok or none_ok) and session_ok)
    live_value = {
        "live_tree_id": tree_id,
        "status_tree_id": (status or {}).get("tree_id"),
        "served_at": (status or {}).get("served_at"),
        "ledger_seq": ((status or {}).get("ledger_head") or {}).get("seq"),
        "audio_owner": a["audio_owner"],
        "device_name": a["device_name"],
        "device_id": a["device_id"],
        "windows_default_name": a["windows_default_name"],
        "windows_default_id": a["windows_default_id"],
        "device_name_matches_windows_default": a["device_name_matches_windows_default"],
        "windows_default_read_independently": True,
        "earcon_device_name": earcon_name,
        "mix_render": a["mix_render"],
        "gate_armed": True,
        "AUDIO_NONE": audio_kind,
        "lease_kind": a["lease_kind"],
        "session_id": c["session_id"],
        "resume_session_id": c["resume_session_id"],
        "session_resumed_same_sid": session_ok,
        "mint_kind": (mint or {}).get("kind"),
        "resume_kind": (resumed or {}).get("kind"),
        "core_kind": c["core_kind"],
        "voice_timeout_s": VOICE_READ_S,
        "base": base,
    }
    rec = {
        "ok": ok,
        "stage": 6,
        "deliverable": "cvm-dt",
        "agent": "G46",
        "slice": "pr2",
        "gated_at_epoch": t,
        "utc_offset_s": off,
        "source_path": str(src),
        "source_sha256": _sha256_file(src),
        "source_bytes": src.stat().st_size,
        "live_root": str(Path(root).resolve()),
        "live_tree_id": tree_id,
        "live_system": paths.sentinel.system,
        "sentinel": str(paths.root / ".cosmos-root.json"),
        "python": sys.version.split()[0],
        "executable": sys.executable,
        "live_value": live_value,
        "wire": WIRE,
        "note": "rc=0 is not the gate. The live_value fields are. "
                "Loopback selftest is a green log, not this record. "
                "AUDIO_NONE is a passing refusal when the default device is missing.",
    }
    rec["emitted"] = "cvm-dt:%s:%s:%s:%s:%s" % (
        tree_id,
        c["session_id"] or (audio_kind or "NO_SID"),
        (a["device_name"] or audio_kind or "NO_DEVICE"),
        _mix_sig(a["mix_render"]),
        rec["source_sha256"],
    )
    dest = Path(proof_path) if proof_path else (src.parent / PROOF_NAME)
    rec["proof_path"] = str(dest.resolve())
    _atomic_install(dest, rec)
    if c["core_kind"] == RefusalKind.UNREACHABLE:
        # Proof is on disk with kind=UNREACHABLE. Do not invent a :8791 trial.
        raise CvmDtError(RefusalKind.UNREACHABLE,
                         "Core at %s is down — proof at %s" % (base, rec["proof_path"]))
    return rec


# ---------------- CLI ----------------
def main(argv: Optional[list[str]] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    # `voice` is the ear/mouth loop — parser lives on cvm_dt_voice (one CLI).
    if argv[:1] == ["voice"]:
        import cvm_dt_voice as _voice
        return _voice.voice_main(argv[1:])

    ap = argparse.ArgumentParser(
        prog="cvm-dt",
        description="COSMOS desktop voice client (WASAPI default device, HTTP client of Core)")
    sub = ap.add_subparsers(dest="verb", required=True)

    sub.add_parser("selftest", help="loopback honor + AUDIO_NONE, no Core, green log")
    sub.add_parser("voice",
                   help="ear/mouth loop (heartbeat + POST /api/v1/voice). See: cvm-dt voice -h")

    def add_root(p):
        p.add_argument("--root", required=True,
                       help="COSMOS runtime root (handed in; sentinel verified)")
        p.add_argument("--base", default="http://127.0.0.1:8770",
                       help="Core base URL (HTTP client; default loopback :8770)")
        p.add_argument("--arm", action="store_true",
                       help="allow DT when AUDIO_OWNER=none (explicit; mic still never auto-starts)")
        return p

    add_root(sub.add_parser("probe", help="print WASAPI default device or AUDIO_NONE"))
    add_root(sub.add_parser("lease", help="print AUDIO_OWNER from the pull-clock ticket (read-only honor)"))
    a = add_root(sub.add_parser("ask", help="POST /api/v1/voice and speak the reply"))
    a.add_argument("transcript")
    a.add_argument("--session-id", default="", help="existing sid to resume")
    a.add_argument("--no-speak", action="store_true")
    r = add_root(sub.add_parser("resume",
                                help="POST /api/v1/voice with an existing session_id (same sid)"))
    r.add_argument("session_id")
    r.add_argument("transcript")
    r.add_argument("--no-speak", action="store_true")
    L = add_root(sub.add_parser("listen", help="armed WASAPI capture (never auto-starts)"))
    L.add_argument("--seconds", type=float, default=2.0)
    add_root(sub.add_parser("stop", help="abort in-flight HTTP (no-op unless a client is held)"))
    g = add_root(sub.add_parser("gate", help="stage-6 runtime-binding against live Core + WASAPI"))
    g.add_argument("--proof", default="", help="proof JSON path (default: STAGE6_GATE.json beside this module)")

    ns = ap.parse_args(argv)

    if ns.verb == "selftest":
        rec = run_selftest()
        print(json.dumps(rec, indent=1))
        return 0 if rec["selftest"] == "ok" else 1

    def _dt() -> CvmDt:
        return make_dt(ns.root, ns.base, arm=getattr(ns, "arm", False))

    try:
        if ns.verb == "probe":
            p = WasapiBackend().probe()
            print(json.dumps({
                "render": {"device_name": p.render.device_name,
                           "device_id": p.render.device_id, "is_bt": p.render.is_bt},
                "capture": {"device_name": p.capture.device_name,
                            "device_id": p.capture.device_id, "is_bt": p.capture.is_bt},
                "communications_render_name": p.communications_render_name,
            }, indent=1))
            return 0
        if ns.verb == "gate":
            rec = run_gate(ns.root, ns.base, proof_path=ns.proof or None)
            print(json.dumps({
                "ok": rec["ok"],
                "stage": 6,
                "proof_path": rec["proof_path"],
                "emitted": rec["emitted"],
                "live_value": rec["live_value"],
            }, indent=1))
            return 0 if rec["ok"] else 1
        dt = _dt()
        try:
            if ns.verb == "lease":
                rec = dt.honor_audio()
                print(json.dumps(rec, indent=1))
                return 0
            if ns.verb == "ask":
                out = dt.ask(ns.transcript, session_id=ns.session_id or None,
                             speak=not ns.no_speak)
                print(json.dumps({k: out[k] for k in out if k != "tts"} | {
                    "tts": out.get("tts")}, indent=1, default=str))
                return 0
            if ns.verb == "resume":
                out = dt.resume(ns.session_id, ns.transcript, speak=not ns.no_speak)
                print(json.dumps(out, indent=1, default=str))
                return 0
            if ns.verb == "listen":
                print(json.dumps(dt.listen(ns.seconds), indent=1))
                return 0
            if ns.verb == "stop":
                dt.stop()
                print(json.dumps({"stopped": True}))
                return 0
        finally:
            dt.close()
    except CvmDtError as e:
        print(json.dumps({"ok": False, "status": "refused",
                          "kind": str(e.kind), "detail": str(e)}))
        return 2
    return 1


if __name__ == "__main__":
    sys.exit(main())
