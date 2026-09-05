#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Run the NEW B1 scenario against the PRE-EDIT code and show it fails.

`old_path_is_deaf_STT_NONE` inside test_cvm_phone_ear.py measures
`stt_interrupt` directly. This goes one level up and drives the pre-edit
`DesktopPullClock.on_speech` itself — the exact function that changed —
from the staged copy under `_delme/predispose_b1_ear_*/`, on bytes produced
the same way. If the new checks did not depend on the change, this would
also come back "ok".

    py -3.14 builds\\cvm-dt\\_disposal\\b1_old_code_proof.py
"""
from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
FENCE = HERE.parent
staged = sorted((FENCE / "_delme").glob("predispose_b1_ear_*"))
if not staged:
    raise SystemExit("no staged pre-edit copy under _delme/")
OLD = staged[-1]

# The staged dir FIRST so `cvm_pull` / `cvm_dt_stt` resolve to the old files;
# the fence second so cvm_dt / cvm_test_guard still resolve.
sys.path.insert(0, str(FENCE))
sys.path.insert(0, str(FENCE.parent.parent / "cosmos"))
sys.path.insert(0, str(OLD))

import cvm_pull  # noqa: E402
import cvm_dt_stt  # noqa: E402
from cosmos_paths import CosmosPaths, write_sentinel  # noqa: E402
from cosmos_cvm_push import phone_state, reset_voice_ack, stamp_desktop_pull  # noqa: E402
from cvm_dt import CoreClient, _sapi_wav  # noqa: E402

TREE_ID = "KMesh-COSMOS-live"
PHRASE = "open the status report"

assert Path(cvm_pull.__file__).parent == OLD, cvm_pull.__file__
assert Path(cvm_dt_stt.__file__).parent == OLD, cvm_dt_stt.__file__

td = Path(tempfile.mkdtemp(prefix="cvm-ear-oldproof-"))
write_sentinel(td, TREE_ID)
paths = CosmosPaths(td)
pcm, rate = cvm_dt_stt.wav_to_pcm(_sapi_wav(PHRASE))
sha = hashlib.sha256(pcm).hexdigest()
cas = paths.state("cvm") / "cas"
cas.mkdir(parents=True, exist_ok=True)
(cas / sha).write_bytes(pcm)
paths.state("cvm", "phone.json").write_text(json.dumps({
    "cvm": 1, "tree_id": TREE_ID, "cursor_out": "ear-1",
    "kinds": {"pcm": {"status": "ok", "sha256": sha, "n_bytes": len(pcm),
                      "rate": rate, "ch": 1},
              "voice_session": {"status": "ok", "queue_depth": 1,
                                "last_turn_epoch": time.time()}},
}), encoding="utf-8")

reset_voice_ack()
stamp_desktop_pull(paths, {"cursor": "ear-1"}, writer="cvm-dt-pull")
clock = cvm_pull.DesktopPullClock(
    CoreClient("http://127.0.0.1:1", "unused"), paths)
clock.last = json.loads(
    paths.state("cvm", "pull.json").read_text(encoding="utf-8"))
got = clock.on_speech(now=time.time())
ticket = json.loads(
    paths.state("cvm", "pull.json").read_text(encoding="utf-8"))

checks = {
    "new_path_stt_kind_ok": got.get("stt_kind") == "ok",
    "new_path_engine_sapi": got.get("stt_engine") == "sapi",
    "new_path_transcript_nonempty": bool(str(got.get("transcript") or "").strip()),
    "new_path_ear_ms_is_the_recognizers": (
        isinstance(got.get("ear_ms"), (int, float))
        and got.get("ear_ms") == (got.get("stt_fallback") or {}).get("ear_ms")),
    "new_path_publishes_cvm_ear_ms": got.get("cvm_ear_ms") is not None,
    "fallback_note_is_named": bool(got.get("stt_fallback")),
    "pull_json_stamped_ok_sapi": (ticket.get("stt_kind") == "ok"
                                  and ticket.get("stt_engine") == "sapi"),
}
print(json.dumps({
    "ran_against": str(OLD),
    "cvm_pull_file": cvm_pull.__file__,
    "has_phone_ear_fallback": hasattr(cvm_dt_stt, "phone_ear_fallback"),
    "old_on_speech": {"stt_kind": got.get("stt_kind"),
                      "stt_engine": got.get("stt_engine"),
                      "transcript": got.get("transcript"),
                      "ack": got.get("ack"),
                      "ear_ms": got.get("ear_ms")},
    "old_pull_json": {"stt_kind": ticket.get("stt_kind"),
                      "stt_engine": ticket.get("stt_engine")},
    "new_checks_against_old_code": checks,
    "any_passed": any(checks.values()),
}, indent=1, default=str))
raise SystemExit(0 if not any(checks.values()) else 1)
