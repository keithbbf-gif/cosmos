#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bite: durable BootUP.json gate (NO_BOOTUP when missing/closed).

    py -3.14 cosmos/_bite_bootup.py
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent / "cosmos"
sys.path.insert(0, str(HERE))

from cosmos_kernel import Kernel, install  # noqa: E402
from cosmos_session import (  # noqa: E402
    SessionError,
    bootup_path,
    read_bootup,
    require_bootup,
)

OUT = HERE / "_bite_bootup.json"


def main() -> int:
    td = Path(tempfile.mkdtemp(prefix="cosmos_bite_bootup_"))
    root = install(td / "live", tree_id="bootup-bite")
    k = Kernel(root, worker="bite")
    sm = k.sessions
    bp = bootup_path(k.paths)

    missing_kind = None
    try:
        require_bootup(k.paths)
    except SessionError as e:
        missing_kind = e.kind

    sm.open("s0", "Cm")
    sm.session.record_fact("lane", "bite")
    sm.close_session(handoff_to="s1")
    closed_after_tidy = bp.is_file() and read_bootup(k.paths).get("open") is False
    closed_kind = None
    try:
        require_bootup(k.paths)
    except SessionError as e:
        closed_kind = e.kind

    sm.start_session("Cm")
    opened = read_bootup(k.paths).get("open") is True
    gate_ok = require_bootup(k.paths).get("stream") == "Cm"

    k2 = Kernel(root, worker="bite-b")
    survives = require_bootup(k2.paths).get("open") is True

    sm.close_session(handoff_to="next")
    after_close = read_bootup(k.paths).get("open") is False

    rec = {
        "missing_is_no_bootup": missing_kind == "NO_BOOTUP",
        "close_writes_open_false": closed_after_tidy,
        "closed_is_no_bootup": closed_kind == "NO_BOOTUP",
        "start_writes_open_true": opened,
        "require_bootup_open": gate_ok,
        "survives_new_kernel": survives,
        "close_clears_gate": after_close,
    }
    rec["all_bite"] = all(rec.values())
    OUT.write_text(json.dumps(rec, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(rec, indent=2))
    return 0 if rec["all_bite"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
