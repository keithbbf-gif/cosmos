#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hermetic emit: BACKUP_VERIFIED.node and COMMAND_HANDLED.node.

Run: py -3.14 cosmos/_emit_follow_backup_command.py
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "cosmos"))

from cosmos_backup import Backup  # noqa: E402
from cosmos_command import COMMAND_NODE, Commander  # noqa: E402
from cosmos_kernel import Kernel, install  # noqa: E402
from cosmos_ledger import Ledger  # noqa: E402

OUT = REPO / "cosmos" / "_f_backup_command_follow.json"


def main() -> int:
    td = Path(tempfile.mkdtemp(prefix="cosmos_emit_follow_bc_"))
    root = install(td / "live", tree_id="follow-bc-emit")
    k = Kernel(root, worker="core-follow-bc")
    Commander(k).handle("status")
    ch = [r for r in k.ledger.verify() if r["event"] == "COMMAND_HANDLED"][-1]

    src = td / "src"
    src.mkdir()
    (src / "a.txt").write_text("alpha", encoding="utf-8")
    tgt = td / "tgt"
    tgt.mkdir()
    led = Ledger(td / "b.jsonl", b"k", "emit-bak")
    node = k.paths.sentinel.system
    br = Backup(led, node=node).run(src, tgt)
    bv = next(r for r in led.verify() if r["event"] == "BACKUP_VERIFIED")
    evidence = {
        "ok": bool(
            ch["payload"].get("node") == COMMAND_NODE
            and ch["payload"].get("ok") is True
            and bv["payload"].get("node") == node
            and node == "COSMOS"
            and br.get("files") == 1
        ),
        "command_handled": ch["payload"],
        "command_node": COMMAND_NODE,
        "backup_verified": {
            "node": bv["payload"].get("node"),
            "files": bv["payload"].get("files"),
            "verified": bv["payload"].get("verified"),
        },
        "sentinel_system": node,
        "clock_source_has_node": (
            "node=paths.sentinel.system"
            in "".join((REPO / "cosmos" / "cosmos_backup_clock.py")
                       .read_text(encoding="utf-8").split())
        ),
        "cli_source_has_node": (
            "node=k.paths.sentinel.system"
            in "".join((REPO / "cosmos" / "cosmos.py")
                       .read_text(encoding="utf-8").split())
        ),
    }
    OUT.write_text(json.dumps(evidence, indent=1), encoding="utf-8")
    print("ok=%s command.node=%s backup.node=%s files=%s"
          % (evidence["ok"], ch["payload"].get("node"),
             bv["payload"].get("node"), br.get("files")))
    print("EVIDENCE %s" % OUT)
    return 0 if evidence["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
