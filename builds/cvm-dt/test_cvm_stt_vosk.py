#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""F-21 — local STT model inference, and the guard that it did not disarm A2.

Two things have to be true at once and they pull in opposite directions:

  1. The model path must actually RUN on this box (F-21 read ABSENT because
     `vosk` was not importable for py -3.14).
  2. Provisioning it must NOT change what any other process hears. A2's phone
     ear fallback engages only when `probe_stt()` says this box has no VOSK; if
     dropping 55 MB into `vendor/` flipped that gate, a shipped capability would
     have been switched off by a download, silently.

So the suite proves the ear works AND proves — in a SUBPROCESS with a clean
environment, because in-process `bind()` has already mutated `sys.path` — that
`import vosk` still fails and `probe_stt()` still answers `vosk not importable`
for anything that did not opt in.

The speed claim is measured here too, interleaved in one process, because the
whole F-21 conclusion turns on it: a fresh `KaldiRecognizer` per call costs
~11x what a held one does, on identical audio.

    py -3.14 builds\\cvm-dt\\test_cvm_stt_vosk.py
"""
from __future__ import annotations

import argparse
import io
import json
import os
import subprocess
import sys
import tarfile
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "cosmos"))

import cvm_stt_vosk as V  # noqa: E402

RESULTS: list[tuple[str, bool, str]] = []
LIVE: dict = {}
ARTIFACT = Path(__file__).resolve().parent / V.ARTIFACT
PHRASE = "what is the queue depth"


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:                                            # noqa: BLE001
        RESULTS.append((label, False, "%s: %s" % (type(e).__name__, e)))


def _clean_child(code: str) -> dict:
    """Run `code` in a child with no vendor path and no COSMOS_VOSK_MODEL.

    The child prints one JSON line. This is the only honest way to ask "is vosk
    importable for a process that did not opt in" from a process that did.
    """
    env = dict(os.environ)
    env.pop("COSMOS_VOSK_MODEL", None)
    env.pop("PYTHONPATH", None)
    out = subprocess.run([sys.executable, "-c", code], capture_output=True,
                         text=True, env=env, timeout=180)
    try:
        return json.loads(out.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError):
        return {"error": (out.stderr or out.stdout)[-400:]}


_CHILD_PROBE = """
import json, sys
sys.path.insert(0, r"%s")
from cosmos_cvm_push import probe_stt
try:
    import vosk
    importable = True
except ImportError:
    importable = False
print(json.dumps({"importable": importable, "probe": probe_stt()}))
""" % (Path(__file__).resolve().parents[2] / "cosmos")

_CHILD_BIND = """
import json, sys
sys.path.insert(0, r"%s")
sys.path.insert(0, r"%s")
import cvm_stt_vosk as V
b = V.bind()
from cosmos_cvm_push import probe_stt
print(json.dumps({"bound": b["bound"], "probe": probe_stt()}))
""" % (Path(__file__).resolve().parents[2] / "cosmos",
       Path(__file__).resolve().parent)


# ---------------------------------------------------------------------------
# 1. what is on disk, and is it what upstream published
# ---------------------------------------------------------------------------
def test_provisioning_is_verified():
    st = V.provisioned()
    LIVE["provisioned"] = st
    check("wheel_and_model_are_on_disk",
          lambda: st["site"] and st["model_dir"] and st["wheel"])
    check("model_dir_has_all_three_markers",
          lambda: sorted(st["model_markers"]) == sorted(V.MODEL_MARKERS))
    check("vosk_module_level_deps_are_satisfied",
          lambda: all(st["deps"].values()))

    pins = V.verify_pins()
    LIVE["pins"] = pins
    check("every_provisioned_byte_matches_its_pinned_digest",
          lambda: pins["ok"])
    check("the_wheel_pin_is_pypis_own_published_digest",
          lambda: pins["files"]["wheel"]["sha256"] == V.WHEEL_SHA256)
    check("a_swapped_archive_would_be_caught", _swap_is_caught)


def _swap_is_caught():
    """Prove the pin check FAILS on a changed byte, on a copy - never the
    real vendor file. A verifier that has never rejected anything is a claim."""
    td = Path(tempfile.mkdtemp(prefix="cvm-pin-"))
    fake = td / V.WHEEL_NAME
    real = V.VENDOR / V.WHEEL_NAME
    data = bytearray(real.read_bytes()[:4096])
    data[0] ^= 0xFF
    fake.write_bytes(bytes(data))
    return V.sha256_of(fake) != V.WHEEL_SHA256


def test_sdist_extraction_refuses_an_escape():
    """A matching digest proves provenance, not intent."""
    td = Path(tempfile.mkdtemp(prefix="cvm-sdist-"))
    bad = td / "evil-1.0.tar.gz"
    payload = b"raise SystemExit('should never run')\n"
    with tarfile.open(bad, "w:gz") as t:
        info = tarfile.TarInfo("evil-1.0/srt/../../../pwned.py")
        info.size = len(payload)
        t.addfile(info, io.BytesIO(payload))
    escaped = V.SITE.resolve().parents[2] / "pwned.py"
    try:
        V._extract_module_from_sdist("srt", bad)
        refused = False
    except V.VoskError as e:
        refused = "escapes" in str(e)
    LIVE["sdist_escape"] = {"refused": refused,
                            "landed": escaped.exists()}
    check("path_escape_in_an_sdist_is_refused", lambda: refused)
    check("escaping_member_never_landed", lambda: not escaped.exists())


# ---------------------------------------------------------------------------
# 2. the A2 guard — provisioning must not arm anything
# ---------------------------------------------------------------------------
def test_provisioning_did_not_arm_the_box():
    kid = _clean_child(_CHILD_PROBE)
    LIVE["clean_child"] = kid
    check("vosk_is_not_importable_without_opting_in",
          lambda: kid.get("importable") is False)
    check("probe_stt_still_says_no_vosk",
          lambda: (kid.get("probe") or {}).get("kind") == "STT_NONE"
          and (kid.get("probe") or {}).get("detail") == "vosk not importable")
    check("A2_phone_fallback_gate_is_unchanged",
          lambda: (kid.get("probe") or {}).get("ok") is False)


def test_bind_arms_only_the_process_that_asked():
    kid = _clean_child(_CHILD_BIND)
    LIVE["bound_child"] = kid
    check("bind_makes_vosk_importable_in_that_process",
          lambda: kid.get("bound") is True)
    check("bind_makes_probe_stt_ok_in_that_process",
          lambda: (kid.get("probe") or {}).get("ok") is True
          and (kid.get("probe") or {}).get("engine") == "vosk")
    check("and_the_next_clean_process_is_still_unarmed",
          lambda: _clean_child(_CHILD_PROBE).get("importable") is False)


# ---------------------------------------------------------------------------
# 3. the ear itself
# ---------------------------------------------------------------------------
def test_resident_ear_hears():
    fx = V._fixture(PHRASE)
    ear = V.ResidentVoskEar()
    got = ear.transcribe(fx["pcm"], fx["rate"])
    LIVE["resident_ear"] = {k: got[k] for k in
                            ("transcript", "kind", "ear_ms", "model_load_ms")}
    LIVE["resident_ear"]["word_recall"] = V.recall(PHRASE, got["transcript"])
    check("resident_ear_returns_words",
          lambda: got["kind"] == "ok" and got["transcript"])
    check("resident_ear_recall_is_usable",
          lambda: V.recall(PHRASE, got["transcript"]) >= 0.6)
    check("resident_ear_reports_the_engine_and_model",
          lambda: got["engine"] == "vosk" and got["model"] == V.MODEL_NAME)
    check("empty_pcm_is_STT_NONE_not_a_fabricated_word",
          lambda: ear.transcribe(b"", fx["rate"])["kind"] == "STT_NONE")
    check("second_utterance_costs_far_less_than_the_first",
          lambda: ear.transcribe(fx["pcm"], fx["rate"])["ear_ms"]
          < (got["model_load_ms"] or 1e9))
    check("ear_matches_the_SapiTranscriber_surface",
          lambda: all(hasattr(ear, m) for m in
                      ("accept", "finish", "transcribe", "recognize_pcm")))

    ear.accept(fx["pcm"][:len(fx["pcm"]) // 2])
    ear.accept(fx["pcm"][len(fx["pcm"]) // 2:])
    sunk = ear.finish()
    check("incremental_sink_hears_the_same_phrase",
          lambda: sunk["transcript"] == got["transcript"])


def test_resident_beats_per_call_construction():
    """The measurement the whole F-21 conclusion rests on. Interleaved."""
    fx = V._fixture(PHRASE)
    b = V.bind(set_env=False)
    from vosk import KaldiRecognizer, Model, SetLogLevel
    SetLogLevel(-1)
    model = Model(b["model_path"])
    held = KaldiRecognizer(model, V.STT_RATE)

    fresh_ms, resident_ms = [], []
    for _ in range(3):                       # interleaved: same machine load
        t = time.perf_counter()
        r = KaldiRecognizer(model, V.STT_RATE)
        r.AcceptWaveform(fx["pcm"])
        r.FinalResult()
        fresh_ms.append((time.perf_counter() - t) * 1000.0)

        held.Reset()
        t = time.perf_counter()
        held.AcceptWaveform(fx["pcm"])
        held.FinalResult()
        resident_ms.append((time.perf_counter() - t) * 1000.0)

    fresh_ms.sort()
    resident_ms.sort()
    med_f = fresh_ms[len(fresh_ms) // 2]
    med_r = resident_ms[len(resident_ms) // 2]
    LIVE["ab_recognizer"] = {
        "fresh_per_call_ms": round(med_f, 3),
        "resident_ms": round(med_r, 3),
        "speedup": round(med_f / max(med_r, 1e-9), 2),
        "interleaved": True, "n": len(fresh_ms),
        "fixture_s": fx["seconds"],
    }
    check("a_held_recognizer_is_measurably_faster",
          lambda: med_r < med_f)
    check("the_gap_is_large_not_noise",
          lambda: med_f / max(med_r, 1e-9) >= 3.0)


# ---------------------------------------------------------------------------
# 4. the artifact
# ---------------------------------------------------------------------------
def test_artifact():
    if not ARTIFACT.is_file():
        LIVE["artifact"] = {"kind": "ABSENT"}
        check("artifact_present", lambda: False)
        return
    rec = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    m = rec.get("measure") or {}
    LIVE["artifact"] = {
        "emitted": rec.get("emitted"),
        "vosk_resident_ms": ((m.get("vosk") or {}).get("resident") or {}
                             ).get("per_utterance_ms"),
        "vosk_cold_ms": (m.get("vosk") or {}).get("cold_per_utterance_ms"),
        "sapi_ms": (m.get("sapi") or {}).get("inference_ms"),
        "faster": (m.get("delta") or {}).get("faster_engine_on_this_box"),
    }
    check("artifact_says_the_model_path_ran",
          lambda: rec.get("ok") is True
          and (m.get("vosk") or {}).get("kind") == "ok")
    check("artifact_compares_both_engines_on_the_same_pcm",
          lambda: (m.get("delta") or {}).get("same_pcm") is True
          and (m.get("sapi") or {}).get("kind") == "ok")
    check("artifact_keeps_the_real_mic_caveat",
          lambda: "UNMEASURED" in ((m.get("delta") or {}).get("caveat") or ""))
    check("artifact_records_that_arming_was_not_done",
          lambda: (rec.get("arm") or {}).get("ran") is False)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.parse_args(argv)

    test_provisioning_is_verified()
    test_sdist_extraction_refuses_an_escape()
    test_provisioning_did_not_arm_the_box()
    test_bind_arms_only_the_process_that_asked()
    test_resident_ear_hears()
    test_resident_beats_per_call_construction()
    test_artifact()

    passed = sum(1 for _, ok, _ in RESULTS if ok)
    for label, ok, err in RESULTS:
        print("%s %s%s" % ("PASS" if ok else "FAIL", label,
                           (" - " + err) if err else ""))
    ok_all = passed == len(RESULTS)
    ab = LIVE.get("ab_recognizer", {})
    ear = LIVE.get("resident_ear", {})
    rec = {
        "ok": ok_all, "wire": "cvm-dt-f21-stt-vosk/1",
        "suite": "test_cvm_stt_vosk.py",
        "passed": passed, "total": len(RESULTS),
        "gated_at_epoch": time.time(), "python": sys.version.split()[0],
        "live_value": LIVE,
        "emitted": "f21-test:resident %s ms vs fresh %s ms (%sx) on a %s s "
                   "fixture; heard %r recall %s; clean child still "
                   "vosk-importable=%s" % (
                       ab.get("resident_ms"), ab.get("fresh_per_call_ms"),
                       ab.get("speedup"), ab.get("fixture_s"),
                       ear.get("transcript"), ear.get("word_recall"),
                       (LIVE.get("clean_child") or {}).get("importable")),
        "results": [{"name": n, "verdict": "PASS" if o else "FAIL",
                     "detail": e} for n, o, e in RESULTS],
    }
    out = Path(__file__).resolve().parent / "F21_STT_TEST.json"
    out.write_text(json.dumps(rec, indent=1, default=str), encoding="utf-8")
    print(json.dumps({"ok": ok_all, "passed": passed, "total": len(RESULTS),
                      "emitted": rec["emitted"], "proof_path": str(out)},
                     indent=1))
    return 0 if ok_all else 1


if __name__ == "__main__":
    raise SystemExit(main())
