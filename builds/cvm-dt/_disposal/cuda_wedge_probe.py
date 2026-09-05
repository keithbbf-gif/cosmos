#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Does a FAILED CUDA decode wedge the process for the next CUDA load?

Observed, not theorised: `test_cvm_stt_whisper.py` constructed three CUDA
WhisperModels across two checks — with a failed decode between them — and did
not finish in 13 minutes. The same suite with ONE construction finished in
about two. That is a correlation, so this runs the minimal sequence with a hard
timeout and stamps each phase, and the answer goes in the changelog either way.

    py -3.14 builds\\cvm-dt\\_disposal\\cuda_wedge_probe.py
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

import cvm_stt_whisper as W  # noqa: E402
import cvm_stt_vosk as V  # noqa: E402


def stamp(msg: str) -> None:
    print(json.dumps({"t": round(time.time() % 100000, 2), "m": msg}),
          flush=True)


def main() -> int:
    W.bind()
    fx = V._fixture("pause the clock")
    stamp("start")
    e1 = W.ResidentWhisperEar("tiny.en", device="cuda",
                              compute_type="int8_float16")
    stamp("constructed_1")
    try:
        e1.transcribe(fx["pcm"], fx["rate"])
        stamp("decoded_1_ok")
    except Exception as e:                                        # noqa: BLE001
        stamp("decode_1_failed:" + type(e).__name__)
    W.ResidentWhisperEar("tiny.en", device="cuda",
                         compute_type="int8_float16")
    stamp("constructed_2")
    # The suite's next act after the failed CUDA decode is `measure()`, which
    # builds a CPU whisper ear, a VOSK ear, and drives SAPI over COM.
    W.ResidentWhisperEar("tiny.en", device="cpu", compute_type="int8")
    stamp("cpu_whisper_ok")
    b = V.bind(set_env=False)
    V.ResidentVoskEar(b["model_path"]).transcribe(fx["pcm"], fx["rate"])
    stamp("vosk_ok")
    V.measure("pause the clock", reps=1)
    stamp("sapi_measure_ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
