#!/usr/bin/env python3
"""A/B the two installed recognizer engines on IDENTICAL audio.

Measured question, not assumed: is the OneCore Embedded DNN v11.1 engine
reachable through the desktop SpInprocRecognizer, and is it more accurate
than MS-1033-80-DESK? The winner sets `cvm_dt_stt.ENGINE_ORDER`.

Both arms run inside ONE process against byte-identical PCM (asserted), so
the comparison is of engines, not of machine load.

    py -3.14 builds/cvm-dt/_disposal/sapi_engine_ab.py
"""
from __future__ import annotations

import hashlib
import json
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import cvm_dt_stt as S  # noqa: E402
from cvm_dt import _sapi_wav  # noqa: E402

DESK, DNN = "MS-1033-80-DESK", "MS-1033-110-WINMO-DNN"
PHRASES = [
    "open the status report", "what is the queue depth", "pause the mesh",
    "status", "show me the ledger", "resume all carried over tasks",
    "what is the spend today", "stop", "read the last three events",
    "how many jobs are running",
]


def recall(phrase: str, heard: str) -> float:
    w = set(phrase.lower().split())
    h = set(str(heard or "").lower().replace(".", " ").replace(",", " ").split())
    return round(len(w & h) / max(1, len(w)), 3)


def main() -> int:
    rows, arms = [], {DESK: [], DNN: []}
    for ph in PHRASES:
        pcm, rate = S.wav_to_pcm(_sapi_wav(ph))
        sha = hashlib.sha256(pcm).hexdigest()[:16]
        row = {"phrase": ph, "pcm_sha16": sha, "pcm_bytes": len(pcm)}
        for eng in (DESK, DNN):
            try:
                got = S.SapiTranscriber(prefer=eng).recognize_pcm(pcm, rate)
                r = recall(ph, got["transcript"])
                row[eng] = {"heard": got["transcript"], "recall": r,
                            "ear_ms": got["ear_ms"],
                            "bound": got.get("recognizer")}
                arms[eng].append((r, got["ear_ms"]))
            except Exception as e:  # noqa: BLE001 - report, never swallow
                row[eng] = {"error": "%s: %s" % (type(e).__name__, e)}
        rows.append(row)

    out = {"rows": rows, "summary": {}}
    for eng, got in arms.items():
        if got:
            out["summary"][eng] = {
                "n": len(got),
                "mean_recall": round(statistics.mean(r for r, _ in got), 3),
                "exact": sum(1 for r, _ in got if r == 1.0),
                "median_ear_ms": round(statistics.median(m for _, m in got), 1),
            }
    a, b = out["summary"].get(DESK), out["summary"].get(DNN)
    if a and b:
        out["verdict"] = (
            "DNN" if b["mean_recall"] > a["mean_recall"] else
            "DESK" if a["mean_recall"] > b["mean_recall"] else "TIE")
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
