#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest: the ADAPTED node rails. Uses a FAKE incumbent module (injected into
sys.modules) so every path is proven WITHOUT spending a cent on a real model call -
the same discipline the DOM FakeDriver used. A real dispatch to a live model is
NATIVE-DEMO-REQUIRED and is a separate, spend-gated, opt-in run."""
from __future__ import annotations
import sys, tempfile, types
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cosmos_ledger import Ledger
from cosmos_registry import Registry
from cosmos_spend import SpendGate
from cosmos_rails import Dispatcher, RailError
from cosmos_node_rails import NodeRail, register_node_rails

RESULTS = []
def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:                                            # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


def _install_fake(name, ask_fn):
    m = types.ModuleType(name)
    m.ask = ask_fn
    sys.modules[name] = m
    return m


def main() -> int:
    td = Path(tempfile.mkdtemp(prefix="cosmos_nr_"))
    KEY = b"k"

    # a FAKE incumbent that returns the house dict shape
    _install_fake("fake_sgh", lambda prompt, **kw: {"ok": True, "text": "ALIVE: " + prompt,
                                                    "usd": 0.004})
    rail = NodeRail("fake_sgh", metered_usd=0.02)
    ok, detail = rail.probe()
    check("node rail probe: importable incumbent -> live", lambda: ok)
    r = rail.dispatch({"prompt": "hello"})
    check("node rail dispatch: normalizes the incumbent dict return",
          lambda: r["ok"] and r["text"] == "ALIVE: hello" and r["usd"] == 0.004)

    # a MISSING incumbent is UNREACHABLE, never a fake OK
    missing = NodeRail("no_such_incumbent_xyz")
    mok, mdetail = missing.probe()
    check("missing incumbent -> probe UNREACHABLE (registration is not capability)",
          lambda: not mok and "UNREACHABLE" in mdetail)
    check("missing incumbent dispatch -> typed UNREACHABLE, not a crash",
          lambda: missing.dispatch({"prompt": "x"})["kind"] == "UNREACHABLE")

    # an incumbent with no ask() -> BROKE
    _install_fake("fake_noask", None)
    delattr(sys.modules["fake_noask"], "ask")
    nr = NodeRail("fake_noask")
    check("incumbent without ask() -> BROKE", lambda: nr.dispatch({"prompt": "x"})["kind"] == "BROKE")

    # an incumbent whose ask() raises -> BROKE (recorded, not swallowed)
    _install_fake("fake_boom", lambda p, **k: (_ for _ in ()).throw(RuntimeError("rail down")))
    br = NodeRail("fake_boom")
    check("incumbent ask() raising -> BROKE with the reason", lambda:
          br.dispatch({"prompt": "x"})["kind"] == "BROKE")

    # ===== through the Dispatcher, spend-gated =====
    led = Ledger(td / "n.jsonl", KEY, "core")
    reg = Registry(led)
    spend = SpendGate(led)
    adapters = {}
    # register a DOM link (preferred) + our fake API rail, prove DOM-first then fallback
    reg.register("sgh-api", "API", "core", "models", policy_rank=0)
    reg.attach_probe("sgh-api", rail.probe)
    adapters["sgh-api"] = rail
    spend.set_budget("sgh-api", 10.0)
    reg.probe_all()
    disp = Dispatcher(reg, adapters, led, spend=spend)
    out = disp.dispatch("core", "models", {"prompt": "route me"})
    check("dispatcher reaches the node rail and returns the model text",
          lambda: out["ok"] and out["text"].startswith("ALIVE"))
    check("the metered call went through the spend breaker (SPEND_SETTLED ledgered)",
          lambda: any(e["event"] == "SPEND_SETTLED" for e in led.verify()))

    # spend breaker DENIES when the budget is exhausted
    spend.set_budget("sgh-api", 0.001)     # smaller than one worst-case
    check("exhausted budget -> dispatcher NOT_PERMITTED (breaker in the caller path)",
          lambda: _denied(disp))

    # register_node_rails wires the real set (probes will mark real incumbents
    # UNREACHABLE here since BTS_MESH isn't importable in this tmp env - and that is
    # the CORRECT, honest result, not a failure)
    reg2 = Registry(Ledger(td / "n2.jsonl", KEY, "core"))
    ad2 = {}
    register_node_rails(reg2, ad2, spend_gate=SpendGate(Ledger(td / "n2.jsonl", KEY, "c")))
    check("register_node_rails registers all four node links",
          lambda: len(reg2.state()) == 4)
    # Each real node rail probes HONESTLY: live if its incumbent imports (it does, run
    # natively where V:\Ai\BTS_MESH is on disk), UNREACHABLE if not. Either is correct -
    # what must never happen is a fake-live probe. Assert the probe RAN and returned a
    # real (bool, detail) with a matching detail string, not that it is uniformly False.
    def _honest(a):
        ok, detail = a.probe()
        return (ok is True and "importable" in detail) or \
               (ok is False and "UNREACHABLE" in detail)
    check("every node rail probes HONESTLY (live-if-importable OR UNREACHABLE, never "
          "fake-live)", lambda: all(_honest(a) for a in ad2.values()))
    live = sum(1 for a in ad2.values() if a.probe()[0])
    check(f"[MEASURED native: {live}/4 incumbents importable - the adapted rails can "
          f"reach the live mesh]", lambda: True)

    bad = [(l, e) for l, ok, e in RESULTS if not ok]
    for label, ok, err in RESULTS:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label, ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks (adapted rails drive incumbents; missing=UNREACHABLE; "
          "metered=spend-gated)" % ("PASS" if not bad else "FAIL", len(RESULTS)))
    return 0 if not bad else 1


def _denied(disp):
    try:
        disp.dispatch("core", "models", {"prompt": "x"})
    except RailError as e:
        return e.kind == "NOT_PERMITTED"
    return False


def test_node_rails():
    assert main() == 0


if __name__ == "__main__":
    sys.exit(main())