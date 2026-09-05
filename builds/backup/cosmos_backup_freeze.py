#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Point-in-time freeze for builds/backup/cosmos_backup.py (F-43 gap 3).

Default backup still detect-and-refuses SOURCE_MUTATED — no admin, no
shadow. `--freeze` / freeze=True asks Windows VSS for a ClientAccessible
shadow of the source volume. No shadow (not Windows, not a fixed volume,
COM fail, access denied) is typed VSS_UNAVAILABLE: the live tree is
NEVER copied under a freeze flag. Tests inject FrozenTree: a copy taken
at capture() so later source mutations cannot appear in the backup.

Stdlib only. Never deletes source files. A shadow is deleted in
release(); a FrozenTree owned copy is rmtree'd (test scratch).
"""
from __future__ import annotations

import ctypes
import os
import shutil
import sys
from ctypes import POINTER, Structure, Union, byref, c_void_p, c_wchar_p, pointer
from ctypes import wintypes
from pathlib import Path

# Do not import cosmos_backup at module load — do_backup lazy-imports us.


def _refuse(kind: str, detail: str):
    from cosmos_backup import BackupRefusal
    raise BackupRefusal(kind, detail)


class FreezeHandle:
    """read_root() is the tree the backup walks. release() is always called."""

    kind = "none"

    def read_root(self) -> Path:
        raise NotImplementedError

    def info(self) -> dict:
        return {"kind": self.kind}

    def release(self) -> None:
        return None


class IdentityHandle(FreezeHandle):
    kind = "none"

    def __init__(self, root: Path):
        self._root = Path(root)

    def read_root(self) -> Path:
        return self._root

    def info(self) -> dict:
        return {"kind": "none", "read_root": str(self._root)}


class FrozenTree(FreezeHandle):
    """Injected freeze: a copy of source taken at capture(). Test pin."""

    kind = "copy"

    def __init__(self, frozen_root: Path, *, owned: bool = True):
        self._root = Path(frozen_root)
        self._owned = owned

    def read_root(self) -> Path:
        return self._root

    def info(self) -> dict:
        return {"kind": "copy", "read_root": str(self._root)}

    def release(self) -> None:
        if self._owned and self._root.exists():
            shutil.rmtree(self._root, True)

    @classmethod
    def capture(cls, source_root: Path, dest: Path, excludes=None) -> "FrozenTree":
        import cosmos_backup as cb
        source_root = Path(source_root).resolve()
        dest = Path(dest)
        if dest.exists():
            _refuse("FREEZE_DEST_OCCUPIED",
                    f"freeze dest already exists (will not overwrite): {dest}")
        dest.mkdir(parents=True)
        if excludes is None:
            excludes = cb.DEFAULT_EXCLUDES
        for rel in cb.iter_files(source_root, excludes):
            src = cb._child(source_root, rel)
            dst = cb._child(dest, rel)
            cb._xmkdirs(dst.parent)
            shutil.copy2(cb._x(src), cb._x(dst))
        return cls(dest, owned=True)


class VssHandle(FreezeHandle):
    kind = "vss"

    def __init__(self, read_root: Path, info: dict, delete):
        self._root = Path(read_root)
        self._info = dict(info)
        self._delete = delete
        self._released = False

    def read_root(self) -> Path:
        return self._root

    def info(self) -> dict:
        return dict(self._info)

    def release(self) -> None:
        if self._released:
            return
        self._released = True
        if self._delete is not None:
            self._delete()


def _is_handle(freeze) -> bool:
    """A freeze handle is the three methods do_backup actually calls."""
    return (callable(getattr(freeze, "read_root", None))
            and callable(getattr(freeze, "release", None))
            and callable(getattr(freeze, "info", None)))


def acquire(source_root: Path, freeze) -> FreezeHandle:
    """Return a freeze handle. freeze=True means VSS (never a silent live copy).

    A duck-typed object missing info() is BAD_FREEZE, never a silent live
    copy that later AttributeErrors in do_backup. Bite
    `_bite_unpinned_round6.json` (predecessor returned the handle).
    """
    if freeze in (None, False):
        return IdentityHandle(Path(source_root).resolve())
    if _is_handle(freeze):
        return freeze
    if freeze is True or freeze == "vss":
        return vss_acquire(Path(source_root).resolve())
    _refuse("BAD_FREEZE", f"freeze={type(freeze).__name__!r} is not True/vss/handle")


def volume_of(path: Path) -> str:
    p = Path(path).resolve()
    drive = p.drive
    if not drive or len(drive) < 2:
        _refuse("VSS_UNAVAILABLE", f"no drive letter on {p}")
    return drive + "\\"


def _drive_type(volume: str) -> int:
    if os.name != "nt":
        return 0
    k32 = ctypes.WinDLL("kernel32", use_last_error=True)
    k32.GetDriveTypeW.argtypes = [wintypes.LPCWSTR]
    k32.GetDriveTypeW.restype = wintypes.UINT
    return int(k32.GetDriveTypeW(volume))


DRIVE_FIXED = 3


def vss_acquire(source_root: Path) -> VssHandle:
    source_root = Path(source_root).resolve()
    if sys.platform != "win32":
        _refuse("VSS_UNAVAILABLE", f"VSS is Windows-only (platform={sys.platform})")
    volume = volume_of(source_root)
    dtype = _drive_type(volume)
    if dtype != DRIVE_FIXED:
        _refuse("VSS_UNAVAILABLE",
                f"volume {volume!r} drive_type={dtype} is not DRIVE_FIXED=3")
    created = _create_shadow(volume)
    device = created["device_object"]
    remainder = str(source_root)[len(Path(source_root).drive):]
    mapped = device.rstrip("\\") + remainder.replace("/", "\\")
    info = {
        "kind": "vss",
        "volume": volume,
        "shadow_id": created["shadow_id"],
        "device_object": device,
        "read_root": mapped,
        "binding": created.get("binding", "wmi"),
    }

    def _delete():
        _delete_shadow(created["shadow_id"], binding=created.get("binding"))

    return VssHandle(Path(mapped), info, _delete)


# ---------------------------------------------------------------- WMI / VSS
#
# Win32_ShadowCopy.Create via the WMI scripting API (IDispatch). pywin32 is
# not installed on this interpreter; stdlib ctypes is the binding.

_ole32 = None
_oleaut32 = None
_com_ready = False

VT_EMPTY = 0
VT_I4 = 3
VT_BSTR = 8
VT_DISPATCH = 9
VT_BOOL = 11
VT_ERROR = 10
VT_UI4 = 19
DISPATCH_METHOD = 1
DISPATCH_PROPERTYGET = 2
DISPATCH_PROPERTYPUT = 4
DISPID_PROPERTYPUT = -3
LOCALE_USER_DEFAULT = 0x0400
COINIT_APARTMENTTHREADED = 0x2
CLSCTX_INPROC_SERVER = 1
IID_IDispatch_s = "{00020400-0000-0000-C000-000000000046}"
IID_NULL_s = "{00000000-0000-0000-0000-000000000000}"


class GUID(Structure):
    _fields_ = [("Data1", wintypes.DWORD),
                ("Data2", wintypes.WORD),
                ("Data3", wintypes.WORD),
                ("Data4", ctypes.c_ubyte * 8)]


class _VARIANT_U(Union):
    # 16-byte union so VARIANT is 24 bytes on 64-bit Windows (vt+reserved=8).
    _fields_ = [
        ("llVal", ctypes.c_longlong),
        ("lVal", ctypes.c_int32),
        ("bstrVal", c_void_p),
        ("pdispVal", c_void_p),
        ("boolVal", ctypes.c_int16),
        ("ulVal", ctypes.c_uint32),
        ("scode", ctypes.c_int32),
        ("_pad16", ctypes.c_byte * 16),
    ]


class VARIANT(Structure):
    _anonymous_ = ("u",)
    _fields_ = [
        ("vt", ctypes.c_uint16),
        ("wReserved1", ctypes.c_uint16),
        ("wReserved2", ctypes.c_uint16),
        ("wReserved3", ctypes.c_uint16),
        ("u", _VARIANT_U),
    ]


class DISPPARAMS(Structure):
    _fields_ = [
        ("rgvarg", POINTER(VARIANT)),
        ("rgdispidNamedArgs", POINTER(ctypes.c_long)),
        ("cArgs", wintypes.UINT),
        ("cNamedArgs", wintypes.UINT),
    ]


class EXCEPINFO(Structure):
    _fields_ = [
        ("wCode", wintypes.WORD),
        ("wReserved", wintypes.WORD),
        ("bstrSource", c_void_p),
        ("bstrDescription", c_void_p),
        ("bstrHelpFile", c_void_p),
        ("dwHelpContext", wintypes.DWORD),
        ("pvReserved", c_void_p),
        ("pfnDeferredFillIn", c_void_p),
        ("scode", wintypes.LONG),
    ]


def _com_init():
    global _ole32, _oleaut32, _com_ready
    if _com_ready:
        return
    _ole32 = ctypes.WinDLL("ole32", use_last_error=True)
    _oleaut32 = ctypes.WinDLL("oleaut32", use_last_error=True)
    _ole32.CoInitializeEx.argtypes = [c_void_p, wintypes.DWORD]
    _ole32.CoInitializeEx.restype = wintypes.LONG
    _ole32.CLSIDFromProgID.argtypes = [wintypes.LPCWSTR, POINTER(GUID)]
    _ole32.CLSIDFromProgID.restype = wintypes.LONG
    _ole32.CLSIDFromString.argtypes = [wintypes.LPCWSTR, POINTER(GUID)]
    _ole32.CLSIDFromString.restype = wintypes.LONG
    _ole32.CoCreateInstance.argtypes = [
        POINTER(GUID), c_void_p, wintypes.DWORD, POINTER(GUID), POINTER(c_void_p)]
    _ole32.CoCreateInstance.restype = wintypes.LONG
    _oleaut32.SysAllocString.argtypes = [wintypes.LPCWSTR]
    _oleaut32.SysAllocString.restype = c_void_p
    _oleaut32.SysStringLen.argtypes = [c_void_p]
    _oleaut32.SysStringLen.restype = wintypes.UINT
    _oleaut32.VariantInit.argtypes = [POINTER(VARIANT)]
    _oleaut32.VariantClear.argtypes = [POINTER(VARIANT)]
    hr = _ole32.CoInitializeEx(None, COINIT_APARTMENTTHREADED)
    # S_OK=0, S_FALSE=1 already init, RPC_E_CHANGED_MODE=0x80010106
    if hr not in (0, 1, 0x80010106, -2147417850):
        _refuse("VSS_UNAVAILABLE", f"CoInitializeEx hr=0x{hr & 0xFFFFFFFF:08X}")
    # WMI scripting needs impersonate; TOO_LATE means someone else already set it.
    _ole32.CoInitializeSecurity.argtypes = [
        c_void_p, ctypes.c_long, c_void_p, c_void_p,
        ctypes.c_ulong, ctypes.c_ulong, c_void_p, ctypes.c_ulong, c_void_p]
    _ole32.CoInitializeSecurity.restype = wintypes.LONG
    hr_sec = _ole32.CoInitializeSecurity(
        None, -1, None, None,
        0, 3, None, 0, None)  # DEFAULT auth, IMPERSONATE
    if hr_sec not in (0, 0x80010119, -2147417831):  # S_OK or RPC_E_TOO_LATE
        # continue anyway — Create() will type the real leftover
        pass
    _com_ready = True


def _guid(s: str) -> GUID:
    g = GUID()
    hr = _ole32.CLSIDFromString(s, byref(g))
    if hr != 0:
        _refuse("VSS_UNAVAILABLE", f"CLSIDFromString({s}) hr=0x{hr & 0xFFFFFFFF:08X}")
    return g


def _bstr_to_str(ptr) -> str:
    if not ptr:
        return ""
    n = int(_oleaut32.SysStringLen(ptr))
    return ctypes.wstring_at(ptr, n)


class _Dispatch:
    def __init__(self, pdisp: int):
        if not pdisp:
            _refuse("VSS_UNAVAILABLE", "null IDispatch")
        self._p = pdisp
        vtbl = ctypes.cast(c_void_p(pdisp), POINTER(c_void_p)).contents
        # IDispatch vtable as an array of pointers
        self._fns = ctypes.cast(vtbl, POINTER(c_void_p * 8)).contents
        self._addref()

    def _call(self, slot, restype, *args):
        proto = ctypes.WINFUNCTYPE(restype, c_void_p, *([type(a) for a in args]))
        fn = proto(self._fns[slot])
        return fn(self._p, *args)

    def _addref(self):
        ctypes.WINFUNCTYPE(wintypes.ULONG, c_void_p)(self._fns[1])(self._p)

    def _release(self):
        ctypes.WINFUNCTYPE(wintypes.ULONG, c_void_p)(self._fns[2])(self._p)

    def _dispid(self, name: str) -> int:
        iid_null = _guid(IID_NULL_s)
        names = (c_wchar_p * 1)(name)
        dispids = (ctypes.c_long * 1)()
        GetIDsOfNames = ctypes.WINFUNCTYPE(
            wintypes.LONG, c_void_p, POINTER(GUID), POINTER(c_wchar_p),
            wintypes.UINT, wintypes.DWORD, POINTER(ctypes.c_long)
        )(self._fns[5])
        hr = GetIDsOfNames(self._p, byref(iid_null), names, 1,
                           LOCALE_USER_DEFAULT, dispids)
        if hr != 0:
            _refuse("VSS_UNAVAILABLE",
                    f"GetIDsOfNames({name!r}) hr=0x{hr & 0xFFFFFFFF:08X}")
        return int(dispids[0])

    def _invoke(self, dispid: int, flags: int, params: DISPPARAMS,
                name: str = "?") -> VARIANT:
        iid_null = _guid(IID_NULL_s)
        result = VARIANT()
        _oleaut32.VariantInit(byref(result))
        excep = EXCEPINFO()
        argerr = wintypes.UINT()
        Invoke = ctypes.WINFUNCTYPE(
            wintypes.LONG, c_void_p, ctypes.c_long, POINTER(GUID),
            wintypes.DWORD, wintypes.WORD, POINTER(DISPPARAMS),
            POINTER(VARIANT), POINTER(EXCEPINFO), POINTER(wintypes.UINT)
        )(self._fns[6])
        hr = Invoke(self._p, dispid, byref(iid_null), LOCALE_USER_DEFAULT,
                    flags, byref(params), byref(result), byref(excep), byref(argerr))
        if hr != 0:
            desc = _bstr_to_str(excep.bstrDescription)
            sc = int(excep.scode) & 0xFFFFFFFF
            _oleaut32.VariantClear(byref(result))
            _refuse("VSS_UNAVAILABLE",
                    f"IDispatch.Invoke {name!r} dispid={dispid} flags={flags} "
                    f"hr=0x{hr & 0xFFFFFFFF:08X} scode=0x{sc:08X} {desc}")
        return result

    def _py_from_var(self, var: VARIANT):
        vt = var.vt
        if vt == VT_EMPTY:
            return None
        if vt in (VT_I4, VT_UI4):
            return int(var.lVal if vt == VT_I4 else var.ulVal)
        if vt == VT_BOOL:
            return bool(var.boolVal)
        if vt == VT_BSTR:
            return _bstr_to_str(var.bstrVal)
        if vt == VT_DISPATCH:
            p = var.pdispVal
            if not p:
                return None
            return _Dispatch(p)
        _refuse("VSS_UNAVAILABLE", f"unsupported VARIANT vt={vt}")

    def _to_var(self, value) -> VARIANT:
        var = VARIANT()
        _oleaut32.VariantInit(byref(var))
        if value is None:
            var.vt = VT_EMPTY
        elif isinstance(value, bool):
            var.vt = VT_BOOL
            var.boolVal = -1 if value else 0
        elif isinstance(value, int):
            var.vt = VT_I4
            var.lVal = int(value)
        elif isinstance(value, str):
            var.vt = VT_BSTR
            var.bstrVal = _oleaut32.SysAllocString(value)
        elif isinstance(value, _Dispatch):
            var.vt = VT_DISPATCH
            var.pdispVal = value._p
            value._addref()
        else:
            _refuse("VSS_UNAVAILABLE", f"cannot pack {type(value).__name__}")
        return var

    def _invoke_name(self, name: str, flags: int, *args):
        dispid = self._dispid(name)
        n = len(args)
        arr = (VARIANT * max(n, 1))()
        packed = []
        for i, a in enumerate(reversed(args)):
            arr[i] = self._to_var(a)
            packed.append(arr[i])
        params = DISPPARAMS()
        if n:
            params.rgvarg = ctypes.cast(arr, POINTER(VARIANT))
            params.cArgs = n
        named = ctypes.c_long(DISPID_PROPERTYPUT)
        if flags & DISPATCH_PROPERTYPUT:
            params.rgdispidNamedArgs = pointer(named)
            params.cNamedArgs = 1
        try:
            result = self._invoke(dispid, flags, params, name=name)
            return self._py_from_var(result)
        finally:
            for v in packed:
                _oleaut32.VariantClear(byref(v))

    def __getattr__(self, name: str):
        if name.startswith("_"):
            raise AttributeError(name)
        return self._invoke_name(name, DISPATCH_METHOD | DISPATCH_PROPERTYGET)

    def __setattr__(self, name: str, value):
        if name.startswith("_"):
            object.__setattr__(self, name, value)
            return
        self._invoke_name(name, DISPATCH_PROPERTYPUT, value)

    def __call_method__(self, name: str, *args):
        return self._invoke_name(name, DISPATCH_METHOD | DISPATCH_PROPERTYGET, *args)


def _dispatch_progid(progid: str) -> _Dispatch:
    _com_init()
    clsid = GUID()
    hr = _ole32.CLSIDFromProgID(progid, byref(clsid))
    if hr != 0:
        _refuse("VSS_UNAVAILABLE",
                f"CLSIDFromProgID({progid!r}) hr=0x{hr & 0xFFFFFFFF:08X}")
    iid = _guid(IID_IDispatch_s)
    punk = c_void_p()
    hr = _ole32.CoCreateInstance(byref(clsid), None, CLSCTX_INPROC_SERVER,
                                 byref(iid), byref(punk))
    if hr != 0:
        _refuse("VSS_UNAVAILABLE",
                f"CoCreateInstance({progid!r}) hr=0x{hr & 0xFFFFFFFF:08X}")
    return _Dispatch(int(punk.value))


def _wmi_service():
    loc = _dispatch_progid("WbemScripting.SWbemLocator")
    svc = loc.__call_method__("ConnectServer", ".", r"root\cimv2")
    if svc is None:
        _refuse("VSS_UNAVAILABLE", "SWbemLocator.ConnectServer returned null")
    return svc


def _wmi_put(obj: _Dispatch, prop: str, value) -> None:
    """SWbemObject property put via Properties_.Item.Value (not a bare setattr)."""
    props = obj.__getattr__("Properties_")
    item = props.__call_method__("Item", prop)
    item.Value = value


# Create() return codes (Win32_ShadowCopy). 1 = access denied (need admin).
_CREATE_RC = {
    0: "success",
    1: "access denied",
    2: "invalid argument",
    3: "specified volume not found",
    4: "specified volume not supported",
    5: "unsupported shadow copy context",
    6: "insufficient storage",
    7: "volume is in use",
    8: "maximum number of shadow copies reached",
    9: "another shadow copy creation is already in progress",
    10: "specified shadow copy provider not registered",
    11: "specified shadow copy provider not registered",
    12: "shadow copy provider vetoed the operation",
    13: "provider not ready",
    14: "device not ready",
    15: "provider failure",
    16: "unknown error",
}


def _create_shadow(volume: str) -> dict:
    """Create a ClientAccessible shadow. REFUSE VSS_UNAVAILABLE on any miss."""
    try:
        svc = _wmi_service()
        sc = svc.__call_method__("Get", "Win32_ShadowCopy")
        methods = sc.__getattr__("Methods_")
        try:
            create_m = methods.__call_method__("Item", "Create")
        except Exception:
            create_m = methods.__call_method__("Create")
        in_sig = create_m.__getattr__("inParameters")
        inparams = in_sig.__call_method__("SpawnInstance_")
        vol = volume if volume.endswith("\\") else volume + "\\"
        _wmi_put(inparams, "Volume", vol)
        got_vol = inparams.__getattr__("Volume")
        if not got_vol:
            _refuse("VSS_UNAVAILABLE",
                    f"Win32_ShadowCopy.Create in-param Volume read back empty "
                    f"(wrote {vol!r})")
        out = sc.__call_method__("ExecMethod_", "Create", inparams)
        rc = int(out.__getattr__("ReturnValue"))
        if rc != 0:
            _refuse("VSS_UNAVAILABLE",
                    f"Win32_ShadowCopy.Create rc={rc} ({_CREATE_RC.get(rc, 'unknown')}) "
                    f"volume={volume!r}")
        shadow_id = str(out.__getattr__("ShadowID"))
        q = svc.__call_method__(
            "ExecQuery",
            f"SELECT DeviceObject, ID FROM Win32_ShadowCopy WHERE ID='{shadow_id}'")
        count = int(q.__getattr__("Count"))
        if count < 1:
            _refuse("VSS_UNAVAILABLE",
                    f"shadow {shadow_id} created but query Count=0")
        item = q.__call_method__("ItemIndex", 0)
        device = str(item.__getattr__("DeviceObject"))
        if not device:
            _refuse("VSS_UNAVAILABLE", f"shadow {shadow_id} has empty DeviceObject")
        return {
            "shadow_id": shadow_id,
            "device_object": device,
            "binding": "wmi-idispatch",
            "volume": volume,
        }
    except Exception as e:
        from cosmos_backup import BackupRefusal
        if isinstance(e, BackupRefusal):
            raise
        _refuse("VSS_UNAVAILABLE", f"{type(e).__name__}: {e}")


def _delete_shadow(shadow_id: str, binding=None) -> None:
    """Delete a shadow we created. Never raises into source-tree deletes."""
    try:
        svc = _wmi_service()
        q = svc.__call_method__(
            "ExecQuery",
            f"SELECT * FROM Win32_ShadowCopy WHERE ID='{shadow_id}'")
        count = int(q.__getattr__("Count"))
        for i in range(count):
            item = q.__call_method__("ItemIndex", i)
            item.__call_method__("Delete_")
    except Exception:
        return


def _filesystem(volume: str) -> str | None:
    """Win32_LogicalDisk.FileSystem, or None if WMI cannot answer."""
    try:
        svc = _wmi_service()
        letter = volume[:2].upper() if len(volume) >= 2 else volume
        q = svc.__call_method__(
            "ExecQuery",
            "SELECT FileSystem FROM Win32_LogicalDisk WHERE DeviceID='%s'" % letter)
        if int(q.__getattr__("Count")) < 1:
            return None
        return str(q.__call_method__("ItemIndex", 0).__getattr__("FileSystem") or "") or None
    except Exception:
        return None


def probe(volume: str = "V:\\") -> dict:
    """Create a shadow and delete it. Never copies COSMOS files.

    ok is True when the result is typed (success or VSS_UNAVAILABLE). A
    working freeze is freeze_kind=vss; the common leftover is
    VSS_UNAVAILABLE (Create scode, often WBEM_E_INVALID_PARAMETER /
    access denied — Keith's elevated session).
    """
    rec = {
        "schema": "cosmos-backup-freeze/1",
        "volume": volume,
        "platform": sys.platform,
        "drive_type": _drive_type(volume) if sys.platform == "win32" else None,
        "filesystem": _filesystem(volume) if sys.platform == "win32" else None,
        "freeze_kind": None,
        "kind": None,
        "detail": None,
        "shadow_id": None,
        "device_object": None,
        "released": False,
        "binding": None,
    }
    handle = None
    try:
        # Probe the volume itself, not a COSMOS subtree — cheaper mapping,
        # still a real Create. vss_acquire needs a path on the volume.
        root = Path(volume)
        handle = vss_acquire(root)
        info = handle.info()
        rec["freeze_kind"] = "vss"
        rec["kind"] = "ok"
        rec["shadow_id"] = info.get("shadow_id")
        rec["device_object"] = info.get("device_object")
        rec["binding"] = info.get("binding")
        rec["read_root"] = info.get("read_root")
    except Exception as e:
        rec["kind"] = getattr(e, "kind", None) or type(e).__name__
        rec["detail"] = getattr(e, "detail", None) or str(e)
        rec["freeze_kind"] = rec["kind"]
    finally:
        if handle is not None:
            handle.release()
            rec["released"] = True
    rec["ok"] = rec["kind"] in ("ok", "VSS_UNAVAILABLE")
    return rec


def main(argv=None) -> int:
    import argparse
    import json
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--probe", action="store_true",
                    help="create+delete a VSS shadow; copies nothing")
    ap.add_argument("--volume", default="V:\\")
    args = ap.parse_args(argv)
    if args.probe:
        rec = probe(args.volume)
        print(json.dumps(rec, indent=2, default=str))
        return 0 if rec.get("ok") else 2
    print("usage: cosmos_backup_freeze.py --probe [--volume V:\\]", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
