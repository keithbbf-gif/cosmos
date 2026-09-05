#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""GET /api/v1/events: one verify() walk, optional ?tail=N (newest N).

FOLLOW_DECISION P-1: the handler used to materialise every record past
since_seq then slice to 100, then call ledger.head_seq() — a SECOND full
verify() — on every poll. A cold deck also had no server-side "newest N"
primitive, so it opened on seq 1..100 (the 2026-08-23 bootstrap, zero
FOLLOW_KEYS) and spent minutes catching up.

Default since_seq=0 still returns the OLDEST EVENTS_PAGE (cursor contract,
test_wave3). ?tail=N returns the NEWEST N past the cursor. head_seq is the
last seq of the one walk.

BITE FIRST against _delme/predispose_follow_events_20260831T105507Z/.

Run:  py -3.14 tests/test_events_page.py
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import tempfile
from http.client import HTTPConnection
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(REPO / "cosmos"))

from cosmos_kernel import Kernel, install  # noqa: E402
from cosmos_service import EVENTS_PAGE, page_events  # noqa: E402

EVIDENCE = REPO / "cosmos" / "_events_page_prove.json"
PRECHANGE_PY = (
    REPO / "_delme" / "predispose_follow_events_20260831T105507Z"
    / "cosmos" / "cosmos_service.py"
)

PAD = 120
TAIL_N = 5

DISCRIMINATING = (
    "tail_returns_newest",
    "tail_last_is_head",
    "one_verify_walk",
    "bad_tail_400",
)


def _load_service_class(service_py: Path | None):
    if service_py is None:
        from cosmos_service import Service
        return Service, "live:cosmos/cosmos_service.py"
    name = "cosmos_service_events_" + hashlib.sha256(
        str(service_py).encode("utf-8")).hexdigest()[:12]
    spec = importlib.util.spec_from_file_location(name, service_py)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load " + str(service_py))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod.Service, str(service_py)


def _raw_get(port, path, token=None):
    c = HTTPConnection("127.0.0.1", port, timeout=15)
    try:
        hdrs = {}
        if token:
            hdrs["Authorization"] = "Bearer " + token
        c.request("GET", path, headers=hdrs)
        r = c.getresponse()
        body = r.read()
        try:
            parsed = json.loads(body.decode("utf-8"))
        except ValueError:
            parsed = {"_raw": body[:200].decode("utf-8", "replace")}
        return r.status, parsed
    except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError) as e:
        return 599, {"error": type(e).__name__}
    finally:
        c.close()


def _pad(k, n: int) -> int:
    """Append n FOLLOW_PROBE events. Returns the new head seq."""
    for i in range(n):
        rec = k.ledger.append("FOLLOW_PROBE", {"i": i, "node": "probe"})
    return rec["seq"]


def run_named_checks(svc, k) -> list:
    out = []

    def rec(name, ok, detail=""):
        out.append({"name": name, "ok": bool(ok), "detail": str(detail)[:400]})

    port, token = svc.port, svc.token
    head = _pad(k, PAD)

    walks = {"n": 0}
    orig = k.ledger.verify

    def counting():
        walks["n"] += 1
        return orig()

    k.ledger.verify = counting
    try:
        code, body = _raw_get(port, "/api/v1/events?since_seq=0", token)
        rec("since0_oldest_first",
            code == 200 and body.get("events")
            and body["events"][0]["seq"] == 1
            and len(body["events"]) == EVENTS_PAGE
            and body.get("head_seq") == head,
            "status=%s n=%s first=%s head=%s want_head=%s" % (
                code, len(body.get("events") or []),
                (body.get("events") or [{}])[0].get("seq"),
                body.get("head_seq"), head))

        walks["n"] = 0
        code, body = _raw_get(
            port, "/api/v1/events?since_seq=0&tail=%d" % TAIL_N, token)
        evs = body.get("events") or []
        rec("tail_returns_newest",
            code == 200 and len(evs) == TAIL_N
            and evs[0]["seq"] == head - TAIL_N + 1
            and evs[-1]["seq"] == head
            and evs[0]["seq"] != 1,
            "status=%s n=%s first=%s last=%s head=%s" % (
                code, len(evs),
                evs[0]["seq"] if evs else None,
                evs[-1]["seq"] if evs else None,
                body.get("head_seq")))
        rec("tail_last_is_head",
            code == 200 and body.get("head_seq") == head
            and evs and evs[-1]["seq"] == body["head_seq"],
            "head_seq=%s last=%s" % (body.get("head_seq"),
                                     evs[-1]["seq"] if evs else None))
        rec("one_verify_walk",
            walks["n"] == 1,
            "verify_calls=%s (want 1; old handler called 2)" % walks["n"])
    finally:
        k.ledger.verify = orig

    code, body = _raw_get(port, "/api/v1/events?tail=abc", token)
    rec("bad_tail_400",
        code == 400 and body.get("error") == "BAD_TAIL",
        "status=%s error=%s" % (code, body.get("error")))
    code, body = _raw_get(port, "/api/v1/events?tail=0", token)
    rec("tail_zero_400",
        code == 400 and body.get("error") == "BAD_TAIL",
        "status=%s error=%s" % (code, body.get("error")))
    code, body = _raw_get(port, "/api/v1/events?tail=101", token)
    rec("tail_over_page_400",
        code == 400 and body.get("error") == "BAD_TAIL",
        "status=%s error=%s" % (code, body.get("error")))

    code, body = _raw_get(
        port, "/api/v1/events?since_seq=%d" % head, token)
    rec("cursor_at_head_empty",
        code == 200 and body.get("events") == []
        and body.get("head_seq") == head,
        "status=%s n=%s head=%s" % (
            code, len(body.get("events") or []), body.get("head_seq")))

    # helper: same numbers without HTTP
    h2, rows = page_events(k.ledger, 0, tail=TAIL_N)
    rec("helper_tail_matches_http",
        h2 == head and len(rows) == TAIL_N and rows[-1]["seq"] == head,
        "head=%s n=%s last=%s" % (h2, len(rows),
                                  rows[-1]["seq"] if rows else None))
    rec("boot_verified_carries_node",
        any(r["event"] == "BOOT_VERIFIED"
            and r["payload"].get("node") == r["payload"].get("worker")
            and r["payload"].get("node")
            for r in k.ledger.verify()),
        "BOOT_VERIFIED.node must equal worker (FOLLOW_KEYS)")
    return out


def run_against(service_py: Path | None, tag: str) -> dict:
    ServiceCls, loaded = _load_service_class(service_py)
    td = Path(tempfile.mkdtemp(prefix="cosmos_events_"))
    root = td / tag
    install(root, tree_id="events-" + tag)
    k = Kernel(root, worker="core")
    svc = ServiceCls(k, host="127.0.0.1", port=0)
    svc.serve_background()
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
        "all_named_pass": passed == len(checks),
        "discriminating_failed": all(
            not c["ok"] for c in checks if c["name"] in DISCRIMINATING),
        "head_seq_emitted": next(
            (c["detail"] for c in checks if c["name"] == "tail_last_is_head"),
            ""),
    }


def _print_run(title, run):
    print("== %s ==" % title)
    print("  loaded: %s" % run.get("loaded"))
    for c in run.get("checks") or []:
        print("  %s  %s  %s" % (
            "OK  " if c["ok"] else "FAIL", c["name"], c.get("detail") or ""))
    print("  %d/%d passed" % (run.get("tests_passed", 0),
                              run.get("tests_run", 0)))


def main() -> int:
    if not PRECHANGE_PY.is_file():
        print("REFUSING: pre-change service not staged at %s" % PRECHANGE_PY)
        return 1
    pre = run_against(PRECHANGE_PY, "pre")
    if not pre.get("discriminating_failed"):
        evidence = {"ok": False, "refused": "PRECHANGE_DID_NOT_FAIL",
                    "prechange": pre}
        EVIDENCE.write_text(json.dumps(evidence, indent=1), encoding="utf-8")
        _print_run("PRECHANGE (must FAIL discriminating)", pre)
        print("BITE FAIL — current module not run")
        return 1
    cur = run_against(None, "cur")
    evidence = {
        "ok": bool(cur.get("all_named_pass"))
        and bool(pre.get("discriminating_failed")),
        "probe": "tests/test_events_page.py — P-1 events page + ?tail=N",
        "prechange_path": str(PRECHANGE_PY),
        "prechange": pre,
        "current": cur,
        "events_page": EVENTS_PAGE,
        "tail_n": TAIL_N,
        "pad": PAD,
    }
    EVIDENCE.write_text(json.dumps(evidence, indent=1), encoding="utf-8")
    _print_run("PRECHANGE (discriminating MUST fail)", pre)
    _print_run("CURRENT (all MUST pass)", cur)
    print("EVIDENCE %s" % EVIDENCE)
    print("SELFTEST %s - %d checks current, %d passed; prechange discriminating "
          "failed=%s"
          % ("PASS" if evidence["ok"] else "FAIL",
             cur["tests_run"], cur["tests_passed"],
             pre.get("discriminating_failed")))
    return 0 if evidence["ok"] else 1


def test_events_page():
    assert main() == 0


if __name__ == "__main__":
    sys.exit(main())
