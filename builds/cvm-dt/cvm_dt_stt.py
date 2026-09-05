#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cvm-dt EAR — on-box STT so the desktop voice client can actually hear.

The gap this closes (measured 2026-08-31, not asserted): every STT path in
this fence routed through `cosmos_cvm_push.probe_stt`, which requires BOTH the
`vosk` pip package AND `COSMOS_VOSK_MODEL`. On this box:

    vosk importable ............ False
    COSMOS_VOSK_MODEL .......... unset

so `probe_stt()` answered `STT_NONE` on every call, `default_transcriber()`
returned `None`, and `CvmDtVoice` reported `VOICE_UNAVAILABLE` for every
utterance. The desktop mouth worked; the desktop ear did not exist.
`docs/CVM_ARCH.md` H4 asks for a path that *cannot run out* — and one was
already installed:

    HKLM\\SOFTWARE\\Microsoft\\Speech\\Recognizers\\Tokens -> ['MS-1033-80-DESK']

Microsoft Speech Recognizer 8.0 (desktop, en-US), shipped with Windows. No
download, no pip, no model file, no key, no quota, no consent to lapse. That
is the strongest H4 candidate on the machine, so it becomes the ear FLOOR:
VOSK still wins when it is bound (same family as the phone, per CVM_ARCH
§6.3); SAPI catches the fall instead of `STT_NONE`.

    vosk bound  -> engine="vosk"  (unchanged; this module does not touch it)
    else SAPI   -> engine="sapi"  (NEW; nothing to install)
    else        -> STT_NONE       (typed refusal, never a fabricated word)

## Why the raw vtable bridge

SAPI's *automation* surface (`ISpeechRecoContext`) delivers results only
through IConnectionPoint events, which needs an IDispatch sink implemented in
ctypes. The C++ surface (`ISpRecoContext`, which inherits `ISpEventSource`)
exposes `GetEvents()` — a POLLING read. Polling has no sink, no message pump
and no window, so it works from a windowless `pythonw` daemon, which is
exactly the vehicle `cvm_dt_voice --loop` runs under.

## Every constant here was read off THIS box, not remembered

`_disposal/sapi_typelib_probe.py` and `_disposal/sapi_enum_probe.py` load
`C:\\Windows\\System32\\Speech\\Common\\sapi.dll`'s own typelib and dump the
IIDs, the vtable widths and the enum values; the results are checked in as
`_disposal/sapi_typelib.json` / `_disposal/sapi_enums.json`. `verify_abi()`
re-reads the typelib at runtime and refuses if any constant below disagrees,
so a wrong IID or a shifted vtable slot is a NAMED refusal at bind time
rather than an access violation later. `test_cvm_dt_stt.py` runs that check.

    py -3.14 builds\\cvm-dt\\cvm_dt_stt.py probe
    py -3.14 builds\\cvm-dt\\cvm_dt_stt.py verify
    py -3.14 builds\\cvm-dt\\cvm_dt_stt.py selftest      # mouth -> ear round trip
    py -3.14 builds\\cvm-dt\\cvm_dt_stt.py hear <file.wav>

rc=0 is not the gate. The gate is `selftest`'s `live_value`: a transcript the
box's own recognizer produced from audio the box's own synthesizer spoke,
plus the recognizer token id that produced it.
"""
from __future__ import annotations

import argparse
import ctypes
import io
import json
import os
import sys
import time
import wave
from pathlib import Path
from typing import Any, Optional

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from cvm_dt import (  # noqa: E402
    CvmDtError, RefusalKind, _com, _GUID, _vtbl,
)

WIRE = "cvm-dt-stt/1"
ENGINE = "sapi"
STT_RATE = 16000
SAPI_DLL = r"C:\Windows\System32\Speech\Common\sapi.dll"

# ---------------------------------------------------------------------------
# Measured ABI. Source: _disposal/sapi_typelib.json (this box's sapi.dll).
# `slots` is cbSizeVft/8 as the typelib reports it; the method indices below
# are only valid while the width matches, which verify_abi() enforces.
# ---------------------------------------------------------------------------
IID = {
    "ISpStream": "{12E3CCA9-7518-44C5-A5E7-BA5A79CB929E}",
    "ISpRecognizer": "{C2B5F241-DAA0-4507-9E16-5A1EAA2B7A5C}",
    "ISpRecoContext": "{F740A62F-7C15-489E-8234-940A33D9272D}",
    "ISpRecoGrammar": "{2177DB29-7F45-47D0-8554-067E91C80502}",
    "ISpRecoResult": "{20B053BE-E235-43CD-9A2A-8D17A48B7842}",
    "ISpPhrase": "{1A5C0354-B621-4B5A-8791-D306ED379E53}",
}
VTBL_SLOTS = {
    "ISpStream": 19, "ISpRecognizer": 23, "ISpRecoContext": 31,
    "ISpRecoGrammar": 29, "ISpRecoResult": 14, "ISpPhrase": 7,
}
# HKCR\SAPI.SpInprocRecognizer\CLSID and HKCR\SAPI.SpFileStream\CLSID, read
# 2026-08-31. Two stream CLSIDs are tried in order and the winner is REPORTED,
# because which one exposes ISpStream is a property of the box, not a guess.
CLSID_SP_INPROC_RECOGNIZER = "{41B89B6B-9399-11D2-9623-00C04F8EE628}"
CLSID_SP_STREAM = "{715D9C59-4442-11D2-9605-00C04F8EE628}"
CLSID_SP_FILE_STREAM = "{947812B3-2AE1-4644-BA86-9E90DED7EC91}"
CLSID_SP_OBJECT_TOKEN = "{EF411752-3736-4CB4-9C8C-8EF4CCB58EFE}"
IID_ISP_OBJECT_TOKEN = "{14056589-E16C-11D2-BB90-00C04F8EE6C0}"

# Where each recognizer token lives. Windows 10 carries two SR stacks and the
# desktop SpInprocRecognizer can be pinned to EITHER (measured: SetRecognizer
# returns S_OK for both). The DNN engine wins on accuracy — see ENGINE_ORDER.
TOKEN_ROOTS = {
    "desk": r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech"
            r"\Recognizers\Tokens",
    "onecore": r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech_OneCore"
               r"\Recognizers\Tokens",
}
# Preference order, set FROM the measurement in _disposal/sapi_engine_ab.py,
# not from the version numbers. The newer OneCore "Embedded DNN v11.1" engine
# is DELIBERATELY second: it binds (SetRecognizer -> S_OK) and then refuses
# LoadDictation with 0x8004503A, because it carries no free-text dictation
# topic. Ranking it first on its version number would have made every
# utterance a refusal. Unknown boxes fall through to whatever is installed;
# recognize_wav skips any engine that cannot load dictation.
ENGINE_ORDER = ("MS-1033-80-DESK", "MS-1033-110-WINMO-DNN")

# Vtable slots. IUnknown occupies 0..2 on every interface.
#   ISpStream       : ISpStreamFormat(15) + SetBaseStream/GetBaseStream/
#                     BindToFile/Close
#   ISpRecognizer   : ISpProperties(7) + 16 methods
#   ISpRecoContext  : ISpNotifySource(10) + ISpEventSource(3) + 18 methods
#   ISpRecoGrammar  : ISpGrammarBuilder(11) + 18 methods
#   ISpPhrase       : 3 GetPhrase, 4 GetSerializedPhrase, 5 GetText, 6 Discard
S_BIND_TO_FILE = 17
S_STREAM_CLOSE = 18
T_SET_ID = 15  # ISpObjectToken: ISpDataKey(15) + SetId
R_SET_RECOGNIZER = 7
R_SET_INPUT = 9
R_CREATE_RECO_CONTEXT = 12
R_SET_RECO_STATE = 17
C_SET_NOTIFY_WIN32_EVENT = 7
C_WAIT_FOR_NOTIFY_EVENT = 8
C_SET_INTEREST = 10
C_GET_EVENTS = 11
C_CREATE_GRAMMAR = 14
G_LOAD_DICTATION = 20
G_SET_DICTATION_STATE = 22
P_GET_TEXT = 5

# Measured. Source: _disposal/sapi_enums.json (SPEVENTENUM etc).
SPEI_END_SR_STREAM = 34
SPEI_RECOGNITION = 38
SPEI_FALSE_RECOGNITION = 43
SPEI_RESERVED1 = 30
SPEI_RESERVED2 = 33
SPRST_ACTIVE = 1
SPRST_INACTIVE = 0
SPRS_ACTIVE = 1
SPLO_STATIC = 0
SPFM_OPEN_READONLY = 0
SP_GETWHOLEPHRASE = 0xFFFFFFFF
CLSCTX_ALL = 0x17
S_FALSE = 1

# SAPI packs the reserved bits into every interest mask; omitting them makes
# SetInterest silently deliver nothing.
def SPFEI(event_id: int) -> int:
    """SAPI's SPFEI macro: the event bit plus the two reserved bits."""
    return ((1 << SPEI_RESERVED1) | (1 << SPEI_RESERVED2) | (1 << event_id))


class SPEVENT(ctypes.Structure):
    """sapi.h SPEVENT. 32 bytes on x64; two 16-bit bitfields share one DWORD."""
    _fields_ = (
        ("eEventId", ctypes.c_ushort), ("elParamType", ctypes.c_ushort),
        ("ulStreamNum", ctypes.c_ulong),
        ("ullAudioStreamOffset", ctypes.c_ulonglong),
        ("wParam", ctypes.c_size_t), ("lParam", ctypes.c_ssize_t),
    )


SPEVENT_ABI_BYTES = 32


def _guid(text: str) -> _GUID:
    """Build cvm_dt's _GUID (NOT wasapi's — the ole32 argtypes are bound to it)."""
    h = text.strip().strip("{}").replace("-", "")
    if len(h) != 32:
        raise CvmDtError(RefusalKind.STT_NONE, "bad GUID %r" % text)
    b = bytes.fromhex(h)
    return _GUID(int.from_bytes(b[0:4], "big"), int.from_bytes(b[4:6], "big"),
                 int.from_bytes(b[6:8], "big"),
                 (ctypes.c_ubyte * 8).from_buffer_copy(b[8:16]))


def _hr(hr, what: str) -> None:
    if int(hr) < 0:
        raise CvmDtError(RefusalKind.STT_NONE,
                         "%s hr=0x%08X" % (what, int(hr) & 0xFFFFFFFF))


def _call(punk, slot: int, restype, argtypes, *args):
    proto = ctypes.WINFUNCTYPE(restype, ctypes.c_void_p, *argtypes)
    return proto(_vtbl(punk, slot))(punk, *args)


def _hrcall(punk, slot: int, what: str, argtypes, *args) -> int:
    """A vtable call returning a RAW hr.

    `restype=ctypes.HRESULT` makes ctypes raise a bare `OSError: [WinError
    -2147200966]` before any of this module's code can name what failed —
    which is how an engine that simply lacks a dictation topic looked like a
    crash. Returning `c_long` keeps the refusal typed and NAMED, so
    `ISpRecoGrammar::LoadDictation hr=0x8004503A` is what the caller sees.
    """
    hr = int(_call(punk, slot, ctypes.c_long, argtypes, *args))
    if hr < 0:
        raise CvmDtError(RefusalKind.STT_NONE,
                         "%s hr=0x%08X" % (what, hr & 0xFFFFFFFF))
    return hr


def _release(punk) -> None:
    if punk and getattr(punk, "value", punk):
        _call(punk, 2, ctypes.c_ulong, ())


def _ensure_com() -> None:
    """Reuse wasapi's refcounted per-thread apartment. Do not open a second one."""
    import wasapi
    wasapi.ensure_com()


def _create(clsid: str, iid: str):
    """CoCreateInstance through cvm_dt's PRIVATE ole32 handle (bound argtypes)."""
    com = _com()
    _ensure_com()
    punk = ctypes.c_void_p()
    hr = com["ole"].CoCreateInstance(
        ctypes.byref(_guid(clsid)), None, CLSCTX_ALL,
        ctypes.byref(_guid(iid)), ctypes.byref(punk))
    if int(hr) < 0 or not punk.value:
        return None, int(hr) & 0xFFFFFFFF
    return punk, 0


# ---------------------------------------------------------------------------
# ABI verification — the constants above, re-read from the box at runtime
# ---------------------------------------------------------------------------
def read_typelib() -> dict:
    """IID + vtable width for every ISp* type, straight from sapi.dll."""
    oleaut = ctypes.WinDLL("oleaut32")
    oleaut.LoadTypeLib.argtypes = [ctypes.c_wchar_p,
                                   ctypes.POINTER(ctypes.c_void_p)]
    oleaut.LoadTypeLib.restype = ctypes.c_long
    tl = ctypes.c_void_p()
    _hr(oleaut.LoadTypeLib(SAPI_DLL, ctypes.byref(tl)),
        "LoadTypeLib %s" % SAPI_DLL)

    class _TA(ctypes.Structure):
        _fields_ = (("guid", _GUID), ("lcid", ctypes.c_ulong),
                    ("dwReserved", ctypes.c_ulong),
                    ("memidConstructor", ctypes.c_long),
                    ("memidDestructor", ctypes.c_long),
                    ("lpstrSchema", ctypes.c_void_p),
                    ("cbSizeInstance", ctypes.c_ulong),
                    ("typekind", ctypes.c_int),
                    ("cFuncs", ctypes.c_ushort), ("cVars", ctypes.c_ushort),
                    ("cImplTypes", ctypes.c_ushort),
                    ("cbSizeVft", ctypes.c_ushort),
                    ("cbAlignment", ctypes.c_ushort),
                    ("wTypeFlags", ctypes.c_ushort),
                    ("wMajorVerNum", ctypes.c_ushort),
                    ("wMinorVerNum", ctypes.c_ushort))

    out: dict[str, dict] = {}
    try:
        n = int(_call(tl, 3, ctypes.c_uint, ()))
        for i in range(n):
            nm = ctypes.c_void_p()
            if _call(tl, 9, ctypes.c_long,
                     (ctypes.c_int, ctypes.POINTER(ctypes.c_void_p),
                      ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p),
                     i, ctypes.byref(nm), None, None, None):
                continue
            name = ctypes.wstring_at(nm.value) if nm.value else ""
            oleaut.SysFreeString(nm)
            if name not in IID:
                continue
            ti = ctypes.c_void_p()
            if _call(tl, 4, ctypes.c_long,
                     (ctypes.c_uint, ctypes.POINTER(ctypes.c_void_p)),
                     i, ctypes.byref(ti)):
                continue
            pa = ctypes.POINTER(_TA)()
            if _call(ti, 3, ctypes.c_long,
                     (ctypes.POINTER(ctypes.POINTER(_TA)),),
                     ctypes.byref(pa)) == 0:
                a = pa.contents
                g = a.guid
                out[name] = {
                    "iid": "{%08X-%04X-%04X-%s-%s}" % (
                        g.Data1, g.Data2, g.Data3,
                        "".join("%02X" % b for b in g.Data4[:2]),
                        "".join("%02X" % b for b in g.Data4[2:])),
                    "slots": int(a.cbSizeVft) // 8,
                }
                _call(ti, 19, None, (ctypes.POINTER(_TA),), pa)
            _release(ti)
    finally:
        _release(tl)
    return out


def verify_abi() -> dict:
    """Refuse at BIND time if any hard-coded IID or vtable width drifted."""
    got = read_typelib()
    bad = []
    for name, iid in IID.items():
        live = got.get(name)
        if live is None:
            bad.append("%s absent from typelib" % name)
            continue
        if live["iid"].upper() != iid.upper():
            bad.append("%s IID %s != typelib %s" % (name, iid, live["iid"]))
        if live["slots"] != VTBL_SLOTS[name]:
            bad.append("%s vtable %d slots != typelib %d"
                       % (name, VTBL_SLOTS[name], live["slots"]))
    if ctypes.sizeof(SPEVENT) != SPEVENT_ABI_BYTES:
        bad.append("SPEVENT is %d bytes, sapi.h packs %d"
                   % (ctypes.sizeof(SPEVENT), SPEVENT_ABI_BYTES))
    return {"ok": not bad, "checked": sorted(IID), "typelib": SAPI_DLL,
            "mismatches": bad, "spevent_bytes": ctypes.sizeof(SPEVENT)}


def _bind_engine(reco, token_id: str) -> None:
    """ISpRecognizer::SetRecognizer(token). Refuses by name, never silently."""
    tok, hr = _create(CLSID_SP_OBJECT_TOKEN, IID_ISP_OBJECT_TOKEN)
    if tok is None:
        raise CvmDtError(RefusalKind.STT_NONE,
                         "CoCreate SpObjectToken hr=0x%08X" % hr)
    try:
        _hrcall(tok, T_SET_ID, "ISpObjectToken::SetId %s" % token_id,
                (ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_int),
                None, token_id, 0)
        _hrcall(reco, R_SET_RECOGNIZER,
                "ISpRecognizer::SetRecognizer %s" % token_id,
                (ctypes.c_void_p,), tok)
    finally:
        _release(tok)


# ---------------------------------------------------------------------------
# Probe
# ---------------------------------------------------------------------------
def recognizer_tokens() -> list[dict]:
    """Installed SAPI recognizer tokens, both stacks. Empty is honest absence.

    Each row carries the FULL token id, because that is what
    `ISpObjectToken::SetId` takes — a bare key name cannot be bound.
    """
    if os.name != "nt":
        return []
    import winreg
    out: list[dict] = []
    for stack, root in TOKEN_ROOTS.items():
        sub = root.split("\\", 1)[1]
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, sub)
        except OSError:
            continue
        i = 0
        while True:
            try:
                name = winreg.EnumKey(key, i)
            except OSError:
                break
            i += 1
            row = {"stack": stack, "name": name, "id": root + "\\" + name}
            try:
                tk = winreg.OpenKey(key, name)
                row["description"] = str(winreg.QueryValueEx(tk, "")[0])
                try:
                    row["preferred_rate"] = int(
                        winreg.QueryValueEx(tk, "PreferredAudioRate")[0])
                except OSError:
                    pass
            except OSError:
                pass
            out.append(row)
    return out


def pick_token(prefer: str = "") -> Optional[dict]:
    """The engine to bind. ENGINE_ORDER, or an explicit name/id override.

    Order is MEASURED, not assumed — see `_disposal/sapi_engine_ab.py` and the
    A/B row in CVM_BACKLOG.md. If the preferred engine is not installed the
    next one is used; if none are, the caller gets None and refuses STT_NONE.
    """
    rows = recognizer_tokens()
    if prefer:
        for r in rows:
            if prefer in (r["name"], r["id"]):
                return r
        return None
    for want in ENGINE_ORDER:
        for r in rows:
            if r["name"] == want:
                return r
    return rows[0] if rows else None


def probe_sapi(prefer: str = "") -> dict:
    """On-box SAPI ear: typed STT_NONE with a REASON, never a bare False."""
    if os.name != "nt":
        return {"ok": False, "engine": ENGINE, "kind": "STT_NONE",
                "detail": "SAPI is Windows-only"}
    if not Path(SAPI_DLL).is_file():
        return {"ok": False, "engine": ENGINE, "kind": "STT_NONE",
                "detail": "sapi.dll not present at %s" % SAPI_DLL}
    tokens = recognizer_tokens()
    if not tokens:
        return {"ok": False, "engine": ENGINE, "kind": "STT_NONE",
                "detail": "no SAPI recognizer token installed"}
    abi = verify_abi()
    if not abi["ok"]:
        return {"ok": False, "engine": ENGINE, "kind": "STT_NONE",
                "detail": "sapi ABI drift: " + "; ".join(abi["mismatches"])}
    punk, hr = _create(CLSID_SP_INPROC_RECOGNIZER, IID["ISpRecognizer"])
    if punk is None:
        return {"ok": False, "engine": ENGINE, "kind": "STT_NONE",
                "detail": "CoCreate SpInprocRecognizer hr=0x%08X" % hr}
    _release(punk)
    pick = pick_token(prefer)
    if pick is None:
        return {"ok": False, "engine": ENGINE, "kind": "STT_NONE",
                "detail": "recognizer %r not installed" % prefer}
    return {"ok": True, "engine": ENGINE, "kind": "ok",
            "recognizers": [t["name"] for t in tokens],
            "recognizer": pick["name"], "recognizer_id": pick["id"],
            "recognizer_stack": pick["stack"],
            "description": pick.get("description"),
            "abi": "typelib-verified"}


def probe_ear() -> dict:
    """The ear the client will actually bind: VOSK first, then on-box SAPI.

    VOSK keeps priority because it is the phone's engine (CVM_ARCH §6.3 —
    desk and road should sound like one assistant). SAPI is the floor that
    makes `STT_NONE` mean "no ear on this machine" instead of "nobody ran pip".
    """
    from cosmos_cvm_push import probe_stt as probe_vosk
    vosk = probe_vosk()
    if vosk.get("ok"):
        return dict(vosk, source="vosk")
    sapi = probe_sapi()
    if sapi.get("ok"):
        return dict(sapi, source="sapi", vosk_detail=vosk.get("detail"))
    return {"ok": False, "engine": None, "kind": "STT_NONE", "source": None,
            "detail": "no ear: vosk=%s; sapi=%s"
                      % (vosk.get("detail"), sapi.get("detail"))}


# ---------------------------------------------------------------------------
# The transcriber
# ---------------------------------------------------------------------------
def pcm_to_wav_bytes(pcm: bytes, rate: int = STT_RATE, ch: int = 1) -> bytes:
    """PCM16 -> a real RIFF container so BindToFile can read the format."""
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(ch)
        w.setsampwidth(2)
        w.setframerate(int(rate) or STT_RATE)
        w.writeframes(pcm)
    return buf.getvalue()


def wav_to_pcm(data: bytes) -> tuple[bytes, int]:
    """Unwrap a RIFF WAV to (pcm16_mono_frames, rate). Refuses non-PCM16."""
    with wave.open(io.BytesIO(data), "rb") as w:
        if w.getsampwidth() != 2:
            raise CvmDtError(RefusalKind.STT_NONE,
                             "WAV is %d-bit, need 16" % (w.getsampwidth() * 8))
        return w.readframes(w.getnframes()), int(w.getframerate())


class SapiTranscriber:
    """On-box Windows recognizer. Nothing to install, nothing to run out.

    Same shape as `cvm_dt_voice.VoskTranscriber` (`accept` / `finish` /
    `transcribe`) so `vad_interrupt`'s incremental sink path works unchanged.
    SAPI's file-stream input wants a complete stream, so `accept` buffers and
    `finish` recognizes — the streaming API is honored, the streaming *claim*
    is not made.
    """

    def __init__(self, *, prefer: str = "", wait_ms: int = 1500,
                 max_wait_s: float = 30.0):
        self._pcm: list[bytes] = []
        self._rate = STT_RATE
        self._t0 = 0.0
        self.prefer = prefer
        self.wait_ms = int(wait_ms)
        self.max_wait_s = float(max_wait_s)
        self.last: dict[str, Any] = {}

    def accept(self, pcm: bytes, rate: int = STT_RATE) -> None:
        if not self._pcm:
            self._t0 = time.perf_counter()
            self._rate = int(rate) or STT_RATE
        if pcm:
            self._pcm.append(pcm)

    def finish(self) -> dict:
        pcm, self._pcm = b"".join(self._pcm), []
        if not pcm:
            raise CvmDtError(RefusalKind.STT_NONE, "sapi got no audio")
        got = self.recognize_pcm(pcm, self._rate)
        text = str(got.get("transcript") or "").strip()
        if not text:
            raise CvmDtError(RefusalKind.STT_NONE,
                             "sapi returned empty transcript")
        return {"transcript": text, "engine": ENGINE, "rate": self._rate,
                "ear_ms": round((time.perf_counter() - self._t0) * 1000.0, 3),
                "recognizer": got.get("recognizer"),
                "events": got.get("events")}

    def transcribe(self, pcm: bytes, rate: int) -> dict:
        self.accept(pcm, rate)
        return self.finish()

    # -- the COM work ------------------------------------------------------
    def recognize_pcm(self, pcm: bytes, rate: int = STT_RATE) -> dict:
        """PCM16 mono -> transcript. Empty text is honest, not fabricated."""
        import tempfile
        fd, tmp = tempfile.mkstemp(suffix=".wav", prefix="cvm_dt_ear_")
        try:
            with os.fdopen(fd, "wb") as fh:
                fh.write(pcm_to_wav_bytes(pcm, rate))
            return self.recognize_wav(tmp)
        finally:
            try:
                os.unlink(tmp)
            except OSError:
                pass

    def recognize_wav(self, path: str | os.PathLike) -> dict:
        """Recognize, trying each DICTATION-capable engine in ENGINE_ORDER.

        Not every installed recognizer can do free-text. Measured on this box:
        `MS-1033-110-WINMO-DNN` (OneCore Embedded DNN v11.1) accepts
        `SetRecognizer` and then refuses `LoadDictation` with 0x8004503A — it
        carries no dictation topic, only command-and-control. Hard-coding one
        token name would strand a peer whose engines are named differently, so
        an engine that cannot load dictation is SKIPPED BY NAME and the next
        candidate is tried. If none can, the refusal names every one it tried.
        """
        p = Path(path)
        if not p.is_file():
            raise CvmDtError(RefusalKind.STT_NONE, "no such wav %s" % p)
        if self.prefer:
            cands = [c for c in recognizer_tokens()
                     if self.prefer in (c["name"], c["id"])]
            if not cands:
                raise CvmDtError(RefusalKind.STT_NONE,
                                 "recognizer %r not installed" % self.prefer)
        else:
            rows = recognizer_tokens()
            ranked = [r for w in ENGINE_ORDER for r in rows if r["name"] == w]
            cands = ranked + [r for r in rows if r not in ranked]
        if not cands:
            raise CvmDtError(RefusalKind.STT_NONE,
                             "no SAPI recognizer token installed")
        tried: list[str] = []
        for cand in cands:
            try:
                return self._recognize_with(p, cand)
            except CvmDtError as e:
                tried.append("%s: %s" % (cand["name"], e))
        raise CvmDtError(RefusalKind.STT_NONE,
                         "no dictation-capable engine: " + "; ".join(tried))

    def _recognize_with(self, p: Path, cand: dict) -> dict:
        probe = probe_sapi(cand["name"])
        if not probe.get("ok"):
            raise CvmDtError(RefusalKind.STT_NONE, str(probe.get("detail")))

        _ensure_com()  # per-thread MTA; SAPI holds this apartment
        t0 = time.perf_counter()
        stream = reco = ctx = gram = None
        parts: list[str] = []
        events: list[int] = []
        stream_clsid = None
        try:
            for clsid in (CLSID_SP_STREAM, CLSID_SP_FILE_STREAM):
                stream, hr = _create(clsid, IID["ISpStream"])
                if stream is not None:
                    stream_clsid = clsid
                    break
            if stream is None:
                raise CvmDtError(RefusalKind.STT_NONE,
                                 "no ISpStream from either CLSID hr=0x%08X" % hr)
            _hrcall(stream, S_BIND_TO_FILE, "ISpStream::BindToFile",
                    (ctypes.c_wchar_p, ctypes.c_int, ctypes.c_void_p,
                     ctypes.c_void_p, ctypes.c_ulonglong),
                    str(p), SPFM_OPEN_READONLY, None, None, 0)

            reco, hr = _create(CLSID_SP_INPROC_RECOGNIZER, IID["ISpRecognizer"])
            if reco is None:
                raise CvmDtError(RefusalKind.STT_NONE,
                                 "CoCreate recognizer hr=0x%08X" % hr)
            # Pin the engine BEFORE SetInput: SetRecognizer resets the input.
            _bind_engine(reco, probe["recognizer_id"])
            _hrcall(reco, R_SET_INPUT, "ISpRecognizer::SetInput",
                    (ctypes.c_void_p, ctypes.c_int), stream, 1)

            ctx = ctypes.c_void_p()
            _hrcall(reco, R_CREATE_RECO_CONTEXT,
                    "ISpRecognizer::CreateRecoContext",
                    (ctypes.POINTER(ctypes.c_void_p),), ctypes.byref(ctx))
            _hrcall(ctx, C_SET_NOTIFY_WIN32_EVENT,
                    "ISpRecoContext::SetNotifyWin32Event", ())
            interest = (SPFEI(SPEI_RECOGNITION) | SPFEI(SPEI_FALSE_RECOGNITION)
                        | SPFEI(SPEI_END_SR_STREAM))
            _hrcall(ctx, C_SET_INTEREST, "ISpRecoContext::SetInterest",
                    (ctypes.c_ulonglong, ctypes.c_ulonglong),
                    interest, interest)

            gram = ctypes.c_void_p()
            _hrcall(ctx, C_CREATE_GRAMMAR, "ISpRecoContext::CreateGrammar",
                    (ctypes.c_ulonglong, ctypes.POINTER(ctypes.c_void_p)),
                    1, ctypes.byref(gram))
            # The engine-capability gate: a command-and-control-only engine
            # refuses HERE, by name, and recognize_wav moves to the next one.
            _hrcall(gram, G_LOAD_DICTATION, "ISpRecoGrammar::LoadDictation",
                    (ctypes.c_wchar_p, ctypes.c_int), None, SPLO_STATIC)
            _hrcall(gram, G_SET_DICTATION_STATE,
                    "ISpRecoGrammar::SetDictationState",
                    (ctypes.c_int,), SPRS_ACTIVE)
            _hrcall(reco, R_SET_RECO_STATE, "ISpRecognizer::SetRecoState",
                    (ctypes.c_int,), SPRST_ACTIVE)

            deadline = time.perf_counter() + self.max_wait_s
            ev, fetched = SPEVENT(), ctypes.c_ulong(0)
            while time.perf_counter() < deadline:
                waited = _call(ctx, C_WAIT_FOR_NOTIFY_EVENT, ctypes.c_long,
                               (ctypes.c_ulong,), self.wait_ms)
                drained = False
                while _call(ctx, C_GET_EVENTS, ctypes.c_long,
                            (ctypes.c_ulong, ctypes.POINTER(SPEVENT),
                             ctypes.POINTER(ctypes.c_ulong)),
                            1, ctypes.byref(ev),
                            ctypes.byref(fetched)) == 0 and fetched.value:
                    drained = True
                    events.append(int(ev.eEventId))
                    if ev.eEventId == SPEI_RECOGNITION and ev.lParam:
                        parts.append(self._text_of(ev.lParam))
                    if ev.lParam:
                        _release(ctypes.c_void_p(ev.lParam))
                if SPEI_END_SR_STREAM in events:
                    break
                if int(waited) == S_FALSE and not drained:
                    break  # engine went quiet: the stream is spent
        finally:
            if reco is not None:
                _call(reco, R_SET_RECO_STATE, ctypes.c_long,
                      (ctypes.c_int,), SPRST_INACTIVE)
            if stream is not None:
                _call(stream, S_STREAM_CLOSE, ctypes.c_long, ())
            for h in (gram, ctx, reco, stream):
                _release(h)

        text = " ".join(t for t in parts if t).strip()
        self.last = {
            "transcript": text, "engine": ENGINE,
            "ear_ms": round((time.perf_counter() - t0) * 1000.0, 3),
            "recognizer": probe.get("recognizer"), "events": events,
            "recognizer_id": probe.get("recognizer_id"),
            "recognizer_stack": probe.get("recognizer_stack"),
            "stream_clsid": stream_clsid, "phrases": len(parts),
            "kind": "ok" if text else "STT_NONE",
        }
        return self.last

    @staticmethod
    def _text_of(lparam: int) -> str:
        """ISpRecoResult (an ISpPhrase) -> the whole phrase, CoTaskMemFree'd."""
        res = ctypes.c_void_p(lparam)
        out = ctypes.c_void_p()
        hr = _call(res, P_GET_TEXT, ctypes.c_long,
                   (ctypes.c_ulong, ctypes.c_ulong, ctypes.c_int,
                    ctypes.POINTER(ctypes.c_void_p), ctypes.c_void_p),
                   SP_GETWHOLEPHRASE, SP_GETWHOLEPHRASE, 1,
                   ctypes.byref(out), None)
        if int(hr) < 0 or not out.value:
            return ""
        try:
            return ctypes.wstring_at(out.value)
        finally:
            ctypes.WinDLL("ole32").CoTaskMemFree(out)


def default_ear() -> Optional[Any]:
    """The bound transcriber, or None. Mirrors cvm_dt_voice.default_transcriber."""
    p = probe_ear()
    if not p.get("ok"):
        return None
    if p.get("source") == "vosk":
        from cvm_dt_voice import VoskTranscriber
        return VoskTranscriber(str(p["model"]))
    return SapiTranscriber()


# ---------------------------------------------------------------------------
# The phone half of the same ear (CVM_BACKLOG B1).
#
# `cosmos_cvm_push.bind_phone_stt` folds phone-pushed PCM through VOSK ONLY
# (`probe_stt` at :280, `transcribe_pcm` at :297). On a box with no vosk wheel
# and no COSMOS_VOSK_MODEL it transports the audio correctly and then
# transcribes nothing — every phone utterance comes back `STT_NONE`. That is
# wishlist #1 ("pull it off the phone for LOCAL processing") arriving at a deaf
# PC. `bind_phone_stt` is Core-adjacent and outside this fence, so the second
# tier is applied at the CALLER (`cvm_pull.DesktopPullClock.on_speech`), which
# is the desktop drain clock and is in-fence.
#
# The engage condition is deliberately NOT inferred from the returned dict:
# `bind_phone_stt` writes `stt_engine="vosk"` both when the probe failed
# (:359-361) and when VOSK really ran and heard no words (:365-368). Those two
# must not be confused — re-running a real empty result through a second engine
# would be fishing for a word. So the gate is `probe_stt()` itself: engage only
# when this box HAS NO VOSK, in which case an `STT_NONE` cannot be a word
# verdict because nothing listened.
# ---------------------------------------------------------------------------
FALLBACK_WIRE = "cvm-dt-stt-fallback/1"
# STT_NONE ack fields bind_phone_stt merges in from ack_stt_none(). If the
# on-box ear then HEARS, the "speech recognition unavailable" ack is false and
# must be withdrawn, not left riding alongside a transcript.
_STT_NONE_ACK_KEYS = ("ack", "ack_kind", "ack_emitted")


def phone_ear_fallback(paths, phone, stt, *, transcriber=None,
                       vosk_probe=None) -> dict:
    """Second-tier on-box ear for a phone fold that came back STT_NONE.

    Returns a NEW dict. `stt_fallback` always records what happened and why,
    so a skip is a named skip and never a silent pass-through.

    Engages only when ALL of:
      * the fold reported `stt_kind == "STT_NONE"` (not `ok`, not UNREACHABLE),
      * `probe_stt()` says this box has no VOSK at all,
      * the consumed CAS sha still resolves to bytes,
      * `probe_sapi()` says there is an on-box recognizer.

    An empty SAPI transcript stays `STT_NONE` — with `stt_engine="sapi"`, so
    the record says the ear RAN and heard nothing, which is a different fact
    from "no ear was ever bound".
    """
    from cosmos_cvm_push import (VOICE_READY, _kinds_of, load_cas_pcm,
                                 set_voice_state)
    from cosmos_cvm_push import probe_stt as _probe_vosk

    out = dict(stt or {})
    note: dict[str, Any] = {"wire": FALLBACK_WIRE, "engaged": False,
                            "heard": False, "reason": ""}
    out["stt_fallback"] = note

    kind = str(out.get("stt_kind") or "")
    if kind != "STT_NONE":
        note["reason"] = "fold reported stt_kind=%r, not STT_NONE" % kind
        return out
    vosk = (vosk_probe or _probe_vosk)()
    if vosk.get("ok"):
        note["reason"] = ("vosk is bound on this box, so its STT_NONE is a "
                          "word verdict, not a missing ear")
        return out
    note["vosk_detail"] = vosk.get("detail")

    sha = str(out.get("stt_pcm_sha256") or out.get("pcm_sha256") or "")
    pcm = load_cas_pcm(paths, sha) if sha else None
    if pcm is None:
        note["reason"] = ("no CAS bytes behind sha %r" % sha[:16]) if sha \
            else "fold consumed no pcm pointer"
        return out
    note["pcm_bytes"] = len(pcm)
    note["pcm_sha256"] = sha

    probe = probe_sapi()
    if not probe.get("ok"):
        note["reason"] = "no on-box ear either: %s" % probe.get("detail")
        return out

    blob = _kinds_of(phone).get("pcm")
    try:
        rate = int((blob if isinstance(blob, dict) else {}).get("rate")
                   or STT_RATE)
    except (TypeError, ValueError):
        rate = STT_RATE
    note["rate"] = rate

    note["engaged"] = True
    t0 = time.perf_counter()
    try:
        got = (transcriber or SapiTranscriber()).recognize_pcm(pcm, rate)
    except CvmDtError as e:
        note["reason"] = "on-box ear refused: %s: %s" % (e.kind, e)
        out["stt_engine"] = ENGINE
        out["ear_ms"] = round((time.perf_counter() - t0) * 1000.0, 3)
        return out
    ear_ms = got.get("ear_ms")
    if ear_ms is None:
        ear_ms = round((time.perf_counter() - t0) * 1000.0, 3)
    text = str(got.get("transcript") or "").strip()

    out["stt_engine"] = ENGINE
    out["ear_ms"] = ear_ms
    out["stt_recognizer"] = got.get("recognizer")
    note["recognizer"] = got.get("recognizer")
    note["events"] = got.get("events")
    note["ear_ms"] = ear_ms
    if not text:
        note["reason"] = "on-box ear ran and returned an empty transcript"
        return out
    out["stt_kind"] = "ok"
    out["transcript"] = text
    for k in _STT_NONE_ACK_KEYS:
        out.pop(k, None)
    out["voice_state"] = set_voice_state(VOICE_READY)["voice_state"]
    note["heard"] = True
    note["reason"] = "vosk absent; on-box %s recognized the pulled PCM" % ENGINE
    note["transcript"] = text
    return out


# ---------------------------------------------------------------------------
# selftest — the mouth speaks, the ear hears. No Core, no network, no key.
# ---------------------------------------------------------------------------
SELFTEST_PHRASE = "open the status report"


def run_selftest(phrase: str = SELFTEST_PHRASE) -> dict:
    """Round-trip THIS box: SAPI TTS -> WAV -> SAPI reco -> transcript.

    The live_value is a transcript no loopback fake can produce: the words
    came back out of the Windows recognizer, from audio the Windows
    synthesizer generated in this process.
    """
    from cvm_dt import _sapi_wav
    rec: dict[str, Any] = {"selftest": "cvm-dt-stt", "wire": WIRE,
                           "phrase": phrase, "abi": verify_abi(),
                           "probe": probe_sapi()}
    if not rec["probe"].get("ok"):
        rec.update(ok=False, kind="STT_NONE",
                   detail=rec["probe"].get("detail"))
        return rec
    t0 = time.perf_counter()
    wav = _sapi_wav(phrase)
    rec["tts_ms"] = round((time.perf_counter() - t0) * 1000.0, 3)
    rec["wav_bytes"] = len(wav)
    pcm, rate = wav_to_pcm(wav)
    rec["tts_rate"] = rate
    rec["pcm_bytes"] = len(pcm)
    got = SapiTranscriber().recognize_pcm(pcm, rate)
    heard = str(got.get("transcript") or "")
    want = set(phrase.lower().split())
    hits = want & set(heard.lower().replace(",", " ").replace(".", " ").split())
    rec["live_value"] = {
        "spoken": phrase, "heard": heard, "engine": got.get("engine"),
        "recognizer": got.get("recognizer"), "ear_ms": got.get("ear_ms"),
        "events": got.get("events"), "stream_clsid": got.get("stream_clsid"),
        "words_matched": sorted(hits), "word_recall": round(
            len(hits) / max(1, len(want)), 3),
    }
    rec["ok"] = bool(heard)
    rec["kind"] = "ok" if heard else "STT_NONE"
    return rec


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="cvm-dt on-box ear (SAPI STT)")
    ap.add_argument("verb", choices=("probe", "verify", "selftest", "hear"))
    ap.add_argument("wav", nargs="?")
    ap.add_argument("--phrase", default=SELFTEST_PHRASE)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)

    if a.verb == "verify":
        out = verify_abi()
    elif a.verb == "probe":
        out = {"sapi": probe_sapi(), "ear": probe_ear(),
               "tokens": recognizer_tokens()}
    elif a.verb == "selftest":
        out = run_selftest(a.phrase)
    else:
        if not a.wav:
            ap.error("hear needs a .wav path")
        out = SapiTranscriber().recognize_wav(a.wav)

    print(json.dumps(out, indent=1, sort_keys=True, default=str))
    ok = out.get("ok", out.get("kind") == "ok")
    return 0 if ok else 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except CvmDtError as e:
        print(json.dumps({"ok": False, "kind": str(e.kind), "detail": str(e)}))
        raise SystemExit(2)
