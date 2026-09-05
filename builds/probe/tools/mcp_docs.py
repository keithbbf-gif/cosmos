#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""mcp_docs — the first two tools on the F-29 surface.

WHY THESE TWO FIRST. Maker-hands shortlist (docs/research/MAKER_HANDS_SHORTLIST.md
§3 Tier 1) measured both as HAND, keyless, on this machine:

    POST https://docs.x.ai/api/mcp            initialize → serverInfo.name=xai-docs-mcp
    POST https://developers.openai.com/mcp    initialize → serverInfo.name=openai-docs-mcp

Neither holds a COSMOS secret. GitLab/GitHub already have a staged *rail*
(`builds/probe/proposed/cosmos_forge_rail.py`); duplicating them here would
be bloat. Docs MCP is a TOOL, not a dispatchable rail: $0, no spend gate,
no Kernel attach.

    py -3.14 builds/probe/tools/mcp_docs.py            # hermetic selfcheck
    py -3.14 builds/probe/tools/mcp_docs.py --live     # real MCP, evidence not a gate
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE.parent) not in sys.path:
    sys.path.insert(0, str(_HERE.parent))

from tools.surface import (  # noqa: E402
    ToolError, ToolSpec, ToolSurface, parse_server_info, _INIT_BODY, _HEADERS,
)

MCP_DOCS: dict[str, ToolSpec] = {
    "xai-docs": ToolSpec(
        name="xai-docs",
        verbs=("probe",),
        behavior="JSON-RPC initialize against docs.x.ai MCP; binds serverInfo.name",
        bind="serverInfo.name",
        url="https://docs.x.ai/api/mcp",
    ),
    "openai-docs": ToolSpec(
        name="openai-docs",
        verbs=("probe",),
        behavior="JSON-RPC initialize against OpenAI docs MCP (SSE); binds serverInfo.name",
        bind="serverInfo.name",
        url="https://developers.openai.com/mcp",
    ),
}


def default_http(url: str, body: str, headers: dict, timeout: int = 25) -> dict:
    """One POST. Never raises — a failure is evidence too. No key is sent."""
    req = urllib.request.Request(
        url, data=body.encode("utf-8"), method="POST", headers=dict(headers))
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return {"http": r.status,
                    "body": r.read(4000).decode("utf-8", "replace"),
                    "rc": 0}
    except urllib.error.HTTPError as e:
        return {"http": e.code,
                "body": e.read(1200).decode("utf-8", "replace"),
                "rc": 1}
    except (urllib.error.URLError, OSError, ValueError) as e:
        return {"http": None, "body": f"{type(e).__name__}: {e}", "rc": None}


def make_surface(transport=None) -> ToolSurface:
    return ToolSurface(MCP_DOCS, transport=transport or default_http,
                       parser=parse_server_info)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="mcp_docs")
    ap.add_argument("--live", action="store_true",
                    help="hit the real keyless MCP endpoints")
    a = ap.parse_args(argv)
    surf = make_surface()
    if not a.live:
        print(json.dumps({"schema": "cosmos-tools-surface/1",
                          "mode": "inventory",
                          "tools": surf.inventory()}, indent=1))
        return 0
    rows = []
    rc = 0
    for name in sorted(MCP_DOCS):
        try:
            rows.append(surf.invoke(name))
        except ToolError as e:
            rows.append({"ok": False, "tool": name, "kind": e.kind,
                         "detail": str(e)})
            rc = 2
    doc = {"schema": "cosmos-tools-surface/1", "mode": "live", "rows": rows}
    sys.path.insert(0, str(_HERE.parent))
    import artifact_freshness as af                                    # noqa: WPS433
    af.stamp(doc, _HERE.parents[2], [
        "builds/probe/tools/mcp_docs.py",
        "builds/probe/tools/surface.py",
    ])
    print(json.dumps(doc, indent=1, default=str))
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
