#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cvm-dt pull-clock — heavy-local drain loop (GET /cvm/pull + fold + stamp).

Desktop half of the CVM ticket (docs/CVM_ARCH.md §§4–6, 8.2). The phone
is a thin mule; this clock ACTIVELY DRAIN phone turns onto the PC:

  * continuously GET /api/v1/cvm/pull (FAST 8 s, same budget as the phone)
  * fold the last POST /cvm/push|/cvm/snapshot locally (cvm_snap)
  * stamp audio_owner=desktop via stamp_desktop_pull (ONE helper)
  * emit pull_ms / backlog / drain_lag_ms onto state/cvm/pull.json

Idle is 2 s heartbeat; Core GET coalesces for IDLE_BACKOFF_S when
backlog==0 and the last GET is fresh (local phone.json read). Command
initiation is stt_interrupt (VAD/PCM -> local STT) — independent of
the idle-GET schedule. Speech wakes cadence_wait; it does not burst
GET. A backlog>0 tick drains until idle (cap MAX_DRAIN_TURNS). Does
NOT write audio.json (H13). Never invents a ticket. Typed refusal on
dead Core / non-200.

    py -3.14 builds\\cvm-dt\\cvm_pull.py --root <RUNTIME> --once
    py -3.14 builds\\cvm-dt\\cvm_pull.py --root <RUNTIME> --loop

rc=0 is not the gate. Quote live_value.audio_owner + live_value.cursor +
live_value.pull_ms from a real GET /api/v1/cvm/pull drain cycle.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Callable, Optional

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
# Source layout: builds/cvm-dt/*.py → repo/cosmos (same hop as cvm_dt.py).
_COSMOS_LIB = Path(__file__).resolve().parents[2] / "cosmos"
if _COSMOS_LIB.is_dir() and str(_COSMOS_LIB) not in sys.path:
    sys.path.insert(0, str(_COSMOS_LIB))

from cosmos_paths import CosmosPaths  # noqa: E402
from cosmos_cvm_push import (  # noqa: E402
    DRAIN_IDLE_S, IDLE_BACKOFF_S, PULL_CLOCK_ID, PULL_INTERVAL_S,
    SPEECH_BURST_S, STAMP_OVERLAY, ack_listening, cadence_mode,
    cadence_next_s, cadence_wait, pcm_pointer, phone_cursor, phone_state,
    speech_live, stamp_desktop_pull, stt_interrupt, voice_state,
)

from cvm_dt import (  # noqa: E402
    CLIENT_ID, FAST_READ_S, ROAD_KINDS, VOICE_READ_S,
    CoreClient, CvmDtError, RefusalKind, core_get, load_paths, load_token,
    pull_url,
)
# Second-tier ear. bind_phone_stt is VOSK-only and this box has no VOSK, so
# without this the pulled phone PCM lands on a deaf PC (CVM_BACKLOG B1).
from cvm_dt_stt import phone_ear_fallback  # noqa: E402

# Exact CVM_ARCH §4–6 / §8.2 ticket. Extra keys may ride through; these six
# are the contract. voice_client_timeout_s is the heavy-local (P0) budget.
CONTRACT = (
    "tree_id", "issued_epoch", "kinds", "cursor",
    "audio_owner", "voice_client_timeout_s",
)
# GET /cvm/pull is FAST on the phone helper; reuse, do not invent a third.
HEAVY_LOCAL_PULL_S = FAST_READ_S
MAX_DRAIN_TURNS = 8
PASS_THROUGH = tuple(k for k in STAMP_OVERLAY if k not in (
    "issued_epoch", "voice_client_timeout_s"))
LIVE_KEYS = (
    "audio_owner", "cursor", "quoted_audio_owner", "quoted_cursor",
    "quoted_backlog", "pull_ms", "fold_ms", "pull_cycle_ms", "tick_ms",
    "backlog", "drain_lag_ms", "last_pull_epoch", "skipped_http",
    "cadence_mode", "speech_live", "pcm_sha256", "http_gets",
    "drained", "drain_turns", "drain_ms",
)


def ms_since(t0: float) -> float:
    return round((time.perf_counter() - t0) * 1000.0, 3)


def attach_live(rec: dict) -> dict:
    rec["live_value"] = {k: rec[k] for k in LIVE_KEYS if k in rec}
    return rec


def idle_fresh(last, *, now: float, cursor: str = "",
               phone_cur: str = "", idle_s: float = IDLE_BACKOFF_S) -> bool:
    """Skip Core GET when last GET is fresh, cursor folded, backlog==0."""
    if not last:
        return False
    try:
        if int(last.get("backlog") or 0) > 0:
            return False
        last_ep = float(last.get("last_pull_epoch") or 0.0)
    except (TypeError, ValueError):
        return False
    if not last_ep or (now - last_ep) >= idle_s:
        return False
    return not (phone_cur and phone_cur != cursor)


def parse_ticket(data: dict, tree_id: str) -> dict:
    """Read the arch contract. Missing pull → UNREACHABLE, never invent kinds."""
    if data.get("pull") is False:
        raise CvmDtError(
            RefusalKind.UNREACHABLE,
            "GET /api/v1/cvm/pull published no ticket (pull=false)")
    kind = str(data.get("core_kind") or "").strip().upper()
    if kind in ROAD_KINDS:
        raise CvmDtError(RefusalKind.UNREACHABLE,
                         "core_kind=%s" % (data.get("core_kind"),))
    got_tid = str(data.get("tree_id") or "")
    if got_tid != tree_id:
        raise CvmDtError(
            RefusalKind.IDENTITY_MISMATCH,
            "pull tree_id=%r != sentinel %r" % (got_tid, tree_id))
    raw_kinds = data.get("kinds")
    if raw_kinds is None:
        kinds: list[str] = []
    elif isinstance(raw_kinds, list):
        kinds = [str(k) for k in raw_kinds if str(k)]
    else:
        raise CvmDtError(RefusalKind.BAD_CORE, "kinds[] is the contract")
    try:
        issued = float(data.get("issued_epoch") or 0.0)
    except (TypeError, ValueError):
        issued = 0.0
    try:
        vto = float(data.get("voice_client_timeout_s") or VOICE_READ_S)
    except (TypeError, ValueError):
        vto = float(VOICE_READ_S)
    ticket = {
        "cvm": 1,
        "tree_id": tree_id,
        "issued_epoch": issued,
        "pull": True,
        "kinds": kinds,
        "cursor": str(data.get("cursor") or ""),
        "audio_owner": str(data.get("audio_owner") or "none"),
        "voice_client_timeout_s": vto,
    }
    for k in PASS_THROUGH:
        if k in data and k not in ticket:
            ticket[k] = data[k]
    return ticket


class DesktopPullClock:
    """GET /cvm/pull drain loop. Folds locally; stamps desktop + metrics."""

    def __init__(self, core: CoreClient, paths: CosmosPaths,
                 client_id: str = CLIENT_ID, *,
                 folder: Optional[Callable[[dict], dict]] = None):
        self.core = core
        self.paths = paths
        self.client_id = client_id
        self.tree_id = paths.sentinel.tree_id
        self.cursor = ""
        self.last: Optional[dict] = None
        self.folder = folder
        self.http_gets = 0

    def get_pull(self) -> dict:
        self.http_gets += 1
        return core_get(self.core, pull_url(self.client_id), HEAVY_LOCAL_PULL_S)

    def _backlog(self, ticket: dict, fold_rec: Optional[dict],
                 incoming: str) -> int:
        """Unfolder phone turns remaining AFTER this cycle.

        Only a fold (or replay of an already-folded turn) zeros backlog.
        A GET-only stamp must not clear a phone push's backlog=1.
        """
        phone_cur = phone_cursor(self.paths, self.tree_id)
        try:
            existing = int(ticket.get("backlog") or 0)
        except (TypeError, ValueError):
            existing = 0
        if fold_rec is not None and (
                fold_rec.get("folded") or fold_rec.get("replayed")):
            folded_cur = str(fold_rec.get("cursor") or incoming or "")
            if not phone_cur or folded_cur == phone_cur:
                return 0
            return 1
        if not phone_cur:
            return 0
        if phone_cur != self.cursor:
            return max(1, existing)
        return existing

    def pull_once(self, *, fold: Optional[Callable[[dict], dict]] = None
                  ) -> dict:
        t0 = time.perf_counter()
        data = self.get_pull()
        pull_ms = ms_since(t0)
        quoted_owner = str(data.get("audio_owner") or "")
        quoted_cursor = str(data.get("cursor") or "")
        quoted_backlog = data.get("backlog")
        ticket = parse_ticket(data, self.tree_id)
        fold_fn = fold if fold is not None else self.folder
        fold_rec: Optional[dict] = None
        fold_kind: Optional[str] = None
        fold_ms = 0.0
        if fold_fn is not None:
            t1 = time.perf_counter()
            try:
                fold_rec = fold_fn(ticket)
            except CvmDtError as e:
                if e.kind != RefusalKind.UNREACHABLE:
                    raise
                fold_kind = str(e.kind)
            fold_ms = ms_since(t1)

        prev = self.cursor
        incoming = str((fold_rec or {}).get("cursor")
                       or ticket.get("cursor") or "")
        backlog = self._backlog(ticket, fold_rec, incoming)
        last_pull_epoch = time.time()
        cycle_ms = ms_since(t0)
        phone = phone_state(self.paths, self.tree_id)
        speech = speech_live(phone, self.last, now=last_pull_epoch) or backlog > 0
        pcm = pcm_pointer(phone)
        overlay = dict(ticket)
        overlay.update(
            cursor=incoming or ticket.get("cursor") or "",
            clock_id=PULL_CLOCK_ID,
            pull_ms=pull_ms,
            fold_ms=fold_ms,
            pull_cycle_ms=cycle_ms,
            tick_ms=cycle_ms,
            backlog=backlog,
            drained=int(bool(fold_rec and fold_rec.get("folded"))),
            last_pull_epoch=last_pull_epoch,
            cadence_mode=cadence_mode(speech=speech, backlog=backlog),
            speech_live=speech,
            skipped_http=False,
            pcm_wanted=bool(pcm) or speech,
        )
        claimed = stamp_desktop_pull(self.paths, overlay, writer="cvm-dt-pull")
        incoming = str(claimed.get("cursor") or incoming)
        self.cursor = incoming
        self.last = claimed
        rec = {
            "ok": True,
            "cvm": 1,
            "tree_id": claimed["tree_id"],
            "issued_epoch": claimed["issued_epoch"],
            "kinds": list(claimed.get("kinds") or []),
            "cursor": incoming,
            "cursor_prev": prev,
            "cursor_advanced": incoming != prev,
            "audio_owner": "desktop",
            "voice_client_timeout_s": claimed["voice_client_timeout_s"],
            "quoted_from": "GET /api/v1/cvm/pull",
            "quoted_audio_owner": quoted_owner,
            "quoted_cursor": quoted_cursor,
            "quoted_backlog": quoted_backlog,
            "folded": bool(fold_rec and fold_rec.get("folded")),
            "fold_kind": fold_kind,
            "fold": ({
                k: fold_rec.get(k) for k in (
                    "folded", "replayed", "cursor", "cursor_prev",
                    "cursor_advanced", "fold_count", "request_id",
                )
            } if fold_rec else None),
            "pull_ms": pull_ms,
            "fold_ms": fold_ms,
            "pull_cycle_ms": claimed.get("pull_cycle_ms", cycle_ms),
            "tick_ms": cycle_ms,
            "backlog": backlog,
            "drained": overlay["drained"],
            "drain_lag_ms": claimed.get("drain_lag_ms"),
            "last_pull_epoch": last_pull_epoch,
            "skipped_http": False,
            "cadence_mode": overlay["cadence_mode"],
            "speech_live": speech,
            "pcm_sha256": pcm,
            "http_gets": self.http_gets,
            "timeout_s": HEAVY_LOCAL_PULL_S,
            "published": str(self.paths.state("cvm", "pull.json")),
            "client_id": self.client_id,
        }
        return attach_live(rec)

    def _should_coalesce(self, phone, now: float) -> bool:
        """Skip Core GET when last GET is fresh, cursor folded, backlog==0.

        Speech does NOT block coalesce — command initiation is on_speech
        (no GET). GET is background state + unfolder/backlog fallback.
        """
        return idle_fresh(
            self.last, now=now, cursor=self.cursor,
            phone_cur=phone_cursor(self.paths, self.tree_id))

    def _coalesce(self, t0: float, phone) -> dict:
        """Local phone.json read — no HTTP. Keep last real pull_ms."""
        tick_ms = ms_since(t0)
        rec = dict(self.last or {})
        pcm = pcm_pointer(phone)
        claimed = stamp_desktop_pull(
            self.paths,
            {"cadence_mode": "coalesced", "speech_live": False,
             "skipped_http": True, "tick_ms": tick_ms,
             "pcm_wanted": bool(pcm), "cursor": self.cursor},
            writer="cvm-dt-pull")
        self.last = claimed
        rec.update(
            ok=True, cvm=1, audio_owner="desktop", skipped_http=True,
            cadence_mode="coalesced", speech_live=False, tick_ms=tick_ms,
            fold_ms=0.0, pull_cycle_ms=tick_ms,
            quoted_from="local phone.json", folded=False, fold=None,
            fold_kind=None, cursor_advanced=False,
            cursor_prev=self.cursor, cursor=self.cursor, backlog=0,
            drained=0, drain_turns=0, drain_ms=tick_ms, pcm_sha256=pcm,
            http_gets=self.http_gets, quoted_backlog=0,
            drain_lag_ms=claimed.get("drain_lag_ms"),
            kinds=list(claimed.get("kinds") or []),
            tree_id=claimed.get("tree_id"),
            issued_epoch=claimed.get("issued_epoch"),
            voice_client_timeout_s=claimed.get("voice_client_timeout_s"),
            timeout_s=HEAVY_LOCAL_PULL_S, client_id=self.client_id,
            published=str(self.paths.state("cvm", "pull.json")),
        )
        return attach_live(rec)

    def on_speech(self, *, now: Optional[float] = None) -> dict:
        """Foreground interrupt: local STT, no Core GET. Never invents pull.json.

        Listening ack fires BEFORE stt_interrupt / stamp — not gated on
        idle-GET, drain-GET, or the id18 writer.
        """
        now = time.time() if now is None else float(now)
        phone = phone_state(self.paths, self.tree_id)
        sha = pcm_pointer(phone)
        prev_sha = str((self.last or {}).get("stt_pcm_sha256") or "")
        listen = ack_listening(now=now) if sha and sha != prev_sha else None
        stt = stt_interrupt(self.paths, phone, self.last, now=now)
        # Heavy-local means the PC actually hears it. bind_phone_stt only
        # knows VOSK; on a box without it this promotes STT_NONE to the
        # on-box recognizer. Named skip when it does not engage.
        stt = phone_ear_fallback(self.paths, phone, stt)
        if stt.get("ear_ms") is not None:
            # CVM_PULLCLOCK_ARCH:118 names cvm_ear_ms the product gate. The
            # desktop half now measures it; the ticket cannot carry it yet
            # (see CVM_BACKLOG B5 — cvm_ear_ms is not in DRAIN_KEYS).
            stt["cvm_ear_ms"] = stt["ear_ms"]
        if listen:
            stt["listen_ack"] = listen.get("ack")
            stt["gated_on_pull"] = False
            stt["gated_on_id18"] = False
        stt.setdefault("voice_state", voice_state())
        pull_p = self.paths.state("cvm", "pull.json")
        if self.last is not None and pull_p.is_file():
            overlay = {k: stt.get(k) for k in (
                "first_word_ms", "stt_kind", "stt_engine", "stt_pcm_sha256",
                "vad_event") if stt.get(k) is not None}
            overlay["cursor"] = self.cursor
            if overlay:
                self.last = stamp_desktop_pull(
                    self.paths, overlay, writer="cvm-dt-pull")
        stt["http_gets"] = self.http_gets
        return stt

    def _fold_stt(self, rec: dict, stt: dict) -> dict:
        for k in ("first_word_ms", "stt_kind", "stt_engine", "stt_pcm_sha256",
                  "vad_event", "voice_state", "listen_ack", "ack",
                  "gated_on_pull", "ear_ms", "cvm_ear_ms", "transcript",
                  "stt_recognizer", "stt_fallback"):
            if stt.get(k) is not None:
                rec[k] = stt[k]
                live = rec.get("live_value")
                if isinstance(live, dict):
                    live[k] = stt[k]
        rec.setdefault("voice_state", voice_state())
        return rec

    def drain(self, *, fold: Optional[Callable[[dict], dict]] = None,
              max_turns: int = MAX_DRAIN_TURNS) -> dict:
        """GET + fold + stamp until backlog==0 or max_turns (fail-closed cap).

        stt_interrupt runs without GET whenever a ticket already exists.
        Idle ticks inside IDLE_BACKOFF_S skip Core GET. Backlog>0 is the
        only GET burst; speech is interrupt.
        """
        t0 = time.perf_counter()
        now = time.time()
        stt = (self.on_speech(now=now) if self.last is not None else
               {"vad_event": False})
        phone = phone_state(self.paths, self.tree_id)
        if self._should_coalesce(phone, now):
            return self._fold_stt(self._coalesce(t0, phone), stt)
        last: Optional[dict] = None
        n = 0
        total_folded = 0
        while n < max(1, int(max_turns)):
            rec = self.pull_once(fold=fold)
            n += 1
            last = rec
            if rec.get("folded"):
                total_folded += 1
            try:
                left = int(rec.get("backlog") or 0)
            except (TypeError, ValueError):
                left = 0
            if left <= 0:
                break
        assert last is not None
        last["drained"] = total_folded
        last["drain_turns"] = n
        last["drain_ms"] = ms_since(t0)
        return self._fold_stt(attach_live(last), self.on_speech(now=time.time()))


def loop(clock: DesktopPullClock, interval_s: float = DRAIN_IDLE_S) -> int:
    while True:
        rec: Optional[dict] = None
        try:
            rec = clock.drain()
            print(json.dumps(rec, indent=1, default=str), flush=True)
        except CvmDtError as e:
            rec = {
                "ok": False,
                "kind": str(e.kind),
                "detail": str(e),
                "quoted_from": "GET /api/v1/cvm/pull",
            }
            print(json.dumps(rec, indent=1), flush=True)
        cadence_wait(rec, interval_s, paths=clock.paths,
                     tree_id=clock.tree_id)


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(prog="cvm-dt-pull")
    ap.add_argument("--root", required=True)
    ap.add_argument("--base", default="http://127.0.0.1:8770")
    ap.add_argument("--client-id", default=CLIENT_ID)
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--loop", action="store_true")
    ap.add_argument("--interval", type=float, default=DRAIN_IDLE_S)
    ns = ap.parse_args(argv)
    if not ns.once and not ns.loop:
        ap.error("one of --once / --loop is required")
    paths = load_paths(ns.root)
    token = load_token(paths)
    core = CoreClient(ns.base, token)
    # Lazy: cvm_snap imports this module (CONTRACT / parse_ticket).
    from cvm_snap import SnapshotConsumer
    snap = SnapshotConsumer(core, paths, ns.client_id)

    def _fold(ticket: dict) -> dict:
        snap.seed_ticket(ticket)
        return snap.ingest_phone()

    clock = DesktopPullClock(core, paths, ns.client_id, folder=_fold)
    if ns.once:
        rec = clock.drain()
        print(json.dumps(rec, indent=1, default=str))
        return 0
    return loop(clock, ns.interval)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except CvmDtError as e:
        print(json.dumps({"ok": False, "kind": str(e.kind), "detail": str(e)},
                         indent=1), file=sys.stderr)
        raise SystemExit(2)
