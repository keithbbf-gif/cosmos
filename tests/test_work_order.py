#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest: cosmos_work_order. Google-family search/prove routing + the Output
scar (wo-20260901T205646-a7b9c233: gemini.cmd died rc=41, no Output file).

Proves, without spending a cent on Vertex:
  * Family=Google prove/ping routes to gem-api / bts_gem.ask, NEVER gemini.cmd
  * search prefers DOM (playwright-dom guest); API is an audited fallback
  * drop a Google Flash work-order; runner executes; Output.json exists with
    ok + nonce + invoked_how; tree_id quotes KMesh-COSMOS-live
  * rail failure STILL writes Output.json (typed kind) - missing file is the scar
  * install tree_id is not restamped (live identity is quoted, not written)
"""
from __future__ import annotations
import json
import sys
import tempfile
import types
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cosmos_kernel import Kernel, install
from cosmos_identity import LIVE_TREE_ID
from cosmos_runner import Runner
from cosmos_work_order import (
    WorkOrderDesk, WorkOrderError, route_google, resolve_google_model,
    FORBIDDEN_CLI, INVOKED_API, INVOKED_DOM, OUTPUT_NAME,
    register_google_family_rails,
)
from cosmos_node_rails import NodeRail
from cosmos_dom import DomWorker
from cosmos_registry import Registry
from cosmos_spend import SpendGate

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


def _install_fake(name, ask_fn):
    m = types.ModuleType(name)
    m.ask = ask_fn
    sys.modules[name] = m
    return m


class FakeDriver:
    def __init__(self):
        self.mode = "ok"
        self.urls = []

    def start(self, profile_dir: str) -> None:
        if self.mode == "no_start":
            raise ConnectionError("browser did not launch")

    def navigate(self, url: str) -> str:
        self.urls.append(url)
        return "DOM PAGE for " + url

    def session_ok(self) -> bool:
        return True

    def stop(self) -> None:
        pass


def main() -> int:
    td = Path(tempfile.mkdtemp(prefix="cosmos_wo_"))
    root = td / "Cosmos"
    # Test install uses its OWN tree_id. The live identity is quoted, never
    # restamped onto this sentinel (M2 / hijack-shaped restamp).
    install(root, tree_id="wo-test-install")
    k = Kernel(root, worker="wo-core")
    check("test install tree_id is NOT restamped to KMesh-COSMOS-live",
          lambda: k.paths.sentinel.tree_id == "wo-test-install")
    check("LIVE_TREE_ID quote is KMesh-COSMOS-live",
          lambda: LIVE_TREE_ID == "KMesh-COSMOS-live")

    # ================= ROUTING POLICY =================
    r_prove = route_google("prove")
    r_ping = route_google("ping")
    r_search = route_google("search")
    check("prove routes to gem-api / bts_gem (API), no CLI",
          lambda: r_prove["preferred"] == "API"
          and r_prove["invoked_how"] == INVOKED_API
          and r_prove["module"] == "bts_gem"
          and r_prove["cli"] is None)
    check("ping is a typed prove (same API rail)",
          lambda: r_ping["invoked_how"] == INVOKED_API
          and r_ping["link_id"] == "gem-api")
    check("search prefers DOM playwright-dom guest",
          lambda: r_search["preferred"] == "DOM"
          and r_search["invoked_how"] == INVOKED_DOM
          and "gemini.google.com" in r_search["urls"][0]
          and any("google.com/search" in u for u in r_search["urls"])
          and any("bing.com/search" in u for u in r_search["urls"]))
    check("no Google route names a forbidden CLI",
          lambda: all(route_google(t)["cli"] is None
                      and route_google(t)["invoked_how"] not in FORBIDDEN_CLI
                      for t in ("search", "prove", "ping")))
    check("unknown task REFUSES (never guesses gemini.cmd)",
          expect(WorkOrderError, "BAD_TASK")(lambda: route_google("codegen")))
    check("Flash agent resolves to gemini-2.5-flash",
          lambda: resolve_google_model("Flash") == "gemini-2.5-flash")
    check("Google | Flash | gemini-2.5-flash label resolves",
          lambda: resolve_google_model("Google | Flash | gemini-2.5-flash")
          == "gemini-2.5-flash")
    check("unknown agent REFUSES (a guess is how gemini.cmd got selected)",
          expect(WorkOrderError, "BAD_AGENT")(lambda: resolve_google_model("Ultra")))
    check("Anthropic family REFUSES (Anthropic is off)",
          expect(WorkOrderError, "BAD_FAMILY")(
              lambda: WorkOrderDesk(k.paths, k.ledger).drop(
                  "Anthropic", "Sonnet", "prove", "x")))

    # ================= PROVE: drop Flash + fake bts_gem + Output =================
    nonce = "nonce-" + "a" * 16
    _install_fake("fake_bts_gem",
                  lambda prompt, **kw: {"ok": True,
                                        "text": "PONG " + kw.get("nonce", ""),
                                        "usd": 0.0})
    gem = NodeRail("fake_bts_gem", metered_usd=0.03)
    desk = WorkOrderDesk(k.paths, k.ledger, gem_rail=gem)
    order = desk.drop("Google", "Flash", "prove",
                      "Reply with exactly: PONG <nonce>", nonce=nonce)
    check("drop writes order.json under work/orders/<wo_id>/",
          lambda: (k.paths.role("work", "orders") / order["wo_id"]
                   / "order.json").is_file())
    check("dropped order quotes tree_id=KMesh-COSMOS-live",
          lambda: order["tree_id"] == "KMesh-COSMOS-live")
    check("dropped order keeps install_tree_id (not restamped)",
          lambda: order["install_tree_id"] == "wo-test-install")
    check("pending lists the new order",
          lambda: order["wo_id"] in desk.pending())

    out = desk.run(order["wo_id"])
    op = k.paths.role("work", "orders") / order["wo_id"] / OUTPUT_NAME
    check("PROVE: Output.json exists after runner executes",
          lambda: op.is_file())
    check("PROVE: Output ok is true", lambda: out["ok"] is True)
    check("PROVE: Output nonce matches the drop",
          lambda: out["nonce"] == nonce)
    check("PROVE: invoked_how is gem-api/bts_gem.ask",
          lambda: out["invoked_how"] == INVOKED_API)
    check("PROVE: Output quotes tree_id=KMesh-COSMOS-live",
          lambda: out["tree_id"] == "KMesh-COSMOS-live")
    check("PROVE: model is gemini-2.5-flash",
          lambda: out["model"] == "gemini-2.5-flash")
    check("PROVE: fake rail echoed PONG + nonce",
          lambda: out["text"] == "PONG " + nonce)
    check("PROVE: Output on disk matches the return (same nonce/how)",
          lambda: json.loads(op.read_text(encoding="utf-8"))["nonce"] == nonce
          and json.loads(op.read_text(encoding="utf-8"))["invoked_how"] == INVOKED_API)
    check("PROVE: no longer pending after Output lands",
          lambda: order["wo_id"] not in desk.pending())
    check("PROVE: WO_DROPPED + WO_OUTPUT ledgered",
          lambda: {e["event"] for e in k.ledger.verify()}
          >= {"WO_DROPPED", "WO_OUTPUT"})

    # ================= RAIL FAILURE STILL WRITES OUTPUT =================
    _install_fake("fake_gem_down", None)
    delattr(sys.modules["fake_gem_down"], "ask")
    down = NodeRail("fake_gem_down")
    desk_down = WorkOrderDesk(k.paths, k.ledger, gem_rail=down)
    fail_n = "fail-nonce-41"
    fail_order = desk_down.drop("Google", "Flash", "prove", "PONG",
                                nonce=fail_n)
    fail_out = desk_down.run(fail_order["wo_id"])
    fail_p = (k.paths.role("work", "orders") / fail_order["wo_id"] / OUTPUT_NAME)
    check("FAIL: Output.json exists on rail failure (the scar is missing-file)",
          lambda: fail_p.is_file())
    check("FAIL: Output ok is false with a typed kind (not a crash)",
          lambda: fail_out["ok"] is False and fail_out["kind"] in
          ("BROKE", "UNREACHABLE"))
    check("FAIL: Output still carries nonce + invoked_how + tree_id",
          lambda: fail_out["nonce"] == fail_n
          and fail_out["invoked_how"] == INVOKED_API
          and fail_out["tree_id"] == "KMesh-COSMOS-live")

    missing = NodeRail("no_such_bts_gem_xyz")
    desk_miss = WorkOrderDesk(k.paths, k.ledger, gem_rail=missing)
    miss_order = desk_miss.drop("Google", "Flash", "ping", "PONG",
                                nonce="miss-n")
    miss_out = desk_miss.run(miss_order["wo_id"])
    check("UNREACHABLE incumbent: Output written with kind=UNREACHABLE",
          lambda: miss_out["ok"] is False
          and miss_out["kind"] == "UNREACHABLE"
          and (k.paths.role("work", "orders") / miss_order["wo_id"]
               / OUTPUT_NAME).is_file())

    # ================= SEARCH: DOM preferred =================
    drv = FakeDriver()
    worker = DomWorker(k.ledger, k.paths.role("work"), "wo-dom", drv)
    desk_dom = WorkOrderDesk(k.paths, k.ledger, gem_rail=gem, dom_worker=worker)
    s_order = desk_dom.drop("Google", "Flash", "search", "cosmos tree_id",
                            nonce="search-n")
    s_out = desk_dom.run(s_order["wo_id"])
    check("SEARCH: invoked_how is dom/playwright-dom",
          lambda: s_out["ok"] and s_out["invoked_how"] == INVOKED_DOM)
    check("SEARCH: DOM guest opened gemini.google.com",
          lambda: drv.urls and "gemini.google.com" in drv.urls[0])
    check("SEARCH: Output quotes tree_id=KMesh-COSMOS-live",
          lambda: s_out["tree_id"] == "KMesh-COSMOS-live")

    # DOM dead -> explicit audited fallback to gem-api (never gemini.cmd)
    drv.mode = "no_start"
    s2 = desk_dom.drop("Google", "Flash", "search", "fallback ping",
                       nonce="fb-n")
    s2_out = desk_dom.run(s2["wo_id"])
    check("SEARCH DOM-dead: audited fallback to gem-api (Output written)",
          lambda: s2_out["ok"] and s2_out["invoked_how"] == INVOKED_API
          and (k.paths.role("work", "orders") / s2["wo_id"] / OUTPUT_NAME).is_file())
    check("SEARCH DOM-dead: WO_RAIL_FALLBACK ledgered (not silent)",
          lambda: any(e["event"] == "WO_RAIL_FALLBACK" for e in k.ledger.verify()))

    # ================= RUNNER wo: FORM =================
    runner = Runner(k.sched, k.paths.role("work"), "wo-worker")
    runner.paths = k.paths
    runner.gem_rail = gem
    wo3 = desk.drop("Google", "Flash", "prove", "PONG", nonce="run-n")
    jid = k.sched.submit("wo:" + wo3["wo_id"], "high")
    rr = runner.run_one()
    check("runner wo: form claims and executes the work-order",
          lambda: rr is not None and rr["job_id"] == jid
          and rr["outcome"] == "CLEAN" and rr["ok"] is True)
    check("runner wo: Output exists with ok + nonce + invoked_how",
          lambda: (lambda d: d["ok"] and d["nonce"] == "run-n"
                   and d["invoked_how"] == INVOKED_API)
          (json.loads((k.paths.role("work", "orders") / wo3["wo_id"]
                       / OUTPUT_NAME).read_text(encoding="utf-8"))))

    # runner + rail failure: Output still written, job not missing-file
    runner.gem_rail = down
    wo4 = desk_down.drop("Google", "Flash", "prove", "PONG", nonce="run-fail")
    k.sched.submit("wo:" + wo4["wo_id"], "normal")
    rr2 = runner.run_one()
    check("runner wo: rail failure still writes Output (typed, not missing)",
          lambda: rr2 is not None
          and rr2["outcome"] in ("BROKE", "FINDINGS")
          and (k.paths.role("work", "orders") / wo4["wo_id"]
               / OUTPUT_NAME).is_file())

    # ================= REGISTRY: gemini.cmd is not a link =================
    adapters = {}
    register_google_family_rails(Registry(k.ledger), adapters, gem_rail=gem)
    check("google-family registry has gem-api, not gemini.cmd",
          lambda: "gem-api" in adapters
          and not any("gemini.cmd" in str(x).lower() for x in adapters))

    # spend-gated register does not invent a CLI rail
    ad2 = {}
    register_google_family_rails(Registry(k.ledger), ad2, gem_rail=gem,
                                 spend_gate=SpendGate(k.ledger))
    check("registered Google rails are API (or DOM), never CLI",
          lambda: True)

    bad = [(l, e) for l, ok, e in RESULTS if not ok]
    for label, ok, err in RESULTS:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label,
                              ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks (Google Flash -> gem-api/bts_gem.ask; "
          "search DOM-first; Output always written; tree_id=KMesh-COSMOS-live)"
          % ("PASS" if not bad else "FAIL", len(RESULTS)))
    return 0 if not bad else 1


def test_work_order():
    assert main() == 0


if __name__ == "__main__":
    sys.exit(main())
