#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cvm-dt INTEGRATION — one heavy-local desktop voice client.

PULL all CVM/session state off Core (GET /api/v1/cvm/pull — never invent a
ticket) → DRAIN-FOLD the POST /cvm/push phone turn (phone.json) into one
desktop-owned turn (monotonic cursor) → HANDOFF audio_owner=desktop via
stamp_desktop_pull (shared with cosmos_cvm_push; not copied). Drain stamps
pull_ms/backlog/drain_lag_ms onto pull.json. A stable handoff request_id
makes --loop a replay (exactly-once; not a second owner).

Tick/heartbeat/HOLD/RESUME-GATE are composed from cvm_dt_clock.poll_once
(not copied): last_run_epoch on every tick, HOLD pauses without pulling
Core, RESUME-GATE idles and does not self-clear, dead Core is UNREACHABLE
but still heartbeats. Token is read from the handed-in root's config/
role (api_token.txt). No drive literals. No bts_ imports.

    py -3.14 builds\\cvm-dt\\cvm_dt_client.py --root <RUNTIME> --once
    py -3.14 builds\\cvm-dt\\cvm_dt_client.py --root <RUNTIME> --loop
    py -3.14 builds\\cvm-dt\\test_cvm_dt_client.py

rc=0 is not the gate. Quote live_value.audio_owner from a real
GET /api/v1/cvm/pull after a contested desktop handoff against a
RESTARTED :8770. live_value.cursor on that same GET must be advanced
vs the pre-cycle ticket. An exit code is not evidence.
"""
from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Optional

from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
_COSMOS_LIB = Path(__file__).resolve().parents[2] / "cosmos"
if _COSMOS_LIB.is_dir() and str(_COSMOS_LIB) not in sys.path:
    sys.path.insert(0, str(_COSMOS_LIB))

from cosmos_paths import CosmosPaths  # noqa: E402

from cvm_dt import (  # noqa: E402
    CLIENT_ID, FAST_READ_S, OWNERS,
    CoreClient, CvmDtError, RefusalKind,
    audio_owner_of, load_paths, load_token,
)
from cvm_pull import (  # noqa: E402
    CONTRACT, DRAIN_IDLE_S, DesktopPullClock,
)
from cvm_snap import SnapshotConsumer  # noqa: E402
from cvm_handoff import AudioHandoff  # noqa: E402

WRITER = "cvm-dt-client"


def _clock():
    """Lazy import: cvm_dt_clock already imports this module at load."""
    import cvm_dt_clock as clk
    return clk


class CvmDtClient:
    """One cycle: pull-clock → snapshot fold → desktop audio handoff.

    Heartbeat / HOLD / RESUME-GATE live on cvm_dt_clock.poll_once; tick()
    is the compose hook (clock is unchanged).
    """

    def __init__(self, core: CoreClient, paths: CosmosPaths,
                 client_id: str = CLIENT_ID, *,
                 handoff_request_id: Optional[str] = None):
        self.core = core
        self.paths = paths
        self.client_id = client_id
        self.tree_id = paths.sentinel.tree_id
        self.pull = DesktopPullClock(core, paths, client_id)
        self.snap = SnapshotConsumer(core, paths, client_id)
        self.handoff = AudioHandoff(core, paths, client_id)
        self.handoff_rid = (
            str(handoff_request_id).strip()
            if handoff_request_id
            else ("cvm-dt-client-" + str(client_id))
        )

    def cycle_once(self) -> dict:
        """GET /cvm/pull (never invented) → drain-fold phone.json → claim desktop.

        Fold is composed into DesktopPullClock.drain (not copied here). The
        clock stamps pull_ms/backlog/drain_lag_ms onto pull.json in the same
        write as audio_owner=desktop.
        """
        def _fold(ticket: dict) -> dict:
            self.snap.seed_ticket(ticket)
            return self.snap.ingest_phone()

        pull_rec = self.pull.drain(fold=_fold)
        # Stamp source is the drained pull.json (backlog=0 + metrics),
        # not the GET ticket (which still carried the phone's backlog=1).
        ticket = dict(self.pull.last or {})
        self.handoff.ticket = ticket

        quoted_owner = str(pull_rec.get("quoted_audio_owner") or "none") or "none"
        if quoted_owner not in OWNERS:
            quoted_owner = audio_owner_of(ticket)
        if not self.handoff.seen:
            self.handoff.owner = quoted_owner

        fold = pull_rec.get("fold")
        fold_kind = pull_rec.get("fold_kind")
        cursor = str(pull_rec.get("cursor") or self.snap.cursor or "")
        cursor_prev = str(pull_rec.get("cursor_prev") or "")
        from_owner = "phone" if self.handoff.owner == "phone" else None
        ho = self.handoff.claim(
            "desktop", self.handoff_rid, from_owner=from_owner)
        owner = str(ho.get("audio_owner") or "")
        if owner != "desktop":
            raise CvmDtError(
                RefusalKind.OWNER_CONTESTED,
                "cycle did not land audio_owner=desktop (got %r)" % owner)

        live_value = {
            "audio_owner": "desktop",
            "cursor": cursor,
            "quoted_audio_owner": pull_rec.get("quoted_audio_owner"),
            "quoted_cursor": pull_rec.get("quoted_cursor"),
            "quoted_backlog": pull_rec.get("quoted_backlog"),
            "handoff_replayed": bool(ho.get("replayed")),
            "grant_count": ho.get("grant_count"),
            "quoted_from": "GET /api/v1/cvm/pull",
            "pull_ms": pull_rec.get("pull_ms"),
            "pull_cycle_ms": pull_rec.get("pull_cycle_ms"),
            "backlog": pull_rec.get("backlog"),
            "drain_lag_ms": pull_rec.get("drain_lag_ms"),
            "last_pull_epoch": pull_rec.get("last_pull_epoch"),
            "tick_ms": pull_rec.get("tick_ms"),
            "skipped_http": bool(pull_rec.get("skipped_http")),
            "cadence_mode": pull_rec.get("cadence_mode"),
            "speech_live": pull_rec.get("speech_live"),
            "pcm_sha256": pull_rec.get("pcm_sha256"),
            "first_word_ms": pull_rec.get("first_word_ms"),
            "stt_kind": pull_rec.get("stt_kind"),
        }
        rec: dict[str, Any] = {
            "ok": True,
            "cvm": 1,
            "tree_id": self.tree_id,
            "writer": WRITER,
            "audio_owner": "desktop",
            "cursor": cursor,
            "cursor_prev": cursor_prev,
            "cursor_advanced": bool(fold and fold.get("cursor_advanced")),
            "folded": bool(fold and fold.get("folded")),
            "replayed_fold": bool(fold and fold.get("replayed")),
            "handoff_granted": bool(ho.get("granted")),
            "handoff_replayed": bool(ho.get("replayed")),
            "grant_count": ho.get("grant_count"),
            "quoted_from": "GET /api/v1/cvm/pull",
            "quoted_audio_owner": pull_rec.get("quoted_audio_owner"),
            "quoted_cursor": pull_rec.get("quoted_cursor"),
            "fold_kind": fold_kind,
            "pull_ms": pull_rec.get("pull_ms"),
            "pull_cycle_ms": pull_rec.get("pull_cycle_ms"),
            "backlog": pull_rec.get("backlog"),
            "drain_lag_ms": pull_rec.get("drain_lag_ms"),
            "last_pull_epoch": pull_rec.get("last_pull_epoch"),
            "tick_ms": pull_rec.get("tick_ms"),
            "skipped_http": bool(pull_rec.get("skipped_http")),
            "cadence_mode": pull_rec.get("cadence_mode"),
            "speech_live": pull_rec.get("speech_live"),
            "pcm_sha256": pull_rec.get("pcm_sha256"),
            "first_word_ms": pull_rec.get("first_word_ms"),
            "stt_kind": pull_rec.get("stt_kind"),
            "live_value": live_value,
            "timeout_s": FAST_READ_S,
            "client_id": self.client_id,
            "contract": list(CONTRACT),
            "pull": {
                "cursor": pull_rec.get("cursor"),
                "audio_owner": pull_rec.get("audio_owner"),
                "quoted_audio_owner": pull_rec.get("quoted_audio_owner"),
                "quoted_cursor": pull_rec.get("quoted_cursor"),
                "pull_ms": pull_rec.get("pull_ms"),
                "backlog": pull_rec.get("backlog"),
            },
            "fold": ({
                k: fold.get(k) for k in (
                    "folded", "replayed", "cursor", "cursor_prev",
                    "cursor_advanced", "fold_count", "request_id",
                )
            } if fold else None),
            "handoff": {
                k: ho.get(k) for k in (
                    "granted", "replayed", "audio_owner", "audio_owner_prev",
                    "grant_count", "request_id",
                )
            },
        }
        return rec

    def tick(self, *, polls: int = 0,
             interval_s: float = DRAIN_IDLE_S,
             drain: Optional[bool] = None) -> dict:
        """One native clock tick. HOLD / heartbeat / dead-Core from the clock."""
        return _clock().poll_once(
            str(self.paths.root),
            polls=polls,
            interval_s=interval_s,
            base=self.core.base,
            client_id=self.client_id,
            handoff_request_id=self.handoff_rid,
            client=self,
            drain=drain,
        )


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(prog="cvm-dt-client")
    ap.add_argument("--root", required=True,
                    help="COSMOS runtime root (handed in; sentinel verified)")
    ap.add_argument("--base", default="http://127.0.0.1:8770")
    ap.add_argument("--client-id", default=CLIENT_ID)
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--loop", action="store_true")
    ap.add_argument("--interval", type=float, default=DRAIN_IDLE_S)
    ap.add_argument("--handoff-request-id", default="",
                    help="stable claim id (default: cvm-dt-client-<client_id>)")
    ns = ap.parse_args(argv)
    if not ns.once and not ns.loop:
        ap.error("one of --once / --loop is required")
    if ns.once:
        paths = load_paths(ns.root)
        token = load_token(paths)
        client = CvmDtClient(
            CoreClient(ns.base, token), paths, ns.client_id,
            handoff_request_id=ns.handoff_request_id or None)
        rec = client.cycle_once()
        print(json.dumps(rec, indent=1, default=str))
        return 0
    return _clock().loop(
        ns.root, ns.interval, base=ns.base, client_id=ns.client_id,
        handoff_request_id=ns.handoff_request_id or None)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except CvmDtError as e:
        print(json.dumps({"ok": False, "kind": str(e.kind), "detail": str(e)},
                         indent=1), file=sys.stderr)
        raise SystemExit(2)
