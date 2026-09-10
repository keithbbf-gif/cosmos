#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bite: P06 COMPARE stays UNMEASURED until obs.jsonl has rows.

    py -3.14 cosmos/_bite_p06_unmeasured.py
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from cosmos_kernel import install  # noqa: E402
from cosmos_p06_compare import compare_box_token  # noqa: E402
from cosmos_paths import CosmosPaths  # noqa: E402
from cosmos_porosity import PorosityError, snapshot  # noqa: E402

OUT = HERE / "_bite_p06_unmeasured.json"


def main() -> int:
    td = Path(tempfile.mkdtemp(prefix="cosmos_bite_p06_"))
    root = install(td / "live", tree_id="bite-p06")
    paths = CosmosPaths(root)

    luna = "openai/gpt-5.6-luna"
    sol = "openai/gpt-5.6-sol"
    glm = "z-ai/glm-5.3-flash"
    ds = "deepseek/deepseek-v4-flash-0731"

    cmp0 = compare_box_token(
        paths, box_agents=[glm, ds], token_agents=[luna])
    snap0 = snapshot(
        paths, profile="forge", agents=[glm, ds, luna])

    same_fam_kind = None
    try:
        compare_box_token(paths, box_agents=[luna, sol], token_agents=[])
    except PorosityError as e:
        same_fam_kind = e.kind

    rot_kind = None
    try:
        compare_box_token(
            paths, box_agents=["openrouter/free"], token_agents=[glm])
    except PorosityError as e:
        rot_kind = e.kind

    rec = {
        "compare_kind": cmp0.get("compare_kind"),
        "compare_n_obs": cmp0.get("n_obs"),
        "compare_pair_is_none": cmp0.get("pair") is None,
        "compare_coverage_n_is_none": cmp0.get("coverage_n") is None,
        "compare_pairs_empty": cmp0.get("pairs") == [],
        "snap_kind": snap0.get("kind"),
        "snap_n_obs": snap0.get("n_obs"),
        "snap_pairs_empty": snap0.get("pairs") == [],
        "snap_no_coverage_key": "coverage" not in snap0,
        "same_family_refused": same_fam_kind,
        "rotator_refused": rot_kind,
    }
    rec["all_bite"] = (
        rec["compare_kind"] == "UNMEASURED"
        and rec["compare_n_obs"] == 0
        and rec["compare_pair_is_none"] is True
        and rec["compare_coverage_n_is_none"] is True
        and rec["compare_pairs_empty"] is True
        and rec["snap_kind"] == "UNMEASURED"
        and rec["snap_n_obs"] == 0
        and rec["snap_pairs_empty"] is True
        and rec["snap_no_coverage_key"] is True
        and rec["same_family_refused"] == "REFUSED"
        and rec["rotator_refused"] == "REFUSED"
    )
    OUT.write_text(json.dumps(rec, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(rec, indent=2))
    return 0 if rec["all_bite"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
