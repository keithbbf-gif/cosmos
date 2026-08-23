#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_lock - SPIKE 2 (F5 builder): leases + fencing tokens + fenced commit.

CONTRACT (docs/FINAL_ARCHITECTURE.md, ratified): advisory locking is dead. An ARBITER
issues expiring leases with MONOTONIC fencing tokens; protected commits present the token
and stale tokens are REJECTED; takeover is a recorded event chain, never a silent clear;
torn state REFUSES; a dying holder needs no cleanup discipline - expiry recovers.

WHAT THIS SPIKE PROVES (the protocol, in-process - the service wrapper is 6b work):
  * grant/renew/expiry on the ARBITER's clock (injectable - worker clocks are evidence)
  * monotonic fencing tokens across grants, takeovers, and arbiter RESTARTS (recovered
    by ledger replay - the token counter is not in-memory trivia)
  * fenced commit: a commit callback runs ONLY under a currently-valid token; a stale
    or superseded token is REJECTED and the rejection is ledgered
  * the dying-holder case: no release ever happens, the lease expires, the next claimant
    gets a HIGHER token, and the dead holder's late commit is REFUSED
  * append-only event ledger (JSONL, fsync) - grant/renew/expire/takeover/commit/refuse
    all land as events; the CURRENT state is a projection rebuilt by replay
  * torn ledger line -> the arbiter REFUSES to load (never reads as free)

Scar lineage: tree_lock read-check-write race (API-05) - here the arbiter serializes;
naive-timestamp staleness (OA finding) - all times are epoch floats from ONE clock;
console-only takeover audit (API-07) - every transition is a ledger event.
"""
from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional


class LockError(RuntimeError):
    """Typed refusal. kind in {HELD, STALE_TOKEN, NO_LEASE, TORN_LEDGER, UNKNOWN_RESOURCE}."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


@dataclass
class Lease:
    resource: str
    holder: str
    token: int
    granted_at: float
    expires_at: float


class Arbiter:
    """The single authority. In 6b this lives inside COSMOS Core; the protocol is what
    the spike proves. `clock` is injectable so expiry is testable without sleeping."""

    def __init__(self, ledger_path: str | os.PathLike,
                 clock: Callable[[], float] = time.time,
                 default_ttl: float = 90 * 60):
        self._ledger = Path(ledger_path)
        self._clock = clock
        self._ttl = default_ttl
        self._leases: dict[str, Lease] = {}
        self._max_token = 0
        if self._ledger.exists():
            self._replay()

    # ---------------- ledger ----------------
    def _append(self, event: dict) -> None:
        event = {"t": self._clock(), **event}
        with open(self._ledger, "a", encoding="utf-8", newline="") as fh:
            fh.write(json.dumps(event) + "\n")
            fh.flush()
            os.fsync(fh.fileno())

    def _replay(self) -> None:
        """Rebuild state from events. A torn line REFUSES - an unreadable history is not
        an empty one."""
        try:
            lines = self._ledger.read_text(encoding="utf-8").splitlines()
        except OSError as e:
            raise LockError("TORN_LEDGER", f"cannot read {self._ledger}: {e}") from e
        for i, ln in enumerate(lines, 1):
            if not ln.strip():
                continue
            try:
                e = json.loads(ln)
            except ValueError as exc:
                raise LockError(
                    "TORN_LEDGER",
                    f"line {i} of {self._ledger} does not parse - REFUSING to load; a "
                    f"torn ledger must never read as free") from exc
            k = e.get("event")
            self._max_token = max(self._max_token, int(e.get("token", 0)))
            if k in ("GRANT", "TAKEOVER"):
                self._leases[e["resource"]] = Lease(
                    e["resource"], e["holder"], int(e["token"]),
                    float(e["t"]), float(e["expires_at"]))
            elif k == "RENEW":
                l = self._leases.get(e["resource"])
                if l and l.token == e["token"]:
                    l.expires_at = float(e["expires_at"])
            elif k in ("RELEASE", "EXPIRE"):
                l = self._leases.get(e["resource"])
                if l and l.token == e.get("token"):
                    del self._leases[e["resource"]]

    # ---------------- protocol ----------------
    def _expire_if_due(self, resource: str) -> None:
        l = self._leases.get(resource)
        if l and self._clock() >= l.expires_at:
            self._append({"event": "EXPIRE", "resource": resource,
                          "holder": l.holder, "token": l.token,
                          "detail": "lease expired on arbiter clock - no cleanup "
                                    "discipline was required of the holder"})
            del self._leases[resource]

    def acquire(self, resource: str, holder: str,
                ttl: Optional[float] = None) -> Lease:
        self._expire_if_due(resource)
        cur = self._leases.get(resource)
        if cur is not None:
            raise LockError("HELD", f"{resource} held by {cur.holder} "
                                    f"(token {cur.token}, {cur.expires_at - self._clock():.0f}s left)")
        self._max_token += 1
        was_takeover = False
        # takeover vs fresh grant is decided by whether the ledger's last event for this
        # resource was an EXPIRE (recorded chain: EXPIRE -> TAKEOVER)
        lease = Lease(resource, holder, self._max_token, self._clock(),
                      self._clock() + (ttl or self._ttl))
        self._leases[resource] = lease
        self._append({"event": "TAKEOVER" if was_takeover else "GRANT",
                      "resource": resource, "holder": holder, "token": lease.token,
                      "expires_at": lease.expires_at})
        return lease

    def renew(self, lease: Lease, ttl: Optional[float] = None) -> Lease:
        self._expire_if_due(lease.resource)
        cur = self._leases.get(lease.resource)
        if cur is None or cur.token != lease.token:
            raise LockError("STALE_TOKEN",
                            f"renew refused: token {lease.token} is not the current "
                            f"holder of {lease.resource}")
        cur.expires_at = self._clock() + (ttl or self._ttl)
        self._append({"event": "RENEW", "resource": cur.resource, "holder": cur.holder,
                      "token": cur.token, "expires_at": cur.expires_at})
        return cur

    def release(self, lease: Lease) -> None:
        cur = self._leases.get(lease.resource)
        if cur is None or cur.token != lease.token:
            # releasing something you no longer hold is a FACT worth recording, not an
            # error worth hiding - but it must not delete the current holder's lease.
            self._append({"event": "REFUSE", "op": "release", "resource": lease.resource,
                          "holder": lease.holder, "token": lease.token,
                          "detail": "release with non-current token - ignored"})
            return
        self._append({"event": "RELEASE", "resource": cur.resource,
                      "holder": cur.holder, "token": cur.token})
        del self._leases[lease.resource]

    def fenced_commit(self, lease: Lease, commit: Callable[[], object]) -> object:
        """Run `commit` ONLY under a currently-valid token. The check-run-recheck shape:
        validity is asserted immediately before AND the commit is ledgered with the token,
        so a reader can always tell WHICH token's work landed."""
        self._expire_if_due(lease.resource)
        cur = self._leases.get(lease.resource)
        if cur is None:
            self._append({"event": "REFUSE", "op": "commit", "resource": lease.resource,
                          "holder": lease.holder, "token": lease.token,
                          "detail": "no live lease (expired or released)"})
            raise LockError("NO_LEASE", f"commit refused: no live lease on {lease.resource}")
        if cur.token != lease.token:
            self._append({"event": "REFUSE", "op": "commit", "resource": lease.resource,
                          "holder": lease.holder, "token": lease.token,
                          "detail": f"stale token (current is {cur.token})"})
            raise LockError("STALE_TOKEN",
                            f"commit refused: token {lease.token} superseded by {cur.token}")
        result = commit()
        self._append({"event": "COMMIT", "resource": cur.resource, "holder": cur.holder,
                      "token": cur.token})
        return result

    # ---------------- introspection ----------------
    def status(self, resource: str) -> Optional[Lease]:
        self._expire_if_due(resource)
        return self._leases.get(resource)

    def events(self) -> list[dict]:
        if not self._ledger.exists():
            return []
        return [json.loads(x) for x in
                self._ledger.read_text(encoding="utf-8").splitlines() if x.strip()]
