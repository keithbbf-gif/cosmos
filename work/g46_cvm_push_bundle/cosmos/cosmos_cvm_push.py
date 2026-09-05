#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Core POST /api/v1/cvm/push — phone turn landing surface (P10 propose-only).

The thin phone clock POSTs the SS8.3 snapshot_delta envelope at this path
(docs/CVM_ARCH.md §8.3). Core already stores that body via
cosmos_service._cvm_store_snapshot (state/cvm/phone.json). This module
COMPOSES that helper and cosmos_service._cvm_pull_response — it does not
copy kinds-filter, idempotency, cursor hash, or pull assembly.

Contract:
  * Body is the §8.3 snapshot_delta envelope. No second schema.
  * Auth is the existing /api/v1 bearer (wired in cosmos_service.do_POST).
  * A phone push NEVER claims audio ownership: any body audio_owner is
    stripped, pull.json is stamped audio_owner=desktop, and the composed
    GET /cvm/pull view is refused if it is not desktop.
  * GET /cvm/pull then overlays cursor from phone.json (existing P3
    behaviour), so the pull ticket reflects the pushed turn.

Resolver paths only (kernel.paths.state). No drive literals. No bts_ imports.
Does not write audio.json or handoff.json. Does not append the ledger.

    py -3.14 tests\\test_cvm_push.py
"""
from __future__ import annotations

import time

PUSH_PATH = "/api/v1/cvm/push"
SNAP_PATH = "/api/v1/cvm/snapshot"
WRITER = "cosmos-service-cvm-push"


def _stamp_desktop_owner(kernel, rec: dict) -> None:
    """Persist audio_owner=desktop on pull.json so GET /cvm/pull quotes it.

    Seeds a ticket when the clock has not written pull.json yet (otherwise
    GET returns pull=false / UNREACHABLE and the phone has no owner to
    quote). Never writes audio.json. Never stores body's audio_owner.
    """
    from cosmos_clock import atomic_json
    from cosmos_service import CvmError, _cvm_read_json

    tree_id = kernel.paths.sentinel.tree_id
    pull_path = kernel.paths.state("cvm", "pull.json")
    try:
        ticket = _cvm_read_json(pull_path)
    except CvmError:
        ticket = None
    if ticket is None:
        try:
            from cosmos_brain import voice_client_timeout_s
            vto = float(voice_client_timeout_s())
        except Exception:                                             # noqa: BLE001
            vto = 70.0
        ticket = {
            "cvm": 1,
            "tree_id": tree_id,
            "pull": True,
            "kinds": list(rec.get("stored") or []),
            "issued_epoch": time.time(),
            "voice_client_timeout_s": vto,
            "writer": WRITER,
        }
    else:
        ticket = dict(ticket)
        if str(ticket.get("tree_id") or "") != tree_id:
            raise CvmError(
                "IDENTITY_MISMATCH",
                "pull.json tree_id does not match the sentinel")
    ticket["cvm"] = 1
    ticket["tree_id"] = tree_id
    ticket["pull"] = True
    ticket["audio_owner"] = "desktop"
    ticket["claimed"] = False
    cursor = rec.get("cursor_out") or rec.get("cursor") or ticket.get("cursor") or ""
    if cursor:
        ticket["cursor"] = cursor
    if not ticket.get("kinds"):
        ticket["kinds"] = list(rec.get("stored") or [])
    ticket["pushed_via"] = PUSH_PATH
    try:
        atomic_json(pull_path, ticket)
    except OSError as e:
        raise CvmError("UNREADABLE", str(e)[:300]) from e


def cvm_store_push(kernel, d: dict) -> dict:
    """Land a phone turn. Compose snapshot store + pull publish.

    `_cvm_store_snapshot` validates the §8.3 envelope, is idempotent on
    request_id, and replaces state/cvm/phone.json. This function then
    stamps audio_owner=desktop and quotes `_cvm_pull_response` so the
    subsequent GET /api/v1/cvm/pull is the same view.
    """
    from cosmos_service import (
        CvmError, _cvm_pull_response, _cvm_store_snapshot,
    )

    if not isinstance(d, dict):
        raise CvmError("BAD_SNAPSHOT", "body must be a JSON object")
    body = dict(d)
    body.pop("audio_owner", None)

    rec = _cvm_store_snapshot(kernel, body)
    _stamp_desktop_owner(kernel, rec)

    client_id = str(body.get("client_id") or "").strip()
    pulled = _cvm_pull_response(kernel, client_id)
    owner = str(pulled.get("audio_owner") or "none") or "none"
    if owner != "desktop":
        raise CvmError(
            "OWNER_CONTESTED",
            "phone push must not become audio owner (got %r)" % owner)
    if pulled.get("pull") is False:
        raise CvmError(
            "UNREACHABLE",
            "GET /cvm/pull published no ticket after POST /cvm/push")

    out = dict(rec)
    out["audio_owner"] = "desktop"
    out["claimed"] = False
    if "idempotent" not in out:
        out["idempotent"] = False
    out["cursor"] = pulled.get("cursor") or rec.get("cursor_out")
    return out


def cvm_post(kernel, path: str, d: dict) -> dict:
    """One POST dispatcher: snapshot stays the P3 helper; push composes it."""
    from cosmos_service import _cvm_store_snapshot

    if path == PUSH_PATH:
        return cvm_store_push(kernel, d)
    if path == SNAP_PATH:
        return _cvm_store_snapshot(kernel, d)
    from cosmos_service import CvmError
    raise CvmError("NOT_FOUND", path)
