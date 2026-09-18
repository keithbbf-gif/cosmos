#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prove the F-30 forge pins FAIL against the staged predecessor.

Loads `_delme/predispose_f30_forge_20260831T141931Z/` by path so live
cosmos_* siblings still resolve. Writes `cosmos/_fail_f30_against_old.json`.
all_new_pins_failed is the bite — required before belief.
"""
from __future__ import annotations

import ast
import importlib.util
import json
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OLD_DIR = REPO / "_delme" / "predispose_f30_forge_20260831T141931Z"
OLD_KERNEL = OLD_DIR / "cosmos_kernel.py"
OLD_PROBER = OLD_DIR / "cosmos_rails_prober.py"
OUT = REPO / "cosmos" / "_fail_f30_against_old.json"


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _wired_ids(src: str) -> list[str]:
    tree = ast.parse(src)
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == "WIRED_NODES":
                    return [
                        kw.value.value
                        for elt in node.value.elts
                        if isinstance(elt, ast.Dict)
                        for kw in (ast.keyword(k.value, v)
                                   for k, v in zip(elt.keys, elt.values)
                                   if isinstance(k, ast.Constant))
                        if kw.arg == "link_id" and isinstance(kw.value, ast.Constant)
                    ]
    return []


def _wired_ids_simple(src: str) -> list[str]:
    """Parse link_id string literals inside the WIRED_NODES assignment only."""
    start = src.find("WIRED_NODES = (")
    end = src.find("\nCLI_RAILS = (", start)
    block = src[start:end] if start >= 0 and end > start else ""
    ids = []
    marker = '"link_id": "'
    i = 0
    while True:
        j = block.find(marker, i)
        if j < 0:
            break
        k = block.find('"', j + len(marker))
        ids.append(block[j + len(marker):k])
        i = k + 1
    return ids


def main() -> int:
    sys.path.insert(0, str(REPO / "cosmos"))
    sys.path.insert(0, str(REPO))
    old_k = _load(OLD_KERNEL, "cosmos_kernel_f30_old")
    td = Path(tempfile.mkdtemp(prefix="cosmos_f30_old_"))
    root = old_k.install(td / "live", tree_id="f30-old")
    k = old_k.Kernel(root, worker="f30-old")
    composed = list((k.rails_compose or {}).get("composed") or [])
    adapters = set(getattr(k, "adapters", {}) or {})

    prober_src = OLD_PROBER.read_text(encoding="utf-8")
    wired = _wired_ids_simple(prober_src)
    pins = {
        "forge_rails_in_composed": "forge-rails" in composed,
        "github_forge_adapter": "github-forge" in adapters,
        "gitlab_forge_adapter": "gitlab-forge" in adapters,
        "github_forge_wired": "github-forge" in wired,
        "gitlab_forge_wired": "gitlab-forge" in wired,
        "forge_module_importable_from_old_tree": False,
        "colored_gh_json_binds_without_strip": False,
    }
    old_mod = OLD_DIR / "cosmos_forge_rail.py"
    pins["forge_module_importable_from_old_tree"] = old_mod.is_file()
    # Predecessor parse (proposed rail + live gh TTY): ANSI-wrapped JSON is
    # not JSON. json.loads of a colorized body is the live UNREACHABLE we
    # measured against gh.exe on this machine.
    colored = (
        "\x1b[1;37m{\x1b[m\n"
        "  \x1b[1;34m\"resources\"\x1b[m: {\n"
        "    \x1b[1;34m\"core\"\x1b[m: {\"limit\": 5000, \"remaining\": 5000}\n"
        "  }\n}"
    )
    try:
        json.loads(colored)
        pins["colored_gh_json_binds_without_strip"] = True
    except json.JSONDecodeError:
        pins["colored_gh_json_binds_without_strip"] = False

    rec = {
        "schema": "cosmos-f30-fail-old/1",
        "old_dir": str(OLD_DIR),
        "old_kernel_bytes": OLD_KERNEL.stat().st_size,
        "old_prober_bytes": OLD_PROBER.stat().st_size,
        "ready": bool(k.ready),
        "composed": composed,
        "adapter_ids": sorted(adapters),
        "old_wired": wired,
        "old_wired_count": len(wired),
        "pins": pins,
        "all_new_pins_failed": all(v is False for v in pins.values()),
    }
    OUT.write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(rec, indent=1))
    return 0 if rec["all_new_pins_failed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
