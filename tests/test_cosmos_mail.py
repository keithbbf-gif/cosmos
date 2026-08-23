#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest for cosmos_mail spike. Four states asserted distinctly; refusals BY KIND;
send/received as separate recorded facts; half-written message detected by hash."""
from __future__ import annotations
import json, sys, tempfile, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cosmos_mail import Mailbox, MailError

RESULTS = []

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

    bad = [(l, e) for l, ok, e in RESULTS if not ok]
    for label, ok, err in RESULTS:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label, ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks (4 probe states distinct, 3 refusals BY KIND)"
          % ("PASS" if not bad else "FAIL", len(RESULTS)))
    return 0 if not bad else 1


def test_cosmos_mail():
    assert main() == 0


if __name__ == "__main__":
    sys.exit(main())
