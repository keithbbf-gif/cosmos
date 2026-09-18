#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bite F-55: the three named mailbox requirements fail on pre-change cosmos_mail.

Prove, before belief, that current (or a staged predecessor) cosmos_mail:
  * does not emit prev_hash / msg_sha256 / writer_sig on send
  * has no hash-chained append (a planted prev_hash lie is unread()able)
  * Mailbox.__init__ does not take arbiter= or key=
  * Kernel.mail is not composed onto the Arbiter

Run:
  py -3.14 cosmos/_bite_f55_mail.py
  py -3.14 cosmos/_bite_f55_mail.py --impl _delme/predispose_cosmos_mail_f55_20260831T124826Z/cosmos_mail.py
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent / "cosmos"
REPO = HERE.parent
GENESIS = "0" * 64


def _load(path: Path, name: str = "cosmos_mail_under_test"):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def _src_hits(text: str) -> dict:
    return {
        "prev_hash": bool(re.search(r"prev_hash", text)),
        "chain": bool(re.search(r"chain", text, re.I)),
        "lock": bool(re.search(r"cosmos_lock|\barbiter\b|fenced_commit", text)),
        "fenc": bool(re.search(r"fenc", text, re.I)),
        "writer_sig": bool(re.search(r"writer_sig", text)),
    }


def bite(impl: Path) -> dict:
    src = impl.read_text(encoding="utf-8")
    hits = _src_hits(src)
    mail = _load(impl)
    Mailbox = mail.Mailbox
    MailError = mail.MailError

    td = Path(tempfile.mkdtemp(prefix="bite_f55_"))
    a = Mailbox(td, "COW")
    b = Mailbox(td, "GROK")
    a.register()
    b.register()

    mid1 = a.send("GROK", "hello", "first")
    mid2 = a.send("GROK", "hello", "second")
    unread = b.unread()
    by_id = {m["id"]: m for m in unread}

    m1 = by_id[mid1]
    m2 = by_id[mid2]
    has_prev = "prev_hash" in m1 and "prev_hash" in m2
    has_msg = "msg_sha256" in m1 and "msg_sha256" in m2
    has_sig = "writer_sig" in m1 and "writer_sig" in m2
    chained = bool(
        has_prev and has_msg
        and m1.get("prev_hash") == GENESIS
        and m2.get("prev_hash") == m1.get("msg_sha256")
    )

    # Plant a chain-break. Old unread() only checks body_sha256, so a
    # well-formed lie with a bogus prev_hash is still returned.
    planted = td / "GROK" / "inbox" / "1-planted.json"
    planted.write_text(json.dumps({
        "id": "1-planted",
        "from": "COW",
        "to": "GROK",
        "subject": "lie",
        "body": "ok-body",
        "epoch": 1,
        "utc_offset_s": 0,
        "requires_ack": False,
        "body_sha256": __import__("hashlib").sha256(b"ok-body").hexdigest(),
        "prev_hash": "deadbeef" * 8,
        "msg_sha256": "cafebabe" * 8,
        "writer_sig": "",
        "signed": False,
    }, indent=1), encoding="utf-8")
    chain_break_kind = None
    chain_break_raised = False
    try:
        b.unread()
    except Exception as e:  # noqa: BLE001
        chain_break_raised = True
        chain_break_kind = getattr(e, "kind", type(e).__name__)

    arbiter_kw = False
    try:
        Mailbox(td, "X", arbiter=object(), key=b"k" * 32)
        arbiter_kw = True
    except TypeError:
        arbiter_kw = False

    # Kernel composition: does cosmos_kernel pass arbiter= into Mailbox?
    ksrc = (HERE / "cosmos_kernel.py").read_text(encoding="utf-8")
    kernel_wires = "arbiter=None if read_only else self.arbiter" in ksrc

    claims = {
        "source_has_prev_hash": hits["prev_hash"],
        "source_has_chain": hits["chain"],
        "source_has_lock": hits["lock"],
        "source_has_fenc": hits["fenc"],
        "source_has_writer_sig": hits["writer_sig"],
        "payload_has_prev_hash": has_prev,
        "payload_has_msg_sha256": has_msg,
        "payload_has_writer_sig": has_sig,
        "two_sends_chain": chained,
        "planted_chain_lie_refused": chain_break_raised,
        "mailbox_accepts_arbiter_key": arbiter_kw,
        "kernel_wires_arbiter": kernel_wires,
    }
    # Bite is true when the OLD code lacks the feature.
    all_bite = not any((
        claims["payload_has_prev_hash"],
        claims["two_sends_chain"],
        claims["planted_chain_lie_refused"],
        claims["mailbox_accepts_arbiter_key"],
        claims["kernel_wires_arbiter"],
    ))
    out = {
        "ok": True,
        "impl": str(impl),
        "all_bite": all_bite,
        "claims": claims,
        "m1_keys": sorted(m1.keys()),
        "chain_break_kind": chain_break_kind,
        "scratch": str(td),
    }
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--impl", default=str(HERE / "cosmos_mail.py"))
    ap.add_argument("--out", default=str(HERE / "_bite_f55_mail.json"))
    args = ap.parse_args()
    rec = bite(Path(args.impl))
    Path(args.out).write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(rec, indent=1))
    print("all_bite=%s" % rec["all_bite"])
    return 0 if rec["all_bite"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
