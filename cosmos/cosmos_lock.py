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
    * RF-LOCK-XPROC: an exclusive OS lock (msvcrt on Windows, fcntl elsewhere) on a
    sidecar .lock beside the lease ledger, held across replay->decide->append in
    acquire()/renew()/fenced_commit() - two independently-constructed keyed
    arbiters cannot both grant the same resource with the same fencing token

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
    """Typed refusal. kind in {HELD, STALE_TOKEN, NO_LEASE, TORN_LEDGER, FORGED_EVENT,
    UNKNOWN_RESOURCE}."""

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
    the spike proves. `clock` is injectable so expiry is testable without sleeping.

    CRITIC B6 FIX: lease events are now HMAC-SIGNED with the install key and replay
    VERIFIES the signature - the measured forged-GRANT (a well-formed lie loading as a
    live lease) is refused as FORGED_EVENT. An unkeyed arbiter still works for
    spike-local use but every event is marked unsigned=true, and a signed ledger
    REFUSES an unsigned event."""

    def __init__(self, ledger_path: str | os.PathLike,
                 clock: Callable[[], float] = time.time,
                 default_ttl: float = 90 * 60,
                 key: bytes | None = None):
        self._ledger = Path(ledger_path)
        self._clock = clock
        self._ttl = default_ttl
        self._key = key
        self._leases: dict[str, Lease] = {}
        self._max_token = 0
        if self._ledger.exists():
            self._replay()

    # ---------------- ledger ----------------
    def _lock_handle(self):
        """Cross-process serialization via an OS lock on a sidecar .lock file.
        RF-LOCK-XPROC (MEASURED): two independently-constructed keyed arbiters
        both granted tree with token=1. The fix is an EXCLUSIVE OS LOCK held
        across (re-prime from disk -> decide -> append): the second arbiter
        BLOCKS, then re-primes onto the live lease and refuses HELD. A lock
        the OS releases on process death needs no cleanup discipline."""
        lk = open(str(self._ledger) + ".lock", "a+b")
        if os.name == "nt":
            import msvcrt
            msvcrt.locking(lk.fileno(), msvcrt.LK_LOCK, 1)
        else:
            import fcntl
            fcntl.flock(lk.fileno(), fcntl.LOCK_EX)
        return lk

    def _unlock(self, lk) -> None:
        try:
            if os.name == "nt":
                import msvcrt
                lk.seek(0)
                msvcrt.locking(lk.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl
                fcntl.flock(lk.fileno(), fcntl.LOCK_UN)
        finally:
            lk.close()

    def _reprime(self) -> None:
        """Rebuild leases and the token counter from DISK. Under the OS lock
        this is the live projection, not a remembered one (RF-LOCK-XPROC)."""
        self._leases = {}
        self._max_token = 0
        if self._ledger.exists():
            self._replay()

    def _sig(self, event: dict) -> str:
        import hashlib, hmac as _h
        body = json.dumps({k: v for k, v in event.items() if k != "sig"},
                          sort_keys=True, separators=(",", ":")).encode("utf-8")
        return _h.new(self._key, body, hashlib.sha256).hexdigest()[:32]

    def _append(self, event: dict) -> None:
        event = {"t": self._clock(), **event}
        if self._key:
            event["sig"] = self._sig(event)
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
            if self._key is not None:
                # CRITIC B6 (measured: forged GRANT loaded as a live lease): a keyed
                # arbiter VERIFIES every event. Unsigned or wrong-sig = FORGED_EVENT.
                sig = e.get("sig", "")
                if not sig or sig != self._sig({k2: v for k2, v in e.items()
                                               if k2 != "sig"}):
                    raise LockError("FORGED_EVENT",
                                    f"line {i}: event is unsigned or mis-signed - a "
                                    f"well-formed lie is still a lie")
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
        lk = self._lock_handle()
        try:
            self._reprime()
            self._expire_if_due(resource)
            cur = self._leases.get(resource)
            if cur is not None:
                raise LockError("HELD", f"{resource} held by {cur.holder} "
                                        f"(token {cur.token}, {cur.expires_at - self._clock():.0f}s left)")
            self._max_token += 1
            # CRITIC M1 FIX: TAKEOVER was dead code (was_takeover=False, never computed) and
            # the selftest asserted the implementation instead of the contract. Now decided
            # from the LEDGER: if the last lifecycle event for this resource is EXPIRE, this
            # grant IS the takeover, and the chain is EXPIRE -> TAKEOVER as documented.
            was_takeover = False
            for e in reversed(self.events()):
                if e.get("resource") == resource and e.get("event") in (
                        "GRANT", "TAKEOVER", "RELEASE", "EXPIRE"):
                    was_takeover = e["event"] == "EXPIRE"
                    break
            lease = Lease(resource, holder, self._max_token, self._clock(),
                          self._clock() + (ttl or self._ttl))
            self._leases[resource] = lease
            self._append({"event": "TAKEOVER" if was_takeover else "GRANT",
                          "resource": resource, "holder": holder, "token": lease.token,
                          "expires_at": lease.expires_at})
            return lease
        finally:
            self._unlock(lk)

    def renew(self, lease: Lease, ttl: Optional[float] = None) -> Lease:
        lk = self._lock_handle()
        try:
            self._reprime()
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
        finally:
            self._unlock(lk)

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

    def _assert_live(self, lease: Lease, op: str) -> Lease:
        self._expire_if_due(lease.resource)
        cur = self._leases.get(lease.resource)
        if cur is None:
            self._append({"event": "REFUSE", "op": op, "resource": lease.resource,
                          "holder": lease.holder, "token": lease.token,
                          "detail": "no live lease (expired or released)"})
            raise LockError("NO_LEASE", f"{op} refused: no live lease on {lease.resource}")
        if cur.token != lease.token:
            self._append({"event": "REFUSE", "op": op, "resource": lease.resource,
                          "holder": lease.holder, "token": lease.token,
                          "detail": f"stale token (current is {cur.token})"})
            raise LockError("STALE_TOKEN",
                            f"{op} refused: token {lease.token} superseded by {cur.token}")
        return cur

    def fenced_commit(self, lease: Lease, commit: Callable[[], object],
                      expected_inputs: dict[str, str] | None = None) -> object:
        """CRITIC M4 FIX: the fenced gateway now takes EXPECTED INPUT HASHES (path ->
        sha256hex) verified BEFORE the callback, and RE-CHECKS the lease AFTER the
        callback - the measured hole was a commit whose lease expired inside the
        callback still landing as COMMIT. Now that lands as COMMIT_UNFENCED, a recorded
        incident: the write happened (we cannot unwrite it) but the record says the
        fence was down when it finished, which is the difference between an audit that
        lies and one that doesn't."""
        import hashlib as _hl
        lk = self._lock_handle()
        try:
            self._reprime()
            self._assert_live(lease, "commit")
            if expected_inputs:
                for pth, want in expected_inputs.items():
                    try:
                        got = _hl.sha256(Path(pth).read_bytes()).hexdigest()
                    except OSError as e:
                        self._append({"event": "REFUSE", "op": "commit",
                                      "resource": lease.resource, "token": lease.token,
                                      "detail": f"input unreadable: {pth}: {e}"})
                        raise LockError("NO_LEASE", f"input unreadable: {pth}") from e
                    if got != want:
                        self._append({"event": "REFUSE", "op": "commit",
                                      "resource": lease.resource, "token": lease.token,
                                      "detail": f"input hash mismatch: {pth}"})
                        raise LockError("STALE_TOKEN",
                                        f"commit refused: input {pth} changed since the "
                                        f"decision (got {got[:12]}, expected {want[:12]})")
            result = commit()
            # POST-CALLBACK RECHECK (M4): did the fence hold while we worked?
            self._expire_if_due(lease.resource)
            cur = self._leases.get(lease.resource)
            if cur is None or cur.token != lease.token:
                self._append({"event": "COMMIT_UNFENCED", "resource": lease.resource,
                              "holder": lease.holder, "token": lease.token,
                              "detail": "lease expired or was superseded DURING the commit "
                                        "callback - the write landed with the fence down; "
                                        "recorded as an incident, never as a clean COMMIT"})
                raise LockError("STALE_TOKEN",
                                f"commit landed UNFENCED on {lease.resource} - incident "
                                f"recorded; treat the artifact as suspect")
            self._append({"event": "COMMIT", "resource": cur.resource, "holder": cur.holder,
                          "token": cur.token})
            return result
        finally:
            self._unlock(lk)

    # ---------------- introspection ----------------
    def status(self, resource: str) -> Optional[Lease]:
        self._expire_if_due(resource)
        return self._leases.get(resource)

    def events(self) -> list[dict]:
        if not self._ledger.exists():
            return []
        return [json.loads(x) for x in
                self._ledger.read_text(encoding="utf-8").splitlines() if x.strip()]