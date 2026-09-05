#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_mail - SPIKE 3 (F5 builder): the mailbox at N>2.

CONTRACT (docs/FINAL_ARCHITECTURE.md + brief): per-worker inbox directories; messages are
IMMUTABLE, uniquely named, carry sender identity + offset-aware timestamp + payload hash;
missing / empty / unreadable / stale are FOUR typed states; send and received are separate
recorded facts (receipt files); a dead mailbox is THE PHONE IS DEAD, never "no news."

F-55 (wishlist inter-orchestrator comms): hash-chained append (prev_hash + msg_sha256),
each note HMAC-signed with the writer id when a key is handed in, and send() is a
cosmos_lock fenced commit (ONE writer at a time, fencing tokens) when an Arbiter
is composed in. Unkeyed / unfenced remains the spike-local path so a unit test
does not have to stand up Core. Kernel always composes both.

Scar lineage: bts_phone's two costumes of one defect (wrong universe, wrong surface) -
here every address is derived from ONE mail root handed in explicitly (no resolution in
this module at all - the resolver spike owns that); the incumbent's missing send() (OA
API-08) - this one HAS a send, and send() proves delivery-side existence by read-back of
its own file; naive timestamps - epoch + offset both carried; BTS-MESH deletion was a
WRITE CONFLICT of two orchestrators with no arbiter - the chain + lock is that fix.
"""
from __future__ import annotations

import hashlib
import hmac as hmac_mod
import json
import os
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from cosmos_lock import Arbiter, StagedArtifact

GENESIS_HASH = "0" * 64
LEASE_TTL_S = 30.0
_SIG_EXCLUDED = ("msg_sha256", "writer_sig", "signed", "fence_token")


class MailError(RuntimeError):
    """kind in {MAILBOX_MISSING, UNREADABLE, TORN_MESSAGE, SELF_SEND,
    CHAIN_BREAK, FORGED_MESSAGE}."""

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


def resource_for(worker: str) -> str:
    """Lease resource the arbiter holds for one inbox. One writer at a time."""
    return "mail:%s" % worker


def _canon(payload: dict) -> bytes:
    body = {k: payload[k] for k in payload if k not in _SIG_EXCLUDED}
    return json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")


def msg_sha256(payload: dict) -> str:
    return hashlib.sha256(_canon(payload)).hexdigest()


def writer_sig(payload: dict, key: bytes | None, writer_id: str) -> str:
    """HMAC-SHA256 over the canonical note + writer id. Empty when unkeyed."""
    if not key:
        return ""
    return hmac_mod.new(key, _canon(payload) + writer_id.encode("utf-8"),
                        hashlib.sha256).hexdigest()


class Mailbox:
    """One worker's mail endpoint under a shared mail root. The root is HANDED IN -
    this module never resolves anything.

    `arbiter` (cosmos_lock.Arbiter) and `key` (install HMAC) are optional for
    spike-local tests. Kernel hands both in: send is then a fenced commit on
    mail:{to} and every note carries a writer signature.
    """

    def __init__(self, mail_root: str | os.PathLike, worker_id: str,
                 arbiter: Arbiter | None = None,
                 key: bytes | None = None,
                 lease_ttl_s: float = LEASE_TTL_S):
        self.root = Path(mail_root)
        self.me = worker_id
        self.arbiter = arbiter
        self.key = key
        self._lease_ttl_s = lease_ttl_s

    def _inbox(self, worker: str) -> Path:
        return self.root / worker / "inbox"

    def _receipts(self, worker: str) -> Path:
        return self.root / worker / "receipts"

    def register(self) -> None:
        """Create MY endpoint. Registering is explicit - a mailbox that appears as a
        side effect of a send is a mailbox nobody knows they own."""
        self._inbox(self.me).mkdir(parents=True, exist_ok=True)
        self._receipts(self.me).mkdir(parents=True, exist_ok=True)

    def _chain_head(self, inbox: Path) -> str:
        """Tip of the hash chain: chained note with the greatest (epoch, id).
        Genesis when the inbox has no chained notes. Legacy notes (no
        msg_sha256) are skipped — they predate F-55 and are not in the chain."""
        best = None  # (epoch, id, sha)
        for p in inbox.glob("*.json"):
            try:
                d = json.loads(p.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                continue
            sha = d.get("msg_sha256")
            if not sha:
                continue
            key = (float(d.get("epoch") or 0), str(d.get("id") or p.stem))
            if best is None or key > (best[0], best[1]):
                best = (key[0], key[1], sha)
        return best[2] if best else GENESIS_HASH

    def _build_payload(self, to: str, subject: str, body: str,
                       requires_ack: bool, prev_hash: str,
                       fence_token: object | None) -> dict:
        t, off = _now()
        mid = "%d-%s" % (int(t * 1000), uuid.uuid4().hex[:12])
        payload = {
            "id": mid, "from": self.me, "to": to, "subject": subject,
            "body": body, "epoch": t, "utc_offset_s": off,
            "requires_ack": requires_ack,
            "body_sha256": hashlib.sha256(body.encode("utf-8")).hexdigest(),
            "prev_hash": prev_hash,
        }
        if fence_token is not None:
            payload["fence_token"] = fence_token
        payload["msg_sha256"] = msg_sha256(payload)
        payload["writer_sig"] = writer_sig(payload, self.key, self.me)
        payload["signed"] = bool(self.key)
        return payload

    def _stage_note(self, inbox: Path, payload: dict) -> StagedArtifact:
        mid = payload["id"]
        tmp = inbox / (mid + ".part")
        final = inbox / (mid + ".json")
        tmp.write_text(json.dumps(payload, indent=1), encoding="utf-8")
        return StagedArtifact(src=tmp, dst=final, result=mid)

    def _readback(self, final: Path, payload: dict) -> None:
        back = json.loads(final.read_text(encoding="utf-8"))
        if back["body_sha256"] != payload["body_sha256"]:
            raise MailError("TORN_MESSAGE", f"read-back hash mismatch for {final}")
        if back.get("msg_sha256") != payload.get("msg_sha256"):
            raise MailError("TORN_MESSAGE", f"read-back chain hash mismatch for {final}")

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

        def stage(token=None):
            prev = self._chain_head(inbox)
            payload = self._build_payload(
                to, subject, body, requires_ack, prev, token)
            return self._stage_note(inbox, payload)

        if self.arbiter is not None:
            lease = self.arbiter.acquire(
                resource_for(to), self.me, ttl=self._lease_ttl_s)
            try:
                mid = self.arbiter.fenced_commit(lease, stage)
            finally:
                self.arbiter.release(lease)
        else:
            art = stage(None)
            os.replace(art.src, art.dst)
            mid = art.result

        final = inbox / (str(mid) + ".json")
        payload = json.loads(final.read_text(encoding="utf-8"))
        self._readback(final, payload)
        return str(mid)

    def _verify_note(self, p: Path, d: dict) -> None:
        if hashlib.sha256(d["body"].encode("utf-8")).hexdigest() != d["body_sha256"]:
            raise MailError("TORN_MESSAGE", f"{p}: body hash mismatch - half-written")
        if "msg_sha256" not in d:
            return  # legacy unchained note (pre-F-55)
        want = msg_sha256(d)
        if not hmac_mod.compare_digest(want, d["msg_sha256"]):
            raise MailError("TORN_MESSAGE",
                            f"{p}: msg_sha256 does not match canonical payload")
        if d.get("signed") and self.key:
            got = d.get("writer_sig") or ""
            expect = writer_sig(d, self.key, d.get("from") or "")
            if not got or not hmac_mod.compare_digest(got, expect):
                raise MailError("FORGED_MESSAGE",
                                f"{p}: writer_sig does not verify for from="
                                f"{d.get('from')!r} - a well-formed lie is still a lie")

    def _verify_chain(self, notes: list[tuple[Path, dict]]) -> None:
        """Hash-chained append: each chained note's prev_hash is the previous
        note's msg_sha256, genesis first. A fork or a planted lie is CHAIN_BREAK."""
        chained = [(p, d) for p, d in notes if d.get("msg_sha256")]
        chained.sort(key=lambda pd: (float(pd[1].get("epoch") or 0),
                                     str(pd[1].get("id") or pd[0].stem)))
        head = GENESIS_HASH
        for p, d in chained:
            prev = d.get("prev_hash")
            if prev != head:
                raise MailError(
                    "CHAIN_BREAK",
                    f"{p}: prev_hash {prev!r} does not chain to {head!r}")
            head = d["msg_sha256"]

    # ---------------- receive ----------------
    def unread(self) -> list[dict]:
        inbox = self._inbox(self.me)
        if not inbox.is_dir():
            raise MailError("MAILBOX_MISSING", f"my own inbox is missing: {inbox}")
        out = []
        acked = {p.stem.replace("read-", "") for p in self._receipts(self.me).glob("read-*.json")}
        loaded: list[tuple[Path, dict]] = []
        for p in sorted(inbox.glob("*.json")):
            try:
                d = json.loads(p.read_text(encoding="utf-8"))
            except (OSError, ValueError) as e:
                raise MailError("TORN_MESSAGE", f"{p}: {e}") from e
            self._verify_note(p, d)
            loaded.append((p, d))
            if p.stem in acked:
                continue
            out.append(d)
        self._verify_chain(loaded)
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
