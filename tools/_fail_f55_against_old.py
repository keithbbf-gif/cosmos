#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prove the F-55 pins FAIL against the staged pre-change cosmos_mail.

The new test_cosmos_mail.py checks are the pins; this runner loads the
predecessor from _delme and applies the same assertions. A pin that PASSES
on the old module is not a pin.

  py -3.14 cosmos/_fail_f55_against_old.py
"""
from __future__ import annotations

import hashlib
import importlib.util
import inspect
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent / "cosmos"
OLD = HERE.parent / "_delme" / "predispose_cosmos_mail_f55_20260831T124826Z" / "cosmos_mail.py"
GENESIS = "0" * 64


def _load(path: Path):
    spec = importlib.util.spec_from_file_location("cosmos_mail_old", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["cosmos_mail_old"] = mod
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    old = _load(OLD)
    Mailbox = old.Mailbox
    pins = []

    def pin(name, fn):
        try:
            ok = bool(fn())
            err = ""
        except Exception as e:  # noqa: BLE001
            ok = False
            err = "%s: %s" % (type(e).__name__, e)
        pins.append({"name": name, "passed_on_old": ok, "err": err})

    sig = inspect.signature(Mailbox.__init__)
    pin("Mailbox.__init__ takes arbiter=",
        lambda: "arbiter" in sig.parameters)
    pin("Mailbox.__init__ takes key=",
        lambda: "key" in sig.parameters)
    pin("GENESIS_HASH exported",
        lambda: getattr(old, "GENESIS_HASH", None) == GENESIS)

    td = Path(tempfile.mkdtemp(prefix="fail_f55_old_"))
    a = Mailbox(td, "COW")
    b = Mailbox(td, "GROK")
    a.register()
    b.register()
    i1 = a.send("GROK", "n1", "one")
    i2 = a.send("GROK", "n2", "two")
    msgs = {m["id"]: m for m in b.unread()}
    m1, m2 = msgs[i1], msgs[i2]
    pin("first send prev_hash is GENESIS",
        lambda: m1.get("prev_hash") == GENESIS)
    pin("second send prev_hash equals first msg_sha256",
        lambda: m2.get("prev_hash") == m1.get("msg_sha256") and bool(m1.get("msg_sha256")))
    pin("messages carry writer_sig + signed",
        lambda: "writer_sig" in m1 and "signed" in m1)

    body = "ok-body"
    lie = {
        "id": "0-lie", "from": "COW", "to": "GROK", "subject": "lie",
        "body": body, "epoch": 1, "utc_offset_s": 0, "requires_ack": False,
        "body_sha256": hashlib.sha256(body.encode("utf-8")).hexdigest(),
        "prev_hash": "ab" * 32, "msg_sha256": "cd" * 32,
        "writer_sig": "", "signed": False,
    }
    (td / "GROK" / "inbox" / "0-lie.json").write_text(
        json.dumps(lie, indent=1), encoding="utf-8")

    def chain_break():
        try:
            b.unread()
        except Exception as e:  # noqa: BLE001
            return getattr(e, "kind", "") == "CHAIN_BREAK"
        return False
    pin("planted prev_hash lie -> CHAIN_BREAK", chain_break)

    ksrc = (HERE / "cosmos_kernel.py").read_text(encoding="utf-8")
    # The LIVE kernel is already wired; the pin against OLD is the staged copy.
    oldk = (OLD.parent / "cosmos_kernel.py").read_text(encoding="utf-8")
    pin("staged kernel wires arbiter=",
        lambda: "arbiter=" in oldk and "Mailbox(" in oldk)
    pin("staged kernel does NOT wire arbiter (pre-change)",
        lambda: "arbiter=" not in oldk)

    failed_as_required = [p for p in pins if not p["passed_on_old"]]
    # The staged-kernel-does-NOT-wire pin is inverted: it SHOULD pass on old.
    # Split: pins that must FAIL on old vs the control that must PASS on old.
    must_fail = [p for p in pins if p["name"] != "staged kernel does NOT wire arbiter (pre-change)"]
    control = [p for p in pins if p["name"] == "staged kernel does NOT wire arbiter (pre-change)"]
    all_new_pins_failed = all(not p["passed_on_old"] for p in must_fail) and all(
        p["passed_on_old"] for p in control)
    rec = {
        "ok": all_new_pins_failed,
        "all_new_pins_failed": all_new_pins_failed,
        "impl": str(OLD),
        "pins": pins,
        "n_must_fail": len(must_fail),
        "n_failed_on_old": sum(1 for p in must_fail if not p["passed_on_old"]),
        "live_kernel_has_arbiter": "arbiter=" in ksrc,
    }
    out = HERE / "_fail_f55_against_old.json"
    out.write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(rec, indent=1))
    print("all_new_pins_failed=%s  %d/%d failed on old"
          % (all_new_pins_failed, rec["n_failed_on_old"], rec["n_must_fail"]))
    return 0 if all_new_pins_failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
