#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_mail - SPIKE 3 (F5 builder): the mailbox at N>2.

CONTRACT (docs/FINAL_ARCHITECTURE.md + brief): per-worker inbox directories; messages are
IMMUTABLE, uniquely named, carry sender identity + offset-aware timestamp + payload hash;
missing / empty / unreadable / stale are FOUR typed states; send and received are separate
recorded facts (receipt files); a dead mailbox is THE PHONE IS DEAD, never "no news."

Scar lineage: bts_phone's two costumes of one defect (wrong universe, wrong surface) -
here every address is derived from ONE mail root handed in explicitly (no resolution in
this module at all - the resolver spike owns that); the incumbent's missing send() (OA
API-08) - this one HAS a send, and send() proves delivery-side existence by read-back of
its own file; naive timestamps - epoch + offset both carried.
"""
from __future__ import annotations

import hashlib
import json
import os
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


class MailError(RuntimeError):
    """kind in {MAILBOX_MISSING, UNREADABLE, TORN_MESSAGE, SELF_SEND}."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


@dataclass(frozen=True)
class ProbeResult:
    state: str            # LIVE | EMPTY | MISSING | UNREADABLE | STALE
    unread: int
    oldest_unread_age: Optional[float]
    detail: str


def _now():
    t = time.time()
    local = time.localtime(t)
    off = -time.timezone + (3600 if local.tm_isdst else 0)
    return t, off


class Mailbox:
    """One worker's mail endpoint under a shared mail root. The root is HANDED IN -
    this module never resolves anything."""

    def __init__(self, mail_root: str | os.PathLike, worker_id: str):
        self.root = Path(mail_root)
        self.me = worker_id

    def _inbox(self, worker: str) -> Path:
        return self.root / worker / "inbox"

    def _receipts(self, worker: str) -> Path:
        return self.root / worker / "receipts"

    def register(self) -> None:
        """Create MY endpoint. Registering is explicit - a mailbox that appears as a
        side effect of a send is a mailbox nobody knows they own."""
        self._inbox(self.me).mkdir(parents=True, exist_ok=True)
        self._receipts(self.me).mkdir(parents=True, exist_ok=True)

    # ---------------- send ----------------
    def send(self, to: str, subject: str, body: str,
             requires_ack: bool = False) -> str:
        if to == self.me:
            raise MailError("SELF_SEND", "nobody talks to themselves (outbox==inbox scar)")
        inbox = self._inbox(to)
        if not inbox.is_dir():
            # THE PHONE IS DEAD - a missing recipient endpoint is a routing failure, not
            # a quiet no-op. Creating it silently would be a successful write to a place
            # the reader is not.
            raise MailError("MAILBOX_MISSING",
                            f"recipient {to!r} has no inbox at {inbox} - THE PHONE IS "
                            f"DEAD, not 'no news'")
        t, off = _now()
        mid = "%d-%s" % (int(t * 1000), uuid.uuid4().hex[:12])
        payload = {"id": mid, "from": self.me, "to": to, "subject": subject,
                   "body": body, "epoch": t, "utc_offset_s": off,
                   "requires_ack": requires_ack,
                   "body_sha256": hashlib.sha256(body.encode("utf-8")).hexdigest()}
        tmp = inbox / (mid + ".part")
        final = inbox / (mid + ".json")
        tmp.write_text(json.dumps(payload, indent=1), encoding="utf-8")
        os.replace(tmp, final)                     # single-volume atomic install
        # SEND-side read-back: the file exists and parses where the READER will look.
        back = json.loads(final.read_text(encoding="utf-8"))
        if back["body_sha256"] != payload["body_sha256"]:
            raise MailError("TORN_MESSAGE", f"read-back hash mismatch for {final}")
        return mid

    # ---------------- receive ----------------
    def unread(self) -> list[dict]:
        inbox = self._inbox(self.me)
        if not inbox.is_dir():
            raise MailError("MAILBOX_MISSING", f"my own inbox is missing: {inbox}")
        out = []
        acked = {p.stem.replace("read-", "") for p in self._receipts(self.me).glob("read-*.json")}
        for p in sorted(inbox.glob("*.json")):
            if p.stem in acked:
                continue
            try:
                d = json.loads(p.read_text(encoding="utf-8"))
            except (OSError, ValueError) as e:
                raise MailError("TORN_MESSAGE", f"{p}: {e}") from e
            if hashlib.sha256(d["body"].encode("utf-8")).hexdigest() != d["body_sha256"]:
                raise MailError("TORN_MESSAGE", f"{p}: body hash mismatch - half-written")
            out.append(d)
        return out

    def ack(self, message_id: str) -> None:
        """Received is a RECORDED FACT, separate from sent."""
        t, off = _now()
        r = self._receipts(self.me) / f"read-{message_id}.json"
        r.write_text(json.dumps({"id": message_id, "by": self.me,
                                 "epoch": t, "utc_offset_s": off}), encoding="utf-8")

    def receipt_for(self, to: str, message_id: str) -> bool:
        """Sender-side: has the recipient RECORDED reading my message?"""
        return (self._receipts(to) / f"read-{message_id}.json").exists()

    # ---------------- probe ----------------
    def probe(self, worker: str, stale_after_s: float = 24 * 3600) -> ProbeResult:
        """The four states, never collapsed. Probing is how a dead channel is told from a
        quiet one - the whole reason bts_phone exists, generalized."""
        inbox = self._inbox(worker)
        if not inbox.is_dir():
            return ProbeResult("MISSING", 0, None,
                               f"no endpoint for {worker!r} - THE PHONE IS DEAD")
        try:
            msgs = sorted(inbox.glob("*.json"))
        except OSError as e:
            return ProbeResult("UNREADABLE", 0, None, f"{inbox}: {e}")
        acked = {p.stem.replace("read-", "") for p in self._receipts(worker).glob("read-*.json")}
        pending = [p for p in msgs if p.stem not in acked]
        if not pending:
            return ProbeResult("EMPTY", 0, None, "endpoint live, no unread mail")
        oldest = min(p.stat().st_mtime for p in pending)
        age = time.time() - oldest
        if age > stale_after_s:
            return ProbeResult("STALE", len(pending), age,
                               f"oldest unread is {age/3600:.1f} h old - a letter nobody "
                               f"reads is a dead conversation, not a quiet one")
        return ProbeResult("LIVE", len(pending), age, "unread mail within freshness window")
