"""Throwaway diagnostic: which SAPI IDispatch step raises DISP_E_BADVARTYPE.

Replicates cvm_dt._sapi_wav step by step and prints after each call, then
retries the AudioOutputStream putref WITH the DISPID_PROPERTYPUT named arg.
Not part of the build. Staged to _delme after the answer is read.
"""
import ctypes
import os
import tempfile
from ctypes import POINTER, byref, c_void_p
from ctypes.wintypes import BYTE, DWORD, WORD


class GUID(ctypes.Structure):
    _fields_ = (("Data1", DWORD), ("Data2", WORD), ("Data3", WORD),
                ("Data4", BYTE * 8))


class BRECORD(ctypes.Structure):
    _fields_ = (("pvRecord", c_void_p), ("pRecInfo", c_void_p))


class VARIANT(ctypes.Structure):
    class _U(ctypes.Union):
        _fields_ = (("llVal", ctypes.c_longlong), ("bstrVal", c_void_p),
                    ("pdispVal", c_void_p), ("lVal", ctypes.c_int),
                    ("brecord", BRECORD))
    _anonymous_ = ("u",)
    _fields_ = (("vt", ctypes.c_ushort), ("r1", ctypes.c_ushort),
                ("r2", ctypes.c_ushort), ("r3", ctypes.c_ushort), ("u", _U))


print("sizeof(VARIANT) =", ctypes.sizeof(VARIANT),
      "expected", 8 + 2 * ctypes.sizeof(c_void_p))


class DISPPARAMS(ctypes.Structure):
    _fields_ = (("rgvarg", POINTER(VARIANT)),
                ("rgdispidNamedArgs", POINTER(ctypes.c_int)),
                ("cArgs", ctypes.c_uint), ("cNamedArgs", ctypes.c_uint))


VT_BSTR, VT_I4, VT_DISPATCH, VT_UNKNOWN = 8, 3, 9, 13
METHOD, PUT, PUTREF = 1, 4, 8
DISPID_PROPERTYPUT = -3
LCID = 0x400
IID_NULL = GUID(0, 0, 0, (BYTE * 8)())
IID_IDispatch = GUID(0x00020400, 0, 0,
                     (BYTE * 8).from_buffer_copy(bytes.fromhex("C000000000000046")))
ole = ctypes.windll.ole32
oleaut = ctypes.windll.oleaut32
ole.CoInitializeEx(None, 0)
ole.CLSIDFromProgID.argtypes = [ctypes.c_wchar_p, POINTER(GUID)]
ole.CLSIDFromProgID.restype = ctypes.HRESULT
ole.CoCreateInstance.argtypes = [POINTER(GUID), c_void_p, DWORD, POINTER(GUID),
                                 POINTER(c_void_p)]
ole.CoCreateInstance.restype = ctypes.HRESULT
oleaut.SysAllocString.argtypes = [ctypes.c_wchar_p]
oleaut.SysAllocString.restype = c_void_p


def vtbl(p, i):
    return ctypes.cast(ctypes.cast(p, POINTER(c_void_p))[0], POINTER(c_void_p))[i]


def create(progid):
    c = GUID()
    ole.CLSIDFromProgID(progid, byref(c))
    p = c_void_p()
    ole.CoCreateInstance(byref(c), None, 0x17, byref(IID_IDispatch), byref(p))
    return p


def dispid(p, name):
    names = (ctypes.c_wchar_p * 1)(name)
    ids = (ctypes.c_int * 1)()
    proto = ctypes.WINFUNCTYPE(ctypes.HRESULT, c_void_p, POINTER(GUID),
                               POINTER(ctypes.c_wchar_p), ctypes.c_uint, DWORD,
                               POINTER(ctypes.c_int))
    proto(vtbl(p, 5))(p, byref(IID_NULL), names, 1, LCID, ids)
    return int(ids[0])


def invoke(p, name, args, flags=METHOD, named=False, vt_obj=VT_DISPATCH):
    did = dispid(p, name)
    n = len(args)
    arr = (VARIANT * max(n, 1))()
    for i, a in enumerate(reversed(args)):
        if isinstance(a, int):
            arr[i].vt = VT_I4
            arr[i].lVal = a
        elif isinstance(a, c_void_p):
            arr[i].vt = vt_obj
            arr[i].pdispVal = a
        else:
            arr[i].vt = VT_BSTR
            arr[i].bstrVal = oleaut.SysAllocString(str(a))
    nm = ctypes.c_int(DISPID_PROPERTYPUT)
    dp = DISPPARAMS()
    if n:
        dp.rgvarg = arr
        dp.cArgs = n
    if named:
        dp.rgdispidNamedArgs = ctypes.pointer(nm)
        dp.cNamedArgs = 1
    proto = ctypes.WINFUNCTYPE(ctypes.HRESULT, c_void_p, ctypes.c_int,
                               POINTER(GUID), DWORD, ctypes.c_ushort,
                               POINTER(DISPPARAMS), c_void_p, c_void_p, c_void_p)
    proto(vtbl(p, 6))(p, did, byref(IID_NULL), LCID, flags, byref(dp),
                      None, None, None)


fd, wav = tempfile.mkstemp(suffix=".wav")
os.close(fd)
st = create("SAPI.SpFileStream")
print("SpFileStream created:", bool(st.value))
invoke(st, "Open", [wav, 3])
print("SpFileStream.Open OK")
vo = create("SAPI.SpVoice")
print("SpVoice created:", bool(vo.value))
ok = False
for label, kw in (("PUTREF named=False (shipped)", dict(flags=PUTREF, named=False)),
                  ("PUTREF named=True", dict(flags=PUTREF, named=True)),
                  ("PUT named=True", dict(flags=PUT, named=True)),
                  ("PUTREF named=True VT_UNKNOWN",
                   dict(flags=PUTREF, named=True, vt_obj=VT_UNKNOWN))):
    try:
        invoke(vo, "AudioOutputStream", [st], **kw)
        print("AudioOutputStream %-32s -> OK" % label)
        ok = True
        break
    except OSError as e:
        print("AudioOutputStream %-32s -> %s" % (label, e))
if ok:
    invoke(vo, "Speak", ["hello from cosmos", 0])
    print("Speak OK")
    invoke(st, "Close", [])
    print("Close OK, wav bytes:", os.path.getsize(wav))
os.unlink(wav)
