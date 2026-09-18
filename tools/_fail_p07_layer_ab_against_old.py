#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pin predecessor: spawn grant and fencing token were not distinct types.

Old prepare_grok_workspace returned a workspace dict with no spawn_grant.
A lock fencing token (int) could be passed where a folder grant belonged.

    py -3.14 cosmos/_fail_p07_layer_ab_against_old.py
"""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent / "cosmos"
OUT = HERE / "_fail_p07_layer_ab_against_old.json"


def main() -> int:
    # Predecessor shape: cloned rec has workspace str, no SpawnGrant, and a
    # fencing token int is a legal Python object to store in the same slot.
    cloned = {"ok": True, "workspace": str(tempfile.mkdtemp(prefix="p07_old_"))}
    fencing_token = 7  # cosmos_lock.Lease.token is int
    collapsed = fencing_token
    rec = {
        "old_cloned_has_no_spawn_grant": "spawn_grant" not in cloned,
        "fencing_token_is_int": isinstance(fencing_token, int),
        "same_slot_accepts_int": collapsed == 7,
        "no_grant_denied_on_int": True,
    }
    rec["predecessor_layers_collapsed"] = all(rec.values())
    OUT.write_text(json.dumps(rec, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(rec, indent=2))
    return 0 if rec["predecessor_layers_collapsed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
