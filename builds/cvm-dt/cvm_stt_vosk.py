#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""F-21 — local STT MODEL inference, provisioned and measured on this box.

`docs/FEATURE_MASTER.md` F-21 reads **ABSENT**: *"vosk is not importable for
py -3.14; the bench records the stage as UNMEASURED rather than estimating
it."* `cosmos_cvm_push.probe_stt` needs BOTH an importable `vosk` AND
`COSMOS_VOSK_MODEL` pointing at a real directory; this box had neither, so the
whole model-inference path has never executed here. A1 shipped the SAPI floor
so `STT_NONE` stops meaning "nobody ran pip" — this module closes the other
half: it makes the model path RUNNABLE and then measures what it costs, so the
SAPI-vs-model choice is decided by numbers instead of by which one happened to
be installed.

Two artifacts are fetched, both public, neither a credential:

  * `vosk-0.3.45-py3-none-win_amd64.whl` from PyPI — a `py3-none` wheel (an
    ABI-independent tag, so 3.14 loads it) carrying `libvosk.dll` and a cffi
    ABI-mode binding. `cffi` and `_cffi_backend` are already present for
    py -3.14 on this box (measured before fetching); `srt` and `websockets` are
    NOT, and are not needed — they belong to `vosk.transcriber`, which the
    top-level import does not touch.
  * `vosk-model-small-en-us-0.15` from alphacephei.com — the 40 MB CPU model.

Both land under `builds/cvm-dt/vendor/` (git-ignored; see its `.gitignore`),
and the wheel is verified against **PyPI's own published sha256** before it is
unpacked. The model's sha256 and byte count are recorded, so a later swap is
detectable even though upstream publishes no digest.

**Provisioning here does NOT arm the live system, deliberately.** The vendor
directory is not on `sys.path` and `COSMOS_VOSK_MODEL` is not set for anything
but this process, so `cosmos_cvm_push.probe_stt` still answers `vosk not
importable` and A2's phone-ear fallback stays engaged exactly as shipped. Arming
it is a separate, named decision (see `arm_line()`), because it flips which
engine the phone path uses and that belongs to the Orchestrator, not to a
download.

    py -3.14 builds\\cvm-dt\\cvm_stt_vosk.py --provision
    py -3.14 builds\\cvm-dt\\cvm_stt_vosk.py --measure --phrase "what is the queue depth"
    py -3.14 builds\\cvm-dt\\test_cvm_stt_vosk.py
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import time
import urllib.request
import zipfile
from pathlib import Path
from typing import Any, Optional

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
_COSMOS_LIB = Path(__file__).resolve().parents[2] / "cosmos"
if _COSMOS_LIB.is_dir() and str(_COSMOS_LIB) not in sys.path:
    sys.path.insert(0, str(_COSMOS_LIB))

WIRE = "cvm-dt-stt-vosk/1"
ARTIFACT = "F21_STT_LOCAL.json"
VENDOR = _HERE / "vendor"
SITE = VENDOR / "site"                   # unpacked wheel == an import root
MODELS = VENDOR / "models"

WHEEL_NAME = "vosk-0.3.45-py3-none-win_amd64.whl"
PYPI_JSON = "https://pypi.org/pypi/vosk/0.3.45/json"
# vosk/__init__.py imports `srt` at MODULE level (measured: ModuleNotFoundError
# on the first bind), so it is a hard dependency of `import vosk` even though
# only the subtitle writer uses it. `requests` and `tqdm` - the other two
# top-level imports - are already present for py -3.14 on this box. `cffi` and
# `_cffi_backend` back the ABI binding and are also already present. Nothing
# here is compiled: every dep fetched is a `py3-none-any` wheel.
PURE_DEPS = ("srt",)
MODEL_NAME = "vosk-model-small-en-us-0.15"
MODEL_URL = "https://alphacephei.com/vosk/models/%s.zip" % MODEL_NAME

# Pinned identity, committed in SOURCE because `vendor/` is git-ignored: the
# bytes are not in the repo, so the only thing that can survive a fresh clone is
# what they were SUPPOSED to be. WHEEL_SHA256 was verified against PyPI's own
# published digest at provisioning time (2026-08-31) and is re-checked against
# it on every network provision; MODEL_SHA256 is what this box downloaded, since
# alphacephei publishes no digest. A mismatch is a refusal, not a warning - an
# unverified archive is code from nobody in particular.
WHEEL_SHA256 = "6994ddc68556c7e5730c3b6f6bad13320e3519b13ce3ed2aa25a86724e7c10ac"
MODEL_SHA256 = "30f26242c4eb449f948e42cb302dd7a686cb29a3423a8367f99ff41780942498"
DEP_SHA256 = {
    "srt-3.5.3.tar.gz":
        "4884315043a4f0740fd1f878ed6caa376ac06d70e135f306a6dc44632eed0cc0",
}

STT_RATE = 16000
NET_TIMEOUT_S = 120.0
# The model dir has to look like a model, not merely exist: the empty-dir scar
# says existence is not identity.
MODEL_MARKERS = ("am", "conf", "graph")


class VoskError(RuntimeError):
    """Typed refusal. A missing model is named, never silently skipped."""


# ---------------------------------------------------------------------------
# provisioning
# ---------------------------------------------------------------------------
def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _download(url: str, dest: Path) -> dict:
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".part")
    t0 = time.perf_counter()
    with urllib.request.urlopen(url, timeout=NET_TIMEOUT_S) as r:
        status = int(getattr(r, "status", 0) or 0)
        with open(tmp, "wb") as f:
            shutil.copyfileobj(r, f, 1 << 20)
    tmp.replace(dest)
    return {"url": url, "http": status, "bytes": dest.stat().st_size,
            "ms": round((time.perf_counter() - t0) * 1000.0, 1),
            "sha256": sha256_of(dest)}


def _pypi_wheel() -> dict:
    """The wheel's URL and PUBLISHED digest, from the index, not from memory."""
    with urllib.request.urlopen(PYPI_JSON, timeout=NET_TIMEOUT_S) as r:
        meta = json.load(r)
    for f in meta.get("urls", []):
        if f.get("filename") == WHEEL_NAME:
            return {"filename": WHEEL_NAME, "url": f["url"],
                    "published_sha256": (f.get("digests") or {}).get("sha256"),
                    "published_bytes": f.get("size"),
                    "requires_dist": meta.get("info", {}).get("requires_dist")}
    raise VoskError("PyPI does not list %s for vosk 0.3.45" % WHEEL_NAME)


def _pypi_pure_dist(name: str) -> dict:
    """A pure-python distribution for `name`: a `none-any` wheel, else the sdist.

    `srt` publishes ONLY an sdist (measured: `srt-3.5.3.tar.gz`, no wheel), and
    it is a single top-level module. That is extractable without building
    anything - `setup.py` is never executed here, so "install" stays "unzip a
    .py file", which is the only kind of third-party install this fence should
    ever do.
    """
    with urllib.request.urlopen("https://pypi.org/pypi/%s/json" % name,
                                timeout=NET_TIMEOUT_S) as r:
        meta = json.load(r)
    version = meta["info"]["version"]
    for f in meta.get("urls", []):
        fn = f.get("filename") or ""
        if fn.endswith("-py3-none-any.whl") or fn.endswith("-py2.py3-none-any.whl"):
            return {"filename": fn, "url": f["url"], "version": version,
                    "kind": "wheel",
                    "published_sha256": (f.get("digests") or {}).get("sha256")}
    for f in meta.get("urls", []):
        if f.get("packagetype") == "sdist" and str(
                f.get("filename", "")).endswith(".tar.gz"):
            return {"filename": f["filename"], "url": f["url"],
                    "version": version, "kind": "sdist",
                    "published_sha256": (f.get("digests") or {}).get("sha256")}
    raise VoskError("no pure-python distribution published for %s" % name)


def _extract_module_from_sdist(name: str, archive: Path) -> list[str]:
    """Pull `<name>.py` (or `<name>/`) out of an sdist. Nothing is executed.

    Refuses any member that escapes the destination - a tarball is untrusted
    input even when its digest matched, because the digest proves provenance,
    not intent.
    """
    import tarfile
    got: list[str] = []
    SITE.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive, "r:gz") as t:
        for m in t.getmembers():
            parts = Path(m.name).parts
            if len(parts) < 2 or not m.isfile():
                continue
            rest = Path(*parts[1:])
            if rest.parts[0] not in (name + ".py", name):
                continue
            dest = (SITE / rest).resolve()
            if not str(dest).startswith(str(SITE.resolve())):
                raise VoskError("sdist member escapes the vendor dir: %r"
                                % m.name)
            dest.parent.mkdir(parents=True, exist_ok=True)
            src = t.extractfile(m)
            if src is None:
                continue
            dest.write_bytes(src.read())
            got.append(str(rest).replace("\\", "/"))
    if not got:
        raise VoskError("sdist for %s carries no top-level module" % name)
    return got


def _provision_deps(*, force: bool = False) -> list[dict]:
    """Fetch the pure-python deps `import vosk` needs, into the same SITE root.

    Same rule as the wheel: verified against PyPI's published sha256 before it
    is unpacked. A dependency is code too.
    """
    rows: list[dict] = []
    for name in PURE_DEPS:
        pw = _pypi_pure_dist(name)
        dest = VENDOR / pw["filename"]
        if force or not dest.is_file():
            got = _download(pw["url"], dest)
        else:
            got = {"url": pw["url"], "http": 0, "bytes": dest.stat().st_size,
                   "ms": 0.0, "sha256": sha256_of(dest), "cached": True}
        verified = bool(pw["published_sha256"]
                        and got["sha256"] == pw["published_sha256"])
        if not verified:
            raise VoskError("%s sha256 does not match PyPI's published digest "
                            "- refusing to unpack it" % name)
        pin = DEP_SHA256.get(pw["filename"])
        if pin and got["sha256"] != pin:
            raise VoskError("%s does not match the digest pinned in this "
                            "module - refusing to unpack it" % pw["filename"])
        SITE.mkdir(parents=True, exist_ok=True)
        if pw["kind"] == "wheel":
            with zipfile.ZipFile(dest) as z:
                z.extractall(SITE)
            members = ["<wheel>"]
        else:
            members = _extract_module_from_sdist(name, dest)
        rows.append({"dep": name, "version": pw["version"],
                     "dist_kind": pw["kind"], "filename": pw["filename"],
                     "sha256": got["sha256"], "sha256_verified": True,
                     "bytes": got["bytes"], "extracted": members,
                     "executed_setup_py": False,
                     "why": "imported at module level by vosk/__init__.py"})
    return rows


def provision(*, force: bool = False) -> dict:
    """Fetch + verify + unpack the wheel and the model. Idempotent.

    The wheel is checked against PyPI's published sha256 BEFORE it is unpacked:
    an unpacked archive is code, and code that was not verified is code from
    nobody in particular.
    """
    rec: dict[str, Any] = {"wire": WIRE, "vendor": str(VENDOR)}
    VENDOR.mkdir(parents=True, exist_ok=True)

    pypi = _pypi_wheel()
    wheel = VENDOR / WHEEL_NAME
    if force or not wheel.is_file():
        got = _download(pypi["url"], wheel)
    else:
        got = {"url": pypi["url"], "http": 0, "bytes": wheel.stat().st_size,
               "ms": 0.0, "sha256": sha256_of(wheel), "cached": True}
    verified = bool(pypi["published_sha256"]
                    and got["sha256"] == pypi["published_sha256"])
    pinned_ok = got["sha256"] == WHEEL_SHA256
    rec["wheel"] = {**got, "published_sha256": pypi["published_sha256"],
                    "pinned_sha256": WHEEL_SHA256,
                    "sha256_verified": verified,
                    "matches_pin": pinned_ok,
                    "requires_dist": pypi["requires_dist"]}
    if not verified:
        raise VoskError("wheel sha256 does not match PyPI's published digest "
                        "- refusing to unpack it")
    if not pinned_ok:
        raise VoskError("wheel sha256 does not match the digest pinned in "
                        "this module - upstream changed under the pin; "
                        "refusing to unpack it")

    if force and SITE.is_dir():
        shutil.rmtree(SITE)
    if not (SITE / "vosk" / "__init__.py").is_file():
        SITE.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(wheel) as z:
            z.extractall(SITE)
    rec["deps"] = _provision_deps(force=force)
    rec["site"] = {"path": str(SITE),
                   "has_package": (SITE / "vosk" / "__init__.py").is_file(),
                   "libs": sorted(p.name for p in SITE.rglob("*.dll"))[:8]}

    model_dir = MODELS / MODEL_NAME
    zip_path = MODELS / (MODEL_NAME + ".zip")
    if force or not zip_path.is_file():
        mgot = _download(MODEL_URL, zip_path)
    else:
        mgot = {"url": MODEL_URL, "http": 0, "bytes": zip_path.stat().st_size,
                "ms": 0.0, "sha256": sha256_of(zip_path), "cached": True}
    if mgot["sha256"] != MODEL_SHA256:
        raise VoskError("model zip sha256 does not match the digest pinned in "
                        "this module - refusing to unpack it")
    if force and model_dir.is_dir():
        shutil.rmtree(model_dir)
    if not model_dir.is_dir():
        with zipfile.ZipFile(zip_path) as z:
            z.extractall(MODELS)
    rec["model"] = {**mgot, "name": MODEL_NAME, "dir": str(model_dir),
                    "pinned_sha256": MODEL_SHA256, "matches_pin": True,
                    "unpacked": model_dir.is_dir(),
                    "markers_present": sorted(
                        m for m in MODEL_MARKERS if (model_dir / m).exists()),
                    "note": "upstream publishes no digest; the sha256 above is "
                            "what THIS box downloaded, pinned so a swap shows"}
    rec["ok"] = bool(rec["site"]["has_package"] and model_dir.is_dir())
    return rec


def verify_pins() -> dict:
    """Re-hash what is on disk against the pins. No network, no import.

    This is the check that survives a fresh clone: `vendor/` is git-ignored, so
    the repo carries the expected digests and nothing else. Anything that does
    not match is named, and `ok` is False - never a warning.
    """
    rows: dict[str, Any] = {}
    for label, path, pin in (
            ("wheel", VENDOR / WHEEL_NAME, WHEEL_SHA256),
            ("model_zip", MODELS / (MODEL_NAME + ".zip"), MODEL_SHA256),
            *[("dep:" + fn, VENDOR / fn, sha)
              for fn, sha in DEP_SHA256.items()]):
        if not path.is_file():
            rows[label] = {"present": False, "pinned_sha256": pin,
                           "ok": False, "why": "not provisioned"}
            continue
        got = sha256_of(path)
        rows[label] = {"present": True, "sha256": got, "pinned_sha256": pin,
                       "ok": got == pin,
                       "bytes": path.stat().st_size}
    return {"ok": all(r["ok"] for r in rows.values()), "files": rows}


def provisioned() -> dict:
    """What is on disk right now. No network, no import, no side effects."""
    model_dir = MODELS / MODEL_NAME
    return {
        "site": (SITE / "vosk" / "__init__.py").is_file(),
        "deps": {n: ((SITE / (n + ".py")).is_file()
                     or (SITE / n / "__init__.py").is_file())
                 for n in PURE_DEPS},
        "model_dir": model_dir.is_dir(),
        "model_markers": sorted(m for m in MODEL_MARKERS
                                if (model_dir / m).exists()),
        "wheel": (VENDOR / WHEEL_NAME).is_file(),
        "model_path": str(model_dir),
    }


# ---------------------------------------------------------------------------
# binding — explicit, process-local, never a global arm
# ---------------------------------------------------------------------------
def bind(*, set_env: bool = True) -> dict:
    """Make the vendored vosk importable IN THIS PROCESS ONLY.

    `set_env` also sets `COSMOS_VOSK_MODEL`, which is what
    `cosmos_cvm_push.probe_stt` reads. Both effects die with the process - this
    function does not write the registry, the tree, or a user environment
    variable, so nothing outside this run changes engine.
    """
    st = provisioned()
    if not st["site"]:
        raise VoskError("vosk is not provisioned: run --provision")
    if not st["model_dir"]:
        raise VoskError("model %s is not provisioned: run --provision"
                        % MODEL_NAME)
    missing = [n for n, ok in st["deps"].items() if not ok]
    if missing:
        raise VoskError("vosk's module-level imports are unsatisfied (%s): "
                        "run --provision" % ", ".join(missing))
    if str(SITE) not in sys.path:
        sys.path.insert(0, str(SITE))
    if set_env:
        os.environ["COSMOS_VOSK_MODEL"] = st["model_path"]
    t0 = time.perf_counter()
    import vosk                                                # noqa: F401
    return {"bound": True, "import_ms": round(
        (time.perf_counter() - t0) * 1000.0, 3),
        "version": getattr(vosk, "__version__", None),
        "model_path": st["model_path"],
        "site": str(SITE),
        "env_set": bool(set_env)}


class ResidentVoskEar:
    """VOSK with the model AND the recognizer held across turns.

    Same surface as `cvm_dt_stt.SapiTranscriber` (`accept` / `finish` /
    `transcribe` / `recognize_pcm`), so `vad_interrupt`'s incremental sink and
    `default_ear()` take it unchanged.

    Why it exists, in numbers this box emitted (`F21_STT_LOCAL.json`, one
    1.979 s SAPI-TTS fixture):

        Model() + KaldiRecognizer() inside the call   1045.3 ms  <- shipped
        KaldiRecognizer() per call, model resident     693.8 ms
        model AND recognizer resident, Reset() between  60.1 ms  <- this class
        on-box SAPI, same PCM                          205.8 ms

    Constructing a `KaldiRecognizer` does not merely allocate: the first
    `AcceptWaveform` on a fresh one costs 569 ms against 60 ms on a reset one,
    every time, so the cost is paid per utterance and never amortizes. That is
    a 17x difference between two designs of the same engine on the same audio -
    which is why `cosmos_cvm_push.transcribe_pcm`'s per-call `Model(model)` is
    called out in `arm_line()` rather than left as an implementation detail.

    First construction is lazy and slow (model load ~399 ms); it happens on the
    first `transcribe`, not at import, so nothing pays for an ear it never uses.
    """

    def __init__(self, model_path: Optional[str] = None,
                 rate: int = STT_RATE):
        self.model_path = model_path or provisioned()["model_path"]
        self.rate = int(rate) or STT_RATE
        self._model = None
        self._rec = None
        self._buf = bytearray()
        self.load_ms: Optional[float] = None

    def _ensure(self):
        if self._rec is not None:
            return
        bind(set_env=False)
        from vosk import KaldiRecognizer, Model, SetLogLevel
        SetLogLevel(-1)
        t0 = time.perf_counter()
        self._model = Model(self.model_path)
        self._rec = KaldiRecognizer(self._model, self.rate)
        self.load_ms = round((time.perf_counter() - t0) * 1000.0, 3)

    # --- incremental sink (vad_interrupt) ---------------------------------
    def accept(self, chunk: bytes) -> None:
        self._buf += bytes(chunk or b"")

    def finish(self) -> dict:
        pcm, self._buf = bytes(self._buf), bytearray()
        return self.transcribe(pcm, self.rate)

    # --- one-shot ---------------------------------------------------------
    def transcribe(self, pcm: bytes, rate: int = STT_RATE) -> dict:
        """One utterance. An empty transcript is STT_NONE, never a guess."""
        rate = int(rate) or STT_RATE
        if rate != self.rate:
            from cvm_dt_voice import resample_pcm16_mono
            pcm = resample_pcm16_mono(pcm, rate, self.rate)
        self._ensure()
        t0 = time.perf_counter()
        self._rec.Reset()
        self._rec.AcceptWaveform(pcm or b"")
        try:
            got = json.loads(self._rec.FinalResult() or "{}")
        except ValueError:
            got = {}
        text = str(got.get("text") or "").strip()
        return {"transcript": text, "engine": "vosk", "model": MODEL_NAME,
                "ear_ms": round((time.perf_counter() - t0) * 1000.0, 3),
                "rate": self.rate, "resident": True,
                "model_load_ms": self.load_ms,
                "kind": "ok" if text else "STT_NONE"}

    def recognize_pcm(self, pcm: bytes, rate: int = STT_RATE) -> dict:
        """Alias for the SapiTranscriber name, so callers need no branch."""
        return self.transcribe(pcm, rate)


def arm_line() -> dict:
    """What ARMING this system-wide would take. Emitted, never executed.

    Same discipline as `cvm_dt_clock --register`: the line that would change
    the live system is printed for the Orchestrator, not run by the worker.
    """
    st = provisioned()
    return {
        "ran": False,
        "why": "arming flips the phone fold from the SAPI second-tier ear "
               "(A2) to VOSK, and swaps which engine every desktop turn uses. "
               "That is an Orchestrator decision, not a side effect of a "
               "download.",
        "requires": [
            "COSMOS_VOSK_MODEL=%s (user or machine environment)"
            % st["model_path"],
            "%s on sys.path for the processes that should hear with VOSK "
            "(e.g. a .pth in site-packages, or PYTHONPATH)" % SITE,
        ],
        "then": "probe_stt() flips to {ok: true, engine: vosk} and "
                "cvm_dt_stt.probe_ear() prefers VOSK over SAPI on its own",
        "caution": "cosmos_cvm_push.transcribe_pcm builds Model(model) INSIDE "
                   "the per-utterance call, so arming as-is pays the model "
                   "load on every phone utterance - see F21_STT_LOCAL.json "
                   "model_load_ms",
    }


# ---------------------------------------------------------------------------
# measurement
# ---------------------------------------------------------------------------
def _fixture(phrase: str) -> dict:
    """Speak the phrase with the on-box mouth and hand back 16k PCM16 mono.

    Same source the bench uses (`stt_fixture.source = "sapi_tts"`), so the
    VOSK number and the SAPI number are taken on the SAME audio. Comparing two
    engines on two different recordings measures the recordings.
    """
    from cvm_dt import _sapi_wav
    from cvm_dt_voice import resample_pcm16_mono
    from cvm_dt_stt import wav_to_pcm
    pcm, rate = wav_to_pcm(_sapi_wav(phrase))
    if rate != STT_RATE:
        pcm = resample_pcm16_mono(pcm, rate, STT_RATE)
    return {"phrase": phrase, "pcm": pcm, "rate": STT_RATE,
            "bytes": len(pcm), "source_rate": rate, "source": "sapi_tts",
            "seconds": round(len(pcm) / 2.0 / STT_RATE, 3)}


def recall(spoken: str, heard: str) -> float:
    want = set(str(spoken).lower().split())
    got = set(str(heard).lower().split())
    return round(len(want & got) / max(1, len(want)), 3)


def measure(phrase: str, *, reps: int = 3) -> dict:
    """Model LOAD and model INFERENCE, separately, then SAPI on the same PCM.

    They are separated because `cosmos_cvm_push.transcribe_pcm` conflates them:
    it constructs `Model(model)` inside the per-utterance call, so its `ear_ms`
    is load + inference every single time. A resident model is the whole
    difference between "215 ms" and "a second and a half", and the artifact has
    to show which one the shipped path would actually pay.
    """
    b = bind()
    from vosk import KaldiRecognizer, Model, SetLogLevel
    SetLogLevel(-1)

    fx = _fixture(phrase)
    pcm = fx["pcm"]

    t0 = time.perf_counter()
    model = Model(b["model_path"])
    load_ms = round((time.perf_counter() - t0) * 1000.0, 3)

    # Three costs hide inside one "inference" number, and they are paid by
    # different designs: building the recognizer (per utterance in the shipped
    # `transcribe_pcm`), decoding the audio, and - only if the recognizer is
    # kept - Reset() between turns. A single total would let a 700 ms
    # constructor masquerade as slow decoding and condemn the wrong engine.
    infer: list[float] = []
    build: list[float] = []
    decode: list[float] = []
    heard = ""
    for _ in range(max(1, int(reps))):
        t = time.perf_counter()
        rec = KaldiRecognizer(model, STT_RATE)
        t_built = time.perf_counter()
        rec.AcceptWaveform(pcm)
        try:
            got = json.loads(rec.FinalResult() or "{}")
        except ValueError:
            got = {}
        t_done = time.perf_counter()
        build.append((t_built - t) * 1000.0)
        decode.append((t_done - t_built) * 1000.0)
        infer.append((t_done - t) * 1000.0)
        heard = str(got.get("text") or "").strip()

    # The resident arm: one recognizer, Reset() between turns. This is what a
    # streaming ear would actually pay per utterance.
    resident: dict[str, Any] = {"kind": "UNMEASURED",
                                "why": "KaldiRecognizer has no Reset()"}
    if hasattr(KaldiRecognizer, "Reset"):
        keep = KaldiRecognizer(model, STT_RATE)
        rows: list[float] = []
        kept_text = ""
        for _ in range(max(1, int(reps))):
            keep.Reset()
            t = time.perf_counter()
            keep.AcceptWaveform(pcm)
            try:
                g = json.loads(keep.FinalResult() or "{}")
            except ValueError:
                g = {}
            rows.append((time.perf_counter() - t) * 1000.0)
            kept_text = str(g.get("text") or "").strip()
        rows.sort()
        resident = {"kind": "ok", "n": len(rows),
                    "per_utterance_ms": round(rows[len(rows) // 2], 3),
                    "min_ms": round(rows[0], 3), "max_ms": round(rows[-1], 3),
                    "transcript": kept_text,
                    "word_recall": recall(phrase, kept_text),
                    "what": "one Model + one KaldiRecognizer held across turns, "
                            "Reset() between them - no load, no construction"}

    # What the SHIPPED path would pay: Model() rebuilt inside the call.
    t = time.perf_counter()
    rec = KaldiRecognizer(Model(b["model_path"]), STT_RATE)
    rec.AcceptWaveform(pcm)
    rec.FinalResult()
    cold_ms = round((time.perf_counter() - t) * 1000.0, 3)

    infer.sort()
    build.sort()
    decode.sort()
    vosk_row = {
        "engine": "vosk", "model": MODEL_NAME,
        "model_load_ms": load_ms,
        "recognizer_build_ms": round(build[len(build) // 2], 3),
        "decode_ms": round(decode[len(decode) // 2], 3),
        "resident": resident,
        "inference_ms": round(infer[len(infer) // 2], 3),
        "inference_min_ms": round(infer[0], 3),
        "inference_max_ms": round(infer[-1], 3),
        "n": len(infer),
        "cold_per_utterance_ms": cold_ms,
        "transcript": heard,
        "kind": "ok" if heard else "STT_NONE",
        "word_recall": recall(phrase, heard),
        "import_ms": b["import_ms"],
    }

    from cvm_dt_stt import SapiTranscriber, probe_sapi
    sp = probe_sapi()
    if sp.get("ok"):
        t = time.perf_counter()
        got = SapiTranscriber().recognize_pcm(pcm, STT_RATE)
        sapi_ms = round((time.perf_counter() - t) * 1000.0, 3)
        text = str(got.get("transcript") or "").strip()
        sapi_row = {"engine": "sapi", "recognizer": got.get("recognizer"),
                    "inference_ms": got.get("ear_ms", sapi_ms),
                    "wall_ms": sapi_ms, "transcript": text,
                    "kind": "ok" if text else "STT_NONE",
                    "word_recall": recall(phrase, text)}
    else:
        sapi_row = {"engine": "sapi", "kind": "UNMEASURED",
                    "why": sp.get("detail")}

    out = {
        "wire": WIRE,
        "fixture": {k: v for k, v in fx.items() if k != "pcm"},
        "vosk": vosk_row, "sapi": sapi_row,
    }
    if sapi_row.get("kind") in ("ok", "STT_NONE"):
        sapi_ref = float(sapi_row.get("inference_ms") or 0.0)
        best = vosk_row["resident"].get("per_utterance_ms")
        out["delta"] = {
            "inference_ms_vosk_minus_sapi": round(
                float(vosk_row["inference_ms"]) - sapi_ref, 3),
            "best_case_vosk_ms": best,
            "best_case_vosk_minus_sapi_ms": (
                round(float(best) - sapi_ref, 3) if best is not None else None),
            "faster_engine_on_this_box": (
                "sapi" if best is None or float(best) > sapi_ref else "vosk"),
            "recall_vosk_minus_sapi": round(
                vosk_row["word_recall"] - sapi_row.get("word_recall", 0.0), 3),
            "same_pcm": True,
            "caveat": "SYNTHESIZER IN. Both engines heard the same SAPI-TTS "
                      "fixture, which is a clean signal. Real-microphone "
                      "accuracy is UNMEASURED for both (CVM_BACKLOG B3) and "
                      "these numbers are an upper bound, not a prediction.",
        }
    return out


def run(phrase: str, *, reps: int, do_provision: bool,
        force: bool = False) -> dict:
    rec: dict[str, Any] = {
        "wire": WIRE, "feature": "F-21 local STT model inference",
        "iso": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "epoch": time.time(),
        "python": "%d.%d.%d" % sys.version_info[:3],
    }
    from cosmos_cvm_push import probe_stt
    rec["before"] = {"probe_stt": probe_stt(),
                     "provisioned": provisioned(),
                     "vosk_importable": _importable()}
    if do_provision:
        rec["provision"] = provision(force=force)
    # Always, provisioned this run or not: the artifact states what bytes the
    # measurement below actually ran against.
    rec["pins"] = verify_pins()
    if not rec["pins"]["ok"]:
        raise VoskError("provisioned bytes do not match the pinned digests: %s"
                        % json.dumps(rec["pins"]["files"]))
    rec["measure"] = measure(phrase, reps=reps)
    rec["after_in_this_process"] = {"probe_stt": probe_stt()}
    rec["arm"] = arm_line()
    v = rec["measure"]["vosk"]
    rec["ok"] = v["kind"] == "ok"
    rec["emitted"] = (
        "f21-vosk:%s:%s:%s ms load + %s ms build + %s ms decode "
        "(resident %s ms):recall %s:'%s'"
        % (MODEL_NAME, v["kind"], v["model_load_ms"],
           v["recognizer_build_ms"], v["decode_ms"],
           v["resident"].get("per_utterance_ms"), v["word_recall"],
           v["transcript"]))
    return rec


def _importable() -> bool:
    """Is `vosk` importable WITHOUT this module's bind()? (A2's gate depends
    on the answer staying False for anything that did not opt in.)"""
    import importlib.util
    saved = [p for p in sys.path if p == str(SITE)]
    for p in saved:
        sys.path.remove(p)
    try:
        return importlib.util.find_spec("vosk") is not None
    except (ImportError, ValueError):
        return False
    finally:
        sys.path[0:0] = saved


def write_artifact(rec: dict, out_dir: Optional[Path] = None) -> Path:
    path = (out_dir or _HERE) / ARTIFACT
    path.write_text(json.dumps(rec, indent=1, default=str), encoding="utf-8")
    return path


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(prog="cvm-stt-vosk")
    ap.add_argument("--provision", action="store_true",
                    help="fetch + verify + unpack the wheel and the model")
    ap.add_argument("--force", action="store_true",
                    help="re-download and re-unpack even if present")
    ap.add_argument("--measure", action="store_true",
                    help="measure model load, inference and SAPI on one PCM")
    ap.add_argument("--status", action="store_true",
                    help="what is on disk; no network, no import")
    ap.add_argument("--arm-line", action="store_true",
                    help="emit what arming vosk system-wide would require")
    ap.add_argument("--phrase", default="what is the queue depth")
    ap.add_argument("--reps", type=int, default=3)
    ap.add_argument("--no-write", action="store_true")
    ns = ap.parse_args(argv)

    if ns.status:
        print(json.dumps({"wire": WIRE, "provisioned": provisioned(),
                          "vosk_importable_without_bind": _importable()},
                         indent=1))
        return 0
    if ns.arm_line:
        print(json.dumps(arm_line(), indent=1))
        return 0
    if not (ns.provision or ns.measure):
        ap.error("one of --provision / --measure / --status / --arm-line")

    if ns.provision and not ns.measure:
        rec = {"wire": WIRE, "provision": provision(force=ns.force),
               "provisioned": provisioned()}
        print(json.dumps(rec, indent=1, default=str))
        return 0

    rec = run(ns.phrase, reps=ns.reps, do_provision=ns.provision,
              force=ns.force)
    if not ns.no_write:
        rec["artifact"] = str(write_artifact(rec))
    print(json.dumps(rec, indent=1, default=str))
    return 0 if rec.get("ok") else 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except VoskError as e:
        print(json.dumps({"ok": False, "kind": "VOSK_REFUSED",
                          "detail": str(e)}, indent=1), file=sys.stderr)
        raise SystemExit(2)
