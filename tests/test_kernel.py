#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest: the composed kernel - install -> boot -> fenced write -> audit -> refusals."""
from __future__ import annotations
import sys, tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cosmos_kernel import Kernel, install
from cosmos_paths import CosmosPathError
from cosmos_lock import LockError

RESULTS = []

def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:                                            # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


def main() -> int:
    td = Path(tempfile.mkdtemp(prefix="cosmos_k_"))
    root = td / "Cosmos"                       # settable, non-default name on purpose

    # ---- install like normal software ----
    install(root, tree_id="spike-install-1")
    check("installer stands up a bootable root", lambda: (root / ".cosmos-root.json").exists())

    # ---- boot ----
    k = Kernel(root, worker="core-a")
    check("kernel boots READY on a verified root", lambda: k.ready)
    check("boot left a ledgered record", lambda: k.ledger.last()["event"] != None)

    # ---- fenced protected write ----
    out = k.protected_write("tree", "notes/hello.txt", "cosmos v1")
    check("fenced write lands", lambda: out.read_text(encoding="utf-8") == "cosmos v1")
    check("write is ledgered with worker identity",
          lambda: any(r["event"] == "PROTECTED_WRITE" and r["payload"]["worker"] == "core-a"
                      for r in k.ledger.verify()))

    # ---- end-to-end job through the composed kernel ----
    jid = k.sched.submit("echo hello", "high")
    m = k.sched.claim_next()
    k.sched.done(jid, "CLEAN")
    check("submit->claim->done through the kernel", lambda: m["job_id"] == jid)

    # ---- mail through the kernel ----
    from cosmos_mail import Mailbox
    peer = Mailbox(k.paths.role("state", "mail"), "critic")
    peer.register()
    mid = k.mail.send("critic", "review", "check my work")
    check("kernel mail send + peer unread", lambda: peer.unread()[0]["id"] == mid)

    # ---- audit answers with measured state ----
    a = k.audit()
    check("audit: ledger chain VERIFIED", lambda: a["ledger"]["chain"] == "VERIFIED")
    check("audit: jobs projected by state", lambda: a["jobs"].get("CLEAN") == 1)
    check("audit carries its measurement time", lambda: a["measured_at_epoch"] > 0)

    # ---- refusals ----
    check("kernel on an uninstalled root REFUSES (typed)",
          (lambda: (lambda f: f())(lambda: _expect_path(td / "nothere"))))
    l1 = k.arbiter.acquire("tree", "core-a")
    check("second lease on held resource -> HELD",
          (lambda: _expect_lock(k)))
    k.arbiter.release(l1)

    # ---- second kernel on the SAME root replays the same authority ----
    k2 = Kernel(root, worker="core-b")
    check("restarted kernel verifies the same chain and continues it",
          lambda: k2.ledger.last()["event"] == "BOOT_VERIFIED")

    bad = [(l, e) for l, ok, e in RESULTS if not ok]
    for label, ok, err in RESULTS:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label, ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks" % ("PASS" if not bad else "FAIL", len(RESULTS)))
    return 0 if not bad else 1


def _expect_path(root) -> bool:
    try:
        Kernel(root)
    except CosmosPathError as e:
        return e.kind == "NOT_FOUND"
    return False


def _expect_lock(k) -> bool:
    try:
        k.arbiter.acquire("tree", "intruder")
    except LockError as e:
        return e.kind == "HELD"
    return False


def test_kernel():
    assert main() == 0


if __name__ == "__main__":
    sys.exit(main())