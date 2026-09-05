#!/usr/bin/env python3
"""Dump SAPI enum VALUES from the box's own sapi.dll typelib.

Companion to sapi_typelib_probe.py (which dumps IIDs + vtable widths). Every
magic number cvm_dt_stt.py uses is read from here, not from memory.

    py -3.14 builds/cvm-dt/_disposal/sapi_enum_probe.py
"""
from __future__ import annotations

import ctypes
import json
import sys

ole32 = ctypes.WinDLL("ole32")
oleaut32 = ctypes.WinDLL("oleaut32")

WANT = ("SPEVENTENUM", "SPEVENTLPARAMTYPE", "SPRECOSTATE", "SPGRAMMARSTATE",
        "SPRULESTATE", "SPLOADOPTIONS", "SPFILEMODE", "SPINTERFERENCE",
        "SPRECOGNIZERSTATUSFLAGS", "SPCONTEXTSTATE", "SPAUDIOSTATE")


class GUID(ctypes.Structure):
    _fields_ = [("Data1", ctypes.c_ulong), ("Data2", ctypes.c_ushort),
                ("Data3", ctypes.c_ushort), ("Data4", ctypes.c_ubyte * 8)]


class TYPEATTR(ctypes.Structure):
    _fields_ = [("guid", GUID), ("lcid", ctypes.c_ulong),
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
                ("wMinorVerNum", ctypes.c_ushort)]


class TYPEDESC(ctypes.Structure):
    _fields_ = [("u", ctypes.c_void_p), ("vt", ctypes.c_ushort),
                ("_pad", ctypes.c_ushort * 3)]


class PARAMDESC(ctypes.Structure):
    _fields_ = [("pparamdescex", ctypes.c_void_p),
                ("wParamFlags", ctypes.c_ushort),
                ("_pad", ctypes.c_ushort * 3)]


class ELEMDESC(ctypes.Structure):
    _fields_ = [("tdesc", TYPEDESC), ("paramdesc", PARAMDESC)]


class VARDESC(ctypes.Structure):
    _fields_ = [("memid", ctypes.c_long), ("_pad0", ctypes.c_long),
                ("lpstrSchema", ctypes.c_void_p),
                ("lpvarValue", ctypes.c_void_p),
                ("elemdescVar", ELEMDESC),
                ("wVarFlags", ctypes.c_ushort),
                ("varkind", ctypes.c_int)]


class VARIANT_HEAD(ctypes.Structure):
    _fields_ = [("vt", ctypes.c_ushort), ("r1", ctypes.c_ushort),
                ("r2", ctypes.c_ushort), ("r3", ctypes.c_ushort),
                ("llVal", ctypes.c_longlong)]


def vcall(punk, idx, restype, argtypes, *args):
    vtbl = ctypes.cast(punk, ctypes.POINTER(ctypes.c_void_p))[0]
    fn = ctypes.cast(vtbl, ctypes.POINTER(ctypes.c_void_p))[idx]
    return ctypes.WINFUNCTYPE(restype, ctypes.c_void_p, *argtypes)(fn)(
        punk, *args)


def _name(ti, memid):
    """ITypeInfo::GetDocumentation(memid) -> name."""
    bs = ctypes.c_void_p()
    if vcall(ti, 12, ctypes.HRESULT,
             (ctypes.c_long, ctypes.POINTER(ctypes.c_void_p),
              ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p),
             memid, ctypes.byref(bs), None, None, None):
        return None
    out = ctypes.wstring_at(bs.value) if bs.value else None
    oleaut32.SysFreeString(bs)
    return out


def main() -> int:
    ole32.CoInitializeEx(None, 0x2)
    oleaut32.LoadTypeLib.argtypes = [ctypes.c_wchar_p,
                                     ctypes.POINTER(ctypes.c_void_p)]
    oleaut32.LoadTypeLib.restype = ctypes.HRESULT
    path = r"C:\Windows\System32\Speech\Common\sapi.dll"
    tl = ctypes.c_void_p()
    oleaut32.LoadTypeLib(path, ctypes.byref(tl))

    out = {"typelib": path, "enums": {}}
    for i in range(int(vcall(tl, 3, ctypes.c_uint, ()))):
        ti = ctypes.c_void_p()
        if vcall(tl, 4, ctypes.HRESULT,
                 (ctypes.c_uint, ctypes.POINTER(ctypes.c_void_p)),
                 i, ctypes.byref(ti)):
            continue
        nm = _name(ti, -1)  # MEMBERID_NIL -> the type's own name
        pattr = ctypes.POINTER(TYPEATTR)()
        if nm in WANT and vcall(
                ti, 3, ctypes.HRESULT,
                (ctypes.POINTER(ctypes.POINTER(TYPEATTR)),),
                ctypes.byref(pattr)) == 0:
            vals = {}
            for j in range(int(pattr.contents.cVars)):
                pv = ctypes.POINTER(VARDESC)()
                if vcall(ti, 6, ctypes.HRESULT,
                         (ctypes.c_uint,
                          ctypes.POINTER(ctypes.POINTER(VARDESC))),
                         j, ctypes.byref(pv)):
                    continue
                v = pv.contents
                mn = _name(ti, v.memid)
                if mn and v.lpvarValue:
                    var = ctypes.cast(
                        v.lpvarValue, ctypes.POINTER(VARIANT_HEAD)).contents
                    vals[mn] = int(ctypes.c_int32(
                        var.llVal & 0xFFFFFFFF).value)
                vcall(ti, 21, None, (ctypes.POINTER(VARDESC),), pv)
            out["enums"][nm] = vals
            vcall(ti, 19, None, (ctypes.POINTER(TYPEATTR),), pattr)
        vcall(ti, 2, ctypes.c_ulong, ())
    vcall(tl, 2, ctypes.c_ulong, ())
    json.dump(out, sys.stdout, indent=1, sort_keys=True)
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
