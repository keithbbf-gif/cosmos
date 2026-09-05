#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Suite wrapper for cosmos_refusals, plus the projection-freshness invariant.

Phase 5, docs/CORE_RESTRUCTURE.md. The module's own selftest carries the
substance -- that the surveyor is right about this tree AND that it detects
drift on a fixture whose answer is known. This file adds the one property that
cannot live inside the module: if `docs/REFUSAL_TAXONOMY.md` has been filed,
it must still MATCH a fresh render.

That check is the whole reason the taxonomy is generated instead of written. A
hand-maintained refusal table goes stale silently the first time somebody adds
a kind; a projection that is tested against its source cannot. If the doc is
absent (COW has not filed the proposal yet) this SKIPS cleanly rather than
failing -- an absent projection is not drift, and a suite that cannot pass by
construction is exactly what Phase 3 was cleaning up.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "cosmos"))

import cosmos_refusals as refusals  # noqa: E402

DOC = Path(__file__).resolve().parent.parent / "docs" / "REFUSAL_TAXONOMY.md"


def main() -> int:
    rc = refusals.selftest()
    if rc != 0:
        return rc

    sv = refusals.survey(Path(refusals.__file__).resolve().parent)
    fresh = refusals.render_table(sv)

    results = []
    if DOC.exists():
        on_disk = DOC.read_text(encoding="utf-8")
        results.append((
            "docs/REFUSAL_TAXONOMY.md still matches a fresh render",
            on_disk == fresh))
        if on_disk != fresh:
            print("  the filed projection has drifted from the code; "
                  f"regenerate: py -3.14 cosmos\\cosmos_refusals.py --out {DOC}")
    else:
        results.append((
            "docs/REFUSAL_TAXONOMY.md not filed yet -- projection check SKIPPED",
            True))

    for label, ok in results:
        print(f"  {'OK  ' if ok else 'FAIL'}  {label}")
    bad = [r for r in results if not r[1]]
    print("live_value: " + repr({
        "doc_filed": DOC.exists(),
        "render_chars": len(fresh),
        "typed_refusal_classes": sv["typed_refusal_classes"],
        "distinct_kinds": len(sv["kinds"]),
        "collisions": len(sv["collisions"]),
        "synonym_clusters": sorted(sv["synonym_clusters"]),
    }))
    print(f"result: {'ok' if not bad else 'FAIL'}  "
          f"{len(results) - len(bad)}/{len(results)} on the refusal projection")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
