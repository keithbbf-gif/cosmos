#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Throwaway shape probe — learn the real values before asserting on them.

Not a gate, not a suite. Boots the loopback double, seeds a desktop ticket
with a kinds[] ask, drives cvm_phone_clock twice and dumps every field the
phone gate is about to bind to. Measure first, assert second.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PHONE = HERE.parent
DT = PHONE.parent / "cvm-dt"
LIB = PHONE.parents[1] / "cosmos"
for p in (str(PHONE), str(DT), str(LIB)):
    if p not in sys.path:
        sys.path.insert(0, p)

from cosmos_cvm_push import stamp_desktop_pull  # noqa: E402

from cvm_dt import CoreClient, CvmDtError  # noqa: E402
from cvm_double import CoreDouble, dead_loopback_base  # noqa: E402

from cvm_phone_clock import CvmPhoneClock  # noqa: E402

ASK = ["device", "sms", "calls", "pcm", "fax_over_ip"]
out = {}

dbl = CoreDouble(worker="cvm-phone-probe").start()
try:
    core = CoreClient(dbl.base, dbl.token)

    # 1. fresh double, no ticket
    try:
        CvmPhoneClock(core, dbl.paths).cycle_once()
        out["empty"] = "NO REFUSAL"
    except CvmDtError as e:
        out["empty"] = {"kind": str(e.kind), "detail": str(e)}

    # 2. seed the desktop ticket with an ask
    seeded = stamp_desktop_pull(dbl.paths, {"kinds": ASK, "cursor": "desk-1"})
    out["seeded_ticket"] = seeded

    clk = CvmPhoneClock(core, dbl.paths, grants=("device", "sms"))
    body = clk._turn_body()
    out["body_keys"] = sorted(body)
    r1 = clk.cycle_once()
    r2 = clk.cycle_once()
    out["tick1"] = r1["live_value"]
    out["tick1_extra"] = {k: r1.get(k) for k in (
        "unsupported_kinds", "claimed", "push_replayed", "cursor_advanced",
        "quoted_from", "published")}
    out["tick2"] = r2["live_value"]
    out["tick2_extra"] = {k: r2.get(k) for k in (
        "unsupported_kinds", "claimed", "push_replayed", "quoted_from")}
    out["ticket_after"] = json.loads(
        dbl.paths.state("cvm", "pull.json").read_text(encoding="utf-8"))
    out["state_cvm_files"] = sorted(
        p.name for p in dbl.paths.state("cvm").parent.glob("cvm/*"))
    out["phone_turn"] = json.loads(
        dbl.paths.state("cvm", "phone_turn.json").read_text(encoding="utf-8"))

    # 3. inline pcm must be refused as a pointer violation
    clk2 = CvmPhoneClock(core, dbl.paths, client_id="cvm-phone-pcm",
                         push_request_id="probe-pcm",
                         grants=("device", "pcm"),
                         kinds={"device": {"status": "ok"},
                                "pcm": {"status": "ok", "bytes": "AAAA"}})
    clk2.requested = ("device", "pcm")
    try:
        from cvm_dt import FAST_READ_S, core_post
        core_post(core, "/api/v1/cvm/push", clk2._turn_body(), FAST_READ_S)
        out["pcm_inline"] = "ACCEPTED"
    except CvmDtError as e:
        out["pcm_inline"] = {"kind": str(e.kind), "detail": str(e)}

    # 4. dead core
    try:
        d = dead_loopback_base()
        CvmPhoneClock(CoreClient(d, "no-token"), dbl.paths,
                      client_id="cvm-phone-dead").cycle_once()
        out["dead"] = "NO REFUSAL"
    except CvmDtError as e:
        out["dead"] = {"kind": str(e.kind)}
finally:
    dbl.stop()

print(json.dumps(out, indent=1, default=str))
