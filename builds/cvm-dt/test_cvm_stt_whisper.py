#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gate for `cvm_stt_whisper.py` — the third ear, and the claims made about it.

The finding this suite exists to protect is a REVERSAL, so it is exactly the
kind that deserves suspicion. On one phrase, SAPI scored 1.00 and VOSK 0.80,
and `CVM_BACKLOG` B8 refuses to arm the local model ear because of it. On ten
phrases the ordering inverts: SAPI 0.88, VOSK 0.96. A number that flips when
the sample grows from 1 to 10 was never a measurement of the engines.

So the checks below are mostly about the MEASUREMENT, not the models:

* the punctuation-blind metric is proved to differ from the shipped one on the
  exact string that caused the trouble, and to AGREE with it where no
  punctuation is involved — a normaliser that changed every score would just be
  a different bias;
* the harness must refuse a single-phrase verdict silently becoming a ten-
  phrase one — `phrases` is carried in every row;
* provisioning must arm nothing: a clean subprocess must still fail to import
  `faster_whisper`, checked the way A5 checks it (a SUBPROCESS, because this
  process has already opted in);
* the CUDA claim must be a LOAD, not a capability query.

    py -3.14 builds\\cvm-dt\\test_cvm_stt_whisper.py
    py -3.14 builds\\cvm-dt\\test_cvm_stt_whisper.py --fast   # skip decoding
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))

import cvm_stt_whisper as W  # noqa: E402
import cvm_stt_vosk as V  # noqa: E402

RESULTS: list[tuple[str, bool, str]] = []
LIVE: dict = {}


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:                                        # noqa: BLE001
        RESULTS.append((label, False, "%s: %s" % (type(e).__name__, e)))


# --------------------------------------------------------------------------

def _unarmed_in_a_clean_process() -> bool:
    """The provisioned root must not leak. Asked of a SUBPROCESS, not of us."""
    code = ("import json, importlib.util as u\n"
            "print(json.dumps({'fw': u.find_spec('faster_whisper') is not None,"
            " 'ct2': u.find_spec('ctranslate2') is not None}))\n")
    r = subprocess.run([sys.executable, "-I", "-c", code],
                       capture_output=True, text=True, timeout=120)
    got = json.loads(r.stdout.strip().splitlines()[-1])
    LIVE["clean_process_sees"] = got
    return got["fw"] is False and got["ct2"] is False


def _site_is_separate_from_the_vosk_one() -> bool:
    LIVE["roots"] = {"whisper": str(W.SITE), "vosk": str(V.SITE)}
    return W.SITE.resolve() != V.SITE.resolve()


def _weights_stay_inside_the_fence() -> bool:
    """Model weights must land under builds/cvm-dt/, not in the user profile."""
    fence = _HERE.resolve()
    LIVE["hf_cache"] = str(W.HF_CACHE)
    return (W.HF_CACHE.resolve().is_relative_to(fence)
            and str(W.SITE.resolve()).startswith(str(fence)))


def _metric_differs_where_it_should() -> bool:
    said = "what is the queue depth"
    punct = "What is the Q-depth?"
    plain = "what is the queue depth"
    LIVE["metric"] = {
        "punctuated": [V.recall(said, punct), W.norm_recall(said, punct)],
        "clean": [V.recall(said, plain), W.norm_recall(said, plain)],
    }
    # differs on the punctuated string...
    return (W.norm_recall(said, punct) > V.recall(said, punct)
            # ...and agrees where punctuation is not the issue
            and W.norm_recall(said, plain) == V.recall(said, plain) == 1.0
            # ...and does NOT invent a match that is not there
            and W.norm_recall(said, "totally different words") == 0.0)


def _metric_does_not_flatter_everyone() -> bool:
    """A normaliser that raises every score is not a fix, it is a thumb."""
    said = "pause the clock"
    return W.norm_recall(said, "Paz o'clock") < 1.0


def _report_pins_what_pip_installed() -> bool:
    p = W.provisioned()
    LIVE["provisioned"] = {k: v for k, v in p.items() if k != "packages"}
    if not p.get("report"):
        return False
    rep = json.loads(W.REPORT.read_text(encoding="utf-8"))
    names = {d["name"].lower().replace("_", "-") for d in rep["installed"]}
    hashed = [d for d in rep["installed"] if d.get("sha256")]
    LIVE["pins"] = {"packages": len(rep["installed"]),
                    "with_sha256": len(hashed)}
    return ("faster-whisper" in names and "ctranslate2" in names
            and rep.get("only_binary") is True
            and len(hashed) == len(rep["installed"]))


def _artifact_carries_the_digests() -> bool:
    """`vendor/` is git-ignored, so the ARTIFACT is the only committed record.

    A list of package names would not survive a swapped wheel; the digest is
    what makes the provisioning auditable from a fresh clone.
    """
    p = W.provisioned()
    LIVE["pinned_in_artifact"] = {
        "count": p.get("package_count"), "unpinned": p.get("unpinned"),
        "only_binary": p.get("only_binary")}
    pkgs = p.get("packages") or []
    return (bool(pkgs) and p.get("unpinned") == []
            and all(isinstance(d, dict) and d.get("sha256") for d in pkgs))


_CUDA_ONCE: dict = {}


def _cuda_facts() -> dict:
    """Probe the GPU ONCE. Two checks read it; each probe costs a model load."""
    if not _CUDA_ONCE:
        W.bind()
        try:
            W.ResidentWhisperEar("tiny.en", device="cuda",
                                 compute_type="int8_float16")
            constructed = True
        except Exception as e:                                    # noqa: BLE001
            constructed = False
            LIVE["cuda_construct_error"] = str(e)[:200]
        _CUDA_ONCE.update({"devices": W.devices(),
                           "attempt": W.cuda_attempt(),
                           "constructed": constructed})
    return _CUDA_ONCE


def _cuda_claim_is_a_load_not_a_query() -> bool:
    f = _cuda_facts()
    d, a = f["devices"], f["attempt"]
    LIVE["cuda"] = {"device_count": d.get("cuda_device_count"), "attempt": a}
    if a["ok"]:
        # A success must have DECODED, not merely constructed.
        return a.get("decode_ms") is not None and a.get("failed_at") is None
    # A refusal must NAME what is missing and WHERE it failed.
    return bool(a.get("detail")) and a.get("failed_at") in ("construct",
                                                            "decode")


def _construction_alone_would_have_lied() -> bool:
    """The probe must be strictly stronger than the one it replaced.

    Construction succeeding while decode fails is exactly the state this box
    is in, and a construction-only probe reported a working GPU here. If that
    ever stops being true (the CUDA libraries arrive), this check retires
    itself rather than failing: both phases succeed and there is nothing left
    to lie about.
    """
    f = _cuda_facts()
    constructed, a = f["constructed"], f["attempt"]
    LIVE["construct_vs_decode"] = {"constructed": constructed,
                                   "decoded": a["ok"],
                                   "failed_at": a.get("failed_at")}
    if a["ok"]:
        return constructed              # both work: nothing to catch
    # decode fails -> the weaker probe would have said yes; the strong one says
    # no, and names the phase.
    return constructed and a.get("failed_at") == "decode"


def _rows_carry_the_sample_size(m) -> bool:
    return all(r.get("phrases") == len(m["phrases"]) and r.get("n") >= 1
               for r in m["rows"])


def _ear_surface_matches_the_others() -> bool:
    for name in ("accept", "finish", "transcribe"):
        if not callable(getattr(W.ResidentWhisperEar, name, None)):
            return False
        if not callable(getattr(V.ResidentVoskEar, name, None)):
            return False
    return True


def _finish_without_accept_refuses() -> bool:
    W.bind()
    ear = W.ResidentWhisperEar("tiny.en")
    try:
        ear.finish()
    except W.WhisperError as e:
        return e.kind == "STT_NONE"
    return False


def _wrong_rate_refuses() -> bool:
    W.bind()
    ear = W.ResidentWhisperEar("tiny.en")
    try:
        ear.transcribe(b"\x00\x00" * 100, 8000)
    except W.WhisperError as e:
        return e.kind == "RATE"
    return False


def _no_phrases_refuses() -> bool:
    try:
        W.measure(("  ", ""), models=())
    except W.WhisperError as e:
        return e.kind == "NO_PHRASES"
    return False


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fast", action="store_true",
                    help="skip the decoding checks (no model is loaded)")
    a = ap.parse_args(argv)

    check("provisioning_ARMS_NOTHING_in_a_clean_process",
          _unarmed_in_a_clean_process)
    check("the_whisper_root_is_separate_from_the_vosk_root",
          _site_is_separate_from_the_vosk_one)
    check("wheels_and_weights_both_stay_inside_the_fence",
          _weights_stay_inside_the_fence)
    check("pip_report_pins_every_package_with_a_sha256",
          _report_pins_what_pip_installed)
    check("the_committed_artifact_carries_those_digests",
          _artifact_carries_the_digests)
    check("normalised_recall_differs_on_punctuation_and_agrees_elsewhere",
          _metric_differs_where_it_should)
    check("normalised_recall_does_NOT_flatter_a_real_miss",
          _metric_does_not_flatter_everyone)
    check("the_whisper_ear_has_the_same_surface_as_the_vosk_ear",
          _ear_surface_matches_the_others)
    check("a_measure_with_no_phrases_REFUSES", _no_phrases_refuses)

    if not a.fast:
        check("finish_without_accept_REFUSES", _finish_without_accept_refuses)
        check("a_wrong_sample_rate_REFUSES", _wrong_rate_refuses)
        check("the_cuda_claim_is_a_DECODE_not_a_capability_query",
              _cuda_claim_is_a_load_not_a_query)
        check("a_CONSTRUCTION_only_probe_would_have_reported_a_working_gpu",
              _construction_alone_would_have_lied)

        m = W.measure(("what is the queue depth", "pause the clock"),
                      models=("tiny.en",), reps=1)
        LIVE["two_phrase_measure"] = {
            "rows": [{k: r[k] for k in ("engine", "per_utterance_ms",
                                        "word_recall",
                                        "word_recall_normalised", "phrases")}
                     for r in m["rows"]],
            "dominates": m["dominates"]}
        check("every_row_carries_the_sample_size_it_was_scored_on",
              lambda: _rows_carry_the_sample_size(m))
        check("all_three_engines_are_in_the_comparison",
              lambda: {r["engine"].split(":")[0] for r in m["rows"]}
              == {"whisper", "vosk", "sapi"})
        check("every_engine_heard_the_SAME_phrases",
              lambda: all(sorted(r["heard"]) == sorted(m["phrases"])
                          for r in m["rows"]))
        check("the_fixture_bias_against_the_finding_is_recorded",
              lambda: "synthesised BY SAPI" in m["fixture_bias"])
        check("dominance_is_reported_as_a_pair_not_a_boolean",
              lambda: isinstance(m["dominates"], list)
              and all({"faster_and_no_less_accurate", "than", "ms", "recall"}
                      <= set(d) for d in m["dominates"]))

    passed = sum(1 for _, ok, _ in RESULTS if ok)
    for label, ok, err in RESULTS:
        print("%s %s%s" % ("PASS" if ok else "FAIL", label,
                           (" - " + err) if err else ""))
    ok_all = passed == len(RESULTS)
    rec = {"ok": ok_all, "wire": "cvm-dt-stt-whisper-gate/1",
           "suite": "test_cvm_stt_whisper.py", "passed": passed,
           "total": len(RESULTS), "gated_at_epoch": time.time(),
           "python": sys.version.split()[0], "live_value": LIVE,
           "emitted": "f21b-gate:%d/%d:%s" % (
               passed, len(RESULTS),
               (LIVE.get("cuda") or {}).get("attempt", {}).get("detail")
               or "cuda ok"),
           "results": [{"name": n, "verdict": "PASS" if ok else "FAIL",
                        "detail": e} for n, ok, e in RESULTS]}
    (_HERE / "F21B_WHISPER_TEST.json").write_text(
        json.dumps(rec, indent=1), encoding="utf-8")
    print("%d/%d" % (passed, len(RESULTS)))
    print(rec["emitted"])
    return 0 if ok_all else 1


if __name__ == "__main__":
    raise SystemExit(main())
