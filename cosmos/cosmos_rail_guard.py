#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ApprovalGate in front of shell/git/install on coding rails.

SGH: wire guard on claude/codex/cursor before those kinds run.
HARDLINE never runs. CONFIRM needs a captain nonce. ALLOW runs.

    py -3.14 cosmos\\cosmos_rail_guard.py --selftest
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cosmos_approval import ApprovalError, ApprovalGate  # noqa: E402

DANGEROUS = frozenset({"shell", "git", "file_write", "file_delete", "install"})


def maybe_guard(ledger, payload, run, *, principal: str = "worker:rail"):
    p = payload if isinstance(payload, dict) else {}
    kind = str(p.get("kind") or "").strip().lower()
    if kind not in DANGEROUS:
        return run()
    action = {
        "kind": kind,
        "command": str(p.get("command") or p.get("prompt") or "")[:2000],
        "path": str(p.get("path") or "")[:500],
    }
    gate = ApprovalGate(ledger)
    return gate.guard(principal, action, run,
                      request_id=p.get("request_id"), nonce=p.get("nonce"))


def _selftest() -> int:
    import tempfile
    from cosmos_ledger import Ledger
    results = []

    def check(label, fn):
        try:
            results.append((label, bool(fn()), ""))
        except Exception as e:  # noqa: BLE001
            results.append((label, False, f"{type(e).__name__}: {e}"))

    d = Path(tempfile.mkdtemp(prefix="rg_")) / "a.jsonl"
    led = Ledger(d, b"rail-guard-selftest-key-0123", "core")
    ran = []
    rec = maybe_guard(led, {"prompt": "hello"}, lambda: ran.append("ok") or "ok")
    check("non-dangerous payload runs ungated", lambda: rec == "ok" and ran == ["ok"])
    try:
        maybe_guard(led, {"kind": "shell", "command": "rm -rf /"}, lambda: "no")
        results.append(("HARDLINE shell does not run", False, "did not"))
    except ApprovalError as e:
        results.append(("HARDLINE shell does not run", e.kind == "HARDLINE", e.kind))
    try:
        maybe_guard(led, {"kind": "git", "command": "git push origin ccr/x"},
                    lambda: "no")
        results.append(("CONFIRM git push needs approval", False, "did not"))
    except ApprovalError as e:
        results.append(("CONFIRM git push needs approval",
                        e.kind == "NEEDS_APPROVAL", e.kind))
    failed = [r for r in results if not r[1]]
    for label, ok, err in results:
        print(("PASS" if ok else "FAIL"), label, err)
    print("rail-guard selftest", f"{len(results)-len(failed)}/{len(results)}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(_selftest() if "--selftest" in sys.argv else 2)
