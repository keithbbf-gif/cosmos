#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bite: F-30 forge rail is ABSENT / uncomposed on the pre-change tree.

Run against the live tree BEFORE the promotion, or against the staged
predecessor. Writes cosmos/_bite_f30_forge.json. all_bite is the required
pre-belief signal.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "cosmos" / "_bite_f30_forge.json"


def main() -> int:
    sys.path.insert(0, str(REPO / "cosmos"))
    sys.path.insert(0, str(REPO))
    rec = {"schema": "cosmos-f30-bite/1"}
    mod_path = REPO / "cosmos" / "cosmos_forge_rail.py"
    rec["module_path"] = str(mod_path)
    rec["module_exists"] = mod_path.is_file()
    rec["import_kind"] = None
    rec["import_ok"] = False
    try:
        import cosmos_forge_rail as m  # noqa: F401
        rec["import_ok"] = True
    except Exception as e:  # noqa: BLE001
        rec["import_kind"] = type(e).__name__
        rec["import_detail"] = str(e)[:200]

    kernel_src = (REPO / "cosmos" / "cosmos_kernel.py").read_text(encoding="utf-8")
    rec["kernel_has_forge_row"] = "cosmos_forge_rail" in kernel_src
    prober_src = (REPO / "cosmos" / "cosmos_rails_prober.py").read_text(
        encoding="utf-8")
    rec["prober_has_github_forge"] = "github-forge" in prober_src
    rec["prober_has_gitlab_forge"] = "gitlab-forge" in prober_src

    rec["all_bite"] = (
        rec["module_exists"] is False
        and rec["import_ok"] is False
        and rec["import_kind"] in ("ModuleNotFoundError", "ImportError")
        and rec["kernel_has_forge_row"] is False
        and rec["prober_has_github_forge"] is False
        and rec["prober_has_gitlab_forge"] is False
    )
    OUT.write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(rec, indent=1))
    return 0 if rec["all_bite"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
