#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest: F-21 local STT (cosmos_stt + cosmos_cvm_push.probe_stt).

Hermetic: missing vendor site is STT_NONE; missing model is NO_MODEL;
empty PCM is STT_NONE (never a fabricated word). Live: vendor site on
this tree makes vosk importable and probe() ok when the provisioned
model dir exists.

Does not write kernel/ledger/sched/service. Does not write builds/cvm-dt/.
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "cosmos"))

from cosmos_stt import (  # noqa: E402
    SCHEMA, STT_RATE, SttError, probe, provisioned_model, transcribe,
    vendor_site, wav_to_pcm,
)
from cosmos_cvm_push import probe_stt, transcribe_pcm  # noqa: E402

RESULTS = []


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:  # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


def main() -> int:
    check("schema is cosmos-stt/1", lambda: SCHEMA == "cosmos-stt/1")
    rel = vendor_site(REPO)
    check("vendor_site is repo-relative under builds/cvm-dt/vendor/site",
          lambda: rel == REPO / "builds" / "cvm-dt" / "vendor" / "site")

    # Hermetic: a repo with no vendor site / no model.
    fake = Path(tempfile.mkdtemp(prefix="cosmos_stt_absent_"))
    rec = probe(fake)
    check("absent vendor+model is not ok",
          lambda: rec.get("ok") is False
          and rec.get("kind") in ("STT_NONE", "NO_MODEL"))

    empty = transcribe(b"", repo=fake)
    check("empty PCM against absent ear is STT_NONE/NO_MODEL, transcript empty",
          lambda: empty.get("kind") in ("STT_NONE", "NO_MODEL")
          and empty.get("transcript") == "")

    # Live vendor on THIS tree.
    live = probe(REPO)
    site = vendor_site(REPO)
    model = provisioned_model(REPO)
    if site.is_dir() and model.is_dir():
        check("live vendor site + model: probe ok engine=vosk",
              lambda: live.get("ok") is True
              and live.get("engine") == "vosk"
              and live.get("kind") == "ok"
              and Path(live["model"]).is_dir())
        check("live vosk_file is under vendor/site",
              lambda: "vendor" in str(live.get("vosk_file") or "")
              and "site" in str(live.get("vosk_file") or ""))
        silence = transcribe(b"\x00\x00" * 1600, rate=STT_RATE, repo=REPO)
        check("silence decode does not fabricate a word",
              lambda: silence.get("transcript") == ""
              and silence.get("kind") == "STT_NONE"
              and silence.get("resident") is True)
        pushed = probe_stt()
        check("cosmos_cvm_push.probe_stt binds the provisioned model",
              lambda: pushed.get("ok") is True
              and pushed.get("engine") == "vosk"
              and Path(str(pushed.get("model") or "")).is_dir())
        rec_pcm = transcribe_pcm(b"\x00\x00" * 800, rate=STT_RATE,
                                 model=str(pushed["model"]))
        check("transcribe_pcm silence is STT_NONE empty transcript",
              lambda: rec_pcm.get("kind") == "STT_NONE"
              and rec_pcm.get("transcript") == "")
    else:
        check("live vendor site + model: probe ok engine=vosk",
              lambda: False)
        RESULTS[-1] = (RESULTS[-1][0], False,
                       f"site={site.is_dir()} model={model.is_dir()}")

    # wav_to_pcm refuses junk
    junk = Path(tempfile.mkdtemp(prefix="cosmos_stt_wav_")) / "x.wav"
    junk.write_bytes(b"not a wav")
    check("wav_to_pcm junk is BAD_WAV",
          lambda: _kind(lambda: wav_to_pcm(junk)) == "BAD_WAV")

    bad = [(l, e) for l, ok, e in RESULTS if not ok]
    for l, ok, e in RESULTS:
        print(("  OK  " if ok else "  FAIL") + f" {l}" + (f"  {e}" if e else ""))
    live_value = {
        "checks": len(RESULTS),
        "probe_ok": live.get("ok"),
        "probe_kind": live.get("kind"),
        "model": live.get("model"),
        "vosk_file": live.get("vosk_file"),
        "engine": live.get("engine"),
    }
    print("LIVE_VALUE", json.dumps(live_value))
    (REPO / "cosmos" / "_f21_stt.json").write_text(
        json.dumps({"ok": not bad, "schema": SCHEMA, "live_value": live_value},
                   indent=1) + "\n",
        encoding="utf-8")
    return 1 if bad else 0


def _kind(fn):
    try:
        fn()
    except SttError as e:
        return e.kind
    return None


if __name__ == "__main__":
    raise SystemExit(main())
