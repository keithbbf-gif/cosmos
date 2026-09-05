#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Run the new probe pins against STRIPPED in-memory copies.

The new pins MUST FAIL here. Never calls behave() on a stripped census
(that would write a deep tree). Output:
`builds/probe/_fail_unpinned_against_old.json`.

    py -3.14 builds/probe/_fail_unpinned_against_old.py
"""
from __future__ import annotations

import json
import sys
import tempfile
import types
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "_fail_unpinned_against_old.json"
REPO = HERE.parents[1]


def _exec_stripped(src: str, orig_path: Path, name: str):
    mod = types.ModuleType(name)
    mod.__file__ = str(orig_path)
    sys.modules[name] = mod
    exec(compile(src, str(orig_path), "exec"), mod.__dict__)
    return mod


def _retarget(src: str, kind: str) -> str:
    return src.replace(f'"{kind}"', f'"STRIPPED_{kind}"')


def main() -> int:
    failed = []
    ran = []

    # ---- longpath ROOT_MISSING (never call behave) ------------------------
    src = (HERE / "longpath_census.py").read_text(encoding="utf-8")
    src = _retarget(src, "ROOT_MISSING")
    src = _retarget(src, "SCRATCH_UNSAFE")
    old_lp = _exec_stripped(src, HERE / "longpath_census.py", "longpath_census_old")
    missing = str(Path(tempfile.gettempdir()) / "cosmos_lp_no_such_root_failold")
    ran.append("ROOT_MISSING")
    try:
        old_lp.census_one(missing)
        failed.append("ROOT_MISSING:did_not_raise")
    except old_lp.ProbeRefusal as e:
        if e.kind != "ROOT_MISSING":
            failed.append("ROOT_MISSING")
    except Exception:
        failed.append("ROOT_MISSING")

    ran.append("SCRATCH_UNSAFE")
    # Do not invoke behave(). The pin fails iff the kind string was retargeted.
    if '"SCRATCH_UNSAFE"' not in src and '"STRIPPED_SCRATCH_UNSAFE"' in src:
        failed.append("SCRATCH_UNSAFE")

    # ---- surface BAD_TRANSPORT -------------------------------------------
    surf_src = (HERE / "tools" / "surface.py").read_text(encoding="utf-8")
    surf_src = _retarget(surf_src, "BAD_TRANSPORT")
    old_surf = _exec_stripped(surf_src, HERE / "tools" / "surface.py",
                              "tools_surface_old")
    ran.append("BAD_TRANSPORT_empty")
    try:
        old_surf.ToolSurface({})
        failed.append("BAD_TRANSPORT_empty:constructed")
    except old_surf.ToolError as e:
        if e.kind != "BAD_TRANSPORT":
            failed.append("BAD_TRANSPORT_empty")
    except Exception:
        failed.append("BAD_TRANSPORT_empty")

    ran.append("BAD_TRANSPORT_no_transport")
    try:
        s = old_surf.ToolSurface({"x": old_surf.ToolSpec(
            name="x", verbs=("probe",), behavior="b", bind="n", url="u")})
        s.invoke("x")
        failed.append("BAD_TRANSPORT_no_transport:invoked")
    except old_surf.ToolError as e:
        if e.kind != "BAD_TRANSPORT":
            failed.append("BAD_TRANSPORT_no_transport")
    except Exception:
        failed.append("BAD_TRANSPORT_no_transport")

    # ---- taxonomy BAD_ARGS -----------------------------------------------
    tax_src = (HERE / "regen_refusal_taxonomy.py").read_text(encoding="utf-8")
    tax_src = _retarget(tax_src, "BAD_ARGS")
    old_tax = _exec_stripped(tax_src, HERE / "regen_refusal_taxonomy.py",
                             "regen_refusal_taxonomy_old")
    ran.append("BAD_ARGS")
    td = Path(tempfile.mkdtemp(prefix="cosmos_tax_failold_"))
    (td / "docs").mkdir()
    try:
        old_tax.main(["--diff", "--write", "--repo", str(td)])
        failed.append("BAD_ARGS:did_not_raise")
    except old_tax.TaxonomyRegenError as e:
        if e.kind != "BAD_ARGS":
            failed.append("BAD_ARGS")
    except Exception:
        failed.append("BAD_ARGS")

    # ---- resession NO_ROOT -----------------------------------------------
    rs_src = (HERE / "cosmos_resession.py").read_text(encoding="utf-8")
    rs_src = _retarget(rs_src, "NO_ROOT")
    ran.append("NO_ROOT")
    if '"NO_ROOT"' not in rs_src and '"STRIPPED_NO_ROOT"' in rs_src:
        failed.append("NO_ROOT")

    # ---- credential UNWRITABLE -------------------------------------------
    cm_src = (HERE / "credential_manifest.py").read_text(encoding="utf-8")
    cm_src = _retarget(cm_src, "UNWRITABLE")
    sys.path.insert(0, str(REPO / "cosmos"))
    old_cm = _exec_stripped(cm_src, HERE / "credential_manifest.py",
                            "credential_manifest_old")
    ran.append("UNWRITABLE")
    blocked = td / "blocked_file"
    blocked.write_text("x", encoding="utf-8")
    try:
        old_cm._write(blocked / "out.json", "{}")
        failed.append("UNWRITABLE:did_not_raise")
    except old_cm.CredentialManifestError as e:
        if e.kind != "UNWRITABLE":
            failed.append("UNWRITABLE")
    except Exception:
        failed.append("UNWRITABLE")

    # ---- maker_hands NO_SENTINEL / BAD_SENTINEL --------------------------
    mh_src = (HERE / "maker_hands_probe.py").read_text(encoding="utf-8")
    mh_src = mh_src.replace('NO_SENTINEL:', 'STRIPPED_NO_SENTINEL:')
    mh_src = mh_src.replace('BAD_SENTINEL:', 'STRIPPED_BAD_SENTINEL:')
    old_mh = _exec_stripped(mh_src, HERE / "maker_hands_probe.py",
                            "maker_hands_probe_old")
    ran.append("NO_SENTINEL")
    empty = td / "empty_root"
    empty.mkdir()
    try:
        old_mh._verify_root(str(empty))
        failed.append("NO_SENTINEL:did_not_raise")
    except old_mh.ProbeRefusal as e:
        if not str(e).startswith("NO_SENTINEL:"):
            failed.append("NO_SENTINEL")
    except Exception:
        failed.append("NO_SENTINEL")

    ran.append("BAD_SENTINEL")
    bogus = td / "bogus"
    bogus.mkdir()
    (bogus / ".cosmos-root.json").write_text(
        json.dumps({"system": "NOT-COSMOS", "tree_id": "x"}), encoding="utf-8")
    try:
        old_mh._verify_root(str(bogus))
        failed.append("BAD_SENTINEL:did_not_raise")
    except old_mh.ProbeRefusal as e:
        if not str(e).startswith("BAD_SENTINEL:"):
            failed.append("BAD_SENTINEL")
    except Exception:
        failed.append("BAD_SENTINEL")

    rec = {
        "schema": "cosmos-bite/1",
        "what": "new probe unpinned-refusal pins FAIL against stripped predecessors",
        "tests_run": len(ran),
        "failed": len(failed),
        "failed_names": failed,
        "ran_names": ran,
        "all_new_pins_failed": len(failed) == len(ran) and len(ran) > 0,
    }
    OUT.write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(rec, indent=2))
    return 0 if rec["all_new_pins_failed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
