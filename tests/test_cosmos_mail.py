#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest for cosmos_mail spike. Four states asserted distinctly; refusals BY KIND;
send/received as separate recorded facts; half-written message detected by hash.

F-55 (2026-08-31): hash-chained append, writer HMAC, cosmos_lock fenced send.
Those pins FAIL against the pre-change module (no prev_hash / no arbiter=);
that bite is cosmos/_bite_f55_mail.json all_bite=true, then this suite.
"""
from __future__ import annotations
import hashlib
import inspect
import json
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "cosmos"))
from cosmos_mail import Mailbox, MailError, GENESIS_HASH, msg_sha256
from cosmos_lock import Arbiter, LockError

RESULTS = []
LIVE_VALUE: dict = {}

def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:                                            # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))

def expect(kind):
    def wrap(f):
        def inner():
            try:
                f()
            except MailError as e:
                return e.kind == kind
            return False
        return inner
    return wrap


def main() -> int:
    td = Path(tempfile.mkdtemp(prefix="cosmos_mail_"))
    a, b, c = Mailbox(td, "F5"), Mailbox(td, "GROK"), Mailbox(td, "GEM")
    a.register(); b.register(); c.register()

    # ---- N>2 concurrent senders, zero collisions ----
    ids = [a.send("GEM", "s1", "from F5"), b.send("GEM", "s2", "from GROK")]
    check("two senders -> two files, zero collisions (N>2 works)",
          lambda: len(c.unread()) == 2 and len(set(ids)) == 2)
    check("messages carry sender identity + epoch + offset",
          lambda: all(("from" in m and "epoch" in m and "utc_offset_s" in m) for m in c.unread()))

    # ---- send vs received are SEPARATE recorded facts ----
    check("sender sees NO receipt before ack", lambda: not a.receipt_for("GEM", ids[0]))
    c.ack(ids[0])
    check("after ack, sender sees the receipt (received is a recorded fact)",
          lambda: a.receipt_for("GEM", ids[0]))
    check("acked message leaves unread; the other remains",
          lambda: [m["id"] for m in c.unread()] == [ids[1]])

    # ---- the four probe states, distinctly ----
    check("probe LIVE (unread within window)", lambda: a.probe("GEM").state == "LIVE")
    c.ack(ids[1])
    check("probe EMPTY (endpoint live, nothing unread)", lambda: a.probe("GEM").state == "EMPTY")
    check("probe MISSING for an unregistered worker (THE PHONE IS DEAD)",
          lambda: a.probe("NOBODY").state == "MISSING")
    mid = a.send("GROK", "old", "stale letter")
    old = td / "GROK" / "inbox"
    import os
    for p in old.glob("*.json"):
        os.utime(p, (time.time() - 90000, time.time() - 90000))
    check("probe STALE (old unread = dead conversation, not a quiet one)",
          lambda: a.probe("GROK", stale_after_s=86400).state == "STALE")

    # ---- refusals BY KIND ----
    check("send to missing mailbox -> MAILBOX_MISSING, no silent create",
          expect("MAILBOX_MISSING")(lambda: a.send("NOBODY", "x", "y")))
    check("self-send -> SELF_SEND (nobody talks to themselves)",
          expect("SELF_SEND")(lambda: a.send("F5", "x", "y")))
    # half-written message: plant a message with a wrong hash
    forged = td / "F5" / "inbox" / "999-forged.json"
    forged.write_text(json.dumps({"id": "999-forged", "from": "GROK", "to": "F5",
                                  "subject": "s", "body": "tampered", "epoch": 1,
                                  "utc_offset_s": 0, "requires_ack": False,
                                  "body_sha256": "0" * 64}), encoding="utf-8")
    check("half-written/tampered message -> TORN_MESSAGE by hash",
          expect("TORN_MESSAGE")(lambda: a.unread()))

    # ---- F-55: hash-chained append, writer signature, cosmos_lock ----
    f55_dir = Path(tempfile.mkdtemp(prefix="cosmos_mail_f55_"))
    f55_checks(f55_dir)

    bad = [(l, e) for l, ok, e in RESULTS if not ok]
    for label, ok, err in RESULTS:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label, ("  [" + err + "]") if err else ""))
    LIVE_VALUE.update({
        "checks": len(RESULTS),
        "passed": len(RESULTS) - len(bad),
        "refusal_kinds": sorted({
            "MAILBOX_MISSING", "SELF_SEND", "TORN_MESSAGE",
            "CHAIN_BREAK", "FORGED_MESSAGE",
        }),
        "genesis": GENESIS_HASH,
    })
    print("live_value: " + repr(LIVE_VALUE))
    print("SELFTEST %s - %d checks (4 probe states distinct, F-55 chain/sig/lock)"
          % ("PASS" if not bad else "FAIL", len(RESULTS)))
    return 0 if not bad else 1


def _expect_lock(kind):
    def wrap(f):
        def inner():
            try:
                f()
            except LockError as e:
                return e.kind == kind
            return False
        return inner
    return wrap


def f55_checks(td: Path) -> None:
    """Pins the three named F-55 requirements. Bite first against the
    predecessor that had none of them (cosmos/_bite_f55_mail.json)."""
    key = b"f55-writer-hmac-key-not-a-secret!!"

    sig = inspect.signature(Mailbox.__init__)
    check("Mailbox.__init__ takes arbiter= (cosmos_lock seam)",
          lambda: "arbiter" in sig.parameters)
    check("Mailbox.__init__ takes key= (writer HMAC)",
          lambda: "key" in sig.parameters)

    cow = Mailbox(td, "COW")
    grok = Mailbox(td, "GROK")
    cow.register()
    grok.register()
    i1 = cow.send("GROK", "n1", "one")
    i2 = cow.send("GROK", "n2", "two")
    msgs = {m["id"]: m for m in grok.unread()}
    m1, m2 = msgs[i1], msgs[i2]
    check("first send prev_hash is GENESIS (64 zero hex)",
          lambda: m1.get("prev_hash") == GENESIS_HASH)
    check("second send prev_hash equals first msg_sha256 (hash-chained append)",
          lambda: m2.get("prev_hash") == m1.get("msg_sha256") and bool(m1.get("msg_sha256")))
    check("messages carry writer_sig + signed flag",
          lambda: "writer_sig" in m1 and "signed" in m1)

    # Chain-break: well-formed body hash, lying prev_hash. Old unread()
    # returned it; the pin is a typed CHAIN_BREAK.
    planted = td / "GROK" / "inbox" / "0-lie.json"
    body = "ok-body"
    lie = {
        "id": "0-lie", "from": "COW", "to": "GROK", "subject": "lie",
        "body": body, "epoch": 1, "utc_offset_s": 0, "requires_ack": False,
        "body_sha256": hashlib.sha256(body.encode("utf-8")).hexdigest(),
        "prev_hash": "ab" * 32,
        "writer_sig": "", "signed": False,
    }
    lie["msg_sha256"] = msg_sha256(lie)
    planted.write_text(json.dumps(lie, indent=1), encoding="utf-8")
    check("planted prev_hash lie -> CHAIN_BREAK (not silently unread)",
          expect("CHAIN_BREAK")(lambda: grok.unread()))
    planted.unlink()

    # Keyed writer signature: tampering `from` is FORGED_MESSAGE.
    ktd = td / "keyed"
    ka = Mailbox(ktd, "COW", key=key)
    kb = Mailbox(ktd, "GROK", key=key)
    ka.register()
    kb.register()
    kid = ka.send("GROK", "signed", "payload")
    got = kb.unread()[0]
    check("keyed send is signed=true with a nonempty writer_sig",
          lambda: got.get("signed") is True and len(got.get("writer_sig") or "") == 64)
    inbox = ktd / "GROK" / "inbox"
    p = next(inbox.glob(kid + ".json"))
    d = json.loads(p.read_text(encoding="utf-8"))
    d["from"] = "INTRUDER"
    d["msg_sha256"] = msg_sha256(d)  # content hash consistent; writer_sig is still COW's
    p.write_text(json.dumps(d, indent=1), encoding="utf-8")
    check("tampered writer id on a signed note -> FORGED_MESSAGE",
          expect("FORGED_MESSAGE")(lambda: kb.unread()))

    # cosmos_lock: send acquires mail:{to}, fenced COMMIT, HELD serializes.
    ltd = td / "locked"
    ltd.mkdir()
    arb = Arbiter(ltd / "leases.jsonl", key=key)
    la = Mailbox(ltd, "COW", arbiter=arb, key=key)
    lb = Mailbox(ltd, "GROK", arbiter=arb, key=key)
    gem = Mailbox(ltd, "GEM", arbiter=arb, key=key)
    la.register()
    lb.register()
    gem.register()
    mid = la.send("GROK", "locked", "fenced")
    ev = [e.get("event") for e in arb.events() if e.get("resource") == "mail:GROK"]
    check("fenced send leases mail:{to} and COMMITs (GRANT+COMMIT_RESERVED+COMMIT+RELEASE)",
          lambda: ev[:4] == ["GRANT", "COMMIT_RESERVED", "COMMIT", "RELEASE"] and bool(mid))
    held = arb.acquire("mail:GROK", "intruder")
    check("send while mail:{to} is held -> LockError HELD (one writer)",
          _expect_lock("HELD")(lambda: la.send("GROK", "nope", "blocked")))
    arb.release(held)
    # Two senders, one arbiter, linear chain not a fork.
    x = la.send("GEM", "a", "from COW")
    y = lb.send("GEM", "b", "from GROK")
    chain = gem.unread()
    by = {m["id"]: m for m in chain}
    check("two locked senders produce a linear chain (second.prev == first.msg_sha256)",
          lambda: by[y]["prev_hash"] == by[x]["msg_sha256"])
    LIVE_VALUE["fenced_events"] = ev
    LIVE_VALUE["chain_head"] = by[y]["msg_sha256"]


def test_cosmos_mail():
    assert main() == 0


if __name__ == "__main__":
    sys.exit(main())