#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""F-21 — the held recognizer, proved against the code it replaced.

`VoskTranscriber` held the MODEL across turns and dropped the RECOGNIZER in
`finish()`. That looks like caching and is not: the first `AcceptWaveform` on a
freshly built `KaldiRecognizer` costs an order of magnitude more than one on a
`Reset()` recognizer, and a recognizer dropped every turn is a fresh one every
turn. The engine was carrying a per-utterance rebuild that nothing named.

This suite does not compare the new code against a description of the old one.
It loads the PRE-EDIT file from
`_delme/predispose_cvm_dt_voice_<ts>/cvm_dt_voice.py`, instantiates its real
`VoskTranscriber` against the same model and the same PCM, and runs the two
INTERLEAVED in one process — because this box carries other agents and two
sequential passes would compare machine load as much as code.

The gate: the old class must FAIL the reuse check the new one passes. A
regression test that has never failed against the old code is a claim.

    py -3.14 builds\\cvm-dt\\test_cvm_vosk_reuse.py
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import statistics
import sys
import time
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
sys.path.insert(0, str(_HERE.parents[1] / "cosmos"))

import cvm_stt_vosk as V  # noqa: E402
import cvm_dt_voice as NEW  # noqa: E402

RESULTS: list[tuple[str, bool, str]] = []
LIVE: dict = {}
PHRASE = "what is the queue depth"
TURNS = 3


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:                                            # noqa: BLE001
        RESULTS.append((label, False, "%s: %s" % (type(e).__name__, e)))


def staged_old() -> Path:
    """The most recent pre-edit copy. Nothing was deleted to make this test."""
    cands = sorted((_HERE / "_delme").glob(
        "predispose_cvm_dt_voice_*/cvm_dt_voice.py"))
    if not cands:
        raise FileNotFoundError(
            "no staged pre-edit cvm_dt_voice.py under _delme/ - the "
            "regression cannot be proved without the code it replaced")
    return cands[-1]


def load_old():
    path = staged_old()
    spec = importlib.util.spec_from_file_location("cvm_dt_voice_preedit", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["cvm_dt_voice_preedit"] = mod
    spec.loader.exec_module(mod)
    return mod, path


def turns(cls, model_path: str, pcm: bytes, rate: int, n: int) -> list[float]:
    """n turns on ONE transcriber. Turn 1 pays the model load and is dropped."""
    t = cls(model_path)
    out: list[float] = []
    for _ in range(n):
        t.accept(pcm, rate)
        out.append(float(t.finish()["ear_ms"]))
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--turns", type=int, default=TURNS)
    a = ap.parse_args(argv)

    b = V.bind(set_env=False)
    model_path = b["model_path"]
    fx = V._fixture(PHRASE)
    pcm, rate = fx["pcm"], fx["rate"]

    old_mod, old_path = load_old()
    LIVE["staged_pre_edit"] = str(old_path)
    check("pre_edit_copy_is_staged_not_deleted",
          lambda: Path(old_path).is_file())
    check("pre_edit_copy_drops_the_recognizer_in_finish",
          lambda: "rec, self._rec = self._rec, None"
          in Path(old_path).read_text(encoding="utf-8"))

    # Warm both classes once so neither pays the model load inside a timed
    # turn, then interleave.
    old_t = old_mod.VoskTranscriber(model_path)
    new_t = NEW.VoskTranscriber(model_path)
    for t in (old_t, new_t):
        t.accept(pcm, rate)
        t.finish()

    old_ms: list[float] = []
    new_ms: list[float] = []
    reused: list[bool] = []
    for _ in range(max(2, int(a.turns))):
        old_t.accept(pcm, rate)
        old_ms.append(float(old_t.finish()["ear_ms"]))
        new_t.accept(pcm, rate)
        r = new_t.finish()
        new_ms.append(float(r["ear_ms"]))
        reused.append(bool(r.get("recognizer_reused")))

    med_old = statistics.median(old_ms)
    med_new = statistics.median(new_ms)
    LIVE["ab"] = {
        "pre_edit_ms": round(med_old, 3), "post_edit_ms": round(med_new, 3),
        "speedup": round(med_old / max(med_new, 1e-9), 2),
        "saved_ms_per_utterance": round(med_old - med_new, 3),
        "turns": len(old_ms), "interleaved": True,
        "fixture_s": fx["seconds"], "model": V.MODEL_NAME,
        "pre_edit_samples": [round(x, 3) for x in old_ms],
        "post_edit_samples": [round(x, 3) for x in new_ms],
    }

    check("new_code_reports_the_recognizer_was_reused",
          lambda: all(reused))
    check("OLD_CODE_FAILS_THE_REUSE_CHECK", _old_fails_reuse)
    check("new_code_is_faster_on_the_same_pcm", lambda: med_new < med_old)
    check("the_gap_is_large_not_noise",
          lambda: med_old / max(med_new, 1e-9) >= 3.0)
    check("both_paths_heard_the_same_words", _same_words)
    check("a_rate_change_still_rebuilds_the_recognizer", _rate_change_rebuilds)
    check("finish_without_accept_still_refuses", _finish_without_accept)
    check("two_finishes_in_a_row_still_refuse", _double_finish)

    passed = sum(1 for _, ok, _ in RESULTS if ok)
    for label, ok, err in RESULTS:
        print("%s %s%s" % ("PASS" if ok else "FAIL", label,
                           (" - " + err) if err else ""))
    ok_all = passed == len(RESULTS)
    ab = LIVE["ab"]
    rec = {
        "ok": ok_all, "wire": "cvm-dt-f21-vosk-reuse/1",
        "suite": "test_cvm_vosk_reuse.py",
        "passed": passed, "total": len(RESULTS),
        "gated_at_epoch": time.time(), "python": sys.version.split()[0],
        "live_value": LIVE,
        "emitted": "f21-reuse:%s:pre-edit %s ms -> post-edit %s ms per "
                   "utterance (%sx, %s ms saved) on a %s s fixture, "
                   "interleaved; pre-edit copy %s" % (
                       V.MODEL_NAME, ab["pre_edit_ms"], ab["post_edit_ms"],
                       ab["speedup"], ab["saved_ms_per_utterance"],
                       ab["fixture_s"], Path(old_path).name),
        "results": [{"name": n, "verdict": "PASS" if o else "FAIL",
                     "detail": e} for n, o, e in RESULTS],
    }
    out = _HERE / "F21_VOSK_REUSE.json"
    out.write_text(json.dumps(rec, indent=1, default=str), encoding="utf-8")
    print(json.dumps({"ok": ok_all, "passed": passed, "total": len(RESULTS),
                      "emitted": rec["emitted"], "proof_path": str(out)},
                     indent=1))
    return 0 if ok_all else 1


# ---------------------------------------------------------------------------
# the individual claims
# ---------------------------------------------------------------------------
def _old_fails_reuse():
    """The decisive one: run the NEW suite's reuse check against the OLD class."""
    old_mod, _ = load_old()
    b = V.bind(set_env=False)
    fx = V._fixture(PHRASE)
    t = old_mod.VoskTranscriber(b["model_path"])
    t.accept(fx["pcm"], fx["rate"])
    first = t.finish()
    t.accept(fx["pcm"], fx["rate"])
    second = t.finish()
    LIVE["old_code_reuse_probe"] = {
        "first_reports_reused": first.get("recognizer_reused"),
        "second_reports_reused": second.get("recognizer_reused"),
        "why": "the pre-edit finish() sets self._rec = None, so no turn can "
               "report a reused recognizer",
    }
    return not second.get("recognizer_reused")


def _same_words():
    old_mod, _ = load_old()
    b = V.bind(set_env=False)
    fx = V._fixture(PHRASE)
    o = old_mod.VoskTranscriber(b["model_path"])
    n = NEW.VoskTranscriber(b["model_path"])
    o.accept(fx["pcm"], fx["rate"])
    n.accept(fx["pcm"], fx["rate"])
    a, c = o.finish(), n.finish()
    # second turn too: a reused recognizer must not leak the previous turn
    n.accept(fx["pcm"], fx["rate"])
    d = n.finish()
    LIVE["transcripts"] = {"pre_edit": a["transcript"],
                           "post_edit_turn1": c["transcript"],
                           "post_edit_turn2": d["transcript"]}
    return a["transcript"] == c["transcript"] == d["transcript"]


def _rate_change_rebuilds():
    b = V.bind(set_env=False)
    fx = V._fixture(PHRASE)
    t = NEW.VoskTranscriber(b["model_path"])
    t.accept(fx["pcm"], fx["rate"])
    t.finish()
    rec_before = t._rec
    # Empty PCM: `accept` rebuilds for the new rate without decoding anything.
    # Feeding the 16 kHz fixture under an 8 kHz label would not test the
    # rebuild - vosk rejects the WAVEFORM first ("Sampling frequency mismatch,
    # expected 16000, got 8000"), which is the model's rate, not the
    # recognizer's construction.
    t.accept(b"", 8000)
    changed = t._rec is not rec_before and t._rate == 8000
    LIVE["rate_change"] = {"rebuilt": changed, "rate_now": t._rate}
    try:
        t.finish()                      # nothing decoded -> honest refusal
    except NEW.CvmDtError:
        pass
    return changed


def _finish_without_accept():
    b = V.bind(set_env=False)
    t = NEW.VoskTranscriber(b["model_path"])
    try:
        t.finish()
    except NEW.CvmDtError as e:
        return str(e.kind).endswith("STT_NONE") or "STT_NONE" in str(e.kind)
    return False


def _double_finish():
    b = V.bind(set_env=False)
    fx = V._fixture(PHRASE)
    t = NEW.VoskTranscriber(b["model_path"])
    t.accept(fx["pcm"], fx["rate"])
    t.finish()
    try:
        t.finish()
    except NEW.CvmDtError:
        return True
    return False


if __name__ == "__main__":
    raise SystemExit(main())
