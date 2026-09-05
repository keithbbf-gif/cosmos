#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Contradiction guard for cvm-dt — the CODE is the truth, this suite pins it.

Job 010_cvm_dt_gate reported four disagreements between `docs/CVM_ARCH.md` and
this package: the CVM clock id (15 vs 16 vs 18), P3 "HOLD" vs a live
`/cvm/pull` + `/cvm/push`, Piper vs SAPI, and `audio.json` vs `pull.json` as
the AUDIO_OWNER home. Prose drifts silently; a suite does not. Every row here
asserts what the shipped code actually does, so the next reader of the doc has
an executing gate to check it against.

Negative rows are the point: a ticket that is NOT the sole writer's must be
refused even when it claims `audio_owner=desktop`, and refused BEFORE any of
its other fields are believed.

No live Core, no audio hardware, no network. rc=0 here is a green log.
"""
from __future__ import annotations

import json
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "cosmos"))

from cosmos_paths import CosmosPaths, write_sentinel  # noqa: E402

import cosmos_cvm_clock as satellite  # noqa: E402
from cosmos_cvm_push import PULL_CLOCK_ID, PUSH_PATH, stamp_desktop_pull  # noqa: E402

import cvm_dt  # noqa: E402
import cvm_dt_clock as pull_clock  # noqa: E402
import cvm_pull  # noqa: E402
from cvm_dt import (  # noqa: E402
    LEASE_REL, PULL_PATH, SNAP_PATH, AudioLease, CoreClient, CvmDt, CvmDtError,
    FakeBackend, RefusalKind, require_sole_writer,
)
from cvm_dt_voice import consume_id18_pull  # noqa: E402

HERE = Path(__file__).resolve().parent
RESULTS: list[tuple[str, bool, str]] = []


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:                                            # noqa: BLE001
        RESULTS.append((label, False, "%s: %s" % (type(e).__name__, e)))


def _scratch():
    tmp = Path(tempfile.mkdtemp(prefix="cvm-dt-contract-"))
    write_sentinel(tmp, "KMesh-COSMOS-live")
    (tmp / "config").mkdir()
    (tmp / "state").mkdir()
    (tmp / "config" / "api_token.txt").write_text("test-token", encoding="utf-8")
    return tmp


def _ticket(root, **extra):
    p = Path(root) / "state" / "cvm" / "pull.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    d = {
        "cvm": 1,
        "tree_id": "KMesh-COSMOS-live",
        "issued_epoch": time.time(),
        "pull": True,
        "audio_owner": "desktop",
        "clock_id": PULL_CLOCK_ID,
        "core_ready": True,
        "core_kind": "ok",
        "writer": "cvm-dt-clock",
    }
    d.update(extra)
    p.write_text(json.dumps(d), encoding="utf-8")
    return p


def _lease(root):
    paths = CosmosPaths(root)
    return AudioLease(paths.state(*LEASE_REL), paths.sentinel.tree_id)


def _refusal(fn):
    """Run fn; return (kind, detail) of the typed refusal, or (None, '')."""
    try:
        fn()
    except CvmDtError as e:
        return e.kind, str(e)
    return None, ""


# ---------------- 1. the clock id: 18 writes pull.json, 15/16 defer ----------
def test_registry_ids_do_not_collide():
    """15=pool, 16=CVM satellite, 18=desktop pull clock. Three ids, one file."""
    return (PULL_CLOCK_ID == 18
            and pull_clock.CLOCK_ID == PULL_CLOCK_ID
            and satellite.CLOCK_ID == 16
            and satellite.CLOCK_ID != PULL_CLOCK_ID)


def test_writer_normalises_clock_id():
    """The sole writer stamps its own id — the invariant at its source."""
    tmp = _scratch()
    paths = CosmosPaths(tmp)
    stamp_desktop_pull(paths, {"cvm": 1, "pull": True, "clock_id": 16,
                               "audio_owner": "desktop"})
    got = json.loads(paths.state(*LEASE_REL).read_text(encoding="utf-8"))
    return got["clock_id"] == PULL_CLOCK_ID


def test_foreign_clock_id_is_refused():
    """NEGATIVE: an id16 ticket says desktop; it still grants nothing."""
    tmp = _scratch()
    _ticket(tmp, clock_id=16, audio_owner="desktop")
    kind, detail = _refusal(_lease(tmp).current)
    return kind == RefusalKind.UNREACHABLE and "sole writer" in detail


def test_missing_clock_id_is_refused():
    """NEGATIVE: an unstamped ticket is not the clock's either. Fail closed."""
    tmp = _scratch()
    p = _ticket(tmp)
    d = json.loads(p.read_text(encoding="utf-8"))
    del d["clock_id"]
    p.write_text(json.dumps(d), encoding="utf-8")
    kind, _ = _refusal(_lease(tmp).current)
    return kind == RefusalKind.UNREACHABLE


def test_armed_dt_cannot_be_tricked_by_foreign_ticket():
    """NEGATIVE: --arm widens WHO may hold the sink, never WHO may stamp it."""
    tmp = _scratch()
    _ticket(tmp, clock_id=15, audio_owner="none")
    dt = CvmDt(CosmosPaths(tmp), CoreClient("http://127.0.0.1:1", "x"),
               FakeBackend(name="Headphones (FAKE HT3)"), _lease(tmp), arm=True)
    kind, _ = _refusal(dt.ensure_can_speak)
    return kind == RefusalKind.UNREACHABLE


def test_foreign_ticket_refused_before_its_fields_are_believed():
    """Ordering: the voice loop must not trust core_ready on a foreign ticket."""
    tmp = _scratch()
    _ticket(tmp, clock_id=16, core_ready=True, core_kind="ok")
    kind, detail = _refusal(lambda: consume_id18_pull(CosmosPaths(tmp)))
    return kind == RefusalKind.UNREACHABLE and "sole writer" in detail


def test_sole_writer_check_is_one_helper():
    """Improvement is not bloat: one choke point, not a copy per consumer.

    The refusal text is the fingerprint of the check. It may appear in exactly
    one module — the moment a second consumer re-implements the comparison,
    this row reddens.
    """
    owners = [p.name for p in sorted(HERE.glob("*.py"))
              if not p.name.startswith("test_")
              and "is not id%s sole writer" in p.read_text(encoding="utf-8")]
    return callable(require_sole_writer) and owners == ["cvm_dt.py"]


def test_good_ticket_still_grants_desktop():
    """The guard must not over-refuse: the real stamp still opens the sink."""
    tmp = _scratch()
    _ticket(tmp, audio_owner="desktop")
    cur = _lease(tmp).current()
    return cur["audio_owner"] == "desktop" and _lease(tmp).allows(cur)


# ---------------- 2. /cvm/pull + /cvm/push are LIVE, not HOLD ---------------
def test_cvm_routes_are_real_not_hold():
    return (PULL_PATH == "/api/v1/cvm/pull"
            and PUSH_PATH == "/api/v1/cvm/push"
            and SNAP_PATH == "/api/v1/cvm/snapshot"
            and cvm_pull.PULL_CLOCK_ID == PULL_CLOCK_ID
            and hasattr(cvm_pull, "DesktopPullClock"))


# ---------------- 3. the mouth is Piper, SAPI is the floor ------------------
def test_tts_engine_is_piper_with_sapi_floor():
    src = (HERE / "cvm_dt.py").read_text(encoding="utf-8")
    return (hasattr(cvm_dt, "_sapi_wav")
            and "SAPI.SpVoice" in src
            and "cvm_tts_piper" in src
            and "piper" in src.lower())


# ---------------- 4. the lease lives in pull.json, never audio.json ---------
def test_lease_home_is_pull_json_and_audio_json_is_never_written():
    tmp = _scratch()
    _ticket(tmp, audio_owner="desktop")
    _lease(tmp).current()
    audio_json = Path(tmp) / "state" / "cvm" / "audio.json"
    return (LEASE_REL == ("cvm", "pull.json")
            and not audio_json.exists()
            and not hasattr(AudioLease, "acquire")
            and not hasattr(AudioLease, "release")
            and not hasattr(AudioLease, "_write"))


# ---------------- 5. the README in this fence agrees with the code ----------
def test_readme_does_not_contradict_the_code():
    """The doc-drift gate: prose in this fence must match the four rows above."""
    txt = (HERE / "README.md").read_text(encoding="utf-8").lower()
    return ("projection `state/cvm/audio.json`" not in txt
            and "(hold, additive core)" not in txt
            and "cvm clock id 15" not in txt
            and "pull.json" in txt
            and "sapi" in txt)


def main() -> int:
    check("registry ids 15/16/18 do not collide; 18 owns pull.json",
          test_registry_ids_do_not_collide)
    check("sole writer normalises clock_id to 18 on every stamp",
          test_writer_normalises_clock_id)
    check("NEGATIVE id16 ticket claiming desktop is UNREACHABLE",
          test_foreign_clock_id_is_refused)
    check("NEGATIVE unstamped ticket is UNREACHABLE",
          test_missing_clock_id_is_refused)
    check("NEGATIVE --arm does not admit an id15 ticket",
          test_armed_dt_cannot_be_tricked_by_foreign_ticket)
    check("foreign ticket refused before core_ready is believed",
          test_foreign_ticket_refused_before_its_fields_are_believed)
    check("one sole-writer helper, no per-consumer copy",
          test_sole_writer_check_is_one_helper)
    check("guard does not over-refuse: real stamp still grants desktop",
          test_good_ticket_still_grants_desktop)
    check("/cvm/pull + /cvm/push + /cvm/snapshot are live routes, not HOLD",
          test_cvm_routes_are_real_not_hold)
    check("TTS is Piper->WAV->WASAPI; SAPI remains the floor",
          test_tts_engine_is_piper_with_sapi_floor)
    check("AUDIO_OWNER home is pull.json; audio.json never written",
          test_lease_home_is_pull_json_and_audio_json_is_never_written)
    check("README in this fence does not contradict the code",
          test_readme_does_not_contradict_the_code)
    failed = [(l, err) for l, ok, err in RESULTS if not ok]
    for label, ok, err in RESULTS:
        print("%s  %s%s" % ("PASS" if ok else "FAIL", label, ("  " + err) if err else ""))
    print("result: %d/%d" % (len(RESULTS) - len(failed), len(RESULTS)))
    print("note: green log. docs/CVM_ARCH.md is outside this fence — the four "
          "rows above are what the code does, for COW to correct the doc from.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
