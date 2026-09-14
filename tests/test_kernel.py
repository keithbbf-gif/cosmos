#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest: the composed kernel - install -> boot -> fenced write -> audit -> refusals."""
from __future__ import annotations
import sys, tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "cosmos"))
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
    check("four-phase write leaves no staged .part residue beside the target",
          lambda: not [p for p in out.parent.iterdir() if ".part" in p.name])
    check("the install is ledgered as a fenced COMMIT with a reservation before it",
          lambda: (lambda ev: "COMMIT_RESERVED" in ev and "COMMIT" in ev
                   and ev.index("COMMIT_RESERVED") < ev.index("COMMIT"))(
              [e["event"] for e in k.arbiter.events()]))

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
    check("kernel mail is composed on the arbiter (F-55 lock seam)",
          lambda: k.mail.arbiter is k.arbiter)
    check("kernel mail send COMMITs mail:critic (fenced, one writer)",
          lambda: any(e.get("event") == "COMMIT"
                      and e.get("resource") == "mail:critic"
                      for e in k.arbiter.events()))
    check("kernel mail note is signed with the install key",
          lambda: peer.unread()[0].get("signed") is True
          and peer.unread()[0].get("prev_hash") == "0" * 64)

    # ---- F-29 tools/ surface composed on writing boot (no invoke) ----
    composed = list((k.rails_compose or {}).get("composed") or [])
    check("tools-surface compose row landed on writing boot",
          lambda: "tools-surface" in composed)
    check("kernel.tools inventory is a declaration (xai-docs, openai-docs)",
          lambda: k.tools is not None
          and {r["name"] for r in k.tools.inventory()}
          == {"xai-docs", "openai-docs"})
    check("tools-surface compose did not invoke (boot is not a probe)",
          lambda: (k.tools_compose or {}).get("invoked") is False)

    # ---- F-30 forge rails composed on writing boot (adapters, not proven) ----
    check("forge-rails compose row landed on writing boot",
          lambda: "forge-rails" in composed)
    check("gem-api native vertex adapter composed on writing boot",
          lambda: "gem-api" in composed
          and getattr(k, "gem_rail", None) is not None)
    check("gdx-drive compose row landed on writing boot (adapter, not proven)",
          lambda: "gdx-drive" in composed and "gdx-drive" in k.adapters)
    check("gdx-drive adapter is dst=drive (cannot capture core->models)",
          lambda: getattr(k.adapters.get("gdx-drive"), "spec", {}).get("dst")
          == "drive")
    check("forge adapters attached (github-forge + gitlab-forge)",
          lambda: {"github-forge", "gitlab-forge"} <= set(k.adapters))
    check("forge adapters are dst=forge (cannot capture core->code)",
          lambda: all(getattr(k.adapters[lid], "spec", {}).get("dst") == "forge"
                      for lid in ("github-forge", "gitlab-forge")
                      if lid in k.adapters))

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