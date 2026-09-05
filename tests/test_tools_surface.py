#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_tools_surface - F-29, the repo-root tools/ surface.

WISHLIST: "WRITE THE MISSING TOOLS." Prototype lived at builds/probe/tools/.
This suite binds the PROMOTED surface at repo-root tools/.

Default is HERMETIC: injected transport, no network, no live root.

    py -3.14 tests/test_tools_surface.py                 # hermetic gate
    py -3.14 tests/test_tools_surface.py --live          # + real MCP

The load-bearing check is `rc!=0 with a valid body`: a transport returning
HTTP 200, a perfect `serverInfo`, AND rc=1 must REFUSE. That is the
maker-hands scar (a CLI that printed the sought token while failing would
otherwise score green).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
TOOLS = REPO / "tools"

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
                return getattr(e, "kind", None) == kind
            return False
        return inner
    return wrap


class LegacyAnyBodyPass:
    """The fabricated-pass class maker_hands_probe nearly shipped.

    A non-zero rc plus a payload that happens to contain the token we grep
    for is treated as a HAND. The real surface must refuse this.
    """

    def invoke(self, name, verb="probe", *, transport=None):
        res = transport("https://example.invalid/mcp", "{}", {})
        raw = res.get("body") or ""
        if "serverInfo" in raw:
            return {"ok": True, "tool": name, "value": "grepped", "rc": res.get("rc")}
        return {"ok": False}


XAI_JSON = json.dumps({
    "jsonrpc": "2.0", "id": 1,
    "result": {"protocolVersion": "2025-06-18",
               "capabilities": {"tools": {"listChanged": True}},
               "serverInfo": {"name": "xai-docs-mcp", "version": "1.0.0"}},
})
OA_SSE = (
    "event: message\n"
    "data: " + json.dumps({
        "jsonrpc": "2.0", "id": 1,
        "result": {"serverInfo": {"name": "openai-docs-mcp", "version": "1.0.0"}},
    }) + "\n\n"
)


def _transport(body, http=200, rc=0):
    def fn(url, payload, headers):
        fn.calls.append({"url": url, "payload": payload, "headers": headers})
        return {"http": http, "body": body, "rc": rc}
    fn.calls = []
    return fn


def hermetic(surface_mod, mcp_mod) -> None:
    from dataclasses import fields as dc_fields
    ToolError = surface_mod.ToolError
    spy = _transport(XAI_JSON)
    surf = mcp_mod.make_surface(transport=spy)

    check("inventory lists xai-docs and openai-docs (declaration, not capability)",
          lambda: {r["name"] for r in surf.inventory()} == {"xai-docs", "openai-docs"})
    check("inventory does not invoke the transport",
          lambda: spy.calls == [])
    check("report is contracts-shaped and does not invoke (GET /tools pin)",
          lambda: {r["name"] for r in surf.report()} == {"xai-docs", "openai-docs"}
          and all(r["verified"] is None and r["disposition"] is None
                  and r["age_s"] is None for r in surf.report())
          and spy.calls == [])
    check("unknown tool -> UNKNOWN_TOOL",
          expect(ToolError, "UNKNOWN_TOOL")(lambda: surf.invoke("nope-docs")))
    check("bad verb -> BAD_VERB",
          expect(ToolError, "BAD_VERB")(lambda: surf.invoke("xai-docs", "delete")))
    check("UNKNOWN_TOOL / BAD_VERB still did not invoke the transport",
          lambda: spy.calls == [])

    boom_calls = []
    def boom(url, payload, headers):
        boom_calls.append(1)
        raise AssertionError("unknown-tool must not build a transport")
    boom_surf = mcp_mod.make_surface(transport=boom)
    def _unknown_no_request():
        ok = expect(ToolError, "UNKNOWN_TOOL")(
            lambda: boom_surf.invoke("nope-docs"))()
        return ok and boom_calls == []
    check("UNKNOWN_TOOL does not construct a request", _unknown_no_request)

    happy = mcp_mod.make_surface(transport=_transport(XAI_JSON))
    got = happy.invoke("xai-docs")
    check("JSON initialize binds serverInfo.name = xai-docs-mcp",
          lambda: got["ok"] is True and got["value"] == "xai-docs-mcp")
    check("the bound field is named, not grepped from a blob",
          lambda: got["bind"] == "serverInfo.name")

    sse = mcp_mod.make_surface(transport=_transport(OA_SSE))
    got_oa = sse.invoke("openai-docs")
    check("SSE framing binds serverInfo.name = openai-docs-mcp",
          lambda: got_oa["ok"] is True and got_oa["value"] == "openai-docs-mcp")

    scar_transport = _transport(XAI_JSON, http=200, rc=1)
    scar_surf = mcp_mod.make_surface(transport=scar_transport)
    check("rc!=0 with a valid body is NONZERO_RC, never a hand (maker-hands scar)",
          expect(ToolError, "NONZERO_RC")(lambda: scar_surf.invoke("xai-docs")))

    empty = mcp_mod.make_surface(transport=_transport('{"jsonrpc":"2.0","id":1,"result":{}}'))
    check("rc==0 without serverInfo.name is NO_VALUE, never a grepped pass",
          expect(ToolError, "NO_VALUE")(lambda: empty.invoke("xai-docs")))

    down = mcp_mod.make_surface(transport=_transport("connection refused", http=None, rc=None))
    check("no http / no rc is UNREACHABLE, never ABSENT-as-green",
          expect(ToolError, "UNREACHABLE")(lambda: down.invoke("xai-docs")))

    legacy = LegacyAnyBodyPass()
    legacy_got = legacy.invoke("xai-docs", transport=scar_transport)
    check("CONTROL: the legacy shim accepts rc!=0 if the body carries serverInfo",
          lambda: legacy_got.get("ok") is True)
    check("CONTROL: that is exactly the class the real surface now refuses",
          lambda: legacy_got.get("ok") is True and scar_transport.calls != [])

    check("ToolSpec has no credential field (this surface holds no COSMOS secret)",
          lambda: "key" not in "".join(f.name for f in dc_fields(surface_mod.ToolSpec)).lower())


def live(mcp_mod, ToolError) -> None:
    surf = mcp_mod.make_surface()
    for name, expect_value in (("xai-docs", "xai-docs-mcp"),
                               ("openai-docs", "openai-docs-mcp")):
        try:
            got = surf.invoke(name)
            check(f"LIVE {name} binds {expect_value}",
                  lambda g=got, v=expect_value: g["ok"] is True and g["value"] == v)
        except ToolError as e:
            check(f"LIVE {name} binds {expect_value}",
                  lambda: False)
            RESULTS[-1] = (RESULTS[-1][0], False, f"{e.kind}: {e}")
        except Exception as e:                                        # noqa: BLE001
            check(f"LIVE {name} binds {expect_value}", lambda: False)
            RESULTS[-1] = (RESULTS[-1][0], False, f"{type(e).__name__}: {e}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", action="store_true",
                    help="also hit the real keyless MCP endpoints (not a gate)")
    a = ap.parse_args(argv)

    if not (TOOLS / "surface.py").is_file():
        check("tools/surface.py exists (F-29: the missing surface)", lambda: False)
        check("tools/mcp_docs.py exists", lambda: False)
        print("ABSENT: repo-root tools/ is not a surface yet — this is the F-29 bite")
        for label, ok, err in RESULTS:
            print(f"  {'OK  ' if ok else 'FAIL'}  {label}{('  ' + err) if err else ''}")
        print("live_value: " + json.dumps({"rows": 0, "state": "ABSENT"}))
        print("result: FAIL  0/2")
        return 1

    sys.path.insert(0, str(REPO))
    import tools.surface as surface_mod                               # noqa: E402
    import tools.mcp_docs as mcp_mod                                  # noqa: E402

    hermetic(surface_mod, mcp_mod)
    if a.live:
        live(mcp_mod, surface_mod.ToolError)

    for label, ok, err in RESULTS:
        print(f"  {'OK  ' if ok else 'FAIL'}  {label}{('  ' + err) if err else ''}")
    bad = [x for x in RESULTS if not x[1]]
    print("live_value: " + json.dumps(
        {"checks": len(RESULTS), "passed": len(RESULTS) - len(bad),
         "live": bool(a.live),
         "tools": sorted(mcp_mod.MCP_DOCS)}, sort_keys=True))
    print(f"result: {'ok' if not bad else 'FAIL'}  "
          f"{len(RESULTS) - len(bad)}/{len(RESULTS)}")
    return 1 if bad else 0


def test_tools_surface():
    assert main([]) == 0


if __name__ == "__main__":
    raise SystemExit(main())
