#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cvm-phone PULL CLOCK — thin capture/playback surface (heavy-local is DT).

POST phone turn state at Core (POST /api/v1/cvm/push — §8.3 envelope, never
a second body) → GET /api/v1/cvm/pull for the desktop-owned turn +
audio_owner. NEVER claims audio ownership: desktop is the heavy-local
owner; this clock quotes and honors. Does not write audio.json, pull.json,
or handoff.json.

Tick/heartbeat/HOLD/RESUME-GATE are composed from cvm_dt_clock.poll_once
(not copied): last_run_epoch on every tick, HOLD pauses without hitting
Core, RESUME-GATE idles and does not self-clear, dead Core is UNREACHABLE
but still heartbeats. --loop is a thin while around poll_once(client=self);
it does not call cvm_dt_clock.loop (that constructs CvmDtClient and would
claim desktop). Token is read from the handed-in root's config/ role
(api_token.txt). No drive literals. No bts_ imports.

    py -3.14 builds\\cvm-phone\\cvm_phone_clock.py --root <RUNTIME> --once
    py -3.14 builds\\cvm-phone\\cvm_phone_clock.py --root <RUNTIME> --loop
    py -3.14 builds\\cvm-phone\\test_cvm_phone_clock.py

rc=0 is not the gate. Quote live_value.audio_owner from a real
GET /api/v1/cvm/pull after this clock POSTs /cvm/push: it must stay the
desktop-owned token, never a second phone owner. An exit code is not
evidence.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from typing import Any, Optional

from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
_DT = _HERE.parent / "cvm-dt"
if _DT.is_dir() and str(_DT) not in sys.path:
    sys.path.insert(0, str(_DT))
_COSMOS_LIB = _HERE.parents[2] / "cosmos"
if _COSMOS_LIB.is_dir() and str(_COSMOS_LIB) not in sys.path:
    sys.path.insert(0, str(_COSMOS_LIB))

from cosmos_clock import atomic_json  # noqa: E402
from cosmos_paths import CosmosPaths  # noqa: E402

from cvm_dt import (  # noqa: E402
    FAST_READ_S, CoreClient, CvmDtError, RefusalKind,
    audio_owner_of, core_get, core_post, load_paths, load_token, pull_url,
)
from cvm_pull import (  # noqa: E402
    CONTRACT, PULL_INTERVAL_S, parse_ticket,
)
from cvm_snap import snapshot_delta  # noqa: E402

PHONE_ID = "cvm-phone"
PUSH_PATH = "/api/v1/cvm/push"
WRITER = "cvm-phone-clock"
TURN_REL = ("cvm", "phone_turn.json")
DEFAULT_KINDS = {
    "device": {"status": "ok", "audio_route": "none",
               "surface": "capture+playback"},
}


def _clock():
    """Lazy import: cvm_dt_clock is the HOLD/heartbeat owner (not copied)."""
    import cvm_dt_clock as clk
    return clk


class CvmPhoneClock:
    """One cycle: POST /cvm/push → GET /cvm/pull. Never claims audio_owner.

    Heartbeat / HOLD / RESUME-GATE live on cvm_dt_clock.poll_once; tick()
    is the compose hook (clock is unchanged). Always pass client=self so
    poll_once does not construct CvmDtClient.
    """

    def __init__(self, core: CoreClient, paths: CosmosPaths,
                 client_id: str = PHONE_ID, *,
                 push_request_id: Optional[str] = None,
                 kinds: Optional[dict] = None):
        self.core = core
        self.paths = paths
        self.client_id = client_id
        self.tree_id = paths.sentinel.tree_id
        self.push_rid = (
            str(push_request_id).strip()
            if push_request_id
            else ("cvm-phone-" + str(client_id))
        )
        self.kinds: dict[str, Any] = dict(kinds) if kinds else {}
        self.cursor = ""
        self.last_ticket: dict[str, Any] = {}
        self._load()

    def _load(self) -> None:
        path = self.paths.state(*TURN_REL)
        if not path.is_file():
            return
        try:
            obj = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return
        if not isinstance(obj, dict):
            return
        tid = str(obj.get("tree_id") or "")
        if tid and tid != self.tree_id:
            raise CvmDtError(
                RefusalKind.IDENTITY_MISMATCH,
                "phone_turn.json tree_id=%r != sentinel %r" % (tid, self.tree_id))
        self.cursor = str(obj.get("cursor") or "")

    def _kinds(self) -> dict:
        return dict(self.kinds) if self.kinds else dict(DEFAULT_KINDS)

    def _turn_body(self) -> dict:
        """§8.3 envelope (snapshot_delta). No audio_owner key — not a claim."""
        body = snapshot_delta(
            self.push_rid, self.cursor, self._kinds(),
            client_id=self.client_id)
        body.pop("audio_owner", None)
        return body

    def _publish(self, rec: dict) -> Path:
        """Local honor projection. Never audio.json / pull.json / handoff.json."""
        path = self.paths.state(*TURN_REL)
        out: dict[str, Any] = {
            "cvm": 1,
            "tree_id": self.tree_id,
            "writer": WRITER,
            "client_id": self.client_id,
            "cursor": rec.get("cursor") or self.cursor,
            "cursor_in": rec.get("cursor_prev") or "",
            "request_id": self.push_rid,
            "quoted_audio_owner": rec.get("quoted_audio_owner"),
            "quoted_from": "GET /api/v1/cvm/pull",
            "pushed_to": "POST /api/v1/cvm/push",
            "claimed": False,
            "kinds": self._kinds(),
        }
        atomic_json(path, out)
        return path

    def cycle_once(self) -> dict:
        """POST /cvm/push then GET /cvm/pull. Quote owner; do not claim it."""
        body = self._turn_body()
        push_rec = core_post(
            self.core, PUSH_PATH, body, FAST_READ_S,
            default_400=RefusalKind.BAD_SNAPSHOT)
        data = core_get(self.core, pull_url(self.client_id), FAST_READ_S)
        quoted_owner = str(data.get("audio_owner") or "none") or "none"
        quoted_cursor = str(data.get("cursor") or "")
        ticket = parse_ticket(data, self.tree_id)
        owner = audio_owner_of(ticket)
        if owner not in ("phone", "desktop", "none"):
            owner = quoted_owner if quoted_owner in ("phone", "desktop", "none") else "none"

        prev = self.cursor
        cursor = str(
            push_rec.get("cursor_out")
            or ticket.get("cursor")
            or quoted_cursor
            or prev
            or "")
        self.cursor = cursor
        self.last_ticket = ticket

        live_value = {
            "audio_owner": owner,
            "cursor": cursor,
            "quoted_audio_owner": quoted_owner,
            "quoted_cursor": quoted_cursor,
            "claimed": False,
            "quoted_from": "GET /api/v1/cvm/pull",
            "pushed_to": "POST /api/v1/cvm/push",
        }
        rec: dict[str, Any] = {
            "ok": True,
            "cvm": 1,
            "tree_id": self.tree_id,
            "writer": WRITER,
            "audio_owner": owner,
            "claimed": False,
            "cursor": cursor,
            "cursor_prev": prev,
            "cursor_advanced": bool(cursor) and cursor != prev,
            "push_replayed": bool(push_rec.get("idempotent")),
            "quoted_from": "GET /api/v1/cvm/pull",
            "quoted_audio_owner": quoted_owner,
            "quoted_cursor": quoted_cursor,
            "pushed_to": "POST /api/v1/cvm/push",
            "live_value": live_value,
            "timeout_s": FAST_READ_S,
            "client_id": self.client_id,
            "contract": list(CONTRACT),
            "push": {
                "request_id": self.push_rid,
                "cursor_out": push_rec.get("cursor_out"),
                "idempotent": bool(push_rec.get("idempotent")),
                "path": PUSH_PATH,
            },
            "pull": {
                "cursor": quoted_cursor,
                "audio_owner": quoted_owner,
                "quoted_audio_owner": quoted_owner,
                "quoted_cursor": quoted_cursor,
            },
        }
        rec["published"] = str(self._publish(rec))
        return rec

    def tick(self, *, polls: int = 0,
             interval_s: float = PULL_INTERVAL_S,
             drain: Optional[bool] = None) -> dict:
        """One native clock tick. HOLD / heartbeat / dead-Core from DT clock."""
        return _clock().poll_once(
            str(self.paths.root),
            polls=polls,
            interval_s=interval_s,
            base=self.core.base,
            client_id=self.client_id,
            client=self,
            drain=drain,
        )


def loop(root: str, interval_s: float = PULL_INTERVAL_S, *,
         base: str = "http://127.0.0.1:8770", client_id: str = PHONE_ID,
         push_request_id: Optional[str] = None) -> int:
    """Thin --loop. Compose poll_once(client=self); do not call clock.loop."""
    paths = load_paths(root)
    client = CvmPhoneClock(
        CoreClient(base, load_token(paths)), paths, client_id,
        push_request_id=push_request_id)
    polls = 0
    while True:
        polls += 1
        client.tick(polls=polls, interval_s=interval_s)
        time.sleep(float(interval_s))


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(prog="cvm-phone-clock")
    ap.add_argument("--root", required=True,
                    help="COSMOS runtime root (handed in; sentinel verified)")
    ap.add_argument("--base", default="http://127.0.0.1:8770")
    ap.add_argument("--client-id", default=PHONE_ID)
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--loop", action="store_true")
    ap.add_argument("--interval", type=float, default=PULL_INTERVAL_S)
    ap.add_argument("--push-request-id", default="",
                    help="stable push id (default: cvm-phone-<client_id>)")
    ns = ap.parse_args(argv)
    if not ns.once and not ns.loop:
        ap.error("one of --once / --loop is required")
    rid = ns.push_request_id or None
    if ns.once:
        paths = load_paths(ns.root)
        token = load_token(paths)
        client = CvmPhoneClock(
            CoreClient(ns.base, token), paths, ns.client_id,
            push_request_id=rid)
        rec = client.cycle_once()
        print(json.dumps(rec, indent=1, default=str))
        return 0
    return loop(ns.root, ns.interval, base=ns.base, client_id=ns.client_id,
                push_request_id=rid)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except CvmDtError as e:
        print(json.dumps({"ok": False, "kind": str(e.kind), "detail": str(e)},
                         indent=1), file=sys.stderr)
        raise SystemExit(2)
