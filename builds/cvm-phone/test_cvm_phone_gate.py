#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for the cvm-phone stage-6 gate: the SPLIT, not the phone contract.

The phone contract itself is already gated by `test_cvm_phone_pull.py` and
`test_cvm_phone_clock.py`; re-proving `collect_kinds` here would be bloat.
What is new — and what a suite has to hold down — is the split:

  * the core half REFUSES the :8791 trial kernel by port, and writes nothing.
    Three agents already declined that substitution; this makes declining it
    the only thing the code can do
  * with Core down, the core half is a TYPED PENDING_CORE artifact in which
    every check names exactly what it needs, ok is false, and rc is 3 —
    retry, distinguishable from 1 (measured and wrong)
  * the local half stands alone on a scratch root with no Core anywhere,
    and never quotes a Core measurement
  * the verdict algebra is the desktop gate's (imported, not re-implemented),
    so PENDING can never round up to a pass
  * the core half has no import path to the loopback double

No live :8770 and no live tree: every proof lands in a temp file, so running
this suite can never overwrite a published gate artifact. rc=0 here is a green
log — stage 6 is STAGE6_PHONE.json's checks[], not this exit code.
"""
from __future__ import annotations

import json
import re
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
DT_DIR = HERE.parent / "cvm-dt"
COSMOS_DIR = HERE.parents[1] / "cosmos"
for _p in (HERE, DT_DIR, COSMOS_DIR):
    if _p.is_dir() and str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from cvm_dt import CvmDtError, RefusalKind  # noqa: E402
from cvm_double import dead_loopback_base, scratch_root  # noqa: E402
from cvm_gate import FAIL, PASS, PENDING, UNMEASURED  # noqa: E402

import cvm_phone_gate as G  # noqa: E402

RESULTS = []
SRC = (HERE / "cvm_phone_gate.py").read_text(encoding="utf-8")
CORE_SRC = SRC.split("# ---------------- half B")[1].split(
    "# ---------------- the record")[0]
BTS_IMPORT = re.compile(r"^\s*(?:from|import)\s+bts_\w+", re.M)
# Assignment, not comparison: `x["audio_owner"] == "desktop"` is the gate
# READING the owner, which is the whole point. Only a single `=` is a claim.
ASSIGN_OWNER = re.compile(
    r"""audio_owner["']\s*\]\s*=(?!=)|audio_owner\s*=\s*["'](?:phone|desktop)["']""")


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:                                            # noqa: BLE001
        RESULTS.append((label, False, "%s: %s" % (type(e).__name__, e)))


def _tmp(name: str) -> Path:
    return Path(tempfile.mkdtemp(prefix="cvm-phone-gate-test-")) / name


def test_trial_kernel_refused_by_port():
    """:8791 answers. It is not Core, and it writes no proof here."""
    k = scratch_root(worker="cvm-phone-gate-test")
    proof = _tmp("must_not_exist.json")
    try:
        G.run_core(k.paths.root, "http://127.0.0.1:8791", proof_path=str(proof))
        return False
    except CvmDtError as e:
        return (e.kind == RefusalKind.BAD_REQUEST
                and "trial kernel" in str(e)
                and "8791" in str(e)
                and not proof.exists()          # a refusal publishes nothing
                and 8791 in G.TRIAL_PORTS)


def test_core_half_is_typed_pending_naming_its_needs():
    """Core down -> an absence WITH A REASON, per check, and rc=3."""
    k = scratch_root(worker="cvm-phone-gate-test")
    proof = _tmp("core.json")
    rec = G.run_core(k.paths.root, dead_loopback_base(), proof_path=str(proof))
    on_disk = json.loads(proof.read_text(encoding="utf-8"))
    names = [c["name"] for c in rec["checks"]]
    return (
        rec["ok"] is False
        and rec["verdict"] == PENDING
        and G._rc(rec) == 3                     # retry, never "measured wrong"
        and rec["counts"][PENDING] == len(G.CORE_CHECKS)
        and rec["counts"][PASS] == 0
        and names == [n for n, _ in G.CORE_CHECKS]
        # the artifact is a work order: every check says what would unblock it
        and all(c.get("needs") for c in rec["checks"])
        and all(c["kind"] == str(RefusalKind.UNREACHABLE) for c in rec["checks"])
        and rec["core_reachable"] is False
        and rec["core_substitute_used"] is False
        and rec["loopback_double_used"] is False
        and rec["needs"]["routes"]
        and rec["needs"]["mutates_live"]
        and rec["rerun"].startswith("py -3.14 ")
        and all(v is None for v in rec["live_value"].values())
        and on_disk["emitted"] == rec["emitted"]
    )


def test_local_half_stands_alone_with_no_core():
    """Half A on a scratch root: no Core, no substitute, every check measured."""
    k = scratch_root(worker="cvm-phone-gate-test")
    proof = _tmp("local.json")
    rec = G.run_local(k.paths.root, proof_path=str(proof))
    by = {c["name"]: c for c in rec["checks"]}
    reach = by["live_phone_reach_measured"]["value"]
    return (
        rec["ok"] is True
        and rec["verdict"] == PASS
        and G._rc(rec) == 0
        and rec["core_used"] is False
        and rec["core_substitute_used"] is False
        and rec["counts"][FAIL] == 0
        and rec["counts"][UNMEASURED] == 0
        and rec["counts"][PENDING] == 0
        # a root that never saw a phone is MEASURED never_seen, and the
        # convenience wrapper still refuses rather than folding the absence
        and reach["reachable"] is False
        and reach["reason"] == "never_seen"
        and reach["require_phone_kind"] == str(RefusalKind.UNREACHABLE)
        # the double is quoted as a double, wherever it is quoted
        and by["loopback_double_provenance"]["value"]["is_core"] is False
        and by["phone_never_claims_audio"]["value"]["body_has_audio_owner"] is False
        and by["idle_tick_skips_http"]["value"]["tick2"]["push_bytes"] == 0
        and json.loads(proof.read_text(encoding="utf-8"))["emitted"] == rec["emitted"]
    )


def test_pending_never_rounds_up_to_a_pass():
    """The verdict algebra is the desktop gate's. One gate, one meaning."""
    passes = [{"name": "a", "verdict": PASS}]
    pend = passes + [{"name": "b", "verdict": PENDING}]
    fails = pend + [{"name": "c", "verdict": FAIL}]
    unm = passes + [{"name": "d", "verdict": UNMEASURED}]
    return (
        G._roll(passes) == (True, PASS)
        and G._roll(pend) == (False, PENDING)
        and G._roll(fails) == (False, FAIL)      # FAIL dominates PENDING
        and G._roll(unm) == (False, UNMEASURED)  # not measured is not passed
        and G._rc({"ok": False, "verdict": PENDING}) == 3
        and G._rc({"ok": False, "verdict": FAIL}) == 1
        and G._rc({"ok": True, "verdict": PASS}) == 0
    )


def test_core_half_has_no_path_to_the_double():
    """A double may serve half A. Half B has no stand-in at all."""
    return (
        "CoreDouble" not in CORE_SRC
        and "dead_loopback_base" not in CORE_SRC
        and "V:\\" not in SRC
        and "V:/" not in SRC
        and BTS_IMPORT.search(SRC) is None
        # the gate quotes the audio owner; it never assigns one
        and ASSIGN_OWNER.search(SRC) is None
    )


def main() -> int:
    check("core half refuses the :8791 trial kernel by port and publishes "
          "nothing", test_trial_kernel_refused_by_port)
    check("core half with Core down is a typed PENDING_CORE artifact naming "
          "what each check needs (rc=3, no substitute)",
          test_core_half_is_typed_pending_naming_its_needs)
    check("local half stands alone with no Core: measured never_seen reach, "
          "typed refusal, double quoted as a double",
          test_local_half_stands_alone_with_no_core)
    check("verdict algebra imported from the desktop gate: PENDING and "
          "UNMEASURED never round up to a pass",
          test_pending_never_rounds_up_to_a_pass)
    check("core half has no import path to the loopback double; no drive "
          "literal, no bts_, no owner claim",
          test_core_half_has_no_path_to_the_double)
    ok = all(p for _, p, _ in RESULTS)
    for label, passed, err in RESULTS:
        print(("PASS" if passed else "FAIL") + "  " + label
              + (("  " + err) if err else ""))
    print("result: " + ("ok" if ok else "FAIL")
          + "  %d/%d" % (sum(1 for _, p, _ in RESULTS if p), len(RESULTS)))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
