#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Loopback tests: the ticket IS the pull, and an absent phone is UNREACHABLE.

Proves:
  * the pushed body answers every kind the ticket asked for — data,
    PERM_DENIED:<kind> (no capability) or NO_COLLECTOR:<kind> (granted,
    no reader). Never an absent key, never []
  * an unknown asked kind is reported, not smuggled into the body
  * NEGATIVE — unreachable phone: never-seen and stale projections both
    refuse with RefusalKind.UNREACHABLE; a projection that was fresh a
    moment ago goes UNREACHABLE once it ages past the deadline, so the
    verdict is MEASURED, not assumed. A wrong tree_id is IDENTITY_MISMATCH
  * the gate artifact carries emitted values (real statuses, real
    measured age, real source sha256), and flips reason never_seen→fresh
    after an actual pull cycle

No live :8770. rc=0 here is a green log. Stage-6 quotes
STAGE6_PHONE_PULL.json live_value.kind_status + live_value.age_s
measured against the live runtime root. An exit code is not evidence.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
import tempfile
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
PHONE_DIR = HERE
DT_DIR = HERE.parent / "cvm-dt"
COSMOS_DIR = HERE.parents[1] / "cosmos"
sys.path.insert(0, str(PHONE_DIR))
if DT_DIR.is_dir():
    sys.path.insert(0, str(DT_DIR))
if COSMOS_DIR.is_dir():
    sys.path.insert(0, str(COSMOS_DIR))

from cosmos_paths import CosmosPaths, write_sentinel  # noqa: E402

from cvm_dt import CoreClient, CvmDtError, RefusalKind  # noqa: E402
from cvm_snap import KNOWN_KINDS  # noqa: E402

from cvm_phone_clock import CvmPhoneClock, PHONE_ID, PUSH_PATH  # noqa: E402
from cvm_phone_pull import (  # noqa: E402
    DEFAULT_GRANTS, PHONE_DEADLINE_S, PROOF_NAME, collect_kinds, device_kind,
    phone_reach, phone_seen, require_phone, run_gate, statuses, unsupported,
)

TREE_ID = "KMesh-COSMOS-live"
RESULTS = []
SRC = (HERE / "cvm_phone_pull.py").read_text(encoding="utf-8")
BTS_IMPORT = re.compile(r"^\s*(?:from|import)\s+bts_\w+", re.M)
ASSIGN_OWNER = re.compile(
    r"""audio_owner["']\s*\]\s*=|audio_owner\s*=\s*["']"""
    r"""(?:phone|desktop)["']""")
ASKED = ["voice_session", "device", "notifications", "sms", "photos"]


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:                                            # noqa: BLE001
        RESULTS.append((label, False, "%s: %s" % (type(e).__name__, e)))


class _FakeCore(BaseHTTPRequestHandler):
    """HTTP double: GET /cvm/pull asks for ASKED kinds; POST /cvm/push stores."""

    token = "test-token"
    last_push = None
    cursor = "desk-1"

    def log_message(self, *args):                                     # noqa: ARG002
        return

    @classmethod
    def reset(cls):
        cls.last_push = None
        cls.cursor = "desk-1"

    def _send(self, code, obj):
        body = json.dumps(obj).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):                                                 # noqa: N802
        if self.headers.get("Authorization") != "Bearer " + self.token:
            return self._send(401, {"error": "UNAUTHORIZED"})
        if not self.path.startswith("/api/v1/cvm/pull"):
            return self._send(404, {"error": "NOT_FOUND"})
        return self._send(200, {
            "cvm": 1, "tree_id": TREE_ID, "issued_epoch": 1787800000.0,
            "pull": True, "kinds": list(ASKED), "cursor": type(self).cursor,
            "audio_owner": "desktop", "voice_client_timeout_s": 70.0,
            "core_kind": "ok", "client_id": PHONE_ID,
        })

    def do_POST(self):                                                # noqa: N802
        if self.headers.get("Authorization") != "Bearer " + self.token:
            return self._send(401, {"error": "UNAUTHORIZED"})
        if self.path.split("?", 1)[0] != PUSH_PATH:
            return self._send(404, {"error": "NOT_FOUND"})
        n = int(self.headers.get("Content-Length") or 0)
        try:
            body = json.loads((self.rfile.read(n) if n else b"{}").decode("utf-8"))
        except ValueError:
            return self._send(400, {"error": "BAD_SNAPSHOT"})
        type(self).last_push = body
        type(self).cursor = "phone-turn-1"
        return self._send(200, {
            "ok": True, "cvm": 1, "cursor_out": type(self).cursor,
            "idempotent": False, "stored": list((body.get("kinds") or {}).keys()),
            "audio_owner": "desktop", "claimed": False,
        })


def _serve(handler):
    httpd = HTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd


def _scratch():
    tmp = Path(tempfile.mkdtemp(prefix="cvm-phone-pull-test-"))
    write_sentinel(tmp, TREE_ID)
    for d in ("config", "state", "logs"):
        (tmp / d).mkdir()
    (tmp / "config" / "api_token.txt").write_text("test-token", encoding="utf-8")
    return tmp


def _write_turn(paths, obj):
    p = paths.state("cvm", "phone_turn.json")
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj), encoding="utf-8")
    return p


def test_ticket_kinds_are_honored_with_typed_status():
    """The ask is the pull: every asked known kind comes back typed."""
    _FakeCore.reset()
    tmp = _scratch()
    httpd = _serve(_FakeCore)
    base = "http://127.0.0.1:%d" % httpd.server_address[1]
    try:
        paths = CosmosPaths(tmp)
        client = CvmPhoneClock(
            CoreClient(base, "test-token"), paths, push_request_id="r-ask",
            kinds={"device": device_kind()},
            grants=("device", "notifications"))
        rec = client.cycle_once()
        body = _FakeCore.last_push or {}
        got = body.get("kinds") or {}
        st = statuses(got)
        print("kind_status: " + json.dumps(st, sort_keys=True)
              + "  unsupported: " + json.dumps(rec.get("unsupported_kinds")))
        return (
            # every asked KNOWN kind answered — none missing, none []
            sorted(got) == sorted(k for k in ASKED if k in KNOWN_KINDS)
            and st["device"] == "ok"
            # granted, but this build ships no notifications reader
            and st["notifications"] == "NO_COLLECTOR:notifications"
            # no capability at all
            and st["sms"] == "PERM_DENIED:sms"
            and st["voice_session"] == "PERM_DENIED:voice_session"
            and all(isinstance(v, dict) and v for v in got.values())
            and "photos" not in got
            and rec["unsupported_kinds"] == ["photos"]
            and rec["requested"] == ASKED
            and rec["kind_status"] == st
            and rec["audio_owner"] == "desktop"
            and rec["claimed"] is False
        )
    finally:
        httpd.shutdown()


def test_collect_kinds_fails_closed():
    """No ask → only what this build can speak for. Broken blob refuses."""
    empty = collect_kinds((), grants=DEFAULT_GRANTS,
                          data={"device": device_kind()})
    denied = collect_kinds(["sms"], grants=())
    garbage = collect_kinds(["device", "sms"], grants=("device", "sms"),
                            data={"device": {}, "sms": ["not a blob"]})
    return (
        list(empty) == ["device"]
        and statuses(denied) == {"sms": "PERM_DENIED:sms"}
        and denied["sms"] != []
        # a collector that returns nothing usable is TYPED, never [] and
        # never a body Core's filter_kinds would refuse
        and statuses(garbage) == {"device": "NO_COLLECTOR:device",
                                  "sms": "NO_COLLECTOR:sms"}
        and all(isinstance(v, dict) and v for v in garbage.values())
        and unsupported(["sms", "photos"]) == ["photos"]
        and PHONE_DEADLINE_S == 45.0
    )


def test_unreachable_phone_is_typed_never_optimistic():
    """NEGATIVE: never-seen, stale, and aged-out phones all refuse UNREACHABLE."""
    _FakeCore.reset()
    tmp = _scratch()
    paths = CosmosPaths(tmp)

    # (a) nothing has ever checked in
    never = phone_reach(paths, TREE_ID)
    never_kind = None
    try:
        require_phone(paths, TREE_ID)
    except CvmDtError as e:
        never_kind = e.kind

    # (b) a projection older than the deadline is not a live phone
    now = time.time()
    _write_turn(paths, {"cvm": 1, "tree_id": TREE_ID, "cursor": "old",
                        "last_seen_epoch": now - (PHONE_DEADLINE_S + 30.0),
                        "kinds": {"device": {"status": "ok"}}})
    stale = phone_reach(paths, TREE_ID, now=now)
    stale_kind = None
    try:
        require_phone(paths, TREE_ID, now=now)
    except CvmDtError as e:
        stale_kind = e.kind

    # (c) a REAL cycle stamps the projection; the same file is fresh now
    #     and unreachable once it ages past the deadline. Measured, not assumed.
    httpd = _serve(_FakeCore)
    base = "http://127.0.0.1:%d" % httpd.server_address[1]
    try:
        rec = CvmPhoneClock(CoreClient(base, "test-token"), paths,
                            push_request_id="r-reach",
                            kinds={"device": device_kind()}).cycle_once()
    finally:
        httpd.shutdown()
    fresh = phone_reach(paths, TREE_ID)
    aged = phone_reach(paths, TREE_ID, now=time.time() + PHONE_DEADLINE_S + 1.0)
    aged_kind = None
    try:
        require_phone(paths, TREE_ID,
                      now=time.time() + PHONE_DEADLINE_S + 1.0)
    except CvmDtError as e:
        aged_kind = e.kind
    seen = phone_seen(paths, TREE_ID)

    # (d) a projection from another tree is an identity refusal, not "fresh"
    _write_turn(paths, {"cvm": 1, "tree_id": "KMesh-OTHER",
                        "last_seen_epoch": time.time()})
    id_kind = None
    try:
        phone_reach(paths, TREE_ID)
    except CvmDtError as e:
        id_kind = e.kind

    print("reach: " + json.dumps({
        "never": never["live_value"], "stale": stale["live_value"],
        "fresh": fresh["live_value"], "aged": aged["live_value"],
    }, sort_keys=True, default=str))
    return (
        never["reachable"] is False
        and never["reason"] == "never_seen"
        and never["kind"] == str(RefusalKind.UNREACHABLE)
        and never["age_s"] is None
        and never["last_seen_epoch"] is None
        and never_kind == RefusalKind.UNREACHABLE
        and stale["reachable"] is False
        and stale["reason"] == "stale"
        and stale["age_s"] > PHONE_DEADLINE_S
        and stale_kind == RefusalKind.UNREACHABLE
        and fresh["reachable"] is True
        and fresh["reason"] == "fresh"
        and fresh["age_s"] is not None and fresh["age_s"] < PHONE_DEADLINE_S
        and fresh["source"] == "state/cvm/phone_turn.json"
        and fresh["kind_status"].get("device") == "ok"
        and abs(float(seen["last_seen_epoch"])
                - float(rec["last_seen_epoch"])) < 0.001
        and aged["reachable"] is False
        and aged["reason"] == "stale"
        and aged_kind == RefusalKind.UNREACHABLE
        and id_kind == RefusalKind.IDENTITY_MISMATCH
    )


def test_gate_artifact_binds_emitted_values():
    """Gate quotes real statuses + a measured age, and flips after a real pull."""
    _FakeCore.reset()
    tmp = _scratch()
    paths = CosmosPaths(tmp)
    proof = tmp / PROOF_NAME
    before = run_gate(str(tmp), str(proof))
    on_disk = json.loads(proof.read_text(encoding="utf-8"))

    httpd = _serve(_FakeCore)
    base = "http://127.0.0.1:%d" % httpd.server_address[1]
    try:
        CvmPhoneClock(CoreClient(base, "test-token"), paths,
                      push_request_id="r-gate",
                      kinds={"device": device_kind()}).cycle_once()
    finally:
        httpd.shutdown()
    after = run_gate(str(tmp), str(proof))

    clock_sha = hashlib.sha256(
        (HERE / "cvm_phone_clock.py").read_bytes()).hexdigest()
    lv, lv2 = before["live_value"], after["live_value"]
    print("gate emitted: " + before["emitted"] + " -> " + after["emitted"])
    return (
        before["ok"] is True
        and on_disk["emitted"] == before["emitted"]
        and lv["live_tree_id"] == TREE_ID
        and sorted(lv["asked_kinds"]) == sorted(KNOWN_KINDS)
        and lv["unanswered_kinds"] == []
        and lv["kind_status"]["device"] == "ok"
        and lv["kind_status"]["sms"] == "PERM_DENIED:sms"
        and set(lv["denied_kinds"]) == set(KNOWN_KINDS) - {"device"}
        # honest: no phone has checked in yet
        and lv["phone_reachable"] is False
        and lv["phone_reach_reason"] == "never_seen"
        and before["clock_sha256"] == clock_sha
        and before["emitted"].startswith("cvm-phone:" + TREE_ID + ":never_seen:")
        and "NO_SEEN" in before["emitted"]
        and clock_sha[:16] in before["emitted"]
        # after a REAL cycle the same gate reports a measured age
        and lv2["phone_reachable"] is True
        and lv2["phone_reach_reason"] == "fresh"
        and isinstance(lv2["age_s"], float)
        and lv2["age_s"] < PHONE_DEADLINE_S
        and lv2["cursor"]
        and after["emitted"] != before["emitted"]
        and ":fresh:" in after["emitted"]
    )


def test_source_hygiene():
    """No drive literals, no BTS, and the phone never claims the audio owner."""
    return (
        "V:\\" not in SRC
        and BTS_IMPORT.search(SRC) is None
        and ASSIGN_OWNER.search(SRC) is None
        and "audio.json" not in SRC
        and "handoff.json" not in SRC
        and "pull.json" not in SRC
        and "claim_desktop" not in SRC
    )


def main() -> int:
    check("ticket kinds[] is honored — every asked kind typed "
          "(ok / NO_COLLECTOR / PERM_DENIED), unknown kind reported not smuggled",
          test_ticket_kinds_are_honored_with_typed_status)
    check("collect_kinds fails closed (denied is a status, a dead collector "
          "is NO_COLLECTOR, never [] and never an invalid body)",
          test_collect_kinds_fails_closed)
    check("NEGATIVE: unreachable phone — never-seen / stale / aged-out all "
          "refuse UNREACHABLE; wrong tree is IDENTITY_MISMATCH",
          test_unreachable_phone_is_typed_never_optimistic)
    check("gate artifact binds emitted values (statuses + measured age; "
          "never_seen -> fresh after a real pull cycle)",
          test_gate_artifact_binds_emitted_values)
    check("source hygiene: no drive literal, no bts_, no owner claim",
          test_source_hygiene)
    ok = all(p for _, p, _ in RESULTS)
    for label, passed, err in RESULTS:
        print(("PASS" if passed else "FAIL") + "  " + label
              + (("  " + err) if err else ""))
    print("result: " + ("ok" if ok else "FAIL")
          + "  %d/%d" % (sum(1 for _, p, _ in RESULTS if p), len(RESULTS)))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
