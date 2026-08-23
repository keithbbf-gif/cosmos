#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest: cosmos_tools (the tool contract registry). Refusals BY KIND; a failing
check both raises AND lands in the ledger; a tool with no check can never pass by
omission; disposition is a recorded decision, never a drift; verify_all isolates
failures so one broken contract cannot hide the state of the others."""
from __future__ import annotations
import sys, tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cosmos_ledger import Ledger
from cosmos_tools import ToolContracts, ToolsError

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
    td = Path(tempfile.mkdtemp(prefix="cosmos_tl_"))
    KEY = b"k"

    fake = [1000.0]
    led = Ledger(td / "tools.jsonl", KEY, "F5", clock=lambda: fake[0])
    tc = ToolContracts(led, clock=lambda: fake[0])

    # ================= POSITIVE PATH =================
    tc.declare("sgh.ask", ["ask"], "one prompt in, one priced answer out, spend ledgered")
    tc.declare("gdx.put", ["put", "list"], "file lands in QA_REVIEW and is listable back")
    tc.attach_check("sgh.ask", lambda: (True, "round-trip 42ms"))
    r = tc.verify("sgh.ask")
    check("declare -> attach -> verify passes and returns detail",
          lambda: r["ok"] and r["detail"] == "round-trip 42ms")
    check("passing check ledgered as TOOL_CONTRACT_OK",
          lambda: any(x["event"] == "TOOL_CONTRACT_OK"
                      and x["payload"]["name"] == "sgh.ask" for x in led.verify()))
    fake[0] += 60
    rows = {row["name"]: row for row in tc.report()}
    check("report shows AGE on the verified tool (dated, not just true)",
          lambda: rows["sgh.ask"]["verified"] is True and rows["sgh.ask"]["age_s"] == 60)
    check("never-verified tool reports verified=None - UNKNOWN, never True",
          lambda: rows["gdx.put"]["verified"] is None and rows["gdx.put"]["age_s"] is None)

    # ================= REFUSALS BY KIND =================
    check("duplicate declare REFUSES - a second declaration is a drift",
          expect(ToolsError, "DUPLICATE")(
              lambda: tc.declare("sgh.ask", ["ask"], "again")))
    check("disposition on unknown tool -> UNKNOWN_TOOL",
          expect(ToolsError, "UNKNOWN_TOOL")(
              lambda: tc.disposition("nope", "PRESERVED", "it does not exist")))
    check("bad decision -> BAD_DISPOSITION",
          expect(ToolsError, "BAD_DISPOSITION")(
              lambda: tc.disposition("sgh.ask", "SHRUGGED", "not a ruling")))
    check("no check attached -> CONTRACT_FAIL (an unverifiable contract is a claim)",
          expect(ToolsError, "CONTRACT_FAIL")(lambda: tc.verify("gdx.put")))
    check("...and the refusal ledgered NOTHING - nothing was measured",
          lambda: not any(x["payload"].get("name") == "gdx.put"
                          for x in led.verify()
                          if x["event"] in ("TOOL_CONTRACT_OK", "TOOL_CONTRACT_FAIL")))

    tc.declare("origin.export", ["export"], "OPJ in, publication-grade figure out")
    tc.attach_check("origin.export", lambda: (False, "COM server not reachable"))
    check("failing check -> CONTRACT_FAIL raised",
          expect(ToolsError, "CONTRACT_FAIL")(lambda: tc.verify("origin.export")))
    check("...and the failure LANDED IN THE LEDGER, not just the exception",
          lambda: any(x["event"] == "TOOL_CONTRACT_FAIL"
                      and x["payload"]["name"] == "origin.export"
                      and "COM server" in x["payload"]["detail"] for x in led.verify()))
    check("failed tool reports verified=False, dated",
          lambda: next(r for r in tc.report() if r["name"] == "origin.export")
          ["verified"] is False)

    # ================= DISPOSITION IS A RECORDED DECISION =================
    tc.disposition("gdx.put", "ADAPTED",
                   "contract kept, transport moved from Drive connector to queue runner")
    st = tc.state()
    check("disposition ADAPTED with reason lands in state, dated",
          lambda: st["gdx.put"]["disposition"]["decision"] == "ADAPTED"
          and "queue runner" in st["gdx.put"]["disposition"]["reason"]
          and st["gdx.put"]["disposition"]["t"] > 0)
    check("disposition surfaces in report",
          lambda: next(r for r in tc.report() if r["name"] == "gdx.put")
          ["disposition"] == "ADAPTED")

    # ================= verify_all ISOLATES FAILURES =================
    out = tc.verify_all()
    check("verify_all never raises and covers every declared tool",
          lambda: set(out) == {"sgh.ask", "gdx.put", "origin.export"})
    check("verify_all: the passing tool still passes",
          lambda: out["sgh.ask"]["ok"] is True)
    check("verify_all: the failing and the unverifiable both recorded ok=False",
          lambda: out["origin.export"]["ok"] is False and out["gdx.put"]["ok"] is False)
    check("verify_all ledgered the no-check refusal per-tool (UNVERIFIABLE)",
          lambda: any(x["event"] == "TOOL_CONTRACT_FAIL"
                      and x["payload"]["name"] == "gdx.put"
                      and "UNVERIFIABLE" in x["payload"]["detail"] for x in led.verify()))

    bad = [(l, e) for l, ok, e in RESULTS if not ok]
    for label, ok, err in RESULTS:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label, ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks (registration is not capability; only a dated "
          "passing check is)" % ("PASS" if not bad else "FAIL", len(RESULTS)))
    return 0 if not bad else 1


def test_tools():
    assert main() == 0


if __name__ == "__main__":
    sys.exit(main())
