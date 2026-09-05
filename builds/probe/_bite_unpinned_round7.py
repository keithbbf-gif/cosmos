#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bite: round-7 unpinned probe refusals against CURRENT code.

Round 6b typed classify_pause garbage as HOLD. Remaining:

  * CLOSE_REFUSED still never raised (rounds 2-6 leftover)
  * tool_disposition.guard_ledger against a bool/array sentinel
  * apply_proposals bundle=[] / proposals="APPLY"
  * fingerprint(repo, "one/file.py")  — string iterates as characters
  * compare(recorded=[], live={})
  * stamp(rec=[], ...)
  * maker_hands / scout leftover already typed (control)

Expected before a pin: all_bite == true.

    py -3.14 builds/probe/_bite_unpinned_round7.py
"""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
OUT = HERE / "_bite_unpinned_round7.json"

import artifact_freshness as af                                       # noqa: E402
import cosmos_resession as rs                                         # noqa: E402
import tool_disposition as td                                         # noqa: E402


def _catch(fn, typed):
    try:
        got = fn()
        preview = type(got).__name__
        if got is not None and not isinstance(got, (bool, int)):
            try:
                preview = f"{type(got).__name__}:{str(got)[:80]}"
            except Exception:                                         # noqa: BLE001
                preview = type(got).__name__
        return {"kind": None, "crash": None, "returned": type(got).__name__,
                "value_preview": preview}
    except typed as e:
        return {"kind": getattr(e, "kind", None), "crash": None,
                "returned": None, "value_preview": None}
    except Exception as e:                                            # noqa: BLE001
        return {"kind": None, "crash": type(e).__name__, "returned": None,
                "value_preview": str(e)[:80]}


def main() -> int:
    rec = {"schema": "cosmos-bite/1",
           "what": "round7 unpinned probe refusals — current vs claimed"}
    src = Path(rs.__file__).read_text(encoding="utf-8")
    rec["close_refused_in_docstring"] = "CLOSE_REFUSED" in src
    rec["close_refused_raise_present"] = (
        'ResessionRefusal("CLOSE_REFUSED"' in src
        or "ResessionRefusal('CLOSE_REFUSED'" in src
    )
    rec["close_refused_still_unraised"] = (
        rec["close_refused_in_docstring"]
        and not rec["close_refused_raise_present"]
    )

    tmp = Path(tempfile.mkdtemp(prefix="cosmos_pbite7_"))
    try:
        root = tmp / "live"
        root.mkdir()
        sentinel = root / ".cosmos-root.json"
        sentinel.write_text("true", encoding="utf-8")
        ledger = tmp / "scratch.jsonl"
        ledger.write_text("", encoding="utf-8")
        rec["td_bool_sentinel"] = _catch(
            lambda: td.guard_ledger(ledger, root), td.DispositionError)

        sentinel.write_text("[]", encoding="utf-8")
        rec["td_array_sentinel"] = _catch(
            lambda: td.guard_ledger(ledger, root), td.DispositionError)

        sentinel.write_text("1", encoding="utf-8")
        rec["td_number_sentinel"] = _catch(
            lambda: td.guard_ledger(ledger, root), td.DispositionError)

        # Apply-path bites need a VALID sentinel so they are not the
        # AttributeError from CosmosPaths reading a JSON bool.
        sentinel.write_text(
            json.dumps({"system": "COSMOS", "tree_id": "KMesh-COSMOS-live"}),
            encoding="utf-8")
        rec["apply_bundle_list"] = _catch(
            lambda: td.apply_proposals(None, [], ledger_path=ledger,
                                       live_root=root),
            td.DispositionError)
        rec["apply_proposals_str"] = _catch(
            lambda: td.apply_proposals(None, {"proposals": "APPLY"},
                                       ledger_path=ledger, live_root=root),
            td.DispositionError)
        rec["apply_bundle_none"] = _catch(
            lambda: td.apply_proposals(None, None, ledger_path=ledger,
                                       live_root=root),
            td.DispositionError)
        rec["apply_proposals_none"] = _catch(
            lambda: td.apply_proposals(None, {"proposals": None},
                                       ledger_path=ledger, live_root=root),
            td.DispositionError)

        rec["fp_rels_str"] = _catch(
            lambda: af.fingerprint(tmp, "one/file.py"), td.DispositionError)
        rec["fp_rels_none"] = _catch(
            lambda: af.fingerprint(tmp, None), td.DispositionError)
        rec["fp_rels_int"] = _catch(
            lambda: af.fingerprint(tmp, 1), td.DispositionError)

        rec["compare_recorded_list"] = _catch(
            lambda: af.compare([], {"a": {"exists": True, "bytes": 1,
                                          "sha256": "x"}}),
            td.DispositionError)
        rec["compare_recorded_str"] = _catch(
            lambda: af.compare("stale", {"a": {"exists": True, "bytes": 1,
                                               "sha256": "x"}}),
            td.DispositionError)
        rec["stamp_rec_list"] = _catch(
            lambda: af.stamp([], tmp, ["a.py"]), td.DispositionError)

        rec["precheck_seed_array"] = _catch(
            lambda: rs.precheck_seed(tmp / "no_seed.json",
                                     tmp / "no_decl.json",
                                     "KMesh-COSMOS-live"),
            rs.ResessionRefusal)
        seed = tmp / "SEED.json"
        decl = tmp / "SEED.decl.json"
        seed.write_text("[]", encoding="utf-8")
        decl.write_text(json.dumps({"len": 2, "sha": "00"}), encoding="utf-8")
        rec["precheck_seed_body_array"] = _catch(
            lambda: rs.precheck_seed(seed, decl, "KMesh-COSMOS-live"),
            rs.ResessionRefusal)
        decl.write_text("[]", encoding="utf-8")
        rec["precheck_decl_array"] = _catch(
            lambda: rs.precheck_seed(seed, decl, "KMesh-COSMOS-live"),
            rs.ResessionRefusal)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    bites = []
    for name, row in rec.items():
        if not isinstance(row, dict):
            continue
        if row.get("crash"):
            bites.append(name)
        elif (row.get("kind") is None and row.get("returned")
              and name.startswith(("fp_rels_str", "compare_recorded_str"))):
            bites.append(name + ":silent")
    rec["bites"] = bites
    rec["all_bite"] = bool(bites) or rec["close_refused_still_unraised"]
    rec["could_not_pin"] = (
        ["CLOSE_REFUSED"] if rec["close_refused_still_unraised"] else []
    )

    OUT.write_text(json.dumps(rec, indent=1, default=str), encoding="utf-8")
    print(json.dumps(rec, indent=2, default=str))
    print("all_bite", rec["all_bite"], "bites", rec["bites"],
          "could_not_pin", rec["could_not_pin"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
