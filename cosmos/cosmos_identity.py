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

# F-56 (WISHLIST FEDERATION). Named LAN machines, not yet installed.
# host is None until Keith names an address — existence of this table is
# not reachability. probe_lan_node() is the measurement.
LAN_NODES = {
    "SRV1": {
        "id": "SRV1",
        "alias": "SRV1",
        "role": "storage",
        "os": "Linux/Win10",
        "capacity": "9 TB",
        "host": None,
        "status": "not_installed",
    },
    "T7": {
        "id": "T7",
        "alias": "T7920",
        "role": "compute",
        "os": "Linux",
        "cores": 56,
        "ram_gb": 128,
        "ram_mhz": 2666,
        "host": None,
        "status": "not_installed",
    },
}


class FederationError(RuntimeError):
    """kind in {UNKNOWN_NODE, NO_HOST, UNREACHABLE}."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


def lan_node(node_id: str) -> dict:
    """Lookup by id or alias (T7 == T7920). UNKNOWN_NODE is typed."""
    key = str(node_id or "").strip()
    if key in LAN_NODES:
        return dict(LAN_NODES[key])
    folded = key.upper()
    for rec in LAN_NODES.values():
        if rec["id"].upper() == folded or rec["alias"].upper() == folded:
            return dict(rec)
    raise FederationError("UNKNOWN_NODE", f"no LAN node {node_id!r}")


def probe_lan_node(node_id: str, *, transport=None) -> dict:
    """Measure one LAN node. Default host is None → NO_HOST, never READY.

    transport(host) -> dict is the test seam. Production has no host to
    call until Keith names one; this function does not invent an address.
    """
    rec = lan_node(node_id)
    host = rec.get("host")
    out = {
        "id": rec["id"],
        "alias": rec["alias"],
        "ok": False,
        "reachable": False,
        "status": rec.get("status"),
        "host": host,
        "kind": "NO_HOST",
        "detail": "host is unset; Keith names an address, this function does not",
    }
    if not host:
        return out
    fetch = transport or (lambda _h: {
        "ok": False, "kind": "UNREACHABLE",
        "detail": "no transport; federation wire is not installed",
    })
    try:
        got = fetch(host)
    except Exception as e:  # noqa: BLE001
        got = {"ok": False, "kind": "UNREACHABLE",
               "detail": f"{type(e).__name__}: {e}"}
    if not isinstance(got, dict):
        got = {"ok": False, "kind": "UNREACHABLE",
               "detail": f"transport returned {type(got).__name__}"}
    out["kind"] = got.get("kind") or ("READY" if got.get("ok") else "UNREACHABLE")
    out["ok"] = bool(got.get("ok"))
    out["reachable"] = bool(got.get("ok"))
    out["detail"] = got.get("detail") or out["detail"]
    return out


def federation_blockers() -> list[str]:
    """The gate, as a function. COUNT THE LIST - never quote a remembered number."""
    lan = ", ".join(
        f"{n['id']}/{n['alias']}" if n["alias"] != n["id"] else n["id"]
        for n in LAN_NODES.values())
    return [
        "no live peer (JMesh not yet installed and reachable; LAN nodes "
        f"{lan} are declared, not installed)",
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