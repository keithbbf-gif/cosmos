#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""New round-2 probe pins MUST FAIL against the staged predecessor.

Staged at builds/probe/_delme/predispose_unpinned_round2_20260831T133712Z/
Never calls behave() on a stripped census.

    py -3.14 builds/probe/_fail_unpinned_round2_against_old.py
"""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
import types
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
OUT = HERE / "_fail_unpinned_round2_against_old.json"
OLD = HERE / "_delme" / "predispose_unpinned_round2_20260831T133712Z"


def _exec(path: Path, name: str, src: str | None = None):
    mod = types.ModuleType(name)
    mod.__file__ = str(HERE / path.name)
    sys.modules[name] = mod
    text = src if src is not None else path.read_text(encoding="utf-8")
    exec(compile(text, str(path), "exec"), mod.__dict__)
    return mod


def main() -> int:
    failed = []
    ran = []
    sys.path.insert(0, str(REPO / "cosmos"))

    old_tax = _exec(OLD / "regen_refusal_taxonomy.py", "regen_old_r2")
    tdd = Path(tempfile.mkdtemp(prefix="cosmos_failold_tax_"))
    try:
        empty = tdd / "cosmos"
        empty.mkdir()
        old_tax.COSMOS = empty
        ran.append("NO_GENERATOR")
        src = (OLD / "regen_refusal_taxonomy.py").read_text(encoding="utf-8")
        stripped = src.replace('"NO_GENERATOR"', '"STRIPPED_NO_GENERATOR"')
        old_tax_s = _exec(OLD / "regen_refusal_taxonomy.py", "regen_old_r2s", stripped)
        old_tax_s.COSMOS = empty
        try:
            old_tax_s.load_generator()
            failed.append("NO_GENERATOR:did_not_raise")
        except old_tax_s.TaxonomyRegenError as e:
            if e.kind != "NO_GENERATOR":
                failed.append("NO_GENERATOR")
        except Exception:
            failed.append("NO_GENERATOR")

        blocked = tdd / "blocked"
        blocked.write_text("x", encoding="utf-8")
        ran.append("UNWRITABLE")
        try:
            old_tax.write_utf8(blocked / "out.md", "hello")
            failed.append("UNWRITABLE:did_not_raise")
        except old_tax.TaxonomyRegenError as e:
            if e.kind != "UNWRITABLE":
                failed.append("UNWRITABLE")
        except Exception:
            failed.append("UNWRITABLE")
    finally:
        shutil.rmtree(tdd, ignore_errors=True)

    old_lp = _exec(OLD / "longpath_census.py", "lp_old_r2")
    ran.append("NOT_WINDOWS")
    if not hasattr(old_lp, "_require_windows"):
        failed.append("NOT_WINDOWS")
    else:
        old_lp._is_windows = lambda: False
        try:
            old_lp.census_one(str(Path(tempfile.gettempdir()) / "nope_r2"))
            failed.append("NOT_WINDOWS:did_not_raise")
        except old_lp.ProbeRefusal as e:
            if e.kind != "NOT_WINDOWS":
                failed.append("NOT_WINDOWS")
        except Exception:
            failed.append("NOT_WINDOWS")

    ran.append("IMPORT_FAILED")
    src_lp = (OLD / "longpath_census.py").read_text(encoding="utf-8")
    stripped_lp = src_lp.replace('"IMPORT_FAILED"', '"STRIPPED_IMPORT_FAILED"')
    old_lp_s = _exec(OLD / "longpath_census.py", "lp_old_r2s", stripped_lp)
    tdi = Path(tempfile.mkdtemp(prefix="cosmos_failold_imp_"))
    try:
        srcp = tdi / "src"
        srcp.mkdir()
        (srcp / "a.txt").write_text("x", encoding="utf-8")
        rec = old_lp_s._probe_running_backup(
            {"scratch": str(srcp), "files": {}},
            tdi / "scratch", tdi / "no_such_module.py", "missing")
        if rec.get("kind") == "IMPORT_FAILED":
            pass
        else:
            failed.append("IMPORT_FAILED")
    finally:
        shutil.rmtree(tdi, ignore_errors=True)

    old_cm = _exec(OLD / "credential_manifest.py", "cm_old_r2")
    ran.append("BAD_SPEC")
    if not hasattr(old_cm, "check_need"):
        failed.append("BAD_SPEC")
    else:
        failed.append("BAD_SPEC:unexpected_check_need")

    old_td = _exec(OLD / "tool_disposition.py", "td_old_r2")
    ran.append("NO_LEDGER")
    if not hasattr(old_td, "require_apply_ledger"):
        failed.append("NO_LEDGER")
    else:
        try:
            old_td.require_apply_ledger(None)
            failed.append("NO_LEDGER:did_not_raise")
        except old_td.DispositionError as e:
            if e.kind != "NO_LEDGER":
                failed.append("NO_LEDGER")
        except Exception:
            failed.append("NO_LEDGER")

    ran.append("BAD_LEDGER")
    src_td = (OLD / "tool_disposition.py").read_text(encoding="utf-8")
    if 'DispositionError("BAD_LEDGER"' in src_td:
        pass
    else:
        failed.append("BAD_LEDGER")

    rec = {
        "schema": "cosmos-bite/1",
        "what": "round2 probe pins FAIL against staged predecessor",
        "old": str(OLD),
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
