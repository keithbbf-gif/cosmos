#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""F-29 bite: repo-root tools/ + Kernel compose row are ABSENT on the incumbent.

Run against the live tree BEFORE promotion, and against the staged predecessor
AFTER promotion (`--old`). all_bite is true only when every claim is the scar.
"""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OLD = REPO / "_delme" / "predispose_cosmos_kernel_f29_20260831T130051Z" / "cosmos_kernel.py"


def measure(kernel_path: Path) -> dict:
    src = kernel_path.read_text(encoding="utf-8")
    tools_dir = REPO / "tools"
    rec = {
        "kernel_path": str(kernel_path),
        "repo_root_tools_dir": tools_dir.is_dir(),
        "repo_root_surface_py": (tools_dir / "surface.py").is_file(),
        "repo_root_mcp_docs_py": (tools_dir / "mcp_docs.py").is_file(),
        "src_has_tools_surface_row": '"tools-surface"' in src,
        "src_imports_tools_mcp_docs": "tools.mcp_docs" in src,
        "src_self_tools": "self.tools" in src,
    }
    return rec


def boot_scratch(kernel_dir: Path) -> dict:
    """Boot a writing Kernel. kernel_dir is searched FIRST so a staged
    predecessor cosmos_kernel.py wins; live cosmos/ supplies siblings."""
    sys.path.insert(0, str(REPO / "cosmos"))
    if str(kernel_dir) not in sys.path:
        sys.path.insert(0, str(kernel_dir))
    # Drop a cached live kernel if we are measuring the predecessor.
    sys.modules.pop("cosmos_kernel", None)
    from cosmos_kernel import Kernel, install  # noqa: E402
    td = Path(tempfile.mkdtemp(prefix="cosmos_f29_bite_"))
    root = install(td / "live", tree_id="f29-bite")
    k = Kernel(root, worker="f29-bite")
    composed = list((k.rails_compose or {}).get("composed") or [])
    return {
        "ready": bool(k.ready),
        "composed": composed,
        "tools_surface_composed": "tools-surface" in composed,
        "has_tools_attr": hasattr(k, "tools"),
        "tools_is_none": getattr(k, "tools", "MISSING") is None,
        "tools_value_kind": type(getattr(k, "tools", None)).__name__,
        "warnings": dict((k.rails_compose or {}).get("warnings") or {}),
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--old", action="store_true",
                    help="measure the staged predecessor instead of live cosmos/")
    ap.add_argument("--out", default=str(REPO / "cosmos" / "_bite_f29.json"))
    a = ap.parse_args(argv)

    kernel_path = OLD if a.old else (REPO / "cosmos" / "cosmos_kernel.py")
    rec = measure(kernel_path)
    boot = None
    boot_err = None
    if a.old:
        # Predecessor is a single file; boot uses live cosmos/ except the
        # kernel module is loaded from a copy dir containing only the old file
        # PLUS we still import sibling cosmos_* from live cosmos/. Put OLD
        # parent first so cosmos_kernel is the staged one.
        try:
            boot = boot_scratch(OLD.parent)
        except Exception as e:  # noqa: BLE001
            boot_err = f"{type(e).__name__}: {e}"
    else:
        try:
            boot = boot_scratch(REPO / "cosmos")
        except Exception as e:  # noqa: BLE001
            boot_err = f"{type(e).__name__}: {e}"
    rec["boot"] = boot
    rec["boot_err"] = boot_err

    # The scar: repo-root tools/ missing AND no compose row AND boot does not
    # bind a tools surface.
    claims = {
        "no_repo_root_surface": rec["repo_root_surface_py"] is False,
        "no_compose_row_in_src": rec["src_has_tools_surface_row"] is False,
        "boot_did_not_compose_tools_surface": (
            boot is not None and boot["tools_surface_composed"] is False
        ) or (boot is None),
    }
    rec["claims"] = claims
    rec["all_bite"] = all(claims.values())
    rec["schema"] = "cosmos-f29-bite/1"
    Path(a.out).write_text(json.dumps(rec, indent=1, default=str) + "\n",
                           encoding="utf-8")
    print(json.dumps(rec, indent=1, default=str))
    return 0 if rec["all_bite"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
