#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bite: round-5 unpinned probe refusals against CURRENT (pre-fix) code.

  * scout sentinel that is valid JSON but not an object (`[]`) — AttributeError
  * maker_hands unreadable sentinel JSON `{not json`            — JSONDecodeError
  * maker_hands sentinel that is a JSON array                    — AttributeError

Expected (and required before belief): all_bite == true.

    py -3.14 builds/probe/_bite_unpinned_round5.py
"""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
OUT = HERE / "_bite_unpinned_round5.json"

from maker_hands_probe import ProbeRefusal, _verify_root              # noqa: E402
from cosmos_newai_scout import ScoutRefusal, verify_root              # noqa: E402


def main() -> int:
    rec = {"schema": "cosmos-bite/1",
           "what": "round5 unpinned probe refusals — current vs claimed"}
    tmp = Path(tempfile.mkdtemp(prefix="cosmos_bite5p_"))
    try:
        arr = tmp / "arr_root"
        arr.mkdir()
        (arr / ".cosmos-root.json").write_text("[]", encoding="utf-8")
        try:
            verify_root(arr)
            rec["scout_array_kind"] = None
            rec["scout_array_crash"] = None
        except ScoutRefusal as e:
            rec["scout_array_kind"] = e.kind
            rec["scout_array_crash"] = None
        except Exception as e:                                        # noqa: BLE001
            rec["scout_array_kind"] = None
            rec["scout_array_crash"] = type(e).__name__

        garbage = tmp / "hands_garbage"
        garbage.mkdir()
        (garbage / ".cosmos-root.json").write_text("{not json", encoding="utf-8")
        try:
            _verify_root(str(garbage))
            rec["hands_garbage_kind"] = None
            rec["hands_garbage_crash"] = None
            rec["hands_garbage_has_kind"] = False
        except ProbeRefusal as e:
            rec["hands_garbage_kind"] = getattr(e, "kind", None)
            rec["hands_garbage_crash"] = None
            rec["hands_garbage_has_kind"] = hasattr(e, "kind")
        except Exception as e:                                        # noqa: BLE001
            rec["hands_garbage_kind"] = None
            rec["hands_garbage_crash"] = type(e).__name__
            rec["hands_garbage_has_kind"] = False

        harr = tmp / "hands_arr"
        harr.mkdir()
        (harr / ".cosmos-root.json").write_text("[]", encoding="utf-8")
        try:
            _verify_root(str(harr))
            rec["hands_array_kind"] = None
            rec["hands_array_crash"] = None
        except ProbeRefusal as e:
            rec["hands_array_kind"] = getattr(e, "kind", None)
            rec["hands_array_crash"] = None
        except Exception as e:                                        # noqa: BLE001
            rec["hands_array_kind"] = None
            rec["hands_array_crash"] = type(e).__name__
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    rec["all_bite"] = (
        rec.get("scout_array_kind") is None
        and rec.get("scout_array_crash") == "AttributeError"
        and rec.get("hands_garbage_kind") is None
        and rec.get("hands_garbage_crash") == "JSONDecodeError"
        and rec.get("hands_array_kind") is None
        and rec.get("hands_array_crash") == "AttributeError"
    )
    OUT.write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(rec, indent=1))
    return 0 if rec["all_bite"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
