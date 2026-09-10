#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""P01 MOTIF DEFINE-first — BUILD/CRITICS refuse without frozen statement."""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "cosmos"))

from cosmos_kernel import install  # noqa: E402
from cosmos_motif_define import MotifDefineError, stage_graph  # noqa: E402
from cosmos_motif_run import start as motif_run_start  # noqa: E402
from cosmos_paths import CosmosPaths  # noqa: E402
from cosmos_studio import save_pack  # noqa: E402


def test_nine_stage_graph_reused():
    g = stage_graph()
    assert len(g) == 9
    assert g[0]["id"] == "define"
    assert g[4]["id"] == "build"
    assert g[5]["id"] == "critics"


def test_build_critics_refuse_empty_define():
    td = Path(tempfile.mkdtemp(prefix="p01_"))
    paths = CosmosPaths(install(td / "live", tree_id="p01-test"))
    for stage in ("build", "critics"):
        try:
            motif_run_start(paths, stage)
        except MotifDefineError as e:
            assert e.kind == "REFUSED"
        else:
            raise AssertionError(f"{stage} must REFUSED without define")


def test_build_ok_with_studio_define():
    td = Path(tempfile.mkdtemp(prefix="p01ok_"))
    paths = CosmosPaths(install(td / "live", tree_id="p01-ok"))
    save_pack(paths, {"define": {"text": "WHAT: x. WHY: y."}})
    rec = motif_run_start(paths, "build")
    assert rec["ok"] is True
    assert rec["does_not_invent_traces"] is True


def main() -> int:
    test_nine_stage_graph_reused()
    test_build_critics_refuse_empty_define()
    test_build_ok_with_studio_define()
    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
