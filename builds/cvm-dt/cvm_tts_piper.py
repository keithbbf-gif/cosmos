#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B4 — desktop Piper mouth, same voice family as the phone.

`docs/CVM_ARCH.md` §6.3 names the DT mouth: *"TTS: Piper locally (same voice
family as the phone) so desk and road sound like one assistant."* Shipped
until this file was SAPI → WAV → WASAPI, and `test_cvm_dt_contracts.py`
asserted `"piper" not in src` — the contract pinned the gap.

The phone's mouth is not a guess. `TtsModelManager.kt` pins
`vits-piper-en_US-amy-low-int8` / `en_US-amy-low.onnx` (sherpa-onnx OfflineTts).
Desktop `piper-tts` loads the rhasspy `en_US-amy-low` VITS of the same speaker
and quality tier. Quantization differs (APK int8 vs rhasspy fp32); the voice
*id* is the same string. `kdash/mobile.html` still uses the handset default
and cannot be matched from the desktop — that is B4's named limit, not a
regression of this slice.

Discipline, identical to `cvm_stt_whisper.py`:

* **Provisioning arms nothing.** Wheels land in `vendor/piper_site` (a THIRD
  import root, not the VOSK or whisper one). Voice files land in
  `vendor/piper_voices/en_US-amy-low/`. Neither is on anyone else's `sys.path`.
* **`--only-binary=:all:`** — no `setup.py` from the network.
* **pip's own install report is the pin** for wheels. Voice files are
  sha256-pinned in this source after the first verified fetch.
* SAPI stays the **floor**. `CvmDt.speak` tries Piper when `ready()` and
  falls back to `_sapi_wav` on any typed refusal.

    py -3.14 builds\\cvm-dt\\cvm_tts_piper.py --provision
    py -3.14 builds\\cvm-dt\\cvm_tts_piper.py --say "status report"
    py -3.14 builds\\cvm-dt\\test_cvm_tts_piper.py

Artifact: `builds/cvm-dt/B4_TTS_PIPER.json` (`schema cvm-dt-tts-piper/1`).
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.request
import wave
from pathlib import Path
from typing import Optional

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

WIRE = "cvm-dt-tts-piper/1"
ARTIFACT = "B4_TTS_PIPER.json"

VENDOR = _HERE / "vendor"
SITE = VENDOR / "piper_site"
VOICES = VENDOR / "piper_voices"
REPORT = SITE / "_pip_report.json"

# Same speaker id the APK loads (`TtsModelManager.MODEL_FILE` = en_US-amy-low.onnx).
VOICE_ID = "en_US-amy-low"
ONNX_NAME = VOICE_ID + ".onnx"
JSON_NAME = VOICE_ID + ".onnx.json"
VOICE_DIR = VOICES / VOICE_ID
ONNX_PATH = VOICE_DIR / ONNX_NAME
JSON_PATH = VOICE_DIR / JSON_NAME

# rhasspy piper-voices v1.0.0 — stable tag, not floating `main`.
VOICE_BASE = ("https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0"
              "/en/en_US/amy/low/")
ONNX_URL = VOICE_BASE + ONNX_NAME
JSON_URL = VOICE_BASE + JSON_NAME

# rhasspy/piper-voices v1.0.0 en_US-amy-low — hashed on this box 2026-08-31
# after the first fetch (onnx 63,104,526 bytes). Subsequent runs fail-closed.
ONNX_SHA256 = "a5a91abb7de0f104358a25aded480ddacf1ff0762886325886ec406a2e86aab3"
JSON_SHA256 = "2250a9a605b8dc35a116717fadc5056695dd809e34a15d02f72a0f52d53d3ebb"

REQUIREMENT = "piper-tts"
PIP_TIMEOUT_S = 900.0
NET_TIMEOUT_S = 300.0
SAY_TIMEOUT_S = 60.0

PHONE_VOICE = {
    "apk_model_dir": "vits-piper-en_US-amy-low-int8",
    "apk_model_file": "en_US-amy-low.onnx",
    "apk_archive_sha256":
        "93070ac9fadf512e56c46bdd0c5d2ce96b424fdc4e683d560167410bd2c4df7d",
    "source": "V:/Ai/tmp/cosmos-android/app/src/main/java/com/cosmos/voice/TtsModelManager.kt",
}


class PiperError(RuntimeError):
    def __init__(self, kind: str, detail: str = ""):
        super().__init__("[%s] %s" % (kind, detail))
        self.kind = kind
        self.detail = detail


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
    req = urllib.request.Request(url, headers={"User-Agent": "cosmos-cvm-dt/b4"})
    with urllib.request.urlopen(req, timeout=NET_TIMEOUT_S) as r:
        status = int(getattr(r, "status", 0) or 0)
        with open(tmp, "wb") as f:
            shutil.copyfileobj(r, f, 1 << 20)
    tmp.replace(dest)
    return {"url": url, "http": status, "bytes": dest.stat().st_size,
            "ms": round((time.perf_counter() - t0) * 1000.0, 1),
            "sha256": sha256_of(dest)}


def _check_pin(got: dict, pin: str, label: str) -> dict:
    rec = dict(got)
    rec["pinned_sha256"] = pin or None
    if pin:
        if got["sha256"] != pin:
            raise PiperError("SHA256_MISMATCH",
                             "%s got %s pinned %s" % (label, got["sha256"], pin))
        rec["sha256_verified"] = True
    else:
        rec["sha256_verified"] = False
        rec["note"] = "first fetch; pin this digest in source before re-running"
    return rec


# --------------------------------------------------------------------------
# provisioning — arms nothing
# --------------------------------------------------------------------------

def provision(*, force: bool = False, requirement: str = REQUIREMENT) -> dict:
    SITE.mkdir(parents=True, exist_ok=True)
    VOICE_DIR.mkdir(parents=True, exist_ok=True)
    rec: dict = {"ok": True, "requirement": requirement, "target": str(SITE),
                 "voice_dir": str(VOICE_DIR), "voice_id": VOICE_ID,
                 "phone": PHONE_VOICE, "only_binary": True}

    if REPORT.is_file() and not force:
        pip = json.loads(REPORT.read_text(encoding="utf-8"))
        pip["reused"] = True
        rec["pip"] = pip
    else:
        t0 = time.perf_counter()
        out = SITE / "_pip_report.raw.json"
        argv = [sys.executable, "-m", "pip", "install",
                "--target", str(SITE),
                "--only-binary", ":all:",
                "--no-input", "--disable-pip-version-check",
                "--report", str(out), requirement]
        r = subprocess.run(argv, capture_output=True, text=True,
                           timeout=PIP_TIMEOUT_S)
        if r.returncode != 0 or not out.is_file():
            raise PiperError("PIP_FAILED", "rc=%s %s" % (
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
        pip = {"ok": True, "requirement": requirement, "target": str(SITE),
               "pip_report_version": raw.get("version"),
               "installed": sorted(installed, key=lambda d: (d["name"] or "")),
               "package_count": len(installed),
               "elapsed_ms": round((time.perf_counter() - t0) * 1000.0, 1),
               "only_binary": True, "reused": False}
        REPORT.write_text(json.dumps(pip, indent=1), encoding="utf-8")
        rec["pip"] = pip

    rec["onnx"] = _fetch_voice_file(ONNX_PATH, ONNX_URL, ONNX_SHA256, "onnx",
                                    force=force)
    rec["json"] = _fetch_voice_file(JSON_PATH, JSON_URL, JSON_SHA256, "json",
                                    force=force)
    rec["ready"] = ready()
    rec["iso"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    return rec


def _fetch_voice_file(dest: Path, url: str, pin: str, label: str,
                      *, force: bool) -> dict:
    if dest.is_file() and not force:
        got = {"url": url, "bytes": dest.stat().st_size, "ms": 0.0,
               "sha256": sha256_of(dest), "cached": True}
        return _check_pin(got, pin, label)
    got = _download(url, dest)
    got["cached"] = False
    return _check_pin(got, pin, label)


def provisioned() -> dict:
    rec = {"site": SITE.is_dir(), "report": REPORT.is_file(),
           "voice_dir": VOICE_DIR.is_dir(), "onnx": ONNX_PATH.is_file(),
           "json": JSON_PATH.is_file(), "site_path": str(SITE),
           "voice_path": str(VOICE_DIR), "ready": ready()}
    if rec["report"]:
        r = json.loads(REPORT.read_text(encoding="utf-8"))
        rec["packages"] = [{"name": d["name"], "version": d["version"],
                            "sha256": d.get("sha256")} for d in r["installed"]]
        rec["package_count"] = r.get("package_count")
        rec["unpinned"] = [d["name"] for d in r["installed"]
                           if not d.get("sha256")]
        rec["only_binary"] = r.get("only_binary")
    if rec["onnx"]:
        rec["onnx_sha256"] = sha256_of(ONNX_PATH)
        rec["onnx_bytes"] = ONNX_PATH.stat().st_size
        rec["onnx_matches_pin"] = (bool(ONNX_SHA256)
                                   and rec["onnx_sha256"] == ONNX_SHA256)
    if rec["json"]:
        rec["json_sha256"] = sha256_of(JSON_PATH)
        rec["json_bytes"] = JSON_PATH.stat().st_size
        rec["json_matches_pin"] = (bool(JSON_SHA256)
                                   and rec["json_sha256"] == JSON_SHA256)
    return rec


def ready(voice_dir: Optional[Path] = None) -> bool:
    """Files on disk. Does not import piper. Does not arm anyone."""
    d = Path(voice_dir) if voice_dir is not None else VOICE_DIR
    return (d / ONNX_NAME).is_file() and (d / JSON_NAME).is_file()


def bind(*, site: Optional[Path] = None) -> dict:
    """Put THIS process on the private root and import. Arms nothing else."""
    root = Path(site) if site is not None else SITE
    if not root.is_dir():
        raise PiperError("NOT_PROVISIONED",
                         "%s does not exist; run --provision" % root)
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    t0 = time.perf_counter()
    try:
        import piper  # noqa: F401
    except Exception as e:                                        # noqa: BLE001
        raise PiperError("IMPORT_FAILED",
                         "%s: %s" % (type(e).__name__, e)) from e
    return {"bound": True,
            "import_ms": round((time.perf_counter() - t0) * 1000.0, 3),
            "piper": getattr(piper, "__version__", None),
            "site": str(root)}


_VOICE = None
_VOICE_PATH = None


def _load_cls():
    try:
        from piper import PiperVoice
        return PiperVoice
    except ImportError:
        from piper.voice import PiperVoice
        return PiperVoice


def resident(onnx_path: Optional[Path] = None):
    """Hold the voice across calls — first load is the expensive one."""
    global _VOICE, _VOICE_PATH
    path = Path(onnx_path) if onnx_path is not None else ONNX_PATH
    if not path.is_file():
        raise PiperError("VOICE_NONE", "onnx missing at %s" % path)
    if _VOICE is not None and _VOICE_PATH == path:
        return _VOICE
    bind()
    t0 = time.perf_counter()
    cls = _load_cls()
    _VOICE = cls.load(str(path))
    _VOICE_PATH = path
    _VOICE._cosmos_load_ms = round((time.perf_counter() - t0) * 1000.0, 3)
    return _VOICE


def synthesize_wav(text: str, *, onnx_path: Optional[Path] = None) -> bytes:
    """Return a PCM WAV. Typed refusal, never an empty buffer."""
    text = (text or "").strip()
    if not text:
        raise PiperError("EMPTY_TEXT", "nothing to say")
    path = Path(onnx_path) if onnx_path is not None else ONNX_PATH
    if not ready(path.parent):
        raise PiperError("PIPER_NONE", "voice files not on disk at %s" % path.parent)
    voice = resident(path)
    t0 = time.perf_counter()
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        if hasattr(voice, "synthesize_wav"):
            voice.synthesize_wav(text, wf)
        else:
            chunks = []
            for c in voice.synthesize(text):
                audio = getattr(c, "audio_int16_bytes", None)
                if audio is None:
                    audio = bytes(getattr(c, "audio_int16", b""))
                chunks.append(audio)
            cfg = getattr(voice, "config", None)
            rate = int(getattr(cfg, "sample_rate", 22050) or 22050)
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(rate)
            wf.writeframes(b"".join(chunks))
    data = buf.getvalue()
    if len(data) < 44 or data[:4] != b"RIFF":
        raise PiperError("TTS_NONE", "piper wrote a non-WAV (%d bytes)" % len(data))
    return data


def wav_info(data: bytes) -> dict:
    if len(data) < 44 or data[:4] != b"RIFF":
        raise PiperError("NOT_WAV", "len=%s head=%r" % (len(data), data[:4]))
    with wave.open(io.BytesIO(data), "rb") as wf:
        return {"bytes": len(data), "channels": wf.getnchannels(),
                "rate": wf.getframerate(), "bits": wf.getsampwidth() * 8}


def arm_line() -> dict:
    """Emit the env a process would need. Does not run it."""
    site = str(SITE)
    onnx = str(ONNX_PATH)
    return {
        "ran": False,
        "voice_id": VOICE_ID,
        "sys_path_insert": site,
        "env": {"COSMOS_PIPER_VOICE": onnx},
        "note": ("Provisioning does not arm CvmDt.speak. ready() becomes true "
                 "when the onnx+json exist; speak() then tries Piper and "
                 "falls back to SAPI on any typed refusal."),
    }


def say(text: str) -> dict:
    t0 = time.perf_counter()
    wav = synthesize_wav(text)
    info = wav_info(wav)
    load_ms = getattr(_VOICE, "_cosmos_load_ms", None) if _VOICE is not None else None
    return {
        "ok": True, "engine": "piper", "voice_id": VOICE_ID,
        "text": text, "wav": info,
        "synth_ms": round((time.perf_counter() - t0) * 1000.0, 3),
        "load_ms": load_ms,
        "phone_voice_file": PHONE_VOICE["apk_model_file"],
        "same_voice_id": VOICE_ID + ".onnx" == PHONE_VOICE["apk_model_file"],
    }


def measure(text: str = "status report") -> dict:
    rec = {"wire": WIRE, "voice_id": VOICE_ID, "phone": PHONE_VOICE,
           "provisioned": provisioned(), "arm": arm_line()}
    rec["say"] = say(text)            # cold: includes model load
    rec["say_warm"] = say(text)       # resident voice; this is per-utterance
    rec["iso"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    rec["emitted"] = "piper:%s:%sHz:%dB:warm_ms=%s" % (
        VOICE_ID, rec["say"]["wav"]["rate"], rec["say"]["wav"]["bytes"],
        rec["say_warm"]["synth_ms"])
    return rec


def _write_artifact(rec: dict) -> Path:
    p = _HERE / ARTIFACT
    p.write_text(json.dumps(rec, indent=1), encoding="utf-8")
    rec["proof_path"] = str(p)
    return p


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--provision", action="store_true")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--say", default="", help="synthesize one phrase, write artifact")
    ap.add_argument("--measure", action="store_true")
    args = ap.parse_args(argv)
    if args.provision:
        rec = provision(force=args.force)
        _write_artifact({"wire": WIRE, "kind": "provision", **rec})
        print(json.dumps({"ok": rec.get("ok"), "ready": rec.get("ready"),
                          "pip_packages": (rec.get("pip") or {}).get("package_count"),
                          "onnx_sha256": (rec.get("onnx") or {}).get("sha256"),
                          "json_sha256": (rec.get("json") or {}).get("sha256"),
                          "onnx_bytes": (rec.get("onnx") or {}).get("bytes"),
                          "proof": str(_HERE / ARTIFACT)}, indent=1))
        return 0 if rec.get("ok") and rec.get("ready") else 1
    if args.measure or args.say:
        rec = measure(args.say or "status report")
        _write_artifact(rec)
        print(json.dumps({"ok": rec["say"]["ok"], "emitted": rec["emitted"],
                          "synth_ms": rec["say"]["synth_ms"],
                          "wav": rec["say"]["wav"],
                          "proof": str(_HERE / ARTIFACT)}, indent=1))
        return 0
    print(json.dumps({"ready": ready(), "provisioned": provisioned(),
                      "arm": arm_line(), "voice_id": VOICE_ID}, indent=1))
    return 0 if ready() else 2


if __name__ == "__main__":
    sys.exit(main())
