#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_segments - SEGMENTS + CAS, A LAYER OVER THE LEDGER (F5 builder).

CLOSING-CRITIC FINDING M9 (ratified): the authority is "framed JSONL SEGMENTS + a
content-addressed store (CAS); a corrupt segment REFUSES and records an incident." This
module is that layer built ON TOP OF cosmos_ledger.Ledger - NOT a rewrite. Every segment
file IS an ordinary Ledger and is verified with the ordinary Ledger.verify(); this module
only adds rotation, a cross-segment ANCHOR CHAIN, incident recording, and the CAS.

WHY A SEGMENTED LEDGER AT ALL: one ever-growing JSONL file is re-read in full on every
verify and every reload (loading IS verifying, cosmos_ledger). Segments bound that cost,
let old history be sealed, and let a single corrupt segment be named and quarantined
instead of poisoning the whole chain.

SEGMENT FILES:  ledger/seg-00001.jsonl, seg-00002.jsonl, ...   (each a standalone Ledger)
ANCHOR FILES :  ledger/seg-00001.anchor.json, ...              (one per CLOSED segment)

Each anchor carries {segment, first_seq, last_seq, record_count, segment_sha256,
prev_anchor_sha256, hmac} (plus last_record_sha, below). The hmac is service
authentication over the canonical unsigned body with the install key - an attacker who
edits ledger files and re-hashes the bytes still cannot produce an anchor this service
will accept (RF-SEG-ANCHOR / T5). The anchors form THEIR OWN hash chain: anchor N's
prev_anchor_sha256 is the sha256 of anchor N-1's on-disk bytes (the signed file). So the
WHOLE history is verifiable segment-to-segment - a dropped, duplicated, or edited segment
breaks the anchor chain even when each surviving file parses cleanly on its own. A
signature or prev_anchor_sha256 failure REFUSES and records a LEDGER_INCIDENT.

THE RECONCILIATION THAT MATTERS (and it is deliberate, not a shortcut):
  cosmos_ledger.Ledger.verify() requires each file to be SELF-CONTAINED - its first record
  has prev_sha == "" and its seq counts from 1. That is the contract we reuse verbatim. So
  record-level prev_sha CANNOT chain across a segment boundary without breaking the very
  verifier M9 tells us to reuse. Cross-segment continuity therefore lives in the ANCHOR
  chain, and the closing segment's last-record hash is CARRIED IN THE ANCHOR
  (`last_record_sha`) so the seam between segments is explicit and auditable. Within a
  segment: record hash-chain. Across segments: anchor hash-chain. Two chains, one history.

GLOBAL SEQ: continuous 1..N across the whole ledger. Each segment's Ledger keeps a LOCAL
seq from 1 (so Ledger.verify is happy); the global seq of a record is
prior_records + local_seq, and verify_all() yields it. Local seq resets at each boundary;
global seq never does. That is the visible proof the layering is real.

A CORRUPT SEGMENT REFUSES + RECORDS AN INCIDENT: verify_all() catches the first break,
appends a LEDGER_INCIDENT to a SEPARATE incidents.jsonl (itself a plain Ledger, so the
incident record is hash-chained and service-signed too), then re-raises naming the
segment (and, for a line-level break, the line the underlying Ledger named).

CAS: a large artifact goes in the content-addressed store and the LEDGER HOLDS ONLY THE
SHA POINTER. put(bytes) -> sha256 hex (idempotent: same content, same name, no rewrite).
get(sha) -> bytes WITH A READ-BACK HASH CHECK - a blob corrupted on disk raises
LedgerError HASH_MISMATCH rather than handing back silent garbage. All CAS filesystem
calls go through extended() so a >260-char path is not a WinError-3 "not found" (C-60).
"""
from __future__ import annotations

import hashlib
import hmac as hmac_mod
import json
import os
import re
from pathlib import Path
from typing import Iterator, Optional

from cosmos_ledger import Ledger, LedgerError
from cosmos_paths import extended

# LedgerError kinds reused: TORN, BROKEN_CHAIN, FORGED, UNREADABLE, STALE_HEAD.
# FORGED is the unsigned/mis-signed closed-segment anchor (parseable, keyed, bad hmac) -
# the same three-way as cosmos_ledger: TORN != BROKEN_CHAIN != FORGED.
# Added by this layer (prefer existing where possible; these name facts none of the
# above express): HASH_MISMATCH (a CAS blob's bytes disagree with its own name) and
# NOT_FOUND (a CAS blob that was never stored - ABSENT != UNREADABLE, cosmos_ledger).

_ANCHOR_KEYS = ("segment", "first_seq", "last_seq", "record_count",
                "segment_sha256", "prev_anchor_sha256")
# hmac is required but checked separately as FORGED, not as a missing-key BROKEN_CHAIN.


def _sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _anchor_hmac(key: bytes, anchor: dict) -> str:
    """HMAC-SHA256 of the canonical unsigned anchor body, truncated like ledger hmac."""
    body = json.dumps({k: v for k, v in anchor.items() if k != "hmac"},
                      sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hmac_mod.new(key, body, hashlib.sha256).hexdigest()[:32]


def _read_bytes(path: Path) -> bytes:
    with open(extended(path), "rb") as fh:
        return fh.read()


class SegmentedLedger:
    """A directory of segment Ledgers with a chained anchor per closed segment.

    max_records / max_bytes bound the ACTIVE segment; exceeding either rotates it CLOSED
    (an anchor is written) and opens the next. Global seq is continuous across segments.
    """

    def __init__(self, root: str | os.PathLike, key: bytes, writer: str,
                 max_records: int = 1000, max_bytes: Optional[int] = None,
                 clock=None):
        self._root = Path(root)
        self._key = key
        self._writer = writer
        self._max_records = int(max_records)
        self._max_bytes = max_bytes
        self._clock = clock
        os.makedirs(extended(self._root), exist_ok=True)
        # incidents live in their OWN plain Ledger - hash-chained and signed like any
        # other history, but never mixed into the segments it reports on.
        self._incidents = self._mk_ledger(self._root / "incidents.jsonl")
        self._load()

    # ---------------- construction helpers ----------------
    def _mk_ledger(self, path: Path) -> Ledger:
        if self._clock is not None:
            return Ledger(path, self._key, self._writer, clock=self._clock)
        return Ledger(path, self._key, self._writer)

    def _seg_path(self, n: int) -> Path:
        return self._root / ("seg-%05d.jsonl" % n)

    def _anchor_path(self, n: int) -> Path:
        return self._root / ("seg-%05d.anchor.json" % n)

    def _closed(self, n: int) -> bool:
        return os.path.exists(extended(self._anchor_path(n)))

    def _segment_numbers(self) -> list[int]:
        try:
            names = os.listdir(extended(self._root))
        except FileNotFoundError:
            return []
        nums = []
        for nm in names:
            m = re.fullmatch(r"seg-(\d{5})\.jsonl", nm)
            if m:
                nums.append(int(m.group(1)))
        return sorted(nums)

    def segments(self) -> list[int]:
        """The segment numbers present on disk, in order (open and closed)."""
        return self._segment_numbers()

    def _load(self) -> None:
        nums = self._segment_numbers()
        if not nums:
            self._active_n = 1
            self._active = self._mk_ledger(self._seg_path(1))
            self._active_count = 0
            self._prior_count = 0
            self._last_anchor_sha = ""
            return
        max_n = nums[-1]
        if self._closed(max_n):
            active_n = max_n + 1        # last file is sealed; the next is where we append
            closed_upto = max_n
        else:
            active_n = max_n
            closed_upto = max_n - 1
        prior = 0
        last_anchor_sha = ""
        for n in range(1, closed_upto + 1):
            raw = _read_bytes(self._anchor_path(n))
            anc = json.loads(raw.decode("utf-8"))
            prior += int(anc.get("record_count", 0))
            last_anchor_sha = _sha(raw)
        self._active_n = active_n
        self._active = self._mk_ledger(self._seg_path(active_n))
        self._active_count = self._active.head_seq()   # local seq of the active segment
        self._prior_count = prior
        self._last_anchor_sha = last_anchor_sha

    # ---------------- write ----------------
    def _should_rotate(self) -> bool:
        if self._active_count == 0:
            return False
        if self._active_count >= self._max_records:
            return True
        if self._max_bytes is not None:
            try:
                if os.path.getsize(extended(self._seg_path(self._active_n))) >= self._max_bytes:
                    return True
            except OSError:
                pass
        return False

    def _rotate(self) -> None:
        """Close the active segment: write its chained anchor, then open the next.
        The new segment is a fresh standalone Ledger (prev_sha restarts at ""); the seam
        is preserved in the anchor's last_record_sha, and continuity is the anchor chain."""
        n = self._active_n
        seg_raw = _read_bytes(self._seg_path(n))
        record_count = self._active_count
        anchor = {
            "segment": n,
            "first_seq": self._prior_count + 1,
            "last_seq": self._prior_count + record_count,
            "record_count": record_count,
            "segment_sha256": _sha(seg_raw),
            "prev_anchor_sha256": self._last_anchor_sha,
            # carry the closing segment's last-record hash so the boundary is auditable
            "last_record_sha": self._active._prev_sha,
        }
        # install-key HMAC: re-hashing the bytes is not enough to rewrite accounting
        anchor["hmac"] = _anchor_hmac(self._key, anchor)
        body = json.dumps(anchor, sort_keys=True, separators=(",", ":")).encode("utf-8")
        with open(extended(self._anchor_path(n)), "wb") as fh:
            fh.write(body)
            fh.flush()
            os.fsync(fh.fileno())
        self._last_anchor_sha = _sha(body)
        self._prior_count += record_count
        self._active_n = n + 1
        self._active = self._mk_ledger(self._seg_path(self._active_n))
        self._active_count = 0

    def append(self, event: str, payload: dict) -> dict:
        """Delegate to the active segment's Ledger.append, rotating first if the active
        segment is full. Returns the underlying record augmented with a continuous
        `global_seq` and the `segment` it landed in."""
        if self._should_rotate():
            self._rotate()
        rec = self._active.append(event, payload)
        self._active_count += 1
        out = dict(rec)
        out["global_seq"] = self._prior_count + rec["seq"]
        out["segment"] = self._active_n
        return out

    def head_global_seq(self) -> int:
        return self._prior_count + self._active_count

    # ---------------- verify ----------------
    def _record_incident(self, segment: int, kind: str, detail: str) -> None:
        self._incidents.append("LEDGER_INCIDENT",
                               {"segment": segment, "kind": kind, "detail": detail[:500]})

    def incidents(self) -> list[dict]:
        return list(self._incidents.verify())

    def verify_all(self) -> Iterator[dict]:
        """Walk EVERY segment in order and REFUSE at the first break, naming the segment
        (and the line, for a record-level break). For each closed segment also verify the
        anchor: its hmac against the install key, its segment_sha256 against the actual
        file bytes, its place in the anchor hash-chain (prev_anchor_sha256), and its seq
        accounting. A signature or chain break appends a LEDGER_INCIDENT to
        incidents.jsonl, then raises. Yields every verified record with a continuous
        `global_seq` (local seq resets per segment; global never does)."""
        nums = self._segment_numbers()
        running = 0
        prev_anchor_sha = ""
        for idx, n in enumerate(nums):
            seg_path = self._seg_path(n)
            seg_first_global = running + 1
            recs = []
            try:
                # Ledger.__init__ VERIFIES an existing file at construction ("loading IS
                # verifying"), so a corrupt segment breaks HERE, not only in the record
                # walk below. Construction therefore lives INSIDE this try: a
                # construction-time break records the same incident and re-raises named
                # the same way as a walk-time break. (It escaped un-named and un-recorded
                # when this call sat above the try - the F5 quarantine defect.)
                led = self._mk_ledger(seg_path)
                for rec in led.verify():
                    running += 1
                    recs.append(rec)
                    out = dict(rec)
                    out["global_seq"] = running
                    out["segment"] = n
                    yield out
            except LedgerError as e:
                self._record_incident(n, e.kind, "seg-%05d.jsonl: %s" % (n, e))
                raise LedgerError(e.kind, "seg-%05d.jsonl: %s" % (n, e)) from e
            seg_last_global = running

            if self._closed(n):
                anchor_path = self._anchor_path(n)
                raw = _read_bytes(anchor_path)
                try:
                    anc = json.loads(raw.decode("utf-8"))
                except ValueError as e:
                    self._record_incident(n, "TORN", "seg-%05d.anchor.json unparseable: %s" % (n, e))
                    raise LedgerError("TORN",
                                      "seg-%05d.anchor.json: does not parse (%s)" % (n, e)) from e
                if not isinstance(anc, dict) or any(k not in anc for k in _ANCHOR_KEYS):
                    self._record_incident(n, "BROKEN_CHAIN", "seg-%05d.anchor.json missing keys" % n)
                    raise LedgerError("BROKEN_CHAIN",
                                      "seg-%05d.anchor.json: not a well-formed anchor" % n)
                # hmac first: edited accounting that was merely re-hashed is FORGED, not
                # a chain-shape fact. Missing or non-string hmac is the same refusal.
                good = _anchor_hmac(self._key, anc)
                got = anc.get("hmac", "")
                if not isinstance(got, str) or not hmac_mod.compare_digest(good, got):
                    self._record_incident(n, "FORGED", "seg-%05d.anchor.json hmac" % n)
                    raise LedgerError("FORGED",
                                      "seg-%05d.anchor.json: hmac does not verify - an "
                                      "anchor this service did not sign" % n)
                actual_seg_sha = _sha(_read_bytes(seg_path))
                if anc["segment_sha256"] != actual_seg_sha:
                    self._record_incident(n, "BROKEN_CHAIN", "seg-%05d.anchor.json segment_sha256" % n)
                    raise LedgerError("BROKEN_CHAIN",
                                      "seg-%05d.anchor.json: segment_sha256 disagrees with the "
                                      "segment file bytes (segment changed since it was sealed)" % n)
                if anc["prev_anchor_sha256"] != prev_anchor_sha:
                    self._record_incident(n, "BROKEN_CHAIN", "seg-%05d.anchor.json prev_anchor" % n)
                    raise LedgerError("BROKEN_CHAIN",
                                      "seg-%05d.anchor.json: prev_anchor_sha256 does not chain to "
                                      "the previous anchor" % n)
                if (anc["first_seq"] != seg_first_global
                        or anc["last_seq"] != seg_last_global
                        or anc["record_count"] != len(recs)):
                    self._record_incident(n, "BROKEN_CHAIN", "seg-%05d.anchor.json seq accounting" % n)
                    raise LedgerError("BROKEN_CHAIN",
                                      "seg-%05d.anchor.json: seq accounting disagrees with the "
                                      "records (first/last/count)" % n)
                prev_anchor_sha = _sha(raw)
            else:
                # an UNCLOSED segment is legal only as the very last one (the live head).
                if idx != len(nums) - 1:
                    self._record_incident(n, "BROKEN_CHAIN", "seg-%05d.jsonl unsealed mid-history" % n)
                    raise LedgerError("BROKEN_CHAIN",
                                      "seg-%05d.jsonl: unsealed segment before the end (its "
                                      "anchor is missing)" % n)


class CAS:
    """Content-addressed store. A large artifact lives here; the LEDGER keeps only the
    sha pointer. Idempotent by construction (name == content hash), MAX_PATH-safe, and
    self-checking on read."""

    def __init__(self, root: str | os.PathLike):
        self._root = Path(root)
        os.makedirs(extended(self._root), exist_ok=True)

    def _blob_path(self, sha: str) -> Path:
        return self._root / (sha + ".blob")

    def put(self, data: bytes) -> str:
        """Write `data` under its own sha256 and return the hex digest. Idempotent: if a
        blob with that name already exists it is NOT rewritten (same content -> same
        name)."""
        if not isinstance(data, (bytes, bytearray)):
            raise LedgerError("BROKEN_CHAIN", "CAS.put takes bytes, not %s" % type(data).__name__)
        sha = _sha(bytes(data))
        p = self._blob_path(sha)
        if not os.path.exists(extended(p)):
            with open(extended(p), "wb") as fh:
                fh.write(data)
                fh.flush()
                os.fsync(fh.fileno())
        return sha

    def get(self, sha: str) -> bytes:
        """Return the blob for `sha`, with a READ-BACK HASH CHECK. A missing blob is
        ABSENT (NOT_FOUND), not UNREADABLE; a present blob whose bytes no longer hash to
        its own name is HASH_MISMATCH - corruption is refused, never handed back."""
        p = self._blob_path(sha)
        if not os.path.exists(extended(p)):
            raise LedgerError("NOT_FOUND",
                              "CAS blob %s is not stored (absent is not corrupt)" % sha)
        try:
            data = _read_bytes(p)
        except OSError as e:
            raise LedgerError("UNREADABLE", "CAS blob %s: %s" % (sha, e)) from e
        actual = _sha(data)
        if actual != sha:
            raise LedgerError("HASH_MISMATCH",
                              "CAS blob %s hashes to %s - the stored bytes were corrupted" %
                              (sha, actual))
        return data

    def has(self, sha: str) -> bool:
        return os.path.exists(extended(self._blob_path(sha)))