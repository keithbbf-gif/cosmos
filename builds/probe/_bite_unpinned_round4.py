#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bite: round-4 unpinned probe refusals against CURRENT (pre-fix) code.

  * maker_hands ProbeRefusal is a message, not a kind — no .kind to branch on.
  * scout missing sentinel is NO_ROOT (docstring lists NO_ROOT_SENTINEL).
  * taxonomy write-then-readback mismatch: without the after!=fresh raise,
    tick reports healed over bytes it did not actually land.

    py -3.14 builds/probe/_bite_unpinned_round4.py
"""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
OUT = HERE / "_bite_unpinned_round4.json"

from maker_hands_probe import ProbeRefusal, _verify_root              # noqa: E402
from cosmos_newai_scout import ScoutRefusal, verify_root              # noqa: E402
import regen_refusal_taxonomy as regen                                # noqa: E402


def main() -> int:
    rec = {"schema": "cosmos-bite/1",
           "what": "round4 unpinned probe refusals — current vs claimed"}
    tmp = Path(tempfile.mkdtemp(prefix="cosmos_bite4p_"))
    try:
        empty = tmp / "empty_root"
        empty.mkdir()
        try:
            _verify_root(str(empty))
            rec["hands_missing_kind"] = None
            rec["hands_missing_has_kind_attr"] = False
            rec["hands_missing_crash"] = None
        except ProbeRefusal as e:
            rec["hands_missing_kind"] = getattr(e, "kind", None)
            rec["hands_missing_has_kind_attr"] = hasattr(e, "kind")
            rec["hands_missing_msg"] = str(e)[:80]
            rec["hands_missing_crash"] = None
        except Exception as e:                                        # noqa: BLE001
            rec["hands_missing_kind"] = None
            rec["hands_missing_has_kind_attr"] = False
            rec["hands_missing_crash"] = type(e).__name__

        missing = tmp / "no_sentinel"
        missing.mkdir()
        try:
            verify_root(missing)
            rec["scout_missing_kind"] = None
            rec["scout_missing_crash"] = None
        except ScoutRefusal as e:
            rec["scout_missing_kind"] = e.kind
            rec["scout_missing_crash"] = None
        except Exception as e:                                        # noqa: BLE001
            rec["scout_missing_kind"] = None
            rec["scout_missing_crash"] = type(e).__name__

        garbage = tmp / "garbage"
        garbage.mkdir()
        (garbage / ".cosmos-root.json").write_text("{not json", encoding="utf-8")
        try:
            verify_root(garbage)
            rec["scout_garbage_kind"] = None
            rec["scout_garbage_crash"] = None
        except ScoutRefusal as e:
            rec["scout_garbage_kind"] = e.kind
            rec["scout_garbage_crash"] = None
        except Exception as e:                                        # noqa: BLE001
            rec["scout_garbage_kind"] = None
            rec["scout_garbage_crash"] = type(e).__name__

        # Strip the readback check and show tick heals over a lie.
        src = (HERE / "regen_refusal_taxonomy.py").read_text(encoding="utf-8")
        needle = (
            "        after = read_doc(doc)\n"
            "        if after != fresh:\n"
            "            raise TaxonomyRegenError(\n"
            "                \"UNWRITABLE\",\n"
            "                f\"wrote {doc} but read-back does not match the render\",\n"
            "            )\n"
        )
        rec["readback_raise_present"] = needle in src
        stripped = src.replace(needle, "        after = read_doc(doc)\n")
        rec["readback_stripped"] = stripped != src and needle not in stripped

        ns: dict = {"__file__": str(HERE / "regen_refusal_taxonomy.py"),
                    "__name__": "regen_stripped"}
        exec(compile(stripped, str(HERE / "regen_refusal_taxonomy.py"), "exec"), ns)
        fake_repo = tmp / "taxrepo"
        (fake_repo / "docs").mkdir(parents=True)
        (fake_repo / "docs" / "REFUSAL_TAXONOMY.md").write_text(
            "DRIFTED\n", encoding="utf-8")

        def lie_write(path: Path, text: str) -> None:
            path.write_text("WRONG-BYTES", encoding="utf-8", newline="\n")

        ns["write_utf8"] = lie_write
        ns["fresh_render"] = lambda refusals=None: (
            "FRESH-RENDER\n",
            {"typed_refusal_classes": 0, "kinds": [], "modules_parsed": 0},
        )
        ns["load_generator"] = lambda: None
        try:
            payload = ns["tick"](repo=fake_repo, write=True)
            rec["readback_old_kind"] = payload.get("kind")
            rec["readback_old_healed"] = payload.get("healed")
            rec["readback_old_raised"] = False
            rec["readback_old_disk"] = (
                (fake_repo / "docs" / "REFUSAL_TAXONOMY.md")
                .read_text(encoding="utf-8")
            )
        except ns["TaxonomyRegenError"] as e:
            rec["readback_old_kind"] = e.kind
            rec["readback_old_healed"] = None
            rec["readback_old_raised"] = True
            rec["readback_old_disk"] = None
        except Exception as e:                                        # noqa: BLE001
            rec["readback_old_kind"] = None
            rec["readback_old_healed"] = None
            rec["readback_old_raised"] = True
            rec["readback_old_crash"] = f"{type(e).__name__}: {e}"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    rec["all_bite"] = (
        rec.get("hands_missing_kind") is None
        and rec.get("hands_missing_has_kind_attr") is False
        and rec.get("scout_missing_kind") == "NO_ROOT"
        and rec.get("scout_garbage_kind") == "NO_ROOT"
        and rec.get("readback_raise_present") is True
        and rec.get("readback_stripped") is True
        and rec.get("readback_old_raised") is False
        and rec.get("readback_old_healed") is True
        and rec.get("readback_old_disk") == "WRONG-BYTES"
    )
    OUT.write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(rec, indent=1))
    return 0 if rec["all_bite"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
