#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest: REST-1/2/3 guard hardening (argv confinement, read-only kernel,
return-validation wired into acceptance). Refusals BY KIND; every guard has a
POSITIVE and a NEGATIVE control."""
from __future__ import annotations
import json, sys, tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "cosmos"))
from cosmos_sched import Scheduler
from cosmos_runner import Runner
from cosmos_kernel import Kernel, install
from cosmos_paths import CosmosPathError
from cosmos_validate import ValidateError

RESULTS = []

def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:                                            # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))

def expect(exc, kind):
    def wrap(f):
        def inner():
            try:
                f()
            except exc as e:
                return e.kind == kind
            return False
        return inner
    return wrap


def main() -> int:
    td = Path(tempfile.mkdtemp(prefix="cosmos_rest_"))
    KEY = b"rest-guards-key"

    # ================= REST-1: argv: confined like py: (K4 bypass) =================
    tools = td / "work" / "cosmos"
    tools.mkdir(parents=True, exist_ok=True)
    s = Scheduler(td / "q", KEY, "F5")
    runner = Runner(s, td / "work", "F5")
    runner.tools_root = tools

    inside = tools / "ok.py"
    inside.write_text("print('inside-ok')\n", encoding="utf-8")
    outside = td / "evil.py"
    outside.write_text("print('pwned')\n", encoding="utf-8")
    helper = tools / "_help.py"
    helper.write_text("print('never')\n", encoding="utf-8")

    # NOTE: use sys.executable, not "python3" - the agent tested in a Linux container
    # where python3 exists; on the native Windows target the launcher is `py` and
    # `python3` is not a runnable command, so the confinement (correctly None) passed
    # but EXECUTION failed. sys.executable is the real interpreter on either platform.
    import sys as _sys
    j_ok = s.submit("argv:" + json.dumps([_sys.executable, str(inside)]), "normal")
    r_ok = runner.run_one()
    check("REST-1 POSITIVE: argv: script UNDER tools_root is accepted and CLEAN",
          lambda: r_ok["outcome"] == "CLEAN" and not r_ok.get("traversal_refused"))

    j_out = s.submit("argv:" + json.dumps(["python3", str(outside)]), "high")
    r_out = runner.run_one()
    check("REST-1 NEGATIVE: argv: script OUTSIDE tools_root -> traversal_refused "
          "(K4 bypass closed)",
          lambda: r_out["outcome"] == "BROKE" and r_out.get("traversal_refused"))
    check("REST-1 NEGATIVE: the outside argv job never ran (no attempt log)",
          lambda: not (td / "work" / j_out).exists() or
          not any((td / "work" / j_out).rglob("attempt.log")))

    j_bin = s.submit("argv:" + json.dumps(["/bin/echo", "pwned"]), "normal")
    r_bin = runner.run_one()
    check("REST-1 NEGATIVE: argv: host binary outside tools_root is refused",
          lambda: r_bin["outcome"] == "BROKE" and r_bin.get("traversal_refused"))

    j_h = s.submit("argv:" + json.dumps(["python3", str(helper)]), "normal")
    r_h = runner.run_one()
    check("REST-1 NEGATIVE: argv: `_`-helper is refused (same convention as py:)",
          lambda: r_h["outcome"] == "BROKE" and r_h.get("helper_refused"))

    j_c = s.submit("argv:" + json.dumps([_sys.executable, "-c", "print('dash-c-ok')"]),
                   "normal")
    r_c = runner.run_one()
    check("REST-1 POSITIVE: argv: whitelisted interpreter + -c still runs "
          "(no path to confine)",
          lambda: r_c["outcome"] == "CLEAN")

    # ================= REST-2: read_only is non-mutating =================
    root = td / "Cosmos"
    install(root, tree_id="rest-2")
    ledger_dir = root / "ledger"
    check("REST-2 setup: installer created the ledger role dir",
          lambda: ledger_dir.is_dir())
    ledger_dir.rmdir()
    kr = Kernel(root, worker="ro-mkdir", read_only=True)
    check("REST-2 NEGATIVE: read_only Kernel does NOT mkdir a missing ledger dir",
          lambda: not ledger_dir.exists())
    check("REST-2 NEGATIVE: read_only worker does NOT mkdir a mail inbox",
          lambda: not (root / "state" / "mail" / "ro-mkdir" / "inbox").exists())
    # audit on a reader must not crash when the inbox was never created
    a0 = kr.audit()
    check("REST-2 POSITIVE: read_only audit still answers (mail unread is 0, "
          "not a crash)",
          lambda: a0["mail"]["my_unread"] == 0 and a0["ledger"]["chain"] == "VERIFIED")

    kw = Kernel(root, worker="writer-mkdir")
    check("REST-2 POSITIVE: writing Kernel DOES mkdir the ledger dir",
          lambda: ledger_dir.is_dir())
    check("REST-2 POSITIVE: writing worker DOES register a mail inbox",
          lambda: (root / "state" / "mail" / "writer-mkdir" / "inbox").is_dir())

    # lease expiry writes: plant a short lease, advance the clock, prove the
    # reader observes expiry WITHOUT appending EXPIRE; the writer does write.
    fake = [1000.0]
    root2 = td / "CosmosLease"
    install(root2, tree_id="rest-2-lease")
    kw2 = Kernel(root2, worker="holder", clock=lambda: fake[0])
    kw2.arbiter.acquire("tree", "holder", ttl=50.0)     # expires at 1050
    lease_file = kw2.paths.ledger("leases.jsonl")
    bytes_before = lease_file.read_bytes()
    fake[0] = 2000.0
    kr2 = Kernel(root2, worker="ro-lease", read_only=True, clock=lambda: fake[0])
    a_ro = kr2.audit()
    check("REST-2 NEGATIVE: read_only audit reports the expired lease as not live",
          lambda: a_ro["leases_live"] == 0)
    check("REST-2 NEGATIVE: read_only audit does NOT write an EXPIRE event "
          "(lease file bytes unchanged)",
          lambda: lease_file.read_bytes() == bytes_before)
    check("REST-2 NEGATIVE: read_only arbiter.append REFUSES (typed)",
          expect(CosmosPathError, "NOT_FOUND")(
              lambda: kr2.arbiter._append({"event": "EXPIRE", "resource": "tree"})))

    kw3 = Kernel(root2, worker="reaper", clock=lambda: fake[0])
    live = kw3.arbiter.status("tree")
    check("REST-2 POSITIVE: writing kernel expires the dead lease and WRITES EXPIRE",
          lambda: live is None and any(e.get("event") == "EXPIRE"
                                      for e in kw3.arbiter.events()))

    # ================= REST-3: validation is the acceptance gate =================
    root3 = td / "CosmosRet"
    install(root3, tree_id="rest-3")
    k = Kernel(root3, worker="core")
    jid = k.sched.submit("return-job", "normal")
    k.sched.claim_next()

    check("REST-3 NEGATIVE: empty claims -> UNVALIDATED (unvalidated return refused)",
          expect(ValidateError, "UNVALIDATED")(
              lambda: k.accept_return("r-empty", [], job_id=jid, outcome="CLEAN")))
    check("REST-3 NEGATIVE: unvalidated return does NOT complete the job "
          "(state still RUNNING)",
          lambda: k.sched._state()[jid]["st"] == "RUNNING")

    check("REST-3 NEGATIVE: failed path_exists -> FAILED_VALIDATION",
          expect(ValidateError, "FAILED_VALIDATION")(
              lambda: k.accept_return(
                  "r-missing",
                  [{"validator": "path_exists",
                    "path": str(td / "never_written.txt")}],
                  job_id=jid, outcome="CLEAN")))
    check("REST-3 NEGATIVE: a failed return still does not affect job state",
          lambda: k.sched._state()[jid]["st"] == "RUNNING")
    check("REST-3 NEGATIVE: no JOB_DONE landed (the projection was not touched)",
          lambda: not any(r["event"] == "JOB_DONE" for r in k.sched.ledger.verify()))
    check("REST-3 NEGATIVE: both refusals are LEDGERED as RETURN_REFUSED",
          lambda: {r["payload"].get("rid")
                   for r in k.ledger.verify() if r["event"] == "RETURN_REFUSED"}
          >= {"r-empty", "r-missing"})

    real = td / "really_here.txt"
    real.write_text("present on disk", encoding="utf-8")
    accepted = k.accept_return(
        "r-ok", [{"validator": "path_exists", "path": str(real)}],
        job_id=jid, outcome="FINDINGS", detail="validated return")
    check("REST-3 POSITIVE: a validated return is accepted",
          lambda: accepted["rid"] == "r-ok" and accepted["checks"][0]["ok"])
    check("REST-3 POSITIVE: only AFTER validation does the job leave RUNNING",
          lambda: k.sched._state()[jid]["st"] == "FINDINGS")
    check("REST-3 POSITIVE: RETURN_VALIDATED is ledgered on the authority chain",
          lambda: any(r["event"] == "RETURN_VALIDATED"
                      and r["payload"].get("rid") == "r-ok"
                      for r in k.ledger.verify()))

    check("REST-3 NEGATIVE: read_only kernel refuses accept_return (typed)",
          expect(CosmosPathError, "NOT_FOUND")(
              lambda: Kernel(root3, worker="ro-ret", read_only=True).accept_return(
                  "r-ro", [{"validator": "path_exists", "path": str(real)}])))

    bad = [(l, e) for l, ok, e in RESULTS if not ok]
    for label, ok, err in RESULTS:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label,
                              ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks (REST-1 argv confinement, REST-2 read-only "
          "non-mutation, REST-3 validation-before-state; + and - controls)"
          % ("PASS" if not bad else "FAIL", len(RESULTS)))
    return 0 if not bad else 1


def test_rest_guards():
    assert main() == 0


if __name__ == "__main__":
    sys.exit(main())