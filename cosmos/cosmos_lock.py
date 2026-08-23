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
    * RF-LOCK-LIVENESS (four-phase fenced commit): the OS mutex is NEVER held
    across the commit callback. Phase A reserves under the lock (COMMIT_RESERVED),
    Phase B stages the artifact UNLOCKED with the fencing token in hand, Phase C
    retakes the lock briefly, CASes the token against the live projection, and
    only then os.replace()s the staged file (COMMIT) - or REFUSES the install
    (COMMIT_REFUSED) so a stale write never lands. See fenced_commit().
    * RF-LOCK-XPROC: an exclusive OS lock on a sidecar .lock beside the lease
    ledger, held across reprime->decide->append in acquire()/renew()/release()
    and across each SHORT phase (A and C) of fenced_commit() - never across the
    callback. fcntl.flock is a whole-file lock; msvcrt.locking is NOT -
    it locks nbytes at the current CRT file position and raises on contention.
    The sidecar therefore always seek(0)s and locks a fixed byte range so both
    backends are a true mutex. Two independently-constructed keyed arbiters
    cannot both grant the same resource with the same fencing token

Scar lineage: tree_lock read-check-write race (API-05) - here the arbiter serializes;
naive-timestamp staleness (OA finding) - all times are epoch floats from ONE clock;
console-only takeover audit (API-07) - every transition is a ledger event.
"""
from __future__ import annotations

import errno
import json
import os
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

# msvcrt.locking(fd, mode, nbytes) locks nbytes at the CURRENT CRT file
# position. It is not fcntl.flock (whole-file, blocking, position-blind).
# Lock AND unlock must use this same offset-0 range or Windows silently
# unlocks a different byte than the one it locked.
LOCK_REGION = 1
LOCK_POLL = 0.01
# None = auto (msvcrt on Windows, fcntl elsewhere). Tests on Linux set
# this to "msvcrt" so the native-Windows branch runs without patching
# os.name (which makes pathlib instantiate WindowsPath and lie about
# exists() on POSIX).
LOCK_BACKEND: str | None = None


def _use_msvcrt() -> bool:
    if LOCK_BACKEND is not None:
        return LOCK_BACKEND == "msvcrt"
    return os.name == "nt"


def sidecar_lock_path(ledger_path: str | os.PathLike) -> Path:
    """The mutex file that sits beside the lease ledger (`<ledger>.lock`)."""
    return Path(str(ledger_path) + ".lock")


class LockError(RuntimeError):
    """Typed refusal. kind in {HELD, STALE_TOKEN, NO_LEASE, TORN_LEDGER, FORGED_EVENT,
    UNKNOWN_RESOURCE, REENTRANT, BAD_STAGE}."""

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


@dataclass
class StagedArtifact:
    """Phase B output of the four-phase fenced commit: a fully-written staging
    file awaiting the fenced install. `src` is the staged temp file (SAME volume
    as `dst` - os.replace must stay atomic); `dst` is the final target. The
    arbiter performs os.replace(src, dst) ONLY after re-verifying, under the OS
    lock, that the presented fencing token is still current (Phase C). `result`
    is what fenced_commit returns on success (defaults to `dst`)."""
    src: str | os.PathLike
    dst: str | os.PathLike
    result: object = None


def _accepts_token(stage: Callable) -> bool:
    """True if the callable can take the fencing token as one positional arg.
    Legacy 0-arg commit callables are still called bare - their side effects run
    unfenced in Phase B and land as COMMIT_UNFENCED if the fence drops, exactly
    the pre-redesign M4 semantics."""
    try:
        import inspect
        sig = inspect.signature(stage)
    except (TypeError, ValueError):
        return True
    for p in sig.parameters.values():
        if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD, p.VAR_POSITIONAL):
            return True
    return False


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
        # Four-phase fenced commit: per-resource in-flight flags (this instance
        # only). Not a mutex - the OS sidecar lock is the mutex - just the typed
        # reentrancy guard for a callback that calls back into fenced_commit for
        # the SAME resource while its own commit is between Phase A and Phase C.
        self._inflight: set[str] = set()
        self._inflight_mu = threading.Lock()
        # last lifecycle event (GRANT/TAKEOVER/RELEASE/EXPIRE) per resource,
        # rebuilt by replay UNDER THE LOCK - acquire()'s takeover decision reads
        # this instead of re-reading the JSONL through events() (which skipped
        # signature verification and raised untyped on a torn line).
        self._last_lifecycle: dict[str, str] = {}
        if self._ledger.exists():
            self._replay()

    # ---------------- ledger ----------------
    def _lock_handle(self):
        """Cross-process serialization via an OS lock on a sidecar .lock file.
        RF-LOCK-XPROC (MEASURED): two independently-constructed keyed arbiters
        both granted tree with token=1. The fix is an EXCLUSIVE OS LOCK held
        across (re-prime from disk -> decide -> append): the second arbiter
        BLOCKS, then re-primes onto the live lease and refuses HELD. A lock
        the OS releases on process death needs no cleanup discipline.

        Native Windows (T1): `open(..., "a+b"); msvcrt.locking(fd, LK_LOCK, 1)`
        is NOT a whole-file mutex. msvcrt locks 1 byte at the CRT file
        position (append mode leaves that at EOF; Python seek() may not
        move the CRT pointer). We open O_RDWR|O_CREAT (never truncate,
        never append-position), write a real LOCK_REGION so the range
        exists, os.lseek(0) so CRT and Python agree, and lock that same
        range on unlock. LK_NBLCK raises on contention (unlike flock),
        so a retry loop provides the blocking acquire flock gives us."""
        path = sidecar_lock_path(self._ledger)
        flags = os.O_RDWR | os.O_CREAT
        if hasattr(os, "O_BINARY"):
            flags |= os.O_BINARY
        if hasattr(os, "O_CLOEXEC"):
            flags |= os.O_CLOEXEC
        fd = os.open(str(path), flags, 0o666)
        lk = os.fdopen(fd, "r+b", buffering=0)
        try:
            self._ensure_lock_region(lk)
            self._os_lock(lk)
            return lk
        except Exception:
            lk.close()
            raise

    def _ensure_lock_region(self, lk) -> None:
        """Guarantee LOCK_REGION real bytes. msvcrt cannot treat '1 byte
        past EOF of a 0-length file' as a whole-file exclusive lock."""
        lk.seek(0, os.SEEK_END)
        have = lk.tell()
        if have < LOCK_REGION:
            lk.write(b"\x00" * (LOCK_REGION - have))
            lk.flush()

    def _lock_region_at_zero(self, lk) -> None:
        """Put the CRT *and* Python file position on byte 0 of the sidecar.
        msvcrt.locking reads the CRT pointer, not lk.tell()."""
        lk.flush()
        os.lseek(lk.fileno(), 0, os.SEEK_SET)

    def _os_lock(self, lk) -> None:
        """Acquire the fixed offset-0 region. Blocks until it is ours."""
        if _use_msvcrt():
            import msvcrt
            # LK_LOCK internally retries ~10s then raises; LK_NBLCK raises
            # immediately. Either way msvcrt does NOT block like flock.
            # Spin until the holder (briefly inside a locked phase) drops it.
            while True:
                self._lock_region_at_zero(lk)
                try:
                    msvcrt.locking(lk.fileno(), msvcrt.LK_NBLCK, LOCK_REGION)
                    return
                except OSError as e:
                    # Contention is EACCES (Windows _locking) / EDEADLK.
                    # EBADF/EINVAL is a programming error — do not spin.
                    if e.errno in (errno.EBADF, errno.EINVAL):
                        raise
                    time.sleep(LOCK_POLL)
        else:
            import fcntl
            fcntl.flock(lk.fileno(), fcntl.LOCK_EX)

    def _unlock(self, lk) -> None:
        try:
            if _use_msvcrt():
                import msvcrt
                self._lock_region_at_zero(lk)
                msvcrt.locking(lk.fileno(), msvcrt.LK_UNLCK, LOCK_REGION)
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
        self._last_lifecycle = {}
        if self._ledger.exists():
            self._replay()

    def _sig(self, event: dict) -> str:
        # FULL hexdigest (256-bit). The old [:32] truncation halved the MAC for
        # no benefit; legacy 32-hex signatures are still ACCEPTED on verify
        # (128-bit HMAC-SHA256 is not forgeable either) so existing ledgers load.
        import hashlib, hmac as _h
        body = json.dumps({k: v for k, v in event.items() if k != "sig"},
                          sort_keys=True, separators=(",", ":")).encode("utf-8")
        return _h.new(self._key, body, hashlib.sha256).hexdigest()

    def _verify_sig(self, e: dict, i: int) -> None:
        """CRITIC B6: a keyed arbiter VERIFIES every event it reads back.
        Unsigned or mis-signed = FORGED_EVENT. compare_digest, not ==."""
        import hmac as _h
        sig = e.get("sig", "")
        want = self._sig({k2: v for k2, v in e.items() if k2 != "sig"})
        ok = bool(sig) and (_h.compare_digest(sig, want)
                            or (len(sig) == 32           # legacy truncated MAC
                                and _h.compare_digest(sig, want[:32])))
        if not ok:
            raise LockError("FORGED_EVENT",
                            f"line {i}: event is unsigned or mis-signed - a "
                            f"well-formed lie is still a lie")

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
                self._verify_sig(e, i)
            k = e.get("event")
            self._max_token = max(self._max_token, int(e.get("token", 0)))
            if k in ("GRANT", "TAKEOVER", "RELEASE", "EXPIRE"):
                self._last_lifecycle[e["resource"]] = k
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
            self._last_lifecycle[resource] = "EXPIRE"

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
            # the selftest asserted the implementation instead of the contract. Decided
            # from the LEDGER: if the last lifecycle event for this resource is EXPIRE, this
            # grant IS the takeover, and the chain is EXPIRE -> TAKEOVER as documented.
            # FINDING #3 FIX: the decision now reads the LOCKED reprime's projection
            # (_last_lifecycle, rebuilt by _replay and updated by _expire_if_due) instead
            # of a second raw events() pass over the live JSONL - one locked read, one
            # decision, one append; a torn or forged line already refused during reprime.
            was_takeover = self._last_lifecycle.get(resource) == "EXPIRE"
            lease = Lease(resource, holder, self._max_token, self._clock(),
                          self._clock() + (ttl or self._ttl))
            self._leases[resource] = lease
            kind = "TAKEOVER" if was_takeover else "GRANT"
            self._append({"event": kind,
                          "resource": resource, "holder": holder, "token": lease.token,
                          "expires_at": lease.expires_at})
            self._last_lifecycle[resource] = kind
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
        # FINDING #1 FIX (was CRITICAL): release appended RELEASE/REFUSE and mutated
        # _leases with NO OS lock and NO reprime - it could interleave its JSONL line
        # with a locked acquire/renew/fenced_commit append and decide from stale
        # in-process state. Same discipline as acquire(): lock -> reprime -> decide
        # -> append -> memory update.
        lk = self._lock_handle()
        try:
            self._reprime()
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
            self._last_lifecycle[lease.resource] = "RELEASE"
        finally:
            self._unlock(lk)

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

    def fenced_commit(self, lease: Lease,
                      stage: Callable[..., object],
                      expected_inputs: dict[str, str] | None = None) -> object:
        """FOUR-PHASE FENCED COMMIT (RF-LOCK-LIVENESS - the unanimous Gemini/OpenAI/
        Grok redesign). The old shape held the sidecar OS mutex ACROSS the arbitrary
        callback: a slow or hung callback blocked every acquire/renew/release/commit
        on the ledger, lease expiry could not recover a live-but-stuck holder, and a
        callback that re-entered the arbiter self-deadlocked. Fencing tokens exist so
        you do NOT hold a lock across the work - and the real fence must be enforced
        at the RESOURCE at install time, not rechecked after the write already landed.

        PHASE A (locked, short): reprime -> expire-if-due -> _assert_live -> verify
          expected_inputs hashes (path -> sha256hex, the M4 fence on decision inputs)
          -> append COMMIT_RESERVED (resource/holder/token) -> RELEASE the OS lock.
        PHASE B (NO arbiter mutex held): run `stage`. Its job is to STAGE an artifact
          (write a temp/.part file), NOT to publish it. It RECEIVES the fencing token
          and returns a StagedArtifact(src, dst[, result]).
        PHASE C (locked, short): retake the lock -> reprime -> COMPARE-AND-SWAP: the
          presented token must STILL be the current token for the resource. ONLY THEN
          os.replace(src, dst) - an O(1) atomic install - and append COMMIT. If the
          token was superseded during Phase B (takeover/expiry), the install is
          REFUSED: no os.replace, the staged file is discarded, COMMIT_REFUSED is
          appended, and the caller gets a typed STALE_TOKEN/NO_LEASE. This
          short-locked check-then-rename IS the resource-side fence.
        INVARIANT: once the arbiter has accepted token N+1 for a resource, an install
          carrying token N or lower is REFUSED (tokens are monotonic; the CAS in
          Phase C compares against the live projection under the OS lock).

        LEGACY SHAPE (0-arg callable returning a non-StagedArtifact) is still
        accepted: its side effects happen unfenced during Phase B, so a failed CAS in
        Phase C cannot un-write them - that lands as the recorded COMMIT_UNFENCED
        incident (M4 semantics preserved verbatim). But it no longer starves the
        arbiter: even a hung legacy callback holds NO lock.

        REENTRANCY: with no lock held across Phase B, re-entry can no longer
        deadlock; a per-resource in-flight flag on this arbiter instance (guarded by
        a threading.Lock) still refuses a callback that calls back into
        fenced_commit for the SAME resource - typed LockError REENTRANT - so a
        nested commit cannot interleave with its own reservation."""
        import hashlib as _hl
        resource = lease.resource
        with self._inflight_mu:
            if resource in self._inflight:
                raise LockError("REENTRANT",
                                f"fenced_commit re-entered for {resource} while its own "
                                f"commit is in flight - stage the work, do not nest it")
            self._inflight.add(resource)
        try:
            # ---------- PHASE A: short locked reserve/validate ----------
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
                                          "resource": resource, "token": lease.token,
                                          "detail": f"input unreadable: {pth}: {e}"})
                            raise LockError("NO_LEASE", f"input unreadable: {pth}") from e
                        if got != want:
                            self._append({"event": "REFUSE", "op": "commit",
                                          "resource": resource, "token": lease.token,
                                          "detail": f"input hash mismatch: {pth}"})
                            raise LockError("STALE_TOKEN",
                                            f"commit refused: input {pth} changed since the "
                                            f"decision (got {got[:12]}, expected {want[:12]})")
                self._append({"event": "COMMIT_RESERVED", "resource": resource,
                              "holder": lease.holder, "token": lease.token})
            finally:
                self._unlock(lk)

            # ---------- PHASE B: the callback runs with NO arbiter mutex held ------
            result = stage(lease.token) if _accepts_token(stage) else stage()
            art = result if isinstance(result, StagedArtifact) else None
            if art is not None and not os.path.isfile(os.fspath(art.src)):
                raise LockError("BAD_STAGE",
                                f"stage returned {art.src} but no such staged file "
                                f"exists - Phase B must write the artifact it hands "
                                f"to the fence")

            # ---------- PHASE C: short locked fenced INSTALL (CAS -> rename) ------
            lk = self._lock_handle()
            fence_ok = False
            refused_cur: Optional[Lease] = None
            try:
                self._reprime()
                self._expire_if_due(resource)
                cur = self._leases.get(resource)
                if cur is not None and cur.token == lease.token:
                    fence_ok = True
                    if art is not None:
                        os.replace(art.src, art.dst)   # O(1) single-volume install
                    self._append({"event": "COMMIT", "resource": cur.resource,
                                  "holder": cur.holder, "token": cur.token})
                elif art is not None:
                    refused_cur = cur
                    self._append({"event": "COMMIT_REFUSED", "resource": resource,
                                  "holder": lease.holder, "token": lease.token,
                                  "detail": "stale token at install ("
                                            + (f"superseded by {cur.token}" if cur
                                               else "no live lease")
                                            + ") - the staged artifact was NOT "
                                              "published; the resource-side fence held"})
                else:
                    refused_cur = cur
                    self._append({"event": "COMMIT_UNFENCED", "resource": resource,
                                  "holder": lease.holder, "token": lease.token,
                                  "detail": "lease expired or was superseded DURING the "
                                            "commit callback - the (unstaged, legacy) "
                                            "write landed with the fence down; recorded "
                                            "as an incident, never as a clean COMMIT"})
            finally:
                self._unlock(lk)
            if fence_ok:
                if art is not None:
                    return art.result if art.result is not None else art.dst
                return result
            # ---------- refusal paths (outside the lock) ----------
            if art is not None:
                try:
                    os.unlink(art.src)                 # the stale artifact never lands
                except OSError:
                    pass
                if refused_cur is not None:
                    raise LockError("STALE_TOKEN",
                                    f"install refused on {resource}: token {lease.token} "
                                    f"superseded by {refused_cur.token} during Phase B - "
                                    f"the stale artifact was not published")
                raise LockError("NO_LEASE",
                                f"install refused on {resource}: no live lease for "
                                f"token {lease.token} - the stale artifact was not "
                                f"published")
            raise LockError("STALE_TOKEN",
                            f"commit landed UNFENCED on {resource} - incident "
                            f"recorded; treat the artifact as suspect")
        finally:
            with self._inflight_mu:
                self._inflight.discard(resource)

    # ---------------- introspection ----------------
    def status(self, resource: str) -> Optional[Lease]:
        """FINDING #2 FIX (was CRITICAL): status() used to append EXPIRE and delete
        the lease with NO OS lock - a ledger mutation racing locked writers. Now the
        common paths are PURE READS of in-process memory; only when an expiry is
        actually due does it take the sidecar OS lock, reprime from disk, and persist
        the EXPIRE inside the locked section (the lease may have been renewed or
        already expired by another process - reprime decides, not memory)."""
        l = self._leases.get(resource)
        if l is None:
            return None
        if self._clock() < l.expires_at:
            return l
        lk = self._lock_handle()
        try:
            self._reprime()
            self._expire_if_due(resource)
            return self._leases.get(resource)
        finally:
            self._unlock(lk)

    def events(self) -> list[dict]:
        """Read-only replay of the raw event stream. A torn line refuses TYPED
        (TORN_LEDGER, never a bare ValueError) and a keyed arbiter VERIFIES each
        signature (FORGED_EVENT) - introspection must not be the one unverified
        window into the ledger (finding #4)."""
        if not self._ledger.exists():
            return []
        out = []
        for i, ln in enumerate(
                self._ledger.read_text(encoding="utf-8").splitlines(), 1):
            if not ln.strip():
                continue
            try:
                e = json.loads(ln)
            except ValueError as exc:
                raise LockError(
                    "TORN_LEDGER",
                    f"line {i} of {self._ledger} does not parse - REFUSING; a torn "
                    f"ledger must never read as clean history") from exc
            if self._key is not None:
                self._verify_sig(e, i)
            out.append(e)
        return out