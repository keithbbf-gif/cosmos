#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest for the F5 cosmos_paths spike. POSITIVE AND NEGATIVE controls, per the brief:
a gate tested only in the passing direction is a gate nobody has seen closed.
Runs under pytest OR as a plain script (exit 0/1) - the native queue lane has no pytest
guarantee, and a selftest that needs a framework to refuse is a framework dependency
dressed as a control.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cosmos_paths import (CosmosPaths, CosmosPathError, write_sentinel, extended,
                          SENTINEL_NAME, ROLES)

RESULTS = []


def check(label, fn):
    try:
        ok = bool(fn())
        RESULTS.append((label, ok, ""))
    except Exception as e:                                            # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


def expect_kind(kind):
    """Return a callable that runs f and asserts CosmosPathError with the right kind -
    the WRONG kind is a failure: typed absence means the type is the claim."""
    def wrap(f):
        def inner():
            try:
                f()
            except CosmosPathError as e:
                return e.kind == kind
            return False
        return inner
    return wrap


def main() -> int:
    td = Path(tempfile.mkdtemp(prefix="cosmos_spike_"))

    # ---- POSITIVE: two installs at two different roots (SETTABILITY) ----
    root_a = td / "installA" / "Ai" / "COSMOS"
    root_b = td / "elsewhere" / "Cosmos"          # different depth, different casing
    write_sentinel(root_a, tree_id="tree-A")
    write_sentinel(root_b, tree_id="tree-B")
    pa = CosmosPaths(root_a)
    pb = CosmosPaths(root_b)
    check("install A resolves", lambda: pa.root == root_a.resolve())
    check("install B resolves at a NON-default root (settability)",
          lambda: pb.root == root_b.resolve())
    check("two installs share no state", lambda: pa.sentinel.tree_id != pb.sentinel.tree_id)
    check("role API joins under the root", lambda: pa.queue("x.json").parts[-2] == "queue")
    check("every declared role resolves", lambda: all(pa.role(r) for r in ROLES))

    # ---- NEGATIVE: the four typed absences, each asserted BY KIND ----
    check("missing root -> NOT_FOUND",
          expect_kind("NOT_FOUND")(lambda: CosmosPaths(td / "nope")))
    empty = td / "existing_but_empty"
    empty.mkdir()
    check("existing-but-empty dir -> IDENTITY_MISMATCH (the mesh() scar)",
          expect_kind("IDENTITY_MISMATCH")(lambda: CosmosPaths(empty)))
    torn = td / "torn"
    torn.mkdir()
    (torn / SENTINEL_NAME).write_text("{ this is not json", encoding="utf-8")
    check("torn sentinel -> UNPARSEABLE (never read as free)",
          expect_kind("UNPARSEABLE")(lambda: CosmosPaths(torn)))
    alien = td / "alien"
    write_sentinel(alien, tree_id="x")
    (alien / SENTINEL_NAME).write_text(json.dumps({"system": "NOT-COSMOS"}), encoding="utf-8")
    check("wrong system -> IDENTITY_MISMATCH",
          expect_kind("IDENTITY_MISMATCH")(lambda: CosmosPaths(alien)))
    check("wrong tree_id -> IDENTITY_MISMATCH (a COSMOS root, not YOUR root)",
          expect_kind("IDENTITY_MISMATCH")(lambda: CosmosPaths(root_a, expected_tree_id="tree-B")))
    filenot = td / "afile"
    filenot.write_text("x", encoding="utf-8")
    check("root-is-a-file -> NOT_A_DIRECTORY",
          expect_kind("NOT_A_DIRECTORY")(lambda: CosmosPaths(filenot)))
    check("unknown role REFUSES (no plausible-path assembly)",
          expect_kind("NOT_FOUND")(lambda: pa.role("scratch")))
    check("install record absent -> NOT_FOUND refusal, no guessing",
          expect_kind("NOT_FOUND")(lambda: (os.environ.pop("COSMOS_INSTALL_RECORD", None),
                                            CosmosPaths.from_install_record())))

    # ---- MAX_PATH (NATIVE-DEMO measured; structural everywhere) ----
    deep = root_a
    for i in range(30):
        deep = deep / ("d%02d_padding_padding" % i)
    check("extended() never double-prefixes",
          lambda: extended(extended(deep)) == extended(deep))
    if os.name == "nt":
        # FINDING (first run, measured): plain pathlib.mkdir(parents=True) fails with
        # WinError 206/3 building this very tree - MAX_PATH bites at CREATION too.
        # The creation itself must go through extended(). This line IS a spike result.
        os.makedirs(extended(deep), exist_ok=True)
        target = Path(extended(deep / "leaf.txt"))
        target.write_text("deep", encoding="utf-8")
        check("MAX_PATH: >260-char path readable via extended() [NATIVE MEASURED, %d chars]"
              % len(str(deep / "leaf.txt")),
              lambda: Path(extended(deep / "leaf.txt")).read_text(encoding="utf-8") == "deep")
        check("walk() traverses past MAX_PATH",
              lambda: any("leaf.txt" in fs for _, _, fs in pa.walk("root")))
    else:
        RESULTS.append(("MAX_PATH native demo", True, "SKIPPED-NON-NATIVE"))

    # ---- import-time purity: importing the module touched no filesystem root ----
    check("no import-time side effects (module has no resolved global root)",
          lambda: not hasattr(sys.modules["cosmos_paths"], "ROOT"))

    bad = [(l, err) for l, ok, err in RESULTS if not ok]
    for label, ok, err in RESULTS:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label, ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks (%d negative controls asserted BY KIND)"
          % ("PASS" if not bad else "FAIL", len(RESULTS), 8))
    return 0 if not bad else 1


# pytest entry
def test_cosmos_paths():
    assert main() == 0


if __name__ == "__main__":
    sys.exit(main())
