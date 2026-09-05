#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prove the regression tests FAIL against the PRE-EDIT code. Not a suite.

A test that passes against the old code proves nothing about the fix. This
driver loads the staged pre-edit modules out of `_delme/predispose_*` under
their real module names and re-asks the two claims:

    1. the spend hazard  — old `stage_respond` POSTs `--phrase` verbatim
    2. the two-gate drift — old `run_gate` scores an unclaimed sink ok=False

Deliberately NOT named `test_*`: `cvm_suites.py` must not collect it.

    py -3.14 builds\\cvm-dt\\prove_old_fails.py --staged <_delme dir>
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import socket
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "cosmos"))


def load_old(staged: Path, name: str):
    """Import staged/<name>.py AS `name`, so dependents bind the old one."""
    spec = importlib.util.spec_from_file_location(name, staged / (name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


class RecordingDt:
    def __init__(self):
        self.posted = []

    def ask(self, transcript, session_id=None, speak=True, title="", cancel=None):
        self.posted.append(transcript)
        return {"rc": 200, "kind": "chat", "brain": "grok",
                "session_id": "old-sid", "spoken": "ok"}


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--staged", required=True)
    ap.add_argument("--base", default="http://127.0.0.1:8770")
    ns = ap.parse_args()
    staged = Path(ns.staged).resolve()

    old_dt = load_old(staged, "cvm_dt")
    old_bench = load_old(staged, "cvm_dt_bench")
    findings = []

    # ---- 1. the shared predicate did not exist ----
    findings.append({
        "claim": "old cvm_dt exposes sink_granted / SINK_OWNERS_OK",
        "old_result": {"sink_granted": hasattr(old_dt, "sink_granted"),
                       "SINK_OWNERS_OK": hasattr(old_dt, "SINK_OWNERS_OK")},
        "fails_against_old": not (hasattr(old_dt, "sink_granted")
                                  and hasattr(old_dt, "SINK_OWNERS_OK")),
    })

    # ---- 2. old run_gate's own expression on the LIVE reading ----
    # The exact values STAGE6_LOCAL.json recorded on this box at 02:03:
    # audio_owner "none", device matched the Windows default, earcon rendered.
    a = {"audio_owner": "none", "device_name_matches_windows_default": True,
         "lease_kind": None}
    old_device_ok = bool(a["device_name_matches_windows_default"]
                         and a["audio_owner"] == "desktop")   # old run_gate:1221
    import cvm_dt as new_dt_mod                               # noqa: E402
    sys.modules.pop("cvm_dt")
    spec = importlib.util.spec_from_file_location("cvm_dt_new", HERE / "cvm_dt.py")
    new_dt = importlib.util.module_from_spec(spec)
    sys.modules["cvm_dt_new"] = new_dt
    spec.loader.exec_module(new_dt)
    findings.append({
        "claim": "an unclaimed+armed sink grants the desktop",
        "reading": a,
        "old_result": old_device_ok,
        "new_result": new_dt.sink_granted(a),
        "fails_against_old": (old_device_ok is False
                              and new_dt.sink_granted(a) is True),
        "consequence_old": "run_gate ok = (device_ok or none_ok) and session_ok "
                           "-> False even with Core answering: STAGE6_GATE.json "
                           "could not close while the split half said PASS",
    })

    # ---- 3. old bench had no spend fence ----
    missing = [n for n in ("spend_class", "stage_voice_post", "felt_latency")
               if not hasattr(old_bench, n)]
    findings.append({
        "claim": "old cvm_dt_bench has a spend fence",
        "old_result": {"missing_symbols": missing},
        "fails_against_old": bool(missing),
    })

    # ---- 4. old stage_respond POSTs the paid default phrase, for real ----
    u = ns.base.rsplit(":", 1)
    port = int(u[-1])
    s = socket.socket()
    s.settimeout(0.75)
    reachable = s.connect_ex(("127.0.0.1", port)) == 0
    s.close()
    paid_phrase = "COSMOS desktop voice latency bench."
    posted = None
    if reachable:
        dt = RecordingDt()
        try:
            old_bench.stage_respond(dt, ns.base, paid_phrase, False)
        except Exception as e:                                   # noqa: BLE001
            posted = "raised %s: %s" % (type(e).__name__, e)
        posted = dt.posted if posted is None else posted
    findings.append({
        "claim": "the bench never POSTs a paid phrase",
        "core_reachable": reachable,
        "phrase": paid_phrase,
        "old_result": {"posted_by_old_stage_respond": posted},
        "fails_against_old": bool(posted) and paid_phrase in (posted or []),
        "consequence_old": "each bench run would POST prose that Core classifies "
                           "kind='chat' -> model rail -> CALL_EST_USD recorded "
                           "against the spend guard",
    })

    out = {"wire": "cvm-dt-old-fails/1", "staged": str(staged),
           "findings": findings,
           "all_fail_against_old": all(f["fails_against_old"] for f in findings)}
    print(json.dumps(out, indent=1))
    return 0 if out["all_fail_against_old"] else 1


if __name__ == "__main__":
    sys.exit(main())
