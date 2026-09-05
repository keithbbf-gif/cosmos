#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cvm-dt audio HANDOFF — slice-3 deferred half (phone HOME ↔ desktop).

Transfers `audio_owner` between the thin phone and the heavy-local desktop
(docs/CVM_ARCH.md §§4–6, H6 exclusive owner). Snapshot-consume is
cvm_snap.py; this module is the requester/acceptor.

  * HTTP: reuse `cvm_dt.CoreClient` + `core_get`/`refuse_http` (FAST 8 s)
    and `cvm_pull.parse_ticket`. GET /api/v1/cvm/pull is the EXISTING Core
    route that quotes `audio_owner`. No second stack, no new Core path (H5,
    H9). Does NOT edit kernel/ledger/one-writer.
  * Contract (do not invent a second): tree_id, issued_epoch, kinds[],
    cursor, audio_owner, voice_client_timeout_s.
  * Claim is IDEMPOTENT on request_id: a replay is a no-op (owner does not
    move). A contested double-claim is OWNER_CONTESTED — never silent,
    never two owners. Cooperative transfer uses from_owner=current.
  * Owner-check is `cvm_dt.audio_owner_of` / `require_single_owner` (ONE
    helper). Does NOT write audio.json (H13: clock remains that file's
    sole writer). Publishes audio_owner onto state/cvm/pull.json so the
    phone GET /cvm/pull sees HOME.

    py -3.14 builds\\cvm-dt\\test_cvm_handoff.py
    py -3.14 builds\\cvm-dt\\cvm_handoff.py --root <RUNTIME> --claim desktop --request-id <id> --once
    py -3.14 builds\\cvm-dt\\cvm_handoff.py --root <RUNTIME> --gate

rc=0 is not the gate. Quote live_value.audio_owner from a real
GET /api/v1/cvm/pull after a contested claim against restarted :8770.
"""
from __future__ import annotations

import argparse
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
from cosmos_cvm_push import stamp_desktop_pull  # noqa: E402

from cvm_dt import (  # noqa: E402
    CLIENT_ID, FAST_READ_S, OWNERS, PULL_PATH, VOICE_READ_S,
    CoreClient, CvmDtError, RefusalKind, _sha256_file,
    audio_owner_of, core_get, load_paths, load_token, pull_url,
    require_single_owner,
)
from cvm_pull import CONTRACT, parse_ticket  # noqa: E402

HANDOFF_READ_S = FAST_READ_S          # do not invent a third budget (H9)
PROOF_NAME = "STAGE6_HANDOFF.json"
WRITER = "cvm-dt-handoff"
GATE_CLIENT = "cvm-dt-handoff-gate"
STATE_REL = ("cvm", "handoff.json")
PULL_REL = ("cvm", "pull.json")


class AudioHandoff:
    """Requester/acceptor for a single audio_owner (phone|desktop|none).

    GET /api/v1/cvm/pull seeds the current owner. claim() is the grant:
    replay of request_id is a no-op; a second claimant is OWNER_CONTESTED.
    """

    def __init__(self, core: CoreClient, paths: CosmosPaths,
                 client_id: str = CLIENT_ID, *,
                 load: bool = True, persist: bool = True):
        self.core = core
        self.paths = paths
        self.client_id = client_id
        self.persist = bool(persist)
        self.tree_id = paths.sentinel.tree_id
        self.owner = "none"
        self.seen: list[str] = []
        self.granted: list[str] = []
        self.grant_count = 0
        self.ticket: dict[str, Any] = {}
        if load:
            self._load()

    def _load(self) -> None:
        path = self.paths.state(*STATE_REL)
        if not path.is_file():
            return
        try:
            obj = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as e:
            raise CvmDtError(RefusalKind.BAD_REQUEST,
                             "handoff.json: %s" % e) from e
        if not isinstance(obj, dict):
            raise CvmDtError(RefusalKind.BAD_REQUEST,
                             "handoff.json is not an object")
        tid = str(obj.get("tree_id") or "")
        if tid and tid != self.tree_id:
            raise CvmDtError(
                RefusalKind.IDENTITY_MISMATCH,
                "handoff.json tree_id=%r != sentinel %r" % (tid, self.tree_id))
        self.owner = audio_owner_of(obj)
        seen = obj.get("seen_request_ids")
        if isinstance(seen, list):
            self.seen = [str(x) for x in seen if str(x)]
        granted = obj.get("granted_request_ids")
        if isinstance(granted, list):
            self.granted = [str(x) for x in granted if str(x)]
        try:
            self.grant_count = int(obj.get("grant_count") or len(self.granted))
        except (TypeError, ValueError):
            self.grant_count = len(self.granted)

    def _publish(self) -> dict[str, str]:
        """Write handoff.json + audio_owner onto pull.json. Never audio.json."""
        rec: dict[str, Any] = {
            "cvm": 1,
            "tree_id": self.tree_id,
            "audio_owner": self.owner,
            "seen_request_ids": list(self.seen),
            "granted_request_ids": list(self.granted),
            "grant_count": self.grant_count,
            "writer": WRITER,
            "client_id": self.client_id,
        }
        for k in CONTRACT:
            if k == "audio_owner":
                continue
            if k in self.ticket:
                rec[k] = self.ticket[k]
        if "voice_client_timeout_s" not in rec:
            rec["voice_client_timeout_s"] = VOICE_READ_S
        handoff_path = self.paths.state(*STATE_REL)
        atomic_json(handoff_path, rec)
        if self.owner == "desktop":
            stamp_desktop_pull(self.paths, dict(self.ticket), writer=WRITER)
        return {"handoff": str(handoff_path),
                "pull": str(self.paths.state(*PULL_REL))}

    def pull_ticket(self) -> dict:
        """GET /api/v1/cvm/pull. Never invent a ticket."""
        data = core_get(self.core, pull_url(self.client_id), HANDOFF_READ_S)
        ticket = parse_ticket(data, self.tree_id)
        self.ticket = ticket
        if not self.seen:
            self.owner = audio_owner_of(ticket)
        return ticket

    def claim(self, want: str, request_id: str, *,
              from_owner: Optional[str] = None) -> dict:
        """Claim exclusive audio_owner. Replay of request_id is a no-op.

        Steal-resistant: another holder → OWNER_CONTESTED. Cooperative
        phone↔desktop transfer passes from_owner=<current holder>.
        """
        rid = str(request_id or "").strip()
        if not rid:
            raise CvmDtError(RefusalKind.BAD_REQUEST, "request_id is required")
        w = str(want or "").strip()
        if w not in OWNERS:
            raise CvmDtError(
                RefusalKind.BAD_REQUEST,
                "want must be phone|desktop|none, not %r" % (want,))
        if not self.ticket:
            self.pull_ticket()
        prev = self.owner
        if rid in self.seen:
            return {
                "ok": True,
                "granted": False,
                "replayed": True,
                "request_id": rid,
                "audio_owner": self.owner,
                "audio_owner_prev": prev,
                "want": w,
                "grant_count": self.grant_count,
                "seen": len(self.seen),
                "tree_id": self.tree_id,
                "quoted_from": "GET /api/v1/cvm/pull",
            }
        cur = self.owner if self.owner else audio_owner_of(self.ticket)
        if from_owner is not None:
            exp = str(from_owner).strip() or "none"
            if cur != exp:
                raise CvmDtError(
                    RefusalKind.OWNER_CONTESTED,
                    "audio_owner=%s, expected from_owner=%s (H6 single owner)"
                    % (cur, exp))
            granted = w
        else:
            granted = require_single_owner(cur, w)
        self.owner = granted
        self.seen.append(rid)
        self.granted.append(rid)
        self.grant_count += 1
        rec = {
            "ok": True,
            "granted": True,
            "replayed": False,
            "request_id": rid,
            "audio_owner": self.owner,
            "audio_owner_prev": prev,
            "want": w,
            "grant_count": self.grant_count,
            "seen": len(self.seen),
            "tree_id": self.tree_id,
            "quoted_from": "GET /api/v1/cvm/pull",
        }
        if self.persist:
            rec["published"] = self._publish()
        return rec


def run_gate(root: str, base: str, proof_path: Optional[str] = None) -> dict:
    """Stage-6: two competing claims + one replay against live :8770.

    The field that proves single-owner is live_value.audio_owner quoted
    from GET /api/v1/cvm/pull AFTER the contest. It must be exactly one
    of phone|desktop|none. live_value.contested_kind must be
    OWNER_CONTESTED. live_value.replayed must be true. An exit code is
    not evidence.
    """
    src = Path(__file__).resolve()
    paths = load_paths(root)
    tree_id = paths.sentinel.tree_id
    token = load_token(paths)
    core = CoreClient(base, token)
    ho = AudioHandoff(core, paths, client_id=GATE_CLIENT,
                      load=False, persist=True)
    t = time.time()

    status = None
    core_kind = None
    winner = loser = replay = None
    quoted_before = ""
    quoted_after = ""
    contested_kind = None
    replayed = None
    grant_count = None
    try:
        status = core.get("/api/v1/status", HANDOFF_READ_S)
        if str(status.get("tree_id") or "") != tree_id:
            raise CvmDtError(
                RefusalKind.IDENTITY_MISMATCH,
                "GET /status tree_id=%r != sentinel %r"
                % (status.get("tree_id"), tree_id))
        ticket = ho.pull_ticket()
        quoted_before = audio_owner_of(ticket)
        rid1 = "handoff-gate-" + uuid.uuid4().hex
        rid2 = "handoff-gate-" + uuid.uuid4().hex
        if quoted_before == "phone":
            winner = ho.claim("desktop", rid1, from_owner="phone")
        else:
            winner = ho.claim("desktop", rid1)
        try:
            loser = ho.claim("phone", rid2)
        except CvmDtError as e:
            if e.kind != RefusalKind.OWNER_CONTESTED:
                raise
            contested_kind = str(e.kind)
            loser = {"ok": False, "kind": str(e.kind), "granted": False}
        replay = ho.claim("desktop", rid1)
        replayed = replay.get("replayed")
        grant_count = int(replay.get("grant_count") or 0)
        after = ho.pull_ticket()
        quoted_after = audio_owner_of(after)
    except CvmDtError as e:
        core_kind = str(e.kind)

    single = quoted_after in ("phone", "desktop", "none")
    ok = bool(
        core_kind is None
        and winner and winner.get("granted")
        and contested_kind == RefusalKind.OWNER_CONTESTED
        and replayed is True
        and replay and replay.get("granted") is False
        and grant_count == 1
        and quoted_after == "desktop"
        and ho.owner == "desktop"
        and single)
    live_value = {
        "live_tree_id": tree_id,
        "status_tree_id": (status or {}).get("tree_id"),
        "served_at": (status or {}).get("served_at"),
        "audio_owner": quoted_after or ho.owner,
        "audio_owner_before": quoted_before,
        "audio_owner_after": quoted_after,
        "single_owner": single and ho.owner == quoted_after,
        "contested_kind": contested_kind,
        "replayed": replayed,
        "grant_count": grant_count,
        "quoted_from": "GET /api/v1/cvm/pull",
        "core_kind": core_kind,
        "base": base,
        "timeout_s": HANDOFF_READ_S,
        "path": PULL_PATH,
    }
    rec = {
        "ok": ok,
        "stage": 6,
        "deliverable": "cvm-dt-handoff",
        "agent": "G46",
        "slice": "slice-3-audio-handoff",
        "gated_at_epoch": t,
        "source_path": str(src),
        "source_sha256": _sha256_file(src),
        "live_root": str(Path(root).resolve()),
        "live_tree_id": tree_id,
        "live_value": live_value,
        "note": "rc=0 is not the gate. live_value.audio_owner is. "
                "It must be a single token after a real contested claim "
                "on restarted :8770 GET /api/v1/cvm/pull. An exit code "
                "is not evidence.",
    }
    rec["emitted"] = "cvm-dt-handoff:%s:%s:%s:%s" % (
        tree_id,
        quoted_after or (core_kind or "NO_OWNER"),
        "contested=" + str(contested_kind or "").lower(),
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
    ap = argparse.ArgumentParser(prog="cvm-dt-handoff")
    ap.add_argument("--root", required=True)
    ap.add_argument("--base", default="http://127.0.0.1:8770")
    ap.add_argument("--client-id", default=CLIENT_ID)
    ap.add_argument("--claim", default="",
                    help="phone|desktop|none (requester)")
    ap.add_argument("--from-owner", default="",
                    help="cooperative transfer: current holder must match")
    ap.add_argument("--request-id", default="")
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
    if not ns.claim or not ns.request_id:
        ap.error("--once requires --claim and --request-id")
    paths = load_paths(ns.root)
    token = load_token(paths)
    ho = AudioHandoff(CoreClient(ns.base, token), paths, ns.client_id)
    from_owner = ns.from_owner.strip() or None
    rec = ho.claim(ns.claim, ns.request_id, from_owner=from_owner)
    print(json.dumps(rec, indent=1, default=str))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except CvmDtError as e:
        print(json.dumps({"ok": False, "kind": str(e.kind), "detail": str(e)},
                         indent=1), file=sys.stderr)
        raise SystemExit(2)
