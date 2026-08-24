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
    CONVO_OPENED   {sid, title, scope, opened_epoch}
    CONVO_TURN     {sid, role, text, mode, sources, job_ids, seq}
    CONVO_CLOSED   {sid, closed_epoch}
    CONVO_REOPENED {sid, reopened_epoch}

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
        ev, p = rec.get("event"), rec.get("payload", {})
        if ev == EV_OPENED:
            sessions[p["sid"]] = {
                "sid": p["sid"], "title": p["title"],
                "scope": list(p.get("scope") or []),
                "open": True, "turns": [],
                "last_epoch": p.get("opened_epoch", rec.get("t")),
            }
        elif ev == EV_TURN and p.get("sid") in sessions:
            s = sessions[p["sid"]]
            s["turns"].append({
                "role": p["role"], "text": p["text"], "mode": p["mode"],
                "sources": list(p.get("sources") or []),
                "job_ids": list(p.get("job_ids") or []),
                "epoch": rec.get("t"),
            })
            s["last_epoch"] = rec.get("t")
        elif ev == EV_CLOSED and p.get("sid") in sessions:
            sessions[p["sid"]]["open"] = False
            sessions[p["sid"]]["last_epoch"] = p.get("closed_epoch", rec.get("t"))
        elif ev == EV_REOPENED and p.get("sid") in sessions:
            sessions[p["sid"]]["open"] = True
            sessions[p["sid"]]["last_epoch"] = p.get("reopened_epoch", rec.get("t"))
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
    def create_session(self, title: str, scope: Optional[list] = None) -> str:
        if scope is not None and not isinstance(scope, list):
            raise ConvoError("BAD_SCOPE",
                             f"scope must be a list of resource tags or None, "
                             f"got {type(scope).__name__}: {scope!r}")
        scope = _str_list(scope, "scope", "BAD_SCOPE")
        if not isinstance(title, str) or not title.strip():
            raise ConvoError("BAD_TURN", "title must be a non-empty string")
        sid = uuid.uuid4().hex
        self._ledger.append(EV_OPENED, {
            "sid": sid, "title": title, "scope": scope,
            "opened_epoch": self._clock(),
        })
        return sid

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
