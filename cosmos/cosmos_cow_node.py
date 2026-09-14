#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_cow_node — CoW (Claude/Cowork) as a first-class mesh node.

CoW VERIFY, SYNTHESISE, ORCHESTRATE. It does not do the reading.
SGH+GBW are the same xAI family — they are not independent checks of
each other; that note is canon on this row, not a measurement.

Registry honesty: `model` is the vendor-emitted responder name only,
and `verified` is True only after a real live call that named one.
A stale proof is STALE (verified False), never a green memory.
age_s is null when unmeasured — never 0.
"""
from __future__ import annotations

LINK_ID = "cow"
NODE_ID = "cow"
LABEL = "CoW"
PRODUCT = "Claude/Cowork"
RAIL_TYPE = "CHAT"
SRC = "core"
DST = "orch"
FAMILY = "anthropic-cowork"
ROLE = "VERIFY, SYNTHESISE, ORCHESTRATE"
DOES_NOT = "read"
INDEPENDENCE_NOTE = "SGH+GBW are not independent checks of each other"
INDEPENDENCE = {
    "note": INDEPENDENCE_NOTE,
    "same_family": ["SGH", "GBW"],
    "family": "xai",
}
# probe_module_for / SATELLITES owner. Not cosmos_claude_rail — claude-cli
# remains the only Anthropic-default WIRED_NODES row (F-24 / test_codex_wired).
PROBE_MODULE = "cosmos_cow_node"


def _age_s(row: dict | None) -> float | None:
    """UNMEASURED is None, never 0."""
    if not row:
        return None
    age = row.get("age_s")
    if age is None:
        return None
    try:
        return float(age)
    except (TypeError, ValueError):
        return None


def bind_row(proof: dict | None, *, ttl_s: float | None = 3600.0) -> dict:
    """Honest COW node row for GET /nodemap. Empty is explicit."""
    rec = proof if isinstance(proof, dict) else {}
    model = str(rec.get("model") or "").strip()
    age = _age_s(rec)
    ok = rec.get("ok")
    verified_claim = rec.get("verified")
    rc = rec.get("rc")
    body_bytes = rec.get("body_bytes")
    has_proof = bool(model) and (ok is True or verified_claim is True) and (
        rc in (0, "0", None) or verified_claim is True
    )
    if verified_claim is False and rec.get("proof_state") == "STALE":
        state = "STALE"
        verified: bool | None = False
    elif has_proof and age is not None and ttl_s is not None and age > ttl_s:
        state = "STALE"
        verified = False
    elif has_proof and (ttl_s is None or age is not None):
        state = "LIVE"
        verified = True
    elif rec.get("link_id") == LINK_ID or rec.get("id") == NODE_ID:
        state = "UNMEASURED"
        verified = None
        model = model if has_proof else ""
    else:
        state = "UNMEASURED"
        verified = None
        model = ""
    return {
        "id": NODE_ID,
        "link_id": LINK_ID,
        "label": LABEL,
        "type": "node",
        "product": PRODUCT,
        "family": FAMILY,
        "role": ROLE,
        "does_not": DOES_NOT,
        "rail": LINK_ID,
        "rail_type": RAIL_TYPE,
        "route": f"{SRC}->{DST}",
        "model": model,
        "model_source": str(rec.get("model_source") or "") if model else "",
        "verified": verified,
        "proof_state": state,
        "age_s": age,
        "rc": rc if has_proof else rec.get("rc"),
        "body_bytes": body_bytes if has_proof else rec.get("body_bytes"),
        "independence": dict(INDEPENDENCE),
    }


def row_from_registry(registry) -> dict:
    """Bind COW from the authority registry. Missing = UNMEASURED, not 0."""
    if registry is None:
        return bind_row(None)
    try:
        live = registry.live_nodes()
    except Exception:  # noqa: BLE001
        live = {}
    if LINK_ID in live:
        return bind_row(live[LINK_ID])
    try:
        stale = registry.stale_nodes()
    except Exception:  # noqa: BLE001
        stale = {}
    if LINK_ID in stale:
        return bind_row(stale[LINK_ID])
    try:
        st = registry.state()
    except Exception:  # noqa: BLE001
        st = {}
    raw = st.get(LINK_ID)
    if isinstance(raw, dict):
        claim = raw.get("claim") or {}
        return bind_row({
            "link_id": LINK_ID,
            "ok": raw.get("ok"),
            "verified": raw.get("ok"),
            "model": raw.get("model"),
            "rc": raw.get("rc"),
            "body_bytes": raw.get("body_bytes"),
            "age_s": None,
            "rail_type": claim.get("rail_type") or RAIL_TYPE,
        })
    return bind_row(None)


def _topology_nodes(body: dict) -> list:
    topo = body.get("topology")
    if not isinstance(topo, dict):
        topo = {}
        body["topology"] = topo
    nodes = topo.get("nodes")
    if not isinstance(nodes, list):
        nodes = []
        topo["nodes"] = nodes
    return nodes


def attach_to_nodemap(body: dict, registry=None) -> dict:
    """Put the COW node on the nodemap payload. Additive; does not invent rails."""
    if not isinstance(body, dict) or body.get("ok") is False:
        return body
    out = dict(body)
    row = row_from_registry(registry)
    nodes = _topology_nodes(out)
    replaced = False
    for i, n in enumerate(nodes):
        if isinstance(n, dict) and n.get("id") in (NODE_ID, LINK_ID):
            merged = dict(n)
            merged.update(row)
            nodes[i] = merged
            replaced = True
            break
    if not replaced:
        nodes.append(row)
    roster = out.get("nodes")
    if not isinstance(roster, list):
        roster = []
    roster = [n for n in roster if not (
        isinstance(n, dict) and n.get("id") in (NODE_ID, LINK_ID))]
    roster.append(row)
    out["nodes"] = roster
    out["cow"] = row
    return out
