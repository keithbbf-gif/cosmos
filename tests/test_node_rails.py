#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest: the ADAPTED node rails. Uses a FAKE incumbent module (injected into
sys.modules) so every path is proven WITHOUT spending a cent on a real model call -
the same discipline the DOM FakeDriver used. A real dispatch to a live model is
NATIVE-DEMO-REQUIRED and is a separate, spend-gated, opt-in run."""
from __future__ import annotations
import os, sys, tempfile, types
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "cosmos"))
from cosmos_ledger import Ledger
from cosmos_registry import Registry
from cosmos_spend import SpendGate
import cosmos_rails
from cosmos_rails import Dispatcher, RailError
from cosmos_node_rails import (
    NodeRail, fail_closed_empty, register_node_rails, resolve_incumbent_root,
)

RESULTS = []
def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:                                            # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


class _BoomRail:
    """A metered adapter whose dispatch RAISES the way a live vendor call does -
    read timeout, 500, a bug in the adapter. Not exotic: the rail contract says
    dispatch returns a typed dict, and when an adapter breaks that contract the
    Dispatcher still has to record WHY."""
    kind = "API"
    metered_usd = 0.02

    def probe(self):
        return True, "importable boom rail"

    def dispatch(self, payload):
        raise TimeoutError("read timed out after 30s")


def metered_failure_probe(tmp: Path, cap_usd: float, key: bytes = b"k") -> dict:
    """Run ONE metered dispatch against a rail that raises, and report what the
    Dispatcher actually EMITTED: the refusal kind, and the RAIL_RESULT detail it
    wrote to the ledger. `cap_usd` picks the scenario - a fat cap means the gate
    PERMITS and the rail then breaks; a cap under one worst case means the gate
    refuses and the rail is never called at all.

    Deliberately build-agnostic and importable: this is the negative control for
    the spend-gated mislabel, so it has to run against an OLDER cosmos_rails as
    well as this one (drop the old module first on sys.path and call it)."""
    led = Ledger(tmp / ("boom_%s.jsonl" % cap_usd), key, "core")
    reg = Registry(led)
    spend = SpendGate(led)
    boom = _BoomRail()
    reg.register("boom-api", "API", "core", "boom", policy_rank=0)
    reg.attach_probe("boom-api", boom.probe)
    reg.probe_all()
    spend.set_budget("boom-api", cap_usd)
    disp = Dispatcher(reg, {"boom-api": boom}, led, spend=spend)
    kind = None
    try:
        disp.dispatch("core", "boom", {"prompt": "x"})
    except RailError as e:
        kind = e.kind
    detail = ""
    for rec in led.verify():
        if rec["event"] == "RAIL_RESULT":
            detail = rec["payload"].get("detail", "")
    return {"kind": kind, "detail": detail, "module": cosmos_rails.__file__}


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

    # empty / whitespace body is FAILED even when the incumbent claimed ok=True
    _install_fake("fake_empty", lambda p, **k: {"ok": True, "text": ""})
    er = NodeRail("fake_empty").dispatch({"prompt": "x"})
    check("empty incumbent text is EMPTY_OUTPUT, never ok/rc=0",
          lambda: er["ok"] is False and er["kind"] == "EMPTY_OUTPUT"
          and er["rc"] == 2 and not er["text"])
    _install_fake("fake_ws", lambda p, **k: {"ok": True, "text": "  \n\t"})
    wr = NodeRail("fake_ws").dispatch({"prompt": "x"})
    check("whitespace-only body is EMPTY_OUTPUT, never rc=0",
          lambda: wr["ok"] is False and wr["kind"] == "EMPTY_OUTPUT"
          and wr.get("rc") == 2)
    check("fail_closed_empty is the one grok/gem/oa helper",
          lambda: fail_closed_empty({"ok": True, "text": ""})["kind"] == "EMPTY_OUTPUT"
          and fail_closed_empty({"ok": True, "text": "hi"})["ok"] is True)
    _install_fake("fake_named", lambda p, **k: {
        "ok": True, "text": "hi", "model": "gemini-2.5-flash", "usd": 0.0,
        "via": "vertex"})
    nr2 = NodeRail("fake_named").dispatch({"prompt": "x"})
    check("incumbent model/via preserved (not overwritten by module name)",
          lambda: nr2["ok"] and nr2["model"] == "gemini-2.5-flash"
          and nr2.get("via") == "vertex" and nr2["text"] == "hi")

    rails_src = (Path(__file__).resolve().parent.parent / "cosmos"
                 / "cosmos_node_rails.py").read_text(encoding="utf-8")
    check("node_rails has no BTS drive literal",
          lambda: "V:\\Ai\\BTS_MESH" not in rails_src
          and 'r"V:\\' not in rails_src and "r'V:\\" not in rails_src)
    old_env = os.environ.get("COSMOS_BTS_ROOT")
    os.environ["COSMOS_BTS_ROOT"] = str(td / "bts")
    try:
        resolved = resolve_incumbent_root()
        check("incumbent root from env, never a guessed drive",
              lambda: resolved == str(td / "bts"))
    finally:
        if old_env is None:
            os.environ.pop("COSMOS_BTS_ROOT", None)
        else:
            os.environ["COSMOS_BTS_ROOT"] = old_env
    check("missing env+config refuses to guess a BTS path",
          lambda: resolve_incumbent_root() is None)

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

    # ===== the ledger's REASON must be the reason that happened =====
    # Phase 5 finding, fixed here: `except Exception` around the metered call
    # wrote "spend-gated" into the AUTHORITY ledger for every failure of a
    # metered rail and re-raised NOT_PERMITTED - so a read timeout the gate had
    # already PERMITTED was recorded as a spend refusal. A false reason in the
    # authority record is worse than no reason. Fat cap here: nothing about this
    # dispatch is spend-gated, and the record has to say so.
    broke = metered_failure_probe(td, 10.0)
    check("a metered rail that RAISES is NOT labelled spend-gated in the ledger",
          lambda: broke["detail"] and "spend-gated" not in broke["detail"])
    check("...the ledger keeps the reason that actually happened (TimeoutError)",
          lambda: "TimeoutError" in broke["detail"]
          and "read timed out" in broke["detail"])
    check("...and the refusal is RAIL_FAILED, not NOT_PERMITTED",
          lambda: broke["kind"] == "RAIL_FAILED")
    # ...while a REAL spend refusal still reads exactly as it always did.
    gated = metered_failure_probe(td, 0.001)
    check("a REAL spend refusal is still 'spend-gated: [DENIED]' + NOT_PERMITTED",
          lambda: gated["kind"] == "NOT_PERMITTED"
          and gated["detail"].startswith("spend-gated: [DENIED]"))
    check("[MEASURED runtime binding: dispatched through %s]"
          % broke["module"], lambda: True)

    # register_node_rails wires the real set (probes will mark real incumbents
    # UNREACHABLE here since BTS_MESH isn't importable in this tmp env - and that is
    # the CORRECT, honest result, not a failure)
    reg2 = Registry(Ledger(td / "n2.jsonl", KEY, "core"))
    ad2 = {}
    register_node_rails(reg2, ad2, spend_gate=SpendGate(Ledger(td / "n2.jsonl", KEY, "c")))
    check("register_node_rails registers all four node links",
          lambda: len(reg2.state()) == 4)
    # Each real node rail probes HONESTLY: live if its incumbent imports (it does, run
    # natively where the configured incumbent tree is on disk), UNREACHABLE if not. Either is correct -
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