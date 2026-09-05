#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cvm-dt snapshot-consume — slice-3 DESKTOP (POST /cvm/snapshot fold).

Desktop half of the CVM snapshot path (docs/CVM_ARCH.md §§4–6, 8.3). The
phone POSTs deltas at Core; this consumer reads those envelopes (the same
§8.3 body Core already stores as state/cvm/phone.json) and FOLDS them
into the local desktop turn, ordered by cursor.

  * HTTP: reuse `cvm_dt.CoreClient` (FAST 8 s, same budget as GET /cvm/pull).
    No second stack (H9). Ticket fields reuse `cvm_pull.CONTRACT` exactly:
    tree_id, issued_epoch, kinds[], cursor, audio_owner, voice_client_timeout_s.
  * Idempotent on request_id: a replayed delta is a no-op, never double-folded.
    (Core P3 only remembers the LAST request_id on phone.json; this seen-set
    covers historical replay too.)
  * Typed refusal (never silent): BAD_SNAPSHOT on a malformed delta,
    CURSOR_GAP when cursor_in does not chain. Unknown kinds are ignored
    (forward compatible), matching Core `_cvm_filter_kinds`.
  * Does NOT write pull.json / audio.json / phone.json. Does NOT append the
    ledger. Does NOT implement audio HANDOFF (deferred). Core :8770 stays up.

    py -3.14 builds\\cvm-dt\\test_cvm_snap.py
    py -3.14 builds\\cvm-dt\\cvm_snap.py --root <RUNTIME> --once
    py -3.14 builds\\cvm-dt\\cvm_snap.py --root <RUNTIME> --gate

rc=0 is not the gate. Quote live_value.replay_folded == false from a real
POST /api/v1/cvm/snapshot replay against restarted :8770.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
import uuid
from pathlib import Path
from typing import Any, Optional

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
_COSMOS_LIB = Path(__file__).resolve().parents[2] / "cosmos"
if _COSMOS_LIB.is_dir() and str(_COSMOS_LIB) not in sys.path:
    sys.path.insert(0, str(_COSMOS_LIB))

from cosmos_clock import atomic_json  # noqa: E402
from cosmos_paths import CosmosPaths  # noqa: E402

from cvm_dt import (  # noqa: E402
    CLIENT_ID, FAST_READ_S, SNAP_PATH, VOICE_READ_S,
    CoreClient, CvmDtError, RefusalKind, _sha256_file, core_get, core_post,
    load_paths, load_token, pull_url, refuse_http,
)
from cvm_pull import CONTRACT, parse_ticket  # noqa: E402

# Must match cosmos_service._CVM_KNOWN_KINDS / _CVM_PCM_INLINE (do not import
# the service module — that would pull Kernel into a satellite).
KNOWN_KINDS = frozenset({
    "voice_session", "device", "notifications",
    "sms", "calls", "contacts", "calendar", "pcm",
})
PCM_INLINE = frozenset({"bytes", "pcm", "data", "b64"})
SNAP_READ_S = FAST_READ_S          # do not invent a third budget (H9)
TURN_REL = ("cvm", "dt_turn.json")
PROOF_NAME = "STAGE6_SNAP.json"
WRITER = "cvm-dt-snap"
GATE_CLIENT = "cvm-dt-snap-gate"


def _cursor_out(tree_id: str, request_id: str, kinds: dict) -> str:
    """Same hash Core `_cvm_store_snapshot` writes as cursor_out."""
    payload = {"tree_id": tree_id, "request_id": request_id, "kinds": kinds}
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def snapshot_delta(request_id: str, cursor_in: str, kinds: dict,
                   client_id: str = CLIENT_ID) -> dict:
    """§8.3 POST /cvm/snapshot body. Do not add a second envelope."""
    return {
        "cvm": 1,
        "client_id": str(client_id),
        "request_id": str(request_id),
        "cursor_in": str(cursor_in or ""),
        "kinds": kinds,
    }


def filter_kinds(kinds) -> dict:
    """Keep known kinds; ignore unknown. Empty/non-object kind → BAD_SNAPSHOT."""
    if not isinstance(kinds, dict):
        raise CvmDtError(RefusalKind.BAD_SNAPSHOT, "kinds must be an object")
    stored: dict[str, Any] = {}
    for name, blob in kinds.items():
        key = str(name)
        if key not in KNOWN_KINDS:
            continue
        if not isinstance(blob, dict) or not blob:
            raise CvmDtError(
                RefusalKind.BAD_SNAPSHOT,
                "kind %r has neither status nor items" % key)
        if key == "pcm" and PCM_INLINE.intersection(blob):
            raise CvmDtError(
                RefusalKind.BAD_SNAPSHOT,
                "pcm must be a pointer (sha256), not inline bytes")
        stored[key] = blob
    return stored


def parse_delta(data: Any, tree_id: str) -> dict:
    """Fail-closed parse of a phone POST /cvm/snapshot body."""
    if not isinstance(data, dict):
        raise CvmDtError(RefusalKind.BAD_SNAPSHOT, "delta must be a JSON object")
    if data.get("cvm") != 1:
        raise CvmDtError(RefusalKind.BAD_SNAPSHOT, "cvm must be 1")
    request_id = str(data.get("request_id") or "").strip()
    if not request_id:
        raise CvmDtError(RefusalKind.BAD_SNAPSHOT, "request_id is required")
    client_id = str(data.get("client_id") or "").strip()
    if not client_id:
        raise CvmDtError(RefusalKind.BAD_REQUEST, "client_id is required")
    got_tid = str(data.get("tree_id") or "")
    if got_tid and got_tid != tree_id:
        raise CvmDtError(
            RefusalKind.IDENTITY_MISMATCH,
            "snapshot tree_id=%r != sentinel %r" % (got_tid, tree_id))
    stored = filter_kinds(data.get("kinds"))
    return {
        "cvm": 1,
        "tree_id": tree_id,
        "client_id": client_id,
        "request_id": request_id,
        "cursor_in": str(data.get("cursor_in") or ""),
        "cursor_out": str(data.get("cursor_out") or ""),
        "kinds": stored,
    }


def refuse_snap_http(data: dict) -> None:
    """Typed refusal on non-200 POST /cvm/snapshot. Delegates to one mapping."""
    refuse_http(data, default_400=RefusalKind.BAD_SNAPSHOT)


class SnapshotConsumer:
    """Fold phone snapshot deltas into the local desktop turn.

    Cursor starts at "". Each first-seen request_id whose cursor_in equals
    the current cursor is applied (kinds merged, cursor becomes cursor_out).
    A seen request_id is a no-op — cursor does not move, kinds are not
    re-merged. A new request_id with a cursor_in gap raises CURSOR_GAP.
    """

    def __init__(self, core: CoreClient, paths: CosmosPaths,
                 client_id: str = CLIENT_ID, *,
                 load: bool = True, persist: bool = True):
        self.core = core
        self.paths = paths
        self.client_id = client_id
        self.persist = bool(persist)
        self.tree_id = paths.sentinel.tree_id
        self.cursor = ""
        self.kinds: dict[str, Any] = {}
        self.seen: list[str] = []
        self.applied: list[str] = []
        self.fold_count = 0
        self.ticket: dict[str, Any] = {}
        if load:
            self._load()

    def _load(self) -> None:
        path = self.paths.state(*TURN_REL)
        if not path.is_file():
            return
        try:
            obj = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as e:
            raise CvmDtError(RefusalKind.BAD_SNAPSHOT,
                             "dt_turn.json: %s" % e) from e
        if not isinstance(obj, dict):
            raise CvmDtError(RefusalKind.BAD_SNAPSHOT,
                             "dt_turn.json is not an object")
        tid = str(obj.get("tree_id") or "")
        if tid and tid != self.tree_id:
            raise CvmDtError(
                RefusalKind.IDENTITY_MISMATCH,
                "dt_turn.json tree_id=%r != sentinel %r" % (tid, self.tree_id))
        self.cursor = str(obj.get("cursor") or "")
        kinds = obj.get("kinds")
        self.kinds = dict(kinds) if isinstance(kinds, dict) else {}
        seen = obj.get("seen_request_ids")
        if isinstance(seen, list):
            self.seen = [str(x) for x in seen if str(x)]
        applied = obj.get("applied_request_ids")
        if isinstance(applied, list):
            self.applied = [str(x) for x in applied if str(x)]
        try:
            self.fold_count = int(obj.get("fold_count") or len(self.applied))
        except (TypeError, ValueError):
            self.fold_count = len(self.applied)

    def _publish(self) -> Path:
        path = self.paths.state(*TURN_REL)
        out: dict[str, Any] = {
            "cvm": 1,
            "tree_id": self.tree_id,
            "cursor": self.cursor,
            "kinds": self.kinds,
            "seen_request_ids": list(self.seen),
            "applied_request_ids": list(self.applied),
            "fold_count": self.fold_count,
            "writer": WRITER,
            "client_id": self.client_id,
        }
        for k in CONTRACT:
            if k == "kinds":
                out["ticket_kinds"] = list(self.ticket.get("kinds") or [])
                continue
            if k == "cursor":
                continue
            if k in self.ticket:
                out[k] = self.ticket[k]
        if "voice_client_timeout_s" not in out:
            out["voice_client_timeout_s"] = VOICE_READ_S
        if "audio_owner" not in out:
            out["audio_owner"] = str(self.ticket.get("audio_owner") or "none")
        atomic_json(path, out)
        return path

    def seed_ticket(self, ticket: dict) -> None:
        """Adopt pull-ticket CONTRACT fields. Does not move cursor.

        Ticket.cursor is the last snapshot's cursor_out (Core overlay). The
        next delta's cursor_in must equal *this consumer's* cursor, not
        necessarily the ticket's.
        """
        self.ticket = dict(ticket)

    def pull_ticket(self) -> dict:
        data = core_get(self.core, pull_url(self.client_id), SNAP_READ_S)
        ticket = parse_ticket(data, self.tree_id)
        self.seed_ticket(ticket)
        return ticket

    def fold(self, raw: Any) -> dict:
        """Apply one §8.3 delta. Replay of request_id is a no-op."""
        parsed = parse_delta(raw, self.tree_id)
        rid = parsed["request_id"]
        prev = self.cursor
        if rid in self.seen:
            return {
                "ok": True,
                "folded": False,
                "replayed": True,
                "request_id": rid,
                "cursor": self.cursor,
                "cursor_prev": prev,
                "cursor_advanced": False,
                "fold_count": self.fold_count,
                "seen": len(self.seen),
                "kinds": dict(self.kinds),
                "tree_id": self.tree_id,
            }
        if parsed["cursor_in"] != self.cursor:
            raise CvmDtError(
                RefusalKind.CURSOR_GAP,
                "cursor_in=%r does not chain from %r (request_id=%s)"
                % (parsed["cursor_in"], self.cursor, rid))
        stored = parsed["kinds"]
        cursor_out = parsed["cursor_out"] or _cursor_out(
            self.tree_id, rid, stored)
        self.kinds.update(stored)
        self.seen.append(rid)
        self.applied.append(rid)
        self.fold_count += 1
        self.cursor = cursor_out
        rec = {
            "ok": True,
            "folded": True,
            "replayed": False,
            "request_id": rid,
            "cursor": self.cursor,
            "cursor_prev": prev,
            "cursor_advanced": self.cursor != prev,
            "fold_count": self.fold_count,
            "seen": len(self.seen),
            "stored": list(stored.keys()),
            "kinds": dict(self.kinds),
            "tree_id": self.tree_id,
        }
        if self.persist:
            rec["published"] = str(self._publish())
        return rec

    def ingest_phone(self) -> dict:
        """Consume Core's last POST /cvm/snapshot (state/cvm/phone.json).

        Core replaces phone.json each POST, so the first ingest of a
        never-seen consumer adopts that projection's cursor_in as the
        chain start (there is no delta log to replay). After that, a new
        request_id must chain or CURSOR_GAP fires.
        """
        path = self.paths.state("cvm", "phone.json")
        if not path.is_file():
            raise CvmDtError(
                RefusalKind.UNREACHABLE,
                "state/cvm/phone.json missing — no POST /cvm/snapshot yet")
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as e:
            raise CvmDtError(RefusalKind.BAD_SNAPSHOT,
                             "phone.json: %s" % e) from e
        if not isinstance(data, dict):
            raise CvmDtError(RefusalKind.BAD_SNAPSHOT,
                             "phone.json is not an object")
        if not self.seen:
            self.cursor = str(data.get("cursor_in") or "")
        return self.fold(data)

    def post_and_fold(self, delta: dict) -> dict:
        """POST the phone envelope at Core, then fold it locally.

        Core is the store; the fold is the desktop turn. A Core-side
        `idempotent: true` is quoted, not trusted as the desktop seen-set.
        """
        data = core_post(self.core, SNAP_PATH, delta, SNAP_READ_S,
                         default_400=RefusalKind.BAD_SNAPSHOT)
        body = dict(delta)
        if data.get("cursor_out"):
            body["cursor_out"] = data.get("cursor_out")
        rec = self.fold(body)
        rec["core_cursor_out"] = data.get("cursor_out")
        rec["core_idempotent"] = bool(data.get("idempotent"))
        rec["core_stored"] = data.get("stored")
        rec["quoted_from"] = "POST /api/v1/cvm/snapshot"
        rec["_http"] = data.get("_http")
        return rec

    def consume_once(self) -> dict:
        """GET /cvm/pull (ticket, never invented) then fold phone.json."""
        try:
            ticket = self.pull_ticket()
            pull_kind = "ok"
        except CvmDtError as e:
            if e.kind != RefusalKind.UNREACHABLE:
                raise
            ticket = {}
            pull_kind = str(e.kind)
        rec = self.ingest_phone()
        rec["ticket"] = {
            k: ticket.get(k) for k in CONTRACT if k in ticket
        } if ticket else {}
        rec["pull_kind"] = pull_kind
        rec["quoted_from"] = "POST /cvm/snapshot via state/cvm/phone.json"
        return rec


def run_gate(root: str, base: str, proof_path: Optional[str] = None) -> dict:
    """Stage-6: two POSTs + one replay against live :8770. rc=0 is not the gate.

    The field that proves the fold is live_value.replay_folded (must be
    false) after a real POST /api/v1/cvm/snapshot of a previously-folded
    request_id. live_value.cursor must equal live_value.cursor_after_second
    (monotonic, no regression). An exit code is not evidence.

    Residual: Core P3 phone.json is last-write; a historical request_id
    replay may overwrite that projection. This gate's proof is the desktop
    seen-set, not Core's last-id. Audio HANDOFF is not in this slice.
    """
    src = Path(__file__).resolve()
    paths = load_paths(root)
    tree_id = paths.sentinel.tree_id
    token = load_token(paths)
    core = CoreClient(base, token)
    consumer = SnapshotConsumer(core, paths, client_id=GATE_CLIENT,
                                load=False, persist=False)
    t = time.time()

    status = None
    core_kind = None
    cursor_after_first = ""
    cursor_after_second = ""
    cursor_after_replay = ""
    replay_folded = None
    fold_count = None
    core_replay_idempotent = None
    first = second = replay = None
    try:
        status = core.get("/api/v1/status", SNAP_READ_S)
        if str(status.get("tree_id") or "") != tree_id:
            raise CvmDtError(
                RefusalKind.IDENTITY_MISMATCH,
                "GET /status tree_id=%r != sentinel %r"
                % (status.get("tree_id"), tree_id))
        cursor_in = ""
        try:
            ticket = consumer.pull_ticket()
            cursor_in = str(ticket.get("cursor") or "")
            consumer.cursor = cursor_in
        except CvmDtError as e:
            if e.kind != RefusalKind.UNREACHABLE:
                raise
        rid1 = "snap-gate-" + uuid.uuid4().hex
        rid2 = "snap-gate-" + uuid.uuid4().hex
        d1 = snapshot_delta(rid1, cursor_in, {
            "device": {"status": "ok", "battery_pct": 1,
                       "net": "gate", "audio_route": "none",
                       "gate": rid1},
        }, client_id=GATE_CLIENT)
        first = consumer.post_and_fold(d1)
        cursor_after_first = str(first.get("cursor") or "")
        d2 = snapshot_delta(rid2, cursor_after_first, {
            "notifications": {"status": "ok",
                              "items": [{"pkg": "cvm-dt-snap-gate",
                                         "title": rid2, "t": 0}]},
        }, client_id=GATE_CLIENT)
        second = consumer.post_and_fold(d2)
        cursor_after_second = str(second.get("cursor") or "")
        replay = consumer.post_and_fold(d1)
        cursor_after_replay = str(replay.get("cursor") or "")
        replay_folded = replay.get("folded")
        fold_count = int(replay.get("fold_count") or 0)
        core_replay_idempotent = replay.get("core_idempotent")
    except CvmDtError as e:
        core_kind = str(e.kind)

    cursor_unchanged = bool(
        cursor_after_second
        and cursor_after_replay == cursor_after_second
        and cursor_after_second != cursor_after_first)
    ok = bool(
        core_kind is None
        and replay_folded is False
        and cursor_unchanged
        and fold_count == 2
        and first and first.get("folded")
        and second and second.get("folded")
        and replay and replay.get("replayed"))
    live_value = {
        "live_tree_id": tree_id,
        "status_tree_id": (status or {}).get("tree_id"),
        "served_at": (status or {}).get("served_at"),
        "replay_folded": replay_folded,
        "cursor": cursor_after_replay,
        "cursor_after_first": cursor_after_first,
        "cursor_after_second": cursor_after_second,
        "cursor_after_replay": cursor_after_replay,
        "cursor_unchanged_on_replay": cursor_unchanged,
        "fold_count": fold_count,
        "core_replay_idempotent": core_replay_idempotent,
        "quoted_from": "POST /api/v1/cvm/snapshot",
        "core_kind": core_kind,
        "base": base,
        "timeout_s": SNAP_READ_S,
    }
    rec = {
        "ok": ok,
        "stage": 6,
        "deliverable": "cvm-dt-snap",
        "agent": "G46",
        "slice": "slice-3-snapshot-consume",
        "gated_at_epoch": t,
        "source_path": str(src),
        "source_sha256": _sha256_file(src),
        "live_root": str(Path(root).resolve()),
        "live_tree_id": tree_id,
        "live_value": live_value,
        "note": "rc=0 is not the gate. live_value.replay_folded is. "
                "It must be false after a real POST /cvm/snapshot replay "
                "on restarted :8770. An exit code is not evidence. "
                "AUDIO HANDOFF is deferred.",
    }
    rec["emitted"] = "cvm-dt-snap:%s:%s:%s:%s" % (
        tree_id,
        cursor_after_replay or (core_kind or "NO_CURSOR"),
        "replay_folded=" + str(replay_folded).lower(),
        rec["source_sha256"],
    )
    dest = Path(proof_path) if proof_path else (src.parent / PROOF_NAME)
    rec["proof_path"] = str(dest.resolve())
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_name(dest.name + ".part")
    tmp.write_text(json.dumps(rec, indent=1, default=str), encoding="utf-8")
    tmp.replace(dest)
    if core_kind == RefusalKind.UNREACHABLE:
        raise CvmDtError(
            RefusalKind.UNREACHABLE,
            "Core at %s is down — proof at %s" % (base, rec["proof_path"]))
    return rec


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(prog="cvm-dt-snap")
    ap.add_argument("--root", required=True)
    ap.add_argument("--base", default="http://127.0.0.1:8770")
    ap.add_argument("--client-id", default=CLIENT_ID)
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--gate", action="store_true")
    ap.add_argument("--proof", default="")
    ns = ap.parse_args(argv)
    if not ns.once and not ns.gate:
        ap.error("one of --once / --gate is required")
    if ns.gate:
        rec = run_gate(ns.root, ns.base, proof_path=ns.proof or None)
        print(json.dumps({
            "ok": rec["ok"],
            "stage": 6,
            "proof_path": rec["proof_path"],
            "emitted": rec["emitted"],
            "live_value": rec["live_value"],
        }, indent=1, default=str))
        return 0 if rec["ok"] else 1
    paths = load_paths(ns.root)
    token = load_token(paths)
    consumer = SnapshotConsumer(CoreClient(ns.base, token), paths, ns.client_id)
    rec = consumer.consume_once()
    print(json.dumps(rec, indent=1, default=str))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except CvmDtError as e:
        print(json.dumps({"ok": False, "kind": str(e.kind), "detail": str(e)},
                         indent=1), file=sys.stderr)
        raise SystemExit(2)
