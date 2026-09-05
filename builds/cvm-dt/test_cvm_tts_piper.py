#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gate for `cvm_tts_piper.py` — desktop mouth, same voice id as the APK.

What this suite protects:

* provisioning must arm nothing: a clean subprocess still fails to import
  `piper` (asked of a SUBPROCESS under `-I`, because this process may already
  have opted in);
* the Piper import root is a THIRD tree, not the VOSK or whisper one;
* voice files stay inside `builds/cvm-dt/`;
* `ready()` is a file check, not an import;
* an empty dir is `PIPER_NONE`, never a silent SAPI call from this module;
* `arm_line()["ran"]` is False;
* the voice id equals the APK's `en_US-amy-low.onnx` stem;
* when provisioned, `synthesize_wav` returns a RIFF WAV.

    py -3.14 builds\\cvm-dt\\test_cvm_tts_piper.py
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))

import cvm_tts_piper as P  # noqa: E402
import cvm_stt_vosk as V  # noqa: E402
import cvm_stt_whisper as W  # noqa: E402

RESULTS: list[tuple[str, bool, str]] = []
LIVE: dict = {}


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:                                        # noqa: BLE001
        RESULTS.append((label, False, "%s: %s" % (type(e).__name__, e)))


def _unarmed_in_a_clean_process() -> bool:
    code = ("import json, importlib.util as u\n"
            "print(json.dumps({'piper': u.find_spec('piper') is not None}))\n")
    r = subprocess.run([sys.executable, "-I", "-c", code],
                       capture_output=True, text=True, timeout=120)
    got = json.loads(r.stdout.strip().splitlines()[-1])
    LIVE["clean_process_sees"] = got
    return got["piper"] is False


def _site_is_a_third_root() -> bool:
    LIVE["roots"] = {"piper": str(P.SITE), "vosk": str(V.SITE),
                     "whisper": str(W.SITE)}
    a, b, c = P.SITE.resolve(), V.SITE.resolve(), W.SITE.resolve()
    return a != b and a != c and b != c


def _voice_files_stay_inside_the_fence() -> bool:
    fence = _HERE.resolve()
    LIVE["voice_dir"] = str(P.VOICE_DIR)
    return (P.VOICE_DIR.resolve().is_relative_to(fence)
            and P.SITE.resolve().is_relative_to(fence))


def _ready_is_a_file_check() -> bool:
    """ready() must not import piper — an empty dir is just False."""
    d = Path(tempfile.mkdtemp(prefix="cvm-piper-empty-"))
    LIVE["empty_ready"] = P.ready(d)
    return LIVE["empty_ready"] is False


def _empty_dir_is_typed_none() -> bool:
    d = Path(tempfile.mkdtemp(prefix="cvm-piper-none-"))
    try:
        P.synthesize_wav("hello", onnx_path=d / P.ONNX_NAME)
    except P.PiperError as e:
        LIVE["empty_kind"] = e.kind
        return e.kind == "PIPER_NONE"
    LIVE["empty_kind"] = "no-raise"
    return False


def _arm_line_does_not_run() -> bool:
    line = P.arm_line()
    LIVE["arm"] = {"ran": line.get("ran"), "voice_id": line.get("voice_id")}
    return line.get("ran") is False and line.get("voice_id") == P.VOICE_ID


def _voice_id_matches_the_apk() -> bool:
    LIVE["phone"] = P.PHONE_VOICE
    return (P.VOICE_ID + ".onnx" == P.PHONE_VOICE["apk_model_file"]
            and P.PHONE_VOICE["apk_model_dir"].endswith(P.VOICE_ID + "-int8"))


def _empty_text_is_typed() -> bool:
    try:
        P.synthesize_wav("   ")
    except P.PiperError as e:
        LIVE["empty_text_kind"] = e.kind
        return e.kind == "EMPTY_TEXT"
    return False


def _wav_info_rejects_non_riff() -> bool:
    try:
        P.wav_info(b"not a wav")
    except P.PiperError as e:
        LIVE["not_wav_kind"] = e.kind
        return e.kind == "NOT_WAV"
    return False


def _provisioned_synth_is_riff() -> bool:
    if not P.ready():
        LIVE["synth"] = "SKIP_NOT_PROVISIONED"
        return True
    rec = P.say("status")
    LIVE["synth"] = rec
    wav = rec["wav"]
    return (rec["ok"] is True
            and rec["engine"] == "piper"
            and rec["same_voice_id"] is True
            and wav["bytes"] > 44
            and wav["rate"] > 0
            and wav["channels"] == 1)


def _pins_recorded_when_files_exist() -> bool:
    if not P.ready():
        return True
    got = P.provisioned()
    LIVE["pins"] = {"onnx": got.get("onnx_sha256"),
                    "json": got.get("json_sha256"),
                    "onnx_bytes": got.get("onnx_bytes")}
    return bool(got.get("onnx_sha256")) and bool(got.get("json_sha256"))


def _cvm_dt_mouth_names_piper_and_keeps_sapi_floor() -> bool:
    src = (_HERE / "cvm_dt.py").read_text(encoding="utf-8")
    low = src.lower()
    LIVE["cvm_dt_mentions"] = {
        "piper": "piper" in low,
        "sapi": "SAPI.SpVoice" in src,
        "sapi_wav": "_sapi_wav" in src,
    }
    return ("piper" in low and "SAPI.SpVoice" in src and "_sapi_wav" in src)


def main() -> int:
    check("clean -I process cannot import piper (provisioning arms nothing)",
          _unarmed_in_a_clean_process)
    check("piper_site is a third root, not vosk or whisper",
          _site_is_a_third_root)
    check("voice files stay inside builds/cvm-dt/",
          _voice_files_stay_inside_the_fence)
    check("ready() on an empty dir is False (file check, not import)",
          _ready_is_a_file_check)
    check("synthesize against an empty dir is PIPER_NONE",
          _empty_dir_is_typed_none)
    check("arm_line ran=false",
          _arm_line_does_not_run)
    check("voice id equals the APK en_US-amy-low.onnx stem",
          _voice_id_matches_the_apk)
    check("empty text is EMPTY_TEXT, not a WAV",
          _empty_text_is_typed)
    check("wav_info refuses a non-RIFF buffer",
          _wav_info_rejects_non_riff)
    check("when provisioned, say() returns a mono RIFF WAV",
          _provisioned_synth_is_riff)
    check("onnx+json sha256 recorded when files exist",
          _pins_recorded_when_files_exist)
    check("cvm_dt.py names piper and keeps the SAPI floor",
          _cvm_dt_mouth_names_piper_and_keeps_sapi_floor)
    failed = [(l, err) for l, ok, err in RESULTS if not ok]
    for label, ok, err in RESULTS:
        print("%s  %s%s" % ("PASS" if ok else "FAIL", label,
                            ("  " + err) if err else ""))
    print("result: %d/%d" % (len(RESULTS) - len(failed), len(RESULTS)))
    print("live: %s" % json.dumps(LIVE, default=str)[:800])
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
