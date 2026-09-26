#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Chamber presence — rooms/boards as a ledger projection.

Agent Chamber + agent-comms mechanisms. Not a second scheduler.
COW orchestrates (P9). Agents propose; CCr disposes (P10).
GET never mkdir.

    py -3.14 cosmos\\cosmos_chamber.py --selftest
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

SCHEMA = "cosmos-chamber/1"
ROOMS = ("Cm", "plumbing", "physics", "chapter")  # legal: GFO + Captain only
EV_JOIN, EV_LEAVE, EV_POST, EV_TICKET = (
    "CHAMBER_JOIN", "CHAMBER_LEAVE", "CHAMBER_POST", "CHAMBER_TICKET")


class ChamberError(RuntimeError):
    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


def _fold(s: dict, rec: dict) -> dict:
    ev, p = rec.get("event"), rec.get("payload") or {}
    room = p.get("room")
    if ev == EV_JOIN and room:
        s["rooms"].setdefault(room, {"presence": {}, "posts": [], "tickets": []})
        s["rooms"][room]["presence"][p.get("principal") or ""] = {
            "at": p.get("at"), "family": p.get("family") or ""}
    elif ev == EV_LEAVE and room in s["rooms"]:
        s["rooms"][room]["presence"].pop(p.get("principal") or "", None)
    elif ev == EV_POST and room in s["rooms"]:
        s["rooms"][room]["posts"].append({
            "principal": p.get("principal"), "text": str(p.get("text") or "")[:400],
            "at": p.get("at"), "seq": rec.get("seq")})
        s["rooms"][room]["posts"] = s["rooms"][room]["posts"][-50:]
    elif ev == EV_TICKET and room in s["rooms"]:
        s["rooms"][room]["tickets"].append({
            "id": p.get("ticket_id"), "title": p.get("title"),
            "state": p.get("state") or "OPEN", "at": p.get("at")})
    return s


def snapshot(ledger, room: str = "Cm") -> dict:
    room = str(room or "Cm")
    if room not in ROOMS:
        raise ChamberError("STREAM_REFUSED", f"room {room!r} is not on this deck")
    if hasattr(ledger, "fold_cached"):
        st = ledger.fold_cached("cosmos_chamber.v1", _fold,
                                lambda: {"rooms": {}})
    else:
        st = {"rooms": {}}
        for rec in ledger.verify():
            _fold(st, rec)
    r = st["rooms"].get(room) or {"presence": {}, "posts": [], "tickets": []}
    return {
        "schema": SCHEMA, "room": room, "kind": "MEASURED" if r["presence"] or r["posts"]
        or r["tickets"] else "UNMEASURED",
        "presence": r["presence"], "posts": r["posts"][-20:],
        "tickets": r["tickets"][-20:],
        "note": "projection of CHAMBER_* events. No daemon. P9/P10 stay.",
    }


def join(ledger, room: str, principal: str, family: str = "") -> dict:
    if room not in ROOMS:
        raise ChamberError("STREAM_REFUSED", f"room {room!r}")
    if not str(principal or "").strip():
        raise ChamberError("BAD_PRINCIPAL", "principal is required")
    ledger.append(EV_JOIN, {"schema": SCHEMA, "room": room,
                            "principal": principal, "family": family,
                            "at": time.time()})
    return snapshot(ledger, room)


def _selftest() -> int:
    import tempfile
    from cosmos_ledger import Ledger
    results = []

    def check(label, fn):
        try:
            results.append((label, bool(fn()), ""))
        except Exception as e:  # noqa: BLE001
            results.append((label, False, f"{type(e).__name__}: {e}"))

    d = Path(tempfile.mkdtemp(prefix="chm_")) / "a.jsonl"
    led = Ledger(d, b"chamber-selftest-key-01234567", "core")
    empty = snapshot(led, "Cm")
    check("empty chamber is UNMEASURED and created no extra files",
          lambda: empty["kind"] == "UNMEASURED" and empty["presence"] == {}
          and not d.exists())
    join(led, "Cm", "seat:native:glm", family="z-ai")
    join(led, "Cm", "seat:openwork:gfo", family="gfo")
    snap = snapshot(led, "Cm")
    check("two families present after join",
          lambda: set(snap["presence"]) == {"seat:native:glm", "seat:openwork:gfo"})
    try:
        snapshot(led, "legal")
        results.append(("legal room REFUSED", False, "did not"))
    except ChamberError as e:
        results.append(("legal room REFUSED", e.kind == "STREAM_REFUSED", e.kind))
    failed = [r for r in results if not r[1]]
    for label, ok, err in results:
        print(("PASS" if ok else "FAIL"), label, err)
    print("chamber selftest", f"{len(results)-len(failed)}/{len(results)}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(_selftest() if "--selftest" in sys.argv else 2)
