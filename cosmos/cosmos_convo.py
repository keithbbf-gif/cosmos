#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_convo - DURABLE CONVERSATIONAL SESSIONS over the authority ledger.

THE PROBLEM THIS CLOSES: a phone client (KDash mobile, voice or text) carries a
throwaway context window - hang up and the conversation is gone. Here the client
carries a SESSION ID instead. A voice turn and a text turn on the same sid
continue ONE conversation; reconnecting from the road resumes it, because the
conversation was never in the client at all.

THE LEDGER IS THE AUTHORITY (COSMOS canon, ratified): ConvoStore keeps NO state
of its own. Every read is a projection folded from ledger.verify(); every write
is an event appended to the chain. A second ConvoStore constructed on the same
ledger sees the same sessions - that IS durability, and it is measured, not
assumed: get_session returns what the ledger actually holds.

EVENTS (this module's vocabulary on the shared chain):
    CONVO_OPENED   {sid, title, scope, owner, opened_epoch}
    CONVO_TURN     {sid, role, text, mode, sources, job_ids, seq}
    CONVO_CLOSED   {sid, closed_epoch}
    CONVO_REOPENED {sid, reopened_epoch}

FOLD HARDENING (2026-08-23 final hardening, three-family convergence): the
ledger is signed, but the fold is still DEFENSE IN DEPTH against a record that
is chained and authenticated yet WRONG for this projection (another module's
bug, a replayed event, a hand-crafted payload signed by a compromised writer):
  * a SECOND CONVO_OPENED for an existing sid is IGNORED - it can never reset a
    session's turns or retitle/reown it;
  * a CONVO_TURN whose sid is unknown, whose session is CLOSED, or whose seq is
    not exactly turn_count+1 (contiguous) is IGNORED - replays and gap-jumps do
    not project;
  * a malformed payload (wrong types, missing fields) is IGNORED, never folded
    and never a crash. Ignoring is correct here: the fold is a projection, and
    refusing to project a bad record keeps the projection honest without
    making history unreadable.

OWNERSHIP (2026-08-23): create_session(..., owner=...) binds a session to a
principal; assert_owner(sid, owner) refuses NO_SESSION on a mismatch - the SAME
kind and detail as an unknown sid, deliberately, so a caller probing other
principals' sids cannot distinguish "not yours" from "not there". Single-bearer
COSMOS has one principal today; device-scoped tokens are coming, and the bind
exists now so they land on a closed seam.

NEVER DELETE: there is no delete API. close_session() appends CONVO_CLOSED and
the turns REMAIN in the chain forever; get_session on a closed sid still returns
every turn.

REOPEN-AFTER-CLOSE RULE (chosen and tested): a turn appended to a closed session
REFUSES with BAD_TURN. reopen_session(sid) appends CONVO_REOPENED, after which
turns flow again. Refusing silently-resurrecting a closed conversation keeps
"closed" an honest claim; making reopen an explicit EVENT keeps the history
honest about when and that it happened. (Close of a closed session and reopen
of an open one likewise refuse BAD_TURN - state transitions are recorded facts,
never no-ops that pretend.)

Typed errors only: ConvoError.kind in {NO_SESSION, BAD_ROLE, BAD_TURN,
BAD_SCOPE}. No bare exceptions escape the API. Injected clock for determinism.
Depends ONLY on cosmos_ledger + stdlib.
"""
from __future__ import annotations

import time
import uuid
from typing import Optional

ROLES = ("user", "assistant", "system")

EV_OPENED = "CONVO_OPENED"
EV_TURN = "CONVO_TURN"
EV_CLOSED = "CONVO_CLOSED"
EV_REOPENED = "CONVO_REOPENED"


class ConvoError(RuntimeError):
    """kind in {NO_SESSION, BAD_ROLE, BAD_TURN, BAD_SCOPE}."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


def _dedup(seq):
    """Order-preserving dedup (first occurrence wins)."""
    seen, out = set(), []
    for x in seq:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


def _str_list(value, what: str, kind: str) -> list:
    """None -> []; a list of strings passes; anything else is a typed refusal."""
    if value is None:
        return []
    if not isinstance(value, list) or not all(isinstance(x, str) for x in value):
        raise ConvoError(kind, f"{what} must be a list of strings, got "
                               f"{type(value).__name__}: {value!r}")
    return list(value)


class ConvoStore:
    """Conversational sessions as a PROJECTION of the ledger. No state here."""

    def __init__(self, ledger, clock=time.time):
        self._ledger = ledger
        self._clock = clock

    # ---------------- projection (the ONLY read path) ----------------
    @staticmethod
    def _fold(sessions: dict, rec: dict) -> dict:
        """Hardened fold (defense in depth over the signed chain - see module
        docstring): duplicate opens never reset, non-contiguous or closed-side
        turns never project, malformed payloads never fold and never crash."""
        if not isinstance(rec, dict):
            return sessions
        ev = rec.get("event")
        p = rec.get("payload")
        if not isinstance(p, dict):
            return sessions
        sid = p.get("sid")
        if not isinstance(sid, str) or not sid:
            return sessions
        if ev == EV_OPENED:
            if sid in sessions:
                # REPLAY/FORGERY FENCE: a second open for a known sid would
                # wipe every turn and rewrite title/owner. It is ignored.
                return sessions
            if not isinstance(p.get("title"), str):
                return sessions                      # malformed: not folded
            owner = p.get("owner")
            if owner is not None and not isinstance(owner, str):
                return sessions                      # malformed: not folded
            sessions[sid] = {
                "sid": sid, "title": p["title"],
                "scope": list(p.get("scope") or []),
                "owner": owner,
                "open": True, "turns": [],
                "last_epoch": p.get("opened_epoch", rec.get("t")),
            }
        elif ev == EV_TURN and sid in sessions:
            s = sessions[sid]
            if not s["open"]:
                return sessions       # a turn on a CLOSED session never projects
            if p.get("seq") != len(s["turns"]) + 1:
                return sessions       # non-contiguous seq: replay/gap, ignored
            if (p.get("role") not in ROLES
                    or not isinstance(p.get("text"), str) or not p["text"].strip()
                    or not isinstance(p.get("mode"), str)):
                return sessions                      # malformed: not folded
            srcs = p.get("sources") or []
            jobs = p.get("job_ids") or []
            if not (isinstance(srcs, list) and all(isinstance(x, str) for x in srcs)
                    and isinstance(jobs, list)
                    and all(isinstance(x, str) for x in jobs)):
                return sessions                      # malformed: not folded
            s["turns"].append({
                "role": p["role"], "text": p["text"], "mode": p["mode"],
                "sources": list(srcs),
                "job_ids": list(jobs),
                "epoch": rec.get("t"),
            })
            s["last_epoch"] = rec.get("t")
        elif ev == EV_CLOSED and sid in sessions and sessions[sid]["open"]:
            sessions[sid]["open"] = False
            sessions[sid]["last_epoch"] = p.get("closed_epoch", rec.get("t"))
        elif ev == EV_REOPENED and sid in sessions and not sessions[sid]["open"]:
            sessions[sid]["open"] = True
            sessions[sid]["last_epoch"] = p.get("reopened_epoch", rec.get("t"))
        return sessions

    def _project(self, records=None) -> dict:
        """Rebuild ALL session state by replaying the verified chain.
        `records` lets append_guarded's decide() reuse its freshly-replayed
        history; otherwise the ledger is re-verified from disk right now -
        measured, not remembered."""
        sessions: dict = {}
        if records is None:
            records = self._ledger.verify()
        for rec in records:
            self._fold(sessions, rec)
        return sessions

    # ---------------- API ----------------
    def create_session(self, title: str, scope: Optional[list] = None,
                       owner: Optional[str] = None) -> str:
        if scope is not None and not isinstance(scope, list):
            raise ConvoError("BAD_SCOPE",
                             f"scope must be a list of resource tags or None, "
                             f"got {type(scope).__name__}: {scope!r}")
        scope = _str_list(scope, "scope", "BAD_SCOPE")
        if not isinstance(title, str) or not title.strip():
            raise ConvoError("BAD_TURN", "title must be a non-empty string")
        if owner is not None and not isinstance(owner, str):
            raise ConvoError("BAD_TURN",
                             f"owner must be a principal string or None, got "
                             f"{type(owner).__name__}: {owner!r}")
        sid = uuid.uuid4().hex
        self._ledger.append(EV_OPENED, {
            "sid": sid, "title": title, "scope": scope, "owner": owner,
            "opened_epoch": self._clock(),
        })
        return sid

    def assert_owner(self, sid: str, owner: Optional[str]) -> None:
        """Refuse unless sid exists AND its recorded owner equals `owner`.
        A mismatch raises NO_SESSION with the SAME detail as an unknown sid -
        existence is never leaked to a principal the session does not belong
        to. (Sessions created with owner=None are owned by the None principal:
        an explicit principal does NOT match them, and vice versa.)"""
        s = self._project().get(sid)
        if s is None or s.get("owner") != owner:
            raise ConvoError("NO_SESSION", f"unknown sid {sid!r}")

    def append_turn(self, sid: str, role: str, text: str, mode: str = "text",
                    sources: Optional[list] = None,
                    job_ids: Optional[list] = None) -> int:
        # Cheap shape checks BEFORE touching the chain - a refused turn
        # appends nothing.
        if role not in ROLES:
            raise ConvoError("BAD_ROLE",
                             f"role {role!r} not in {ROLES}")
        if not isinstance(text, str) or not text.strip():
            raise ConvoError("BAD_TURN", "empty text is not a turn")
        if not isinstance(mode, str) or not mode.strip():
            raise ConvoError("BAD_TURN", "mode must be a non-empty string")
        sources = _str_list(sources, "sources", "BAD_TURN")
        job_ids = _str_list(job_ids, "job_ids", "BAD_TURN")

        result = {}

        def decide(records):
            # Atomic read-decide-append under the ledger's OS lock: the
            # session's existence, openness and NEXT TURN SEQ are all judged
            # against the REAL head, not a remembered projection.
            sessions = self._project(records)
            s = sessions.get(sid)
            if s is None:
                raise ConvoError("NO_SESSION", f"unknown sid {sid!r}")
            if not s["open"]:
                raise ConvoError("BAD_TURN",
                                 f"session {sid} is CLOSED - reopen_session() "
                                 f"first; turns are never silently resurrected")
            seq = len(s["turns"]) + 1
            result["seq"] = seq
            return (EV_TURN, {"sid": sid, "role": role, "text": text,
                              "mode": mode, "sources": sources,
                              "job_ids": job_ids, "seq": seq})

        self._ledger.append_guarded(decide)
        return result["seq"]

    def get_session(self, sid: str) -> dict:
        s = self._project().get(sid)
        if s is None:
            raise ConvoError("NO_SESSION", f"unknown sid {sid!r}")
        return {
            "sid": s["sid"], "title": s["title"], "scope": list(s["scope"]),
            "owner": s.get("owner"),
            "open": s["open"], "turns": [dict(t) for t in s["turns"]],
            "sources": _dedup(x for t in s["turns"] for x in t["sources"]),
            "job_ids": _dedup(x for t in s["turns"] for x in t["job_ids"]),
            "turn_count": len(s["turns"]),
        }

    def list_sessions(self) -> list:
        rows = [{"sid": s["sid"], "title": s["title"],
                 "turn_count": len(s["turns"]), "open": s["open"],
                 "last_epoch": s["last_epoch"]}
                for s in self._project().values()]
        rows.sort(key=lambda r: r["last_epoch"], reverse=True)
        return rows

    def close_session(self, sid: str) -> None:
        def decide(records):
            sessions = self._project(records)
            s = sessions.get(sid)
            if s is None:
                raise ConvoError("NO_SESSION", f"unknown sid {sid!r}")
            if not s["open"]:
                raise ConvoError("BAD_TURN", f"session {sid} is already closed")
            return (EV_CLOSED, {"sid": sid, "closed_epoch": self._clock()})

        self._ledger.append_guarded(decide)

    def reopen_session(self, sid: str) -> None:
        """The explicit road back: CONVO_REOPENED is an EVENT, so the history
        says when the conversation resumed instead of pretending it never
        closed."""
        def decide(records):
            sessions = self._project(records)
            s = sessions.get(sid)
            if s is None:
                raise ConvoError("NO_SESSION", f"unknown sid {sid!r}")
            if s["open"]:
                raise ConvoError("BAD_TURN", f"session {sid} is already open")
            return (EV_REOPENED, {"sid": sid, "reopened_epoch": self._clock()})

        self._ledger.append_guarded(decide)
