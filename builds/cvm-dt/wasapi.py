#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Thin WASAPI (Windows Core Audio) helper for CVM desktop.

Stdlib ctypes only — no pycaw, no sounddevice, no vendor SDK. Capture and
render are independent persisted IDs (input_device_id, output_device_id).
Windows defaults are the INITIAL fallback only; a missing requested
endpoint reopens on the live default and the fallback device is reported,
never silently rerouted. AUDIO_NONE if nothing is openable.

This module does not talk to COSMOS Core and does not write a lease.
"""
from __future__ import annotations

import ctypes
import json
import os
import struct
import threading
import time
from array import array
from ctypes import POINTER, byref, c_uint32, c_void_p, sizeof
from ctypes.wintypes import BYTE, DWORD, LPCWSTR, LPWSTR, WORD
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


class AudioNoneError(RuntimeError):
    """Typed absence of the Windows default audio device. kind is always AUDIO_NONE."""

    def __init__(self, detail: str):
        self.kind = "AUDIO_NONE"
        super().__init__(f"[AUDIO_NONE] {detail}")


# ---------------- COM / WASAPI constants ----------------
HRESULT = ctypes.HRESULT
S_OK = 0
S_FALSE = 1
COINIT_MULTITHREADED = 0x0
RPC_E_CHANGED_MODE = 0x80010106
CLSCTX_ALL = 0x17
STGM_READ = 0
AUDCLNT_SHAREMODE_SHARED = 0
AUDCLNT_BUFFERFLAGS_SILENT = 0x2
AUDCLNT_E_DEVICE_INVALIDATED = 0x88890004
WAVE_FORMAT_PCM = 1
WAVE_FORMAT_IEEE_FLOAT = 3
WAVE_FORMAT_EXTENSIBLE = 0xFFFE
VT_LPWSTR = 31
E_NOTFOUND = 0x80070490
DEVICE_STATE_ACTIVE = 0x1
REFTIMES_PER_MS = 10_000
HNS_BUFFER = 100 * REFTIMES_PER_MS  # 100 ms shared-mode buffer
ENDPOINTS_NAME = "cvm_dt_endpoints.json"
PREROLL_MS = 300.0

eRender, eCapture = 0, 1
eConsole, eMultimedia, eCommunications = 0, 1, 2
_PERSIST = None
_LAST: dict = {}


class GUID(ctypes.Structure):
    _fields_ = (("Data1", DWORD), ("Data2", WORD), ("Data3", WORD),
                ("Data4", BYTE * 8))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, GUID):
            return NotImplemented
        return bytes(self) == bytes(other)


def _guid(text: str) -> GUID:
    s = text.strip().strip("{}")
    a, b, c, d, e = s.split("-")
    return GUID(int(a, 16), int(b, 16), int(c, 16),
                (BYTE * 8).from_buffer_copy(bytes.fromhex(d + e)))


CLSID_MMDeviceEnumerator = _guid("{BCDE0395-E52F-467C-8E3D-C4579291692E}")
IID_IMMDeviceEnumerator = _guid("{A95664D2-9614-4F35-A746-DE8DB63617E6}")
IID_IAudioClient = _guid("{1CB9AD4C-DBFA-4C32-B178-C2F568A703B2}")
IID_IAudioRenderClient = _guid("{F294ACFC-3146-4483-A7BF-ADDCA7C260E2}")
IID_IAudioCaptureClient = _guid("{C8ADBD64-E71E-48A0-A4DE-185C395CD317}")
IID_IPropertyStore = _guid("{886D8EEB-8CF2-4446-8D02-CDBA1DBDCF99}")
KSDATAFORMAT_SUBTYPE_PCM = _guid("{00000001-0000-0010-8000-00AA00389B71}")
KSDATAFORMAT_SUBTYPE_IEEE_FLOAT = _guid("{00000003-0000-0010-8000-00AA00389B71}")


class PROPERTYKEY(ctypes.Structure):
    _fields_ = (("fmtid", GUID), ("pid", DWORD))


PKEY_Device_FriendlyName = PROPERTYKEY(
    _guid("{A45C254E-6149-4ED3-9D18-47BA1B21D2DA}"), 14)


class _PVU(ctypes.Union):
    _fields_ = (("pwszVal", c_void_p), ("uhVal", ctypes.c_ulonglong),
                ("blob", BYTE * 16))


class PROPVARIANT(ctypes.Structure):
    # 24 bytes on x64 (vt+pad at 0, union at 8). A 16-byte overlay truncates.
    _fields_ = (("vt", WORD), ("reserved", WORD * 3), ("u", _PVU))


class WAVEFORMATEX(ctypes.Structure):
    _pack_ = 1
    _fields_ = (
        ("wFormatTag", WORD),
        ("nChannels", WORD),
        ("nSamplesPerSec", DWORD),
        ("nAvgBytesPerSec", DWORD),
        ("nBlockAlign", WORD),
        ("wBitsPerSample", WORD),
        ("cbSize", WORD),
    )


class WAVEFORMATEXTENSIBLE(ctypes.Structure):
    _pack_ = 1
    _fields_ = (
        ("Format", WAVEFORMATEX),
        ("wValidBitsPerSample", WORD),
        ("dwChannelMask", DWORD),
        ("SubFormat", GUID),
    )


@dataclass(frozen=True)
class MixFormat:
    channels: int
    rate: int
    bits: int
    is_float: bool
    block_align: int
    raw: bytes  # the exact blob GetMixFormat returned (passed to Initialize)


@dataclass(frozen=True)
class Endpoint:
    """One WASAPI endpoint (default render or default capture)."""
    flow: str                  # "render" | "capture"
    role: str                  # "console" | "communications"
    device_id: str
    device_name: str
    is_bt: bool


@dataclass(frozen=True)
class Probe:
    """Live Windows default endpoints. Absence of either side is AUDIO_NONE."""
    render: Endpoint
    capture: Endpoint
    communications_render_name: str


_ole32 = None
_tls = threading.local()


def _ole():
    global _ole32
    if _ole32 is None:
        if os.name != "nt":
            raise AudioNoneError("WASAPI is Windows-only (os.name=%r)" % os.name)
        _ole32 = ctypes.windll.ole32
        _ole32.CoInitializeEx.argtypes = [c_void_p, DWORD]
        _ole32.CoInitializeEx.restype = HRESULT
        _ole32.CoCreateInstance.argtypes = [
            POINTER(GUID), c_void_p, DWORD, POINTER(GUID), POINTER(c_void_p)]
        _ole32.CoCreateInstance.restype = HRESULT
        _ole32.CoTaskMemFree.argtypes = [c_void_p]
        _ole32.CoTaskMemFree.restype = None
        _ole32.PropVariantClear.argtypes = [POINTER(PROPVARIANT)]
        _ole32.PropVariantClear.restype = HRESULT
        _ole32.CoUninitialize.argtypes = []
        _ole32.CoUninitialize.restype = None
    return _ole32


def ensure_com() -> None:
    """Public: SAPI holds this thread's apartment (no matching uninit)."""
    _com_init()


def _com_init() -> None:
    """Per-thread CoInitializeEx. Nested calls are refcounted."""
    depth = getattr(_tls, "depth", 0)
    if depth == 0:
        ole = _ole()
        hr = int(ole.CoInitializeEx(None, COINIT_MULTITHREADED))
        if hr < 0 and (hr & 0xFFFFFFFF) != RPC_E_CHANGED_MODE:
            raise AudioNoneError("CoInitializeEx failed hr=0x%08X" % (hr & 0xFFFFFFFF))
        _tls.owned = hr >= 0
    _tls.depth = depth + 1


def _com_uninit() -> None:
    d = getattr(_tls, "depth", 0) - 1
    _tls.depth = max(0, d)
    if d or not getattr(_tls, "owned", False):
        return
    try:
        _ole().CoUninitialize()
    except OSError:
        pass
    _tls.owned = False


def _done(*punks) -> None:
    for p in punks:
        _release(p)
    _com_uninit()


def _hr_ok(hr: int, what: str) -> None:
    if int(hr) < 0:
        raise AudioNoneError("%s hr=0x%08X" % (what, int(hr) & 0xFFFFFFFF))


def _vtbl(punk: c_void_p, index: int):
    lpVtbl = ctypes.cast(punk, POINTER(c_void_p))[0]
    return ctypes.cast(lpVtbl, POINTER(c_void_p))[index]


def _call(punk: c_void_p, index: int, restype, argtypes, *args):
    if restype is HRESULT:  # c_long: x64 HRESULT restype can OSError on S_OK
        restype = ctypes.c_long
    proto = ctypes.WINFUNCTYPE(restype, c_void_p, *argtypes)
    return proto(_vtbl(punk, index))(punk, *args)


def _release(punk: Optional[c_void_p]) -> None:
    if not punk or not punk.value:
        return
    try:
        ctypes.WINFUNCTYPE(ctypes.c_ulong, c_void_p)(_vtbl(punk, 2))(punk)
    except OSError:
        pass


def _create_enumerator() -> c_void_p:
    _com_init()
    ole = _ole()
    punk = c_void_p()
    hr = ole.CoCreateInstance(byref(CLSID_MMDeviceEnumerator), None, CLSCTX_ALL,
                              byref(IID_IMMDeviceEnumerator), byref(punk))
    if int(hr) < 0 or not punk.value:
        raise AudioNoneError(
            "MMDeviceEnumerator missing (no default audio stack) hr=0x%08X"
            % (int(hr) & 0xFFFFFFFF))
    return punk


def _default_device(enum: c_void_p, flow: int, role: int) -> c_void_p:
    dev = c_void_p()
    hr = _call(enum, 4, HRESULT, [ctypes.c_int, ctypes.c_int, POINTER(c_void_p)],
               flow, role, byref(dev))
    code = int(hr) & 0xFFFFFFFF
    if int(hr) < 0 or not dev.value:
        which = "render" if flow == eRender else "capture"
        role_s = {0: "console", 1: "multimedia", 2: "communications"}.get(role, str(role))
        raise AudioNoneError(
            "no Windows default %s device (role=%s) hr=0x%08X"
            % (which, role_s, code))
    return dev


def _device_id(dev: c_void_p) -> str:
    pwsz = LPWSTR()
    _hr_ok(_call(dev, 5, HRESULT, [POINTER(LPWSTR)], byref(pwsz)), "IMMDevice.GetId")
    try:
        return pwsz.value or ""
    finally:
        if pwsz:
            _ole().CoTaskMemFree(pwsz)


def _looks_like_instance_id(s: str) -> bool:
    u = s.upper()
    return (s.startswith("{") or s.startswith("\\\\") or "\\" in s
            or "HDAUDIO" in u or "VEN_" in u or ".INF:" in u
            or u.startswith("USB\\") or u.startswith("SWD\\"))


def _device_name(dev: c_void_p) -> str:
    """Scan the property store for a friendly name. Typed absence if none."""
    store = c_void_p()
    _hr_ok(_call(dev, 4, HRESULT, [DWORD, POINTER(c_void_p)],
                 STGM_READ, byref(store)), "IMMDevice.OpenPropertyStore")
    names: list[str] = []
    try:
        cnt = c_uint32()
        _hr_ok(_call(store, 3, HRESULT, [POINTER(c_uint32)], byref(cnt)),
               "IPropertyStore.GetCount")
        for i in range(int(cnt.value)):
            pk = PROPERTYKEY()
            pv = PROPVARIANT()
            _call(store, 4, HRESULT, [c_uint32, POINTER(PROPERTYKEY)],
                  i, byref(pk))
            _call(store, 5, HRESULT, [POINTER(PROPERTYKEY), POINTER(PROPVARIANT)],
                  byref(pk), byref(pv))
            try:
                if pv.vt in (VT_LPWSTR, 8) and pv.u.pwszVal:
                    s = ctypes.wstring_at(pv.u.pwszVal).strip()
                    if s and not _looks_like_instance_id(s) and not s.startswith("%"):
                        names.append(s)
            finally:
                _ole().PropVariantClear(byref(pv))
    finally:
        _release(store)
    if not names:
        raise AudioNoneError("default device has no friendly name")
    paren = [n for n in names if "(" in n and ")" in n]
    return max(paren or names, key=len)


def _is_bt(device_id: str, name: str) -> bool:
    blob = (device_id + " " + name).upper()
    return any(tag in blob for tag in
               ("BTHENUM", "BTHHFENUM", "BTHLEENUM", "BLUETOOTH", "A2DP"))


def _endpoint(dev: c_void_p, flow: str, role: str) -> Endpoint:
    did = _device_id(dev)
    name = _device_name(dev)
    if not did or not name:
        raise AudioNoneError("default %s device id/name empty" % flow)
    return Endpoint(flow=flow, role=role, device_id=did, device_name=name,
                    is_bt=_is_bt(did, name))


def probe_defaults() -> Probe:
    """Live Windows default render + capture (eConsole). Missing → AUDIO_NONE."""
    enum = _create_enumerator()
    try:
        rend = _default_device(enum, eRender, eConsole)
        try:
            render = _endpoint(rend, "render", "console")
        finally:
            _release(rend)
        cap = _default_device(enum, eCapture, eConsole)
        try:
            capture = _endpoint(cap, "capture", "console")
        finally:
            _release(cap)
        comm_name = ""
        try:
            comm = _default_device(enum, eRender, eCommunications)
            try:
                comm_name = _device_name(comm)
            finally:
                _release(comm)
        except AudioNoneError:
            comm_name = ""
        return Probe(render=render, capture=capture,
                     communications_render_name=comm_name)
    finally:
        _done(enum)


def _device_by_id(enum: c_void_p, device_id: str) -> c_void_p:
    dev = c_void_p()
    hr = _call(enum, 5, HRESULT, [LPCWSTR, POINTER(c_void_p)],
               ctypes.c_wchar_p(str(device_id or "")), byref(dev))
    if int(hr) < 0 or not dev.value:
        raise AudioNoneError(
            "requested device id not present hr=0x%08X"
            % (int(hr) & 0xFFFFFFFF))
    return dev


def enumerate_endpoints(flow: str) -> list[Endpoint]:
    """Active endpoints for one flow. No pairing heuristic."""
    flow_i = eRender if flow == "render" else eCapture
    enum = _create_enumerator()
    out: list[Endpoint] = []
    try:
        coll = c_void_p()
        _hr_ok(_call(enum, 3, HRESULT,
                     [ctypes.c_int, DWORD, POINTER(c_void_p)],
                     flow_i, DEVICE_STATE_ACTIVE, byref(coll)),
               "IMMDeviceEnumerator.EnumAudioEndpoints")
        try:
            n = c_uint32()
            _hr_ok(_call(coll, 3, HRESULT, [POINTER(c_uint32)], byref(n)),
                   "IMMDeviceCollection.GetCount")
            for i in range(int(n.value)):
                dev = c_void_p()
                _hr_ok(_call(coll, 4, HRESULT,
                             [c_uint32, POINTER(c_void_p)], i, byref(dev)),
                       "IMMDeviceCollection.Item")
                try:
                    out.append(_endpoint(dev, flow, "endpoint"))
                except AudioNoneError:
                    pass
                finally:
                    _release(dev)
        finally:
            _release(coll)
    finally:
        _done(enum)
    return out


def pick_endpoint(requested_id: str, available: list[Endpoint],
                  default: Endpoint) -> tuple[Endpoint, bool, str]:
    """Independent pick. Empty id → Windows default (initial, not a fallback)."""
    req = str(requested_id or "").strip()
    if not req:
        return default, False, "windows_default_initial"
    for ep in available:
        if ep.device_id == req:
            return ep, False, "requested"
    return default, True, "requested_missing"


def load_endpoints(path=None) -> dict:
    empty = {"input_device_id": "", "output_device_id": ""}
    if path is None:
        return dict(empty)
    p = Path(path)
    try:
        rec = json.loads(p.read_text(encoding="utf-8")) if p.is_file() else None
    except (OSError, ValueError):
        return dict(empty)
    if not isinstance(rec, dict):
        return dict(empty)
    return {k: str(rec.get(k) or "") for k in empty}


def save_endpoints(path, input_device_id: str = "",
                   output_device_id: str = "") -> dict:
    rec = {"input_device_id": str(input_device_id or ""),
           "output_device_id": str(output_device_id or "")}
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_name(p.name + ".tmp")
    tmp.write_text(json.dumps(rec, indent=1), encoding="utf-8")
    tmp.replace(p)
    return rec


def bind_persist(path=None) -> None:
    """Open-path reads this persist file. None → Windows defaults."""
    global _PERSIST
    _PERSIST = None if path is None else Path(path)


def _wanted(flow_s: str) -> str:
    saved = load_endpoints(_PERSIST)
    key = "output_device_id" if flow_s == "render" else "input_device_id"
    return str(saved.get(key) or "")


def quote_route(probe: Probe, persist=None, *, req_in: str = "",
                req_out: str = "", caps=None, rends=None) -> dict:
    """One picker/status shape. No name-based pairing."""
    saved = load_endpoints(persist if persist is not None else _PERSIST)
    req_in = str(req_in or saved.get("input_device_id") or "")
    req_out = str(req_out or saved.get("output_device_id") or "")
    cap, cap_fb, cap_why = pick_endpoint(
        req_in, list(caps or [probe.capture]), probe.capture)
    rend, rend_fb, rend_why = pick_endpoint(
        req_out, list(rends or [probe.render]), probe.render)
    last_c, last_r = _LAST.get("capture") or {}, _LAST.get("render") or {}
    mix_c, mix_r = dict(last_c.get("mix") or {}), dict(last_r.get("mix") or {})
    if last_c:
        cap_fb, cap_why = bool(last_c.get("fallback")), str(last_c.get("fallback_reason") or "")
    if last_r:
        rend_fb, rend_why = bool(last_r.get("fallback")), str(last_r.get("fallback_reason") or "")
    return {
        "input_device_id": cap.device_id,
        "output_device_id": rend.device_id,
        "capture_name": cap.device_name,
        "render_name": rend.device_name,
        "device_name": rend.device_name,
        "device_id": rend.device_id,
        "is_bt": rend.is_bt,
        "requested_input_device_id": req_in,
        "requested_output_device_id": req_out,
        "capture_opened_on": str(last_c.get("device_id") or ""),
        "render_opened_on": str(last_r.get("device_id") or ""),
        "capture_opened_requested": bool(req_in) and not cap_fb,
        "render_opened_requested": bool(req_out) and not rend_fb,
        "capture_fallback": cap_fb,
        "render_fallback": rend_fb,
        "capture_fallback_reason": cap_why if cap_fb else "",
        "render_fallback_reason": rend_why if rend_fb else "",
        "windows_default_capture_id": probe.capture.device_id,
        "windows_default_render_id": probe.render.device_id,
        "windows_default_capture_name": probe.capture.device_name,
        "windows_default_render_name": probe.render.device_name,
        "mix_capture": mix_c,
        "mix_render": mix_r,
    }


def route_status(persist=None, input_device_id: str = "",
                 output_device_id: str = "") -> dict:
    """Minimal enumerated picker + selected vs default + last-open mix."""
    probe = probe_defaults()
    caps = enumerate_endpoints("capture")
    rends = enumerate_endpoints("render")
    rec = quote_route(probe, persist, req_in=input_device_id,
                      req_out=output_device_id, caps=caps, rends=rends)
    rec["capture"] = [{"device_id": e.device_id, "device_name": e.device_name,
                       "is_bt": e.is_bt} for e in caps]
    rec["render"] = [{"device_id": e.device_id, "device_name": e.device_name,
                      "is_bt": e.is_bt} for e in rends]
    return rec


def _activate_client(dev: c_void_p) -> c_void_p:
    client = c_void_p()
    _hr_ok(_call(dev, 3, HRESULT,
                 [POINTER(GUID), DWORD, c_void_p, POINTER(c_void_p)],
                 byref(IID_IAudioClient), CLSCTX_ALL, None, byref(client)),
           "IMMDevice.Activate(IAudioClient)")
    if not client.value:
        raise AudioNoneError("IAudioClient activate returned null")
    return client


def _mix_format(client: c_void_p) -> MixFormat:
    pwfx = c_void_p()
    _hr_ok(_call(client, 8, HRESULT, [POINTER(c_void_p)], byref(pwfx)),
           "IAudioClient.GetMixFormat")
    try:
        wfx = ctypes.cast(pwfx, POINTER(WAVEFORMATEX)).contents
        nbytes = sizeof(WAVEFORMATEX) + int(wfx.cbSize)
        raw = ctypes.string_at(pwfx, nbytes)
        is_float = wfx.wFormatTag == WAVE_FORMAT_IEEE_FLOAT
        if wfx.wFormatTag == WAVE_FORMAT_EXTENSIBLE and wfx.cbSize >= 22:
            ext = ctypes.cast(pwfx, POINTER(WAVEFORMATEXTENSIBLE)).contents
            is_float = ext.SubFormat == KSDATAFORMAT_SUBTYPE_IEEE_FLOAT
        return MixFormat(channels=int(wfx.nChannels),
                         rate=int(wfx.nSamplesPerSec),
                         bits=int(wfx.wBitsPerSample),
                         is_float=is_float,
                         block_align=int(wfx.nBlockAlign),
                         raw=raw)
    finally:
        _ole().CoTaskMemFree(pwfx)


def _init_shared(client: c_void_p, mix: MixFormat) -> None:
    buf = ctypes.create_string_buffer(mix.raw)
    hr = _call(client, 3, HRESULT,
               [ctypes.c_int, DWORD, ctypes.c_longlong, ctypes.c_longlong,
                c_void_p, c_void_p],
               AUDCLNT_SHAREMODE_SHARED, 0, HNS_BUFFER, 0,
               ctypes.addressof(buf), None)
    _hr_ok(hr, "IAudioClient.Initialize(shared, default mix format)")


def _client_from_dev(dev: c_void_p, flow_s: str
                     ) -> tuple[Endpoint, c_void_p, MixFormat]:
    ep = _endpoint(dev, flow_s, "console")
    client = _activate_client(dev)
    mix = _mix_format(client)
    _init_shared(client, mix)
    return ep, client, mix


def _open_default_client(flow: int) -> tuple[c_void_p, c_void_p, c_void_p, MixFormat, Endpoint]:
    """Open one flow independently. Missing requested id → visible default fallback."""
    flow_s = "render" if flow == eRender else "capture"
    requested = _wanted(flow_s)
    enum = _create_enumerator()
    fallback, reason, dev, client = False, "windows_default_initial", None, None
    try:
        if requested:
            try:
                dev = _device_by_id(enum, requested)
                reason = "requested"
            except AudioNoneError:
                fallback, reason = True, "requested_missing"
                dev = _default_device(enum, flow, eConsole)
        else:
            dev = _default_device(enum, flow, eConsole)
        try:
            ep, client, mix = _client_from_dev(dev, flow_s)
        except AudioNoneError:
            if not (requested and not fallback):
                raise
            _release(client)
            _release(dev)
            client, fallback, reason = None, True, "requested_invalidated"
            dev = _default_device(enum, flow, eConsole)
            ep, client, mix = _client_from_dev(dev, flow_s)
    except AudioNoneError:
        _done(client, dev, enum)
        raise
    _LAST[flow_s] = {
        "device_id": ep.device_id, "device_name": ep.device_name,
        "is_bt": ep.is_bt, "requested_id": requested,
        "opened_requested": bool(requested) and not fallback,
        "fallback": fallback,
        "fallback_reason": reason if fallback else "",
        "mix": {"channels": mix.channels, "rate": mix.rate, "bits": mix.bits,
                "is_float": mix.is_float, "block_align": mix.block_align},
    }
    return enum, dev, client, mix, ep


def _pcm16_mono_to_mix(pcm: bytes, src_rate: int, mix: MixFormat) -> bytes:
    """Linear-resample 16-bit mono PCM into the WASAPI shared mix format.

    Same samples as the per-frame writer it replaces; the interleave is a
    C-level extended-slice assignment instead of a struct.pack and two
    bytearray splices per frame. Measured 2026-08-30: 178 ms of the 241 ms
    between a reply arriving and its first sample was spent right here.
    """
    if not pcm:
        return b""
    src = memoryview(pcm).cast("h")
    n_src = len(src)
    if not n_src:
        return b""
    n_dst = max(1, int(round(n_src * mix.rate / float(src_rate))))
    if int(src_rate) == int(mix.rate) and n_dst == n_src:
        mono = src
    else:
        rate = float(mix.rate)
        mono = [0.0] * n_dst
        for i in range(n_dst):
            pos = i * src_rate / rate
            i0 = int(pos)
            s0 = src[i0] if i0 < n_src else 0
            s1 = src[i0 + 1] if (i0 + 1) < n_src else s0
            mono[i] = s0 + (s1 - s0) * (pos - i0)
    if mix.is_float:
        one = array("f", [max(-1.0, min(1.0, s / 32768.0)) for s in mono])
        width = 4
    else:
        one = array("h", [int(max(-32768, min(32767, s))) for s in mono])
        width = 2
    dst_ch = mix.channels
    if width * dst_ch == mix.block_align:
        if dst_ch == 1:
            return one.tobytes()
        inter = array(one.typecode)
        inter.frombytes(bytes(n_dst * mix.block_align))
        for ch in range(dst_ch):
            inter[ch::dst_ch] = one
        return inter.tobytes()
    # Exotic slot width (24/32-bit integer mix): the sample occupies the low
    # bytes of each slot, exactly as the per-frame writer left it.
    raw = one.tobytes()
    bps = mix.block_align // dst_ch
    frames = bytearray(n_dst * mix.block_align)
    for i in range(n_dst):
        packed = raw[i * width:i * width + width]
        off = i * mix.block_align
        for ch in range(dst_ch):
            frames[off + ch * bps:off + ch * bps + width] = packed
    return bytes(frames)


def parse_wav_pcm16_mono(wav: bytes) -> tuple[bytes, int]:
    """Return (pcm16_mono_bytes, sample_rate) from a PCM WAV. Stereo is mixed down."""
    if len(wav) < 44 or wav[0:4] != b"RIFF" or wav[8:12] != b"WAVE":
        raise AudioNoneError("TTS WAV is not a RIFF/WAVE")
    off = 12
    fmt = None
    data = None
    while off + 8 <= len(wav):
        tag = wav[off:off + 4]
        size = struct.unpack_from("<I", wav, off + 4)[0]
        body = off + 8
        if tag == b"fmt " and size >= 16:
            fmt = wav[body:body + size]
        elif tag == b"data":
            data = wav[body:body + size]
            break
        off = body + size + (size & 1)
    if not fmt or data is None:
        raise AudioNoneError("TTS WAV missing fmt/data")
    tag, ch, rate, _avg, _align, bits = struct.unpack_from("<HHIIHH", fmt, 0)
    if tag != WAVE_FORMAT_PCM or bits != 16:
        raise AudioNoneError("TTS WAV is not PCM16 (tag=%s bits=%s)" % (tag, bits))
    if ch == 1:
        return data, int(rate)
    if ch != 2:
        raise AudioNoneError("TTS WAV channels=%s unsupported" % ch)
    stereo = memoryview(data).cast("h")
    mono = bytearray(len(data) // 2)
    mv = memoryview(mono).cast("h")
    for i in range(len(mv)):
        mv[i] = (stereo[2 * i] + stereo[2 * i + 1]) // 2
    return bytes(mono), int(rate)


def _cancel_set(cancel) -> bool:
    if cancel is None:
        return False
    fn = getattr(cancel, "is_set", None)
    return bool(fn()) if callable(fn) else bool(cancel)


def play_pcm16_mono(pcm: bytes, src_rate: int, cancel=None) -> Endpoint:
    """Render PCM through the current Windows default WASAPI render device.

    cancel.is_set() aborts the drain (barge-in). Independent of idle-GET.
    """
    enum, dev, client, mix, ep = _open_default_client(eRender)
    frames = _pcm16_mono_to_mix(pcm, src_rate, mix)
    try:
        if not frames:
            return ep
        frame_size = mix.block_align
        n_frames_total = len(frames) // frame_size
        svc = c_void_p()
        _hr_ok(_call(client, 14, HRESULT, [POINTER(GUID), POINTER(c_void_p)],
                     byref(IID_IAudioRenderClient), byref(svc)),
               "IAudioClient.GetService(IAudioRenderClient)")
        try:
            buf_frames = c_uint32()
            _hr_ok(_call(client, 4, HRESULT, [POINTER(c_uint32)], byref(buf_frames)),
                   "IAudioClient.GetBufferSize")
            cap = int(buf_frames.value)
            if cap <= 0:
                raise AudioNoneError("render buffer size is 0")
            _hr_ok(_call(client, 10, HRESULT, []), "IAudioClient.Start")
            written = 0
            deadline = time.time() + 30.0 + (n_frames_total / float(mix.rate))
            padding = c_uint32()
            while written < n_frames_total:
                if _cancel_set(cancel):
                    _call(client, 11, HRESULT, [])
                    return ep
                if time.time() > deadline:
                    raise AudioNoneError("render deadline exceeded")
                _hr_ok(_call(client, 6, HRESULT, [POINTER(c_uint32)], byref(padding)),
                       "IAudioClient.GetCurrentPadding")
                avail = cap - int(padding.value)
                if avail <= 0:
                    time.sleep(0.005)
                    continue
                take = min(avail, n_frames_total - written)
                ptr = c_void_p()
                _hr_ok(_call(svc, 3, HRESULT, [c_uint32, POINTER(c_void_p)],
                             take, byref(ptr)),
                       "IAudioRenderClient.GetBuffer")
                ctypes.memmove(ptr, frames[written * frame_size:], take * frame_size)
                _hr_ok(_call(svc, 4, HRESULT, [c_uint32, DWORD], take, 0),
                       "IAudioRenderClient.ReleaseBuffer")
                written += take
            # drain
            while True:
                if _cancel_set(cancel):
                    break
                _hr_ok(_call(client, 6, HRESULT, [POINTER(c_uint32)], byref(padding)),
                       "IAudioClient.GetCurrentPadding")
                if int(padding.value) <= 0:
                    break
                if time.time() > deadline:
                    break
                time.sleep(0.01)
            _call(client, 11, HRESULT, [])  # Stop
        finally:
            _release(svc)
        return ep
    finally:
        _done(client, dev, enum)


def play_wav(wav: bytes, cancel=None) -> Endpoint:
    pcm, rate = parse_wav_pcm16_mono(wav)
    return play_pcm16_mono(pcm, rate, cancel=cancel)


def play_earcon(hz: float = 880.0, ms: int = 160) -> Endpoint:
    """Short tone through the default WASAPI render device (render-path proof)."""
    rate = 16000
    n = max(1, int(rate * ms / 1000))
    import math
    buf = bytearray(n * 2)
    for i in range(n):
        # 8 ms fade in/out so BT codecs don't click
        fade = min(i, n - 1 - i, int(rate * 0.008)) / float(max(1, int(rate * 0.008)))
        s = int(10000 * fade * math.sin(2 * math.pi * hz * i / rate))
        struct.pack_into("<h", buf, i * 2, s)
    return play_pcm16_mono(bytes(buf), rate)


def pcm16_rms(pcm: bytes) -> float:
    n = len(pcm) // 2
    if n <= 0:
        return 0.0
    acc = 0.0
    for s in struct.unpack("<%dh" % n, pcm[: n * 2]):
        acc += float(s) * float(s)
    return (acc / n) ** 0.5


def capture_pcm16_mono(seconds: float = 2.0, *,
                       hangover_ms: float = 0.0,
                       energy_threshold: float = 400.0,
                       min_speech_ms: float = 80.0) -> tuple[bytes, int, Endpoint]:
    """Capture from the Windows default WASAPI capture device, return PCM16 mono.

    hangover_ms>0: stop at trailing silence after speech (PTT endpoint).
    hangover_ms=0: full window (listen / measurement).
    """
    if seconds <= 0 or seconds > 30:
        raise AudioNoneError("capture seconds out of range")
    enum, dev, client, mix, ep = _open_default_client(eCapture)
    try:
        svc = c_void_p()
        _hr_ok(_call(client, 14, HRESULT, [POINTER(GUID), POINTER(c_void_p)],
                     byref(IID_IAudioCaptureClient), byref(svc)),
               "IAudioClient.GetService(IAudioCaptureClient)")
        raw = bytearray()
        heard = False
        speech_ms = silence_ms = 0.0
        try:
            _hr_ok(_call(client, 10, HRESULT, []), "IAudioClient.Start")
            t_end = time.time() + float(seconds)
            pkt, flags, nframes, ptr = c_uint32(), DWORD(), c_uint32(), c_void_p()
            while time.time() < t_end:
                _hr_ok(_call(svc, 5, HRESULT, [POINTER(c_uint32)], byref(pkt)),
                       "IAudioCaptureClient.GetNextPacketSize")
                if int(pkt.value) == 0:
                    time.sleep(0.005)
                    continue
                _hr_ok(_call(svc, 3, HRESULT,
                             [POINTER(c_void_p), POINTER(c_uint32), POINTER(DWORD),
                              c_void_p, c_void_p],
                             byref(ptr), byref(nframes), byref(flags), None, None),
                       "IAudioCaptureClient.GetBuffer")
                nbytes = int(nframes.value) * mix.block_align
                pkt_bytes = (ctypes.string_at(ptr, nbytes)
                             if not (int(flags.value) & AUDCLNT_BUFFERFLAGS_SILENT) and ptr.value
                             else b"\x00" * nbytes)
                _hr_ok(_call(svc, 4, HRESULT, [c_uint32], int(nframes.value)),
                       "IAudioCaptureClient.ReleaseBuffer")
                chunk, _ = _mix_to_pcm16_mono(pkt_bytes, mix)
                raw.extend(chunk)
                n = len(chunk) // 2
                if hangover_ms > 0 and n:
                    dur_ms = 1000.0 * n / float(mix.rate)
                    if pcm16_rms(chunk) >= float(energy_threshold):
                        heard, speech_ms, silence_ms = True, speech_ms + dur_ms, 0.0
                    elif heard:
                        silence_ms += dur_ms
                        if speech_ms >= min_speech_ms and silence_ms >= hangover_ms:
                            break
            _call(client, 11, HRESULT, [])
        finally:
            _release(svc)
        return bytes(raw), mix.rate, ep
    finally:
        _done(client, dev, enum)


def _mix_to_pcm16_mono(raw: bytes, mix: MixFormat) -> tuple[bytes, int]:
    if not raw:
        return b"", mix.rate
    n = len(raw) // mix.block_align
    out = bytearray(n * 2)
    for i in range(n):
        off = i * mix.block_align
        if mix.is_float:
            acc = 0.0
            for ch in range(mix.channels):
                acc += struct.unpack_from("<f", raw, off + ch * 4)[0]
            sample = acc / float(mix.channels)
            v = int(max(-32768, min(32767, sample * 32767.0)))
        else:
            acc = 0
            bps = mix.bits // 8
            for ch in range(mix.channels):
                acc += struct.unpack_from("<h", raw, off + ch * bps)[0]
            v = acc // mix.channels
        struct.pack_into("<h", out, i * 2, v)
    return bytes(out), mix.rate


def windows_default_render() -> Endpoint:
    """The Windows default render device, as WASAPI GetDefaultAudioEndpoint sees it."""
    return probe_defaults().render
