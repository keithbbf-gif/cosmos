#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_ledger - THE AUTHORITY PRIMITIVE (F5 builder, foundation-first per Keith).

CONTRACT (docs/FINAL_ARCHITECTURE.md, ratified): an append-only, HASH-CHAINED,
service-authenticated framed JSONL ledger is the sole authority; every other state is a
rebuildable projection. A corrupt record REFUSES - history is never repaired in place.

EACH RECORD (one JSONL line) CARRIES:
    seq          - record sequence in this segment (monotonic from 1)
    event        - the event type (caller's vocabulary)
    t / utc_off  - epoch float + utc offset seconds (one clock, offset-aware)
    payload      - the event body (canonical JSON)
    payload_len  - byte length of the canonical payload encoding
    payload_sha  - sha256 of that encoding
    prev_sha     - sha256 of the PREVIOUS record's full line ("" for the first)
    writer       - writer identity (per-worker identity in every artifact)
    hmac         - service authentication over (seq|prev_sha|payload_sha) with the
                   install key - a record another writer forges does not verify

VERIFICATION IS TOTAL OR REFUSED: verify() re-walks the chain; ANY break names the line.
The distinction preserved: TORN (unparseable) != BROKEN_CHAIN (parseable, wrong link)
!= FORGED (parseable, chained, bad hmac) - three different facts, three kinds.

Scar lineage: appends survive where atomic renames die (bts_sgh scar) - this file is
append-only with fsync; the mount rule (mount-visible copies are ingress, never
authority) is the CALLER's obligation and is restated in the kernel, not silently
assumed here.
"""
from __future__ import annotations

import hashlib
import hmac as hmac_mod
import json
import os
import time
from pathlib import Path
from typing import Iterator, Optional


class LedgerError(RuntimeError):
    """kind in {TORN, BROKEN_CHAIN, FORGED, UNREADABLE, STALE_HEAD}."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


def _canon(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


class Ledger:
    def __init__(self, path: str | os.PathLike, key: bytes, writer: str,
                 clock=time.time):
        self._path = Path(path)
        self._key = key
        self._writer = writer
        self._clock = clock
        self._seq = 0
        self._prev_sha = ""
        if self._path.exists():
            for _ in self.verify():                 # loading IS verifying
                pass

    # ---------------- write ----------------
    def _sign(self, seq: int, prev_sha: str, payload_sha: str) -> str:
        msg = f"{seq}|{prev_sha}|{payload_sha}".encode("utf-8")
        return hmac_mod.new(self._key, msg, hashlib.sha256).hexdigest()[:32]

    def _lock_handle(self):
        """Cross-process serialization via an OS lock on a sidecar .lock file.
        CRITIC FINDING B1 (Grok, 2026-08-23, MEASURED): two writers on the same head
        both wrote seq=2 and tore the chain. The fix is an EXCLUSIVE OS LOCK held
        across (re-prime from disk -> append -> fsync): the second writer BLOCKS,
        then re-primes onto the new head. A lock the OS releases on process death
        needs no cleanup discipline."""
        lk = open(str(self._path) + ".lock", "a+b")
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

    def append(self, event: str, payload: dict,
               expect_head_seq: Optional[int] = None) -> dict:
        """Serialized append. Under the OS lock the writer RE-PRIMES from disk, so a
        concurrent writer lands on the REAL head instead of a remembered one (B1).
        `expect_head_seq` is optimistic concurrency for callers whose DECISION depended
        on the head they projected (the scheduler's claim): if the head moved since,
        the append refuses with STALE_HEAD instead of recording a decision made on a
        dead projection (B2's clean loser)."""
        lk = self._lock_handle()
        try:
            for _ in self.verify():          # re-prime seq/prev_sha from DISK
                pass
            if expect_head_seq is not None and self._seq != expect_head_seq:
                raise LedgerError("STALE_HEAD",
                                  f"head moved {expect_head_seq} -> {self._seq} while "
                                  f"deciding - losing cleanly, re-project and retry")
            body = _canon(payload)
            t = self._clock()
            local = time.localtime(t)
            off = -time.timezone + (3600 if local.tm_isdst else 0)
            self._seq += 1
            rec = {"seq": self._seq, "event": event, "t": t, "utc_off": off,
                   "payload": payload, "payload_len": len(body),
                   "payload_sha": hashlib.sha256(body).hexdigest(),
                   "prev_sha": self._prev_sha, "writer": self._writer}
            rec["hmac"] = self._sign(rec["seq"], rec["prev_sha"], rec["payload_sha"])
            line = json.dumps(rec, sort_keys=True, separators=(",", ":"))
            with open(self._path, "a", encoding="utf-8", newline="") as fh:
                fh.write(line + "\n")
                fh.flush()
                os.fsync(fh.fileno())
            self._prev_sha = hashlib.sha256(line.encode("utf-8")).hexdigest()
            return rec
        finally:
            self._unlock(lk)

    def head_seq(self) -> int:
        """Current head sequence, re-read from disk - for expect_head_seq callers."""
        for _ in self.verify():
            pass
        return self._seq

    def append_guarded(self, decide):
        """Atomic READ-DECIDE-APPEND under the OS lock. STAGE-7B (RF-LOCK-XPROC / RG-B1,
        MEASURED): expect_head_seq sampled the head at APPEND time, so a decision made on
        a stale projection could still bind a fresh head - two overlapping callers both
        passed a cap/lock check. This holds the exclusive lock across the WHOLE decision:
        `decide(records)` receives the freshly-replayed history and returns (event,
        payload) to append, or raises to abort with nothing written. No caller outside
        this method can interleave between the decision and the append."""
        lk = self._lock_handle()
        try:
            recs = list(self.verify())          # re-primed under the lock
            result = decide(recs)               # may raise to abort
            if result is None:
                return None
            event, payload = result
            body = _canon(payload)
            t = self._clock()
            local = time.localtime(t)
            off = -time.timezone + (3600 if local.tm_isdst else 0)
            self._seq += 1
            rec = {"seq": self._seq, "event": event, "t": t, "utc_off": off,
                   "payload": payload, "payload_len": len(body),
                   "payload_sha": hashlib.sha256(body).hexdigest(),
                   "prev_sha": self._prev_sha, "writer": self._writer}
            rec["hmac"] = self._sign(rec["seq"], rec["prev_sha"], rec["payload_sha"])
            line = json.dumps(rec, sort_keys=True, separators=(",", ":"))
            with open(self._path, "a", encoding="utf-8", newline="") as fh:
                fh.write(line + "\n"); fh.flush(); os.fsync(fh.fileno())
            self._prev_sha = hashlib.sha256(line.encode("utf-8")).hexdigest()
            return rec
        finally:
            self._unlock(lk)

    # ---------------- verify / read ----------------
    def verify(self) -> Iterator[dict]:
        """Walk the whole chain; yield each verified record; REFUSE at the first break.
        Also (re)primes the writer state so appends continue the chain after a reload.

        ABSENT != UNREADABLE (the four-state rule, enforced on this module by its own
        gate 2026-08-23): a ledger file that does not exist yet is a ledger with ZERO
        events - a legitimate empty history - while a file that exists and cannot be
        read is a refusal. The first version collapsed the two and the finisher's
        suites caught it before commit."""
        if not self._path.exists():
            self._prev_sha = ""
            self._seq = 0
            return
        try:
            lines = self._path.read_text(encoding="utf-8").splitlines()
        except OSError as e:
            raise LedgerError("UNREADABLE", f"{self._path}: {e}") from e
        prev_sha = ""
        seq = 0
        for i, ln in enumerate(lines, 1):
            if not ln.strip():
                continue
            try:
                rec = json.loads(ln)
            except ValueError as e:
                raise LedgerError("TORN", f"line {i}: does not parse ({e}) - an "
                                          f"unreadable history is not an empty one") from e
            if not isinstance(rec, dict) or "payload" not in rec:
                # critic H2 finding: a parseable line missing its payload raised an
                # UNTYPED KeyError. A well-formed lie is BROKEN_CHAIN, typed.
                raise LedgerError("BROKEN_CHAIN",
                                  f"line {i}: parseable but not a ledger record "
                                  f"(missing payload)")
            body = _canon(rec["payload"])
            if (rec.get("payload_len") != len(body)
                    or rec.get("payload_sha") != hashlib.sha256(body).hexdigest()):
                raise LedgerError("BROKEN_CHAIN",
                                  f"line {i}: payload bytes/hash disagree with declaration "
                                  f"(the mount's silent-corruption signature)")
            if rec.get("prev_sha") != prev_sha:
                raise LedgerError("BROKEN_CHAIN",
                                  f"line {i}: prev_sha does not chain to line {i-1}")
            if rec.get("seq") != seq + 1:
                raise LedgerError("BROKEN_CHAIN",
                                  f"line {i}: seq {rec.get('seq')} != expected {seq + 1}")
            good = self._sign(rec["seq"], rec["prev_sha"], rec["payload_sha"])
            if not hmac_mod.compare_digest(good, rec.get("hmac", "")):
                raise LedgerError("FORGED",
                                  f"line {i}: hmac does not verify - a record this "
                                  f"service did not sign")
            prev_sha = hashlib.sha256(ln.encode("utf-8")).hexdigest()
            seq = rec["seq"]
            yield rec
        self._prev_sha = prev_sha
        self._seq = seq

    def project(self, fold, init):
        """Rebuild ANY state by replay: project(lambda state, rec: ..., init).
        The projection is disposable; the ledger is the authority."""
        state = init
        for rec in self.verify():
            state = fold(state, rec)
        return state

    def last(self) -> Optional[dict]:
        recs = list(self.verify())
        return recs[-1] if recs else None