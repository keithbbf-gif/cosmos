#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cvm-dt EAR — the on-box recognizer, and the regression it closes.

The defect (measured, not asserted): every STT path in this fence went through
`cosmos_cvm_push.probe_stt`, which needs BOTH the `vosk` wheel AND
`COSMOS_VOSK_MODEL`. This box has neither, so `default_transcriber()` returned
`None` and the desktop client answered `STT_NONE` to every utterance. The
mouth worked; there was no ear.

`test_pre_ear_code_has_no_ear_on_this_box` is the regression row and it is a
REAL A/B, not a story: it reconstructs the exact predecessor expression
(`probe_vosk()` -> `VoskTranscriber` or `None`, the body staged verbatim under
`_disposal/predispose_cvm_dt_voice_*/`) and runs it in the same process as the
replacement. Old returns None; new returns a transcriber that produces a
transcript. Run this file against the pre-ear `cvm_dt_voice.py` and that row
fails, because `default_ear` does not exist there.

    py -3.14 builds\\cvm-dt\\test_cvm_dt_stt.py

rc=0 is not the gate. The runtime-binding value is `live_value.round_trip`:
words the Windows recognizer returned from audio the Windows synthesizer
produced in this process, plus the recognizer token id that did it. No
loopback fake can emit that, and no network or credential is involved.
"""
from __future__ import annotations

import ctypes
import json
import re
import sys
import tempfile
from pathlib import Path

_HERE = Path(__file__).resolve().parent
for _p in (_HERE, _HERE.parents[1] / "cosmos"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import cvm_dt_stt as S  # noqa: E402
from cvm_dt import CvmDtError, RefusalKind, _sapi_wav  # noqa: E402
from cosmos_cvm_push import probe_stt as probe_vosk  # noqa: E402

SRC = (_HERE / "cvm_dt_stt.py").read_text(encoding="utf-8")
DRIVE_LIT = re.compile(r"[A-Za-z]:\\\\?(?:A|Ai|Research4)\b")
PHRASE = "what is the queue depth"


# --------------------------------------------------------------------------
# 1. the constants are bound to THIS box, not to memory
# --------------------------------------------------------------------------
def test_every_iid_and_vtable_matches_the_boxs_typelib():
    """Hard-coded IIDs / vtable widths re-read from sapi.dll at runtime."""
    got = S.verify_abi()
    assert got["ok"], got["mismatches"]
    live = S.read_typelib()
    assert set(live) == set(S.IID), (sorted(live), sorted(S.IID))
    for name, iid in S.IID.items():
        assert live[name]["iid"].upper() == iid.upper(), name
        assert live[name]["slots"] == S.VTBL_SLOTS[name], name
    assert ctypes.sizeof(S.SPEVENT) == S.SPEVENT_ABI_BYTES
    return {"typelib": got["typelib"], "checked": len(S.IID),
            "spevent_bytes": got["spevent_bytes"]}


def test_spfei_sets_the_two_reserved_bits():
    """SetInterest silently delivers NOTHING if the reserved bits are dropped."""
    m = S.SPFEI(S.SPEI_RECOGNITION)
    assert m & (1 << S.SPEI_RESERVED1)
    assert m & (1 << S.SPEI_RESERVED2)
    assert m & (1 << S.SPEI_RECOGNITION)
    assert S.SPFEI(S.SPEI_RECOGNITION) != (1 << S.SPEI_RECOGNITION)
    return {"interest_mask": hex(m)}


# --------------------------------------------------------------------------
# 2. THE REGRESSION — the predecessor has no ear on this box
# --------------------------------------------------------------------------
def _pre_ear_default_transcriber():
    """The staged predecessor body, verbatim from _disposal/predispose_*.

        def default_transcriber() -> Optional[Transcriber]:
            p = probe_vosk()
            return VoskTranscriber(str(p["model"])) if p.get("ok") else None
    """
    from cvm_dt_voice import VoskTranscriber
    p = probe_vosk()
    return VoskTranscriber(str(p["model"])) if p.get("ok") else None


def test_pre_ear_code_has_no_ear_on_this_box():
    """OLD -> None. NEW -> a transcriber that actually transcribes."""
    old = _pre_ear_default_transcriber()
    vosk = probe_vosk()
    new = S.default_ear()
    assert vosk.get("ok") is False, (
        "this box now has VOSK; the A/B needs the no-vosk box it was taken on")
    assert old is None, "predecessor unexpectedly bound an ear: %r" % old
    assert new is not None, "replacement bound no ear"
    pcm, rate = S.wav_to_pcm(_sapi_wav(PHRASE))
    got = new.transcribe(pcm, rate)
    assert got["transcript"].strip(), got
    return {"old_transcriber": None, "new_transcriber": type(new).__name__,
            "vosk_detail": vosk.get("detail"),
            "new_heard": got["transcript"], "new_engine": got["engine"]}


def test_voice_client_binds_the_ear_not_none():
    """The wired path: cvm_dt_voice.default_transcriber is no longer VOSK-only."""
    import cvm_dt_voice as V
    got = V.default_transcriber()
    assert got is not None, "cvm_dt_voice still returns None with no vosk"
    ear = V.probe_ear()
    assert ear["ok"] is True and ear["kind"] == "ok", ear
    return {"bound": type(got).__name__, "engine": ear.get("engine"),
            "recognizer": ear.get("recognizer"), "source": ear.get("source")}


# --------------------------------------------------------------------------
# 3. the round trip — the live value
# --------------------------------------------------------------------------
def test_mouth_to_ear_round_trip():
    """SAPI TTS -> SAPI reco. A transcript only this box can produce."""
    rec = S.run_selftest(PHRASE)
    lv = rec["live_value"]
    assert rec["ok"] is True, rec
    assert lv["heard"].strip(), lv
    assert lv["word_recall"] > 0.0, lv
    assert S.SPEI_RECOGNITION in lv["events"], lv["events"]
    assert lv["recognizer"], lv
    return lv


def test_empty_audio_is_stt_none_not_a_fabricated_word():
    """Silence must refuse. A confident wrong word is the worst answer."""
    try:
        S.SapiTranscriber().transcribe(b"\x00\x00" * 8000, S.STT_RATE)
    except CvmDtError as e:
        assert e.kind == RefusalKind.STT_NONE, e.kind
        return {"kind": str(e.kind), "detail": str(e)[:90]}
    raise AssertionError("silence produced a transcript")


def test_no_audio_at_all_refuses_before_com():
    try:
        S.SapiTranscriber().finish()
    except CvmDtError as e:
        assert e.kind == RefusalKind.STT_NONE
        return {"detail": str(e)[:60]}
    raise AssertionError("empty buffer did not refuse")


# --------------------------------------------------------------------------
# 4. the engine-capability fallback (the DNN finding)
# --------------------------------------------------------------------------
def test_dictationless_engine_refuses_by_name_and_is_skipped():
    """The OneCore DNN binds, then cannot dictate. Named refusal, then skip.

    Pinned: a typed STT_NONE naming ISpRecoGrammar::LoadDictation and the raw
    hr - NOT the bare `OSError: [WinError -2147200966]` that ctypes'
    HRESULT restype used to throw before any code could name the call.
    Unpinned: the ear still works, because the engine is skipped by name.
    """
    names = [t["name"] for t in S.recognizer_tokens()]
    if "MS-1033-110-WINMO-DNN" not in names:
        return {"skipped": "OneCore DNN not installed on this box",
                "installed": names}
    pcm, rate = S.wav_to_pcm(_sapi_wav("status"))
    pinned = None
    try:
        S.SapiTranscriber(prefer="MS-1033-110-WINMO-DNN").recognize_pcm(pcm, rate)
    except CvmDtError as e:
        pinned = str(e)
    assert pinned and "LoadDictation" in pinned, pinned
    assert "0X8004503A" in pinned.upper(), pinned
    unpinned = S.SapiTranscriber().recognize_pcm(pcm, rate)
    assert unpinned["transcript"].strip(), unpinned
    assert unpinned["recognizer"] != "MS-1033-110-WINMO-DNN", unpinned
    return {"pinned_refusal": pinned[:120],
            "unpinned_recognizer": unpinned["recognizer"],
            "unpinned_heard": unpinned["transcript"]}


def test_unknown_engine_name_refuses_instead_of_falling_through():
    try:
        S.SapiTranscriber(prefer="NO-SUCH-ENGINE").recognize_pcm(b"\x01\x02" * 100)
    except CvmDtError as e:
        assert "not installed" in str(e), e
        return {"detail": str(e)[:80]}
    raise AssertionError("unknown engine name did not refuse")


def test_hrcall_returns_hr_instead_of_auto_raising():
    """The fix that made the DNN refusal legible. A failing hr must be OURS.

    Behavioural, not a source grep: a SUCCEEDING call returns a plain int
    (ctypes' HRESULT restype returns None and raises on failure), and a
    FAILING one raises this module's typed refusal naming the call and hr.
    """
    tok, hr = S._create(S.CLSID_SP_OBJECT_TOKEN, S.IID_ISP_OBJECT_TOKEN)
    assert tok is not None, hr
    good = S._hrcall(tok, S.T_SET_ID, "ISpObjectToken::SetId",
                     (ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_int),
                     None, S.pick_token()["id"], 0)
    assert isinstance(good, int) and good >= 0, good
    try:
        S._hrcall(tok, S.T_SET_ID, "ISpObjectToken::SetId",
                  (ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_int),
                  None, r"HKEY_LOCAL_MACHINE\SOFTWARE\NoSuch\Token", 0)
    except CvmDtError as e:
        assert e.kind == RefusalKind.STT_NONE
        assert "SetId" in str(e) and "hr=0x" in str(e), e
        return {"named_refusal": str(e)[:90]}
    finally:
        S._release(tok)
    raise AssertionError("a bad token id did not refuse")


# --------------------------------------------------------------------------
# 5. probes are honest, and the module stays in its lane
# --------------------------------------------------------------------------
def test_probe_reports_real_tokens_with_bindable_ids():
    tokens = S.recognizer_tokens()
    assert tokens, "no recognizer installed"
    for t in tokens:
        assert t["id"].startswith("HKEY_LOCAL_MACHINE\\"), t
        assert t["id"].endswith(t["name"]), t
    pick = S.pick_token()
    assert pick is not None and pick["name"] == S.ENGINE_ORDER[0], pick
    return {"tokens": [t["name"] for t in tokens], "picked": pick["name"],
            "descriptions": [t.get("description") for t in tokens]}


def test_engine_order_puts_the_dictation_capable_engine_first():
    """Ranking the newer engine on its version number broke every utterance."""
    assert S.ENGINE_ORDER[0] == "MS-1033-80-DESK", S.ENGINE_ORDER
    assert "MS-1033-110-WINMO-DNN" in S.ENGINE_ORDER, S.ENGINE_ORDER
    return {"order": list(S.ENGINE_ORDER)}


def test_wav_round_trip_is_lossless():
    pcm = bytes(range(256)) * 40
    back, rate = S.wav_to_pcm(S.pcm_to_wav_bytes(pcm, 16000))
    assert back == pcm and rate == 16000
    return {"bytes": len(pcm), "rate": rate}


def test_module_stays_in_its_lane():
    """No Core kernel/ledger/sched/service import; no drive literal; no server."""
    for bad in ("cosmos_kernel", "cosmos_ledger", "cosmos_sched",
                "cosmos_service", "cosmos_dispatch", "HTTPServer"):
        assert bad not in SRC, bad
    assert DRIVE_LIT.search(SRC) is None, DRIVE_LIT.search(SRC)
    assert "pull.json" not in SRC and "audio.json" not in SRC
    assert S.WIRE == "cvm-dt-stt/1"
    return {"wire": S.WIRE, "bytes": len(SRC)}


def test_temp_wav_is_removed():
    """recognize_pcm writes a temp WAV; it must not leave one behind."""
    before = set(Path(tempfile.gettempdir()).glob("cvm_dt_ear_*.wav"))
    pcm, rate = S.wav_to_pcm(_sapi_wav("status"))
    S.SapiTranscriber().recognize_pcm(pcm, rate)
    after = set(Path(tempfile.gettempdir()).glob("cvm_dt_ear_*.wav"))
    assert after <= before, sorted(after - before)
    return {"leaked": 0, "pool": len(after)}


def main() -> int:
    ok = fail = 0
    live: dict = {}

    def check(label, fn):
        nonlocal ok, fail
        try:
            live[label] = fn()
            print("PASS  %s" % label)
            ok += 1
        except Exception as e:                                    # noqa: BLE001
            print("FAIL  %s: %s: %s" % (label, type(e).__name__, e))
            fail += 1

    check("every IID + vtable width matches the box's own sapi.dll typelib",
          test_every_iid_and_vtable_matches_the_boxs_typelib)
    check("SPFEI sets the two reserved bits (else SetInterest is silent)",
          test_spfei_sets_the_two_reserved_bits)
    check("REGRESSION: pre-ear code binds NO ear on this box; new one hears",
          test_pre_ear_code_has_no_ear_on_this_box)
    check("cvm_dt_voice.default_transcriber now binds an ear, not None",
          test_voice_client_binds_the_ear_not_none)
    check("mouth -> ear round trip on this box (the live value)",
          test_mouth_to_ear_round_trip)
    check("silence is STT_NONE, never a fabricated word",
          test_empty_audio_is_stt_none_not_a_fabricated_word)
    check("no audio at all refuses before touching COM",
          test_no_audio_at_all_refuses_before_com)
    check("dictationless engine refuses BY NAME and is skipped",
          test_dictationless_engine_refuses_by_name_and_is_skipped)
    check("unknown engine name refuses instead of falling through",
          test_unknown_engine_name_refuses_instead_of_falling_through)
    check("_hrcall raises OUR named refusal, not ctypes' bare OSError",
          test_hrcall_returns_hr_instead_of_auto_raising)
    check("probe reports real tokens with SetId-bindable ids",
          test_probe_reports_real_tokens_with_bindable_ids)
    check("ENGINE_ORDER puts the dictation-capable engine first",
          test_engine_order_puts_the_dictation_capable_engine_first)
    check("PCM <-> WAV round trip is lossless",
          test_wav_round_trip_is_lossless)
    check("module stays in its lane (no Core, no drive literal, no server)",
          test_module_stays_in_its_lane)
    check("recognize_pcm leaves no temp WAV behind", test_temp_wav_is_removed)

    print("live_value: %s" % json.dumps(live, sort_keys=True, default=str))
    print("result: %s  %d/%d" % ("ok" if not fail else "FAIL", ok, ok + fail))
    return 0 if not fail else 1


if __name__ == "__main__":
    raise SystemExit(main())
