#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest: the command seam - text in, kernel actions out, refusals typed + ledgered."""
from __future__ import annotations
import sys, tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cosmos_kernel import Kernel, install
from cosmos_command import Commander, CommandError, FORBIDDEN

RESULTS = []

def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:                                            # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


def main() -> int:
    td = Path(tempfile.mkdtemp(prefix="cosmos_c_"))
    root = td / "Cosmos"

    # ---- install + boot, same as any consumer of the kernel ----
    install(root, tree_id="spike-command-1")
    k = Kernel(root, worker="voice-a")
    c = Commander(k)

    # ---- the read commands ----
    r = c.handle("status")
    check("status: ok + READY + root identity",
          lambda: r["ok"] and r["ready"] and r["tree_id"] == "spike-command-1")
    check("status: ledger head is present", lambda: r["ledger_head"]["seq"] >= 1)
    a = c.handle("AUDIT")                      # case-insensitive first word
    check("audit (any case): chain VERIFIED", lambda: a["ledger"]["chain"] == "VERIFIED")
    check("jobs: empty projection before any submit",
          lambda: c.handle("jobs")["jobs"] == {})
    check("help: teaches the submit grammar",
          lambda: any(l.startswith("submit") for l in c.handle("help")["commands"]))

    # ---- submit creates a claimable job ----
    s = c.handle("submit high echo hello")
    m = k.sched.claim_next()
    check("submit high -> claimable job with the same id",
          lambda: m is not None and m["job_id"] == s["job_id"])
    check("claimed job carries the spoken command", lambda: m["command"] == "echo hello")

    # ---- submit parse: a command that CONTAINS a priority word is not mis-split ----
    s2 = c.handle("submit high review this high priority patch")
    m2 = k.sched.claim_next()
    check("submit: priority words inside the command stay in the command",
          lambda: m2 is not None and m2["job_id"] == s2["job_id"]
          and m2["command"] == "review this high priority patch"
          and m2["priority"] == "high")
    s3 = c.handle('submit critical "deploy with high availability"')
    m3 = k.sched.claim_next()
    check("submit: a quoted command containing a priority word is not mis-split",
          lambda: m3 is not None and m3["command"] == "deploy with high availability"
          and m3["priority"] == "critical")
    check("submit: last-word 'high' is NOT stolen as the priority (echo high)",
          lambda: _expect(c, "submit echo high", "BAD_ARGS"))
    check("submit: unclosed quote REFUSES (never guessed)",
          lambda: _expect(c, 'submit high "echo hello', "BAD_ARGS"))

    # ---- refusals, each with its typed kind ----
    check("bad priority -> BAD_ARGS that teaches the grammar",
          lambda: _expect(c, "submit urgent echo hi", "BAD_ARGS"))
    check("missing command -> BAD_ARGS", lambda: _expect(c, "submit high", "BAD_ARGS"))
    check("unknown verb -> UNKNOWN_COMMAND, never a guess",
          lambda: _expect(c, "reboot now", "UNKNOWN_COMMAND"))
    check("'delete everything' -> REFUSED (never-delete canon)",
          lambda: _expect(c, "delete everything", "REFUSED"))
    check("every FORBIDDEN verb refuses",
          lambda: all(_expect(c, v + " x", "REFUSED") for v in FORBIDDEN))

    # ---- the ledger saw all of it ----
    events = list(k.ledger.verify())
    check("refusal is ledgered as COMMAND_REFUSED",
          lambda: any(e["event"] == "COMMAND_REFUSED"
                      and e["payload"]["text"].startswith("delete")
                      for e in events))
    check("handled commands are ledgered with ok flags",
          lambda: any(e["event"] == "COMMAND_HANDLED" and e["payload"]["ok"]
                      for e in events)
          and any(e["event"] == "COMMAND_HANDLED" and not e["payload"]["ok"]
                  for e in events))

    bad = [(l, e) for l, ok, e in RESULTS if not ok]
    for label, ok, err in RESULTS:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label, ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks" % ("PASS" if not bad else "FAIL", len(RESULTS)))
    return 0 if not bad else 1


def _expect(c, text, kind) -> bool:
    try:
        c.handle(text)
    except CommandError as e:
        return e.kind == kind
    return False


def test_command():
    assert main() == 0


if __name__ == "__main__":
    sys.exit(main())
