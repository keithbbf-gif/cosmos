#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Live F-30 evidence: Kernel compose + standalone --probe (no config write).

Does not write live/config/forge_rail.json or the probe record.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "cosmos"))
sys.path.insert(0, str(REPO))

from cosmos_kernel import Kernel, install  # noqa: E402
from cosmos_forge_rail import _probe_all  # noqa: E402
from cosmos_paths import CosmosPaths  # noqa: E402

OUT = REPO / "cosmos" / "_f30_live.json"


def main() -> int:
    live = REPO / "live"
    paths = CosmosPaths(live)
    k = Kernel(live, worker="f30-measure", read_only=True)
    # read_only skips compose. Boot a scratch writing kernel for compose evidence.
    import tempfile
    td = Path(tempfile.mkdtemp(prefix="cosmos_f30_live_"))
    root = install(td / "live", tree_id="f30-compose")
    kw = Kernel(root, worker="f30-compose")
    composed = list((kw.rails_compose or {}).get("composed") or [])
    rec = _probe_all(str(live))
    # Bound values only. Vendor JSON (emails, ids) stays out of the artifact.
    slim = {
        "schema": rec.get("schema"),
        "tree_id": rec.get("tree_id"),
        "ok": rec.get("ok"),
        "dst": rec.get("dst"),
        "links": {
            lid: {"ok": v.get("ok"), "rc": v.get("rc"),
                  "bound": v.get("bound"),
                  "binary_present": bool(v.get("binary")),
                  "detail": (v.get("detail") or "")[:160]}
            for lid, v in (rec.get("links") or {}).items()
        },
    }
    out = {
        "schema": "cosmos-f30-live/1",
        "tree_id": paths.sentinel.tree_id,
        "live_probe": slim,
        "scratch_compose": {
            "ready": bool(kw.ready),
            "composed_forge": "forge-rails" in composed,
            "composed": composed,
            "adapter_ids": sorted(kw.adapters),
            "github_in_adapters": "github-forge" in kw.adapters,
            "gitlab_in_adapters": "gitlab-forge" in kw.adapters,
            "dst": (getattr(kw.adapters.get("github-forge"), "spec", {}) or {}).get("dst"),
        },
        "writes": 0,
        "ok": (
            rec.get("dst") == "forge"
            and "forge-rails" in composed
            and "github-forge" in kw.adapters
            and "gitlab-forge" in kw.adapters
            and paths.sentinel.tree_id == "KMesh-COSMOS-live"
        ),
    }
    OUT.write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=1))
    return 0 if out["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
