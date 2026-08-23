#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_ingress - THE ENVELOPE GATE (F5 builder). CRITIC B3: mount-visible writes
were already real; the architecture says a mount write is INGRESS until the native
service verifies bytes/hash/schema/identity and ledgers INGRESS_ACCEPTED.

A sandbox (or any untrusted surface) writes an ENVELOPE: a JSON file declaring sender,
kind, payload length, and payload sha256, beside a payload file. accept_all() verifies
each declaration against the actual bytes, ledgers INGRESS_ACCEPTED or INGRESS_REFUSED,
and only ACCEPTED envelopes become real (e.g., a job submission). Nothing is deleted -
refused envelopes are renamed .refused so the evidence stays.
"""
from __future__ import annotations

import hashlib
import json
import time
import uuid
from pathlib import Path

from cosmos_ledger import Ledger

KNOWN_KINDS = {"job", "message", "return"}


class IngressError(RuntimeError):
    """kind in {BAD_ENVELOPE, SHORT_PAYLOAD, HASH_MISMATCH, UNKNOWN_KIND}."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


def write_envelope(ingress_dir: Path, sender: str, kind: str, payload: bytes) -> Path:
    """The UNTRUSTED side's helper: drop payload + declaration. (In production the
    sandbox runs this; nothing it writes is real until accept_all verifies it.)"""
    ingress_dir.mkdir(parents=True, exist_ok=True)
    eid = "%d-%s" % (int(time.time() * 1000), uuid.uuid4().hex[:8])
    (ingress_dir / (eid + ".payload")).write_bytes(payload)
    env = {"envelope_id": eid, "sender": sender, "kind": kind,
           "payload_len": len(payload),
           "payload_sha": hashlib.sha256(payload).hexdigest()}
    p = ingress_dir / (eid + ".envelope.json")
    p.write_text(json.dumps(env, indent=1), encoding="utf-8")
    return p


class IngressGate:
    """The NATIVE side. accept_all() is the only path from mount-visible bytes to
    operational reality."""

    def __init__(self, ledger: Ledger, ingress_dir: Path):
        self.ledger = ledger
        self.dir = Path(ingress_dir)

    def accept_all(self) -> dict:
        accepted, refused = [], []
        self.dir.mkdir(parents=True, exist_ok=True)
        for envp in sorted(self.dir.glob("*.envelope.json")):
            try:
                body = self._verify_one(envp)
                self.ledger.append("INGRESS_ACCEPTED",
                                   {"envelope_id": body["envelope_id"],
                                    "sender": body["sender"], "kind": body["kind"],
                                    "payload_sha": body["payload_sha"]})
                envp.rename(envp.with_suffix(".json.accepted"))
                accepted.append(body)
            except IngressError as e:
                self.ledger.append("INGRESS_REFUSED",
                                   {"envelope": envp.name, "kind": e.kind,
                                    "detail": str(e)[:200]})
                envp.rename(envp.with_suffix(".json.refused"))
                refused.append({"envelope": envp.name, "kind": e.kind})
        return {"accepted": accepted, "refused": refused}

    def _verify_one(self, envp: Path) -> dict:
        try:
            env = json.loads(envp.read_text(encoding="utf-8"))
        except (OSError, ValueError) as e:
            raise IngressError("BAD_ENVELOPE", f"{envp.name}: {e}") from e
        for k in ("envelope_id", "sender", "kind", "payload_len", "payload_sha"):
            if k not in env:
                raise IngressError("BAD_ENVELOPE", f"{envp.name}: missing {k}")
        if env["kind"] not in KNOWN_KINDS:
            raise IngressError("UNKNOWN_KIND", f"{env['kind']!r} not in {sorted(KNOWN_KINDS)}")
        payload_path = self.dir / (env["envelope_id"] + ".payload")
        try:
            data = payload_path.read_bytes()
        except OSError as e:
            raise IngressError("BAD_ENVELOPE", f"payload missing: {payload_path}") from e
        if len(data) != env["payload_len"]:
            raise IngressError("SHORT_PAYLOAD",
                               f"{env['envelope_id']}: consumed {len(data)} != declared "
                               f"{env['payload_len']} - the mount's signature")
        if hashlib.sha256(data).hexdigest() != env["payload_sha"]:
            raise IngressError("HASH_MISMATCH", env["envelope_id"])
        env["payload"] = data
        return env