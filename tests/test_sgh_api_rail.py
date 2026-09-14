#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CHECK / WIRE / MAP for the sgh-api com rail (xAI Console / bts_sgh).

Proves registry + prober wiring, Kernel compose (node_rails, no boot invoke),
Model Rater via, grok farm seat, and bts_sgh ask() search/spend_ok contract
via tests/fixtures/bts_sgh.py. Live :8770 probe is UNMEASURED when absent.
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "cosmos"))
FIX = Path(__file__).resolve().parent / "fixtures"
sys.path.insert(0, str(FIX))

from cosmos_kernel import Kernel, install  # noqa: E402
from cosmos_model_rater import VIA_IDS, VIA_OPTIONS  # noqa: E402
from cosmos_node_rails import NodeRail  # noqa: E402
from cosmos_rails_prober import WIRED_NODES, poll_once  # noqa: E402
from cosmos_registry import Registry  # noqa: E402
from cosmos_ledger import Ledger  # noqa: E402
import cosmos_bucket_daemon as bucket  # noqa: E402

RESULTS: list[tuple[str, bool, str]] = []


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:  # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


def _wired_row():
    for s in WIRED_NODES:
        if s["link_id"] == "sgh-api":
            return s
    return {}


def main() -> int:
    row = _wired_row()
    check("WIRED_NODES includes sgh-api with bts_sgh module",
          lambda: row.get("module") == "bts_sgh"
          and row.get("rail_type") == "API"
          and row.get("src") == "core"
          and row.get("dst") == "models")

    prober_src = (Path(__file__).resolve().parent.parent / "cosmos"
                  / "cosmos_rails_prober.py").read_text(encoding="utf-8")
    check("prober uses prove-shaped _node_live_call for module rows",
          lambda: "def _node_live_call" in prober_src
          and "NodeRail(module, paths=paths)" in prober_src)
    check("prober does not import bts_* directly",
          lambda: "import bts_" not in prober_src and "from bts_" not in prober_src)

    kernel_src = (Path(__file__).resolve().parent.parent / "cosmos"
                  / "cosmos_kernel.py").read_text(encoding="utf-8")
    check("Kernel compose_rails wires node_rails (adapters, not prove at import)",
          lambda: '("node_rails", "cosmos_node_rails", "register_node_rails", False)'
          in kernel_src)
    check("Kernel prove path uses map_wired_nodes",
          lambda: "map_wired_nodes" in kernel_src)

    td = Path(tempfile.mkdtemp(prefix="cosmos_sgh_rail_"))
    root = install(td / "live", tree_id="sgh-api-rail")
    k = Kernel(root, worker="core")
    check("Kernel boot composes sgh-api adapter (compose row, no vendor call)",
          lambda: "sgh-api" in k.adapters
          and k.adapters["sgh-api"].module_name == "bts_sgh")

    # Registry.prove + PROBE_RESULT with injected live_call (no vendor spend)
    led = Ledger(td / "led.jsonl", b"k", "prober-test")
    reg = Registry(led)
    fake_call = lambda: {"ok": True, "rc": 0, "body": "PONG", "model": "grok-4.6"}
    rec = reg.prove("sgh-api", "API", "core", "models", fake_call)
    events = [e["event"] for e in led.verify()]
    check("prove() ledgers hash-chained PROBE_RESULT",
          lambda: rec.get("ok") and "PROBE_RESULT" in events
          and events.count("PROBE_RESULT") >= 1)
    check("successful prove registers LINK_REGISTERED once",
          lambda: "LINK_REGISTERED" in events and "sgh-api" in reg.live_nodes())

    # bts_sgh contract: search without spend_ok -> REFUSED
    import bts_sgh as stub_sgh  # noqa: E402

    r_ref = stub_sgh.ask("q", search=True, spend_ok=False)
    check("bts_sgh search=True REFUSED without spend_ok",
          lambda: r_ref.get("kind") == "REFUSED" and not (r_ref.get("text") or "").strip())
    r_ok = stub_sgh.ask("Reply PONG", search=True, spend_ok=True)
    check("bts_sgh search=True allowed when spend_ok",
          lambda: r_ok.get("ok") and r_ok.get("text"))

    sys.modules["bts_sgh"] = stub_sgh
    rail = NodeRail("bts_sgh", metered_usd=0.02, bts_root=str(FIX))
    d0 = rail.dispatch({"prompt": "PONG please"})
    check("NodeRail dispatch forwards kwargs to ask()",
          lambda: d0["ok"] and "PONG" in d0["text"] and d0["model"] == "grok-4.6")
    d1 = rail.dispatch({"prompt": "x", "kwargs": {"search": True, "spend_ok": False}})
    check("NodeRail surfaces REFUSED search through dispatch",
          lambda: d1.get("kind") == "REFUSED" or d1.get("ok") is False)

    check("Model Rater lists sgh-api as a via option",
          lambda: "sgh-api" in VIA_IDS
          and any(v["id"] == "sgh-api" for v in VIA_OPTIONS))
    grok_rails = bucket.NODES["grok"]["rails"]
    check("Grok farm seat prefers sgh-api then gw-api",
          lambda: grok_rails[0]["link_id"] == "sgh-api"
          and grok_rails[0]["module"] == "bts_sgh"
          and grok_rails[1]["link_id"] == "gw-api")

    cred_src = (Path(__file__).resolve().parent.parent / "cosmos"
                / "cosmos_cred_kit.py").read_text(encoding="utf-8")
    check("cred kit maps xai key file to sgh-api link_id",
          lambda: '"link_id": "sgh-api"' in cred_src
          and "xai_api_key.txt" in cred_src)

    kdash = (Path(__file__).resolve().parent.parent / "kdash" / "index.html"
             ).read_text(encoding="utf-8")
    check("KDash RAILS MATRIX panel uses esc() for row text",
          lambda: "function esc(" in kdash and "bd-rails" in kdash
          and "esc(r.link_id" in kdash)

    service_src = (Path(__file__).resolve().parent.parent / "cosmos"
                   / "cosmos_service.py").read_text(encoding="utf-8")
    check("Core exposes GET /api/v1/rails for System/nodemap clients",
          lambda: '"/api/v1/rails"' in service_src)
    check("voice asker binds grok -> sgh-api NodeRail",
          lambda: '"grok":   ("sgh-api", "bts_sgh"' in service_src)

    calls = {"n": 0}

    def _count():
        calls["n"] += 1
        return {"ok": True, "rc": 0, "body": "PONG", "model": "nope"}

    poll_once(str(root), live=False,
              live_calls={lid: _count for lid, *_ in ((s["link_id"],) for s in WIRED_NODES)})
    check("1-minute prober does not spend without --live",
          lambda: calls["n"] == 0)

    bad = [(l, e) for l, ok, e in RESULTS if not ok]
    for label, ok, err in RESULTS:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label,
                              ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks (sgh-api com rail)"
          % ("PASS" if not bad else "FAIL", len(RESULTS)))
    return 0 if not bad else 1


def test_sgh_api_rail():
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
