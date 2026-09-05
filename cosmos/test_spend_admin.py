#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest: POST /api/v1/spend (F-03) - the WRITE side of the money surface.

Two layers, both against real objects (a real installed root, a real Kernel, a
real hash-chained ledger, a real ThreadingHTTPServer):

  A. the module - cosmos_spend_admin.handle_post: validation, the widen gate,
     the below-outstanding gate, the atomic write, the round-trip proof, and
     the LEDGER RECORD that answers who changed what from what to what.
  B. the route - a live Service on a loopback port: bearer required, body
     bounded BEFORE the read, and a real 409 -> 200 -> GET round trip.

THE ONE THAT MATTERS: a cap is never silently widened. Every refusal below is
asserted together with the cap that did NOT move - a typed error beside an
unchanged number, not a typed error on its own.

Run:  py -3.14 cosmos/test_spend_admin.py
"""
from __future__ import annotations
import json
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cosmos_kernel import Kernel, install                          # noqa: E402
from cosmos_service import Service                                 # noqa: E402
from cosmos_spendguard import SpendGuard                           # noqa: E402
from cosmos_spend_admin import handle_post                         # noqa: E402

RESULTS = []
ACTOR = "bearer:0123456789abcdef"


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:                                         # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


def cap_of(kernel, rail):
    """The rail's cap as the LEDGER shows it, re-folded from disk."""
    row = kernel.spend.audit()["rails"].get(rail)
    return None if row is None else row["cap_usd"]


def events(kernel, name):
    return [r for r in kernel.ledger.verify() if r["event"] == name]


def main() -> int:                                                 # noqa: C901
    td = Path(tempfile.mkdtemp(prefix="cosmos_f03_"))

    # ======================= A. the module =======================
    root = td / "mod"
    install(root, tree_id="f03-mod")
    k = Kernel(root, worker="core")
    cfg = k.paths.config("spendguard_config.json")
    guard = SpendGuard(k.paths.config("spendguard_state.json"),
                       config_file=cfg, ledger=k.ledger)

    def post(payload, actor=ACTOR):
        return handle_post(k, guard, cfg, payload, actor, turn_default=60)

    # ---- creating a budget where none existed is WIDENING ----
    code, body = post({"rail": "f03-fresh", "cap_usd": 5.0})
    check("new rail without allow_widen -> 409 WIDEN_REQUIRES_CONFIRM",
          lambda: code == 409 and body["error"] == "WIDEN_REQUIRES_CONFIRM")
    check("...and the rail STILL has no budget (nothing was widened)",
          lambda: cap_of(k, "f03-fresh") is None)
    check("...and the refusal left a SPEND_CAP_REFUSED trace naming the actor",
          lambda: any(r["payload"]["actor"] == ACTOR
                      and r["payload"]["refused"] == "WIDEN_REQUIRES_CONFIRM"
                      and r["payload"]["requested_cap_usd"] == 5.0
                      for r in events(k, "SPEND_CAP_REFUSED")))

    # ---- the truthy-string trap: "false" must not widen ----
    code, body = post({"rail": "f03-fresh", "cap_usd": 5.0, "allow_widen": "false"})
    check('allow_widen:"false" (truthy string) -> 400 BAD_FIELD, not consent',
          lambda: code == 400 and body["error"] == "BAD_FIELD")
    check("...and the rail STILL has no budget",
          lambda: cap_of(k, "f03-fresh") is None)

    # ---- the confirmed create ----
    code, body = post({"rail": "f03-fresh", "cap_usd": 5.0, "allow_widen": True,
                       "reason": "F-03 selftest"})
    check("confirmed create -> 200 and round_trip.verified",
          lambda: code == 200 and body["round_trip"]["verified"] is True)
    check("...and the re-read from the chain shows $5.00",
          lambda: cap_of(k, "f03-fresh") == 5.0)
    check("...and the BUDGET_SET says WHO / FROM / TO / WHY, in one record",
          lambda: any(r["payload"].get("actor") == ACTOR
                      and r["payload"]["rail"] == "f03-fresh"
                      and r["payload"]["prev_cap_usd"] is None
                      and r["payload"]["cap_usd"] == 5.0
                      and r["payload"]["direction"] == "create"
                      and r["payload"]["confirmed_widen"] is True
                      and r["payload"]["reason"] == "F-03 selftest"
                      and r["payload"]["source"] == "POST /api/v1/spend"
                      for r in events(k, "BUDGET_SET")))
    check("...and the record carries NO token material, only a hash prefix",
          lambda: all("token" not in json.dumps(r["payload"]).lower()
                      for r in events(k, "BUDGET_SET")))

    # ---- raising an existing cap is widening ----
    code, body = post({"rail": "f03-fresh", "cap_usd": 9.0})
    check("raise 5 -> 9 without allow_widen -> 409",
          lambda: code == 409 and body["error"] == "WIDEN_REQUIRES_CONFIRM")
    check("...and the cap is still $5.00 (the refusal is the behavior)",
          lambda: cap_of(k, "f03-fresh") == 5.0)

    # ---- lowering a cap needs no ceremony ----
    code, body = post({"rail": "f03-fresh", "cap_usd": 2.0})
    check("lower 5 -> 2 with no flags -> 200 (narrowing is always allowed)",
          lambda: code == 200 and body["direction"] == "narrow")
    check("...and the chain re-reads $2.00",
          lambda: cap_of(k, "f03-fresh") == 2.0)

    # ---- expiry is budget: removing one widens ----
    future = 2_000_000_000.0
    post({"rail": "exp-rail", "cap_usd": 3.0, "expires_epoch": future,
          "allow_widen": True})
    code, body = post({"rail": "exp-rail", "cap_usd": 3.0, "expires_epoch": None})
    check("removing an expiry at the same cap -> 409 (time is budget)",
          lambda: code == 409 and body["error"] == "WIDEN_REQUIRES_CONFIRM")
    code, body = post({"rail": "exp-rail", "cap_usd": 3.0,
                       "expires_epoch": future - 86400})
    check("pulling an expiry EARLIER at the same cap -> 200 narrow",
          lambda: code == 200 and body["direction"] == "narrow")

    # ---- a cap under what is already committed ----
    k.spend.set_budget("busy", 10.0)
    k.spend.guarded_call("busy", 1.0, lambda: {"usd": 1.0})
    code, body = post({"rail": "busy", "cap_usd": 0.5})
    check("cap under settled+reserved -> 409 BELOW_OUTSTANDING",
          lambda: code == 409 and body["error"] == "BELOW_OUTSTANDING")
    check("...and the cap did not move",
          lambda: cap_of(k, "busy") == 10.0)
    code, body = post({"rail": "busy", "cap_usd": 0.5,
                       "allow_below_outstanding": True})
    check("...and it IS allowed when the caller means it explicitly",
          lambda: code == 200 and cap_of(k, "busy") == 0.5)

    # ---- typed refusals on bad input ----
    for label, payload, kind in [
            ("negative cap", {"rail": "r", "cap_usd": -1}, "BAD_CAP"),
            ("boolean cap", {"rail": "r", "cap_usd": True}, "BAD_CAP"),
            ("string cap", {"rail": "r", "cap_usd": "5"}, "BAD_CAP"),
            ("cap over the ceiling", {"rail": "r", "cap_usd": 1e9}, "BAD_CAP"),
            ("missing cap", {"rail": "r"}, "BAD_CAP"),
            ("empty rail", {"rail": "", "cap_usd": 1}, "BAD_RAIL"),
            ("spaced rail", {"rail": "a b", "cap_usd": 1}, "BAD_RAIL"),
            ("non-string rail", {"rail": 7, "cap_usd": 1}, "BAD_RAIL"),
            ("expiry in the year 90000",
             {"rail": "r", "cap_usd": 1, "expires_epoch": 9e12}, "BAD_EXPIRY"),
            ("string expiry",
             {"rail": "r", "cap_usd": 1, "expires_epoch": "soon"}, "BAD_EXPIRY"),
            ("unknown field", {"rail": "r", "cap_usd": 1, "cap": 9}, "BAD_FIELD"),
            ("empty body", {}, "BAD_TARGET"),
            ("both targets", {"rail": "r", "cap_usd": 1,
                              "thresholds": {"day_usd": 1}}, "BAD_TARGET"),
            ("body is a list", [1, 2], "BAD_REQUEST"),
            ("unknown threshold", {"thresholds": {"bogus": 1}}, "BAD_THRESHOLD"),
            ("threshold out of range",
             {"thresholds": {"day_usd": 1e6}}, "BAD_THRESHOLD"),
            ("fractional rate_per_min",
             {"thresholds": {"rate_per_min": 1.5}}, "BAD_THRESHOLD"),
            ("empty thresholds", {"thresholds": {}}, "BAD_THRESHOLD")]:
        c, b = post(payload)
        check(f"{label} -> 400 {kind}",
              lambda c=c, b=b, kind=kind: c == 400 and b["error"] == kind)
    check("no rail named 'r' was created by any of those refusals",
          lambda: cap_of(k, "r") is None)

    # ---- thresholds ----
    cfg.write_text(json.dumps({"session_usd": 0.5, "day_usd": 3.0,
                               "rate_per_min": 20,
                               "keep_me": "not a threshold"}, indent=1),
                   encoding="utf-8")
    code, body = post({"thresholds": {"day_usd": 9.0}})
    check("raising day_usd 3 -> 9 without allow_widen -> 409",
          lambda: code == 409 and body["error"] == "WIDEN_REQUIRES_CONFIRM")
    check("...and the breaker still reads a $3.00 day cap",
          lambda: guard.audit()["day_cap_usd"] == 3.0)
    code, body = post({"thresholds": {"day_usd": 1.0, "rate_per_min": 5},
                       "reason": "tighten"})
    check("lowering day_usd and rate_per_min -> 200 (narrowing)",
          lambda: code == 200 and body["changed"]["day_usd"]["from"] == 3.0
          and body["changed"]["day_usd"]["to"] == 1.0)
    check("...and the LIVE breaker re-reads them without a restart",
          lambda: guard.audit()["day_cap_usd"] == 1.0
          and guard.audit()["rate_per_min"] == 5)
    check("...and the unrelated config key was preserved, not clobbered",
          lambda: json.loads(cfg.read_text(encoding="utf-8"))["keep_me"]
          == "not a threshold")
    check("...and a SPEND_THRESHOLD_CHANGED record names actor + from/to",
          lambda: any(r["payload"]["actor"] == ACTOR
                      and r["payload"]["changed"]["rate_per_min"]
                      == {"from": 20, "to": 5}
                      for r in events(k, "SPEND_THRESHOLD_CHANGED")))
    code, body = post({"thresholds": {"day_usd": 9.0}, "allow_widen": True})
    check("confirmed widen of day_usd -> 200 and the breaker shows $9.00",
          lambda: code == 200 and guard.audit()["day_cap_usd"] == 9.0)

    # a config that exists and does not parse is a REFUSAL, never an overwrite
    cfg.write_text("{ not json", encoding="utf-8")
    code, body = post({"thresholds": {"day_usd": 0.5}})
    check("unparseable config -> 500 CURRENT_UNREADABLE (no blind overwrite)",
          lambda: code == 500 and body["error"] == "CURRENT_UNREADABLE")
    check("...and the unreadable file was left exactly as it was",
          lambda: cfg.read_text(encoding="utf-8") == "{ not json")
    cfg.write_text("{}", encoding="utf-8")

    # ======================= B. the live route =======================
    root2 = td / "svc"
    install(root2, tree_id="f03-svc")
    k2 = Kernel(root2, worker="core")
    svc = Service(k2, host="127.0.0.1", port=0)
    svc.serve_background()
    base = f"http://127.0.0.1:{svc.port}"

    def http(method, path, obj=None, token=None, raw=None, clen=None):
        data = raw if raw is not None else (
            json.dumps(obj).encode("utf-8") if obj is not None else None)
        req = urllib.request.Request(base + path, data=data, method=method)
        if token != "":
            req.add_header("Authorization",
                           "Bearer " + (svc.token if token is None else token))
        if data is not None:
            req.add_header("Content-Type", "application/json")
        if clen is not None:
            req.add_header("Content-Length", str(clen))
        try:
            with urllib.request.urlopen(req, timeout=15) as r:
                return r.status, json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read().decode("utf-8"))

    code, body = http("POST", "/api/v1/spend",
                      {"rail": "f03-live", "cap_usd": 1.0}, token="")
    check("POST /api/v1/spend with NO bearer -> 401",
          lambda: code == 401 and body["error"] == "UNAUTHORIZED")
    code, body = http("POST", "/api/v1/spend",
                      {"rail": "f03-live", "cap_usd": 1.0}, token="wrong")
    check("POST /api/v1/spend with a WRONG bearer -> 401",
          lambda: code == 401)

    # bounded BEFORE the read (service.every_body_is_bounded_before_it_is_read).
    # Raw connection: the declared Content-Length is the whole point, so the
    # bytes are never actually sent - a refusal that arrives without them is
    # the proof the check ran before the read.
    from http import client as _httpc      # not `import http.client`: that
    # would rebind the local `http()` helper above to the stdlib module

    def raw_post(path, headers, payload=b""):
        c = _httpc.HTTPConnection("127.0.0.1", svc.port, timeout=10)
        try:
            c.putrequest("POST", path)
            for hk, hv in headers.items():
                c.putheader(hk, hv)
            c.endheaders()
            if payload:
                c.send(payload)
            r = c.getresponse()
            return r.status, json.loads(r.read().decode("utf-8"))
        finally:
            c.close()

    auth = {"Authorization": "Bearer " + svc.token}
    code, body = raw_post("/api/v1/spend",
                          {**auth, "Content-Length": str((16 << 10) + 1)})
    check("POST body over the 16 KiB endpoint cap -> 413 BODY_TOO_LARGE "
          "(refused before a single byte was read)",
          lambda: code == 413 and body["error"] == "BODY_TOO_LARGE")
    code, body = raw_post("/api/v1/spend", {**auth, "Content-Length": "-5"})
    check("POST with negative Content-Length -> 400 BAD_LENGTH",
          lambda: code == 400 and body["error"] == "BAD_LENGTH")
    code, body = raw_post("/api/v1/spend", {**auth, "Content-Length": "abc"})
    check("POST with a non-integer Content-Length -> 400 BAD_LENGTH",
          lambda: code == 400 and body["error"] == "BAD_LENGTH")
    code, body = raw_post("/api/v1/spend", auth)
    check("POST with no Content-Length at all -> 400 LENGTH_REQUIRED",
          lambda: code == 400 and body["error"] == "LENGTH_REQUIRED")
    code, body = http("POST", "/api/v1/spend", raw=b"{not json")
    check("POST with malformed JSON -> 400 BAD_REQUEST",
          lambda: code == 400 and body["error"] == "BAD_REQUEST")

    code, body = http("POST", "/api/v1/spend", {"rail": "f03-live", "cap_usd": 4.0})
    check("live route: unconfirmed create -> 409 WIDEN_REQUIRES_CONFIRM",
          lambda: code == 409 and body["error"] == "WIDEN_REQUIRES_CONFIRM")
    gcode, gbody = http("GET", "/api/v1/spend")
    check("...and GET /spend shows no f03-live budget",
          lambda: gcode == 200 and "f03-live" not in gbody["rails"])

    code, body = http("POST", "/api/v1/spend",
                      {"rail": "f03-live", "cap_usd": 4.0, "allow_widen": True,
                       "reason": "live proof", "client_id": "selftest"})
    check("live route: confirmed create -> 200 verified round trip",
          lambda: code == 200 and body["round_trip"]["verified"] is True
          and body["after"]["cap_usd"] == 4.0)
    gcode, gbody = http("GET", "/api/v1/spend")
    check("...and GET /api/v1/spend now reports cap_usd 4.0 for f03-live",
          lambda: gcode == 200 and gbody["rails"]["f03-live"]["cap_usd"] == 4.0)
    seq = body["round_trip"]["ledger_seq"]
    check("...and the named ledger seq really is that BUDGET_SET on the chain",
          lambda: any(r["seq"] == seq and r["event"] == "BUDGET_SET"
                      and r["payload"]["client_id"] == "selftest"
                      and r["payload"]["actor"].startswith("bearer:")
                      for r in k2.ledger.verify()))
    check("...and the actor recorded is NOT the token itself",
          lambda: svc.token not in json.dumps(
              [r["payload"] for r in events(k2, "BUDGET_SET")]))
    svc.shutdown()

    bad = [(l, e) for l, ok, e in RESULTS if not ok]
    for label, ok, err in RESULTS:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label,
                              ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks (F-03 POST /api/v1/spend: widen gate, "
          "below-outstanding gate, typed refusals, bounded body, bearer, "
          "ledgered who/what/from/to, live round trip)"
          % ("PASS" if not bad else "FAIL", len(RESULTS)))
    return 0 if not bad else 1


def test_spend_admin():
    assert main() == 0


if __name__ == "__main__":
    sys.exit(main())
