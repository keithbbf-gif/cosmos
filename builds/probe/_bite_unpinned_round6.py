#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bite: round-6 unpinned probe refusals against CURRENT code.

  * CLOSE_REFUSED still never raised (rounds 2-5 leftover)
  * scout sentinel JSON number / null (round 5 pinned array, not number)
  * maker_hands sentinel JSON number / null
  * regen --out is a directory
  * tool_disposition apply ledger that is JSON object not jsonl
  * resession seed that is a JSON array

    py -3.14 builds/probe/_bite_unpinned_round6.py
"""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
OUT = HERE / "_bite_unpinned_round6.json"

import cosmos_newai_scout as scout                                    # noqa: E402
import maker_hands_probe as hands                                     # noqa: E402
import regen_refusal_taxonomy as tax                                  # noqa: E402
import cosmos_resession as rs                                         # noqa: E402
import tool_disposition as td                                         # noqa: E402


def _catch(fn, typed):
    try:
        got = fn()
        return {"kind": None, "crash": None, "returned": type(got).__name__,
                "value_preview": str(got)[:60]}
    except typed as e:
        return {"kind": getattr(e, "kind", None), "crash": None,
                "returned": None, "value_preview": None}
    except Exception as e:                                            # noqa: BLE001
        return {"kind": None, "crash": type(e).__name__, "returned": None,
                "value_preview": str(e)[:80]}


def main() -> int:
    rec = {"schema": "cosmos-bite/1",
           "what": "round6 unpinned probe refusals — current vs claimed"}
    src = Path(rs.__file__).read_text(encoding="utf-8")
    rec["close_refused_in_docstring"] = "CLOSE_REFUSED" in src
    rec["close_refused_raise_present"] = (
        'ResessionRefusal("CLOSE_REFUSED"' in src
        or "ResessionRefusal('CLOSE_REFUSED'" in src
    )
    rec["close_refused_still_unraised"] = rec["close_refused_in_docstring"] and not rec["close_refused_raise_present"]

    tmp = Path(tempfile.mkdtemp(prefix="cosmos_pbite6_"))
    try:
        root = tmp / "live"
        root.mkdir()
        sentinel = root / ".cosmos-root.json"

        sentinel.write_text("1", encoding="utf-8")
        rec["scout_number"] = _catch(lambda: scout.verify_root(root), scout.ScoutRefusal)
        rec["hands_number"] = _catch(lambda: hands._verify_root(str(root)), hands.ProbeRefusal)

        sentinel.write_text("null", encoding="utf-8")
        rec["scout_null"] = _catch(lambda: scout.verify_root(root), scout.ScoutRefusal)
        rec["hands_null"] = _catch(lambda: hands._verify_root(str(root)), hands.ProbeRefusal)

        sentinel.write_text("true", encoding="utf-8")
        rec["scout_true"] = _catch(lambda: scout.verify_root(root), scout.ScoutRefusal)
        rec["hands_true"] = _catch(lambda: hands._verify_root(str(root)), hands.ProbeRefusal)

        out_dir = tmp / "tax_out"
        out_dir.mkdir()
        rec["tax_out_is_dir"] = _catch(lambda: tax.write_utf8(out_dir, "# x\n"),
                                       tax.TaxonomyRegenError)

        ledger_obj = tmp / "ledger.json"
        ledger_obj.write_text("{}", encoding="utf-8")
        rec["td_ledger_json_object"] = _catch(
            lambda: td.guard_ledger(ledger_obj, root), td.DispositionError)

        rec["resession_pause_array"] = _catch(
            lambda: rs.classify_pause([]), rs.ResessionRefusal)
        rec["resession_pause_none"] = _catch(
            lambda: rs.classify_pause(None), rs.ResessionRefusal)
        rec["resession_pause_str"] = _catch(
            lambda: rs.classify_pause("hold"), rs.ResessionRefusal)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    bites = []
    for name in ("scout_number", "hands_number", "scout_null", "hands_null",
                 "scout_true", "hands_true", "tax_out_is_dir",
                 "td_ledger_json_object", "resession_pause_array",
                 "resession_pause_str"):
        row = rec.get(name) or {}
        if row.get("crash"):
            bites.append(name)
        elif row.get("kind") is None and name not in ("resession_pause_none",):
            # silent return where a kind was expected
            if name.startswith(("resession_pause_array", "resession_pause_str",
                                "tax_out_is_dir", "td_ledger")):
                bites.append(name + ":silent_or_untyped_ok")
    rec["bites"] = bites
    rec["all_bite"] = bool(bites) or rec["close_refused_still_unraised"]
    rec["could_not_pin"] = (["CLOSE_REFUSED"] if rec["close_refused_still_unraised"] else [])

    OUT.write_text(json.dumps(rec, indent=1, default=str), encoding="utf-8")
    print(json.dumps(rec, indent=2, default=str))
    print("all_bite", rec["all_bite"], "bites", rec["bites"],
          "could_not_pin", rec["could_not_pin"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
