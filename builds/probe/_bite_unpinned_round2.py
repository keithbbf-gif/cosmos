#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bite: round-2 unpinned probe refusals against CURRENT (pre-change) code.

Kinds that sat in docstrings / kind-sets and were never named by a test,
or that currently crash untyped / succeed when they should refuse.

    py -3.14 builds/probe/_bite_unpinned_round2.py
"""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "cosmos"))
OUT = HERE / "_bite_unpinned_round2.json"

import regen_refusal_taxonomy as regen                                # noqa: E402
import longpath_census as lp                                          # noqa: E402
import tool_disposition as td                                         # noqa: E402


def main() -> int:
    rec: dict = {
        "schema": "cosmos-bite/1",
        "what": "round2 unpinned probe refusals — current vs claimed",
        "all_bite": False,
    }

    old_c = regen.COSMOS
    tdd = Path(tempfile.mkdtemp(prefix="cosmos_nogen_"))
    try:
        empty = tdd / "cosmos"
        empty.mkdir()
        regen.COSMOS = empty
        try:
            regen.load_generator()
            rec["no_generator_old_kind"] = None
            rec["no_generator_old_crash"] = None
        except regen.TaxonomyRegenError as e:
            rec["no_generator_old_kind"] = e.kind
            rec["no_generator_old_crash"] = None
        except Exception as e:                                        # noqa: BLE001
            rec["no_generator_old_kind"] = None
            rec["no_generator_old_crash"] = type(e).__name__
            rec["no_generator_old_detail"] = str(e)[:200]
    finally:
        regen.COSMOS = old_c
        shutil.rmtree(tdd, ignore_errors=True)

    tdw = Path(tempfile.mkdtemp(prefix="cosmos_unw_"))
    try:
        blocked = tdw / "blocked"
        blocked.write_text("x", encoding="utf-8")
        try:
            regen.write_utf8(blocked / "out.md", "hello")
            rec["tax_unwritable_old_kind"] = None
            rec["tax_unwritable_old_crash"] = None
        except regen.TaxonomyRegenError as e:
            rec["tax_unwritable_old_kind"] = e.kind
            rec["tax_unwritable_old_crash"] = None
        except Exception as e:                                        # noqa: BLE001
            rec["tax_unwritable_old_kind"] = None
            rec["tax_unwritable_old_crash"] = type(e).__name__
            rec["tax_unwritable_old_detail"] = str(e)[:200]
    finally:
        shutil.rmtree(tdw, ignore_errors=True)

    td_src = Path(td.__file__).read_text(encoding="utf-8")
    rec["no_ledger_json_print"] = '"kind": "NO_LEDGER"' in td_src
    rec["no_ledger_dispositionerror_raise"] = (
        'raise DispositionError("NO_LEDGER"' in td_src
        or "raise DispositionError('NO_LEDGER'" in td_src
    )
    rec["bad_ledger_in_docstring"] = "BAD_LEDGER" in td_src
    rec["bad_ledger_raise_present"] = 'DispositionError("BAD_LEDGER"' in td_src

    lp_src = Path(lp.__file__).read_text(encoding="utf-8")
    rec["not_windows_in_kind_set"] = "NOT_WINDOWS" in lp_src
    rec["not_windows_raise_present"] = (
        'ProbeRefusal("NOT_WINDOWS"' in lp_src
        or "ProbeRefusal('NOT_WINDOWS'" in lp_src
    )
    rec["import_failed_raise_present"] = (
        'ProbeRefusal("IMPORT_FAILED"' in lp_src
    )
    rec["import_failed_dict_field"] = '"kind": "IMPORT_FAILED"' in lp_src

    tdi = Path(tempfile.mkdtemp(prefix="cosmos_imp_"))
    try:
        src = tdi / "src"
        src.mkdir()
        (src / "a.txt").write_text("x", encoding="utf-8")
        tree = {"scratch": str(src), "files": {}}
        rec_imp = lp._probe_running_backup(
            tree, tdi / "scratch", tdi / "no_such_module.py", "missing")
        rec["import_failed_old_kind"] = rec_imp.get("kind")
        rec["import_failed_old_state"] = rec_imp.get("state")
    finally:
        shutil.rmtree(tdi, ignore_errors=True)

    cm = (HERE / "credential_manifest.py").read_text(encoding="utf-8")
    rec["bad_spec_in_docstring"] = "BAD_SPEC" in cm
    rec["bad_spec_raise_present"] = (
        'CredentialManifestError("BAD_SPEC"' in cm
        or "CredentialManifestError('BAD_SPEC'" in cm
    )

    rs = (HERE / "cosmos_resession.py").read_text(encoding="utf-8")
    rec["close_refused_in_docstring"] = "CLOSE_REFUSED" in rs
    rec["close_refused_raise_present"] = (
        'ResessionRefusal("CLOSE_REFUSED"' in rs
        or "ResessionRefusal('CLOSE_REFUSED'" in rs
    )

    rg = Path(regen.__file__).read_text(encoding="utf-8")
    rec["tax_unwritable_readback_present"] = "read-back does not match" in rg

    rec["all_bite"] = (
        rec.get("no_generator_old_kind") == "NO_GENERATOR"
        and rec.get("tax_unwritable_old_crash") == "FileExistsError"
        and rec.get("tax_unwritable_old_kind") is None
        and rec["no_ledger_json_print"] is True
        and rec["no_ledger_dispositionerror_raise"] is False
        and rec["bad_ledger_raise_present"] is False
        and rec["not_windows_in_kind_set"] is True
        and rec["not_windows_raise_present"] is False
        and rec["import_failed_raise_present"] is False
        and rec.get("import_failed_old_kind") == "IMPORT_FAILED"
        and rec["bad_spec_in_docstring"] is True
        and rec["bad_spec_raise_present"] is False
        and rec["close_refused_in_docstring"] is True
        and rec["close_refused_raise_present"] is False
    )
    OUT.write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(rec, indent=2))
    return 0 if rec["all_bite"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
