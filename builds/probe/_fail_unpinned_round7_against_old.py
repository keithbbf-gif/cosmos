#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""New round-7 pins MUST FAIL against the staged predecessor.

Staged at builds/probe/_delme/predispose_unpinned_round7_20260831T174500Z/

Predecessor (measured `_bite_unpinned_round7.json`):
  * guard_ledger vs JSON bool/array sentinel — AttributeError
  * apply_proposals bundle=[] / proposals="APPLY" / None — AttributeError
  * fingerprint(repo, "one/file.py")         — silent character keys
  * fingerprint(repo, None)                  — TypeError
  * compare("stale", live)                   — AttributeError
  * stamp([], ...)                           — TypeError

CLOSE_REFUSED is documented and never raised; this script does not invent
a satellite close path.

    py -3.14 builds/probe/_fail_unpinned_round7_against_old.py
"""
from __future__ import annotations

import json
import sys
import tempfile
import types
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
OUT = HERE / "_fail_unpinned_round7_against_old.json"
OLD = HERE / "_delme" / "predispose_unpinned_round7_20260831T174500Z"


def _exec(path: Path, name: str, extra_path=None) -> types.ModuleType:
    mod = types.ModuleType(name)
    mod.__file__ = str(path)
    sys.modules[name] = mod
    if extra_path:
        sys.path.insert(0, str(extra_path))
    exec(compile(path.read_text(encoding="utf-8"), str(path), "exec"),
         mod.__dict__)
    return mod


def main() -> int:
    failed = []
    ran = []
    sys.path.insert(0, str(HERE))
    sys.path.insert(0, str(REPO / "cosmos"))
    if not (OLD / "tool_disposition.py").is_file():
        raise SystemExit(f"missing predecessor {OLD}")

    old_td = _exec(OLD / "tool_disposition.py", "tool_disposition")
    old_af = _exec(OLD / "artifact_freshness.py", "artifact_freshness")

    tmp = Path(tempfile.mkdtemp(prefix="cosmos_fold7_"))
    live = tmp / "live"
    live.mkdir()
    from cosmos_paths import write_sentinel
    write_sentinel(live, "KMesh-COSMOS-live")
    scratch = tmp / "scratch.jsonl"
    scratch.write_text("", encoding="utf-8")
    rotten = tmp / "rotten"
    rotten.mkdir()
    (rotten / ".cosmos-root.json").write_text("true", encoding="utf-8")

    def _want_kind(label, fn, kind, err_cls):
        ran.append(label)
        try:
            got = fn()
            failed.append(f"{label}:returned:{type(got).__name__}:{got!r}"[:140])
        except err_cls as e:
            got_kind = getattr(e, "kind", None)
            if got_kind != kind:
                failed.append(f"{label}:{got_kind}")
        except Exception as e:                                        # noqa: BLE001
            failed.append(f"{label}:{type(e).__name__}")

    def _want_eq(label, fn, expected):
        ran.append(label)
        try:
            got = fn()
            if got != expected:
                failed.append(f"{label}:got:{got!r}"[:140])
        except Exception as e:                                        # noqa: BLE001
            failed.append(f"{label}:{type(e).__name__}")

    _want_kind("bool_sentinel_is_BAD_ROOT",
               lambda: old_td.guard_ledger(scratch, rotten),
               "BAD_ROOT", old_td.DispositionError)
    _want_kind("apply_bundle_list_is_BAD_BUNDLE",
               lambda: old_td.apply_proposals(None, [], ledger_path=scratch,
                                              live_root=live),
               "BAD_BUNDLE", old_td.DispositionError)
    _want_kind("apply_proposals_str_is_BAD_BUNDLE",
               lambda: old_td.apply_proposals(None, {"proposals": "APPLY"},
                                              ledger_path=scratch,
                                              live_root=live),
               "BAD_BUNDLE", old_td.DispositionError)
    _want_kind("apply_bundle_none_is_BAD_BUNDLE",
               lambda: old_td.apply_proposals(None, None, ledger_path=scratch,
                                              live_root=live),
               "BAD_BUNDLE", old_td.DispositionError)

    err_cls = getattr(old_af, "FreshnessError", Exception)
    _want_kind("fingerprint_str_is_BAD_RELS",
               lambda: old_af.fingerprint(tmp, "one/file.py"),
               "BAD_RELS", err_cls)
    _want_kind("fingerprint_none_is_BAD_RELS",
               lambda: old_af.fingerprint(tmp, None),
               "BAD_RELS", err_cls)
    _want_eq("compare_str_is_UNFINGERPRINTED",
             lambda: old_af.compare("stale", {"a": {"exists": True}})["kind"],
             "UNFINGERPRINTED")
    _want_kind("stamp_list_is_BAD_REC",
               lambda: old_af.stamp([], tmp, ["a.py"]),
               "BAD_REC", err_cls)

    rec = {
        "schema": "cosmos-fail-old/1",
        "what": "round7 unpinned probe pins against predecessor",
        "predecessor": str(OLD),
        "ran": ran,
        "failed": failed,
        "n_ran": len(ran),
        "n_failed": len(failed),
        "all_new_pins_failed": bool(failed) and len(failed) == len(ran),
        "could_not_pin": ["CLOSE_REFUSED"],
    }
    OUT.write_text(json.dumps(rec, indent=1, default=str), encoding="utf-8")
    print(json.dumps(rec, indent=2, default=str))
    print(f"{len(failed)}/{len(ran)} FAIL  all_new_pins_failed={rec['all_new_pins_failed']}")
    return 0 if rec["all_new_pins_failed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
