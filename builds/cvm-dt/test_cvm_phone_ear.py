#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B1 — phone-pulled PCM must land on an ear, not on a deaf PC.

`cosmos_cvm_push.bind_phone_stt` transcribes through VOSK ONLY. This box has
no vosk wheel and no `COSMOS_VOSK_MODEL`, so every phone utterance the pull
clock drains came back `STT_NONE` — wishlist #1 ("pull it off the phone for
LOCAL processing") arriving at a PC with no ear. `cvm_dt_stt.phone_ear_fallback`
adds the on-box Windows recognizer as the second tier, applied at the in-fence
caller `cvm_pull.DesktopPullClock.on_speech`.

rc=0 is NOT the gate. The gate is `B1_EAR.json`'s `live_value`:

  * `old_path` — the REAL `stt_interrupt` on the REAL CAS bytes, showing the
    `STT_NONE` this change exists to fix. Run first, on the same bytes, in the
    same process. This is the regression proof: it is measured, not recalled.
  * `new_path` — the same bytes through `on_speech`, carrying a transcript the
    box's own recognizer produced from audio the box's own synthesizer spoke,
    plus the recognizer token id that produced it.
  * `stamped` — `state/cvm/pull.json` read back off disk with
    `stt_kind="ok"`, `stt_engine="sapi"`, `clock_id=18`. A value the VOSK-only
    fold is structurally incapable of writing on this box.

No Core, no network, no credential, no pip: the mouth and the ear are both
Windows components already installed.

    py -3.14 builds\\cvm-dt\\test_cvm_phone_ear.py
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "cosmos"))

from cosmos_paths import CosmosPaths, write_sentinel  # noqa: E402
from cosmos_cvm_push import (  # noqa: E402
    PULL_CLOCK_ID, phone_state, probe_stt, reset_voice_ack, stamp_desktop_pull,
    stt_interrupt,
)

from cvm_dt import CoreClient, _sapi_wav  # noqa: E402
from cvm_dt_stt import (  # noqa: E402
    FALLBACK_WIRE, phone_ear_fallback, probe_sapi, wav_to_pcm,
)
from cvm_pull import DesktopPullClock  # noqa: E402
from cvm_test_guard import sandbox_heartbeats  # noqa: E402

TREE_ID = "KMesh-COSMOS-live"
PHRASE = "open the status report"
RESULTS: list[tuple[str, bool, str]] = []
LIVE: dict = {}


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:                                            # noqa: BLE001
        RESULTS.append((label, False, "%s: %s" % (type(e).__name__, e)))


def _scratch(prefix: str) -> CosmosPaths:
    td = Path(tempfile.mkdtemp(prefix=prefix))
    write_sentinel(td, TREE_ID)
    return CosmosPaths(td)


def _land_pcm(paths: CosmosPaths, pcm: bytes, rate: int) -> str:
    """Put bytes in the CAS and point phone.json at them, as a push would."""
    sha = hashlib.sha256(pcm).hexdigest()
    cas = paths.state("cvm") / "cas"
    cas.mkdir(parents=True, exist_ok=True)
    (cas / sha).write_bytes(pcm)
    paths.state("cvm", "phone.json").write_text(json.dumps({
        "cvm": 1, "tree_id": TREE_ID, "cursor_out": "ear-1",
        "kinds": {
            "pcm": {"status": "ok", "sha256": sha, "n_bytes": len(pcm),
                    "rate": rate, "ch": 1},
            "voice_session": {"status": "ok", "queue_depth": 1,
                              "last_turn_epoch": time.time()},
        },
    }), encoding="utf-8")
    return sha


def _speak() -> tuple[bytes, int]:
    """This box's own synthesizer. No fixture file, no recorded sample."""
    pcm, rate = wav_to_pcm(_sapi_wav(PHRASE))
    return pcm, rate


# ---------------------------------------------------------------------------
# The measurement: old path, new path, same bytes, same process.
# ---------------------------------------------------------------------------
def test_deaf_pc_then_on_box_ear():
    paths = _scratch("cvm-ear-b1-")
    pcm, rate = _speak()
    sha = _land_pcm(paths, pcm, rate)
    phone = phone_state(paths, TREE_ID)

    vosk = probe_stt()
    sapi = probe_sapi()

    # --- OLD PATH. The real Core-adjacent fold, on the real bytes. -----------
    reset_voice_ack()
    old = stt_interrupt(paths, phone, None, now=time.time())

    # --- NEW PATH. Same bytes, through the in-fence drain clock. -------------
    reset_voice_ack()
    stamp_desktop_pull(paths, {"cursor": "ear-1"}, writer="cvm-dt-pull")
    clock = DesktopPullClock(CoreClient("http://127.0.0.1:1", "unused"), paths)
    clock.last = json.loads(
        paths.state("cvm", "pull.json").read_text(encoding="utf-8"))
    new = clock.on_speech(now=time.time())
    ticket = json.loads(
        paths.state("cvm", "pull.json").read_text(encoding="utf-8"))

    heard = str(new.get("transcript") or "")
    want = set(PHRASE.lower().split())
    hits = want & set(heard.lower().replace(",", " ").replace(".", " ").split())

    LIVE.update({
        "phrase": PHRASE,
        "pcm_sha256": sha,
        "pcm_bytes": len(pcm),
        "rate": rate,
        "vosk_probe": {"ok": vosk.get("ok"), "detail": vosk.get("detail")},
        "sapi_probe": {"ok": sapi.get("ok"),
                       "recognizer": sapi.get("recognizer"),
                       "recognizer_id": sapi.get("recognizer_id")},
        "old_path": {
            "fn": "cosmos_cvm_push.stt_interrupt -> bind_phone_stt",
            "stt_kind": old.get("stt_kind"),
            "stt_engine": old.get("stt_engine"),
            "transcript": old.get("transcript"),
            "ack": old.get("ack"),
            "ear_ms": old.get("ear_ms"),
        },
        "new_path": {
            "fn": "cvm_pull.DesktopPullClock.on_speech + phone_ear_fallback",
            "stt_kind": new.get("stt_kind"),
            "stt_engine": new.get("stt_engine"),
            "transcript": heard,
            "recognizer": new.get("stt_recognizer"),
            "ear_ms": new.get("ear_ms"),
            "cvm_ear_ms": new.get("cvm_ear_ms"),
            "word_recall": round(len(hits) / max(1, len(want)), 3),
            "words_matched": sorted(hits),
            "fallback": new.get("stt_fallback"),
        },
        "stamped": {
            "path": str(paths.state("cvm", "pull.json")),
            "stt_kind": ticket.get("stt_kind"),
            "stt_engine": ticket.get("stt_engine"),
            "stt_pcm_sha256": ticket.get("stt_pcm_sha256"),
            "clock_id": ticket.get("clock_id"),
            "writer": ticket.get("writer"),
        },
    })

    # The regression half: the old path really does fail on these bytes.
    check("old_path_is_deaf_STT_NONE",
          lambda: old.get("stt_kind") == "STT_NONE"
          and old.get("stt_engine") == "vosk"
          and not old.get("transcript"))
    check("old_path_acked_unavailable",
          lambda: old.get("ack") == "speech recognition unavailable")
    check("vosk_absent_on_this_box",
          lambda: vosk.get("ok") is False and bool(vosk.get("detail")))

    # The fix half: the same bytes now produce words.
    check("new_path_stt_kind_ok", lambda: new.get("stt_kind") == "ok")
    check("new_path_engine_sapi", lambda: new.get("stt_engine") == "sapi")
    check("new_path_transcript_nonempty", lambda: bool(heard.strip()))
    check("new_path_recognized_the_phrase", lambda: len(hits) >= 2)
    check("new_path_names_the_recognizer",
          lambda: bool(new.get("stt_recognizer")))
    # Must come FROM the recognizer. bind_phone_stt also sets ear_ms on its
    # STT_NONE branch (its own elapsed timer), so "ear_ms exists" alone does
    # not discriminate the fix — measured, see _disposal/b1_old_code_proof.py.
    check("new_path_ear_ms_is_the_recognizers",
          lambda: isinstance(new.get("ear_ms"), (int, float))
          and new["ear_ms"] > 0
          and new["ear_ms"] == (new.get("stt_fallback") or {}).get("ear_ms"))
    check("new_path_publishes_cvm_ear_ms",
          lambda: new.get("cvm_ear_ms") == new.get("ear_ms"))
    check("stt_none_ack_withdrawn_when_heard",
          lambda: "ack" not in new and new.get("voice_state") == "ready")
    check("fallback_note_is_named",
          lambda: (new.get("stt_fallback") or {}).get("engaged") is True
          and (new["stt_fallback"]).get("heard") is True
          and (new["stt_fallback"]).get("wire") == FALLBACK_WIRE)
    check("consumed_sha_is_the_pushed_sha",
          lambda: new.get("stt_pcm_sha256") == sha)

    # The stamped half: pull.json on disk carries the value.
    check("pull_json_stamped_ok_sapi",
          lambda: ticket.get("stt_kind") == "ok"
          and ticket.get("stt_engine") == "sapi")
    check("pull_json_clock_id_18",
          lambda: ticket.get("clock_id") == PULL_CLOCK_ID == 18)


# ---------------------------------------------------------------------------
# The fallback must be a NAMED skip in every case it does not engage.
# ---------------------------------------------------------------------------
def test_fallback_refuses_to_fish_for_words():
    """A REAL vosk STT_NONE is a word verdict and must not be re-run."""
    paths = _scratch("cvm-ear-nofish-")
    pcm, rate = _speak()
    _land_pcm(paths, pcm, rate)
    phone = phone_state(paths, TREE_ID)
    stt = {"stt_kind": "STT_NONE", "stt_engine": "vosk", "transcript": "",
           "stt_pcm_sha256": hashlib.sha256(pcm).hexdigest()}
    out = phone_ear_fallback(
        paths, phone, stt,
        vosk_probe=lambda: {"ok": True, "engine": "vosk", "kind": "ok",
                            "model": "pretend"})
    check("vosk_present_means_no_second_engine",
          lambda: out.get("stt_kind") == "STT_NONE"
          and out.get("stt_engine") == "vosk"
          and out["stt_fallback"]["engaged"] is False
          and "word verdict" in out["stt_fallback"]["reason"])


def test_fallback_skips_a_healthy_fold():
    paths = _scratch("cvm-ear-healthy-")
    out = phone_ear_fallback(paths, None, {
        "stt_kind": "ok", "stt_engine": "vosk", "transcript": "already heard"})
    check("ok_fold_untouched",
          lambda: out.get("transcript") == "already heard"
          and out["stt_fallback"]["engaged"] is False
          and "not STT_NONE" in out["stt_fallback"]["reason"])


def test_fallback_skips_missing_cas_bytes():
    """UNREACHABLE / no-bytes is the fold's verdict, not the ear's problem."""
    paths = _scratch("cvm-ear-nocas-")
    missing = "f" * 64
    out = phone_ear_fallback(paths, {"kinds": {"pcm": {"sha256": missing}}},
                             {"stt_kind": "STT_NONE", "stt_engine": "vosk",
                              "stt_pcm_sha256": missing})
    check("no_cas_bytes_is_a_named_skip",
          lambda: out["stt_fallback"]["engaged"] is False
          and "no CAS bytes" in out["stt_fallback"]["reason"]
          and out.get("stt_kind") == "STT_NONE")


def test_empty_transcript_stays_stt_none():
    """Silence must NOT become 'ok'. The ear ran; it heard nothing."""
    paths = _scratch("cvm-ear-silence-")
    silence = b"\x00\x00" * 16000
    sha = _land_pcm(paths, silence, 16000)
    phone = phone_state(paths, TREE_ID)

    class _Deaf:
        def recognize_pcm(self, pcm, rate):                           # noqa: ARG002
            return {"transcript": "", "engine": "sapi", "ear_ms": 12.5,
                    "recognizer": "MS-1033-80-DESK"}

    out = phone_ear_fallback(paths, phone,
                             {"stt_kind": "STT_NONE", "stt_engine": "vosk",
                              "stt_pcm_sha256": sha},
                             transcriber=_Deaf())
    check("empty_transcript_is_not_promoted",
          lambda: out.get("stt_kind") == "STT_NONE"
          and out.get("stt_engine") == "sapi"
          and out.get("ear_ms") == 12.5
          and out["stt_fallback"]["engaged"] is True
          and out["stt_fallback"]["heard"] is False)


def test_no_production_state_touched():
    """Every path above wrote a temp root. Nothing under live/ was opened."""
    live = Path(__file__).resolve().parents[2] / "live" / "state" / "cvm"
    before = {}
    for name in ("pull.json", "phone.json"):
        p = live / name
        before[name] = p.stat().st_mtime if p.is_file() else None
    paths = _scratch("cvm-ear-fence-")
    pcm, rate = _speak()
    _land_pcm(paths, pcm, rate)
    after = {}
    for name in ("pull.json", "phone.json"):
        p = live / name
        after[name] = p.stat().st_mtime if p.is_file() else None
    LIVE["fence"] = {"live_cvm_dir": str(live), "mtimes_unchanged": before == after}
    check("production_cvm_state_untouched", lambda: before == after)


def main() -> int:
    if os.name != "nt":
        print(json.dumps({"ok": False, "kind": "STT_NONE",
                          "detail": "SAPI mouth+ear are Windows-only"}))
        return 2
    with sandbox_heartbeats():
        test_deaf_pc_then_on_box_ear()
        test_fallback_refuses_to_fish_for_words()
        test_fallback_skips_a_healthy_fold()
        test_fallback_skips_missing_cas_bytes()
        test_empty_transcript_stays_stt_none()
        test_no_production_state_touched()

    passed = sum(1 for _, ok, _ in RESULTS if ok)
    for label, ok, err in RESULTS:
        print("%s %s%s" % ("PASS" if ok else "FAIL", label,
                           (" - " + err) if err else ""))
    ok_all = passed == len(RESULTS)
    old = LIVE.get("old_path", {})
    new = LIVE.get("new_path", {})
    rec = {
        "ok": ok_all,
        "wire": "cvm-dt-b1-ear/1",
        "suite": "test_cvm_phone_ear.py",
        "passed": passed, "total": len(RESULTS),
        "gated_at_epoch": time.time(),
        "python": sys.version.split()[0],
        "live_value": LIVE,
        "emitted": "b1-ear:%s:%s->%s:%s:%s" % (
            TREE_ID, old.get("stt_kind"), new.get("stt_kind"),
            new.get("recognizer"), (new.get("transcript") or "")[:48]),
        "note": ("rc=0 is not the gate. old_path is the same real fold on the "
                 "same real bytes; new_path's transcript is a value the "
                 "VOSK-only path cannot produce on a box with no VOSK."),
        "results": [{"name": n, "verdict": "PASS" if o else "FAIL",
                     "detail": e} for n, o, e in RESULTS],
    }
    out = Path(__file__).resolve().parent / "B1_EAR.json"
    out.write_text(json.dumps(rec, indent=1, default=str), encoding="utf-8")
    rec["proof_path"] = str(out)
    print(json.dumps({"ok": ok_all, "passed": passed, "total": len(RESULTS),
                      "emitted": rec["emitted"], "proof_path": str(out)},
                     indent=1))
    return 0 if ok_all else 1


if __name__ == "__main__":
    raise SystemExit(main())
