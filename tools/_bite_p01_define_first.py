#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bite: P01 MOTIF DEFINE-first. BUILD/CRITICS refuse without frozen statement.

    py -3.14 cosmos/_bite_p01_define_first.py
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent / "cosmos"
sys.path.insert(0, str(HERE))

from cosmos_kernel import install  # noqa: E402
from cosmos_motif_define import (  # noqa: E402
    MotifDefineError,
    frozen_statement,
    require_frozen_statement,
    stage_graph,
)
from cosmos_motif_run import start as motif_run_start  # noqa: E402
from cosmos_paths import CosmosPaths  # noqa: E402
from cosmos_studio import save_pack  # noqa: E402

OUT = HERE / "_bite_p01_define_first.json"


def main() -> int:
    td = Path(tempfile.mkdtemp(prefix="cosmos_bite_p01_"))
    root = install(td / "live", tree_id="p01-define-bite")
    paths = CosmosPaths(root)

    graph = stage_graph()
    nine_stage = len(graph) == 9 and graph[0]["id"] == "define"

    build_kind = None
    try:
        motif_run_start(paths, "build")
    except MotifDefineError as e:
        build_kind = e.kind

    critics_kind = None
    try:
        motif_run_start(paths, "critics")
    except MotifDefineError as e:
        critics_kind = e.kind

    empty_stmt = frozen_statement(paths)
    empty_build = False
    try:
        require_frozen_statement("build", empty_stmt)
    except MotifDefineError as e:
        empty_build = e.kind == "REFUSED"

    save_pack(paths, {"define": {"text": "WHAT: P01 bite. WHY: DEFINE-first."}})
    ok_rec = motif_run_start(paths, "build")
    with_define = (
        ok_rec.get("ok") is True
        and ok_rec.get("stage") == "build"
        and ok_rec.get("does_not_invent_traces") is True
        and str(ok_rec.get("define", {}).get("text", "")).startswith("WHAT: P01")
    )

    rec = {
        "nine_stage_graph": nine_stage,
        "build_without_define_kind": build_kind,
        "critics_without_define_kind": critics_kind,
        "empty_statement_build_refused": empty_build,
        "build_with_define_ok": with_define,
    }
    rec["all_bite"] = (
        rec["nine_stage_graph"] is True
        and rec["build_without_define_kind"] == "REFUSED"
        and rec["critics_without_define_kind"] == "REFUSED"
        and rec["empty_statement_build_refused"] is True
        and rec["build_with_define_ok"] is True
    )
    OUT.write_text(json.dumps(rec, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(rec, indent=2))
    return 0 if rec["all_bite"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
