#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_stt - F-21 local STT model inference (VOSK, prepaid, on-box).

Default ``py -3.14 -c "import vosk"`` is ModuleNotFoundError. The wheel and
model already live under ``builds/cvm-dt/vendor/`` (F21_STT_LOCAL.json,
measured 2026-08-31T03:07). This module is the cosmos/ seam that:

  1. puts the vendor site on ``sys.path`` (repo-relative, no drive literal)
  2. binds ``COSMOS_VOSK_MODEL`` if set, else the provisioned model dir
  3. holds one Model + one KaldiRecognizer (Reset between turns) so a
     phone utterance does not pay model_load_ms every time
  4. never fabricates a word — empty decode is STT_NONE

Does not write kernel / ledger / sched / service. Does not write
``builds/cvm-dt/``. Arming CVM-DT's SAPI-vs-VOSK fold is still that
session's leftover (BLOCKED_ITEMS).

    py -3.14 cosmos\\cosmos_stt.py --probe
    py -3.14 cosmos\\cosmos_stt.py --once --wav <file.wav>
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import wave
from pathlib import Path

WORKER = "cosmos-stt"
SCHEMA = "cosmos-stt/1"
STT_RATE = 16000
VENDOR_SITE_REL = Path("builds") / "cvm-dt" / "vendor" / "site"
VENDOR_MODEL_REL = (
    Path("builds") / "cvm-dt" / "vendor" / "models" / "vosk-model-small-en-us-0.15"
)


class SttError(RuntimeError):
    """kind in {STT_NONE, NO_MODEL, BAD_WAV}."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


def repo_tree() -> Path:
    return Path(__file__).resolve().parent.parent


def vendor_site(repo: Path | None = None) -> Path:
    return (repo or repo_tree()) / VENDOR_SITE_REL


def provisioned_model(repo: Path | None = None) -> Path:
    env = (os.environ.get("COSMOS_VOSK_MODEL") or "").strip()
    if env:
        return Path(env)
    return (repo or repo_tree()) / VENDOR_MODEL_REL


def ensure_import(repo: Path | None = None) -> dict:
    """Make vosk importable from the vendor site. Never a drive literal."""
    site = vendor_site(repo)
    inserted = False
    if site.is_dir():
        s = str(site)
        if s not in sys.path:
            sys.path.insert(0, s)
            inserted = True
    try:
        import vosk  # noqa: F401
    except ImportError as e:
        raise SttError(
            "STT_NONE",
            f"vosk not importable ({e}); vendor site {site} "
            f"{'present' if site.is_dir() else 'absent'}",
        ) from e
    import vosk as _vosk
    return {
        "ok": True,
        "inserted": inserted,
        "site": str(site),
        "vosk_file": getattr(_vosk, "__file__", None),
    }


_ENGINE: dict | None = None


def _load_engine(model_dir: Path, rate: int) -> dict:
    global _ENGINE
    if (
        _ENGINE is not None
        and _ENGINE.get("model_dir") == str(model_dir)
        and int(_ENGINE.get("rate") or 0) == int(rate)
    ):
        return _ENGINE
    imp = ensure_import()
    from vosk import KaldiRecognizer, Model, SetLogLevel
    SetLogLevel(-1)
    t0 = time.perf_counter()
    model = Model(str(model_dir))
    load_ms = round((time.perf_counter() - t0) * 1000.0, 3)
    t1 = time.perf_counter()
    rec = KaldiRecognizer(model, int(rate) or STT_RATE)
    build_ms = round((time.perf_counter() - t1) * 1000.0, 3)
    _ENGINE = {
        "model": model,
        "rec": rec,
        "model_dir": str(model_dir),
        "rate": int(rate) or STT_RATE,
        "load_ms": load_ms,
        "build_ms": build_ms,
        "vosk_file": imp.get("vosk_file"),
    }
    return _ENGINE


def probe(repo: Path | None = None) -> dict:
    """Bind the ear. Missing vosk/model is STT_NONE, never a fabricated ok."""
    out = {
        "schema": SCHEMA,
        "ok": False,
        "engine": "vosk",
        "kind": "STT_NONE",
        "model": None,
        "detail": None,
        "vosk_file": None,
    }
    try:
        imp = ensure_import(repo)
    except SttError as e:
        out["kind"] = e.kind
        out["detail"] = str(e)
        return out
    model = provisioned_model(repo)
    out["vosk_file"] = imp.get("vosk_file")
    out["model"] = str(model)
    if not model.is_dir():
        out["kind"] = "NO_MODEL"
        out["detail"] = f"model dir missing: {model}"
        return out
    out["ok"] = True
    out["kind"] = "ok"
    out["detail"] = "vosk bound"
    return out


def transcribe(pcm: bytes, rate: int = STT_RATE, *, model: str | None = None,
               repo: Path | None = None) -> dict:
    """Resident VOSK. Empty text is STT_NONE, not a fabricated word."""
    t0 = time.perf_counter()
    probed = probe(repo)
    if not probed.get("ok"):
        return {
            "transcript": "",
            "engine": "vosk",
            "ear_ms": round((time.perf_counter() - t0) * 1000.0, 3),
            "rate": int(rate) or STT_RATE,
            "kind": probed.get("kind") or "STT_NONE",
            "detail": probed.get("detail"),
            "model": probed.get("model"),
        }
    model_dir = Path(model) if model else Path(probed["model"])
    if not model_dir.is_dir():
        return {
            "transcript": "",
            "engine": "vosk",
            "ear_ms": round((time.perf_counter() - t0) * 1000.0, 3),
            "rate": int(rate) or STT_RATE,
            "kind": "NO_MODEL",
            "detail": f"model dir missing: {model_dir}",
            "model": str(model_dir),
        }
    eng = _load_engine(model_dir, int(rate) or STT_RATE)
    rec = eng["rec"]
    rec.Reset()
    rec.AcceptWaveform(pcm or b"")
    try:
        got = json.loads(rec.FinalResult() or "{}")
    except ValueError:
        got = {}
    text = str(got.get("text") or "").strip()
    return {
        "transcript": text,
        "engine": "vosk",
        "ear_ms": round((time.perf_counter() - t0) * 1000.0, 3),
        "rate": int(rate) or STT_RATE,
        "kind": "ok" if text else "STT_NONE",
        "model": str(model_dir),
        "load_ms": eng.get("load_ms"),
        "build_ms": eng.get("build_ms"),
        "resident": True,
        "vosk_file": eng.get("vosk_file"),
    }


def wav_to_pcm(path: Path) -> tuple[bytes, int]:
    try:
        with wave.open(str(path), "rb") as wf:
            rate = wf.getframerate()
            nch = wf.getnchannels()
            sw = wf.getsampwidth()
            frames = wf.readframes(wf.getnframes())
    except (OSError, wave.Error) as e:
        raise SttError("BAD_WAV", f"{path}: {e}") from e
    if sw != 2:
        raise SttError("BAD_WAV", f"{path}: sample width {sw} (want 16-bit)")
    if nch != 1:
        # downmix stereo by taking left
        if nch != 2:
            raise SttError("BAD_WAV", f"{path}: channels {nch}")
        out = bytearray()
        for i in range(0, len(frames), 4):
            out.extend(frames[i:i + 2])
        frames = bytes(out)
    if rate != STT_RATE:
        # nearest-neighbour resample to 16 kHz (good enough for a fixture)
        import array
        src = array.array("h")
        src.frombytes(frames)
        n = int(len(src) * STT_RATE / float(rate))
        dst = array.array("h", (src[int(i * rate / STT_RATE)] for i in range(n)))
        frames = dst.tobytes()
        rate = STT_RATE
    return frames, rate


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="cosmos_stt")
    ap.add_argument("--probe", action="store_true")
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--wav", type=str, default="")
    ap.add_argument("--out", type=str, default="")
    args = ap.parse_args(argv)
    if args.once and args.wav:
        pcm, rate = wav_to_pcm(Path(args.wav))
        rec = transcribe(pcm, rate)
    else:
        rec = probe()
    rec["schema"] = SCHEMA
    rec["worker"] = WORKER
    text = json.dumps(rec, indent=1) + "\n"
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
    sys.stdout.write(text)
    return 0 if rec.get("ok") or rec.get("kind") in ("ok",) else 2


if __name__ == "__main__":
    raise SystemExit(main())
