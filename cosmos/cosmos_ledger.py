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
    mac_v        - 2 on records written by this version (absent on legacy records)
    hmac         - service authentication with the install key:
                     mac_v 2: over the WHOLE canonical record minus `hmac`
                     legacy : over (seq|prev_sha|payload_sha) only

VERIFICATION IS TOTAL OR REFUSED: verify() re-walks the chain; ANY break names the line.
The distinction preserved: TORN (unparseable) != BROKEN_CHAIN (parseable, wrong link)
!= FORGED (parseable, chained, bad hmac) != TRUNCATED (history shorter than proven).
A well-formed lie is BROKEN_CHAIN, typed.

Opus review findings #5/#6 (2026-09-17; CHANGES.md §4 ledger PR):
  * VERIFIED-HEAD CACHE. The ledger remembers the byte offset, seq and prev_sha it has
    verified. append/append_guarded verify only the bytes another writer added since
    (O(delta)), under the same OS lock. The full walk stays where it is a GATE: open,
    verify(), project(), the ledger_verify clock. A file SHORTER than the verified
    offset is TRUNCATED - tail deletion no longer reads as a clean, shorter history.
  * WHOLE-RECORD MAC (mac_v 2). The legacy MAC left `event`, `writer` and `t` of the
    HEAD record editable undetected. New records authenticate every field. Legacy
    records still verify under the legacy rule; a v2 record cannot be downgraded
    (its stored MAC fails the legacy check).
  * OPTIONAL SIGNED HEAD ANCHOR (head_anchor=True; Kernel turns it on for authority).
    `<ledger>.head.json` records {seq, prev_sha, offset} + HMAC after each append. At
    open, an anchor AHEAD of the file is TRUNCATED; an anchor whose line hash differs
    is BROKEN_CHAIN. An anchor behind the file is a crash after append - accepted.
  * fold_cached(name, fold, init): an incremental projection for hot readers (spend,
    scheduler). Folds only records appended since its last call.

Scar lineage: appends survive where atomic renames die (bts_sgh scar) - this file is
append-only with fsync; the mount rule (mount-visible copies are ingress, never
authority) is the CALLER's obligation and is restated in the kernel, not silently
assumed here.
"""
from __future__ import annotations

import copy
import errno
import hashlib
import hmac as hmac_mod
import json
import os
import tempfile
import threading
import time
from pathlib import Path
from typing import Iterator, Optional

# Sidecar mutex geometry - same discipline as the arbiter's _lock_handle
# (cosmos_lock, RF-LOCK-XPROC / T1): msvcrt.locking locks nbytes at the
# CURRENT CRT file position and raises on contention; it is not flock.
# Lock and unlock must both hit this fixed offset-0 region.
LOCK_REGION = 1
LOCK_POLL = 0.01
MAC_V = 2


class LedgerError(RuntimeError):
    """kind in {TORN, BROKEN_CHAIN, FORGED, UNREADABLE, STALE_HEAD, TRUNCATED}."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


def _canon(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


class _LazyRecords:
    """What append_guarded hands to decide(): the verified history, walked only
    if decide() actually reads it. A decider that ignores its argument (and asks a
    cached projection instead) no longer pays a full-chain walk under the lock."""

    def __init__(self, ledger: "Ledger"):
        self._ledger = ledger
        self._recs: Optional[list] = None

    def _load(self) -> list:
        if self._recs is None:
            self._recs = list(self._ledger.verify())
        return self._recs

    def __iter__(self):
        return iter(self._load())

    def __len__(self):
        return len(self._load())

    def __getitem__(self, i):
        return self._load()[i]

    def __bool__(self):
        return bool(self._load())


class Ledger:
    def __init__(self, path: str | os.PathLike, key: bytes, writer: str,
                 clock=time.time, *, head_anchor: bool = False):
        self._path = Path(path)
        self._key = key
        self._writer = writer
        self._clock = clock
        self._seq = 0
        self._prev_sha = ""
        self._last = None
        self._offset = 0              # bytes of the file already verified
        self._tail_nl = True          # does the verified region end with "\n"?
        self._mu = threading.RLock()
        self._folds: dict = {}
        self._head_anchor = bool(head_anchor)
        self._anchor: Optional[dict] = None
        self._anchor_sha_seen: Optional[str] = None
        self._anchor = self._load_anchor() if self._head_anchor else None
        if self._path.exists():
            for rec in self.verify():                 # loading IS verifying
                self._last = rec
        if self._anchor is not None:
            self._check_anchor()

    # ---------------- signing ----------------
    def _sign(self, seq: int, prev_sha: str, payload_sha: str) -> str:
        # LEGACY scheme (records without mac_v). Kept so existing chains load.
        # FULL hexdigest (256-bit). The old [:32] truncation halved the MAC for
        # nothing; verify() still ACCEPTS legacy 32-hex records (128-bit
        # HMAC-SHA256 is not forgeable either) so existing chains load.
        msg = f"{seq}|{prev_sha}|{payload_sha}".encode("utf-8")
        return hmac_mod.new(self._key, msg, hashlib.sha256).hexdigest()

    def _sign_v2(self, rec: dict) -> str:
        body = {k: v for k, v in rec.items() if k != "hmac"}
        return hmac_mod.new(self._key, _canon(body), hashlib.sha256).hexdigest()

    def _mac_ok(self, rec: dict) -> bool:
        got = rec.get("hmac", "")
        if not isinstance(got, str):
            return False
        if rec.get("mac_v") == MAC_V:
            return hmac_mod.compare_digest(self._sign_v2(rec), got)
        good = self._sign(rec["seq"], rec["prev_sha"], rec["payload_sha"])
        return hmac_mod.compare_digest(good, got) or (
            len(got) == 32 and hmac_mod.compare_digest(good[:32], got))

    # ---------------- OS lock ----------------
    def _lock_handle(self):
        """Cross-process serialization via an OS lock on a sidecar .lock file.
        CRITIC FINDING B1 (Grok, 2026-08-23, MEASURED): two writers on the same head
        both wrote seq=2 and tore the chain. The fix is an EXCLUSIVE OS LOCK held
        across (re-prime from disk -> append -> fsync): the second writer BLOCKS,
        then re-primes onto the new head. A lock the OS releases on process death
        needs no cleanup discipline.

        Native Windows: this now mirrors the arbiter's hardened pattern
        (cosmos_lock T1) instead of `open('a+b') + LK_LOCK`. msvcrt.locking is
        NOT flock - it locks LOCK_REGION bytes at the CRT file position (append
        mode leaves that at EOF) and LK_LOCK retries ~10s then RAISES instead of
        blocking. So: open O_RDWR|O_CREAT (never append-position), guarantee a
        real LOCK_REGION byte exists, os.lseek(0) so CRT and Python agree, and
        take LK_NBLCK in a poll loop; unlock hits the SAME fixed range."""
        path = str(self._path) + ".lock"
        flags = os.O_RDWR | os.O_CREAT
        if hasattr(os, "O_BINARY"):
            flags |= os.O_BINARY
        if hasattr(os, "O_CLOEXEC"):
            flags |= os.O_CLOEXEC
        fd = os.open(path, flags, 0o666)
        lk = os.fdopen(fd, "r+b", buffering=0)
        try:
            lk.seek(0, os.SEEK_END)
            have = lk.tell()
            if have < LOCK_REGION:
                # msvcrt cannot lock a byte past EOF of a 0-length file.
                lk.write(b"\x00" * (LOCK_REGION - have))
                lk.flush()
            if os.name == "nt":
                import msvcrt
                while True:
                    lk.flush()
                    os.lseek(lk.fileno(), 0, os.SEEK_SET)
                    try:
                        msvcrt.locking(lk.fileno(), msvcrt.LK_NBLCK, LOCK_REGION)
                        break
                    except OSError as e:
                        # Contention is EACCES/EDEADLK; EBADF/EINVAL is a
                        # programming error - do not spin on it.
                        if e.errno in (errno.EBADF, errno.EINVAL):
                            raise
                        time.sleep(LOCK_POLL)
            else:
                import fcntl
                fcntl.flock(lk.fileno(), fcntl.LOCK_EX)
            return lk
        except Exception:
            lk.close()
            raise

    def _unlock(self, lk) -> None:
        try:
            if os.name == "nt":
                import msvcrt
                lk.flush()
                os.lseek(lk.fileno(), 0, os.SEEK_SET)
                msvcrt.locking(lk.fileno(), msvcrt.LK_UNLCK, LOCK_REGION)
            else:
                import fcntl
                fcntl.flock(lk.fileno(), fcntl.LOCK_UN)
        finally:
            lk.close()

    # ---------------- the walk (shared by full and incremental verify) ----------------
    def _walk(self, data: bytes, base: int, prev_sha: str, seq: int, *,
              strict_tail: bool, line_no: Optional[int]):
        """Yield (rec|None, prev_sha_after, seq_after, end_offset, ends_nl) for each line
        in `data` (which starts at file offset `base`); None marks a blank line.
        strict_tail=False stops before an unterminated final fragment instead of judging
        it (a lock-free reader may be looking at a write in progress)."""
        pos = 0
        n = len(data)
        i = (line_no - 1) if line_no is not None else 0
        while pos < n:
            nl = data.find(b"\n", pos)
            if nl == -1:
                if not strict_tail:
                    return
                ln, end, ends_nl = data[pos:], n, False
            else:
                ln, end, ends_nl = data[pos:nl], nl + 1, True
            if ln.endswith(b"\r"):
                # CRLF tolerance, as splitlines() gave the previous reader: a file that
                # went through a text-mode copy still chains on the record bytes.
                ln = ln[:-1]
            i += 1
            where = f"line {i}" if line_no is not None else f"offset {base + pos}"
            pos = end
            if not ln.strip():
                yield None, prev_sha, seq, base + end, ends_nl
                continue
            try:
                rec = json.loads(ln)
            except ValueError as e:
                raise LedgerError("TORN", f"{where}: does not parse ({e}) - an "
                                          f"unreadable history is not an empty one") from e
            if not isinstance(rec, dict) or "payload" not in rec:
                # critic H2 finding: a parseable line missing its payload raised an
                # UNTYPED KeyError. A well-formed lie is BROKEN_CHAIN, typed.
                raise LedgerError("BROKEN_CHAIN",
                                  f"{where}: parseable but not a ledger record "
                                  f"(missing payload)")
            body = _canon(rec["payload"])
            if (rec.get("payload_len") != len(body)
                    or rec.get("payload_sha") != hashlib.sha256(body).hexdigest()):
                raise LedgerError("BROKEN_CHAIN",
                                  f"{where}: payload bytes/hash disagree with declaration "
                                  f"(the mount's silent-corruption signature)")
            if rec.get("prev_sha") != prev_sha:
                raise LedgerError("BROKEN_CHAIN",
                                  f"{where}: prev_sha does not chain to the record before")
            if rec.get("seq") != seq + 1:
                raise LedgerError("BROKEN_CHAIN",
                                  f"{where}: seq {rec.get('seq')} != expected {seq + 1}")
            if not self._mac_ok(rec):
                raise LedgerError("FORGED",
                                  f"{where}: hmac does not verify - a record this "
                                  f"service did not sign")
            prev_sha = hashlib.sha256(ln).hexdigest()
            seq = rec["seq"]
            if self._anchor is not None and seq == self._anchor.get("seq"):
                self._anchor_sha_seen = prev_sha
            yield rec, prev_sha, seq, base + end, ends_nl

    def _catch_up(self, *, strict: bool) -> None:
        """Verify only what was appended since the verified offset. Caller holds _mu
        (and, when strict, the OS lock)."""
        try:
            size = os.path.getsize(self._path)
        except FileNotFoundError:
            if self._offset > 0:
                raise LedgerError("TRUNCATED", f"{self._path}: verified {self._offset} "
                                               f"bytes, file is now absent")
            return
        except OSError as e:
            raise LedgerError("UNREADABLE", f"{self._path}: {e}") from e
        if size == self._offset:
            return
        if size < self._offset:
            raise LedgerError("TRUNCATED", f"{self._path}: size {size} < verified "
                                           f"offset {self._offset} - history got shorter")
        try:
            with open(self._path, "rb") as fh:
                fh.seek(self._offset)
                data = fh.read(size - self._offset)
        except OSError as e:
            raise LedgerError("UNREADABLE", f"{self._path}: {e}") from e
        for rec, prev, seq, end, ends_nl in self._walk(
                data, self._offset, self._prev_sha, self._seq,
                strict_tail=strict, line_no=None):
            self._prev_sha, self._seq, self._offset, self._tail_nl = prev, seq, end, ends_nl
            if rec is not None:
                self._last = rec

    # ---------------- write ----------------
    def _make(self, event: str, payload: dict) -> tuple[dict, str]:
        body = _canon(payload)
        t = self._clock()
        local = time.localtime(t)
        off = -time.timezone + (3600 if local.tm_isdst else 0)
        rec = {"seq": self._seq + 1, "event": event, "t": t, "utc_off": off,
               "payload": payload, "payload_len": len(body),
               "payload_sha": hashlib.sha256(body).hexdigest(),
               "prev_sha": self._prev_sha, "writer": self._writer, "mac_v": MAC_V}
        rec["hmac"] = self._sign_v2(rec)
        line = json.dumps(rec, sort_keys=True, separators=(",", ":"))
        return rec, line

    def _write(self, rec: dict, line: str) -> None:
        data = ("" if self._tail_nl else "\n") + line + "\n"
        with open(self._path, "a", encoding="utf-8", newline="") as fh:
            fh.write(data)
            fh.flush()
            os.fsync(fh.fileno())
        self._offset += len(data.encode("utf-8"))
        self._tail_nl = True
        self._seq = rec["seq"]
        self._prev_sha = hashlib.sha256(line.encode("utf-8")).hexdigest()
        self._last = rec
        if self._head_anchor:
            self._write_anchor()

    def append(self, event: str, payload: dict,
               expect_head_seq: Optional[int] = None) -> dict:
        """Serialized append. Under the OS lock the writer RE-PRIMES from disk, so a
        concurrent writer lands on the REAL head instead of a remembered one (B1).
        Catch-up verifies only bytes since the last verified offset (O(delta)); that
        is still re-prime seq/prev_sha from DISK, never a remembered head.
        `expect_head_seq` is optimistic concurrency for callers whose DECISION depended
        on the head they projected (the scheduler's claim): if the head moved since,
        the append refuses with STALE_HEAD instead of recording a decision made on a
        dead projection (B2's clean loser)."""
        lk = self._lock_handle()
        try:
            with self._mu:
                self._catch_up(strict=True)
                if expect_head_seq is not None and self._seq != expect_head_seq:
                    raise LedgerError("STALE_HEAD",
                                      f"head moved {expect_head_seq} -> {self._seq} while "
                                      f"deciding - losing cleanly, re-project and retry")
                rec, line = self._make(event, payload)
                self._write(rec, line)
                return rec
        finally:
            self._unlock(lk)

    def head_seq(self) -> int:
        """Current head sequence from disk, verifying only new bytes."""
        with self._mu:
            self._catch_up(strict=False)
            return self._seq

    def head(self) -> dict:
        with self._mu:
            self._catch_up(strict=False)
            return {"seq": self._seq, "prev_sha": self._prev_sha, "offset": self._offset}

    def append_guarded(self, decide):
        """Atomic READ-DECIDE-APPEND under the OS lock. STAGE-7B (RF-LOCK-XPROC / RG-B1,
        MEASURED): expect_head_seq sampled the head at APPEND time, so a decision made on
        a stale projection could still bind a fresh head - two overlapping callers both
        passed a cap/lock check. This holds the exclusive lock across the WHOLE decision:
        `decide(records)` receives the verified history (walked lazily, only if decide
        reads it) and returns (event, payload) to append, or raises to abort with
        nothing written. No caller outside this method can interleave between the
        decision and the append."""
        lk = self._lock_handle()
        try:
            with self._mu:
                self._catch_up(strict=True)
                result = decide(_LazyRecords(self))
                if result is None:
                    return None
                event, payload = result
                rec, line = self._make(event, payload)
                self._write(rec, line)
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
            with self._mu:
                self._prev_sha, self._seq, self._last = "", 0, None
                self._offset, self._tail_nl = 0, True
            return
        try:
            raw = self._path.read_bytes()
        except OSError as e:
            raise LedgerError("UNREADABLE", f"{self._path}: {e}") from e
        prev, seq, last, end, tail_nl = "", 0, None, 0, True
        for rec, prev, seq, end, tail_nl in self._walk(raw, 0, "", 0, strict_tail=True,
                                                       line_no=1):
            if rec is not None:
                last = rec
                yield rec
        with self._mu:
            self._prev_sha, self._seq, self._last = prev, seq, last
            self._offset, self._tail_nl = end, tail_nl

    def project(self, fold, init):
        """Rebuild ANY state by replay: project(lambda state, rec: ..., init).
        The projection is disposable; the ledger is the authority."""
        state = init
        for rec in self.verify():
            state = fold(state, rec)
        return state

    def fold_cached(self, name: str, fold, init):
        """Incremental projection. Folds only records appended since the last call for
        `name` (chained and MAC-verified like everything else) and returns a deep copy,
        so callers cannot mutate the cache. `init` may be a value or a factory. A file
        shorter than what was folded is TRUNCATED."""
        with self._mu:
            ent = self._folds.get(name)
            if ent is None:
                state = init() if callable(init) else copy.deepcopy(init)
                off, prev, seq = 0, "", 0
            else:
                state, off, prev, seq = ent
            try:
                size = os.path.getsize(self._path)
            except FileNotFoundError:
                if off > 0:
                    raise LedgerError("TRUNCATED", f"{self._path}: absent after {off} "
                                                   f"folded bytes")
                self._folds[name] = (state, 0, "", 0)
                return copy.deepcopy(state)
            if size < off:
                raise LedgerError("TRUNCATED", f"{self._path}: size {size} < folded "
                                               f"offset {off}")
            if size > off:
                with open(self._path, "rb") as fh:
                    fh.seek(off)
                    data = fh.read(size - off)
                for rec, prev, seq, off, _nl in self._walk(
                        data, off, prev, seq, strict_tail=False, line_no=None):
                    if rec is not None:
                        state = fold(state, rec)
            self._folds[name] = (state, off, prev, seq)
            return copy.deepcopy(state)

    def last(self) -> Optional[dict]:
        """Head record from the last successful verify/append/catch-up.

        GET /status must not re-walk 15k records every poll (the 4-7 s walk the deck
        reported as 'server down'). An unverified head is never returned."""
        return self._last

    # ---------------- head anchor ----------------
    def _anchor_path(self) -> Path:
        return self._path.with_name(self._path.name + ".head.json")

    def _load_anchor(self) -> Optional[dict]:
        p = self._anchor_path()
        if not p.exists():
            return None
        try:
            with open(p, encoding="utf-8") as fh:
                d = json.loads(fh.read())
        except (OSError, ValueError) as e:
            raise LedgerError("UNREADABLE", f"head anchor {p}: {e}") from e
        body = {k: v for k, v in d.items() if k != "hmac"}
        want = hmac_mod.new(self._key, _canon(body), hashlib.sha256).hexdigest()
        if not isinstance(d.get("hmac"), str) or not hmac_mod.compare_digest(want, d["hmac"]):
            raise LedgerError("FORGED", f"head anchor {p}: hmac does not verify")
        return d

    def _check_anchor(self) -> None:
        a = self._anchor
        if a["seq"] > self._seq:
            raise LedgerError("TRUNCATED",
                              f"{self._path}: head anchor proves seq {a['seq']} but the "
                              f"file ends at seq {self._seq} - records were removed")
        if a["seq"] > 0 and self._anchor_sha_seen != a["prev_sha"]:
            raise LedgerError("BROKEN_CHAIN",
                              f"{self._path}: record at anchored seq {a['seq']} is not "
                              f"the record the anchor signed")

    def _write_anchor(self) -> None:
        body = {"seq": self._seq, "prev_sha": self._prev_sha, "offset": self._offset,
                "writer": self._writer, "at": self._clock()}
        body["hmac"] = hmac_mod.new(self._key, _canon(body), hashlib.sha256).hexdigest()
        p = self._anchor_path()
        try:
            with open(p, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(json.dumps(body, sort_keys=True))
                fh.flush()
                os.fsync(fh.fileno())
            self._anchor = body
        except OSError:
            # An anchor BEHIND the file is safe (crash-after-append shape); failing to
            # advance it must never fail an append that already reached disk.
            pass


def _selftest() -> int:
    """mac_v 2 roundtrip; legacy line still loads; truncating the file is TRUNCATED."""
    results: list[tuple[str, bool, str]] = []

    def check(label, fn):
        try:
            results.append((label, bool(fn()), ""))
        except Exception as e:                                            # noqa: BLE001
            results.append((label, False, f"{type(e).__name__}: {e}"))

    def kind_of(fn) -> Optional[str]:
        try:
            fn()
        except LedgerError as e:
            return e.kind
        return None

    key = b"mac2-selftest-key-0123456789abcd"
    td = Path(tempfile.mkdtemp(prefix="cosmos_mac2_"))

    p = td / "a.jsonl"
    led = Ledger(p, key, "W")
    led.append("PING", {"n": 1})
    led.append("PING", {"n": 2})
    recs = list(Ledger(p, key, "R").verify())
    check("mac_v 2 roundtrip: new records carry mac_v 2 and verify",
          lambda: all(r.get("mac_v") == 2 for r in recs) and len(recs) == 2)
    def _edit_head_event():
        raw = p.read_bytes()
        cut = raw.rstrip(b"\n").rfind(b"\n") + 1
        p.write_bytes(raw[:cut] + raw[cut:].replace(b'"event":"PING"', b'"event":"PONG"', 1))
        Ledger(p, key, "R")

    check("mac_v 2 HMAC covers the whole record (head event edit is FORGED)",
          lambda: kind_of(_edit_head_event) == "FORGED")

    lg = td / "legacy.jsonl"
    prev, lines = "", []
    for seq in (1, 2):
        payload = {"n": seq}
        body = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        rec = {"seq": seq, "event": "OLD", "t": 1.0, "utc_off": 0, "payload": payload,
               "payload_len": len(body), "payload_sha": hashlib.sha256(body).hexdigest(),
               "prev_sha": prev, "writer": "old"}
        rec["hmac"] = hmac_mod.new(key, f"{seq}|{prev}|{rec['payload_sha']}".encode(),
                                   hashlib.sha256).hexdigest()
        line = json.dumps(rec, sort_keys=True, separators=(",", ":"))
        lines.append(line)
        prev = hashlib.sha256(line.encode()).hexdigest()
    lg.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="")
    ll = Ledger(lg, key, "new")
    ll.append("NEW", {"n": 3})
    check("legacy line still loads; chain continues with mac_v 2",
          lambda: [r.get("mac_v") for r in Ledger(lg, key, "x").verify()]
          == [None, None, 2])

    t = td / "trunc.jsonl"
    tw = Ledger(t, key, "W")
    for i in range(3):
        tw.append("E", {"i": i})
    raw = t.read_bytes()
    t.write_bytes(raw[:raw.rstrip(b"\n").rfind(b"\n") + 1])
    check("truncating the file under a live writer is TRUNCATED",
          lambda: kind_of(lambda: tw.append("E", {"i": 9})) == "TRUNCATED")

    k2 = td / "anch.jsonl"
    al = Ledger(k2, key, "core", head_anchor=True)
    for i in range(3):
        al.append("E", {"i": i})
    raw = k2.read_bytes()
    k2.write_bytes(raw[:raw.rstrip(b"\n").rfind(b"\n") + 1])
    check("head anchor: removed tail is TRUNCATED at open",
          lambda: kind_of(lambda: Ledger(k2, key, "core", head_anchor=True))
          == "TRUNCATED")
    check("authority.jsonl.head.json seq matches the written head",
          lambda: json.loads((td / "anch.jsonl.head.json").read_text())["seq"] == 3)

    def fold(s, r):
        s["n"] += r["payload"].get("n", 0)
        return s
    fpath = td / "fold.jsonl"
    fa = Ledger(fpath, key, "a")
    for i in range(4):
        fa.append("N", {"n": i})
        fa.fold_cached("sum", fold, lambda: {"n": 0})
    check("fold_cached equals a full project",
          lambda: fa.fold_cached("sum", fold, lambda: {"n": 0})
          == fa.project(fold, {"n": 0}) == {"n": 6})

    bad = [(l, e) for l, ok, e in results if not ok]
    for label, ok, err in results:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label,
                              ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks (mac_v 2, legacy load, TRUNCATED)"
          % ("PASS" if not bad else "FAIL", len(results)))
    return 0 if not bad else 1


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="cosmos_ledger selftest")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if not a.selftest:
        ap.error("--selftest is the operator verb")
    raise SystemExit(_selftest())
