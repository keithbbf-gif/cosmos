#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_tools_compose - F-29 Kernel compose row for repo-root tools/.

A writing Kernel boot must compose the tools/ surface as a named row
(`tools-surface`) WITHOUT invoking it. inventory() is a declaration;
invoke() is the measurement and is never a boot side-effect.

    py -3.14 tests/test_tools_compose.py

Bite: against the staged predecessor (no compose row) the first two checks
FAIL. That run is cosmos/_fail_f29_against_old.py.
"""
from __future__ import annotations

import json
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent

sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "cosmos"))
sys.path.insert(0, str(REPO))

from cosmos_kernel import Kernel, install  # noqa: E402

RESULTS = []


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:                                            # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


XAI_JSON = json.dumps({
    "jsonrpc": "2.0", "id": 1,
    "result": {"serverInfo": {"name": "xai-docs-mcp", "version": "1.0.0"}},
})


def _transport(body, http=200, rc=0):
    def fn(url, payload, headers):
        fn.calls.append(url)
        return {"http": http, "body": body, "rc": rc}
    fn.calls = []
    return fn


def main() -> int:
    td = Path(tempfile.mkdtemp(prefix="cosmos_tools_compose_"))
    root = install(td / "live", tree_id="f29-compose")
    k = Kernel(root, worker="f29-compose")
    rec = k.rails_compose or {}
    composed = list(rec.get("composed") or [])
    warnings = dict(rec.get("warnings") or {})

    check("writing Kernel boots READY", lambda: k.ready is True)
    check("compose row tools-surface is in rails_compose.composed",
          lambda: "tools-surface" in composed)
    check("tools-surface is not a warning (import/attach succeeded)",
          lambda: "tools-surface" not in warnings)
    check("kernel.tools is bound (composed surface, not a missing attr)",
          lambda: getattr(k, "tools", None) is not None)

    tools = getattr(k, "tools", None)
    names = []
    if tools is not None:
        names = [r["name"] for r in tools.inventory()]
    check("composed inventory declares xai-docs and openai-docs",
          lambda: set(names) == {"xai-docs", "openai-docs"})
    tcomp = getattr(k, "tools_compose", None) or {}
    check("boot compose did not invoke (no network on boot)",
          lambda: tcomp.get("ok") is True and tcomp.get("invoked") is False)

    # Re-bind an injected transport on the composed surface and measure.
    if tools is not None:
        spy = _transport(XAI_JSON)
        tools.transport = spy
        got = tools.invoke("xai-docs")
        check("composed surface invoke binds vendor serverInfo.name",
              lambda: got.get("ok") is True and got.get("value") == "xai-docs-mcp")
        check("composed surface does not register a Dispatcher adapter",
              lambda: "tools-surface" not in k.adapters
              and "xai-docs" not in k.adapters)
    else:
        check("composed surface invoke binds vendor serverInfo.name",
              lambda: False)
        check("composed surface does not register a Dispatcher adapter",
              lambda: False)

    # Pin: boot suites (test_kernel, test_boot_attach, test_core) can stay
    # green while GET /api/v1/tools 500s. F-29 rebound kernel.tools to
    # ToolSurface; the route called .report(). A promotion that keeps boot
    # green can still break the route. This HTTP pin is the missing evidence.
    from cosmos_service import Service
    svc = Service(k, host="127.0.0.1", port=0)
    svc.serve_background()
    tools_status = 0
    tools_body = None
    tools_err = ""
    try:
        req = urllib.request.Request(
            f"http://127.0.0.1:{svc.port}/api/v1/tools")
        req.add_header("Authorization", "Bearer " + svc.token)
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                tools_status = resp.status
                tools_body = json.loads(resp.read().decode("utf-8"))
        except Exception as e:                                       # noqa: BLE001
            tools_err = f"{type(e).__name__}: {e}"
            if isinstance(e, urllib.error.HTTPError):
                tools_status = e.code
                try:
                    tools_body = json.loads(e.read().decode("utf-8"))
                except Exception:                                    # noqa: BLE001
                    pass
    finally:
        svc.shutdown()

    check("GET /api/v1/tools after tools-surface compose is 200 with a report list",
          lambda: tools_status == 200
          and isinstance((tools_body or {}).get("report"), list))
    check("GET /tools serves ToolContracts (fresh ledger empty), not surface inventory",
          lambda: (tools_body or {}).get("report") == [])
    check("ToolSurface.report exists (kernel.tools.report cannot AttributeError)",
          lambda: callable(getattr(tools, "report", None)))

    # Read-only boot does not run compose_rails; tools stays unset.
    k_ro = Kernel(root, worker="f29-ro", read_only=True)
    check("read-only Kernel skips compose_rails (tools-surface not composed)",
          lambda: k_ro.rails_compose is None
          and getattr(k_ro, "tools", None) is None)

    bad = [x for x in RESULTS if not x[1]]
    for label, ok, err in RESULTS:
        print(f"  {'OK  ' if ok else 'FAIL'}  {label}{('  ' + err) if err else ''}")
    print("live_value: " + json.dumps({
        "composed": composed,
        "tools_bound": tools is not None,
        "inventory": names,
        "warnings_tools": warnings.get("tools-surface"),
        "ready": bool(k.ready),
        "tools_route_status": tools_status,
        "tools_route_err": tools_err,
        "tools_report_len": (len(tools_body["report"])
                             if isinstance(tools_body, dict)
                             and isinstance(tools_body.get("report"), list)
                             else None),
        "tools_has_report_attr": callable(getattr(tools, "report", None)),
    }, sort_keys=True))
    print(f"result: {'ok' if not bad else 'FAIL'}  "
          f"{len(RESULTS) - len(bad)}/{len(RESULTS)}")
    return 1 if bad else 0


def test_tools_compose():
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
