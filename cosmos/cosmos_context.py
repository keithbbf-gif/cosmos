#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_context - SESSION CONTEXT MANIFESTS (F5 builder). OA's adopted stage 5
mechanism: carry-over made structural. A session opens against the ledger, accumulates
facts/watchers/leases, and CANNOT close cleanly without a manifest naming what it hands
off. Closure without a valid manifest is an OPEN_CONTEXT incident - recorded, loud,
and visible to the next boot. "The system forgetting" becomes a detectable bug.
"""
from __future__ import annotations

import time
from typing import Optional

from cosmos_ledger import Ledger


class ContextError(RuntimeError):
    """kind in {NOT_OPEN, ALREADY_CLOSED, UNRESOLVED}."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


class Session:
    def __init__(self, ledger: Ledger, session_id: str, stream: str,
                 clock=time.time):
        self.ledger = ledger
        self.sid = session_id
        self._clock = clock
        self._open = True
        self._facts: dict[str, str] = {}
        self._watchers: dict[str, str] = {}      # watcher_id -> what it awaits
        self.ledger.append("SESSION_OPENED", {"sid": session_id, "stream": stream})

    def record_fact(self, key: str, value: str) -> None:
        if not self._open:
            raise ContextError("ALREADY_CLOSED", self.sid)
        self._facts[key] = value
        self.ledger.append("FACT_RECORDED", {"sid": self.sid, "key": key,
                                             "value": value[:500]})

    def open_watcher(self, watcher_id: str, awaits: str) -> None:
        self._watchers[watcher_id] = awaits
        self.ledger.append("WATCHER_OPENED", {"sid": self.sid, "wid": watcher_id,
                                              "awaits": awaits})

    def resolve_watcher(self, watcher_id: str, outcome: str) -> None:
        if watcher_id not in self._watchers:
            raise ContextError("NOT_OPEN", f"watcher {watcher_id} is not open")
        del self._watchers[watcher_id]
        self.ledger.append("WATCHER_RESOLVED", {"sid": self.sid, "wid": watcher_id,
                                                "outcome": outcome})

    def close(self, handoff_to: str, force: bool = False) -> dict:
        """A clean close REQUIRES nothing unresolved - or an explicit force, which is
        not a bypass: it records OPEN_CONTEXT with the full unresolved list, so the
        forgetting is a NAMED INCIDENT the next boot reads, never a silence."""
        if not self._open:
            raise ContextError("ALREADY_CLOSED", self.sid)
        manifest = {"sid": self.sid, "handoff_to": handoff_to,
                    "facts": dict(self._facts),
                    "unresolved_watchers": dict(self._watchers)}
        if self._watchers and not force:
            raise ContextError(
                "UNRESOLVED",
                f"{len(self._watchers)} watcher(s) still open ({list(self._watchers)}) - "
                f"a session that closes over an open watcher is how a paid return lands "
                f"with nobody watching (S-121). Resolve them or close(force=True) to "
                f"record the incident.")
        self._open = False
        if self._watchers:
            self.ledger.append("OPEN_CONTEXT",
                               {"sid": self.sid, "handoff_to": handoff_to,
                                "unresolved": dict(self._watchers),
                                "detail": "forced close with unresolved watchers - "
                                          "the next boot MUST read this"})
        self.ledger.append("SESSION_CLOSED", manifest)
        return manifest


def boot_inherit(ledger: Ledger) -> dict:
    """What the next session MUST know: last manifest's facts + every OPEN_CONTEXT
    incident since. Reading this at boot is what makes carry-over a mechanism."""
    def fold(s, rec):
        e, p = rec["event"], rec["payload"]
        if e == "SESSION_CLOSED":
            s["facts"].update(p.get("facts", {}))
            s["last_handoff"] = p.get("handoff_to")
        elif e == "OPEN_CONTEXT":
            s["incidents"].append({"sid": p["sid"], "unresolved": p["unresolved"]})
        elif e == "WATCHER_RESOLVED":
            s["incidents"] = [i for i in s["incidents"]
                              if p["wid"] not in i["unresolved"]]
        return s
    return ledger.project(fold, {"facts": {}, "incidents": [], "last_handoff": None})
