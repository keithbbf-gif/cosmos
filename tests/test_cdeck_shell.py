#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gated tests for F-11: Core serves builds/cdeck/ui/ on its own origin.

PARITY_AUDIT K-2: a browser deck is cross-origin to Core unless Core itself
serves the shell. Same-origin is the fix; a header that would let any other
origin read the API is deliberately not added.

Exact-match allowlist, no bearer on the shell. Loopback /api/v1 auto-connects
(DT cDeck, Keith 2026-09-04); Tailscale/phone still need the bearer.
Relative hrefs (app.css, app.js) only work under /cdeck/, so /cdeck 302s there.

BITE FIRST against the pre-F-11 service staged at
_delme/predispose_cosmos_service_f11_20260831T053952/.

Run:  py -3.14 tests/test_cdeck_shell.py
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

EVIDENCE = REPO / "cosmos" / "_f11_test_cdeck_shell.json"
PRECHANGE_PY = (
    REPO / "_delme" / "predispose_cosmos_service_f11_20260831T053952"
    / "cosmos_service.py"
)
UI = REPO / "builds" / "cdeck" / "ui"

NAMED = (
    "slashless_redirect",
    "index_bytes",
    "app_js_bytes",
    "app_css_bytes",
    "manifest_bytes",
    "sw_bytes",
    "api_loopback_open",
    "unknown_cdeck_not_served",
    "traversal_is_not_a_file",
    "no_cross_origin_header",
)
# Inherited: unknown/traversal not the index. Loopback API is open (DT).
# The bite is the shell actually being served as bytes.
DISCRIMINATING = (
    "slashless_redirect",
    "index_bytes",
    "app_js_bytes",
    "app_css_bytes",
    "manifest_bytes",
    "sw_bytes",
    "no_cross_origin_header",
)


def _load_service_class(service_py: Path | None):
    if service_py is None:
        from cosmos_service import Service
        return Service, "live:cosmos/cosmos_service.py"
    name = "cosmos_service_f11_" + hashlib.sha256(
        str(service_py).encode("utf-8")).hexdigest()[:12]
    spec = importlib.util.spec_from_file_location(name, service_py)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load " + str(service_py))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod.Service, str(service_py)


def _raw_get(port, path, token=None):
    """(status, headers-lower, body-bytes). token='' or None = no Authorization."""
    c = HTTPConnection("127.0.0.1", port, timeout=15)
    try:
        hdrs = {}
        if token:
            hdrs["Authorization"] = "Bearer " + token
        c.request("GET", path, headers=hdrs)
        r = c.getresponse()
        return r.status, {k.lower(): v for k, v in r.getheaders()}, r.read()
    except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError) as e:
        return 599, {}, type(e).__name__.encode("ascii")
    finally:
        c.close()


def run_named_checks(svc) -> list:
    out = []

    def rec(name, ok, detail=""):
        out.append({"name": name, "ok": bool(ok), "detail": str(detail)[:400]})

    port = svc.port
    disk = {n: (UI / n).read_bytes() for n in (
        "index.html", "app.js", "app.css", "cdeck.webmanifest", "sw.js")}

    code, hdrs, body = _raw_get(port, "/cdeck")
    rec("slashless_redirect",
        code == 302 and hdrs.get("location") == "/cdeck/",
        "status=%s location=%s" % (code, hdrs.get("location")))

    code, hdrs, body = _raw_get(port, "/cdeck/")
    rec("index_bytes",
        code == 200 and body == disk["index.html"]
        and (hdrs.get("content-type") or "").startswith("text/html"),
        "status=%s bytes=%s disk=%s ctype=%s" % (
            code, len(body), len(disk["index.html"]),
            hdrs.get("content-type")))
    rec("no_cross_origin_header",
        code == 200 and "access-control-allow-origin" not in hdrs,
        "status=%s has_acao=%s" % (
            code, "access-control-allow-origin" in hdrs))

    for name, path, key in (
            ("app_js_bytes", "/cdeck/app.js", "app.js"),
            ("app_css_bytes", "/cdeck/app.css", "app.css"),
            ("manifest_bytes", "/cdeck/cdeck.webmanifest", "cdeck.webmanifest"),
            ("sw_bytes", "/cdeck/sw.js", "sw.js")):
        c, h, b = _raw_get(port, path)
        rec(name,
            c == 200 and b == disk[key],
            "status=%s bytes=%s disk=%s" % (c, len(b), len(disk[key])))

    code, hdrs, body = _raw_get(port, "/api/v1/status")
    rec("api_loopback_open",
        code == 200 and b'"ready"' in body,
        "status=%s" % code)

    code, hdrs, body = _raw_get(port, "/cdeck/nope")
    rec("unknown_cdeck_not_served",
        code in (401, 404) and body != disk["index.html"],
        "status=%s" % code)

    code, hdrs, body = _raw_get(port, "/cdeck/../cosmos/cosmos_service.py")
    py = (REPO / "cosmos" / "cosmos_service.py").read_bytes()
    rec("traversal_is_not_a_file",
        body != py and code in (401, 404, 400),
        "status=%s body_len=%s" % (code, len(body)))
    return out


def run_against(service_py: Path | None, tag: str) -> dict:
    ServiceCls, loaded = _load_service_class(service_py)
    td = Path(tempfile.mkdtemp(prefix="cosmos_f11_"))
    root = td / tag
    install(root, tree_id="f11-" + tag)
    k = Kernel(root, worker="core")
    svc = ServiceCls(k, host="127.0.0.1", port=0)
    svc.serve_background()
    try:
        checks = run_named_checks(svc)
    finally:
        svc.shutdown()
    passed = sum(1 for c in checks if c["ok"])
    return {
        "loaded": loaded,
        "checks": checks,
        "tests_run": len(checks),
        "tests_passed": passed,
        "all_named_pass": passed == len(NAMED),
        "discriminating_failed": all(
            not c["ok"] for c in checks if c["name"] in DISCRIMINATING),
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
        print("REFUSING: pre-F-11 service not staged at %s" % PRECHANGE_PY)
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
        "ok": bool(cur.get("all_named_pass")) and bool(pre.get("discriminating_failed")),
        "probe": "tests/test_cdeck_shell.py — F-11 cDeck same-origin shell",
        "prechange_path": str(PRECHANGE_PY),
        "prechange": pre,
        "current": cur,
        "ui_files": {n: (UI / n).stat().st_size
                     for n in ("index.html", "app.js", "app.css",
                               "cdeck.webmanifest", "sw.js")},
    }
    EVIDENCE.write_text(json.dumps(evidence, indent=1), encoding="utf-8")
    _print_run("PRECHANGE (discriminating MUST fail)", pre)
    _print_run("CURRENT (all ten MUST pass)", cur)
    print("EVIDENCE %s" % EVIDENCE)
    print("SELFTEST %s - %d checks current, %d passed; prechange discriminating "
          "failed=%s"
          % ("PASS" if evidence["ok"] else "FAIL",
             cur["tests_run"], cur["tests_passed"],
             pre.get("discriminating_failed")))
    return 0 if evidence["ok"] else 1


def test_cdeck_shell():
    assert main() == 0


if __name__ == "__main__":
    sys.exit(main())
