#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prove the Kernel-composed tools/ surface ANSWERS.

Boots a writing Kernel on an isolated install (does not touch the live
authority ledger), then invokes both keyless MCP tools through
`k.tools` — the surface compose_rails bound. Writes
`cosmos/_f29_composed_live.json`. A claim is not evidence; the vendor
`serverInfo.name` in the artifact is.
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "cosmos" / "_f29_composed_live.json"

sys.path.insert(0, str(REPO / "cosmos"))
sys.path.insert(0, str(REPO))
from cosmos_kernel import Kernel, install  # noqa: E402
from tools.surface import ToolError  # noqa: E402


def main() -> int:
    td = Path(tempfile.mkdtemp(prefix="cosmos_f29_live_"))
    root = install(td / "live", tree_id="f29-composed-live")
    k = Kernel(root, worker="f29-composed-live")
    rec = k.rails_compose or {}
    composed = list(rec.get("composed") or [])
    rows = []
    rc = 0
    if k.tools is None:
        rows.append({"ok": False, "kind": "NOT_COMPOSED",
                     "detail": "kernel.tools is None after writing boot"})
        rc = 2
    else:
        for name in ("openai-docs", "xai-docs"):
            try:
                rows.append(k.tools.invoke(name))
            except ToolError as e:
                rows.append({"ok": False, "tool": name, "kind": e.kind,
                             "detail": str(e)})
                rc = 2
    art = {
        "schema": "cosmos-tools-surface/1",
        "mode": "composed-live",
        "ready": bool(k.ready),
        "composed_tools_surface": "tools-surface" in composed,
        "composed": composed,
        "tools_compose": getattr(k, "tools_compose", None),
        "adapter_leak": [a for a in (k.adapters or {})
                         if a in {"tools-surface", "xai-docs", "openai-docs"}],
        "rows": rows,
        "ok": rc == 0 and all(r.get("ok") is True for r in rows)
              and "tools-surface" in composed,
    }
    OUT.write_text(json.dumps(art, indent=1, default=str) + "\n",
                   encoding="utf-8")
    print(json.dumps(art, indent=1, default=str))
    return 0 if art["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
