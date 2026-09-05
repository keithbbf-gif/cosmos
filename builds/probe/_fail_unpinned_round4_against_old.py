#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""New round-4 probe pins MUST FAIL against the staged predecessor.

Staged at builds/probe/_delme/predispose_unpinned_round4_20260831T142253Z/

  * maker_hands ProbeRefusal has no .kind
  * scout missing sentinel is NO_ROOT, not NO_ROOT_SENTINEL
  * taxonomy write-then-readback without the after!=fresh raise heals a lie

    py -3.14 builds/probe/_fail_unpinned_round4_against_old.py
"""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
import types
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "_fail_unpinned_round4_against_old.json"
OLD = HERE / "_delme" / "predispose_unpinned_round4_20260831T142253Z"


def _exec(path: Path, name: str, src: str | None = None) -> types.ModuleType:
    mod = types.ModuleType(name)
    mod.__file__ = str(path)
    sys.modules[name] = mod
    text = src if src is not None else path.read_text(encoding="utf-8")
    exec(compile(text, str(path), "exec"), mod.__dict__)
    return mod


def main() -> int:
    failed = []
    ran = []
    tmp = Path(tempfile.mkdtemp(prefix="cosmos_failold_r4p_"))
    try:
        old_h = _exec(OLD / "maker_hands_probe.py", "hands_old_r4")
        empty = tmp / "empty_root"
        empty.mkdir()
        ran.append("hands_NO_SENTINEL_kind")
        try:
            old_h._verify_root(str(empty))
            failed.append("hands_NO_SENTINEL_kind:did_not_raise")
        except old_h.ProbeRefusal as e:
            kind = getattr(e, "kind", None)
            if kind == "NO_SENTINEL":
                pass  # old already had the kind — pin did not fail
            else:
                failed.append(f"hands_NO_SENTINEL_kind:{kind}")
        except Exception as e:                                        # noqa: BLE001
            failed.append(f"hands_NO_SENTINEL_kind:{type(e).__name__}")

        scout_src = (OLD / "cosmos_newai_scout.py").read_text(encoding="utf-8")
        old_s = _exec(OLD / "cosmos_newai_scout.py", "scout_old_r4")
        missing = tmp / "no_sentinel"
        missing.mkdir()
        ran.append("scout_NO_ROOT_SENTINEL")
        try:
            old_s.verify_root(missing)
            failed.append("scout_NO_ROOT_SENTINEL:did_not_raise")
        except old_s.ScoutRefusal as e:
            if e.kind != "NO_ROOT_SENTINEL":
                failed.append(f"scout_NO_ROOT_SENTINEL:{e.kind}")
        except Exception as e:                                        # noqa: BLE001
            failed.append(f"scout_NO_ROOT_SENTINEL:{type(e).__name__}")

        stripped_unr = scout_src.replace(
            '    try:\n'
            '        doc = json.loads(sentinel.read_text(encoding="utf-8"))\n'
            '    except (OSError, ValueError, UnicodeDecodeError) as e:\n'
            '        raise ScoutRefusal("NO_ROOT", f"unreadable sentinel: {type(e).__name__}: {e}") from e\n',
            '    doc = json.loads(sentinel.read_text(encoding="utf-8"))\n',
        )
        if stripped_unr == scout_src:
            failed.append("scout_unreadable:strip_noop")
        old_s2 = _exec(OLD / "cosmos_newai_scout.py", "scout_old_r4u", stripped_unr)
        garbage = tmp / "garbage"
        garbage.mkdir()
        (garbage / ".cosmos-root.json").write_text("{not json", encoding="utf-8")
        ran.append("scout_unreadable_NO_ROOT")
        try:
            old_s2.verify_root(garbage)
            failed.append("scout_unreadable_NO_ROOT:did_not_raise")
        except old_s2.ScoutRefusal as e:
            if e.kind != "NO_ROOT":
                failed.append(f"scout_unreadable_NO_ROOT:{e.kind}")
        except Exception as e:                                        # noqa: BLE001
            failed.append(f"scout_unreadable_NO_ROOT:{type(e).__name__}")

        src = (OLD / "regen_refusal_taxonomy.py").read_text(encoding="utf-8")
        needle = (
            "        after = read_doc(doc)\n"
            "        if after != fresh:\n"
            "            raise TaxonomyRegenError(\n"
            "                \"UNWRITABLE\",\n"
            "                f\"wrote {doc} but read-back does not match the render\",\n"
            "            )\n"
        )
        stripped = src.replace(needle, "        after = read_doc(doc)\n")
        if stripped == src:
            failed.append("readback:strip_noop")
        ns: dict = {"__file__": str(OLD / "regen_refusal_taxonomy.py"),
                    "__name__": "regen_old_r4"}
        exec(compile(stripped, str(OLD / "regen_refusal_taxonomy.py"), "exec"), ns)
        fake = tmp / "taxrepo"
        (fake / "docs").mkdir(parents=True)
        (fake / "docs" / "REFUSAL_TAXONOMY.md").write_text(
            "DRIFTED\n", encoding="utf-8")

        def lie_write(path: Path, text: str) -> None:
            path.write_text("WRONG-BYTES", encoding="utf-8", newline="\n")

        ns["write_utf8"] = lie_write
        ns["fresh_render"] = lambda refusals=None: (
            "FRESH-RENDER\n",
            {"typed_refusal_classes": 0, "kinds": [], "modules_parsed": 0},
        )
        ns["load_generator"] = lambda: None
        ran.append("tax_UNWRITABLE_readback")
        try:
            ns["tick"](repo=fake, write=True)
            failed.append("tax_UNWRITABLE_readback:did_not_raise")
        except ns["TaxonomyRegenError"] as e:
            if e.kind != "UNWRITABLE":
                failed.append(f"tax_UNWRITABLE_readback:{e.kind}")
        except Exception as e:                                        # noqa: BLE001
            failed.append(f"tax_UNWRITABLE_readback:{type(e).__name__}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    out = {
        "schema": "cosmos-fail-against-old/1",
        "what": "round4 probe pins FAIL against staged predecessor / stripped readback",
        "predecessor": str(OLD),
        "ran": ran,
        "failed": failed,
        "all_new_pins_failed": bool(ran) and len(failed) == len(ran),
    }
    OUT.write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=1))
    return 0 if out["all_new_pins_failed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
