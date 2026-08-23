#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_identity - WHO THIS INSTALL IS + the federation seam (F5 builder).
Designed-for-now, delivered-when-gated (ratified goal): the interfaces exist, the
blockers are ASKED FROM THE FUNCTION, and federation is never reported working while
any blocker stands. One constant is all a new peer changes - renaming trees is a fork.

Do not count in prose. Ask federation_ready() (the four-blockers-for-eleven-days scar).
GMesh stays UNASSIGNED - two people answer to G, and an identity constant two people
could answer to resolves to the wrong node (Keith assigns; nobody guesses).
"""
from __future__ import annotations

MESH_ID = "KMesh"
OWNER = "Keith"

PEERS = {
    "JMesh": {"owner": "Jack", "status": "building"},
    "HMesh": {"owner": "Harrison", "status": "planned"},
    # Grant and Grayson: IDs UNASSIGNED - Keith assigns; an ambiguous G resolves wrong.
}


def federation_blockers() -> list[str]:
    """The gate, as a function. COUNT THE LIST - never quote a remembered number."""
    return [
        "no live peer (JMesh not yet installed and reachable)",
        "no meeting point (LAN NAS does not exist; G: was a USB enclosure wearing a "
        "NAS label)",
        "no wire protocol (message schema exists in cosmos_mail; transport between "
        "machines does not)",
        "no trust model (peer identity is a name, not a verified credential)",
        "no notarization of control files across peers (tree_lock's content-hash "
        "fingerprint closes this LOCALLY; cross-peer TOCTOU remains)",
    ]


def federation_ready() -> bool:
    return len(federation_blockers()) == 0
