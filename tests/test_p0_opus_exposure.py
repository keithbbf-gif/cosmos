#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""P0 Opus exposure: loopback CSRF, resume day-cap, wallet=api meter, CCR.lease /2.

These checks FAIL on origin/main (pre-change) and PASS on this branch:
  * _request_authed has no trust/method/headers; CSRF helpers are absent
  * SpendGuard.clear has no reset_day; resume calls clear(cid) and wipes day
  * Dispatcher has no _call_price; wallet=api with metered_usd=0 is dispatched
  * CCR.lease schema is /1; no Arbiter token / renew
"""
from __future__ import annotations

import inspect
import json
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "cosmos"))

from cosmos_ccr import (  # noqa: E402
    SCHEMA, SCHEMA_LEGACY, CcrError, acquire, held, is_legacy, read_lease,
    release, renew, status,
)
from cosmos_clock import atomic_json
from cosmos_kernel import Kernel, install  # noqa: E402
from cosmos_ledger import Ledger  # noqa: E402
from cosmos_paths import CosmosPaths, write_sentinel  # noqa: E402
from cosmos_service import Service  # noqa: E402
from cosmos_rails import Dispatcher, RailError  # noqa: E402
from cosmos_registry import Registry  # noqa: E402
from cosmos_service import (  # noqa: E402
    DEFAULT_LOOPBACK_TRUST, _csrf_headers_ok, _request_authed,
    parse_loopback_trust,
)
from cosmos_spend import SpendGate  # noqa: E402
from cosmos_spendguard import SpendGuard  # noqa: E402

RESULTS: list[tuple[str, bool, str]] = []


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:  # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


def expect(exc, kind):
    def wrap(fn):
        def inner():
            try:
                fn()
            except exc as e:
                return e.kind == kind
            return False
        return inner
    return wrap


class Clock:
    def __init__(self, t: float = 1_000.0):
        self.t = t

    def __call__(self) -> float:
        return self.t


def _ccr_live():
    td = Path(tempfile.mkdtemp(prefix="p0_ccr_"))
    live = td / "live"
    write_sentinel(live, tree_id="p0-ccr")
    (live / "state" / "control").mkdir(parents=True)
    return CosmosPaths(live)


class _WalletApi:
    kind = "API"
    wallet = "api"
    metered_usd = 0.0
    called = False

    def probe(self):
        return True, "ok"

    def dispatch(self, payload):
        self.called = True
        return {"ok": True, "kind": "API", "usd": 0.01}


class _WalletPriced(_WalletApi):
    estimate_usd = 0.02


def _disp(td: Path, adapter, spend=None, lid="api-wallet"):
    td.mkdir(parents=True, exist_ok=True)
    led = Ledger(td / "rails.jsonl", b"p0", "core")
    reg = Registry(led)
    reg.register(lid, "API", "core", "models")
    reg.attach_probe(lid, adapter.probe)
    reg.probe_all()
    return Dispatcher(reg, {lid: adapter}, led, spend=spend), led


def test_loopback_csrf() -> None:
    tok = "secret-for-unit"
    check("code default trust is guarded",
          lambda: DEFAULT_LOOPBACK_TRUST == "guarded")
    check("parse comments then legacy",
          lambda: parse_loopback_trust("# Keith\nlegacy\n") == "legacy")
    check("unknown token fail-closes to guarded",
          lambda: parse_loopback_trust("maybe") == "guarded")
    check("empty file fail-closes to guarded",
          lambda: parse_loopback_trust("") == "guarded")

    good = {
        "Host": "127.0.0.1:8770",
        "Content-Type": "application/json",
        "Sec-Fetch-Site": "same-origin",
    }
    evil = {
        "Host": "127.0.0.1:8770",
        "Origin": "https://evil.example",
        "Content-Type": "application/json",
        "Sec-Fetch-Site": "cross-site",
    }
    form = {
        "Host": "127.0.0.1:8770",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://evil.example",
    }
    check("CSRF ok: loopback Host + JSON + same-origin",
          lambda: _csrf_headers_ok(good) is True)
    check("CSRF refuse: cross-site Origin + Sec-Fetch-Site",
          lambda: _csrf_headers_ok(evil) is False)
    check("CSRF refuse: HTML form Content-Type",
          lambda: _csrf_headers_ok(form) is False)
    check("CSRF refuse: Host not loopback (DNS rebind)",
          lambda: _csrf_headers_ok({"Host": "evil.example",
                                    "Content-Type": "application/json"}) is False)

    check("GET loopback no bearer is authed (DT auto-connect)",
          lambda: _request_authed("127.0.0.1", "", tok, method="GET",
                                  trust="guarded") is True)
    check("POST guarded + evil Origin is NOT authed",
          lambda: _request_authed("127.0.0.1", "", tok, method="POST",
                                  headers=evil, trust="guarded") is False)
    check("POST guarded + good CSRF is authed",
          lambda: _request_authed("127.0.0.1", "", tok, method="POST",
                                  headers=good, trust="guarded") is True)
    check("valid bearer always passes (evil Origin)",
          lambda: _request_authed("127.0.0.1", "Bearer " + tok, tok,
                                  method="POST", headers=evil,
                                  trust="guarded") is True)
    check("valid bearer passes on Tailscale too",
          lambda: _request_authed("100.64.1.2", "Bearer " + tok, tok,
                                  method="POST", headers=evil,
                                  trust="guarded") is True)
    check("legacy open loopback: evil POST still authed",
          lambda: _request_authed("127.0.0.1", "", tok, method="POST",
                                  headers=evil, trust="legacy") is True)
    check("off: loopback without bearer is NOT authed",
          lambda: _request_authed("127.0.0.1", "", tok, method="GET",
                                  trust="off") is False)
    check("off: valid bearer still passes",
          lambda: _request_authed("127.0.0.1", "Bearer " + tok, tok,
                                  method="POST", headers=evil,
                                  trust="off") is True)


def test_resume_does_not_reset_day() -> None:
    td = Path(tempfile.mkdtemp(prefix="p0_sg_"))
    g = SpendGuard(td / "state.json")
    g.record("s1", 0.40)
    before = g.audit()
    check("recorded day spend before resume-clear",
          lambda: before["day_used_usd"] == 0.40)

    sig = inspect.signature(SpendGuard.clear)
    check("SpendGuard.clear accepts reset_day",
          lambda: "reset_day" in sig.parameters)

    ok = g.clear(None, reset_day=False)
    after = g.audit()
    check("clear(reset_day=False) returns True", lambda: ok is True)
    check("clear(reset_day=False) keeps the day lane",
          lambda: after["day_used_usd"] == 0.40)
    check("clear(reset_day=False) still drops session totals",
          lambda: after["sessions"] == {})

    g.record("s2", 0.10)
    g.clear(None)  # default reset_day=True
    wiped = g.audit()
    check("clear(reset_day=True) still zeros the day lane",
          lambda: wiped["day_used_usd"] == 0.0)

    src = (ROOT / "cosmos" / "cosmos_service.py").read_text(encoding="utf-8")
    check("POST /control/resume calls clear(..., reset_day=False)",
          lambda: "reset_day=False" in src
          and "/api/v1/control/resume" in src)


def test_wallet_api_metered() -> None:
    td = Path(tempfile.mkdtemp(prefix="p0_wal_"))
    boom = _WalletApi()
    disp, _led = _disp(td / "unpriced", boom)
    check("Dispatcher exposes _call_price",
          lambda: callable(getattr(disp, "_call_price", None)))
    check("wallet=api with no price is unpriced (None)",
          lambda: disp._call_price(boom, {}) is None)
    check("UNPRICED_METERED refuses BEFORE the call",
          expect(RailError, "UNPRICED_METERED")(
              lambda: disp.dispatch("core", "models", {"prompt": "x"})))
    check("UNPRICED_METERED did not invoke the adapter",
          lambda: boom.called is False)

    priced = _WalletPriced()
    disp2, _ = _disp(td / "ungated", priced)
    check("UNGATED_METERED refuses when spend gate is missing",
          expect(RailError, "UNGATED_METERED")(
              lambda: disp2.dispatch("core", "models", {"prompt": "x"})))
    check("UNGATED_METERED did not invoke the adapter",
          lambda: priced.called is False)

    ok_ad = _WalletPriced()
    led = Ledger(td / "ok.jsonl", b"p0", "core")
    spend = SpendGate(led)
    spend.set_budget("api-wallet", 1.0)
    disp3, _ = _disp(td / "ok", ok_ad, spend=spend)
    out = disp3.dispatch("core", "models", {"prompt": "hi"})
    check("wallet=api + estimate_usd + spend gate runs the call",
          lambda: out.get("ok") is True and ok_ad.called is True)
    check("payload.estimate_usd is used as the call price",
          lambda: disp3._call_price(ok_ad, {"estimate_usd": 0.07}) == 0.07)


def test_ccr_lease_arbiter() -> None:
    check("projection schema is /2", lambda: SCHEMA == "cosmos-ccr-lease/2")
    check("legacy schema /1 is still named",
          lambda: SCHEMA_LEGACY == "cosmos-ccr-lease/1")

    clk = Clock(5_000.0)
    p = _ccr_live()
    rec = acquire(p, sid="s-new", pid=11, stream="Cm", ttl=30.0, clock=clk)
    check("acquire writes schema /2", lambda: rec["schema"] == SCHEMA)
    check("acquire writes fencing token", lambda: int(rec["token"]) >= 1)
    check("acquire writes expires_at", lambda: rec["expires_at"] == 5_030.0)
    check("held() is True while TTL remains", lambda: held(p, clock=clk) is True)

    nxt = renew(p, sid="s-new", ttl=60.0, clock=clk)
    check("renew extends expires_at", lambda: nxt["expires_at"] == 5_060.0)
    check("renew keeps the same token", lambda: nxt["token"] == rec["token"])

    clk.t = 5_061.0
    check("held() is False after TTL", lambda: held(p, clock=clk) is False)
    rec2 = acquire(p, sid="s-next", pid=22, ttl=10.0, clock=clk)
    check("expired /2 can be taken over (new token)",
          lambda: rec2["sid"] == "s-next" and rec2["token"] > rec["token"])
    release(p, sid="s-next", clock=clk)

    legacy_paths = _ccr_live()
    atomic_json(legacy_paths.role("state", "control", "CCR.lease"), {
        "schema": SCHEMA_LEGACY,
        "sid": "s-legacy",
        "pid": 99,
        "stream": "Cm",
        "tree_id": "p0-ccr",
        "taken_at": 1.0,
        "taken_pid": 99,
    })
    cur = read_lease(legacy_paths)
    check("legacy /1 is recognized", lambda: is_legacy(cur) is True)
    check("legacy /1 is held with no TTL",
          lambda: held(legacy_paths, clock=clk) is True)
    check("legacy /1 blocks a second acquire until that sid releases",
          expect(CcrError, "CCR_HELD")(
              lambda: acquire(legacy_paths, sid="s-thief", pid=1, clock=clk)))
    same = renew(legacy_paths, sid="s-legacy", clock=clk)
    check("renew of /1 is a no-op (honor until release)",
          lambda: same.get("schema") == SCHEMA_LEGACY and "token" not in same)
    st = status(legacy_paths, clock=clk)
    check("status names legacy=True for /1",
          lambda: st["legacy"] is True and st["held"] is True)
    release(legacy_paths, sid="s-legacy", clock=clk)
    check("legacy /1 release frees the pen",
          lambda: held(legacy_paths, clock=clk) is False)
    rec3 = acquire(legacy_paths, sid="s-after", pid=3, ttl=9.0, clock=clk)
    check("after /1 release, new acquire is schema /2",
          lambda: rec3["schema"] == SCHEMA and rec3["sid"] == "s-after")


def _http(svc, method, path, obj=None, token=None, extra_headers=None):
    req = urllib.request.Request(
        f"http://127.0.0.1:{svc.port}{path}",
        data=(json.dumps(obj).encode("utf-8") if obj is not None else None),
        method=method)
    if token:
        req.add_header("Authorization", "Bearer " + token)
    if obj is not None:
        req.add_header("Content-Type", "application/json")
    for k, v in (extra_headers or {}).items():
        req.add_header(k, v)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8"))


def test_resume_http_and_csrf() -> None:
    td = Path(tempfile.mkdtemp(prefix="p0_http_"))
    root = install(td / "live", tree_id="p0-resume")
    k = Kernel(root, worker="core")
    lt = time.localtime()
    day = f"{lt.tm_year:04d}-{lt.tm_mon:02d}-{lt.tm_mday:02d}"
    state = k.paths.config("spendguard_state.json")
    state.write_text(json.dumps({
        "day": day,
        "day_usd": 1.25,
        "day_credit_usd": 0.0,
        "sessions": {"phone-a": 0.40},
        "req_epochs": [time.time()],
    }, indent=1), encoding="utf-8")
    svc = Service(k, host="127.0.0.1", port=0)
    svc.serve_background()
    try:
        code, body = _http(svc, "POST", "/api/v1/control/resume", {},
                           token=svc.token)
        check("POST /control/resume is 200",
              lambda: code == 200 and body.get("resumed") is True)
        after = json.loads(state.read_text(encoding="utf-8"))
        check("HTTP resume kept day_usd (did not reset the day cap)",
              lambda: float(after.get("day_usd") or 0) == 1.25)
        check("HTTP resume cleared the session lane",
              lambda: after.get("sessions") == {})

        evil_code, _evil = _http(
            svc, "POST", "/api/v1/control/resume", {},
            extra_headers={
                "Origin": "https://evil.example",
                "Sec-Fetch-Site": "cross-site",
            })
        check("guarded POST resume from evil Origin is 401 without bearer",
              lambda: evil_code == 401)
    finally:
        svc.shutdown()


def main() -> int:
    test_loopback_csrf()
    test_resume_does_not_reset_day()
    test_wallet_api_metered()
    test_ccr_lease_arbiter()
    test_resume_http_and_csrf()
    bad = 0
    for label, ok, err in RESULTS:
        print(("  [ok] " if ok else "  [FAIL] ") + label
              + ((" " + err) if err else ""))
        if not ok:
            bad += 1
    print(f"{len(RESULTS) - bad}/{len(RESULTS)} passed")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
