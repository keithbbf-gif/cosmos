#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_maker_hands - pin the probe's sentinel REFUSALS.

maker_hands_probe claims a typed refusal and will not guess: a missing
sentinel is NO_SENTINEL, a file that is not COSMOS is BAD_SENTINEL.
Existence of the directory is not identity (the empty-dir scar). Round-4
pins `e.kind` (the class used to be a message-only Exception).

Hermetic: throwaway dirs, no live root, no network, no secrets opened.

    py -3.14 builds/probe/test_maker_hands.py
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from maker_hands_probe import ProbeRefusal, _verify_root              # noqa: E402

RESULTS: list[tuple[str, bool, str]] = []


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:                                            # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


def _msg(fn) -> str | None:
    try:
        fn()
    except ProbeRefusal as e:
        return str(e)
    return None


def _kind(fn) -> str | None:
    try:
        fn()
    except ProbeRefusal as e:
        return getattr(e, "kind", None)
    return None


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="cosmos_hands_") as td:
        td = Path(td)
        empty = td / "empty_root"
        empty.mkdir()
        msg = _msg(lambda: _verify_root(str(empty)))
        check("a dir with no sentinel is NO_SENTINEL, not a guessed root",
              lambda: bool(msg) and str(msg).startswith("NO_SENTINEL:"))
        check("missing sentinel has kind=NO_SENTINEL (not just a message)",
              lambda: _kind(lambda: _verify_root(str(empty))) == "NO_SENTINEL")

        bogus = td / "bogus_root"
        bogus.mkdir()
        (bogus / ".cosmos-root.json").write_text(
            json.dumps({"system": "NOT-COSMOS", "tree_id": "x"}),
            encoding="utf-8")
        msg2 = _msg(lambda: _verify_root(str(bogus)))
        check("a sentinel that is not COSMOS is BAD_SENTINEL",
              lambda: bool(msg2) and str(msg2).startswith("BAD_SENTINEL:"))
        check("wrong-content sentinel has kind=BAD_SENTINEL",
              lambda: _kind(lambda: _verify_root(str(bogus))) == "BAD_SENTINEL")

        garbage = td / "garbage_root"
        garbage.mkdir()
        (garbage / ".cosmos-root.json").write_text("{not json", encoding="utf-8")
        check("unreadable sentinel JSON is BAD_SENTINEL, not JSONDecodeError",
              lambda: _kind(lambda: _verify_root(str(garbage))) == "BAD_SENTINEL")

        harr = td / "array_root"
        harr.mkdir()
        (harr / ".cosmos-root.json").write_text("[]", encoding="utf-8")
        check("JSON-array sentinel is BAD_SENTINEL, not AttributeError",
              lambda: _kind(lambda: _verify_root(str(harr))) == "BAD_SENTINEL")

        good = td / "good_root"
        good.mkdir()
        (good / ".cosmos-root.json").write_text(
            json.dumps({"system": "COSMOS", "tree_id": "KMesh-COSMOS-test"}),
            encoding="utf-8")
        doc = _verify_root(str(good))
        check("a real COSMOS sentinel is accepted and returns tree_id",
              lambda: doc.get("system") == "COSMOS"
              and doc.get("tree_id") == "KMesh-COSMOS-test")

        bite = HERE / "_bite_unpinned_round4.json"
        rec = json.loads(bite.read_text(encoding="utf-8")) if bite.is_file() else {}
        check("round4 bite records untyped ProbeRefusal (no .kind)",
              lambda: rec.get("all_bite") is True
              and rec.get("hands_missing_kind") is None
              and rec.get("hands_missing_has_kind_attr") is False)

        bite5 = HERE / "_bite_unpinned_round5.json"
        rec5 = json.loads(bite5.read_text(encoding="utf-8")) if bite5.is_file() else {}
        check("round5 bite records unreadable JSON as JSONDecodeError",
              lambda: rec5.get("all_bite") is True
              and rec5.get("hands_garbage_crash") == "JSONDecodeError"
              and rec5.get("hands_array_crash") == "AttributeError")

    bad = [r for r in RESULTS if not r[1]]
    for label, ok, err in RESULTS:
        print(f"  {'OK  ' if ok else 'FAIL'}  {label}{('  ' + err) if err else ''}")
    print("live_value: " + json.dumps(
        {"checks": len(RESULTS), "passed": len(RESULTS) - len(bad),
         "refusal_kinds": ["NO_SENTINEL", "BAD_SENTINEL"],
         "typed_kind_attr": True},
        sort_keys=True))
    print(f"result: {'ok' if not bad else 'FAIL'}  "
          f"{len(RESULTS) - len(bad)}/{len(RESULTS)}")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
