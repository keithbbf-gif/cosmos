#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""F-21b — whisper as a THIRD local ear, measured against the two that ship.

`CVM_BACKLOG` B3 says the honest next step, if real-mic recall is poor, is
"whisper.cpp / faster-whisper on the RTX 3070, which CVM_ARCH §4 classes as
OVERFLOW *until measured*". `cvm_runtimes.py` measured the first half of that:
every wheel `faster-whisper` needs exists for `cp314-win_amd64`, 81.5 MB for
the whole closure, no credential (`RUNTIMES.json:reachability`). So the
question stopped being "is it reachable" and became "is it BETTER", and that
one only a measurement can answer.

The specific thing being tested is the one that blocks `CVM_BACKLOG` B8:
**VOSK is faster than SAPI and less accurate than SAPI** (62.5 ms vs 210.0 ms;
recall 0.80 vs 1.00, re-measured today, `F21_STT_LOCAL.json`), so arming the
local model ear trades accuracy for latency. A third engine that is both fast
AND accurate would dissolve that trade instead of deciding it.

Discipline, inherited from `cvm_stt_vosk.py` (A5) and kept identical here:

* **Provisioning arms nothing.** The wheels land in `vendor/whisper_site`,
  which is a SEPARATE import root from the VOSK one and is on nobody's
  `sys.path`. Model weights land in `vendor/hf`, not in the user profile
  cache, so nothing outside `builds/cvm-dt/` is written.
* **`--only-binary=:all:`** — no `setup.py` from the network ever executes.
* **pip's own install report is the pin.** Every wheel's URL and sha256 come
  back from the resolver and are written to `vendor/whisper_site/_pip_report.json`,
  so a later run can say what it actually installed rather than what it meant to.
* **Same PCM, one process, interleaved.** The fixture is
  `cvm_stt_vosk._fixture` — the identical SAPI-TTS bytes the VOSK and SAPI rows
  were measured on. Three engines measured in separate passes on a box that
  carries other agents would compare machine load as much as models.

    py -3.14 builds\\cvm-dt\\cvm_stt_whisper.py --provision
    py -3.14 builds\\cvm-dt\\cvm_stt_whisper.py --models tiny.en,base.en

Artifact: `builds/cvm-dt/F21B_STT_WHISPER.json` (`schema cvm-dt-stt-whisper/1`).
"""
from __future__ import annotations

import argparse
import json
import os
import statistics
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
_COSMOS_LIB = _HERE.parents[1] / "cosmos"
if str(_COSMOS_LIB) not in sys.path:
    sys.path.insert(0, str(_COSMOS_LIB))

import cvm_stt_vosk as V  # noqa: E402  (the fixture, the recall metric, the ears)

WIRE = "cvm-dt-stt-whisper/1"
ARTIFACT = "F21B_STT_WHISPER.json"

VENDOR = _HERE / "vendor"
SITE = VENDOR / "whisper_site"       # separate root: cannot perturb the VOSK ear
HF_CACHE = VENDOR / "hf"             # model weights stay inside the fence
REPORT = SITE / "_pip_report.json"

REQUIREMENT = "faster-whisper"
DEFAULT_MODELS = ("tiny.en",)

# What Keith would actually SAY to COSMOS. Not tongue-twisters and not the
# single phrase every prior artifact used: a verdict about one utterance is a
# verdict about one word, and "queue depth" is a domain term that any engine
# may reasonably mis-hear.
DEFAULT_PHRASES = (
    "what is the queue depth",
    "open a status report",
    "show me the ledger",
    "how much have I spent today",
    "pause the clock",
    "run the audit",
    "what is the spend guard saying",
    "list the running jobs",
    "back up the tree",
    "read me the last incident",
)
STT_RATE = 16000
PIP_TIMEOUT_S = 900.0


class WhisperError(RuntimeError):
    def __init__(self, kind: str, detail: str = ""):
        super().__init__("[%s] %s" % (kind, detail))
        self.kind = kind
        self.detail = detail


# --------------------------------------------------------------------------
# provisioning — arms nothing, runs no setup.py, and pins what it got
# --------------------------------------------------------------------------

def provision(*, force: bool = False, requirement: str = REQUIREMENT) -> dict:
    """Install the closure into a private root. Returns pip's OWN report."""
    SITE.mkdir(parents=True, exist_ok=True)
    if REPORT.is_file() and not force:
        rec = json.loads(REPORT.read_text(encoding="utf-8"))
        rec["reused"] = True
        return rec
    t0 = time.perf_counter()
    out = SITE / "_pip_report.raw.json"
    argv = [sys.executable, "-m", "pip", "install",
            "--target", str(SITE),
            "--only-binary", ":all:",          # no setup.py from the network
            "--no-input", "--disable-pip-version-check",
            "--report", str(out), requirement]
    r = subprocess.run(argv, capture_output=True, text=True,
                       timeout=PIP_TIMEOUT_S)
    if r.returncode != 0 or not out.is_file():
        raise WhisperError("PIP_FAILED", "rc=%s %s" % (
            r.returncode, (r.stderr or r.stdout or "").strip()[-600:]))
    raw = json.loads(out.read_text(encoding="utf-8"))
    installed = []
    for item in raw.get("install") or []:
        info = item.get("download_info") or {}
        meta = item.get("metadata") or {}
        installed.append({
            "name": meta.get("name"), "version": meta.get("version"),
            "url": info.get("url"),
            "sha256": ((info.get("archive_info") or {}).get("hashes")
                       or {}).get("sha256"),
        })
    rec = {"ok": True, "requirement": requirement, "target": str(SITE),
           "pip_report_version": raw.get("version"),
           "installed": sorted(installed, key=lambda d: (d["name"] or "")),
           "package_count": len(installed),
           "elapsed_ms": round((time.perf_counter() - t0) * 1000.0, 1),
           "only_binary": True, "reused": False,
           "iso": time.strftime("%Y-%m-%dT%H:%M:%S%z")}
    REPORT.write_text(json.dumps(rec, indent=1), encoding="utf-8")
    return rec


def provisioned() -> dict:
    """What is on disk right now — no import, no network."""
    rec = {"site": SITE.is_dir(), "report": REPORT.is_file(),
           "hf_cache": HF_CACHE.is_dir(), "site_path": str(SITE),
           "hf_path": str(HF_CACHE)}
    if rec["report"]:
        r = json.loads(REPORT.read_text(encoding="utf-8"))
        # Name, version AND digest. `vendor/` is git-ignored, so the artifact
        # is the only committed record of what is actually on this disk — a
        # list of names would not survive a swapped wheel.
        rec["packages"] = [{"name": d["name"], "version": d["version"],
                            "sha256": d.get("sha256")} for d in r["installed"]]
        rec["package_count"] = r.get("package_count")
        rec["unpinned"] = [d["name"] for d in r["installed"]
                           if not d.get("sha256")]
        rec["only_binary"] = r.get("only_binary")
    if rec["hf_cache"]:
        rec["models_on_disk"] = sorted(
            p.name for p in HF_CACHE.glob("models--*"))
        rec["hf_bytes"] = sum(f.stat().st_size
                              for f in HF_CACHE.rglob("*") if f.is_file())
    return rec


def bind(*, set_env: bool = False) -> dict:
    """Put the private root on THIS process's path and import. Arms nothing.

    `set_env` writes nothing to the machine: it only points this process's
    HuggingFace cache at `vendor/hf` so a model download cannot escape the
    fence. Nothing here changes what any other process can import.
    """
    if not SITE.is_dir():
        raise WhisperError("NOT_PROVISIONED",
                           "%s does not exist; run --provision" % SITE)
    if str(SITE) not in sys.path:
        sys.path.insert(0, str(SITE))
    HF_CACHE.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("HF_HOME", str(HF_CACHE))
    os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")
    t0 = time.perf_counter()
    try:
        import faster_whisper                                     # noqa: F401
    except Exception as e:                                        # noqa: BLE001
        raise WhisperError("IMPORT_FAILED",
                           "%s: %s" % (type(e).__name__, e)) from e
    import ctranslate2                                            # noqa: F401
    return {"bound": True,
            "import_ms": round((time.perf_counter() - t0) * 1000.0, 3),
            "faster_whisper": getattr(faster_whisper, "__version__", None),
            "ctranslate2": getattr(ctranslate2, "__version__", None),
            "site": str(SITE), "hf_home": os.environ.get("HF_HOME"),
            "env_set": bool(set_env)}


def devices() -> dict:
    """Which CTranslate2 devices this box will actually accept. Measured."""
    import ctranslate2
    out: dict = {"ctranslate2": ctranslate2.__version__}
    for dev in ("cpu", "cuda"):
        try:
            out[dev] = {"ok": True, "compute_types": sorted(
                ctranslate2.get_supported_compute_types(dev))}
        except Exception as e:                                    # noqa: BLE001
            out[dev] = {"ok": False,
                        "why": "%s: %s" % (type(e).__name__, e)}
    try:
        n = int(ctranslate2.get_cuda_device_count())
    except Exception as e:                                        # noqa: BLE001
        n, out["cuda_count_error"] = 0, "%s: %s" % (type(e).__name__, e)
    out["cuda_device_count"] = n
    if not n:
        out["cuda_why"] = (
            "CTranslate2 reports 0 CUDA devices. nvidia-smi DOES see the GPU "
            "(RUNTIMES.json:gpu names an RTX 3070, driver 610.62), and "
            "RUNTIMES.json:accelerator_libs.toolkit_present is false — so "
            "this is a missing CUDA/cuDNN runtime on the box, not missing "
            "hardware. GPU whisper is a further download, not a further wheel")
    return out


def cuda_attempt(model: str = "tiny.en",
                 compute_type: str = "int8_float16",
                 phrase: str = "pause the clock") -> dict:
    """DECODE on the GPU. Constructing the model is not enough — measured.

    Three probes of increasing strength give three different answers here, and
    only the last one is true:

      `get_cuda_device_count()`      -> 1     (the DRIVER enumerates the 3070)
      `WhisperModel(device='cuda')`  -> ok    (construction touches no kernel)
      first `transcribe()` on it     -> RuntimeError:
                                        Library cublas64_12.dll is not found

    CTranslate2 loads cuBLAS lazily, at first compute. A probe that stopped at
    construction reported a working GPU on a box where `cublas64_12.dll` does
    not exist in System32, in either interpreter's site-packages, or anywhere
    under `vendor/` — which is how this function was written the first time.
    So it decodes, and the phase that failed is named in the result.
    """
    t0 = time.perf_counter()
    phase = "construct"
    try:
        ear = ResidentWhisperEar(model, device="cuda",
                                 compute_type=compute_type)
        load_ms = ear.load_ms
        phase = "decode"
        fx = V._fixture(phrase)
        out = ear.transcribe(fx["pcm"], fx["rate"])
    except Exception as e:                                        # noqa: BLE001
        return {"ok": False, "failed_at": phase, "kind": type(e).__name__,
                "detail": str(e)[:400], "model": model,
                "compute_type": compute_type,
                "ms": round((time.perf_counter() - t0) * 1000.0, 1),
                "means": "the GPU is visible to the driver and unusable to the "
                         "runtime; see RUNTIMES.json:reachability."
                         "gpu-cuda-libs for what the missing libraries cost"}
    return {"ok": True, "failed_at": None, "kind": "ok", "model": model,
            "compute_type": compute_type, "load_ms": load_ms,
            "decode_ms": out["ear_ms"], "transcript": out["transcript"],
            "phrase": phrase}


# --------------------------------------------------------------------------
# the ear — same surface as ResidentVoskEar / SapiTranscriber, no caller branch
# --------------------------------------------------------------------------

class ResidentWhisperEar:
    """Model held across turns. Same `accept`/`finish`/`transcribe` surface.

    A7 measured what happens when a local model ear is rebuilt per utterance
    (663.6 ms -> 64.5 ms on VOSK). The same trap is here: `WhisperModel()`
    loads weights. It is constructed ONCE and reused.
    """

    def __init__(self, name: str, *, device: str = "cpu",
                 compute_type: str = "int8"):
        from faster_whisper import WhisperModel
        t0 = time.perf_counter()
        self.name = name
        self.device = device
        self.compute_type = compute_type
        self._model = WhisperModel(name, device=device,
                                   compute_type=compute_type,
                                   download_root=str(HF_CACHE))
        self.load_ms = round((time.perf_counter() - t0) * 1000.0, 3)
        self._buf = bytearray()
        self._rate = STT_RATE

    def accept(self, pcm: bytes, rate: int = STT_RATE) -> None:
        self._rate = int(rate) or STT_RATE
        self._buf += pcm

    def finish(self) -> dict:
        if not self._buf:
            raise WhisperError("STT_NONE", "finish() with nothing accepted")
        pcm, self._buf = bytes(self._buf), bytearray()
        return self.transcribe(pcm, self._rate)

    def transcribe(self, pcm: bytes, rate: int = STT_RATE) -> dict:
        import numpy as np
        if int(rate) != STT_RATE:
            raise WhisperError("RATE", "whisper wants %d Hz, got %s"
                               % (STT_RATE, rate))
        audio = (np.frombuffer(pcm, dtype="<i2").astype("float32") / 32768.0)
        t0 = time.perf_counter()
        segs, info = self._model.transcribe(audio, language="en",
                                            vad_filter=False, beam_size=1)
        text = " ".join(s.text.strip() for s in segs).strip()
        return {"engine": "whisper", "model": self.name, "kind": "ok" if text
                else "STT_NONE", "transcript": text,
                "ear_ms": round((time.perf_counter() - t0) * 1000.0, 3),
                "device": self.device, "compute_type": self.compute_type,
                "language": getattr(info, "language", None)}


# --------------------------------------------------------------------------
# the measurement — three engines, same bytes, one process, interleaved
# --------------------------------------------------------------------------

_WORD = __import__("re").compile(r"[a-z0-9]+")


def norm_recall(spoken: str, heard: str) -> float:
    """`cvm_stt_vosk.recall`, with punctuation and case taken out first.

    The shipped metric splits on whitespace only. VOSK and SAPI return bare
    lowercase-ish words, so it never mattered — but whisper returns PUNCTUATED,
    capitalised prose, so "What is the Q-depth?" scores 0.60 under it while
    SAPI's "What is the queue depth" scores 1.00, and part of that gap is the
    question mark rather than the model. Both numbers are reported: this one is
    the fair comparison, `word_recall` is the one every prior artifact used and
    is kept so the rows stay comparable with `F21_STT_LOCAL.json`.
    """
    want = set(_WORD.findall(str(spoken).lower()))
    got = set(_WORD.findall(str(heard).lower()))
    return round(len(want & got) / max(1, len(want)), 3)


def measure(phrases, *, models: tuple = DEFAULT_MODELS,
            reps: int = 3, device: str = "cpu",
            compute_type: str = "int8") -> dict:
    """Every engine, every phrase, same bytes, one process, interleaved.

    Phrases are plural on purpose. One phrase is an anecdote: "Q-depth" for
    "queue depth" is a defensible reading of synthesised speech, and a verdict
    resting on it would be a verdict about one word.
    """
    if isinstance(phrases, str):
        phrases = (phrases,)
    phrases = tuple(p for p in phrases if p.strip())
    if not phrases:
        raise WhisperError("NO_PHRASES", "nothing to say")

    ears: list[tuple[str, object]] = []
    load: dict[str, float] = {}
    for name in models:
        e = ResidentWhisperEar(name, device=device, compute_type=compute_type)
        load["whisper:" + name] = e.load_ms
        ears.append(("whisper:" + name, e))

    vb = V.bind(set_env=False)
    ears.append(("vosk:" + V.MODEL_NAME, V.ResidentVoskEar(vb["model_path"])))

    fixtures = {p: V._fixture(p) for p in phrases}

    # Warm every ear once on the first fixture: the first call on any of them
    # pays a one-time cost that belongs in `load`, not in a per-utterance
    # median.
    first = fixtures[phrases[0]]
    warm = {label: e.transcribe(first["pcm"], first["rate"])["ear_ms"]
            for label, e in ears}

    ms: dict[str, list[float]] = {label: [] for label, _ in ears}
    heard: dict[str, dict[str, str]] = {label: {} for label, _ in ears}
    for phrase in phrases:
        fx = fixtures[phrase]
        for _ in range(max(1, int(reps))):
            for label, e in ears:                    # interleaved, not batched
                r = e.transcribe(fx["pcm"], fx["rate"])
                ms[label].append(float(r["ear_ms"]))
                heard[label][phrase] = r["transcript"]

    # SAPI, per phrase, through the same helper every prior artifact used.
    sapi_rows = {p: V.measure(p, reps=1)["sapi"] for p in phrases}

    def _agg(label, per_phrase_text, times, load_ms, warm_ms):
        raw = [V.recall(p, per_phrase_text[p]) for p in phrases]
        norm = [norm_recall(p, per_phrase_text[p]) for p in phrases]
        return {
            "engine": label,
            "per_utterance_ms": round(statistics.median(times), 3),
            "min_ms": round(min(times), 3), "max_ms": round(max(times), 3),
            "n": len(times), "phrases": len(phrases),
            "word_recall": round(statistics.mean(raw), 3),
            "word_recall_normalised": round(statistics.mean(norm), 3),
            "perfect_phrases": sum(1 for x in norm if x >= 1.0),
            "load_ms": load_ms, "warm_first_call_ms": warm_ms,
            "heard": {p: per_phrase_text[p] for p in phrases},
        }

    rows = [_agg(label, heard[label], ms[label], load.get(label), warm[label])
            for label, _ in ears]
    rec_name = str(sapi_rows[phrases[0]].get("recognizer"))
    rows.append(_agg(
        "sapi:" + rec_name,
        {p: sapi_rows[p]["transcript"] for p in phrases},
        [float(sapi_rows[p]["inference_ms"]) for p in phrases],
        None, None))

    best_ms = min(rows, key=lambda r: r["per_utterance_ms"])
    best_rec = max(rows, key=lambda r: (r["word_recall_normalised"],
                                        -r["per_utterance_ms"]))
    # "Fastest" and "most accurate" being different engines does NOT mean a
    # trade has to be made. What matters for B8 is whether one engine beats
    # another on BOTH axes — that is a decision with nothing to weigh.
    dominates = []
    for a in rows:
        for b in rows:
            if a is b:
                continue
            if (a["per_utterance_ms"] < b["per_utterance_ms"]
                    and a["word_recall_normalised"] >= b["word_recall_normalised"]
                    and a["perfect_phrases"] >= b["perfect_phrases"]):
                dominates.append({
                    "faster_and_no_less_accurate": a["engine"],
                    "than": b["engine"],
                    "ms": [a["per_utterance_ms"], b["per_utterance_ms"]],
                    "recall": [a["word_recall_normalised"],
                               b["word_recall_normalised"]],
                    "perfect": [a["perfect_phrases"], b["perfect_phrases"]],
                })
    return {
        "wire": WIRE,
        "fixtures": {p: {k: v for k, v in fixtures[p].items() if k != "pcm"}
                     for p in phrases},
        "phrases": list(phrases),
        "rows": rows,
        "fastest": best_ms["engine"], "most_accurate": best_rec["engine"],
        "dissolves_the_b8_trade": bool(
            best_rec["engine"] == best_ms["engine"]),
        "dominates": dominates,
        "interleaved": True,
        "fixture_bias": "The fixtures are synthesised BY SAPI. SAPI is "
                        "therefore being scored on hearing its own "
                        "synthesiser, which can only FLATTER it — so any row "
                        "SAPI loses, it loses with the advantage.",
        "metric_note": "`word_recall` is the shipped whitespace-split metric "
                       "(`cvm_stt_vosk.recall`), kept so these rows compare "
                       "with F21_STT_LOCAL.json. It penalises whisper for "
                       "punctuation no other engine emits, so "
                       "`word_recall_normalised` is the one the verdicts use.",
        "caveat": "SYNTHESIZER IN. Every engine here heard the same SAPI-TTS "
                  "fixture, which is a clean signal. Real-microphone accuracy "
                  "is UNMEASURED for all of them (CVM_BACKLOG B3); these are "
                  "an upper bound, not a prediction.",
    }


def arm_line() -> dict:
    """What arming WOULD take. Emitted, never done — same rule as A5."""
    return {
        "ran": False,
        "why": "a third ear is a routing decision (which engine every desktop "
               "and phone turn uses), not a side effect of a download",
        "requires": [
            "%s on sys.path for the processes that should hear with whisper"
            % SITE,
            "HF_HOME=%s so model weights resolve inside the fence" % HF_CACHE,
            "a real-microphone comparison (CVM_BACKLOG B3) — every recall "
            "number here is synthesizer-in",
        ],
    }


def run(phrases, *, models: tuple, reps: int, do_provision: bool,
        device: str, compute_type: str) -> dict:
    rec = {"wire": WIRE, "feature": "F-21b whisper as a local ear",
           "iso": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "epoch": time.time(),
           "python": sys.version.split()[0],
           "before": {"provisioned": provisioned()}}
    if do_provision:
        rec["provision"] = provision()
    try:
        rec["bind"] = bind()
    except WhisperError as e:
        rec.update({"ok": False, "kind": e.kind, "detail": e.detail,
                    "emitted": "f21b-whisper:%s:%s" % (e.kind, e.detail[:160])})
        return rec
    rec["devices"] = devices()
    rec["cuda_attempt"] = cuda_attempt()
    rec["measure"] = measure(phrases, models=tuple(models), reps=reps,
                             device=device, compute_type=compute_type)
    rec["after"] = {"provisioned": provisioned()}
    rec["arm"] = arm_line()
    rec["ok"] = True
    rows = rec["measure"]["rows"]
    rec["emitted"] = "f21b-whisper:%s:%d phrases x %d reps:%s" % (
        rec["bind"].get("faster_whisper"), len(rec["measure"]["phrases"]), reps,
        " | ".join("%s %.1f ms recall %.2f (raw %.2f) %d/%d perfect" % (
            r["engine"], r["per_utterance_ms"], r["word_recall_normalised"],
            r["word_recall"], r["perfect_phrases"], r["phrases"])
            for r in rows))
    return rec


def write_artifact(rec: dict, out_dir: Optional[Path] = None) -> Path:
    out = (Path(out_dir) if out_dir else _HERE) / ARTIFACT
    out.write_text(json.dumps(rec, indent=1), encoding="utf-8")
    return out


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--phrases", default="|".join(DEFAULT_PHRASES),
                    help="pipe-separated; the default is the COSMOS verb set")
    ap.add_argument("--models", default=",".join(DEFAULT_MODELS))
    ap.add_argument("--reps", type=int, default=3)
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--compute-type", default="int8")
    ap.add_argument("--provision", action="store_true")
    ap.add_argument("--out", default=None)
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args(argv)
    rec = run(tuple(p.strip() for p in a.phrases.split("|") if p.strip()),
              models=tuple(m.strip() for m in a.models.split(",") if m.strip()),
              reps=a.reps, do_provision=a.provision, device=a.device,
              compute_type=a.compute_type)
    path = write_artifact(rec, Path(a.out) if a.out else None)
    if not a.quiet:
        print(json.dumps(rec, indent=1))
    print(rec["emitted"])
    print(str(path))
    return 0 if rec.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
