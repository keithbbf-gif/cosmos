#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Action-level hash chain + SoD (rkchoudary/hermes + OpenFang, COSMOS-shaped).

Ledger already chains state transitions. After the wipe we also chain ACTIONS.
creator ≠ reviewer ≠ approver. Not a second audit product.

    py -3.14 cosmos\\cosmos_action_chain.py --selftest
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

SCHEMA = "cosmos-action-chain/1"
EV = "ACTION"


class ActionError(RuntimeError):
    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


def _sha(obj) -> str:
    body = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(body).hexdigest()


def last_action_sha(ledger) -> str:
    sha = ""
    for rec in ledger.verify():
        if rec.get("event") == EV:
            sha = rec["payload"].get("action_sha") or ""
    return sha


def append_action(ledger, *, creator: str, reviewer: str, approver: str,
                  kind: str, detail: str, token: int | None = None) -> dict:
    roles = [str(creator), str(reviewer), str(approver)]
    if any(not r for r in roles):
        raise ActionError("SOD", "creator, reviewer, approver are required")
    if len(set(roles)) < 3:
        raise ActionError("SOD", "creator ≠ reviewer ≠ approver (SoD)")
    prev = last_action_sha(ledger)
    payload = {
        "schema": SCHEMA, "kind": str(kind)[:40], "detail": str(detail)[:500],
        "creator": creator, "reviewer": reviewer, "approver": approver,
        "prev_action_sha": prev, "token": token, "at": time.time(),
    }
    payload["action_sha"] = _sha({k: payload[k] for k in payload if k != "action_sha"})
    rec = ledger.append(EV, payload)
    return {"ok": True, "seq": rec["seq"], "action_sha": payload["action_sha"],
            "prev_action_sha": prev}


def snapshot(ledger) -> dict:
    """HTTP GET fold. Never mkdir. Empty chain is UNMEASURED, not invented."""
    try:
        rec = verify_actions(ledger)
    except ActionError as e:
        return {"schema": SCHEMA, "kind": e.kind, "ok": False,
                "error": e.kind, "detail": str(e)[:300]}
    rec["schema"] = SCHEMA
    rec["kind"] = "MEASURED" if rec.get("n") else "UNMEASURED"
    rec["note"] = "GET never mkdir. creator ≠ reviewer ≠ approver."
    return rec


def verify_actions(ledger) -> dict:
    prev, n = "", 0
    for rec in ledger.verify():
        if rec.get("event") != EV:
            continue
        p = rec["payload"]
        expect = _sha({k: p[k] for k in p if k != "action_sha"})
        if p.get("action_sha") != expect:
            raise ActionError("FORGED", f"seq {rec['seq']} action_sha mismatch")
        if p.get("prev_action_sha") != prev:
            raise ActionError("BROKEN_CHAIN", f"seq {rec['seq']} prev mismatch")
        prev = p["action_sha"]
        n += 1
    return {"ok": True, "n": n, "head": prev}


def _selftest() -> int:
    import tempfile

    from cosmos_ledger import Ledger
    results = []

    def check(label, fn):
        try:
            results.append((label, bool(fn()), ""))
        except Exception as e:  # noqa: BLE001
            results.append((label, False, f"{type(e).__name__}: {e}"))

    d = Path(tempfile.mkdtemp(prefix="act_")) / "a.jsonl"
    led = Ledger(d, b"action-chain-selftest-key0123", "core")
    try:
        append_action(led, creator="a", reviewer="a", approver="b",
                      kind="shell", detail="x")
        results.append(("SoD refuses shared role", False, "did not"))
    except ActionError as e:
        results.append(("SoD refuses shared role", e.kind == "SOD", e.kind))
    a1 = append_action(led, creator="worker:w1", reviewer="gitur:sonnet",
                       approver="captain:keith", kind="git", detail="push ccr/x")
    a2 = append_action(led, creator="worker:w2", reviewer="gitur:glm",
                       approver="ccr:716fbaea", kind="file_write",
                       detail="work_orders/ccr/x.md")
    v = verify_actions(led)
    check("two actions chain", lambda: v["n"] == 2 and v["head"] == a2["action_sha"])
    check("second action points at first",
          lambda: a2["prev_action_sha"] == a1["action_sha"])
    snap = snapshot(led)
    check("snapshot is MEASURED n=2",
          lambda: snap["kind"] == "MEASURED" and snap["n"] == 2)
    failed = [r for r in results if not r[1]]
    for label, ok, err in results:
        print(("PASS" if ok else "FAIL"), label, err)
    print("action-chain selftest", f"{len(results)-len(failed)}/{len(results)}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(_selftest() if "--selftest" in sys.argv else 2)
