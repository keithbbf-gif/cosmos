#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cvm_gate — the split stage-6 gate. Green log, NOT the gate.

These rows prove the SPLIT behaves: that half A runs to a verdict with no Core
anywhere, that half B refuses a substitute and files a typed PENDING_CORE
artifact instead of a failure, and that neither half can round the other up.
The gate itself is STAGE6_LOCAL.json / STAGE6_CORE.json on the live tree.

Audio here is the injected FakeBackend on a scratch root: this suite runs on
the 15-minute selftest clock and must never seize the speakers or read the
live ticket.

    py -3.14 builds\\cvm-dt\\test_cvm_gate.py
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "cosmos"))

from cosmos_paths import CosmosPaths, write_sentinel                # noqa: E402
from cosmos_cvm_push import PULL_CLOCK_ID                           # noqa: E402

from cvm_dt import (                                                # noqa: E402
    AudioLease, CoreClient, CvmDtError, FakeBackend, RefusalKind,
    gate_audio, gate_core,
)
from cvm_double import CoreDouble, dead_loopback_base               # noqa: E402
import cvm_gate                                                     # noqa: E402
from cvm_gate import (                                              # noqa: E402
    FAIL, PASS, PENDING, REFUSED, UNMEASURED, TRIAL_PORTS,
    run_core, run_local, wait_for_core,
)

TREE_ID = "KMesh-COSMOS-live"
RESULTS = []


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:                                          # noqa: BLE001
        RESULTS.append((label, False, "%s: %s" % (type(e).__name__, e)))


def _scratch(prefix="cvm-gate-test-"):
    tmp = Path(tempfile.mkdtemp(prefix=prefix))
    write_sentinel(tmp, TREE_ID)
    (tmp / "config").mkdir(exist_ok=True)
    (tmp / "state").mkdir(exist_ok=True)
    (tmp / "config" / "api_token.txt").write_text("gate-token", encoding="utf-8")
    return tmp


def _by_name(rec, name):
    return next(c for c in rec["checks"] if c["name"] == name)


def test_local_half_runs_to_a_verdict_with_no_core():
    """Half A files real numbers while :8770 is down — the whole point."""
    tmp = _scratch()
    proof = tmp / "STAGE6_LOCAL.json"
    rec = run_local(tmp, proof_path=proof, audio=FakeBackend(), tts=False)
    on_disk = json.loads(proof.read_text(encoding="utf-8"))
    rt = _by_name(rec, "double_push_pull_roundtrip")
    return (
        rec["half"] == "local"
        and rec["core_used"] is False
        and rec["core_substitute_used"] is False
        and on_disk["emitted"] == rec["emitted"]
        and _by_name(rec, "root_identity")["verdict"] == PASS
        and _by_name(rec, "wasapi_default_match")["verdict"] == PASS
        and _by_name(rec, "dead_core_typed_refusal")["verdict"] == PASS
        and _by_name(rec, "double_empty_ticket_refused")["verdict"] == PASS
        and rt["verdict"] == PASS
        # measured, not estimated
        and rt["value"]["push_ms"] > 0 and rt["value"]["pull_ms"] > 0
        and rt["value"]["audio_owner"] == "desktop"
        and rt["value"]["cursor_advanced"] is True
        and rt["value"]["backlog_after"] == 0
        and rt["value"]["sole_writer_clock_id"] == int(PULL_CLOCK_ID)
        and rt["value"]["double"]["is_core"] is False
        and rt["value"]["double"]["kind"] == "LOOPBACK_DOUBLE"
    )


def test_voice_loop_ticks_and_heartbeats_with_no_core():
    """The ear/mouth loop is local: it ticks, heartbeats, never opens the mic."""
    rec = cvm_gate._check_voice_loop(FakeBackend())
    v = rec["value"]
    return (rec["verdict"] == PASS
            and v["no_ticket"]["core_kind"] == "UNREACHABLE"
            and v["no_ticket"]["mic_state"] == "idle"
            and v["seeded_id18_ticket"]["mic_state"] == "idle"
            and v["seeded_id18_ticket"]["ticket_clock_id"] == int(PULL_CLOCK_ID)
            and v["seeded_id18_ticket"]["audio_owner"] == "desktop"
            and v["heartbeat"]["last_run_epoch"] > 0
            # the scratch root, NEVER the live one
            and "cvm-double-" in v["scratch_root"])


def test_unmeasured_never_counts_as_a_pass():
    """--no-tts leaves a row UNMEASURED, so the half is NOT ok. No rounding up."""
    tmp = _scratch()
    rec = run_local(tmp, proof_path=tmp / "p.json", audio=FakeBackend(), tts=False)
    # --no-tts silences the mouth, so BOTH mouth rows go UNMEASURED: the
    # synthesis itself and the ear round trip that consumes it (there is
    # nothing spoken to hear). Naming the rows beats counting them -- the
    # old `counts[UNMEASURED] == 1` was a constant that had to be edited
    # every time a row was added, which is not what this test is about.
    # phone_pcm_lands_on_an_ear synthesizes the "phone" PCM with the same
    # mouth, so --no-tts silences it too.
    silenced = ("sapi_tts_wav", "on_box_ear_round_trip",
                "phone_pcm_lands_on_an_ear")
    return (all(_by_name(rec, n)["verdict"] == UNMEASURED for n in silenced)
            and rec["ok"] is False
            and rec["verdict"] == UNMEASURED
            and rec["counts"][UNMEASURED] == len(silenced)
            and rec["counts"][FAIL] == 0)


def test_missing_default_device_is_a_passing_refusal():
    """AUDIO_NONE is the measurement, not its absence — and never a fake name."""
    tmp = _scratch()
    rec = run_local(tmp, proof_path=tmp / "p.json",
                    audio=FakeBackend(none=True), tts=False)
    m = _by_name(rec, "wasapi_default_match")
    return (m["verdict"] == REFUSED
            and m["kind"] == str(RefusalKind.AUDIO_NONE)
            and _by_name(rec, "earcon_render")["verdict"] == REFUSED
            and rec["counts"][FAIL] == 0)


def test_core_half_files_typed_pending_not_a_failure():
    """Core down → STAGE6_CORE.json says PENDING_CORE, names the kind and rerun."""
    tmp = _scratch()
    proof = tmp / "STAGE6_CORE.json"
    dead = dead_loopback_base()
    rec = run_core(tmp, dead, proof_path=proof)
    on_disk = json.loads(proof.read_text(encoding="utf-8"))
    return (
        proof.is_file()
        and rec["verdict"] == PENDING and rec["ok"] is False
        and rec["core_reachable"] is False
        and rec["core_kind"] == str(RefusalKind.UNREACHABLE)
        and rec["core_substitute_used"] is False
        and rec["counts"][PENDING] == 4 and rec["counts"][FAIL] == 0
        and all(c["kind"] == str(RefusalKind.UNREACHABLE) for c in rec["checks"])
        and "--root" in rec["rerun"] and dead in rec["rerun"]
        and on_disk["verdict"] == PENDING
        and cvm_gate._rc(rec) == 3          # PENDING is not FAILED
    )


def test_core_half_refuses_the_trial_kernel():
    """:8791 answers. It is not Core. A stand-in is refused before the gate."""
    tmp = _scratch()
    try:
        run_core(tmp, "http://127.0.0.1:8791")
        return False
    except CvmDtError as e:
        return (e.kind == RefusalKind.BAD_REQUEST and 8791 in TRIAL_PORTS
                and not (tmp / "STAGE6_CORE.json").exists())


def test_core_half_passes_against_a_real_service():
    """The core half is not vacuous: a real Core mints a sid resume keeps.

    The double stands in HERE only to prove the half's own logic is sound —
    the live record is written against :8770 and never against this.
    """
    with CoreDouble(tree_id=TREE_ID) as dbl:
        core = CoreClient(dbl.base, dbl.token)
        c = gate_core(core, TREE_ID)
        up = wait_for_core(core, 0.0)
        return (up["up"] is True and up["polls"] == 1
                and c["core_kind"] is None
                and bool(c["session_id"])
                and c["session_id"] == c["resume_session_id"]
                and c["session_ok"] is True)


def test_watch_gives_up_with_the_kind_it_last_saw():
    """--watch returns PENDING with the refusal kind, not a silent timeout."""
    core = CoreClient(dead_loopback_base(), "t")
    got = wait_for_core(core, 0.0)
    return (got["up"] is False and got["polls"] == 1
            and got["last_kind"] == str(RefusalKind.UNREACHABLE)
            and got["waited_ms"] >= 0.0)


def test_foreign_clock_ticket_is_named_not_crashed():
    """A ticket from a non-id18 writer is a typed lease_kind, fail-closed."""
    tmp = _scratch()
    cvm = tmp / "state" / "cvm"
    cvm.mkdir(parents=True, exist_ok=True)
    (cvm / "pull.json").write_text(json.dumps({
        "cvm": 1, "tree_id": TREE_ID, "clock_id": 15,
        "audio_owner": "desktop", "issued_epoch": 9e9,
    }), encoding="utf-8")
    paths = CosmosPaths(tmp)
    a = gate_audio(FakeBackend(), AudioLease(paths.state("cvm", "pull.json"),
                                             TREE_ID), armed=True)
    rec = run_local(tmp, proof_path=tmp / "p.json", audio=FakeBackend(), tts=False)
    honor = _by_name(rec, "audio_lease_honor")
    return (a["lease_kind"] == str(RefusalKind.UNREACHABLE)
            and a["earcon_device_name"] == ""
            and honor["verdict"] == REFUSED
            and honor["kind"] == str(RefusalKind.UNREACHABLE))


def test_halves_share_one_implementation():
    """gate_audio/gate_core are the SAME functions run_gate uses — no fork."""
    import cvm_dt
    src = (Path(__file__).resolve().parent / "cvm_dt.py").read_text(encoding="utf-8")
    return (cvm_gate.gate_audio is cvm_dt.gate_audio
            and cvm_gate.gate_core is cvm_dt.gate_core
            and src.count("def gate_audio(") == 1
            and src.count("def gate_core(") == 1
            and "a = gate_audio(" in src and "c = gate_core(" in src)


def main() -> int:
    # A cp1252 console must never decide whether a gate is green (the
    # 2026-08-30 scar). The labels below are prose; the codepage is not.
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass
    for fn in (
        test_local_half_runs_to_a_verdict_with_no_core,
        test_voice_loop_ticks_and_heartbeats_with_no_core,
        test_unmeasured_never_counts_as_a_pass,
        test_missing_default_device_is_a_passing_refusal,
        test_core_half_files_typed_pending_not_a_failure,
        test_core_half_refuses_the_trial_kernel,
        test_core_half_passes_against_a_real_service,
        test_watch_gives_up_with_the_kind_it_last_saw,
        test_foreign_clock_ticket_is_named_not_crashed,
        test_halves_share_one_implementation,
    ):
        check(fn.__doc__.splitlines()[0].strip(), fn)
    bad = [r for r in RESULTS if not r[1]]
    for label, ok, err in RESULTS:
        print("%s %s%s" % ("PASS" if ok else "FAIL", label,
                           (" -- " + err) if err else ""))
    print("%d/%d" % (len(RESULTS) - len(bad), len(RESULTS)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
