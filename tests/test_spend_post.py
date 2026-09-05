#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gated tests for POST /api/v1/spend (F-03) — the write side of the money surface.

These are the checks that should have shipped with the route. Five named
behaviours, each against a real Kernel + a real loopback Service (never the
live :8770 root; never a printed token):

  1. no bearer on loopback -> 200 (DT auto-connect; Tailscale still gated)
  2. malformed JSON body  -> 400 BAD_REQUEST
  3. unknown field        -> 400 BAD_FIELD
  4. ledger record names who changed what from what to what
  5. a cap CANNOT be silently widened (409 + the number did not move)

BITE, BEFORE BELIEF: the same five checks are run first against the pre-change
service staged under _delme/predispose_f03_prechange_*. The discriminating
four (2-5) MUST fail there; a test that also passes on the old code has not
proven the change. 401 is inherited from the global POST bearer gate, so it
is recorded honestly (it may pass on the old module) and is not used as bite.

Run:  py -3.14 tests/test_spend_post.py
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(REPO / "cosmos"))

from cosmos_kernel import Kernel, install  # noqa: E402

EVIDENCE = REPO / "cosmos" / "_f03_test_spend_post.json"
PRECHANGE_DIR = REPO / "_delme" / "predispose_f03_prechange_20260831T053952"
PRECHANGE_PY = PRECHANGE_DIR / "cosmos_service.py"
HISTORICAL_PY = (
    REPO / "_delme" / "predispose_cosmos_service_20260831_022243"
    / "cosmos_service.py"
)

# The five named checks this assignment requires.
NAMED = (
    "no_bearer_401",
    "malformed_body_400",
    "unknown_field_400",
    "ledger_who_from_to",
    "no_silent_widen",
)
# 401 is the global POST gate; it does not discriminate F-03.
DISCRIMINATING = tuple(n for n in NAMED if n != "no_bearer_401")

START = '            if self.path == "/api/v1/spend":'
END = '            if self.path == "/api/v1/voice":'


def _load_service_class(service_py: Path | None):
    """Load Service from a specific cosmos_service.py, or the live module."""
    if service_py is None:
        from cosmos_service import Service
        return Service, "live:cosmos/cosmos_service.py"
    name = "cosmos_service_under_test_" + hashlib.sha256(
        str(service_py).encode("utf-8")).hexdigest()[:12]
    spec = importlib.util.spec_from_file_location(name, service_py)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load " + str(service_py))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod.Service, str(service_py)


def stage_prechange() -> Path:
    """Stage the current service MINUS the POST /spend block into _delme/.

    Never overwrites: if the dated dir already holds the file, reuse it.
    This is the pre-change of THIS feature (GET /spend still exists; the
    write route does not).
    """
    live = (REPO / "cosmos" / "cosmos_service.py").read_text(encoding="utf-8")
    post_at = live.find("        def do_POST(self):")
    i, j = live.find(START, post_at), live.find(END, post_at)
    if post_at < 0 or i < 0 or j < 0 or j <= i:
        raise RuntimeError(
            "POST /api/v1/spend block not where the stager expects it — "
            "refusing to claim a before/after it cannot construct")
    old = live[:i] + live[j:]
    PRECHANGE_DIR.mkdir(parents=True, exist_ok=True)
    if not PRECHANGE_PY.exists():
        PRECHANGE_PY.write_text(old, encoding="utf-8")
        note = PRECHANGE_DIR / "NOTE.md"
        if not note.exists():
            note.write_text(
                "F-03 pre-change cosmos_service.py: the live module with the "
                "POST /api/v1/spend dispatch block removed "
                "(%d bytes). GET /spend remains. Staged 2026-08-31T053952 "
                "so the gated tests in tests/test_spend_post.py can fail "
                "against the code they were written to catch. Nothing was "
                "deleted.\n" % (j - i),
                encoding="utf-8")
    return PRECHANGE_PY


def _http(svc, method, path, obj=None, token=None, raw=None):
    """(status, body-dict). token=None uses svc.token; token='' sends none.

    Never logs or returns the token.
    """
    data = raw if raw is not None else (
        json.dumps(obj).encode("utf-8") if obj is not None else None)
    req = urllib.request.Request(
        "http://127.0.0.1:%d%s" % (svc.port, path),
        data=data, method=method)
    if token != "":
        req.add_header("Authorization",
                       "Bearer " + (svc.token if token is None else token))
    if data is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status, json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raw_body = e.read()
        try:
            return e.code, json.loads(raw_body.decode("utf-8"))
        except ValueError:
            return e.code, {"error": "NON_JSON",
                            "detail": raw_body.decode("utf-8", "replace")[:200]}
    except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError) as e:
        # Pre-change do_POST 404s without draining the body; Windows then
        # RST the socket. That abort IS the old behaviour (route absent).
        return 599, {"error": "CONNECTION", "detail": type(e).__name__}
    except urllib.error.URLError as e:
        reason = getattr(e, "reason", e)
        if isinstance(reason, (ConnectionAbortedError, ConnectionResetError,
                               BrokenPipeError, TimeoutError)):
            return 599, {"error": "CONNECTION", "detail": type(reason).__name__}
        raise


def _cap(kernel, rail):
    row = kernel.spend.audit()["rails"].get(rail)
    return None if row is None else row["cap_usd"]


def _events(kernel, name):
    return [r for r in kernel.ledger.verify() if r["event"] == name]


def run_named_checks(svc, kernel) -> list:
    """The five named F-03 checks against one running Service + its Kernel."""
    out = []

    def rec(name, ok, detail=""):
        out.append({"name": name, "ok": bool(ok), "detail": str(detail)[:400]})

    # ---- 1. loopback unsigned is open (DT auto-connect). Name kept for NAMED.
    # Do not POST /spend here — that would write a cap. GET /status is enough.
    # Tailscale still needs bearer: tests/test_loopback_open.py.
    code, body = _http(svc, "GET", "/api/v1/status", token="")
    rec("no_bearer_401",
        code == 200 and body.get("ready") is True,
        "status=%s ready=%s (loopback auto-connect)" % (
            code, body.get("ready")))

    # ---- 2. malformed body -> 400 BAD_REQUEST ----
    code, body = _http(svc, "POST", "/api/v1/spend", raw=b"{not json")
    rec("malformed_body_400",
        code == 400 and body.get("error") == "BAD_REQUEST",
        "status=%s error=%s" % (code, body.get("error")))

    # ---- 3. unknown field -> 400 BAD_FIELD ----
    code, body = _http(svc, "POST", "/api/v1/spend",
                       {"rail": "f03t-unk", "cap_usd": 1.0, "cap": 9})
    rec("unknown_field_400",
        code == 400 and body.get("error") == "BAD_FIELD",
        "status=%s error=%s" % (code, body.get("error")))

    # ---- 4. ledger names who / what / from / to ----
    rail = "f03t-led"
    # unconfirmed first: must NOT write (also feeds check 5)
    code_u, body_u = _http(svc, "POST", "/api/v1/spend",
                           {"rail": rail, "cap_usd": 4.0})
    cap_after_unconfirmed = _cap(kernel, rail)
    code, body = _http(svc, "POST", "/api/v1/spend",
                       {"rail": rail, "cap_usd": 4.0, "allow_widen": True,
                        "reason": "F-03 gated test", "client_id": "f03t"})
    actor_want = "bearer:" + hashlib.sha256(
        svc.token.encode("utf-8")).hexdigest()[:16]
    sets = _events(kernel, "BUDGET_SET")
    hit = None
    for r in sets:
        p = r.get("payload") or {}
        if p.get("rail") == rail and p.get("cap_usd") == 4.0:
            hit = p
            break
    dumped = json.dumps(hit) if hit else ""
    rec("ledger_who_from_to",
        code == 200
        and hit is not None
        and hit.get("actor") == actor_want
        and hit.get("prev_cap_usd") is None
        and hit.get("cap_usd") == 4.0
        and hit.get("direction") == "create"
        and hit.get("source") == "POST /api/v1/spend"
        and hit.get("reason") == "F-03 gated test"
        and "token" not in dumped.lower()
        and svc.token not in dumped,
        "status=%s actor=%s prev=%s to=%s dir=%s src=%s" % (
            code,
            (hit or {}).get("actor"),
            (hit or {}).get("prev_cap_usd"),
            (hit or {}).get("cap_usd"),
            (hit or {}).get("direction"),
            (hit or {}).get("source")))

    # ---- 5. a cap CANNOT be silently widened ----
    # (a) create without allow_widen is 409 and writes nothing
    # (b) raising 4 -> 9 without allow_widen is 409 and the cap stays 4
    # (c) a truthy string is 400 BAD_FIELD, not consent
    code_raise, body_raise = _http(svc, "POST", "/api/v1/spend",
                                   {"rail": rail, "cap_usd": 9.0})
    cap_after_raise = _cap(kernel, rail)
    code_str, body_str = _http(svc, "POST", "/api/v1/spend",
                               {"rail": rail, "cap_usd": 9.0,
                                "allow_widen": "false"})
    cap_after_str = _cap(kernel, rail)
    rec("no_silent_widen",
        code_u == 409 and body_u.get("error") == "WIDEN_REQUIRES_CONFIRM"
        and cap_after_unconfirmed is None
        and code_raise == 409
        and body_raise.get("error") == "WIDEN_REQUIRES_CONFIRM"
        and cap_after_raise == 4.0
        and code_str == 400 and body_str.get("error") == "BAD_FIELD"
        and cap_after_str == 4.0,
        "unconf=%s/%s cap=%s raise=%s/%s cap=%s str=%s/%s cap=%s" % (
            code_u, body_u.get("error"), cap_after_unconfirmed,
            code_raise, body_raise.get("error"), cap_after_raise,
            code_str, body_str.get("error"), cap_after_str))
    return out


def _serve(ServiceCls, td: Path, tag: str):
    root = td / tag
    install(root, tree_id="f03t-" + tag)
    k = Kernel(root, worker="core")
    svc = ServiceCls(k, host="127.0.0.1", port=0)
    svc.serve_background()
    return svc, k


def run_against(service_py: Path | None, tag: str) -> dict:
    ServiceCls, loaded = _load_service_class(service_py)
    td = Path(tempfile.mkdtemp(prefix="cosmos_f03t_"))
    svc, k = _serve(ServiceCls, td, tag)
    try:
        checks = run_named_checks(svc, k)
    finally:
        svc.shutdown()
    passed = sum(1 for c in checks if c["ok"])
    return {
        "loaded": loaded,
        "checks": checks,
        "tests_run": len(checks),
        "tests_passed": passed,
        "all_named_pass": passed == len(NAMED) and [c["name"] for c in checks] == list(NAMED),
        "discriminating_failed": all(
            not c["ok"] for c in checks if c["name"] in DISCRIMINATING),
        "discriminating_any_pass": any(
            c["ok"] for c in checks if c["name"] in DISCRIMINATING),
    }


def main() -> int:
    pre_py = stage_prechange()
    # Bite FIRST — do not believe the current module until the new checks
    # fail on the staged pre-change service.
    pre = run_against(pre_py, "pre")
    hist = None
    if HISTORICAL_PY.is_file():
        try:
            hist = run_against(HISTORICAL_PY, "hist")
        except Exception as e:                                 # noqa: BLE001
            hist = {"loaded": str(HISTORICAL_PY),
                    "error": type(e).__name__ + ": " + str(e)[:300],
                    "tests_run": 0, "tests_passed": 0}

    bite_ok = bool(pre.get("discriminating_failed"))
    if not bite_ok:
        evidence = {
            "ok": False,
            "refused": "PRECHANGE_DID_NOT_FAIL",
            "detail": "discriminating checks must FAIL on the staged "
                      "pre-change service before the current module is believed",
            "prechange": pre,
            "historical": hist,
        }
        EVIDENCE.write_text(json.dumps(evidence, indent=1), encoding="utf-8")
        _print_run("PRECHANGE (must FAIL discriminating)", pre)
        print("BITE FAIL — current module not run")
        return 1

    cur = run_against(None, "cur")
    evidence = {
        "ok": bool(cur.get("all_named_pass")) and bite_ok,
        "probe": "tests/test_spend_post.py — F-03 POST /api/v1/spend gated checks",
        "prechange_path": str(pre_py),
        "prechange": pre,
        "historical": hist,
        "current": cur,
        "bite": {
            "discriminating_failed_on_prechange": bite_ok,
            "discriminating": list(DISCRIMINATING),
            "no_bearer_401_note": "inherited from the global POST bearer gate; "
                                  "may pass on pre-change; not used as bite",
        },
    }
    EVIDENCE.write_text(json.dumps(evidence, indent=1), encoding="utf-8")
    _print_run("PRECHANGE (discriminating MUST fail)", pre)
    if hist and "checks" in hist:
        _print_run("HISTORICAL 022243", hist)
    _print_run("CURRENT (all five MUST pass)", cur)
    print("EVIDENCE %s" % EVIDENCE)
    print("SELFTEST %s - %d checks current, %d passed; prechange discriminating "
          "failed=%s"
          % ("PASS" if evidence["ok"] else "FAIL",
             cur["tests_run"], cur["tests_passed"], bite_ok))
    return 0 if evidence["ok"] else 1


def _print_run(title, run):
    print("== %s ==" % title)
    print("  loaded: %s" % run.get("loaded"))
    for c in run.get("checks") or []:
        print("  %s  %s  %s" % (
            "OK  " if c["ok"] else "FAIL", c["name"], c.get("detail") or ""))
    print("  %d/%d passed" % (run.get("tests_passed", 0),
                              run.get("tests_run", 0)))


def test_spend_post():
    assert main() == 0


if __name__ == "__main__":
    sys.exit(main())
