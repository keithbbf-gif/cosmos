#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_cvm_projection - CVM P3 projection helpers (not the ledger).

PHASE 4, docs/CORE_RESTRUCTURE.md. `cosmos_service.py` was 1,732 lines. This
module is ONE cut along a seam the file already named for itself:

    # ---------------- CVM projection (P3 additive; not the ledger) ----------------

Everything between that banner and `_frontend_file` (the static shell) is
here, byte-for-byte in behaviour. Clock writes state/cvm/pull.json; Core
publishes it. Snapshot lands as state/cvm/phone.json (replace). POST
/cvm/push reuses `_cvm_store_snapshot` then stamps audio_owner=desktop on
pull.json so GET /cvm/pull (unchanged) returns the desktop-owned turn.

Why this seam and not another. The block has inbound coupling only to
`Kernel` (identity + paths + ledger.last for the status prewarm) and
`cosmos_clock.atomic_json`. It does not touch the HTTP handler, bearer
auth, the static/cDeck shell, or voice. The handlers in `make_handler`
only *call* these helpers. The other named leftover (`cosmos_codex_rail.py`)
has no existing `# seam` banner, so it is not this cut.

The move is ADDITIVE. `cosmos_service` re-exports every name below, so
`cosmos_cvm_push.py` and `tests/test_cvm_push.py` keep:

    from cosmos_service import (
        CvmError, _cvm_pull_response, _cvm_store_snapshot,
    )

Does not modify kernel / ledger / sched. No hard-coded paths: projection
files resolve through `kernel.paths.state("cvm", ...)`.
"""
from __future__ import annotations

import json
import time

from cosmos_kernel import Kernel

# ---------------- CVM projection (P3 additive; not the ledger) ----------------
# Clock writes state/cvm/pull.json; Core publishes it. Snapshot lands as
# state/cvm/phone.json (replace). POST /cvm/push reuses _cvm_store_snapshot
# then stamps audio_owner=desktop on pull.json so GET /cvm/pull (unchanged)
# returns the desktop-owned turn. Handlers below only call these helpers.
_CVM_KNOWN_KINDS = frozenset({
    "voice_session", "device", "notifications",
    "sms", "calls", "contacts", "calendar", "pcm",
})
_CVM_PCM_INLINE = frozenset({"bytes", "pcm", "data", "b64"})


class CvmError(Exception):
    """Typed CVM refusal. `kind` is the JSON error token."""

    def __init__(self, kind: str, detail: str = ""):
        self.kind = kind
        super().__init__(detail or kind)


def _cvm_read_json(path):
    if not path.is_file():
        return None
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise CvmError("UNPARSEABLE", f"{path.name}: {e}"[:300]) from e
    if not isinstance(obj, dict):
        raise CvmError("UNPARSEABLE", f"{path.name} is not an object")
    return obj


def _cvm_stat(path):
    """mtime / owner / size of a projection file (P3 live-tree quote)."""
    st = path.stat()
    try:
        owner = path.owner()
    except Exception:                                                 # noqa: BLE001
        owner = str(int(getattr(st, "st_uid", 0) or 0))
    return float(st.st_mtime), str(owner or ""), int(st.st_size)


def _cvm_status_prewarm(kernel: Kernel) -> dict:
    """Identity the phone needs without teaching a drive letter.
    Not a refactor of GET /status - that handler stays byte-identical."""
    last = kernel.ledger.last()
    return {"ready": kernel.ready,
            "tree_id": kernel.paths.sentinel.tree_id,
            "ledger_head": {"seq": last["seq"], "event": last["event"]}}


def _cvm_filter_kinds(kinds) -> dict:
    """Keep known kinds; ignore unknown (forward compatible). A declared
    kind that is not an object, or is {}, is BAD_SNAPSHOT. Device blobs
    with fields and no `status` are accepted (CVM_ARCH §8.3 example)."""
    if not isinstance(kinds, dict):
        raise CvmError("BAD_SNAPSHOT", "kinds must be an object")
    stored = {}
    for name, blob in kinds.items():
        key = str(name)
        if key not in _CVM_KNOWN_KINDS:
            continue
        if not isinstance(blob, dict) or not blob:
            raise CvmError("BAD_SNAPSHOT",
                           f"kind {key!r} has neither status nor items")
        if key == "pcm" and _CVM_PCM_INLINE.intersection(blob):
            raise CvmError("BAD_SNAPSHOT",
                           "pcm must be a pointer (sha256), not inline bytes")
        stored[key] = blob
    return stored


def _cvm_blob_ptrs(kinds) -> list:
    pcm = kinds.get("pcm") if isinstance(kinds, dict) else None
    if isinstance(pcm, dict) and pcm.get("sha256"):
        return [str(pcm["sha256"])]
    return []


def _cvm_pull_response(kernel: Kernel, client_id: str) -> dict:
    """Publish pull.json (source of truth) + status prewarm. Overlay cursor
    from phone.json in the RESPONSE only - never rewrite the clock's file."""
    tree_id = kernel.paths.sentinel.tree_id
    status = _cvm_status_prewarm(kernel)
    pull_path = kernel.paths.state("cvm", "pull.json")
    ticket = _cvm_read_json(pull_path)
    if ticket is None:
        return {"cvm": 1, "tree_id": tree_id, "pull": False,
                "core_kind": "UNREACHABLE", "client_id": client_id,
                "status": status}
    if str(ticket.get("tree_id") or "") != tree_id:
        raise CvmError("IDENTITY_MISMATCH",
                       "pull.json tree_id does not match the sentinel")
    try:
        phone = _cvm_read_json(kernel.paths.state("cvm", "phone.json"))
    except CvmError:
        phone = None
    if isinstance(phone, dict) and str(phone.get("tree_id") or "") == tree_id:
        cur = phone.get("cursor_out") or phone.get("cursor")
        if cur:
            ticket = dict(ticket)
            ticket["cursor"] = cur
    mtime, owner, size = _cvm_stat(pull_path)
    out = dict(ticket)
    out.update(client_id=client_id, status=status,
               projection_mtime=mtime, projection_owner=owner,
               projection_size=size)
    return out


def _cvm_store_snapshot(kernel: Kernel, d: dict) -> dict:
    """Replace state/cvm/phone.json. Idempotent on request_id. No ledger."""
    if d.get("cvm") != 1:
        raise CvmError("BAD_SNAPSHOT", "cvm must be 1")
    request_id = str(d.get("request_id") or "").strip()
    if not request_id:
        raise CvmError("BAD_SNAPSHOT", "request_id is required")
    client_id = str(d.get("client_id") or "").strip()
    if not client_id:
        raise CvmError("CLIENT_ID_REQUIRED", "client_id is required")
    stored_kinds = _cvm_filter_kinds(d.get("kinds"))
    tree_id = kernel.paths.sentinel.tree_id
    phone_path = kernel.paths.state("cvm", "phone.json")
    try:
        existing = _cvm_read_json(phone_path)
    except CvmError:
        existing = None
    if (isinstance(existing, dict)
            and str(existing.get("request_id") or "") == request_id
            and str(existing.get("tree_id") or "") == tree_id):
        stored = list(existing.get("stored")
                      or (existing.get("kinds") or {}).keys())
        return {"cursor_out": existing.get("cursor_out") or existing.get("cursor"),
                "stored": stored,
                "blob_sha256s": _cvm_blob_ptrs(existing.get("kinds") or {}),
                "cvm_ear_ms": None, "idempotent": True}
    import hashlib as _hashlib
    from cosmos_clock import atomic_json
    cursor_out = _hashlib.sha256(json.dumps(
        {"tree_id": tree_id, "request_id": request_id, "kinds": stored_kinds},
        sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    blobs = _cvm_blob_ptrs(stored_kinds)
    rec = {
        "cvm": 1,
        "tree_id": tree_id,
        "client_id": client_id,
        "request_id": request_id,
        "cursor_in": str(d.get("cursor_in") or ""),
        "cursor_out": cursor_out,
        "cursor": cursor_out,
        "kinds": stored_kinds,
        "stored": list(stored_kinds.keys()),
        "blob_sha256s": blobs,
        "received_epoch": time.time(),
        "writer": "cosmos-service",
    }
    try:
        atomic_json(phone_path, rec)
    except OSError as e:
        raise CvmError("UNREADABLE", str(e)[:300]) from e
    return {"cursor_out": cursor_out, "stored": rec["stored"],
            "blob_sha256s": blobs, "cvm_ear_ms": None}
