#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Temporal graph fold — Graphiti mechanism, ledger authority.

Entities/edges with valid_at / invalid_at. Invalidate, never delete
(same ethic as _delme). Rebuildable projection. Not Letta Server.

    py -3.14 cosmos\\cosmos_temporal_fold.py --selftest
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

SCHEMA = "cosmos-temporal-fold/1"
EV_FACT, EV_INVALID = "TEMPORAL_FACT", "TEMPORAL_INVALID"


class TemporalError(RuntimeError):
    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


def _fold(s: dict, rec: dict) -> dict:
    ev, p = rec.get("event"), rec.get("payload") or {}
    fid = p.get("fact_id")
    if ev == EV_FACT and fid:
        s["facts"][fid] = {
            "subject": p.get("subject"), "rel": p.get("rel"),
            "object": p.get("object"), "valid_at": p.get("valid_at"),
            "invalid_at": None, "seq": rec.get("seq"),
        }
    elif ev == EV_INVALID and fid in s["facts"]:
        s["facts"][fid]["invalid_at"] = p.get("invalid_at")
    return s


def snapshot(ledger, *, at=None) -> dict:
    at = float(at if at is not None else time.time())
    if hasattr(ledger, "fold_cached"):
        st = ledger.fold_cached("cosmos_temporal.v1", _fold, lambda: {"facts": {}})
    else:
        st = {"facts": {}}
        for rec in ledger.verify():
            _fold(st, rec)
    live, gone = [], []
    for fid, f in st["facts"].items():
        row = {"fact_id": fid, **f}
        inv = f.get("invalid_at")
        if inv is None or float(inv) > at:
            live.append(row)
        else:
            gone.append(row)
    return {"schema": SCHEMA, "kind": "MEASURED" if st["facts"] else "UNMEASURED",
            "at": at, "live": live, "invalidated": gone,
            "note": "invalidate ≠ delete. Ledger is authority. GET never mkdir."}


def assert_fact(ledger, fact_id: str, subject: str, rel: str, obj: str,
                *, valid_at=None) -> dict:
    if not str(fact_id or "").strip():
        raise TemporalError("BAD_FACT", "fact_id is required")
    ledger.append(EV_FACT, {
        "schema": SCHEMA, "fact_id": fact_id, "subject": subject, "rel": rel,
        "object": obj, "valid_at": float(valid_at if valid_at is not None else time.time()),
    })
    return snapshot(ledger)


def invalidate(ledger, fact_id: str, *, invalid_at=None) -> dict:
    st = snapshot(ledger)
    if not any(f["fact_id"] == fact_id for f in st["live"]):
        raise TemporalError("NOT_FOUND", f"no live fact {fact_id!r}")
    ledger.append(EV_INVALID, {
        "schema": SCHEMA, "fact_id": fact_id,
        "invalid_at": float(invalid_at if invalid_at is not None else time.time()),
    })
    return snapshot(ledger)


def _selftest() -> int:
    import tempfile
    from cosmos_ledger import Ledger
    results = []

    def check(label, fn):
        try:
            results.append((label, bool(fn()), ""))
        except Exception as e:  # noqa: BLE001
            results.append((label, False, f"{type(e).__name__}: {e}"))

    d = Path(tempfile.mkdtemp(prefix="tmpf_")) / "a.jsonl"
    led = Ledger(d, b"temporal-fold-selftest-key01", "core")
    clock = [1000.0]
    assert_fact(led, "f1", "scar:wipe", "caused", "sandbox-escape", valid_at=clock[0])
    s1 = snapshot(led, at=1001)
    check("fact is live", lambda: len(s1["live"]) == 1 and not s1["invalidated"])
    invalidate(led, "f1", invalid_at=2000)
    s2 = snapshot(led, at=1500)
    check("before invalid_at the fact is still live",
          lambda: len(s2["live"]) == 1)
    s3 = snapshot(led, at=2001)
    check("after invalid_at the fact is invalidated, not deleted",
          lambda: not s3["live"] and s3["invalidated"][0]["fact_id"] == "f1")
    failed = [r for r in results if not r[1]]
    for label, ok, err in results:
        print(("PASS" if ok else "FAIL"), label, err)
    print("temporal-fold selftest", f"{len(results)-len(failed)}/{len(results)}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(_selftest() if "--selftest" in sys.argv else 2)
