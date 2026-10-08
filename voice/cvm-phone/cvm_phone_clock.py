#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cvm-phone PULL CLOCK — thin capture/playback surface (heavy-local is DT).

GET /api/v1/cvm/pull first (honor the ticket; H12 / arch §6.3) then POST
/api/v1/cvm/push only on a delta. The ticket's kinds[] IS the pull: every
asked kind comes back with a typed status (data / `PERM_DENIED:<kind>` /
`NO_COLLECTOR:<kind>`, see cvm_phone_pull) — never an absent key, which
would read as "nothing to report". Idle ticks inside IDLE_BACKOFF_S skip
HTTP — a replay POST of an identical body is radio tax. NEVER claims
audio ownership: desktop is the heavy-local owner; this clock quotes
and honors. Does not write audio.json, pull.json, or handoff.json.

Tick/heartbeat/HOLD/RESUME-GATE are composed from cvm_dt_clock.poll_once
(not copied). --loop is a thin while around poll_once(client=self); it
does not call cvm_dt_clock.loop (that constructs CvmDtClient and would
claim desktop). Token from the handed-in root's config/ role. No drive
literals. No bts_ imports.

    py -3.14 builds\\cvm-phone\\cvm_phone_clock.py --root <RUNTIME> --once
    py -3.14 builds\\cvm-phone\\cvm_phone_clock.py --root <RUNTIME> --loop
    py -3.14 builds\\cvm-phone\\test_cvm_phone_clock.py

rc=0 is not the gate. Quote live_value.tick_ms + skipped_http + http_posts
from a real GET /cvm/pull after this clock POSTs /cvm/push: audio_owner
stays desktop, idle second tick skips the replay POST.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from typing import Any, Iterable, Optional

from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
_DT = _HERE.parent / "cvm-dt"
if _DT.is_dir() and str(_DT) not in sys.path:
    sys.path.insert(0, str(_DT))
# builds/cvm-phone -> repo/cosmos. parents[1] because _HERE is already the
# directory; parents[2] pointed a hop too high, so the documented --once CLI
# died on `cosmos_clock` and only ever worked from a test that pre-seeded
# sys.path. A suite passing is not the module running.
_COSMOS_LIB = _HERE.parents[1] / "cosmos"
if _COSMOS_LIB.is_dir() and str(_COSMOS_LIB) not in sys.path:
    sys.path.insert(0, str(_COSMOS_LIB))

from cosmos_clock import atomic_json  # noqa: E402
from cosmos_paths import CosmosPaths  # noqa: E402

from cvm_dt import (  # noqa: E402
    FAST_READ_S, OWNERS, CoreClient, CvmDtError, RefusalKind,
    audio_owner_of, core_get, core_post, load_paths, load_token, pull_url,
)
from cvm_pull import (  # noqa: E402
    CONTRACT, PULL_INTERVAL_S, idle_fresh, ms_since, parse_ticket,
)
from cvm_snap import snapshot_delta  # noqa: E402

from cvm_phone_pull import (  # noqa: E402
    DEFAULT_GRANTS, collect_kinds, device_kind, statuses, unsupported,
)

PHONE_ID = "cvm-phone"
PUSH_PATH = "/api/v1/cvm/push"
WRITER = "cvm-phone-clock"
TURN_REL = ("cvm", "phone_turn.json")


def _clock():
    """Lazy import: cvm_dt_clock is the HOLD/heartbeat owner (not copied)."""
    import cvm_dt_clock as clk
    return clk


class CvmPhoneClock:
    """GET /cvm/pull, POST /cvm/push only on delta. Never claims audio_owner."""

    def __init__(self, core: CoreClient, paths: CosmosPaths,
                 client_id: str = PHONE_ID, *,
                 push_request_id: Optional[str] = None,
                 kinds: Optional[dict] = None,
                 grants: Optional[Iterable[Any]] = None):
        self.core = core
        self.paths = paths
        self.client_id = client_id
        self.tree_id = paths.sentinel.tree_id
        self.push_rid = (
            str(push_request_id).strip()
            if push_request_id
            else ("cvm-phone-" + str(client_id))
        )
        # Held data (what this build can actually read) vs granted
        # capability (what it is allowed to read). Both fail closed:
        # an ungranted kind is PERM_DENIED, a granted kind with no
        # reader is NO_COLLECTOR — never a silent empty.
        self.kinds: dict[str, Any] = (
            dict(kinds) if kinds else {"device": device_kind()})
        self.grants: tuple = tuple(
            grants if grants is not None else DEFAULT_GRANTS)
        self.requested: tuple = ()
        self.cursor = ""
        self.last_ticket: dict[str, Any] = {}
        self.http_gets = self.http_posts = 0
        self._last_pull_epoch = 0.0
        self._pushed_rid = ""
        self._pushed_kinds: Optional[dict] = None
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
        req = obj.get("requested")
        if isinstance(req, list):
            self.requested = tuple(str(k) for k in req if str(k))
        if str(obj.get("request_id") or "") == self.push_rid:
            self._pushed_rid = self.push_rid
            k = obj.get("kinds")
            self._pushed_kinds = k if isinstance(k, dict) else None

    def _kinds(self) -> dict:
        """Answer the ticket's kinds[] — the pull. Typed, never absent."""
        return collect_kinds(self.requested, grants=self.grants,
                             data=self.kinds)

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
        atomic_json(path, {
            "cvm": 1, "tree_id": self.tree_id, "writer": WRITER,
            "client_id": self.client_id,
            "cursor": rec.get("cursor") or self.cursor,
            "cursor_in": rec.get("cursor_prev") or "",
            "request_id": self.push_rid,
            "quoted_audio_owner": rec.get("quoted_audio_owner"),
            "quoted_from": rec.get("quoted_from"),
            "pushed_to": rec.get("pushed_to"),
            "claimed": False, "kinds": self._kinds(),
            "requested": list(self.requested),
            "kind_status": rec.get("kind_status"),
            # The measured value phone reachability is read from
            # (cvm_phone_pull.phone_seen). A stale stamp is a stale phone.
            "last_seen_epoch": rec.get("last_seen_epoch"),
            "skipped_http": rec.get("skipped_http"),
            "tick_ms": rec.get("tick_ms"),
            "push_bytes": rec.get("push_bytes"),
            "http_posts": rec.get("http_posts"),
        })
        return path

    def cycle_once(self) -> dict:
        """GET ticket first; POST only on delta; idle ticks skip HTTP."""
        t0 = time.perf_counter()
        now, prev = time.time(), self.cursor
        push_rec: Optional[dict] = None
        pull_ms = push_ms = 0.0
        push_bytes, skipped_http = 0, False
        if self.last_ticket and idle_fresh(
                {"last_pull_epoch": self._last_pull_epoch, "backlog": 0},
                now=now, cursor=self.cursor):
            skipped_http, ticket = True, self.last_ticket
            quoted_owner = str(ticket.get("audio_owner") or "none") or "none"
            quoted_cursor = str(prev or ticket.get("cursor") or "")
            quoted_from, cursor = "local phone_turn.json", quoted_cursor
        else:
            data = core_get(self.core, pull_url(self.client_id), FAST_READ_S)
            pull_ms, self.http_gets = ms_since(t0), self.http_gets + 1
            self._last_pull_epoch = now
            quoted_owner = str(data.get("audio_owner") or "none") or "none"
            quoted_cursor = str(data.get("cursor") or "")
            ticket = parse_ticket(data, self.tree_id)
            # The ticket's kinds[] IS the pull. Honor the ask; a kind the
            # PC stops asking for stops costing radio.
            self.requested = tuple(str(k) for k in (ticket.get("kinds") or ())
                                   if str(k))
            quoted_from = "GET /api/v1/cvm/pull"
            if (self._pushed_rid != self.push_rid
                    or self._pushed_kinds != self._kinds()):
                t1, body = time.perf_counter(), self._turn_body()
                push_bytes = len(json.dumps(body, separators=(",", ":"))
                                 .encode("utf-8"))
                push_rec = core_post(
                    self.core, PUSH_PATH, body, FAST_READ_S,
                    default_400=RefusalKind.BAD_SNAPSHOT)
                push_ms, self.http_posts = ms_since(t1), self.http_posts + 1
                self._pushed_rid, self._pushed_kinds = self.push_rid, self._kinds()
            cursor = str((push_rec or {}).get("cursor_out")
                         or ticket.get("cursor") or quoted_cursor or prev or "")
            ticket = dict(ticket, **({"cursor": cursor} if cursor else {}))
            self.last_ticket = ticket
        owner = audio_owner_of(ticket)
        if owner not in OWNERS:
            owner = quoted_owner if quoted_owner in OWNERS else "none"
        self.cursor = cursor
        replayed = bool((push_rec or {}).get("idempotent")) or (
            push_rec is None and self._pushed_rid == self.push_rid)
        rec: dict[str, Any] = {
            "ok": True, "cvm": 1, "tree_id": self.tree_id, "writer": WRITER,
            "audio_owner": owner, "claimed": False,
            "cursor": cursor, "cursor_prev": prev,
            "cursor_advanced": bool(cursor) and cursor != prev,
            "push_replayed": replayed, "quoted_from": quoted_from,
            "quoted_audio_owner": quoted_owner, "quoted_cursor": quoted_cursor,
            "pushed_to": "POST /api/v1/cvm/push", "timeout_s": FAST_READ_S,
            "client_id": self.client_id, "contract": list(CONTRACT),
            "requested": list(self.requested),
            "kind_status": statuses(self._kinds()),
            "unsupported_kinds": unsupported(ticket.get("kinds") or ()),
            "last_seen_epoch": now,
            "skipped_http": skipped_http, "tick_ms": ms_since(t0),
            "pull_ms": pull_ms, "push_ms": push_ms, "push_bytes": push_bytes,
            "http_gets": self.http_gets, "http_posts": self.http_posts,
        }
        rec["live_value"] = {k: rec[k] for k in (
            "audio_owner", "cursor", "claimed", "quoted_audio_owner",
            "quoted_cursor", "quoted_from", "pushed_to", "skipped_http",
            "tick_ms", "pull_ms", "push_ms", "push_bytes", "http_gets",
            "http_posts", "requested", "kind_status", "last_seen_epoch")}
        rec["published"] = str(self._publish(rec))
        return rec

    def tick(self, *, polls: int = 0,
             interval_s: float = PULL_INTERVAL_S,
             drain: Optional[bool] = None) -> dict:
        """One native clock tick. HOLD / heartbeat / dead-Core from DT clock."""
        return _clock().poll_once(
            str(self.paths.root), polls=polls, interval_s=interval_s,
            base=self.core.base, client_id=self.client_id, client=self,
            drain=drain)


def loop(root: str, interval_s: float = PULL_INTERVAL_S, *,
         base: str = "http://127.0.0.1:8770", client_id: str = PHONE_ID,
         push_request_id: Optional[str] = None,
         grants: Optional[Iterable[Any]] = None) -> int:
    """Thin --loop. Compose poll_once(client=self); do not call clock.loop."""
    paths = load_paths(root)
    client = CvmPhoneClock(
        CoreClient(base, load_token(paths)), paths, client_id,
        push_request_id=push_request_id, grants=grants)
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
    ap.add_argument("--grants", default=",".join(DEFAULT_GRANTS),
                    help="capability-granted kinds, comma separated; every "
                         "other asked kind answers PERM_DENIED:<kind>")
    ns = ap.parse_args(argv)
    if not ns.once and not ns.loop:
        ap.error("one of --once / --loop is required")
    rid = ns.push_request_id or None
    grants = tuple(g.strip() for g in str(ns.grants).split(",") if g.strip())
    if ns.once:
        paths = load_paths(ns.root)
        rec = CvmPhoneClock(
            CoreClient(ns.base, load_token(paths)), paths, ns.client_id,
            push_request_id=rid, grants=grants).cycle_once()
        print(json.dumps(rec, indent=1, default=str))
        return 0
    return loop(ns.root, ns.interval, base=ns.base, client_id=ns.client_id,
                push_request_id=rid, grants=grants)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except CvmDtError as e:
        print(json.dumps({"ok": False, "kind": str(e.kind), "detail": str(e)},
                         indent=1), file=sys.stderr)
        raise SystemExit(2)
