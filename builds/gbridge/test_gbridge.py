#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest for gbridge slice 1. No external network anywhere: transports are injected
(loopback, canned fake, bot-doubles over the REAL MailboxTransport in a temp dir).
Refusals asserted BY KIND, repo style.
Runs under pytest OR as a plain script (exit 0/1).
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from datetime import datetime

from gbridge import (Answer, GBridge, GBridgeError, LoopbackTransport,
                     MailboxTransport, RefusalKind, WIRE_VERSION, XaiApiTransport,
                     _now, _sha256, run_gate)

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
            except GBridgeError as e:
                return e.kind == kind
            return False
        return inner
    return wrap


class CannedTransport:
    """Injected transport returning a fixed status - the pure-interface happy path."""

    def __init__(self, status="ok", answer="canned"):
        self.status, self.answer = status, answer
        self._rid = None

    def send(self, ask):
        self._rid = ask.request_id

    def poll(self, ask, final=False):
        return Answer(self._rid, self.status, self.answer)


class AnsweringBot(MailboxTransport):
    """Bot-double: on first poll, plays the team - reads the request file gbridge
    actually wrote and writes a valid reply atomically (write_reply)."""

    def poll(self, ask, final=False):
        reply = self.from_dir / (ask.request_id + ".json")
        if not reply.exists():
            req = json.loads((self.to_dir / (ask.request_id + ".json"))
                             .read_text(encoding="utf-8"))
            body = "answered:" + req["body_sha256"]
            self.write_reply(ask.request_id, "ok", body)
        return super().poll(ask, final)


class TornBot(MailboxTransport):
    """Bot-double that writes a reply whose hash never verifies - half-written forever.
    Uses a direct write_text (non-atomic) so poll's mid-write tolerance is exercised."""

    def poll(self, ask, final=False):
        reply = self.from_dir / (ask.request_id + ".json")
        if not reply.exists():
            reply.write_text(json.dumps(
                {"gbridge": WIRE_VERSION, "request_id": ask.request_id,
                 "status": "ok", "answer": "mangled", "body_sha256": "0" * 64}),
                encoding="utf-8")
        return super().poll(ask, final)


class WeirdStatusBot(MailboxTransport):
    """Bot-double with a valid hash but a status outside the enum."""

    def poll(self, ask, final=False):
        reply = self.from_dir / (ask.request_id + ".json")
        if not reply.exists():
            self.write_reply(ask.request_id, "vibing", "x")
        return super().poll(ask, final)


class MidWriteBot(MailboxTransport):
    """Writes truncated JSON on first poll (the non-atomic mid-write the HIGH
    critique names), then completes atomically. ask() must succeed, not TORN_REPLY."""

    def __init__(self, mail_root):
        super().__init__(mail_root)
        self._stage = 0

    def poll(self, ask, final=False):
        if self._stage == 0:
            reply = self.from_dir / (ask.request_id + ".json")
            reply.write_text('{"gbridge": 1, "request_id":', encoding="utf-8")
            self._stage = 1
        elif self._stage == 1:
            self.write_reply(ask.request_id, "ok", "completed-after-tear")
            self._stage = 2
        return super().poll(ask, final)


class EmptyReplyBot(MailboxTransport):
    """Present-but-empty file: poll must treat as not-yet, deadline as TORN_REPLY."""

    def poll(self, ask, final=False):
        reply = self.from_dir / (ask.request_id + ".json")
        if not reply.exists():
            reply.write_text("", encoding="utf-8")
        return super().poll(ask, final)


def main() -> int:
    RESULTS.clear()
    td = Path(tempfile.mkdtemp(prefix="gbridge_"))

    # ---- happy paths, no network ----
    br = GBridge(LoopbackTransport(), poll_interval_s=0.01)
    ans = br.ask("ping")
    check("loopback round-trip emits the live value",
          lambda: ans.status == "ok" and ans.answer == "loopback:" + _sha256("ping"))

    canned = GBridge(CannedTransport(status="needs_input"), poll_interval_s=0.01)
    check("injected transport: any enum status passes through",
          lambda: canned.ask("q").status == "needs_input")

    bot = AnsweringBot(td / "m1")
    bot.register()
    got = GBridge(bot, poll_interval_s=0.01).ask("real mailbox?", timeout_s=5.0)
    check("REAL mailbox round-trip: request written atomically, reply parsed+verified",
          lambda: got.status == "ok" and got.answer.startswith("answered:")
          and (bot.to_dir / (got.request_id + ".json")).exists())

    # ---- refusals, each BY KIND ----
    check("empty ask refuses BAD_REQUEST",
          expect("BAD_REQUEST")(lambda: br.ask("   ")))

    check("unregistered root refuses ROOT_MISSING (phone is dead, no silent mkdir)",
          expect("ROOT_MISSING")(
              lambda: GBridge(MailboxTransport(td / "nope")).ask("q", timeout_s=0.1)))

    empty = MailboxTransport(td / "m2")
    empty.register()
    check("no reply by deadline refuses TIMEOUT (request file left in place)",
          expect("TIMEOUT")(
              lambda: GBridge(empty, poll_interval_s=0.02).ask("q", timeout_s=0.15)))
    check("after TIMEOUT the request file is still collectible",
          lambda: len(list(empty.to_dir.glob("*.json"))) == 1)

    torn = TornBot(td / "m3")
    torn.register()
    check("reply that never verifies refuses TORN_REPLY at deadline (not before)",
          expect("TORN_REPLY")(
              lambda: GBridge(torn, poll_interval_s=0.02).ask("q", timeout_s=0.15)))

    weird = WeirdStatusBot(td / "m4")
    weird.register()
    check("status outside the enum refuses BAD_STATUS",
          expect("BAD_STATUS")(
              lambda: GBridge(weird, poll_interval_s=0.01).ask("q", timeout_s=5.0)))

    check("fallback XaiApiTransport with no key refuses NO_KEY",
          expect("NO_KEY")(
              lambda: GBridge(XaiApiTransport(api_key="")).ask("q", timeout_s=0.1)))
    check("fallback with a key still refuses NOT_WIRED in slice 1 (fail-closed)",
          expect("NOT_WIRED")(
              lambda: GBridge(XaiApiTransport(api_key="k")).ask("q", timeout_s=0.1)))

    # ---- HIGH: poll race / atomic reply / mid-write tolerance ----
    wr = MailboxTransport(td / "m5")
    wr.register()
    wr.write_reply("rid-atomic", "ok", "hello")
    final_p = wr.from_dir / "rid-atomic.json"
    part_p = wr.from_dir / "rid-atomic.part"
    check("write_reply installs atomically (final exists, no leftover .part)",
          lambda: final_p.is_file() and (not part_p.exists())
          and json.loads(final_p.read_text(encoding="utf-8"))["answer"] == "hello")

    mid = MidWriteBot(td / "m6")
    mid.register()
    mid_got = GBridge(mid, poll_interval_s=0.02).ask("q", timeout_s=2.0)
    check("mid-write truncated JSON is 'not yet'; completed reply then succeeds",
          lambda: mid_got.status == "ok" and mid_got.answer == "completed-after-tear")

    empty_bot = EmptyReplyBot(td / "m7")
    empty_bot.register()
    check("empty reply file at deadline is TORN_REPLY (present-but-invalid)",
          expect("TORN_REPLY")(
              lambda: GBridge(empty_bot, poll_interval_s=0.02).ask("q", timeout_s=0.15)))

    # ---- MED: typed kinds + body_sha256 is the text-field hash ----
    def unknown_kind_is_closed():
        try:
            GBridgeError("TIME_OUT", "x")
        except ValueError:
            return True
        return False

    check("typo kind TIME_OUT is refused at construction (typed refusals)",
          unknown_kind_is_closed)
    check("RefusalKind.TIMEOUT compares equal to the string TIMEOUT",
          lambda: GBridgeError(RefusalKind.TIMEOUT, "x").kind == "TIMEOUT"
          and GBridgeError("TIMEOUT", "x").kind == RefusalKind.TIMEOUT)

    hash_box = MailboxTransport(td / "m8")
    hash_box.register()
    try:
        GBridge(hash_box, poll_interval_s=0.02).ask("hash-me", timeout_s=0.1)
    except GBridgeError:
        pass
    req = json.loads(next(hash_box.to_dir.glob("*.json")).read_text(encoding="utf-8"))
    check("body_sha256 is sha256 of the text field, not the whole JSON document",
          lambda: req["body_sha256"] == _sha256("hash-me")
          and req["body_sha256"] != _sha256(json.dumps(req)))

    # ---- LOW-applied: tz-aware _now; filename stem must match field ----
    def now_matches_astimezone():
        t, off = _now()
        dt = datetime.now().astimezone()
        want = int(dt.utcoffset().total_seconds()) if dt.utcoffset() else 0
        return off == want and abs(t - dt.timestamp()) < 2.0

    check("_now offset matches datetime.now().astimezone() (not time.timezone shortcut)",
          now_matches_astimezone)

    class StemMismatchBot(MailboxTransport):
        def poll(self, ask, final=False):
            reply = self.from_dir / (ask.request_id + ".json")
            if not reply.exists():
                # Valid hash, but the JSON claims a different request_id.
                payload = {"gbridge": WIRE_VERSION, "request_id": "other-id",
                           "status": "ok", "answer": "x",
                           "body_sha256": _sha256("x")}
                reply.write_text(json.dumps(payload), encoding="utf-8")
            return super().poll(ask, final)

    stem = StemMismatchBot(td / "m9")
    stem.register()
    check("filename/field request_id mismatch is TORN_REPLY at deadline",
          expect("TORN_REPLY")(
              lambda: GBridge(stem, poll_interval_s=0.02).ask("q", timeout_s=0.15)))

    check("unregistered live-root for gate refuses ROOT_MISSING",
          expect("ROOT_MISSING")(
              lambda: run_gate(td / "gate_mail", td / "no-live")))

    # Isolated gate (temp sentinel + temp mail): proves run_gate writes files.
    # The Motif stage-6 proof is the LIVE run, not this check.
    iso_live = td / "iso_live"
    iso_live.mkdir()
    (iso_live / ".cosmos-root.json").write_text(
        json.dumps({"system": "COSMOS", "tree_id": "iso-test", "schema_version": 1}),
        encoding="utf-8")
    iso_proof = td / "STAGE6_GATE.json"
    iso = run_gate(td / "iso_mail", iso_live, proof_path=iso_proof)

    check("isolated run_gate ok (happy mailbox + TIMEOUT leftover)",
          lambda: iso["ok"] is True
          and iso["live_value"]["answer"].startswith("gate:")
          and iso["timeout"]["kind"] == "TIMEOUT"
          and Path(iso["happy"]["request_path"]).is_file()
          and Path(iso["timeout"]["request_left"]).is_file()
          and iso_proof.is_file()
          and json.loads(iso_proof.read_text(encoding="utf-8"))["emitted"] == iso["emitted"])

    # ---- report ----
    fails = 0
    for label, ok, err in RESULTS:
        mark = "PASS" if ok else "FAIL"
        fails += 0 if ok else 1
        print(f"[{mark}] {label}" + (f"  <- {err}" if err else ""))
    print(f"\n{len(RESULTS) - fails}/{len(RESULTS)} passed")
    return 0 if fails == 0 else 1


def test_gbridge():
    assert main() == 0


if __name__ == "__main__":
    sys.exit(main())
