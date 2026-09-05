#!/usr/bin/env python3
"""Dump every ISp* / ISpeech* IID from the BOX'S OWN sapi.dll typelib.

Measured, not remembered. Writes JSON to stdout. Read-only: LoadTypeLib does
not register anything (LoadTypeLib on a full path does not call RegisterTypeLib).

    py -3.14 builds/cvm-dt/_disposal/sapi_typelib_probe.py
"""
from __future__ import annotations

import ctypes
import ctypes.wintypes as w
import json
import sys

ole32 = ctypes.WinDLL("ole32")
oleaut32 = ctypes.WinDLL("oleaut32")


class GUID(ctypes.Structure):
    _fields_ = [("Data1", ctypes.c_ulong), ("Data2", ctypes.c_ushort),
                ("Data3", ctypes.c_ushort), ("Data4", ctypes.c_ubyte * 8)]

    def __str__(self) -> str:
        return "{%08X-%04X-%04X-%s-%s}" % (
            self.Data1, self.Data2, self.Data3,
            "".join("%02X" % b for b in self.Data4[:2]),
            "".join("%02X" % b for b in self.Data4[2:]))


class TYPEATTR(ctypes.Structure):
    """Only the head matters: guid is at offset 0, typekind later."""
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


TKIND = {0: "enum", 1: "record", 2: "module", 3: "interface",
         4: "dispatch", 5: "coclass", 6: "alias", 7: "union"}


def vcall(punk, idx, restype, argtypes, *args):
    vtbl = ctypes.cast(punk, ctypes.POINTER(ctypes.c_void_p))[0]
    fn = ctypes.cast(vtbl, ctypes.POINTER(ctypes.c_void_p))[idx]
    proto = ctypes.WINFUNCTYPE(restype, ctypes.c_void_p, *argtypes)
    return proto(fn)(punk, *args)


def release(punk) -> None:
    if punk:
        vcall(punk, 2, ctypes.c_ulong, ())


def main() -> int:
    ole32.CoInitializeEx(None, 0x2)
    tl = ctypes.c_void_p()
    oleaut32.LoadTypeLib.argtypes = [ctypes.c_wchar_p,
                                     ctypes.POINTER(ctypes.c_void_p)]
    oleaut32.LoadTypeLib.restype = ctypes.HRESULT
    path = r"C:\Windows\System32\Speech\Common\sapi.dll"
    oleaut32.LoadTypeLib(path, ctypes.byref(tl))

    n = vcall(tl, 3, ctypes.c_uint, ())
    out = {"typelib": path, "type_count": int(n), "types": {}}
    for i in range(int(n)):
        name = ctypes.c_void_p()
        hr = vcall(tl, 9, ctypes.HRESULT,
                   (ctypes.c_int, ctypes.POINTER(ctypes.c_void_p),
                    ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p),
                   i, ctypes.byref(name), None, None, None)
        if hr:
            continue
        nm = ctypes.wstring_at(name.value) if name.value else ""
        oleaut32.SysFreeString(name)
        if not (nm.startswith("ISp") or nm.startswith("SPEVENT")
                or nm.startswith("SPRECOSTATE") or nm.startswith("SPGRAMMAR")):
            continue
        ti = ctypes.c_void_p()
        if vcall(tl, 4, ctypes.HRESULT,
                 (ctypes.c_uint, ctypes.POINTER(ctypes.c_void_p)),
                 i, ctypes.byref(ti)):
            continue
        pattr = ctypes.POINTER(TYPEATTR)()
        if vcall(ti, 3, ctypes.HRESULT,
                 (ctypes.POINTER(ctypes.POINTER(TYPEATTR)),),
                 ctypes.byref(pattr)) == 0:
            a = pattr.contents
            out["types"][nm] = {
                "iid": str(a.guid), "kind": TKIND.get(a.typekind, a.typekind),
                "cFuncs": int(a.cFuncs), "cbSizeVft": int(a.cbSizeVft),
                "vtbl_slots": int(a.cbSizeVft) // 8,
                "cImplTypes": int(a.cImplTypes),
            }
            vcall(ti, 19, None, (ctypes.POINTER(TYPEATTR),), pattr)
        release(ti)
    release(tl)
    json.dump(out, sys.stdout, indent=1, sort_keys=True)
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
