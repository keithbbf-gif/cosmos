#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest wave 4: rails + DOM-into-scheduler (M6 closed) + MCP server + surfaces
integration. DOM is now a dispatchable rail with typed failure and audited fallback;
COSMOS speaks MCP; surfaces qualify backup targets by the three questions."""
from __future__ import annotations
import json, sys, tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cosmos_ledger import Ledger
from cosmos_registry import Registry
from cosmos_dom import DomWorker
from cosmos_rails import Dispatcher, DomRail, ApiRail, CliRail, RailError
from cosmos_mcp import MCPServer, TOOLS
from cosmos_kernel import Kernel, install

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


class FakeDriver:
    def __init__(self, mode="ok"): self.mode = mode; self.started = []
    def start(self, profile):
        self.started.append(profile)
        if self.mode == "dead_start":
            raise ConnectionError("no browser")
    def navigate(self, url):
        if self.mode == "auth":
            raise PermissionError("login wall")
        return f"page at {url}"
    def session_ok(self):
        return self.mode != "expired"
    def stop(self): pass


def main() -> int:
    td = Path(tempfile.mkdtemp(prefix="cosmos_w4_"))
    KEY = b"k"

    # ===== M6: DOM AS A DISPATCHABLE RAIL =====
    led = Ledger(td / "rails.jsonl", KEY, "core")
    reg = Registry(led)
    reg.register("dom-link", "DOM", "core", "web", policy_rank=1)
    reg.register("api-link", "API", "core", "web")
    dom_ok = DomWorker(led, td / "domwork", "domworker", FakeDriver("ok"))
    dom_rail = DomRail(dom_ok)
    api_rail = ApiRail(lambda p: {"ok": True, "kind": "API", "via": "api"})
    reg.attach_probe("dom-link", dom_rail.probe)
    reg.attach_probe("api-link", api_rail.probe)
    reg.probe_all()
    disp = Dispatcher(reg, {"dom-link": dom_rail, "api-link": api_rail}, led)

    r = disp.dispatch("core", "web", {"job_id": "j1", "url": "https://x"})
    check("M6: DOM-first dispatch runs the DOM rail (was: DOM is just a sort key)",
          lambda: r["ok"] and r["kind"] == "OK")
    check("M6: RAIL_DISPATCH + RAIL_RESULT ledgered",
          lambda: {"RAIL_DISPATCH", "RAIL_RESULT"} <= {e["event"] for e in led.verify()})

    # DOM session expired -> typed failure -> AUDITED fallback to API (not silent)
    reg2 = Registry(Ledger(td / "r2.jsonl", KEY, "core"))
    reg2.register("dom2", "DOM", "core", "web", policy_rank=1)
    reg2.register("api2", "API", "core", "web")
    dom_dead = DomRail(DomWorker(Ledger(td / "r2.jsonl", KEY, "c"), td / "d2", "w",
                                 FakeDriver("expired")))
    api2 = ApiRail(lambda p: {"ok": True, "kind": "API", "via": "fallback"})
    reg2.attach_probe("dom2", lambda: (True, "claims live"))   # probe says live
    reg2.attach_probe("api2", api2.probe)
    reg2.probe_all()
    d2led = reg2.ledger
    disp2 = Dispatcher(reg2, {"dom2": dom_dead, "api2": api2}, d2led)
    r2 = disp2.dispatch("core", "web", {"job_id": "j2", "url": "https://y",
                                        "require_session": True})
    check("M6: dead DOM session -> AUDITED fallback to API, never silent",
          lambda: r2["via"] == "fallback")
    check("M6: the fallback is a RECORDED event with its reason",
          lambda: any(e["event"] == "RAIL_FALLBACK" and
                      e["payload"]["reason"] == "SESSION_EXPIRED" for e in d2led.verify()))

    # no live link at all
    reg3 = Registry(Ledger(td / "r3.jsonl", KEY, "core"))
    reg3.register("x", "API", "a", "b")   # registered, never probed -> not live
    disp3 = Dispatcher(reg3, {"x": api_rail}, reg3.ledger)
    check("M6: no MEASURED-live link -> NO_LIVE_LINK (registration is not capability)",
          expect(RailError, "NO_LIVE_LINK")(lambda: disp3.dispatch("a", "b", {})))

    # ===== MCP SERVER =====
    root = td / "Cosmos"; install(root, tree_id="w4")
    k = Kernel(root, worker="core")
    mcp = MCPServer(k)

    def rpc(method, params=None, rid=1):
        return json.loads(mcp.handle(json.dumps(
            {"jsonrpc": "2.0", "id": rid, "method": method,
             "params": params or {}})))

    init = rpc("initialize")
    check("MCP: initialize returns protocol + serverInfo",
          lambda: init["result"]["serverInfo"]["name"] == "cosmos")
    tl = rpc("tools/list")
    check("MCP: tools/list exposes the kernel verbs",
          lambda: len(tl["result"]["tools"]) == len(TOOLS) >= 7)
    st = rpc("tools/call", {"name": "cosmos_status", "arguments": {}})
    check("MCP: tools/call cosmos_status delegates to the kernel",
          lambda: json.loads(st["result"]["content"][0]["text"])["ready"] is True)
    sub = rpc("tools/call", {"name": "cosmos_submit",
                             "arguments": {"command": "echo", "priority": "high"}})
    check("MCP: cosmos_submit creates a real job (client cannot reach around authority)",
          lambda: "job_id" in json.loads(sub["result"]["content"][0]["text"]))
    check("MCP: the submit is in the kernel's own job state",
          lambda: len(k.sched._state()) == 1)
    cmd = rpc("tools/call", {"name": "cosmos_command",
                             "arguments": {"text": "status"}})
    check("MCP: cosmos_command drives the voice/frontend seam",
          lambda: json.loads(cmd["result"]["content"][0]["text"])["ok"] is True)
    bad = rpc("tools/call", {"name": "no_such_tool", "arguments": {}})
    check("MCP: unknown tool -> JSON-RPC error, not a crash",
          lambda: bad["error"]["code"] == -32602)
    parse = json.loads(mcp.handle("{ not json"))
    check("MCP: torn request -> parse error (-32700), never a silent drop",
          lambda: parse["error"]["code"] == -32700)
    note = mcp.handle(json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}))
    check("MCP: a notification gets NO response line (protocol-correct)",
          lambda: note is None)

    # ===== SURFACES (integration - the module was built + tested separately) =====
    from cosmos_surfaces import Surfaces, SurfaceError
    sled = Ledger(td / "surf.jsonl", KEY, "core")
    surf = Surfaces(sled)
    surf.register("srv1", "LAN", "\\\\srv1\\backup", "BACKUP")
    surf.attach_probe("srv1", lambda: (True, 9 * 10**12, "9 TB free"))
    surf.measure("srv1")
    q = surf.qualify_backup_target("srv1", min_free_bytes=10**12)
    check("SURFACES: a reachable off-machine LAN target with capacity QUALIFIES",
          lambda: q["qualified"] is True)
    surf.register("clocal", "LOCAL", "P:\\", "SCRATCH")
    surf.attach_probe("clocal", lambda: (True, 10**13, "local"))
    surf.measure("clocal")
    ql = surf.qualify_backup_target("clocal", min_free_bytes=10**12)
    check("SURFACES: a LOCAL surface FAILS off-machine (one copy on one machine is zero)",
          lambda: ql["qualified"] is False and any("machine" in r.lower()
                                                   for r in ql["reasons"]))

    bad = [(l, e) for l, ok, e in RESULTS if not ok]
    for label, ok, err in RESULTS:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label, ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks (DOM is a rail; COSMOS speaks MCP; surfaces qualified)"
          % ("PASS" if not bad else "FAIL", len(RESULTS)))
    return 0 if not bad else 1


def test_wave4():
    assert main() == 0


if __name__ == "__main__":
    sys.exit(main())